"""Export per-sample instability probabilities and metadata of the trained set-based generator response model.

Runs where the simulated dataset, the trained checkpoints and the model code live; nothing is retrained and no
simulation is run. Each run's inputs are rebuilt with the model code's own helpers (predict_runs.Data.inputs), the
probabilities are recomputed from best_model.pt, and every set is checked against the stored per-sample predictions
(validation, main test, N-2 to N-4) or the stored AUC / miss rate (N-5, N-6, held-out N-1 topologies).

Outputs in --out-dir:
  scores_main.npz     proposed model, one row of probabilities per seed: validation, main test, N-2 to N-6
  scores_holdout.npz  the same model trained without five single-line-outage topologies: its validation and test
                      sets and the held-out topologies
  embed_main_s0.npz   mean-pooled token embedding z (input of the final MLP) of the first main run, same sample order

Example:
  python export_scores.py --code-dir CODE --dataset FULL.npz --nk56 NK56.npz --pred-dir PRED --nk56-ref EXT.json \
      --main-runs RUN_s0 ... RUN_s4 --holdout-runs HOLD_s0 HOLD_s1 HOLD_s2 --out-dir OUT --device cuda:0
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

SET_CODES = {"val": 0, "test": 1, "n2": 2, "n3": 3, "n4": 4, "n5": 5, "n6": 6,
             "holdout": 10, "holdout_test": 11}
NK56_OP_OFFSET = 1_000_000          # operating-point ids of the N-5 / N-6 dataset, kept apart from the main dataset's


def topo_keys(op_outages: np.ndarray) -> np.ndarray:
    """Outaged lines of each operating point as a sorted string, '' for the intact network."""
    return np.array(["-".join(str(int(v)) for v in sorted(r[r >= 0])) for r in op_outages])


def infer(model, inputs, device, embed: bool, batch: int = 2048):
    """Probabilities, and with embed also the pooled embedding fed to the final MLP."""
    store: list = []
    hook = model.mlp.register_forward_hook(lambda m, inp, out: store.append(inp[0].detach().cpu().numpy())) \
        if embed else None
    probs = []
    with torch.no_grad():
        for i in range(0, len(inputs[0]), batch):
            args = [torch.from_numpy(np.ascontiguousarray(a[i:i + batch])).to(device) for a in inputs]
            probs.append(torch.sigmoid(model(*args)).cpu().numpy())
    if hook is not None:
        hook.remove()
    prob = np.concatenate(probs).astype(np.float32)
    return (prob, np.concatenate(store).astype(np.float16)) if embed else (prob, None)


def miss_rate(y: np.ndarray, prob: np.ndarray, thr: float) -> float:
    return 100.0 * float((prob[y == 1] < thr).mean())


def metadata(d: dict, idx: np.ndarray, op_offset: int, keys: np.ndarray) -> dict:
    op = d["s_op"][idx]
    return {"label": d["s_label"][idx].astype(np.int8), "layer": d["op_layer"][op].astype(np.int8),
            "op": (op + op_offset).astype(np.int32), "topo_key": keys[op],
            "fault_line": d["s_fault_line"][idx].astype(np.int16), "fault_loc": d["s_fault_loc"][idx].astype(np.int16),
            "fault_dur": d["s_fault_dur"][idx].astype(np.float32), "t240": d["s_t_delta_240"][idx].astype(np.float32),
            "first_violation": d["s_psops_label"][idx].astype(np.int8), "delta0": d["s_delta0"][idx].astype(np.float32)}


def concat(parts: list[dict]) -> dict:
    return {k: np.concatenate([p[k] for p in parts]) for k in parts[0]}


def holdout_sets(d: dict, a: dict, split_main) -> tuple[dict, list]:
    """Validation, test and held-out sets of a run trained with --holdout-topos, as train_tsa_model.py draws them."""
    ok = d["s_status"] == 0
    main_ops = np.flatnonzero((d["op_layer"] == 0) & d["op_pf_ok"])
    split = split_main(d["op_outages"], main_ops, a["split_seed"])
    rows = d["op_outages"][main_ops]
    topos = np.unique(rows, axis=0)
    n1 = [r for r in topos if (r >= 0).sum() == 1]
    pick = np.random.default_rng(a["holdout_seed"]).choice(len(n1), size=a["holdout_topos"], replace=False)
    held = [n1[i] for i in sorted(pick)]
    is_held = np.zeros(len(main_ops), dtype=bool)
    for r in held:
        is_held |= (rows == r).all(1)
    held_ops = main_ops[is_held]
    held_test_ops = split["test"][np.isin(split["test"], held_ops)]
    split = {k: v[~np.isin(v, held_ops)] for k, v in split.items()}
    sets = {name: np.flatnonzero(ok & np.isin(d["s_op"], split[name])) for name in ("val", "test")}
    sets["holdout"] = np.flatnonzero(ok & np.isin(d["s_op"], held_ops))
    sets["holdout_test"] = np.flatnonzero(ok & np.isin(d["s_op"], held_test_ops))
    return sets, [int(r[r >= 0][0]) for r in held]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--code-dir", required=True, help="directory with predict_runs.py, eval_external.py, models.py")
    p.add_argument("--dataset", required=True, help="main dataset (main layer and N-2 to N-4)")
    p.add_argument("--nk56", required=True, help="N-5 / N-6 test-only dataset")
    p.add_argument("--pred-dir", required=True, help="stored per-sample predictions <run>.npz of the main runs")
    p.add_argument("--nk56-ref", required=True, help="stored N-5 / N-6 results (eval_external.py output) of the main runs")
    p.add_argument("--main-runs", nargs="+", required=True)
    p.add_argument("--holdout-runs", nargs="*", default=[])
    p.add_argument("--network", default=None, help="network json (default: ieee39_network.json in --code-dir)")
    p.add_argument("--out-dir", required=True)
    p.add_argument("--device", default="cuda:0")
    a = p.parse_args()

    sys.path.insert(0, a.code_dir)
    from eval_external import ExternalData
    from predict_runs import Data, load_model, run_args, run_network
    from train_tsa_model import split_main

    network = json.loads(Path(a.network or Path(a.code_dir) / "ieee39_network.json").read_text())
    device = torch.device(a.device)
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    nk_ref = json.loads(Path(a.nk56_ref).read_text())["runs"]

    # ---- proposed model: validation, main test, N-2 to N-4 (main dataset), N-5 / N-6 (boundary dataset) ----
    runs = [Path(r) for r in a.main_runs]
    a0 = run_args(runs[0])
    net = run_network(a0, network)
    full = Data(Path(a.dataset), net, a0["split_seed"])
    nk = ExternalData(Path(a.nk56), net)
    keys_full, keys_nk = topo_keys(full.d["op_outages"]), topo_keys(nk.d["op_outages"])
    plan = [(name, full, full.sets[name], 0, keys_full) for name in ("val", "test", "n2", "n3", "n4")]
    plan += [(name, nk, nk.sets[name], NK56_OP_OFFSET, keys_nk) for name in ("n5", "n6")]
    meta = concat([metadata(src.d, idx, off, keys) | {"set": np.full(len(idx), SET_CODES[name], np.int8)}
                   for name, src, idx, off, keys in plan])
    probs, thrs, z0 = [], [], None
    for k, run in enumerate(runs):
        ra = run_args(run)
        assert ra["split_seed"] == a0["split_seed"] and ra["dataset"] == a0["dataset"], run
        model = load_model(run, ra, net, device)
        thr = float(json.loads((run / "results.json").read_text())["threshold_val"]["threshold"])
        stored = np.load(Path(a.pred_dir) / f"{run.name}.npz")
        assert abs(float(stored["threshold_val"]) - thr) < 1e-6, (run, float(stored["threshold_val"]), thr)
        row, zs, report = [], [], []
        for name, src, idx, _, _ in plan:
            prob, z = infer(model, src.inputs(ra, idx), device, embed=(k == 0))
            y = src.y[idx]
            if name in ("n5", "n6"):
                ref = nk_ref[run.name]["sets"][name]
                diff = abs(miss_rate(y, prob, thr) - ref["fnr"])
                assert diff < 0.02, (run.name, name, miss_rate(y, prob, thr), ref["fnr"])
                report.append(f"{name} FNR {miss_rate(y, prob, thr):.2f} (stored {ref['fnr']:.2f})")
            else:
                assert np.array_equal(stored[f"{name}_idx"], idx), (run.name, name)
                dmax = float(np.abs(stored[f"{name}_prob"] - prob).max())
                assert dmax < 1e-3, (run.name, name, dmax)
                report.append(f"{name} max|dp| {dmax:.1e}")
            row.append(prob)
            if z is not None:
                zs.append(z)
        probs.append(np.concatenate(row))
        thrs.append(thr)
        if k == 0:
            z0 = np.concatenate(zs)
        print(f"{run.name}: " + ", ".join(report), flush=True)
    np.savez_compressed(out / "scores_main.npz", prob=np.stack(probs), threshold_val=np.array(thrs, np.float32),
                        run=np.array([r.name for r in runs]), **meta)
    np.savez_compressed(out / "embed_main_s0.npz", z=z0, run=np.array(runs[0].name))
    print(f"scores_main.npz: {len(meta['label'])} samples, {len(runs)} runs; embed {z0.shape}", flush=True)

    # ---- the same model trained without five N-1 topologies ----
    if not a.holdout_runs:
        return
    hruns = [Path(r) for r in a.holdout_runs]
    h0 = run_args(hruns[0])
    sets, held_lines = holdout_sets(full.d, h0, split_main)
    names = ("val", "test", "holdout", "holdout_test")
    hmeta = concat([metadata(full.d, sets[n], 0, keys_full) | {"set": np.full(len(sets[n]), SET_CODES[n], np.int8)}
                    for n in names])
    hprobs, hthrs = [], []
    for run in hruns:
        ra = run_args(run)
        for key in ("split_seed", "holdout_seed", "holdout_topos"):
            assert ra[key] == h0[key], (run, key)
        r = json.loads((run / "results.json").read_text())
        assert sorted(held_lines) == sorted(v[0] for v in r["holdout_topologies"]), (held_lines, r["holdout_topologies"])
        model = load_model(run, ra, net, device)
        thr = float(r["threshold_val"]["threshold"])
        row, report = [], []
        for n in names:
            prob, _ = infer(model, full.inputs(ra, sets[n]), device, embed=False)
            y = full.y[sets[n]]
            ref = r["sets"][n]
            fnr = miss_rate(y, prob, thr)
            ref_fnr = ref.get("thr_val", {}).get("fnr")
            if ref_fnr is not None:
                assert abs(fnr - ref_fnr) < 0.02, (run.name, n, fnr, ref_fnr)
            report.append(f"{n} n={len(y)} FNR {fnr:.2f} (stored {ref_fnr})")
            row.append(prob)
        hprobs.append(np.concatenate(row))
        hthrs.append(thr)
        print(f"{run.name}: " + ", ".join(report), flush=True)
    np.savez_compressed(out / "scores_holdout.npz", prob=np.stack(hprobs), threshold_val=np.array(hthrs, np.float32),
                        run=np.array([r.name for r in hruns]), held_lines=np.array(held_lines, np.int16), **hmeta)
    print(f"scores_holdout.npz: {len(hmeta['label'])} samples, held-out lines {held_lines}", flush=True)


if __name__ == "__main__":
    main()

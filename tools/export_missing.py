"""Export per-sample probabilities of the proposed model with persistently missing generator PMUs.

A missing PMU delivers nothing: all channels of that generator are zero, and the angle reference is applied after
the zeroing, as in the model code's robustness evaluation (eval_robustness.py, perturbation 'missing', zero
representation). The missing sets are the first three random draws for three and five missing PMUs of that
evaluation (generator sets drawn with numpy default_rng(7)); the same generators miss for every sample. Nothing is
retrained. Each run's probabilities without missing PMUs are checked against the stored per-sample predictions, and
its miss and false-alarm rates under every missing set against the stored robustness results (where present).

Output: scores_missing.npz in --out-dir, the samples of the validation set, the main test set and N-4 in the order of
the code's evaluation sets, with prob [runs, missing sets, samples].

Example:
  python export_missing.py --code-dir CODE --pred-dir PRED --robust-ref ROBUST.json --main-runs RUN_s0 ... RUN_s4 \
      --out-dir OUT --device cuda:0
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

SETS = ("val", "test", "n4")
SET_CODES = {"val": 0, "test": 1, "n4": 4}


def missing_sets(n_gen: int) -> dict[str, list[int]]:
    """The first three draws for k = 3 and k = 5 of the robustness evaluation (same rng sequence)."""
    rng = np.random.default_rng(7)
    first = {(k, j): sorted(rng.choice(n_gen, size=k, replace=False).tolist()) for k in (1, 2, 3, 4, 5) for j in range(3)}
    return {"none": []} | {f"k{k}_d{j}": first[(k, j)] for k in (3, 5) for j in range(3)}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--code-dir", required=True)
    p.add_argument("--pred-dir", required=True, help="stored per-sample predictions <run>.npz")
    p.add_argument("--robust-ref", required=True, help="stored missing-PMU results (eval_robustness.py output)")
    p.add_argument("--main-runs", nargs="+", required=True)
    p.add_argument("--network", default=None)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--device", default="cuda:0")
    a = p.parse_args()

    sys.path.insert(0, a.code_dir)
    from eval_time_sync import build_inputs as shifted_inputs
    from eval_time_sync import window_positions
    from predict_runs import apply_reference, channel_idx, get_data, load_model, run_args, run_network
    from train_tsa_model import ensure_full_cache, metrics, predict

    network = json.loads(Path(a.network or Path(a.code_dir) / "ieee39_network.json").read_text())
    device = torch.device(a.device)
    ref = json.loads(Path(a.robust_ref).read_text())
    runs = [Path(r) for r in a.main_runs]
    cache: dict = {}
    a0 = run_args(runs[0])
    data = get_data(cache, a0, run_network(a0, network))
    scen = missing_sets(a0["n_gen"])
    for name, gens in scen.items():                       # the draws must be the ones the stored results used
        if name != "none":
            assert ref["scenarios"][f"missing_{name}"][1] == gens, (name, ref["scenarios"][f"missing_{name}"], gens)
    idx_all = {s: data.sets[s] for s in SETS}
    x_full = np.load(ensure_full_cache(data.dataset), mmap_mode="r")
    probs = np.zeros((len(runs), len(scen), sum(len(v) for v in idx_all.values())), dtype=np.float32)
    thrs = []
    for r_i, run in enumerate(runs):
        ra = run_args(run)
        net = run_network(ra, network)
        model = load_model(run, ra, net, device)
        thr = float(json.loads((run / "results.json").read_text())["threshold_val"]["threshold"])
        thrs.append(thr)
        stored = np.load(Path(a.pred_dir) / f"{run.name}.npz")
        rref = ref["runs"].get(run.name)
        report, off = [], 0
        for s in SETS:
            idx = idx_all[s]
            assert np.array_equal(stored[f"{s}_idx"], idx), (run.name, s)
            y = data.y[idx]
            xf = np.asarray(x_full[idx])
            pos = window_positions(data.d["s_fault_dur"][idx], ra["window_align"], ra["window_steps"])
            ch = channel_idx(ra)
            for c_i, (name, gens) in enumerate(scen.items()):
                if name == "none":
                    x = data.inputs(ra, idx)[0]
                else:
                    x = apply_reference(np.ascontiguousarray(shifted_inputs(xf, pos, gens, "drop", 0.0)[..., ch]), ra)
                prob = predict(model, [x], device).astype(np.float32)
                probs[r_i, c_i, off:off + len(idx)] = prob
                if name == "none":
                    d = float(np.abs(stored[f"{s}_prob"] - prob).max())
                    assert d < 1e-3, (run.name, s, d)
                    report.append(f"{s} max|dp| {d:.1e}")
                elif rref is not None and s in rref["sets"]:
                    m, st = metrics(y, prob, thr), rref["sets"][s][f"missing_{name}"]
                    assert abs(m["fnr"] - st["fnr"]) < 0.02 and abs(m["fpr"] - st["fpr"]) < 0.02, (run.name, s, name, m, st)
                    report.append(f"{s} {name} FNR {m['fnr']:.2f} (stored {st['fnr']:.2f})")
            del xf
            off += len(idx)
        print(f"{run.name}: " + ", ".join(report), flush=True)
    idx = np.concatenate([idx_all[s] for s in SETS])
    d = data.d
    op = d["s_op"][idx]
    keys = np.array(["-".join(str(int(v)) for v in sorted(r[r >= 0])) for r in d["op_outages"]])
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "scores_missing.npz", prob=probs, threshold_val=np.array(thrs, np.float32),
                        run=np.array([r.name for r in runs]), missing=np.array(list(scen)),
                        missing_gens=np.array([",".join(map(str, g)) for g in scen.values()]),
                        set=np.concatenate([np.full(len(idx_all[s]), SET_CODES[s], np.int8) for s in SETS]),
                        label=d["s_label"][idx].astype(np.int8), layer=d["op_layer"][op].astype(np.int8),
                        op=op.astype(np.int32), topo_key=keys[op], fault_line=d["s_fault_line"][idx].astype(np.int16),
                        fault_loc=d["s_fault_loc"][idx].astype(np.int16), fault_dur=d["s_fault_dur"][idx].astype(np.float32),
                        t240=d["s_t_delta_240"][idx].astype(np.float32),
                        first_violation=d["s_psops_label"][idx].astype(np.int8), delta0=d["s_delta0"][idx].astype(np.float32))
    print(f"scores_missing.npz: {probs.shape}", flush=True)


if __name__ == "__main__":
    main()

"""A1. Calibration on the main layer only, evaluated on every layer.

The alarm threshold is calibrated on unstable main-layer samples (class-conditional split conformal, scores 1 - p)
and applied unchanged to the remaining main-test points, the N-2 to N-6 layers and five N-1 topologies left out of
training. Calibration sources:
  test-half   a random half of the main-test operating points (never used for any model choice), R splits;
              exchangeability unit = operating point, all faults of a point used together
  test-half-1 the same split with one random unstable fault per calibration operating point (strict variant)
  val         the paper's validation set (also used for checkpoint selection), deterministic
Held-out N-1 topologies: the model trained without them is calibrated on its own test half / validation set.

Outputs: results/a1_main_calibration.csv (one row per seed, split, source, alpha, evaluation set),
         results/a1_summary.md
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from tsa_conformal import data as D
from tsa_conformal.conformal import alarm_threshold, one_per_cluster
from tsa_conformal.evaluate import cluster_bootstrap, false_alarm_rate, miss_rate, split_clusters

ALPHAS = (0.01, 0.02, 0.05, 0.10)


def evaluate_sets(rows: list, base: dict, p: np.ndarray, y: np.ndarray, masks: dict, t: float) -> None:
    for name, m in masks.items():
        rows.append(base | {"eval": name, "n_unstable": int((y[m] == 1).sum()), "threshold": t,
                            "miss": miss_rate(p[m], y[m], t), "false_alarm": false_alarm_rate(p[m], y[m], t)})


def run_model(sc: D.Scores, eval_sets: dict[str, int], n_splits: int, seed: int, rows: list, model: str) -> None:
    rng = np.random.default_rng(seed)
    y = sc.label
    test = sc.set == 1
    for r in range(sc.n_runs):
        p = sc.prob[r]
        # paper's validation set
        val_u = (sc.set == 0) & (y == 1)
        masks = {"main test (all)": test} | {k: sc.set == v for k, v in eval_sets.items()}
        for a in ALPHAS:
            evaluate_sets(rows, {"model": model, "seed": r, "split": -1, "cal": "val", "alpha": a}, p, y, masks,
                          alarm_threshold(p[val_u], a))
        # random halves of the main-test operating points
        for s in range(n_splits):
            cal_ops, _ = split_clusters(sc.op[test], 0.5, rng)
            cal = test & np.isin(sc.op, cal_ops)
            masks = {"main test (other half)": test & ~cal} | {k: sc.set == v for k, v in eval_sets.items()}
            strict = one_per_cluster(sc.op, cal & (y == 1), rng)
            for a in ALPHAS:
                base = {"model": model, "seed": r, "split": s, "alpha": a}
                evaluate_sets(rows, base | {"cal": "test-half"}, p, y, masks, alarm_threshold(p[cal & (y == 1)], a))
                evaluate_sets(rows, base | {"cal": "test-half-1"}, p, y, masks, alarm_threshold(p[strict], a))


def summary(df: pd.DataFrame, sc: D.Scores, n_boot: int) -> str:
    out = ["# A1. Calibration on the main layer only", ""]
    order = ["main test (other half)", "main test (all)", "N-2", "N-3", "N-4", "N-5", "N-6", "held-out N-1"]
    for a in ALPHAS:
        d = df[df.alpha == a]
        g = d.groupby(["cal", "eval"]).agg(miss=("miss", "mean"), miss_sd_seed=("miss", "std"),
                                           q05=("miss", lambda v: v.quantile(0.05)),
                                           q95=("miss", lambda v: v.quantile(0.95)),
                                           fa=("false_alarm", "mean")).reset_index()
        out += [f"## alpha = {a:.2f}", "",
                "Miss rate (%) of the unstable samples, mean over seeds (and splits); [5th, 95th percentile] over "
                "seeds x splits; false-alarm rate (%) in the last column of each source.", "",
                "| evaluation set | val | test-half | test-half-1 (strict) | false alarm, test-half |",
                "|---|---|---|---|---|"]
        for e in order:
            cells = []
            for c in ("val", "test-half", "test-half-1"):
                row = g[(g.cal == c) & (g["eval"] == e)]
                if row.empty:
                    cells.append("")
                elif c == "val":
                    cells.append(f"{100 * row.miss.iloc[0]:.2f}")
                else:
                    cells.append(f"{100 * row.miss.iloc[0]:.2f} [{100 * row.q05.iloc[0]:.2f}, {100 * row.q95.iloc[0]:.2f}]")
            fa = g[(g.cal == "test-half") & (g["eval"] == e)].fa
            if any(cells):
                out.append(f"| {e} | " + " | ".join(cells) + f" | {100 * fa.iloc[0]:.2f} |" if len(fa) else
                           f"| {e} | " + " | ".join(cells) + " | |")
        out.append("")
    # topology-bootstrap interval of the seed-mean miss rate, validation calibration, alpha = 0.02
    rng = np.random.default_rng(7)
    out += ["## Uncertainty of the layer miss rates (alpha = 0.02, validation calibration)", "",
            "Seed-mean miss rate (%) with a 95 % percentile interval from resampling whole topologies "
            f"({n_boot} resamples).", "", "| layer | miss | 95 % interval | topologies |", "|---|---|---|---|"]
    thr = [alarm_threshold(sc.prob[r][(sc.set == 0) & (sc.label == 1)], 0.02) for r in range(sc.n_runs)]
    for v in D.NK_SETS:
        m = np.flatnonzero(sc.set == v)
        y = sc.label[m]
        miss_by_seed = lambda i: np.mean([miss_rate(sc.prob[r][m][i], y[i], thr[r]) for r in range(sc.n_runs)])  # noqa: E731
        lo, hi = cluster_bootstrap(miss_by_seed, sc.topo[m], n_boot, rng)
        point = miss_by_seed(np.arange(len(m)))
        out.append(f"| {D.SET_LABELS[v]} | {100 * point:.2f} | [{100 * lo:.2f}, {100 * hi:.2f}] | "
                   f"{len(np.unique(sc.topo[m]))} |")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", type=int, default=50)
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    rows: list = []
    sc = D.load("scores_main")
    run_model(sc, {D.SET_LABELS[v]: v for v in D.NK_SETS}, a.splits, 0, rows, "proposed")
    hold = D.load("scores_holdout")
    run_model(hold, {"held-out N-1": 10}, a.splits, 1, rows, "trained without five N-1 topologies")
    df = pd.DataFrame(rows)
    D.RESULTS.mkdir(exist_ok=True)
    df.to_csv(D.RESULTS / "a1_main_calibration.csv", index=False, float_format="%.6g")
    (D.RESULTS / "a1_summary.md").write_text(summary(df, sc, a.boot))
    print((D.RESULTS / "a1_summary.md").read_text())


if __name__ == "__main__":
    main()

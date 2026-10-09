"""A4. One calibration rather than the average over calibrations.

The conformal miss-rate statement (A1, A2) is marginal: it holds on average over the draw of the calibration set,
and a single calibration ends above alpha about half the time. The calibration-conditional (PAC) threshold of
Vovk (2013) instead bounds the probability, over the calibration draw, that the miss rate exceeds alpha:
P(miss rate > alpha) <= delta. It places the threshold at the (c + 1)-th smallest calibration value, c the largest
count with P(Binomial(n, alpha) <= c) <= delta, and needs n >= log(delta) / log(1 - alpha) values (149 at
alpha = 2 %, delta = 5 %).

The binomial argument needs exchangeable calibration values. Four variants are compared:
  marginal / conditional  x  all faults of the calibration clusters (approximate: faults of a cluster are
  correlated) / one random unstable fault per calibration cluster (exact at the cluster level)
on the main layer (cluster = operating point, half of the main-test points for calibration) and on each N-k layer
(cluster = topology; half of the layer, and 150 topologies so that the one-per-topology variant is finite).

Two miss rates on the evaluation part: per case (all unstable faults pooled) and per cluster (mean over clusters of
the cluster's miss fraction), the quantity the one-per-cluster statement refers to.

Outputs: results/a4_calibration_conditional.csv, results/a4_summary.md
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from tsa_conformal import data as D
from tsa_conformal.conformal import (alarm_threshold, alarm_threshold_conditional, min_calibration_size_conditional,
                                     one_per_cluster)
from tsa_conformal.evaluate import false_alarm_rate, split_clusters

ALPHAS = (0.01, 0.02, 0.05, 0.10)
DELTA = 0.05
METHODS = ("marginal, all faults", "conditional, all faults", "marginal, one per cluster",
           "conditional, one per cluster")


def thresholds(p: np.ndarray, cal_u: np.ndarray, strict: np.ndarray, alpha: float) -> dict[str, float]:
    return {METHODS[0]: alarm_threshold(p[cal_u], alpha),
            METHODS[1]: alarm_threshold_conditional(p[cal_u], alpha, DELTA),
            METHODS[2]: alarm_threshold(p[strict], alpha),
            METHODS[3]: alarm_threshold_conditional(p[strict], alpha, DELTA)}


def evaluate(rows: list, base: dict, p: np.ndarray, y: np.ndarray, clusters: np.ndarray, test: np.ndarray,
             ts: dict[str, float], n_cal: dict[str, int]) -> None:
    tu = test & (y == 1)
    _, inv = np.unique(clusters[tu], return_inverse=True)
    counts = np.bincount(inv)
    for name, t in ts.items():
        missed = p[tu] < t
        rows.append(base | {"method": name, "n_cal": n_cal[name], "finite": bool(np.isfinite(t)), "threshold": t,
                            "miss": float(missed.mean()),
                            "miss_per_cluster": float((np.bincount(inv, weights=missed) / counts).mean()),
                            "false_alarm": false_alarm_rate(p[test], y[test], t)})


def run(p_all: np.ndarray, y: np.ndarray, clusters: np.ndarray, pool: np.ndarray, m, n_splits: int,
        rng: np.random.Generator, rows: list, base: dict) -> None:
    """Calibration on m clusters of the pool (samples where pool is true), evaluation on the pool's other clusters."""
    for r in range(p_all.shape[0]):
        p = p_all[r]
        for s in range(n_splits):
            cal_c, _ = split_clusters(clusters[pool], m, rng)
            cal = pool & np.isin(clusters, cal_c)
            cal_u = cal & (y == 1)
            strict = one_per_cluster(clusters, cal_u, rng)
            n_cal = dict(zip(METHODS, (int(cal_u.sum()),) * 2 + (len(strict),) * 2))
            for a in ALPHAS:
                evaluate(rows, base | {"seed": r, "split": s, "alpha": a, "n_cal_clusters": len(cal_c)}, p, y,
                         clusters, pool & ~cal, thresholds(p, cal_u, strict, a), n_cal)


def summary(df: pd.DataFrame) -> str:
    out = ["# A4. Calibration-conditional thresholds", "",
           f"delta = {DELTA}. Minimum number of exchangeable calibration values for a finite conditional threshold: " +
           ", ".join(f"alpha {a:.2f}: {min_calibration_size_conditional(a, DELTA)}" for a in ALPHAS) + ".", "",
           "Per row, over seeds x splits: mean miss rate (%), share of single calibrations whose miss rate exceeds "
           "alpha, per case and per cluster (target <= delta for the conditional variants), mean false-alarm rate "
           "(%), share of draws with a finite threshold. Draws without a finite threshold alarm on every case.", ""]
    for a in ALPHAS:
        d = df[df.alpha == a]
        out += [f"## alpha = {a:.2f}", "",
                "| evaluation | calibration clusters | variant | calibration values | miss | P(miss > alpha) | "
                "P(per-cluster miss > alpha) | false alarm | finite |", "|---|---|---|---|---|---|---|---|---|"]
        for (layer, m), g in d.groupby(["eval", "m"], sort=False):
            for meth in METHODS:
                x = g[g.method == meth]
                out.append(f"| {layer} | {m} (={int(x.n_cal_clusters.median())}) | {meth} | {int(x.n_cal.median())} | "
                           f"{100 * x.miss.mean():.2f} | {100 * (x.miss > a).mean():.0f} % | "
                           f"{100 * (x.miss_per_cluster > a).mean():.0f} % | {100 * x.false_alarm.mean():.1f} | "
                           f"{100 * x.finite.mean():.0f} % |")
        out.append("")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", type=int, default=50)
    a = ap.parse_args()
    sc = D.load("scores_main")
    rng = np.random.default_rng(4)
    rows: list = []
    run(sc.prob, sc.label, sc.op, sc.set == 1, 0.5, a.splits, rng, rows,
        {"eval": "main test", "cluster": "operating point", "m": "half"})
    for v in D.NK_SETS:
        for m in (0.5, 150):
            run(sc.prob, sc.label, sc.topo, sc.set == v, m, a.splits, rng, rows,
                {"eval": D.SET_LABELS[v], "cluster": "topology", "m": "half" if m == 0.5 else str(m)})
    df = pd.DataFrame(rows)
    D.RESULTS.mkdir(exist_ok=True)
    df.to_csv(D.RESULTS / "a4_calibration_conditional.csv", index=False, float_format="%.6g")
    (D.RESULTS / "a4_summary.md").write_text(summary(df))
    print((D.RESULTS / "a4_summary.md").read_text())


if __name__ == "__main__":
    main()

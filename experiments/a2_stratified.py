"""A2. Calibration stratified by N-k layer (the stratified split conformal of Alcantara & Chatzivasileiadis, 2026),
and the number of calibration topologies it needs.

For every layer N-2 to N-6 the topologies are split at random into m calibration topologies and the rest; the
alarm threshold is calibrated on the unstable samples of the calibration topologies and the miss rate is measured
on the other topologies of the same layer. The topologies of a layer are drawn at random, so they are exchangeable
at the topology level and the statement is expected to hold; its finite-sample form needs one sample per
topology (strict variant), while all samples of the calibration topologies together give an approximate one whose
spread over splits shows the cost of the clustering. With the strict variant a finite threshold at level alpha
needs at least ceil(1 / alpha) - 1 calibration topologies with an unstable sample (49 at alpha = 0.02).

B1 is the same procedure with the calibration topologies drawn from N-2 and the evaluation on N-3 to N-6.

Outputs: results/a2_stratified.csv, results/a2_summary.md
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from tsa_conformal import data as D
from tsa_conformal.conformal import alarm_threshold, min_calibration_size, one_per_cluster
from tsa_conformal.evaluate import false_alarm_rate, miss_rate, split_clusters

ALPHAS = (0.01, 0.02, 0.05, 0.10)
M_VALUES = (5, 10, 20, 50, 0.5)             # calibration topologies per layer (0.5 = half of the layer)


def m_label(m) -> str:
    return "half" if isinstance(m, float) else str(m)


def stratified(sc: D.Scores, n_splits: int, rng: np.random.Generator, rows: list) -> None:
    for v in D.NK_SETS:
        layer = np.flatnonzero(sc.set == v)
        y, topo = sc.label[layer], sc.topo[layer]
        for r in range(sc.n_runs):
            p = sc.prob[r][layer]
            for m in M_VALUES:
                for s in range(n_splits):
                    cal_t, _ = split_clusters(topo, m, rng)
                    cal = np.isin(topo, cal_t)
                    strict = one_per_cluster(topo, cal & (y == 1), rng)
                    for a in ALPHAS:
                        for name, sel in (("all samples", cal & (y == 1)), ("one per topology", strict)):
                            t = alarm_threshold(p[sel], a)
                            rows.append({"cal_layer": D.SET_LABELS[v], "eval": D.SET_LABELS[v], "seed": r,
                                         "m": m_label(m), "n_cal_topologies": len(cal_t), "split": s, "alpha": a,
                                         "variant": name, "n_cal_unstable": int(len(p[sel])),
                                         "finite": bool(np.isfinite(t)), "threshold": t,
                                         "miss": miss_rate(p[~cal], y[~cal], t),
                                         "false_alarm": false_alarm_rate(p[~cal], y[~cal], t)})


def from_n2(sc: D.Scores, n_splits: int, rng: np.random.Generator, rows: list) -> None:
    """B1: calibrate on half of the N-2 topologies, evaluate on the other N-2 half and on N-3 to N-6."""
    n2 = np.flatnonzero(sc.set == 2)
    y = sc.label
    for r in range(sc.n_runs):
        p = sc.prob[r]
        for s in range(n_splits):
            cal_t, _ = split_clusters(sc.topo[n2], 0.5, rng)
            cal = (sc.set == 2) & np.isin(sc.topo, cal_t)
            for a in ALPHAS:
                t = alarm_threshold(p[cal & (y == 1)], a)
                for v in D.NK_SETS:
                    m = (sc.set == v) & ~cal
                    rows.append({"cal_layer": "N-2", "eval": D.SET_LABELS[v], "seed": r, "m": "half",
                                 "n_cal_topologies": len(cal_t), "split": s, "alpha": a, "variant": "all samples",
                                 "n_cal_unstable": int((cal & (y == 1)).sum()), "finite": True, "threshold": t,
                                 "miss": miss_rate(p[m], y[m], t), "false_alarm": false_alarm_rate(p[m], y[m], t)})


def summary(df: pd.DataFrame) -> str:
    q = lambda f: (lambda v: v.quantile(f))  # noqa: E731
    out = ["# A2. Calibration stratified by N-k layer", "",
           f"Minimum calibration size for a finite threshold: " +
           ", ".join(f"alpha {a:.2f}: {min_calibration_size(a)}" for a in ALPHAS) + ".", ""]
    a = 0.02
    st = df[(df.cal_layer == df["eval"]) & (df.alpha == a)]
    out += [f"## Half of each layer's topologies for calibration, alpha = {a:.2f}", "",
            "Miss rate (%) on the other topologies of the layer: mean, [5th, 95th percentile] and share of "
            "seed x split draws above alpha; false-alarm rate (%).", "",
            "| layer | variant | miss | 5th-95th | P(miss > alpha) | false alarm |", "|---|---|---|---|---|---|"]
    g = st[st.m == "half"].groupby(["eval", "variant"])
    for (e, var), d in g:
        out.append(f"| {e} | {var} | {100 * d.miss.mean():.2f} | [{100 * d.miss.quantile(0.05):.2f}, "
                   f"{100 * d.miss.quantile(0.95):.2f}] | {100 * (d.miss > a).mean():.0f} % | "
                   f"{100 * d.false_alarm.mean():.2f} |")
    out += ["", f"## Data cost: miss rate against the number of calibration topologies, alpha = {a:.2f}", "",
            "All samples of the calibration topologies; mean [5th, 95th percentile] of the miss rate (%), share of "
            "draws above alpha and mean false-alarm rate (%). The strict variant needs at least 49 topologies "
            "with an unstable sample and is reported for m >= 50.", "",
            "| layer | m | miss | 5th-95th | P(miss > alpha) | false alarm | strict: miss | strict: P(> alpha) | strict: finite |",
            "|---|---|---|---|---|---|---|---|---|"]
    for e in sorted(st["eval"].unique()):
        for m in [m_label(x) for x in M_VALUES]:
            d = st[(st["eval"] == e) & (st.m == m) & (st.variant == "all samples")]
            s1 = st[(st["eval"] == e) & (st.m == m) & (st.variant == "one per topology")]
            fin = s1[s1.finite]
            strict = (f"{100 * fin.miss.mean():.2f} | {100 * (fin.miss > a).mean():.0f} % | "
                      f"{100 * s1.finite.mean():.0f} %") if len(fin) else f"- | - | {100 * s1.finite.mean():.0f} %"
            out.append(f"| {e} | {m} (={d.n_cal_topologies.iloc[0]}) | {100 * d.miss.mean():.2f} | "
                       f"[{100 * d.miss.quantile(0.05):.2f}, {100 * d.miss.quantile(0.95):.2f}] | "
                       f"{100 * (d.miss > a).mean():.0f} % | {100 * d.false_alarm.mean():.2f} | {strict} |")
    b1 = df[(df.cal_layer == "N-2") & (df.alpha == a) & (df.m == "half") & (df.variant == "all samples")]
    out += ["", f"## B1. Calibration on half of the N-2 topologies only, alpha = {a:.2f}", "",
            "| evaluation layer | miss | 5th-95th | P(miss > alpha) | false alarm |", "|---|---|---|---|---|"]
    for e, d in b1[b1.index.isin(b1.index)].groupby("eval"):
        if e == "N-2":
            continue
        out.append(f"| {e} | {100 * d.miss.mean():.2f} | [{100 * d.miss.quantile(0.05):.2f}, "
                   f"{100 * d.miss.quantile(0.95):.2f}] | {100 * (d.miss > a).mean():.0f} % | "
                   f"{100 * d.false_alarm.mean():.2f} |")
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", type=int, default=50)
    a = ap.parse_args()
    sc = D.load("scores_main")
    rng = np.random.default_rng(2)
    rows: list = []
    stratified(sc, a.splits, rng, rows)
    b1: list = []
    from_n2(sc, a.splits, rng, b1)
    df = pd.concat([pd.DataFrame(rows), pd.DataFrame(b1)], ignore_index=True)
    D.RESULTS.mkdir(exist_ok=True)
    df.to_csv(D.RESULTS / "a2_stratified.csv", index=False, float_format="%.6g")
    (D.RESULTS / "a2_summary.md").write_text(summary(df))
    print((D.RESULTS / "a2_summary.md").read_text())


if __name__ == "__main__":
    main()

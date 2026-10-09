"""B2. Missing PMUs as a second kind of shift.

Six persistent PMU losses of the model's robustness evaluation: three sets of three and three sets of five missing
generator PMUs (zero-filled, the same generators for every case), five seeds, data/scores_missing.npz. Calibration
on a random half of the main-test operating points (R splits per seed), evaluated on the other half (missing PMUs
only) and on N-4 (missing PMUs and topology shift):
  as deployed    the alarm threshold calibrated without missing PMUs, applied unchanged
  recalibrated   the alarm threshold calibrated under the same missing PMUs (the conformal counterpart of the paper's
                 threshold re-selected on the validation set, which is also reported: 'validation, recalibrated')
  two-sided      both class thresholds calibrated under the same missing PMUs; {S,U} is referred to simulation
  N-4 own layer  half of the N-4 topologies under the same missing PMUs calibrate the N-4 threshold (both shifts
                 covered by the calibration data)

Outputs: results/b2_missing_pmu.csv, results/b2_summary.md
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from tsa_conformal import data as D
from tsa_conformal.conformal import alarm_threshold, prediction_sets, stable_threshold
from tsa_conformal.evaluate import false_alarm_rate, miss_rate, set_rates, split_clusters

ALPHAS = (0.02, 0.05)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", type=int, default=20)
    a = ap.parse_args()
    z = np.load(D.DATA / "scores_missing.npz")
    prob, missing, gens = z["prob"], list(z["missing"]), list(z["missing_gens"])
    y, st, op = z["label"], z["set"], z["op"]
    _, topo = np.unique(z["topo_key"], return_inverse=True)
    val, test, n4 = st == 0, st == 1, st == 4
    rng = np.random.default_rng(6)
    rows: list = []

    def add(base: dict, p: np.ndarray, m: np.ndarray, t: float) -> None:
        rows.append(base | {"miss": miss_rate(p[m], y[m], t), "false_alarm": false_alarm_rate(p[m], y[m], t),
                            "threshold": t})

    for r in range(prob.shape[0]):
        p0 = prob[r, 0]
        for c, name in enumerate(missing):
            p = prob[r, c]
            for al in ALPHAS:
                b = {"seed": r, "missing": name, "generators": gens[c], "alpha": al, "split": -1}
                t_val = alarm_threshold(p[val & (y == 1)], al)
                add(b | {"method": "validation, recalibrated", "eval": "main test"}, p, test, t_val)
                add(b | {"method": "validation, recalibrated", "eval": "N-4"}, p, n4, t_val)
        for s in range(a.splits):
            cal_ops, _ = split_clusters(op[test], 0.5, rng)
            cal = test & np.isin(op, cal_ops)
            other = test & ~cal
            cal_t, _ = split_clusters(topo[n4], 0.5, rng)
            n4_cal = n4 & np.isin(topo, cal_t)
            n4_other = n4 & ~n4_cal
            for c, name in enumerate(missing):
                p = prob[r, c]
                for al in ALPHAS:
                    b = {"seed": r, "missing": name, "generators": gens[c], "alpha": al, "split": s}
                    t_dep = alarm_threshold(p0[cal & (y == 1)], al)
                    t_rec = alarm_threshold(p[cal & (y == 1)], al)
                    t_s = stable_threshold(p[cal & (y == 0)], al)
                    for ev, m in (("main test", other), ("N-4", n4)):
                        add(b | {"method": "as deployed", "eval": ev}, p, m, t_dep)
                        add(b | {"method": "recalibrated", "eval": ev}, p, m, t_rec)
                        sets = prediction_sets(p[m], t_rec, t_s)
                        rows.append(b | {"method": "two-sided, recalibrated", "eval": ev, "threshold": t_rec,
                                         "t_stable": t_s} | set_rates(sets, y[m]))
                    t_n4 = alarm_threshold(p[n4_cal & (y == 1)], al)
                    add(b | {"method": "N-4 own layer, recalibrated", "eval": "N-4 (other half)"}, p, n4_other, t_n4)
                    t_n4s = stable_threshold(p[n4_cal & (y == 0)], al)
                    rows.append(b | {"method": "two-sided, N-4 own layer", "eval": "N-4 (other half)", "threshold": t_n4,
                                     "t_stable": t_n4s} | set_rates(prediction_sets(p[n4_other], t_n4, t_n4s), y[n4_other]))
    df = pd.DataFrame(rows)
    D.RESULTS.mkdir(exist_ok=True)
    df.to_csv(D.RESULTS / "b2_missing_pmu.csv", index=False, float_format="%.6g")
    (D.RESULTS / "b2_summary.md").write_text(summary(df, missing, gens))
    print((D.RESULTS / "b2_summary.md").read_text())


def summary(df: pd.DataFrame, missing: list, gens: list) -> str:
    def cell(x: pd.DataFrame, col: str) -> str:
        return f"{100 * x[col].mean():.2f}" if len(x) else ""

    out = ["# B2. Missing PMUs", "",
           "Five seeds; random halves of the main-test operating points (and of the N-4 topologies for the own-layer "
           "rows); means over seeds x splits, %. Missing sets: " +
           ", ".join(f"{m} = generators {{{g}}}" for m, g in zip(missing[1:], gens[1:])) + ".", ""]
    for al in ALPHAS:
        d = df[df.alpha == al]
        out += [f"## alpha = {al:.2f}: one-sided alarm threshold", "",
                "| missing | main: miss, as deployed | main: miss, recalibrated | main: false alarm, recalibrated | "
                "N-4: miss, as deployed | N-4: miss, recalibrated on main | N-4: false alarm, recalibrated on main | "
                "N-4: miss, own layer | N-4: false alarm, own layer | validation recalibration: N-4 miss / false alarm |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for m in missing:
            x = d[d.missing == m]
            g = lambda meth, ev: x[(x.method == meth) & (x["eval"] == ev)]  # noqa: E731
            v = g("validation, recalibrated", "N-4")
            out.append(f"| {m} | {cell(g('as deployed', 'main test'), 'miss')} | {cell(g('recalibrated', 'main test'), 'miss')} | "
                       f"{cell(g('recalibrated', 'main test'), 'false_alarm')} | {cell(g('as deployed', 'N-4'), 'miss')} | "
                       f"{cell(g('recalibrated', 'N-4'), 'miss')} | {cell(g('recalibrated', 'N-4'), 'false_alarm')} | "
                       f"{cell(g('N-4 own layer, recalibrated', 'N-4 (other half)'), 'miss')} | "
                       f"{cell(g('N-4 own layer, recalibrated', 'N-4 (other half)'), 'false_alarm')} | "
                       f"{cell(v, 'miss')} / {cell(v, 'false_alarm')} |")
        out += ["", f"## alpha = {al:.2f}: two-sided sets, recalibrated under the same missing PMUs", "",
                "miss = P(declared stable | unstable); false alarm = P({U} or {} | stable); refer = P({S,U}).", "",
                "| missing | main: miss | main: false alarm | main: refer | N-4 (main calibration): miss | false alarm | refer | "
                "N-4 (own layer): miss | false alarm | refer |", "|---|---|---|---|---|---|---|---|---|---|"]
        for m in missing:
            x = d[d.missing == m]
            g = lambda meth, ev: x[(x.method == meth) & (x["eval"] == ev)]  # noqa: E731
            a1, a2, a3 = g("two-sided, recalibrated", "main test"), g("two-sided, recalibrated", "N-4"), \
                g("two-sided, N-4 own layer", "N-4 (other half)")
            out.append(f"| {m} | {cell(a1, 'miss')} | {cell(a1, 'false_alarm')} | {cell(a1, 'refer')} | "
                       f"{cell(a2, 'miss')} | {cell(a2, 'false_alarm')} | {cell(a2, 'refer')} | "
                       f"{cell(a3, 'miss')} | {cell(a3, 'false_alarm')} | {cell(a3, 'refer')} |")
        out.append("")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    main()

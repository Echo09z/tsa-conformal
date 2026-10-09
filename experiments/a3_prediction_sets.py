"""A3. Two-sided prediction sets and referral to time-domain simulation.

Each class gets its own conformal threshold at the same alpha: U enters the set when p >= t_U (calibrated on
unstable samples), S when p <= t_S (calibrated on stable samples). The set is read as an operating decision:
{S} declared stable, {U} alarm, {S,U} referred to time-domain simulation, {} treated as an alarm.

Calibration:
  main        a random half of the main-test operating points; evaluation on the other half, N-2 to N-6 and the
              held-out N-1 topologies (model trained without them, calibrated on its own test half)
  stratified  per layer, a random half of its topologies; evaluation on the other half

Which unstable samples end where (alpha = 0.02): lead time from the decision to the 240-degree crossing, and the
share whose first violated simulator criterion is the voltage one.

Outputs: results/a3_prediction_sets.csv, results/a3_outcomes_by_lead.csv, results/a3_summary.md
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from tsa_conformal import data as D
from tsa_conformal.conformal import SET_EMPTY, SET_S, SET_SU, SET_U, alarm_threshold, prediction_sets, stable_threshold
from tsa_conformal.evaluate import set_rates, split_clusters

ALPHAS = (0.01, 0.02, 0.05, 0.10)
LEAD_BINS = [(-np.inf, 0.0, "crossed in window"), (0.0, 0.5, "0-0.5 s"), (0.5, 1.0, "0.5-1 s"),
             (1.0, 3.0, "1-3 s"), (3.0, np.inf, "> 3 s")]
OUTCOME = {SET_S: "missed", SET_SU: "referred", SET_U: "alarm", SET_EMPTY: "alarm"}


def record(rows: list, outcomes: list, base: dict, sets: np.ndarray, y: np.ndarray, lead: np.ndarray,
           volt: np.ndarray) -> None:
    rows.append(base | {"n": len(y), "n_unstable": int((y == 1).sum())} | set_rates(sets, y))
    if base["alpha"] != 0.02:
        return
    u = y == 1
    for lo, hi, name in LEAD_BINS:
        b = u & (lead > lo) & (lead <= hi)
        for code in (SET_S, SET_SU, SET_U, SET_EMPTY):
            k = b & (sets == code)
            outcomes.append(base | {"lead_bin": name, "outcome": OUTCOME[code], "n": int(k.sum()),
                                    "n_voltage_first": int((k & volt).sum())})


def main_calibration(sc: D.Scores, eval_sets: dict, n_splits: int, rng, rows: list, outcomes: list, model: str) -> None:
    y, test, lead, volt = sc.label, sc.set == 1, sc.lead_time(), sc.voltage_first()
    for r in range(sc.n_runs):
        p = sc.prob[r]
        for s in range(n_splits):
            cal_ops, _ = split_clusters(sc.op[test], 0.5, rng)
            cal = test & np.isin(sc.op, cal_ops)
            masks = {"main test (other half)": test & ~cal} | {k: sc.set == v for k, v in eval_sets.items()}
            for a in ALPHAS:
                t_u, t_s = alarm_threshold(p[cal & (y == 1)], a), stable_threshold(p[cal & (y == 0)], a)
                for name, m in masks.items():
                    record(rows, outcomes, {"model": model, "cal": "main", "eval": name, "seed": r, "split": s,
                                            "alpha": a, "t_alarm": t_u, "t_stable": t_s},
                           prediction_sets(p[m], t_u, t_s), y[m], lead[m], volt[m])


def stratified(sc: D.Scores, n_splits: int, rng, rows: list, outcomes: list) -> None:
    lead, volt = sc.lead_time(), sc.voltage_first()
    for v in D.NK_SETS:
        layer = np.flatnonzero(sc.set == v)
        y, topo, ld, vf = sc.label[layer], sc.topo[layer], lead[layer], volt[layer]
        for r in range(sc.n_runs):
            p = sc.prob[r][layer]
            for s in range(n_splits):
                cal_t, _ = split_clusters(topo, 0.5, rng)
                cal = np.isin(topo, cal_t)
                for a in ALPHAS:
                    t_u, t_s = alarm_threshold(p[cal & (y == 1)], a), stable_threshold(p[cal & (y == 0)], a)
                    record(rows, outcomes, {"model": "proposed", "cal": "stratified", "eval": D.SET_LABELS[v],
                                            "seed": r, "split": s, "alpha": a, "t_alarm": t_u, "t_stable": t_s},
                           prediction_sets(p[~cal], t_u, t_s), y[~cal], ld[~cal], vf[~cal])


def summary(df: pd.DataFrame, oc: pd.DataFrame) -> str:
    order = ["main test (other half)", "held-out N-1", "N-2", "N-3", "N-4", "N-5", "N-6"]
    out = ["# A3. Two-sided prediction sets and referral to simulation", ""]
    for a in (0.02, 0.05):
        d = df[df.alpha == a]
        out += [f"## alpha = {a:.2f} for both classes", "",
                "Means over seeds x splits, %. miss = P(declared stable | unstable); false omission = "
                "P(unstable | declared stable); refer = P({S,U}); refer | U = P({S,U} | unstable); "
                "alarm | S = P({U} or {} | stable); empty = P({}).", "",
                "| calibration | evaluation | miss | false omission | refer | refer, unstable | false alarm | empty | t_U | t_S |",
                "|---|---|---|---|---|---|---|---|---|---|"]
        for cal in ("main", "stratified"):
            for e in order:
                x = d[(d.cal == cal) & (d["eval"] == e)]
                if x.empty:
                    continue
                out.append(f"| {cal} | {e} | {100 * x.miss.mean():.2f} | {100 * x.false_omission.mean():.2f} | "
                           f"{100 * x.refer.mean():.2f} | {100 * x.refer_unstable.mean():.2f} | "
                           f"{100 * x.false_alarm.mean():.2f} | {100 * x['empty'].mean():.2f} | "
                           f"{x.t_alarm.mean():.3f} | {x.t_stable.mean():.3f} |")
        out.append("")
    out += ["## Where the unstable samples end, alpha = 0.02", "",
            "Unstable samples per draw (seed x split) in each lead-time bin, and the share (%) that is missed / "
            "referred / alarmed, pooled over draws; last column: share of voltage-first cases among the missed ones.", ""]
    for cal, e in (("main", "main test (other half)"), ("main", "N-4"), ("stratified", "N-4")):
        x = oc[(oc.cal == cal) & (oc["eval"] == e)]
        tot = x.groupby("lead_bin").n.sum()
        n_draws = len(x[["seed", "split"]].drop_duplicates())
        out += [f"### {cal} calibration, {e}", "", "| lead time | unstable per draw | missed | referred | alarm | voltage-first among missed |",
                "|---|---|---|---|---|---|"]
        for _, _, b in LEAD_BINS:
            xb = x[x.lead_bin == b]
            n = tot.get(b, 0)
            if n == 0:
                continue
            share = lambda o: 100 * xb[xb.outcome == o].n.sum() / n  # noqa: E731
            missed = xb[xb.outcome == "missed"]
            vf = 100 * missed.n_voltage_first.sum() / missed.n.sum() if missed.n.sum() else float("nan")
            out.append(f"| {b} | {n / n_draws:.0f} | {share('missed'):.1f} | {share('referred'):.1f} | {share('alarm'):.1f} | {vf:.0f} |")
        allm = x[x.outcome == "missed"]
        allu = x
        out += ["", f"Voltage-first share: {100 * allm.n_voltage_first.sum() / max(allm.n.sum(), 1):.0f} % of the missed, "
                f"{100 * allu.n_voltage_first.sum() / max(allu.n.sum(), 1):.0f} % of all unstable samples.", ""]
    return "\n".join(out) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", type=int, default=20)
    a = ap.parse_args()
    rng = np.random.default_rng(3)
    rows: list = []
    outcomes: list = []
    sc = D.load("scores_main")
    main_calibration(sc, {D.SET_LABELS[v]: v for v in D.NK_SETS}, a.splits, rng, rows, outcomes, "proposed")
    main_calibration(D.load("scores_holdout"), {"held-out N-1": 10}, a.splits, rng, rows, outcomes,
                     "trained without five N-1 topologies")
    stratified(sc, a.splits, rng, rows, outcomes)
    df, oc = pd.DataFrame(rows), pd.DataFrame(outcomes)
    # the held-out model's own main-test half is reported under its model name only
    df = df[~((df.model != "proposed") & (df["eval"] == "main test (other half)"))]
    oc = oc[~((oc.model != "proposed") & (oc["eval"] == "main test (other half)"))]
    D.RESULTS.mkdir(exist_ok=True)
    df.to_csv(D.RESULTS / "a3_prediction_sets.csv", index=False, float_format="%.6g")
    oc.to_csv(D.RESULTS / "a3_outcomes_by_lead.csv", index=False)
    (D.RESULTS / "a3_summary.md").write_text(summary(df, oc))
    print((D.RESULTS / "a3_summary.md").read_text())


if __name__ == "__main__":
    main()

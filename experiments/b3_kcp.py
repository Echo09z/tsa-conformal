"""B3. Kernel-weighted conformal prediction (KCP) instead of one threshold per layer.

KCP (src/tsa_conformal/kcp.py, after Alcantara & Chatzivasileiadis, v2) localizes the alarm threshold of every test
case to the unstable calibration cases near it. Two representations:
  embedding  the model's mean-pooled token embedding (first 32 principal components, seed 0): available online
             from the PMU responses alone, as the source suggests for a foundation model's latent space
  topology   the outage indicator vector of the post-fault network: needs the topology, like own-layer calibration
Two calibration pools:
  main layer  unstable cases of a random half of the main-test operating points; evaluation on the other half and
              on the whole N-2 to N-6 layers (A1 setting)
  pooled      the same main-layer half plus a random half of the topologies of every N-k layer, without layer
              labels; evaluation on the other halves. Reference: one threshold per layer (A2), which uses the labels

A rule that alarms on more cases misses fewer, so every result is compared with one threshold set on the evaluation
cases themselves to give the same miss rate (reference only, it uses the test labels): the false-alarm rate a
single threshold needs for the same miss rate. A second reference is one threshold shared by all sets, placed so
that it misses as many N-4 cases as the method does. The embedding kernel is also run with larger k_nn, which the
source notes may need tuning.

Seed 0 only (the embedding was exported for one seed); R random splits; up to N_SUB unstable and N_SUB stable cases
per evaluation set.

Outputs: results/b3_kcp.csv, results/b3_summary.md
"""
from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from tsa_conformal import data as D
from tsa_conformal.conformal import alarm_threshold
from tsa_conformal.evaluate import split_clusters
from tsa_conformal.kcp import kcp_alarm_thresholds, outage_features

ALPHAS = (0.02, 0.05, 0.10)
KNN_SWEEP = (100, 500, 2000)              # embedding kernel, main-layer calibration
N_SUB = 4000
SEED = 0
LATE_S = 1.0


def reference_false_alarm(p_u: np.ndarray, p_s: np.ndarray, miss: float) -> float:
    """False-alarm rate of one threshold on these cases that misses the same share of the unstable ones."""
    pu = np.sort(p_u)
    t = pu[min(int(np.floor(miss * len(pu) + 1e-9)), len(pu) - 1)]
    return float((p_s >= t).mean())


def subsample(idx: np.ndarray, y: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    out = []
    for c in (1, 0):
        k = idx[y[idx] == c]
        out.append(k if len(k) <= N_SUB else rng.choice(k, N_SUB, replace=False))
    return np.sort(np.concatenate(out))


def score(rows: list, base: dict, t: np.ndarray, idx: np.ndarray, p: np.ndarray, y: np.ndarray, late: np.ndarray,
          n_eff: np.ndarray | None) -> None:
    u, s = y[idx] == 1, y[idx] == 0
    pi = p[idx]
    for a_i, a in enumerate(ALPHAS):
        ta = t[:, a_i] if t.ndim == 2 else np.full(len(idx), t[a_i])
        missed = pi < ta
        miss = float(missed[u].mean())
        rows.append(base | {"alpha": a, "n_unstable": int(u.sum()), "n_stable": int(s.sum()), "miss": miss,
                            "miss_late": float(missed[u & late[idx]].mean()),
                            "false_alarm": float((~missed)[s].mean()),
                            "reference_false_alarm": reference_false_alarm(pi[u], pi[s], miss),
                            "fallback": float((n_eff < 5).mean()) if n_eff is not None else float("nan"),
                            "n_eff_median": float(np.median(n_eff)) if n_eff is not None else float("nan")})


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--splits", type=int, default=5)
    a = ap.parse_args()
    sc = D.load("scores_main")
    p, y = sc.prob[SEED], sc.label
    late = np.nan_to_num(sc.lead_time(), nan=-np.inf) > LATE_S
    reps = {"embedding": np.load(D.DATA / "embed_pca32_s0.npz")["z"].astype(np.float32),
            "topology": outage_features(sc.topo_keys)[sc.topo]}
    rng = np.random.default_rng(5)
    test = sc.set == 1
    rows: list = []
    for s in range(a.splits):
        cal_ops, _ = split_clusters(sc.op[test], 0.5, rng)
        cal_main = test & np.isin(sc.op, cal_ops)
        own = {"main test": cal_main & (y == 1)}
        evals_main = {"main test": test & ~cal_main} | {D.SET_LABELS[v]: sc.set == v for v in D.NK_SETS}
        evals_pool = {"main test": test & ~cal_main}
        pooled = cal_main & (y == 1)
        for v in D.NK_SETS:
            layer = sc.set == v
            cal_t, _ = split_clusters(sc.topo[layer], 0.5, rng)
            cal = layer & np.isin(sc.topo, cal_t)
            own[D.SET_LABELS[v]] = cal & (y == 1)
            evals_pool[D.SET_LABELS[v]] = layer & ~cal
            pooled |= cal & (y == 1)
        for setting, cal_u, evals in (("main layer", cal_main & (y == 1), evals_main), ("pooled", pooled, evals_pool)):
            cu = np.flatnonzero(cal_u)
            one = np.array([alarm_threshold(p[cu], al) for al in ALPHAS])
            for name, m in evals.items():
                idx = subsample(np.flatnonzero(m), y, rng)
                base = {"setting": setting, "eval": name, "split": s}
                score(rows, base | {"method": "one threshold"}, one, idx, p, y, late, None)
                if setting == "pooled":
                    own_t = np.array([alarm_threshold(p[own[name]], al) for al in ALPHAS])
                    score(rows, base | {"method": "one threshold per layer (labels)"}, own_t, idx, p, y, late, None)
                for rep, z in reps.items():
                    t, n_eff = kcp_alarm_thresholds(z[idx], z[cu], p[cu], ALPHAS)
                    score(rows, base | {"method": f"KCP, {rep}"}, t, idx, p, y, late, n_eff)
                if setting == "main layer":
                    for k in KNN_SWEEP:
                        t, n_eff = kcp_alarm_thresholds(reps["embedding"][idx], reps["embedding"][cu], p[cu], ALPHAS, k_nn=k)
                        score(rows, base | {"method": f"KCP, embedding, k_nn = {k}"}, t, idx, p, y, late, n_eff)
            print(f"split {s} {setting} done", flush=True)
    df = pd.DataFrame(rows)
    D.RESULTS.mkdir(exist_ok=True)
    df.to_csv(D.RESULTS / "b3_kcp.csv", index=False, float_format="%.6g")
    (D.RESULTS / "b3_summary.md").write_text(summary(df, a.splits) + shared_threshold_reference(df, sc))
    print((D.RESULTS / "b3_summary.md").read_text())


def summary(df: pd.DataFrame, n_splits: int) -> str:
    order = ["main test", "N-2", "N-3", "N-4", "N-5", "N-6"]
    out = ["# B3. Kernel-weighted conformal prediction", "",
           f"Seed {SEED}, {n_splits} random splits, up to {N_SUB} unstable and {N_SUB} stable cases per evaluation set. "
           "Each cell: miss % / false alarm % (false alarm % of one threshold set on the same cases for the same "
           "miss rate; reference only). k_nn = 20, n_eff_min = 5 as in the source.", ""]
    for a in (0.02, 0.05):
        d = df[df.alpha == a]
        out += [f"## alpha = {a:.2f}", "", "| calibration | method | " + " | ".join(order) + " |",
                "|---|---|" + "---|" * len(order)]
        for (setting, meth), g in d.groupby(["setting", "method"], sort=False):
            cells = []
            for e in order:
                x = g[g["eval"] == e]
                cells.append(f"{100 * x.miss.mean():.2f} / {100 * x.false_alarm.mean():.1f} "
                             f"({100 * x.reference_false_alarm.mean():.1f})" if len(x) else "")
            out.append(f"| {setting} | {meth} | " + " | ".join(cells) + " |")
        out.append("")
    d = df[(df.alpha == 0.02) & (df["eval"] == "N-4")]
    out += ["## N-4 in detail, alpha = 0.02", "",
            f"Late = unstable cases crossing 240 degrees more than {LATE_S:.0f} s after the decision.", "",
            "| calibration | method | miss | miss, late | false alarm | reference false alarm | fallback | median n_eff |",
            "|---|---|---|---|---|---|---|---|"]
    for (setting, meth), g in d.groupby(["setting", "method"], sort=False):
        out.append(f"| {setting} | {meth} | {100 * g.miss.mean():.2f} | {100 * g.miss_late.mean():.2f} | "
                   f"{100 * g.false_alarm.mean():.1f} | {100 * g.reference_false_alarm.mean():.1f} | "
                   f"{100 * g.fallback.mean():.1f} % | {g.n_eff_median.mean():.0f} |")
    return "\n".join(out) + "\n"


def shared_threshold_reference(df: pd.DataFrame, sc: D.Scores) -> str:
    """One threshold for every set, placed to miss the method's mean N-4 miss rate on all N-4 cases (reference)."""
    p, y = sc.prob[SEED], sc.label
    n4u = np.sort(p[(sc.set == 4) & (y == 1)])
    d = df[(df.alpha == 0.02) & (df.setting == "main layer")]
    out = ["", "## One shared threshold at the same N-4 miss rate, alpha = 0.02, main-layer calibration", "",
           "For each method: its mean miss / false alarm (%) on the main test and N-4, then the same two sets under one "
           "threshold shared by all sets and placed on all N-4 cases to give the method's N-4 miss rate (reference, "
           "uses the N-4 labels).", "",
           "| method | main test | N-4 | shared threshold | main test, shared | N-4, shared |", "|---|---|---|---|---|---|"]
    for meth, g in d.groupby("method", sort=False):
        mt, n4 = g[g["eval"] == "main test"], g[g["eval"] == "N-4"]
        t = n4u[int(np.floor(n4.miss.mean() * len(n4u)))]
        cell = lambda v: f"{100 * (p[(sc.set == v) & (y == 1)] < t).mean():.2f} / {100 * (p[(sc.set == v) & (y == 0)] >= t).mean():.1f}"  # noqa: E731
        out.append(f"| {meth} | {100 * mt.miss.mean():.2f} / {100 * mt.false_alarm.mean():.1f} | "
                   f"{100 * n4.miss.mean():.2f} / {100 * n4.false_alarm.mean():.1f} | {t:.3f} | {cell(1)} | {cell(4)} |")
    return "\n".join(out) + "\n"


if __name__ == "__main__":
    main()

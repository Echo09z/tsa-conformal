"""Rates on an evaluation set, cluster splits and cluster bootstrap."""
from __future__ import annotations

import numpy as np

from .conformal import SET_EMPTY, SET_S, SET_SU, SET_U


def miss_rate(p: np.ndarray, y: np.ndarray, t_alarm: float) -> float:
    """Share of unstable samples that are not alarmed (p < t_alarm)."""
    u = y == 1
    return float((p[u] < t_alarm).mean()) if u.any() else float("nan")


def false_alarm_rate(p: np.ndarray, y: np.ndarray, t_alarm: float) -> float:
    s = y == 0
    return float((p[s] >= t_alarm).mean()) if s.any() else float("nan")


def set_rates(sets: np.ndarray, y: np.ndarray) -> dict[str, float]:
    """Operational reading of the prediction sets: {S} = declared stable, {U} and {} = alarm, {S,U} = refer to
    time-domain simulation.

    miss            P(declared stable | unstable): the rate the unstable-class calibration bounds by alpha
    false_omission  P(unstable | declared stable): how trustworthy a 'stable' declaration is
    refer           P(referred), all samples
    false_alarm     P(alarm | stable)
    refer_unstable  P(referred | unstable): the unstable samples that simulation would have to resolve
    """
    u, s = y == 1, y == 0
    declared_stable = sets == SET_S
    alarm = (sets == SET_U) | (sets == SET_EMPTY)
    refer = sets == SET_SU
    return {
        "miss": float(declared_stable[u].mean()) if u.any() else float("nan"),
        "false_omission": float(u[declared_stable].mean()) if declared_stable.any() else float("nan"),
        "refer": float(refer.mean()),
        "false_alarm": float(alarm[s].mean()) if s.any() else float("nan"),
        "refer_unstable": float(refer[u].mean()) if u.any() else float("nan"),
        "empty": float((sets == SET_EMPTY).mean()),
    }


def split_clusters(clusters: np.ndarray, n_cal: int | float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Random calibration / test split of the unique cluster ids; n_cal is a count (int) or a fraction (float)."""
    ids = rng.permutation(np.unique(clusters))
    m = int(round(n_cal * len(ids))) if isinstance(n_cal, float) else int(n_cal)
    if not 0 < m < len(ids):
        raise ValueError(f"cannot put {m} of {len(ids)} clusters into calibration")
    return np.sort(ids[:m]), np.sort(ids[m:])


def cluster_bootstrap(stat, clusters: np.ndarray, n_boot: int, rng: np.random.Generator,
                      level: float = 0.95) -> tuple[float, float]:
    """Percentile interval of stat(sample_indices) under resampling of whole clusters with replacement."""
    ids, inv = np.unique(clusters, return_inverse=True)
    members = np.split(np.argsort(inv, kind="stable"), np.cumsum(np.bincount(inv))[:-1])
    vals = []
    for _ in range(n_boot):
        pick = rng.integers(0, len(ids), len(ids))
        vals.append(stat(np.concatenate([members[i] for i in pick])))
    lo, hi = np.nanpercentile(vals, [50 * (1 - level), 50 * (1 + level)])
    return float(lo), float(hi)


__all__ = ["miss_rate", "false_alarm_rate", "set_rates", "split_clusters", "cluster_bootstrap",
           "SET_S", "SET_U", "SET_SU", "SET_EMPTY"]

"""Kernel-weighted conformal prediction (KCP) on the unstable class.

After Alcantara & Chatzivasileiadis (arXiv:2602.07995, v2, Sec. II-B), transferred from regression residuals to the
class-conditional alarm threshold of conformal.py: for a test case with representation z, every unstable
calibration case j gets the weight

    w_j = exp(-d_j^2 / h^2) / sum_i exp(-d_i^2 / h^2),   d_j = ||z - z_j||,   h^2 = d^2 of the k_nn-th nearest case,

and the alarm threshold is the weighted quantile of the calibration probabilities: the largest t such that the
calibration weight of the unstable cases with p < t stays below alpha. When the effective sample size
n_eff = 1 / sum_j w_j^2 falls below n_eff_min, the uniform-weight threshold of the whole calibration set is used
(alarm_threshold). As in the source, the weights are normalized over the calibration cases only; the test case
itself carries no weight, so the statement is approximate.
"""
from __future__ import annotations

import numpy as np

from .conformal import alarm_threshold


def kcp_alarm_thresholds(z_test: np.ndarray, z_cal: np.ndarray, p_cal: np.ndarray, alphas: tuple[float, ...],
                         k_nn: int = 20, n_eff_min: float = 5.0, block: int = 256) -> tuple[np.ndarray, np.ndarray]:
    """Alarm thresholds [n_test, len(alphas)] and effective sample sizes [n_test].

    z_cal, p_cal: representations and predicted probabilities of the unstable calibration cases."""
    order = np.argsort(-np.asarray(p_cal, dtype=np.float64), kind="stable")   # descending p = ascending score 1 - p
    p_desc = np.asarray(p_cal, dtype=np.float64)[order]
    zc = np.asarray(z_cal, dtype=np.float32)[order]
    zc2 = (zc.astype(np.float64) ** 2).sum(1)
    n = len(p_desc)
    if n == 0:
        raise ValueError("empty calibration set")
    k = min(k_nn, n)
    fallback = np.array([alarm_threshold(p_desc, a) for a in alphas])
    out = np.empty((len(z_test), len(alphas)))
    n_eff = np.empty(len(z_test))
    for i in range(0, len(z_test), block):
        zt = np.asarray(z_test[i:i + block], dtype=np.float32)
        d2 = (zt.astype(np.float64) ** 2).sum(1)[:, None] + zc2[None] - 2.0 * (zt @ zc.T)
        np.maximum(d2, 0.0, out=d2)
        # h -> 0 (k_nn cases at distance zero) gives uniform weight over the exact matches
        h2 = np.maximum(np.partition(d2, k - 1, axis=1)[:, k - 1], 1e-12)
        w = np.exp(-d2 / h2[:, None])
        w /= w.sum(1, keepdims=True)
        ne = 1.0 / (w ** 2).sum(1)
        cw = np.cumsum(w, axis=1)
        for a_i, a in enumerate(alphas):
            idx = np.minimum((cw < 1.0 - a - 1e-12).sum(1), n - 1)
            t = p_desc[idx]
            out[i:i + block, a_i] = np.where(ne < n_eff_min, fallback[a_i], t)
        n_eff[i:i + block] = ne
    return out, n_eff


def outage_features(topo_keys: np.ndarray, n_lines: int = 33) -> np.ndarray:
    """Outage indicator vector (one column per line 1..n_lines) of each topology key ('3-17', '' = intact)."""
    f = np.zeros((len(topo_keys), n_lines), dtype=np.float32)
    for r, key in enumerate(topo_keys):
        for v in filter(None, str(key).split("-")):
            f[r, int(v) - 1] = 1.0
    return f

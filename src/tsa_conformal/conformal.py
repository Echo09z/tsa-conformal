"""Class-conditional (Mondrian) split conformal calibration for a binary stability classifier.

Model-agnostic: everything here takes predicted probabilities of instability p and labels y (1 = unstable) only.

Nonconformity scores, one per class:
  unstable class U: s = 1 - p     (U enters the prediction set when 1 - p <= q_U, i.e. p >= 1 - q_U)
  stable class S:   s = p         (S enters the prediction set when p <= q_S)
Each q is the ceil((n + 1)(1 - alpha))-th smallest calibration score of its own class, +inf when that rank exceeds
n. For a new sample exchangeable with the calibration samples of its class, P(true class in the set) >= 1 - alpha;
for the unstable class this reads P(miss) <= alpha, a bound on the miss rate rather than on marginal coverage.
"""
from __future__ import annotations

import math

import numpy as np

# Prediction-set codes
SET_S, SET_U, SET_SU, SET_EMPTY = 0, 1, 2, 3
SET_NAMES = {SET_S: "{S}", SET_U: "{U}", SET_SU: "{S,U}", SET_EMPTY: "{}"}


def conformal_rank(n: int, alpha: float) -> int:
    """1-based rank ceil((n + 1)(1 - alpha)) of the calibration score used as the quantile; may exceed n."""
    if n < 0 or not 0.0 < alpha < 1.0:
        raise ValueError(f"need n >= 0 and 0 < alpha < 1, got n={n}, alpha={alpha}")
    # the small tolerance keeps exact products such as (49 + 1) * 0.98 = 49 from rounding up to 50
    return math.ceil((n + 1) * (1.0 - alpha) - 1e-9)


def min_calibration_size(alpha: float) -> int:
    """Smallest n with a finite conformal quantile: ceil((n + 1)(1 - alpha)) <= n."""
    n = 0
    while conformal_rank(n, alpha) > n:
        n += 1
    return n


def conformal_quantile(scores: np.ndarray, alpha: float) -> float:
    """The ceil((n + 1)(1 - alpha))-th smallest score, +inf when that rank exceeds n."""
    s = np.sort(np.asarray(scores, dtype=np.float64))
    k = conformal_rank(len(s), alpha)
    return float("inf") if k > len(s) else float(s[k - 1])


def alarm_threshold(p_unstable: np.ndarray, alpha: float) -> float:
    """Threshold t on p with U in the set iff p >= t, calibrated on unstable samples only (scores 1 - p).

    Returns -inf when the calibration set is too small for a finite quantile (U is then always in the set).
    The k-th smallest score 1 - p is the k-th largest p, taken directly so that t is exactly a calibration value."""
    p = np.sort(np.asarray(p_unstable, dtype=np.float64))
    k = conformal_rank(len(p), alpha)
    return -math.inf if k > len(p) else float(p[len(p) - k])


def stable_threshold(p_stable: np.ndarray, alpha: float) -> float:
    """Threshold t on p with S in the set iff p <= t, calibrated on stable samples only (scores p)."""
    return conformal_quantile(p_stable, alpha)


def max_misses_conditional(n: int, alpha: float, delta: float) -> int:
    """Largest c with P(Binomial(n, alpha) <= c) <= delta, or -1 if even c = 0 exceeds delta.

    With the threshold at the (c + 1)-th smallest of n exchangeable calibration values, the miss rate conditional on
    the calibration set is Beta(c + 1, n - c) distributed, and P(miss rate > alpha) = P(Binomial(n, alpha) <= c)
    (Vovk, 2013). Summed in log space so that large n does not underflow the first terms."""
    if not 0.0 < alpha < 1.0 or not 0.0 < delta < 1.0:
        raise ValueError(f"need 0 < alpha, delta < 1, got alpha={alpha}, delta={delta}")
    log_pmf, log_ratio = n * math.log1p(-alpha), math.log(alpha / (1.0 - alpha))
    cdf = 0.0
    for c in range(n + 1):
        cdf += math.exp(log_pmf)
        if cdf > delta:
            return c - 1
        log_pmf += math.log((n - c) / (c + 1)) + log_ratio if c < n else 0.0
    return n


def min_calibration_size_conditional(alpha: float, delta: float) -> int:
    """Smallest n with a finite calibration-conditional threshold: (1 - alpha)^n <= delta."""
    return math.ceil(math.log(delta) / math.log1p(-alpha) - 1e-9)


def alarm_threshold_conditional(p_unstable: np.ndarray, alpha: float, delta: float) -> float:
    """Alarm threshold whose miss rate exceeds alpha with probability at most delta over the calibration draw
    (training-conditional, or PAC, version of alarm_threshold). -inf when the calibration set is too small."""
    p = np.sort(np.asarray(p_unstable, dtype=np.float64))
    c = max_misses_conditional(len(p), alpha, delta)
    return -math.inf if c < 0 else float(p[c])


def paper_threshold(p_unstable: np.ndarray, target_fnr: float) -> float:
    """The paper's validation rule: the highest threshold whose miss rate on the given unstable samples does not
    exceed target_fnr (at most floor(target_fnr * n) samples below it). Differs from alarm_threshold by at most one
    order statistic (see tests)."""
    p = np.sort(np.asarray(p_unstable, dtype=np.float64))
    return float(p[int(math.floor(target_fnr * len(p)))]) if len(p) else 0.5


def prediction_sets(p: np.ndarray, t_alarm: float, t_stable: float) -> np.ndarray:
    """Prediction-set code per sample: {S}, {U}, {S,U} (refer to time-domain simulation) or {} (treat as alarm)."""
    p = np.asarray(p, dtype=np.float64)
    has_u = p >= t_alarm
    has_s = p <= t_stable
    out = np.full(p.shape, SET_EMPTY, dtype=np.int8)
    out[has_s & ~has_u] = SET_S
    out[has_u & ~has_s] = SET_U
    out[has_u & has_s] = SET_SU
    return out


def one_per_cluster(clusters: np.ndarray, mask: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Indices of one randomly chosen sample per cluster among the samples where mask is true.

    With calibration clusters exchangeable with a test cluster, a calibration set of one sample per cluster is
    exchangeable with one random sample of the test cluster, which restores the finite-sample statement exactly."""
    idx = np.flatnonzero(mask)
    if len(idx) == 0:
        return idx
    idx = idx[rng.permutation(len(idx))]
    _, first = np.unique(clusters[idx], return_index=True)
    return np.sort(idx[first])

import math

import numpy as np
import pytest

from tsa_conformal.conformal import (SET_EMPTY, SET_S, SET_SU, SET_U, alarm_threshold, conformal_quantile,
                                     conformal_rank, min_calibration_size, one_per_cluster, paper_threshold,
                                     prediction_sets, stable_threshold)
from tsa_conformal.evaluate import cluster_bootstrap, miss_rate, set_rates, split_clusters


@pytest.mark.parametrize("alpha,n_min", [(0.01, 99), (0.02, 49), (0.05, 19), (0.10, 9)])
def test_minimum_calibration_size(alpha, n_min):
    assert min_calibration_size(alpha) == n_min
    assert conformal_rank(n_min, alpha) == n_min
    assert conformal_rank(n_min - 1, alpha) > n_min - 1


def test_rank_exact_products_do_not_round_up():
    # (49 + 1) * 0.98 is 49 in exact arithmetic but not in floating point
    assert conformal_rank(49, 0.02) == 49
    assert conformal_rank(99, 0.01) == 99
    assert conformal_rank(100, 0.02) == 99


def test_quantile_too_few_samples_is_infinite():
    assert math.isinf(conformal_quantile(np.arange(10), 0.02))
    assert alarm_threshold(np.linspace(0.5, 1, 10), 0.02) == -math.inf


def test_quantile_order_statistic():
    s = np.random.default_rng(0).permutation(np.arange(1, 101, dtype=float))
    # n = 100, alpha = 0.1: rank ceil(101 * 0.9) = 91
    assert conformal_quantile(s, 0.1) == 91.0


def test_alarm_threshold_matches_score_quantile():
    p = np.random.default_rng(1).uniform(size=500)
    for alpha in (0.01, 0.02, 0.05, 0.1):
        t = alarm_threshold(p, alpha)
        assert t in p
        assert t == pytest.approx(1 - conformal_quantile(1 - p, alpha), abs=1e-12)


@pytest.mark.parametrize("n", [49, 50, 137, 600, 1001])
@pytest.mark.parametrize("alpha", [0.01, 0.02, 0.05, 0.1])
def test_paper_rule_differs_by_at_most_one_order_statistic(n, alpha):
    p = np.random.default_rng(n).uniform(size=n)
    if conformal_rank(n, alpha) > n:
        return
    below_paper = int((p < paper_threshold(p, alpha)).sum())
    below_conformal = int((p < alarm_threshold(p, alpha)).sum())
    assert below_paper == math.floor(alpha * n)
    assert 0 <= below_paper - below_conformal <= 1


@pytest.mark.parametrize("alpha", [0.02, 0.1])
def test_miss_rate_bound_on_exchangeable_data(alpha):
    """Calibration and test unstable samples from one distribution: the expected miss rate is
    (n - k + 1) / (n + 1) <= alpha, k = ceil((n + 1)(1 - alpha))."""
    rng = np.random.default_rng(2)
    n, trials = 200, 4000
    misses = []
    for _ in range(trials):
        cal, test = rng.beta(5, 2, size=n), rng.beta(5, 2, size=50)
        misses.append(miss_rate(test, np.ones(50), alarm_threshold(cal, alpha)))
    expected = (n - conformal_rank(n, alpha) + 1) / (n + 1)
    assert expected <= alpha
    se = np.std(misses) / np.sqrt(trials)
    assert abs(np.mean(misses) - expected) < 4 * se + 1e-4


def test_stable_class_coverage_on_exchangeable_data():
    rng = np.random.default_rng(3)
    cover = []
    for _ in range(2000):
        cal, test = rng.beta(2, 8, size=300), rng.beta(2, 8, size=50)
        cover.append(float((test <= stable_threshold(cal, 0.05)).mean()))
    assert np.mean(cover) >= 0.95 - 0.003


def test_prediction_set_codes():
    p = np.array([0.05, 0.3, 0.5, 0.9])
    # t_alarm < t_stable: band [t_alarm, t_stable] is referred
    np.testing.assert_array_equal(prediction_sets(p, 0.25, 0.6), [SET_S, SET_SU, SET_SU, SET_U])
    # t_alarm > t_stable: gap (t_stable, t_alarm) is empty
    np.testing.assert_array_equal(prediction_sets(p, 0.6, 0.25), [SET_S, SET_EMPTY, SET_EMPTY, SET_U])


def test_set_rates():
    sets = np.array([SET_S, SET_S, SET_SU, SET_U, SET_EMPTY, SET_S])
    y = np.array([0, 1, 1, 1, 0, 0])
    r = set_rates(sets, y)
    assert r["miss"] == pytest.approx(1 / 3)
    assert r["false_omission"] == pytest.approx(1 / 3)
    assert r["refer"] == pytest.approx(1 / 6)
    assert r["false_alarm"] == pytest.approx(1 / 3)
    assert r["refer_unstable"] == pytest.approx(1 / 3)


def test_one_per_cluster():
    rng = np.random.default_rng(4)
    clusters = np.repeat(np.arange(30), 7)
    mask = rng.uniform(size=len(clusters)) < 0.5
    idx = one_per_cluster(clusters, mask, rng)
    assert mask[idx].all()
    assert len(idx) == len(np.unique(clusters[mask])) == len(np.unique(clusters[idx]))


def test_split_clusters_is_a_partition():
    rng = np.random.default_rng(5)
    clusters = np.repeat(np.arange(40), 3)
    cal, test = split_clusters(clusters, 0.5, rng)
    assert len(cal) == 20 and len(np.intersect1d(cal, test)) == 0
    assert len(np.union1d(cal, test)) == 40
    cal, test = split_clusters(clusters, 5, rng)
    assert len(cal) == 5


def test_cluster_bootstrap_brackets_the_estimate():
    rng = np.random.default_rng(6)
    clusters = np.repeat(np.arange(100), 10)
    x = rng.normal(size=1000) + np.repeat(rng.normal(size=100), 10)
    lo, hi = cluster_bootstrap(lambda i: x[i].mean(), clusters, 500, rng)
    assert lo < x.mean() < hi


def test_max_misses_conditional_matches_exact_binomial():
    from tsa_conformal.conformal import max_misses_conditional
    for n, alpha, delta in [(50, 0.1, 0.05), (300, 0.02, 0.05), (1000, 0.05, 0.1), (149, 0.02, 0.05)]:
        cdf = np.cumsum([math.comb(n, k) * alpha ** k * (1 - alpha) ** (n - k) for k in range(n + 1)])
        expected = int(np.flatnonzero(cdf <= delta)[-1]) if cdf[0] <= delta else -1
        assert max_misses_conditional(n, alpha, delta) == expected


def test_conditional_minimum_calibration_size():
    from tsa_conformal.conformal import alarm_threshold_conditional, min_calibration_size_conditional
    n = min_calibration_size_conditional(0.02, 0.05)
    assert n == 149
    p = np.linspace(0.3, 1, 200)
    assert alarm_threshold_conditional(p[:n - 1], 0.02, 0.05) == -math.inf
    assert alarm_threshold_conditional(p[:n], 0.02, 0.05) == p[0]
    # large n: no underflow of the first binomial terms
    assert alarm_threshold_conditional(np.random.default_rng(0).uniform(size=60000), 0.1, 0.05) > 0


def test_conditional_threshold_is_below_the_marginal_one():
    from tsa_conformal.conformal import alarm_threshold_conditional
    p = np.random.default_rng(8).uniform(size=2000)
    for alpha in (0.02, 0.05, 0.1):
        assert alarm_threshold_conditional(p, alpha, 0.05) <= alarm_threshold(p, alpha)


def test_conditional_threshold_exceeds_alpha_rarely_on_exchangeable_data():
    """P(miss rate > alpha) over calibration draws: about one half for the marginal threshold, <= delta for the
    calibration-conditional one. The miss rate of a threshold is known exactly here: the uniform CDF."""
    from tsa_conformal.conformal import alarm_threshold_conditional
    rng = np.random.default_rng(9)
    alpha, delta, n, trials = 0.05, 0.1, 500, 4000
    marginal, conditional = [], []
    for _ in range(trials):
        cal = rng.uniform(size=n)
        marginal.append(alarm_threshold(cal, alpha) > alpha)
        conditional.append(alarm_threshold_conditional(cal, alpha, delta) > alpha)
    assert 0.3 < np.mean(marginal) < 0.6
    assert np.mean(conditional) <= delta + 3 * np.sqrt(delta * (1 - delta) / trials)

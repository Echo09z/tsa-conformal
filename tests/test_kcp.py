import math

import numpy as np

from tsa_conformal.conformal import alarm_threshold
from tsa_conformal.kcp import kcp_alarm_thresholds, outage_features


def test_equal_distances_give_the_uniform_weighted_quantile():
    rng = np.random.default_rng(0)
    p = rng.uniform(size=400)
    z_cal = np.zeros((400, 3))
    t, n_eff = kcp_alarm_thresholds(np.ones((5, 3)), z_cal, p, (0.02, 0.1))
    assert np.allclose(n_eff, 400)
    p_desc = np.sort(p)[::-1]
    for a_i, a in enumerate((0.02, 0.1)):
        # uniform weights: first rank with cumulative weight >= 1 - alpha (no +1 correction)
        assert np.all(t[:, a_i] == p_desc[math.ceil(400 * (1 - a)) - 1])


def test_concentrated_weights_fall_back_to_the_global_threshold():
    rng = np.random.default_rng(1)
    p = rng.uniform(size=300)
    z_cal = rng.normal(size=(300, 4)) * 100
    z_test = z_cal[:3] + 1e-3                     # each test case sits on one calibration case
    t, n_eff = kcp_alarm_thresholds(z_test, z_cal, p, (0.05,), k_nn=1)
    assert np.all(n_eff < 5)
    assert np.all(t[:, 0] == alarm_threshold(p, 0.05))


def test_exact_matches_share_the_weight():
    p = np.array([0.9, 0.8, 0.7, 0.6, 0.1, 0.05])
    z_cal = np.array([[0.0], [0.0], [0.0], [0.0], [5.0], [5.0]])
    t, n_eff = kcp_alarm_thresholds(np.array([[0.0]]), z_cal, p, (0.3,), k_nn=2, n_eff_min=1)
    assert n_eff[0] == 4
    # weight 1/4 on 0.9, 0.8, 0.7, 0.6: the cumulative weight reaches 1 - 0.3 at 0.7, so only 0.6 (weight 0.25 <= 0.3)
    # falls below the threshold
    assert t[0, 0] == 0.7


def test_local_calibration_follows_the_local_distribution():
    """Two separated groups with different score distributions: each test case gets its own group's quantile."""
    rng = np.random.default_rng(2)
    p = np.r_[rng.uniform(0.0, 0.5, 500), rng.uniform(0.5, 1.0, 500)]
    z = np.r_[np.zeros((500, 1)), np.full((500, 1), 10.0)]
    t, _ = kcp_alarm_thresholds(np.array([[0.0], [10.0]]), z, p, (0.1,))
    for g, row in ((p[:500], 0), (p[500:], 1)):
        assert t[row, 0] == np.sort(g)[::-1][math.ceil(500 * 0.9) - 1]


def test_outage_features():
    f = outage_features(np.array(["", "3", "1-33"]))
    assert f.shape == (3, 33)
    assert f[0].sum() == 0 and f[1, 2] == 1 and f[2, 0] == 1 and f[2, 32] == 1 and f[2].sum() == 2

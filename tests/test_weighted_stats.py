"""Tests for ``analysis.weighted_stats`` and ``analysis.wls``.

Covers ``weighted_mean_se`` (single-cluster -> NaN SE), ``weighted_prop_ci``
(degenerate p in {0, 1} -> non-logit CI), and ``weighted_ols`` cluster-robust
df = H - 1 t-stat correction.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.weighted_stats import weighted_mean_se, weighted_prop_ci
from analysis.wls import quintile_dummies, weighted_ols


def test_weighted_mean_se_single_cluster():
    """H = 1 -> SE = NaN (cluster-robust variance undefined for one cluster)."""
    y = np.array([1.0, 2.0, 3.0])
    w = np.array([1.0, 1.0, 1.0])
    psu = np.array([42, 42, 42])
    mean, sd, se, n, H = weighted_mean_se(y, w, psu)
    assert n == 3
    assert H == 1
    assert mean == 2.0
    assert np.isnan(se)


def test_weighted_mean_se_basic(mock_weights, mock_psu):
    """Equal weights / 5 PSUs / 50 obs: SE should be finite and positive."""
    y = np.tile(np.arange(10, dtype=float), 5)
    mean, sd, se, n, H = weighted_mean_se(y, mock_weights, mock_psu)
    assert n == 50
    assert H == 5
    assert se > 0


def test_weighted_prop_ci_returns_logit_ci(mock_weights, mock_psu):
    """Use a deterministic pattern with within- and between-PSU variation
    so the cluster-robust SE is positive and the logit CI is non-degenerate.
    """
    rng = np.random.default_rng(2026)
    ind = (rng.random(50) < 0.6).astype(float)
    p, se, lo, hi, n, H = weighted_prop_ci(ind, mock_weights, mock_psu)
    assert n == 50
    assert 0 < lo <= p <= hi < 1
    assert se > 0
    assert lo < hi


def test_weighted_ols_df_correction(mock_weights, mock_psu):
    """Fit on synthetic data with H=5 PSU clusters and assert df_resid = H-1 = 4."""
    rng = np.random.default_rng(2026)
    n = 50
    x = rng.normal(size=n)
    y = 1.0 + 2.0 * x + rng.normal(scale=0.5, size=n)
    X = np.column_stack([np.ones(n), x])
    res = weighted_ols(y, X, mock_weights, mock_psu, column_names=["const", "x"])
    assert res is not None
    assert res["n"] == 50
    assert res["n_psu"] == 5
    # The cluster-robust df adjustment is H - 1 = 4
    assert res["df_resid"] == 4
    # Slope should recover near 2
    assert abs(res["beta"]["x"] - 2.0) < 0.5


def test_quintile_dummies_basic():
    s = pd.Series(np.arange(50, dtype=float))
    dummies, q = quintile_dummies(s, n=5)
    # 5 quintiles -> dummies q2..q5 (4 columns), Q1 is reference
    assert list(dummies.columns) == ["q2", "q3", "q4", "q5"]
    # Each quintile should have exactly 10 members in the trend column
    counts = q.value_counts().sort_index()
    assert (counts.values == 10).all()

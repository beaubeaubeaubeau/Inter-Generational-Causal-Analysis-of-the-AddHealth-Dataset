"""Tests for ``analysis.wls``.

Covers ``weighted_ols`` (df adjustment, coefficient recovery, output schema,
short-circuit when too few clusters) and ``quintile_dummies`` (column count,
trend integer mapping, NaN propagation).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from analysis.wls import quintile_dummies, weighted_ols


# ---------------------------------------------------------------------------
# weighted_ols
# ---------------------------------------------------------------------------

def test_weighted_ols_df_resid_is_n_minus_k(mock_weights, mock_psu):
    """Per the 2026-04-26 decision, weighted_ols defers to statsmodels'
    default ``df_resid = n - k`` (not the manual H - 1 override). With
    n=50 observations and k=2 regressors (const + x), df_resid = 48.
    """
    rng = np.random.default_rng(2026)
    n = 50
    x = rng.normal(size=n)
    y = 1.0 + 2.0 * x + rng.normal(scale=0.5, size=n)
    X = np.column_stack([np.ones(n), x])
    res = weighted_ols(y, X, mock_weights, mock_psu, column_names=["const", "x"])
    assert res is not None
    assert res["n"] == 50
    assert res["n_psu"] == 5
    assert res["df_resid"] == 48  # n - k = 50 - 2
    assert abs(res["beta"]["x"] - 2.0) < 0.5


def test_weighted_ols_recovers_planted_coefficients():
    """With 200 obs, low noise, and known β=(intercept=1, slope=3), the WLS
    estimator should recover the slope to within 0.05 even with cluster SE."""
    rng = np.random.default_rng(0)
    n = 200
    x = rng.normal(size=n)
    y = 1.0 + 3.0 * x + rng.normal(scale=0.1, size=n)
    X = np.column_stack([np.ones(n), x])
    w = np.ones(n)
    psu = np.repeat(np.arange(20), 10)
    res = weighted_ols(y, X, w, psu, column_names=["const", "x"])
    assert res is not None
    assert abs(res["beta"]["const"] - 1.0) < 0.05
    assert abs(res["beta"]["x"] - 3.0) < 0.05


def test_weighted_ols_output_schema(mock_weights, mock_psu):
    """Result dict exposes beta/se/t/p/ci_lo/ci_hi as Series, plus n, n_psu,
    df_resid, rsquared."""
    rng = np.random.default_rng(2026)
    n = 50
    x = rng.normal(size=n)
    y = 1.0 + 0.5 * x + rng.normal(scale=0.5, size=n)
    X = np.column_stack([np.ones(n), x])
    res = weighted_ols(y, X, mock_weights, mock_psu, column_names=["const", "x"])
    assert res is not None
    for key in ("beta", "se", "t", "p", "ci_lo", "ci_hi"):
        assert isinstance(res[key], pd.Series)
        assert list(res[key].index) == ["const", "x"]
    for key in ("n", "n_psu", "df_resid"):
        assert isinstance(res[key], int)
    assert isinstance(res["rsquared"], float)


def test_weighted_ols_too_few_clusters_returns_none():
    """H < 2 -> function returns None (cluster-robust SE undefined)."""
    n = 10
    rng = np.random.default_rng(0)
    x = rng.normal(size=n)
    y = rng.normal(size=n)
    X = np.column_stack([np.ones(n), x])
    w = np.ones(n)
    psu = np.zeros(n)
    res = weighted_ols(y, X, w, psu)
    assert res is None


def test_weighted_ols_default_column_names_are_x0_xN():
    """When column_names=None, beta uses x0/x1/... index labels."""
    rng = np.random.default_rng(0)
    n = 50
    X = np.column_stack([np.ones(n), rng.normal(size=n), rng.normal(size=n)])
    y = X.sum(axis=1) + rng.normal(scale=0.2, size=n)
    w = np.ones(n)
    psu = np.repeat(np.arange(5), 10)
    res = weighted_ols(y, X, w, psu)
    assert res is not None
    assert list(res["beta"].index) == ["x0", "x1", "x2"]


def test_weighted_ols_drops_rows_with_nan():
    """Rows with NaN in y, w, or X are excluded; n reflects post-mask count."""
    n = 30
    rng = np.random.default_rng(0)
    x = rng.normal(size=n)
    y = 0.5 + x + rng.normal(scale=0.1, size=n)
    X = np.column_stack([np.ones(n), x])
    w = np.ones(n)
    psu = np.repeat(np.arange(3), 10)
    # Inject 5 NaNs into y
    y[:5] = np.nan
    res = weighted_ols(y, X, w, psu)
    assert res is not None
    assert res["n"] == 25


# ---------------------------------------------------------------------------
# quintile_dummies
# ---------------------------------------------------------------------------

def test_quintile_dummies_basic():
    s = pd.Series(np.arange(50, dtype=float))
    dummies, q = quintile_dummies(s, n=5)
    assert list(dummies.columns) == ["q2", "q3", "q4", "q5"]
    counts = q.value_counts().sort_index()
    assert (counts.values == 10).all()


def test_quintile_dummies_reference_quintile_omitted():
    """Q1 (lowest) is the implicit reference; only k-1 dummy columns returned."""
    s = pd.Series(np.arange(20, dtype=float))
    dummies, q = quintile_dummies(s, n=4)
    assert list(dummies.columns) == ["q2", "q3", "q4"]
    # Each row has exactly one '1' across the 3 dummies, OR all zeros (Q1).
    sums = dummies.sum(axis=1)
    assert sums.isin([0.0, 1.0]).all()


def test_quintile_dummies_nan_propagation():
    """NaN inputs -> NaN trend value AND NaN in every dummy column for that row."""
    s = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0])
    dummies, q = quintile_dummies(s, n=5)
    assert pd.isna(q.iloc[2])
    for col in dummies.columns:
        assert pd.isna(dummies.iloc[2][col])


def test_quintile_dummies_trend_is_1_to_n():
    """Trend column values are in [1, n] for non-NaN rows."""
    s = pd.Series(np.arange(100, dtype=float))
    dummies, q = quintile_dummies(s, n=5)
    obs = q.dropna().unique()
    assert set(obs) == {1.0, 2.0, 3.0, 4.0, 5.0}


def test_quintile_dummies_n_other_than_5():
    """quintile_dummies(n=3) gives k-1=2 dummy columns named q2, q3."""
    s = pd.Series(np.arange(30, dtype=float))
    dummies, q = quintile_dummies(s, n=3)
    assert list(dummies.columns) == ["q2", "q3"]
    counts = q.value_counts().sort_index()
    assert (counts.values == 10).all()

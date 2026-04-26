"""Tests for ``analysis.weighted_stats``.

Covers ``weighted_mean_se`` (single-cluster -> NaN SE, multi-cluster recovery,
all-NaN handling) and ``weighted_prop_ci`` (logit CI for non-degenerate p,
clamped linear CI for p=0/1, single-cluster -> NaN SE).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from analysis.weighted_stats import weighted_mean_se, weighted_prop_ci


# ---------------------------------------------------------------------------
# weighted_mean_se
# ---------------------------------------------------------------------------

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


def test_weighted_mean_se_known_mean_recovery():
    """Plant a known weighted mean: y constant -> SE = 0, mean recovered exactly."""
    y = np.full(20, 7.5)
    w = np.full(20, 2.0)
    psu = np.repeat(np.arange(4), 5)  # 4 clusters of 5
    mean, sd, se, n, H = weighted_mean_se(y, w, psu)
    assert mean == 7.5
    assert sd == 0.0
    assert se == 0.0
    assert n == 20
    assert H == 4


def test_weighted_mean_se_all_nan_returns_nan():
    """All inputs NaN -> mean/sd/se NaN, n=0, H=0."""
    y = np.array([np.nan, np.nan, np.nan])
    w = np.array([1.0, 1.0, 1.0])
    psu = np.array([0, 0, 1])
    mean, sd, se, n, H = weighted_mean_se(y, w, psu)
    assert np.isnan(mean)
    assert np.isnan(sd)
    assert np.isnan(se)
    assert n == 0
    assert H == 0


def test_weighted_mean_se_zero_or_negative_weights_dropped():
    """Observations with w<=0 or NaN w are excluded from estimation."""
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    w = np.array([1.0, 0.0, -1.0, np.nan, 1.0])
    psu = np.array([0, 0, 1, 1, 2])
    mean, _, _, n, H = weighted_mean_se(y, w, psu)
    # Only y=1 (psu 0) and y=5 (psu 2) survive
    assert n == 2
    assert H == 2
    assert mean == 3.0   # (1*1 + 1*5) / (1+1) = 3


def test_weighted_mean_se_reference_calc():
    """Hand-computed example with 5 clusters of 2 observations.

    y = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], w = ones, PSU = [0,0,1,1,2,2,3,3,4,4]
    sum(w*y) = 55, W = 10 -> mean = 5.5
    cluster sums of u_i = w*(y - mean):
      psu 0: (1-5.5) + (2-5.5) = -8
      psu 1: (3-5.5) + (4-5.5) = -4
      psu 2: (5-5.5) + (6-5.5) =  0
      psu 3: (7-5.5) + (8-5.5) =  4
      psu 4: (9-5.5) + (10-5.5) = 8
    u_bar = 0; sum((u_h - u_bar)^2) = 64+16+0+16+64 = 160
    var = (5/4) * 160 / 100 = 2.0; se = sqrt(2.0)
    """
    y = np.arange(1, 11, dtype=float)
    w = np.ones(10)
    psu = np.repeat(np.arange(5), 2)
    mean, sd, se, n, H = weighted_mean_se(y, w, psu)
    assert mean == 5.5
    assert n == 10
    assert H == 5
    assert abs(se - np.sqrt(2.0)) < 1e-10


# ---------------------------------------------------------------------------
# weighted_prop_ci
# ---------------------------------------------------------------------------

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


def test_weighted_prop_ci_p_equals_zero_returns_clamped_ci():
    """When everyone is 0, p=0 -> linear CI clamped to [0, 1] (no logit)."""
    ind = np.zeros(20)
    w = np.ones(20)
    psu = np.repeat(np.arange(4), 5)
    p, se, lo, hi, n, H = weighted_prop_ci(ind, w, psu)
    assert p == 0.0
    # se is 0, so lo == hi == 0
    assert lo == 0.0
    assert hi == 0.0


def test_weighted_prop_ci_p_equals_one_returns_clamped_ci():
    """When everyone is 1, p=1 -> linear CI clamped to [0, 1]."""
    ind = np.ones(20)
    w = np.ones(20)
    psu = np.repeat(np.arange(4), 5)
    p, se, lo, hi, n, H = weighted_prop_ci(ind, w, psu)
    assert p == 1.0
    assert lo == 1.0
    assert hi == 1.0


def test_weighted_prop_ci_single_cluster_se_is_nan():
    """H=1 -> SE NaN; CI defaults to clamp around p with no widening."""
    ind = np.array([0.0, 1.0, 1.0, 0.0])
    w = np.ones(4)
    psu = np.zeros(4)
    p, se, lo, hi, n, H = weighted_prop_ci(ind, w, psu)
    assert H == 1
    assert n == 4
    assert p == 0.5
    assert np.isnan(se)
    # Falls into the degenerate branch; lo/hi should still be defined
    # (max(0, p - 1.96*0) = p and min(1, p + 1.96*0) = p)
    assert lo == pytest.approx(0.5)
    assert hi == pytest.approx(0.5)


def test_weighted_prop_ci_logit_ci_brackets_p():
    """For 0 < p < 1 with multi-cluster variance, the logit CI must bracket
    the point estimate strictly."""
    rng = np.random.default_rng(7)
    ind = (rng.random(60) < 0.4).astype(float)
    w = np.ones(60)
    psu = np.repeat(np.arange(6), 10)
    p, se, lo, hi, n, H = weighted_prop_ci(ind, w, psu)
    assert 0 < p < 1
    assert lo < p < hi
    assert 0 <= lo <= 1
    assert 0 <= hi <= 1

"""Tests for ``analysis.plot_style`` pure helpers.

The matplotlib/seaborn ``setup`` and ``save`` helpers are stateful and
not worth testing here; we cover only the pure-numeric helpers
(``weighted_mean`` and ``weighted_median``) plus the ``GROUP_COLORS``
canonical-palette dict.
"""
from __future__ import annotations

import numpy as np
import pytest

from analysis.plot_style import GROUP_COLORS, weighted_mean, weighted_median


def test_weighted_mean_basic():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    w = np.array([1.0, 1.0, 1.0, 1.0])
    assert weighted_mean(y, w) == 2.5


def test_weighted_mean_unequal_weights():
    """weighted_mean(y, w) = sum(w*y) / sum(w)."""
    y = np.array([1.0, 2.0, 3.0])
    w = np.array([1.0, 2.0, 1.0])
    assert weighted_mean(y, w) == (1 + 4 + 3) / 4


def test_weighted_mean_nan_y_dropped():
    y = np.array([1.0, np.nan, 3.0])
    w = np.array([1.0, 1.0, 1.0])
    assert weighted_mean(y, w) == 2.0


def test_weighted_mean_zero_or_nan_weights_dropped():
    y = np.array([1.0, 2.0, 3.0, 4.0])
    w = np.array([1.0, 0.0, np.nan, 1.0])
    # Only y=1 (w=1) and y=4 (w=1) survive
    assert weighted_mean(y, w) == 2.5


def test_weighted_mean_all_nan_returns_nan():
    y = np.array([np.nan, np.nan])
    w = np.array([1.0, 1.0])
    assert np.isnan(weighted_mean(y, w))


def test_weighted_median_basic():
    """Equal weights -> just the unweighted median."""
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    w = np.ones(5)
    assert weighted_median(y, w) == 3.0


def test_weighted_median_skews_toward_heavy_weight():
    """Skewing weight toward y=5 should pull the weighted median above the
    unweighted median (3.0).
    """
    y = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    w = np.array([0.1, 0.1, 0.1, 0.1, 100.0])
    out = weighted_median(y, w)
    assert out == 5.0


def test_weighted_median_all_nan_returns_nan():
    y = np.array([np.nan, np.nan])
    w = np.array([1.0, 1.0])
    assert np.isnan(weighted_median(y, w))


def test_group_colors_has_all_canonical_groups():
    """All five outcome groups must be present and resolve to hex strings."""
    expected = {"cognitive", "cardiometabolic", "mental_health",
                "functional", "ses"}
    assert set(GROUP_COLORS.keys()) == expected
    for group, color in GROUP_COLORS.items():
        assert isinstance(color, str)
        assert color.startswith("#")
        assert len(color) == 7  # "#RRGGBB"

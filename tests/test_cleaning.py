"""Tests for ``analysis.cleaning``.

Covers the per-variable valid-range filter (``VALID_RANGES``) and the
``clean_var`` reserve-code stripping behaviour.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from analysis.cleaning import VALID_RANGES, clean_var


def test_clean_var_reserve_codes():
    """Per the test specification: AH_RAW range is [0, 87]. Inputs
    [-1, 0.5, 1, 6, 99] should clean to [NaN, 0.5, 1, 6, NaN]
    (-1 below range, 99 above range; 0.5/1/6 are inside [0, 87]).
    """
    s = pd.Series([-1, 0.5, 1, 6, 99], dtype=float)
    out = clean_var(s, "AH_RAW")
    assert pd.isna(out.iloc[0])    # -1 below range
    assert out.iloc[1] == 0.5
    assert out.iloc[2] == 1.0
    assert out.iloc[3] == 6.0      # 6 IS inside [0, 87] for AH_RAW
    assert pd.isna(out.iloc[4])    # 99 above range


def test_clean_var_strips_reserves_for_cesd():
    """CES-D items have range [0, 3]. Reserve codes 6/7/8/9 should drop."""
    s = pd.Series([0, 1, 2, 3, 6, 7, 8, 9], dtype=float)
    out = clean_var(s, "H1FS1")
    assert (out.iloc[:4].values == [0, 1, 2, 3]).all()
    assert out.iloc[4:].isna().all()


def test_clean_var_unknown_var_passes_through():
    """A variable not in VALID_RANGES should only get numeric coercion."""
    s = pd.Series(["1", "2", "abc", None])
    out = clean_var(s, "NOT_A_REAL_CODE")
    assert out.iloc[0] == 1.0
    assert out.iloc[1] == 2.0
    assert pd.isna(out.iloc[2])    # "abc" -> NaN via to_numeric coerce
    assert pd.isna(out.iloc[3])


def test_valid_ranges_covers_expected_keys():
    expected_subset = {
        "IDGX2", "ODGX2", "AH_PVT", "AH_RAW", "BIO_SEX",
        "C4WD90_1", "C4WD60_1", "C4NUMSCR",
        "H4BMI", "H4SBP", "H4DBP", "H4WAIST", "H4BMICLS",
        "H5MN1", "H5EC1",
    }
    missing = expected_subset - VALID_RANGES.keys()
    assert not missing, f"VALID_RANGES missing expected entries: {missing}"

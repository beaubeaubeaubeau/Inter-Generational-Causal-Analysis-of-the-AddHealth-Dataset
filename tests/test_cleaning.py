"""Tests for ``analysis.cleaning``.

Covers the per-variable valid-range filter (``VALID_RANGES``), the
``clean_var`` reserve-code stripping behaviour, the ``neg_control_outcome``
HEIGHT_IN aggregation (which reads from cache), and a meta-test on the
shape of every entry in ``VALID_RANGES``.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from analysis import CACHE
from analysis.cleaning import VALID_RANGES, clean_var, neg_control_outcome


def test_clean_var_reserve_codes():
    """AH_RAW range is [0, 87]. Inputs [-1, 0.5, 1, 6, 99] should clean to
    [NaN, 0.5, 1, 6, NaN] (-1 below range, 99 above range)."""
    s = pd.Series([-1, 0.5, 1, 6, 99], dtype=float)
    out = clean_var(s, "AH_RAW")
    assert pd.isna(out.iloc[0])
    assert out.iloc[1] == 0.5
    assert out.iloc[2] == 1.0
    assert out.iloc[3] == 6.0
    assert pd.isna(out.iloc[4])


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
    assert pd.isna(out.iloc[2])
    assert pd.isna(out.iloc[3])


def test_valid_ranges_covers_expected_keys():
    """Spot-check that the canonical keys are present."""
    expected_subset = {
        "IDGX2", "ODGX2", "AH_PVT", "AH_RAW", "BIO_SEX",
        "C4WD90_1", "C4WD60_1", "C4NUMSCR",
        "H4BMI", "H4SBP", "H4DBP", "H4WAIST", "H4BMICLS",
        "H5MN1", "H5EC1",
    }
    missing = expected_subset - VALID_RANGES.keys()
    assert not missing, f"VALID_RANGES missing expected entries: {missing}"


# ---------------------------------------------------------------------------
# Extended clean_var coverage: W4, W5, derived vars, edge cases
# ---------------------------------------------------------------------------

def test_clean_var_w4_cardiometabolic_ranges():
    """H4BMI valid in [10, 80]; reserves 996/997/998 should drop. H4SBP in
    [50, 250]; H4WAIST in [40, 200]."""
    bmi = pd.Series([5.0, 10.0, 25.0, 80.0, 81.0, 996.0])
    out = clean_var(bmi, "H4BMI")
    assert pd.isna(out.iloc[0])
    assert out.iloc[1] == 10.0
    assert out.iloc[2] == 25.0
    assert out.iloc[3] == 80.0
    assert pd.isna(out.iloc[4])
    assert pd.isna(out.iloc[5])

    sbp = pd.Series([49.9, 50.0, 120.0, 250.0, 250.1])
    out = clean_var(sbp, "H4SBP")
    assert pd.isna(out.iloc[0])
    assert out.iloc[1] == 50.0
    assert out.iloc[3] == 250.0
    assert pd.isna(out.iloc[4])


def test_clean_var_w5_outcomes():
    """H5EC1 (employment status) range is [1, 13]; H5MN1 (mental health) [1, 5]."""
    ec1 = pd.Series([0, 1, 7, 13, 14, 96], dtype=float)
    out = clean_var(ec1, "H5EC1")
    assert pd.isna(out.iloc[0])
    assert out.iloc[1] == 1.0
    assert out.iloc[3] == 13.0
    assert pd.isna(out.iloc[4])
    assert pd.isna(out.iloc[5])

    mn1 = pd.Series([0, 1, 3, 5, 6], dtype=float)
    out = clean_var(mn1, "H5MN1")
    assert pd.isna(out.iloc[0])
    assert out.iloc[1] == 1.0
    assert out.iloc[3] == 5.0
    assert pd.isna(out.iloc[4])


def test_clean_var_unit_interval_continuous_keeps_fractions():
    """PRXPREST is documented as continuous in [0, 1]. Fractional values
    such as 0.0, 0.32, 0.77, 1.0 must survive cleaning."""
    s = pd.Series([0.0, 0.32, 0.77, 1.0, 1.5, -0.1])
    out = clean_var(s, "PRXPREST")
    assert out.iloc[0] == 0.0
    assert out.iloc[1] == 0.32
    assert out.iloc[2] == 0.77
    assert out.iloc[3] == 1.0
    assert pd.isna(out.iloc[4])
    assert pd.isna(out.iloc[5])


def test_clean_var_negative_range_bcent10x():
    """BCENT10X is real-valued; range is (-1e6, 1e6). Negative numbers must survive."""
    s = pd.Series([-500.0, -1.5, 0.0, 1e5, 1e7])
    out = clean_var(s, "BCENT10X")
    assert out.iloc[0] == -500.0
    assert out.iloc[1] == -1.5
    assert out.iloc[2] == 0.0
    assert out.iloc[3] == 1e5
    assert pd.isna(out.iloc[4])  # 1e7 outside (-1e6, 1e6)


def test_clean_var_w5_bds_per_trial_binary():
    """H5MH3A..H5MH9B are 0/1 only; reserves 95/96/97 etc drop."""
    s = pd.Series([0, 1, 2, 95, 96, 97, 98], dtype=float)
    out = clean_var(s, "H5MH3A")
    assert out.iloc[0] == 0.0
    assert out.iloc[1] == 1.0
    assert pd.isna(out.iloc[2])  # 2 outside [0,1]
    assert out.iloc[3:].isna().all()


def test_clean_var_integer_only_h1ed19_likert():
    """H1ED19 (school belonging) is a 1-5 Likert; 0 and 6 drop out."""
    s = pd.Series([0, 1, 2, 3, 4, 5, 6, 8], dtype=float)
    out = clean_var(s, "H1ED19")
    assert pd.isna(out.iloc[0])
    assert out.iloc[1] == 1.0
    assert out.iloc[5] == 5.0
    assert pd.isna(out.iloc[6])
    assert pd.isna(out.iloc[7])


# ---------------------------------------------------------------------------
# VALID_RANGES meta-tests
# ---------------------------------------------------------------------------

def test_valid_ranges_well_formed():
    """Every entry must be a (lo, hi) tuple of floats with lo < hi."""
    for key, val in VALID_RANGES.items():
        assert isinstance(val, tuple), f"VALID_RANGES[{key!r}] is not a tuple"
        assert len(val) == 2, f"VALID_RANGES[{key!r}] does not have 2 elements"
        lo, hi = val
        assert isinstance(lo, (int, float)), f"VALID_RANGES[{key!r}] lo is non-numeric"
        assert isinstance(hi, (int, float)), f"VALID_RANGES[{key!r}] hi is non-numeric"
        assert lo < hi, f"VALID_RANGES[{key!r}] lo >= hi: ({lo}, {hi})"


def test_valid_ranges_contains_all_cesd_items():
    """All 19 CES-D items H1FS1..H1FS19 must have VALID_RANGES = (0, 3)."""
    for i in range(1, 20):
        key = f"H1FS{i}"
        assert key in VALID_RANGES, f"Missing CES-D key {key}"
        assert VALID_RANGES[key] == (0, 3)


def test_valid_ranges_contains_all_w5_bds_items():
    """All 14 H5MH{3..9}{A,B} BDS trials must have VALID_RANGES = (0, 1)."""
    for L in range(3, 10):
        for s in "AB":
            key = f"H5MH{L}{s}"
            assert key in VALID_RANGES, f"Missing BDS trial {key}"
            assert VALID_RANGES[key] == (0, 1)


# ---------------------------------------------------------------------------
# neg_control_outcome — depends on cached w4inhome.parquet
# ---------------------------------------------------------------------------

_W4_PARQUET = CACHE / "w4inhome.parquet"


@pytest.mark.skipif(
    not _W4_PARQUET.exists(),
    reason="requires cached w4inhome.parquet from prep pipeline",
)
def test_neg_control_outcome_height_aggregation():
    """HEIGHT_IN = feet * 12 + inches. Pull a few real AIDs from the cache,
    rebuild HEIGHT_IN by hand, and confirm neg_control_outcome agrees.
    """
    w4 = pd.read_parquet(_W4_PARQUET)[["AID", "H4GH5F", "H4GH5I"]]
    aid_sample = w4["AID"].iloc[:20]
    out = neg_control_outcome(aid_sample)
    assert out.index.equals(aid_sample.index)
    # Re-derive expected
    feet = pd.to_numeric(w4["H4GH5F"], errors="coerce").where(
        lambda s: s.between(4, 7))
    inch = pd.to_numeric(w4["H4GH5I"], errors="coerce").where(
        lambda s: s.between(0, 11))
    expected_full = (feet * 12 + inch)
    expected = pd.DataFrame({"AID": aid_sample.values}).merge(
        pd.DataFrame({"AID": w4["AID"], "EXP": expected_full}),
        on="AID", how="left")["EXP"].values
    out_vals = out.values
    # Compare element-wise allowing both NaN
    for got, exp in zip(out_vals, expected):
        if pd.isna(exp):
            assert pd.isna(got)
        else:
            assert got == exp


@pytest.mark.skipif(
    not _W4_PARQUET.exists(),
    reason="requires cached w4inhome.parquet from prep pipeline",
)
def test_neg_control_outcome_unknown_aid_returns_nan():
    """A wholly fake AID should return NaN HEIGHT_IN."""
    aid = pd.Series(["FAKEAID9999"], name="AID")
    out = neg_control_outcome(aid)
    assert pd.isna(out.iloc[0])

"""Tests for ``analysis.derivation``.

Covers the seven derivation helpers + reserved-code propagation. Includes
the known TODO B P0 bug test (``test_derive_w5_bds_nan_propagation``) which
captures the *current* "fail at NaN" semantic via xfail so the bug is
documented rather than silently masked.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from analysis.derivation import (
    CESD_ITEMS,
    CESD_REVERSE,
    derive_cesd_sum,
    derive_friendship_grid,
    derive_parent_ed,
    derive_race_ethnicity,
    derive_school_belonging,
    derive_w4_cog_composite,
    derive_w5_bds,
)


def test_derive_cesd_sum_reverse_scoring(synthetic_w1_df):
    """Items {4, 8, 11, 15} reverse-coded; row 0 has all H1FS items = 0,
    which after reversing those four becomes 4 * 3 = 12 (the 15 non-reversed
    items contribute 0). Row 2 is all-NaN -> NaN (min_count=19).
    """
    out = derive_cesd_sum(synthetic_w1_df)
    assert out.iloc[0] == 12.0
    # Row 2 all-missing -> NaN (min_count=19)
    assert pd.isna(out.iloc[2])
    # Row 1 has reserve codes 96 / 99 in items 1, 2 — those get scrubbed,
    # leaving fewer than 19 valid items -> NaN
    assert pd.isna(out.iloc[1])


def test_derive_cesd_constants_match_spec():
    """CES-D items 1-19 enumerated; reverse set is {4, 8, 11, 15}."""
    assert CESD_ITEMS == [f"H1FS{i}" for i in range(1, 20)]
    assert CESD_REVERSE == {4, 8, 11, 15}


@pytest.mark.xfail(
    reason=(
        "TODO §B P0: derive_w5_bds NaN handling. (a == 1) | (b == 1) returns"
        " False when a/b are NaN (NaN == 1 -> False), so a respondent with"
        " items missing at length L=4+ but passing at L=2,3 gets a final"
        " score of 3 — indistinguishable from a respondent who actually"
        " failed at L=4. The user has not yet decided whether the chosen"
        " semantic is 'fail at NaN' (current) or 'NaN propagates' (proposed)."
        " This test asserts the proposed-NaN-propagation semantic; flip"
        " expectation when the decision is made."
    )
)
def test_derive_w5_bds_nan_propagation():
    """Construct a respondent who passes at L=2, L=3 and is missing at L=4-8.

    Under current semantic the score = 3 (highest passed level).
    Under the proposed 'NaN propagates' semantic, missing items at higher
    levels should yield NaN because we cannot determine whether the
    respondent could have continued.
    """
    rec = {f"H5MH{L+1}{s}": np.nan for L in range(2, 9) for s in "AB"}
    rec["H5MH3A"] = 1.0   # L=2 pass
    rec["H5MH3B"] = 0.0
    rec["H5MH4A"] = 1.0   # L=3 pass
    rec["H5MH4B"] = 0.0
    # L=4-8 left as NaN
    df = pd.DataFrame([rec])
    out = derive_w5_bds(df)
    # Proposed semantic — currently fails (out.iloc[0] == 3.0 under current code).
    assert pd.isna(out.iloc[0])


def test_derive_w5_bds_all_missing_is_nan():
    """A respondent missing every BDS item should always score NaN."""
    rec = {f"H5MH{L+1}{s}": np.nan for L in range(2, 9) for s in "AB"}
    df = pd.DataFrame([rec])
    out = derive_w5_bds(df)
    assert pd.isna(out.iloc[0])


def test_derive_w5_bds_clean_pass():
    """Pass at L=4, fail at L=5 onward -> score = 4."""
    rec = {f"H5MH{L+1}{s}": 0.0 for L in range(2, 9) for s in "AB"}
    rec["H5MH3A"] = 1.0  # L=2
    rec["H5MH4A"] = 1.0  # L=3
    rec["H5MH5A"] = 1.0  # L=4
    df = pd.DataFrame([rec])
    out = derive_w5_bds(df)
    assert out.iloc[0] == 4.0


def test_derive_school_belonging_double_reverse(synthetic_w1_df):
    """Row 0 has all six belonging items = 1.

    Each cleaned item is reversed via (6 - x) so 1 -> 5. With 6 items the
    total reflects higher = more belonging: 6 * 5 = 30.
    """
    out = derive_school_belonging(synthetic_w1_df)
    assert out.iloc[0] == 30.0


def test_derive_race_ethnicity_categories(synthetic_w1_df):
    out = derive_race_ethnicity(synthetic_w1_df)
    assert out.iloc[3] == "Hispanic"
    assert out.iloc[4] == "NH-White"
    assert out.iloc[5] == "NH-Black"
    assert out.iloc[6] == "Other"


def test_derive_parent_ed_max_recodes(synthetic_w1_df):
    out = derive_parent_ed(synthetic_w1_df)
    # Row 7: mom college grad (7 -> 5), dad HS grad (4 -> 2) -> max = 5
    assert out.iloc[7] == 5.0
    # Row 8: both never (9 -> 0) -> 0
    assert out.iloc[8] == 0.0
    # Row 9: mom reserve 99 (NaN), dad HS grad (4 -> 2) -> max ignores NaN -> 2
    assert out.iloc[9] == 2.0


def test_derive_friendship_grid_nomination_count(synthetic_w1_df):
    """Row 0 has exactly 1 nominated slot (H1MF2A=1) with all five contact
    items=1. Row 1 has H1MF2A=7 (legit-skip) -> not nominated, even though
    H1MF6A=1 (its contact item should not count).
    """
    grid = derive_friendship_grid(synthetic_w1_df)
    assert grid["FRIEND_N_NOMINEES"].iloc[0] == 1
    assert grid["FRIEND_CONTACT_SUM"].iloc[0] == 5.0
    assert grid["FRIEND_DISCLOSURE_ANY"].iloc[0] == 1
    assert grid["FRIEND_N_NOMINEES"].iloc[1] == 0
    assert grid["FRIEND_CONTACT_SUM"].iloc[1] == 0.0
    assert grid["FRIEND_DISCLOSURE_ANY"].iloc[1] == 0


def test_derive_w4_cog_composite_zscore_mean(synthetic_w4_df):
    """Composite is mean of three z-scored series. By construction each
    z-score has mean ~ 0, so the composite has mean ~ 0 and finite SD."""
    out = derive_w4_cog_composite(synthetic_w4_df)
    assert not out.dropna().empty
    assert abs(out.mean()) < 1e-9 or abs(out.mean()) < 0.5
    assert out.dropna().std() > 0

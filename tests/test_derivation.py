"""Tests for ``analysis.derivation``.

Covers every public derive_* helper plus the module-level constants. Tests
extend the seed coverage with all-missing edge cases, partial-missing
behaviour, and known-bug captures via xfail.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from analysis.derivation import (
    CESD_ITEMS,
    CESD_REVERSE,
    FRIEND_ITEM_DISCLOSURE,
    FRIEND_ITEMS_CONTACT,
    FRIEND_SLOTS,
    derive_cesd_sum,
    derive_friendship_grid,
    derive_parent_ed,
    derive_race_ethnicity,
    derive_school_belonging,
    derive_w4_cog_composite,
    derive_w5_bds,
    derive_w5_cog_composite,
)


# ---------------------------------------------------------------------------
# CES-D
# ---------------------------------------------------------------------------

def test_derive_cesd_sum_reverse_scoring(synthetic_w1_df):
    """Items {4, 8, 11, 15} reverse-coded; row 0 has all 0 -> after reverse
    those four = 3, others = 0 -> sum = 12.
    """
    out = derive_cesd_sum(synthetic_w1_df)
    assert out.iloc[0] == 12.0
    # Row 2 all-missing -> NaN (min_count=19)
    assert pd.isna(out.iloc[2])
    # Row 1 has reserve codes 96 / 99 in items 1, 2 — those get scrubbed,
    # leaving fewer than 19 valid items -> NaN
    assert pd.isna(out.iloc[1])


def test_derive_cesd_constants_match_spec():
    assert CESD_ITEMS == [f"H1FS{i}" for i in range(1, 20)]
    assert CESD_REVERSE == {4, 8, 11, 15}


def test_derive_cesd_sum_strips_reserves_before_summing():
    """A respondent with mostly-valid items + one reserve code should fall
    below min_count=19 and return NaN; a fully valid respondent's sum
    should NOT include any reserve-code values.
    """
    base = {f"H1FS{i}": 1.0 for i in range(1, 20)}
    # All valid (1) — items 4/8/11/15 reverse to (3-1)=2, others stay 1
    df = pd.DataFrame([base])
    out = derive_cesd_sum(df)
    expected = 4 * (3 - 1) + 15 * 1  # 8 + 15 = 23
    assert out.iloc[0] == float(expected)

    # Same record but item 5 set to reserve code 7 -> dropped -> 18 valid -> NaN
    rec = dict(base)
    rec["H1FS5"] = 7.0
    df2 = pd.DataFrame([rec])
    out2 = derive_cesd_sum(df2)
    assert pd.isna(out2.iloc[0])


# ---------------------------------------------------------------------------
# W5 BDS
# ---------------------------------------------------------------------------

@pytest.mark.xfail(
    reason=(
        "TODO §B P0: derive_w5_bds NaN handling. (a == 1) | (b == 1) returns"
        " False when a/b are NaN (NaN == 1 -> False), so a respondent with"
        " items missing at length L=4+ but passing at L=2,3 gets a final"
        " score of 3 — indistinguishable from a respondent who actually"
        " failed at L=4. Test asserts the proposed-NaN-propagation semantic."
    )
)
def test_derive_w5_bds_nan_propagation():
    """Construct a respondent who passes at L=2, L=3 and is missing at L=4-8.

    Under current semantic the score = 3 (highest passed level). Proposed:
    NaN since we cannot determine whether the respondent could have continued.
    """
    rec = {f"H5MH{L+1}{s}": np.nan for L in range(2, 9) for s in "AB"}
    rec["H5MH3A"] = 1.0
    rec["H5MH3B"] = 0.0
    rec["H5MH4A"] = 1.0
    rec["H5MH4B"] = 0.0
    df = pd.DataFrame([rec])
    out = derive_w5_bds(df)
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
    rec["H5MH3A"] = 1.0
    rec["H5MH4A"] = 1.0
    rec["H5MH5A"] = 1.0
    df = pd.DataFrame([rec])
    out = derive_w5_bds(df)
    assert out.iloc[0] == 4.0


def test_derive_w5_bds_deterministic_pass_2_through_5_no_nan():
    """A respondent who passes cleanly at L=2,3,4,5 with all later items 0
    should score exactly 5. No NaN handling involved.
    """
    rec = {f"H5MH{L+1}{s}": 0.0 for L in range(2, 9) for s in "AB"}
    rec["H5MH3A"] = 1.0   # L=2 pass
    rec["H5MH4B"] = 1.0   # L=3 pass (use B trial)
    rec["H5MH5A"] = 1.0   # L=4 pass
    rec["H5MH6B"] = 1.0   # L=5 pass
    # L=6, 7, 8 left at 0 -> fail
    df = pd.DataFrame([rec])
    out = derive_w5_bds(df)
    assert out.iloc[0] == 5.0


def test_derive_w5_bds_no_pass_returns_zero():
    """Respondent answers everything 0 -> score = 0."""
    rec = {f"H5MH{L+1}{s}": 0.0 for L in range(2, 9) for s in "AB"}
    df = pd.DataFrame([rec])
    out = derive_w5_bds(df)
    assert out.iloc[0] == 0.0


# ---------------------------------------------------------------------------
# W4 cognitive composite
# ---------------------------------------------------------------------------

def test_derive_w4_cog_composite_zscore_mean(synthetic_w4_df):
    """Composite is mean of three z-scored series. Each z-score has mean ~0,
    so the composite has mean ~0 and finite SD."""
    out = derive_w4_cog_composite(synthetic_w4_df)
    assert not out.dropna().empty
    assert abs(out.dropna().mean()) < 0.5
    assert out.dropna().std() > 0


def test_derive_w4_cog_composite_all_nan_yields_nan(synthetic_w4_df):
    """Row 1 is constructed with all three components NaN -> composite NaN."""
    out = derive_w4_cog_composite(synthetic_w4_df)
    assert pd.isna(out.iloc[1])


def test_derive_w4_cog_composite_partial_missing_propagates_nan(synthetic_w4_df):
    """Row 2 has only C4WD90_1 valid; the helper uses skipna=False, so the
    composite must be NaN. Documents the chosen semantic: a respondent
    must have all three components for a composite score.
    """
    out = derive_w4_cog_composite(synthetic_w4_df)
    assert pd.isna(out.iloc[2])


# ---------------------------------------------------------------------------
# W5 cognitive composite
# ---------------------------------------------------------------------------

def test_derive_w5_cog_composite_basic(synthetic_w5_df):
    """Composite is mean of z(C5WD90_1) + z(C5WD60_1) + z(BDS). With random
    integers it should be finite, mean ~0, and have positive std."""
    bds = derive_w5_bds(synthetic_w5_df)
    out = derive_w5_cog_composite(synthetic_w5_df, bds)
    assert out.shape == (len(synthetic_w5_df),)
    assert not out.dropna().empty
    assert abs(out.dropna().mean()) < 0.5
    assert out.dropna().std() > 0


def test_derive_w5_cog_composite_propagates_nan(synthetic_w5_df):
    """One respondent with all three components NaN should get NaN composite."""
    df = synthetic_w5_df.copy()
    df.at[0, "C5WD90_1"] = np.nan
    df.at[0, "C5WD60_1"] = np.nan
    bds = derive_w5_bds(df)
    bds.iloc[0] = np.nan
    out = derive_w5_cog_composite(df, bds)
    assert pd.isna(out.iloc[0])


# ---------------------------------------------------------------------------
# School belonging
# ---------------------------------------------------------------------------

def test_derive_school_belonging_double_reverse(synthetic_w1_df):
    """Row 0 has all six belonging items = 1; reversed (6 - x) -> 5 each ->
    sum = 30."""
    out = derive_school_belonging(synthetic_w1_df)
    assert out.iloc[0] == 30.0


def test_derive_school_belonging_all_missing_yields_nan():
    """All six belonging items NaN -> NaN (min_count=6)."""
    df = pd.DataFrame([{c: np.nan for c in
                        ["H1ED19", "H1ED20", "H1ED21", "H1ED22",
                         "H1ED23", "H1ED24"]}])
    out = derive_school_belonging(df)
    assert pd.isna(out.iloc[0])


def test_derive_school_belonging_partial_missing_yields_nan():
    """Five of six items present -> below min_count=6 -> NaN."""
    rec = {c: 1.0 for c in ["H1ED19", "H1ED20", "H1ED21", "H1ED22", "H1ED23"]}
    rec["H1ED24"] = np.nan
    df = pd.DataFrame([rec])
    out = derive_school_belonging(df)
    assert pd.isna(out.iloc[0])


# ---------------------------------------------------------------------------
# Race / ethnicity
# ---------------------------------------------------------------------------

def test_derive_race_ethnicity_categories(synthetic_w1_df):
    out = derive_race_ethnicity(synthetic_w1_df)
    assert out.iloc[3] == "Hispanic"
    assert out.iloc[4] == "NH-White"
    assert out.iloc[5] == "NH-Black"
    assert out.iloc[6] == "Other"


def test_derive_race_ethnicity_all_missing_returns_na():
    """When hispanic/white/black are all NaN, the result must be missing
    (pd.NA) for that row.
    """
    df = pd.DataFrame([{"H1GI4": np.nan, "H1GI6A": np.nan, "H1GI6B": np.nan}])
    out = derive_race_ethnicity(df)
    assert pd.isna(out.iloc[0])


def test_derive_race_ethnicity_hispanic_overrides_race():
    """Hispanic=1 must override any white/black flag."""
    df = pd.DataFrame([{"H1GI4": 1.0, "H1GI6A": 1.0, "H1GI6B": 1.0}])
    out = derive_race_ethnicity(df)
    assert out.iloc[0] == "Hispanic"


def test_derive_race_ethnicity_black_subsumed_when_white_and_black():
    """Hispanic=0 + black=1 -> NH-Black (even when white also = 1)."""
    df = pd.DataFrame([{"H1GI4": 0.0, "H1GI6A": 1.0, "H1GI6B": 1.0}])
    out = derive_race_ethnicity(df)
    assert out.iloc[0] == "NH-Black"


# ---------------------------------------------------------------------------
# Parent education
# ---------------------------------------------------------------------------

def test_derive_parent_ed_max_recodes(synthetic_w1_df):
    """Row 7: mom 7 -> 5, dad 4 -> 2 -> max = 5.
    Row 8: both 9 -> 0 -> 0.
    Row 9: mom 99 (NaN), dad 4 -> 2 -> max ignores NaN -> 2.
    """
    out = derive_parent_ed(synthetic_w1_df)
    assert out.iloc[7] == 5.0
    assert out.iloc[8] == 0.0
    assert out.iloc[9] == 2.0


def test_derive_parent_ed_both_missing_yields_nan():
    df = pd.DataFrame([{"H1RM1": np.nan, "H1RF1": np.nan}])
    out = derive_parent_ed(df)
    assert pd.isna(out.iloc[0])


def test_derive_parent_ed_recoded_ordinal_mapping():
    """Verify each input code maps to the documented ordinal:
        9 -> 0; 1,2,3 -> 1; 4 -> 2; 5 -> 3; 6 -> 4; 7 -> 5; 8/10/11 -> 6.
    """
    inputs = pd.DataFrame({
        "H1RM1": [9.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 11.0],
        "H1RF1": [9.0] * 10,  # always lower
    })
    out = derive_parent_ed(inputs)
    expected = [0, 1, 1, 1, 2, 3, 4, 5, 6, 6]
    assert out.tolist() == [float(x) for x in expected]


# ---------------------------------------------------------------------------
# Friendship grid
# ---------------------------------------------------------------------------

def test_derive_friendship_grid_nomination_count(synthetic_w1_df):
    """Row 0 has exactly 1 nominated slot (H1MF2A=1) with all five contact
    items=1. Row 1 has H1MF2A=7 -> not nominated."""
    grid = derive_friendship_grid(synthetic_w1_df)
    assert grid["FRIEND_N_NOMINEES"].iloc[0] == 1
    assert grid["FRIEND_CONTACT_SUM"].iloc[0] == 5.0
    assert grid["FRIEND_DISCLOSURE_ANY"].iloc[0] == 1
    assert grid["FRIEND_N_NOMINEES"].iloc[1] == 0
    assert grid["FRIEND_CONTACT_SUM"].iloc[1] == 0.0
    assert grid["FRIEND_DISCLOSURE_ANY"].iloc[1] == 0


def test_derive_friendship_grid_contact_sum_aggregates_across_slots():
    """Two nominated slots, contact items 1 in slot A and 1 in slot B -> sum = 2."""
    rec = {}
    # Make MF block: nominate slots A and B, in-school = 0 to count as nominated
    for s in "ABCDE":
        rec[f"H1MF2{s}"] = 7.0
    rec["H1MF2A"] = 0.0
    rec["H1MF2B"] = 0.0
    # Contact items 6-10 = 0 in slot A except item 6=1; slot B item 10=1
    for s in "ABCDE":
        for item in [6, 7, 8, 9, 10]:
            rec[f"H1MF{item}{s}"] = 0.0
    rec["H1MF6A"] = 1.0
    rec["H1MF10B"] = 1.0
    # FF block: no nominations
    for s in "ABCDE":
        rec[f"H1FF2{s}"] = 7.0
        for item in [6, 7, 8, 9, 10]:
            rec[f"H1FF{item}{s}"] = 0.0
    df = pd.DataFrame([rec])
    grid = derive_friendship_grid(df)
    assert grid["FRIEND_N_NOMINEES"].iloc[0] == 2
    assert grid["FRIEND_CONTACT_SUM"].iloc[0] == 2.0


def test_derive_friendship_grid_disclosure_any_flag():
    """Disclosure (item 9) = 1 in any nominated slot -> flag = 1; else 0."""
    rec = {}
    for s in "ABCDE":
        rec[f"H1MF2{s}"] = 7.0
        for item in [6, 7, 8, 9, 10]:
            rec[f"H1MF{item}{s}"] = 0.0
    # Nominate slot A; disclosure in slot A item 9 = 1
    rec["H1MF2A"] = 0.0
    rec["H1MF9A"] = 1.0
    for s in "ABCDE":
        rec[f"H1FF2{s}"] = 7.0
        for item in [6, 7, 8, 9, 10]:
            rec[f"H1FF{item}{s}"] = 0.0
    df = pd.DataFrame([rec])
    grid = derive_friendship_grid(df)
    assert grid["FRIEND_DISCLOSURE_ANY"].iloc[0] == 1


def test_derive_friendship_grid_reserve_codes_not_counted():
    """When a contact item carries a reserve code (e.g. 7=skip), it must
    contribute 0 to the contact sum, not a positive count.
    """
    rec = {}
    for s in "ABCDE":
        rec[f"H1MF2{s}"] = 7.0
        for item in [6, 7, 8, 9, 10]:
            rec[f"H1MF{item}{s}"] = 7.0  # legit-skip everywhere
    rec["H1MF2A"] = 0.0  # nominated slot
    # Contact items in A all carry reserve code 7 -> filtered to 0 -> sum 0
    for s in "ABCDE":
        rec[f"H1FF2{s}"] = 7.0
        for item in [6, 7, 8, 9, 10]:
            rec[f"H1FF{item}{s}"] = 0.0
    df = pd.DataFrame([rec])
    grid = derive_friendship_grid(df)
    assert grid["FRIEND_N_NOMINEES"].iloc[0] == 1
    assert grid["FRIEND_CONTACT_SUM"].iloc[0] == 0.0
    assert grid["FRIEND_DISCLOSURE_ANY"].iloc[0] == 0


def test_friendship_grid_constants_match_spec():
    """Spot-check FRIEND_* constants against codebook description."""
    assert FRIEND_SLOTS == ["A", "B", "C", "D", "E"]
    assert FRIEND_ITEMS_CONTACT == [6, 7, 8, 9, 10]
    assert FRIEND_ITEM_DISCLOSURE == 9

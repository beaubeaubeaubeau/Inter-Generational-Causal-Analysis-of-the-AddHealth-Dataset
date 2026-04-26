"""Derived-variable constructors used across waves.

Functions:
  - ``derive_cesd_sum`` (W1 CES-D 19-item sum, items 4/8/11/15 reverse-scored)
  - ``derive_w5_bds`` (Wave 5 backward-digit-span ascending-difficulty score)
  - ``derive_w4_cog_composite`` / ``derive_w5_cog_composite`` (per-wave z-mean)
  - ``derive_school_belonging`` (5+1 belonging items, double-reverse on H1ED21)
  - ``derive_race_ethnicity`` (NH-White / NH-Black / Hispanic / Other)
  - ``derive_parent_ed`` (max(mother, father) education on a 0-6 ordinal)
  - ``derive_friendship_grid`` (nominees + contact-intensity + disclosure)

Constants ``CESD_ITEMS``, ``CESD_REVERSE``, ``FRIEND_SLOTS``,
``FRIEND_ITEMS_CONTACT``, ``FRIEND_ITEM_DISCLOSURE`` are exposed for
downstream tests and scripts that re-derive on a different frame.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .cleaning import clean_var

CESD_ITEMS = [f"H1FS{i}" for i in range(1, 20)]
CESD_REVERSE = {4, 8, 11, 15}


def derive_cesd_sum(df: pd.DataFrame, min_valid: int = 15) -> pd.Series:
    """Sum of the 19 CES-D items with items 4/8/11/15 reverse-scored.

    Default ``min_valid=15``: at least 15 of the 19 items must be present;
    fewer → NaN. Respondents with 15-19 valid items get a *scaled* sum
    (``raw_sum * 19 / n_valid``) so the result is on the canonical 0-57 scale
    regardless of how many items they answered. This is more permissive than
    strict listwise (``min_valid=19``); per the project decision (2026-04-26)
    the 4-item tolerance is acceptable to avoid zeroing respondents with a
    single missing item.

    Reverse-scored items (4, 8, 11, 15) propagate NaN through ``3 - NaN``,
    so a NaN at any reverse item still counts as missing.
    """
    cleaned = pd.DataFrame({v: clean_var(df[v], v) for v in CESD_ITEMS})
    for idx in CESD_REVERSE:
        col = f"H1FS{idx}"
        cleaned[col] = 3 - cleaned[col]
    raw_sum = cleaned.sum(axis=1, min_count=min_valid)
    n_valid = cleaned.notna().sum(axis=1)
    # Scale to the 19-item-equivalent total. Where n_valid < min_valid,
    # raw_sum is already NaN (min_count); leave NaN.
    scaled = raw_sum * (len(CESD_ITEMS) / n_valid.replace(0, np.nan))
    return scaled


def derive_w5_bds(df: pd.DataFrame) -> pd.Series:
    n = len(df)
    # float dtype is required: np.nan can't be assigned to an int array.
    score = np.zeros(n, dtype=float)
    item_cols = [f"H5MH{L+1}{s}" for L in range(2, 9) for s in "AB"]
    cleaned = {c: clean_var(df[c], c) for c in item_cols}
    all_missing_mask = np.ones(n, dtype=bool)
    for c, s in cleaned.items():
        all_missing_mask &= s.isna().values
    for L in range(2, 9):
        a = cleaned[f"H5MH{L+1}A"].values
        b = cleaned[f"H5MH{L+1}B"].values
        success = (a == 1) | (b == 1)
        score = np.where(success, float(L), score)
    out = pd.Series(score, index=df.index, dtype=float)
    out[all_missing_mask] = np.nan
    return out


def _zscore(s: pd.Series) -> pd.Series:
    mu = s.mean(skipna=True)
    sd = s.std(skipna=True)
    return (s - mu) / sd if sd and not np.isnan(sd) and sd > 0 else s * np.nan


def derive_w4_cog_composite(df: pd.DataFrame) -> pd.Series:
    """Mean of individually z-scored C4WD90_1, C4WD60_1, C4NUMSCR."""
    z1 = _zscore(clean_var(df["C4WD90_1"], "C4WD90_1"))
    z2 = _zscore(clean_var(df["C4WD60_1"], "C4WD60_1"))
    z3 = _zscore(clean_var(df["C4NUMSCR"], "C4NUMSCR"))
    comp = pd.concat([z1, z2, z3], axis=1).mean(axis=1, skipna=False)
    return comp


def derive_w5_cog_composite(df: pd.DataFrame, bds: pd.Series) -> pd.Series:
    z1 = _zscore(clean_var(df["C5WD90_1"], "C5WD90_1"))
    z2 = _zscore(clean_var(df["C5WD60_1"], "C5WD60_1"))
    z3 = _zscore(bds)
    comp = pd.concat([z1, z2, z3], axis=1).mean(axis=1, skipna=False)
    return comp


def derive_school_belonging(df: pd.DataFrame) -> pd.Series:
    """Sum of belonging items, reverse-scored so higher = more belonging.

    H1ED19 close, H1ED20 part-of, H1ED22 happy, H1ED23 teachers fair, H1ED24 safe:
        1=strongly agree -> reverse to 5 (more belonging)
    H1ED21 prejudiced:
        keep as-is so higher = more prejudice = less belonging (include with sign flip).
    Reported sum reflects higher = more belonging.
    """
    cols = ["H1ED19", "H1ED20", "H1ED22", "H1ED23", "H1ED24"]
    vals = pd.DataFrame({c: 6 - clean_var(df[c], c) for c in cols})  # reverse
    # H1ED21 reversed: higher raw = more prejudice -> invert so all items point with belonging.
    vals["H1ED21_rev"] = clean_var(df["H1ED21"], "H1ED21")
    vals["H1ED21_rev"] = 6 - vals["H1ED21_rev"]
    return vals.sum(axis=1, min_count=6)


def derive_race_ethnicity(df: pd.DataFrame) -> pd.Series:
    """4-level: NH-white, NH-Black, Hispanic (any race), Other."""
    hisp = clean_var(df["H1GI4"], "H1GI4")
    white = clean_var(df["H1GI6A"], "H1GI6A")
    black = clean_var(df["H1GI6B"], "H1GI6B")
    race = pd.Series(pd.NA, index=df.index, dtype="object")
    race[hisp == 1] = "Hispanic"
    race[(hisp == 0) & (white == 1) & (black != 1)] = "NH-White"
    race[(hisp == 0) & (black == 1)] = "NH-Black"
    race[race.isna() & hisp.notna() & white.notna() & black.notna()] = "Other"
    return race


def derive_parent_ed(df: pd.DataFrame) -> pd.Series:
    """Teen-reported max(mother, father) education on a 0-6 ordinal.

    H1RM1/H1RF1 W1 codebook codes:
      1 = 8th grade or less
      2 = more than 8th but did not graduate from HS
      3 = went to business/trade/vocational *instead of* HS
      4 = HS grad
      5 = went to business/trade/vocational *after* HS
      6 = went to college, did not graduate
      7 = graduated from college
      8 = professional training beyond a 4-year college (post-bachelor's: MA/JD/MD/PhD)
      9 = never went to school

    Codes 10/11/12 ("other / don't know / NA") are stripped to NaN at the
    ``clean_var`` stage via ``VALID_RANGES["H1RM1"] = (1, 9)`` and so do
    NOT enter the recode below. Previously (pre-2026-04-26) those codes
    were silently mapped to ordinal 6, biasing parent_ed upward for
    respondents with missing data.

    Resulting ordinal:
      0 = never went to school (code 9)
      1 = less than HS (codes 1, 2, 3)
      2 = HS grad (code 4)
      3 = post-HS vocational (code 5)
      4 = some college (code 6)
      5 = college grad (code 7)
      6 = post-grad / professional training (code 8)
    """
    def recode(x, name):
        x = clean_var(x, name)
        out = pd.Series(np.nan, index=x.index, dtype=float)
        out[x == 9] = 0
        out[x.isin([1, 2, 3])] = 1
        out[x == 4] = 2
        out[x == 5] = 3
        out[x == 6] = 4
        out[x == 7] = 5
        out[x == 8] = 6  # post-grad ONLY (codes 10/11 are NaN, not 6)
        return out
    m = recode(df["H1RM1"], "H1RM1")
    f = recode(df["H1RF1"], "H1RF1")
    return pd.concat([m, f], axis=1).max(axis=1, skipna=True)


# Grid indexing (per W1 codebook, confirmed from w1inhome labels):
#   digit 2..10 = item number within each friend's block:
#     2 = in your school?       3 = grade
#     4 = sample school?        5 = sister school?
#     6 = went to friend's house (past 7 days)
#     7 = met after school (past 7 days)
#     8 = spent time last weekend
#     9 = talked about a problem (past 7 days)
#     10 = talked on the phone (past 7 days)
#   letter A..E = friend slot (1st-5th nominated friend).
# So `H1MF2A` = "is 1st male friend in your school?"
#    `H1MF10E` = "did you talk on phone with 5th male friend?"
FRIEND_SLOTS = ["A", "B", "C", "D", "E"]     # 5 friends per gender -> 10 max
# Contact items are past-7-day non-disclosure interaction items. Item 9
# ("talked about a problem") is the disclosure anchor and is NOT counted in
# contact-sum to avoid double-counting it as both contact intensity and
# disclosure (decision 2026-04-26).
FRIEND_ITEMS_CONTACT = [6, 7, 8, 10]
FRIEND_ITEM_DISCLOSURE = 9                    # "talked about a problem"


def derive_friendship_grid(df: pd.DataFrame) -> pd.DataFrame:
    """Derive total nominees + contact-intensity from H1MF/H1FF grid.

    A friend *slot* is counted as nominated when the "is in your school" item
    (digit 2) has a valid response (0 or 1). Legit-skip (7) and any other
    non-{0,1} value mean no nomination *for that slot*.

    Per-respondent semantics (2026-04-26 decision):
      * If ALL 10 anchor items (H1MF2A..E + H1FF2A..E) are NaN, the
        respondent is treated as having no friendship-grid data — the three
        returned columns are NaN.
      * Otherwise, total_noms / contact_sum / disclosure_any are computed
        from whichever slots have a valid anchor.

    Contact-intensity sums 0/1 responses across items 6, 7, 8, 10 (item 9
    is the disclosure anchor and is NOT included in contact-sum so the two
    columns measure non-overlapping aspects of friendship intensity).
    Disclosure is any item-9 = 1 across nominated slots.
    """
    total_noms = pd.Series(0, index=df.index, dtype=int)
    contact_intensity = pd.Series(0.0, index=df.index, dtype=float)
    disclosure = pd.Series(0, index=df.index, dtype=int)
    # Track which respondents have at least one valid anchor item somewhere.
    any_anchor = pd.Series(False, index=df.index)

    for prefix in ["H1MF", "H1FF"]:
        for slot in FRIEND_SLOTS:
            in_school_col = f"{prefix}2{slot}"
            if in_school_col not in df.columns:
                continue
            anchor_valid = df[in_school_col].isin([0, 1])
            any_anchor = any_anchor | df[in_school_col].notna()
            nominated = anchor_valid
            total_noms = total_noms + nominated.astype(int)
            for item in FRIEND_ITEMS_CONTACT:
                c = f"{prefix}{item}{slot}"
                if c in df.columns:
                    v = df[c].where(df[c].isin([0, 1])).fillna(0)
                    contact_intensity = contact_intensity + (v * nominated.astype(int))
            dcol = f"{prefix}{FRIEND_ITEM_DISCLOSURE}{slot}"
            if dcol in df.columns:
                v = df[dcol].where(df[dcol].isin([0, 1])).fillna(0)
                disclosure = disclosure + ((v == 1) & nominated).astype(int)

    out = pd.DataFrame({
        "FRIEND_N_NOMINEES": total_noms.astype(float),
        "FRIEND_CONTACT_SUM": contact_intensity,
        "FRIEND_DISCLOSURE_ANY": (disclosure > 0).astype(float),
    })
    # Propagate NaN for respondents with no observable anchor data anywhere.
    no_data = ~any_anchor
    out.loc[no_data, :] = np.nan
    return out

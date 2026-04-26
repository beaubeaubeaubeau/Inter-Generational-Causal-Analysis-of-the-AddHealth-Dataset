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


def derive_cesd_sum(df: pd.DataFrame) -> pd.Series:
    """Sum of the 19 CES-D items with items 4/8/11/15 reverse-scored.

    Returns NaN if ANY of the 19 items is missing (``min_count=19``);
    reverse-scored items propagate NaN through ``3 - NaN``. Strict listwise
    by design — one missing item zeroes the respondent's score.
    """
    cleaned = pd.DataFrame({v: clean_var(df[v], v) for v in CESD_ITEMS})
    for idx in CESD_REVERSE:
        col = f"H1FS{idx}"
        cleaned[col] = 3 - cleaned[col]
    return cleaned.sum(axis=1, min_count=19)


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
    """Teen-reported max(mother, father) education using valid-range filter.

    H1RM1/H1RF1 codes (approx per W1 codebook):
      1 = 8th grade or less
      2 = more than 8, less than HS
      3 = business/trade/vocational, instead of HS
      4 = HS grad
      5 = business/trade/vocational after HS
      6 = some college
      7 = college grad
      8 = professional training beyond college
      9 = never went to school
      10, 11 = other / don't know / NA via reserves
    We collapse to an ordinal 0-7 scale: 0 = never, 1 = <HS, 2 = HS,
    3 = post-HS voc, 4 = some college, 5 = college, 6 = post-grad.
    """
    def recode(x):
        x = clean_var(x, "H1RM1")
        out = pd.Series(np.nan, index=x.index, dtype=float)
        out[x == 9] = 0
        out[x.isin([1, 2, 3])] = 1
        out[x == 4] = 2
        out[x == 5] = 3
        out[x == 6] = 4
        out[x == 7] = 5
        out[x.isin([8, 10, 11])] = 6
        return out
    m = recode(df["H1RM1"])
    f = recode(df["H1RF1"])
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
FRIEND_ITEMS_CONTACT = [6, 7, 8, 9, 10]      # past-7-day interaction items
FRIEND_ITEM_DISCLOSURE = 9                    # "talked about a problem"


def derive_friendship_grid(df: pd.DataFrame) -> pd.DataFrame:
    """Derive total nominees + contact-intensity from H1MF/H1FF grid.

    A friend *slot* is counted as nominated when the "is in your school" item
    (digit 2) has a valid response (0 or 1). Legit-skip (7) and NA mean no
    nomination. Contact-intensity sums 0/1 responses across items 6-10 over
    all nominated slots; disclosure is any item-9 = 1.
    """
    total_noms = pd.Series(0, index=df.index, dtype=int)
    contact_intensity = pd.Series(0.0, index=df.index, dtype=float)
    disclosure = pd.Series(0, index=df.index, dtype=int)

    for prefix in ["H1MF", "H1FF"]:
        for slot in FRIEND_SLOTS:
            in_school_col = f"{prefix}2{slot}"
            if in_school_col not in df.columns:
                continue
            nominated = df[in_school_col].isin([0, 1])
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

    return pd.DataFrame({
        "FRIEND_N_NOMINEES": total_noms,
        "FRIEND_CONTACT_SUM": contact_intensity,
        "FRIEND_DISCLOSURE_ANY": (disclosure > 0).astype(int),
    })

"""Variable-cleaning utilities: ``VALID_RANGES``, ``clean_var``, ``neg_control_outcome``.

Reserve codes ({6,7,8,9, 96-99, 95, 995-999, 9995}) are scrubbed implicitly
through per-variable valid ranges. ``neg_control_outcome`` constructs the
HEIGHT_IN negative-control outcome used by task13 / cognitive-screening.
"""
from __future__ import annotations

import warnings
from typing import Dict, Tuple

import pandas as pd

from . import CACHE

# ---------------------------------------------------------------------------
# Valid ranges (min, max inclusive) - anything outside -> NaN.
# Reserve codes {6,7,8,9, 96-99, 95, 995-999, 9995} drop out via these ranges.
# ---------------------------------------------------------------------------
VALID_RANGES: Dict[str, Tuple[float, float]] = {
    # W1 network
    "IDGX2": (0, 50), "ODGX2": (0, 50), "BCENT10X": (-1e6, 1e6),
    "REACH": (0, 5000), "REACH3": (0, 5000),
    "PRXPREST": (0, 1), "INFLDMN": (0, 5000),
    "IGDMEAN": (0, 100),
    "ESDEN": (0, 1), "ERDEN": (0, 1), "ESRDEN": (0, 1), "RCHDEN": (0, 1),
    "HAVEBMF": (0, 1), "HAVEBFF": (0, 1),
    "BMFRECIP": (0, 1), "BFFRECIP": (0, 1),
    # W1 daily activity / belonging / loneliness
    "H1DA7": (0, 3),
    "H1ED19": (1, 5), "H1ED20": (1, 5), "H1ED21": (1, 5),
    "H1ED22": (1, 5), "H1ED23": (1, 5), "H1ED24": (1, 5),
    # W1 baseline cognitive + demographics
    "AH_PVT": (0, 200), "AH_RAW": (0, 87),
    "BIO_SEX": (1, 2),
    "H1GI1M": (1, 12),  # birth month; 96 = refused, 97 = legit-skip, 98 = DK, 99 = NA
    "H1GI4": (0, 1),
    "H1GI6A": (0, 1), "H1GI6B": (0, 1), "H1GI6C": (0, 1),
    "H1GI6D": (0, 1), "H1GI6E": (0, 1),
    "H1GH1": (1, 5),
    # Parent ed: only codes 1-9 are substantive (1=8th-or-less, 2=>8 not HS,
    # 3=trade-instead-of-HS, 4=HS grad, 5=trade-after-HS, 6=some college,
    # 7=college grad, 8=professional-training-beyond-college, 9=never-went-to-
    # school). Codes 10/11/12 are "other / don't know / NA" — strip to NaN
    # so that `derive_parent_ed` does not silently lump unknowns with code 8.
    "H1RM1": (1, 9), "H1RF1": (1, 9),
    "PA12": (1, 9),
    # Household income (thousands, top-coded); treat 0-500 as valid
    "PA55": (0, 500),
    # CES-D items
    **{f"H1FS{i}": (0, 3) for i in range(1, 20)},
    # CES-D summed score: 19 items each 0-3 -> theoretical (0, 57). Observed
    # max in the W1 cohort tops out near 50; cap matches the item range. The
    # derived variable was already cleaned at construction time but is
    # registered here so `clean_var` does not warn when downstream
    # experiments (e.g. em-depression-buffering) pass it through defensively.
    "CESD_SUM": (0, 57),
    # W4 cognitive
    "C4WD90_1": (0, 15), "C4WD60_1": (0, 15), "C4NUMSCR": (0, 7),
    "C4WD90_2": (0, 15), "C4WD90_3": (0, 15),
    "C4WD60_2": (0, 15), "C4WD60_3": (0, 15),
    # W5 cognitive
    "C5WD90_1": (0, 15), "C5WD60_1": (0, 15),
    # W4 cardiometabolic (in-home Section 27 measures)
    "H4BMI": (10, 80), "H4SBP": (50, 250), "H4DBP": (30, 180),
    "H4WAIST": (40, 200), "H4BMICLS": (1, 6),
    # W5 non-cognitive outcomes
    "H5MN1": (1, 5), "H5MN2": (1, 5),
    "H5ID1": (1, 5), "H5ID4": (1, 3), "H5ID16": (0, 4),
    "H5LM5": (1, 3), "H5EC1": (1, 13),
    # Derived W1 indicator/exposure variables (already cleaned at derivation time;
    # registered here so clean_var doesn't emit a warning when downstream
    # experiments pass them through defensively).
    "IDG_ZERO": (0, 1), "IDG_LEQ1": (0, 1),
    "FRIEND_DISCLOSURE_ANY": (0, 1),
    "FRIEND_N_NOMINEES": (0, 10),
    "FRIEND_CONTACT_SUM": (0, 40),  # max = 4 contact items × 10 nominees
    "SCHOOL_BELONG": (0, 30),       # max = 6 items × 5 (post-reverse)
    # Derived parental education (max of H1RM1 / H1RF1 recoded to 0-6 ordinal:
    # 0 = <HS, ..., 6 = professional training beyond college). Already cleaned
    # at derivation time; registered so defensive `clean_var` calls don't warn.
    "PARENT_ED": (0, 6),
    # PCA-derived composite (no clipping; identity-pass with warning suppressed).
    "POLYSOCIAL_PC1": (-1e6, 1e6),
    # W4/W5 substance-use items (popularity-and-substance-use experiment).
    # H4TO5 / H5TO2: smoking days past 30 days (count 0-30); refuse/DK = 96/98.
    # H4TO39 / H4TO70 / H5TO12 / H5TO15: ordinal frequency 0-6 over the look-back
    # window. Code 97 ("legitimate skip" — never drank / never used) is a real
    # zero exposure but is OUTSIDE the substantive 0-6 range; per-experiment
    # callers must impute 97 -> 0 BEFORE calling clean_var (clean_var strips
    # 97 to NaN through the (0, 6) gate). Refuse/DK = 96/98.
    # H4TO65B / H4TO65C: binary 0/1 (ever used MJ / cocaine); refuse/DK = 6/8.
    "H4TO5": (0, 30),
    "H4TO39": (0, 6),
    "H4TO70": (0, 6),
    "H4TO65B": (0, 1),
    "H4TO65C": (0, 1),
    "H5TO2": (0, 30),
    "H5TO12": (0, 6),
    "H5TO15": (0, 6),
}
for L in range(3, 10):
    for suf in ("A", "B"):
        VALID_RANGES[f"H5MH{L}{suf}"] = (0, 1)


def clean_var(s: pd.Series, name: str) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    if name in VALID_RANGES:
        lo, hi = VALID_RANGES[name]
        s = s.where((s >= lo) & (s <= hi))
    else:
        # Reserve-code stripping is opt-in via VALID_RANGES; warn so callers
        # don't silently consume a variable with codes 6/7/8/9 / 96–99 etc.
        warnings.warn(
            f"clean_var called on {name!r} which is not in VALID_RANGES; "
            f"passing through unstripped (reserve codes may contaminate the result).",
            stacklevel=2,
        )
    return s


def neg_control_outcome(aid: pd.Series) -> pd.Series:
    """HEIGHT_IN (total inches) for each AID.

    Reads W4 in-home H4GH5F (feet, valid 4-7) and H4GH5I (inches, valid 0-11),
    combines into total inches. Returns a float Series aligned to the input.
    Replicates the task13_verification.py construction.
    """
    w4 = pd.read_parquet(CACHE / "w4inhome.parquet")[["AID", "H4GH5F", "H4GH5I"]].copy()
    feet = pd.to_numeric(w4["H4GH5F"], errors="coerce").where(
        lambda s: s.between(4, 7)
    )
    inch = pd.to_numeric(w4["H4GH5I"], errors="coerce").where(
        lambda s: s.between(0, 11)
    )
    w4["HEIGHT_IN"] = feet * 12 + inch
    m = pd.DataFrame({"AID": aid}).merge(
        w4[["AID", "HEIGHT_IN"]], on="AID", how="left"
    )
    m.index = aid.index
    return m["HEIGHT_IN"]

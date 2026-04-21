"""Shared utilities for the Wave I network -> Wave IV/V cognitive analysis.

Provides:
  - VALID_RANGES: reserve-code-aware valid-range dict (extends task05)
  - clean_var(): numeric coercion + valid-range filter
  - weighted_mean_se(): cluster-robust linearized SE for a weighted mean
  - weighted_prop_ci(): weighted proportion with logit 95% CI
  - weighted_ols(): weighted OLS with cluster-robust variance on CLUSTER2
                    (use_t=True, df = n_psu - 1)
  - load_*() helpers backed by cached parquets
  - derive_cesd_sum, derive_w5_bds, derive_w4_cog_composite,
    derive_w5_cog_composite, derive_school_belonging,
    derive_race_ethnicity, derive_parent_ed, derive_friendship_grid
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

ROOT = Path("/Users/jb/Desktop/Inter-Generational-Causal-Analysis-of-the-AddHealth-Dataset")
DATA = ROOT / "data"
CACHE = ROOT / "outputs" / "cache"

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
    "H1GI4": (0, 1),
    "H1GI6A": (0, 1), "H1GI6B": (0, 1), "H1GI6C": (0, 1),
    "H1GI6D": (0, 1), "H1GI6E": (0, 1),
    "H1GH1": (1, 5),
    # Parent ed: 1=<8th grade, ..., 11=never went to school; 12=did not go/not finish HS; skip reserves
    "H1RM1": (1, 11), "H1RF1": (1, 11),
    "PA12": (1, 11),
    # Household income (thousands, top-coded); treat 0-500 as valid
    "PA55": (0, 500),
    # CES-D items
    **{f"H1FS{i}": (0, 3) for i in range(1, 20)},
    # W4 cognitive
    "C4WD90_1": (0, 15), "C4WD60_1": (0, 15), "C4NUMSCR": (0, 7),
    "C4WD90_2": (0, 15), "C4WD90_3": (0, 15),
    "C4WD60_2": (0, 15), "C4WD60_3": (0, 15),
    # W5 cognitive
    "C5WD90_1": (0, 15), "C5WD60_1": (0, 15),
}
for L in range(3, 10):
    for suf in ("A", "B"):
        VALID_RANGES[f"H5MH{L}{suf}"] = (0, 1)

CESD_ITEMS = [f"H1FS{i}" for i in range(1, 20)]
CESD_REVERSE = {4, 8, 11, 15}


# ---------------------------------------------------------------------------
# Core cleaning / survey-weighted statistics
# ---------------------------------------------------------------------------
def clean_var(s: pd.Series, name: str) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    if name in VALID_RANGES:
        lo, hi = VALID_RANGES[name]
        s = s.where((s >= lo) & (s <= hi))
    return s


def weighted_mean_se(y, w, psu) -> Tuple[float, float, float, int, int]:
    y = np.asarray(y, dtype=float)
    w = np.asarray(w, dtype=float)
    psu = np.asarray(psu)
    mask = ~np.isnan(y) & ~np.isnan(w) & (w > 0)
    y, w, psu = y[mask], w[mask], psu[mask]
    n = len(y)
    if n == 0:
        return (np.nan, np.nan, np.nan, 0, 0)
    W = w.sum()
    mean = float(np.sum(w * y) / W)
    sd = float(np.sqrt(np.sum(w * (y - mean) ** 2) / W))
    u_i = w * (y - mean)
    df = pd.DataFrame({"u": u_i, "psu": psu})
    u_h = df.groupby("psu")["u"].sum().values
    H = len(u_h)
    if H < 2:
        return (mean, sd, np.nan, n, H)
    u_bar = u_h.mean()
    var_mean = (H / (H - 1.0)) * np.sum((u_h - u_bar) ** 2) / (W ** 2)
    se = float(np.sqrt(max(var_mean, 0.0)))
    return (mean, sd, se, n, H)


def weighted_prop_ci(ind, w, psu) -> Tuple[float, float, float, float, int, int]:
    p, _sd, se, n, H = weighted_mean_se(np.asarray(ind, dtype=float), w, psu)
    if np.isnan(p) or np.isnan(se) or p <= 0 or p >= 1:
        lo = np.nan if np.isnan(p) else max(0.0, p - 1.96 * (se if not np.isnan(se) else 0.0))
        hi = np.nan if np.isnan(p) else min(1.0, p + 1.96 * (se if not np.isnan(se) else 0.0))
        return (p, se, lo, hi, n, H)
    logit = np.log(p / (1 - p))
    se_logit = se / (p * (1 - p))
    lo = 1 / (1 + np.exp(-(logit - 1.96 * se_logit)))
    hi = 1 / (1 + np.exp(-(logit + 1.96 * se_logit)))
    return (p, se, lo, hi, n, H)


def weighted_ols(
    y: np.ndarray, X: np.ndarray, w: np.ndarray, psu: np.ndarray,
    column_names: Optional[List[str]] = None,
):
    """Weighted OLS with cluster-robust variance on `psu`.

    Returns a dict with beta (pd.Series), se, t, p, ci_lo, ci_hi,
    n, n_psu, r2_weighted, df_resid. Uses statsmodels OLS fit with weights
    and cov_type='cluster', use_t=True, df adjustment = (n_psu - 1).

    X must include a constant column.
    """
    import statsmodels.api as sm

    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    w = np.asarray(w, dtype=float)
    psu = np.asarray(psu)
    mask = (
        ~np.isnan(y)
        & ~np.isnan(w)
        & (w > 0)
        & ~np.isnan(X).any(axis=1)
    )
    y, X, w, psu = y[mask], X[mask], w[mask], psu[mask]
    n = len(y)
    H = len(np.unique(psu))
    if n == 0 or H < 2:
        return None
    model = sm.WLS(y, X, weights=w)
    res = model.fit(
        cov_type="cluster",
        cov_kwds={"groups": psu, "use_correction": True},
        use_t=True,
    )
    # statsmodels uses df = n - k by default. For cluster-robust inference
    # we override t-stats against df = H - 1 (common convention).
    import scipy.stats as stats
    df_cluster = H - 1
    t_stats = res.params / res.bse
    p_vals = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=df_cluster))
    crit = stats.t.ppf(0.975, df=df_cluster)
    ci_lo = res.params - crit * res.bse
    ci_hi = res.params + crit * res.bse

    names = column_names if column_names is not None else [f"x{i}" for i in range(X.shape[1])]
    return {
        "beta": pd.Series(res.params, index=names),
        "se": pd.Series(res.bse, index=names),
        "t": pd.Series(t_stats, index=names),
        "p": pd.Series(p_vals, index=names),
        "ci_lo": pd.Series(ci_lo, index=names),
        "ci_hi": pd.Series(ci_hi, index=names),
        "n": int(n),
        "n_psu": int(H),
        "df_resid": int(df_cluster),
        "rsquared": float(res.rsquared),
        "model": res,
    }


# ---------------------------------------------------------------------------
# Cache loaders
# ---------------------------------------------------------------------------
def _load_parquet(name: str) -> pd.DataFrame:
    path = CACHE / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Missing cached parquet: {path}")
    return pd.read_parquet(path)


def load_w1_network() -> pd.DataFrame:
    return _load_parquet("w1network")


def load_w1_inhome() -> pd.DataFrame:
    return _load_parquet("w1inhome")


def load_w4_inhome() -> pd.DataFrame:
    return _load_parquet("w4inhome")


def load_w5() -> pd.DataFrame:
    return _load_parquet("pwave5")


def load_w1_weight() -> pd.DataFrame:
    import pyreadstat
    df, _ = pyreadstat.read_sas7bdat(str(DATA / "W1" / "w1weight.sas7bdat"))
    return df[["AID", "CLUSTER2", "GSWGT1"]]


def load_w4_weight() -> pd.DataFrame:
    import pyreadstat
    df, _ = pyreadstat.read_sas7bdat(str(DATA / "W4" / "w4weight.sas7bdat"))
    return df[["AID", "CLUSTER2", "GSWGT4_2"]]


def load_w5_weight() -> pd.DataFrame:
    import pyreadstat
    df, _ = pyreadstat.read_xport(str(DATA / "W5" / "p5weight.xpt"))
    return df[["AID", "CLUSTER2", "GSW5"]]


# ---------------------------------------------------------------------------
# Derivations
# ---------------------------------------------------------------------------
def derive_cesd_sum(df: pd.DataFrame) -> pd.Series:
    cleaned = pd.DataFrame({v: clean_var(df[v], v) for v in CESD_ITEMS})
    for idx in CESD_REVERSE:
        col = f"H1FS{idx}"
        cleaned[col] = 3 - cleaned[col]
    return cleaned.sum(axis=1, min_count=19)


def derive_w5_bds(df: pd.DataFrame) -> pd.Series:
    n = len(df)
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
    vals["H1ED21_rev"] = clean_var(df["H1ED21"], "H1ED21")  # higher prejudice = stays
    # Flip prejudice so it adds in the same direction (less prejudice -> more belonging)
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

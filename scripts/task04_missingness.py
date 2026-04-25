"""Task 4: Empirical missingness profiling for the Add Health public-use
feasibility sweep.

For every variable in the target list (W1 network exposures, W1 in-home
friendship and CES-D items, W1 cognitive baseline, W3 AHPVT, W4 cognition,
W5 cognition plus mode-stratified tables, and W1 confounders), compute:

    * n_total, n_nonmissing (includes reserve codes), n_valid (excludes them)
    * pct_missing_true (pure NA)
    * pct_refused / pct_skip / pct_dk / pct_na / pct_not_asked  (reserve codes,
      chosen per-variable by value range)
    * for continuous vars: min_valid, max_valid, mean_valid, median_valid

Derived variables:
    * isolated flag  = (IDGX2 == 0 AND ODGX2 == 0)      [W1 network]
    * CES-D sum      = sum of 19 Likert items with items 4,8,11,15 reverse-
                       scored (0<->3, 1<->2)             [W1 in-home]
    * W5 digit span  = max length L in {2..8} such that H5MHLA == 1 OR
                       H5MHLB == 1, else 0               [W5]

Outputs:
    outputs/04_missingness_profile.csv
    outputs/04_missingness_profile.md
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pyreadstat

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "outputs"
CACHE = OUT / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

W1_NET = DATA / "W1" / "w1network.sas7bdat"
W1_IN = DATA / "W1" / "w1inhome.sas7bdat"
W3_PVT = DATA / "W3" / "w3pvt.sas7bdat"
W4_IN = DATA / "W4" / "w4inhome.sas7bdat"
W5_MAIN = DATA / "W5" / "pwave5.xpt"

CSV_OUT = OUT / "04_missingness_profile.csv"
MD_OUT = OUT / "04_missingness_profile.md"


# ---------------------------------------------------------------------------
# Reserve-code scheme selection and tallying
# ---------------------------------------------------------------------------
#
# Standard Add Health codes (one variant per scale-width):
#
#   2-digit scale (max valid typically <= 15):   6/7/8/9
#   3-digit scale (max valid < 95):             96/97/98/99    + Wave V: 95
#   4-digit scale (max valid < 995):            996/997/998/999 + Wave V: 995
#   5-digit scale (max valid < 9995):           9996/9997/9998/9999 + Wave V: 9995
#
# Weights and "constructed" numeric scores (e.g. BCENT10X, IGDMEAN,
# PRXPREST, RCHDEN, GSWGT) use NO reserve codes.
#
# Meaning: 6=Refused, 7=Skip, 8=Don't Know, 9=Not Applicable/Other.
#
# scheme_by_kind maps 'kind' label -> {code: category}
SCHEMES = {
    "none": {},
    "1digit": {6: "refused", 7: "skip", 8: "dk", 9: "na"},
    "2digit": {96: "refused", 97: "skip", 98: "dk", 99: "na"},
    "3digit": {996: "refused", 997: "skip", 998: "dk", 999: "na"},
    "4digit": {9996: "refused", 9997: "skip", 9998: "dk", 9999: "na"},
    # Wave V "question not asked" extensions
    "2digit_w5": {95: "not_asked", 96: "refused", 97: "skip", 98: "dk", 99: "na"},
    "3digit_w5": {
        995: "not_asked", 996: "refused", 997: "skip", 998: "dk", 999: "na",
    },
    "4digit_w5": {
        9995: "not_asked",
        9996: "refused",
        9997: "skip",
        9998: "dk",
        9999: "na",
    },
}

# Order of pct_* columns we always emit.
RESERVE_CATS = ("refused", "skip", "dk", "na", "not_asked")


# ---------------------------------------------------------------------------
# File readers with local parquet cache
# ---------------------------------------------------------------------------

def _cache_path(src: Path) -> Path:
    return CACHE / f"{src.stem}.parquet"


def read_file(path: Path) -> tuple[pd.DataFrame, dict[str, str]]:
    """Return (df, labels) for a SAS7BDAT or XPT source. Cache DF as parquet,
    labels as a side-car parquet so we don't reparse the SAS file each run."""
    cache = _cache_path(path)
    lbl_cache = cache.with_suffix(".labels.parquet")
    if cache.exists() and lbl_cache.exists():
        df = pd.read_parquet(cache)
        lbls = pd.read_parquet(lbl_cache)
        labels = dict(zip(lbls["var_name"], lbls["label"]))
        return df, labels

    if path.suffix.lower() == ".xpt":
        df, meta = pyreadstat.read_xport(str(path))
    else:
        df, meta = pyreadstat.read_sas7bdat(str(path))
    labels = {n: (meta.column_names_to_labels.get(n) or "") for n in df.columns}
    # Cache
    try:
        df.to_parquet(cache)
        pd.DataFrame({"var_name": list(labels.keys()),
                      "label": list(labels.values())}).to_parquet(lbl_cache)
    except Exception as e:  # parquet may fail on exotic dtypes
        print(f"  [warn] parquet cache failed for {path.name}: {e}")
    return df, labels


# ---------------------------------------------------------------------------
# Reserve-scheme inference (heuristic by observed value range)
# ---------------------------------------------------------------------------

def infer_scheme(s: pd.Series, wave5: bool = False,
                 override: str | None = None) -> str:
    """Pick a reserve-code scheme. Override wins; otherwise use the
    observed max non-null value to choose a digit-width."""
    if override is not None:
        return override
    v = s.dropna()
    if v.empty or not pd.api.types.is_numeric_dtype(v):
        return "none"
    # Use the integer-like max to pick scale. Non-integer -> no reserve codes.
    vmax = float(v.max())
    # If the column is very obviously continuous (non-integer values exist),
    # treat as no reserve codes.
    # Accept the column as "integer-looking" if at least 95% of non-null
    # values round-trip through int.
    near_int = np.isclose(v, v.round()).mean()
    if near_int < 0.95:
        return "none"
    if vmax >= 9990:
        return "4digit_w5" if wave5 else "4digit"
    if vmax >= 990:
        return "3digit_w5" if wave5 else "3digit"
    if vmax >= 90:
        return "2digit_w5" if wave5 else "2digit"
    if vmax > 9:
        # Values in [10,89] with no evidence of reserve codes -> no scheme.
        return "none"
    # Very small scale (0-9). Only claim a 1-digit scheme if 6/7/8/9 actually
    # appear AND the scale looks like a 0-5 Likert (or 0-3). Otherwise leave
    # untouched -- many of these are genuine valid values, not reserve codes.
    # To stay safe and not misclassify 0/1 binaries, require that substantive
    # max <= 5 before treating 6-9 as reserves.
    # Additionally only flip if 6/7/8/9 values are actually present.
    vals = set(v.astype(float).round().astype(int).tolist())
    reserves_present = vals & {6, 7, 8, 9}
    if reserves_present and vmax <= 9:
        # Does the distribution look Likert-ish (e.g. 0-3 or 0-5)?
        # Count of values <=5 vs total.
        small_share = (v <= 5).mean()
        if small_share >= 0.80:
            return "1digit"
    return "none"


def summarize(name: str, s: pd.Series, *, wave5: bool = False,
              override: str | None = None,
              force_continuous: bool = False) -> dict:
    """Return one row of the missingness profile."""
    total = len(s)
    n_missing_true = int(s.isna().sum())
    non_null = s.dropna()

    scheme = infer_scheme(non_null, wave5=wave5, override=override)
    scheme_map = SCHEMES[scheme]

    counts = {cat: 0 for cat in RESERVE_CATS}
    if pd.api.types.is_numeric_dtype(non_null) and scheme_map:
        # Round to handle floats stored as 96.0 etc.
        int_like = non_null.round().astype("Int64")
        for code, cat in scheme_map.items():
            counts[cat] += int((int_like == code).sum())
        reserve_mask = int_like.isin(list(scheme_map.keys())).to_numpy()
        valid = non_null[~reserve_mask]
    else:
        valid = non_null

    n_nonmissing = int(non_null.size)
    n_valid = int(valid.size)

    row = {
        "variable": name,
        "n_total": total,
        "n_nonmissing": n_nonmissing,
        "n_valid": n_valid,
        "scheme": scheme,
        "pct_missing_true": 100.0 * n_missing_true / total if total else np.nan,
        "pct_refused": 100.0 * counts["refused"] / total if total else np.nan,
        "pct_skip": 100.0 * counts["skip"] / total if total else np.nan,
        "pct_dk": 100.0 * counts["dk"] / total if total else np.nan,
        "pct_na": 100.0 * counts["na"] / total if total else np.nan,
        "pct_not_asked": 100.0 * counts["not_asked"] / total if total else np.nan,
        "min_valid": None,
        "max_valid": None,
        "mean_valid": None,
        "median_valid": None,
    }

    # Treat as continuous if the valid values have > 10 unique levels or the
    # caller explicitly asked for continuous stats.
    if pd.api.types.is_numeric_dtype(valid) and valid.size > 0:
        if force_continuous or valid.nunique() > 10:
            row["min_valid"] = float(valid.min())
            row["max_valid"] = float(valid.max())
            row["mean_valid"] = float(valid.mean())
            row["median_valid"] = float(valid.median())
        else:
            # Still report min/max so the scheme choice is auditable.
            row["min_valid"] = float(valid.min())
            row["max_valid"] = float(valid.max())
            row["mean_valid"] = float(valid.mean())
            row["median_valid"] = float(valid.median())
    return row


# ---------------------------------------------------------------------------
# Variable lists
# ---------------------------------------------------------------------------

NETWORK_VARS = [
    "IDGX2", "ODGX2", "BCENT10X", "REACH", "REACH3",
    "IGDMEAN", "PRXPREST", "INFLDMN", "RCHDEN",
    "HAVEBMF", "HAVEBFF", "BMFRECIP", "BFFRECIP",
]
# Constructed network scores with no reserve codes.
NETWORK_NO_RESERVE = {"BCENT10X", "IGDMEAN", "PRXPREST", "INFLDMN", "RCHDEN"}

W1_INHOME_SINGLES = [
    "H1DA7", "H1ED19", "H1ED20", "H1ED21", "H1ED22", "H1ED23", "H1ED24",
]
CESD_ITEMS = [f"H1FS{i}" for i in range(1, 20)]
CESD_REVERSE = {"H1FS4", "H1FS8", "H1FS11", "H1FS15"}

W1_OUTCOMES = ["AH_PVT", "AH_RAW"]
W3_OUTCOMES = ["AH_RAW", "PVTSTD3C", "PVTSTD3L"]
W4_COG = ["C4WD90_1", "C4WD60_1", "C4NUMSCR"]

W5_COG_WORDS = ["C5WD90_1", "C5WD60_1"]
# Digit-span lengths 2..8 map to variable suffixes 3..9 (H5MH3 = 2 digits,
# H5MH4 = 3 digits, ..., H5MH9 = 8 digits). We report both the variable
# names as published and the digit-length they correspond to.
W5_DIGIT_LENGTHS = list(range(2, 9))  # conceptual lengths
W5_DIGIT_SUFFIXES = list(range(3, 10))  # actual variable-name suffixes
W5_DIGIT_VARS = [f"H5MH{s}{t}" for s in W5_DIGIT_SUFFIXES for t in ("A", "B")]

W1_CONFOUNDERS = [
    "BIO_SEX", "H1GI4",
    "H1GI6A", "H1GI6B", "H1GI6C", "H1GI6D", "H1GI6E",
]
W1_SES_CANDIDATES = ["PA55", "PA12", "PB8", "H1NM4", "H1NF4", "H1RM1", "H1RF1"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def _head_h1mf_h1ff(inhome_labels: dict[str, str]
                    ) -> tuple[list[str], list[str]]:
    h1mf = sorted([n for n in inhome_labels if n.startswith("H1MF")])
    h1ff = sorted([n for n in inhome_labels if n.startswith("H1FF")])
    return h1mf, h1ff


def cesd_sum(df: pd.DataFrame) -> pd.Series:
    """CES-D total (0..57 range with 19 items on 0-3 Likert). Reverse-score
    items 4, 8, 11, 15. Treats reserve codes (6/7/8) on these 0-3 scales as
    missing for the sum.

    Per standard Add Health coding, H1FS* items use 0=never/rarely, 1=some,
    2=often, 3=most of the time, and reserves 6 (refused) / 8 (DK). We treat
    any value > 3 as missing for the sum."""
    items = []
    for var in CESD_ITEMS:
        s = df[var].copy()
        s = s.where(s <= 3)  # NaN out reserve codes / invalid
        if var in CESD_REVERSE:
            s = 3 - s
        items.append(s)
    mat = pd.concat(items, axis=1)
    # Sum only rows with ALL 19 items non-missing (standard practice).
    total = mat.sum(axis=1, min_count=19)
    return total


def wave5_digit_score(df: pd.DataFrame) -> pd.Series:
    """Backward digit span score = max length L in {2..8} such that
    trial A == 1 OR trial B == 1. Else 0.

    A respondent is missing on this score if NONE of the 14 trials has a
    substantive (non-reserve) value — which in the public-use file means
    web/mail/spanish respondents (coded 995 on every trial) are NOT scored
    as zero, they are flagged missing. In-person and telephone respondents
    who genuinely failed every trial get score 0."""
    reserve = {95, 96, 97, 98, 99, 995, 996, 997, 998, 999}
    score = pd.Series(0, index=df.index, dtype="float")
    any_substantive = pd.Series(False, index=df.index)
    for L, suf in zip(W5_DIGIT_LENGTHS, W5_DIGIT_SUFFIXES):
        a = df.get(f"H5MH{suf}A")
        b = df.get(f"H5MH{suf}B")
        if a is None or b is None:
            continue
        a_sub = a.notna() & ~a.round().astype("Int64").isin(list(reserve))
        b_sub = b.notna() & ~b.round().astype("Int64").isin(list(reserve))
        any_substantive |= (a_sub | b_sub)
        ok = ((a == 1) & a_sub) | ((b == 1) & b_sub)
        score = score.where(~ok, L)
    score = score.where(any_substantive, np.nan)
    return score


def stratify_by_mode(df5: pd.DataFrame, var: str) -> pd.DataFrame:
    """For a Wave V variable, compute n_valid and pct_valid per MODE."""
    s = df5[var]
    mode = df5["MODE"].astype(str)
    # Define valid the same way as summarize(): drop NA and reserve codes.
    scheme = infer_scheme(s.dropna(), wave5=True)
    scheme_map = SCHEMES[scheme]
    int_like = s.round().astype("Int64") if pd.api.types.is_numeric_dtype(s) else s
    if scheme_map:
        valid_mask = s.notna() & ~int_like.isin(list(scheme_map.keys()))
    else:
        valid_mask = s.notna()
    rows = []
    for m, grp in df5.groupby(mode):
        m_total = len(grp)
        m_valid = int(valid_mask.loc[grp.index].sum())
        rows.append({
            "MODE": m,
            "n_total": m_total,
            "n_valid": m_valid,
            "pct_valid": 100.0 * m_valid / m_total if m_total else np.nan,
        })
    return pd.DataFrame(rows).sort_values("MODE").reset_index(drop=True)


def main() -> None:
    # --- Load all source files (with parquet cache) -----------------------
    print("Loading W1 network ...")
    df_net, lbl_net = read_file(W1_NET)
    print(f"  {df_net.shape}")
    print("Loading W1 in-home ...")
    df_in, lbl_in = read_file(W1_IN)
    print(f"  {df_in.shape}")
    print("Loading W3 PVT ...")
    df_w3, lbl_w3 = read_file(W3_PVT)
    print(f"  {df_w3.shape}")
    print("Loading W4 in-home ...")
    df_w4, lbl_w4 = read_file(W4_IN)
    print(f"  {df_w4.shape}")
    print("Loading W5 main (pwave5) ...")
    df_w5, lbl_w5 = read_file(W5_MAIN)
    print(f"  {df_w5.shape}")

    rows: list[dict] = []

    # --- Block: W1 network -------------------------------------------------
    for v in NETWORK_VARS:
        override = "none" if v in NETWORK_NO_RESERVE else None
        row = summarize(v, df_net[v], override=override,
                        force_continuous=(v in NETWORK_NO_RESERVE))
        row["block"] = "W1_network"
        row["label"] = lbl_net.get(v, "")
        rows.append(row)

    # Derived: isolated flag
    iso_flag = ((df_net["IDGX2"] == 0) & (df_net["ODGX2"] == 0)).astype("Int64")
    # Only valid where BOTH inputs are non-missing.
    both_obs = df_net["IDGX2"].notna() & df_net["ODGX2"].notna()
    iso_flag = iso_flag.where(both_obs, other=pd.NA)
    iso_row = summarize("ISOLATED_derived", iso_flag, override="none")
    iso_row["block"] = "W1_network"
    iso_row["label"] = "Derived: IDGX2==0 AND ODGX2==0"
    rows.append(iso_row)
    iso_rate = iso_flag.dropna().astype(int).mean()

    # --- Block: W1 friendship grid (first 5 of each block) ----------------
    all_h1mf, all_h1ff = _head_h1mf_h1ff(lbl_in)
    head_h1mf = all_h1mf[:5]
    head_h1ff = all_h1ff[:5]
    friendship_vars = head_h1mf + head_h1ff
    for v in friendship_vars:
        row = summarize(v, df_in[v])
        row["block"] = "W1_friendship"
        row["label"] = lbl_in.get(v, "")
        rows.append(row)

    # --- Block: W1 in-home singles (H1DA7, H1ED19..24) --------------------
    for v in W1_INHOME_SINGLES:
        row = summarize(v, df_in[v])
        row["block"] = "W1_inhome_singles"
        row["label"] = lbl_in.get(v, "")
        rows.append(row)

    # --- Block: CES-D items + derived sum --------------------------------
    for v in CESD_ITEMS:
        row = summarize(v, df_in[v])
        row["block"] = "W1_CESD"
        row["label"] = lbl_in.get(v, "")
        rows.append(row)
    cesd = cesd_sum(df_in)
    row = summarize("CESD_SUM_derived", cesd, override="none",
                    force_continuous=True)
    row["block"] = "W1_CESD"
    row["label"] = "Derived: sum of 19 CES-D items; items 4,8,11,15 reversed"
    rows.append(row)

    # --- Block: W1 cognitive baseline -------------------------------------
    for v in W1_OUTCOMES:
        row = summarize(v, df_in[v], force_continuous=True)
        row["block"] = "W1_cognitive"
        row["label"] = lbl_in.get(v, "")
        rows.append(row)

    # --- Block: W3 AHPVT ---------------------------------------------------
    for v in W3_OUTCOMES:
        row = summarize(v, df_w3[v], force_continuous=True)
        row["block"] = "W3_AHPVT"
        row["label"] = lbl_w3.get(v, "")
        rows.append(row)

    # --- Block: W4 cognitive ----------------------------------------------
    for v in W4_COG:
        row = summarize(v, df_w4[v], force_continuous=True)
        row["block"] = "W4_cognitive"
        row["label"] = lbl_w4.get(v, "")
        rows.append(row)

    # --- Block: W5 cognitive (overall) -----------------------------------
    w5_cog_vars = W5_COG_WORDS + W5_DIGIT_VARS
    for v in w5_cog_vars:
        row = summarize(v, df_w5[v], wave5=True, force_continuous=True)
        row["block"] = "W5_cognitive"
        row["label"] = lbl_w5.get(v, "")
        rows.append(row)
    # Derived backward digit span
    w5_digit = wave5_digit_score(df_w5)
    row = summarize("W5_DIGIT_SPAN_derived", w5_digit, wave5=True,
                    override="none", force_continuous=True)
    row["block"] = "W5_cognitive"
    row["label"] = "Derived: max L in 2..8 with A==1 OR B==1, else 0"
    rows.append(row)

    # --- Block: W5 cognitive, stratified by MODE --------------------------
    mode_tables: dict[str, pd.DataFrame] = {}
    for v in w5_cog_vars + ["W5_DIGIT_SPAN_derived"]:
        if v == "W5_DIGIT_SPAN_derived":
            tmp = df_w5[["MODE"]].copy()
            tmp["W5_DIGIT_SPAN_derived"] = w5_digit
            mode_tables[v] = stratify_by_mode(tmp, "W5_DIGIT_SPAN_derived")
        else:
            mode_tables[v] = stratify_by_mode(df_w5, v)

    # --- Block: W1 confounders --------------------------------------------
    for v in W1_CONFOUNDERS:
        row = summarize(v, df_in[v])
        row["block"] = "W1_confounders"
        row["label"] = lbl_in.get(v, "")
        rows.append(row)

    # SES / parent-ed candidates
    ses_found: list[tuple[str, str]] = []
    for v in W1_SES_CANDIDATES:
        if v in df_in.columns:
            ses_found.append((v, lbl_in.get(v, "")))
            row = summarize(v, df_in[v], force_continuous=True)
            row["block"] = "W1_SES"
            row["label"] = lbl_in.get(v, "")
            rows.append(row)
        else:
            # Record as "not found"
            rows.append({
                "variable": v, "n_total": 0, "n_nonmissing": 0, "n_valid": 0,
                "scheme": "none", "pct_missing_true": np.nan,
                "pct_refused": np.nan, "pct_skip": np.nan, "pct_dk": np.nan,
                "pct_na": np.nan, "pct_not_asked": np.nan,
                "min_valid": None, "max_valid": None,
                "mean_valid": None, "median_valid": None,
                "block": "W1_SES", "label": "NOT PRESENT IN w1inhome",
            })

    # Also keyword-search for any other income/education vars we missed.
    label_search_hits = []
    for var, lbl in lbl_in.items():
        low = (lbl or "").lower()
        if ("household income" in low or "parental income" in low or
                "parent education" in low or "mother education" in low or
                "father education" in low or "level of education" in low):
            label_search_hits.append((var, lbl))

    # --- Write CSV --------------------------------------------------------
    df_out = pd.DataFrame(rows)
    col_order = [
        "block", "variable", "label", "scheme",
        "n_total", "n_nonmissing", "n_valid",
        "pct_missing_true", "pct_refused", "pct_skip", "pct_dk",
        "pct_na", "pct_not_asked",
        "min_valid", "max_valid", "mean_valid", "median_valid",
    ]
    df_out = df_out[col_order]
    df_out.to_csv(CSV_OUT, index=False)
    print(f"Wrote {CSV_OUT}")

    # --- Write Markdown ---------------------------------------------------
    lines: list[str] = []
    lines.append("# Task 4: Missingness Profile\n")
    lines.append(
        "Per-variable missingness for the Add Health public-use feasibility "
        "sweep. Reserve codes (refused / legitimate skip / don't know / "
        "not applicable / Wave V 'question not asked') are tallied "
        "separately from true NA."
    )
    lines.append("")
    lines.append(f"- CSV: `outputs/04_missingness_profile.csv`")
    lines.append(f"- Sources: `{W1_NET.name}`, `{W1_IN.name}`, "
                 f"`{W3_PVT.name}`, `{W4_IN.name}`, `{W5_MAIN.name}`")
    lines.append("")

    def _fmt(x, digits=2):
        if x is None or (isinstance(x, float) and np.isnan(x)):
            return ""
        if isinstance(x, float):
            return f"{x:.{digits}f}"
        return str(x)

    def _block_table(block: str) -> list[str]:
        sub = df_out[df_out["block"] == block]
        out = []
        out.append("| variable | label | n_total | n_valid | "
                   "%miss | %ref | %skip | %dk | %na | %notAsk | "
                   "min | max | mean | median |")
        out.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|"
                   "---:|---:|---:|---:|")
        for _, r in sub.iterrows():
            out.append(
                f"| `{r['variable']}` | {r['label']} | "
                f"{int(r['n_total'])} | {int(r['n_valid'])} | "
                f"{_fmt(r['pct_missing_true'])} | "
                f"{_fmt(r['pct_refused'])} | "
                f"{_fmt(r['pct_skip'])} | "
                f"{_fmt(r['pct_dk'])} | "
                f"{_fmt(r['pct_na'])} | "
                f"{_fmt(r['pct_not_asked'])} | "
                f"{_fmt(r['min_valid'])} | "
                f"{_fmt(r['max_valid'])} | "
                f"{_fmt(r['mean_valid'], 3)} | "
                f"{_fmt(r['median_valid'])} |"
            )
        out.append("")
        return out

    # ---- Wave I network
    lines.append("## Block: W1 network (exposures) — `w1network.sas7bdat`\n")
    lines += _block_table("W1_network")
    lines.append("### Derived: `ISOLATED_derived` = (IDGX2 == 0 AND ODGX2 == 0)\n")
    lines.append(f"- Rate among observed: {iso_rate*100:.2f}% of respondents "
                 f"with both IDGX2 and ODGX2 are fully isolated.\n")

    # ---- Wave I friendship
    lines.append("## Block: W1 friendship grid (first 5 vars per gender)\n")
    lines.append(
        f"Full H1MF* block has {len(all_h1mf)} variables; H1FF* has "
        f"{len(all_h1ff)}. These name "
        "a 9-item x 5-nominee grid (per gender). The grid starts at "
        "`H1MFnA`/`H1FFnA` for friend 1. There is NO `H1MF1` / `H1FF1` — "
        "the 'nomination indicator' for friend 1 is the presence of any "
        "non-missing value on the first nominee's block (e.g. `H1MF2A`)."
    )
    lines.append("")
    lines.append("Full H1MF variable list:")
    lines.append("")
    lines.append(", ".join(f"`{n}`" for n in all_h1mf))
    lines.append("")
    lines.append("Full H1FF variable list:")
    lines.append("")
    lines.append(", ".join(f"`{n}`" for n in all_h1ff))
    lines.append("")
    lines += _block_table("W1_friendship")

    # ---- Wave I in-home singles
    lines.append("## Block: W1 in-home activity + school belonging\n")
    lines += _block_table("W1_inhome_singles")

    # ---- Wave I CES-D
    lines.append("## Block: W1 CES-D items (`H1FS1`..`H1FS19`) + derived sum\n")
    lines += _block_table("W1_CESD")
    lines.append("### Derived: `CESD_SUM_derived`\n")
    lines.append(
        "**Formula.** For each respondent, recode items **H1FS4, H1FS8, "
        "H1FS11, H1FS15** as `3 - x` (reverse-scoring positively-worded "
        "items); leave the other 15 items unchanged. Treat any value > 3 "
        "(i.e. reserve codes 6/7/8) as missing. The CES-D sum is the sum "
        "of all 19 recoded items, and is missing for any respondent with "
        "any missing item (strict complete-case). Expected range 0..57.\n"
    )

    # ---- Wave I cognitive baseline
    lines.append("## Block: W1 cognitive baseline (AHPVT)\n")
    lines += _block_table("W1_cognitive")

    # ---- Wave III AHPVT
    lines.append("## Block: W3 AHPVT\n")
    lines += _block_table("W3_AHPVT")

    # ---- Wave IV cognitive
    lines.append("## Block: W4 cognitive\n")
    lines += _block_table("W4_cognitive")

    # ---- Wave V cognitive (overall)
    lines.append("## Block: W5 cognitive (overall)\n")
    lines += _block_table("W5_cognitive")
    lines.append("### Derived: `W5_DIGIT_SPAN_derived`\n")
    lines.append(
        "**Formula.** For each length L in {2,3,4,5,6,7,8}, look at trials "
        "`H5MHLA` and `H5MHLB`. The score is the **maximum L** such that "
        "either trial scored 1 (correct). If no length has a correct "
        "trial, the score is 0. The score is missing only if both trials "
        "at EVERY length are NA (i.e. the backward digit span task was "
        "not administered to that respondent at all).\n"
    )

    # ---- Wave V cognitive, stratified by MODE
    lines.append("## Block: W5 cognitive missingness by `MODE`\n")
    lines.append(
        "MODE codes (per W5 codebook): **W=Web, I=In-person, M=Mail, "
        "T=Telephone/CATI, S=Spanish**. The Wave V mixed-mode design "
        "changed which cognitive items were asked per mode (web/mail had "
        "no DK/Refused option, so DK became silent NA)."
    )
    lines.append("")
    for var in W5_COG_WORDS + W5_DIGIT_VARS + ["W5_DIGIT_SPAN_derived"]:
        tbl = mode_tables[var]
        lines.append(f"### `{var}`")
        lines.append("")
        lines.append("| MODE | n_total | n_valid | pct_valid |")
        lines.append("|---|---:|---:|---:|")
        for _, r in tbl.iterrows():
            lines.append(
                f"| {r['MODE']} | {int(r['n_total'])} | "
                f"{int(r['n_valid'])} | {_fmt(r['pct_valid'])} |"
            )
        lines.append("")

    # ---- Wave I confounders
    lines.append("## Block: W1 confounders (sex, race, Hispanic origin)\n")
    lines += _block_table("W1_confounders")

    # ---- SES / parent education search
    lines.append("## Block: W1 household income & parental education "
                 "(search result)\n")
    lines.append(
        "Searched `w1inhome.sas7bdat` labels for 'household income', "
        "'parental income', 'level of education', and '{mother,father,"
        "parent} education'. The hits below show the exact variables "
        "found in the merged in-home file (which includes Parent "
        "Questionnaire items prefixed `PA*`, `PB*`, `PC*`)."
    )
    lines.append("")
    lines.append("### Candidates from the feasibility report")
    lines.append("")
    lines.append("| variable | present? | label |")
    lines.append("|---|---|---|")
    for v in W1_SES_CANDIDATES:
        present = "yes" if v in df_in.columns else "**NO**"
        lbl = lbl_in.get(v, "(not in file)")
        lines.append(f"| `{v}` | {present} | {lbl} |")
    lines.append("")
    lines.append("### Additional label-search hits")
    lines.append("")
    lines.append("| variable | label |")
    lines.append("|---|---|")
    for var, lbl in label_search_hits:
        lines.append(f"| `{var}` | {lbl} |")
    lines.append("")
    lines.append("### Missingness of the SES / parent-ed variables\n")
    lines += _block_table("W1_SES")

    # ---- Callouts
    lines.append("## Callouts\n")

    high_missing = df_out[
        (df_out["n_total"] > 0)
        & (df_out["pct_missing_true"] > 10.0)
    ]
    lines.append("### Variables with > 10% pure-NA missing (excluding reserve codes)\n")
    if high_missing.empty:
        lines.append("_None._\n")
    else:
        lines.append("| variable | block | %miss | n_total |")
        lines.append("|---|---|---:|---:|")
        for _, r in high_missing.sort_values(
                "pct_missing_true", ascending=False).iterrows():
            lines.append(
                f"| `{r['variable']}` | {r['block']} | "
                f"{_fmt(r['pct_missing_true'])} | {int(r['n_total'])} |"
            )
        lines.append("")

    # Reserve > true-missing
    reserve_total = (
        df_out[["pct_refused", "pct_skip", "pct_dk",
                "pct_na", "pct_not_asked"]].fillna(0).sum(axis=1)
    )
    reserve_dominant = df_out[
        (df_out["n_total"] > 0)
        & (reserve_total > df_out["pct_missing_true"].fillna(0))
    ]
    lines.append("### Variables where reserve codes exceed true-missing\n")
    if reserve_dominant.empty:
        lines.append("_None._\n")
    else:
        lines.append("| variable | block | %miss | %reserve (all) |")
        lines.append("|---|---|---:|---:|")
        for i, r in reserve_dominant.iterrows():
            lines.append(
                f"| `{r['variable']}` | {r['block']} | "
                f"{_fmt(r['pct_missing_true'])} | "
                f"{_fmt(reserve_total.loc[i])} |"
            )
        lines.append("")

    # ---- Reserve-scheme legend
    lines.append("## Reserve-code scheme legend\n")
    lines.append(
        "- `none`: continuous / constructed score; no reserve codes applied.\n"
        "- `1digit`: 6=Refused, 7=Skip, 8=DK, 9=NA (Likert scales ≤5).\n"
        "- `2digit`: 96=Refused, 97=Skip, 98=DK, 99=NA.\n"
        "- `3digit`: 996=Refused, 997=Skip, 998=DK, 999=NA.\n"
        "- `4digit`: 9996=Refused, 9997=Skip, 9998=DK, 9999=NA.\n"
        "- `*_w5` variants add the Wave V 'question not asked' code "
        "(95/995/9995).\n"
    )

    MD_OUT.write_text("\n".join(lines))
    print(f"Wrote {MD_OUT}")

    # Console summary ------------------------------------------------------
    print("\n=== Summary ===")
    print("SES / parent-ed candidates present in w1inhome:",
          [v for v, _ in ses_found])
    print("Label-search hits beyond the candidate list:")
    for v, l in label_search_hits:
        print(f"   {v}  {l}")


if __name__ == "__main__":
    main()

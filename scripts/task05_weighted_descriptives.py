"""
Task 05 - Survey-weighted univariate descriptives.

Design:
  - Cluster (PSU) = CLUSTER2
  - Stratum      = not provided in Add Health public-use; treated as None
  - Weights      = pweights (GSWGT1 for W1, GSWGT4_2 for W4 cross-sectional,
                   GSW5 for W5 cross-sectional); never normalized
  - With-replacement design; singleton clusters contribute 0 between-cluster
    variance (singleunit(missing) semantics).

Implementation note:
  `samplics` is not installed in this environment, so all survey-weighted
  quantities are computed manually:
    - weighted mean     : sum(w*y) / sum(w)
    - weighted variance : Sum_i w_i*(y_i - mean)^2 / Sum_i w_i  (population)
    - weighted SD       : sqrt(weighted variance)
    - SE of the mean    : cluster-robust linearized SE (Taylor expansion)
      with PSU = CLUSTER2.  With no stratum the formula reduces to
        Var_hat(mean) = (H/(H-1)) * (1/W_total^2) * Sum_h (u_h - u_bar)^2
      where
        u_h = Sum_{i in PSU h} w_i * (y_i - mean)
        u_bar = mean of u_h over clusters
        H = # PSUs with at least one observation on y.
    - 95% CI            : mean +/- 1.96 * SE
    - For proportions   : same machinery applied to the 0/1 indicator;
      CI is a logit-transformed CI (Korn-Graubard style) bounded to [0,1].

Reserve codes (set to NaN before any statistic):
    6/96/996/9996 refused, 7/97/997/9997 legitimate skip,
    8/98/998/9998 don't know, 9/99/999/9999 not applicable,
    95/995/9995 not asked in W5 module.
  Filtering is applied conservatively against each variable's
  codebook-implied valid range (see VALID_RANGES below).

Outputs:
    outputs/05_weighted_descriptives.md
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import pyreadstat

ROOT = Path("/Users/jb/Desktop/Inter-Generational-Causal-Analysis-of-the-AddHealth-Dataset")
DATA = ROOT / "data"
OUT = ROOT / "outputs" / "05_weighted_descriptives.md"

# ---------------------------------------------------------------------------
# Valid ranges (min, max, inclusive).  Anything outside is set to NaN.
# Reserve codes are handled by these ranges.
# ---------------------------------------------------------------------------
VALID_RANGES: Dict[str, Tuple[float, float]] = {
    # W1 network (continuous counts / real-valued centralities)
    "IDGX2": (0, 50),
    "ODGX2": (0, 50),
    "BCENT10X": (-1e6, 1e6),      # real-valued; keep everything finite
    "REACH": (0, 5000),
    "REACH3": (0, 5000),
    "PRXPREST": (0, 1),
    "HAVEBMF": (0, 1),
    "HAVEBFF": (0, 1),
    "BMFRECIP": (0, 1),
    "BFFRECIP": (0, 1),
    # W1 friendship / belonging (ordinal 0-6 / 1-5 etc.)
    "H1DA7": (0, 3),              # 4-level freq (0-3); reserves 6/8/9
    "H1ED19": (1, 5),
    "H1ED20": (1, 5),
    "H1ED21": (1, 5),
    "H1ED22": (1, 5),
    "H1ED23": (1, 5),
    "H1ED24": (1, 5),
    # W1 baseline cog & demog
    "AH_PVT": (0, 200),           # standardized score ~55-145; reserves 996/7/8
    "BIO_SEX": (1, 2),
    "H1GI4": (0, 1),
    "H1GI6A": (0, 1),
    "H1GI6B": (0, 1),
    "H1GI6C": (0, 1),
    "H1GI6D": (0, 1),
    "H1GI6E": (0, 1),
    # CES-D items
    **{f"H1FS{i}": (0, 3) for i in range(1, 20)},
    # W4 cognitive
    "C4WD90_1": (0, 15),
    "C4WD60_1": (0, 15),
    "C4NUMSCR": (0, 7),           # 0-7; reserves 96/97/98/99
    # W5 cognitive
    "C5WD90_1": (0, 15),
    "C5WD60_1": (0, 15),
    # W5 BDS per-trial items are 0/1
}
for L in range(3, 10):
    for suf in ("A", "B"):
        VALID_RANGES[f"H5MH{L}{suf}"] = (0, 1)

CESD_ITEMS = [f"H1FS{i}" for i in range(1, 20)]
CESD_REVERSE = {4, 8, 11, 15}    # 1-based item numbers to reverse-score


def clean_var(s: pd.Series, name: str) -> pd.Series:
    """Apply valid-range filter; values outside -> NaN."""
    s = pd.to_numeric(s, errors="coerce")
    if name in VALID_RANGES:
        lo, hi = VALID_RANGES[name]
        s = s.where((s >= lo) & (s <= hi))
    return s


# ---------------------------------------------------------------------------
# Survey-weighted estimation (manual, no samplics)
# ---------------------------------------------------------------------------
def weighted_mean_se(
    y: np.ndarray, w: np.ndarray, psu: np.ndarray
) -> Tuple[float, float, float, int, int]:
    """
    Returns (mean, sd, se, n_unweighted, n_psu).
    Cluster-robust (linearized) SE with PSUs; no stratification.
    """
    mask = ~np.isnan(y) & ~np.isnan(w) & (w > 0)
    y = y[mask]; w = w[mask]; psu = psu[mask]
    n = len(y)
    if n == 0:
        return (np.nan, np.nan, np.nan, 0, 0)
    W = w.sum()
    mean = float(np.sum(w * y) / W)
    var_pop = float(np.sum(w * (y - mean) ** 2) / W)
    sd = float(np.sqrt(var_pop))
    # Cluster-robust linearized SE for the ratio estimator of the mean.
    # u_i = w_i * (y_i - mean); u_h = Sum u_i over PSU h.
    # Var(mean) ~= (H/(H-1)) * (1/W^2) * Sum_h (u_h - u_bar)^2
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


def weighted_prop_ci(
    ind: np.ndarray, w: np.ndarray, psu: np.ndarray
) -> Tuple[float, float, float, float, int, int]:
    """
    Survey-weighted proportion with logit-transformed 95% CI.
    Returns (p, se, ci_lo, ci_hi, n, n_psu).
    """
    p, _sd, se, n, H = weighted_mean_se(ind.astype(float), w, psu)
    if np.isnan(p) or np.isnan(se) or p <= 0 or p >= 1:
        # Fall back to symmetric normal CI bounded to [0,1].
        if np.isnan(p):
            return (p, se, np.nan, np.nan, n, H)
        lo = max(0.0, p - 1.96 * (se if not np.isnan(se) else 0.0))
        hi = min(1.0, p + 1.96 * (se if not np.isnan(se) else 0.0))
        return (p, se, lo, hi, n, H)
    # logit transform
    logit = np.log(p / (1 - p))
    se_logit = se / (p * (1 - p))
    lo_l = logit - 1.96 * se_logit
    hi_l = logit + 1.96 * se_logit
    lo = 1 / (1 + np.exp(-lo_l))
    hi = 1 / (1 + np.exp(-hi_l))
    return (p, se, lo, hi, n, H)


# ---------------------------------------------------------------------------
# Data loading helpers
# ---------------------------------------------------------------------------
def load_w1_network() -> Tuple[pd.DataFrame, dict]:
    df, meta = pyreadstat.read_sas7bdat(str(DATA / "W1" / "w1network.sas7bdat"))
    return df, meta.column_names_to_labels


def load_w1_inhome() -> Tuple[pd.DataFrame, dict]:
    df, meta = pyreadstat.read_sas7bdat(str(DATA / "W1" / "w1inhome.sas7bdat"))
    return df, meta.column_names_to_labels


def load_w1_weight() -> pd.DataFrame:
    df, _ = pyreadstat.read_sas7bdat(str(DATA / "W1" / "w1weight.sas7bdat"))
    return df[["AID", "CLUSTER2", "GSWGT1"]]


def load_w4_inhome() -> Tuple[pd.DataFrame, dict]:
    df, meta = pyreadstat.read_sas7bdat(str(DATA / "W4" / "w4inhome.sas7bdat"))
    return df, meta.column_names_to_labels


def load_w4_weight() -> pd.DataFrame:
    df, _ = pyreadstat.read_sas7bdat(str(DATA / "W4" / "w4weight.sas7bdat"))
    return df[["AID", "CLUSTER2", "GSWGT4_2"]]


def load_w5() -> Tuple[pd.DataFrame, dict]:
    df, meta = pyreadstat.read_xport(str(DATA / "W5" / "pwave5.xpt"))
    return df, meta.column_names_to_labels


def load_w5_weight() -> pd.DataFrame:
    df, _ = pyreadstat.read_xport(str(DATA / "W5" / "p5weight.xpt"))
    return df[["AID", "CLUSTER2", "GSW5"]]


# ---------------------------------------------------------------------------
# Derivation helpers
# ---------------------------------------------------------------------------
def derive_cesd_sum(df: pd.DataFrame) -> pd.Series:
    """CES-D sum from H1FS1-H1FS19, items 4/8/11/15 reverse-scored (0..3 -> 3..0)."""
    cleaned = pd.DataFrame({v: clean_var(df[v], v) for v in CESD_ITEMS})
    for idx in CESD_REVERSE:
        col = f"H1FS{idx}"
        cleaned[col] = 3 - cleaned[col]
    # Sum only if all 19 items are present (conservative).
    total = cleaned.sum(axis=1, min_count=19)
    return total


def derive_bds_score(df: pd.DataFrame) -> pd.Series:
    """
    Max L in {2..8} such that H5MH(L+1)A == 1 OR H5MH(L+1)B == 1; else 0.
    Using variable naming convention H5MH<i><A|B> where i = L+1 ranges 3..9.
    """
    n = len(df)
    score = np.zeros(n, dtype=float)
    # Drop-to-NaN only if ALL 14 items are NaN.
    item_cols = [f"H5MH{L+1}{s}" for L in range(2, 9) for s in "AB"]
    cleaned = {c: clean_var(df[c], c) for c in item_cols}
    all_missing_mask = np.ones(n, dtype=bool)
    for c, s in cleaned.items():
        all_missing_mask &= s.isna().values
    # Compute best L per respondent
    for L in range(2, 9):                       # L = 2..8
        a = cleaned[f"H5MH{L+1}A"].values
        b = cleaned[f"H5MH{L+1}B"].values
        success = (a == 1) | (b == 1)
        score = np.where(success, float(L), score)
    out = pd.Series(score, index=df.index, dtype=float)
    out[all_missing_mask] = np.nan
    return out


# ---------------------------------------------------------------------------
# Block drivers
# ---------------------------------------------------------------------------
def summarize_block(
    block_name: str,
    df: pd.DataFrame,
    weight_df: pd.DataFrame,
    weight_var: str,
    variables: List[str],
    labels: dict,
    kinds: Optional[Dict[str, str]] = None,
) -> pd.DataFrame:
    """
    df must contain AID + the listed variables.
    weight_df has AID, CLUSTER2, <weight_var>.
    kinds[var] in {"continuous","binary"}; default inferred from VALID_RANGES.
    """
    kinds = kinds or {}
    merged = df.merge(weight_df, on="AID", how="inner")
    rows = []
    psu = merged["CLUSTER2"].values
    w = merged[weight_var].values
    for v in variables:
        if v not in merged.columns:
            rows.append({
                "block": block_name, "variable": v,
                "label": labels.get(v, ""), "kind": "missing",
                "n": 0, "n_psu": 0,
                "mean_or_prop": np.nan, "sd": np.nan, "se": np.nan,
                "ci_lo": np.nan, "ci_hi": np.nan,
            })
            continue
        y = clean_var(merged[v], v).values
        kind = kinds.get(v)
        if kind is None:
            lo, hi = VALID_RANGES.get(v, (None, None))
            kind = "binary" if (lo == 0 and hi == 1) else "continuous"
        if kind == "binary":
            p, se, clo, chi, n, H = weighted_prop_ci(y, w, psu)
            rows.append({
                "block": block_name, "variable": v,
                "label": labels.get(v, ""), "kind": "binary (prop)",
                "n": n, "n_psu": H,
                "mean_or_prop": p, "sd": np.nan, "se": se,
                "ci_lo": clo, "ci_hi": chi,
            })
        else:
            m, sd, se, n, H = weighted_mean_se(y, w, psu)
            if np.isnan(se):
                clo, chi = np.nan, np.nan
            else:
                clo, chi = m - 1.96 * se, m + 1.96 * se
            rows.append({
                "block": block_name, "variable": v,
                "label": labels.get(v, ""), "kind": "continuous (mean)",
                "n": n, "n_psu": H,
                "mean_or_prop": m, "sd": sd, "se": se,
                "ci_lo": clo, "ci_hi": chi,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------
def main() -> None:
    print("Loading W1 weight / inhome / network ...")
    w1w = load_w1_weight()
    w1h, w1h_lab = load_w1_inhome()
    w1n, w1n_lab = load_w1_network()
    labels = {**w1h_lab, **w1n_lab}

    # -- W1 exposures (network) --------------------------------------------
    w1_net_vars = ["IDGX2", "ODGX2", "BCENT10X", "REACH", "REACH3",
                   "PRXPREST", "HAVEBMF", "HAVEBFF", "BMFRECIP", "BFFRECIP"]
    # PRXPREST is continuous in [0, 0.77]; its VALID_RANGES entry is (0, 1)
    # which would otherwise match the binary heuristic.
    res_w1_net = summarize_block(
        "W1 exposures (network)", w1n[["AID", *w1_net_vars]],
        w1w, "GSWGT1", w1_net_vars, labels,
        kinds={"PRXPREST": "continuous"},
    )

    # -- W1 friendship / belonging -----------------------------------------
    w1_fb_vars = ["H1DA7", "H1ED19", "H1ED20", "H1ED21", "H1ED22", "H1ED23",
                  "H1ED24"]
    res_w1_fb = summarize_block(
        "W1 friendship/belonging", w1h[["AID", *w1_fb_vars]],
        w1w, "GSWGT1", w1_fb_vars, labels,
        kinds={v: "continuous" for v in w1_fb_vars},
    )

    # -- W1 baseline cog & demog + CES-D -----------------------------------
    w1_cd_vars = ["AH_PVT", "BIO_SEX", "H1GI4", "H1GI6A", "H1GI6B", "H1GI6C",
                  "H1GI6D", "H1GI6E"]
    # Add derived CES-D sum
    w1h_aug = w1h[["AID", *w1_cd_vars, *CESD_ITEMS]].copy()
    w1h_aug["CESD_SUM"] = derive_cesd_sum(w1h_aug)
    labels["CESD_SUM"] = "DERIVED CES-D SUM (H1FS1-H1FS19, reverse 4/8/11/15)"
    # BIO_SEX is handled as continuous-style (coded 1/2); also report male%.
    res_w1_cd = summarize_block(
        "W1 baseline cognitive & demographics",
        w1h_aug[["AID", *w1_cd_vars, "CESD_SUM"]],
        w1w, "GSWGT1",
        [*w1_cd_vars, "CESD_SUM"], labels,
        kinds={
            "AH_PVT": "continuous", "BIO_SEX": "continuous",
            "CESD_SUM": "continuous",
            **{v: "binary" for v in ["H1GI4", "H1GI6A", "H1GI6B", "H1GI6C",
                                     "H1GI6D", "H1GI6E"]},
        },
    )

    # -- Sanity checks (need joined W1 frame) ------------------------------
    sanity_src = w1h_aug.merge(w1w, on="AID", how="inner")
    psu_s = sanity_src["CLUSTER2"].values
    w_s = sanity_src["GSWGT1"].values
    # % male
    male = (clean_var(sanity_src["BIO_SEX"], "BIO_SEX") == 1).astype(float)
    male = male.where(clean_var(sanity_src["BIO_SEX"], "BIO_SEX").notna())
    p_male, se_male, lo_m, hi_m, n_m, H_m = weighted_prop_ci(male.values, w_s, psu_s)
    # % non-Hispanic Black  (H1GI4==0 AND H1GI6B==1)
    hisp = clean_var(sanity_src["H1GI4"], "H1GI4")
    black = clean_var(sanity_src["H1GI6B"], "H1GI6B")
    nhb_valid = hisp.notna() & black.notna()
    nhb = ((hisp == 0) & (black == 1)).astype(float).where(nhb_valid)
    p_nhb, se_nhb, lo_nhb, hi_nhb, n_nhb, H_nhb = weighted_prop_ci(nhb.values, w_s, psu_s)
    # AH_PVT mean
    pvt = clean_var(sanity_src["AH_PVT"], "AH_PVT").values
    m_pvt, sd_pvt, se_pvt, n_pvt, H_pvt = weighted_mean_se(pvt, w_s, psu_s)
    ci_pvt = (m_pvt - 1.96 * se_pvt, m_pvt + 1.96 * se_pvt) if not np.isnan(se_pvt) else (np.nan, np.nan)

    sanity = {
        "male": (p_male, se_male, lo_m, hi_m, n_m),
        "nhblack": (p_nhb, se_nhb, lo_nhb, hi_nhb, n_nhb),
        "pvt": (m_pvt, sd_pvt, se_pvt, ci_pvt[0], ci_pvt[1], n_pvt),
    }

    # -- W4 cognitive ------------------------------------------------------
    print("Loading W4 weight / inhome ...")
    w4w = load_w4_weight()
    w4h, w4h_lab = load_w4_inhome()
    labels.update(w4h_lab)
    w4_vars = ["C4WD90_1", "C4WD60_1", "C4NUMSCR"]
    res_w4 = summarize_block(
        "W4 cognitive", w4h[["AID", *w4_vars]],
        w4w, "GSWGT4_2", w4_vars, labels,
        kinds={v: "continuous" for v in w4_vars},
    )

    # -- W5 cognitive ------------------------------------------------------
    print("Loading W5 weight / pwave5 ...")
    w5w = load_w5_weight()
    w5, w5_lab = load_w5()
    labels.update(w5_lab)
    bds_items = [f"H5MH{i}{s}" for i in range(3, 10) for s in "AB"]
    w5_need = ["AID", "C5WD90_1", "C5WD60_1", *bds_items]
    w5_sub = w5[[c for c in w5_need if c in w5.columns]].copy()
    w5_sub["BDS_SCORE"] = derive_bds_score(w5_sub)
    labels["BDS_SCORE"] = "DERIVED BACKWARD DIGIT SPAN (max length correct)"
    res_w5 = summarize_block(
        "W5 cognitive (mode-restricted subgroup)",
        w5_sub[["AID", "C5WD90_1", "C5WD60_1", "BDS_SCORE"]],
        w5w, "GSW5", ["C5WD90_1", "C5WD60_1", "BDS_SCORE"], labels,
        kinds={"C5WD90_1": "continuous", "C5WD60_1": "continuous",
               "BDS_SCORE": "continuous"},
    )

    # -- Combine and write -------------------------------------------------
    all_results = pd.concat(
        [res_w1_net, res_w1_fb, res_w1_cd, res_w4, res_w5], ignore_index=True
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_markdown(OUT, all_results, sanity)
    print(f"Wrote {OUT}")


def fmt(x, digits=4):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "NA"
    return f"{x:.{digits}f}"


def write_markdown(path: Path, results: pd.DataFrame, sanity: dict) -> None:
    lines: List[str] = []
    lines.append("# Task 05 - Survey-weighted univariate descriptives")
    lines.append("")
    lines.append("Weights, PSUs, and formulas are documented in the 'Notes on design' footer.")
    lines.append("")

    # Sanity checks
    p_male, se_male, lo_m, hi_m, n_m = sanity["male"]
    p_nhb, se_nhb, lo_nhb, hi_nhb, n_nhb = sanity["nhblack"]
    m_pvt, sd_pvt, se_pvt, lo_pvt, hi_pvt, n_pvt = sanity["pvt"]

    lines.append("## Sanity checks (W1, weight = GSWGT1)")
    lines.append("")
    lines.append("| Check | Estimate | SE | 95% CI | N | Expectation |")
    lines.append("|---|---|---|---|---|---|")
    lines.append(f"| Weighted % male (BIO_SEX==1) | {fmt(p_male)} | {fmt(se_male)} | [{fmt(lo_m)}, {fmt(hi_m)}] | {n_m} | ~0.49-0.51 |")
    lines.append(f"| Weighted % non-Hispanic Black (H1GI4==0 & H1GI6B==1) | {fmt(p_nhb)} | {fmt(se_nhb)} | [{fmt(lo_nhb)}, {fmt(hi_nhb)}] | {n_nhb} | ~0.14 |")
    lines.append(f"| Weighted mean AH_PVT | {fmt(m_pvt,3)} | {fmt(se_pvt,3)} | [{fmt(lo_pvt,3)}, {fmt(hi_pvt,3)}] | {n_pvt} | ~100 |")
    lines.append("")

    # One table per block
    for block in results["block"].unique():
        sub = results[results["block"] == block]
        lines.append(f"## {block}")
        lines.append("")
        lines.append("| Variable | Label | Kind | N | PSUs | Weighted mean / prop | SD | SE | 95% CI |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for _, r in sub.iterrows():
            ci = f"[{fmt(r['ci_lo'])}, {fmt(r['ci_hi'])}]"
            lines.append(
                f"| {r['variable']} | {r['label']} | {r['kind']} | "
                f"{int(r['n'])} | {int(r['n_psu'])} | "
                f"{fmt(r['mean_or_prop'])} | {fmt(r['sd'])} | {fmt(r['se'])} | {ci} |"
            )
        lines.append("")

    # Footer
    lines.append("## Notes on design")
    lines.append("")
    lines.append("- **Weights / PSU.** W1 blocks use `GSWGT1` with PSU `CLUSTER2` "
                 "(`w1weight.sas7bdat`); W4 cognitive uses the cross-sectional "
                 "`GSWGT4_2` with `CLUSTER2` (`w4weight.sas7bdat`); W5 cognitive "
                 "uses the cross-sectional `GSW5` with `CLUSTER2` "
                 "(`p5weight.xpt`). Weights are applied on the pweight scale and "
                 "are never normalized.")
    lines.append("- **Reserve codes.** Values matching the usual Add Health "
                 "reserve codes (refused / don't know / legitimate skip / NA / "
                 "W5-not-asked; 6/7/8/9, 96/97/98/99, 995/996/997/998, 95/9995, "
                 "etc.) are filtered by per-variable valid-range checks before "
                 "computing any statistic.")
    lines.append("- **Stratum.** The Add Health public-use release does not "
                 "include the stratum identifier. It is therefore treated as "
                 "None. Per Add Health documentation this has minimal impact on "
                 "standard errors relative to the cluster-robust linearization "
                 "that is applied here.")
    lines.append("- **SE / CI.** For continuous variables a cluster-robust "
                 "linearized (Taylor) SE with PSUs = `CLUSTER2` is used and a "
                 "95% CI is formed as mean +/- 1.96*SE. For binary indicators "
                 "the 95% CI uses a logit transformation of the weighted "
                 "proportion. `samplics` was not available in this environment; "
                 "the manual implementation in this script is equivalent to "
                 "Stata `svy, vce(linearized)` with `singleunit(missing)` for "
                 "an un-stratified single-stage cluster design with pweights.")
    lines.append("- **W5 cognitive subgroup.** W5 immediate word recall "
                 "(`C5WD90_1`, `C5WD60_1`) and the derived backward digit span "
                 "(`BDS_SCORE`) were administered only in the in-person / "
                 "phone modes (variable `MODE`). The `GSW5` cross-sectional "
                 "weight is still applied, so the reported weighted means and "
                 "CIs describe the mode-eligible subgroup rather than the full "
                 "W5 respondent population.")
    lines.append("")

    path.write_text("\n".join(lines))


if __name__ == "__main__":
    main()

"""cross-sex-friendship — sex × friend-sex stratified WLS across 13 outcomes.

For each of two stratifications (`BIO_SEX × HAVEBMF`, `BIO_SEX × HAVEBFF`),
runs WLS within each of the 4 cells against all 13 outcomes — a 8 × 13
matrix of cell-specific β estimates. The narrative contrast is between
cross-sex and same-sex cells *within sex*.

Per-outcome adjustment set inherited from the relevant existing DAG
(DAG-Cog for `W4_COG_COMP`, DAG-SES for SES outcomes which drop AHPVT,
otherwise screen-default L0+L1+AHPVT).

Sensitivity re-runs the whole grid using `FRIEND_*` derived friendship-grid
counts as alternative friendship coding.

This file is a SKELETON.

Outputs:
  tables/primary/cross_sex_matrix.csv
  tables/primary/cross_sex.md
  tables/sensitivity/cross_sex_friendcoding_alt.csv
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analysis import CACHE  # noqa: E402
from analysis.cleaning import clean_var  # noqa: E402
from analysis.wls import weighted_ols  # noqa: E402
from analysis.data_loading import load_outcome  # noqa: E402
from analysis.sensitivity import evalue  # noqa: E402
from analysis.sensitivity_panel import (  # noqa: E402
    build_cornfield_grid,
    build_eta_cell_from_quintile_contrast,
    build_eta_tilt_table,
    build_evalue_table,
)
from scipy import stats as _scipy_stats  # noqa: E402

TABLES_PRIMARY = HERE / "tables" / "primary"
TABLES_SENS = HERE / "tables" / "sensitivity"
TABLES_PRIMARY.mkdir(parents=True, exist_ok=True)
TABLES_SENS.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Outcome battery — 13 outcomes (1 cog + 12 secondary).
# (label, group, kind, weight_col, drops_ahpvt)
# ---------------------------------------------------------------------------
OUTCOMES: Dict[str, Tuple[str, str, str, str, bool]] = {
    "W4_COG_COMP": ("W4 cognition composite",                          "cognitive",       "z-score",       "GSWGT4_2", False),
    "H4BMI":       ("S27 BMI—W4",                                      "cardiometabolic", "continuous",    "GSWGT4_2", False),
    "H4SBP":       ("S27 SYSTOLIC BLOOD PRESSURE—W4",                  "cardiometabolic", "continuous",    "GSWGT4_2", False),
    "H4DBP":       ("S27 DIASTOLIC BLOOD PRESSURE—W4",                 "cardiometabolic", "continuous",    "GSWGT4_2", False),
    "H4WAIST":     ("S27 MEASURED WAIST (CM)—W4",                      "cardiometabolic", "continuous",    "GSWGT4_2", False),
    "H4BMICLS":    ("S27 BMI CLASS—W4",                                 "cardiometabolic", "ordinal-1-6",   "GSWGT4_2", False),
    "H5MN1":       ("S13Q1 LAST MO NO CNTRL IMPORT THINGS—W5",         "mental_health",   "likert-1-5",    "GSW5",     False),
    "H5MN2":       ("S13Q2 LAST MO CONFID HANDLE PERS PBMS—W5",        "mental_health",   "likert-1-5",    "GSW5",     False),
    "H5ID1":       ("S5Q1 HOW IS GEN PHYSICAL HEALTH—W5",              "functional",      "likert-1-5",    "GSW5",     False),
    "H5ID4":       ("S5Q4 LIMIT CLIMB SEV. FLIGHT STAIRS—W5",          "functional",      "ordinal-1-3",   "GSW5",     False),
    "H5ID16":      ("S5Q16 HOW OFTEN TROUBLE SLEEPING—W5",             "functional",      "ordinal-0-4",   "GSW5",     False),
    "H5LM5":       ("S3Q5 CURRENTLY WORK—W5",                           "ses",             "ordinal-1-3",   "GSW5",     True),
    "H5EC1":       ("S4Q1 INCOME PERS EARNINGS [W4–W5]—W5",            "ses",             "bracketed-1-13","GSW5",     True),
}

# Stratification schemes: (label, sex_label_for_cell, friend_indicator_col)
STRATIFICATIONS: List[Tuple[str, str]] = [
    ("BIO_SEX × HAVEBMF", "HAVEBMF"),
    ("BIO_SEX × HAVEBFF", "HAVEBFF"),
]

# Sex codes: 1 = male, 2 = female (Add Health convention).
SEX_CELLS = [(1, "male"), (2, "female")]
FRIEND_CELLS = [(0, "no"), (1, "yes")]

# Alternative friendship coding (sensitivity).
FRIEND_ALT_EXPOSURES = ["FRIEND_N_NOMINEES", "FRIEND_CONTACT_SUM", "FRIEND_DISCLOSURE_ANY"]


# ---------------------------------------------------------------------------
# Adjustment-set builders.
# ---------------------------------------------------------------------------
RACE_LEVELS = ["NH-Black", "Hispanic", "Other"]


def _race_dummies(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for lvl in RACE_LEVELS:
        out[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    out.loc[df["RACE"].isna(), :] = np.nan
    return out


def _adj_L0(df: pd.DataFrame, drop_sex: bool = True) -> pd.DataFrame:
    """L0 within a sex-stratified cell — drop sex dummy because cell IS sex."""
    parts = [_race_dummies(df), df["PARENT_ED"].rename("parent_ed")]
    if not drop_sex:
        parts.insert(0, pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index))
    return pd.concat(parts, axis=1)


def _adj_L0_L1(df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([
        _adj_L0(df),
        df["CESD_SUM"].rename("cesd_sum"),
        df["H1GH1"].rename("srh"),
    ], axis=1)


def _adj_full(df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([
        _adj_L0_L1(df),
        df["AH_RAW"].rename("ahpvt"),
    ], axis=1)


def adj_for_outcome(df: pd.DataFrame, outcome_code: str) -> pd.DataFrame:
    """Per-outcome adjustment set: SES drops AHPVT, others use L0+L1+AHPVT."""
    drops_ahpvt = OUTCOMES[outcome_code][4]
    return _adj_L0_L1(df) if drops_ahpvt else _adj_full(df)


# ---------------------------------------------------------------------------
# Frame loading
# ---------------------------------------------------------------------------
def _load_frame() -> pd.DataFrame:
    """Load W4 saturated-school analytic frame, attach outcomes + GSW5.

    Question for next pass: friendship-grid columns (HAVEBMF, HAVEBFF,
    FRIEND_*) — are they pre-derived in `analytic_w4.parquet`, or do they
    need a derive_friendship_grid() merge from `scripts/analysis/derivation.py`?
    The skeleton assumes they are present in the analytic frame; if not,
    add the merge step here.
    """
    W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
    # Attach GSW5 from the W5 weight file (.xpt). Wave-V weights live outside
    # the cached parquets; load_w5_weight pulls them via pyreadstat.
    try:
        from analysis.data_loading import load_w5_weight  # local import
        w5w = load_w5_weight()[["AID", "GSW5"]]
        W4 = W4.merge(w5w, on="AID", how="left")
    except Exception as exc:  # noqa: BLE001
        print(f"WARN: GSW5 not loaded ({exc}); W5 fits will fall back to GSWGT4_2.")
        W4["GSW5"] = np.nan
    for code in OUTCOMES:
        if code != "W4_COG_COMP":  # already on the analytic frame
            W4[code] = load_outcome(W4["AID"], code)
    return W4


# ---------------------------------------------------------------------------
# Within-cell WLS primitive
# ---------------------------------------------------------------------------
def _fit_within_cell(df: pd.DataFrame, exposure_col: str, y_col: str,
                     w_col: str) -> Optional[dict]:
    """WLS of y_col on (exposure_col + per-outcome adj) within the supplied df."""
    if df.shape[0] == 0:
        return None
    exp = clean_var(df[exposure_col], exposure_col)
    adj = adj_for_outcome(df, y_col)
    X = pd.concat([exp.rename("exposure"), adj], axis=1)
    X.insert(0, "const", 1.0)
    y = df[y_col].values
    w = df[w_col].values
    psu = df["CLUSTER2"].values
    return weighted_ols(y, X.values, w, psu, column_names=list(X.columns))


# ---------------------------------------------------------------------------
# Primary 8 × 13 grid.
# ---------------------------------------------------------------------------
def run_primary(df: pd.DataFrame) -> pd.DataFrame:
    """Per (stratification, sex_cell, friend_cell, outcome) row."""
    rows = []
    for strat_label, friend_col in STRATIFICATIONS:
        for sex_code, sex_name in SEX_CELLS:
            for friend_code, friend_label in FRIEND_CELLS:
                cell_mask = (df["BIO_SEX"] == sex_code) & (df[friend_col] == friend_code)
                cell_df = df[cell_mask].copy()
                # The "exposure" within a cell is constant — but we can still
                # fit using the friend indicator as a constant-removed term:
                # actually the design here is to compare cells, NOT to fit a
                # within-cell exposure coefficient. So per-cell we report:
                #  - cell N
                #  - per-outcome WEIGHTED MEAN (not regression beta) within cell
                #    after residualizing on adj (i.e. adjusted cell-mean).
                # The cross-cell contrast lives in the figures step.
                for outcome_code, (label, group, kind, w_col, _drops) in OUTCOMES.items():
                    weight_col = w_col if w_col in cell_df.columns and cell_df[w_col].notna().any() else "GSWGT4_2"
                    n_cell = int(cell_df[outcome_code].notna().sum())
                    if n_cell < 30:
                        adj_mean = np.nan
                        adj_se = np.nan
                    else:
                        # Adjusted cell-mean = intercept of WLS of y on adj alone
                        # within the cell (cluster-SE on CLUSTER2).
                        adj = adj_for_outcome(cell_df, outcome_code)
                        X = pd.concat([adj], axis=1)
                        X.insert(0, "const", 1.0)
                        y = cell_df[outcome_code].values
                        w = cell_df[weight_col].values
                        psu = cell_df["CLUSTER2"].values
                        res = weighted_ols(y, X.values, w, psu, column_names=list(X.columns))
                        if res is None:
                            adj_mean = np.nan
                            adj_se = np.nan
                        else:
                            adj_mean = float(res["beta"]["const"])
                            adj_se = float(res["se"]["const"])
                    rows.append({
                        "stratification": strat_label,
                        "friend_indicator": friend_col,
                        "sex": sex_name,
                        "sex_code": sex_code,
                        "friend_present": friend_label,
                        "friend_code": friend_code,
                        "outcome": outcome_code,
                        "outcome_label": label,
                        "outcome_group": group,
                        "n_cell": n_cell,
                        "adj_mean": adj_mean,
                        "adj_se": adj_se,
                        "weight_col_used": weight_col,
                    })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity — alternative friendship coding via FRIEND_* derivations.
# Re-fit WLS of outcome ~ FRIEND_* + adj, stratified by sex only.
# ---------------------------------------------------------------------------
def run_friendcoding_alt(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for sex_code, sex_name in SEX_CELLS:
        sex_df = df[df["BIO_SEX"] == sex_code].copy()
        for exp_col in FRIEND_ALT_EXPOSURES:
            if exp_col not in sex_df.columns:
                continue
            for outcome_code, (label, group, kind, w_col, _drops) in OUTCOMES.items():
                weight_col = w_col if w_col in sex_df.columns and sex_df[w_col].notna().any() else "GSWGT4_2"
                res = _fit_within_cell(sex_df, exp_col, outcome_code, weight_col)
                if res is None:
                    continue
                rows.append({
                    "sex": sex_name,
                    "exposure": exp_col,
                    "outcome": outcome_code,
                    "outcome_label": label,
                    "outcome_group": group,
                    "n": int(res["n"]),
                    "beta": float(res["beta"]["exposure"]),
                    "se": float(res["se"]["exposure"]),
                    "p": float(res["p"]["exposure"]),
                })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Markdown narrative
# ---------------------------------------------------------------------------
def write_markdown(matrix: pd.DataFrame) -> None:
    lines = ["# cross-sex-friendship — primary results\n"]
    lines.append(
        "Adjusted cell means (intercept of WLS of outcome ~ per-outcome "
        "adjustment set within each cell). Two stratification schemes "
        "(BIO_SEX × HAVEBMF and BIO_SEX × HAVEBFF), each producing 4 cells "
        "× 13 outcomes = 52 rows; both schemes together = 104 rows.\n"
    )
    for strat in matrix["stratification"].unique():
        lines.append(f"\n## {strat}\n")
        sub = matrix[matrix.stratification == strat]
        # Pivot to a wide cell-mean table per outcome.
        pvt = sub.pivot_table(
            index="outcome",
            columns=["sex", "friend_present"],
            values="adj_mean",
            aggfunc="first",
        )
        lines.append(pvt.round(3).to_markdown())
        lines.append("")
    lines.append(
        "\nTBD interpretation: which outcomes show a *cross-sex vs. same-sex* "
        "asymmetry within a sex? Compare `(female, friend=yes) - (female, "
        "friend=no)` for `HAVEBMF` (cross-sex contrast in females) against "
        "the same difference for `HAVEBFF` (same-sex contrast in females), "
        "and likewise for males. The figures.py forest plot is the visual "
        "form of this comparison.\n"
    )
    (TABLES_PRIMARY / "cross_sex.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _between_cell_contrasts(matrix: pd.DataFrame) -> pd.DataFrame:
    """Convert the per-cell adjusted-mean grid into between-cell contrasts.

    For each (stratification, sex, outcome), compute the difference between
    "friend present" and "friend absent" cells: Δ = mean_present − mean_absent.
    SE under independence: √(SE_a² + SE_b²). p-value: two-sided z-test.
    Output schema mimics a regular β table so it routes through the standard
    sensitivity helpers (E-value, Cornfield grid).
    """
    rows = []
    for (strat_label, friend_indicator, sex_name), grp in matrix.groupby(
        ["stratification", "friend_indicator", "sex"]
    ):
        for outcome_code, ogrp in grp.groupby("outcome"):
            present = ogrp[ogrp["friend_present"].astype(str).str.lower() == "yes"]
            absent = ogrp[ogrp["friend_present"].astype(str).str.lower() == "no"]
            if present.empty or absent.empty:
                continue
            p_row = present.iloc[0]
            a_row = absent.iloc[0]
            if pd.isna(p_row["adj_mean"]) or pd.isna(a_row["adj_mean"]):
                continue
            delta = float(p_row["adj_mean"]) - float(a_row["adj_mean"])
            se = float(np.sqrt(p_row["adj_se"] ** 2 + a_row["adj_se"] ** 2))
            z = delta / se if se > 0 else float("nan")
            p = float(2 * (1 - _scipy_stats.norm.cdf(abs(z)))) if np.isfinite(z) else float("nan")
            rows.append({
                "stratification": strat_label,
                "friend_indicator": friend_indicator,
                "sex": sex_name,
                "outcome": outcome_code,
                "outcome_label": p_row["outcome_label"],
                "outcome_group": p_row["outcome_group"],
                "n_present": int(p_row["n_cell"]),
                "n_absent": int(a_row["n_cell"]),
                "exposure": f"{friend_indicator}-present-vs-absent ({sex_name})",
                "label": f"{friend_indicator}+ vs {friend_indicator}- "
                         f"({sex_name}) -> {outcome_code}",
                "beta": delta,
                "se": se,
                "p": p,
                "sig": bool(np.isfinite(p) and p < 0.05),
            })
    return pd.DataFrame(rows)


def _sd_col(df: pd.DataFrame, col: str) -> float:
    if col not in df.columns:
        return float("nan")
    vals = clean_var(df[col], col).dropna()
    return float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")


def run_sensitivity_extended(df: pd.DataFrame, matrix: pd.DataFrame) -> dict:
    """E-value + Cornfield grid for cross-sex contrasts. η-tilt sweep uses
    the raw 0/1 friend-indicator (binary) within the relevant sex stratum
    for the most-significant contrast.
    """
    contrasts = _between_cell_contrasts(matrix)
    contrasts.to_csv(TABLES_SENS / "cross_sex_contrasts.csv", index=False)
    pri = contrasts.copy()
    pri["sd_x"] = 0.5  # binary friend indicator → SD ≈ 0.5
    pri["sd_y"] = pri["outcome"].map(lambda c: _sd_col(df, c))

    ev_full = build_evalue_table(
        pri, beta_col="beta", sd_x_col="sd_x", sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label",
                   "stratification", "sex"),
    )
    cf = build_cornfield_grid(
        pri, sd_x_col="sd_x", sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label",
                   "stratification", "sex"),
    )
    sig = pri.dropna(subset=["p"]).sort_values("p")
    target = sig[sig["p"] < 0.05].head(2)
    if target.empty:
        target = sig.head(2)
    cells = []
    for _, r in target.iterrows():
        sex_code = 2 if r["sex"] == "female" else 1
        sub = df.loc[df["BIO_SEX"] == sex_code].copy()
        cell = build_eta_cell_from_quintile_contrast(
            label=r["label"],
            df=sub,
            exposure_col=r["friend_indicator"],
            outcome_col=r["outcome"],
            weight_col="GSWGT4_2",
            cluster_col="CLUSTER2",
            adj_builder=lambda d: adj_for_outcome(d, r["outcome"]),
            extra_keys={"exposure": r["exposure"], "outcome": r["outcome"]},
            force_binary=True,
        )
        if cell is not None:
            cells.append(cell)
    eta_tbl = build_eta_tilt_table(cells)
    return {"evalue_full": ev_full, "cornfield": cf, "eta_tilt": eta_tbl,
            "contrasts": contrasts}


def main() -> None:
    print("Running cross-sex-friendship ...")
    df = _load_frame()
    matrix = run_primary(df)
    matrix.to_csv(TABLES_PRIMARY / "cross_sex_matrix.csv", index=False)
    print(f"Wrote {TABLES_PRIMARY / 'cross_sex_matrix.csv'} ({len(matrix)} rows)")

    sens = run_friendcoding_alt(df)
    sens.to_csv(TABLES_SENS / "cross_sex_friendcoding_alt.csv", index=False)
    print(f"Wrote {TABLES_SENS / 'cross_sex_friendcoding_alt.csv'} ({len(sens)} rows)")

    print("Sensitivity: extended (between-cell contrasts + E-value + Cornfield + η-tilt) ...")
    ext = run_sensitivity_extended(df, matrix)
    ext["evalue_full"].to_csv(
        TABLES_SENS / "cross_sex_evalue_chinn2000.csv", index=False)
    ext["cornfield"].to_csv(
        TABLES_SENS / "cross_sex_cornfield_grid.csv", index=False)
    ext["eta_tilt"].to_csv(
        TABLES_SENS / "cross_sex_eta_tilt.csv", index=False)
    print(f"Wrote {TABLES_SENS}/cross_sex_contrasts + evalue_chinn2000 + cornfield_grid + eta_tilt")

    write_markdown(matrix)
    print(f"Wrote {TABLES_PRIMARY / 'cross_sex.md'}")


if __name__ == "__main__":
    main()

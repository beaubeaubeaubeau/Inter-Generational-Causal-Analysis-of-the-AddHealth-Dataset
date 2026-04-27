"""EXP-QVQ -- friendship quality vs quantity vs frequency, head-to-head.

Three W1 in-home friendship-grid exposures fit JOINTLY (same regression)
per outcome, so each beta is the marginal effect conditional on the other
two friendship measures:

  - FRIEND_DISCLOSURE_ANY  (binary; quality / disclosure)
  - FRIEND_N_NOMINEES      (count 0-10; quantity)
  - FRIEND_CONTACT_SUM     (sum across nominees; frequency)

Sample frame: full W1 in-home cohort (no within-saturated-schools gate).
Outcomes: all 13 (cognitive + cardiometabolic + mental + functional + SES).

Design points (see ``dag.md``):
  - Joint fit, NOT separate fits. Joint is required because the three are
    empirically correlated; the marginal-conditional interpretation is the
    estimand the quality-vs-quantity hypothesis demands.
  - Per-outcome adjustment-set inheritance same as `popularity-vs-sociability`.
  - Sample-frame sensitivity vs the network-derived experiments is not
    directly comparable; see weak points in `dag.md`.

Sensitivity blocks:
  - Quintile dose-response on `FRIEND_N_NOMINEES` only (the only continuous-
    meaningful integer exposure; the other two are binary / sum-dominated).
  - Drop-one-exposure sensitivity: refit each outcome dropping each of the
    three exposures in turn, to see how much each beta shifts when its
    competitor is uncontrolled.
  - E-value per significant beta via `analysis.sensitivity.evalue`.

Outputs (relative to this experiment folder):
  tables/primary/qvq_primary.csv             (39 rows = 3 exposures x 13 outcomes)
  tables/primary/qvq_primary.md
  tables/sensitivity/qvq_quintile.csv
  tables/sensitivity/qvq_drop_one.csv
  tables/sensitivity/qvq_evalue.csv

Run as:
    python experiments/friendship-quality-vs-quantity/run.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analysis import CACHE  # noqa: E402
from analysis.cleaning import clean_var  # noqa: E402
from analysis.data_loading import load_outcome  # noqa: E402
from analysis.derivation import derive_friendship_grid  # noqa: E402
from analysis.wls import quintile_dummies, weighted_ols  # noqa: E402
from analysis.sensitivity import evalue  # noqa: E402
from analysis.sensitivity_panel import (  # noqa: E402
    build_cornfield_grid,
    build_eta_cell_from_quintile_contrast,
    build_eta_tilt_table,
    build_evalue_table,
)

TABLES_PRIMARY = HERE / "tables" / "primary"
TABLES_SENS = HERE / "tables" / "sensitivity"
for _p in (TABLES_PRIMARY, TABLES_SENS):
    _p.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Exposure & outcome registries
# ---------------------------------------------------------------------------
# Three friendship-grid exposures, fit JOINTLY (same regression). The
# (label) values describe the construct; the design matrix uses these
# columns by name.
EXPOSURES: Dict[str, str] = {
    "FRIEND_DISCLOSURE_ANY": "quality (talked to a nominated friend about a problem this past week, binary)",
    "FRIEND_N_NOMINEES":     "quantity (count of nominated friends, 0-10)",
    "FRIEND_CONTACT_SUM":    "frequency (sum across nominees of W1 friendship-grid contact items)",
}

# Same 13-outcome battery as popularity-vs-sociability.
OUTCOMES: Dict[str, Tuple[str, str]] = {
    "W4_COG_COMP": ("W4 cognitive composite", "cognitive"),
    "H4BMI":       ("S27 BMI -- W4", "cardiometabolic"),
    "H4WAIST":     ("S27 MEASURED WAIST (CM) -- W4", "cardiometabolic"),
    "H4SBP":       ("S27 SYSTOLIC BLOOD PRESSURE -- W4", "cardiometabolic"),
    "H4DBP":       ("S27 DIASTOLIC BLOOD PRESSURE -- W4", "cardiometabolic"),
    "H4BMICLS":    ("S27 BMI CLASS -- W4", "cardiometabolic"),
    "H5MN1":       ("S13Q1 LAST MO NO CNTRL IMPORT THINGS -- W5", "mental_health"),
    "H5MN2":       ("S13Q2 LAST MO CONFID HANDLE PERS PBMS -- W5", "mental_health"),
    "H5ID1":       ("S5Q1 HOW IS GEN PHYSICAL HEALTH -- W5", "functional"),
    "H5ID4":       ("S5Q4 LIMIT CLIMB SEV. FLIGHT STAIRS -- W5", "functional"),
    "H5ID16":      ("S5Q16 HOW OFTEN TROUBLE SLEEPING -- W5", "functional"),
    "H5LM5":       ("S3Q5 CURRENTLY WORK -- W5", "ses"),
    "H5EC1":       ("S4Q1 INCOME PERS EARNINGS [W4-W5] -- W5", "ses"),
}

# Per-outcome adjustment-set tier (inherits from per-outcome DAG; see dag.md).
ADJ_TIER_BY_OUTCOME: Dict[str, str] = {
    "W4_COG_COMP": "L0+L1+AHPVT",
    "H4BMI":       "L0+L1+AHPVT",
    "H4WAIST":     "L0+L1+AHPVT",
    "H4SBP":       "L0+L1+AHPVT",
    "H4DBP":       "L0+L1+AHPVT",
    "H4BMICLS":    "L0+L1+AHPVT",
    "H5MN1":       "L0+L1",
    "H5MN2":       "L0+L1",
    "H5ID1":       "L0+L1",
    "H5ID4":       "L0+L1",
    "H5ID16":      "L0+L1",
    "H5LM5":       "L0+L1",  # DAG-SES drops AHPVT
    "H5EC1":       "L0+L1",
}

RACE_LEVELS = ["NH-Black", "Hispanic", "Other"]


# ---------------------------------------------------------------------------
# Adjustment-set builders
# ---------------------------------------------------------------------------
def _race_dummies(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for lvl in RACE_LEVELS:
        out[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    out.loc[df["RACE"].isna(), :] = np.nan
    return out


def _adj_L0(df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index),
        _race_dummies(df),
        df["PARENT_ED"].rename("parent_ed"),
    ], axis=1)


def _adj_L0_L1(df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([
        _adj_L0(df),
        df["CESD_SUM"].rename("cesd_sum"),
        df["H1GH1"].rename("srh"),
    ], axis=1)


def _adj_L0_L1_AHPVT(df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([
        _adj_L0_L1(df),
        df["AH_RAW"].rename("ahpvt"),
    ], axis=1)


ADJ_BUILDERS: Dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "L0":          _adj_L0,
    "L0+L1":       _adj_L0_L1,
    "L0+L1+AHPVT": _adj_L0_L1_AHPVT,
}


# ---------------------------------------------------------------------------
# Frame loading
# ---------------------------------------------------------------------------
def _load_frame() -> pd.DataFrame:
    """Load the W1 in-home full cohort frame and attach the friendship-grid
    derivations + W4/W5 outcomes via load_outcome.

    Prefers `analytic_w1_full.parquet` if present (precomputed friendship
    columns); otherwise falls back to deriving from `w1inhome.parquet`.
    `analytic_w4.parquet` is used as a fallback for outcome attachment when
    the W1-full frame doesn't carry the W4 cohort restriction.
    """
    w1_full_path = CACHE / "analytic_w1_full.parquet"
    if w1_full_path.exists():
        DF = pd.read_parquet(w1_full_path)
    else:
        # Fall back to the W4 analytic frame (smaller cohort, but always available
        # since it underlies the screening experiments). Derive friendship grid
        # in-place if the columns aren't already there.
        DF = pd.read_parquet(CACHE / "analytic_w4.parquet")
    # Defensive derivation: if any of the three exposure columns is missing,
    # derive them from the W1 in-home raw parquet.
    missing_cols = [c for c in EXPOSURES if c not in DF.columns]
    if missing_cols:
        w1 = pd.read_parquet(CACHE / "w1inhome.parquet")
        # Align on AID; fill the missing columns.
        derived = derive_friendship_grid(w1)
        derived["AID"] = w1["AID"].values
        DF = DF.merge(derived[["AID"] + list(EXPOSURES.keys())],
                      on="AID", how="left", suffixes=("", "_derived"))
    # Attach W4/W5 outcomes.
    for code in OUTCOMES:
        if code in DF.columns:
            continue
        DF[code] = load_outcome(DF["AID"], code)
    return DF


# ---------------------------------------------------------------------------
# Joint-fit primitive: all three exposures in the same regression
# ---------------------------------------------------------------------------
def _fit_joint(df: pd.DataFrame, outcome_col: str,
               adj_builder: Callable[[pd.DataFrame], pd.DataFrame],
               exposure_cols: Optional[List[str]] = None,
               w_col: str = "GSWGT4_2") -> Optional[dict]:
    """Joint WLS of `outcome ~ const + (joint exposures) + adjustment`.

    `exposure_cols` defaults to all three EXPOSURES. The drop-one sensitivity
    refits the same spec but with one column dropped from this list.
    """
    cols = list(exposure_cols) if exposure_cols is not None else list(EXPOSURES.keys())
    parts = []
    for c in cols:
        parts.append(clean_var(df[c], c).rename(c))
    parts.append(adj_builder(df))
    X = pd.concat(parts, axis=1)
    X.insert(0, "const", 1.0)
    return weighted_ols(
        df[outcome_col].values, X.values,
        df[w_col].values, df["CLUSTER2"].values,
        column_names=list(X.columns),
    )


# ---------------------------------------------------------------------------
# Primary block: 3 exposures (joint) x 13 outcomes
# ---------------------------------------------------------------------------
def run_primary(DF: pd.DataFrame) -> pd.DataFrame:
    """One joint regression per outcome; emit one row per (exposure, outcome) cell."""
    rows = []
    for outcome_code, (label, o_group) in OUTCOMES.items():
        tier = ADJ_TIER_BY_OUTCOME[outcome_code]
        res = _fit_joint(DF, outcome_code, ADJ_BUILDERS[tier])
        for exp_name in EXPOSURES:
            row = {
                "exposure": exp_name, "outcome": outcome_code,
                "outcome_label": label, "outcome_group": o_group,
                "adj_tier": tier,
            }
            if res is None or exp_name not in res["beta"].index:
                row.update({
                    "n": 0 if res is None else int(res["n"]),
                    "beta": np.nan, "se": np.nan, "p": np.nan,
                    "ci_lo": np.nan, "ci_hi": np.nan, "sig": False,
                })
            else:
                p = float(res["p"][exp_name])
                row.update({
                    "n": int(res["n"]),
                    "beta": float(res["beta"][exp_name]),
                    "se": float(res["se"][exp_name]),
                    "p": p,
                    "ci_lo": float(res["ci_lo"][exp_name]),
                    "ci_hi": float(res["ci_hi"][exp_name]),
                    "sig": bool(p < 0.05),
                })
            rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity 1 -- quintile dose-response on FRIEND_N_NOMINEES
# ---------------------------------------------------------------------------
def run_sensitivity_quintile(DF: pd.DataFrame) -> pd.DataFrame:
    """Quintile dose-response on `FRIEND_N_NOMINEES` only (continuous-meaningful).

    The other two exposures (binary `FRIEND_DISCLOSURE_ANY`, sum-dominated
    `FRIEND_CONTACT_SUM`) remain in the joint fit alongside the quintile
    contrast.
    """
    rows = []
    nom_clean = clean_var(DF["FRIEND_N_NOMINEES"], "FRIEND_N_NOMINEES")
    dummies, trend = quintile_dummies(nom_clean, n=5)
    for outcome_code, (label, o_group) in OUTCOMES.items():
        tier = ADJ_TIER_BY_OUTCOME[outcome_code]
        adj = ADJ_BUILDERS[tier](DF)
        # Trend spec
        X_t = pd.concat([
            trend.rename("nominees_qtrend"),
            clean_var(DF["FRIEND_DISCLOSURE_ANY"], "FRIEND_DISCLOSURE_ANY")
                .rename("FRIEND_DISCLOSURE_ANY"),
            clean_var(DF["FRIEND_CONTACT_SUM"], "FRIEND_CONTACT_SUM")
                .rename("FRIEND_CONTACT_SUM"),
            adj,
        ], axis=1)
        X_t.insert(0, "const", 1.0)
        res_t = weighted_ols(
            DF[outcome_code].values, X_t.values,
            DF["GSWGT4_2"].values, DF["CLUSTER2"].values,
            column_names=list(X_t.columns),
        )
        row = {
            "outcome": outcome_code, "outcome_label": label,
            "outcome_group": o_group, "adj_tier": tier,
        }
        if res_t is not None:
            row["beta_trend"] = float(res_t["beta"]["nominees_qtrend"])
            row["se_trend"]   = float(res_t["se"]["nominees_qtrend"])
            row["p_trend"]    = float(res_t["p"]["nominees_qtrend"])
        rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity 2 -- drop-one-exposure
# ---------------------------------------------------------------------------
def run_sensitivity_drop_one(DF: pd.DataFrame) -> pd.DataFrame:
    """For each (outcome, dropped-exposure) pair: refit the joint spec without
    the dropped exposure, and report the surviving betas. Pairs with
    `qvq_primary.csv` to show how much each beta shifts when its competitor
    is uncontrolled."""
    rows = []
    exposure_list = list(EXPOSURES.keys())
    for outcome_code, (label, o_group) in OUTCOMES.items():
        tier = ADJ_TIER_BY_OUTCOME[outcome_code]
        for dropped in exposure_list:
            kept = [e for e in exposure_list if e != dropped]
            res = _fit_joint(DF, outcome_code, ADJ_BUILDERS[tier],
                             exposure_cols=kept)
            for exp_name in kept:
                row = {
                    "outcome": outcome_code, "outcome_label": label,
                    "outcome_group": o_group, "dropped": dropped,
                    "exposure": exp_name,
                }
                if res is None or exp_name not in res["beta"].index:
                    row.update({"beta": np.nan, "se": np.nan, "p": np.nan})
                else:
                    row.update({
                        "beta": float(res["beta"][exp_name]),
                        "se":   float(res["se"][exp_name]),
                        "p":    float(res["p"][exp_name]),
                    })
                rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity 3 -- E-values per significant beta
# ---------------------------------------------------------------------------
def run_sensitivity_evalue(primary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in primary.iterrows():
        if not r["sig"] or pd.isna(r["beta"]):
            continue
        try:
            rr_proxy = float(np.exp(abs(r["beta"])))
            ev = evalue(rr_proxy)
        except (ValueError, OverflowError):
            rr_proxy = np.nan
            ev = np.nan
        rows.append({
            "exposure": r["exposure"], "outcome": r["outcome"],
            "outcome_group": r["outcome_group"], "beta": r["beta"],
            "p": r["p"], "rr_proxy_unit_exposure": rr_proxy,
            "evalue_unit_exposure": ev,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity 4 — Cornfield bias-factor grid + η-tilt sweep + Chinn-2000 E-value
# ---------------------------------------------------------------------------
def _outcome_sd(DF: pd.DataFrame, code: str) -> float:
    if code not in DF.columns:
        return float("nan")
    vals = pd.to_numeric(DF[code], errors="coerce").dropna()
    return float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")


def _exposure_sd(DF: pd.DataFrame, exp_col: str) -> float:
    if exp_col not in DF.columns:
        return float("nan")
    vals = clean_var(DF[exp_col], exp_col).dropna()
    return float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")


def run_sensitivity_extended(DF: pd.DataFrame, primary: pd.DataFrame) -> dict:
    """Cornfield bias-factor grid + η-tilt sweep + Chinn-2000 E-values.

    Mixed-A note: ``FRIEND_DISCLOSURE_ANY`` is binary; the other two
    exposures (``FRIEND_N_NOMINEES`` integer 0-10 and ``FRIEND_CONTACT_SUM``
    sum-across-nominees) are continuous. The η-tilt sweep is run on the raw
    binary code where applicable and on a top-quintile-vs-bottom-quintile
    binarisation otherwise; the ``binarisation`` column on each row of the
    eta-tilt CSV records which mode was used.
    """
    primary = primary.copy()
    primary["sd_x"] = primary["exposure"].map(lambda c: _exposure_sd(DF, c))
    primary["sd_y"] = primary["outcome"].map(lambda c: _outcome_sd(DF, c))
    primary["label"] = primary["exposure"] + " -> " + primary["outcome"]

    ev_full = build_evalue_table(
        primary,
        beta_col="beta",
        sd_x_col="sd_x",
        sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label"),
    )
    cf = build_cornfield_grid(
        primary,
        sd_x_col="sd_x",
        sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label"),
    )
    sig = primary[primary["sig"] & primary["p"].notna()].sort_values("p").head(2)
    cells = []
    for _, r in sig.iterrows():
        adj_builder = ADJ_BUILDERS[r["adj_tier"]]
        cell = build_eta_cell_from_quintile_contrast(
            label=r["label"],
            df=DF,
            exposure_col=r["exposure"],
            outcome_col=r["outcome"],
            weight_col="GSWGT4_2",
            cluster_col="CLUSTER2",
            adj_builder=adj_builder,
            extra_keys={"exposure": r["exposure"], "outcome": r["outcome"]},
        )
        if cell is not None:
            cells.append(cell)
    eta_tbl = build_eta_tilt_table(cells)
    return {"evalue_full": ev_full, "cornfield": cf, "eta_tilt": eta_tbl}


# ---------------------------------------------------------------------------
# Markdown writer
# ---------------------------------------------------------------------------
def write_primary_markdown(primary: pd.DataFrame) -> None:
    lines = ["# EXP-QVQ -- friendship quality vs quantity, head-to-head joint fit\n"]
    lines.append(
        "Per-outcome WLS beta for the three friendship-grid exposures, fit "
        "**JOINTLY** (same regression) so each beta is the marginal effect "
        "conditional on the other two friendship measures. Cluster-robust SE "
        "on `CLUSTER2`. Sample frame: full W1 in-home cohort. See "
        "[dag.md](../../dag.md) for the per-outcome adjustment-set inheritance.\n"
    )
    show = primary.copy()
    for c in ("beta", "se", "ci_lo", "ci_hi"):
        show[c] = show[c].map(lambda v: f"{v:.4g}" if pd.notna(v) else "NA")
    show["p"] = show["p"].map(lambda v: f"{v:.3g}" if pd.notna(v) else "NA")
    lines.append(show[["exposure", "outcome", "outcome_group", "n",
                       "beta", "se", "ci_lo", "ci_hi", "p", "sig"]]
                 .to_markdown(index=False))
    (TABLES_PRIMARY / "qvq_primary.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def run_qvq() -> pd.DataFrame:
    print("Loading W1 in-home + W4/W5 outcomes ...")
    DF = _load_frame()
    print("Running primary 3x13 joint-fit grid ...")
    primary = run_primary(DF)
    primary.to_csv(TABLES_PRIMARY / "qvq_primary.csv", index=False)
    write_primary_markdown(primary)

    print("Sensitivity: quintile dose-response on FRIEND_N_NOMINEES ...")
    quint = run_sensitivity_quintile(DF)
    quint.to_csv(TABLES_SENS / "qvq_quintile.csv", index=False)

    print("Sensitivity: drop-one-exposure ...")
    drop = run_sensitivity_drop_one(DF)
    drop.to_csv(TABLES_SENS / "qvq_drop_one.csv", index=False)

    print("Sensitivity: E-values per significant beta ...")
    ev = run_sensitivity_evalue(primary)
    ev.to_csv(TABLES_SENS / "qvq_evalue.csv", index=False)

    print("Sensitivity: extended (Cornfield grid + η-tilt + Chinn-2000 E-values) ...")
    ext = run_sensitivity_extended(DF, primary)
    ext["evalue_full"].to_csv(
        TABLES_SENS / "qvq_evalue_chinn2000.csv", index=False)
    ext["cornfield"].to_csv(
        TABLES_SENS / "qvq_cornfield_grid.csv", index=False)
    ext["eta_tilt"].to_csv(
        TABLES_SENS / "qvq_eta_tilt.csv", index=False)
    return primary


def main() -> None:
    run_qvq()


if __name__ == "__main__":
    main()

"""lonely-at-the-top — popularity × loneliness paradox via continuous interaction.

Tests whether `IDGX2 × H1FS13` (popularity × loneliness, both z-scored)
predicts mid-life cardiometabolic / mental-health / functional outcomes
*after adjusting for both main effects*. The interaction coefficient β₃
is the headline paradox test.

Pre-flight (2026-04-26): a median-split 2x2 of IDGX2 × H1FS13 had minimum
cell N = 73, below the project's N ≥ 150 positivity floor. The stratified
design was abandoned; this script implements the continuous interaction.
The 4-cell descriptive means are still computed under "Sensitivity" for
narrative purposes only — they are NOT identification claims.

This file is a SKELETON — the analytic primitives are wired but no full run
has been validated against the data.

Outputs:
  tables/primary/lonely_top_matrix.csv
  tables/primary/lonely_top.md
  tables/sensitivity/lonely_top_2x2_descriptive.csv
  tables/sensitivity/lonely_top_interaction_surface.csv
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

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

TABLES_PRIMARY = HERE / "tables" / "primary"
TABLES_SENS = HERE / "tables" / "sensitivity"
TABLES_PRIMARY.mkdir(parents=True, exist_ok=True)
TABLES_SENS.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Outcome battery — cardiometabolic + mental + functional subset.
# ---------------------------------------------------------------------------
OUTCOMES: Dict[str, Tuple[str, str, str, str]] = {
    "H4BMI":   ("S27 BMI—W4",                                  "cardiometabolic", "continuous", "GSWGT4_2"),
    "H4WAIST": ("S27 MEASURED WAIST (CM)—W4",                  "cardiometabolic", "continuous", "GSWGT4_2"),
    "H5MN1":   ("S13Q1 LAST MO NO CNTRL IMPORT THINGS—W5",     "mental_health",   "likert-1-5", "GSW5"),
    "H5MN2":   ("S13Q2 LAST MO CONFID HANDLE PERS PBMS—W5",    "mental_health",   "likert-1-5", "GSW5"),
    "H5ID1":   ("S5Q1 HOW IS GEN PHYSICAL HEALTH—W5",          "functional",      "likert-1-5", "GSW5"),
}

POP_COL = "IDGX2"          # popularity (in-degree)
LONE_COL = "H1FS13"        # loneliness item (CES-D §13: "I felt lonely")

# Pre-flight result locked here:
PREFLIGHT_MIN_CELL_N_2X2 = 73   # < 150 positivity floor → 2x2 abandoned
POSITIVITY_FLOOR = 150


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


def _adj_full(df: pd.DataFrame) -> pd.DataFrame:
    return pd.concat([
        _adj_L0_L1(df),
        df["AH_RAW"].rename("ahpvt"),
    ], axis=1)


ADJ_BUILDERS: Dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "L0": _adj_L0,
    "L0+L1": _adj_L0_L1,
    "L0+L1+AHPVT": _adj_full,
}


# ---------------------------------------------------------------------------
# Frame loading + interaction construction
# ---------------------------------------------------------------------------
def _load_frame() -> pd.DataFrame:
    """Load W4 saturated-school frame, attach H1FS13 from raw W1, and outcomes.

    Question for next pass: is `H1FS13` already present on `analytic_w4.parquet`,
    or does it need to be merged in from `w1inhome.parquet`? The skeleton
    assumes it must be merged (mirroring how `multi-outcome-screening` merges
    `H1PR4`); revisit once the cached frames' columns are inspected.
    """
    W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
    if LONE_COL not in W4.columns:
        w1raw = pd.read_parquet(CACHE / "w1inhome.parquet", columns=["AID", LONE_COL])
        w1raw[LONE_COL] = clean_var(w1raw[LONE_COL], LONE_COL)
        W4 = W4.merge(w1raw, on="AID", how="left")
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
        W4[code] = load_outcome(W4["AID"], code)
    # Construct z-scored interaction term up front.
    pop = clean_var(W4[POP_COL], POP_COL)
    lone = clean_var(W4[LONE_COL], LONE_COL)
    W4["IDGX2_z"] = (pop - pop.mean()) / pop.std(ddof=0)
    W4["H1FS13_z"] = (lone - lone.mean()) / lone.std(ddof=0)
    W4["IDGX2_x_H1FS13"] = W4["IDGX2_z"] * W4["H1FS13_z"]
    return W4


# ---------------------------------------------------------------------------
# Fit primitive — three exposure terms forced into the model.
# ---------------------------------------------------------------------------
def _fit_interaction(df: pd.DataFrame, y_col: str,
                     adj_builder: Callable[[pd.DataFrame], pd.DataFrame],
                     w_col: str) -> Optional[dict]:
    """WLS of y on [IDGX2_z, H1FS13_z, IDGX2_x_H1FS13, adj]."""
    main_pop = df["IDGX2_z"]
    main_lone = df["H1FS13_z"]
    inter = df["IDGX2_x_H1FS13"]
    adj = adj_builder(df)
    X = pd.concat([
        main_pop.rename("IDGX2_z"),
        main_lone.rename("H1FS13_z"),
        inter.rename("IDGX2_x_H1FS13"),
        adj,
    ], axis=1)
    X.insert(0, "const", 1.0)
    y = df[y_col].values
    w = df[w_col].values
    psu = df["CLUSTER2"].values
    return weighted_ols(y, X.values, w, psu, column_names=list(X.columns))


# ---------------------------------------------------------------------------
# Primary matrix
# ---------------------------------------------------------------------------
def run_primary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome_code, (label, group, kind, w_col) in OUTCOMES.items():
        weight_col = w_col if w_col in df.columns and df[w_col].notna().any() else "GSWGT4_2"
        for adj_name, builder in ADJ_BUILDERS.items():
            res = _fit_interaction(df, outcome_code, builder, w_col=weight_col)
            if res is None:
                rows.append({
                    "outcome": outcome_code, "outcome_label": label,
                    "outcome_group": group, "adj": adj_name,
                    "n": 0, "beta_pop": np.nan, "beta_lone": np.nan,
                    "beta_inter": np.nan, "se_inter": np.nan, "p_inter": np.nan,
                    "ci_lo_inter": np.nan, "ci_hi_inter": np.nan,
                    "weight_col_used": weight_col,
                })
                continue
            rows.append({
                "outcome": outcome_code,
                "outcome_label": label,
                "outcome_group": group,
                "adj": adj_name,
                "n": int(res["n"]),
                "beta_pop": float(res["beta"]["IDGX2_z"]),
                "se_pop": float(res["se"]["IDGX2_z"]),
                "p_pop": float(res["p"]["IDGX2_z"]),
                "beta_lone": float(res["beta"]["H1FS13_z"]),
                "se_lone": float(res["se"]["H1FS13_z"]),
                "p_lone": float(res["p"]["H1FS13_z"]),
                "beta_inter": float(res["beta"]["IDGX2_x_H1FS13"]),
                "se_inter": float(res["se"]["IDGX2_x_H1FS13"]),
                "p_inter": float(res["p"]["IDGX2_x_H1FS13"]),
                "ci_lo_inter": float(res["ci_lo"]["IDGX2_x_H1FS13"]),
                "ci_hi_inter": float(res["ci_hi"]["IDGX2_x_H1FS13"]),
                "weight_col_used": weight_col,
                "paradox_test_pass": float(res["p"]["IDGX2_x_H1FS13"]) < 0.05,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity (a) — descriptive 2x2 weighted means.
# Explicitly under-powered; reported only for narrative/visual aid.
# ---------------------------------------------------------------------------
def run_2x2_descriptive(df: pd.DataFrame) -> pd.DataFrame:
    # IDGX2 supports a median split (continuous-ish, median = 4 nominations).
    # H1FS13 is a 4-point CES-D item (0-3) with mode = 0 ("never lonely past
    # week"); the median is 0 so a `>= median` rule lumps EVERY respondent with
    # any loneliness rating into the "high" cell and leaves the "low" cell
    # populated only by NaN rows. Threshold loneliness at "any > 0" instead;
    # this matches the pre-flight N=73 / N=150 cell-count audit recorded in
    # `reference/research_journal.md`.
    pop_med = df["IDGX2_z"].median()
    high_pop = df["IDGX2_z"] >= pop_med
    high_lone = df["H1FS13"] > 0  # any loneliness rating above "never"
    cells = {
        "low_pop_low_lone":   (~high_pop) & (~high_lone),
        "low_pop_high_lone":  (~high_pop) & (high_lone),
        "high_pop_low_lone":  (high_pop) & (~high_lone),
        "high_pop_high_lone": (high_pop) & (high_lone),
    }
    rows = []
    for outcome_code, (label, group, kind, w_col) in OUTCOMES.items():
        weight_col = w_col if w_col in df.columns and df[w_col].notna().any() else "GSWGT4_2"
        y = df[outcome_code].values
        w = df[weight_col].values
        for cell_name, mask in cells.items():
            mvals = mask.values
            sel = mvals & ~np.isnan(y) & ~np.isnan(w) & (w > 0)
            n_cell = int(sel.sum())
            if n_cell == 0:
                wmean = np.nan
            else:
                wmean = float(np.sum(w[sel] * y[sel]) / np.sum(w[sel]))
            rows.append({
                "outcome": outcome_code,
                "outcome_label": label,
                "cell": cell_name,
                "n_cell": n_cell,
                "weighted_mean": wmean,
                "below_positivity_floor": n_cell < POSITIVITY_FLOOR,
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity (b) — interaction surface for the primary outcome (H4BMI).
# A small grid of predicted means at fixed (z_pop, z_lone) combinations.
# ---------------------------------------------------------------------------
def run_interaction_surface(df: pd.DataFrame, outcome: str = "H4BMI") -> pd.DataFrame:
    weight_col = "GSWGT4_2"
    res = _fit_interaction(df, outcome, _adj_full, w_col=weight_col)
    if res is None:
        return pd.DataFrame()
    b = res["beta"]
    # Predicted means with adj-vars set to 0 (i.e. centred / reference).
    grid_z = np.linspace(-2.0, 2.0, 9)
    rows = []
    for zp in grid_z:
        for zl in grid_z:
            pred = (
                b["const"]
                + b["IDGX2_z"] * zp
                + b["H1FS13_z"] * zl
                + b["IDGX2_x_H1FS13"] * zp * zl
            )
            rows.append({"z_pop": zp, "z_lone": zl, "pred_outcome": pred})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Markdown narrative
# ---------------------------------------------------------------------------
def _sd_col(df: pd.DataFrame, col: str) -> float:
    if col not in df.columns:
        return float("nan")
    vals = clean_var(df[col], col).dropna()
    return float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")


def run_sensitivity_extended(df: pd.DataFrame, primary: pd.DataFrame) -> dict:
    """E-value + Cornfield grid + η-tilt for the IDGX2 × H1FS13 paradox
    interaction. Continuous-A note: the η-tilt sweep operates on a top-vs-
    bottom-quintile binarisation of the standardised popularity x loneliness
    PRODUCT (the paradox-cell exposure), so "treated" = high-pop AND
    high-lonely tail and "control" = low-pop AND low-lonely tail.
    """
    sd_pop = _sd_col(df, "IDGX2")
    sd_lone = _sd_col(df, "H1FS13")
    # Interaction-term SD on the standardised product = 1 (z(IDGX2) × z(H1FS13)
    # has unit variance after centring); we use the product of unit SDs as
    # the conservative pseudo-SD for Chinn-2000 scaling.
    sd_inter = 1.0 if (np.isfinite(sd_pop) and np.isfinite(sd_lone)) else float("nan")

    pri = primary.copy()
    pri["sd_x"] = sd_inter
    pri["sd_y"] = pri["outcome"].map(lambda c: _sd_col(df, c))
    pri["beta"] = pri["beta_inter"]
    pri["p"] = pri["p_inter"]
    pri["label"] = "z(IDGX2) x z(H1FS13) -> " + pri["outcome"]
    pri["exposure"] = "z(IDGX2) x z(H1FS13)"
    pri["outcome_group"] = pri["outcome_group"]

    ev_full = build_evalue_table(
        pri, beta_col="beta", sd_x_col="sd_x", sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label"),
    )
    cf = build_cornfield_grid(
        pri, sd_x_col="sd_x", sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label"),
    )
    # η-tilt: build a paradox-product exposure column on the frame, then
    # cut to top-vs-bottom quintile.
    df2 = df.copy()
    pop_z = (clean_var(df2["IDGX2"], "IDGX2") - clean_var(df2["IDGX2"], "IDGX2").mean()) / sd_pop
    lone_z = (clean_var(df2["H1FS13"], "H1FS13") - clean_var(df2["H1FS13"], "H1FS13").mean()) / sd_lone
    df2["_paradox"] = pop_z * lone_z
    sig = pri.dropna(subset=["p"]).sort_values("p")
    target = sig[sig["p"] < 0.05].head(2)
    if target.empty:
        target = sig.head(2)
    cells = []
    for _, r in target.iterrows():
        w_col = r.get("weight_col_used", "GSWGT4_2")
        cell = build_eta_cell_from_quintile_contrast(
            label=r["label"],
            df=df2,
            exposure_col="_paradox",
            outcome_col=r["outcome"],
            weight_col=w_col,
            cluster_col="CLUSTER2",
            adj_builder=_adj_full,
            extra_keys={"exposure": "z(IDGX2) x z(H1FS13)", "outcome": r["outcome"]},
        )
        if cell is not None:
            cells.append(cell)
    eta_tbl = build_eta_tilt_table(cells)
    return {"evalue_full": ev_full, "cornfield": cf, "eta_tilt": eta_tbl}


def write_markdown(matrix: pd.DataFrame) -> None:
    lines = ["# lonely-at-the-top — primary results\n"]
    lines.append(
        "WLS of each mid-life outcome on `[IDGX2_z, H1FS13_z, IDGX2_x_H1FS13, "
        "adj]`. Three nested adjustment tiers (L0 / L0+L1 / L0+L1+AHPVT). "
        "The interaction coefficient β₃ on `IDGX2_x_H1FS13` is the headline "
        "paradox test (β₃ ≠ 0 ⇒ paradox confirmed).\n"
    )
    lines.append(
        f"\n**Pre-flight note:** the median-split 2x2 of (IDGX2, H1FS13) has "
        f"minimum cell N = {PREFLIGHT_MIN_CELL_N_2X2}, below the project "
        f"positivity floor of N ≥ {POSITIVITY_FLOOR}. The 2x2 is therefore "
        "abandoned for identification; this script reports the continuous "
        "interaction as the primary estimand. The 4-cell weighted means are "
        "still produced (`tables/sensitivity/lonely_top_2x2_descriptive.csv`) "
        "as a narrative aid, with the under-powered cells flagged.\n"
    )
    lines.append("## Per-outcome interaction β₃ (primary spec L0+L1+AHPVT)\n")
    primary = matrix[matrix.adj == "L0+L1+AHPVT"].copy()
    show = primary[[
        "outcome", "outcome_label", "outcome_group", "n",
        "beta_inter", "se_inter", "p_inter",
        "ci_lo_inter", "ci_hi_inter", "paradox_test_pass",
    ]].copy()
    for c in ["beta_inter", "se_inter", "ci_lo_inter", "ci_hi_inter"]:
        show[c] = show[c].map(lambda v: f"{v:.4g}" if pd.notna(v) else "NA")
    show["p_inter"] = show["p_inter"].map(lambda v: f"{v:.3g}" if pd.notna(v) else "NA")
    lines.append(show.to_markdown(index=False))
    lines.append("")
    n_pass = int(primary["paradox_test_pass"].sum())
    lines.append(
        f"\nTBD interpretation: {n_pass} / {len(primary)} outcomes show a "
        "significant interaction (paradox test passes). Inspect signs to "
        "determine whether high-pop/high-lonely is *worse* than additive "
        "for each outcome.\n"
    )
    (TABLES_PRIMARY / "lonely_top.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("Running lonely-at-the-top ...")
    df = _load_frame()
    primary = run_primary(df)
    primary.to_csv(TABLES_PRIMARY / "lonely_top_matrix.csv", index=False)
    print(f"Wrote {TABLES_PRIMARY / 'lonely_top_matrix.csv'} ({len(primary)} rows)")

    desc = run_2x2_descriptive(df)
    desc.to_csv(TABLES_SENS / "lonely_top_2x2_descriptive.csv", index=False)
    print(f"Wrote {TABLES_SENS / 'lonely_top_2x2_descriptive.csv'} ({len(desc)} rows)")

    surface = run_interaction_surface(df, outcome="H4BMI")
    surface.to_csv(TABLES_SENS / "lonely_top_interaction_surface.csv", index=False)
    print(f"Wrote {TABLES_SENS / 'lonely_top_interaction_surface.csv'} ({len(surface)} rows)")

    print("Sensitivity: extended (E-value + Cornfield grid + η-tilt) ...")
    ext = run_sensitivity_extended(df, primary)
    ext["evalue_full"].to_csv(
        TABLES_SENS / "lonely_top_evalue_chinn2000.csv", index=False)
    ext["cornfield"].to_csv(
        TABLES_SENS / "lonely_top_cornfield_grid.csv", index=False)
    ext["eta_tilt"].to_csv(
        TABLES_SENS / "lonely_top_eta_tilt.csv", index=False)
    print(f"Wrote {TABLES_SENS}/lonely_top_evalue_chinn2000.csv + cornfield_grid + eta_tilt")

    write_markdown(primary)
    print(f"Wrote {TABLES_PRIMARY / 'lonely_top.md'}")


if __name__ == "__main__":
    main()

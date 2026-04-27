"""popularity-and-substance-use — dark-side outcome screen for IDGX2.

Tests whether the W1 in-degree popularity exposure (`IDGX2`) that yields
protective cardiometabolic associations in `multi-outcome-screening` flips
sign for substance-use outcomes. Implements:

  1. WLS fits (primary L0+L1+AHPVT) for `IDGX2` against the 8 substance-use
     outcomes (5 W4, 3 W5), with cluster-SE on `CLUSTER2`.
  2. Adjustment-set stability across L0 / L0+L1 / L0+L1+AHPVT (D4-style).
  3. Quintile dose-response via `analysis.wls:quintile_dummies`.
  4. E-value sensitivity bound per significant pair via `analysis.sensitivity:evalue`.

The substance-use variable list is HARDCODED from the 2026-04-26 pre-flight
inventory; do not edit without re-checking codebook reserve-code patterns
in `scripts/analysis/cleaning.py:VALID_RANGES`.

This file is a SKELETON — the analytic primitives are wired but no full run
has been validated against the data. Outputs are written if the cached frames
exist; otherwise the script prints a load-error and exits non-zero.

Outputs (relative to this experiment folder):
  tables/primary/popularity_subst_matrix.csv
  tables/primary/popularity_subst.md
  tables/sensitivity/popularity_subst_quintiles.csv
  tables/sensitivity/popularity_subst_evalues.csv
"""
from __future__ import annotations

import math
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
from analysis.wls import weighted_ols, quintile_dummies  # noqa: E402
from analysis.data_loading import load_outcome  # noqa: E402
from analysis.sensitivity import evalue  # noqa: E402
from analysis.sensitivity_panel import (  # noqa: E402
    build_cornfield_grid,
    build_eta_cell_from_quintile_contrast,
    build_eta_tilt_table,
    build_evalue_table,
)

# Outcomes whose raw codebook uses 97 = "legitimate skip" (never drank /
# never used the substance). Per the design decision recorded in the
# experiment's report: re-code 97 -> 0 BEFORE the (0, 6) reserve-code gate
# in clean_var, so the analytic frame retains never-users at the zero end
# of the frequency scale rather than dropping them. Refuse/DK codes (96, 98)
# remain reserve and become NaN.
LEGIT_SKIP_TO_ZERO_OUTCOMES = ("H4TO39", "H4TO70", "H5TO12", "H5TO15")

TABLES_PRIMARY = HERE / "tables" / "primary"
TABLES_SENS = HERE / "tables" / "sensitivity"
TABLES_PRIMARY.mkdir(parents=True, exist_ok=True)
TABLES_SENS.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Outcome battery — locked from 2026-04-26 pre-flight inventory.
#   Keys are codebook codes; tuple = (label, wave, kind, weight_col).
#   Labels MUST match codebook wording verbatim (per project memory rule).
# ---------------------------------------------------------------------------
SUBSTANCE_OUTCOMES: Dict[str, Tuple[str, str, str, str]] = {
    # W4 substance use (GSWGT4_2)
    "H4TO5":   ("S28Q5 SMOKING DAYS PAST 30 DAYS—W4",        "W4", "count-0-30",   "GSWGT4_2"),
    "H4TO39":  ("S28Q39 DRINKING DAYS PAST 30 DAYS—W4",       "W4", "count-0-30",   "GSWGT4_2"),
    "H4TO70":  ("S28Q70 MARIJUANA DAYS PAST 12 MONTHS—W4",    "W4", "count-0-365",  "GSWGT4_2"),
    "H4TO65B": ("S28Q65B EVER USED MARIJUANA—W4",             "W4", "binary",       "GSWGT4_2"),
    "H4TO65C": ("S28Q65C EVER USED COCAINE—W4",               "W4", "binary",       "GSWGT4_2"),
    # W5 substance use (GSW5; W4->W5 attrition caveat applies)
    "H5TO2":   ("S6Q2 SMOKING DAYS PAST 30 DAYS—W5",          "W5", "count-0-30",   "GSW5"),
    "H5TO12":  ("S6Q12 ALCOHOL DAYS PAST 12 MONTHS—W5",       "W5", "count-0-365",  "GSW5"),
    "H5TO15":  ("S6Q15 BINGE-DRINKING DAYS PAST 12 MONTHS—W5","W5", "count-0-365",  "GSW5"),
}

# Single exposure: in-degree popularity. Network exposure → restricted to
# saturated schools (the W4 analytic frame is already so restricted).
EXPOSURE_COL = "IDGX2"


# ---------------------------------------------------------------------------
# Adjustment-set builders — mirror multi-outcome-screening.
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
# Frame loading
# ---------------------------------------------------------------------------
def _load_frame() -> pd.DataFrame:
    """Load the W4 saturated-schools analytic frame and attach all 8 outcomes.

    Question for next pass: should W5 outcomes use a separate W5 analytic frame
    (with GSW5 weights and W4->W5 attrition adjustment) instead of attaching
    W5 outcome columns to the W4 frame? The current scaffold attaches W5
    columns to W4 for simplicity, applying GSW5 only on the WLS call. This is
    the same simplification multi-outcome-screening makes; revisit alongside
    the planned IPAW-W5 work in TODO §A3.
    """
    W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
    # Attach GSW5 from the W5 weight file (.xpt). Wave-V weights live outside
    # the cached parquets; load_w5_weight pulls them via pyreadstat.
    try:
        from analysis.data_loading import load_w5_weight  # local import: avoid pyreadstat at module load
        w5w = load_w5_weight()[["AID", "GSW5"]]
        W4 = W4.merge(w5w, on="AID", how="left")
    except Exception as exc:  # noqa: BLE001 - graceful fall-back
        print(f"WARN: GSW5 not loaded ({exc}); W5 fits will fall back to GSWGT4_2.")
        W4["GSW5"] = np.nan
    for code in SUBSTANCE_OUTCOMES:
        if code in LEGIT_SKIP_TO_ZERO_OUTCOMES:
            # Hand-roll the load so we can impute 97 -> 0 BEFORE clean_var's
            # (0, 6) gate strips it. Mirrors load_outcome otherwise.
            wave = SUBSTANCE_OUTCOMES[code][1]
            src_path = CACHE / ("w4inhome.parquet" if wave == "W4" else "pwave5.parquet")
            src = pd.read_parquet(src_path, columns=["AID", code])
            raw = pd.to_numeric(src[code], errors="coerce")
            raw = raw.where(raw != 97, 0.0)  # legit skip => 0 frequency
            src[code] = clean_var(raw, code)
            m = pd.DataFrame({"AID": W4["AID"].values}).merge(src, on="AID", how="left")
            W4[code] = pd.Series(m[code].values, index=W4.index, name=code)
        else:
            W4[code] = load_outcome(W4["AID"], code)
    return W4


# ---------------------------------------------------------------------------
# Fit primitives
# ---------------------------------------------------------------------------
def _fit(df: pd.DataFrame, exposure_col: str, y_col: str,
         adj_builder: Callable[[pd.DataFrame], pd.DataFrame],
         w_col: str = "GSWGT4_2") -> Optional[dict]:
    exp = clean_var(df[exposure_col], exposure_col)
    adj = adj_builder(df)
    X = pd.concat([exp.rename("exposure"), adj], axis=1)
    X.insert(0, "const", 1.0)
    y = df[y_col].values
    w = df[w_col].values
    psu = df["CLUSTER2"].values
    return weighted_ols(y, X.values, w, psu, column_names=list(X.columns))


# ---------------------------------------------------------------------------
# Primary matrix: D1 + D4-style adjustment-set stability.
# ---------------------------------------------------------------------------
def run_primary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome_code, (label, wave, kind, w_col) in SUBSTANCE_OUTCOMES.items():
        # Fall back to GSWGT4_2 if GSW5 wasn't loaded.
        weight_col = w_col if w_col in df.columns and df[w_col].notna().any() else "GSWGT4_2"
        betas: Dict[str, dict] = {}
        for adj_name, builder in ADJ_BUILDERS.items():
            res = _fit(df, EXPOSURE_COL, outcome_code, builder, w_col=weight_col)
            if res is None:
                betas[adj_name] = {"beta": np.nan, "se": np.nan, "p": np.nan, "n": 0}
            else:
                betas[adj_name] = {
                    "beta": float(res["beta"]["exposure"]),
                    "se":   float(res["se"]["exposure"]),
                    "p":    float(res["p"]["exposure"]),
                    "n":    int(res["n"]),
                }
        primary = betas["L0+L1+AHPVT"]
        b0, b1, bf = betas["L0"]["beta"], betas["L0+L1"]["beta"], betas["L0+L1+AHPVT"]["beta"]
        if not (np.isnan(b0) or np.isnan(b1)):
            ref = abs(b1) if abs(b1) > 1e-10 else abs(b0)
            d4a_rel_shift = abs(b0 - b1) / ref if ref > 0 else np.nan
            d4a_sign_stable = (np.sign(b0) == np.sign(b1)) and (b0 != 0) and (b1 != 0)
        else:
            d4a_rel_shift = np.nan
            d4a_sign_stable = False
        rows.append({
            "exposure": EXPOSURE_COL,
            "outcome": outcome_code,
            "outcome_label": label,
            "wave": wave,
            "kind": kind,
            "weight_col_used": weight_col,
            "n": primary["n"],
            "beta": primary["beta"],
            "se": primary["se"],
            "p": primary["p"],
            "d1_pass": primary["p"] < 0.05 if not np.isnan(primary["p"]) else False,
            "beta_predicted_sign": "+",  # dark-side hypothesis
            "beta_sign_matches_prediction": (primary["beta"] > 0) if not np.isnan(primary["beta"]) else False,
            "beta_L0": b0,
            "beta_L0_L1": b1,
            "beta_L0_L1_AHPVT": bf,
            "d4a_rel_shift": d4a_rel_shift,
            "d4a_sign_stable": bool(d4a_sign_stable),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity (a) — quintile dose-response.
# ---------------------------------------------------------------------------
def run_quintile(df: pd.DataFrame) -> pd.DataFrame:
    """Q1-vs-Q2..Q5 means via WLS on quintile dummies + L0+L1+AHPVT."""
    rows = []
    exp_clean = clean_var(df[EXPOSURE_COL], EXPOSURE_COL)
    dummies, _q = quintile_dummies(exp_clean, n=5)
    for outcome_code, (label, wave, kind, w_col) in SUBSTANCE_OUTCOMES.items():
        weight_col = w_col if w_col in df.columns and df[w_col].notna().any() else "GSWGT4_2"
        adj = _adj_full(df)
        X = pd.concat([dummies, adj], axis=1)
        X.insert(0, "const", 1.0)
        y = df[outcome_code].values
        w = df[weight_col].values
        psu = df["CLUSTER2"].values
        res = weighted_ols(y, X.values, w, psu, column_names=list(X.columns))
        if res is None:
            continue
        for qcol in dummies.columns:
            rows.append({
                "outcome": outcome_code,
                "outcome_label": label,
                "wave": wave,
                "quintile": qcol,
                "beta_vs_q1": float(res["beta"][qcol]),
                "se": float(res["se"][qcol]),
                "p": float(res["p"][qcol]),
                "ci_lo": float(res["ci_lo"][qcol]),
                "ci_hi": float(res["ci_hi"][qcol]),
                "n_total": int(res["n"]),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity (b) — E-value bounds.
# ---------------------------------------------------------------------------
def run_evalues(matrix: pd.DataFrame) -> pd.DataFrame:
    """Compute VanderWeele-Ding E-values per significant outcome.

    Uses an approximate continuous-outcome -> RR conversion (Chinn 2000):
    RR ~= exp(0.91 * d), where d = beta / sd_y. We do not have sd_y in the
    primary matrix; for the skeleton we bound the E-value using the absolute
    value of standardized beta (z = beta / se, on a per-fit basis). This is
    a placeholder — the next pass should use proper standardized effect sizes
    per outcome, and for binary outcomes use the raw odds ratio. See
    `scripts/analysis/sensitivity.py:evalue` for the formula.
    """
    rows = []
    for _, r in matrix.iterrows():
        if not r["d1_pass"] or np.isnan(r["beta"]) or np.isnan(r["se"]) or r["se"] <= 0:
            continue
        # Skeleton-level approximation; replace with proper sd-of-y rescaling.
        d = abs(r["beta"]) / max(r["se"] * math.sqrt(max(r["n"], 1)), 1e-9)
        rr_approx = math.exp(max(0.91 * d, 1e-9))
        try:
            ev = evalue(rr_approx)
        except ValueError:
            ev = np.nan
        rows.append({
            "outcome": r["outcome"],
            "outcome_label": r["outcome_label"],
            "beta": r["beta"],
            "se": r["se"],
            "n": r["n"],
            "approx_rr": rr_approx,
            "evalue": ev,
            "interpretation": "An unmeasured confounder must have at least this RR with both exposure and outcome to explain away the observed association.",
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Markdown narrative
# ---------------------------------------------------------------------------
def _sd_col(df: pd.DataFrame, col: str) -> float:
    if col not in df.columns:
        return float("nan")
    vals = clean_var(df[col], col).dropna()
    return float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")


def run_sensitivity_extended(df: pd.DataFrame, matrix: pd.DataFrame) -> dict:
    """Cornfield grid + η-tilt + Chinn-2000 E-values for the IDGX2 → substance
    cells. Continuous-A note: IDGX2 is binarised via top-vs-bottom-quintile
    for the η-tilt sweep, which doubles as the operational definition of
    "popular vs unpopular" used elsewhere in the project.
    """
    sd_idgx2 = _sd_col(df, "IDGX2")
    pri = matrix.copy()
    pri["sd_x"] = sd_idgx2
    pri["sd_y"] = pri["outcome"].map(lambda c: _sd_col(df, c))
    pri["label"] = pri["exposure"] + " -> " + pri["outcome"]

    ev_full = build_evalue_table(
        pri, beta_col="beta", sd_x_col="sd_x", sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "wave", "kind", "label"),
    )
    cf = build_cornfield_grid(
        pri, sd_x_col="sd_x", sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "wave", "kind", "label"),
    )
    sig = pri.dropna(subset=["p"]).sort_values("p")
    target = sig[sig["p"] < 0.05].head(2)
    if target.empty:
        target = sig.head(2)
    cells = []
    for _, r in target.iterrows():
        # weight column varies by wave; substance frame embeds it as
        # weight_col_used per-row.
        w_col = r.get("weight_col_used", "GSWGT4_2")
        cell = build_eta_cell_from_quintile_contrast(
            label=r["label"],
            df=df,
            exposure_col=r["exposure"],
            outcome_col=r["outcome"],
            weight_col=w_col,
            cluster_col="CLUSTER2",
            adj_builder=_adj_full,
            extra_keys={"exposure": r["exposure"], "outcome": r["outcome"]},
        )
        if cell is not None:
            cells.append(cell)
    eta_tbl = build_eta_tilt_table(cells)
    return {"evalue_full": ev_full, "cornfield": cf, "eta_tilt": eta_tbl}


def write_markdown(matrix: pd.DataFrame) -> None:
    lines = ["# popularity-and-substance-use — primary results\n"]
    lines.append(
        "WLS fits of `IDGX2` against the 8 substance-use outcomes locked in "
        "the 2026-04-26 pre-flight inventory. Primary spec L0+L1+AHPVT, "
        "cluster-SE on `CLUSTER2`. The dark-side hypothesis predicts β > 0 "
        "for every outcome, inverting the cardiometabolic protective signal.\n"
    )
    lines.append("## Per-outcome primary β\n")
    show = matrix[[
        "outcome", "outcome_label", "wave", "n", "beta", "se", "p",
        "d1_pass", "beta_sign_matches_prediction",
    ]].copy()
    show["beta"] = show["beta"].map(lambda v: f"{v:.4g}" if pd.notna(v) else "NA")
    show["se"] = show["se"].map(lambda v: f"{v:.4g}" if pd.notna(v) else "NA")
    show["p"] = show["p"].map(lambda v: f"{v:.3g}" if pd.notna(v) else "NA")
    lines.append(show.to_markdown(index=False))
    lines.append("")
    n_pos = int(matrix["beta_sign_matches_prediction"].sum())
    n_sig = int(matrix["d1_pass"].sum())
    lines.append(
        f"\nTBD interpretation: {n_pos} / {len(matrix)} outcomes show β > 0 "
        f"(matches dark-side prediction); {n_sig} reach p < 0.05.\n"
    )
    (TABLES_PRIMARY / "popularity_subst.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("Running popularity-and-substance-use ...")
    df = _load_frame()
    matrix = run_primary(df)
    matrix.to_csv(TABLES_PRIMARY / "popularity_subst_matrix.csv", index=False)
    print(f"Wrote {TABLES_PRIMARY / 'popularity_subst_matrix.csv'} ({len(matrix)} rows)")

    quintile = run_quintile(df)
    quintile.to_csv(TABLES_SENS / "popularity_subst_quintiles.csv", index=False)
    print(f"Wrote {TABLES_SENS / 'popularity_subst_quintiles.csv'} ({len(quintile)} rows)")

    evals = run_evalues(matrix)
    evals.to_csv(TABLES_SENS / "popularity_subst_evalues.csv", index=False)
    print(f"Wrote {TABLES_SENS / 'popularity_subst_evalues.csv'} ({len(evals)} rows)")

    print("Sensitivity: extended (Cornfield grid + η-tilt + Chinn-2000 E-values) ...")
    ext = run_sensitivity_extended(df, matrix)
    ext["evalue_full"].to_csv(
        TABLES_SENS / "popularity_subst_evalue_chinn2000.csv", index=False)
    ext["cornfield"].to_csv(
        TABLES_SENS / "popularity_subst_cornfield_grid.csv", index=False)
    ext["eta_tilt"].to_csv(
        TABLES_SENS / "popularity_subst_eta_tilt.csv", index=False)

    write_markdown(matrix)
    print(f"Wrote {TABLES_PRIMARY / 'popularity_subst.md'}")


if __name__ == "__main__":
    main()

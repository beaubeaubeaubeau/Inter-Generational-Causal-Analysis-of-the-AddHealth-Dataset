"""EXP-EGODEN — ego-network-density at constant size.

Tests Burt's structural-holes hypothesis: high ego-network density predicts
mental-health protection (close-tie support); low density (brokerage)
predicts SES advantage (information diffusion). The load-bearing
methodological move is **conditioning on `REACH3` (egonet size)** so β
estimates "density at constant network size."

Design points (see ``dag.md``):
  - Four density exposures (`RCHDEN`, `ESDEN`, `ERDEN`, `ESRDEN`) fit in
    SEPARATE regressions per outcome (collinear by construction; joint fit
    is uninterpretable).
  - 6 outcomes: mental health (`H5MN1`, `H5MN2`, `H5ID16`), SES (`H5LM5`,
    `H5EC1`), cognitive (`W4_COG_COMP`).
  - Per-outcome adjustment set + `REACH3` always.
  - Sensitivity: quintile dose-response per density exposure; E-value per
    significant β; no-`REACH3` parallel to make the size-confound visible.

Outputs (relative to this experiment folder):
  tables/primary/egoden_primary.csv             (24 rows = 4 × 6)
  tables/primary/egoden_primary.md
  tables/sensitivity/egoden_quintile.csv
  tables/sensitivity/egoden_evalue.csv
  tables/sensitivity/egoden_no_reach3.csv

Run as:
    python experiments/ego-network-density/run.py
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

EXPOSURES: Dict[str, str] = {
    "RCHDEN":  "reach-density",
    "ESDEN":   "ego-send density",
    "ERDEN":   "ego-receive density",
    "ESRDEN":  "ego send-or-receive density",
}

OUTCOMES: Dict[str, Tuple[str, str]] = {
    "W4_COG_COMP": ("W4 cognitive composite", "cognitive"),
    "H5MN1":  ("S13Q1 LAST MO NO CNTRL IMPORT THINGS—W5", "mental_health"),
    "H5MN2":  ("S13Q2 LAST MO CONFID HANDLE PERS PBMS—W5", "mental_health"),
    "H5ID16": ("S5Q16 HOW OFTEN TROUBLE SLEEPING—W5", "functional"),
    "H5LM5":  ("S3Q5 CURRENTLY WORK—W5", "ses"),
    "H5EC1":  ("S4Q1 INCOME PERS EARNINGS [W4–W5]—W5", "ses"),
}

# Per-outcome adjustment-set tier (pre-REACH3). REACH3 is appended in the fit.
ADJ_TIER_BY_OUTCOME: Dict[str, str] = {
    "W4_COG_COMP": "L0+L1+AHPVT",
    "H5MN1":  "L0+L1",
    "H5MN2":  "L0+L1",
    "H5ID16": "L0+L1",
    "H5LM5":  "L0+L1",  # DAG-SES drops AHPVT
    "H5EC1":  "L0+L1",
}

RACE_LEVELS = ["NH-Black", "Hispanic", "Other"]


# ---------------------------------------------------------------------------
# Adjustment-set builders (REACH3 added separately at fit time)
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
    "L0":         _adj_L0,
    "L0+L1":      _adj_L0_L1,
    "L0+L1+AHPVT": _adj_L0_L1_AHPVT,
}


# ---------------------------------------------------------------------------
# Frame loading
# ---------------------------------------------------------------------------
def _load_frame() -> pd.DataFrame:
    W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
    for code in OUTCOMES:
        if code == "W4_COG_COMP":
            continue
        W4[code] = load_outcome(W4["AID"], code)
    return W4


# ---------------------------------------------------------------------------
# Single-cell fit (always conditions on REACH3 unless `with_reach3=False`)
# ---------------------------------------------------------------------------
def _fit_cell(df: pd.DataFrame, exposure_col: str, outcome_col: str,
              adj_builder: Callable[[pd.DataFrame], pd.DataFrame],
              with_reach3: bool = True,
              w_col: str = "GSWGT4_2") -> Optional[dict]:
    exp = clean_var(df[exposure_col], exposure_col)
    adj = adj_builder(df)
    parts = [exp.rename("exposure"), adj]
    if with_reach3:
        parts.append(clean_var(df["REACH3"], "REACH3").rename("reach3"))
    X = pd.concat(parts, axis=1)
    X.insert(0, "const", 1.0)
    y = df[outcome_col].values
    w = df[w_col].values
    psu = df["CLUSTER2"].values
    return weighted_ols(y, X.values, w, psu, column_names=list(X.columns))


# ---------------------------------------------------------------------------
# Primary block — 4 × 6, with REACH3 always in the adjustment set
# ---------------------------------------------------------------------------
def run_primary(W4: pd.DataFrame, with_reach3: bool = True) -> pd.DataFrame:
    rows = []
    for exp_name in EXPOSURES:
        for outcome_code, (label, o_group) in OUTCOMES.items():
            tier = ADJ_TIER_BY_OUTCOME[outcome_code]
            res = _fit_cell(W4, exp_name, outcome_code, ADJ_BUILDERS[tier],
                            with_reach3=with_reach3)
            row = {
                "exposure": exp_name, "outcome": outcome_code,
                "outcome_label": label, "outcome_group": o_group,
                "adj_tier": tier, "with_reach3": with_reach3,
            }
            if res is None:
                row.update({
                    "n": 0, "beta": np.nan, "se": np.nan, "p": np.nan,
                    "ci_lo": np.nan, "ci_hi": np.nan, "sig": False,
                    "beta_reach3": np.nan, "p_reach3": np.nan,
                })
            else:
                row.update({
                    "n": int(res["n"]),
                    "beta": float(res["beta"]["exposure"]),
                    "se": float(res["se"]["exposure"]),
                    "p": float(res["p"]["exposure"]),
                    "ci_lo": float(res["ci_lo"]["exposure"]),
                    "ci_hi": float(res["ci_hi"]["exposure"]),
                    "sig": bool(float(res["p"]["exposure"]) < 0.05),
                    "beta_reach3": (
                        float(res["beta"]["reach3"])
                        if with_reach3 and "reach3" in res["beta"] else np.nan
                    ),
                    "p_reach3": (
                        float(res["p"]["reach3"])
                        if with_reach3 and "reach3" in res["p"] else np.nan
                    ),
                })
            rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity 1 — quintile dose-response per density exposure
# ---------------------------------------------------------------------------
def run_sensitivity_quintile(W4: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for exp_name in EXPOSURES:
        for outcome_code, (label, o_group) in OUTCOMES.items():
            tier = ADJ_TIER_BY_OUTCOME[outcome_code]
            adj = ADJ_BUILDERS[tier](W4)
            reach3 = clean_var(W4["REACH3"], "REACH3").rename("reach3")
            exp_clean = clean_var(W4[exp_name], exp_name)
            dummies, trend = quintile_dummies(exp_clean, n=5)

            X = pd.concat([dummies, adj, reach3], axis=1)
            X.insert(0, "const", 1.0)
            res_d = weighted_ols(
                W4[outcome_code].values, X.values,
                W4["GSWGT4_2"].values, W4["CLUSTER2"].values,
                column_names=list(X.columns),
            )
            X_t = pd.concat([trend.rename("quintile_trend"), adj, reach3], axis=1)
            X_t.insert(0, "const", 1.0)
            res_t = weighted_ols(
                W4[outcome_code].values, X_t.values,
                W4["GSWGT4_2"].values, W4["CLUSTER2"].values,
                column_names=list(X_t.columns),
            )
            row = {
                "exposure": exp_name, "outcome": outcome_code,
                "outcome_label": label, "outcome_group": o_group,
                "adj_tier": tier,
            }
            if res_d is not None:
                for q in ["q2", "q3", "q4", "q5"]:
                    row[f"beta_{q}_vs_q1"] = float(res_d["beta"].get(q, np.nan))
                    row[f"p_{q}_vs_q1"] = float(res_d["p"].get(q, np.nan))
            if res_t is not None:
                row["beta_trend"] = float(res_t["beta"]["quintile_trend"])
                row["se_trend"] = float(res_t["se"]["quintile_trend"])
                row["p_trend"] = float(res_t["p"]["quintile_trend"])
            rows.append(row)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity 2 — E-values per significant β
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
# Sensitivity 3 — no-REACH3 parallel (size-confound visibility)
# ---------------------------------------------------------------------------
def run_sensitivity_no_reach3(W4: pd.DataFrame) -> pd.DataFrame:
    """Refit primary spec WITHOUT `REACH3` in the adjustment set; pair with the
    primary β to make the size-confound bias quantitatively visible."""
    return run_primary(W4, with_reach3=False)


# ---------------------------------------------------------------------------
# Sensitivity 4 — Cornfield bias-factor grid + η-tilt sweep + Chinn-2000 E-value
# ---------------------------------------------------------------------------
def _outcome_sd(W4: pd.DataFrame, code: str) -> float:
    if code not in W4.columns:
        return float("nan")
    vals = pd.to_numeric(W4[code], errors="coerce").dropna()
    return float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")


def _exposure_sd(W4: pd.DataFrame, exp_col: str) -> float:
    if exp_col not in W4.columns:
        return float("nan")
    vals = clean_var(W4[exp_col], exp_col).dropna()
    return float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")


def run_sensitivity_extended(W4: pd.DataFrame, primary: pd.DataFrame) -> dict:
    """Cornfield bias-factor grid + η-tilt sweep + Chinn-2000 E-values.

    Continuous-A note: all four density exposures are continuous; the η-tilt
    sweep uses a top-quintile-vs-bottom-quintile binarisation. The two
    most-significant primary cells (smallest p) are sent through the η-tilt
    cell-builder; remaining cells appear on the E-value bar chart and the
    Cornfield grid only.
    """
    primary = primary.copy()
    primary["sd_x"] = primary["exposure"].map(lambda c: _exposure_sd(W4, c))
    primary["sd_y"] = primary["outcome"].map(lambda c: _outcome_sd(W4, c))
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
        # Custom adjustment-set builder: tier-specific covariates + REACH3
        # (the size-conditioning that the structural-holes estimand requires).
        base_builder = ADJ_BUILDERS[r["adj_tier"]]
        def adj_builder_with_reach3(df, _b=base_builder):
            base = _b(df)
            r3 = clean_var(df["REACH3"], "REACH3").rename("reach3")
            return pd.concat([base, r3], axis=1)
        cell = build_eta_cell_from_quintile_contrast(
            label=r["label"],
            df=W4,
            exposure_col=r["exposure"],
            outcome_col=r["outcome"],
            weight_col="GSWGT4_2",
            cluster_col="CLUSTER2",
            adj_builder=adj_builder_with_reach3,
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
    lines = ["# EXP-EGODEN — ego-network density at constant size\n"]
    lines.append(
        "Per-outcome WLS β for the four ego-network density measures, fit in "
        "**separate** regressions with cluster-robust SE on `CLUSTER2`. "
        "**`REACH3` (egonet size) is in every adjustment set** — without this "
        "conditioning, β̂ confounds 'density effect' with 'smaller-network "
        "effect.' See [dag.md](../../dag.md) for the structural-holes-theoretic "
        "estimand.\n"
    )
    show = primary.copy()
    for c in ("beta", "se", "ci_lo", "ci_hi", "beta_reach3"):
        show[c] = show[c].map(lambda v: f"{v:.4g}" if pd.notna(v) else "NA")
    show["p"] = show["p"].map(lambda v: f"{v:.3g}" if pd.notna(v) else "NA")
    show["p_reach3"] = show["p_reach3"].map(
        lambda v: f"{v:.3g}" if pd.notna(v) else "NA")
    lines.append(show[["exposure", "outcome", "outcome_group", "n", "beta",
                       "se", "ci_lo", "ci_hi", "p", "sig",
                       "beta_reach3", "p_reach3"]].to_markdown(index=False))
    (TABLES_PRIMARY / "egoden_primary.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def run_egoden() -> pd.DataFrame:
    print("Loading W4 + W5 outcomes ...")
    W4 = _load_frame()
    print("Running primary 4x6 grid (with REACH3) ...")
    primary = run_primary(W4, with_reach3=True)
    primary.to_csv(TABLES_PRIMARY / "egoden_primary.csv", index=False)
    write_primary_markdown(primary)

    print("Sensitivity: quintile dose-response per density measure ...")
    quint = run_sensitivity_quintile(W4)
    quint.to_csv(TABLES_SENS / "egoden_quintile.csv", index=False)
    print("Sensitivity: E-values per significant β ...")
    ev = run_sensitivity_evalue(primary)
    ev.to_csv(TABLES_SENS / "egoden_evalue.csv", index=False)
    print("Sensitivity: no-REACH3 parallel (size-confound visibility) ...")
    no_r = run_sensitivity_no_reach3(W4)
    no_r.to_csv(TABLES_SENS / "egoden_no_reach3.csv", index=False)

    print("Sensitivity: extended (Cornfield grid + η-tilt + Chinn-2000 E-values) ...")
    ext = run_sensitivity_extended(W4, primary)
    ext["evalue_full"].to_csv(
        TABLES_SENS / "egoden_evalue_chinn2000.csv", index=False)
    ext["cornfield"].to_csv(
        TABLES_SENS / "egoden_cornfield_grid.csv", index=False)
    ext["eta_tilt"].to_csv(
        TABLES_SENS / "egoden_eta_tilt.csv", index=False)
    return primary


def main() -> None:
    run_egoden()


if __name__ == "__main__":
    main()

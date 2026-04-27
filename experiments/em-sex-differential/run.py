"""EM-Sex-Differential -- `IDGX2 x BIO_SEX` effect modification.

Tests whether the marginal effect of W1 in-degree (`IDGX2`) on adult
cardiometabolic + mental-health outcomes differs by biological sex. The
substantive hypothesis is that peer status policing of body weight is
stronger for girls (sex-asymmetric).

Pipeline (this scaffold; `main()` exists but doesn't auto-run anything
that requires the parquet cache):

  1. WLS interaction model per outcome:
        Y ~ const + IDGX2 + male + IDGX2:male + adjust + ...
     fit via `analysis.wls.weighted_ols`, cluster-robust on `CLUSTER2`.
  2. Sex-stratified quintile dose-response (sensitivity).
  3. Sex-stratified bias-corrected matching: top-quintile-`IDGX2` vs
     bottom-quintile-`IDGX2` separately for boys and for girls. Calls
     `analysis.matching.match_ate_bias_corrected`.
  4. E-value on the interaction coefficient via `analysis.sensitivity.evalue`.

Outputs (relative to this experiment folder):
  tables/primary/em_sex_interaction.csv
  tables/primary/em_sex_stratified_betas.csv
  tables/sensitivity/em_sex_quintile_by_sex.csv
  tables/sensitivity/em_sex_evalue.csv
  tables/handoff/em_sex_matching_by_sex.csv
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analysis import CACHE  # noqa: E402
from analysis.cleaning import clean_var  # noqa: E402
from analysis.wls import weighted_ols, quintile_dummies  # noqa: E402
from analysis.data_loading import load_outcome, load_w5_weight  # noqa: E402
from analysis.matching import match_ate_bias_corrected  # noqa: E402
from analysis.sensitivity import evalue  # noqa: E402
from analysis.sensitivity_panel import (  # noqa: E402
    build_cornfield_grid,
    build_eta_cell_from_quintile_contrast,
    build_eta_tilt_table,
    build_evalue_table,
)

TABLES_PRIMARY = HERE / "tables" / "primary"
TABLES_SENS = HERE / "tables" / "sensitivity"
TABLES_HANDOFF = HERE / "tables" / "handoff"
for _d in (TABLES_PRIMARY, TABLES_SENS, TABLES_HANDOFF):
    _d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Outcome battery
# ---------------------------------------------------------------------------
# name: (label, group, kind, weight_col)
OUTCOMES: Dict[str, Tuple[str, str, str, str]] = {
    "H4BMI":    ("S27 BMI -- W4",                       "cardiometabolic", "continuous",   "GSWGT4_2"),
    "H4WAIST":  ("S27 MEASURED WAIST (CM) -- W4",       "cardiometabolic", "continuous",   "GSWGT4_2"),
    "H4BMICLS": ("S27 BMI CLASS -- W4",                 "cardiometabolic", "ordinal-1-6",  "GSWGT4_2"),
    "H5MN1":    ("S13Q1 LAST MO NO CNTRL IMPORT THINGS -- W5", "mental_health", "likert-1-5", "GSW5"),
    "H5MN2":    ("S13Q2 LAST MO CONFID HANDLE PERS PBMS -- W5","mental_health", "likert-1-5", "GSW5"),
}


# ---------------------------------------------------------------------------
# Adjustment-set builder (placeholder L0+L1+AHPVT until per-outcome DAGs locked)
# ---------------------------------------------------------------------------
RACE_LEVELS = ["NH-Black", "Hispanic", "Other"]


def _race_dummies(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for lvl in RACE_LEVELS:
        out[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    out.loc[df["RACE"].isna(), :] = np.nan
    return out


def _adj_full(df: pd.DataFrame) -> pd.DataFrame:
    """Placeholder adjustment set (L0 + L1 + AHPVT). Note: `male` is INCLUDED
    here -- the interaction term `IDGX2:male` is added on top of the main
    `male` term that lives in the adjustment set."""
    return pd.concat([
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index),
        _race_dummies(df),
        df["PARENT_ED"].rename("parent_ed"),
        df["CESD_SUM"].rename("cesd_sum"),
        df["H1GH1"].rename("srh"),
        df["AH_RAW"].rename("ahpvt"),
    ], axis=1)


# ---------------------------------------------------------------------------
# Frame loading
# ---------------------------------------------------------------------------
def _load_frame() -> pd.DataFrame:
    """W4 analytic frame with all listed outcomes attached.

    Merges the W5 cross-sectional weight `GSW5` from the raw W5 weight file
    so that W5-target outcomes (`H5MN1`, `H5MN2`) can be weighted with their
    own design weight rather than `GSWGT4_2`. Respondents not in W5 get
    `NaN` for `GSW5`; `weighted_ols` drops them via its row-mask.
    """
    W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
    if "GSW5" not in W4.columns:
        w5w = load_w5_weight()[["AID", "GSW5"]]
        W4 = W4.merge(w5w, on="AID", how="left")
    for code in OUTCOMES:
        W4[code] = load_outcome(W4["AID"], code)
    return W4


# ---------------------------------------------------------------------------
# Primary: WLS interaction fit
# ---------------------------------------------------------------------------
def fit_interaction(df: pd.DataFrame, outcome: str) -> Optional[dict]:
    """WLS of `outcome ~ const + IDGX2 + IDGX2:male + adj`."""
    _, _, _, w_col = OUTCOMES[outcome]
    exp = clean_var(df["IDGX2"], "IDGX2").rename("idgx2")
    male = (df["BIO_SEX"] == 1).astype(float)
    inter = (exp * male).rename("idgx2_x_male")
    adj = _adj_full(df)
    X = pd.concat([exp, inter, adj], axis=1)
    X.insert(0, "const", 1.0)
    return weighted_ols(
        df[outcome].values, X.values, df[w_col].values,
        df["CLUSTER2"].values, column_names=list(X.columns),
    )


def fit_stratified(df: pd.DataFrame, outcome: str, sex_male: bool) -> Optional[dict]:
    """Per-sex stratified fit of `outcome ~ const + IDGX2 + adj_minus_male`."""
    _, _, _, w_col = OUTCOMES[outcome]
    sub = df[(df["BIO_SEX"] == 1) == sex_male].copy()
    exp = clean_var(sub["IDGX2"], "IDGX2").rename("idgx2")
    adj = _adj_full(sub).drop(columns=["male"])  # constant within stratum
    X = pd.concat([exp, adj], axis=1)
    X.insert(0, "const", 1.0)
    return weighted_ols(
        sub[outcome].values, X.values, sub[w_col].values,
        sub["CLUSTER2"].values, column_names=list(X.columns),
    )


def run_primary(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (interaction_df, stratified_df) -- the two primary CSVs."""
    inter_rows = []
    strat_rows = []
    for outcome, (label, group, kind, w_col) in OUTCOMES.items():
        res = fit_interaction(df, outcome)
        if res is None:
            inter_rows.append({"outcome": outcome, "outcome_label": label,
                               "outcome_group": group, "n": 0, "beta_inter": np.nan})
        else:
            inter_rows.append({
                "outcome": outcome,
                "outcome_label": label,
                "outcome_group": group,
                "n": int(res["n"]),
                "beta_idgx2": float(res["beta"]["idgx2"]),
                "se_idgx2":   float(res["se"]["idgx2"]),
                "beta_inter": float(res["beta"]["idgx2_x_male"]),
                "se_inter":   float(res["se"]["idgx2_x_male"]),
                "p_inter":    float(res["p"]["idgx2_x_male"]),
                "ci_lo_inter": float(res["ci_lo"]["idgx2_x_male"]),
                "ci_hi_inter": float(res["ci_hi"]["idgx2_x_male"]),
            })
        for sex_male, label_s in [(False, "female"), (True, "male")]:
            res_s = fit_stratified(df, outcome, sex_male)
            if res_s is None:
                strat_rows.append({"outcome": outcome, "stratum": label_s,
                                   "n": 0, "beta_idgx2": np.nan})
                continue
            strat_rows.append({
                "outcome": outcome,
                "stratum": label_s,
                "n": int(res_s["n"]),
                "beta_idgx2": float(res_s["beta"]["idgx2"]),
                "se_idgx2":   float(res_s["se"]["idgx2"]),
                "p_idgx2":    float(res_s["p"]["idgx2"]),
                "ci_lo":      float(res_s["ci_lo"]["idgx2"]),
                "ci_hi":      float(res_s["ci_hi"]["idgx2"]),
            })
    return pd.DataFrame(inter_rows), pd.DataFrame(strat_rows)


# ---------------------------------------------------------------------------
# Sensitivity: quintile dose-response by sex
# ---------------------------------------------------------------------------
def quintile_by_sex(df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    _, _, _, w_col = OUTCOMES[outcome]
    rows = []
    for sex_male, label_s in [(False, "female"), (True, "male")]:
        sub = df[(df["BIO_SEX"] == 1) == sex_male].copy()
        if len(sub) < 50:
            continue
        _, qtrend = quintile_dummies(clean_var(sub["IDGX2"], "IDGX2"), n=5)
        adj = _adj_full(sub).drop(columns=["male"])
        X = pd.concat([qtrend.rename("idgx2_qtrend"), adj], axis=1)
        X.insert(0, "const", 1.0)
        res = weighted_ols(
            sub[outcome].values, X.values, sub[w_col].values,
            sub["CLUSTER2"].values, column_names=list(X.columns),
        )
        if res is None:
            continue
        rows.append({
            "outcome": outcome,
            "stratum": label_s,
            "n": int(res["n"]),
            "beta_qtrend": float(res["beta"]["idgx2_qtrend"]),
            "se_qtrend":   float(res["se"]["idgx2_qtrend"]),
            "p_qtrend":    float(res["p"]["idgx2_qtrend"]),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity: E-value on interaction coefficient
# ---------------------------------------------------------------------------
def evalue_on_interaction(primary: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, r in primary.iterrows():
        if pd.isna(r["beta_inter"]):
            rows.append({"outcome": r["outcome"], "rr_proxy": np.nan, "evalue": np.nan})
            continue
        rr = float(np.exp(abs(r["beta_inter"])))
        rows.append({
            "outcome": r["outcome"],
            "beta_inter": float(r["beta_inter"]),
            "rr_proxy": rr,
            "evalue": evalue(rr),
        })
    return pd.DataFrame(rows)


def _sd_col(df: pd.DataFrame, col: str) -> float:
    if col not in df.columns:
        return float("nan")
    vals = clean_var(df[col], col).dropna()
    return float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")


def run_sensitivity_extended(W4: pd.DataFrame, primary: pd.DataFrame) -> dict:
    """Cornfield grid + η-tilt + Chinn-2000 E-values for the IDGX2×BIO_SEX
    interaction. The interaction is the load-bearing estimand; η-tilt sweep
    binarises IDGX2 via top-vs-bottom-quintile WITHIN the female stratum
    (where the protective slope is steepest per primary).
    """
    sd_idgx2 = _sd_col(W4, "IDGX2")
    sd_sex = _sd_col(W4.assign(_male=(W4["BIO_SEX"] == 1).astype(float)), "_male")
    sd_inter = sd_idgx2 * sd_sex if (
        np.isfinite(sd_idgx2) and np.isfinite(sd_sex)
    ) else float("nan")

    pri = primary.copy()
    pri["sd_x"] = sd_inter
    pri["sd_y"] = pri["outcome"].map(lambda c: _sd_col(W4, c))
    pri["beta"] = pri["beta_inter"]
    pri["p"] = pri["p_inter"]
    pri["label"] = "IDGX2 x male -> " + pri["outcome"]
    pri["exposure"] = "IDGX2 x male"

    ev_full = build_evalue_table(
        pri, beta_col="beta", sd_x_col="sd_x", sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label"),
    )
    cf = build_cornfield_grid(
        pri, sd_x_col="sd_x", sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label"),
    )
    sig = pri.dropna(subset=["p"]).sort_values("p")
    target = sig[sig["p"] < 0.05].head(2)
    if target.empty:
        target = sig.head(2)
    cells = []
    female = W4.loc[W4["BIO_SEX"] == 2].copy()  # female stratum (steeper slope)
    for _, r in target.iterrows():
        _, _, _, w_col = OUTCOMES[r["outcome"]]
        cell = build_eta_cell_from_quintile_contrast(
            label=r["label"] + " [female]",
            df=female,
            exposure_col="IDGX2",
            outcome_col=r["outcome"],
            weight_col=w_col,
            cluster_col="CLUSTER2",
            adj_builder=_adj_full,
            extra_keys={
                "exposure": "IDGX2 (top-vs-bot quintile, female stratum)",
                "outcome": r["outcome"],
            },
        )
        if cell is not None:
            cells.append(cell)
    eta_tbl = build_eta_tilt_table(cells)
    return {"evalue_full": ev_full, "cornfield": cf, "eta_tilt": eta_tbl}


# ---------------------------------------------------------------------------
# Robustness: sex-stratified bias-corrected matching, top-vs-bottom IDGX2
# ---------------------------------------------------------------------------
def matching_by_sex(df: pd.DataFrame, outcome: str, sex_male: bool, M: int = 4):
    """Top-Q5 vs bottom-Q1 IDGX2 within one sex; match on covariates ex-sex."""
    sub = df[(df["BIO_SEX"] == 1) == sex_male].copy()
    _, qidg = quintile_dummies(clean_var(sub["IDGX2"], "IDGX2"), n=5)
    treated_mask = (qidg == 5)
    control_mask = (qidg == 1)
    keep = (treated_mask | control_mask) & sub[outcome].notna()
    sub = sub.loc[keep].copy()
    A = treated_mask.loc[sub.index].astype(int).to_numpy()
    Y = sub[outcome].astype(float).to_numpy()
    Xdf = pd.concat([
        _race_dummies(sub),
        sub["PARENT_ED"].rename("parent_ed"),
        sub["CESD_SUM"].rename("cesd_sum"),
        sub["H1GH1"].rename("srh"),
        sub["AH_RAW"].rename("ahpvt"),
    ], axis=1).dropna()
    Y = Y[Xdf.index.get_indexer_for(Xdf.index)]
    A = A[Xdf.index.get_indexer_for(Xdf.index)]
    if A.sum() < M or (1 - A).sum() < M:
        return None
    return match_ate_bias_corrected(Y, A, Xdf.to_numpy(), M=M)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def run_all() -> Dict[str, pd.DataFrame]:
    print("Loading frame ...")
    W4 = _load_frame()

    print("Primary: WLS interaction + sex-stratified fits ...")
    inter, strat = run_primary(W4)
    inter.to_csv(TABLES_PRIMARY / "em_sex_interaction.csv", index=False)
    strat.to_csv(TABLES_PRIMARY / "em_sex_stratified_betas.csv", index=False)

    print("Sensitivity: quintile dose-response by sex ...")
    qdr_rows = []
    for outcome in OUTCOMES:
        qdr_rows.append(quintile_by_sex(W4, outcome))
    qdr = pd.concat(qdr_rows, ignore_index=True)
    qdr.to_csv(TABLES_SENS / "em_sex_quintile_by_sex.csv", index=False)

    print("Sensitivity: E-value on interaction ...")
    ev = evalue_on_interaction(inter)
    ev.to_csv(TABLES_SENS / "em_sex_evalue.csv", index=False)

    print("Sensitivity: extended (Cornfield grid + η-tilt + Chinn-2000 E-values) ...")
    ext = run_sensitivity_extended(W4, inter)
    ext["evalue_full"].to_csv(
        TABLES_SENS / "em_sex_evalue_chinn2000.csv", index=False)
    ext["cornfield"].to_csv(
        TABLES_SENS / "em_sex_cornfield_grid.csv", index=False)
    ext["eta_tilt"].to_csv(
        TABLES_SENS / "em_sex_eta_tilt.csv", index=False)

    print("Robustness: sex-stratified matching ...")
    match_rows = []
    for outcome in OUTCOMES:
        for sex_male, label_s in [(False, "female"), (True, "male")]:
            res = matching_by_sex(W4, outcome, sex_male)
            if res is None:
                match_rows.append({"outcome": outcome, "stratum": label_s,
                                   "ate": np.nan, "se": np.nan,
                                   "n_treated": 0, "n_control": 0})
                continue
            match_rows.append({
                "outcome": outcome,
                "stratum": label_s,
                "ate": float(res["ate"]),
                "se":  float(res["se"]),
                "n_treated": int(res["n_treated"]),
                "n_control": int(res["n_control"]),
            })
    match_df = pd.DataFrame(match_rows)
    match_df.to_csv(TABLES_HANDOFF / "em_sex_matching_by_sex.csv", index=False)

    return {"interaction": inter, "stratified": strat,
            "qdr": qdr, "evalue": ev, "matching": match_df}


def main() -> None:
    run_all()


if __name__ == "__main__":
    main()

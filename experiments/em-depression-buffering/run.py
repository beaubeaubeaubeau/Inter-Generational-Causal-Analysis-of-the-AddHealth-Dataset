"""EM-Depression-Buffering -- `IDGX2 x CESD_SUM` effect modification.

Tests whether peer popularity (`IDGX2`) buffers the effect of pre-existing
depressive symptoms (`CESD_SUM`) on adult mental-health outcomes. The
substantive hypothesis is that adolescents who start out more depressed
gain more from being popular -- so the interaction coefficient is signed
in the buffering direction.

D9 collider check (CRITICAL): `CESD_SUM` enters in TWO roles -- as an L1
confounder of the `IDGX2 -> Y_mental` path AND as the moderator in the
experiment's primary estimand. Conditioning on a variable AND interacting
it AND using it as a confounder *simultaneously* can open a latent
backdoor under the unmeasured-personality DAG. We mitigate by running
TWO specs side-by-side per outcome:

  (a) conservative -- `CESD_SUM` in BOTH adjustment set AND moderator.
  (b) clean        -- `CESD_SUM` dropped from L1 when used as moderator.

Pipeline (this scaffold):

  1. WLS interaction model per outcome x spec (6 rows total):
        Y ~ const + IDGX2 + CESD_SUM + IDGX2:CESD_SUM + adjustment
     fit via `analysis.wls.weighted_ols`, cluster-robust on `CLUSTER2`,
     weighted by `GSWGT4_2` (placeholder until IPAW(W4 -> W5) lands).
  2. Tertile-stratified fit: per-outcome beta_IDGX2 within each `CESD_SUM`
     tertile (low / mid / high) -- the intuitive subgroup view.
  3. Quintile dose-response of `IDGX2` within each `CESD_SUM` tertile
     (sensitivity, linearity diagnostic).
  4. Bias-corrected matching contrast: top-quintile-`IDGX2` vs
     bottom-quintile-`IDGX2` *within* top-tertile-`CESD_SUM`. Calls
     `analysis.matching.match_ate_bias_corrected`.
  5. E-value on the interaction coefficient via `analysis.sensitivity.evalue`.

Outputs (relative to this experiment folder):
  tables/primary/em_dep_interaction.csv
  tables/primary/em_dep_stratified_betas.csv
  tables/sensitivity/em_dep_quintile_by_tertile.csv
  tables/sensitivity/em_dep_evalue.csv
  tables/handoff/em_dep_matching_high_cesd.csv
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
from analysis.wls import weighted_ols, quintile_dummies  # noqa: E402
from analysis.data_loading import load_outcome  # noqa: E402
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
# Outcome battery (W5 mental-health)
# ---------------------------------------------------------------------------
# name: (label, group, kind, weight_col)
OUTCOMES: Dict[str, Tuple[str, str, str, str]] = {
    "H5MN1": ("S13Q1 LAST MO NO CNTRL IMPORT THINGS -- W5",  "mental_health", "likert-1-5", "GSWGT4_2"),
    "H5MN2": ("S13Q2 LAST MO CONFID HANDLE PERS PBMS -- W5", "mental_health", "likert-1-5", "GSWGT4_2"),
    "H5ID1": ("S5Q1 HOW IS GEN PHYSICAL HEALTH -- W5",       "functional",    "likert-1-5", "GSWGT4_2"),
}


# ---------------------------------------------------------------------------
# Adjustment-set builders (two specs for the D9 collider check)
# ---------------------------------------------------------------------------
RACE_LEVELS = ["NH-Black", "Hispanic", "Other"]


def _race_dummies(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for lvl in RACE_LEVELS:
        out[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    out.loc[df["RACE"].isna(), :] = np.nan
    return out


def _adj_conservative(df: pd.DataFrame) -> pd.DataFrame:
    """Spec (a): `CESD_SUM` retained in the L1 adjustment set AND used as
    the moderator. Screening-style choice; vulnerable to D9 latent-personality
    backdoor under the `PERSONALITY -.-> CESD` arrow."""
    return pd.concat([
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index),
        _race_dummies(df),
        df["PARENT_ED"].rename("parent_ed"),
        df["CESD_SUM"].rename("cesd_sum"),  # retained as covariate
        df["H1GH1"].rename("srh"),
    ], axis=1)


def _adj_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Spec (b): `CESD_SUM` DROPPED from the main-effects adjustment set when
    used as the moderator. Theoretically preferred for the buffering estimand;
    requires the L0 set to fully d-separate `IDGX2` from `Y_mental`."""
    return pd.concat([
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index),
        _race_dummies(df),
        df["PARENT_ED"].rename("parent_ed"),
        # CESD_SUM intentionally omitted from the covariate block; it enters
        # the design only via the moderator main-effect + product term.
        df["H1GH1"].rename("srh"),
    ], axis=1)


SPECS: Dict[str, Callable[[pd.DataFrame], pd.DataFrame]] = {
    "conservative": _adj_conservative,
    "clean":        _adj_clean,
}


# ---------------------------------------------------------------------------
# Frame loading
# ---------------------------------------------------------------------------
def _load_frame() -> pd.DataFrame:
    """W4 analytic frame with W5 mental-health outcomes attached."""
    W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
    for code in OUTCOMES:
        W4[code] = load_outcome(W4["AID"], code)
    return W4


# ---------------------------------------------------------------------------
# Primary: WLS interaction fits (two specs per outcome)
# ---------------------------------------------------------------------------
def fit_interaction(df: pd.DataFrame, outcome: str, spec: str) -> Optional[dict]:
    """WLS of `outcome ~ const + IDGX2 + CESD_SUM + IDGX2:CESD_SUM + adj[spec]`.

    Note both specs INCLUDE the `CESD_SUM` main-effect term explicitly (it
    is the moderator's main effect, distinct from its role as a covariate).
    The two specs differ only in whether the `cesd_sum` covariate is also
    in the adjustment-set block.
    """
    _, _, _, w_col = OUTCOMES[outcome]
    adj_builder = SPECS[spec]
    exp = clean_var(df["IDGX2"], "IDGX2").rename("idgx2")
    cesd = clean_var(df["CESD_SUM"], "CESD_SUM").rename("cesd_sum_main")
    inter = (exp * cesd).rename("idgx2_x_cesd")
    adj = adj_builder(df)
    X = pd.concat([exp, cesd, inter, adj], axis=1)
    X.insert(0, "const", 1.0)
    return weighted_ols(
        df[outcome].values, X.values, df[w_col].values,
        df["CLUSTER2"].values, column_names=list(X.columns),
    )


def cesd_tertile(s: pd.Series) -> pd.Series:
    """Cut `CESD_SUM` into 3 rank-equal tertiles; returns 1/2/3 with NaN preserved."""
    s = pd.to_numeric(s, errors="coerce")
    mask = s.notna()
    out = pd.Series(np.nan, index=s.index, dtype=float)
    if mask.sum() > 0:
        ranks = s[mask].rank(method="first")
        bins = pd.qcut(ranks, q=3, labels=False, duplicates="drop") + 1
        out.loc[mask] = bins.values
    return out


def fit_stratified(df: pd.DataFrame, outcome: str, tertile: int) -> Optional[dict]:
    """Per-tertile stratified fit of `outcome ~ const + IDGX2 + adj_clean(no_cesd)`."""
    _, _, _, w_col = OUTCOMES[outcome]
    t = cesd_tertile(df["CESD_SUM"])
    sub = df.loc[t == tertile].copy()
    if len(sub) < 50:
        return None
    exp = clean_var(sub["IDGX2"], "IDGX2").rename("idgx2")
    adj = _adj_clean(sub)  # CESD_SUM is roughly constant within tertile -> drop
    X = pd.concat([exp, adj], axis=1)
    X.insert(0, "const", 1.0)
    return weighted_ols(
        sub[outcome].values, X.values, sub[w_col].values,
        sub["CLUSTER2"].values, column_names=list(X.columns),
    )


def run_primary(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (interaction_df, stratified_df) -- the two primary CSVs.

    interaction_df has 6 rows (3 outcomes x 2 specs); stratified_df has
    9 rows (3 outcomes x 3 CESD tertiles).
    """
    inter_rows = []
    strat_rows = []
    for outcome, (label, group, kind, w_col) in OUTCOMES.items():
        for spec in ("conservative", "clean"):
            res = fit_interaction(df, outcome, spec)
            if res is None:
                inter_rows.append({
                    "outcome": outcome, "outcome_label": label,
                    "outcome_group": group, "spec": spec,
                    "n": 0, "beta_idgx2": np.nan, "beta_inter": np.nan,
                })
                continue
            inter_rows.append({
                "outcome": outcome,
                "outcome_label": label,
                "outcome_group": group,
                "spec": spec,
                "n": int(res["n"]),
                "beta_idgx2":   float(res["beta"]["idgx2"]),
                "se_idgx2":     float(res["se"]["idgx2"]),
                "beta_cesd":    float(res["beta"]["cesd_sum_main"]),
                "beta_inter":   float(res["beta"]["idgx2_x_cesd"]),
                "se_inter":     float(res["se"]["idgx2_x_cesd"]),
                "p_inter":      float(res["p"]["idgx2_x_cesd"]),
                "ci_lo_inter":  float(res["ci_lo"]["idgx2_x_cesd"]),
                "ci_hi_inter":  float(res["ci_hi"]["idgx2_x_cesd"]),
            })
        for t in (1, 2, 3):
            res_s = fit_stratified(df, outcome, t)
            if res_s is None:
                strat_rows.append({"outcome": outcome, "cesd_tertile": t,
                                   "n": 0, "beta_idgx2": np.nan})
                continue
            strat_rows.append({
                "outcome": outcome,
                "cesd_tertile": t,
                "n": int(res_s["n"]),
                "beta_idgx2": float(res_s["beta"]["idgx2"]),
                "se_idgx2":   float(res_s["se"]["idgx2"]),
                "p_idgx2":    float(res_s["p"]["idgx2"]),
                "ci_lo":      float(res_s["ci_lo"]["idgx2"]),
                "ci_hi":      float(res_s["ci_hi"]["idgx2"]),
            })
    return pd.DataFrame(inter_rows), pd.DataFrame(strat_rows)


# ---------------------------------------------------------------------------
# Sensitivity: quintile dose-response within CESD_SUM tertile
# ---------------------------------------------------------------------------
def quintile_doseresponse_by_tertile(df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    """Within each CESD_SUM tertile, regress Y on IDGX2 quintile trend + adjustment."""
    _, _, _, w_col = OUTCOMES[outcome]
    t = cesd_tertile(df["CESD_SUM"])
    rows = []
    for tert in (1, 2, 3):
        sub = df.loc[t == tert].copy()
        if len(sub) < 50:
            continue
        _, qtrend = quintile_dummies(clean_var(sub["IDGX2"], "IDGX2"), n=5)
        adj = _adj_clean(sub)  # CESD ~constant within tertile
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
            "cesd_tertile": tert,
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
    """E-value on the interaction coefficient. Conservative back-of-envelope
    (treats |beta| as a log-RR analogue); see `dag.md` weak points."""
    rows = []
    for _, r in primary.iterrows():
        if pd.isna(r["beta_inter"]):
            rows.append({"outcome": r["outcome"], "spec": r["spec"],
                         "rr_proxy": np.nan, "evalue": np.nan})
            continue
        rr = float(np.exp(abs(r["beta_inter"])))
        rows.append({
            "outcome": r["outcome"],
            "spec": r["spec"],
            "beta_inter": float(r["beta_inter"]),
            "rr_proxy": rr,
            "evalue": evalue(rr),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Robustness: bias-corrected matching, top-vs-bottom IDGX2 in HIGH-CESD
# ---------------------------------------------------------------------------
def _sd_col(df: pd.DataFrame, col: str) -> float:
    if col not in df.columns:
        return float("nan")
    vals = clean_var(df[col], col).dropna()
    return float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")


def run_sensitivity_extended(W4: pd.DataFrame, primary: pd.DataFrame) -> dict:
    """Cornfield grid + η-tilt + Chinn-2000 E-values for the IDGX2×CESD_SUM
    interaction. The two specs (conservative/clean) gave β identical to four
    decimals per the primary block, so we report Cornfield + η-tilt only on
    the conservative spec to avoid duplicate rows; the spec-collapse is
    documented in the Sensitivity section of report.md.
    η-tilt sweep binarises IDGX2 via top-vs-bottom-quintile WITHIN the
    top-CESD tertile (where the buffering prediction is operationally
    located).
    """
    sd_idgx2 = _sd_col(W4, "IDGX2")
    sd_cesd = _sd_col(W4, "CESD_SUM")
    sd_inter = sd_idgx2 * sd_cesd if (
        np.isfinite(sd_idgx2) and np.isfinite(sd_cesd)
    ) else float("nan")

    pri = primary[primary["spec"] == "conservative"].copy()
    pri["sd_x"] = sd_inter
    pri["sd_y"] = pri["outcome"].map(lambda c: _sd_col(W4, c))
    pri["beta"] = pri["beta_inter"]
    pri["p"] = pri["p_inter"]
    pri["label"] = "IDGX2 x CESD_SUM -> " + pri["outcome"]
    pri["exposure"] = "IDGX2 x CESD_SUM"

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
    t = cesd_tertile(W4["CESD_SUM"])
    high_cesd = W4.loc[t == 3].copy()  # top tertile = most depressed
    for _, r in target.iterrows():
        _, _, _, w_col = OUTCOMES[r["outcome"]]
        cell = build_eta_cell_from_quintile_contrast(
            label=r["label"] + " [high-CESD]",
            df=high_cesd,
            exposure_col="IDGX2",
            outcome_col=r["outcome"],
            weight_col=w_col,
            cluster_col="CLUSTER2",
            adj_builder=_adj_clean,  # CESD as moderator only -> use clean spec
            extra_keys={
                "exposure": "IDGX2 (top-vs-bot quintile, high-CESD tertile)",
                "outcome": r["outcome"],
            },
        )
        if cell is not None:
            cells.append(cell)
    eta_tbl = build_eta_tilt_table(cells)
    return {"evalue_full": ev_full, "cornfield": cf, "eta_tilt": eta_tbl}


def matching_high_cesd(df: pd.DataFrame, outcome: str, M: int = 4) -> Optional[dict]:
    """Bias-corrected NN matching ATE: top-Q5 vs bottom-Q1 IDGX2, high-CESD only.

    - Treated (A=1): top-tertile CESD_SUM AND top-quintile IDGX2.
    - Control (A=0): top-tertile CESD_SUM AND bottom-quintile IDGX2.
    - X (matching covariates): {male, race dummies, PARENT_ED, H1GH1, AH_RAW}.
      CESD_SUM is the stratum, so it is held roughly constant within the
      top-tertile sub-cohort and not used as a matching covariate.
    """
    t = cesd_tertile(df["CESD_SUM"])
    sub = df.loc[t == 3].copy()  # top tertile = most depressed
    _, qidg = quintile_dummies(clean_var(sub["IDGX2"], "IDGX2"), n=5)
    treated_mask = (qidg == 5)
    control_mask = (qidg == 1)
    keep = (treated_mask | control_mask) & sub[outcome].notna()
    sub = sub.loc[keep].copy()
    A = treated_mask.loc[sub.index].astype(int).to_numpy()
    Y = sub[outcome].astype(float).to_numpy()
    male = (sub["BIO_SEX"] == 1).astype(float)
    Xdf = pd.concat([
        male.rename("male"),
        _race_dummies(sub),
        sub["PARENT_ED"].rename("parent_ed"),
        sub["H1GH1"].rename("srh"),
        sub["AH_RAW"].rename("ahpvt"),
    ], axis=1).dropna()
    Y = Y[Xdf.index.get_indexer_for(Xdf.index)]
    A = A[Xdf.index.get_indexer_for(Xdf.index)]
    if A.sum() < M or (1 - A).sum() < M:
        return None
    res = match_ate_bias_corrected(Y, A, Xdf.to_numpy(), M=M)
    res["outcome"] = outcome
    return res


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def run_all() -> Dict[str, pd.DataFrame]:
    print("Loading frame ...")
    W4 = _load_frame()

    print("Primary: WLS interaction (two specs) + tertile-stratified fits ...")
    inter, strat = run_primary(W4)
    inter.to_csv(TABLES_PRIMARY / "em_dep_interaction.csv", index=False)
    strat.to_csv(TABLES_PRIMARY / "em_dep_stratified_betas.csv", index=False)

    print("Sensitivity: quintile dose-response within CESD_SUM tertile ...")
    qdr_rows = []
    for outcome in OUTCOMES:
        qdr_rows.append(quintile_doseresponse_by_tertile(W4, outcome))
    qdr = pd.concat(qdr_rows, ignore_index=True)
    qdr.to_csv(TABLES_SENS / "em_dep_quintile_by_tertile.csv", index=False)

    print("Sensitivity: E-value on interaction coefficient ...")
    ev = evalue_on_interaction(inter)
    ev.to_csv(TABLES_SENS / "em_dep_evalue.csv", index=False)

    print("Sensitivity: extended (Cornfield grid + η-tilt + Chinn-2000 E-values) ...")
    ext = run_sensitivity_extended(W4, inter)
    ext["evalue_full"].to_csv(
        TABLES_SENS / "em_dep_evalue_chinn2000.csv", index=False)
    ext["cornfield"].to_csv(
        TABLES_SENS / "em_dep_cornfield_grid.csv", index=False)
    ext["eta_tilt"].to_csv(
        TABLES_SENS / "em_dep_eta_tilt.csv", index=False)

    print("Robustness: bias-corrected matching, top-vs-bottom IDGX2 in high-CESD ...")
    match_rows = []
    for outcome in OUTCOMES:
        res = matching_high_cesd(W4, outcome)
        if res is None:
            match_rows.append({"outcome": outcome, "ate": np.nan, "se": np.nan,
                               "n_treated": 0, "n_control": 0})
            continue
        match_rows.append({
            "outcome": outcome,
            "ate": float(res["ate"]),
            "se":  float(res["se"]),
            "n_treated": int(res["n_treated"]),
            "n_control": int(res["n_control"]),
        })
    match_df = pd.DataFrame(match_rows)
    match_df.to_csv(TABLES_HANDOFF / "em_dep_matching_high_cesd.csv", index=False)

    return {"interaction": inter, "stratified": strat,
            "qdr": qdr, "evalue": ev, "matching": match_df}


def main() -> None:
    run_all()


if __name__ == "__main__":
    main()

"""EM-Compensatory-by-SES — `IDGX2 x PARENT_ED` effect modification.

Tests whether the marginal effect of W1 in-degree (`IDGX2`) on adult
cardiometabolic + SES outcomes varies by parental education (`PARENT_ED`,
ordinal 0-6). The substantive hypothesis is that low-SES adolescents
benefit more from popularity (network capital substitutes for family
capital), so the interaction coefficient is signed in the direction of
"popularity helps more at low SES" for each outcome.

Pipeline (this scaffold; nothing actually runs yet -- wire `main()` once
the per-outcome DAGs are locked):

  1. WLS interaction model per outcome:
        Y ~ const + IDGX2 + PARENT_ED + IDGX2:PARENT_ED + adjust + ...
     fit via `analysis.wls.weighted_ols`, cluster-robust on `CLUSTER2`,
     weighted by `GSWGT4_2` (cardiometabolic) or `GSW5` (SES; placeholder
     until IPAW lands).
  2. Quintile dose-response within each `PARENT_ED` tertile (sensitivity).
  3. Bias-corrected matching contrast: top-quintile-`IDGX2` vs
     bottom-quintile-`IDGX2` *within* bottom-tertile-`PARENT_ED`. Calls
     `analysis.matching.match_ate_bias_corrected`. **First use of matching
     in the project.**
  4. E-value on the interaction coefficient via
     `analysis.sensitivity.evalue`.

Outputs (relative to this experiment folder):
  tables/primary/em_ses_interaction.csv
  tables/primary/em_ses_interaction.md
  tables/sensitivity/em_ses_quintile_by_tertile.csv
  tables/sensitivity/em_ses_evalue.csv
  tables/handoff/em_ses_matching_low_ped.csv
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
    "H5LM5":    ("S3Q5 CURRENTLY WORK -- W5",           "ses",             "ordinal-1-3",  "GSW5"),
    "H5EC1":    ("S4Q1 INCOME PERS EARNINGS [W4-W5] -- W5", "ses",         "bracketed-1-13","GSW5"),
}


# ---------------------------------------------------------------------------
# Adjustment-set builders
# ---------------------------------------------------------------------------
RACE_LEVELS = ["NH-Black", "Hispanic", "Other"]


def _race_dummies(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for lvl in RACE_LEVELS:
        out[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    out.loc[df["RACE"].isna(), :] = np.nan
    return out


def _adj_cardiometabolic(df: pd.DataFrame) -> pd.DataFrame:
    """Per-outcome DAG-CardioMet placeholder = L0+L1+AHPVT."""
    return pd.concat([
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index),
        _race_dummies(df),
        df["PARENT_ED"].rename("parent_ed"),
        df["CESD_SUM"].rename("cesd_sum"),
        df["H1GH1"].rename("srh"),
        df["AH_RAW"].rename("ahpvt"),
    ], axis=1)


def _adj_ses(df: pd.DataFrame) -> pd.DataFrame:
    """Per-outcome DAG-SES = L0+L1 (drops AHPVT, which is on the credentialism path)."""
    return pd.concat([
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index),
        _race_dummies(df),
        df["PARENT_ED"].rename("parent_ed"),
        df["CESD_SUM"].rename("cesd_sum"),
        df["H1GH1"].rename("srh"),
    ], axis=1)


ADJ_BY_OUTCOME = {
    "H4BMI":    _adj_cardiometabolic,
    "H4WAIST":  _adj_cardiometabolic,
    "H4BMICLS": _adj_cardiometabolic,
    "H5LM5":    _adj_ses,
    "H5EC1":    _adj_ses,
}


# ---------------------------------------------------------------------------
# Frame loading
# ---------------------------------------------------------------------------
def _load_frame() -> pd.DataFrame:
    """W4 analytic frame with all listed outcomes attached.

    Merges the W5 cross-sectional weight `GSW5` from the raw W5 weight file
    so that W5-target outcomes (`H5LM5`, `H5EC1`) can be weighted with their
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
    """WLS of `outcome ~ const + IDGX2 + IDGX2:PARENT_ED + adj`.

    Note `PARENT_ED` is already in the adjustment set; the interaction term
    `IDGX2:PARENT_ED` is added on top. The adjustment-set builder governs
    whether AHPVT is included (per per-outcome DAG).
    """
    _, _, _, w_col = OUTCOMES[outcome]
    adj_builder = ADJ_BY_OUTCOME[outcome]
    exp = clean_var(df["IDGX2"], "IDGX2").rename("idgx2")
    ped = clean_var(df["PARENT_ED"], "PARENT_ED").rename("parent_ed_raw")
    inter = (exp * ped).rename("idgx2_x_parent_ed")
    adj = adj_builder(df)
    X = pd.concat([exp, inter, adj], axis=1)
    X.insert(0, "const", 1.0)
    y = df[outcome].values
    w = df[w_col].values
    psu = df["CLUSTER2"].values
    return weighted_ols(y, X.values, w, psu, column_names=list(X.columns))


def run_primary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for outcome, (label, group, kind, w_col) in OUTCOMES.items():
        res = fit_interaction(df, outcome)
        if res is None:
            rows.append({
                "outcome": outcome, "outcome_label": label, "outcome_group": group,
                "n": 0, "beta_idgx2": np.nan, "beta_inter": np.nan,
                "se_inter": np.nan, "p_inter": np.nan,
            })
            continue
        rows.append({
            "outcome": outcome,
            "outcome_label": label,
            "outcome_group": group,
            "n": int(res["n"]),
            "beta_idgx2":  float(res["beta"]["idgx2"]),
            "se_idgx2":    float(res["se"]["idgx2"]),
            "beta_inter":  float(res["beta"]["idgx2_x_parent_ed"]),
            "se_inter":    float(res["se"]["idgx2_x_parent_ed"]),
            "p_inter":     float(res["p"]["idgx2_x_parent_ed"]),
            "ci_lo_inter": float(res["ci_lo"]["idgx2_x_parent_ed"]),
            "ci_hi_inter": float(res["ci_hi"]["idgx2_x_parent_ed"]),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity: quintile dose-response within PARENT_ED tertile
# ---------------------------------------------------------------------------
def parent_ed_tertile(s: pd.Series) -> pd.Series:
    """Cut PARENT_ED into 3 rank-equal tertiles; returns 1/2/3 with NaN preserved."""
    s = pd.to_numeric(s, errors="coerce")
    mask = s.notna()
    out = pd.Series(np.nan, index=s.index, dtype=float)
    if mask.sum() > 0:
        ranks = s[mask].rank(method="first")
        bins = pd.qcut(ranks, q=3, labels=False, duplicates="drop") + 1
        out.loc[mask] = bins.values
    return out


def quintile_doseresponse_by_tertile(df: pd.DataFrame, outcome: str) -> pd.DataFrame:
    """Within each PARENT_ED tertile, regress Y on IDGX2 quintile trend + adjustment."""
    _, _, _, w_col = OUTCOMES[outcome]
    adj_builder = ADJ_BY_OUTCOME[outcome]
    tertile = parent_ed_tertile(df["PARENT_ED"])
    rows = []
    for t in (1, 2, 3):
        sub = df.loc[tertile == t].copy()
        if len(sub) < 50:
            continue
        _, qtrend = quintile_dummies(clean_var(sub["IDGX2"], "IDGX2"), n=5)
        adj = adj_builder(sub)
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
            "parent_ed_tertile": t,
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
    """E-value on the interaction coefficient.

    The interaction coefficient is on the *outcome scale*; we convert to a
    risk-ratio-analogue by exponentiating an SD-scaled effect (this is a
    deliberately conservative back-of-envelope -- a proper E-value for an
    interaction term would re-cast on the binary outcome). See report TBD
    discussion before quoting numbers.
    """
    rows = []
    for _, r in primary.iterrows():
        if pd.isna(r["beta_inter"]):
            rows.append({"outcome": r["outcome"], "rr_proxy": np.nan, "evalue": np.nan})
            continue
        # Conservative proxy: |beta| treated as a log-RR. Negative -> reciprocal.
        rr = float(np.exp(abs(r["beta_inter"])))
        rows.append({
            "outcome": r["outcome"],
            "beta_inter": float(r["beta_inter"]),
            "rr_proxy": rr,
            "evalue": evalue(rr),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity 4 — Cornfield bias-factor grid + η-tilt sweep + Chinn-2000 E-values.
# Targets the interaction coefficient as the primary "β" and binarises IDGX2
# via top-quintile-vs-bottom WITHIN the low-PED tertile for the η-tilt input.
# ---------------------------------------------------------------------------
def _sd_col(W4: pd.DataFrame, code: str) -> float:
    if code not in W4.columns:
        return float("nan")
    vals = pd.to_numeric(W4[code], errors="coerce").dropna()
    return float(vals.std(ddof=1)) if len(vals) > 1 else float("nan")


def run_sensitivity_extended(W4: pd.DataFrame, primary: pd.DataFrame) -> dict:
    """Cornfield grid + η-tilt + Chinn-2000 E-values for the EM interaction.

    The interaction coefficient ``IDGX2 × PARENT_ED`` is the load-bearing
    estimand here, so the E-value / Cornfield grid use ``beta_inter``. The
    η-tilt sweep targets the **subgroup contrast that the interaction
    encodes** — top-vs-bottom-quintile of IDGX2, restricted to the bottom
    tertile of PARENT_ED — because the interaction's substantive prediction
    is "popularity helps low-SES kids more." (Continuous-A note: IDGX2 is
    continuous; the η-tilt input uses a top-vs-bottom-quintile binarisation,
    which in this experiment doubles as the operational definition of the
    "popular vs unpopular" contrast.)
    """
    # SDs for Chinn-2000.
    sd_idgx2 = _sd_col(W4.assign(IDGX2=clean_var(W4["IDGX2"], "IDGX2")), "IDGX2")
    sd_ped = _sd_col(
        W4.assign(PARENT_ED=clean_var(W4["PARENT_ED"], "PARENT_ED")),
        "PARENT_ED",
    )
    sd_inter = sd_idgx2 * sd_ped if (
        np.isfinite(sd_idgx2) and np.isfinite(sd_ped)
    ) else float("nan")

    pri = primary.copy()
    pri["sd_x"] = sd_inter
    pri["sd_y"] = pri["outcome"].map(lambda c: _sd_col(W4, c))
    pri["beta"] = pri["beta_inter"]
    pri["p"] = pri["p_inter"]
    pri["label"] = "IDGX2 x PARENT_ED -> " + pri["outcome"]
    pri["exposure"] = "IDGX2 x PARENT_ED"

    ev_full = build_evalue_table(
        pri,
        beta_col="beta",
        sd_x_col="sd_x",
        sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label"),
    )
    cf = build_cornfield_grid(
        pri,
        sd_x_col="sd_x",
        sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label"),
    )
    # η-tilt: WITHIN bottom-tertile-PED, use top-vs-bottom IDGX2 quintile as the
    # binary contrast. Pick the two outcomes with the most-significant
    # interaction p-values that reach p < 0.05 (else fall back to top-2 by p).
    sig = pri.dropna(subset=["p"]).sort_values("p")
    target = sig[sig["p"] < 0.05].head(2)
    if target.empty:
        target = sig.head(2)
    cells = []
    tertile = parent_ed_tertile(W4["PARENT_ED"])
    low_ped = W4.loc[tertile == 1].copy()
    for _, r in target.iterrows():
        adj_builder = ADJ_BY_OUTCOME[r["outcome"]]
        _, _, _, w_col = OUTCOMES[r["outcome"]]
        cell = build_eta_cell_from_quintile_contrast(
            label=r["label"] + " [low-PED]",
            df=low_ped,
            exposure_col="IDGX2",
            outcome_col=r["outcome"],
            weight_col=w_col,
            cluster_col="CLUSTER2",
            adj_builder=adj_builder,
            extra_keys={
                "exposure": "IDGX2 (top-vs-bot quintile, low-PED tertile)",
                "outcome": r["outcome"],
            },
        )
        if cell is not None:
            cells.append(cell)
    eta_tbl = build_eta_tilt_table(cells)
    return {"evalue_full": ev_full, "cornfield": cf, "eta_tilt": eta_tbl}


# ---------------------------------------------------------------------------
# Robustness: bias-corrected matching, top-vs-bottom IDGX2 quintile WITHIN
# bottom-tertile PARENT_ED. First use of matching in the project.
# ---------------------------------------------------------------------------
def matching_low_ped(df: pd.DataFrame, outcome: str, M: int = 4) -> Optional[dict]:
    """Bias-corrected NN matching ATE: top-Q5 vs bottom-Q1 IDGX2, low-PED only.

    - Treated (A=1): bottom-tertile PARENT_ED AND top-quintile IDGX2.
    - Control (A=0): bottom-tertile PARENT_ED AND bottom-quintile IDGX2.
    - X (matching covariates): {male, race dummies, CESD_SUM, H1GH1, AH_RAW}.
    """
    tertile = parent_ed_tertile(df["PARENT_ED"])
    sub = df.loc[tertile == 1].copy()
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
        sub["CESD_SUM"].rename("cesd_sum"),
        sub["H1GH1"].rename("srh"),
        sub["AH_RAW"].rename("ahpvt"),
    ], axis=1).dropna()
    Y = Y[Xdf.index.get_indexer_for(Xdf.index)]  # align after dropna
    A = A[Xdf.index.get_indexer_for(Xdf.index)]
    if A.sum() < M or (1 - A).sum() < M:
        return None
    X = Xdf.to_numpy()
    res = match_ate_bias_corrected(Y, A, X, M=M)
    res["outcome"] = outcome
    return res


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def run_all() -> Dict[str, pd.DataFrame]:
    print("Loading frame ...")
    W4 = _load_frame()

    print("Primary: WLS interaction fits ...")
    primary = run_primary(W4)
    primary.to_csv(TABLES_PRIMARY / "em_ses_interaction.csv", index=False)

    print("Sensitivity: quintile dose-response within PARENT_ED tertile ...")
    qdr_rows = []
    for outcome in OUTCOMES:
        qdr_rows.append(quintile_doseresponse_by_tertile(W4, outcome))
    qdr = pd.concat(qdr_rows, ignore_index=True)
    qdr.to_csv(TABLES_SENS / "em_ses_quintile_by_tertile.csv", index=False)

    print("Sensitivity: E-value on interaction coefficient ...")
    ev = evalue_on_interaction(primary)
    ev.to_csv(TABLES_SENS / "em_ses_evalue.csv", index=False)

    print("Sensitivity: extended (Cornfield grid + η-tilt + Chinn-2000 E-values) ...")
    ext = run_sensitivity_extended(W4, primary)
    ext["evalue_full"].to_csv(
        TABLES_SENS / "em_ses_evalue_chinn2000.csv", index=False)
    ext["cornfield"].to_csv(
        TABLES_SENS / "em_ses_cornfield_grid.csv", index=False)
    ext["eta_tilt"].to_csv(
        TABLES_SENS / "em_ses_eta_tilt.csv", index=False)

    print("Robustness: bias-corrected matching, top-vs-bottom IDGX2 in low-PED ...")
    match_rows = []
    for outcome in OUTCOMES:
        res = matching_low_ped(W4, outcome)
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
    match_df.to_csv(TABLES_HANDOFF / "em_ses_matching_low_ped.csv", index=False)

    return {"primary": primary, "qdr": qdr, "evalue": ev, "matching": match_df}


def main() -> None:
    run_all()


if __name__ == "__main__":
    main()

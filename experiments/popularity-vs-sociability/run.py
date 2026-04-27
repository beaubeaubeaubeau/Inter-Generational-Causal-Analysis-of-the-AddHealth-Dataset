"""EXP-POPSOC — popularity vs. sociability across all 13 outcomes.

Two-exposure contrast experiment: ``IDGX2`` (in-degree, peer-conferred
popularity) vs. ``ODGX2`` (out-degree, self-driven sociability), each fit in
a SEPARATE regression per outcome, with the cross-exposure contrast
``Δβ = β_in − β_out`` per outcome computed via paired cluster-bootstrap on
``CLUSTER2``.

Design points (see ``dag.md``):
  - Each (exposure, outcome) cell: WLS via ``analysis.wls.weighted_ols`` with
    ``GSWGT4_2`` and cluster-robust SE on ``CLUSTER2``.
  - Per-outcome adjustment set inherited from each outcome's per-DAG (cog
    uses L0+L1+AHPVT; SES drops AHPVT; mental/functional drop AHPVT until
    DAG-Mental / DAG-Functional are finalised).
  - Paired bootstrap of ``Δβ`` uses ``np.random.default_rng(20260427)``,
    200 iterations, cluster-resampling on ``CLUSTER2``.

Sensitivity blocks:
  - Quintile dose-response per exposure (``analysis.wls.quintile_dummies``).
  - Polysocial-PCA-PC1 alt-exposure: PCA on the 24 z-standardized exposures
    used by cognitive-screening, take PC1, refit primary spec.
  - E-value column per significant β via ``analysis.sensitivity:evalue``.

Outputs (relative to this experiment folder):
  tables/primary/popsoc_primary.csv             (26 rows)
  tables/primary/popsoc_primary.md
  tables/primary/popsoc_paired_bootstrap.csv    (13 rows)
  tables/sensitivity/popsoc_quintile.csv
  tables/sensitivity/popsoc_polysocial_pca.csv
  tables/sensitivity/popsoc_evalue.csv

Run as:
    python experiments/popularity-vs-sociability/run.py
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

RNG_SEED = 20260427
N_BOOT = 200


# ---------------------------------------------------------------------------
# Exposure & outcome registries
# ---------------------------------------------------------------------------
EXPOSURES: Dict[str, str] = {
    "IDGX2": "in-degree (popularity, peer-conferred)",
    "ODGX2": "out-degree (sociability, self-driven)",
}

# (code, label, group)
OUTCOMES: Dict[str, Tuple[str, str]] = {
    "W4_COG_COMP": ("W4 cognitive composite", "cognitive"),
    "H4BMI":       ("S27 BMI—W4", "cardiometabolic"),
    "H4WAIST":     ("S27 MEASURED WAIST (CM)—W4", "cardiometabolic"),
    "H4SBP":       ("S27 SYSTOLIC BLOOD PRESSURE—W4", "cardiometabolic"),
    "H4DBP":       ("S27 DIASTOLIC BLOOD PRESSURE—W4", "cardiometabolic"),
    "H4BMICLS":    ("S27 BMI CLASS—W4", "cardiometabolic"),
    "H5MN1":       ("S13Q1 LAST MO NO CNTRL IMPORT THINGS—W5", "mental_health"),
    "H5MN2":       ("S13Q2 LAST MO CONFID HANDLE PERS PBMS—W5", "mental_health"),
    "H5ID1":       ("S5Q1 HOW IS GEN PHYSICAL HEALTH—W5", "functional"),
    "H5ID4":       ("S5Q4 LIMIT CLIMB SEV. FLIGHT STAIRS—W5", "functional"),
    "H5ID16":      ("S5Q16 HOW OFTEN TROUBLE SLEEPING—W5", "functional"),
    "H5LM5":       ("S3Q5 CURRENTLY WORK—W5", "ses"),
    "H5EC1":       ("S4Q1 INCOME PERS EARNINGS [W4–W5]—W5", "ses"),
}

# Per-outcome adjustment-set tier (inherits from per-outcome DAG; see dag.md).
#   "L0+L1+AHPVT": cognitive + cardiometabolic (provisional until DAG-CardioMet)
#   "L0+L1":       mental + functional + SES (SES drops AHPVT under DAG-SES)
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
    "H5EC1":       "L0+L1",  # DAG-SES drops AHPVT
}

RACE_LEVELS = ["NH-Black", "Hispanic", "Other"]

# Polysocial-PCA exposure list — the 24 W1 social exposures used by
# cognitive-screening and multi-outcome-screening. Matches the `EXPOSURES`
# dict in ``experiments/multi-outcome-screening/run.py``.
POLYSOCIAL_EXPOSURES: List[str] = [
    "IDGX2", "ODGX2", "BCENT10X", "REACH", "REACH3", "INFLDMN", "PRXPREST",
    "IGDMEAN", "IDG_ZERO", "IDG_LEQ1", "HAVEBMF", "HAVEBFF",
    "ESDEN", "ERDEN", "ESRDEN", "RCHDEN",
    "FRIEND_N_NOMINEES", "FRIEND_CONTACT_SUM", "FRIEND_DISCLOSURE_ANY",
    "SCHOOL_BELONG", "H1FS13", "H1FS14", "H1DA7", "H1PR4",
]


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
    "L0":         _adj_L0,
    "L0+L1":      _adj_L0_L1,
    "L0+L1+AHPVT": _adj_L0_L1_AHPVT,
}


# ---------------------------------------------------------------------------
# Frame loading
# ---------------------------------------------------------------------------
def _load_frame() -> pd.DataFrame:
    """Load the W4 analytic frame and attach the W5 outcomes via load_outcome."""
    W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
    for code in OUTCOMES:
        if code == "W4_COG_COMP":
            # Already on the analytic frame; clean defensively in case of nans.
            continue
        W4[code] = load_outcome(W4["AID"], code)
    return W4


# ---------------------------------------------------------------------------
# Single-cell fit
# ---------------------------------------------------------------------------
def _fit_cell(df: pd.DataFrame, exposure_col: str, outcome_col: str,
              adj_builder: Callable[[pd.DataFrame], pd.DataFrame],
              w_col: str = "GSWGT4_2",
              extra_X: Optional[pd.DataFrame] = None) -> Optional[dict]:
    """WLS for one (exposure, outcome) cell with the given adjustment-set builder."""
    exp = clean_var(df[exposure_col], exposure_col)
    adj = adj_builder(df)
    parts = [exp.rename("exposure"), adj]
    if extra_X is not None:
        parts.append(extra_X)
    X = pd.concat(parts, axis=1)
    X.insert(0, "const", 1.0)
    y = df[outcome_col].values
    w = df[w_col].values
    psu = df["CLUSTER2"].values
    return weighted_ols(y, X.values, w, psu, column_names=list(X.columns))


# ---------------------------------------------------------------------------
# Primary block: 2 exposures × 13 outcomes (separate regressions)
# ---------------------------------------------------------------------------
def run_primary(W4: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for exp_name in EXPOSURES:
        for outcome_code, (label, o_group) in OUTCOMES.items():
            tier = ADJ_TIER_BY_OUTCOME[outcome_code]
            res = _fit_cell(W4, exp_name, outcome_code, ADJ_BUILDERS[tier])
            if res is None:
                rows.append({
                    "exposure": exp_name, "outcome": outcome_code,
                    "outcome_label": label, "outcome_group": o_group,
                    "adj_tier": tier, "n": 0,
                    "beta": np.nan, "se": np.nan, "t": np.nan, "p": np.nan,
                    "ci_lo": np.nan, "ci_hi": np.nan, "sig": False,
                })
                continue
            beta = float(res["beta"]["exposure"])
            se = float(res["se"]["exposure"])
            p = float(res["p"]["exposure"])
            rows.append({
                "exposure": exp_name, "outcome": outcome_code,
                "outcome_label": label, "outcome_group": o_group,
                "adj_tier": tier, "n": int(res["n"]),
                "beta": beta, "se": se,
                "t": float(res["t"]["exposure"]), "p": p,
                "ci_lo": float(res["ci_lo"]["exposure"]),
                "ci_hi": float(res["ci_hi"]["exposure"]),
                "sig": bool(p < 0.05),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Paired cluster-bootstrap of Δβ = β_in − β_out per outcome
# ---------------------------------------------------------------------------
def _bootstrap_delta_one_outcome(
    W4: pd.DataFrame, outcome_code: str, rng: np.random.Generator,
) -> dict:
    """Cluster-resampling paired bootstrap of Δβ = β_IDGX2 − β_ODGX2 for one outcome."""
    tier = ADJ_TIER_BY_OUTCOME[outcome_code]
    adj_builder = ADJ_BUILDERS[tier]

    # Observed Δβ on full sample
    res_in = _fit_cell(W4, "IDGX2", outcome_code, adj_builder)
    res_out = _fit_cell(W4, "ODGX2", outcome_code, adj_builder)
    if res_in is None or res_out is None:
        return {
            "outcome": outcome_code, "delta_beta": np.nan,
            "delta_se_boot": np.nan, "delta_ci_lo": np.nan,
            "delta_ci_hi": np.nan, "delta_p_boot": np.nan,
            "n_boot_valid": 0,
        }
    delta_obs = float(res_in["beta"]["exposure"]) - float(res_out["beta"]["exposure"])

    # Cluster-resample N_BOOT times
    clusters = W4["CLUSTER2"].dropna().unique()
    cl_to_rows = {c: W4.index[W4["CLUSTER2"] == c].to_numpy() for c in clusters}
    deltas = np.full(N_BOOT, np.nan)
    for b in range(N_BOOT):
        sampled_cl = rng.choice(clusters, size=len(clusters), replace=True)
        idx = np.concatenate([cl_to_rows[c] for c in sampled_cl])
        boot = W4.loc[idx].reset_index(drop=True)
        r_in = _fit_cell(boot, "IDGX2", outcome_code, adj_builder)
        r_out = _fit_cell(boot, "ODGX2", outcome_code, adj_builder)
        if r_in is None or r_out is None:
            continue
        deltas[b] = float(r_in["beta"]["exposure"]) - float(r_out["beta"]["exposure"])
    valid = deltas[~np.isnan(deltas)]
    if valid.size < 20:  # too many failed bootstrap iterations
        return {
            "outcome": outcome_code, "delta_beta": delta_obs,
            "delta_se_boot": np.nan, "delta_ci_lo": np.nan,
            "delta_ci_hi": np.nan, "delta_p_boot": np.nan,
            "n_boot_valid": int(valid.size),
        }
    se_boot = float(valid.std(ddof=1))
    ci_lo, ci_hi = np.percentile(valid, [2.5, 97.5])
    # Two-sided p from the percentile of zero in the centered bootstrap dist.
    centered = valid - delta_obs
    p_boot = 2.0 * min(
        float(np.mean(centered <= -abs(delta_obs))),
        float(np.mean(centered >= abs(delta_obs))),
    )
    p_boot = max(p_boot, 1.0 / valid.size)  # avoid 0
    return {
        "outcome": outcome_code, "delta_beta": delta_obs,
        "delta_se_boot": se_boot, "delta_ci_lo": float(ci_lo),
        "delta_ci_hi": float(ci_hi), "delta_p_boot": p_boot,
        "n_boot_valid": int(valid.size),
    }


def run_paired_bootstrap(W4: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    for outcome_code in OUTCOMES:
        rows.append(_bootstrap_delta_one_outcome(W4, outcome_code, rng))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity 1 — quintile dose-response per exposure
# ---------------------------------------------------------------------------
def run_sensitivity_quintile(W4: pd.DataFrame) -> pd.DataFrame:
    """For each (exposure, outcome) cell: refit with quintile dummies of the
    exposure (Q1 = reference) and the integer-quintile linear-trend variable.
    Reports β_q5 vs Q1 plus the linear-trend β/p.
    """
    rows = []
    for exp_name in EXPOSURES:
        for outcome_code, (label, o_group) in OUTCOMES.items():
            tier = ADJ_TIER_BY_OUTCOME[outcome_code]
            adj = ADJ_BUILDERS[tier](W4)
            exp_clean = clean_var(W4[exp_name], exp_name)
            dummies, trend = quintile_dummies(exp_clean, n=5)
            # Dummy spec
            X = pd.concat([dummies, adj], axis=1)
            X.insert(0, "const", 1.0)
            res_d = weighted_ols(
                W4[outcome_code].values, X.values,
                W4["GSWGT4_2"].values, W4["CLUSTER2"].values,
                column_names=list(X.columns),
            )
            # Trend spec
            X_t = pd.concat([trend.rename("quintile_trend"), adj], axis=1)
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
# Sensitivity 2 — polysocial PCA (PC1 as alt-exposure)
# ---------------------------------------------------------------------------
def run_sensitivity_polysocial_pca(W4: pd.DataFrame) -> pd.DataFrame:
    """Fit PCA(n_components=5) on the 24 z-standardized W1 exposures, take PC1,
    refit primary spec per outcome with PC1 as the lone exposure."""
    from sklearn.decomposition import PCA

    # Build the (z-standardized) exposure matrix; rows with any NaN are dropped
    # for the PCA fit, then PC1 is back-projected onto the full frame.
    expo_clean = pd.DataFrame(index=W4.index)
    for col in POLYSOCIAL_EXPOSURES:
        if col not in W4.columns:
            # Survey exposures not on W4 frame won't be present; flag and skip.
            continue
        s = clean_var(W4[col], col).astype(float)
        expo_clean[col] = (s - s.mean()) / s.std()
    expo_clean = expo_clean.dropna(how="any")
    if len(expo_clean) < 100:
        return pd.DataFrame()  # not enough overlap
    pca = PCA(n_components=min(5, expo_clean.shape[1]))
    pca.fit(expo_clean.values)
    # Project ALL rows (NaN-safe: rows with any NaN in inputs get NaN in PC1).
    full = pd.DataFrame(index=W4.index)
    for col in POLYSOCIAL_EXPOSURES:
        if col not in W4.columns:
            continue
        s = clean_var(W4[col], col).astype(float)
        full[col] = (s - s.mean()) / s.std()
    pc1 = pd.Series(np.nan, index=W4.index)
    valid = full.dropna(how="any").index
    pc1.loc[valid] = pca.transform(full.loc[valid].values)[:, 0]
    W4_pc = W4.copy()
    W4_pc["POLYSOCIAL_PC1"] = pc1.values

    rows = []
    for outcome_code, (label, o_group) in OUTCOMES.items():
        tier = ADJ_TIER_BY_OUTCOME[outcome_code]
        res = _fit_cell(W4_pc, "POLYSOCIAL_PC1", outcome_code, ADJ_BUILDERS[tier])
        if res is None:
            continue
        rows.append({
            "outcome": outcome_code, "outcome_label": label,
            "outcome_group": o_group, "adj_tier": tier,
            "n": int(res["n"]),
            "beta_pc1": float(res["beta"]["exposure"]),
            "se_pc1": float(res["se"]["exposure"]),
            "p_pc1": float(res["p"]["exposure"]),
            "ci_lo_pc1": float(res["ci_lo"]["exposure"]),
            "ci_hi_pc1": float(res["ci_hi"]["exposure"]),
            "pca_explained_variance_ratio_pc1": float(pca.explained_variance_ratio_[0]),
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Sensitivity 3 — E-values per significant β
# ---------------------------------------------------------------------------
def run_sensitivity_evalue(primary: pd.DataFrame) -> pd.DataFrame:
    """Compute E-values for each significant β. Continuous β is converted to a
    pseudo risk-ratio via the VanderWeele-Ding linear-effect transform:
    treat |β/SE_y| as the equivalent log-odds shift per 1-SD exposure change,
    map to RR = exp(β/SE_y). Residual SD ≈ outcome SD on the sample (rough
    proxy; see methods.md §Sensitivity)."""
    rows = []
    for _, r in primary.iterrows():
        if not r["sig"] or pd.isna(r["beta"]):
            continue
        # Rough RR proxy: exp(beta / 1.0); the OUTCOME-SD scaling is left to
        # the figures.py post-processing step where outcome SDs are loaded.
        # Here we record beta and let figures.py compute RR + evalue with a
        # documented scaling. To keep the sensitivity table self-contained,
        # also store evalue at RR = exp(|beta|) for a unit-exposure proxy.
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
def _outcome_sd(W4: pd.DataFrame, code: str) -> float:
    """Sample SD of an outcome on the analytic frame (used for Chinn-2000 RR)."""
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
    """Cornfield bias-factor grid, η-tilt sweep, and a Chinn-2000-scaled E-value
    table that supplements the unit-exposure table written by
    ``run_sensitivity_evalue``.

    Continuous-A note: ``IDGX2`` and ``ODGX2`` are continuous in-/out-degree.
    The η-tilt sweep is therefore run on a top-quintile-vs-bottom-quintile
    binarisation of each exposure. The two most-significant primary cells
    (selected by the smallest p-value across the 26 cells) get a sweep entry;
    other cells skip the η-tilt input but are still on the Cornfield grid and
    the E-value table.
    """
    # Per-cell SDs.
    primary = primary.copy()
    primary["sd_x"] = primary["exposure"].map(lambda c: _exposure_sd(W4, c))
    primary["sd_y"] = primary["outcome"].map(lambda c: _outcome_sd(W4, c))
    # Build a "label" for each cell so the figure can name them.
    primary["label"] = primary["exposure"] + " -> " + primary["outcome"]

    # 4a — E-value with Chinn-2000 scaling on every primary cell.
    ev_full = build_evalue_table(
        primary,
        beta_col="beta",
        sd_x_col="sd_x",
        sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label"),
    )

    # 4b — Cornfield bias-factor grid for every significant cell.
    cf = build_cornfield_grid(
        primary,
        sd_x_col="sd_x",
        sd_y_col="sd_y",
        keep_cols=("exposure", "outcome", "outcome_group", "label"),
    )

    # 4c — η-tilt sweep on the top-2 most-significant cells via Q5-vs-Q1.
    sig = primary[primary["sig"] & primary["p"].notna()].copy()
    sig = sig.sort_values("p").head(2)
    cells = []
    for _, r in sig.iterrows():
        adj_builder = ADJ_BUILDERS[r["adj_tier"]]
        cell = build_eta_cell_from_quintile_contrast(
            label=r["label"],
            df=W4,
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
# Markdown writer for the primary table
# ---------------------------------------------------------------------------
def write_primary_markdown(primary: pd.DataFrame,
                           bootstrap: pd.DataFrame) -> None:
    lines = ["# EXP-POPSOC — popularity vs. sociability primary results\n"]
    lines.append(
        "Per-outcome WLS β for `IDGX2` (popularity) and `ODGX2` (sociability), "
        "fit in **separate** regressions with cluster-robust SE on `CLUSTER2`. "
        "The cross-exposure contrast `Δβ = β_in − β_out` per outcome is from a "
        f"paired cluster-bootstrap (N={N_BOOT} iterations, seed={RNG_SEED}).\n"
    )
    lines.append(
        "**Adjustment-set inheritance:** L0+L1+AHPVT for cognitive + "
        "cardiometabolic; L0+L1 for mental / functional / SES (SES drops "
        "AHPVT under DAG-SES). See [dag.md](../../dag.md) for the full table.\n"
    )

    # Per-exposure × outcome table.
    lines.append("## Per-(exposure, outcome) cells\n")
    show = primary.copy()
    for c in ("beta", "se", "ci_lo", "ci_hi"):
        show[c] = show[c].map(lambda v: f"{v:.4g}" if pd.notna(v) else "NA")
    show["p"] = show["p"].map(lambda v: f"{v:.3g}" if pd.notna(v) else "NA")
    lines.append(show[["exposure", "outcome", "outcome_group", "n",
                       "beta", "se", "ci_lo", "ci_hi", "p", "sig"]]
                 .to_markdown(index=False))
    lines.append("")

    # Δβ table.
    lines.append("## Paired bootstrap Δβ = β_in − β_out per outcome\n")
    bs = bootstrap.copy()
    for c in ("delta_beta", "delta_se_boot", "delta_ci_lo", "delta_ci_hi"):
        bs[c] = bs[c].map(lambda v: f"{v:.4g}" if pd.notna(v) else "NA")
    bs["delta_p_boot"] = bs["delta_p_boot"].map(
        lambda v: f"{v:.3g}" if pd.notna(v) else "NA")
    lines.append(bs[["outcome", "delta_beta", "delta_se_boot", "delta_ci_lo",
                     "delta_ci_hi", "delta_p_boot", "n_boot_valid"]]
                 .to_markdown(index=False))

    (TABLES_PRIMARY / "popsoc_primary.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def run_popsoc() -> Tuple[pd.DataFrame, pd.DataFrame]:
    print("Loading W4 + W5 outcomes ...")
    W4 = _load_frame()
    print("Running primary 2x13 grid ...")
    primary = run_primary(W4)
    primary.to_csv(TABLES_PRIMARY / "popsoc_primary.csv", index=False)
    print("Running paired cluster-bootstrap of Δβ ...")
    bootstrap = run_paired_bootstrap(W4)
    bootstrap.to_csv(TABLES_PRIMARY / "popsoc_paired_bootstrap.csv", index=False)
    write_primary_markdown(primary, bootstrap)

    print("Sensitivity: quintile dose-response ...")
    quint = run_sensitivity_quintile(W4)
    quint.to_csv(TABLES_SENS / "popsoc_quintile.csv", index=False)
    print("Sensitivity: polysocial-PCA PC1 ...")
    pca = run_sensitivity_polysocial_pca(W4)
    pca.to_csv(TABLES_SENS / "popsoc_polysocial_pca.csv", index=False)
    print("Sensitivity: E-values per significant β ...")
    ev = run_sensitivity_evalue(primary)
    ev.to_csv(TABLES_SENS / "popsoc_evalue.csv", index=False)
    print("Sensitivity: extended (Cornfield grid + η-tilt + Chinn-2000 E-values) ...")
    ext = run_sensitivity_extended(W4, primary)
    ext["evalue_full"].to_csv(
        TABLES_SENS / "popsoc_evalue_chinn2000.csv", index=False)
    ext["cornfield"].to_csv(
        TABLES_SENS / "popsoc_cornfield_grid.csv", index=False)
    ext["eta_tilt"].to_csv(
        TABLES_SENS / "popsoc_eta_tilt.csv", index=False)
    return primary, bootstrap


def main() -> None:
    run_popsoc()


if __name__ == "__main__":
    main()

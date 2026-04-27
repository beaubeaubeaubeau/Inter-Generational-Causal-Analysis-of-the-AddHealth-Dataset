"""Cognitive-screening experiment — end-to-end run.

Merges the four task scripts that produced this experiment's tables:

  - run_baseline_regressions()  was scripts/task10_baseline_regressions.py
  - run_causal_screening()      was scripts/task14_causal_screening.py
  - run_sensitivity_audit()     was scripts/task11_sensitivity.py
  - run_verification()          was scripts/task13_verification.py

main() invokes them in dependency order: baseline → screening → sensitivity →
verification (verification reads the screening shortlist + the baseline
coefficient table). All write into ./tables/{primary,sensitivity,verification}/
relative to this script.

Cache (parquet inputs) lives at cache/ in the repo root and is read via the
analysis package's CACHE constant.
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths and analysis-library imports
# ---------------------------------------------------------------------------
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]  # experiments/cognitive-screening/ -> repo root
sys.path.insert(0, str(ROOT / "scripts"))

from analysis import CACHE  # noqa: E402
from analysis.cleaning import clean_var, neg_control_outcome, VALID_RANGES  # noqa: E402
from analysis.derivation import derive_parent_ed, derive_race_ethnicity  # noqa: E402
from analysis.wls import weighted_ols, quintile_dummies  # noqa: E402
from analysis.weighted_stats import weighted_mean_se, weighted_prop_ci  # noqa: E402

TABLES_PRIMARY = HERE / "tables" / "primary"
TABLES_SENSITIVITY = HERE / "tables" / "sensitivity"
TABLES_VERIFICATION = HERE / "tables" / "verification"
for _p in (TABLES_PRIMARY, TABLES_SENSITIVITY, TABLES_VERIFICATION):
    _p.mkdir(parents=True, exist_ok=True)

RNG = np.random.default_rng(42)

# ---------------------------------------------------------------------------
# Shared frames (loaded once at import; all four blocks read these).
# ---------------------------------------------------------------------------
W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
W1_FULL = pd.read_parquet(CACHE / "analytic_w1_full.parquet")
W5_MODE = pd.read_parquet(CACHE / "analytic_w5_mode_audit.parquet")
W1_ALL = pd.read_parquet(CACHE / "w1inhome.parquet")
W1_NET = pd.read_parquet(CACHE / "w1network.parquet")
W4_HOME = pd.read_parquet(CACHE / "w4inhome.parquet")
W5_FULL = pd.read_parquet(CACHE / "analytic_w5.parquet")

RACE_LEVELS_FULL = ["NH-White", "NH-Black", "Hispanic", "Other"]
RACE_LEVELS = ["NH-Black", "Hispanic", "Other"]


# ===========================================================================
# Block 1 — Baseline regressions  (was scripts/task10_baseline_regressions.py)
# ===========================================================================
def _race_dummies_baseline(df: pd.DataFrame) -> pd.DataFrame:
    """Return k-1 race dummies (ref = NH-White)."""
    out = pd.DataFrame(index=df.index)
    for lvl in RACE_LEVELS:
        out[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    out.loc[df["RACE"].isna(), :] = np.nan
    return out


def _base_covariates(df: pd.DataFrame, include_ahpvt: bool = True) -> pd.DataFrame:
    """Return design matrix for baseline adjustment (WITHOUT intercept)."""
    parts = [
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male"),
        _race_dummies_baseline(df),
        df["PARENT_ED"].rename("parent_ed"),
        df["CESD_SUM"].rename("cesd_sum"),
        df["H1GH1"].rename("srh"),
    ]
    if include_ahpvt:
        parts.append(df["AH_RAW"].rename("ahpvt"))
    return pd.concat(parts, axis=1)


def _build_design_baseline(exposures: Dict[str, pd.Series], df: pd.DataFrame,
                           include_ahpvt: bool = True) -> Tuple[pd.DataFrame, List[str]]:
    """Stack exposures and baseline covariates, plus intercept."""
    cov = _base_covariates(df, include_ahpvt=include_ahpvt)
    exp_df = pd.DataFrame(exposures, index=df.index)
    X = pd.concat([exp_df, cov], axis=1)
    X.insert(0, "const", 1.0)
    return X, list(X.columns)


def _fit_spec_baseline(spec_id: str, label: str, df: pd.DataFrame,
                       y_col: str, exposures: Dict[str, pd.Series],
                       weight_col: str = "GSWGT4_2",
                       include_ahpvt: bool = True) -> List[dict]:
    X, names = _build_design_baseline(exposures, df, include_ahpvt=include_ahpvt)
    y = df[y_col].values
    w = df[weight_col].values
    psu = df["CLUSTER2"].values
    res = weighted_ols(y, X.values, w, psu, column_names=names)
    rows: List[dict] = []
    if res is None:
        return rows
    for term in names:
        rows.append({
            "spec_id": spec_id,
            "spec_label": label,
            "outcome": y_col,
            "term": term,
            "beta": float(res["beta"][term]),
            "se": float(res["se"][term]),
            "t": float(res["t"][term]),
            "p": float(res["p"][term]),
            "ci_lo": float(res["ci_lo"][term]),
            "ci_hi": float(res["ci_hi"][term]),
            "n": res["n"],
            "n_psu": res["n_psu"],
            "r2": res["rsquared"],
            "ahpvt_adjusted": include_ahpvt,
        })
    return rows


def _run_all_baseline_specs() -> pd.DataFrame:
    rows: List[dict] = []

    # ---- Spec 1: anchor linear IDGX2 -> C4WD90_1 ------------------------
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        rows += _fit_spec_baseline(f"S01{tag}",
                         f"IDGX2 -> C4WD90_1 (linear{'+AHPVT' if include_pvt else ''})",
                         W4, "C4WD90_1", {"idgx2": W4["IDGX2"]},
                         include_ahpvt=include_pvt)
        rows += _fit_spec_baseline(f"S01C{tag}",
                         f"IDGX2 -> W4_COG_COMP (linear{'+AHPVT' if include_pvt else ''})",
                         W4, "W4_COG_COMP", {"idgx2": W4["IDGX2"]},
                         include_ahpvt=include_pvt)

    # ---- Spec 2: IDGX2 quintile dummies ----------------------------------
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        qs = W4["IDGX2_QUINTILE"]
        exposures = {f"idg_q{int(q+1)}": (qs == q).astype(float)
                     for q in range(1, 5)}
        rows += _fit_spec_baseline(f"S02{tag}",
                         f"IDGX2 quintiles -> C4WD90_1{'+AHPVT' if include_pvt else ''}",
                         W4, "C4WD90_1", exposures,
                         include_ahpvt=include_pvt)
        rows += _fit_spec_baseline(f"S02C{tag}",
                         f"IDGX2 quintiles -> W4_COG_COMP{'+AHPVT' if include_pvt else ''}",
                         W4, "W4_COG_COMP", exposures,
                         include_ahpvt=include_pvt)

    # ---- Spec 3: composite + components side-by-side --------------------
    for include_pvt in (True,):
        tag = "" if include_pvt else "_noAHPVT"
        for y in ["C4WD90_1", "C4WD60_1", "C4NUMSCR", "W4_COG_COMP"]:
            rows += _fit_spec_baseline(f"S03_{y}{tag}",
                             f"IDGX2 -> {y} (AHPVT adj)",
                             W4, y, {"idgx2": W4["IDGX2"]},
                             include_ahpvt=include_pvt)

    # ---- Spec 4: alternative exposures (swap in) -------------------------
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        for exp_name, col in [
            ("ODGX2_placebo", "ODGX2"),
            ("BCENT10X", "BCENT10X"),
            ("REACH", "REACH"),
            ("PRXPREST", "PRXPREST"),
        ]:
            rows += _fit_spec_baseline(f"S04_{exp_name}{tag}",
                             f"{exp_name} -> W4_COG_COMP",
                             W4, "W4_COG_COMP", {exp_name.lower(): W4[col]},
                             include_ahpvt=include_pvt)

    # ---- Spec 5: isolation indicators ------------------------------------
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        rows += _fit_spec_baseline(f"S05_ZERO{tag}",
                         "I(IDGX2==0) -> W4_COG_COMP",
                         W4, "W4_COG_COMP", {"idg_zero": W4["IDG_ZERO"]},
                         include_ahpvt=include_pvt)
        rows += _fit_spec_baseline(f"S05_LEQ1{tag}",
                         "I(IDGX2<=1) -> W4_COG_COMP",
                         W4, "W4_COG_COMP", {"idg_leq1": W4["IDG_LEQ1"]},
                         include_ahpvt=include_pvt)

    # ---- Spec 6: school belonging (full W1 sample, not network-gated) ----
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        rows += _fit_spec_baseline(f"S06{tag}",
                         "SCHOOL_BELONG -> W4_COG_COMP (full W1)",
                         W1_FULL, "W4_COG_COMP",
                         {"school_belong": W1_FULL["SCHOOL_BELONG"]},
                         include_ahpvt=include_pvt)

    # ---- Spec 7: loneliness / unfriendly (full W1 sample) ----------------
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        rows += _fit_spec_baseline(f"S07{tag}",
                         "H1FS13 + H1FS14 -> W4_COG_COMP",
                         W1_FULL, "W4_COG_COMP",
                         {"lonely": W1_FULL["H1FS13"],
                          "unfriendly": W1_FULL["H1FS14"]},
                         include_ahpvt=include_pvt)

    # ---- Spec 9: heterogeneity (interactions) ----------------------------
    df9 = W4.copy()
    df9["idgx2_c"] = df9["IDGX2"] - df9["IDGX2"].mean(skipna=True)
    df9["male"] = (df9["BIO_SEX"] == 1).astype(float)
    df9["idgx2_x_male"] = df9["idgx2_c"] * df9["male"]
    rows += _fit_spec_baseline("S09_sex",
                     "IDGX2 × sex on W4_COG_COMP",
                     df9, "W4_COG_COMP",
                     {"idgx2_c": df9["idgx2_c"],
                      "idgx2_x_male": df9["idgx2_x_male"]},
                     include_ahpvt=True)
    df9["parent_ed_c"] = df9["PARENT_ED"] - df9["PARENT_ED"].mean(skipna=True)
    df9["idgx2_x_parented"] = df9["idgx2_c"] * df9["parent_ed_c"]
    rows += _fit_spec_baseline("S09_parented",
                     "IDGX2 × parent_ed on W4_COG_COMP",
                     df9, "W4_COG_COMP",
                     {"idgx2_c": df9["idgx2_c"],
                      "idgx2_x_parented": df9["idgx2_x_parented"]},
                     include_ahpvt=True)

    # ---- Spec 10: friendship-grid derived exposures (full W1 sample) -----
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        rows += _fit_spec_baseline(f"S10_nominees{tag}",
                         "FRIEND_N_NOMINEES -> W4_COG_COMP (full W1)",
                         W1_FULL, "W4_COG_COMP",
                         {"friend_n": W1_FULL["FRIEND_N_NOMINEES"]},
                         include_ahpvt=include_pvt)
        rows += _fit_spec_baseline(f"S10_contact{tag}",
                         "FRIEND_CONTACT_SUM -> W4_COG_COMP",
                         W1_FULL, "W4_COG_COMP",
                         {"friend_contact": W1_FULL["FRIEND_CONTACT_SUM"]},
                         include_ahpvt=include_pvt)
        rows += _fit_spec_baseline(f"S10_disclose{tag}",
                         "FRIEND_DISCLOSURE_ANY -> W4_COG_COMP",
                         W1_FULL, "W4_COG_COMP",
                         {"friend_disclose": W1_FULL["FRIEND_DISCLOSURE_ANY"]},
                         include_ahpvt=include_pvt)

    return pd.DataFrame(rows)


def _write_baseline_markdown(df: pd.DataFrame, path: Path) -> None:
    lines = ["# Baseline regressions (exploratory)", ""]
    lines.append("All specifications: WLS on GSWGT4_2, cluster-robust on CLUSTER2, "
                 "use_t=True, df = (n_psu − 1). Exposures reported per spec; covariates "
                 "are sex, race dummies (ref NH-White), parent education, CES-D sum, "
                 "self-rated health, and (unless noted) AHPVT raw.")
    lines.append("")
    lines.append("## Exposure coefficients (primary terms only)")
    lines.append("")
    lines.append("| Spec | Label | Term | β | SE | 95% CI | t | p | N | PSUs | AHPVT-adj |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    exposure_terms = (
        df["term"].str.startswith(("idgx2", "odgx", "bcent", "reach", "prxp",
                                    "idg_", "friend_", "school_", "lonely",
                                    "unfriendly", "idg_q"))
        .fillna(False)
    )
    exposure_rows = df[exposure_terms].copy()
    for _, r in exposure_rows.iterrows():
        ci = f"[{r['ci_lo']:.3f}, {r['ci_hi']:.3f}]"
        lines.append(
            f"| {r['spec_id']} | {r['spec_label']} | {r['term']} | "
            f"{r['beta']:.4f} | {r['se']:.4f} | {ci} | {r['t']:.2f} | "
            f"{r['p']:.3g} | {int(r['n'])} | {int(r['n_psu'])} | "
            f"{'yes' if r['ahpvt_adjusted'] else 'no'} |"
        )
    lines.append("")
    lines.append("## Full coefficient table")
    lines.append("")
    lines.append("See `10_regressions.csv` for all terms (baseline covariates included).")
    lines.append("")
    path.write_text("\n".join(lines))


def run_baseline_regressions() -> pd.DataFrame:
    """Task-10 block: weighted-OLS specifications S01–S10. Writes 10_regressions.{csv,md}."""
    print("Running baseline regressions ...")
    results = _run_all_baseline_specs()
    csv_path = TABLES_PRIMARY / "10_regressions.csv"
    md_path = TABLES_PRIMARY / "10_regressions.md"
    results.to_csv(csv_path, index=False)
    _write_baseline_markdown(results, md_path)
    print(f"Wrote {csv_path} ({len(results)} rows)")
    print(f"Wrote {md_path}")
    return results


# ===========================================================================
# Block 2 — Causal screening  (was scripts/task14_causal_screening.py)
# ===========================================================================
# D8 saturated-school selection fraction. The share of W1 in-home respondents
# whose school was NOT in the network-saturated frame.
_w1net_for_d8 = pd.read_parquet(CACHE / "w1network.parquet", columns=["AID", "IDGX2"])
_w1home_for_d8 = pd.read_parquet(CACHE / "w1inhome.parquet", columns=["AID"])
_n_inhome = len(_w1home_for_d8)
_n_network = int(pd.to_numeric(_w1net_for_d8["IDGX2"], errors="coerce").notna().sum())
SATURATED_LOSS_FRAC: float = (
    1.0 - _n_network / _n_inhome if _n_inhome > 0 else float("nan")
)
del _w1net_for_d8, _w1home_for_d8, _n_inhome, _n_network


def _attach_screening_extras() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Attach H1PR4 + HEIGHT_IN onto W4 / W1_FULL copies for screening."""
    w4 = W4.copy()
    w1f = W1_FULL.copy()
    raw = pd.read_parquet(CACHE / "w1inhome.parquet")[["AID", "H1PR4"]]
    raw["H1PR4"] = pd.to_numeric(raw["H1PR4"], errors="coerce").where(
        lambda s: s.between(1, 5)
    )
    w4 = w4.merge(raw, on="AID", how="left")
    w1f = w1f.merge(raw, on="AID", how="left")
    w4["HEIGHT_IN"] = neg_control_outcome(w4["AID"])
    w1f["HEIGHT_IN"] = neg_control_outcome(w1f["AID"])
    return w4, w1f


NETWORK_EXPOSURES = {
    "IDGX2":       ("IDGX2",    "peer_network",   "continuous"),
    "ODGX2":       ("ODGX2",    "self_network",   "continuous"),
    "BCENT10X":    ("BCENT10X", "peer_network",   "continuous"),
    "REACH":       ("REACH",    "peer_network",   "continuous"),
    "REACH3":      ("REACH3",   "peer_network",   "continuous"),
    "INFLDMN":     ("INFLDMN",  "peer_network",   "continuous"),
    "PRXPREST":    ("PRXPREST", "peer_network",   "continuous"),
    "IGDMEAN":     ("IGDMEAN",  "peer_network",   "continuous"),
    "IDG_ZERO":    ("IDG_ZERO", "isolation",      "binary"),
    "IDG_LEQ1":    ("IDG_LEQ1", "isolation",      "binary"),
    "HAVEBMF":     ("HAVEBMF",  "isolation",      "binary"),
    "HAVEBFF":     ("HAVEBFF",  "isolation",      "binary"),
    "ESDEN":       ("ESDEN",    "egonet",         "continuous"),
    "ERDEN":       ("ERDEN",    "egonet",         "continuous"),
    "ESRDEN":      ("ESRDEN",   "egonet",         "continuous"),
    "RCHDEN":      ("RCHDEN",   "egonet",         "continuous"),
}

SURVEY_EXPOSURES = {
    "FRIEND_N_NOMINEES":     ("FRIEND_N_NOMINEES",     "friendship_grid", "continuous"),
    "FRIEND_CONTACT_SUM":    ("FRIEND_CONTACT_SUM",    "friendship_grid", "continuous"),
    "FRIEND_DISCLOSURE_ANY": ("FRIEND_DISCLOSURE_ANY", "friendship_grid", "binary"),
    "SCHOOL_BELONG":         ("SCHOOL_BELONG",         "belonging",       "continuous"),
    # H1FS13/14, H1DA7, H1PR4 are 4-5 level Likert ordinals (verified vs
    # variable_dictionary §2.3.6/7). Tagged `ordinal` rather than `continuous`
    # so the kind taxonomy is consistent with the dictionary and any future
    # ordinal-aware D6/D7 logic routes correctly. The current screen treats
    # both kinds the same in practice (linear-in-quintile rank correlation),
    # but tagging matters for documentation and downstream interpretability.
    "H1FS13":                ("H1FS13",                "loneliness",      "ordinal"),
    "H1FS14":                ("H1FS14",                "loneliness",      "ordinal"),
    "H1DA7":                 ("H1DA7",                 "qualitative",     "ordinal"),
    "H1PR4":                 ("H1PR4",                 "qualitative",     "ordinal"),
}

EXPOSURES: Dict[str, Tuple[str, str, str, str, bool]] = {}
for _name, (_col, _group, _kind) in NETWORK_EXPOSURES.items():
    EXPOSURES[_name] = ("W4", _col, _group, _kind, True)
for _name, (_col, _group, _kind) in SURVEY_EXPOSURES.items():
    EXPOSURES[_name] = ("W1_FULL", _col, _group, _kind, False)

RED_FLAGS: Dict[str, str] = {
    "H1FS13": "CES-D item; contained in CESD_SUM covariate -> double-adjustment",
    "H1FS14": "CES-D item; contained in CESD_SUM covariate -> double-adjustment",
    "SCHOOL_BELONG": "Mixes individual disposition with school-level context; possible collider given W1 CESD/SRH",
}

SIBLINGS: Dict[str, str] = {
    "IDGX2": "ODGX2",
    "BCENT10X": "ODGX2",
    "FRIEND_DISCLOSURE_ANY": "FRIEND_N_NOMINEES",
    "HAVEBMF": "HAVEBFF",
}


def _race_dummies_screen(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for lvl in RACE_LEVELS:
        out[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    out.loc[df["RACE"].isna(), :] = np.nan
    return out


def _adj_L0(df: pd.DataFrame) -> pd.DataFrame:
    """Demographics only."""
    return pd.concat([
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index),
        _race_dummies_screen(df),
        df["PARENT_ED"].rename("parent_ed"),
    ], axis=1)


def _adj_L0_L1(df: pd.DataFrame) -> pd.DataFrame:
    """Demographics + W1 mental/health state."""
    return pd.concat([
        _adj_L0(df),
        df["CESD_SUM"].rename("cesd_sum"),
        df["H1GH1"].rename("srh"),
    ], axis=1)


def _adj_full(df: pd.DataFrame) -> pd.DataFrame:
    """L0 + L1 + AHPVT (baseline cognitive)."""
    return pd.concat([
        _adj_L0_L1(df),
        df["AH_RAW"].rename("ahpvt"),
    ], axis=1)


ADJ_BUILDERS = {
    "L0": _adj_L0,
    "L0+L1": _adj_L0_L1,
    "L0+L1+AHPVT": _adj_full,
}


def _fit_screen(df: pd.DataFrame, exposure_col: str, y_col: str,
                adj_builder: Callable[[pd.DataFrame], pd.DataFrame],
                w_col: str = "GSWGT4_2") -> Optional[dict]:
    """Weighted OLS of y ~ exposure + adj, cluster-robust on CLUSTER2."""
    exp = clean_var(df[exposure_col], exposure_col)
    adj = adj_builder(df)
    X = pd.concat([exp.rename("exposure"), adj], axis=1)
    X.insert(0, "const", 1.0)
    y = df[y_col].values
    w = df[w_col].values
    psu = df["CLUSTER2"].values
    return weighted_ols(y, X.values, w, psu, column_names=list(X.columns))


def _fit_quintiles(df: pd.DataFrame, exposure_col: str, y_col: str,
                   adj_builder: Callable[[pd.DataFrame], pd.DataFrame],
                   w_col: str = "GSWGT4_2") -> Tuple[Optional[dict], pd.Series]:
    """Fit with Q2..Q5 dummies (ref=Q1). Returns result + trend ranks 1..5."""
    exp = clean_var(df[exposure_col], exposure_col)
    dummies, trend = quintile_dummies(exp, n=5)
    adj = adj_builder(df)
    X = pd.concat([dummies, adj], axis=1)
    X.insert(0, "const", 1.0)
    y = df[y_col].values
    w = df[w_col].values
    psu = df["CLUSTER2"].values
    res = weighted_ols(y, X.values, w, psu, column_names=list(X.columns))
    return res, trend


def _d1_baseline(df, col):
    res = _fit_screen(df, col, "W4_COG_COMP", _adj_full)
    if res is None:
        # Could not fit at all — distinguish from a real fail with pass=None.
        return {"beta": np.nan, "se": np.nan, "p": np.nan, "n": 0, "pass": None}
    b = float(res["beta"]["exposure"])
    p = float(res["p"]["exposure"])
    # Degenerate fit (p=NaN) is a third state distinct from FAIL.
    passes = None if np.isnan(p) else bool(p < 0.05)
    return {"beta": b, "se": float(res["se"]["exposure"]),
            "p": p, "n": int(res["n"]),
            "pass": passes}


def _d2_negctrl(df, col):
    res = _fit_screen(df, col, "HEIGHT_IN", _adj_full)
    if res is None:
        # Could not fit at all — distinguish from a real fail with pass=None.
        return {"beta": np.nan, "se": np.nan, "p": np.nan, "n": 0, "pass": None}
    b = float(res["beta"]["exposure"])
    p = float(res["p"]["exposure"])
    # Degenerate fit (p=NaN) is a third state distinct from FAIL.
    passes = None if np.isnan(p) else bool(p > 0.10)
    return {"beta": b, "se": float(res["se"]["exposure"]),
            "p": p, "n": int(res["n"]),
            "pass": passes}


def _d3_sibling(df, col, sibling_col):
    res_t = _fit_screen(df, col, "W4_COG_COMP", _adj_full)
    res_s = _fit_screen(df, sibling_col, "W4_COG_COMP", _adj_full)
    if res_t is None or res_s is None:
        return {"sibling": sibling_col, "beta_sibling": np.nan,
                "p_sibling": np.nan, "delta": np.nan, "se_pooled": np.nan,
                "pass": False}
    b_t = float(res_t["beta"]["exposure"])
    b_s = float(res_s["beta"]["exposure"])
    se_t = float(res_t["se"]["exposure"])
    se_s = float(res_s["se"]["exposure"])
    se_pooled = float(np.sqrt(se_t ** 2 + se_s ** 2))
    delta = abs(b_t) - abs(b_s)
    same_sign = (np.sign(b_t) == np.sign(b_s)) and (b_t != 0) and (b_s != 0)
    passes = (abs(b_t) > abs(b_s)) and (abs(b_t - b_s) > se_pooled) and same_sign
    return {"sibling": sibling_col, "beta_sibling": b_s,
            "p_sibling": float(res_s["p"]["exposure"]),
            "delta_abs_beta": delta, "se_pooled": se_pooled,
            "pass": bool(passes)}


def _d4_adj_stability(df, col):
    """D4 split into D4a (sensitivity) and D4b (estimand presentation).

    Per the 2026-04-26 reframing (TODO §A18): the L0+L1 → L0+L1+AHPVT step
    is not a sensitivity check but a deliberate change of estimand (level →
    trajectory). Lumping both shifts into one rel_shift conflates two
    different concerns. We now compute:

      * **D4a (sensitivity, pass/fail):** rel-shift across L0 → L0+L1 only.
        Detects hidden confounding via W1 health/affect covariates.
        Threshold: rel_shift < 0.30 AND sign stable.
      * **D4b (estimand presentation, informational, no pass/fail):** records
        β_L0+L1 ("levels estimand") and β_L0+L1+AHPVT ("trajectory estimand")
        side by side, plus the absolute and percentage attenuation between
        them. Big attenuation here is *expected* for cognitive outcomes
        (AHPVT is the trajectory baseline) and is informative, not a
        confounding signal.
    """
    betas = {}
    for name, builder in ADJ_BUILDERS.items():
        res = _fit_screen(df, col, "W4_COG_COMP", builder)
        betas[name] = float(res["beta"]["exposure"]) if res else np.nan

    # D4a: sensitivity check on L0 → L0+L1 (no AHPVT).
    b0 = betas["L0"]
    b1 = betas["L0+L1"]
    if not (np.isnan(b0) or np.isnan(b1)):
        ref_a = abs(b1) if abs(b1) > 1e-10 else abs(b0)
        d4a_rel_shift = abs(b0 - b1) / ref_a if ref_a > 0 else np.nan
        d4a_sign_stable = (np.sign(b0) == np.sign(b1)) and (b0 != 0) and (b1 != 0)
    else:
        d4a_rel_shift = np.nan
        d4a_sign_stable = False
    d4a_pass = (not np.isnan(d4a_rel_shift)) and (d4a_rel_shift < 0.30) and d4a_sign_stable

    # D4b: estimand-change presentation. β_levels vs β_trajectory.
    bf = betas["L0+L1+AHPVT"]
    if not (np.isnan(b1) or np.isnan(bf)):
        d4b_abs_shift = abs(b1 - bf)
        d4b_pct_attenuation = (1 - abs(bf) / abs(b1)) if abs(b1) > 1e-10 else np.nan
    else:
        d4b_abs_shift = np.nan
        d4b_pct_attenuation = np.nan

    return {
        "beta_L0": betas["L0"],
        "beta_L0_L1": betas["L0+L1"],
        "beta_L0_L1_AHPVT": betas["L0+L1+AHPVT"],
        # D4a: sensitivity, drives pass/fail. Loop adds d4_ prefix.
        "a_rel_shift": d4a_rel_shift,
        "a_sign_stable": bool(d4a_sign_stable),
        "a_pass": bool(d4a_pass),
        # D4b: estimand presentation, informational only.
        "b_beta_levels": b1,
        "b_beta_trajectory": bf,
        "b_abs_shift": d4b_abs_shift,
        "b_pct_attenuation": d4b_pct_attenuation,
    }


def _d5_component_consistency(df, col):
    results = {}
    for y in ["C4WD90_1", "C4WD60_1", "C4NUMSCR"]:
        res = _fit_screen(df, col, y, _adj_full)
        if res is None:
            results[y] = {"beta": np.nan, "p": np.nan}
        else:
            results[y] = {
                "beta": float(res["beta"]["exposure"]),
                "p": float(res["p"]["exposure"]),
            }
    betas = [r["beta"] for r in results.values() if not np.isnan(r["beta"])]
    pvals = [r["p"] for r in results.values() if not np.isnan(r["p"])]
    sign_consistent = (
        len(betas) == 3 and (all(b > 0 for b in betas) or all(b < 0 for b in betas))
    )
    n_sig = sum(p < 0.10 for p in pvals)
    passes = sign_consistent and n_sig >= 2
    return {"beta_c4wd90": results["C4WD90_1"]["beta"],
            "beta_c4wd60": results["C4WD60_1"]["beta"],
            "beta_c4numscr": results["C4NUMSCR"]["beta"],
            "p_c4wd90": results["C4WD90_1"]["p"],
            "p_c4wd60": results["C4WD60_1"]["p"],
            "p_c4numscr": results["C4NUMSCR"]["p"],
            "sign_consistent": sign_consistent, "n_sig_p10": int(n_sig),
            "pass": bool(passes)}


def _d6_dose_response(df, col, kind):
    if kind == "binary":
        return {"trend_rho": np.nan, "monotone_sign": None, "pass": None}
    res, trend = _fit_quintiles(df, col, "W4_COG_COMP", _adj_full)
    if res is None:
        return {"trend_rho": np.nan, "monotone_sign": None, "pass": False}
    q_terms = [f"q{k}" for k in range(2, 6) if f"q{k}" in res["beta"].index]
    q_vals = np.array([int(t[1:]) for t in q_terms], dtype=float)
    b_vals = np.array([float(res["beta"][t]) for t in q_terms])
    ranks_q = pd.Series(q_vals).rank().values
    ranks_b = pd.Series(b_vals).rank().values
    rho = float(np.corrcoef(ranks_q, ranks_b)[0, 1]) if len(q_vals) >= 2 else np.nan
    monotone_sign = (
        all(b > 0 for b in b_vals) or all(b < 0 for b in b_vals)
    ) if len(b_vals) >= 2 else None
    # Threshold |rho| > 0.6 per the conventional dose-response dose-monotonicity
    # cutoff (decision 2026-04-26). Previously 0.7; loosened to align with
    # the standard convention and avoid being needlessly strict on the
    # 4-free-quintile-β rank correlation.
    passes = (not np.isnan(rho)) and (abs(rho) > 0.6) and bool(monotone_sign)
    return {"trend_rho": rho, "monotone_sign": bool(monotone_sign),
            "betas_q2_q5": b_vals.tolist(),
            "pass": bool(passes)}


def _d7_overlap(df, col, kind):
    import statsmodels.api as sm
    if kind == "binary":
        exp = clean_var(df[col], col)
        adj = _adj_full(df)
        mask = exp.notna() & adj.notna().all(axis=1)
        if mask.sum() < 50 or len(exp[mask].unique()) < 2:
            return {"overlap_min_p": np.nan, "overlap_max_p": np.nan,
                    "eff_n": int(mask.sum()), "pass": False}
        X = sm.add_constant(adj[mask])
        try:
            m = sm.Logit(exp[mask].astype(int), X).fit(disp=False)
            p_hat = m.predict(X)
        except Exception:
            return {"overlap_min_p": np.nan, "overlap_max_p": np.nan,
                    "eff_n": int(mask.sum()), "pass": False}
    else:
        exp = clean_var(df[col], col)
        _, trend = quintile_dummies(exp, n=5)
        sub_mask = trend.isin([1.0, 5.0])
        if sub_mask.sum() < 50:
            return {"overlap_min_p": np.nan, "overlap_max_p": np.nan,
                    "eff_n": int(sub_mask.sum()), "pass": False}
        sub = df[sub_mask].copy()
        sub["A"] = (trend[sub_mask] == 5.0).astype(int)
        adj = _adj_full(sub)
        mask = adj.notna().all(axis=1) & sub["A"].notna()
        if mask.sum() < 50:
            return {"overlap_min_p": np.nan, "overlap_max_p": np.nan,
                    "eff_n": int(mask.sum()), "pass": False}
        X = sm.add_constant(adj[mask])
        try:
            m = sm.Logit(sub.loc[mask, "A"].astype(int), X).fit(disp=False)
            p_hat = m.predict(X)
        except Exception:
            return {"overlap_min_p": np.nan, "overlap_max_p": np.nan,
                    "eff_n": int(mask.sum()), "pass": False}
    pmin = float(p_hat.min())
    pmax = float(p_hat.max())
    eff_n = int(((p_hat >= 0.05) & (p_hat <= 0.95)).sum())
    passes = (pmin >= 0.02) and (pmax <= 0.98) and (eff_n >= 500)
    return {"overlap_min_p": pmin, "overlap_max_p": pmax,
            "eff_n": eff_n, "pass": bool(passes)}


def _d8_saturation(requires_sat):
    frac = SATURATED_LOSS_FRAC if requires_sat else 0.0
    return {"saturated_loss_frac": frac, "flag": bool(requires_sat and frac > 0.25)}


def _d9_red_flag(name):
    msg = RED_FLAGS.get(name, "")
    return {"red_flag": bool(msg), "red_flag_msg": msg}


def _screen_all(w4_screen: pd.DataFrame, w1_screen: pd.DataFrame) -> pd.DataFrame:
    rows: List[dict] = []
    for name, (frame_key, col, group, kind, req_sat) in EXPOSURES.items():
        df = w4_screen if frame_key == "W4" else w1_screen
        row = {"exposure": name, "group": group, "kind": kind,
               "frame": frame_key}
        d1 = _d1_baseline(df, col)
        d2 = _d2_negctrl(df, col)
        d4 = _d4_adj_stability(df, col)
        d5 = _d5_component_consistency(df, col)
        d6 = _d6_dose_response(df, col, kind)
        d7 = _d7_overlap(df, col, kind)
        d8 = _d8_saturation(req_sat)
        d9 = _d9_red_flag(name)
        # D3 sibling-dissociation skipped for network exposures (req_sat=True):
        # the within-network-file siblings (ODGX2 ↔ IDGX2 etc.) are too
        # construct-correlated to dissociate (decision 2026-04-26 / TODO §A16).
        # No structurally-independent placebo is available within the network
        # data; D2 (negative-control outcome) and D7 (overlap) carry the
        # confounding-detection load for these exposures instead.
        sibling = SIBLINGS.get(name)
        if sibling and not req_sat:
            sib_col = EXPOSURES[sibling][1] if sibling in EXPOSURES else sibling
            d3 = _d3_sibling(df, col, sib_col)
        else:
            d3 = {"sibling": None, "beta_sibling": np.nan,
                  "p_sibling": np.nan, "delta_abs_beta": np.nan,
                  "se_pooled": np.nan, "pass": None}
        for k, v in {"d1_": d1, "d2_": d2, "d3_": d3, "d4_": d4,
                     "d5_": d5, "d6_": d6, "d7_": d7, "d8_": d8,
                     "d9_": d9}.items():
            for kk, vv in v.items():
                row[k + kk] = vv
        rows.append(row)
    return pd.DataFrame(rows)


def _classify_screening(df: pd.DataFrame) -> pd.DataFrame:
    def _is_none(v) -> bool:
        # Helper: a diagnostic is "None" (degenerate / not applicable) when
        # it is literally None or NaN.
        return v is None or (isinstance(v, float) and pd.isna(v))

    def _row(r: pd.Series) -> Tuple[str, int, str]:
        d1 = r["d1_pass"]
        d2 = r["d2_pass"]
        d3 = r["d3_pass"]
        d4 = r["d4_a_pass"]  # D4a sensitivity (L0 → L0+L1 only) drives pass/fail
        d5 = r["d5_pass"]
        d6 = r["d6_pass"]
        d7 = r["d7_pass"]
        red = r["d9_red_flag"]

        # Build score from real pass/fail booleans only; skip None (degenerate).
        passes = []
        for d in (d1, d2, d4, d5, d7):
            if not _is_none(d):
                passes.append(d)
        if not _is_none(d3):
            passes.append(d3)
        if not _is_none(d6):
            passes.append(d6)
        score = int(sum(bool(p) for p in passes))
        wscore = score
        for w in (d2, d4):
            if w is True:
                wscore += 1
        if d3 is True:
            wscore += 1

        notes = []
        # D2 (HEIGHT_IN) is contaminated per methods.md §2 — do not Drop on
        # D2 alone; only flag.
        # D3-fail with sibling stronger remains a Drop reason. Guard the
        # comparisons against NaN/None p-values.
        if (d3 is False) and (r["d3_delta_abs_beta"] is not None) \
                and (not pd.isna(r["d3_delta_abs_beta"])) \
                and (r["d3_delta_abs_beta"] < 0):
            notes.append("D3 fails: sibling stronger")
            cat = "Drop"
        elif d1 is False:
            notes.append("D1 association null (p>=0.05)")
            cat = "Weakened"
        elif red:
            notes.append(f"D9 red flag: {r['d9_red_flag_msg']}")
            cat = "Weakened"
        elif d1 and (d2 is True or _is_none(d2)) and d4 and (
                d3 is True or _is_none(d3)):
            cat = "Promising"
        else:
            cat = "Mixed"
            fails = []
            # NaN-guard the D2 weak-fail flag — only annotate when d2_p is
            # a real number.
            if d2 is False and pd.notna(r["d2_p"]) and r["d2_p"] <= 0.10:
                fails.append("D2 weakly fails (p<=0.10)")
            if d3 is False:
                fails.append("D3 fails (sibling not dissociated)")
            if not d4:
                fails.append("D4 unstable across adjustment sets")
            notes.append(", ".join(fails))
        return cat, wscore, "; ".join([n for n in notes if n])

    cats, scores, notes = [], [], []
    for _, r in df.iterrows():
        c, s, n = _row(r)
        cats.append(c)
        scores.append(s)
        notes.append(n)
    df = df.copy()
    df["category"] = cats
    df["score"] = scores
    df["notes"] = notes
    return df


def _write_screening_markdown(results: pd.DataFrame, path: Path) -> None:
    L: List[str] = []
    L.append("# Preliminary causal screening of social-exposure treatments")
    L.append("")
    L.append("Screens each W1 adolescent-social exposure against a battery of "
             "falsification / plausibility diagnostics (D1-D9). All diagnostics "
             "reuse weighted OLS on `GSWGT4_2`, cluster-robust SEs on `CLUSTER2`, "
             "and the same adjustment set conventions used in the "
             "baseline-regressions block of this experiment.")
    L.append("")
    L.append("## Diagnostics")
    L.append("")
    L.append("- **D1** baseline association on W4_COG_COMP (L0+L1+AHPVT); pass: p<0.05.")
    L.append("- **D2** negative-control outcome HEIGHT_IN; pass: p>0.10.")
    L.append("- **D3** sibling-exposure dissociation (where a sibling exists); pass: |beta_t| > |beta_sib| with |diff| > pooled SE.")
    L.append("- **D4** adjustment-set stability across L0 / L0+L1 / L0+L1+AHPVT; pass: relative shift <30% AND sign stable.")
    L.append("- **D5** outcome-component consistency across C4WD90_1 / C4WD60_1 / C4NUMSCR; pass: sign consistent AND >=2/3 with p<0.10.")
    L.append("- **D6** dose-response monotonicity (continuous only); pass: |rho_trend| > 0.6 AND monotone sign.")
    L.append("- **D7** positivity / overlap (Q5 vs Q1 logit, or binary balance); pass: p_hat in (0.02, 0.98) AND eff N >= 500.")
    L.append("- **D8** saturated-school selection penalty (network exposures, informational).")
    L.append("- **D9** collider / double-adjustment red flag (hard-coded lookup).")
    L.append("")

    L.append("## Screening matrix")
    L.append("")
    L.append("| Exposure | Group | N | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D9 | Category | Score |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|---|")

    def _p(v):
        if v is None or (isinstance(v, float) and pd.isna(v)):
            return "NA"
        return "PASS" if bool(v) else "FAIL"

    for _, r in results.iterrows():
        L.append(
            f"| {r.exposure} | {r.group} | {int(r.d1_n)} | {_p(r.d1_pass)} | "
            f"{_p(r.d2_pass)} | {_p(r.d3_pass)} | {_p(r.d4_a_pass)} | "
            f"{_p(r.d5_pass)} | {_p(r.d6_pass)} | {_p(r.d7_pass)} | "
            f"{'YES' if r.d9_red_flag else 'no'} | "
            f"{r.category} | {r.score} |"
        )
    L.append("")

    L.append("## Per-exposure commentary")
    L.append("")
    for _, r in results.iterrows():
        L.append(f"### {r.exposure} ({r.group})  --  **{r.category}** [score {r.score}]")
        L.append("")
        L.append(f"- D1 primary beta = {r.d1_beta:.4g} (SE {r.d1_se:.4g}, p = {r.d1_p:.3g}, N = {int(r.d1_n)}).")
        L.append(f"- D2 HEIGHT_IN beta = {r.d2_beta:.4g} (p = {r.d2_p:.3g}); {'PASS' if r.d2_pass else 'FAIL'}.")
        if r.d3_sibling is not None and not (isinstance(r.d3_sibling, float) and pd.isna(r.d3_sibling)):
            L.append(f"- D3 sibling {r.d3_sibling}: beta_sib = {r.d3_beta_sibling:.4g}, "
                     f"delta |beta| = {r.d3_delta_abs_beta:.4g}; {'PASS' if r.d3_pass else 'FAIL'}.")
        L.append(
            f"- **D4a (sensitivity, L0 → L0+L1):** rel-shift = "
            f"{r.d4_a_rel_shift if not pd.isna(r.d4_a_rel_shift) else float('nan'):.3g}; "
            f"sign stable = {bool(r.d4_a_sign_stable)}; "
            f"{'PASS' if r.d4_a_pass else 'FAIL'}."
        )
        L.append(
            f"- **D4b (estimand presentation, L0+L1 vs L0+L1+AHPVT, no pass/fail):** "
            f"β_levels = {r.d4_b_beta_levels:.4g}; "
            f"β_trajectory = {r.d4_b_beta_trajectory:.4g}; "
            f"AHPVT-driven attenuation = "
            f"{r.d4_b_pct_attenuation if not pd.isna(r.d4_b_pct_attenuation) else float('nan'):.1%}."
        )
        L.append(f"- D5 {r.d5_n_sig_p10}/3 components significant at p<0.10; sign consistent = {bool(r.d5_sign_consistent)}; "
                 f"{'PASS' if r.d5_pass else 'FAIL'}.")
        if r.kind != "binary":
            rho = r.d6_trend_rho
            L.append(f"- D6 trend rho = {rho if not pd.isna(rho) else float('nan'):.3g}; "
                     f"monotone sign = {r.d6_monotone_sign}; {'PASS' if r.d6_pass else 'FAIL'}.")
        L.append(f"- D7 overlap: p_hat in [{r.d7_overlap_min_p:.3g}, {r.d7_overlap_max_p:.3g}]; "
                 f"eff N = {int(r.d7_eff_n)}; {'PASS' if r.d7_pass else 'FAIL'}.")
        if r.d8_flag:
            L.append(f"- D8 saturated-school selection: {r.d8_saturated_loss_frac * 100:.1f}% of W1 is outside the network frame.")
        if r.d9_red_flag:
            L.append(f"- D9 RED FLAG: {r.d9_red_flag_msg}.")
        if r.notes:
            L.append(f"- Notes: {r.notes}.")
        L.append("")

    L.append("## Shortlist")
    L.append("")
    promising = results[results["category"] == "Promising"].sort_values("score", ascending=False)
    mixed = results[results["category"] == "Mixed"].sort_values("score", ascending=False)
    weakened = results[results["category"] == "Weakened"]
    dropped = results[results["category"] == "Drop"]
    L.append(f"- **Promising ({len(promising)}):** "
             + (", ".join(promising["exposure"].tolist()) if len(promising) else "(none)"))
    L.append(f"- **Mixed ({len(mixed)}):** "
             + (", ".join(mixed["exposure"].tolist()) if len(mixed) else "(none)"))
    L.append(f"- **Weakened ({len(weakened)}):** "
             + (", ".join(weakened["exposure"].tolist()) if len(weakened) else "(none)"))
    L.append(f"- **Dropped ({len(dropped)}):** "
             + (", ".join(dropped["exposure"].tolist()) if len(dropped) else "(none)"))
    L.append("")

    shortlist = pd.concat([promising.head(4), mixed.head(2)])
    if len(shortlist) == 0:
        L.append("**Shortlist for formal causal estimation: NONE** - no exposure "
                 "passes the screen. Recommended next steps: widen the adjustment "
                 "set (consider adding parent occupational status and household "
                 "income PA55 where available), consider the cardiometabolic "
                 "pivot from reference/addhealth_synthesis.md section 9, or shift "
                 "to formal bounding with Manski-style worst-case assumptions "
                 "for the saturated-school selection.")
    else:
        L.append("**Shortlist for formal causal estimation: "
                 + ", ".join(shortlist["exposure"].tolist()) + "**")
        L.append("")
        L.append("> Note: this shortlist is for the **cognitive** outcome only. "
                 "The cross-outcome handoff list (which includes IDGX2 for "
                 "cardiometabolic outcomes) comes from "
                 "`experiments/multi-outcome-screening/`.")
        L.append("")
        for _, r in shortlist.iterrows():
            L.append(f"- `{r.exposure}` ({r.category}): D1 beta = {r.d1_beta:.3g} (p={r.d1_p:.3g}); "
                     f"D2 HEIGHT_IN p = {r.d2_p:.3g}; D4a rel-shift = "
                     f"{r.d4_a_rel_shift if not pd.isna(r.d4_a_rel_shift) else float('nan'):.3g}.")
    L.append("")

    path.write_text("\n".join(L))


def _bh_qvalues(pvals: np.ndarray) -> np.ndarray:
    """Benjamini-Hochberg q-values for a 1-D array of p-values.

    Uses scipy.stats.false_discovery_control when available; otherwise
    falls back to a manual implementation. NaN p-values pass through as
    NaN q-values (BH only applied across valid p-values).
    """
    arr = np.asarray(pvals, dtype=float)
    out = np.full_like(arr, np.nan, dtype=float)
    valid = ~np.isnan(arr)
    if valid.sum() == 0:
        return out
    p_valid = arr[valid]
    try:
        from scipy.stats import false_discovery_control
        q_valid = false_discovery_control(p_valid, method="bh")
    except (ImportError, AttributeError):
        # Manual BH: sort ascending, q_i = p_i * N / rank_i, then enforce
        # monotonicity from the largest rank down.
        m = len(p_valid)
        order = np.argsort(p_valid)
        ranked = p_valid[order]
        q_sorted = ranked * m / np.arange(1, m + 1)
        # Cumulative min from the right (largest p downward).
        for i in range(m - 2, -1, -1):
            q_sorted[i] = min(q_sorted[i], q_sorted[i + 1])
        q_valid = np.empty(m, dtype=float)
        q_valid[order] = np.clip(q_sorted, 0.0, 1.0)
    out[valid] = q_valid
    return out


def run_causal_screening() -> pd.DataFrame:
    """Task-14 block: 24 × D1–D9 screening matrix + shortlist + markdown."""
    print("Running causal screening pass ...")
    w4_screen, w1_screen = _attach_screening_extras()
    results = _screen_all(w4_screen, w1_screen)
    results = _classify_screening(results)

    # BH-FDR within outcome on the D1 grid. Cognitive-screening has only one
    # outcome (W4_COG_COMP), so the q-values are computed across all 24
    # exposures.
    results["d1_q"] = _bh_qvalues(results["d1_p"].to_numpy())

    matrix_path = TABLES_PRIMARY / "14_screening_matrix.csv"
    results.to_csv(matrix_path, index=False)
    print(f"Wrote {matrix_path} ({len(results)} rows)")

    shortlist = (
        results[results["category"].isin(["Promising", "Mixed"])]
        .sort_values(["category", "score"], ascending=[True, False])
        [["exposure", "category", "score", "notes"]]
    )
    shortlist["recommended_next"] = shortlist["category"].map({
        "Promising": "AIPW + E-value",
        "Mixed": "AIPW conditional on widened adjustment set",
    })
    shortlist_path = TABLES_PRIMARY / "14_shortlist.csv"
    shortlist.to_csv(shortlist_path, index=False)
    print(f"Wrote {shortlist_path} ({len(shortlist)} rows)")

    md_path = TABLES_PRIMARY / "14_screening.md"
    _write_screening_markdown(results, md_path)
    print(f"Wrote {md_path}")
    return results


# ===========================================================================
# Block 3 — Sensitivity audit  (was scripts/task11_sensitivity.py)
# ===========================================================================
def _race_dummies_sens(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for lvl in RACE_LEVELS:
        out[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    out.loc[df["RACE"].isna(), :] = np.nan
    return out


def _build_design_idgx2(df, exp_col="IDGX2", include_ahpvt=True):
    parts = [
        df[exp_col].rename("exposure"),
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index),
        _race_dummies_sens(df),
        df["PARENT_ED"].rename("parent_ed"),
        df["CESD_SUM"].rename("cesd_sum"),
        df["H1GH1"].rename("srh"),
    ]
    if include_ahpvt:
        parts.append(df["AH_RAW"].rename("ahpvt"))
    X = pd.concat(parts, axis=1)
    X.insert(0, "const", 1.0)
    return X


def _weighted_vs_unweighted() -> pd.DataFrame:
    rows = []
    specs = [
        ("IDGX2 linear", W4, "IDGX2", "W4_COG_COMP", "GSWGT4_2"),
        ("ODGX2 placebo", W4, "ODGX2", "W4_COG_COMP", "GSWGT4_2"),
        ("BCENT10X", W4, "BCENT10X", "W4_COG_COMP", "GSWGT4_2"),
        ("REACH", W4, "REACH", "W4_COG_COMP", "GSWGT4_2"),
        ("Isolation (<=1)", W4, "IDG_LEQ1", "W4_COG_COMP", "GSWGT4_2"),
        ("School belong (full)", W1_FULL, "SCHOOL_BELONG", "W4_COG_COMP", "GSWGT4_2"),
    ]
    for label, df, exp, y_col, w_col in specs:
        X = _build_design_idgx2(df, exp_col=exp, include_ahpvt=True)
        y = df[y_col].values
        psu = df["CLUSTER2"].values
        w = df[w_col].values
        res_w = weighted_ols(y, X.values, w, psu, column_names=list(X.columns))
        res_u = weighted_ols(y, X.values, np.ones_like(w), psu,
                             column_names=list(X.columns))
        if res_w is None or res_u is None:
            continue
        rows.append({
            "spec": label,
            "beta_weighted": res_w["beta"]["exposure"],
            "se_weighted": res_w["se"]["exposure"],
            "t_weighted": res_w["t"]["exposure"],
            "p_weighted": res_w["p"]["exposure"],
            "beta_unweighted": res_u["beta"]["exposure"],
            "se_unweighted": res_u["se"]["exposure"],
            "t_unweighted": res_u["t"]["exposure"],
            "p_unweighted": res_u["p"]["exposure"],
            "sign_flip": (
                (res_w["beta"]["exposure"] * res_u["beta"]["exposure"]) < 0
            ),
            "t_ratio": (
                abs(res_w["t"]["exposure"]) / max(abs(res_u["t"]["exposure"]), 1e-6)
            ),
            "n": res_w["n"],
        })
    return pd.DataFrame(rows)


def _collinearity() -> Tuple[pd.DataFrame, pd.DataFrame]:
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    cols = ["IDGX2", "ODGX2", "BCENT10X", "REACH", "PRXPREST"]
    sub = W4[cols].dropna()
    corr = sub.corr()
    X = sm.add_constant(sub)
    vifs = []
    for i, c in enumerate(X.columns):
        if c == "const":
            continue
        vif = variance_inflation_factor(X.values, i)
        vifs.append({"variable": c, "VIF": vif})
    return pd.DataFrame(vifs), corr


def _permutation_placebo(n_perm=500) -> pd.DataFrame:
    df = W4.dropna(subset=["IDGX2", "W4_COG_COMP", "BIO_SEX", "PARENT_ED",
                           "CESD_SUM", "H1GH1", "AH_RAW", "RACE", "CLUSTER2",
                           "GSWGT4_2"]).copy()
    betas = []
    for i in range(n_perm):
        df["idg_perm"] = (
            df.groupby("CLUSTER2")["IDGX2"]
              .transform(lambda x: RNG.permutation(x.values))
        )
        X = _build_design_idgx2(df.assign(IDGX2=df["idg_perm"]))
        res = weighted_ols(df["W4_COG_COMP"].values, X.values,
                           df["GSWGT4_2"].values, df["CLUSTER2"].values,
                           column_names=list(X.columns))
        if res is not None:
            betas.append(res["beta"]["exposure"])
    perm = pd.DataFrame({"beta_permuted": betas})
    X = _build_design_idgx2(df)
    res_obs = weighted_ols(df["W4_COG_COMP"].values, X.values,
                           df["GSWGT4_2"].values, df["CLUSTER2"].values,
                           column_names=list(X.columns))
    perm.attrs["observed_beta"] = float(res_obs["beta"]["exposure"])
    perm.attrs["p_perm"] = float(
        np.mean(np.abs(perm["beta_permuted"]) >= abs(perm.attrs["observed_beta"]))
    )
    return perm


def _ahpvt_shift(regressions_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(regressions_csv)
    exp_terms = ("idgx2", "odgx2_placebo", "bcent10x", "reach", "prxprest",
                 "idg_zero", "idg_leq1", "school_belong",
                 "friend_n", "friend_contact", "friend_disclose")
    mask = df["term"].isin(exp_terms)
    sub = df[mask].copy()
    rows = []
    for (outcome, term), grp in sub.groupby(["outcome", "term"]):
        with_pvt = grp[grp["ahpvt_adjusted"]]
        without_pvt = grp[~grp["ahpvt_adjusted"]]
        if len(with_pvt) == 0 or len(without_pvt) == 0:
            continue
        bw = with_pvt["beta"].iloc[0]
        bnw = without_pvt["beta"].iloc[0]
        shrinkage = (bnw - bw) / bnw if bnw != 0 else np.nan
        rows.append({
            "outcome": outcome,
            "term": term,
            "beta_with_ahpvt": bw,
            "beta_without_ahpvt": bnw,
            "pct_shrinkage_from_adjustment": shrinkage,
            "flag_large_shift": abs(shrinkage) > 0.5,
        })
    return pd.DataFrame(rows)


def _saturated_school_balance() -> pd.DataFrame:
    w1net_aids = set(W1_NET.loc[W1_NET["IDGX2"].notna(), "AID"])
    w1all = W1_ALL.copy()
    w1all["in_network"] = w1all["AID"].isin(w1net_aids).astype(int)
    vars_compare = ["BIO_SEX", "AH_RAW", "H1GI4", "H1GI6B", "H1GH1", "PA12", "PA55"]
    rows = []
    for v in vars_compare:
        vv = clean_var(w1all[v], v)
        for group in [0, 1]:
            mask = (w1all["in_network"] == group) & vv.notna()
            m = vv[mask].mean()
            n = mask.sum()
            rows.append({"variable": v, "group": "in_network" if group == 1 else "out_network",
                         "n": int(n), "mean": float(m)})
    return pd.DataFrame(rows)


def _w5_mode_selection() -> Dict:
    import statsmodels.api as sm

    df = (
        W1_ALL[["AID", "BIO_SEX", "AH_RAW"]]
        .merge(W1_NET[["AID", "IDGX2"]], on="AID", how="left")
        .merge(W5_MODE, on="AID", how="inner")
    )
    df["male"] = (df["BIO_SEX"] == 1).astype(float)
    df["ahpvt"] = clean_var(df["AH_RAW"], "AH_RAW")
    df["idgx2"] = clean_var(df["IDGX2"], "IDGX2")
    df = df.dropna(subset=["IS_COG_MODE", "idgx2", "male", "ahpvt"])
    X = sm.add_constant(df[["idgx2", "male", "ahpvt"]])
    y = df["IS_COG_MODE"]
    model = sm.Probit(y, X).fit(disp=False)
    rows = []
    for term in X.columns:
        rows.append({
            "term": term,
            "coef": float(model.params[term]),
            "se": float(model.bse[term]),
            "z": float(model.tvalues[term]),
            "p": float(model.pvalues[term]),
        })
    return {"table": pd.DataFrame(rows), "n": int(len(df)),
            "pseudo_r2": float(model.prsquared)}


def _write_sensitivity_report(path, wu, vif_df, corr, perm, shift, balance, mode_sel):
    L: List[str] = ["# Sensitivity analyses", ""]
    L.append("## 1. Weighted vs unweighted (primary exposures)")
    L.append("")
    L.append("Any sign flip or |t_w/t_u| > 3 is flagged.")
    L.append("")
    L.append(wu.to_markdown(index=False))
    L.append("")

    L.append("## 2. Collinearity among network centrality measures")
    L.append("")
    L.append("Variance-inflation factors:")
    L.append("")
    L.append(vif_df.to_markdown(index=False))
    L.append("")
    L.append("Pairwise Pearson correlations:")
    L.append("")
    L.append(corr.round(3).to_markdown())
    L.append("")

    L.append("## 3. Permutation placebo: IDGX2 within-PSU shuffle (500 reps)")
    L.append("")
    L.append(f"- **Observed β (IDGX2 -> W4_COG_COMP)**: {perm.attrs['observed_beta']:.4f}")
    L.append(f"- **Permutation p-value** (two-sided): {perm.attrs['p_perm']:.3f}")
    L.append(f"- **Permuted null**: mean={perm['beta_permuted'].mean():.4f}, "
             f"SD={perm['beta_permuted'].std():.4f}, "
             f"95%: [{perm['beta_permuted'].quantile(0.025):.4f}, "
             f"{perm['beta_permuted'].quantile(0.975):.4f}]")
    L.append("")

    L.append("## 4. AHPVT bad-control shift")
    L.append("")
    L.append("Percent shrinkage = (β_without − β_with) / β_without. "
             "Values >0.5 are flagged as suggestive of mediation "
             "(AHPVT may be on the causal pathway rather than a confounder).")
    L.append("")
    L.append(shift.to_markdown(index=False))
    L.append("")

    L.append("## 5. Saturated-school selection balance")
    L.append("")
    L.append("Mean of baseline covariates in respondents with vs. without W1 "
             "network data. Large differences imply generalizability caveats.")
    L.append("")
    L.append(balance.pivot(index="variable", columns="group",
                           values=["mean", "n"]).round(3).to_markdown())
    L.append("")

    L.append("## 6. W5 mode-selection probit")
    L.append("")
    L.append("P(cognitive-eligible mode: in-person or phone) ~ IDGX2 + male + AHPVT.")
    L.append(f"N = {mode_sel['n']:,}; pseudo-R² = {mode_sel['pseudo_r2']:.4f}")
    L.append("")
    L.append(mode_sel["table"].to_markdown(index=False))
    L.append("")
    L.append("**Interpretation.** If IDGX2's probit coefficient is near zero, "
             "W5 mode restriction is unlikely to bias the W1→W5 regression on "
             "network position.")
    L.append("")

    path.write_text("\n".join(L))


def run_sensitivity_audit() -> None:
    """Task-11 block: 6 sensitivity audits on the IDGX2 anchor model."""
    print("1. Weighted vs unweighted ...")
    wu = _weighted_vs_unweighted()

    print("2. Collinearity ...")
    vif_df, corr = _collinearity()

    print("3. Permutation placebo (500 reps, may take ~60s) ...")
    perm = _permutation_placebo(n_perm=500)
    perm.to_csv(TABLES_SENSITIVITY / "11_placebo_permutation.csv", index=False)

    print("4. AHPVT bad-control shift ...")
    shift = _ahpvt_shift(TABLES_PRIMARY / "10_regressions.csv")

    print("5. Saturated-school balance ...")
    balance = _saturated_school_balance()

    print("6. W5 mode-selection probit ...")
    mode_sel = _w5_mode_selection()

    vif_df.to_csv(TABLES_SENSITIVITY / "11_collinearity.csv", index=False)
    corr.to_csv(TABLES_SENSITIVITY / "11_correlation.csv")
    shift.to_csv(TABLES_SENSITIVITY / "11_ahpvt_shift.csv", index=False)
    balance.to_csv(TABLES_SENSITIVITY / "11_saturated_balance.csv", index=False)

    _write_sensitivity_report(TABLES_SENSITIVITY / "11_sensitivity.md",
                              wu, vif_df, corr, perm, shift, balance, mode_sel)
    print("Wrote sensitivity outputs.")


# ===========================================================================
# Block 4 — Verification  (was scripts/task13_verification.py)
# ===========================================================================
def run_verification() -> None:
    """Task-13 block: 10-section verification pack on the screening anchor model.

    Reads the baseline regressions CSV (written by run_baseline_regressions)
    for the BH-FDR step, so it must be invoked AFTER baseline regressions.
    """
    np.random.seed(20260419)

    w4 = W4.copy()
    w1full = W1_FULL.copy()

    # Build base covariates on W4
    w4["male"] = (w4["BIO_SEX"] == 1).astype(float)
    for lvl in RACE_LEVELS:
        w4[f"race_{lvl}"] = (w4["RACE"] == lvl).astype(float)
    w4.loc[w4["RACE"].isna(), [f"race_{x}" for x in RACE_LEVELS]] = np.nan
    w4["parent_ed"] = w4["PARENT_ED"]
    w4["cesd_sum"] = w4["CESD_SUM"]
    w4["srh"] = w4["H1GH1"]
    w4["ahpvt"] = w4["AH_RAW"]

    COVARS = ["male", "race_NH-Black", "race_Hispanic", "race_Other",
              "parent_ed", "cesd_sum", "srh", "ahpvt"]

    sections: list[str] = []

    def wmean(x: np.ndarray, w: np.ndarray) -> float:
        m = ~np.isnan(x) & ~np.isnan(w) & (w > 0)
        if m.sum() == 0:
            return float("nan")
        return float(np.sum(w[m] * x[m]) / np.sum(w[m]))

    # 1. Published-benchmark weighted means
    w1w = w1full.dropna(subset=["GSWGT1"]).copy()
    w1w["male"] = (w1w["BIO_SEX"] == 1).astype(float)
    w1w["nhblack"] = (w1w["RACE"] == "NH-Black").astype(float)

    benchmarks = {
        "pct_male": (wmean(w1w["male"].values, w1w["GSWGT1"].values), 0.508),
        "pct_NH_Black": (wmean(w1w["nhblack"].values, w1w["GSWGT1"].values), 0.161),
        "mean_AH_PVT": (wmean(w1w["AH_PVT"].values, w1w["GSWGT1"].values), 100.7),
    }
    net = W1_NET.merge(w1full[["AID", "GSWGT1"]], on="AID", how="left")
    net["IDGX2"] = pd.to_numeric(net["IDGX2"], errors="coerce")
    net.loc[~net["IDGX2"].between(0, 50), "IDGX2"] = np.nan
    benchmarks["mean_IDGX2"] = (
        wmean(net["IDGX2"].values, net["GSWGT1"].values),
        4.6,
    )

    bench_rows = []
    for k, (obs, pub) in benchmarks.items():
        diff = obs - pub
        bench_rows.append({"metric": k, "observed": obs, "published": pub,
                           "abs_diff": abs(diff)})
    bench_df = pd.DataFrame(bench_rows)
    bench_df.to_csv(TABLES_VERIFICATION / "13_benchmarks.csv", index=False)
    sections.append("## 1. Published-benchmark weighted means\n\n"
                    + bench_df.to_markdown(index=False))

    # 2. Reserve-code leakage assertion
    leak_rows = []
    for col in w4.columns:
        if col not in VALID_RANGES:
            continue
        lo, hi = VALID_RANGES[col]
        vals = pd.to_numeric(w4[col], errors="coerce").dropna()
        if vals.empty:
            continue
        vmax, vmin = float(vals.max()), float(vals.min())
        out_of_range = ((vals < lo) | (vals > hi)).sum()
        leak_rows.append({
            "variable": col, "valid_range": f"[{lo}, {hi}]",
            "min": vmin, "max": vmax, "n_out_of_range": int(out_of_range),
        })
    leak_df = pd.DataFrame(leak_rows)
    leak_df.to_csv(TABLES_VERIFICATION / "13_reserve_leakage.csv", index=False)
    n_bad = int((leak_df["n_out_of_range"] > 0).sum())
    sections.append(
        "## 2. Reserve-code leakage assertion\n\n"
        f"- Columns checked: {len(leak_df)}\n"
        f"- Columns with any out-of-valid-range values: **{n_bad}**\n"
        f"- Detailed CSV: `tables/verification/13_reserve_leakage.csv`\n"
    )

    # 3. Reserve-code sensitivity on primary spec
    cesd_cols = [f"H1FS{i}" for i in range(1, 20)]
    reverse = {4, 8, 11, 15}

    def build_cesd(mode: str) -> pd.Series:
        d = W1_ALL[cesd_cols].copy()
        for c in d.columns:
            raw = pd.to_numeric(d[c], errors="coerce")
            valid_mask = raw.between(0, 3)
            item_num = int(c.replace("H1FS", ""))
            scored = raw.where(valid_mask)
            if item_num in reverse:
                scored = 3 - scored
            if mode == "na":
                out = scored
            elif mode == "zero":
                out = scored.fillna(0)
            elif mode == "category":
                out = scored.where(valid_mask, -1)
            d[c] = out
        return d.sum(axis=1, min_count=len(cesd_cols) if mode == "na" else 1)

    primary_rows = []
    for mode in ["na", "zero", "category"]:
        w4m = w4.copy()
        aid_to_cesd = pd.Series(build_cesd(mode).values, index=W1_ALL["AID"])
        w4m["cesd_sum"] = w4m["AID"].map(aid_to_cesd)

        keep = ["IDGX2", "W4_COG_COMP", "GSWGT4_2", "CLUSTER2"] + COVARS
        d = w4m.dropna(subset=keep).copy()
        Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
        Xdf["IDGX2"] = d["IDGX2"].values
        for c in COVARS:
            Xdf[c] = d[c].values
        names = ["const", "IDGX2"] + COVARS
        y = d["W4_COG_COMP"].astype(float).values
        wt = d["GSWGT4_2"].astype(float).values
        psu = d["CLUSTER2"].astype(int).values
        res = weighted_ols(y, Xdf.values, wt, psu, names)
        primary_rows.append({
            "cesd_reserve_mode": mode,
            "beta_idgx2": float(res["beta"]["IDGX2"]),
            "se": float(res["se"]["IDGX2"]),
            "p": float(res["p"]["IDGX2"]),
            "n": int(res["n"]),
        })
    primary_df = pd.DataFrame(primary_rows)
    primary_df.to_csv(TABLES_VERIFICATION / "13_reserve_code_sensitivity.csv", index=False)
    sections.append("## 3. Reserve-code sensitivity (CES-D handling)\n\n"
                    + primary_df.to_markdown(index=False))

    # 4. DEFF and cluster-SE / naive-SE ratio
    import statsmodels.api as sm

    keep = ["IDGX2", "W4_COG_COMP", "GSWGT4_2", "CLUSTER2"] + COVARS
    d = w4.dropna(subset=keep).copy()
    Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
    Xdf["IDGX2"] = d["IDGX2"].values
    for c in COVARS:
        Xdf[c] = d[c].values
    X = Xdf.values
    y = d["W4_COG_COMP"].astype(float).values
    wt = d["GSWGT4_2"].astype(float).values
    psu = d["CLUSTER2"].astype(int).values

    wls = sm.WLS(y, X, weights=wt).fit()
    naive_se = wls.bse[1]
    cluster = sm.WLS(y, X, weights=wt).fit(
        cov_type="cluster", cov_kwds={"groups": psu, "use_correction": True}, use_t=True,
    )
    cluster_se = cluster.bse[1]
    se_ratio = cluster_se / naive_se
    deff_primary = se_ratio ** 2

    deff_row = pd.DataFrame([{
        "spec": "S01C IDGX2 -> W4_COG_COMP",
        "naive_se": naive_se,
        "cluster_se": cluster_se,
        "se_ratio": se_ratio,
        "deff_proxy": deff_primary,
    }])
    deff_row.to_csv(TABLES_VERIFICATION / "13_deff.csv", index=False)
    sections.append("## 4. DEFF and cluster-SE / naive-SE ratio (primary spec)\n\n"
                    + deff_row.to_markdown(index=False))

    # 5. Negative-control OUTCOME: adult height at W4
    height = W4_HOME[["AID", "H4GH5F", "H4GH5I"]].copy()
    height["H4GH5F"] = pd.to_numeric(height["H4GH5F"], errors="coerce").where(lambda s: s.between(4, 7))
    height["H4GH5I"] = pd.to_numeric(height["H4GH5I"], errors="coerce").where(lambda s: s.between(0, 11))
    height["HEIGHT_IN"] = height["H4GH5F"] * 12 + height["H4GH5I"]
    w4h = w4.merge(height[["AID", "HEIGHT_IN"]], on="AID", how="left")

    keep_h = ["IDGX2", "HEIGHT_IN", "GSWGT4_2", "CLUSTER2"] + COVARS
    d = w4h.dropna(subset=keep_h).copy()
    Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
    Xdf["IDGX2"] = d["IDGX2"].values
    for c in COVARS:
        Xdf[c] = d[c].values
    X = Xdf.values
    y = d["HEIGHT_IN"].astype(float).values
    wt = d["GSWGT4_2"].astype(float).values
    psu = d["CLUSTER2"].astype(int).values
    names = ["const", "IDGX2"] + COVARS
    nco = weighted_ols(y, X, wt, psu, names)
    nco_row = pd.DataFrame([{
        "outcome": "HEIGHT_IN",
        "beta_idgx2": float(nco["beta"]["IDGX2"]),
        "se": float(nco["se"]["IDGX2"]),
        "p": float(nco["p"]["IDGX2"]),
        "n": int(nco["n"]),
    }])
    nco_row.to_csv(TABLES_VERIFICATION / "13_negctrl_outcome.csv", index=False)
    sections.append(
        "## 5. Negative-control OUTCOME: adult height (inches)\n\n"
        "IDGX2 should not predict adult height if our adjustment set is adequate.\n\n"
        + nco_row.to_markdown(index=False)
    )

    # 6. Negative-control EXPOSURE: American-Indian indicator (H1GI6C)
    ai = W1_ALL[["AID", "H1GI6C"]].copy()
    ai["H1GI6C"] = pd.to_numeric(ai["H1GI6C"], errors="coerce").where(lambda s: s.isin([0, 1]))
    w4a = w4.merge(ai, on="AID", how="left")
    keep_a = ["H1GI6C", "W4_COG_COMP", "GSWGT4_2", "CLUSTER2"] + COVARS
    d = w4a.dropna(subset=keep_a).copy()
    Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
    Xdf["AI"] = d["H1GI6C"].values
    for c in COVARS:
        Xdf[c] = d[c].values
    X = Xdf.values
    y = d["W4_COG_COMP"].astype(float).values
    wt = d["GSWGT4_2"].astype(float).values
    psu = d["CLUSTER2"].astype(int).values
    names = ["const", "AI"] + COVARS
    nce = weighted_ols(y, X, wt, psu, names)
    nce_row = pd.DataFrame([{
        "exposure": "H1GI6C (AI/AN)",
        "beta": float(nce["beta"]["AI"]),
        "se": float(nce["se"]["AI"]),
        "p": float(nce["p"]["AI"]),
        "n": int(nce["n"]),
    }])
    nce_row.to_csv(TABLES_VERIFICATION / "13_negctrl_exposure.csv", index=False)
    sections.append(
        "## 6. Negative-control EXPOSURE: American-Indian indicator (H1GI6C)\n\n"
        "A baseline indicator with no theoretical link to cognitive outcomes — should be null under adjustment.\n\n"
        + nce_row.to_markdown(index=False)
    )

    # 7. Attrition-IPW re-fit of anchor model
    # Live refit of the primary anchor (IDGX2 -> W4_COG_COMP, _adj_full,
    # GSWGT4_2) so the comparison row reflects the current data, not a
    # frozen snapshot from a previous run.
    keep_primary = ["IDGX2", "W4_COG_COMP", "GSWGT4_2", "CLUSTER2"] + COVARS
    d_primary = w4.dropna(subset=keep_primary).copy()
    Xdf_p = pd.DataFrame({"const": 1.0}, index=d_primary.index)
    Xdf_p["IDGX2"] = d_primary["IDGX2"].values
    for c in COVARS:
        Xdf_p[c] = d_primary[c].values
    primary_res = weighted_ols(
        d_primary["W4_COG_COMP"].astype(float).values,
        Xdf_p.values,
        d_primary["GSWGT4_2"].astype(float).values,
        d_primary["CLUSTER2"].astype(int).values,
        ["const", "IDGX2"] + COVARS,
    )

    w1net2 = W1_NET[["AID", "IDGX2"]].copy()
    w1net2["IDGX2"] = pd.to_numeric(w1net2["IDGX2"], errors="coerce").where(lambda s: s.between(0, 50))
    w1net2 = w1net2.dropna(subset=["IDGX2"])

    base = W1_ALL[["AID", "BIO_SEX", "H1GH1"]].copy()
    base["AH_RAW"] = pd.to_numeric(W1_ALL.get("AH_PVT"), errors="coerce").where(lambda s: s.between(0, 200))
    base["BIO_SEX"] = pd.to_numeric(base["BIO_SEX"], errors="coerce").where(lambda s: s.between(1, 2))
    base["H1GH1"] = pd.to_numeric(base["H1GH1"], errors="coerce").where(lambda s: s.between(1, 5))

    w1race = W1_ALL[["AID", "H1GI4", "H1GI6A", "H1GI6B", "H1GI6C", "H1GI6D", "H1GI6E",
                     "H1RM1", "H1RF1"]].copy()
    w1race["PARENT_ED"] = derive_parent_ed(w1race)
    w1race["RACE"] = derive_race_ethnicity(w1race)

    cesd = build_cesd("na")
    cesd.name = "CESD_SUM"
    cesd.index = W1_ALL["AID"].values

    base = base.merge(w1race[["AID", "RACE", "PARENT_ED"]], on="AID", how="left")
    base = base.merge(cesd.rename("CESD_SUM").reset_index().rename(columns={"index": "AID"}),
                      on="AID", how="left")

    base = base.merge(w1full[["AID", "GSWGT1"]].drop_duplicates("AID"), on="AID", how="left")

    u = w1net2.merge(base, on="AID", how="left").dropna(
        subset=["BIO_SEX", "AH_RAW", "RACE", "PARENT_ED", "CESD_SUM", "H1GH1", "GSWGT1"]
    )
    u["male"] = (u["BIO_SEX"] == 1).astype(float)
    for lvl in RACE_LEVELS:
        u[f"race_{lvl}"] = (u["RACE"] == lvl).astype(float)
    u["parent_ed"] = u["PARENT_ED"]
    u["cesd_sum"] = u["CESD_SUM"]
    u["srh"] = u["H1GH1"]
    u["ahpvt"] = u["AH_RAW"]
    resp_set = set(w4.loc[w4["W4_COG_COMP"].notna(), "AID"].astype(str))
    u["responded"] = u["AID"].astype(str).isin(resp_set).astype(int)

    logit_cols = ["male", "race_NH-Black", "race_Hispanic", "race_Other",
                  "parent_ed", "cesd_sum", "srh", "ahpvt", "IDGX2"]
    Xl = sm.add_constant(u[logit_cols].values)
    try:
        logit = sm.Logit(u["responded"].values, Xl).fit(disp=0, maxiter=100)
        phat = logit.predict(Xl)
        u["ipw"] = 1.0 / np.clip(phat, 0.05, 1.0)
    except Exception as e:
        print(f"[warn] logit failed: {e}")
        u["ipw"] = 1.0
        logit = None

    ipw_map = u.set_index("AID")["ipw"]
    w4i = w4.merge(ipw_map.rename("ATTR_IPW"), left_on="AID", right_index=True, how="left")
    w4i["IPW_SW"] = w4i["GSWGT4_2"] * w4i["ATTR_IPW"]

    keep = ["IDGX2", "W4_COG_COMP", "IPW_SW", "CLUSTER2"] + COVARS
    d = w4i.dropna(subset=keep).copy()
    Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
    Xdf["IDGX2"] = d["IDGX2"].values
    for c in COVARS:
        Xdf[c] = d[c].values
    X = Xdf.values
    y = d["W4_COG_COMP"].astype(float).values
    wt = d["IPW_SW"].astype(float).values
    psu = d["CLUSTER2"].astype(int).values
    names = ["const", "IDGX2"] + COVARS
    ipw_res = weighted_ols(y, X, wt, psu, names)
    ipw_rows = pd.DataFrame([
        {"spec": "Primary (GSWGT4_2 only)",
         "beta_idgx2": float(primary_res["beta"]["IDGX2"]),
         "p": float(primary_res["p"]["IDGX2"]),
         "n": int(primary_res["n"])},
        {"spec": "With attrition IPW",
         "beta_idgx2": float(ipw_res["beta"]["IDGX2"]),
         "p": float(ipw_res["p"]["IDGX2"]),
         "n": int(ipw_res["n"])},
    ])
    ipw_rows.to_csv(TABLES_VERIFICATION / "13_attrition_ipw.csv", index=False)
    if logit is not None:
        sections.append(
            "## 7. Attrition IPW re-fit of anchor model (S01C)\n\n"
            f"Stage-1 logit pseudo-R² = {logit.prsquared:.4f}, N = {int(logit.nobs)}.\n\n"
            + ipw_rows.to_markdown(index=False)
        )
    else:
        sections.append(
            "## 7. Attrition IPW re-fit of anchor model (S01C)\n\n"
            "Stage-1 logit failed; IPW set to 1.\n\n"
            + ipw_rows.to_markdown(index=False)
        )

    # 8. BH-FDR multiple testing adjustment (reads baseline regressions output)
    coefs = pd.read_csv(TABLES_PRIMARY / "10_regressions.csv")
    FAMILY = [
        ("S01", "idgx2"),
        ("S01C", "idgx2"),
        ("S04_ODGX2_placebo", "odgx2_placebo"),
        ("S04_BCENT10X", "bcent10x"),
        ("S04_REACH", "reach"),
        ("S04_PRXPREST", "prxprest"),
        ("S05_ZERO", "idg_zero"),
        ("S05_LEQ1", "idg_leq1"),
        ("S06", "school_belong"),
        ("S07", "lonely"),
        ("S10_nominees", "friend_n"),
        ("S10_contact", "friend_contact"),
        ("S10_disclose", "friend_disclose"),
    ]
    fam = []
    for spec, term in FAMILY:
        r = coefs[(coefs.spec_id == spec) & (coefs.term == term)].iloc[0]
        fam.append({"spec": spec, "term": term, "beta": r.beta, "p": r.p})
    fam = pd.DataFrame(fam).sort_values("p").reset_index(drop=True)
    m = len(fam)
    fam["rank"] = np.arange(1, m + 1)
    fam["bh_threshold"] = 0.05 * fam["rank"] / m
    p_sorted = fam["p"].values
    q = np.empty(m)
    running_min = 1.0
    for j in range(m - 1, -1, -1):
        running_min = min(running_min, p_sorted[j] * m / (j + 1))
        q[j] = running_min
    fam["q_BH"] = q
    fam["reject_at_q0.05"] = fam["q_BH"] < 0.05
    fam.to_csv(TABLES_VERIFICATION / "13_bh_fdr.csv", index=False)
    sections.append("## 8. BH-FDR multiple-testing adjustment (primary family)\n\n"
                    + fam.to_markdown(index=False))

    # 9. Weight sums + PSU counts
    psu_counts = {
        "W1 (all analytic_w1_full)": (w1full["CLUSTER2"].nunique(), w1full.shape[0]),
        "W4 analytic": (w4["CLUSTER2"].nunique(), w4.shape[0]),
        "W4 with valid cognitive": (
            w4.dropna(subset=["C4WD90_1"])["CLUSTER2"].nunique(),
            w4.dropna(subset=["C4WD90_1"]).shape[0]),
    }
    psu_counts["W5 analytic (I/T modes)"] = (W5_FULL["CLUSTER2"].nunique(), W5_FULL.shape[0])

    w_sum_w4 = float(w4["GSWGT4_2"].dropna().sum())
    w_sum_w1 = float(w1full["GSWGT1"].dropna().sum())
    psu_rows = [{"frame": k, "n_psu": v[0], "n_rows": v[1]} for k, v in psu_counts.items()]
    psu_df = pd.DataFrame(psu_rows)
    psu_df.to_csv(TABLES_VERIFICATION / "13_psu_counts.csv", index=False)
    sections.append(
        "## 9. Weight sums and PSU counts\n\n"
        f"- Sum(GSWGT1) across W1 analytic = **{w_sum_w1:,.0f}**\n"
        f"- Sum(GSWGT4_2) across W4 analytic = **{w_sum_w4:,.0f}**\n\n"
        + psu_df.to_markdown(index=False)
    )

    # 10. CLUSTER2 missingness assertion
    miss = {
        "W1 full": int(w1full["CLUSTER2"].isna().sum()),
        "W4": int(w4["CLUSTER2"].isna().sum()),
        "W5": int(W5_FULL["CLUSTER2"].isna().sum()),
    }
    sections.append(
        "## 10. CLUSTER2 missingness assertion\n\n"
        + "\n".join(f"- {k}: **{v}** rows missing CLUSTER2" for k, v in miss.items())
    )

    md = "# Verification pass\n\n" + "\n\n".join(sections) + "\n"
    (TABLES_VERIFICATION / "13_verification.md").write_text(md)
    print(f"Wrote {TABLES_VERIFICATION / '13_verification.md'}")


# ===========================================================================
# Entry point
# ===========================================================================
def main() -> None:
    run_baseline_regressions()
    run_causal_screening()
    run_sensitivity_audit()
    run_verification()


if __name__ == "__main__":
    main()

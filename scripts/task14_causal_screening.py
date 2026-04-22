"""Task 14 - Preliminary causal screening of candidate social-exposure treatments.

Screens each candidate W1 adolescent-social exposure against a battery of
falsification / plausibility diagnostics (D1-D9) to produce a ranked shortlist
for formal causal estimation. All diagnostics reuse weighted_ols with cluster-
robust SEs on CLUSTER2 and GSWGT4_2 survey weights.

Diagnostics:
  D1 Baseline association on W4_COG_COMP (primary spec = AHPVT-adjusted).
  D2 Negative-control outcome HEIGHT_IN (should be null under good adjustment).
  D3 Sibling-exposure dissociation (treatment vs placebo sibling).
  D4 Adjustment-set stability across L0, L0+L1, L0+L1+AHPVT.
  D5 Outcome-component consistency (C4WD90_1, C4WD60_1, C4NUMSCR).
  D6 Dose-response monotonicity (quintile trend; continuous only).
  D7 Positivity / overlap (Q5 vs Q1 logit).
  D8 Saturated-school selection loss (informational; network-only exposures).
  D9 Collider / double-adjustment red flag (hard-coded lookup).

Outputs:
  outputs/14_screening_matrix.csv - full exposure x diagnostic table
  outputs/14_shortlist.csv        - ranked shortlist with category + score
  outputs/14_screening.md         - narrative report
  img/causal/screening_heatmap.png
  img/causal/negctrl_failure_grid.png
  img/causal/sibling_dissociation.png
  img/causal/adjustment_stability.png
  img/causal/component_consistency.png
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from analysis_utils import (  # noqa: E402
    ROOT, CACHE, clean_var, weighted_ols, neg_control_outcome, quintile_dummies,
)
import plot_style  # noqa: E402

OUT = ROOT / "outputs"
IMG = ROOT / "img" / "causal"
IMG.mkdir(parents=True, exist_ok=True)

W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
W1_FULL = pd.read_parquet(CACHE / "analytic_w1_full.parquet")

# Attach H1PR4 from raw W1 in-home (not in cache frame).
_w1raw = pd.read_parquet(CACHE / "w1inhome.parquet")[["AID", "H1PR4"]]
_w1raw["H1PR4"] = pd.to_numeric(_w1raw["H1PR4"], errors="coerce").where(
    lambda s: s.between(1, 5)
)
W4 = W4.merge(_w1raw, on="AID", how="left")
W1_FULL = W1_FULL.merge(_w1raw, on="AID", how="left")

# HEIGHT_IN (negative-control outcome) attached to W4 / W1_FULL.
W4["HEIGHT_IN"] = neg_control_outcome(W4["AID"])
W1_FULL["HEIGHT_IN"] = neg_control_outcome(W1_FULL["AID"])

# Derived H1FS13/H1FS14 are already in the cache frames.


# ---------------------------------------------------------------------------
# Candidate exposure specification
# ---------------------------------------------------------------------------
NETWORK_EXPOSURES = {
    # name: (column_in_W4, group, kind)
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
    "H1FS13":                ("H1FS13",                "loneliness",      "continuous"),
    "H1FS14":                ("H1FS14",                "loneliness",      "continuous"),
    "H1DA7":                 ("H1DA7",                 "qualitative",     "continuous"),
    "H1PR4":                 ("H1PR4",                 "qualitative",     "continuous"),
}

# Exposure -> (frame_key, column, group, kind, requires_saturation)
EXPOSURES: Dict[str, Tuple[str, str, str, str, bool]] = {}
for name, (col, group, kind) in NETWORK_EXPOSURES.items():
    EXPOSURES[name] = ("W4", col, group, kind, True)
for name, (col, group, kind) in SURVEY_EXPOSURES.items():
    # Survey exposures use W1_FULL (no network gate) so the D1 sample is larger.
    EXPOSURES[name] = ("W1_FULL", col, group, kind, False)

# Hard-coded D9 red flags (double-adjustment / collider risks).
RED_FLAGS: Dict[str, str] = {
    "H1FS13": "CES-D item; contained in CESD_SUM covariate -> double-adjustment",
    "H1FS14": "CES-D item; contained in CESD_SUM covariate -> double-adjustment",
    "SCHOOL_BELONG": "Mixes individual disposition with school-level context; possible collider given W1 CESD/SRH",
}

# Sibling pairs for D3.
SIBLINGS: Dict[str, str] = {
    "IDGX2": "ODGX2",
    "BCENT10X": "ODGX2",
    "FRIEND_DISCLOSURE_ANY": "FRIEND_N_NOMINEES",
    "HAVEBMF": "HAVEBFF",
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


def _adj_L0(df: pd.DataFrame) -> pd.DataFrame:
    """Demographics only."""
    return pd.concat([
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index),
        _race_dummies(df),
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


# ---------------------------------------------------------------------------
# Fitting primitives
# ---------------------------------------------------------------------------
def _fit(df: pd.DataFrame, exposure_col: str, y_col: str,
         adj_builder: Callable[[pd.DataFrame], pd.DataFrame],
         w_col: str = "GSWGT4_2",
         drop_rows_for_exposure: bool = True) -> Optional[dict]:
    """Weighted OLS of y ~ exposure + adj, cluster-robust on CLUSTER2."""
    # Exposure gets cleaned against VALID_RANGES where applicable.
    exp = clean_var(df[exposure_col], exposure_col)
    adj = adj_builder(df)
    X = pd.concat([exp.rename("exposure"), adj], axis=1)
    X.insert(0, "const", 1.0)
    y = df[y_col].values
    w = df[w_col].values
    psu = df["CLUSTER2"].values
    res = weighted_ols(y, X.values, w, psu, column_names=list(X.columns))
    return res


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


# ---------------------------------------------------------------------------
# Diagnostic computations
# ---------------------------------------------------------------------------
def d1_baseline(df: pd.DataFrame, col: str) -> dict:
    """Primary spec: W4_COG_COMP ~ exposure + L0+L1+AHPVT."""
    res = _fit(df, col, "W4_COG_COMP", _adj_full)
    if res is None:
        return {"beta": np.nan, "se": np.nan, "p": np.nan, "n": 0, "pass": False}
    b = float(res["beta"]["exposure"])
    p = float(res["p"]["exposure"])
    return {
        "beta": b, "se": float(res["se"]["exposure"]),
        "p": p, "n": int(res["n"]),
        "pass": bool(p < 0.05),
    }


def d2_negctrl(df: pd.DataFrame, col: str) -> dict:
    """HEIGHT_IN ~ exposure + L0+L1+AHPVT. Pass iff p > 0.10."""
    res = _fit(df, col, "HEIGHT_IN", _adj_full)
    if res is None:
        return {"beta": np.nan, "se": np.nan, "p": np.nan, "n": 0, "pass": False}
    b = float(res["beta"]["exposure"])
    p = float(res["p"]["exposure"])
    return {
        "beta": b, "se": float(res["se"]["exposure"]),
        "p": p, "n": int(res["n"]),
        "pass": bool(p > 0.10),
    }


def d3_sibling(df: pd.DataFrame, col: str, sibling_col: str) -> dict:
    """Compare |beta_exposure| vs |beta_sibling| on W4_COG_COMP (primary spec).

    Pass iff |beta_exposure| > |beta_sibling| AND |beta_exposure - beta_sibling|
    exceeds 1 pooled SE.
    """
    res_t = _fit(df, col, "W4_COG_COMP", _adj_full)
    res_s = _fit(df, sibling_col, "W4_COG_COMP", _adj_full)
    if res_t is None or res_s is None:
        return {
            "sibling": sibling_col, "beta_sibling": np.nan,
            "p_sibling": np.nan, "delta": np.nan, "se_pooled": np.nan,
            "pass": False,
        }
    b_t = float(res_t["beta"]["exposure"])
    b_s = float(res_s["beta"]["exposure"])
    se_t = float(res_t["se"]["exposure"])
    se_s = float(res_s["se"]["exposure"])
    se_pooled = float(np.sqrt(se_t ** 2 + se_s ** 2))
    delta = abs(b_t) - abs(b_s)
    same_sign = (np.sign(b_t) == np.sign(b_s)) and (b_t != 0) and (b_s != 0)
    passes = (abs(b_t) > abs(b_s)) and (abs(b_t - b_s) > se_pooled) and same_sign
    return {
        "sibling": sibling_col, "beta_sibling": b_s,
        "p_sibling": float(res_s["p"]["exposure"]),
        "delta_abs_beta": delta, "se_pooled": se_pooled,
        "pass": bool(passes),
    }


def d4_adj_stability(df: pd.DataFrame, col: str) -> dict:
    """Fit primary spec under L0, L0+L1, L0+L1+AHPVT. Report relative shift."""
    betas = {}
    for name, builder in ADJ_BUILDERS.items():
        res = _fit(df, col, "W4_COG_COMP", builder)
        betas[name] = float(res["beta"]["exposure"]) if res else np.nan
    b0 = betas["L0"]
    bf = betas["L0+L1+AHPVT"]
    ref = abs(bf) if not np.isnan(bf) and abs(bf) > 1e-10 else (
        abs(b0) if not np.isnan(b0) else np.nan
    )
    vals = [v for v in betas.values() if not np.isnan(v)]
    max_shift = (max(vals) - min(vals)) if len(vals) >= 2 else np.nan
    rel_shift = abs(max_shift) / ref if ref and ref > 0 else np.nan
    sign_stable = (
        len(vals) >= 2 and (all(v > 0 for v in vals) or all(v < 0 for v in vals))
    )
    passes = (not np.isnan(rel_shift)) and (rel_shift < 0.30) and sign_stable
    return {
        "beta_L0": betas["L0"], "beta_L0_L1": betas["L0+L1"],
        "beta_L0_L1_AHPVT": betas["L0+L1+AHPVT"],
        "rel_shift": rel_shift, "sign_stable": sign_stable,
        "pass": bool(passes),
    }


def d5_component_consistency(df: pd.DataFrame, col: str) -> dict:
    """Fit the primary spec against each W4 cognitive component.

    Pass iff signs are consistent across all three AND at least 2/3 have p<0.10.
    """
    results = {}
    for y in ["C4WD90_1", "C4WD60_1", "C4NUMSCR"]:
        res = _fit(df, col, y, _adj_full)
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
    return {
        "beta_c4wd90": results["C4WD90_1"]["beta"],
        "beta_c4wd60": results["C4WD60_1"]["beta"],
        "beta_c4numscr": results["C4NUMSCR"]["beta"],
        "p_c4wd90": results["C4WD90_1"]["p"],
        "p_c4wd60": results["C4WD60_1"]["p"],
        "p_c4numscr": results["C4NUMSCR"]["p"],
        "sign_consistent": sign_consistent, "n_sig_p10": int(n_sig),
        "pass": bool(passes),
    }


def d6_dose_response(df: pd.DataFrame, col: str, kind: str) -> dict:
    """Quintile dose-response. NA for binary exposures."""
    if kind == "binary":
        return {"trend_rho": np.nan, "monotone_sign": None, "pass": None}
    res, trend = _fit_quintiles(df, col, "W4_COG_COMP", _adj_full)
    if res is None:
        return {"trend_rho": np.nan, "monotone_sign": None, "pass": False}
    q_terms = [f"q{k}" for k in range(2, 6) if f"q{k}" in res["beta"].index]
    # Use Q-index (2,3,4,5) and beta to compute Spearman
    q_vals = np.array([int(t[1:]) for t in q_terms], dtype=float)
    b_vals = np.array([float(res["beta"][t]) for t in q_terms])
    # Spearman on (q_index, beta). With just 4 points this is discrete but OK.
    ranks_q = pd.Series(q_vals).rank().values
    ranks_b = pd.Series(b_vals).rank().values
    rho = float(np.corrcoef(ranks_q, ranks_b)[0, 1]) if len(q_vals) >= 2 else np.nan
    # Monotone sign: all same-sign for b_vals
    monotone_sign = (
        all(b > 0 for b in b_vals) or all(b < 0 for b in b_vals)
    ) if len(b_vals) >= 2 else None
    passes = (not np.isnan(rho)) and (abs(rho) > 0.7) and bool(monotone_sign)
    return {
        "trend_rho": rho, "monotone_sign": bool(monotone_sign),
        "betas_q2_q5": b_vals.tolist(),
        "pass": bool(passes),
    }


def d7_overlap(df: pd.DataFrame, col: str, kind: str) -> dict:
    """Logit of Q5 vs Q1 on L0+L1+AHPVT. Pass iff pmin >= 0.02 and pmax <= 0.98."""
    import statsmodels.api as sm
    if kind == "binary":
        # For binary exposure, overlap is just P(A=1) balance on adj set.
        exp = clean_var(df[col], col)
        adj = _adj_full(df)
        mask = exp.notna() & adj.notna().all(axis=1)
        if mask.sum() < 50 or len(exp[mask].unique()) < 2:
            return {
                "overlap_min_p": np.nan, "overlap_max_p": np.nan,
                "eff_n": int(mask.sum()), "pass": False,
            }
        X = sm.add_constant(adj[mask])
        try:
            m = sm.Logit(exp[mask].astype(int), X).fit(disp=False)
            p_hat = m.predict(X)
        except Exception:
            return {
                "overlap_min_p": np.nan, "overlap_max_p": np.nan,
                "eff_n": int(mask.sum()), "pass": False,
            }
    else:
        exp = clean_var(df[col], col)
        _, trend = quintile_dummies(exp, n=5)
        sub_mask = trend.isin([1.0, 5.0])
        if sub_mask.sum() < 50:
            return {
                "overlap_min_p": np.nan, "overlap_max_p": np.nan,
                "eff_n": int(sub_mask.sum()), "pass": False,
            }
        sub = df[sub_mask].copy()
        sub["A"] = (trend[sub_mask] == 5.0).astype(int)
        adj = _adj_full(sub)
        mask = adj.notna().all(axis=1) & sub["A"].notna()
        if mask.sum() < 50:
            return {
                "overlap_min_p": np.nan, "overlap_max_p": np.nan,
                "eff_n": int(mask.sum()), "pass": False,
            }
        X = sm.add_constant(adj[mask])
        try:
            m = sm.Logit(sub.loc[mask, "A"].astype(int), X).fit(disp=False)
            p_hat = m.predict(X)
        except Exception:
            return {
                "overlap_min_p": np.nan, "overlap_max_p": np.nan,
                "eff_n": int(mask.sum()), "pass": False,
            }
    pmin = float(p_hat.min())
    pmax = float(p_hat.max())
    # Effective N after trimming (keep only 0.05 <= p <= 0.95).
    eff_n = int(((p_hat >= 0.05) & (p_hat <= 0.95)).sum())
    passes = (pmin >= 0.02) and (pmax <= 0.98) and (eff_n >= 500)
    return {
        "overlap_min_p": pmin, "overlap_max_p": pmax,
        "eff_n": eff_n, "pass": bool(passes),
    }


def d8_saturation(requires_sat: bool) -> dict:
    frac = 0.324 if requires_sat else 0.0
    return {"saturated_loss_frac": frac, "flag": bool(requires_sat and frac > 0.25)}


def d9_red_flag(name: str) -> dict:
    msg = RED_FLAGS.get(name, "")
    return {"red_flag": bool(msg), "red_flag_msg": msg}


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
def screen_all() -> pd.DataFrame:
    rows: List[dict] = []
    for name, (frame_key, col, group, kind, req_sat) in EXPOSURES.items():
        df = W4 if frame_key == "W4" else W1_FULL
        row = {"exposure": name, "group": group, "kind": kind,
               "frame": frame_key}
        d1 = d1_baseline(df, col)
        d2 = d2_negctrl(df, col)
        d4 = d4_adj_stability(df, col)
        d5 = d5_component_consistency(df, col)
        d6 = d6_dose_response(df, col, kind)
        d7 = d7_overlap(df, col, kind)
        d8 = d8_saturation(req_sat)
        d9 = d9_red_flag(name)
        # D3 requires a sibling; NA otherwise.
        sibling = SIBLINGS.get(name)
        if sibling:
            # Sibling uses the same frame.
            sib_col = EXPOSURES[sibling][1] if sibling in EXPOSURES else sibling
            d3 = d3_sibling(df, col, sib_col)
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


# ---------------------------------------------------------------------------
# Scoring / classification
# ---------------------------------------------------------------------------
def classify(df: pd.DataFrame) -> pd.DataFrame:
    def _row(r: pd.Series) -> Tuple[str, int, str]:
        # Convert pass bits (None -> NA; else bool).
        d1 = r["d1_pass"]
        d2 = r["d2_pass"]
        d3 = r["d3_pass"]  # None if NA
        d4 = r["d4_pass"]
        d5 = r["d5_pass"]
        d6 = r["d6_pass"]  # None for binary
        d7 = r["d7_pass"]
        red = r["d9_red_flag"]

        passes = [d1, d2, d4, d5, d7]
        if d3 is not None and not (isinstance(d3, float) and pd.isna(d3)):
            passes.append(d3)
        if d6 is not None and not (isinstance(d6, float) and pd.isna(d6)):
            passes.append(d6)
        score = int(sum(bool(p) for p in passes))
        # Weighted tiebreaker count: D2, D3 (if applicable), D4 double-weighted.
        wscore = score
        for w in (d2, d4):
            if w:
                wscore += 1
        if d3 is True:
            wscore += 1

        notes = []
        # Drop: outright failure on negative-control or sibling.
        if d2 is False and r["d2_p"] < 0.05:
            notes.append("D2 fails hard (p<0.05)")
            cat = "Drop"
        elif (d3 is False) and (r["d3_delta_abs_beta"] is not None) \
                and (not pd.isna(r["d3_delta_abs_beta"])) \
                and (r["d3_delta_abs_beta"] < 0):
            notes.append("D3 fails: sibling stronger")
            cat = "Drop"
        # Weakened: D1 fails or red flag.
        elif not d1:
            notes.append("D1 association null (p>=0.05)")
            cat = "Weakened"
        elif red:
            notes.append(f"D9 red flag: {r['d9_red_flag_msg']}")
            cat = "Weakened"
        # Promising: pass D1, D2, D4 and (D3 pass or NA), no red flag.
        elif d1 and d2 and d4 and (d3 is True or d3 is None or
                                    (isinstance(d3, float) and pd.isna(d3))):
            cat = "Promising"
        # Mixed: D1 passes but at least one of D2/D3/D4 fails (and not hard fail).
        else:
            cat = "Mixed"
            fails = []
            if not d2:
                fails.append("D2 weakly fails (p<=0.10)")
            if d3 is False:
                fails.append("D3 fails (sibling not dissociated)")
            if not d4:
                fails.append("D4 unstable across adjustment sets")
            notes.append(", ".join(fails))
        # Cap: saturation >50% loss -> at best "Promising w/ sat caveat"
        # (not used here; 32% < 50%).
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


# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------
def plot_figures(results: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    plot_style.setup()

    # 1. Screening heatmap.
    diag_cols = [
        ("D1 baseline", "d1_pass"),
        ("D2 neg-ctrl", "d2_pass"),
        ("D3 sibling", "d3_pass"),
        ("D4 adj-stable", "d4_pass"),
        ("D5 components", "d5_pass"),
        ("D6 dose-resp", "d6_pass"),
        ("D7 overlap", "d7_pass"),
        ("D9 red flag", "d9_red_flag"),
    ]
    labels = [l for l, _ in diag_cols]
    M = np.full((len(results), len(diag_cols)), np.nan)
    for i, (_, r) in enumerate(results.iterrows()):
        for j, (_, c) in enumerate(diag_cols):
            v = r[c]
            if c == "d9_red_flag":
                M[i, j] = 0.0 if bool(v) else 1.0  # Flip: red flag = "bad"
            else:
                if v is None or (isinstance(v, float) and pd.isna(v)):
                    M[i, j] = np.nan
                else:
                    M[i, j] = 1.0 if bool(v) else 0.0
    fig, ax = plt.subplots(figsize=(9, max(4, 0.35 * len(results))))
    cmap = mcolors.ListedColormap(["#e15759", "#59a14f"])
    cmap.set_bad(color="#d0d0d0")
    im = ax.imshow(np.ma.masked_invalid(M), cmap=cmap, vmin=0, vmax=1,
                   aspect="auto")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right")
    ax.set_yticks(range(len(results)))
    ax.set_yticklabels([f"{r.exposure}  ({r.group})"
                        for _, r in results.iterrows()])
    ax.set_title("Screening diagnostics: green=pass, red=fail, grey=NA")
    # Overlay pass-count badges.
    for i, (_, r) in enumerate(results.iterrows()):
        ax.text(len(labels) - 0.5 + 0.8, i,
                f"{r.category} ({r.score})",
                va="center", ha="left", fontsize=8)
    ax.set_xlim(-0.5, len(labels) + 2.0)
    plot_style.save(fig, "causal/screening_heatmap.png")

    # 2. Negative-control failure grid.
    fig, ax = plt.subplots(figsize=(7, max(4, 0.28 * len(results))))
    order = results.sort_values("d2_beta", key=lambda s: s.abs(),
                                ascending=False)
    ys = np.arange(len(order))
    for i, (_, r) in enumerate(order.iterrows()):
        b, se, pv = r["d2_beta"], r["d2_se"], r["d2_p"]
        if np.isnan(b):
            continue
        color = "#e15759" if pv < 0.10 else "#59a14f"
        ax.errorbar(b, i, xerr=1.96 * se, fmt="o", color=color,
                    ecolor=color, markersize=5)
    ax.axvline(0, color="#444", lw=0.8)
    ax.set_yticks(ys)
    ax.set_yticklabels(order["exposure"].values)
    ax.set_xlabel("beta on HEIGHT_IN (inches); red = D2 FAIL (p<0.10)")
    ax.set_title("D2 negative-control: exposure -> adult height")
    plot_style.save(fig, "causal/negctrl_failure_grid.png")

    # 3. Sibling dissociation.
    sib_rows = results[results["d3_sibling"].notna()]
    if len(sib_rows) > 0:
        fig, ax = plt.subplots(figsize=(7, 0.5 + 0.6 * len(sib_rows)))
        ys = np.arange(len(sib_rows)) * 2.5
        for i, (_, r) in enumerate(sib_rows.iterrows()):
            # Need to look up the primary beta for both exposure and sibling.
            b_t = r["d1_beta"]
            b_s = r["d3_beta_sibling"]
            ax.barh(ys[i] + 0.6, b_t, height=0.5, color="#4e79a7",
                    label="treatment" if i == 0 else None)
            ax.barh(ys[i], b_s, height=0.5, color="#f28e2b",
                    label="sibling" if i == 0 else None)
            ax.text(max(b_t, b_s, 0) * 1.05,
                    ys[i] + 0.3, r["d3_sibling"],
                    va="center", fontsize=8, color="#555")
        ax.axvline(0, color="#444", lw=0.8)
        ax.set_yticks(ys + 0.3)
        ax.set_yticklabels(sib_rows["exposure"].values)
        ax.set_xlabel("beta on W4_COG_COMP (L0+L1+AHPVT)")
        ax.set_title("D3 sibling dissociation: treatment vs placebo sibling")
        ax.legend(loc="lower right", frameon=True)
        plot_style.save(fig, "causal/sibling_dissociation.png")

    # 4. Adjustment stability.
    fig, ax = plt.subplots(figsize=(7, max(4, 0.28 * len(results))))
    order = results.sort_values("d4_rel_shift", ascending=False,
                                na_position="last")
    for i, (_, r) in enumerate(order.iterrows()):
        vals = [r["d4_beta_L0"], r["d4_beta_L0_L1"], r["d4_beta_L0_L1_AHPVT"]]
        if all(np.isnan(v) for v in vals):
            continue
        for j, v in enumerate(vals):
            if np.isnan(v):
                continue
            ax.scatter(v, i + (j - 1) * 0.18, s=25,
                       color=["#4e79a7", "#f28e2b", "#e15759"][j],
                       label=["L0", "L0+L1", "L0+L1+AHPVT"][j] if i == 0 else None)
    ax.axvline(0, color="#444", lw=0.8)
    ax.set_yticks(range(len(order)))
    ax.set_yticklabels(order["exposure"].values)
    ax.set_xlabel("beta on W4_COG_COMP across adjustment sets")
    ax.set_title("D4 adjustment-set stability")
    ax.legend(loc="lower right", frameon=True)
    plot_style.save(fig, "causal/adjustment_stability.png")

    # 5. Component consistency.
    fig, axes = plt.subplots(1, 3, figsize=(11, max(3, 0.26 * len(results))),
                             sharey=True)
    components = [
        ("d5_beta_c4wd90", "C4WD90_1 immediate"),
        ("d5_beta_c4wd60", "C4WD60_1 delayed"),
        ("d5_beta_c4numscr", "C4NUMSCR digit span"),
    ]
    order = results.sort_values("d1_beta", ascending=False)
    for ax, (bcol, title) in zip(axes, components):
        vals = order[bcol].values
        ax.barh(np.arange(len(order)), vals, color="#4e79a7")
        ax.axvline(0, color="#444", lw=0.8)
        ax.set_title(title)
        ax.set_yticks(np.arange(len(order)))
        ax.set_yticklabels(order["exposure"].values)
    plt.suptitle("D5 outcome-component consistency (primary spec)")
    plot_style.save(fig, "causal/component_consistency.png")


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def write_markdown(results: pd.DataFrame, path: Path) -> None:
    L: List[str] = []
    L.append("# Task 14 - Preliminary causal screening of social-exposure treatments")
    L.append("")
    L.append("Screens each W1 adolescent-social exposure against a battery of "
             "falsification / plausibility diagnostics (D1-D9). All diagnostics "
             "reuse weighted OLS on `GSWGT4_2`, cluster-robust SEs on `CLUSTER2`, "
             "and the same adjustment set conventions used in task10.")
    L.append("")
    L.append("## Diagnostics")
    L.append("")
    L.append("- **D1** baseline association on W4_COG_COMP (L0+L1+AHPVT); pass: p<0.05.")
    L.append("- **D2** negative-control outcome HEIGHT_IN; pass: p>0.10.")
    L.append("- **D3** sibling-exposure dissociation (where a sibling exists); pass: |beta_t| > |beta_sib| with |diff| > pooled SE.")
    L.append("- **D4** adjustment-set stability across L0 / L0+L1 / L0+L1+AHPVT; pass: relative shift <30% AND sign stable.")
    L.append("- **D5** outcome-component consistency across C4WD90_1 / C4WD60_1 / C4NUMSCR; pass: sign consistent AND >=2/3 with p<0.10.")
    L.append("- **D6** dose-response monotonicity (continuous only); pass: |rho_trend| > 0.7 AND monotone sign.")
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
            f"{_p(r.d2_pass)} | {_p(r.d3_pass)} | {_p(r.d4_pass)} | "
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
        L.append(f"- D4 rel-shift across adj sets = {r.d4_rel_shift if not pd.isna(r.d4_rel_shift) else float('nan'):.3g}; "
                 f"sign stable = {bool(r.d4_sign_stable)}; {'PASS' if r.d4_pass else 'FAIL'}.")
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

    # Shortlist.
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
        for _, r in shortlist.iterrows():
            L.append(f"- `{r.exposure}` ({r.category}): D1 beta = {r.d1_beta:.3g} (p={r.d1_p:.3g}); "
                     f"D2 HEIGHT_IN p = {r.d2_p:.3g}; D4 rel-shift = "
                     f"{r.d4_rel_shift if not pd.isna(r.d4_rel_shift) else float('nan'):.3g}.")
    L.append("")

    path.write_text("\n".join(L))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    print("Running causal screening pass ...")
    results = screen_all()
    results = classify(results)

    out_csv = OUT / "14_screening_matrix.csv"
    results.to_csv(out_csv, index=False)
    print(f"Wrote {out_csv} ({len(results)} rows)")

    shortlist = (
        results[results["category"].isin(["Promising", "Mixed"])]
        .sort_values(["category", "score"], ascending=[True, False])
        [["exposure", "category", "score", "notes"]]
    )
    shortlist["recommended_next"] = shortlist["category"].map({
        "Promising": "AIPW + E-value",
        "Mixed": "AIPW conditional on widened adjustment set",
    })
    shortlist.to_csv(OUT / "14_shortlist.csv", index=False)
    print(f"Wrote outputs/14_shortlist.csv ({len(shortlist)} rows)")

    write_markdown(results, OUT / "14_screening.md")
    print(f"Wrote outputs/14_screening.md")

    plot_figures(results)
    print("Wrote img/causal/*.png")


if __name__ == "__main__":
    main()

"""EXP-15-MULTI — Multi-outcome screening.

Extends the cognitive-screening D1/D4 sweep across 12 non-cognitive outcomes
(cardiometabolic W4, mental-health/functional/SES W5). For each (exposure,
outcome) pair, runs the two outcome-dependent diagnostics (D1 baseline, D4
adjustment-set stability) and writes a long-format matrix.

Outcome-independent diagnostics (D2 NC-height, D6 dose-response, D7 overlap,
D8 saturation, D9 red-flag) stay in cognitive-screening and are not recomputed
here. Sibling (D3) and component-consistency (D5) are cognition-specific and
NA for non-cognitive outcomes.

Weights: GSWGT4_2 is used for all outcomes (screening scope). Final causal
estimation on W5 outcomes should switch to GSW5 and model W4->W5 attrition
explicitly (see planned EXP-16-IPAW-W5).

Outputs (relative to this experiment folder):
  tables/primary/15_multi_outcome_matrix.csv
  tables/primary/15_multi_outcome.md
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

TABLES = HERE / "tables" / "primary"
TABLES.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Outcome battery
# ---------------------------------------------------------------------------
# name: (label, group, kind_note)
OUTCOMES: Dict[str, Tuple[str, str, str]] = {
    "H4BMI":    ("S27 BMI—W4",                              "cardiometabolic", "continuous"),
    "H4SBP":    ("S27 SYSTOLIC BLOOD PRESSURE—W4",          "cardiometabolic", "continuous"),
    "H4DBP":    ("S27 DIASTOLIC BLOOD PRESSURE—W4",         "cardiometabolic", "continuous"),
    "H4WAIST":  ("S27 MEASURED WAIST (CM)—W4",              "cardiometabolic", "continuous"),
    "H4BMICLS": ("S27 BMI CLASS—W4",                         "cardiometabolic", "ordinal-1-6"),
    "H5MN1":    ("S13Q1 LAST MO NO CNTRL IMPORT THINGS—W5", "mental_health",   "likert-1-5"),
    "H5MN2":    ("S13Q2 LAST MO CONFID HANDLE PERS PBMS—W5","mental_health",   "likert-1-5"),
    "H5ID1":    ("S5Q1 HOW IS GEN PHYSICAL HEALTH—W5",      "functional",      "likert-1-5"),
    "H5ID4":    ("S5Q4 LIMIT CLIMB SEV. FLIGHT STAIRS—W5",  "functional",      "ordinal-1-3"),
    "H5ID16":   ("S5Q16 HOW OFTEN TROUBLE SLEEPING—W5",     "functional",      "ordinal-0-4"),
    "H5LM5":    ("S3Q5 CURRENTLY WORK—W5",                   "ses",             "ordinal-1-3"),
    "H5EC1":    ("S4Q1 INCOME PERS EARNINGS [W4–W5]—W5",    "ses",             "bracketed-1-13"),
}


# ---------------------------------------------------------------------------
# Exposure registry — same 24 as EXP-14-COG
# Inlined from task14_causal_screening.py so this experiment is self-contained
# (the cognitive-screening run.py is the canonical home of these constants;
# any change there must be mirrored here).
# ---------------------------------------------------------------------------
NETWORK_EXPOSURES = {
    # name: (column, group, kind)
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
for _name, (_col, _group, _kind) in NETWORK_EXPOSURES.items():
    EXPOSURES[_name] = ("W4", _col, _group, _kind, True)
for _name, (_col, _group, _kind) in SURVEY_EXPOSURES.items():
    # Survey exposures use W1_FULL (no network gate) so the D1 sample is larger.
    EXPOSURES[_name] = ("W1_FULL", _col, _group, _kind, False)


# ---------------------------------------------------------------------------
# Adjustment-set builders (mirror cognitive-screening)
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
# Fitting primitive
# ---------------------------------------------------------------------------
def _fit(df: pd.DataFrame, exposure_col: str, y_col: str,
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
    res = weighted_ols(y, X.values, w, psu, column_names=list(X.columns))
    return res


# ---------------------------------------------------------------------------
# Frame loading (cached parquets via CACHE constant)
# ---------------------------------------------------------------------------
def _load_frames() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load W4 + W1_FULL analytic frames and attach H1PR4 + outcomes."""
    W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
    W1_FULL = pd.read_parquet(CACHE / "analytic_w1_full.parquet")

    # Attach H1PR4 from raw W1 in-home (not in cache frame).
    w1raw = pd.read_parquet(CACHE / "w1inhome.parquet")[["AID", "H1PR4"]]
    w1raw["H1PR4"] = pd.to_numeric(w1raw["H1PR4"], errors="coerce").where(
        lambda s: s.between(1, 5)
    )
    W4 = W4.merge(w1raw, on="AID", how="left")
    W1_FULL = W1_FULL.merge(w1raw, on="AID", how="left")

    # Attach each outcome column to both frames.
    for code in OUTCOMES:
        W4[code] = load_outcome(W4["AID"], code)
        W1_FULL[code] = load_outcome(W1_FULL["AID"], code)
    return W4, W1_FULL


# ---------------------------------------------------------------------------
# Per-outcome D1 and D4 (thin re-uses of the screening primitive but with
# outcome as a parameter instead of hardcoded W4_COG_COMP).
# ---------------------------------------------------------------------------
def d1_outcome(df: pd.DataFrame, exposure_col: str, outcome_col: str) -> dict:
    res = _fit(df, exposure_col, outcome_col, _adj_full)
    if res is None:
        return {"beta": np.nan, "se": np.nan, "p": np.nan, "n": 0, "pass": False}
    p = float(res["p"]["exposure"])
    return {
        "beta": float(res["beta"]["exposure"]),
        "se": float(res["se"]["exposure"]),
        "p": p,
        "n": int(res["n"]),
        "pass": bool(p < 0.05),
    }


def d4_outcome(df: pd.DataFrame, exposure_col: str, outcome_col: str) -> dict:
    betas = {}
    for name, builder in ADJ_BUILDERS.items():
        res = _fit(df, exposure_col, outcome_col, builder)
        betas[name] = float(res["beta"]["exposure"]) if res else np.nan
    bf = betas["L0+L1+AHPVT"]
    b0 = betas["L0"]
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
        "beta_L0": betas["L0"],
        "beta_L0_L1": betas["L0+L1"],
        "beta_L0_L1_AHPVT": betas["L0+L1+AHPVT"],
        "rel_shift": rel_shift,
        "sign_stable": sign_stable,
        "pass": bool(passes),
    }


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def run_matrix(W4: pd.DataFrame, W1_FULL: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for exp_name, (frame_key, col, group, kind, _) in EXPOSURES.items():
        df = W4 if frame_key == "W4" else W1_FULL
        for outcome_code, (label, o_group, o_kind) in OUTCOMES.items():
            d1 = d1_outcome(df, col, outcome_code)
            d4 = d4_outcome(df, col, outcome_code)
            rows.append({
                "exposure": exp_name,
                "exposure_group": group,
                "outcome": outcome_code,
                "outcome_label": label,
                "outcome_group": o_group,
                "n": d1["n"],
                "beta": d1["beta"],
                "se": d1["se"],
                "p": d1["p"],
                "d1_pass": d1["pass"],
                "beta_L0": d4["beta_L0"],
                "beta_L0_L1": d4["beta_L0_L1"],
                "beta_full": d4["beta_L0_L1_AHPVT"],
                "d4_rel_shift": d4["rel_shift"],
                "d4_sign_stable": d4["sign_stable"],
                "d4_pass": d4["pass"],
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Narrative markdown
# ---------------------------------------------------------------------------
def write_markdown(mat: pd.DataFrame) -> None:
    lines = ["# EXP-15-MULTI — Multi-outcome screening\n"]
    lines.append(
        "Re-runs the outcome-dependent part of the cognitive-screening diagnostic "
        "battery (D1 baseline WLS on `GSWGT4_2`, cluster-robust on `CLUSTER2`, "
        "primary spec L0+L1+AHPVT; D4 adjustment-set stability across L0 / "
        "L0+L1 / L0+L1+AHPVT) across 12 non-cognitive outcomes. Outcome-"
        "independent diagnostics (D2 height NC, D6/D7 dose-response + overlap, "
        "D8 saturation loss, D9 red flags) are inherited from "
        "[../cognitive-screening/tables/primary/14_screening_matrix.csv]"
        "(../../cognitive-screening/tables/primary/14_screening_matrix.csv).\n"
    )
    lines.append(
        "**Weight caveat:** `GSWGT4_2` is used uniformly for screening. "
        "Formal causal estimation on W5 outcomes should substitute `GSW5` and "
        "handle W4→W5 attrition (IPAW or bounding).\n"
    )
    lines.append(
        "**Adjustment-set caveat:** the primary spec includes `AH_PVT` (verbal "
        "IQ at W1) uniformly. For `H5EC1` / `H5LM5` / `H4BMI` this is plausibly "
        "a mediator (cognition → attainment / health behaviours → outcome); "
        "D4 flags any outcome where adding AHPVT moves β by > 30%.\n"
    )

    # Per-outcome tables.
    lines.append("## Per-outcome rankings\n")
    for o in OUTCOMES:
        sub = mat[mat.outcome == o].copy().sort_values(
            by=["d1_pass", "p"], ascending=[False, True]
        )
        lab = OUTCOMES[o][0]
        lines.append(f"### {o} — {lab}\n")
        lines.append(
            f"N range across exposures: {sub.n.min()}–{sub.n.max()}. "
            f"Significant (p<0.05) exposures: {int(sub.d1_pass.sum())} / {len(sub)}.\n"
        )
        top = sub.head(6)
        tbl = top[["exposure", "n", "beta", "se", "p", "d1_pass",
                   "d4_rel_shift", "d4_pass"]].copy()
        tbl["beta"] = tbl["beta"].map(lambda v: f"{v:.4g}")
        tbl["se"] = tbl["se"].map(lambda v: f"{v:.4g}")
        tbl["p"] = tbl["p"].map(lambda v: f"{v:.3g}")
        tbl["d4_rel_shift"] = tbl["d4_rel_shift"].map(
            lambda v: f"{v:.2f}" if pd.notna(v) else "NA"
        )
        lines.append(tbl.to_markdown(index=False))
        lines.append("")

    # Cross-outcome robust list.
    lines.append("## Cross-outcome robust candidates\n")
    # "Top 3 per outcome by lowest p among d1_pass exposures."
    top_by_outcome: Dict[str, list] = {}
    for o in OUTCOMES:
        sub = mat[(mat.outcome == o) & (mat.d1_pass)].sort_values("p").head(3)
        top_by_outcome[o] = sub["exposure"].tolist()
    # Count appearances.
    counts: Dict[str, int] = {}
    for o, lst in top_by_outcome.items():
        for e in lst:
            counts[e] = counts.get(e, 0) + 1
    robust = {e: n for e, n in counts.items() if n >= 3}
    if robust:
        lines.append(
            "Exposures appearing in top-3 (by lowest p among significant) for "
            f"≥3 outcomes:\n"
        )
        for e, n in sorted(robust.items(), key=lambda kv: -kv[1]):
            outs = [o for o, lst in top_by_outcome.items() if e in lst]
            lines.append(f"- **{e}** ({n} outcomes): {', '.join(outs)}")
        lines.append("")
    else:
        lines.append(
            "No exposure appears in the top-3 for 3+ outcomes. Cross-outcome "
            "robustness is weak. Consider focusing task16 on a single "
            "(exposure, outcome) pair justified by task14's primary-cognition "
            "screen rather than attempting a multi-outcome summary estimator.\n"
        )

    # Handoff recommendation.
    lines.append("## Task16 handoff\n")
    # Pick the top-2 (exposure, outcome) pairs by lowest p among cells that
    # pass BOTH d1 and d4, across all outcomes.
    qualifying = mat[(mat.d1_pass) & (mat.d4_pass)].copy()
    qualifying = qualifying.sort_values("p").head(4)
    if len(qualifying) == 0:
        lines.append(
            "**No (exposure, outcome) pair passes both D1 and D4.** Task16 "
            "should either widen the adjustment set (drop AHPVT where it is "
            "a plausible mediator) or accept the D4 instability and run "
            "sensitivity curves. The strongest D1-only signals are:\n"
        )
        strongest = mat[mat.d1_pass].sort_values("p").head(4)
        pairs = [f"{r.exposure} → {r.outcome}" for _, r in strongest.iterrows()]
        lines.append(f"**Task16 handoff: {pairs}**")
    else:
        pairs = [f"{r.exposure} → {r.outcome}" for _, r in qualifying.iterrows()]
        lines.append(
            f"**Task16 handoff: {pairs}**\n\n"
            "Each pair passes D1 (β significantly non-zero under primary spec) "
            "and D4 (β stable across nested adjustment sets to within 30%). "
            "Cross-reference with task14's D2/D6/D7 for the chosen exposures "
            "before committing to formal causal estimation."
        )

    (TABLES / "15_multi_outcome.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------
def run_multi_outcome_screen() -> pd.DataFrame:
    """Build the 24×12 (exposure, outcome) screening matrix and write outputs.

    Returns the matrix DataFrame for callers (tests, downstream notebooks)
    that want to inspect it directly without re-reading the CSV.
    """
    print("Running multi-outcome screening ...")
    W4, W1_FULL = _load_frames()
    mat = run_matrix(W4, W1_FULL)
    csv_path = TABLES / "15_multi_outcome_matrix.csv"
    mat.to_csv(csv_path, index=False)
    print(f"Wrote {csv_path} ({len(mat)} rows)")
    write_markdown(mat)
    print(f"Wrote {TABLES / '15_multi_outcome.md'}")
    return mat


def main() -> None:
    run_multi_outcome_screen()


if __name__ == "__main__":
    main()

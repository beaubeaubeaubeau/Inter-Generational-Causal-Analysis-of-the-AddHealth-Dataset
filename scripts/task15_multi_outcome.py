"""Task 15 - Multi-outcome screening.

Extends the task14 causal screen by modulating over 12 non-cognitive outcomes
(cardiometabolic W4, mental-health/functional/SES W5). For each (exposure,
outcome) pair, runs the two outcome-dependent diagnostics (D1 baseline, D4
adjustment-set stability) and writes a long-format matrix.

Outcome-independent diagnostics (D2 NC-height, D6 dose-response, D7 overlap,
D8 saturation, D9 red-flag) stay in task14 and are not recomputed here.
Sibling (D3) and component-consistency (D5) are cognition-specific and NA
for non-cognitive outcomes.

Weights: GSWGT4_2 is used for all outcomes (screening scope). Final causal
estimation on W5 outcomes should switch to GSW5 and model W4->W5 attrition
explicitly.

Outputs:
  outputs/15_multi_outcome_matrix.csv
  outputs/15_multi_outcome.md
  img/causal/multi_outcome_beta_heatmap.png
  img/causal/multi_outcome_sig_heatmap.png
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Callable, Dict, Optional, Tuple

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from analysis_utils import (  # noqa: E402
    ROOT, CACHE, clean_var, weighted_ols, load_outcome,
)
import plot_style  # noqa: E402
import task14_causal_screening as t14  # noqa: E402

OUT = ROOT / "outputs"
IMG = ROOT / "img" / "causal"
IMG.mkdir(parents=True, exist_ok=True)


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
# Frames (reuse task14's already-loaded W4 and W1_FULL with H1PR4 / HEIGHT_IN)
# ---------------------------------------------------------------------------
W4 = t14.W4.copy()
W1_FULL = t14.W1_FULL.copy()

# Attach each outcome column to both frames (survey exposures live in W1_FULL,
# network exposures in W4; outcomes are AID-keyed in either).
for code in OUTCOMES:
    W4[code] = load_outcome(W4["AID"], code)
    W1_FULL[code] = load_outcome(W1_FULL["AID"], code)


# ---------------------------------------------------------------------------
# Per-outcome D1 and D4 (thin re-uses of task14 primitives but with outcome as
# a parameter instead of hardcoded W4_COG_COMP).
# ---------------------------------------------------------------------------
def d1_outcome(df: pd.DataFrame, exposure_col: str, outcome_col: str) -> dict:
    res = t14._fit(df, exposure_col, outcome_col, t14._adj_full)
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
    for name, builder in t14.ADJ_BUILDERS.items():
        res = t14._fit(df, exposure_col, outcome_col, builder)
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
def run_matrix() -> pd.DataFrame:
    rows = []
    for exp_name, (frame_key, col, group, kind, _) in t14.EXPOSURES.items():
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
# Figures
# ---------------------------------------------------------------------------
def plot_heatmaps(mat: pd.DataFrame) -> None:
    import matplotlib.pyplot as plt
    import seaborn as sns

    plot_style.setup()

    exp_order = list(t14.EXPOSURES.keys())
    out_order = list(OUTCOMES.keys())

    # Beta heatmap — standardize per outcome column (z-score of beta across
    # exposures) to make the heatmap comparable across outcomes on different
    # natural scales.
    beta_wide = mat.pivot(index="exposure", columns="outcome", values="beta")
    beta_wide = beta_wide.reindex(index=exp_order, columns=out_order)
    beta_z = beta_wide.apply(
        lambda col: (col - col.mean()) / col.std(ddof=0) if col.std(ddof=0) > 0 else col * 0,
        axis=0,
    )
    p_wide = mat.pivot(index="exposure", columns="outcome", values="p")
    p_wide = p_wide.reindex(index=exp_order, columns=out_order)
    sig = (p_wide < 0.05)

    fig, ax = plt.subplots(figsize=(10, 10))
    sns.heatmap(
        beta_z, cmap="RdBu_r", center=0, vmin=-2.5, vmax=2.5,
        ax=ax, cbar_kws={"label": "Per-outcome z-score of β"}, linewidths=0.4,
        linecolor="white",
    )
    # Star-mark p<0.05 cells.
    for i, exp in enumerate(exp_order):
        for j, out in enumerate(out_order):
            if bool(sig.loc[exp, out]):
                ax.text(
                    j + 0.5, i + 0.5, "*",
                    ha="center", va="center", color="black", fontsize=14, fontweight="bold",
                )
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    plot_style.save(fig, "causal/multi_outcome_beta_heatmap.png")

    # Significance heatmap — −log10(p), clamped 0–5.
    logp = -np.log10(p_wide.clip(lower=1e-5))
    fig, ax = plt.subplots(figsize=(10, 10))
    sns.heatmap(
        logp, cmap="viridis", vmin=0, vmax=5,
        ax=ax, cbar_kws={"label": "−log10(p), clipped at 5"},
        linewidths=0.4, linecolor="white",
    )
    ax.set_title("Multi-outcome significance (−log10 p) per (exposure, outcome) pair")
    ax.set_xlabel("")
    ax.set_ylabel("")
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    plot_style.save(fig, "causal/multi_outcome_sig_heatmap.png")


# ---------------------------------------------------------------------------
# Narrative markdown
# ---------------------------------------------------------------------------
def write_markdown(mat: pd.DataFrame) -> None:
    lines = ["# Task 15 — Multi-outcome screening\n"]
    lines.append(
        "Re-runs the outcome-dependent part of the task14 diagnostic battery "
        "(D1 baseline WLS on `GSWGT4_2`, cluster-robust on `CLUSTER2`, primary "
        "spec L0+L1+AHPVT; D4 adjustment-set stability across L0 / L0+L1 / "
        "L0+L1+AHPVT) across 12 non-cognitive outcomes. Outcome-independent "
        "diagnostics (D2 height NC, D6/D7 dose-response + overlap, D8 "
        "saturation loss, D9 red flags) are inherited from "
        "[outputs/14_screening_matrix.csv](14_screening_matrix.csv).\n"
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

    (OUT / "15_multi_outcome.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("Running multi-outcome screening ...")
    mat = run_matrix()
    mat.to_csv(OUT / "15_multi_outcome_matrix.csv", index=False)
    print(f"Wrote {OUT / '15_multi_outcome_matrix.csv'} ({len(mat)} rows)")
    plot_heatmaps(mat)
    print("Wrote img/causal/multi_outcome_*.png")
    write_markdown(mat)
    print(f"Wrote {OUT / '15_multi_outcome.md'}")


if __name__ == "__main__":
    main()

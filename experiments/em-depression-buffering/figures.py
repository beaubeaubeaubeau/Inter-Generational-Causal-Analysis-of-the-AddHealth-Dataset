"""Figures for em-depression-buffering.

Three plots, all with descriptive titles baked into the figure (per the
chart-explanation convention -- see ../README.md).

  1. primary/em_dep_interaction_forest.png
        Forest plot of beta_{IDGX2 x CESD_SUM} +/- 95% CI per outcome,
        with TWO points per outcome (conservative spec vs clean spec) so
        the D9 collider double-use sensitivity is visible at a glance.

  2. primary/em_dep_subgroup_forest.png
        Tertile-stratified forest: marginal beta_IDGX2 within each
        CESD_SUM tertile (low / mid / high), per outcome. The intuitive
        unpacking of the buffering hypothesis.

  3. sensitivity/em_dep_dose_response_panels.png
        Per-outcome panel of mean(Y) vs IDGX2 quintile, one line per
        CESD_SUM tertile. Linearity diagnostic for the linear-in-CESD
        interaction spec.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
TABLES_PRIMARY = HERE / "tables" / "primary"
TABLES_SENS = HERE / "tables" / "sensitivity"
FIGS_PRIMARY = HERE / "figures" / "primary"
FIGS_SENS = HERE / "figures" / "sensitivity"
for _d in (FIGS_PRIMARY, FIGS_SENS):
    _d.mkdir(parents=True, exist_ok=True)

import sys  # noqa: E402
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from analysis.sensitivity_panel import plot_sensitivity_panel  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Interaction-coefficient forest with two specs side-by-side
# ---------------------------------------------------------------------------
def fig_interaction_forest(primary: pd.DataFrame) -> Path:
    """Forest of beta_{IDGX2 x CESD_SUM} per outcome x spec.

    Two markers per outcome (conservative vs clean spec). Substantial
    divergence between the two for any outcome indicates the D9 collider
    issue is empirically real; consistency is the substantive defence.
    """
    df = primary.dropna(subset=["beta_inter"]).copy()
    outcomes = df["outcome"].unique().tolist()
    fig, ax = plt.subplots(figsize=(8.0, 0.6 * len(outcomes) * 2 + 1.5))
    y = 0
    yticks, ylabels = [], []
    spec_color = {"conservative": "#DD8452", "clean": "#4C72B0"}
    for oc in outcomes:
        for spec in ("conservative", "clean"):
            sub = df[(df["outcome"] == oc) & (df["spec"] == spec)]
            if sub.empty or pd.isna(sub["beta_inter"].iloc[0]):
                y += 1
                continue
            r = sub.iloc[0]
            ax.errorbar(
                [r["beta_inter"]], [y],
                xerr=[[r["beta_inter"] - r["ci_lo_inter"]],
                      [r["ci_hi_inter"] - r["beta_inter"]]],
                fmt="o", color=spec_color[spec], ecolor=spec_color[spec],
                capsize=3,
            )
            yticks.append(y)
            ylabels.append(f"{oc} ({spec})")
            y += 1
        y += 0.5  # gap between outcomes
    ax.axvline(0.0, color="red", linestyle="--", linewidth=1)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=9)
    ax.set_xlabel("Interaction coefficient (IDGX2 x CESD_SUM)")
    ax.set_title(
        "Effect modification of W1 popularity (IDGX2) by depression "
        "(CESD_SUM)\nBeta_{IDGX2 x CESD_SUM} per outcome under TWO specs "
        "(D9 collider check)",
        fontsize=11,
    )
    from matplotlib.patches import Patch
    handles = [
        Patch(color=spec_color["conservative"],
              label="conservative (CESD in adj. set + as moderator)"),
        Patch(color=spec_color["clean"],
              label="clean (CESD as moderator only)"),
    ]
    ax.legend(handles=handles, loc="best", fontsize=8, frameon=True)
    fig.tight_layout()
    out = FIGS_PRIMARY / "em_dep_interaction_forest.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# 2. Tertile-stratified subgroup forest
# ---------------------------------------------------------------------------
def fig_subgroup_forest(strat: pd.DataFrame) -> Path:
    """Per-outcome panel of beta_IDGX2 +/- 95% CI within each CESD tertile."""
    outcomes = strat["outcome"].unique().tolist()
    fig, axes = plt.subplots(len(outcomes), 1,
                              figsize=(7.0, 1.5 * len(outcomes)),
                              sharex=True)
    if len(outcomes) == 1:
        axes = [axes]
    for ax, oc in zip(axes, outcomes):
        sub = strat[strat["outcome"] == oc].dropna(subset=["beta_idgx2"])
        ys = np.arange(len(sub))
        ax.errorbar(
            sub["beta_idgx2"], ys,
            xerr=[sub["beta_idgx2"] - sub["ci_lo"],
                  sub["ci_hi"] - sub["beta_idgx2"]],
            fmt="o", color="black", ecolor="grey", capsize=3,
        )
        ax.axvline(0.0, color="red", linestyle="--", linewidth=1)
        ax.set_yticks(ys)
        ax.set_yticklabels([f"CESD tertile {int(t)}"
                            for t in sub["cesd_tertile"]], fontsize=9)
        ax.set_title(f"{oc} -- beta_IDGX2 within each CESD_SUM tertile",
                     fontsize=10)
    axes[-1].set_xlabel("Stratum-specific IDGX2 coefficient (95% CI)")
    fig.suptitle(
        "Tertile-stratified IDGX2 effect by CESD_SUM tertile\n"
        "Marginal beta_IDGX2 fit separately within each tertile of CESD_SUM",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = FIGS_PRIMARY / "em_dep_subgroup_forest.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# 3. Dose-response panels (mean Y vs IDGX2 quintile, line per CESD tertile)
# ---------------------------------------------------------------------------
def fig_dose_response_panels(panel_df: pd.DataFrame) -> Path:
    """Mean Y vs IDGX2 quintile, line per CESD_SUM tertile, panel per outcome.

    `panel_df` columns: outcome, cesd_tertile, idgx2_quintile, y_mean, y_se.
    Computed in `run.py` (TBD aggregator) or inline here from the analytic
    frame. This is the linearity-of-interaction diagnostic.
    """
    outcomes = panel_df["outcome"].unique().tolist()
    n = len(outcomes)
    cols = min(3, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4.0 * cols, 3.0 * rows),
                              squeeze=False)
    for k, oc in enumerate(outcomes):
        ax = axes[k // cols][k % cols]
        for t, sub in panel_df[panel_df["outcome"] == oc].groupby("cesd_tertile"):
            ax.errorbar(sub["idgx2_quintile"], sub["y_mean"],
                        yerr=sub["y_se"], marker="o",
                        label=f"CESD tertile {int(t)}")
        ax.set_xlabel("IDGX2 quintile")
        ax.set_ylabel(oc)
        ax.set_title(oc, fontsize=9)
        ax.legend(fontsize=7)
    for k in range(n, rows * cols):
        axes[k // cols][k % cols].axis("off")
    fig.suptitle(
        "Dose-response of outcome on IDGX2 quintile by CESD_SUM tertile\n"
        "Linearity diagnostic for the WLS interaction spec",
        fontsize=11,
    )
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = FIGS_SENS / "em_dep_dose_response_panels.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def fig_sensitivity_panel() -> Path:
    """Three-panel sensitivity figure for em-depression-buffering."""
    ev_path = TABLES_SENS / "em_dep_evalue_chinn2000.csv"
    cf_path = TABLES_SENS / "em_dep_cornfield_grid.csv"
    et_path = TABLES_SENS / "em_dep_eta_tilt.csv"
    return plot_sensitivity_panel(
        FIGS_SENS / "em_dep_sensitivity_panel.png",
        title=("EM-Depression-Buffering — sensitivity panel\n"
               "(a) E-value per cell · (b) Cornfield B grid · (c) η-tilt ATE surface"),
        evalue_table=pd.read_csv(ev_path) if (ev_path.exists() and ev_path.stat().st_size > 8) else pd.DataFrame(),
        cornfield_table=pd.read_csv(cf_path) if (cf_path.exists() and cf_path.stat().st_size > 8) else pd.DataFrame(),
        eta_tilt_table=pd.read_csv(et_path) if (et_path.exists() and et_path.stat().st_size > 8) else pd.DataFrame(),
        eta_continuous_note=(
            "η-tilt: top-vs-bottom-quintile IDGX2 within high-CESD tertile "
            "(operational location of the buffering prediction). "
            "Conservative/clean specs collapsed to clean only."
        ),
    )


def main() -> None:
    primary = pd.read_csv(TABLES_PRIMARY / "em_dep_interaction.csv")
    strat = pd.read_csv(TABLES_PRIMARY / "em_dep_stratified_betas.csv")
    fig_interaction_forest(primary)
    fig_subgroup_forest(strat)
    fig_sensitivity_panel()
    # fig_dose_response_panels needs a panel CSV produced by a TBD aggregator
    # in run.py. Wire when run.py is enriched.
    print("Figures written to:", FIGS_PRIMARY, FIGS_SENS)


if __name__ == "__main__":
    main()

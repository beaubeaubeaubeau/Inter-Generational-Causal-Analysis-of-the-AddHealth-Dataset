"""Figures for em-sex-differential.

Three primary plots, all with descriptive titles baked into the figure
(per the chart-explanation convention -- see ../README.md).

  1. primary/em_sex_interaction_forest.png
        Forest plot of beta_{IDGX2 x male} +/- 95% CI across the 5
        outcomes (3 cardiometabolic + 2 mental-health). Reference line at 0.

  2. primary/em_sex_stratified_forest.png
        Sex-stratified forest: marginal beta_IDGX2 separately for boys and
        for girls, side-by-side per outcome. The intuitive presentation of
        the modification.

  3. sensitivity/em_sex_dose_response_panels.png
        Per-outcome panel of mean(Y) vs IDGX2 quintile, one line per sex.
        Linearity / sex-by-sex shape diagnostic.
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
# 1. Interaction-coefficient forest
# ---------------------------------------------------------------------------
def fig_interaction_forest(primary: pd.DataFrame) -> Path:
    df = primary.dropna(subset=["beta_inter"]).copy()
    fig, ax = plt.subplots(figsize=(7.5, 4.0))
    ys = np.arange(len(df))
    ax.errorbar(
        df["beta_inter"], ys,
        xerr=[df["beta_inter"] - df["ci_lo_inter"],
              df["ci_hi_inter"] - df["beta_inter"]],
        fmt="o", color="black", ecolor="grey", capsize=3,
    )
    ax.axvline(0.0, color="red", linestyle="--", linewidth=1)
    ax.set_yticks(ys)
    ax.set_yticklabels(df["outcome"])
    ax.set_xlabel("Interaction coefficient (IDGX2 x male)")
    ax.set_title("Sex-differential effect of W1 popularity (IDGX2)\n"
                 "Interaction coefficient with 95% CI, per outcome "
                 "(WLS, cluster-robust)")
    fig.tight_layout()
    out = FIGS_PRIMARY / "em_sex_interaction_forest.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# 2. Sex-stratified subgroup forest
# ---------------------------------------------------------------------------
def fig_stratified_forest(strat: pd.DataFrame) -> Path:
    """Per-outcome side-by-side beta_IDGX2 +/- 95% CI for boys vs girls."""
    outcomes = strat["outcome"].unique().tolist()
    fig, ax = plt.subplots(figsize=(7.5, 0.6 * len(outcomes) * 2 + 1))
    y = 0
    yticks, ylabels = [], []
    for oc in outcomes:
        for stratum, color in [("female", "tab:purple"), ("male", "tab:blue")]:
            sub = strat[(strat["outcome"] == oc) & (strat["stratum"] == stratum)]
            if sub.empty or pd.isna(sub["beta_idgx2"].iloc[0]):
                y += 1
                continue
            r = sub.iloc[0]
            ax.errorbar(
                [r["beta_idgx2"]], [y],
                xerr=[[r["beta_idgx2"] - r["ci_lo"]], [r["ci_hi"] - r["beta_idgx2"]]],
                fmt="o", color=color, ecolor=color, capsize=3,
            )
            yticks.append(y)
            ylabels.append(f"{oc} ({stratum})")
            y += 1
        y += 0.5  # gap between outcomes
    ax.axvline(0.0, color="red", linestyle="--", linewidth=1)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.set_xlabel("Stratum-specific IDGX2 coefficient (95% CI)")
    ax.set_title("IDGX2 effect by sex, stratified WLS fits\n"
                 "Per-outcome beta_IDGX2 fit separately within each sex")
    fig.tight_layout()
    out = FIGS_PRIMARY / "em_sex_stratified_forest.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# 3. Sex-stratified dose-response panels
# ---------------------------------------------------------------------------
def fig_dose_response_panels(panel_df: pd.DataFrame) -> Path:
    """Mean Y vs IDGX2 quintile, one line per sex, panel per outcome.

    `panel_df` columns: outcome, stratum, idgx2_quintile, y_mean, y_se.
    """
    outcomes = panel_df["outcome"].unique().tolist()
    n = len(outcomes)
    cols = min(3, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4.0 * cols, 3.0 * rows),
                              squeeze=False)
    for k, oc in enumerate(outcomes):
        ax = axes[k // cols][k % cols]
        for stratum, sub in panel_df[panel_df["outcome"] == oc].groupby("stratum"):
            ax.errorbar(sub["idgx2_quintile"], sub["y_mean"],
                        yerr=sub["y_se"], marker="o", label=stratum)
        ax.set_xlabel("IDGX2 quintile")
        ax.set_ylabel(oc)
        ax.set_title(oc, fontsize=9)
        ax.legend(fontsize=7)
    for k in range(n, rows * cols):
        axes[k // cols][k % cols].axis("off")
    fig.suptitle("Sex-stratified dose-response of outcome on IDGX2 quintile\n"
                 "Linearity diagnostic for the WLS interaction spec", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = FIGS_SENS / "em_sex_dose_response_panels.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def fig_sensitivity_panel() -> Path:
    """Three-panel sensitivity figure for em-sex-differential."""
    ev_path = TABLES_SENS / "em_sex_evalue_chinn2000.csv"
    cf_path = TABLES_SENS / "em_sex_cornfield_grid.csv"
    et_path = TABLES_SENS / "em_sex_eta_tilt.csv"
    return plot_sensitivity_panel(
        FIGS_SENS / "em_sex_sensitivity_panel.png",
        title=("EM-Sex-Differential — sensitivity panel\n"
               "(a) E-value per cell · (b) Cornfield B grid · (c) η-tilt ATE surface"),
        evalue_table=pd.read_csv(ev_path) if (ev_path.exists() and ev_path.stat().st_size > 8) else pd.DataFrame(),
        cornfield_table=pd.read_csv(cf_path) if (cf_path.exists() and cf_path.stat().st_size > 8) else pd.DataFrame(),
        eta_tilt_table=pd.read_csv(et_path) if (et_path.exists() and et_path.stat().st_size > 8) else pd.DataFrame(),
        eta_continuous_note=(
            "η-tilt: top-vs-bottom-quintile IDGX2 within the female stratum "
            "(steeper protective slope per primary)."
        ),
    )


def main() -> None:
    primary = pd.read_csv(TABLES_PRIMARY / "em_sex_interaction.csv")
    strat = pd.read_csv(TABLES_PRIMARY / "em_sex_stratified_betas.csv")
    fig_interaction_forest(primary)
    fig_stratified_forest(strat)
    fig_sensitivity_panel()
    print("Figures written to:", FIGS_PRIMARY, FIGS_SENS)


if __name__ == "__main__":
    main()

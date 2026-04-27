"""Figures for em-compensatory-by-ses.

Three primary plots, all with descriptive titles baked into the figure
(per the chart-explanation convention -- see ../README.md).

  1. primary/em_ses_interaction_forest.png
        Forest plot of the interaction coefficient beta_{IDGX2 x PARENT_ED}
        across the 5 outcomes, with 95% CIs. Reference line at 0.

  2. primary/em_ses_subgroup_forest.png
        Subgroup-stratified forest: marginal beta_IDGX2 within each
        PARENT_ED tertile (low / mid / high), per outcome. Highlights the
        substantive direction of the modification.

  3. sensitivity/em_ses_dose_response_panels.png
        Per-outcome panel of mean(Y) vs IDGX2 quintile, one line per
        PARENT_ED tertile. Visual diagnostic for nonlinearity in the
        interaction (the WLS spec assumes linear interaction).

This is a scaffold. None of these functions are wired to actual data; they
demonstrate the intended figure shapes and call sites for `run.py`'s
output CSVs.
"""
from __future__ import annotations

import sys
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

ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from analysis.sensitivity_panel import plot_sensitivity_panel  # noqa: E402


# ---------------------------------------------------------------------------
# 1. Interaction-coefficient forest
# ---------------------------------------------------------------------------
def fig_interaction_forest(primary: pd.DataFrame) -> Path:
    """Forest of beta_{IDGX2 x PARENT_ED} +/- 95% CI per outcome."""
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
    ax.set_xlabel("Interaction coefficient (IDGX2 x PARENT_ED)")
    ax.set_title("Effect modification of W1 popularity (IDGX2) by parental "
                 "education (PARENT_ED)\nInteraction coefficient with 95% CI, "
                 "per outcome (WLS, cluster-robust)")
    fig.tight_layout()
    out = FIGS_PRIMARY / "em_ses_interaction_forest.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# 2. Subgroup-stratified forest (beta_IDGX2 within each PARENT_ED tertile)
# ---------------------------------------------------------------------------
def fig_subgroup_forest(qdr: pd.DataFrame) -> Path:
    """Per-outcome panel of beta_qtrend +/- 1.96*SE for each PARENT_ED tertile."""
    outcomes = qdr["outcome"].unique().tolist()
    fig, axes = plt.subplots(len(outcomes), 1, figsize=(6.5, 1.5 * len(outcomes)),
                              sharex=True)
    if len(outcomes) == 1:
        axes = [axes]
    for ax, oc in zip(axes, outcomes):
        sub = qdr[qdr["outcome"] == oc]
        ys = np.arange(len(sub))
        ax.errorbar(
            sub["beta_qtrend"], ys,
            xerr=1.96 * sub["se_qtrend"],
            fmt="o", color="black", ecolor="grey", capsize=3,
        )
        ax.axvline(0.0, color="red", linestyle="--", linewidth=1)
        ax.set_yticks(ys)
        ax.set_yticklabels([f"PED tertile {int(t)}" for t in sub["parent_ed_tertile"]])
        ax.set_title(f"{oc} -- IDGX2 quintile-trend beta within each PARENT_ED tertile",
                     fontsize=9)
    fig.suptitle("Subgroup-stratified IDGX2 effect by PARENT_ED tertile\n"
                 "Quintile-trend slope of IDGX2, fit within each tertile of PARENT_ED",
                 fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.96))
    out = FIGS_PRIMARY / "em_ses_subgroup_forest.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# 3. Dose-response panels (mean Y vs IDGX2 quintile, one line per PED tertile)
# ---------------------------------------------------------------------------
def fig_dose_response_panels(panel_df: pd.DataFrame) -> Path:
    """Mean Y vs IDGX2 quintile, line per PARENT_ED tertile, panel per outcome.

    `panel_df` is expected to have columns:
      outcome, parent_ed_tertile, idgx2_quintile, y_mean, y_se
    Computed in `run.py` (TBD aggregator) or inline here from the analytic frame.
    """
    outcomes = panel_df["outcome"].unique().tolist()
    n = len(outcomes)
    cols = min(3, n)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4.0 * cols, 3.0 * rows),
                              squeeze=False)
    for k, oc in enumerate(outcomes):
        ax = axes[k // cols][k % cols]
        for t, sub in panel_df[panel_df["outcome"] == oc].groupby("parent_ed_tertile"):
            ax.errorbar(sub["idgx2_quintile"], sub["y_mean"],
                        yerr=sub["y_se"], marker="o",
                        label=f"PED tertile {int(t)}")
        ax.set_xlabel("IDGX2 quintile")
        ax.set_ylabel(oc)
        ax.set_title(oc, fontsize=9)
        ax.legend(fontsize=7)
    # Hide unused subplots.
    for k in range(n, rows * cols):
        axes[k // cols][k % cols].axis("off")
    fig.suptitle("Dose-response of outcome on IDGX2 quintile by PARENT_ED tertile\n"
                 "Linearity diagnostic for the WLS interaction spec", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    out = FIGS_SENS / "em_ses_dose_response_panels.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def fig_sensitivity_panel() -> Path:
    """Three-panel sensitivity figure for em-compensatory-by-ses."""
    ev_path = TABLES_SENS / "em_ses_evalue_chinn2000.csv"
    cf_path = TABLES_SENS / "em_ses_cornfield_grid.csv"
    et_path = TABLES_SENS / "em_ses_eta_tilt.csv"
    return plot_sensitivity_panel(
        FIGS_SENS / "em_ses_sensitivity_panel.png",
        title=("EM-Compensatory-by-SES — sensitivity panel\n"
               "(a) E-value per cell · (b) Cornfield B grid · (c) η-tilt ATE surface"),
        evalue_table=pd.read_csv(ev_path) if (ev_path.exists() and ev_path.stat().st_size > 8) else pd.DataFrame(),
        cornfield_table=pd.read_csv(cf_path) if (cf_path.exists() and cf_path.stat().st_size > 8) else pd.DataFrame(),
        eta_tilt_table=pd.read_csv(et_path) if (et_path.exists() and et_path.stat().st_size > 8) else pd.DataFrame(),
        eta_continuous_note=(
            "η-tilt: top-vs-bottom-quintile IDGX2 within bottom PARENT_ED tertile."
        ),
    )


def main() -> None:
    primary = pd.read_csv(TABLES_PRIMARY / "em_ses_interaction.csv")
    qdr = pd.read_csv(TABLES_SENS / "em_ses_quintile_by_tertile.csv")
    fig_interaction_forest(primary)
    fig_subgroup_forest(qdr)
    fig_sensitivity_panel()
    # fig_dose_response_panels needs a panel CSV produced by a TBD aggregator
    # in run.py. Wire when run.py is enriched.
    print("Figures written to:", FIGS_PRIMARY, FIGS_SENS)


if __name__ == "__main__":
    main()

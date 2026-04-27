"""popularity-and-substance-use — figure generators.

Three planned figures:

  1. ``outcome_specificity_heatmap.png`` (primary) — side-by-side signed
     beta heatmap: substance-use outcomes (this experiment) on the left,
     cardiometabolic outcomes (read from `multi-outcome-screening`) on the
     right, both with `IDGX2` as the row. The visual point is the sign
     inversion: red bars on substance-use, blue bars on cardiometabolic.

  2. ``popularity_subst_forest.png`` (primary) — forest plot of β ± 1.96·SE
     for each of the 8 substance-use outcomes, sorted by wave and outcome
     family. Reference line at β = 0.

  3. ``popularity_subst_quintiles.png`` (sensitivity) — small-multiple
     dose-response panels (one per outcome): mean outcome by IDGX2 quintile
     with WLS-derived 95% CIs. The visual test of "is the elevation
     concentrated at the top quintile?".

Reads:
  ./tables/primary/popularity_subst_matrix.csv
  ./tables/sensitivity/popularity_subst_quintiles.csv
  ../multi-outcome-screening/tables/primary/15_multi_outcome_matrix.csv
    (for cardiometabolic comparison strip in figure 1)

Writes:
  ./figures/primary/outcome_specificity_heatmap.png
  ./figures/primary/popularity_subst_forest.png
  ./figures/sensitivity/popularity_subst_quintiles.png
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analysis import plot_style  # noqa: E402
from analysis.sensitivity_panel import plot_sensitivity_panel  # noqa: E402

plot_style.setup()

TABLES_PRIMARY = HERE / "tables" / "primary"
TABLES_SENS = HERE / "tables" / "sensitivity"
FIG_PRIMARY = HERE / "figures" / "primary"
FIG_SENS = HERE / "figures" / "sensitivity"
FIG_PRIMARY.mkdir(parents=True, exist_ok=True)
FIG_SENS.mkdir(parents=True, exist_ok=True)

MULTI_MATRIX = ROOT / "experiments" / "multi-outcome-screening" / "tables" / "primary" / "15_multi_outcome_matrix.csv"


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def outcome_specificity_heatmap() -> None:
    """Two-panel signed-beta heatmap: substance vs. cardiometabolic for IDGX2."""
    sub = pd.read_csv(TABLES_PRIMARY / "popularity_subst_matrix.csv")
    multi = pd.read_csv(MULTI_MATRIX)
    cardio = multi[(multi.exposure == "IDGX2") & (multi.outcome_group == "cardiometabolic")]

    fig, axes = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={"width_ratios": [1, 1]})

    # Left: substance use (predicted +)
    ax = axes[0]
    s_vals = sub.set_index("outcome")["beta"].values
    s_labels = sub["outcome"].tolist()
    vmax = float(np.nanmax(np.abs(np.concatenate([s_vals, cardio["beta"].values]))) or 1.0)
    im0 = ax.imshow(s_vals.reshape(-1, 1), cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_yticks(range(len(s_labels)))
    ax.set_yticklabels(s_labels)
    ax.set_xticks([0])
    ax.set_xticklabels(["IDGX2"])
    ax.set_title("Substance-use outcomes\n(predicted: red / +)")

    # Right: cardiometabolic (predicted -)
    ax = axes[1]
    c_vals = cardio["beta"].values
    c_labels = cardio["outcome"].tolist()
    im1 = ax.imshow(c_vals.reshape(-1, 1), cmap="RdBu_r", vmin=-vmax, vmax=vmax, aspect="auto")
    ax.set_yticks(range(len(c_labels)))
    ax.set_yticklabels(c_labels)
    ax.set_xticks([0])
    ax.set_xticklabels(["IDGX2"])
    ax.set_title("Cardiometabolic outcomes\n(observed: blue / -)")

    cbar = fig.colorbar(im1, ax=axes, fraction=0.04, pad=0.06, location="right")
    cbar.set_label("β (raw scale)")
    fig.suptitle("Outcome-specificity inversion: IDGX2 popularity vs. substance-use and cardiometabolic outcomes")
    _save(fig, FIG_PRIMARY / "outcome_specificity_heatmap.png")


def popularity_subst_forest() -> None:
    """Forest plot of IDGX2 -> substance-use beta with 95% CI."""
    df = pd.read_csv(TABLES_PRIMARY / "popularity_subst_matrix.csv").copy()
    df = df.sort_values(["wave", "outcome"]).reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    y = np.arange(len(df))
    ax.errorbar(
        df["beta"], y,
        xerr=1.96 * df["se"],
        fmt="o", color="#c44e52", ecolor="#888", capsize=3,
    )
    ax.axvline(0.0, linestyle=":", color="black", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r.outcome}  ({r.wave})" for _, r in df.iterrows()])
    ax.invert_yaxis()
    ax.set_xlabel("β (per-1-unit IDGX2; cluster-SE)")
    ax.set_title("IDGX2 → substance-use outcomes\n(L0+L1+AHPVT, 95% CI)")
    _save(fig, FIG_PRIMARY / "popularity_subst_forest.png")


def quintile_panels() -> None:
    """Small multiples: outcome mean by IDGX2 quintile (Q1 baseline)."""
    df = pd.read_csv(TABLES_SENS / "popularity_subst_quintiles.csv")
    outcomes = df["outcome"].unique()
    n = len(outcomes)
    cols = 4
    rows = int(np.ceil(n / cols))
    fig, axes = plt.subplots(rows, cols, figsize=(3.0 * cols, 2.4 * rows), sharex=True)
    axes = np.atleast_2d(axes)
    for i, oc in enumerate(outcomes):
        ax = axes[i // cols, i % cols]
        sub = df[df.outcome == oc].copy()
        # Q1 is the omitted reference (β = 0); add as Q1.
        q_index = [1] + [int(q.lstrip("q")) for q in sub["quintile"]]
        beta = [0.0] + sub["beta_vs_q1"].tolist()
        ci_lo = [0.0] + sub["ci_lo"].tolist()
        ci_hi = [0.0] + sub["ci_hi"].tolist()
        ax.errorbar(q_index, beta,
                    yerr=[np.subtract(beta, ci_lo), np.subtract(ci_hi, beta)],
                    fmt="o-", color="#c44e52", ecolor="#888", capsize=2)
        ax.axhline(0.0, linestyle=":", color="black", linewidth=0.6)
        ax.set_title(oc, fontsize=10)
        ax.set_xlabel("IDGX2 quintile")
        ax.set_ylabel("β vs. Q1")
    # Hide any unused subplots.
    for j in range(n, rows * cols):
        axes[j // cols, j % cols].axis("off")
    fig.suptitle("Quintile dose-response of IDGX2 on substance-use outcomes (Q1 reference)")
    fig.tight_layout()
    _save(fig, FIG_SENS / "popularity_subst_quintiles.png")


def fig_sensitivity_panel() -> Path:
    """Three-panel sensitivity figure for popularity-and-substance-use."""
    ev_path = TABLES_SENS / "popularity_subst_evalue_chinn2000.csv"
    cf_path = TABLES_SENS / "popularity_subst_cornfield_grid.csv"
    et_path = TABLES_SENS / "popularity_subst_eta_tilt.csv"
    return plot_sensitivity_panel(
        FIG_SENS / "popularity_subst_sensitivity_panel.png",
        title=("Popularity → substance use — sensitivity panel\n"
               "(a) E-value per cell · (b) Cornfield B grid · (c) η-tilt ATE surface"),
        evalue_table=pd.read_csv(ev_path) if (ev_path.exists() and ev_path.stat().st_size > 8) else pd.DataFrame(),
        cornfield_table=pd.read_csv(cf_path) if (cf_path.exists() and cf_path.stat().st_size > 8) else pd.DataFrame(),
        eta_tilt_table=pd.read_csv(et_path) if (et_path.exists() and et_path.stat().st_size > 8) else pd.DataFrame(),
        eta_continuous_note=(
            "η-tilt: top-vs-bottom-quintile IDGX2 binarisation."
        ),
    )


def main() -> None:
    print("Building popularity-and-substance-use figures ...")
    outcome_specificity_heatmap()
    popularity_subst_forest()
    quintile_panels()
    fig_sensitivity_panel()
    print("Done.")


if __name__ == "__main__":
    main()

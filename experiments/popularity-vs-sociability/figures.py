"""Figures for popularity-vs-sociability (EXP-POPSOC).

Two primary plots, all with descriptive titles baked into the figure
(per the chart-explanation convention -- see ../README.md).

  1. primary/popsoc_beta_heatmap.png
        2 x 13 standardized-beta heatmap with significance markers, one row
        per exposure (`IDGX2`, `ODGX2`) and one column per outcome.

  2. primary/popsoc_pairedboot_forest.png
        Forest plot of the paired-bootstrap contrast `Delta_beta = beta_in -
        beta_out` per outcome with 95% bootstrap CI. The single-number-per-
        outcome view of the experiment's primary inferential target.

Reads:
  ./tables/primary/popsoc_primary.csv             (26 rows)
  ./tables/primary/popsoc_paired_bootstrap.csv    (13 rows)

Writes:
  ./figures/primary/popsoc_beta_heatmap.png
  ./figures/primary/popsoc_pairedboot_forest.png
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
FIGS_PRIMARY.mkdir(parents=True, exist_ok=True)
FIGS_SENS.mkdir(parents=True, exist_ok=True)

# Allow shared sensitivity-panel helper to be imported.
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analysis.sensitivity_panel import plot_sensitivity_panel  # noqa: E402


# ---------------------------------------------------------------------------
# 1. 2 x 13 standardized-beta heatmap
# ---------------------------------------------------------------------------
def fig_beta_heatmap(primary: pd.DataFrame) -> Path:
    """2 x 13 heatmap of standardized beta with significance asterisks.

    `primary` columns expected: exposure, outcome, outcome_group, beta, p, sig.
    Standardisation: column-wise z over the two exposures' beta within an
    outcome (so the heatmap reads "which exposure dominates" rather than
    raw effect magnitudes which differ across outcome scales).
    """
    df = primary.copy()
    # Pivot to (exposure x outcome) matrix.
    beta = df.pivot(index="exposure", columns="outcome", values="beta")
    sig = df.pivot(index="exposure", columns="outcome", values="sig")
    # Within-outcome standardisation: divide each column by its absolute max
    # (keeps the sign + relative size, makes the heatmap comparable across
    # outcomes of different scales).
    norm = beta.copy()
    col_max = beta.abs().max(axis=0).replace(0, np.nan)
    for c in beta.columns:
        norm[c] = beta[c] / col_max[c]

    fig, ax = plt.subplots(figsize=(10, 3.0))
    vmax = 1.0
    im = ax.imshow(norm.values, cmap="RdBu_r", vmin=-vmax, vmax=vmax,
                   aspect="auto")
    ax.set_xticks(np.arange(len(norm.columns)))
    ax.set_xticklabels(norm.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(norm.index)))
    ax.set_yticklabels(norm.index, fontsize=9)
    # Significance markers: '*' for p<0.05.
    for i, exp_name in enumerate(norm.index):
        for j, oc_name in enumerate(norm.columns):
            mark = "*" if bool(sig.loc[exp_name, oc_name]) else ""
            if mark:
                ax.text(j, i, mark, ha="center", va="center",
                        color="black", fontsize=10, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02,
                 label="beta / max(|beta|) within outcome")
    ax.set_title(
        "Popularity (IDGX2) vs sociability (ODGX2) per outcome\n"
        "Standardised WLS beta (cluster-robust); * marks p<0.05",
        fontsize=11,
    )
    fig.tight_layout()
    out = FIGS_PRIMARY / "popsoc_beta_heatmap.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# 2. Paired-bootstrap forest of Delta_beta = beta_in - beta_out
# ---------------------------------------------------------------------------
def fig_pairedboot_forest(bootstrap: pd.DataFrame,
                          primary: pd.DataFrame | None = None) -> Path:
    """Forest of `Delta_beta` +/- bootstrap 95% CI per outcome.

    Sign convention: positive `Delta_beta` means popularity (IDGX2) dominates
    sociability (ODGX2); negative means the reverse.
    """
    df = bootstrap.dropna(subset=["delta_beta"]).copy()
    # If primary is provided, attach outcome_group for color-coding.
    if primary is not None and "outcome_group" in primary.columns:
        og = (primary[["outcome", "outcome_group"]]
              .drop_duplicates().set_index("outcome")["outcome_group"])
        df["outcome_group"] = df["outcome"].map(og)
    else:
        df["outcome_group"] = "unknown"

    # Stable color palette by group (matches the multi-outcome screen aesthetic).
    palette = {
        "cognitive":       "#4C72B0",
        "cardiometabolic": "#DD8452",
        "mental_health":   "#55A868",
        "functional":      "#C44E52",
        "ses":             "#8172B3",
        "unknown":         "#888888",
    }
    colors = df["outcome_group"].map(palette).fillna("#888888")

    fig, ax = plt.subplots(figsize=(7.5, 0.4 * len(df) + 1.5))
    ys = np.arange(len(df))
    # Colour-coded per-row error bars.
    for y, (_, r), color in zip(ys, df.iterrows(), colors):
        ax.errorbar(
            r["delta_beta"], y,
            xerr=[[r["delta_beta"] - r["delta_ci_lo"]],
                  [r["delta_ci_hi"] - r["delta_beta"]]],
            fmt="o", color=color, ecolor=color, capsize=3,
        )
    ax.axvline(0.0, color="red", linestyle="--", linewidth=1)
    ax.set_yticks(ys)
    ax.set_yticklabels(df["outcome"])
    ax.set_xlabel("Delta_beta = beta_IDGX2 - beta_ODGX2")
    ax.set_title(
        "Cross-exposure contrast: popularity vs sociability per outcome\n"
        "Paired cluster-bootstrap on CLUSTER2 (200 iterations); 95% percentile CI",
        fontsize=11,
    )
    # Group legend.
    from matplotlib.patches import Patch
    handles = [Patch(color=c, label=g) for g, c in palette.items()
               if g in df["outcome_group"].unique()]
    if handles:
        ax.legend(handles=handles, loc="best", fontsize=8, frameon=True)
    fig.tight_layout()
    out = FIGS_PRIMARY / "popsoc_pairedboot_forest.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# 3. Sensitivity panel (E-value bars + Cornfield heatmap + η-tilt surface)
# ---------------------------------------------------------------------------
def fig_sensitivity_panel() -> Path:
    """Three-panel sensitivity figure for popularity-vs-sociability.

    Reads the Chinn-2000-scaled E-value table, the Cornfield bias-factor grid,
    and the binary-A η-tilt sweep produced by ``run.py:run_sensitivity_extended``.
    Both `IDGX2` and `ODGX2` are continuous in-/out-degree, so the η-tilt panel
    operates on a top-quintile-vs-bottom-quintile contrast (documented in the
    panel title via the ``binarisation`` column).
    """
    ev_path = TABLES_SENS / "popsoc_evalue_chinn2000.csv"
    cf_path = TABLES_SENS / "popsoc_cornfield_grid.csv"
    et_path = TABLES_SENS / "popsoc_eta_tilt.csv"
    ev = pd.read_csv(ev_path) if (ev_path.exists() and ev_path.stat().st_size > 8) else pd.DataFrame()
    cf = pd.read_csv(cf_path) if (cf_path.exists() and cf_path.stat().st_size > 8) else pd.DataFrame()
    et = pd.read_csv(et_path) if (et_path.exists() and et_path.stat().st_size > 8) else pd.DataFrame()
    return plot_sensitivity_panel(
        FIGS_SENS / "popsoc_sensitivity_panel.png",
        title=("Popularity vs sociability — sensitivity panel\n"
               "(a) E-value per cell · (b) Cornfield B grid · "
               "(c) η-tilt ATE surface"),
        evalue_table=ev,
        cornfield_table=cf,
        eta_tilt_table=et,
        eta_continuous_note=(
            "Continuous-A note: IDGX2/ODGX2 are continuous in-/out-degree;"
            " η-tilt sweep is on a top-quintile-vs-bottom-quintile contrast."
        ),
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    primary = pd.read_csv(TABLES_PRIMARY / "popsoc_primary.csv")
    bootstrap = pd.read_csv(TABLES_PRIMARY / "popsoc_paired_bootstrap.csv")
    fig_beta_heatmap(primary)
    fig_pairedboot_forest(bootstrap, primary)
    fig_sensitivity_panel()
    print("Figures written to:", FIGS_PRIMARY, "and", FIGS_SENS)


if __name__ == "__main__":
    main()

"""Figures for ego-network-density (EXP-EGODEN).

Two plots, all with descriptive titles baked into the figure (per the
chart-explanation convention -- see ../README.md).

  1. primary/egoden_beta_heatmap.png
        4 x 6 standardized-beta heatmap with significance markers, one row
        per density measure (`RCHDEN`, `ESDEN`, `ERDEN`, `ESRDEN`) and one
        column per outcome (focused 6: 3 mental + 2 SES + 1 cognitive).

  2. sensitivity/egoden_size_conditioning.png
        Paired-bar diagnostic showing beta WITH-`REACH3` vs WITHOUT-`REACH3`
        per (density measure, outcome) cell. Makes the size confound
        quantitatively visible -- the load-bearing identification move per
        Burt's structural-holes interpretation.

Reads:
  ./tables/primary/egoden_primary.csv             (24 rows, with REACH3)
  ./tables/sensitivity/egoden_no_reach3.csv       (24 rows, without REACH3)

Writes:
  ./figures/primary/egoden_beta_heatmap.png
  ./figures/sensitivity/egoden_size_conditioning.png
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
# 1. 4 x 6 standardized-beta heatmap (with REACH3 conditioning)
# ---------------------------------------------------------------------------
def fig_beta_heatmap(primary: pd.DataFrame) -> Path:
    """4 x 6 heatmap of standardized beta for the four density measures
    against the focused outcome subset, all conditioned on `REACH3`.

    Standardisation: within-outcome normalisation by the largest-|β| across
    the four density measures for that outcome, so the heatmap reads
    "which density measure dominates" rather than raw magnitudes.
    """
    df = primary.copy()
    beta = df.pivot(index="exposure", columns="outcome", values="beta")
    sig = df.pivot(index="exposure", columns="outcome", values="sig")
    norm = beta.copy()
    col_max = beta.abs().max(axis=0).replace(0, np.nan)
    for c in beta.columns:
        norm[c] = beta[c] / col_max[c]

    fig, ax = plt.subplots(figsize=(8.0, 3.5))
    vmax = 1.0
    im = ax.imshow(norm.values, cmap="RdBu_r", vmin=-vmax, vmax=vmax,
                   aspect="auto")
    ax.set_xticks(np.arange(len(norm.columns)))
    ax.set_xticklabels(norm.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(np.arange(len(norm.index)))
    ax.set_yticklabels(norm.index, fontsize=9)
    for i, exp_name in enumerate(norm.index):
        for j, oc_name in enumerate(norm.columns):
            mark = "*" if bool(sig.loc[exp_name, oc_name]) else ""
            if mark:
                ax.text(j, i, mark, ha="center", va="center",
                        color="black", fontsize=10, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02,
                 label="beta / max(|beta|) within outcome")
    ax.set_title(
        "Ego-network density (4 measures) vs focused 6 outcomes\n"
        "Standardised WLS beta, ALL conditioned on REACH3 (egonet size); "
        "* marks p<0.05",
        fontsize=11,
    )
    fig.tight_layout()
    out = FIGS_PRIMARY / "egoden_beta_heatmap.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# 2. Size-conditioning sensitivity: beta with vs without REACH3
# ---------------------------------------------------------------------------
def fig_size_conditioning(primary: pd.DataFrame, no_reach3: pd.DataFrame) -> Path:
    """Paired bars of beta(with-REACH3) vs beta(without-REACH3) per cell.

    Visualises the size-confound bias quantitatively. Cells where the bars
    flip sign across conditioning indicate the unconditioned beta is size-
    dominated rather than density-dominated.
    """
    # Merge the two tables on (exposure, outcome).
    a = primary[["exposure", "outcome", "outcome_group", "beta"]].rename(
        columns={"beta": "beta_with_reach3"})
    b = no_reach3[["exposure", "outcome", "beta"]].rename(
        columns={"beta": "beta_no_reach3"})
    merged = a.merge(b, on=["exposure", "outcome"], how="left")
    merged["cell"] = merged["exposure"] + " | " + merged["outcome"]
    merged = merged.dropna(subset=["beta_with_reach3", "beta_no_reach3"])
    merged = merged.sort_values(["exposure", "outcome"]).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(8.5, max(4.0, 0.25 * len(merged))))
    ys = np.arange(len(merged))
    width = 0.4
    ax.barh(ys - width / 2, merged["beta_with_reach3"], height=width,
            color="#4C72B0", label="with REACH3 (primary)", edgecolor="white")
    ax.barh(ys + width / 2, merged["beta_no_reach3"], height=width,
            color="#DD8452", label="without REACH3 (size-confounded)",
            edgecolor="white")
    ax.axvline(0.0, color="black", linewidth=0.7)
    ax.set_yticks(ys)
    ax.set_yticklabels(merged["cell"], fontsize=7)
    ax.set_xlabel("WLS beta on density measure")
    ax.set_title(
        "Size-conditioning diagnostic: density beta with vs without REACH3\n"
        "Per (density measure, outcome) cell; sign-flips reveal size-dominated cells",
        fontsize=11,
    )
    ax.legend(loc="best", fontsize=8, frameon=True)
    fig.tight_layout()
    out = FIGS_SENS / "egoden_size_conditioning.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Sensitivity panel — E-value bars + Cornfield grid + η-tilt surface
# ---------------------------------------------------------------------------
def fig_sensitivity_panel() -> Path:
    """Three-panel sensitivity figure for ego-network-density.

    Reads the Chinn-2000-scaled E-value, Cornfield bias-factor grid, and
    binary-A η-tilt sweep produced by ``run.py:run_sensitivity_extended``. All
    four density exposures are continuous, so the η-tilt panel uses a
    top-quintile-vs-bottom-quintile binarisation (``binarisation`` column in
    the eta-tilt CSV).
    """
    ev_path = TABLES_SENS / "egoden_evalue_chinn2000.csv"
    cf_path = TABLES_SENS / "egoden_cornfield_grid.csv"
    et_path = TABLES_SENS / "egoden_eta_tilt.csv"
    ev = pd.read_csv(ev_path) if (ev_path.exists() and ev_path.stat().st_size > 8) else pd.DataFrame()
    cf = pd.read_csv(cf_path) if (cf_path.exists() and cf_path.stat().st_size > 8) else pd.DataFrame()
    et = pd.read_csv(et_path) if (et_path.exists() and et_path.stat().st_size > 8) else pd.DataFrame()
    return plot_sensitivity_panel(
        FIGS_SENS / "egoden_sensitivity_panel.png",
        title=("Ego-network density — sensitivity panel\n"
               "(a) E-value per cell · (b) Cornfield B grid · "
               "(c) η-tilt ATE surface"),
        evalue_table=ev,
        cornfield_table=cf,
        eta_tilt_table=et,
        eta_continuous_note=(
            "Continuous-A note: density measures are continuous;"
            " η-tilt sweep is on a top-quintile-vs-bottom-quintile contrast."
        ),
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    primary = pd.read_csv(TABLES_PRIMARY / "egoden_primary.csv")
    no_reach3 = pd.read_csv(TABLES_SENS / "egoden_no_reach3.csv")
    fig_beta_heatmap(primary)
    fig_size_conditioning(primary, no_reach3)
    fig_sensitivity_panel()
    print("Figures written to:", FIGS_PRIMARY, FIGS_SENS)


if __name__ == "__main__":
    main()

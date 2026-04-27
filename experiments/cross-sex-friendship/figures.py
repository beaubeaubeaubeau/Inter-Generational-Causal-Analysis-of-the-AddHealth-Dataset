"""cross-sex-friendship — figure generators.

Two planned figures:

  1. ``cross_sex_forest.png`` (primary) — for each of the 13 outcomes,
     a 4-cell forest plot of adjusted cell means (with 95% CI based on
     the WLS intercept SE), faceted by stratification scheme. Overlaid
     reference lines mark the within-sex friend=no baseline so the
     within-sex *contrast* is visually obvious.

  2. ``cross_sex_heatmap.png`` (primary) — 8 × 13 signed-mean heatmap.
     Rows are (stratification, sex, friend-present); columns are outcomes.
     Z-scored within outcome so cross-outcome cells are visually
     comparable. The headline visual.

Reads:
  ./tables/primary/cross_sex_matrix.csv

Writes:
  ./figures/primary/cross_sex_forest.png
  ./figures/primary/cross_sex_heatmap.png
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
from analysis.plot_style import GROUP_COLORS  # noqa: E402
from analysis.sensitivity_panel import plot_sensitivity_panel  # noqa: E402

plot_style.setup()

TABLES_PRIMARY = HERE / "tables" / "primary"
TABLES_SENS = HERE / "tables" / "sensitivity"
FIG_PRIMARY = HERE / "figures" / "primary"
FIG_SENS = HERE / "figures" / "sensitivity"
FIG_PRIMARY.mkdir(parents=True, exist_ok=True)
FIG_SENS.mkdir(parents=True, exist_ok=True)
import pandas as _pd_for_sens  # noqa: E402


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def cross_sex_forest() -> None:
    """Per-outcome 4-cell forest, faceted by stratification."""
    df = pd.read_csv(TABLES_PRIMARY / "cross_sex_matrix.csv")
    outcomes = list(df["outcome"].unique())
    strats = list(df["stratification"].unique())
    n_o = len(outcomes)
    fig, axes = plt.subplots(n_o, len(strats), figsize=(7.5, max(2.0 * n_o, 4.0)),
                             sharex=False, squeeze=False)
    for i, oc in enumerate(outcomes):
        for j, strat in enumerate(strats):
            ax = axes[i, j]
            sub = df[(df.outcome == oc) & (df.stratification == strat)].copy()
            sub["cell_label"] = sub["sex"].str.cat(sub["friend_present"], sep=" / ")
            cell_order = ["female / no", "female / yes", "male / no", "male / yes"]
            sub = sub.set_index("cell_label").reindex(cell_order).reset_index()
            y = np.arange(len(sub))
            ax.errorbar(
                sub["adj_mean"], y,
                xerr=1.96 * sub["adj_se"],
                fmt="o", color="#4c72b0", ecolor="#888", capsize=2,
            )
            ax.set_yticks(y)
            ax.set_yticklabels(sub["cell_label"], fontsize=7)
            ax.invert_yaxis()
            if i == 0:
                ax.set_title(strat, fontsize=9)
            if j == 0:
                ax.set_ylabel(oc, fontsize=8)
            ax.tick_params(axis="x", labelsize=7)
    fig.suptitle("Cross-sex friendship — adjusted cell means by (sex, friend-present)\nLeft column: HAVEBMF stratification; right column: HAVEBFF stratification")
    fig.tight_layout()
    _save(fig, FIG_PRIMARY / "cross_sex_forest.png")


def cross_sex_heatmap() -> None:
    """8-row × 13-column signed-mean heatmap (z-scored within outcome)."""
    df = pd.read_csv(TABLES_PRIMARY / "cross_sex_matrix.csv")
    df["row_label"] = (
        df["stratification"].str.replace("BIO_SEX × ", "", regex=False)
        + " | " + df["sex"] + " | " + df["friend_present"]
    )
    pvt = df.pivot_table(index="row_label", columns="outcome", values="adj_mean", aggfunc="first")
    # Z-score within outcome (column).
    pvt_z = (pvt - pvt.mean()) / pvt.std(ddof=0)
    # Order rows and columns deterministically.
    row_order = [
        "HAVEBMF | female | no",  "HAVEBMF | female | yes",
        "HAVEBMF | male   | no",  "HAVEBMF | male   | yes",
        "HAVEBFF | female | no",  "HAVEBFF | female | yes",
        "HAVEBFF | male   | no",  "HAVEBFF | male   | yes",
    ]
    row_order = [r for r in row_order if r.replace("   ", " ") in pvt_z.index]
    # Tolerate label whitespace differences.
    pvt_z.index = pvt_z.index.str.replace(r"\s+", " ", regex=True)
    fig, ax = plt.subplots(figsize=(11, 5))
    im = ax.imshow(pvt_z.values, cmap="RdBu_r", aspect="auto", vmin=-2.5, vmax=2.5)
    ax.set_xticks(range(len(pvt_z.columns)))
    ax.set_xticklabels(pvt_z.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(pvt_z.index)))
    ax.set_yticklabels(pvt_z.index, fontsize=8)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Adjusted cell mean (z-scored within outcome)")
    ax.set_title("Sex × friend-sex × outcome — adjusted cell means\nRows: stratification | sex | friend present;  cols: outcome (z-scored within column)")
    fig.tight_layout()
    _save(fig, FIG_PRIMARY / "cross_sex_heatmap.png")


def fig_sensitivity_panel() -> Path:
    """Three-panel sensitivity figure for cross-sex-friendship.
    Built on the between-cell contrasts (cell-mean differences) since the
    primary outputs are adjusted cell means rather than regression β.
    """
    ev_path = TABLES_SENS / "cross_sex_evalue_chinn2000.csv"
    cf_path = TABLES_SENS / "cross_sex_cornfield_grid.csv"
    et_path = TABLES_SENS / "cross_sex_eta_tilt.csv"
    return plot_sensitivity_panel(
        FIG_SENS / "cross_sex_sensitivity_panel.png",
        title=("Cross-sex friendship — sensitivity panel\n"
               "Between-cell contrasts (friend present − absent within sex stratum)\n"
               "(a) E-value · (b) Cornfield B grid · (c) η-tilt ATE surface"),
        evalue_table=_pd_for_sens.read_csv(ev_path) if (ev_path.exists() and ev_path.stat().st_size > 8) else _pd_for_sens.DataFrame(),
        cornfield_table=_pd_for_sens.read_csv(cf_path) if (cf_path.exists() and cf_path.stat().st_size > 8) else _pd_for_sens.DataFrame(),
        eta_tilt_table=_pd_for_sens.read_csv(et_path) if (et_path.exists() and et_path.stat().st_size > 8) else _pd_for_sens.DataFrame(),
        eta_continuous_note=(
            "η-tilt: raw 0/1 friend-indicator within the relevant sex stratum."
        ),
    )


def main() -> None:
    print("Building cross-sex-friendship figures ...")
    cross_sex_forest()
    cross_sex_heatmap()
    fig_sensitivity_panel()
    print("Done.")


if __name__ == "__main__":
    main()

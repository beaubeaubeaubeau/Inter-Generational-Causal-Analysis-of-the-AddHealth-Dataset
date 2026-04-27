"""lonely-at-the-top — figure generators.

Three planned figures:

  1. ``paradox_interaction.png`` (primary) — predicted-outcome surface
     plot over the (z(IDGX2), z(H1FS13)) grid, overlaid with the four
     median-split corners. The headline visual: a non-flat surface with
     the high-pop/high-lonely corner deviating from the additive plane
     is the paradox.

  2. ``lonely_top_forest.png`` (primary) — interaction coefficient β₃
     ± 1.96·SE per outcome under the primary spec, with main-effect
     coefficients shown alongside for context.

  3. ``lonely_top_4cell_descriptive.png`` (sensitivity) — bar plot of
     weighted cell means in the 2x2, with cell N annotated and an
     "under-powered" badge on cells with N < 150. Explicitly framed as
     descriptive only.

Reads:
  ./tables/primary/lonely_top_matrix.csv
  ./tables/sensitivity/lonely_top_2x2_descriptive.csv
  ./tables/sensitivity/lonely_top_interaction_surface.csv

Writes:
  ./figures/primary/paradox_interaction.png
  ./figures/primary/lonely_top_forest.png
  ./figures/sensitivity/lonely_top_4cell_descriptive.png
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


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def paradox_interaction() -> None:
    """Surface plot of predicted outcome over (z_pop, z_lone) grid."""
    surf = pd.read_csv(TABLES_SENS / "lonely_top_interaction_surface.csv")
    if surf.empty:
        print("WARN: surface CSV empty — skipping paradox_interaction.")
        return
    pivot = surf.pivot(index="z_lone", columns="z_pop", values="pred_outcome")
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(
        pivot.values,
        extent=[pivot.columns.min(), pivot.columns.max(),
                pivot.index.min(), pivot.index.max()],
        origin="lower", aspect="auto", cmap="RdBu_r",
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Predicted H4BMI")
    # Mark the four median-split corners.
    for zp in (-1, 1):
        for zl in (-1, 1):
            ax.scatter(zp, zl, color="black", s=40, zorder=5)
            ax.annotate(
                f"({zp:+d},{zl:+d})", (zp, zl),
                textcoords="offset points", xytext=(6, 6), fontsize=8,
            )
    ax.set_xlabel("z(IDGX2)")
    ax.set_ylabel("z(H1FS13)")
    ax.set_title("Paradox interaction surface\nPredicted H4BMI by (popularity, loneliness)")
    _save(fig, FIG_PRIMARY / "paradox_interaction.png")


def lonely_top_forest() -> None:
    """Interaction β₃ ± 1.96·SE per outcome (primary spec)."""
    df = pd.read_csv(TABLES_PRIMARY / "lonely_top_matrix.csv")
    df = df[df.adj == "L0+L1+AHPVT"].sort_values("outcome").reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    y = np.arange(len(df))
    ax.errorbar(
        df["beta_inter"], y,
        xerr=1.96 * df["se_inter"],
        fmt="o", color="#8172b2", ecolor="#888", capsize=3,
    )
    ax.axvline(0.0, linestyle=":", color="black", linewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels(df["outcome"].tolist())
    ax.invert_yaxis()
    ax.set_xlabel("β₃ on z(IDGX2) × z(H1FS13)  (cluster-SE 95% CI)")
    ax.set_title("Paradox interaction coefficient per outcome\n(L0+L1+AHPVT, both main effects forced in)")
    _save(fig, FIG_PRIMARY / "lonely_top_forest.png")


def four_cell_descriptive() -> None:
    """2x2 weighted cell-mean bar chart with cell-N annotation."""
    df = pd.read_csv(TABLES_SENS / "lonely_top_2x2_descriptive.csv")
    outcomes = df["outcome"].unique()
    cell_order = ["low_pop_low_lone", "low_pop_high_lone",
                  "high_pop_low_lone", "high_pop_high_lone"]
    cell_label = {
        "low_pop_low_lone":   "Low pop\nLow lone",
        "low_pop_high_lone":  "Low pop\nHigh lone",
        "high_pop_low_lone":  "High pop\nLow lone",
        "high_pop_high_lone": "High pop\nHigh lone\n(paradox cell)",
    }
    n = len(outcomes)
    fig, axes = plt.subplots(1, n, figsize=(3.0 * n, 4), sharey=False)
    axes = np.atleast_1d(axes)
    for i, oc in enumerate(outcomes):
        ax = axes[i]
        sub = df[df.outcome == oc].set_index("cell").loc[cell_order]
        means = sub["weighted_mean"].values
        ns = sub["n_cell"].values
        underpwr = sub["below_positivity_floor"].values
        colors = ["#cccccc" if u else "#55a868" for u in underpwr]
        bars = ax.bar(range(4), means, color=colors, edgecolor="black")
        for j, (b, n_j, u) in enumerate(zip(bars, ns, underpwr)):
            ax.text(j, b.get_height(), f"N={n_j}", ha="center", va="bottom", fontsize=8)
            if u:
                ax.text(j, b.get_height() * 0.5, "under-pwr",
                        ha="center", va="center", fontsize=7, color="darkred", rotation=90)
        ax.set_xticks(range(4))
        ax.set_xticklabels([cell_label[c] for c in cell_order], fontsize=7)
        ax.set_title(oc, fontsize=10)
    fig.suptitle("2x2 descriptive cell means (under-powered cells flagged grey)\nDescriptive only — primary estimand is the continuous interaction")
    fig.tight_layout()
    _save(fig, FIG_SENS / "lonely_top_4cell_descriptive.png")


def fig_sensitivity_panel() -> Path:
    """Three-panel sensitivity figure for lonely-at-the-top."""
    ev_path = TABLES_SENS / "lonely_top_evalue_chinn2000.csv"
    cf_path = TABLES_SENS / "lonely_top_cornfield_grid.csv"
    et_path = TABLES_SENS / "lonely_top_eta_tilt.csv"
    return plot_sensitivity_panel(
        FIG_SENS / "lonely_top_sensitivity_panel.png",
        title=("Lonely-at-the-top — sensitivity panel\n"
               "(a) E-value per cell · (b) Cornfield B grid · (c) η-tilt ATE surface"),
        evalue_table=pd.read_csv(ev_path) if (ev_path.exists() and ev_path.stat().st_size > 8) else pd.DataFrame(),
        cornfield_table=pd.read_csv(cf_path) if (cf_path.exists() and cf_path.stat().st_size > 8) else pd.DataFrame(),
        eta_tilt_table=pd.read_csv(et_path) if (et_path.exists() and et_path.stat().st_size > 8) else pd.DataFrame(),
        eta_continuous_note=(
            "η-tilt: top-vs-bottom-quintile of the standardised "
            "z(IDGX2)×z(H1FS13) paradox product."
        ),
    )


def main() -> None:
    print("Building lonely-at-the-top figures ...")
    paradox_interaction()
    lonely_top_forest()
    four_cell_descriptive()
    fig_sensitivity_panel()
    print("Done.")


if __name__ == "__main__":
    main()

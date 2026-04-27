"""Figures for friendship-quality-vs-quantity (EXP-QVQ).

Single primary plot, all with descriptive titles baked into the figure
(per the chart-explanation convention -- see ../README.md).

  1. primary/qvq_beta_heatmap.png
        3 x 13 standardized-beta heatmap with significance markers, one row
        per friendship exposure (`FRIEND_DISCLOSURE_ANY` quality,
        `FRIEND_N_NOMINEES` quantity, `FRIEND_CONTACT_SUM` frequency) and one
        column per outcome. Joint-fit marginal-conditional beta from the
        same head-to-head regression per outcome.

Reads:
  ./tables/primary/qvq_primary.csv   (39 rows = 3 x 13)

Writes:
  ./figures/primary/qvq_beta_heatmap.png
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

ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analysis.sensitivity_panel import plot_sensitivity_panel  # noqa: E402


# ---------------------------------------------------------------------------
# 1. 3 x 13 standardized-beta heatmap
# ---------------------------------------------------------------------------
def _exposure_sds() -> dict:
    """Compute per-exposure SD on the analytic frame so we can convert
    natural-unit beta -> per-SD-of-exposure beta. The three exposures live
    on incommensurable scales: binary (0/1), count (0-10), sum (0-40);
    naive comparison of raw beta is dominated by scale, not by signal.
    """
    REPO_ROOT = HERE.parent.parent
    cache = REPO_ROOT / "cache"
    df = pd.read_parquet(cache / "analytic_w1_full.parquet")
    return {
        c: float(pd.to_numeric(df[c], errors="coerce").std(ddof=1))
        for c in ("FRIEND_DISCLOSURE_ANY", "FRIEND_N_NOMINEES",
                  "FRIEND_CONTACT_SUM")
        if c in df.columns
    }


def fig_beta_heatmap(primary: pd.DataFrame) -> Path:
    """3 x 13 heatmap of joint-fit marginal-conditional beta with sig markers.

    Cohen's-d-style standardisation: per-SD-of-exposure beta (raw beta x
    SD_X), so the three exposures (binary 0/1, count 0-10, sum 0-40) are
    on a comparable footing. Then within-outcome normalisation by
    max(|standardised beta|) so the heatmap reads "which friendship
    measure dominates per SD of itself" rather than which has the biggest
    natural-unit jump (which is a pure scale artifact for binary vars).
    """
    df = primary.copy()
    sds = _exposure_sds()
    df["beta_std"] = df.apply(
        lambda r: r["beta"] * sds.get(r["exposure"], 1.0), axis=1
    )
    beta = df.pivot(index="exposure", columns="outcome", values="beta_std")
    sig = df.pivot(index="exposure", columns="outcome", values="sig")
    norm = beta.copy()
    col_max = beta.abs().max(axis=0).replace(0, np.nan)
    for c in beta.columns:
        norm[c] = beta[c] / col_max[c]

    fig, ax = plt.subplots(figsize=(10.0, 3.5))
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
                 label="per-SD-of-exposure beta / max(|.|) within outcome")
    ax.set_title(
        "Friendship quality vs quantity vs frequency, head-to-head joint fit\n"
        "Cohen's-d-style: per-SD-of-exposure beta, normalised within outcome; "
        "* marks p<0.05",
        fontsize=11,
    )
    fig.tight_layout()
    out = FIGS_PRIMARY / "qvq_beta_heatmap.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


# ---------------------------------------------------------------------------
# Sensitivity panel — E-value bars + Cornfield grid + η-tilt surface
# ---------------------------------------------------------------------------
def fig_sensitivity_panel() -> Path:
    """Three-panel sensitivity figure for friendship-quality-vs-quantity.

    Reads the Chinn-2000-scaled E-value, Cornfield bias-factor grid, and
    η-tilt sweep produced by ``run.py:run_sensitivity_extended``. Mixed-A:
    `FRIEND_DISCLOSURE_ANY` is binary so the η-tilt sweep can use the raw
    0/1 contrast; the integer-count and sum exposures fall back to a
    top-quintile-vs-bottom-quintile binarisation (annotated in the
    ``binarisation`` column of the eta-tilt CSV).
    """
    ev_path = TABLES_SENS / "qvq_evalue_chinn2000.csv"
    cf_path = TABLES_SENS / "qvq_cornfield_grid.csv"
    et_path = TABLES_SENS / "qvq_eta_tilt.csv"
    ev = pd.read_csv(ev_path) if (ev_path.exists() and ev_path.stat().st_size > 8) else pd.DataFrame()
    cf = pd.read_csv(cf_path) if (cf_path.exists() and cf_path.stat().st_size > 8) else pd.DataFrame()
    et = pd.read_csv(et_path) if (et_path.exists() and et_path.stat().st_size > 8) else pd.DataFrame()
    return plot_sensitivity_panel(
        FIGS_SENS / "qvq_sensitivity_panel.png",
        title=("Friendship quality vs quantity — sensitivity panel\n"
               "(a) E-value per cell · (b) Cornfield B grid · "
               "(c) η-tilt ATE surface"),
        evalue_table=ev,
        cornfield_table=cf,
        eta_tilt_table=et,
        eta_continuous_note=(
            "Mixed-A note: FRIEND_DISCLOSURE_ANY uses the raw binary contrast;"
            " count / sum exposures fall back to a top-quintile-vs-bottom contrast."
        ),
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    primary = pd.read_csv(TABLES_PRIMARY / "qvq_primary.csv")
    fig_beta_heatmap(primary)
    fig_sensitivity_panel()
    print("Figures written to:", FIGS_PRIMARY, "and", FIGS_SENS)


if __name__ == "__main__":
    main()

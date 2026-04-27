"""EXP-15-MULTI — cross-outcome figures.

Two charts that depict cross-outcome content (and therefore live with the
multi-outcome screen rather than with cognitive-screening):

  1. ``15_per_outcome_pcount.png`` — horizontal bar chart of "# exposures
     with p<0.05, per outcome", with the primary cognitive outcome appended
     for comparison. Bars colored by outcome group. Lives under
     ``figures/primary/``.
  2. ``15_handoff_forest.png`` — forest plot of the 4 Task 16 handoff pairs
     with standardized β ± 1.96·SE, N, and D4 rel-shift. The explicit bridge
     to the planned ``cardiometabolic-handoff`` and ``ses-handoff`` formal-
     estimation experiments. Lives under ``figures/handoff/``.

Reads:
  ./tables/primary/15_multi_outcome_matrix.csv
  ../cognitive-screening/tables/primary/14_screening_matrix.csv  (for n_cog)

Writes:
  ./figures/primary/15_per_outcome_pcount.png
  ./figures/handoff/15_handoff_forest.png
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

from analysis import CACHE  # noqa: E402
from analysis import plot_style  # noqa: E402
from analysis.plot_style import GROUP_COLORS  # noqa: E402
from analysis.cleaning import clean_var  # noqa: E402

plot_style.setup()

TABLES = HERE / "tables" / "primary"
FIG_PRIMARY = HERE / "figures" / "primary"
FIG_HANDOFF = HERE / "figures" / "handoff"
FIG_PRIMARY.mkdir(parents=True, exist_ok=True)
FIG_HANDOFF.mkdir(parents=True, exist_ok=True)

# Cross-experiment read: Agent B places the cognitive-screening primary
# matrix here. If that move hasn't landed yet, per_outcome_pcount() will
# raise FileNotFoundError — by design (no silent fallback).
COG_SCREEN_MATRIX = ROOT / "experiments" / "cognitive-screening" / "tables" / "primary" / "14_screening_matrix.csv"


def _save(fig: plt.Figure, path: Path) -> None:
    """Save a figure to ``path`` and close it (mirrors plot_style.save's contract)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def per_outcome_pcount() -> None:
    mo = pd.read_csv(TABLES / "15_multi_outcome_matrix.csv")
    counts = (
        mo.groupby(["outcome", "outcome_group"])["d1_pass"]
        .sum().reset_index().rename(columns={"d1_pass": "n_sig"})
    )

    # Append the primary cognitive outcome from cognitive-screening for comparison.
    scr = pd.read_csv(COG_SCREEN_MATRIX)
    n_cog = int((scr["d1_p"] < 0.05).sum())
    counts = pd.concat(
        [counts, pd.DataFrame([{
            "outcome": "W4_COG_COMP", "outcome_group": "cognitive", "n_sig": n_cog,
        }])],
        ignore_index=True,
    )
    counts = counts.sort_values("n_sig", ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    colors = [GROUP_COLORS[g] for g in counts["outcome_group"]]
    ax.barh(counts["outcome"], counts["n_sig"], color=colors, edgecolor="white")
    for i, n in enumerate(counts["n_sig"]):
        ax.text(n + 0.2, i, str(int(n)), va="center", fontsize=8, color="#333")
    ax.axvline(24, linestyle=":", color="#888", linewidth=0.8)
    ax.set_xlim(0, 26)
    ax.set_xlabel("# of 24 exposures with p < 0.05")
    ax.set_title(
        "Per-outcome breadth: # of W1 social exposures with screen p < 0.05\n"
        "(D1 baseline WLS, L0+L1+AHPVT spec; W4_COG_COMP shown for comparison)",
        fontsize=11,
    )

    # Legend for group colors.
    from matplotlib.patches import Patch
    handles = [Patch(color=c, label=g) for g, c in GROUP_COLORS.items()]
    ax.legend(handles=handles, loc="lower right", frameon=True, framealpha=0.9)

    out = FIG_PRIMARY / "15_per_outcome_pcount.png"
    _save(fig, out)
    print(f"Wrote {out}")


def _outcome_sd(code: str) -> float:
    """Pull the outcome's SD from the cached parquets so we can standardize beta."""
    src = CACHE / ("w4inhome.parquet" if code.startswith("H4") else "pwave5.parquet")
    s = pd.read_parquet(src, columns=[code])[code]
    return float(clean_var(s, code).std())


def handoff_forest() -> None:
    mo = pd.read_csv(TABLES / "15_multi_outcome_matrix.csv")
    HANDOFF = [
        ("IDGX2", "H4WAIST"),
        ("IDGX2", "H4BMI"),
        ("IDGX2", "H4BMICLS"),
        ("ODGX2", "H5EC1"),
    ]
    rows = []
    for exp, out in HANDOFF:
        r = mo[(mo["exposure"] == exp) & (mo["outcome"] == out)].iloc[0]
        sd_y = _outcome_sd(out)
        rows.append({
            "label": f"{exp} -> {out}",
            "outcome_label": r["outcome_label"],
            "beta_std": r["beta"] / sd_y,
            "se_std": r["se"] / sd_y,
            "beta_raw": r["beta"],
            "se_raw": r["se"],
            "n": int(r["n"]), "rs": r["d4a_rel_shift"],
            "outcome_group": r["outcome_group"],
        })
    df = pd.DataFrame(rows)
    df["lo"] = df["beta_std"] - 1.96 * df["se_std"]
    df["hi"] = df["beta_std"] + 1.96 * df["se_std"]
    # Plot in a single panel, ordered top-to-bottom as in HANDOFF.
    df = df.iloc[::-1].reset_index(drop=True)  # matplotlib draws bottom-up

    fig, ax = plt.subplots(figsize=(8.5, 3.2))
    for i, r in df.iterrows():
        color = GROUP_COLORS[r["outcome_group"]]
        ax.errorbar(
            r["beta_std"], i,
            xerr=[[r["beta_std"] - r["lo"]], [r["hi"] - r["beta_std"]]],
            fmt="o", color=color, ecolor=color,
            capsize=4, markersize=8, elinewidth=1.5,
        )
        # Right-margin annotation: raw beta + N + D4 shift.
        ax.text(
            1.02, i, f"beta_raw = {r['beta_raw']:+.3f}   N = {r['n']:,}   D4 shift = {r['rs']:.2f}",
            transform=ax.get_yaxis_transform(), ha="left", va="center",
            fontsize=8, color="#444",
        )
    ax.axvline(0, color="#888", linewidth=0.8, linestyle="--")
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df["label"], fontsize=10)
    ax.set_xlabel("Standardized beta  (per 1-unit exposure, in SDs of outcome)")
    ax.set_title(
        "Handoff candidates from the multi-outcome screen\n"
        "(4 (exposure, outcome) pairs passing both D1 and D4)",
        fontsize=11,
    )
    # Extra right-side room for annotations.
    ax.set_xlim(min(df["lo"].min(), 0) * 1.2 - 0.01, max(df["hi"].max(), 0) * 1.2 + 0.01)
    plt.subplots_adjust(right=0.55)
    ax.grid(axis="x", alpha=0.3)

    out = FIG_HANDOFF / "15_handoff_forest.png"
    _save(fig, out)
    print(f"Wrote {out}")


def beta_heatmap() -> None:
    """24 exposures × 12 outcomes; cells = β z-standardized within each outcome."""
    mo = pd.read_csv(TABLES / "15_multi_outcome_matrix.csv")
    pivot_beta = mo.pivot(index="exposure", columns="outcome", values="beta")
    pivot_p = mo.pivot(index="exposure", columns="outcome", values="p")
    # Z-standardize β within each outcome column.
    z = (pivot_beta - pivot_beta.mean(axis=0)) / pivot_beta.std(axis=0)

    fig, ax = plt.subplots(figsize=(10, 9))
    im = ax.imshow(z.values, cmap="RdBu_r", aspect="auto", vmin=-2.5, vmax=2.5)
    ax.set_xticks(range(z.shape[1]))
    ax.set_xticklabels(z.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(z.shape[0]))
    ax.set_yticklabels(z.index, fontsize=8)
    # Mark p < 0.05 cells with an asterisk.
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            p = pivot_p.iloc[i, j]
            if pd.notna(p) and p < 0.05:
                ax.text(j, i, "*", ha="center", va="center", color="black", fontsize=10)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label("β z-score (within outcome)", fontsize=9)
    ax.set_title(
        "Multi-outcome β heatmap\n"
        "(24 W1 social exposures × 12 non-cognitive outcomes; * = screen p < 0.05)",
        fontsize=11,
    )
    fig.tight_layout()
    out = FIG_PRIMARY / "multi_outcome_beta_heatmap.png"
    _save(fig, out)
    print(f"Wrote {out}")


def sig_heatmap() -> None:
    """24 exposures × 12 outcomes; cells = −log10(p) so larger = more significant."""
    mo = pd.read_csv(TABLES / "15_multi_outcome_matrix.csv")
    pivot_p = mo.pivot(index="exposure", columns="outcome", values="p")
    neg_log_p = -np.log10(pivot_p.where(pivot_p > 0, 1e-300))

    fig, ax = plt.subplots(figsize=(10, 9))
    im = ax.imshow(neg_log_p.values, cmap="viridis", aspect="auto", vmin=0, vmax=neg_log_p.max().max())
    ax.set_xticks(range(neg_log_p.shape[1]))
    ax.set_xticklabels(neg_log_p.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(neg_log_p.shape[0]))
    ax.set_yticklabels(neg_log_p.index, fontsize=8)
    cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cbar.set_label("−log10(p)", fontsize=9)
    # Reference line at p = 0.05 (-log10 = 1.30).
    cbar.ax.axhline(y=-np.log10(0.05), color="red", linewidth=1)
    ax.set_title(
        "Multi-outcome significance heatmap\n"
        "(−log10(p), 24 W1 social exposures × 12 non-cognitive outcomes; "
        "red mark on colourbar = p = 0.05)",
        fontsize=11,
    )
    fig.tight_layout()
    out = FIG_PRIMARY / "multi_outcome_sig_heatmap.png"
    _save(fig, out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    per_outcome_pcount()
    handoff_forest()
    beta_heatmap()
    sig_heatmap()

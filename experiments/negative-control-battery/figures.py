"""negative-control-battery — figure generators.

Three planned figures:

  1. ``nc_comparison.png`` (primary) — side-by-side β bars: real
     exposure → real outcome (positive control), real exposure → NC
     outcome (Direction 2), NC exposure → real outcome (Direction 1).
     The visual claim: the "real" panel shows non-zero β; the two NC
     panels should show β ≈ 0.

  2. ``nc_failure_grid.png`` (primary) — per-exposure × per-outcome
     heatmap of −log10(p), with a hatched overlay marking cells that
     FAIL the null test (p < 0.05). One panel per direction.

  3. ``nc_availability_diagram.png`` (sensitivity) — bar chart of
     non-null N for each NC exposure candidate from the pre-flight
     check. Quick visual confirmation of which candidates survived
     pre-flight.

Reads:
  ./tables/primary/nc_battery_matrix.csv
  ./tables/sensitivity/nc_preflight_availability.csv
  ../cognitive-screening/tables/primary/14_screening_matrix.csv
    (for the positive-control real β panel, optional)

Writes:
  ./figures/primary/nc_comparison.png
  ./figures/primary/nc_failure_grid.png
  ./figures/sensitivity/nc_availability_diagram.png
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

plot_style.setup()

TABLES_PRIMARY = HERE / "tables" / "primary"
TABLES_SENS = HERE / "tables" / "sensitivity"
FIG_PRIMARY = HERE / "figures" / "primary"
FIG_SENS = HERE / "figures" / "sensitivity"
FIG_PRIMARY.mkdir(parents=True, exist_ok=True)
FIG_SENS.mkdir(parents=True, exist_ok=True)

COG_SCREEN_MATRIX = ROOT / "experiments" / "cognitive-screening" / "tables" / "primary" / "14_screening_matrix.csv"


def _save(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path)
    plt.close(fig)


def nc_comparison() -> None:
    """Side-by-side: real β (positive control) | Direction 1 NC β | Direction 2 NC β."""
    matrix = pd.read_csv(TABLES_PRIMARY / "nc_battery_matrix.csv")
    d1 = matrix[matrix.direction == 1]
    d2 = matrix[matrix.direction == 2]

    # Optional positive-control panel from cognitive-screening (real exposure -> real outcome).
    if COG_SCREEN_MATRIX.exists():
        cog = pd.read_csv(COG_SCREEN_MATRIX)
        # Try the most common shape; tolerate column-name drift.
        if "d1_beta" in cog.columns:
            pos = cog[["exposure", "d1_beta"]].copy().rename(columns={"d1_beta": "beta"})
        elif "beta" in cog.columns:
            pos = cog[["exposure", "beta"]].copy()
        else:
            pos = pd.DataFrame(columns=["exposure", "beta"])
    else:
        pos = pd.DataFrame(columns=["exposure", "beta"])

    fig, axes = plt.subplots(1, 3, figsize=(11, 4.5))
    # Panel A — positive control
    ax = axes[0]
    ax.bar(range(len(pos)), pos["beta"], color="#4c72b0")
    ax.set_xticks([])
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_title(f"A. Real exposure → real outcome\n(positive control, n={len(pos)})")
    ax.set_ylabel("β")

    # Panel B — Direction 2 (real exposure → NC outcome) — should be ~0
    ax = axes[1]
    ax.bar(range(len(d2)), d2["beta"], color="#dd8452")
    ax.set_xticks([])
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_title(f"B. Real exposure → NC outcome\n(Dir 2; should be ≈ 0; n={len(d2)})")
    ax.set_ylabel("β")

    # Panel C — Direction 1 (NC exposure → real outcome) — should be ~0
    ax = axes[2]
    ax.bar(range(len(d1)), d1["beta"], color="#55a868")
    ax.set_xticks([])
    ax.axhline(0, color="black", linewidth=0.6)
    ax.set_title(f"C. NC exposure → real outcome\n(Dir 1; should be ≈ 0; n={len(d1)})")
    ax.set_ylabel("β")

    fig.suptitle("Negative-control battery — both null directions vs. positive control")
    fig.tight_layout()
    _save(fig, FIG_PRIMARY / "nc_comparison.png")


def nc_failure_grid() -> None:
    """Per-exposure × per-outcome −log10(p) heatmap, hatched where p<0.05."""
    matrix = pd.read_csv(TABLES_PRIMARY / "nc_battery_matrix.csv")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    for i, d in enumerate((1, 2)):
        ax = axes[i]
        sub = matrix[matrix.direction == d].copy()
        if sub.empty:
            ax.set_title(f"Direction {d}: no rows")
            continue
        sub["nlogp"] = -np.log10(sub["p"].clip(lower=1e-9))
        pvt = sub.pivot_table(index="exposure", columns="outcome", values="nlogp", aggfunc="first")
        sig = sub.pivot_table(index="exposure", columns="outcome",
                              values="null_test_pass", aggfunc="first")
        im = ax.imshow(pvt.values, cmap="Reds", aspect="auto", vmin=0, vmax=3)
        # Hatch cells where the null test failed (p < 0.05 ⇒ null_test_pass = False).
        for ri, exp_name in enumerate(pvt.index):
            for ci, out_name in enumerate(pvt.columns):
                failed = (sig.loc[exp_name, out_name] is False) or (sig.loc[exp_name, out_name] == 0)
                if failed:
                    ax.add_patch(plt.Rectangle((ci - 0.5, ri - 0.5), 1, 1,
                                               fill=False, hatch="///", edgecolor="black", linewidth=0.5))
        ax.set_xticks(range(len(pvt.columns)))
        ax.set_xticklabels(pvt.columns, rotation=45, ha="right", fontsize=7)
        ax.set_yticks(range(len(pvt.index)))
        ax.set_yticklabels(pvt.index, fontsize=7)
        cbar = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
        cbar.set_label("−log10(p)")
        ax.set_title(f"Direction {d} ({'NC→real' if d == 1 else 'real→NC'})\nhatch = NC FAIL (p<0.05)")
    fig.suptitle("Negative-control failure grid — both directions")
    fig.tight_layout()
    _save(fig, FIG_PRIMARY / "nc_failure_grid.png")


def nc_availability_diagram() -> None:
    """Bar chart of N nonnull per NC exposure candidate."""
    avail = pd.read_csv(TABLES_SENS / "nc_preflight_availability.csv")
    if avail.empty:
        print("WARN: availability CSV empty — skipping nc_availability_diagram.")
        return
    fig, ax = plt.subplots(figsize=(8, 3.5))
    colors = ["#55a868" if a else "#cccccc" for a in avail["available"]]
    ax.barh(avail["candidate"], avail["n_nonnull"], color=colors, edgecolor="black")
    for i, (n, lab) in enumerate(zip(avail["n_nonnull"], avail["reason"])):
        ax.text(n, i, f"  n={n}  ({lab})", va="center", fontsize=8)
    ax.set_xlabel("N non-null in W4 analytic frame")
    ax.set_title("NC exposure candidates — pre-flight availability\n(green = available; grey = missing or all-NaN)")
    fig.tight_layout()
    _save(fig, FIG_SENS / "nc_availability_diagram.png")


def main() -> None:
    print("Building negative-control-battery figures ...")
    nc_comparison()
    nc_failure_grid()
    nc_availability_diagram()
    print("Done.")


if __name__ == "__main__":
    main()

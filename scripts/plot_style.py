"""Shared plotting style and helpers."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
IMG = ROOT / "img"


# Canonical per-outcome-group palette. Single source of truth for any chart
# that wants to colour by `outcome_group` (cognitive / cardiometabolic /
# mental_health / functional / ses). Imported by task15_journal_figs and
# task15_multi_outcome so future per-group colouring stays coherent across
# the report.
GROUP_COLORS = {
    "cognitive":        "#4c72b0",
    "cardiometabolic":  "#c44e52",
    "mental_health":    "#8172b2",
    "functional":       "#55a868",
    "ses":              "#dd8452",
}


def setup() -> None:
    sns.set_theme(
        style="whitegrid",
        palette="deep",
        rc={
            "figure.dpi": 110,
            "savefig.dpi": 150,
            "savefig.bbox": "tight",
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "figure.titlesize": 12,
        },
    )


def weighted_mean(y: np.ndarray, w: np.ndarray) -> float:
    mask = ~np.isnan(y) & ~np.isnan(w) & (w > 0)
    if mask.sum() == 0:
        return float("nan")
    return float(np.sum(w[mask] * y[mask]) / np.sum(w[mask]))


def weighted_median(y: np.ndarray, w: np.ndarray) -> float:
    mask = ~np.isnan(y) & ~np.isnan(w) & (w > 0)
    if mask.sum() == 0:
        return float("nan")
    y_s, w_s = y[mask], w[mask]
    order = np.argsort(y_s)
    y_s, w_s = y_s[order], w_s[order]
    cw = np.cumsum(w_s)
    half = cw[-1] / 2.0
    idx = np.searchsorted(cw, half)
    return float(y_s[min(idx, len(y_s) - 1)])


def save(fig: plt.Figure, rel_path: str) -> Path:
    """Save figure as PNG at IMG / rel_path."""
    path_png = IMG / rel_path
    path_png.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path_png)
    plt.close(fig)
    return path_png


def annotate_n(ax: plt.Axes, n: int) -> None:
    ax.text(
        0.99, 0.99, f"N = {n:,}",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=8, color="#555",
        bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#ccc", alpha=0.85),
    )

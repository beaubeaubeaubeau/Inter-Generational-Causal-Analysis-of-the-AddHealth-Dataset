"""Task 09 - Variable distribution plots.

Produces:
  img/distributions/
    treatments/IDGX2_by_demographics.png   # FEATURED plot
    treatments/IDGX2_raw_histogram.png
    treatments/<var>.png                   # all other treatments
    outcomes/<var>.png
    covariates/<var>.png
    conditional/<exposure>_by_<facet>_scatter.png

All plots use the W4 analytic frame (N=5,114). Variables restricted to the
W1-network-gated subsample are labelled in their title.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

import matplotlib.pyplot as plt
import seaborn as sns

from plot_style import setup, save, annotate_n, weighted_mean, weighted_median, IMG  # noqa: E402
from analysis_utils import CACHE, clean_var  # noqa: E402


setup()


# ---------------------------------------------------------------------------
# Frames
# ---------------------------------------------------------------------------
W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
W5 = pd.read_parquet(CACHE / "analytic_w5.parquet")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _weighted_hist(ax, values, weights, bins=30, **kwargs):
    mask = ~np.isnan(values) & ~np.isnan(weights) & (weights > 0)
    v, w = values[mask], weights[mask]
    if len(v) == 0:
        return 0
    # Scale weights so histogram shows weighted frequency
    ax.hist(v, bins=bins, weights=w / w.mean(), **kwargs)
    return int(mask.sum())


def continuous_plot(var, data=W4, weight="GSWGT1", rel_path=None,
                    title=None, xlabel=None, bins=30):
    y = data[var].astype(float).values
    w = data[weight].astype(float).values
    # If the variable is a discrete integer sum with a compact range, use
    # integer-aligned bins so we don't draw spurious empty gaps between integers.
    clean = y[~np.isnan(y)]
    if len(clean) and np.all(clean == np.round(clean)):
        vmin, vmax = int(clean.min()), int(clean.max())
        if vmax - vmin <= 60:
            bins = np.arange(vmin - 0.5, vmax + 1.5, 1)
    fig, ax = plt.subplots(figsize=(5.2, 3.4))
    n = _weighted_hist(ax, y, w, bins=bins, color="#3a6fb0",
                       edgecolor="white", alpha=0.85)
    mean = weighted_mean(y, w)
    median = weighted_median(y, w)
    if not np.isnan(mean):
        ax.axvline(mean, color="#b33", linestyle="--", linewidth=1.2,
                   label=f"weighted mean = {mean:.2f}")
    if not np.isnan(median):
        ax.axvline(median, color="#2b8a3e", linestyle=":", linewidth=1.2,
                   label=f"weighted median = {median:.2f}")
    ax.set_xlabel(xlabel or var)
    ax.set_ylabel("weighted frequency")
    ax.set_title(title or f"{var} distribution")
    ax.legend(loc="upper right", frameon=True)
    annotate_n(ax, n)
    return save(fig, rel_path or f"distributions/{var}.png")


def likert_plot(var, data=W4, weight="GSWGT1", rel_path=None,
                title=None, xlabel=None):
    y = data[var].astype(float).values
    w = data[weight].astype(float).values
    mask = ~np.isnan(y) & ~np.isnan(w) & (w > 0)
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    if mask.sum():
        vals, counts = np.unique(y[mask], return_counts=True)
        wsum = np.array([w[mask & (y == v)].sum() for v in vals])
        ax.bar(vals.astype(int), wsum / wsum.sum() * 100,
               color="#3a6fb0", edgecolor="white")
    ax.set_xlabel(xlabel or var)
    ax.set_ylabel("weighted %")
    ax.set_title(title or f"{var} distribution")
    annotate_n(ax, int(mask.sum()))
    return save(fig, rel_path or f"distributions/{var}.png")


def reserve_code_panel(var, raw_series, rel_path):
    """Secondary panel: raw value counts including reserve codes."""
    counts = raw_series.value_counts(dropna=False).sort_index()
    fig, ax = plt.subplots(figsize=(4.8, 3.0))
    ax.bar(range(len(counts)), counts.values, color="#888")
    ax.set_xticks(range(len(counts)))
    labels = ["NaN" if pd.isna(v) else (f"{v:g}" if isinstance(v, float) else str(v))
              for v in counts.index]
    ax.set_xticklabels(labels, rotation=60, ha="right")
    ax.set_ylabel("raw count (pre-recode)")
    ax.set_title(f"{var} raw values (reserve-code audit)")
    annotate_n(ax, len(raw_series))
    return save(fig, rel_path)


# ---------------------------------------------------------------------------
# FEATURED: IDGX2 by major demographics (stacked subplots)
# ---------------------------------------------------------------------------
def idgx2_by_demographics():
    # Use the W1-network subsample; every respondent with IDGX2 observed
    df = W4.dropna(subset=["IDGX2"]).copy()
    w = df["GSWGT1"].fillna(0).astype(float)

    # Prepare categorical facets
    df["sex_lbl"] = df["BIO_SEX"].map({1: "Male", 2: "Female"})
    ed_q = pd.qcut(df["PARENT_ED"], 3, labels=["low", "mid", "high"], duplicates="drop")
    df["ed_lbl"] = ed_q
    df["race_lbl"] = df["RACE"].fillna("Unknown")
    pvt_q = pd.qcut(df["AH_RAW"], 4, labels=["Q1", "Q2", "Q3", "Q4"], duplicates="drop")
    df["pvt_lbl"] = pvt_q

    panels = [
        ("Sex", "sex_lbl"),
        ("Parental education tercile", "ed_lbl"),
        ("Race / ethnicity", "race_lbl"),
        ("AHPVT quartile", "pvt_lbl"),
    ]

    fig, axes = plt.subplots(len(panels), 1, figsize=(7.5, 2.3 * len(panels)),
                             sharex=True)
    for ax, (title, col) in zip(axes, panels):
        groups = df[col].dropna().unique()
        # Stable sort
        groups = sorted(groups, key=lambda g: str(g))
        palette = sns.color_palette("deep", n_colors=len(groups))
        # Bin edges for in-degree
        bins = np.arange(0, df["IDGX2"].max() + 2) - 0.5
        for i, g in enumerate(groups):
            sub = df[df[col] == g]
            ww = sub["GSWGT1"].fillna(0).astype(float).values
            vv = sub["IDGX2"].astype(float).values
            if len(vv) == 0:
                continue
            # Weighted histogram normalized as % within group
            counts, _ = np.histogram(vv, bins=bins, weights=ww)
            if counts.sum() > 0:
                counts = counts / counts.sum() * 100
            ax.plot(bins[:-1] + 0.5, counts, label=f"{g} (N={len(sub):,})",
                    color=palette[i], linewidth=1.6, alpha=0.85)
        med = weighted_median(df["IDGX2"].values, w.values)
        ax.axvline(med, color="#444", linestyle=":", linewidth=1,
                   label=f"overall median = {med:.1f}")
        ax.set_title(f"In-degree (IDGX2) by {title}", fontsize=10)
        ax.set_ylabel("% within group")
        ax.legend(loc="upper right", fontsize=7, ncol=2, frameon=True)
    axes[-1].set_xlabel("in-degree (IDGX2)")
    fig.suptitle("Wave I in-degree distribution, by demographics", fontsize=12)
    fig.tight_layout()
    return save(fig, "distributions/treatments/IDGX2_by_demographics.png")


def idgx2_raw_histogram():
    df = W4.dropna(subset=["IDGX2"]).copy()
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.3))
    v = df["IDGX2"].astype(float).values
    w = df["GSWGT1"].astype(float).values
    mask = ~np.isnan(v) & ~np.isnan(w)
    axes[0].hist(v[mask], bins=np.arange(0, v.max() + 2) - 0.5,
                 weights=w[mask], color="#3a6fb0", edgecolor="white")
    axes[0].set_xlabel("in-degree (IDGX2)")
    axes[0].set_ylabel("weighted frequency")
    axes[0].set_title("In-degree (IDGX2), weighted")
    annotate_n(axes[0], int(mask.sum()))

    # Reserve-code audit panel: compare cleaned distribution to raw network file
    raw = pd.read_parquet(CACHE / "w1network.parquet")["IDGX2"]
    counts = raw.value_counts(dropna=False).sort_index()
    axes[1].bar(range(len(counts)), counts.values, color="#888")
    axes[1].set_xticks(range(0, len(counts), max(len(counts) // 10, 1)))
    lbls = ["NaN" if pd.isna(v) else f"{int(v)}" for v in counts.index]
    axes[1].set_xticklabels([lbls[i] for i in range(0, len(counts), max(len(counts) // 10, 1))],
                             rotation=60, ha="right")
    axes[1].set_title("Raw IDGX2 counts (reserve-code audit)")
    axes[1].set_ylabel("raw count")
    fig.tight_layout()
    return save(fig, "distributions/treatments/IDGX2_raw_histogram.png")


# ---------------------------------------------------------------------------
# Conditional scatter: IDGX2 × W4 composite, faceted by sex × ed tercile
# ---------------------------------------------------------------------------
def idgx2_x_w4comp_facets():
    df = W4.dropna(subset=["IDGX2", "W4_COG_COMP", "BIO_SEX", "PARENT_ED"]).copy()
    ed_q = pd.qcut(df["PARENT_ED"], 3, labels=["low", "mid", "high"], duplicates="drop")
    df["ed_q"] = ed_q
    # Translate numeric PARENT_ED (0-6 ordinal of max(H1RM1,H1RF1)) into human-readable
    # tercile labels. Tercile cut-points on the 0-6 scale are [0, 2, 5, 6], so the
    # categories coincide with the natural breakpoints of the AddHealth codebook.
    ed_tercile_text = {
        "low":  "Low parent-ed\n(≤ HS grad; 0-2 on max H1RM1/H1RF1)",
        "mid":  "Mid parent-ed\n(post-HS voc → college grad; 3-5)",
        "high": "High parent-ed\n(post-grad / professional; 6)",
    }
    df["ed_lbl"] = df["ed_q"].map(ed_tercile_text)
    df["sex_lbl"] = df["BIO_SEX"].map({1: "Male", 2: "Female"})
    col_order = [ed_tercile_text[k] for k in ["low", "mid", "high"]]

    # N per facet for sub-titles
    counts = df.groupby(["sex_lbl", "ed_lbl"]).size().to_dict()

    g = sns.lmplot(
        data=df, x="IDGX2", y="W4_COG_COMP",
        row="sex_lbl", col="ed_lbl",
        row_order=["Male", "Female"],
        col_order=col_order,
        scatter_kws={"alpha": 0.25, "s": 10, "color": "#3a6fb0"},
        line_kws={"color": "#b33", "linewidth": 1.4},
        height=3.0, aspect=1.15, lowess=True,
    )
    g.set_axis_labels("in-degree (IDGX2)", "W4 cognitive composite (z)")
    # Per-facet title = sex, with N annotated; ed label is already in the column header.
    for (row_val, col_val), ax in g.axes_dict.items():
        n = counts.get((row_val, col_val), 0)
        ax.set_title(f"{col_val}\n{row_val}, N={n:,}", fontsize=9)
    g.figure.suptitle(
        "In-degree vs. W4 cognitive composite, faceted by sex × parental-education tercile\n"
        f"PARENT_ED = max of H1RM1/H1RF1 recoded to 0-6; LOWESS fit in red. Overall N={len(df):,}",
        y=1.02, fontsize=10,
    )
    g.figure.tight_layout()
    return save(g.figure, "distributions/conditional/IDGX2_x_W4COMP_by_sex_edtercile.png")


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------
TREATMENT_VARS_CONT = [
    ("IDGX2", "in-degree (nominations received)"),
    ("ODGX2", "out-degree (nominations given)"),
    ("BCENT10X", "Bonacich centrality (β=0.1)"),
    ("REACH", "reachable alters"),
    ("REACH3", "reachable alters (≤3 hops)"),
    ("PRXPREST", "proximity prestige"),
    ("FRIEND_N_NOMINEES", "friendship grid: total nominees (0-10)"),
    ("FRIEND_CONTACT_SUM", "friendship grid: 7-day contact intensity"),
    ("SCHOOL_BELONG", "school belonging (sum of 6 items, 6-30)"),
    ("CESD_SUM", "CES-D depression sum (0-57)"),
]

TREATMENT_VARS_LIKERT = [
    ("H1DA7", "hang out with friends (past week)"),
    ("H1ED19", "feel close to people at school"),
    ("H1ED20", "feel part of your school"),
    ("H1ED21", "students at your school are prejudiced"),
    ("H1ED22", "happy at your school"),
    ("H1ED23", "teachers treat students fairly"),
    ("H1ED24", "feel safe in your school"),
    ("H1FS13", "felt lonely (past week)"),
    ("H1FS14", "people unfriendly (past week)"),
]

TREATMENT_VARS_BINARY = [
    ("HAVEBMF", "has a best male friend"),
    ("HAVEBFF", "has a best female friend"),
    ("IDG_ZERO", "in-degree = 0 (isolate)"),
    ("IDG_LEQ1", "in-degree ≤ 1"),
    ("FRIEND_DISCLOSURE_ANY", "talked about a problem with any friend"),
]

OUTCOME_VARS = [
    ("C4WD90_1", "W4 immediate word recall (0-15)"),
    ("C4WD60_1", "W4 delayed word recall (0-15)"),
    ("C4NUMSCR", "W4 backward digit span (0-7)"),
    ("W4_COG_COMP", "W4 cognitive composite (z-score)"),
]

OUTCOME_VARS_W5 = [
    ("C5WD90_1", "W5 immediate word recall (0-15)"),
    ("C5WD60_1", "W5 delayed word recall (0-15)"),
    ("BDS_SCORE", "W5 backward digit span (derived, 0-8)"),
    ("W5_COG_COMP", "W5 cognitive composite (z-score)"),
]

COVARIATE_VARS = [
    ("AH_RAW", "AHPVT raw (receptive vocabulary, 0-87)"),
    ("PARENT_ED", "parent education (derived 0-6)"),
    ("H1GH1", "self-rated health (1-5)"),
]


def run() -> None:
    print("FEATURED: IDGX2 by demographics ...")
    idgx2_by_demographics()
    idgx2_raw_histogram()

    print("Treatment continuous ...")
    for var, desc in TREATMENT_VARS_CONT:
        continuous_plot(var, rel_path=f"distributions/treatments/{var}.png",
                        title=f"{var} — {desc}")

    print("Treatment Likert ...")
    for var, desc in TREATMENT_VARS_LIKERT:
        likert_plot(var, rel_path=f"distributions/treatments/{var}.png",
                    title=f"{var} — {desc}")

    print("Treatment binary ...")
    for var, desc in TREATMENT_VARS_BINARY:
        likert_plot(var, rel_path=f"distributions/treatments/{var}.png",
                    title=f"{var} — {desc}")

    print("W4 outcomes ...")
    for var, desc in OUTCOME_VARS:
        continuous_plot(var, weight="GSWGT4_2",
                        rel_path=f"distributions/outcomes/{var}.png",
                        title=f"{var} — {desc}", bins=20)

    print("W5 outcomes (mode-restricted I/T) ...")
    for var, desc in OUTCOME_VARS_W5:
        continuous_plot(var, data=W5, weight="GSW5",
                        rel_path=f"distributions/outcomes/{var}.png",
                        title=f"{var} — {desc} (mode I/T)", bins=16)

    print("Covariates ...")
    for var, desc in COVARIATE_VARS:
        continuous_plot(var, rel_path=f"distributions/covariates/{var}.png",
                        title=f"{var} — {desc}")

    # Reserve-code audit panels for the top-attention variables
    print("Reserve-code audit panels ...")
    raw_w1 = pd.read_parquet(CACHE / "w1inhome.parquet")
    raw_w4 = pd.read_parquet(CACHE / "w4inhome.parquet")
    for var in ["AH_RAW", "CESD_SUM"]:  # composite / derived — skip raw audit
        pass
    for var in ["H1FS13", "H1FS14", "H1ED19", "H1ED20"]:
        reserve_code_panel(var, raw_w1[var],
                           f"distributions/covariates/{var}_raw_audit.png")
    for var in ["C4WD90_1", "C4WD60_1", "C4NUMSCR"]:
        reserve_code_panel(var, raw_w4[var],
                           f"distributions/outcomes/{var}_raw_audit.png")

    print("Conditional scatter ...")
    idgx2_x_w4comp_facets()

    print(f"Done. Plots in {IMG}/distributions/")


if __name__ == "__main__":
    run()

"""Task 12 - Regression result and sensitivity figures.

Reads:
  outputs/10_regressions.csv
  outputs/11_placebo_permutation.csv
  outputs/11_sensitivity.md (via pandas from the constituent CSVs)
  outputs/11_collinearity.csv
  outputs/11_correlation.csv
  outputs/11_ahpvt_shift.csv
  outputs/11_saturated_balance.csv
  outputs/cache/analytic_w4.parquet
  outputs/cache/analytic_w1_full.parquet
  outputs/06_attrition_summary.md  (we re-derive attrition per IDGX2 decile from the cached frames)

Writes figures to img/regressions/ and img/sensitivity/.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sys.path.insert(0, str(Path(__file__).parent))
from plot_style import setup, save, annotate_n, weighted_mean  # noqa: E402
from analysis_utils import weighted_ols  # noqa: E402


def load_analytic_w4() -> pd.DataFrame:
    return pd.read_parquet(ROOT / "outputs" / "cache" / "analytic_w4.parquet")


def load_analytic_w1_full() -> pd.DataFrame:
    return pd.read_parquet(ROOT / "outputs" / "cache" / "analytic_w1_full.parquet")

ROOT = Path("/Users/jb/Desktop/Inter-Generational-Causal-Analysis-of-the-AddHealth-Dataset")
OUT = ROOT / "outputs"
IMG_REG = ROOT / "img" / "regressions"
IMG_SENS = ROOT / "img" / "sensitivity"
IMG_REG.mkdir(parents=True, exist_ok=True)
IMG_SENS.mkdir(parents=True, exist_ok=True)

setup()
np.random.seed(20260419)

# ----------------------------------------------------------------------
# Load coefficient CSV
# ----------------------------------------------------------------------
coefs = pd.read_csv(OUT / "10_regressions.csv")

# map spec -> exposure term(s) to plot on forest
EXPOSURE_TERMS = {
    "S01": "idgx2",
    "S01C": "idgx2",
    "S03_C4WD90_1": "idgx2",
    "S03_C4WD60_1": "idgx2",
    "S03_C4NUMSCR": "idgx2",
    "S03_W4_COG_COMP": "idgx2",
    "S04_ODGX2_placebo": "odgx2_placebo",
    "S04_BCENT10X": "bcent10x",
    "S04_REACH": "reach",
    "S04_PRXPREST": "prxprest",
    "S05_ZERO": "idg_zero",
    "S05_LEQ1": "idg_leq1",
    "S06": "school_belong",
    "S07": "lonely",
    "S10_nominees": "friend_n",
    "S10_contact": "friend_contact",
    "S10_disclose": "friend_disclose",
}

# Labels for plots
SPEC_LABELS = {
    "S01": "IDGX2 → immediate recall",
    "S01C": "IDGX2 → W4 composite",
    "S03_C4WD90_1": "IDGX2 → immediate recall",
    "S03_C4WD60_1": "IDGX2 → delayed recall",
    "S03_C4NUMSCR": "IDGX2 → backward digit span",
    "S03_W4_COG_COMP": "IDGX2 → W4 composite",
    "S04_ODGX2_placebo": "ODGX2 placebo → W4 comp",
    "S04_BCENT10X": "Bonacich β=0.1 → W4 comp",
    "S04_REACH": "Reachable alters → W4 comp",
    "S04_PRXPREST": "Prox. prestige → W4 comp",
    "S05_ZERO": "Isolation (IDGX2=0) → W4 comp",
    "S05_LEQ1": "Near-isolation (≤1) → W4 comp",
    "S06": "School belonging → W4 comp",
    "S07": "Loneliness → W4 comp",
    "S10_nominees": "# friend nominees → W4 comp",
    "S10_contact": "Friend contact index → W4 comp",
    "S10_disclose": "Emotional disclosure → W4 comp",
}


def get_row(spec_id: str, term: str) -> pd.Series:
    sub = coefs[(coefs.spec_id == spec_id) & (coefs.term == term)]
    if sub.empty:
        raise KeyError(f"No row for {spec_id}/{term}")
    return sub.iloc[0]


# ----------------------------------------------------------------------
# 1. Coefficient forest plot
# ----------------------------------------------------------------------
def plot_forest() -> None:
    rows = []
    for spec, term in EXPOSURE_TERMS.items():
        r = get_row(spec, term)
        rows.append({
            "label": SPEC_LABELS[spec],
            "beta": r.beta,
            "ci_lo": r.ci_lo,
            "ci_hi": r.ci_hi,
            "p": r.p,
            "n": int(r.n),
        })
    d = pd.DataFrame(rows)
    # sort by absolute beta magnitude descending
    d["abs_beta"] = d.beta.abs()
    d = d.sort_values("abs_beta", ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(9, 7))
    y = np.arange(len(d))
    colors = ["#c0392b" if p < 0.05 else "#7f8c8d" for p in d.p]
    ax.errorbar(
        d.beta, y,
        xerr=[d.beta - d.ci_lo, d.ci_hi - d.beta],
        fmt="o", capsize=3, elinewidth=1.2, markersize=6,
        color="#34495e", ecolor="#7f8c8d",
    )
    for i, (b, c) in enumerate(zip(d.beta, colors)):
        ax.plot(b, i, "o", color=c, markersize=6.5, zorder=5)
    ax.axvline(0, color="k", lw=0.8, linestyle="--", alpha=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(d.label)
    ax.set_xlabel("Regression coefficient (β, adjusted incl. AH_PVT)")
    ax.set_title("Forest plot of primary exposures\nRed = p<0.05 (unadjusted for multiplicity)")
    # annotate N beside each
    for i, row in d.iterrows():
        ax.text(
            ax.get_xlim()[1], i, f"  N={row.n:,}",
            va="center", ha="left", fontsize=7, color="#555",
        )
    fig.tight_layout()
    save(fig, "regressions/coefficient_forest.png")


# ----------------------------------------------------------------------
# 2. Quintile dose-response (S02C)
# ----------------------------------------------------------------------
def plot_quintile_dose_response() -> None:
    df_c = coefs[coefs.spec_id == "S02C"].copy()
    df_lin = coefs[coefs.spec_id == "S02"].copy()
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2), sharey=False)

    for ax, spec_df, title, ylab in [
        (axes[0], df_lin, "Outcome = C4WD90_1 (immediate recall)", "β vs. Q1 (words recalled)"),
        (axes[1], df_c, "Outcome = W4_COG_COMP (z-score)", "β vs. Q1 (SD units)"),
    ]:
        qterms = ["idg_q2", "idg_q3", "idg_q4", "idg_q5"]
        rows = spec_df[spec_df.term.isin(qterms)].set_index("term").loc[qterms]
        # reference category at x=1
        xs = [1, 2, 3, 4, 5]
        beta = [0.0] + rows.beta.tolist()
        lo = [0.0] + rows.ci_lo.tolist()
        hi = [0.0] + rows.ci_hi.tolist()
        ax.errorbar(
            xs, beta,
            yerr=[np.array(beta) - np.array(lo), np.array(hi) - np.array(beta)],
            fmt="o-", capsize=3, color="#2874a6",
        )
        ax.axhline(0, color="k", lw=0.7, ls="--", alpha=0.4)
        ax.set_xticks(xs)
        ax.set_xticklabels(["Q1 (ref)", "Q2", "Q3", "Q4", "Q5"])
        ax.set_title(title)
        ax.set_ylabel(ylab)
        ax.set_xlabel("In-degree quintile")
        annotate_n(ax, int(rows.n.iloc[0]))

    fig.suptitle("In-degree quintile dose-response (adjusted incl. AH_PVT)")
    fig.tight_layout()
    save(fig, "regressions/quintile_dose_response.png")


# ----------------------------------------------------------------------
# 3. Weighted vs unweighted scatter (from sensitivity)
# ----------------------------------------------------------------------
def plot_weighted_vs_unweighted() -> None:
    # Re-derive from task11 output directly to keep it self-contained.
    # We re-read the file as markdown table; simpler is to re-run the comparison.
    # Since we don't have a separate CSV, build it here from coefs.
    # Use same set of specs and terms from EXPOSURE_TERMS, comparing primary-spec (weighted)
    # vs. the _noAHPVT? no, we want weighted vs unweighted. That's not saved to 10_regressions.
    # Read the already-produced 11_sensitivity md's table 1 via the CSV? Not available.
    # Re-run the weighted-vs-unweighted directly here on the spec list.
    df = load_analytic_w4().copy()
    df["male"] = (df["BIO_SEX"] == 1).astype(float)
    for lvl in ["NH-Black", "Hispanic", "Other"]:
        df[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    df.loc[df["RACE"].isna(), [f"race_{x}" for x in ["NH-Black", "Hispanic", "Other"]]] = np.nan
    df["parent_ed"] = df["PARENT_ED"]
    df["cesd_sum"] = df["CESD_SUM"]
    df["srh"] = df["H1GH1"]
    df["ahpvt"] = df["AH_RAW"]

    pairs = []
    COVARS = ["male", "race_NH-Black", "race_Hispanic", "race_Other",
              "parent_ed", "cesd_sum", "srh", "ahpvt"]

    def design(frame, exposure):
        d = frame.dropna(subset=[exposure, "W4_COG_COMP", "GSWGT4_2", "CLUSTER2"] + COVARS).copy()
        Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
        Xdf[exposure] = d[exposure].values
        for c in COVARS:
            Xdf[c] = d[c].values
        return d, Xdf.values, ["const", exposure] + COVARS

    for spec_id, exp in [
        ("IDGX2 linear", "IDGX2"),
        ("ODGX2 placebo", "ODGX2"),
        ("BCENT10X", "BCENT10X"),
        ("REACH", "REACH"),
    ]:
        d, X, names = design(df, exp)
        if d.empty:
            continue
        y = d["W4_COG_COMP"].astype(float).values
        w = d["GSWGT4_2"].astype(float).values
        psu = d["CLUSTER2"].astype(int).values
        wres = weighted_ols(y, X, w, psu, names)
        w1 = np.ones_like(w)
        ures = weighted_ols(y, X, w1, psu, names)
        pairs.append({
            "label": spec_id,
            "beta_w": float(wres["beta"][exp]),
            "se_w": float(wres["se"][exp]),
            "beta_u": float(ures["beta"][exp]),
            "se_u": float(ures["se"][exp]),
            "n": len(d),
        })
    d = pd.DataFrame(pairs)

    fig, ax = plt.subplots(figsize=(6.5, 6))
    ax.errorbar(
        d.beta_w, d.beta_u,
        xerr=1.96 * d.se_w, yerr=1.96 * d.se_u,
        fmt="o", capsize=3, color="#34495e",
    )
    # 45-degree line
    lim = max(d.beta_w.abs().max(), d.beta_u.abs().max()) * 1.5
    ax.plot([-lim, lim], [-lim, lim], "--", color="#7f8c8d", lw=0.8)
    ax.axhline(0, color="k", lw=0.5, alpha=0.3)
    ax.axvline(0, color="k", lw=0.5, alpha=0.3)
    for _, r in d.iterrows():
        ax.annotate(r.label, (r.beta_w, r.beta_u),
                    xytext=(5, 5), textcoords="offset points", fontsize=8)
    ax.set_xlabel("β (weighted, GSWGT4_2)")
    ax.set_ylabel("β (unweighted)")
    ax.set_title("Weighted vs. unweighted β — W4_COG_COMP outcome\n"
                 "(95% CI via cluster-robust SE in both)")
    fig.tight_layout()
    save(fig, "regressions/weighted_vs_unweighted.png")


# ----------------------------------------------------------------------
# 4. Composite vs. components
# ----------------------------------------------------------------------
def plot_composite_vs_components() -> None:
    rows = []
    for spec in ["S03_C4WD90_1", "S03_C4WD60_1", "S03_C4NUMSCR", "S03_W4_COG_COMP"]:
        r = get_row(spec, "idgx2")
        rows.append({
            "outcome": {
                "S03_C4WD90_1": "Immediate recall\n(C4WD90_1, 0-15)",
                "S03_C4WD60_1": "Delayed recall\n(C4WD60_1, 0-15)",
                "S03_C4NUMSCR": "Backward digit span\n(C4NUMSCR, 0-7)",
                "S03_W4_COG_COMP": "Composite z\n(mean of 3)",
            }[spec],
            "beta": r.beta,
            "ci_lo": r.ci_lo,
            "ci_hi": r.ci_hi,
            "p": r.p,
            "n": int(r.n),
        })
    d = pd.DataFrame(rows)

    fig, ax = plt.subplots(figsize=(7, 4))
    y = np.arange(len(d))
    colors = ["#c0392b" if p < 0.05 else "#7f8c8d" for p in d.p]
    ax.errorbar(
        d.beta, y,
        xerr=[d.beta - d.ci_lo, d.ci_hi - d.beta],
        fmt="o", capsize=3, color="#34495e",
    )
    for i, (b, c) in enumerate(zip(d.beta, colors)):
        ax.plot(b, i, "o", color=c, markersize=7, zorder=5)
    ax.axvline(0, color="k", lw=0.8, ls="--", alpha=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels(d.outcome)
    ax.set_xlabel("β for IDGX2 (adjusted, incl. AH_PVT)")
    ax.set_title("Composite vs. each W4 cognitive component\n"
                 "(composite = mean of three individually-z-scored components)")
    for i, r in d.iterrows():
        ax.text(ax.get_xlim()[1], i, f"  N={r.n:,}",
                va="center", ha="left", fontsize=7, color="#555")
    fig.tight_layout()
    save(fig, "regressions/composite_vs_components.png")


# ----------------------------------------------------------------------
# 5. Partial-residual plot for anchor model S01C
# ----------------------------------------------------------------------
def plot_partial_residual() -> None:
    df = load_analytic_w4().copy()
    df["male"] = (df["BIO_SEX"] == 1).astype(float)
    for lvl in ["NH-Black", "Hispanic", "Other"]:
        df[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    df.loc[df["RACE"].isna(), [f"race_{x}" for x in ["NH-Black", "Hispanic", "Other"]]] = np.nan
    df["parent_ed"] = df["PARENT_ED"]
    df["cesd_sum"] = df["CESD_SUM"]
    df["srh"] = df["H1GH1"]
    df["ahpvt"] = df["AH_RAW"]
    COVARS = ["male", "race_NH-Black", "race_Hispanic", "race_Other",
              "parent_ed", "cesd_sum", "srh", "ahpvt"]
    keep = ["IDGX2", "W4_COG_COMP", "GSWGT4_2", "CLUSTER2"] + COVARS
    d = df.dropna(subset=keep).copy()
    y = d["W4_COG_COMP"].astype(float).values
    Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
    Xdf["IDGX2"] = d["IDGX2"].values
    for c in COVARS:
        Xdf[c] = d[c].values
    X = Xdf.values
    names = ["const", "IDGX2"] + COVARS
    w = d["GSWGT4_2"].astype(float).values
    psu = d["CLUSTER2"].astype(int).values
    res = weighted_ols(y, X, w, psu, names)
    beta_idg = float(res["beta"]["IDGX2"])

    import statsmodels.api as sm
    wls = sm.WLS(y, X, weights=w).fit()
    part_resid = wls.resid + beta_idg * d["IDGX2"].astype(float).values

    fig, ax = plt.subplots(figsize=(7, 5))
    # bin-means of partial-residual by IDGX2 for readability
    x_idg = d["IDGX2"].astype(float).values
    bins = np.arange(0, int(np.nanmax(x_idg)) + 2) - 0.5
    idx = np.digitize(x_idg, bins) - 1
    bin_centers, bin_means, bin_counts = [], [], []
    for i in range(len(bins) - 1):
        mask = idx == i
        if mask.sum() >= 10:
            bin_centers.append(0.5 * (bins[i] + bins[i+1]) + 0.5)
            bin_means.append(part_resid[mask].mean())
            bin_counts.append(mask.sum())
    ax.scatter(x_idg + np.random.uniform(-0.15, 0.15, x_idg.size),
               part_resid, s=5, alpha=0.2, color="#34495e")
    ax.plot(bin_centers, bin_means, "o-", color="#c0392b",
            markersize=8, label="bin means (N≥10)")
    # slope line
    xs = np.linspace(x_idg.min(), x_idg.max(), 50)
    intercept = np.mean(part_resid) - beta_idg * np.mean(x_idg)
    ax.plot(xs, intercept + beta_idg * xs, "--", color="#2874a6",
            label=f"β = {beta_idg:+.4f}")
    ax.axhline(0, color="k", lw=0.5, alpha=0.4)
    ax.set_xlabel("IDGX2 (in-degree)")
    ax.set_ylabel("Partial residual of W4_COG_COMP")
    ax.set_title("Partial-residual plot — IDGX2 → W4 composite (S01C)")
    ax.legend(loc="lower right")
    annotate_n(ax, len(d))
    fig.tight_layout()
    save(fig, "regressions/partial_residual_IDGX2.png")


# ----------------------------------------------------------------------
# 6. Placebo panel: IDGX2 vs ODGX2 vs permuted null
# ----------------------------------------------------------------------
def plot_placebo_panel() -> None:
    perm = pd.read_csv(OUT / "11_placebo_permutation.csv")
    b_idg = get_row("S01C", "idgx2").beta
    b_odg = get_row("S04_ODGX2_placebo", "odgx2_placebo").beta
    b_bcent = get_row("S04_BCENT10X", "bcent10x").beta

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(perm.beta_permuted, bins=40, color="#bdc3c7",
            edgecolor="#7f8c8d", alpha=0.85,
            label="Permuted IDGX2 (within-PSU, 500 reps)")
    ymax = ax.get_ylim()[1]
    ax.axvline(b_idg, color="#2874a6", lw=2.2,
               label=f"Observed IDGX2 β = {b_idg:+.4f}")
    ax.axvline(b_odg, color="#c0392b", lw=2.2, ls="--",
               label=f"ODGX2 placebo β = {b_odg:+.4f}")
    ax.axvline(b_bcent, color="#d35400", lw=2.2, ls=":",
               label=f"BCENT10X β = {b_bcent:+.4f}")
    ax.axvline(0, color="k", lw=0.6, alpha=0.35)
    ax.set_xlabel("β on W4_COG_COMP")
    ax.set_ylabel("Count")
    ax.set_title("Placebo panel: IDGX2 signal vs. permutation null\n"
                 "(out-degree exceeds in-degree — see red-team note)")
    ax.legend(fontsize=8)
    fig.tight_layout()
    save(fig, "regressions/placebo_panel.png")


# ----------------------------------------------------------------------
# 7. Heterogeneity interactions
# ----------------------------------------------------------------------
def plot_heterogeneity() -> None:
    # S09_sex: idgx2_c + idgx2_x_male
    # S09_parented: idgx2_c + idgx2_x_parented (parented centered? check)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))

    # SEX
    main = get_row("S09_sex", "idgx2_c").beta
    inter = get_row("S09_sex", "idgx2_x_male").beta
    se_main = get_row("S09_sex", "idgx2_c").se
    se_inter = get_row("S09_sex", "idgx2_x_male").se
    beta_f = main
    beta_m = main + inter
    se_f = se_main
    se_m = np.sqrt(se_main**2 + se_inter**2)  # upper bound w/o covariance
    d = pd.DataFrame({
        "group": ["Female (ref)", "Male"],
        "beta": [beta_f, beta_m],
        "se": [se_f, se_m],
    })
    axes[0].errorbar(d.group, d.beta, yerr=1.96 * d.se,
                     fmt="o", capsize=4, color="#34495e", markersize=7)
    axes[0].axhline(0, color="k", lw=0.6, ls="--", alpha=0.4)
    axes[0].set_title(f"IDGX2 × BIO_SEX  (interaction β={inter:+.4f}, p={get_row('S09_sex','idgx2_x_male').p:.3f})")
    axes[0].set_ylabel("β on W4_COG_COMP")

    # PARENT-ED (continuous: we show slope at low (0) and high (6))
    main = get_row("S09_parented", "idgx2_c").beta
    inter = get_row("S09_parented", "idgx2_x_parented").beta
    # Slope of IDGX2 at parent_ed value p = main + inter * p (parent_ed was centered)
    # Plot slope across the parent-ed range with a band
    ps = np.linspace(-3, 3, 41)  # centered parented — roughly z units
    slopes = main + inter * ps
    axes[1].plot(ps, slopes, color="#2874a6")
    axes[1].axhline(0, color="k", lw=0.6, ls="--", alpha=0.4)
    axes[1].set_xlabel("Parent-ed (centered)")
    axes[1].set_ylabel("β of IDGX2 on W4_COG_COMP")
    axes[1].set_title(f"IDGX2 × parent-ed  (interaction β={inter:+.5f}, p={get_row('S09_parented','idgx2_x_parented').p:.3f})")

    fig.suptitle("Heterogeneity of IDGX2 → W4 composite by sex and parent-ed")
    fig.tight_layout()
    save(fig, "regressions/heterogeneity_interactions.png")


# ----------------------------------------------------------------------
# 8. Sensitivity: AHPVT with/without
# ----------------------------------------------------------------------
def plot_ahpvt_with_without() -> None:
    d = pd.read_csv(OUT / "11_ahpvt_shift.csv")
    d = d.sort_values("pct_shrinkage_from_adjustment", key=abs, ascending=True).reset_index(drop=True)

    fig, ax = plt.subplots(figsize=(8, 6))
    y = np.arange(len(d))
    for i, row in d.iterrows():
        ax.plot([row.beta_without_ahpvt, row.beta_with_ahpvt], [i, i],
                "-", color="#bdc3c7", lw=1.2)
    ax.scatter(d.beta_without_ahpvt, y, color="#7f8c8d", marker="o",
               s=55, label="Without AH_PVT")
    ax.scatter(d.beta_with_ahpvt, y, color="#c0392b", marker="s",
               s=55, label="With AH_PVT")
    ax.axvline(0, color="k", lw=0.7, ls="--", alpha=0.4)
    ax.set_yticks(y)
    ax.set_yticklabels([f"{r.term} → {r.outcome}" for _, r in d.iterrows()])
    ax.set_xlabel("β (W4 cognition)")
    ax.legend()
    fig.tight_layout()
    save(fig, "sensitivity/ahpvt_with_without.png")


# ----------------------------------------------------------------------
# 9. Saturated-school vs full sample balance
# ----------------------------------------------------------------------
def plot_saturated_vs_full() -> None:
    d = pd.read_csv(OUT / "11_saturated_balance.csv")
    wide = d.pivot(index="variable", columns="group", values="mean")
    n_wide = d.pivot(index="variable", columns="group", values="n")

    # Standardize means relative to pooled SD (from analytic_w1_full) for interpretability
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(wide))
    width = 0.35
    ax.bar(x - width/2, wide["in_network"], width,
           label=f"In-network (W1 saturated, max N={n_wide['in_network'].max():,})",
           color="#2874a6")
    ax.bar(x + width/2, wide["out_network"], width,
           label=f"Out-of-network W1 (max N={n_wide['out_network'].max():,})",
           color="#e67e22")
    ax.set_xticks(x)
    ax.set_xticklabels(wide.index, rotation=30, ha="right")
    ax.set_ylabel("Unweighted mean")
    ax.set_title("Saturated-school vs. full W1: covariate balance\n"
                 "(Differences imply generalizability caveats for network-based analyses)")
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    save(fig, "sensitivity/saturated_vs_full.png")


# ----------------------------------------------------------------------
# 10. Mode-selection balance (W5)
# ----------------------------------------------------------------------
def plot_mode_selection_balance() -> None:
    # Merge W1 baseline (analytic_w4 has the derived cols) with W5 mode audit.
    audit = pd.read_parquet(ROOT / "outputs" / "cache" / "analytic_w5_mode_audit.parquet")
    w4 = load_analytic_w4().copy()
    w4["male"] = (w4["BIO_SEX"] == 1).astype(float)
    w4["parent_ed"] = w4["PARENT_ED"]
    w4["cesd_sum"] = w4["CESD_SUM"]

    d = w4.merge(audit[["AID", "MODE", "IS_COG_MODE"]], on="AID", how="inner")
    d["mode_elig"] = d["IS_COG_MODE"].astype(bool)
    vars_to_compare = ["IDGX2", "AH_RAW", "male", "parent_ed", "cesd_sum"]
    rows = []
    for v in vars_to_compare:
        if v not in d.columns:
            continue
        s = d[[v, "mode_elig"]].dropna()
        if s.empty:
            continue
        g = s.groupby("mode_elig")[v].agg(["mean", "std", "count"])
        if True in g.index and False in g.index:
            m_elig = g.loc[True, "mean"]
            m_inel = g.loc[False, "mean"]
            sd = s[v].std()
            std_diff = (m_elig - m_inel) / sd if sd > 0 else np.nan
            rows.append({
                "variable": v,
                "mean_elig": m_elig,
                "mean_inel": m_inel,
                "std_diff": std_diff,
                "n_elig": int(g.loc[True, "count"]),
                "n_inel": int(g.loc[False, "count"]),
            })
    b = pd.DataFrame(rows)
    if b.empty:
        print("[warn] mode-selection balance: no data")
        return

    fig, ax = plt.subplots(figsize=(7, 4))
    colors = ["#c0392b" if abs(x) > 0.1 else "#34495e" for x in b.std_diff]
    ax.barh(b.variable, b.std_diff, color=colors)
    ax.axvline(0, color="k", lw=0.7)
    ax.axvline(0.1, color="#7f8c8d", lw=0.6, ls="--")
    ax.axvline(-0.1, color="#7f8c8d", lw=0.6, ls="--")
    ax.set_xlabel("Std. mean diff (elig − ineligible)")
    ax.set_title("W5 mode eligibility: covariate balance\n"
                 "|SMD|>0.1 highlighted — potential selection bias on that variable")
    fig.tight_layout()
    save(fig, "sensitivity/mode_selection_balance.png")


# ----------------------------------------------------------------------
# 11. Attrition balance
# ----------------------------------------------------------------------
def plot_attrition_balance() -> None:
    # Universe = W1 saturated-school network respondents (IDGX2 non-NA in w1network).
    # Responded = has valid W4 cognitive (C4WD90_1 non-NA).
    w1net = pd.read_parquet(ROOT / "outputs" / "cache" / "w1network.parquet")
    w4 = load_analytic_w4()
    w4_resp = set(w4.loc[w4["C4WD90_1"].notna(), "AID"].astype(str))

    network = w1net.dropna(subset=["IDGX2"]).copy()
    network["responded_w4"] = network["AID"].astype(str).isin(w4_resp)
    network["idg_dec"] = pd.qcut(network["IDGX2"], 10, labels=False, duplicates="drop")
    rates = network.groupby("idg_dec")["responded_w4"].mean()
    counts = network.groupby("idg_dec").size()
    means = network.groupby("idg_dec")["IDGX2"].mean()

    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(means, rates, "o-", color="#2874a6", markersize=7)
    ax.set_ylim(0, 1)
    ax.set_xlabel("Mean IDGX2 (decile)")
    ax.set_ylabel("W4 cognitive-response rate")
    ax.set_title("W4 response rate by IDGX2 decile\n"
                 "(flat line = attrition unrelated to network position)")
    for x, y_, n in zip(means, rates, counts):
        ax.text(x, y_ + 0.01, f"n={n}", ha="center", fontsize=7, color="#555")
    annotate_n(ax, int(len(network)))
    fig.tight_layout()
    save(fig, "sensitivity/attrition_balance.png")


# ----------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------
if __name__ == "__main__":
    steps = [
        ("forest", plot_forest),
        ("quintile_dose_response", plot_quintile_dose_response),
        ("weighted_vs_unweighted", plot_weighted_vs_unweighted),
        ("composite_vs_components", plot_composite_vs_components),
        ("partial_residual", plot_partial_residual),
        ("placebo_panel", plot_placebo_panel),
        ("heterogeneity", plot_heterogeneity),
        ("ahpvt_with_without", plot_ahpvt_with_without),
        ("saturated_vs_full", plot_saturated_vs_full),
        ("mode_selection_balance", plot_mode_selection_balance),
        ("attrition_balance", plot_attrition_balance),
    ]
    for name, fn in steps:
        print(f"... {name}")
        try:
            fn()
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            raise
    print("Done.")

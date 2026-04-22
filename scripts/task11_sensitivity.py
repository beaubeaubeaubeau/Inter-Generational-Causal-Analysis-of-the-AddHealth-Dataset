"""Task 11 - Sensitivity analyses and verification checks.

Implements from the verification plan:
  - Weighted-vs-unweighted coefficient comparison (all primary specs)
  - VIF + pairwise correlation for network measures
  - Permutation placebo for IDGX2 (500 reps, within-PSU shuffle)
  - AHPVT bad-control coefficient shift tracker
  - Saturated-school selection balance (4397 vs 6504)
  - W5 mode-selection probit (does IDGX2 predict mode assignment?)

Outputs:
  outputs/11_sensitivity.md
  outputs/11_placebo_permutation.csv
  outputs/11_collinearity.csv
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from analysis_utils import (  # noqa: E402
    ROOT, CACHE, clean_var, weighted_ols, weighted_mean_se, weighted_prop_ci,
)

OUT = ROOT / "outputs"
RNG = np.random.default_rng(42)

W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
W1_FULL = pd.read_parquet(CACHE / "analytic_w1_full.parquet")
W5_MODE = pd.read_parquet(CACHE / "analytic_w5_mode_audit.parquet")
W1_ALL = pd.read_parquet(CACHE / "w1inhome.parquet")
W1_NET = pd.read_parquet(CACHE / "w1network.parquet")


def race_dummies(df):
    out = pd.DataFrame(index=df.index)
    for lvl in ["NH-Black", "Hispanic", "Other"]:
        out[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    out.loc[df["RACE"].isna(), :] = np.nan
    return out


def build_design_idgx2(df, exp_col="IDGX2", include_ahpvt=True):
    parts = [
        df[exp_col].rename("exposure"),
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index),
        race_dummies(df),
        df["PARENT_ED"].rename("parent_ed"),
        df["CESD_SUM"].rename("cesd_sum"),
        df["H1GH1"].rename("srh"),
    ]
    if include_ahpvt:
        parts.append(df["AH_RAW"].rename("ahpvt"))
    X = pd.concat(parts, axis=1)
    X.insert(0, "const", 1.0)
    return X


# ---------------------------------------------------------------------------
# 1. Weighted vs unweighted
# ---------------------------------------------------------------------------
def weighted_vs_unweighted() -> pd.DataFrame:
    """For each primary exposure, fit weighted and unweighted OLS and compare."""
    rows = []
    specs = [
        ("IDGX2 linear", W4, "IDGX2", "W4_COG_COMP", "GSWGT4_2"),
        ("ODGX2 placebo", W4, "ODGX2", "W4_COG_COMP", "GSWGT4_2"),
        ("BCENT10X", W4, "BCENT10X", "W4_COG_COMP", "GSWGT4_2"),
        ("REACH", W4, "REACH", "W4_COG_COMP", "GSWGT4_2"),
        ("Isolation (<=1)", W4, "IDG_LEQ1", "W4_COG_COMP", "GSWGT4_2"),
        ("School belong (full)", W1_FULL, "SCHOOL_BELONG", "W4_COG_COMP", "GSWGT4_2"),
    ]
    for label, df, exp, y_col, w_col in specs:
        X = build_design_idgx2(df, exp_col=exp, include_ahpvt=True)
        y = df[y_col].values
        psu = df["CLUSTER2"].values
        w = df[w_col].values
        res_w = weighted_ols(y, X.values, w, psu, column_names=list(X.columns))
        res_u = weighted_ols(y, X.values, np.ones_like(w), psu,
                             column_names=list(X.columns))
        if res_w is None or res_u is None:
            continue
        rows.append({
            "spec": label,
            "beta_weighted": res_w["beta"]["exposure"],
            "se_weighted": res_w["se"]["exposure"],
            "t_weighted": res_w["t"]["exposure"],
            "p_weighted": res_w["p"]["exposure"],
            "beta_unweighted": res_u["beta"]["exposure"],
            "se_unweighted": res_u["se"]["exposure"],
            "t_unweighted": res_u["t"]["exposure"],
            "p_unweighted": res_u["p"]["exposure"],
            "sign_flip": (
                (res_w["beta"]["exposure"] * res_u["beta"]["exposure"]) < 0
            ),
            "t_ratio": (
                abs(res_w["t"]["exposure"]) / max(abs(res_u["t"]["exposure"]), 1e-6)
            ),
            "n": res_w["n"],
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 2. VIF + correlation
# ---------------------------------------------------------------------------
def collinearity() -> Tuple[pd.DataFrame, pd.DataFrame]:
    import statsmodels.api as sm
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    cols = ["IDGX2", "ODGX2", "BCENT10X", "REACH", "PRXPREST"]
    sub = W4[cols].dropna()
    # Correlation
    corr = sub.corr()
    # VIF requires constant
    X = sm.add_constant(sub)
    vifs = []
    for i, c in enumerate(X.columns):
        if c == "const":
            continue
        vif = variance_inflation_factor(X.values, i)
        vifs.append({"variable": c, "VIF": vif})
    return pd.DataFrame(vifs), corr


# ---------------------------------------------------------------------------
# 3. Permutation placebo: shuffle IDGX2 within PSU, refit, collect
# ---------------------------------------------------------------------------
def permutation_placebo(n_perm=500) -> pd.DataFrame:
    df = W4.dropna(subset=["IDGX2", "W4_COG_COMP", "BIO_SEX", "PARENT_ED",
                           "CESD_SUM", "H1GH1", "AH_RAW", "RACE", "CLUSTER2",
                           "GSWGT4_2"]).copy()
    betas = []
    for i in range(n_perm):
        df["idg_perm"] = (
            df.groupby("CLUSTER2")["IDGX2"]
              .transform(lambda x: RNG.permutation(x.values))
        )
        X = build_design_idgx2(df.assign(IDGX2=df["idg_perm"]))
        res = weighted_ols(df["W4_COG_COMP"].values, X.values,
                           df["GSWGT4_2"].values, df["CLUSTER2"].values,
                           column_names=list(X.columns))
        if res is not None:
            betas.append(res["beta"]["exposure"])
    perm = pd.DataFrame({"beta_permuted": betas})
    # Observed beta
    X = build_design_idgx2(df)
    res_obs = weighted_ols(df["W4_COG_COMP"].values, X.values,
                           df["GSWGT4_2"].values, df["CLUSTER2"].values,
                           column_names=list(X.columns))
    perm.attrs["observed_beta"] = float(res_obs["beta"]["exposure"])
    perm.attrs["p_perm"] = float(
        np.mean(np.abs(perm["beta_permuted"]) >= abs(perm.attrs["observed_beta"]))
    )
    return perm


# ---------------------------------------------------------------------------
# 4. AHPVT bad-control: coefficient shift when AHPVT is included
# ---------------------------------------------------------------------------
def ahpvt_shift(regressions_csv: Path) -> pd.DataFrame:
    df = pd.read_csv(regressions_csv)
    exp_terms = ("idgx2", "odgx2_placebo", "bcent10x", "reach", "prxprest",
                 "idg_zero", "idg_leq1", "school_belong",
                 "friend_n", "friend_contact", "friend_disclose")
    mask = df["term"].isin(exp_terms)
    sub = df[mask].copy()
    # Match adjusted/unadjusted within spec family
    rows = []
    for (outcome, term), grp in sub.groupby(["outcome", "term"]):
        with_pvt = grp[grp["ahpvt_adjusted"]]
        without_pvt = grp[~grp["ahpvt_adjusted"]]
        if len(with_pvt) == 0 or len(without_pvt) == 0:
            continue
        bw = with_pvt["beta"].iloc[0]
        bnw = without_pvt["beta"].iloc[0]
        shrinkage = (bnw - bw) / bnw if bnw != 0 else np.nan
        rows.append({
            "outcome": outcome,
            "term": term,
            "beta_with_ahpvt": bw,
            "beta_without_ahpvt": bnw,
            "pct_shrinkage_from_adjustment": shrinkage,
            "flag_large_shift": abs(shrinkage) > 0.5,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 5. Saturated-school selection balance
# ---------------------------------------------------------------------------
def saturated_school_balance() -> pd.DataFrame:
    w1net_aids = set(W1_NET.loc[W1_NET["IDGX2"].notna(), "AID"])
    w1all = W1_ALL.copy()
    w1all["in_network"] = w1all["AID"].isin(w1net_aids).astype(int)
    vars_compare = ["BIO_SEX", "AH_RAW", "H1GI4", "H1GI6B", "H1GH1", "PA12", "PA55"]
    rows = []
    for v in vars_compare:
        vv = clean_var(w1all[v], v)
        for group in [0, 1]:
            mask = (w1all["in_network"] == group) & vv.notna()
            m = vv[mask].mean()
            n = mask.sum()
            rows.append({"variable": v, "group": "in_network" if group == 1 else "out_network",
                         "n": int(n), "mean": float(m)})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 6. W5 mode-selection: does IDGX2 predict in-person|phone (vs web|mail)?
# ---------------------------------------------------------------------------
def w5_mode_selection() -> Dict:
    """Probit of IS_COG_MODE on IDGX2 + baselines, among all W5 respondents
    who are in W1 network file."""
    import statsmodels.api as sm

    df = (
        W1_ALL[["AID", "BIO_SEX", "AH_RAW"]]
        .merge(W1_NET[["AID", "IDGX2"]], on="AID", how="left")
        .merge(W5_MODE, on="AID", how="inner")
    )
    df["male"] = (df["BIO_SEX"] == 1).astype(float)
    df["ahpvt"] = clean_var(df["AH_RAW"], "AH_RAW")
    df["idgx2"] = clean_var(df["IDGX2"], "IDGX2")
    df = df.dropna(subset=["IS_COG_MODE", "idgx2", "male", "ahpvt"])
    X = sm.add_constant(df[["idgx2", "male", "ahpvt"]])
    y = df["IS_COG_MODE"]
    model = sm.Probit(y, X).fit(disp=False)
    rows = []
    for term in X.columns:
        rows.append({
            "term": term,
            "coef": float(model.params[term]),
            "se": float(model.bse[term]),
            "z": float(model.tvalues[term]),
            "p": float(model.pvalues[term]),
        })
    return {"table": pd.DataFrame(rows), "n": int(len(df)),
            "pseudo_r2": float(model.prsquared)}


# ---------------------------------------------------------------------------
# Markdown writer
# ---------------------------------------------------------------------------
def write_report(path, wu, vif_df, corr, perm, shift, balance, mode_sel):
    L: List[str] = ["# Task 11 - Sensitivity analyses", ""]
    L.append("## 1. Weighted vs unweighted (primary exposures)")
    L.append("")
    L.append("Any sign flip or |t_w/t_u| > 3 is flagged.")
    L.append("")
    L.append(wu.to_markdown(index=False))
    L.append("")

    L.append("## 2. Collinearity among network centrality measures")
    L.append("")
    L.append("Variance-inflation factors:")
    L.append("")
    L.append(vif_df.to_markdown(index=False))
    L.append("")
    L.append("Pairwise Pearson correlations:")
    L.append("")
    L.append(corr.round(3).to_markdown())
    L.append("")

    L.append("## 3. Permutation placebo: IDGX2 within-PSU shuffle (500 reps)")
    L.append("")
    L.append(f"- **Observed β (IDGX2 -> W4_COG_COMP)**: {perm.attrs['observed_beta']:.4f}")
    L.append(f"- **Permutation p-value** (two-sided): {perm.attrs['p_perm']:.3f}")
    L.append(f"- **Permuted null**: mean={perm['beta_permuted'].mean():.4f}, "
             f"SD={perm['beta_permuted'].std():.4f}, "
             f"95%: [{perm['beta_permuted'].quantile(0.025):.4f}, "
             f"{perm['beta_permuted'].quantile(0.975):.4f}]")
    L.append("")

    L.append("## 4. AHPVT bad-control shift")
    L.append("")
    L.append("Percent shrinkage = (β_without − β_with) / β_without. "
             "Values >0.5 are flagged as suggestive of mediation "
             "(AHPVT may be on the causal pathway rather than a confounder).")
    L.append("")
    L.append(shift.to_markdown(index=False))
    L.append("")

    L.append("## 5. Saturated-school selection balance")
    L.append("")
    L.append("Mean of baseline covariates in respondents with vs. without W1 "
             "network data. Large differences imply generalizability caveats.")
    L.append("")
    L.append(balance.pivot(index="variable", columns="group",
                           values=["mean", "n"]).round(3).to_markdown())
    L.append("")

    L.append("## 6. W5 mode-selection probit")
    L.append("")
    L.append("P(cognitive-eligible mode: in-person or phone) ~ IDGX2 + male + AHPVT.")
    L.append(f"N = {mode_sel['n']:,}; pseudo-R² = {mode_sel['pseudo_r2']:.4f}")
    L.append("")
    L.append(mode_sel["table"].to_markdown(index=False))
    L.append("")
    L.append("**Interpretation.** If IDGX2's probit coefficient is near zero, "
             "W5 mode restriction is unlikely to bias the W1→W5 regression on "
             "network position.")
    L.append("")

    path.write_text("\n".join(L))


def main() -> None:
    print("1. Weighted vs unweighted ...")
    wu = weighted_vs_unweighted()

    print("2. Collinearity ...")
    vif_df, corr = collinearity()

    print("3. Permutation placebo (500 reps, may take ~60s) ...")
    perm = permutation_placebo(n_perm=500)
    perm.to_csv(OUT / "11_placebo_permutation.csv", index=False)

    print("4. AHPVT bad-control shift ...")
    shift = ahpvt_shift(OUT / "10_regressions.csv")

    print("5. Saturated-school balance ...")
    balance = saturated_school_balance()

    print("6. W5 mode-selection probit ...")
    mode_sel = w5_mode_selection()

    vif_df.to_csv(OUT / "11_collinearity.csv", index=False)
    corr.to_csv(OUT / "11_correlation.csv")
    shift.to_csv(OUT / "11_ahpvt_shift.csv", index=False)
    balance.to_csv(OUT / "11_saturated_balance.csv", index=False)

    write_report(OUT / "11_sensitivity.md", wu, vif_df, corr, perm, shift,
                 balance, mode_sel)
    print("Wrote sensitivity outputs.")


if __name__ == "__main__":
    main()

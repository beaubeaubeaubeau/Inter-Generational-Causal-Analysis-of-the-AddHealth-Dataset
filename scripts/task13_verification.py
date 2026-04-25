"""Task 13 - Final verification pass.

Covers the plan's verification items not yet handled in task10/11:

  1. Published-benchmark weighted means (BIO_SEX, NH-Black, AH_PVT, IDGX2).
  2. Reserve-code leakage assertions on the merged analytic frame.
  3. Reserve-code sensitivity (NA vs 0 vs own-category) on primary IDGX2 spec.
  4. DEFF and cluster-SE / naive-SE ratio for the primary spec.
  5. Negative-control OUTCOME (adult height at W4).
  6. Negative-control EXPOSURE (American-Indian indicator → W4 composite).
  7. Differential-attrition IPW re-fit of the anchor model.
  8. BH-FDR multiple-testing adjustment on primary-exposure p-values.
  9. Weight-sum and PSU counts.
 10. CLUSTER2 missingness assertion.

Writes outputs/13_verification.md plus CSV artefacts.
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from analysis_utils import (  # noqa: E402
    weighted_ols,
    VALID_RANGES,
)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
CACHE = OUT / "cache"

np.random.seed(20260419)

# ----------------------------------------------------------------------
# Load frames
# ----------------------------------------------------------------------
W4 = pd.read_parquet(CACHE / "analytic_w4.parquet").copy()
W1FULL = pd.read_parquet(CACHE / "analytic_w1_full.parquet").copy()
W1NET = pd.read_parquet(CACHE / "w1network.parquet")
W1HOME = pd.read_parquet(CACHE / "w1inhome.parquet")
W4HOME = pd.read_parquet(CACHE / "w4inhome.parquet")

# Build base covariates on W4
W4["male"] = (W4["BIO_SEX"] == 1).astype(float)
for lvl in ["NH-Black", "Hispanic", "Other"]:
    W4[f"race_{lvl}"] = (W4["RACE"] == lvl).astype(float)
W4.loc[W4["RACE"].isna(), [f"race_{x}" for x in ["NH-Black", "Hispanic", "Other"]]] = np.nan
W4["parent_ed"] = W4["PARENT_ED"]
W4["cesd_sum"] = W4["CESD_SUM"]
W4["srh"] = W4["H1GH1"]
W4["ahpvt"] = W4["AH_RAW"]

COVARS = ["male", "race_NH-Black", "race_Hispanic", "race_Other",
          "parent_ed", "cesd_sum", "srh", "ahpvt"]

sections: list[str] = []


def wmean(x: np.ndarray, w: np.ndarray) -> float:
    m = ~np.isnan(x) & ~np.isnan(w) & (w > 0)
    if m.sum() == 0:
        return float("nan")
    return float(np.sum(w[m] * x[m]) / np.sum(w[m]))


# ----------------------------------------------------------------------
# 1. Published-benchmark weighted means
# ----------------------------------------------------------------------
w1w = W1FULL.dropna(subset=["GSWGT1"]).copy()
w1w["male"] = (w1w["BIO_SEX"] == 1).astype(float)
w1w["nhblack"] = (w1w["RACE"] == "NH-Black").astype(float)

benchmarks = {
    "pct_male": (wmean(w1w["male"].values, w1w["GSWGT1"].values), 0.508),
    "pct_NH_Black": (wmean(w1w["nhblack"].values, w1w["GSWGT1"].values), 0.161),
    "mean_AH_PVT": (wmean(w1w["AH_PVT"].values, w1w["GSWGT1"].values), 100.7),
}
# IDGX2 uses W1 network saturated + GSWGT1
net = W1NET.merge(W1FULL[["AID", "GSWGT1"]], on="AID", how="left")
net["IDGX2"] = pd.to_numeric(net["IDGX2"], errors="coerce")
net.loc[~net["IDGX2"].between(0, 50), "IDGX2"] = np.nan
benchmarks["mean_IDGX2"] = (
    wmean(net["IDGX2"].values, net["GSWGT1"].values),
    4.6,
)

bench_rows = []
for k, (obs, pub) in benchmarks.items():
    diff = obs - pub
    bench_rows.append({"metric": k, "observed": obs, "published": pub,
                       "abs_diff": abs(diff)})
bench_df = pd.DataFrame(bench_rows)
bench_df.to_csv(OUT / "13_benchmarks.csv", index=False)
sections.append("## 1. Published-benchmark weighted means\n\n" + bench_df.to_markdown(index=False))


# ----------------------------------------------------------------------
# 2. Reserve-code leakage assertion
# ----------------------------------------------------------------------
leak_rows = []
for col in W4.columns:
    if col not in VALID_RANGES:
        continue
    lo, hi = VALID_RANGES[col]
    vals = pd.to_numeric(W4[col], errors="coerce").dropna()
    if vals.empty:
        continue
    vmax, vmin = float(vals.max()), float(vals.min())
    out_of_range = ((vals < lo) | (vals > hi)).sum()
    leak_rows.append({
        "variable": col, "valid_range": f"[{lo}, {hi}]",
        "min": vmin, "max": vmax, "n_out_of_range": int(out_of_range),
    })
leak_df = pd.DataFrame(leak_rows)
leak_df.to_csv(OUT / "13_reserve_leakage.csv", index=False)
n_bad = int((leak_df["n_out_of_range"] > 0).sum())
sections.append(
    "## 2. Reserve-code leakage assertion\n\n"
    f"- Columns checked: {len(leak_df)}\n"
    f"- Columns with any out-of-valid-range values: **{n_bad}**\n"
    f"- Detailed CSV: `outputs/13_reserve_leakage.csv`\n"
)


# ----------------------------------------------------------------------
# 3. Reserve-code sensitivity on primary spec
# ----------------------------------------------------------------------
# Re-run S01C with CES-D reserve codes handled as (a) NA [baseline], (b) 0, (c) own category.
# CES-D items H1FS1..H1FS19: reserve codes are 6/8 in raw data.

cesd_cols = [f"H1FS{i}" for i in range(1, 20)]
reverse = {4, 8, 11, 15}

def build_cesd(mode: str) -> pd.Series:
    d = W1HOME[cesd_cols].copy()
    for c in d.columns:
        raw = pd.to_numeric(d[c], errors="coerce")
        valid_mask = raw.between(0, 3)
        item_num = int(c.replace("H1FS", ""))
        # reverse-code valid responses first
        scored = raw.where(valid_mask)
        if item_num in reverse:
            scored = 3 - scored
        if mode == "na":
            out = scored
        elif mode == "zero":
            out = scored.fillna(0)
        elif mode == "category":
            # keep scored values for valid responses, set reserve codes to -1
            out = scored.where(valid_mask, -1)
        d[c] = out
    return d.sum(axis=1, min_count=len(cesd_cols) if mode == "na" else 1)


primary_rows = []
for mode in ["na", "zero", "category"]:
    w4 = W4.copy()
    cesd_new = build_cesd(mode).reindex(w4.index)
    # Re-attach by AID
    aid_to_cesd = pd.Series(build_cesd(mode).values, index=W1HOME["AID"])
    w4["cesd_sum"] = w4["AID"].map(aid_to_cesd)

    keep = ["IDGX2", "W4_COG_COMP", "GSWGT4_2", "CLUSTER2"] + COVARS
    d = w4.dropna(subset=keep).copy()
    Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
    Xdf["IDGX2"] = d["IDGX2"].values
    for c in COVARS:
        Xdf[c] = d[c].values
    names = ["const", "IDGX2"] + COVARS
    y = d["W4_COG_COMP"].astype(float).values
    w = d["GSWGT4_2"].astype(float).values
    psu = d["CLUSTER2"].astype(int).values
    res = weighted_ols(y, Xdf.values, w, psu, names)
    primary_rows.append({
        "cesd_reserve_mode": mode,
        "beta_idgx2": float(res["beta"]["IDGX2"]),
        "se": float(res["se"]["IDGX2"]),
        "p": float(res["p"]["IDGX2"]),
        "n": int(res["n"]),
    })
primary_df = pd.DataFrame(primary_rows)
primary_df.to_csv(OUT / "13_reserve_code_sensitivity.csv", index=False)
sections.append("## 3. Reserve-code sensitivity (CES-D handling)\n\n" + primary_df.to_markdown(index=False))


# ----------------------------------------------------------------------
# 4. DEFF and cluster-SE / naive-SE ratio
# ----------------------------------------------------------------------
import statsmodels.api as sm

keep = ["IDGX2", "W4_COG_COMP", "GSWGT4_2", "CLUSTER2"] + COVARS
d = W4.dropna(subset=keep).copy()
Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
Xdf["IDGX2"] = d["IDGX2"].values
for c in COVARS:
    Xdf[c] = d[c].values
X = Xdf.values
y = d["W4_COG_COMP"].astype(float).values
w = d["GSWGT4_2"].astype(float).values
psu = d["CLUSTER2"].astype(int).values

wls = sm.WLS(y, X, weights=w).fit()
naive_se = wls.bse[1]  # IDGX2 is col 1
cluster = sm.WLS(y, X, weights=w).fit(
    cov_type="cluster", cov_kwds={"groups": psu, "use_correction": True}, use_t=True,
)
cluster_se = cluster.bse[1]
se_ratio = cluster_se / naive_se

# DEFF on the outcome — ratio of weighted-variance / simple-variance of beta
# Use heuristic: 1 + (CV_w^2) * (1 - intra-cluster corr), approximated as (cluster_se/naive_se)**2
deff_primary = se_ratio ** 2

deff_row = pd.DataFrame([{
    "spec": "S01C IDGX2 -> W4_COG_COMP",
    "naive_se": naive_se,
    "cluster_se": cluster_se,
    "se_ratio": se_ratio,
    "deff_proxy": deff_primary,
}])
deff_row.to_csv(OUT / "13_deff.csv", index=False)
sections.append("## 4. DEFF and cluster-SE / naive-SE ratio (primary spec)\n\n" + deff_row.to_markdown(index=False))


# ----------------------------------------------------------------------
# 5. Negative-control OUTCOME: adult height at W4
# ----------------------------------------------------------------------
# H4GH5F = feet, H4GH5I = inches. Valid reserve codes 96/98/99 for missing.
height = W4HOME[["AID", "H4GH5F", "H4GH5I"]].copy()
height["H4GH5F"] = pd.to_numeric(height["H4GH5F"], errors="coerce").where(lambda s: s.between(4, 7))
height["H4GH5I"] = pd.to_numeric(height["H4GH5I"], errors="coerce").where(lambda s: s.between(0, 11))
height["HEIGHT_IN"] = height["H4GH5F"] * 12 + height["H4GH5I"]
w4h = W4.merge(height[["AID", "HEIGHT_IN"]], on="AID", how="left")

keep_h = ["IDGX2", "HEIGHT_IN", "GSWGT4_2", "CLUSTER2"] + COVARS
d = w4h.dropna(subset=keep_h).copy()
Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
Xdf["IDGX2"] = d["IDGX2"].values
for c in COVARS:
    Xdf[c] = d[c].values
X = Xdf.values
y = d["HEIGHT_IN"].astype(float).values
w = d["GSWGT4_2"].astype(float).values
psu = d["CLUSTER2"].astype(int).values
names = ["const", "IDGX2"] + COVARS
nco = weighted_ols(y, X, w, psu, names)
nco_row = pd.DataFrame([{
    "outcome": "HEIGHT_IN",
    "beta_idgx2": float(nco["beta"]["IDGX2"]),
    "se": float(nco["se"]["IDGX2"]),
    "p": float(nco["p"]["IDGX2"]),
    "n": int(nco["n"]),
}])
nco_row.to_csv(OUT / "13_negctrl_outcome.csv", index=False)
sections.append(
    "## 5. Negative-control OUTCOME: adult height (inches)\n\n"
    "IDGX2 should not predict adult height if our adjustment set is adequate.\n\n"
    + nco_row.to_markdown(index=False)
)


# ----------------------------------------------------------------------
# 6. Negative-control EXPOSURE: American-Indian indicator (H1GI6C)
# ----------------------------------------------------------------------
ai = W1HOME[["AID", "H1GI6C"]].copy()
ai["H1GI6C"] = pd.to_numeric(ai["H1GI6C"], errors="coerce").where(lambda s: s.isin([0, 1]))
w4a = W4.merge(ai, on="AID", how="left")
keep_a = ["H1GI6C", "W4_COG_COMP", "GSWGT4_2", "CLUSTER2"] + COVARS
d = w4a.dropna(subset=keep_a).copy()
Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
Xdf["AI"] = d["H1GI6C"].values
for c in COVARS:
    Xdf[c] = d[c].values
X = Xdf.values
y = d["W4_COG_COMP"].astype(float).values
w = d["GSWGT4_2"].astype(float).values
psu = d["CLUSTER2"].astype(int).values
names = ["const", "AI"] + COVARS
nce = weighted_ols(y, X, w, psu, names)
nce_row = pd.DataFrame([{
    "exposure": "H1GI6C (AI/AN)",
    "beta": float(nce["beta"]["AI"]),
    "se": float(nce["se"]["AI"]),
    "p": float(nce["p"]["AI"]),
    "n": int(nce["n"]),
}])
nce_row.to_csv(OUT / "13_negctrl_exposure.csv", index=False)
sections.append(
    "## 6. Negative-control EXPOSURE: American-Indian indicator (H1GI6C)\n\n"
    "A baseline indicator with no theoretical link to cognitive outcomes — should be null under adjustment.\n\n"
    + nce_row.to_markdown(index=False)
)


# ----------------------------------------------------------------------
# 7. Attrition-IPW re-fit of anchor model
# ----------------------------------------------------------------------
# Universe = W1 saturated-school network respondents (IDGX2 non-missing in w1network).
# Stage 1: P(responded to W4 cognitive | W1 baselines).
# Stage 2: refit S01C with IPW = 1 / fitted probability on responders.

w1net2 = W1NET[["AID", "IDGX2"]].copy()
w1net2["IDGX2"] = pd.to_numeric(w1net2["IDGX2"], errors="coerce").where(lambda s: s.between(0, 50))
w1net2 = w1net2.dropna(subset=["IDGX2"])

# Rebuild baselines directly from W1HOME (so universe isn't restricted to W4)
# plus network file for weight.
base = W1HOME[["AID", "BIO_SEX", "H1GH1"]].copy()
base["AH_RAW"] = pd.to_numeric(W1HOME.get("AH_PVT"), errors="coerce").where(lambda s: s.between(0, 200))
base["BIO_SEX"] = pd.to_numeric(base["BIO_SEX"], errors="coerce").where(lambda s: s.between(1, 2))
base["H1GH1"] = pd.to_numeric(base["H1GH1"], errors="coerce").where(lambda s: s.between(1, 5))

# Race and parent-ed already derived in analytic_w1_full under the AID that appears in W4.
# For those not in W4, approximate from W1HOME raw columns. Simplest: approximate race
# via H1GI4 (Hispanic) + H1GI6A (white) + H1GI6B (black). For parent-ed, use H1RM1/H1RF1.
w1race = W1HOME[["AID", "H1GI4", "H1GI6A", "H1GI6B", "H1GI6C", "H1GI6D", "H1GI6E",
                 "H1RM1", "H1RF1"]].copy()
for c in ["H1GI4", "H1GI6A", "H1GI6B"]:
    w1race[c] = pd.to_numeric(w1race[c], errors="coerce").where(lambda s: s.between(0, 1))
hisp = w1race["H1GI4"].fillna(0) == 1
black = (w1race["H1GI6B"].fillna(0) == 1) & (~hisp)
white = (w1race["H1GI6A"].fillna(0) == 1) & (~hisp) & (~black)
other = ~hisp & ~black & ~white
w1race["RACE"] = np.where(hisp, "Hispanic",
                  np.where(black, "NH-Black",
                  np.where(white, "NH-White", "Other")))
# Parent-ed: max of H1RM1 and H1RF1, valid 1–9 (remove reserve codes)
for c in ["H1RM1", "H1RF1"]:
    w1race[c] = pd.to_numeric(w1race[c], errors="coerce").where(lambda s: s.between(1, 9))
w1race["PARENT_ED"] = w1race[["H1RM1", "H1RF1"]].max(axis=1)

# CES-D sum from W1HOME (use the build_cesd "na" mode result)
cesd = build_cesd("na")
cesd.name = "CESD_SUM"
cesd.index = W1HOME["AID"].values

base = base.merge(w1race[["AID", "RACE", "PARENT_ED"]], on="AID", how="left")
base = base.merge(cesd.rename("CESD_SUM").reset_index().rename(columns={"index": "AID"}),
                  on="AID", how="left")

# Weight
base = base.merge(W1FULL[["AID", "GSWGT1"]].drop_duplicates("AID"), on="AID", how="left")

u = w1net2.merge(base, on="AID", how="left").dropna(
    subset=["BIO_SEX", "AH_RAW", "RACE", "PARENT_ED", "CESD_SUM", "H1GH1", "GSWGT1"]
)
u["male"] = (u["BIO_SEX"] == 1).astype(float)
for lvl in ["NH-Black", "Hispanic", "Other"]:
    u[f"race_{lvl}"] = (u["RACE"] == lvl).astype(float)
u["parent_ed"] = u["PARENT_ED"]
u["cesd_sum"] = u["CESD_SUM"]
u["srh"] = u["H1GH1"]
u["ahpvt"] = u["AH_RAW"]
resp_set = set(W4.loc[W4["W4_COG_COMP"].notna(), "AID"].astype(str))
u["responded"] = u["AID"].astype(str).isin(resp_set).astype(int)

logit_cols = ["male", "race_NH-Black", "race_Hispanic", "race_Other",
              "parent_ed", "cesd_sum", "srh", "ahpvt", "IDGX2"]
Xl = sm.add_constant(u[logit_cols].values)
try:
    logit = sm.Logit(u["responded"].values, Xl).fit(disp=0, maxiter=100)
    phat = logit.predict(Xl)
    u["ipw"] = 1.0 / np.clip(phat, 0.05, 1.0)  # trim extreme weights
except Exception as e:
    print(f"[warn] logit failed: {e}")
    u["ipw"] = 1.0

ipw_map = u.set_index("AID")["ipw"]
w4i = W4.merge(ipw_map.rename("ATTR_IPW"), left_on="AID", right_index=True, how="left")
w4i["IPW_SW"] = w4i["GSWGT4_2"] * w4i["ATTR_IPW"]

keep = ["IDGX2", "W4_COG_COMP", "IPW_SW", "CLUSTER2"] + COVARS
d = w4i.dropna(subset=keep).copy()
Xdf = pd.DataFrame({"const": 1.0}, index=d.index)
Xdf["IDGX2"] = d["IDGX2"].values
for c in COVARS:
    Xdf[c] = d[c].values
X = Xdf.values
y = d["W4_COG_COMP"].astype(float).values
w = d["IPW_SW"].astype(float).values
psu = d["CLUSTER2"].astype(int).values
names = ["const", "IDGX2"] + COVARS
ipw_res = weighted_ols(y, X, w, psu, names)
ipw_rows = pd.DataFrame([
    {"spec": "Primary (GSWGT4_2 only)",
     "beta_idgx2": 0.00926, "p": 0.0154, "n": 3268},
    {"spec": "With attrition IPW",
     "beta_idgx2": float(ipw_res["beta"]["IDGX2"]),
     "p": float(ipw_res["p"]["IDGX2"]),
     "n": int(ipw_res["n"])},
])
ipw_rows.to_csv(OUT / "13_attrition_ipw.csv", index=False)
sections.append(
    "## 7. Attrition IPW re-fit of anchor model (S01C)\n\n"
    f"Stage-1 logit pseudo-R² = {logit.prsquared:.4f}, N = {int(logit.nobs)}.\n\n"
    + ipw_rows.to_markdown(index=False)
)


# ----------------------------------------------------------------------
# 8. BH-FDR multiple testing adjustment
# ----------------------------------------------------------------------
coefs = pd.read_csv(OUT / "10_regressions.csv")
# Primary family: each exposure → W4_COG_COMP (or C4WD90_1 for S01), with AHPVT adjusted.
FAMILY = [
    ("S01", "idgx2"),
    ("S01C", "idgx2"),
    ("S04_ODGX2_placebo", "odgx2_placebo"),
    ("S04_BCENT10X", "bcent10x"),
    ("S04_REACH", "reach"),
    ("S04_PRXPREST", "prxprest"),
    ("S05_ZERO", "idg_zero"),
    ("S05_LEQ1", "idg_leq1"),
    ("S06", "school_belong"),
    ("S07", "lonely"),
    ("S10_nominees", "friend_n"),
    ("S10_contact", "friend_contact"),
    ("S10_disclose", "friend_disclose"),
]
fam = []
for spec, term in FAMILY:
    r = coefs[(coefs.spec_id == spec) & (coefs.term == term)].iloc[0]
    fam.append({"spec": spec, "term": term, "beta": r.beta, "p": r.p})
fam = pd.DataFrame(fam).sort_values("p").reset_index(drop=True)
m = len(fam)
fam["rank"] = np.arange(1, m + 1)
fam["bh_threshold"] = 0.05 * fam["rank"] / m
# BH-FDR q-values: q_i = min over j >= i of (m/j)*p_(j)
p_sorted = fam["p"].values
q = np.empty(m)
running_min = 1.0
for j in range(m - 1, -1, -1):
    running_min = min(running_min, p_sorted[j] * m / (j + 1))
    q[j] = running_min
fam["q_BH"] = q
fam["reject_at_q0.05"] = fam["q_BH"] < 0.05
fam.to_csv(OUT / "13_bh_fdr.csv", index=False)
sections.append("## 8. BH-FDR multiple-testing adjustment (primary family)\n\n" + fam.to_markdown(index=False))


# ----------------------------------------------------------------------
# 9. Weight sums + PSU counts
# ----------------------------------------------------------------------
psu_counts = {
    "W1 (all analytic_w1_full)": (W1FULL["CLUSTER2"].nunique(), W1FULL.shape[0]),
    "W4 analytic": (W4["CLUSTER2"].nunique(), W4.shape[0]),
    "W4 with valid cognitive": (
        W4.dropna(subset=["C4WD90_1"])["CLUSTER2"].nunique(),
        W4.dropna(subset=["C4WD90_1"]).shape[0]),
}
w5f = pd.read_parquet(CACHE / "analytic_w5.parquet")
psu_counts["W5 analytic (I/T modes)"] = (w5f["CLUSTER2"].nunique(), w5f.shape[0])

w_sum_w4 = float(W4["GSWGT4_2"].dropna().sum())
w_sum_w1 = float(W1FULL["GSWGT1"].dropna().sum())
psu_rows = [{"frame": k, "n_psu": v[0], "n_rows": v[1]} for k, v in psu_counts.items()]
psu_df = pd.DataFrame(psu_rows)
psu_df.to_csv(OUT / "13_psu_counts.csv", index=False)
sections.append(
    "## 9. Weight sums and PSU counts\n\n"
    f"- Sum(GSWGT1) across W1 analytic = **{w_sum_w1:,.0f}**\n"
    f"- Sum(GSWGT4_2) across W4 analytic = **{w_sum_w4:,.0f}**\n\n"
    + psu_df.to_markdown(index=False)
)


# ----------------------------------------------------------------------
# 10. CLUSTER2 missingness assertion
# ----------------------------------------------------------------------
miss = {
    "W1 full": int(W1FULL["CLUSTER2"].isna().sum()),
    "W4": int(W4["CLUSTER2"].isna().sum()),
    "W5": int(w5f["CLUSTER2"].isna().sum()),
}
sections.append(
    "## 10. CLUSTER2 missingness assertion\n\n"
    + "\n".join(f"- {k}: **{v}** rows missing CLUSTER2" for k, v in miss.items())
)


# ----------------------------------------------------------------------
# Write master markdown
# ----------------------------------------------------------------------
md = "# Task 13 — Verification pass\n\n" + "\n\n".join(sections) + "\n"
(OUT / "13_verification.md").write_text(md)
print("Wrote outputs/13_verification.md")

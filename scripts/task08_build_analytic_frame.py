"""Task 08 - Build the merged analytic frame for Wave I -> W4 (primary) and
Wave I -> W5 (deferred-spec support) cognitive regressions.

Output parquets:
  outputs/cache/analytic_w4.parquet  (W1 network + W1 inhome + W4 in-home + weights)
  outputs/cache/analytic_w5.parquet  (W1 network + W1 inhome + W5 cognitive + weights,
                                      MODE-restricted to in-person + phone)
  outputs/cache/analytic_w1_full.parquet (W1 in-home + W1 weights only - for full-N
                                      specs that do not require the network file)

Also writes a diagnostic N table to outputs/08_analytic_frame_n.md that reconciles
the 620-vs-394 W5 question:
  - 620 = W5 cognitive administrations (in-person + phone only)
  - 394 = W5 cognitive AND W1 network both observed
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from analysis_utils import (  # noqa: E402
    ROOT, CACHE,
    clean_var,
    load_w1_network, load_w1_inhome, load_w4_inhome, load_w5,
    load_w1_weight, load_w4_weight, load_w5_weight,
    derive_cesd_sum, derive_w5_bds, derive_w4_cog_composite,
    derive_w5_cog_composite, derive_school_belonging,
    derive_race_ethnicity, derive_parent_ed, derive_friendship_grid,
)

OUT_DIR = ROOT / "outputs"


def build_frames():
    print("Loading cached frames ...")
    w1h = load_w1_inhome()
    w1n = load_w1_network()
    w4h = load_w4_inhome()
    w5 = load_w5()

    w1w = load_w1_weight()
    w4w = load_w4_weight()
    w5w = load_w5_weight()

    # -- W1 derived covariates ------------------------------------------------
    print("Deriving W1 covariates ...")
    w1_cov = pd.DataFrame({
        "AID": w1h["AID"],
        "BIO_SEX": clean_var(w1h["BIO_SEX"], "BIO_SEX"),
        "AH_RAW": clean_var(w1h["AH_RAW"], "AH_RAW"),
        "AH_PVT": clean_var(w1h["AH_PVT"], "AH_PVT"),
        "H1GH1": clean_var(w1h["H1GH1"], "H1GH1"),
        "H1DA7": clean_var(w1h["H1DA7"], "H1DA7"),
        "H1FS13": clean_var(w1h["H1FS13"], "H1FS13"),
        "H1FS14": clean_var(w1h["H1FS14"], "H1FS14"),
        "H1ED19": clean_var(w1h["H1ED19"], "H1ED19"),
        "H1ED20": clean_var(w1h["H1ED20"], "H1ED20"),
        "H1ED21": clean_var(w1h["H1ED21"], "H1ED21"),
        "H1ED22": clean_var(w1h["H1ED22"], "H1ED22"),
        "H1ED23": clean_var(w1h["H1ED23"], "H1ED23"),
        "H1ED24": clean_var(w1h["H1ED24"], "H1ED24"),
    })
    w1_cov["CESD_SUM"] = derive_cesd_sum(w1h)
    w1_cov["RACE"] = derive_race_ethnicity(w1h)
    w1_cov["PARENT_ED"] = derive_parent_ed(w1h)
    w1_cov["SCHOOL_BELONG"] = derive_school_belonging(w1h)

    friend = derive_friendship_grid(w1h)
    friend["AID"] = w1h["AID"].values
    w1_cov = w1_cov.merge(friend, on="AID", how="left")

    # -- W1 network exposures -------------------------------------------------
    print("Cleaning W1 network variables ...")
    net_cols = ["IDGX2", "ODGX2", "BCENT10X", "REACH", "REACH3",
                "PRXPREST", "INFLDMN", "IGDMEAN",
                "ESDEN", "ERDEN", "ESRDEN", "RCHDEN",
                "HAVEBMF", "HAVEBFF", "BMFRECIP", "BFFRECIP"]
    w1_net = pd.DataFrame({"AID": w1n["AID"]})
    for c in net_cols:
        if c in w1n.columns:
            w1_net[c] = clean_var(w1n[c], c)

    # Isolation indicators
    w1_net["IDG_ZERO"] = (w1_net["IDGX2"] == 0).astype(float)
    w1_net.loc[w1_net["IDGX2"].isna(), "IDG_ZERO"] = np.nan
    w1_net["IDG_LEQ1"] = (w1_net["IDGX2"] <= 1).astype(float)
    w1_net.loc[w1_net["IDGX2"].isna(), "IDG_LEQ1"] = np.nan

    # Quintiles of in-degree (computed on non-missing)
    qt = pd.qcut(w1_net["IDGX2"].dropna(), 5, labels=False, duplicates="drop")
    w1_net["IDGX2_QUINTILE"] = np.nan
    w1_net.loc[qt.index, "IDGX2_QUINTILE"] = qt.values

    # -- W4 outcomes ----------------------------------------------------------
    print("Deriving W4 outcomes ...")
    w4_out = pd.DataFrame({
        "AID": w4h["AID"],
        "C4WD90_1": clean_var(w4h["C4WD90_1"], "C4WD90_1"),
        "C4WD60_1": clean_var(w4h["C4WD60_1"], "C4WD60_1"),
        "C4NUMSCR": clean_var(w4h["C4NUMSCR"], "C4NUMSCR"),
    })
    w4_out["W4_COG_COMP"] = derive_w4_cog_composite(w4h)

    # -- W5 outcomes (mode-restricted) ---------------------------------------
    print("Deriving W5 outcomes (mode-restricted to I/T) ...")
    w5_eligible = w5["MODE"].isin(["I", "T"])
    w5_sub = w5[w5_eligible].copy()
    w5_sub["BDS_SCORE"] = derive_w5_bds(w5_sub)
    w5_sub["W5_COG_COMP"] = derive_w5_cog_composite(w5_sub, w5_sub["BDS_SCORE"])
    w5_out = pd.DataFrame({
        "AID": w5_sub["AID"],
        "MODE": w5_sub["MODE"],
        "C5WD90_1": clean_var(w5_sub["C5WD90_1"], "C5WD90_1"),
        "C5WD60_1": clean_var(w5_sub["C5WD60_1"], "C5WD60_1"),
        "BDS_SCORE": w5_sub["BDS_SCORE"],
        "W5_COG_COMP": w5_sub["W5_COG_COMP"],
    })

    # -- Mode-selection audit dataset (for sensitivity: W5 full cohort) ------
    print("Building W5 mode-selection audit frame ...")
    w5_all_mode = pd.DataFrame({
        "AID": w5["AID"],
        "MODE": w5["MODE"],
        "IS_COG_MODE": w5_eligible.astype(int).values,
    })

    # -- Sort and deduplicate AIDs --------------------------------------------
    for frame in (w1_cov, w1_net, w1w, w4w, w5w, w4_out, w5_out, w5_all_mode):
        frame.sort_values("AID", inplace=True)
        assert frame["AID"].is_unique, f"Duplicate AIDs in frame: {frame.columns.tolist()}"

    # -- Build W4 analytic frame ---------------------------------------------
    print("Merging W4 analytic frame ...")
    w4_frame = (
        w1_cov.merge(w1_net, on="AID", how="left", validate="one_to_one")
        .merge(w1w, on="AID", how="left", validate="one_to_one")
        .merge(w4_out, on="AID", how="inner", validate="one_to_one")
        .merge(w4w, on="AID", how="left", validate="one_to_one",
               suffixes=("", "_w4"))
    )
    # Resolve duplicate CLUSTER2 after w4w merge
    if "CLUSTER2_w4" in w4_frame.columns:
        w4_frame["CLUSTER2"] = w4_frame["CLUSTER2"].fillna(w4_frame["CLUSTER2_w4"])
        w4_frame.drop(columns=["CLUSTER2_w4"], inplace=True)

    # -- Build W5 analytic frame (mode-restricted) ---------------------------
    print("Merging W5 analytic frame (I/T only) ...")
    w5_frame = (
        w1_cov.merge(w1_net, on="AID", how="left", validate="one_to_one")
        .merge(w1w, on="AID", how="left", validate="one_to_one")
        .merge(w5_out, on="AID", how="inner", validate="one_to_one")
        .merge(w5w, on="AID", how="left", validate="one_to_one",
               suffixes=("", "_w5"))
    )
    if "CLUSTER2_w5" in w5_frame.columns:
        w5_frame["CLUSTER2"] = w5_frame["CLUSTER2"].fillna(w5_frame["CLUSTER2_w5"])
        w5_frame.drop(columns=["CLUSTER2_w5"], inplace=True)

    # -- Build W1-full frame (for specs that do not require the network file)
    print("Merging W1-full (for full-N belonging / loneliness / friendship specs) ...")
    # Link to W4 outcomes since those are the primary outcome even for these exposures
    w1_full = (
        w1_cov.merge(w1w, on="AID", how="left", validate="one_to_one")
        .merge(w4_out, on="AID", how="inner", validate="one_to_one")
        .merge(w4w, on="AID", how="left", validate="one_to_one",
               suffixes=("", "_w4"))
    )
    if "CLUSTER2_w4" in w1_full.columns:
        w1_full["CLUSTER2"] = w1_full["CLUSTER2"].fillna(w1_full["CLUSTER2_w4"])
        w1_full.drop(columns=["CLUSTER2_w4"], inplace=True)

    CACHE.mkdir(parents=True, exist_ok=True)
    w4_frame.to_parquet(CACHE / "analytic_w4.parquet")
    w5_frame.to_parquet(CACHE / "analytic_w5.parquet")
    w1_full.to_parquet(CACHE / "analytic_w1_full.parquet")
    w5_all_mode.to_parquet(CACHE / "analytic_w5_mode_audit.parquet")

    return w4_frame, w5_frame, w1_full


def write_diagnostics(w4_frame, w5_frame, w1_full):
    """Cross-check N against /outputs/07_analytic_n.csv."""
    lines = ["# Task 08 - Analytic frame diagnostics", ""]
    expected = pd.read_csv(OUT_DIR / "07_analytic_n.csv")
    lines.append("## Pre-registered N benchmarks (from 07_analytic_n.csv)")
    lines.append("")
    lines.append(expected.to_markdown(index=False))
    lines.append("")

    def count(df, expr_cols):
        mask = pd.Series(True, index=df.index)
        for c in expr_cols:
            mask &= df[c].notna()
        return int(mask.sum())

    lines.append("## Reproduced N from merged frames")
    lines.append("")
    lines.append("| Configuration | N observed | N reproduced | Match? |")
    lines.append("|---|---|---|---|")

    checks = [
        ("W1 network ∩ W4 immediate", 3505,
         count(w4_frame, ["IDGX2", "C4WD90_1"])),
        ("W1 network ∩ W4 BDS", 3506,
         count(w4_frame, ["IDGX2", "C4NUMSCR"])),
        ("W1 network ∩ W5 immediate", 394,
         count(w5_frame, ["IDGX2", "C5WD90_1"])),
        ("W1 network ∩ W5 BDS (any trial)", 394,
         count(w5_frame, ["IDGX2", "BDS_SCORE"])),
        ("W1 AH_PVT ∩ W4 immediate",
         4883, count(w1_full, ["AH_PVT", "C4WD90_1"])),
        ("W4 immediate (all W1)", 5101,
         count(w1_full, ["C4WD90_1"])),
        ("W5 cog admin (I/T only)", 623,
         count(w5_frame, ["C5WD90_1"])),
    ]
    for label, expected_n, got_n in checks:
        match = "✅" if got_n == expected_n else f"⚠️ off by {got_n - expected_n}"
        lines.append(f"| {label} | {expected_n} | {got_n} | {match} |")
    lines.append("")

    lines.append("## N reconciliation: 620 vs 394")
    lines.append("")
    lines.append("- **623** W5 respondents have an immediate-recall score administered "
                 "(in-person + phone modes only).")
    lines.append("- **394** of those 623 also have a valid W1 network exposure (IDGX2); "
                 "this is the N for spec #1 when applied to W5.")
    lines.append("- **620** in the feasibility summary likely refers to delayed recall "
                 "(`C5WD60_1`, N=620); **623** is immediate recall.")
    lines.append("- **Both numbers are correct for their respective intersections.**")
    lines.append("")
    lines.append("## Derived variable ranges (W4 frame)")
    lines.append("")
    summary_cols = [
        "IDGX2", "ODGX2", "BCENT10X", "REACH",
        "C4WD90_1", "C4WD60_1", "C4NUMSCR", "W4_COG_COMP",
        "AH_RAW", "CESD_SUM", "SCHOOL_BELONG",
        "FRIEND_N_NOMINEES", "FRIEND_CONTACT_SUM",
        "PARENT_ED",
    ]
    summary_cols = [c for c in summary_cols if c in w4_frame.columns]
    desc = w4_frame[summary_cols].describe().T[["count", "mean", "std", "min", "max"]]
    lines.append(desc.to_markdown())
    lines.append("")

    lines.append("## Key N's in each frame")
    lines.append("")
    lines.append(f"- `analytic_w4.parquet`: {len(w4_frame)} rows "
                 f"(W1 inhome inner-joined to W4 in-home)")
    lines.append(f"- `analytic_w5.parquet`: {len(w5_frame)} rows "
                 f"(W1 inhome inner-joined to W5 cognitive, mode=I/T)")
    lines.append(f"- `analytic_w1_full.parquet`: {len(w1_full)} rows "
                 f"(W1 inhome inner-joined to W4 in-home, no network gate)")
    lines.append("")

    out_md = OUT_DIR / "08_analytic_frame_n.md"
    out_md.write_text("\n".join(lines))
    print(f"Wrote {out_md}")


def main() -> None:
    w4_frame, w5_frame, w1_full = build_frames()
    write_diagnostics(w4_frame, w5_frame, w1_full)


if __name__ == "__main__":
    main()

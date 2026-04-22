"""Task 10 - Baseline exploratory regressions (specs #1-#7, #9-#10).

Spec #8 (W5 sensitivity) is deferred pending user review of W4 findings.

Design: weighted OLS with GSWGT4_2, cluster-robust variance on CLUSTER2,
use_t=True, df = (n_psu - 1). Base adjustment set: BIO_SEX, race dummies,
PARENT_ED, AH_RAW (AHPVT), CESD_SUM, H1GH1. (H1DA7 and SCHOOL_BELONG kept
separate since they overlap with exposure families #6/#10.)

All specs are run TWICE: with and without AH_RAW (bad-control sensitivity).

Outputs:
  outputs/10_regressions.csv     - one row per (spec_id, term)
  outputs/10_regressions.md      - human-readable summary
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

from analysis_utils import (  # noqa: E402
    ROOT, CACHE, clean_var, weighted_ols,
)

OUT = ROOT / "outputs"

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
W1_FULL = pd.read_parquet(CACHE / "analytic_w1_full.parquet")

RACE_LEVELS = ["NH-White", "NH-Black", "Hispanic", "Other"]


def race_dummies(df: pd.DataFrame) -> pd.DataFrame:
    """Return k-1 race dummies (ref = NH-White)."""
    out = pd.DataFrame(index=df.index)
    for lvl in ["NH-Black", "Hispanic", "Other"]:
        out[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    out.loc[df["RACE"].isna(), :] = np.nan
    return out


def base_covariates(df: pd.DataFrame, include_ahpvt: bool = True) -> pd.DataFrame:
    """Return design matrix for baseline adjustment (WITHOUT intercept)."""
    parts = [
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male"),
        race_dummies(df),
        df["PARENT_ED"].rename("parent_ed"),
        df["CESD_SUM"].rename("cesd_sum"),
        df["H1GH1"].rename("srh"),
    ]
    if include_ahpvt:
        parts.append(df["AH_RAW"].rename("ahpvt"))
    X = pd.concat(parts, axis=1)
    return X


def build_design(exposures: Dict[str, pd.Series], df: pd.DataFrame,
                 include_ahpvt: bool = True) -> Tuple[pd.DataFrame, List[str]]:
    """Stack exposures and baseline covariates, plus intercept."""
    cov = base_covariates(df, include_ahpvt=include_ahpvt)
    exp_df = pd.DataFrame(exposures, index=df.index)
    X = pd.concat([exp_df, cov], axis=1)
    X.insert(0, "const", 1.0)
    return X, list(X.columns)


def fit_spec(spec_id: str, label: str, df: pd.DataFrame,
             y_col: str, exposures: Dict[str, pd.Series],
             weight_col: str = "GSWGT4_2",
             include_ahpvt: bool = True) -> List[dict]:
    X, names = build_design(exposures, df, include_ahpvt=include_ahpvt)
    y = df[y_col].values
    w = df[weight_col].values
    psu = df["CLUSTER2"].values
    res = weighted_ols(y, X.values, w, psu, column_names=names)
    rows: List[dict] = []
    if res is None:
        return rows
    for term in names:
        rows.append({
            "spec_id": spec_id,
            "spec_label": label,
            "outcome": y_col,
            "term": term,
            "beta": float(res["beta"][term]),
            "se": float(res["se"][term]),
            "t": float(res["t"][term]),
            "p": float(res["p"][term]),
            "ci_lo": float(res["ci_lo"][term]),
            "ci_hi": float(res["ci_hi"][term]),
            "n": res["n"],
            "n_psu": res["n_psu"],
            "r2": res["rsquared"],
            "ahpvt_adjusted": include_ahpvt,
        })
    return rows


# ---------------------------------------------------------------------------
# Specifications
# ---------------------------------------------------------------------------
def run_all() -> pd.DataFrame:
    rows: List[dict] = []

    # ---- Spec 1: anchor linear IDGX2 -> C4WD90_1 ------------------------
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        rows += fit_spec(f"S01{tag}",
                         f"IDGX2 -> C4WD90_1 (linear{'+AHPVT' if include_pvt else ''})",
                         W4, "C4WD90_1", {"idgx2": W4["IDGX2"]},
                         include_ahpvt=include_pvt)
        # Plus composite
        rows += fit_spec(f"S01C{tag}",
                         f"IDGX2 -> W4_COG_COMP (linear{'+AHPVT' if include_pvt else ''})",
                         W4, "W4_COG_COMP", {"idgx2": W4["IDGX2"]},
                         include_ahpvt=include_pvt)

    # ---- Spec 2: IDGX2 quintile dummies ----------------------------------
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        # Ref = Q1 (lowest in-degree)
        qs = W4["IDGX2_QUINTILE"]
        exposures = {f"idg_q{int(q+1)}": (qs == q).astype(float)
                     for q in range(1, 5)}
        rows += fit_spec(f"S02{tag}",
                         f"IDGX2 quintiles -> C4WD90_1{'+AHPVT' if include_pvt else ''}",
                         W4, "C4WD90_1", exposures,
                         include_ahpvt=include_pvt)
        rows += fit_spec(f"S02C{tag}",
                         f"IDGX2 quintiles -> W4_COG_COMP{'+AHPVT' if include_pvt else ''}",
                         W4, "W4_COG_COMP", exposures,
                         include_ahpvt=include_pvt)

    # ---- Spec 3: composite (already covered by S01C) -- add individual
    # components side-by-side for comparability
    for include_pvt in (True,):
        tag = "" if include_pvt else "_noAHPVT"
        for y in ["C4WD90_1", "C4WD60_1", "C4NUMSCR", "W4_COG_COMP"]:
            rows += fit_spec(f"S03_{y}{tag}",
                             f"IDGX2 -> {y} (AHPVT adj)",
                             W4, y, {"idgx2": W4["IDGX2"]},
                             include_ahpvt=include_pvt)

    # ---- Spec 4: alternative exposures (swap in) -------------------------
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        for exp_name, col in [
            ("ODGX2_placebo", "ODGX2"),
            ("BCENT10X", "BCENT10X"),
            ("REACH", "REACH"),
            ("PRXPREST", "PRXPREST"),
        ]:
            rows += fit_spec(f"S04_{exp_name}{tag}",
                             f"{exp_name} -> W4_COG_COMP",
                             W4, "W4_COG_COMP", {exp_name.lower(): W4[col]},
                             include_ahpvt=include_pvt)

    # ---- Spec 5: isolation indicators ------------------------------------
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        rows += fit_spec(f"S05_ZERO{tag}",
                         "I(IDGX2==0) -> W4_COG_COMP",
                         W4, "W4_COG_COMP", {"idg_zero": W4["IDG_ZERO"]},
                         include_ahpvt=include_pvt)
        rows += fit_spec(f"S05_LEQ1{tag}",
                         "I(IDGX2<=1) -> W4_COG_COMP",
                         W4, "W4_COG_COMP", {"idg_leq1": W4["IDG_LEQ1"]},
                         include_ahpvt=include_pvt)

    # ---- Spec 6: school belonging (full W1 sample, not network-gated) ----
    # NOTE: belonging scale is both the exposure and cannot enter covariates
    # here (over-adjustment).
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        rows += fit_spec(f"S06{tag}",
                         "SCHOOL_BELONG -> W4_COG_COMP (full W1)",
                         W1_FULL, "W4_COG_COMP",
                         {"school_belong": W1_FULL["SCHOOL_BELONG"]},
                         include_ahpvt=include_pvt)

    # ---- Spec 7: loneliness / unfriendly (full W1 sample) ----------------
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        rows += fit_spec(f"S07{tag}",
                         "H1FS13 + H1FS14 -> W4_COG_COMP",
                         W1_FULL, "W4_COG_COMP",
                         {"lonely": W1_FULL["H1FS13"],
                          "unfriendly": W1_FULL["H1FS14"]},
                         include_ahpvt=include_pvt)

    # ---- Spec 9: heterogeneity (interactions) ----------------------------
    # IDGX2 x sex
    df9 = W4.copy()
    df9["idgx2_c"] = df9["IDGX2"] - df9["IDGX2"].mean(skipna=True)
    df9["male"] = (df9["BIO_SEX"] == 1).astype(float)
    df9["idgx2_x_male"] = df9["idgx2_c"] * df9["male"]
    rows += fit_spec("S09_sex",
                     "IDGX2 × sex on W4_COG_COMP",
                     df9, "W4_COG_COMP",
                     {"idgx2_c": df9["idgx2_c"],
                      "idgx2_x_male": df9["idgx2_x_male"]},
                     include_ahpvt=True)
    # IDGX2 x parent_ed (standardized)
    df9["parent_ed_c"] = df9["PARENT_ED"] - df9["PARENT_ED"].mean(skipna=True)
    df9["idgx2_x_parented"] = df9["idgx2_c"] * df9["parent_ed_c"]
    rows += fit_spec("S09_parented",
                     "IDGX2 × parent_ed on W4_COG_COMP",
                     df9, "W4_COG_COMP",
                     {"idgx2_c": df9["idgx2_c"],
                      "idgx2_x_parented": df9["idgx2_x_parented"]},
                     include_ahpvt=True)

    # ---- Spec 10: friendship-grid derived exposures (full W1 sample) -----
    for include_pvt in (True, False):
        tag = "" if include_pvt else "_noAHPVT"
        rows += fit_spec(f"S10_nominees{tag}",
                         "FRIEND_N_NOMINEES -> W4_COG_COMP (full W1)",
                         W1_FULL, "W4_COG_COMP",
                         {"friend_n": W1_FULL["FRIEND_N_NOMINEES"]},
                         include_ahpvt=include_pvt)
        rows += fit_spec(f"S10_contact{tag}",
                         "FRIEND_CONTACT_SUM -> W4_COG_COMP",
                         W1_FULL, "W4_COG_COMP",
                         {"friend_contact": W1_FULL["FRIEND_CONTACT_SUM"]},
                         include_ahpvt=include_pvt)
        rows += fit_spec(f"S10_disclose{tag}",
                         "FRIEND_DISCLOSURE_ANY -> W4_COG_COMP",
                         W1_FULL, "W4_COG_COMP",
                         {"friend_disclose": W1_FULL["FRIEND_DISCLOSURE_ANY"]},
                         include_ahpvt=include_pvt)

    return pd.DataFrame(rows)


def write_markdown(df: pd.DataFrame, path: Path) -> None:
    lines = ["# Task 10 - Baseline regressions (exploratory)", ""]
    lines.append("All specifications: WLS on GSWGT4_2, cluster-robust on CLUSTER2, "
                 "use_t=True, df = (n_psu − 1). Exposures reported per spec; covariates "
                 "are sex, race dummies (ref NH-White), parent education, CES-D sum, "
                 "self-rated health, and (unless noted) AHPVT raw.")
    lines.append("")
    lines.append("## Exposure coefficients (primary terms only)")
    lines.append("")
    lines.append("| Spec | Label | Term | β | SE | 95% CI | t | p | N | PSUs | AHPVT-adj |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
    # Filter to the exposure terms (exclude const/covariates)
    exposure_terms = (
        df["term"].str.startswith(("idgx2", "odgx", "bcent", "reach", "prxp",
                                    "idg_", "friend_", "school_", "lonely",
                                    "unfriendly", "idg_q"))
        .fillna(False)
    )
    exposure_rows = df[exposure_terms].copy()
    for _, r in exposure_rows.iterrows():
        ci = f"[{r['ci_lo']:.3f}, {r['ci_hi']:.3f}]"
        lines.append(
            f"| {r['spec_id']} | {r['spec_label']} | {r['term']} | "
            f"{r['beta']:.4f} | {r['se']:.4f} | {ci} | {r['t']:.2f} | "
            f"{r['p']:.3g} | {int(r['n'])} | {int(r['n_psu'])} | "
            f"{'yes' if r['ahpvt_adjusted'] else 'no'} |"
        )
    lines.append("")

    lines.append("## Full coefficient table")
    lines.append("")
    lines.append("See `10_regressions.csv` for all terms (baseline covariates included).")
    lines.append("")
    path.write_text("\n".join(lines))


def main() -> None:
    print("Running baseline regressions ...")
    results = run_all()
    results.to_csv(OUT / "10_regressions.csv", index=False)
    write_markdown(results, OUT / "10_regressions.md")
    print(f"Wrote {OUT}/10_regressions.csv ({len(results)} rows)")
    print(f"Wrote {OUT}/10_regressions.md")


if __name__ == "__main__":
    main()

"""negative-control-battery — exposure-side AND outcome-side null-control sweeps.

Runs two null directions side by side under the cognitive-screening WLS
spec (L0+L1+AHPVT, GSWGT4_2 weights, cluster-SE on CLUSTER2):

  Direction 1 — NC exposure → real outcome.
    Exposures: blood type, age at menarche, hand-dominance, residential
    stability pre-W1. Outcomes: W4_COG_COMP + cardiometabolic outcomes.
    PRE-FLIGHT REQUIRED per TODO §A2 — exposure availability is uncertain
    in the public-use file. This script INCLUDES guards that skip a
    candidate exposure with a warning rather than crash if its column
    is missing from the cached parquets.

  Direction 2 — Real exposure (IDGX2 + 23 others) → NC outcome.
    Outcomes hardcoded from the 2026-04-27 pre-flight inventory:
    H5EL6D, H5EL6F, H5DA9, H5EL6A, H5EL6B. All N > 4,000.
    H5ID1 is explicitly excluded (too socially confounded).

This file is a SKELETON.

Outputs:
  tables/primary/nc_battery_matrix.csv
  tables/primary/nc_battery.md
  tables/sensitivity/nc_preflight_availability.csv
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from analysis import CACHE  # noqa: E402
from analysis.cleaning import clean_var  # noqa: E402
from analysis.wls import weighted_ols  # noqa: E402
from analysis.data_loading import load_outcome  # noqa: E402

TABLES_PRIMARY = HERE / "tables" / "primary"
TABLES_SENS = HERE / "tables" / "sensitivity"
TABLES_PRIMARY.mkdir(parents=True, exist_ok=True)
TABLES_SENS.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Direction 2 — outcome-side NCs locked from 2026-04-27 pre-flight.
# (label, source_wave, N_preflight, kind)
# ---------------------------------------------------------------------------
NC_OUTCOMES: Dict[str, Tuple[str, str, int, str]] = {
    "H5EL6D": ("TOLD OF SIGHT PROBLEM BEFORE AGE 16—W5",         "W5", 4168, "binary"),
    "H5EL6F": ("TOLD OF HEARING PROBLEM/DEAF BEFORE AGE 16—W5",  "W5", 4166, "binary"),
    "H5DA9":  ("HEARING QUALITY WITHOUT AIDS—W5",                "W5", 4082, "ordinal"),
    "H5EL6A": ("TOLD OF ASTHMA BEFORE AGE 16—W5",                "W5", 4171, "binary"),
    "H5EL6B": ("TOLD OF ALLERGY BEFORE AGE 16—W5",               "W5", 4168, "binary"),
}

# Explicitly excluded — socially confounded, fails biology-only sniff test.
NC_OUTCOMES_EXCLUDED: Dict[str, str] = {
    "H5ID1": "Self-rated general health is too socially confounded.",
}


# ---------------------------------------------------------------------------
# Direction 1 — outcome-side "real" outcomes the NC exposures must NOT predict.
# Mirror of cognitive-screening + cardiometabolic from multi-outcome-screening.
# ---------------------------------------------------------------------------
REAL_OUTCOMES_DIR1: Dict[str, Tuple[str, str, str]] = {
    "W4_COG_COMP": ("W4 cognition composite",     "cognitive",       "z-score"),
    "H4BMI":       ("S27 BMI—W4",                 "cardiometabolic", "continuous"),
    "H4WAIST":     ("S27 MEASURED WAIST (CM)—W4", "cardiometabolic", "continuous"),
    "H4SBP":       ("S27 SYSTOLIC BP—W4",          "cardiometabolic", "continuous"),
    "H4DBP":       ("S27 DIASTOLIC BP—W4",         "cardiometabolic", "continuous"),
}


# ---------------------------------------------------------------------------
# Direction 1 — candidate NC EXPOSURES. Pre-flight required per TODO §A2.
# Each entry: (column_name, source_parquet, codebook_label).
# The script tolerates missing columns: skip with warning + record in
# nc_preflight_availability.csv.
# ---------------------------------------------------------------------------
NC_EXPOSURE_CANDIDATES: List[Tuple[str, str, str]] = [
    # Genetic / biological invariants — should not predict adult outcomes
    ("BLOODTYPE",     "w4inhome.parquet",   "Blood type (genetic)"),
    ("H1GH53",        "w1inhome.parquet",   "Age at menarche (girls only) — W1 codebook check"),
    ("H1GH50",        "w1inhome.parquet",   "Hand-dominance — W1 codebook check"),
    # Pre-baseline mobility — should not directly cause adult outcomes once SES is controlled
    ("H1MO_RESID",    "w1inhome.parquet",   "Residential stability pre-W1 (constructed; verify column name)"),
]

# Real exposures for Direction 2 — same 24 as cognitive-screening, but
# headline focus is IDGX2 (popularity).
REAL_EXPOSURES_DIR2: List[str] = [
    "IDGX2", "ODGX2", "BCENT10X", "REACH", "REACH3",
    "INFLDMN", "PRXPREST", "IGDMEAN",
    "IDG_ZERO", "IDG_LEQ1", "HAVEBMF", "HAVEBFF",
    "ESDEN", "ERDEN", "ESRDEN", "RCHDEN",
    "FRIEND_N_NOMINEES", "FRIEND_CONTACT_SUM", "FRIEND_DISCLOSURE_ANY",
    "SCHOOL_BELONG", "H1FS13", "H1FS14", "H1DA7", "H1PR4",
]


# ---------------------------------------------------------------------------
# Adjustment-set builders — mirror cognitive-screening exactly.
# ---------------------------------------------------------------------------
RACE_LEVELS = ["NH-Black", "Hispanic", "Other"]


def _race_dummies(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    for lvl in RACE_LEVELS:
        out[f"race_{lvl}"] = (df["RACE"] == lvl).astype(float)
    out.loc[df["RACE"].isna(), :] = np.nan
    return out


def _adj_full(df: pd.DataFrame) -> pd.DataFrame:
    """L0 + L1 + AHPVT — mirror cognitive-screening primary spec."""
    return pd.concat([
        pd.Series((df["BIO_SEX"] == 1).astype(float), name="male", index=df.index),
        _race_dummies(df),
        df["PARENT_ED"].rename("parent_ed"),
        df["CESD_SUM"].rename("cesd_sum"),
        df["H1GH1"].rename("srh"),
        df["AH_RAW"].rename("ahpvt"),
    ], axis=1)


# ---------------------------------------------------------------------------
# Frame loading + pre-flight availability check.
# ---------------------------------------------------------------------------
def _load_frame_and_check_availability() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load W4 analytic frame, attach all NC outcomes + GSW5; check NC exposure availability.

    Returns (W4 frame, availability dataframe).

    Question for next pass: the pre-W1 residential-stability NC is a
    *derived* variable — the column name `H1MO_RESID` here is a placeholder.
    The next-pass derivation should follow the convention used in
    `scripts/analysis/derivation.py:derive_*` functions and the resulting
    column should be added to `analytic_w4.parquet` upstream rather than
    constructed here.
    """
    W4 = pd.read_parquet(CACHE / "analytic_w4.parquet")
    # Attach GSW5 if available (some NC fits target W5 outcomes via real exposures).
    try:
        w5 = pd.read_parquet(CACHE / "pwave5.parquet", columns=["AID", "GSW5"])
        W4 = W4.merge(w5, on="AID", how="left")
    except Exception:  # noqa: BLE001
        print("WARN: GSW5 not loaded; W5 fits will fall back to GSWGT4_2.")
        W4["GSW5"] = np.nan

    # Attach NC outcomes via load_outcome.
    for code in NC_OUTCOMES:
        W4[code] = load_outcome(W4["AID"], code)

    # Pre-flight availability check for each NC exposure candidate.
    avail_rows = []
    for col, parquet, label in NC_EXPOSURE_CANDIDATES:
        path = CACHE / parquet
        if not path.exists():
            avail_rows.append({
                "candidate": col, "label": label, "source_parquet": parquet,
                "available": False, "reason": "parquet missing", "n_nonnull": 0,
            })
            continue
        try:
            src = pd.read_parquet(path, columns=["AID", col])
        except (KeyError, ValueError) as e:
            avail_rows.append({
                "candidate": col, "label": label, "source_parquet": parquet,
                "available": False, "reason": f"column missing: {e}", "n_nonnull": 0,
            })
            continue
        # Attach to W4 with cleaning.
        src[col] = clean_var(src[col], col)
        W4 = W4.merge(src, on="AID", how="left", suffixes=("", "_dup"))
        n_nn = int(W4[col].notna().sum())
        avail_rows.append({
            "candidate": col, "label": label, "source_parquet": parquet,
            "available": n_nn > 0, "reason": "ok" if n_nn > 0 else "all-NaN after clean",
            "n_nonnull": n_nn,
        })
    avail = pd.DataFrame(avail_rows)
    return W4, avail


# ---------------------------------------------------------------------------
# Fit primitive
# ---------------------------------------------------------------------------
def _fit(df: pd.DataFrame, exposure_col: str, y_col: str, w_col: str) -> Optional[dict]:
    if exposure_col not in df.columns:
        return None
    exp = clean_var(df[exposure_col], exposure_col)
    adj = _adj_full(df)
    X = pd.concat([exp.rename("exposure"), adj], axis=1)
    X.insert(0, "const", 1.0)
    y = df[y_col].values
    w = df[w_col].values
    psu = df["CLUSTER2"].values
    return weighted_ols(y, X.values, w, psu, column_names=list(X.columns))


# ---------------------------------------------------------------------------
# Direction 1 — NC exposures × real outcomes.
# ---------------------------------------------------------------------------
def run_direction1(df: pd.DataFrame, avail: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, av in avail.iterrows():
        if not av["available"]:
            continue
        exp_col = av["candidate"]
        for outcome_code, (label, group, kind) in REAL_OUTCOMES_DIR1.items():
            res = _fit(df, exp_col, outcome_code, w_col="GSWGT4_2")
            if res is None:
                rows.append({
                    "direction": 1, "exposure": exp_col, "exposure_kind": "NC",
                    "outcome": outcome_code, "outcome_label": label,
                    "outcome_kind": "real", "outcome_group": group,
                    "n": 0, "beta": np.nan, "se": np.nan, "p": np.nan,
                    "null_test_pass": False,
                })
                continue
            p = float(res["p"]["exposure"])
            rows.append({
                "direction": 1,
                "exposure": exp_col,
                "exposure_kind": "NC",
                "outcome": outcome_code,
                "outcome_label": label,
                "outcome_kind": "real",
                "outcome_group": group,
                "n": int(res["n"]),
                "beta": float(res["beta"]["exposure"]),
                "se": float(res["se"]["exposure"]),
                "p": p,
                "null_test_pass": p >= 0.05,  # we WANT non-significance
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Direction 2 — real exposures × NC outcomes.
# ---------------------------------------------------------------------------
def run_direction2(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for exp_col in REAL_EXPOSURES_DIR2:
        if exp_col not in df.columns:
            print(f"WARN: real exposure {exp_col} missing from frame; skipping.")
            continue
        for outcome_code, (label, wave, n_pre, kind) in NC_OUTCOMES.items():
            res = _fit(df, exp_col, outcome_code, w_col="GSWGT4_2")
            if res is None:
                rows.append({
                    "direction": 2, "exposure": exp_col, "exposure_kind": "real",
                    "outcome": outcome_code, "outcome_label": label,
                    "outcome_kind": "NC", "outcome_group": "biology",
                    "n": 0, "beta": np.nan, "se": np.nan, "p": np.nan,
                    "null_test_pass": False,
                })
                continue
            p = float(res["p"]["exposure"])
            rows.append({
                "direction": 2,
                "exposure": exp_col,
                "exposure_kind": "real",
                "outcome": outcome_code,
                "outcome_label": label,
                "outcome_kind": "NC",
                "outcome_group": "biology",
                "n": int(res["n"]),
                "beta": float(res["beta"]["exposure"]),
                "se": float(res["se"]["exposure"]),
                "p": p,
                "null_test_pass": p >= 0.05,  # we WANT non-significance
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------
def write_markdown(matrix: pd.DataFrame, avail: pd.DataFrame) -> None:
    lines = ["# negative-control-battery — both directions\n"]
    lines.append(
        "WLS L0+L1+AHPVT, GSWGT4_2, cluster-SE on CLUSTER2. Direction 1: "
        "NC exposure × real outcome (β should be ≈ 0). Direction 2: real "
        "exposure × NC outcome (β should be ≈ 0). A pass = p ≥ 0.05; "
        "a FAIL is evidence of unmeasured confounding.\n"
    )
    # Pre-flight availability summary.
    lines.append("## Pre-flight availability of NC exposures (Direction 1)\n")
    lines.append(avail.to_markdown(index=False))
    lines.append("")
    # Excluded outcomes.
    lines.append("## Outcomes explicitly excluded\n")
    for code, reason in NC_OUTCOMES_EXCLUDED.items():
        lines.append(f"- **{code}**: {reason}")
    lines.append("")
    # Per-direction summary.
    for d in (1, 2):
        sub = matrix[matrix.direction == d]
        if sub.empty:
            continue
        lines.append(f"\n## Direction {d}\n")
        lines.append(
            f"N tests = {len(sub)};  pass (p ≥ 0.05) = {int(sub.null_test_pass.sum())};  "
            f"fail = {int((~sub.null_test_pass).sum())}.\n"
        )
        show = sub[["exposure", "outcome", "n", "beta", "se", "p", "null_test_pass"]].copy()
        for c in ["beta", "se"]:
            show[c] = show[c].map(lambda v: f"{v:.4g}" if pd.notna(v) else "NA")
        show["p"] = show["p"].map(lambda v: f"{v:.3g}" if pd.notna(v) else "NA")
        lines.append(show.to_markdown(index=False))
        lines.append("")
    (TABLES_PRIMARY / "nc_battery.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    print("Running negative-control-battery (both directions) ...")
    df, avail = _load_frame_and_check_availability()
    avail.to_csv(TABLES_SENS / "nc_preflight_availability.csv", index=False)
    print(f"Wrote {TABLES_SENS / 'nc_preflight_availability.csv'}")

    d1 = run_direction1(df, avail)
    d2 = run_direction2(df)
    matrix = pd.concat([d1, d2], ignore_index=True)
    matrix.to_csv(TABLES_PRIMARY / "nc_battery_matrix.csv", index=False)
    print(f"Wrote {TABLES_PRIMARY / 'nc_battery_matrix.csv'} ({len(matrix)} rows)")

    write_markdown(matrix, avail)
    print(f"Wrote {TABLES_PRIMARY / 'nc_battery.md'}")


if __name__ == "__main__":
    main()

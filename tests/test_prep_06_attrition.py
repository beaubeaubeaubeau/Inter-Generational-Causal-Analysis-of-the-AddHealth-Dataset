"""Tests for ``scripts/prep/06_attrition.py`` helpers.

Covers the pure-function helpers:
  - ``_collapse_race`` race-categorisation
  - ``_parent_ed_tertile`` PA12 -> Low/Mid/High/Missing tertile
  - ``compute_joint_counts`` overlap counting on a synthetic presence frame
  - ``stratified_breakdown`` group-level rate calculation
  - ``_fmt_pct`` and ``_df_to_md`` formatting helpers
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PREP06 = REPO_ROOT / "scripts" / "prep" / "06_attrition.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("prep06", PREP06)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# _collapse_race
# ---------------------------------------------------------------------------

def test_collapse_race_hispanic_short_circuits():
    mod = _load_module()
    row = pd.Series({"H1GI4": 1, "H1GI6A": 1, "H1GI6B": 1,
                     "H1GI6C": 0, "H1GI6D": 0, "H1GI6E": 0})
    assert mod._collapse_race(row) == "Hispanic"


def test_collapse_race_white_only_nh():
    mod = _load_module()
    row = pd.Series({"H1GI4": 0, "H1GI6A": 1, "H1GI6B": 0,
                     "H1GI6C": 0, "H1GI6D": 0, "H1GI6E": 0})
    assert mod._collapse_race(row) == "White-NH"


def test_collapse_race_black_only_nh():
    mod = _load_module()
    row = pd.Series({"H1GI4": 0, "H1GI6A": 0, "H1GI6B": 1,
                     "H1GI6C": 0, "H1GI6D": 0, "H1GI6E": 0})
    assert mod._collapse_race(row) == "Black-NH"


def test_collapse_race_multiracial_to_other():
    mod = _load_module()
    row = pd.Series({"H1GI4": 0, "H1GI6A": 1, "H1GI6B": 1,
                     "H1GI6C": 0, "H1GI6D": 0, "H1GI6E": 0})
    assert mod._collapse_race(row) == "Other-NH"


def test_collapse_race_no_yes_responses_unknown():
    mod = _load_module()
    row = pd.Series({"H1GI4": 0, "H1GI6A": 0, "H1GI6B": 0,
                     "H1GI6C": 0, "H1GI6D": 0, "H1GI6E": 0})
    assert mod._collapse_race(row) == "Unknown"


# ---------------------------------------------------------------------------
# _parent_ed_tertile
# ---------------------------------------------------------------------------

def test_parent_ed_tertile_marks_invalid_as_missing():
    """PA12 = 10 (never went) and 96 (refused) -> Missing."""
    mod = _load_module()
    s = pd.Series([1, 5, 9, 10, 96, np.nan], dtype=float)
    out = mod._parent_ed_tertile(s)
    # Indices 3, 4, 5 are out of [1, 9] -> Missing
    assert out.iloc[3] == "Missing"
    assert out.iloc[4] == "Missing"
    assert out.iloc[5] == "Missing"


def test_parent_ed_tertile_distributes_into_three_buckets():
    """A 30-row uniform sample on [1, 9] should produce ~10 in each tertile."""
    mod = _load_module()
    s = pd.Series(np.tile([1, 2, 3, 4, 5, 6, 7, 8, 9], 4), dtype=float)
    out = mod._parent_ed_tertile(s)
    counts = pd.Series(out).value_counts()
    # All three buckets should be present
    assert {"Low", "Mid", "High"}.issubset(set(counts.index))


# ---------------------------------------------------------------------------
# compute_joint_counts
# ---------------------------------------------------------------------------

def test_compute_joint_counts_basic():
    """Synthetic presence frame with 10 W1 AIDs, varying participation:
      - All 10 in W1 in-home
      - 5 in W2
      - 4 in W4
      - 3 in W4 ∩ W5
    """
    mod = _load_module()
    pres = pd.DataFrame({
        "AID": [f"A{i:02d}" for i in range(10)],
        "w1_inhome":    [1] * 10,
        "w1_network":   [1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        "w2_inhome":    [1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
        "w3_inhome":    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        "w4_inhome":    [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        "w4_biomarker": [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        "w5_inhome":    [1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
        "w5_biomarker": [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
        "w5_meds":      [0] * 10,
        "w6_inhome":    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        "w6_biomarker": [0] * 10,
        "w6_meds":      [0] * 10,
    })
    joints = mod.compute_joint_counts(pres)
    assert joints["W1"] == 10
    assert joints["W1 & W2"] == 5
    assert joints["W1 & W3"] == 3
    assert joints["W1 & W4"] == 4
    assert joints["W1 & W5"] == 3
    assert joints["W1 & W6"] == 1
    assert joints["W1 & W4 & W5"] == 3   # AIDs 0, 1, 2 (all 3 of them)
    assert joints["W1 & W4 bio & W5 bio"] == 2


# ---------------------------------------------------------------------------
# stratified_breakdown
# ---------------------------------------------------------------------------

def test_stratified_breakdown_returns_per_cell_rates():
    """For a 6-row frame (2 sex × 1 race × 1 tertile, 3 each), counts and
    pct_appear should be correct per stratum."""
    mod = _load_module()
    pres = pd.DataFrame({
        "sex":   ["Male"] * 3 + ["Female"] * 3,
        "race":  ["White-NH"] * 6,
        "parent_ed_tertile": ["Mid"] * 6,
        "w5_inhome": [1, 1, 0, 0, 1, 0],
    })
    out = mod.stratified_breakdown(pres, "w5_inhome")
    male_row = out[out["sex"] == "Male"].iloc[0]
    female_row = out[out["sex"] == "Female"].iloc[0]
    assert male_row["n_w1"] == 3
    assert male_row["n_appear"] == 2
    assert male_row["pct_appear"] == 66.7
    assert female_row["n_w1"] == 3
    assert female_row["n_appear"] == 1
    assert female_row["pct_appear"] == 33.3


# ---------------------------------------------------------------------------
# _fmt_pct
# ---------------------------------------------------------------------------

def test_fmt_pct_basic():
    mod = _load_module()
    assert mod._fmt_pct(50, 100) == "50.0%"
    assert mod._fmt_pct(33, 99) == "33.3%"


def test_fmt_pct_zero_denom():
    mod = _load_module()
    assert mod._fmt_pct(0, 0) == "-"
    assert mod._fmt_pct(5, 0) == "-"


# ---------------------------------------------------------------------------
# _df_to_md
# ---------------------------------------------------------------------------

def test_df_to_md_renders_header_and_rows():
    mod = _load_module()
    df = pd.DataFrame({"a": [1, 2], "b": [3.0, 4.5]})
    md = mod._df_to_md(df)
    lines = md.split("\n")
    assert lines[0] == "| a | b |"
    assert lines[1] == "|---|---|"
    assert "| 1 | 3 |" in lines        # 3.0 renders as 3
    assert "| 2 | 4.5 |" in lines


def test_df_to_md_handles_nan_renders_as_empty():
    """NaN floats render as the empty string, not the literal 'nan'.

    The bug was that ``isinstance(v, float)`` was checked BEFORE
    ``pd.isna(v)``, so NaN floats fell into the float-formatter branch and
    rendered as the string 'nan'. Fixed 2026-04-26 by reordering the
    conditional to check ``pd.isna(v)`` first.
    """
    mod = _load_module()
    df = pd.DataFrame({"a": [1, np.nan]})
    md = mod._df_to_md(df)
    # Header + separator + two data rows; the NaN row should render as "| |".
    assert "| 1 |" in md
    assert "|  |" in md  # the empty NaN cell
    assert "nan" not in md.lower().replace("\n", " ").replace("|", "")

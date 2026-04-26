"""Tests for ``scripts/prep/04_missingness.py`` helpers.

Covers:
  - ``infer_scheme`` reserve-code heuristic by digit-width
  - ``cesd_sum`` derivation parity vs. canonical ``derive_cesd_sum``
  - ``wave5_digit_score`` BDS derivation
  - ``summarize`` row-shape and reserve-code accounting
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PREP04 = REPO_ROOT / "scripts" / "prep" / "04_missingness.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("prep04", PREP04)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# infer_scheme: heuristic
# ---------------------------------------------------------------------------

def test_infer_scheme_4digit_when_max_above_9990():
    mod = _load_module()
    s = pd.Series([100.0, 9999.0, 5.0, 9996.0])
    assert mod.infer_scheme(s) == "4digit"
    assert mod.infer_scheme(s, wave5=True) == "4digit_w5"


def test_infer_scheme_3digit_when_max_in_990_to_9989():
    mod = _load_module()
    s = pd.Series([100.0, 999.0, 5.0, 996.0])
    assert mod.infer_scheme(s) == "3digit"
    assert mod.infer_scheme(s, wave5=True) == "3digit_w5"


def test_infer_scheme_2digit_when_max_in_90_to_989():
    mod = _load_module()
    s = pd.Series([1.0, 99.0, 5.0, 96.0])
    assert mod.infer_scheme(s) == "2digit"
    assert mod.infer_scheme(s, wave5=True) == "2digit_w5"


def test_infer_scheme_1digit_for_low_likert_with_reserves():
    """0-3 Likert with substantive values dominating (>=80% in [0,5]) plus
    6/7/8/9 reserves -> 1digit. With only 50% in [0,5] the heuristic falls
    through to 'none', so make the substantive-share large enough to trip
    the threshold.
    """
    mod = _load_module()
    # 24 in [0, 3] + 4 reserves -> 24/28 = 85.7% in [0,5]
    vals = [0, 1, 2, 3] * 6 + [6, 7, 8, 9]
    s = pd.Series(vals, dtype=float)
    assert mod.infer_scheme(s) == "1digit"


def test_infer_scheme_none_for_continuous_data():
    """Continuous data with non-integer values -> 'none'."""
    mod = _load_module()
    s = pd.Series([0.1, 0.5, 0.7, 1.2, 3.4, 7.8])
    assert mod.infer_scheme(s) == "none"


def test_infer_scheme_none_when_no_reserves_present():
    """Even small-scale [0, 5] but no 6/7/8/9 in data -> no scheme applied."""
    mod = _load_module()
    s = pd.Series([0, 1, 2, 3, 4, 5], dtype=float)
    assert mod.infer_scheme(s) == "none"


def test_infer_scheme_none_for_binary_0_1():
    """Binary 0/1 should never trigger a reserve scheme."""
    mod = _load_module()
    s = pd.Series([0, 1, 0, 1, 1, 0], dtype=float)
    assert mod.infer_scheme(s) == "none"


def test_infer_scheme_none_for_empty_series():
    mod = _load_module()
    assert mod.infer_scheme(pd.Series([], dtype=float)) == "none"


def test_infer_scheme_override_wins():
    """Caller-supplied override should bypass the heuristic."""
    mod = _load_module()
    s = pd.Series([1.0, 99.0, 5.0])
    assert mod.infer_scheme(s, override="none") == "none"


# ---------------------------------------------------------------------------
# cesd_sum (inlined in prep04) vs canonical analysis.derivation.derive_cesd_sum
# ---------------------------------------------------------------------------

def test_cesd_sum_inlined_matches_canonical(synthetic_w1_df):
    """The inlined CES-D sum in prep04 should match analysis.derive_cesd_sum
    bit-for-bit when given the same input frame.
    """
    mod = _load_module()
    from analysis.derivation import derive_cesd_sum
    inlined = mod.cesd_sum(synthetic_w1_df)
    canonical = derive_cesd_sum(synthetic_w1_df)
    pd.testing.assert_series_equal(inlined, canonical, check_names=False)


# ---------------------------------------------------------------------------
# wave5_digit_score (inlined BDS)
# ---------------------------------------------------------------------------

def test_wave5_digit_score_clean_pass():
    """Pass at L=2 (H5MH3A=1), fail elsewhere -> score = 2."""
    mod = _load_module()
    rec = {f"H5MH{L+1}{s}": 0.0 for L in range(2, 9) for s in "AB"}
    rec["H5MH3A"] = 1.0
    df = pd.DataFrame([rec])
    out = mod.wave5_digit_score(df)
    assert out.iloc[0] == 2.0


def test_wave5_digit_score_all_reserve_returns_nan():
    """If every trial is a reserve code (995), no substantive value, -> NaN."""
    mod = _load_module()
    rec = {f"H5MH{L+1}{s}": 995.0 for L in range(2, 9) for s in "AB"}
    df = pd.DataFrame([rec])
    out = mod.wave5_digit_score(df)
    assert pd.isna(out.iloc[0])


def test_wave5_digit_score_all_zero_returns_zero():
    """Substantive 0 everywhere -> score = 0 (not NaN)."""
    mod = _load_module()
    rec = {f"H5MH{L+1}{s}": 0.0 for L in range(2, 9) for s in "AB"}
    df = pd.DataFrame([rec])
    out = mod.wave5_digit_score(df)
    assert out.iloc[0] == 0.0


# ---------------------------------------------------------------------------
# summarize: row schema and counts
# ---------------------------------------------------------------------------

def test_summarize_returns_canonical_keys():
    """Every summary row exposes the canonical column set."""
    mod = _load_module()
    s = pd.Series([1, 2, 3, 4, 5, np.nan], dtype=float)
    row = mod.summarize("X", s)
    expected_keys = {
        "variable", "n_total", "n_nonmissing", "n_valid", "scheme",
        "pct_missing_true", "pct_refused", "pct_skip", "pct_dk", "pct_na",
        "pct_not_asked",
        "min_valid", "max_valid", "mean_valid", "median_valid",
    }
    assert expected_keys.issubset(row.keys())


def test_summarize_counts_reserves_correctly():
    """A 1-digit Likert with sufficient substantive values to trigger the
    1-digit scheme: each reserve code (6/7/8/9) should populate its own
    pct_* bucket.
    """
    mod = _load_module()
    # 24 substantive in [0,3] + 1 each of 6/7/8/9 -> 28 total, 24 valid
    vals = [0, 1, 2, 3] * 6 + [6, 7, 8, 9]
    s = pd.Series(vals, dtype=float)
    row = mod.summarize("Y", s)
    assert row["scheme"] == "1digit"
    assert row["n_total"] == 28
    assert row["n_valid"] == 24
    # Each reserve code count is 1/28 ~ 3.57%
    assert row["pct_refused"] == pytest.approx(100 / 28)
    assert row["pct_skip"] == pytest.approx(100 / 28)
    assert row["pct_dk"] == pytest.approx(100 / 28)
    assert row["pct_na"] == pytest.approx(100 / 28)

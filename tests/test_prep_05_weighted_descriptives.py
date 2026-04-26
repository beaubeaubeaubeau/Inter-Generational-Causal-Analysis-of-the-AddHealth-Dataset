"""Tests for ``scripts/prep/05_weighted_descriptives.py``.

The script has its own (independent) implementations of ``clean_var``,
``weighted_mean_se``, ``weighted_prop_ci``, ``derive_cesd_sum``, and
``derive_bds_score``. We verify they agree with the canonical analysis
counterparts (parity tests) and exercise ``summarize_block`` end-to-end on a
small synthetic frame.

The PRXPREST binary-vs-continuous heuristic is also tested — TODO §B P2
flagged this as the historical cause of misclassifying continuous-in-[0,1]
variables; the explicit ``kinds={"PRXPREST": "continuous"}`` override in
the script must produce a `continuous (mean)` row, not `binary (prop)`.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PREP05 = REPO_ROOT / "scripts" / "prep" / "05_weighted_descriptives.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("prep05", PREP05)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Parity with analysis library
# ---------------------------------------------------------------------------

def test_prep05_clean_var_parity_for_known_var():
    """Both clean_var implementations must produce identical output for
    H1FS1 (CES-D item, range 0-3)."""
    mod = _load_module()
    from analysis.cleaning import clean_var as canonical_clean
    s = pd.Series([0, 1, 2, 3, 6, 7, 99, np.nan], dtype=float)
    a = mod.clean_var(s, "H1FS1")
    b = canonical_clean(s, "H1FS1")
    pd.testing.assert_series_equal(a, b)


def test_prep05_weighted_mean_se_parity():
    """Manual weighted_mean_se in prep05 must match analysis.weighted_stats."""
    mod = _load_module()
    from analysis.weighted_stats import weighted_mean_se as canonical_se
    rng = np.random.default_rng(2026)
    y = rng.normal(size=40)
    w = rng.random(40) + 0.5
    psu = np.repeat(np.arange(8), 5)
    a = mod.weighted_mean_se(y, w, psu)
    b = canonical_se(y, w, psu)
    for av, bv in zip(a, b):
        if isinstance(av, float) and np.isnan(av):
            assert np.isnan(bv)
        else:
            assert av == pytest.approx(bv)


def test_prep05_weighted_prop_ci_parity():
    """prep05's weighted_prop_ci must match the canonical implementation."""
    mod = _load_module()
    from analysis.weighted_stats import weighted_prop_ci as canonical_ci
    rng = np.random.default_rng(2026)
    ind = (rng.random(50) < 0.4).astype(float)
    w = np.ones(50)
    psu = np.repeat(np.arange(5), 10)
    a = mod.weighted_prop_ci(ind, w, psu)
    b = canonical_ci(ind, w, psu)
    for av, bv in zip(a, b):
        if isinstance(av, float) and np.isnan(av):
            assert np.isnan(bv)
        else:
            assert av == pytest.approx(bv)


def test_prep05_derive_cesd_sum_parity(synthetic_w1_df):
    """prep05's inlined derive_cesd_sum must match the canonical version."""
    mod = _load_module()
    from analysis.derivation import derive_cesd_sum as canonical_cesd
    a = mod.derive_cesd_sum(synthetic_w1_df)
    b = canonical_cesd(synthetic_w1_df)
    pd.testing.assert_series_equal(a, b, check_names=False)


# ---------------------------------------------------------------------------
# summarize_block + binary-vs-continuous heuristic
# ---------------------------------------------------------------------------

def _build_small_frame():
    """3 PSUs of 10 observations each, fixed seed."""
    rng = np.random.default_rng(0)
    n = 30
    df = pd.DataFrame({
        "AID": [f"A{i:04d}" for i in range(n)],
        "BIO_SEX": rng.choice([1.0, 2.0], size=n),
        "PRXPREST": rng.random(size=n) * 0.7,   # all in (0, 0.7) -> continuous
        "H1GI4": rng.choice([0.0, 1.0], size=n, p=[0.7, 0.3]),
    })
    weights = pd.DataFrame({
        "AID": df["AID"],
        "CLUSTER2": np.repeat(np.arange(3), 10),
        "GSWGT1": np.ones(n),
    })
    labels = {"BIO_SEX": "biological sex", "PRXPREST": "prestige proximity",
              "H1GI4": "Hispanic origin"}
    return df, weights, labels


def test_summarize_block_continuous_vs_binary_default_routing():
    """Without explicit kinds, BIO_SEX (range 1-2) routes to continuous because
    its (lo, hi) = (1, 2) doesn't match the (0, 1) binary heuristic. H1GI4
    (lo, hi) = (0, 1) routes to binary.
    """
    mod = _load_module()
    df, weights, labels = _build_small_frame()
    res = mod.summarize_block("test", df, weights, "GSWGT1",
                              ["BIO_SEX", "H1GI4"], labels)
    biosex_row = res[res["variable"] == "BIO_SEX"].iloc[0]
    assert biosex_row["kind"] == "continuous (mean)"
    h1gi4_row = res[res["variable"] == "H1GI4"].iloc[0]
    assert h1gi4_row["kind"] == "binary (prop)"


def test_summarize_block_prxprest_explicit_continuous_override():
    """Regression test for TODO §B (resolved 2026-04-25): PRXPREST with
    VALID_RANGES = (0, 1) was previously misclassified as binary. The fix
    is the explicit kinds override; verify it routes to continuous.
    """
    mod = _load_module()
    df, weights, labels = _build_small_frame()
    res = mod.summarize_block("test", df, weights, "GSWGT1",
                              ["PRXPREST"], labels,
                              kinds={"PRXPREST": "continuous"})
    row = res[res["variable"] == "PRXPREST"].iloc[0]
    assert row["kind"] == "continuous (mean)"
    # SD should be defined for continuous; mean in (0, 1)
    assert not pd.isna(row["sd"])
    assert 0 < row["mean_or_prop"] < 1


def test_summarize_block_prxprest_default_misclassified_binary():
    """WITHOUT the explicit kinds override, the (0, 1) range causes the
    binary heuristic to fire — this is the latent bug pattern flagged in
    TODO §B P2.

    The script protects against this by always passing kinds={"PRXPREST":
    "continuous"} in production. This test pins the misclassification
    behaviour so any future change to the heuristic itself is loud.
    """
    mod = _load_module()
    df, weights, labels = _build_small_frame()
    res = mod.summarize_block("test", df, weights, "GSWGT1",
                              ["PRXPREST"], labels)
    row = res[res["variable"] == "PRXPREST"].iloc[0]
    # CURRENT behaviour (no fix) — heuristic misroutes to binary.
    # TODO: remove this test once the heuristic itself is hardened (e.g.
    # to detect non-integer values and route to continuous automatically).
    assert row["kind"] == "binary (prop)"


def test_summarize_block_missing_variable_returns_zero_n_row():
    """A variable not in the frame yields a 'missing' kind row with n=0."""
    mod = _load_module()
    df, weights, labels = _build_small_frame()
    res = mod.summarize_block("test", df, weights, "GSWGT1",
                              ["NONEXISTENT_VAR"], labels)
    row = res[res["variable"] == "NONEXISTENT_VAR"].iloc[0]
    assert row["kind"] == "missing"
    assert row["n"] == 0


def test_fmt_handles_nan_and_none():
    """The fmt helper for markdown output returns 'NA' for None or NaN."""
    mod = _load_module()
    assert mod.fmt(None) == "NA"
    assert mod.fmt(float("nan")) == "NA"
    assert mod.fmt(1.234, digits=2) == "1.23"
    assert mod.fmt(0) == "0.0000"

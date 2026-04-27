"""Smoke tests for em-compensatory-by-ses.

Lightweight checks that the run.py / figures.py modules import and that
the primitive helpers behave on synthetic data. Does NOT exercise the
full pipeline against the actual W4 frame -- that would slow down CI and
require parquet caches that may not be available in every environment.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
EXP_DIR = HERE.parent
ROOT = EXP_DIR.parents[1]
sys.path.insert(0, str(EXP_DIR))
sys.path.insert(0, str(ROOT / "scripts"))


def test_run_module_imports():
    """`run.py` should import cleanly."""
    import run  # noqa: F401


def test_figures_module_imports():
    """`figures.py` should import cleanly."""
    import figures  # noqa: F401


def test_outcome_registry_shape():
    """Outcome registry has the 5 documented outcomes with 4-tuple values."""
    import run
    assert set(run.OUTCOMES.keys()) == {
        "H4BMI", "H4WAIST", "H4BMICLS", "H5LM5", "H5EC1",
    }
    for code, val in run.OUTCOMES.items():
        assert len(val) == 4, f"OUTCOMES[{code}] expected 4-tuple, got {val!r}"


def test_parent_ed_tertile_returns_three_bins():
    """`parent_ed_tertile` cuts a uniform vector into 3 rank-equal bins."""
    import run
    s = pd.Series(np.arange(30))
    t = run.parent_ed_tertile(s)
    counts = t.value_counts().sort_index()
    assert set(counts.index) == {1.0, 2.0, 3.0}
    # Roughly equal sizes (rank-equal).
    assert counts.min() >= 9 and counts.max() <= 11


def test_evalue_proxy_smoke():
    """E-value helper from analysis.sensitivity is reachable and monotone."""
    from analysis.sensitivity import evalue
    e_small = evalue(1.1)
    e_large = evalue(2.0)
    assert e_large > e_small > 1.0


def test_matching_helper_reachable():
    """match_ate_bias_corrected is importable and runs on a tiny synthetic case."""
    from analysis.matching import match_ate_bias_corrected
    rng = np.random.default_rng(0)
    n = 60
    X = rng.normal(size=(n, 2))
    A = (rng.uniform(size=n) > 0.5).astype(int)
    Y = 0.5 * A + X[:, 0] + rng.normal(scale=0.5, size=n)
    res = match_ate_bias_corrected(Y, A, X, M=2)
    assert "ate" in res and "se" in res
    assert np.isfinite(res["ate"])


@pytest.mark.skipif(
    not (ROOT / "scripts" / "analysis" / "data_loading.py").exists(),
    reason="Requires analysis package and parquet cache; skip outside full env.",
)
def test_full_pipeline_constructs_design_matrix():
    """Optional: smoke-fit one interaction model on a tiny synthetic frame."""
    import run
    from analysis.wls import weighted_ols
    rng = np.random.default_rng(1)
    n = 200
    df = pd.DataFrame({
        "AID": np.arange(n),
        "BIO_SEX": rng.choice([1, 2], size=n),
        "RACE": rng.choice(["NH-White", "NH-Black", "Hispanic", "Other"], size=n),
        "PARENT_ED": rng.integers(0, 7, size=n).astype(float),
        "CESD_SUM": rng.normal(15, 5, size=n),
        "H1GH1": rng.integers(1, 6, size=n).astype(float),
        "AH_RAW": rng.normal(100, 15, size=n),
        "IDGX2": rng.normal(0, 1, size=n),
        "CLUSTER2": rng.integers(0, 10, size=n),
        "GSWGT4_2": rng.uniform(0.5, 2.0, size=n),
        "GSW5": rng.uniform(0.5, 2.0, size=n),
        "H4BMI": rng.normal(27, 5, size=n),
    })
    res = run.fit_interaction(df, "H4BMI")
    assert res is not None
    assert "idgx2_x_parent_ed" in res["beta"].index

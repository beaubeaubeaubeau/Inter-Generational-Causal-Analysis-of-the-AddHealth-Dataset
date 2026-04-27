"""Smoke tests for em-depression-buffering.

Lightweight checks that the run.py / figures.py modules import and that
the primitive helpers behave on synthetic data. Does NOT exercise the
full pipeline against the actual W4 frame.
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
    """Outcome registry has the 3 documented W5 mental-health outcomes with
    4-tuple values."""
    import run
    assert set(run.OUTCOMES.keys()) == {"H5MN1", "H5MN2", "H5ID1"}
    for code, val in run.OUTCOMES.items():
        assert len(val) == 4, f"OUTCOMES[{code}] expected 4-tuple, got {val!r}"


def test_two_specs_for_d9_collider_check():
    """The D9 collider-check requires TWO specs: 'conservative' (CESD in adj.
    set + as moderator) and 'clean' (CESD as moderator only). Both must be
    registered in SPECS."""
    import run
    assert set(run.SPECS.keys()) == {"conservative", "clean"}
    # The conservative builder must include CESD_SUM as a covariate column;
    # the clean builder must NOT.
    df = pd.DataFrame({
        "BIO_SEX": [1, 2, 1, 2],
        "RACE": ["NH-White", "NH-Black", "Hispanic", "Other"],
        "PARENT_ED": [4.0, 5.0, 3.0, 6.0],
        "CESD_SUM": [10.0, 20.0, 30.0, 15.0],
        "H1GH1": [2.0, 3.0, 1.0, 4.0],
    })
    cons = run.SPECS["conservative"](df)
    clean = run.SPECS["clean"](df)
    assert "cesd_sum" in cons.columns
    assert "cesd_sum" not in clean.columns


def test_cesd_tertile_returns_three_bins():
    """`cesd_tertile` cuts a uniform vector into 3 rank-equal bins."""
    import run
    s = pd.Series(np.arange(30))
    t = run.cesd_tertile(s)
    counts = t.value_counts().sort_index()
    assert set(counts.index) == {1.0, 2.0, 3.0}
    assert counts.min() >= 9 and counts.max() <= 11


def test_evalue_proxy_smoke():
    """E-value helper from analysis.sensitivity is reachable and monotone."""
    from analysis.sensitivity import evalue
    assert evalue(2.0) > evalue(1.1) > 1.0


def test_matching_helper_reachable():
    """match_ate_bias_corrected is importable and runs on a tiny synthetic case."""
    from analysis.matching import match_ate_bias_corrected
    rng = np.random.default_rng(0)
    n = 60
    X = rng.normal(size=(n, 2))
    A = (rng.uniform(size=n) > 0.5).astype(int)
    Y = 0.5 * A + X[:, 0] + rng.normal(scale=0.5, size=n)
    res = match_ate_bias_corrected(Y, A, X, M=2)
    assert "ate" in res and np.isfinite(res["ate"])


@pytest.mark.skipif(
    not (ROOT / "scripts" / "analysis" / "data_loading.py").exists(),
    reason="Requires analysis package and parquet cache; skip outside full env.",
)
def test_full_pipeline_constructs_design_matrix():
    """Optional: smoke-fit one interaction model on synthetic frame, both specs."""
    import run
    rng = np.random.default_rng(3)
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
        "H5MN1": rng.normal(3.0, 1.0, size=n),
    })
    for spec in ("conservative", "clean"):
        res = run.fit_interaction(df, "H5MN1", spec)
        assert res is not None
        assert "idgx2_x_cesd" in res["beta"].index

"""Smoke tests for popularity-vs-sociability (EXP-POPSOC).

Lightweight checks that the run.py / figures.py modules import and that
their registries / primitives are correctly shaped. Does NOT exercise the
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


def test_exposures_dict_shape():
    """EXPOSURES dict is shaped {"IDGX2": "popularity", "ODGX2": "sociability"} —
    two W1 network-derived exposures, in-degree (popularity) and out-degree
    (sociability), as documented in the README."""
    import run
    assert isinstance(run.EXPOSURES, dict)
    assert set(run.EXPOSURES.keys()) == {"IDGX2", "ODGX2"}
    # Labels should mention the construct names (popularity / sociability).
    assert "popularity" in run.EXPOSURES["IDGX2"].lower()
    assert "sociability" in run.EXPOSURES["ODGX2"].lower()


def test_outcomes_registry_has_13_entries():
    """13-outcome battery as documented in the README."""
    import run
    assert len(run.OUTCOMES) == 13
    # Every outcome maps to (label, group) tuple.
    for code, val in run.OUTCOMES.items():
        assert len(val) == 2, f"OUTCOMES[{code}] expected 2-tuple, got {val!r}"


def test_adjustment_tier_per_outcome():
    """Adjustment tier registry covers every outcome and only uses known tiers."""
    import run
    assert set(run.ADJ_TIER_BY_OUTCOME.keys()) == set(run.OUTCOMES.keys())
    assert set(run.ADJ_TIER_BY_OUTCOME.values()) <= {"L0", "L0+L1", "L0+L1+AHPVT"}
    # SES outcomes drop AHPVT under DAG-SES.
    for ses_oc in ("H5LM5", "H5EC1"):
        assert run.ADJ_TIER_BY_OUTCOME[ses_oc] == "L0+L1"


def test_polysocial_exposure_list_nonempty():
    """The polysocial PCA list should include both popularity and sociability
    plus a broad battery of W1 social exposures."""
    import run
    assert "IDGX2" in run.POLYSOCIAL_EXPOSURES
    assert "ODGX2" in run.POLYSOCIAL_EXPOSURES
    assert len(run.POLYSOCIAL_EXPOSURES) >= 20


def test_evalue_proxy_smoke():
    """E-value helper from analysis.sensitivity is reachable and monotone."""
    from analysis.sensitivity import evalue
    assert evalue(2.0) > evalue(1.1) > 1.0

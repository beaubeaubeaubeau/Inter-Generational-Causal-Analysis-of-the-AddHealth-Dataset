"""Smoke tests for friendship-quality-vs-quantity (EXP-QVQ).

Lightweight checks that the run.py / figures.py modules import and that
their registries / primitives are correctly shaped. Does NOT exercise the
full pipeline against the actual W1/W4/W5 frame.
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


def test_exposures_are_three_friendship_grid_vars():
    """EXPOSURES is the three W1 friendship-grid head-to-head exposures."""
    import run
    assert isinstance(run.EXPOSURES, dict)
    assert set(run.EXPOSURES.keys()) == {
        "FRIEND_DISCLOSURE_ANY", "FRIEND_N_NOMINEES", "FRIEND_CONTACT_SUM",
    }
    # Labels mention quality / quantity / frequency.
    assert "quality" in run.EXPOSURES["FRIEND_DISCLOSURE_ANY"].lower()
    assert "quantity" in run.EXPOSURES["FRIEND_N_NOMINEES"].lower()
    assert "frequency" in run.EXPOSURES["FRIEND_CONTACT_SUM"].lower()


def test_outcomes_registry_has_13_entries():
    """13-outcome battery, same as popularity-vs-sociability."""
    import run
    assert len(run.OUTCOMES) == 13


def test_adjustment_tier_per_outcome():
    """Adjustment tier registry covers every outcome and only uses known tiers.
    SES outcomes drop AHPVT under DAG-SES."""
    import run
    assert set(run.ADJ_TIER_BY_OUTCOME.keys()) == set(run.OUTCOMES.keys())
    assert set(run.ADJ_TIER_BY_OUTCOME.values()) <= {"L0", "L0+L1", "L0+L1+AHPVT"}
    for ses_oc in ("H5LM5", "H5EC1"):
        assert run.ADJ_TIER_BY_OUTCOME[ses_oc] == "L0+L1"


def test_joint_fit_default_uses_all_three_exposures():
    """The joint-fit primitive defaults to all three exposures (head-to-head),
    which is the load-bearing identification choice."""
    import inspect
    import run
    sig = inspect.signature(run._fit_joint)
    assert "exposure_cols" in sig.parameters
    # Default is None -> all three.
    assert sig.parameters["exposure_cols"].default is None


def test_drop_one_function_exists():
    """Drop-one-exposure sensitivity is exposed as a top-level function."""
    import run
    assert callable(run.run_sensitivity_drop_one)


def test_friendship_grid_derivation_reachable():
    """The friendship-grid derivation utility is importable for the fallback
    path in `_load_frame`."""
    from analysis.derivation import derive_friendship_grid
    assert callable(derive_friendship_grid)


def test_evalue_proxy_smoke():
    """E-value helper from analysis.sensitivity is reachable and monotone."""
    from analysis.sensitivity import evalue
    assert evalue(2.0) > evalue(1.1) > 1.0

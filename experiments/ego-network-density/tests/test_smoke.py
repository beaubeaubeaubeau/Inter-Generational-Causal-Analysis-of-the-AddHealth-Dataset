"""Smoke tests for ego-network-density (EXP-EGODEN).

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


def test_exposures_are_four_density_vars():
    """EXPOSURES is the four W1 ego-network density measures: RCHDEN, ESDEN,
    ERDEN, ESRDEN."""
    import run
    assert isinstance(run.EXPOSURES, dict)
    assert set(run.EXPOSURES.keys()) == {"RCHDEN", "ESDEN", "ERDEN", "ESRDEN"}


def test_outcomes_focused_six():
    """Focused outcome subset: 3 mental health + 2 SES + 1 cognitive (6 total)."""
    import run
    assert len(run.OUTCOMES) == 6
    assert "W4_COG_COMP" in run.OUTCOMES
    for ses_oc in ("H5LM5", "H5EC1"):
        assert ses_oc in run.OUTCOMES
    for mh_oc in ("H5MN1", "H5MN2", "H5ID16"):
        assert mh_oc in run.OUTCOMES


def test_fit_cell_default_includes_reach3():
    """The primary fit cell defaults to with_reach3=True; the conditioning is
    the load-bearing identification move per Burt's structural-holes
    interpretation. The SES tier drops AHPVT but always retains REACH3."""
    import inspect
    import run
    sig = inspect.signature(run._fit_cell)
    assert sig.parameters["with_reach3"].default is True
    # Adjustment tier registry must cover all outcomes (REACH3 added on top).
    assert set(run.ADJ_TIER_BY_OUTCOME.keys()) == set(run.OUTCOMES.keys())
    for ses_oc in ("H5LM5", "H5EC1"):
        assert run.ADJ_TIER_BY_OUTCOME[ses_oc] == "L0+L1"


def test_no_reach3_sensitivity_runs_primary_with_flag_off():
    """The no-REACH3 sensitivity is reachable as a function and toggles the
    `with_reach3=False` path of run_primary."""
    import inspect
    import run
    src = inspect.getsource(run.run_sensitivity_no_reach3)
    assert "with_reach3=False" in src


def test_evalue_proxy_smoke():
    """E-value helper from analysis.sensitivity is reachable and monotone."""
    from analysis.sensitivity import evalue
    assert evalue(2.0) > evalue(1.1) > 1.0

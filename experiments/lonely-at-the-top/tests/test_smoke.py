"""Smoke tests for lonely-at-the-top.

Lock in the pre-flight findings (2x2 abandoned, continuous interaction
adopted) and the outcome inventory. Do not run the full pipeline.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
EXP_ROOT = HERE.parent
REPO_ROOT = EXP_ROOT.parents[1]


def _import_run():
    sys.path.insert(0, str(EXP_ROOT))
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    if "run" in sys.modules:
        del sys.modules["run"]
    return importlib.import_module("run")


def test_module_imports() -> None:
    run = _import_run()
    assert run is not None


def test_exposure_columns_locked() -> None:
    run = _import_run()
    assert run.POP_COL == "IDGX2"
    assert run.LONE_COL == "H1FS13"


def test_outcome_inventory_locked() -> None:
    run = _import_run()
    expected = {"H4BMI", "H4WAIST", "H5MN1", "H5MN2", "H5ID1"}
    assert set(run.OUTCOMES) == expected


def test_preflight_2x2_decision_recorded() -> None:
    """The pre-flight finding (min cell N=73 < 150 floor) must be hardcoded."""
    run = _import_run()
    assert run.PREFLIGHT_MIN_CELL_N_2X2 == 73
    assert run.POSITIVITY_FLOOR == 150
    assert run.PREFLIGHT_MIN_CELL_N_2X2 < run.POSITIVITY_FLOOR, (
        "If pre-flight N has changed, revisit whether the 2x2 design can be "
        "reinstated as the primary identification strategy."
    )


def test_adjustment_builders_present() -> None:
    run = _import_run()
    assert set(run.ADJ_BUILDERS) == {"L0", "L0+L1", "L0+L1+AHPVT"}


@pytest.mark.parametrize("module_name", ["figures"])
def test_figures_module_imports(module_name: str) -> None:
    sys.path.insert(0, str(EXP_ROOT))
    if module_name in sys.modules:
        del sys.modules[module_name]
    importlib.import_module(module_name)

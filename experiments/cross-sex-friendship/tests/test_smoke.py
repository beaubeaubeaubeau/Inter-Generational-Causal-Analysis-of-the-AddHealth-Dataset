"""Smoke tests for cross-sex-friendship.

Locks in the 8-cell × 13-outcome design and the per-outcome
adjustment-set policy (drop AHPVT for SES outcomes only).
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


def test_outcome_inventory_locked() -> None:
    run = _import_run()
    expected = {
        "W4_COG_COMP", "H4BMI", "H4SBP", "H4DBP", "H4WAIST", "H4BMICLS",
        "H5MN1", "H5MN2", "H5ID1", "H5ID4", "H5ID16", "H5LM5", "H5EC1",
    }
    assert set(run.OUTCOMES) == expected
    assert len(run.OUTCOMES) == 13


def test_stratifications_locked() -> None:
    run = _import_run()
    assert run.STRATIFICATIONS == [
        ("BIO_SEX × HAVEBMF", "HAVEBMF"),
        ("BIO_SEX × HAVEBFF", "HAVEBFF"),
    ]


def test_cell_grid_is_8_cells() -> None:
    run = _import_run()
    n_cells = len(run.STRATIFICATIONS) * len(run.SEX_CELLS) * len(run.FRIEND_CELLS)
    assert n_cells == 8


def test_ses_outcomes_drop_ahpvt() -> None:
    """DAG-SES requires AHPVT to be dropped for H5LM5 and H5EC1."""
    run = _import_run()
    for outcome, meta in run.OUTCOMES.items():
        drops_ahpvt = meta[4]
        if outcome in {"H5LM5", "H5EC1"}:
            assert drops_ahpvt is True, f"{outcome}: SES outcome must drop AHPVT"
        else:
            assert drops_ahpvt is False, f"{outcome}: non-SES outcome must keep AHPVT"


def test_friend_alt_exposures_present() -> None:
    """Alternative friendship coding for sensitivity must include grid metrics."""
    run = _import_run()
    assert "FRIEND_N_NOMINEES" in run.FRIEND_ALT_EXPOSURES
    assert "FRIEND_DISCLOSURE_ANY" in run.FRIEND_ALT_EXPOSURES


@pytest.mark.parametrize("module_name", ["figures"])
def test_figures_module_imports(module_name: str) -> None:
    sys.path.insert(0, str(EXP_ROOT))
    if module_name in sys.modules:
        del sys.modules[module_name]
    importlib.import_module(module_name)

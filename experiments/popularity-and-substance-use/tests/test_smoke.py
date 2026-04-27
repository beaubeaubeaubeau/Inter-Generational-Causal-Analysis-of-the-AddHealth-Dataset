"""Smoke tests for popularity-and-substance-use.

These tests exist to catch import-level breakage and to lock in the
hardcoded outcome inventory shape. They do NOT execute the full WLS
pipeline (which requires the cached parquets). For end-to-end coverage
defer to the project-level `tests/` battery.
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
    """run.py imports cleanly (catches missing analysis utilities)."""
    run = _import_run()
    assert run is not None


def test_substance_outcome_inventory_locked() -> None:
    """Pre-flight outcome list must remain exactly the 8 codebook codes locked 2026-04-26."""
    run = _import_run()
    expected = {
        "H4TO5", "H4TO39", "H4TO70", "H4TO65B", "H4TO65C",
        "H5TO2", "H5TO12", "H5TO15",
    }
    assert set(run.SUBSTANCE_OUTCOMES) == expected
    # Each entry is (label, wave, kind, weight_col).
    for code, value in run.SUBSTANCE_OUTCOMES.items():
        assert isinstance(value, tuple) and len(value) == 4, code
        label, wave, kind, w_col = value
        assert wave in {"W4", "W5"}, code
        assert w_col in {"GSWGT4_2", "GSW5"}, code
        assert label, code  # non-empty


def test_exposure_is_idgx2() -> None:
    """Exposure column is locked to IDGX2 (popularity, in-degree)."""
    run = _import_run()
    assert run.EXPOSURE_COL == "IDGX2"


def test_adjustment_builders_present() -> None:
    """L0 / L0+L1 / L0+L1+AHPVT builders all present for D4 stability."""
    run = _import_run()
    assert set(run.ADJ_BUILDERS) == {"L0", "L0+L1", "L0+L1+AHPVT"}


@pytest.mark.parametrize("module_name", ["figures"])
def test_figures_module_imports(module_name: str) -> None:
    """figures.py imports cleanly."""
    sys.path.insert(0, str(EXP_ROOT))
    if module_name in sys.modules:
        del sys.modules[module_name]
    importlib.import_module(module_name)

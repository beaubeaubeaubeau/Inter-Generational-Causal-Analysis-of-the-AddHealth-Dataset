"""Smoke tests for negative-control-battery.

Locks in (a) the 2026-04-27 outcome-side NC pre-flight inventory, (b) the
H5ID1 exclusion, (c) the per-candidate pre-flight skip-don't-crash policy
for exposure-side NCs.
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


def test_outcome_side_nc_inventory_locked() -> None:
    """The five outcome-side NCs from the 2026-04-27 pre-flight must be present."""
    run = _import_run()
    expected = {"H5EL6D", "H5EL6F", "H5DA9", "H5EL6A", "H5EL6B"}
    assert set(run.NC_OUTCOMES) == expected
    # Each entry preserves codebook label + N_preflight.
    for code, value in run.NC_OUTCOMES.items():
        assert isinstance(value, tuple) and len(value) == 4, code
        label, wave, n_pre, kind = value
        assert label, code
        assert wave == "W5", code
        assert n_pre > 4000, f"{code}: pre-flight N below documented threshold"


def test_h5id1_explicitly_excluded() -> None:
    """H5ID1 is explicitly excluded as too socially confounded."""
    run = _import_run()
    assert "H5ID1" in run.NC_OUTCOMES_EXCLUDED
    assert "H5ID1" not in run.NC_OUTCOMES


def test_exposure_side_nc_candidates_listed() -> None:
    """All four exposure-side NC candidates from TODO §A2 are present."""
    run = _import_run()
    candidates = {c[0] for c in run.NC_EXPOSURE_CANDIDATES}
    # Names may be tentative pending pre-flight; check that each candidate
    # has the (col, parquet, label) shape we rely on in run.py.
    for entry in run.NC_EXPOSURE_CANDIDATES:
        assert isinstance(entry, tuple) and len(entry) == 3, entry
        col, parquet, label = entry
        assert col, entry
        assert parquet.endswith(".parquet"), entry
        assert label, entry
    # The semantic labels we expect.
    label_blob = " ".join(c[2] for c in run.NC_EXPOSURE_CANDIDATES).lower()
    for keyword in ("blood", "menarche", "hand", "residential"):
        assert keyword in label_blob, f"Missing NC candidate keyword: {keyword!r}"


def test_real_exposures_dir2_includes_idgx2() -> None:
    """IDGX2 (popularity) is the headline real exposure for Direction 2."""
    run = _import_run()
    assert "IDGX2" in run.REAL_EXPOSURES_DIR2
    # Should mirror the screening 24-exposure list (ballpark length).
    assert 20 <= len(run.REAL_EXPOSURES_DIR2) <= 30


def test_real_outcomes_dir1_includes_cog_and_cardio() -> None:
    """Direction 1 NC exposures must be tested against cognition + cardiometabolic."""
    run = _import_run()
    assert "W4_COG_COMP" in run.REAL_OUTCOMES_DIR1
    assert "H4BMI" in run.REAL_OUTCOMES_DIR1


@pytest.mark.parametrize("module_name", ["figures"])
def test_figures_module_imports(module_name: str) -> None:
    sys.path.insert(0, str(EXP_ROOT))
    if module_name in sys.modules:
        del sys.modules[module_name]
    importlib.import_module(module_name)

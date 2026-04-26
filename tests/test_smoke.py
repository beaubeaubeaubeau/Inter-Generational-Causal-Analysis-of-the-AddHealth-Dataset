"""End-to-end smoke test for the cognitive-screening experiment.

Spawns ``python experiments/cognitive-screening/run.py`` in a subprocess so
test isolation is clean (no shared module state with pytest), then asserts
the key output artefacts were written.

Skipped automatically if the cached parquets aren't present (the prep
pipeline has not been run yet).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
EXP = REPO_ROOT / "experiments" / "cognitive-screening"
RUN = EXP / "run.py"

# Cached parquets that the experiment requires
REQUIRED_CACHE = REPO_ROOT / "cache" / "analytic_w4.parquet"


@pytest.mark.slow
@pytest.mark.skipif(
    not REQUIRED_CACHE.exists(),
    reason="requires cached parquets from prep pipeline (cache/analytic_w4.parquet)",
)
def test_cognitive_screening_runs_end_to_end():
    """Run the full cognitive-screening pipeline and verify primary outputs.

    Asserts:
      * Process exits with returncode 0.
      * tables/primary/14_screening_matrix.csv exists and is > 1 KB.
      * At least one figure in figures/primary/ exists and is > 10 KB.

    This test is marked ``slow`` so fast CI runs can deselect it via
    ``pytest -m 'not slow'``.
    """
    result = subprocess.run(
        [sys.executable, str(RUN)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert result.returncode == 0, (
        f"cognitive-screening run failed:\nSTDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )

    # Primary screening matrix
    matrix = EXP / "tables" / "primary" / "14_screening_matrix.csv"
    assert matrix.exists(), f"Missing primary screening matrix: {matrix}"
    assert matrix.stat().st_size > 1024, (
        f"Screening matrix is suspiciously small: {matrix.stat().st_size} bytes"
    )

    # At least one primary figure
    figures = list((EXP / "figures" / "primary").glob("*.png"))
    assert figures, "No primary figures produced"
    assert any(f.stat().st_size > 10240 for f in figures), (
        "No primary figure exceeds 10 KB; rendering likely failed"
    )

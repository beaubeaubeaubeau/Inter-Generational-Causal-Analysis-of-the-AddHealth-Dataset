"""Tests for ``scripts/prep/08_build_analytic_frame.py``.

08 is mostly a data-pipeline orchestrator (load → derive → merge → write
parquet). Its only directly testable surface is the merge structure of
already-built analytic frames. We assert that the cached parquets satisfy
the documented invariants (AID is unique, MODE is restricted to {I, T}
in W5, weight columns survive the merge), which is the lightest possible
end-to-end smoke check on the merge logic.

Skipped if the cache parquets aren't present.
"""
from __future__ import annotations

import pandas as pd
import pytest

from analysis import CACHE


_W4 = CACHE / "analytic_w4.parquet"
_W5 = CACHE / "analytic_w5.parquet"
_W1F = CACHE / "analytic_w1_full.parquet"


@pytest.mark.skipif(
    not _W4.exists(),
    reason="requires cached analytic_w4.parquet from prep pipeline",
)
def test_analytic_w4_aid_unique():
    """The W4 analytic frame has unique AIDs (one_to_one merge invariant)."""
    df = pd.read_parquet(_W4)
    assert df["AID"].is_unique


@pytest.mark.skipif(
    not _W4.exists(),
    reason="requires cached analytic_w4.parquet from prep pipeline",
)
def test_analytic_w4_has_required_columns():
    """W4 frame must carry the W1 covariates, W4 outcomes, and weight columns."""
    df = pd.read_parquet(_W4)
    required = {
        "AID", "BIO_SEX", "AH_PVT", "RACE", "PARENT_ED",
        "CESD_SUM", "SCHOOL_BELONG", "FRIEND_N_NOMINEES",
        "C4WD90_1", "C4WD60_1", "C4NUMSCR", "W4_COG_COMP",
        "CLUSTER2", "GSWGT4_2",
    }
    missing = required - set(df.columns)
    assert not missing, f"Missing W4 columns: {missing}"


@pytest.mark.skipif(
    not _W5.exists(),
    reason="requires cached analytic_w5.parquet from prep pipeline",
)
def test_analytic_w5_mode_restricted_to_in_person_or_telephone():
    """The W5 analytic frame is mode-restricted to MODE ∈ {I, T}."""
    df = pd.read_parquet(_W5)
    modes = set(df["MODE"].dropna().unique())
    assert modes.issubset({"I", "T"}), f"Unexpected modes in W5 frame: {modes}"


@pytest.mark.skipif(
    not _W5.exists(),
    reason="requires cached analytic_w5.parquet from prep pipeline",
)
def test_analytic_w5_aid_unique():
    df = pd.read_parquet(_W5)
    assert df["AID"].is_unique


@pytest.mark.skipif(
    not _W5.exists(),
    reason="requires cached analytic_w5.parquet from prep pipeline",
)
def test_analytic_w5_has_w5_outcomes():
    df = pd.read_parquet(_W5)
    required = {"AID", "MODE", "C5WD90_1", "C5WD60_1",
                "BDS_SCORE", "W5_COG_COMP", "CLUSTER2", "GSW5"}
    missing = required - set(df.columns)
    assert not missing, f"Missing W5 columns: {missing}"


@pytest.mark.skipif(
    not _W1F.exists(),
    reason="requires cached analytic_w1_full.parquet from prep pipeline",
)
def test_analytic_w1_full_aid_unique():
    df = pd.read_parquet(_W1F)
    assert df["AID"].is_unique


@pytest.mark.skipif(
    not _W1F.exists(),
    reason="requires cached analytic_w1_full.parquet from prep pipeline",
)
def test_analytic_w1_full_does_not_carry_network_columns():
    """The W1-full frame is the no-network design — IDGX2/ODGX2 should
    NOT be present in the schema (they're only in the W4/W5 frames)."""
    df = pd.read_parquet(_W1F)
    assert "IDGX2" not in df.columns
    assert "ODGX2" not in df.columns


@pytest.mark.skipif(
    not (_W4.exists() and _W1F.exists()),
    reason="requires cached W4 and W1-full parquets from prep pipeline",
)
def test_w4_subset_of_w1_full_aids():
    """Every AID in analytic_w4 (which requires both W1 inhome + W4) must
    also appear in analytic_w1_full (which requires only W1 inhome + W4)."""
    w4 = pd.read_parquet(_W4)
    w1f = pd.read_parquet(_W1F)
    assert set(w4["AID"]) <= set(w1f["AID"])

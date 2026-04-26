"""Tests for ``analysis.data_loading``.

Covers ``load_outcome`` (which has non-trivial routing logic + clean_var
application). The ``load_w*`` functions are deliberately untested: they
are pure pandas/pyreadstat IO wrappers (e.g. ``return _load_parquet(...)``)
with no transformation logic worth testing in isolation.
"""
from __future__ import annotations

import pandas as pd
import pytest

from analysis import CACHE
from analysis.data_loading import load_outcome


_W4_PARQUET = CACHE / "w4inhome.parquet"
_W5_PARQUET = CACHE / "pwave5.parquet"


def test_load_outcome_unknown_prefix_raises():
    """Codes that don't start with H4 or H5 must raise ValueError."""
    aid = pd.Series(["A0001", "A0002"], name="AID")
    with pytest.raises(ValueError, match="Unrecognized outcome prefix"):
        load_outcome(aid, "C4WD90_1")


@pytest.mark.skipif(
    not _W4_PARQUET.exists(),
    reason="requires cached w4inhome.parquet from prep pipeline",
)
def test_load_outcome_w4_returns_aligned_series():
    """load_outcome with a real W4 code returns a series aligned to the
    input AID series and named after the code."""
    w4 = pd.read_parquet(_W4_PARQUET, columns=["AID", "H4BMI"])
    aid_sample = w4["AID"].iloc[:30].reset_index(drop=True)
    out = load_outcome(aid_sample, "H4BMI")
    assert out.name == "H4BMI"
    assert len(out) == len(aid_sample)
    assert out.index.equals(aid_sample.index)


@pytest.mark.skipif(
    not _W4_PARQUET.exists(),
    reason="requires cached w4inhome.parquet from prep pipeline",
)
def test_load_outcome_applies_clean_var():
    """If the code has a VALID_RANGES entry, out-of-range values must be NaN.
    Run on the real W4 cache for H4BMI (range 10-80); reserve codes
    996/997/998 should not appear in the cleaned output."""
    w4 = pd.read_parquet(_W4_PARQUET, columns=["AID"])
    aid = w4["AID"]
    out = load_outcome(aid, "H4BMI")
    cleaned = out.dropna()
    assert (cleaned >= 10).all()
    assert (cleaned <= 80).all()


@pytest.mark.skipif(
    not _W4_PARQUET.exists(),
    reason="requires cached w4inhome.parquet from prep pipeline",
)
def test_load_outcome_unknown_aid_returns_nan():
    """An AID that doesn't exist in the source frame should yield NaN."""
    aid = pd.Series(["FAKEAID9999"], name="AID")
    out = load_outcome(aid, "H4BMI")
    assert pd.isna(out.iloc[0])


@pytest.mark.skipif(
    not _W5_PARQUET.exists(),
    reason="requires cached pwave5.parquet from prep pipeline",
)
def test_load_outcome_routes_h5_to_pwave5():
    """H5 codes route to pwave5.parquet."""
    w5 = pd.read_parquet(_W5_PARQUET, columns=["AID"])
    aid = w5["AID"].iloc[:10].reset_index(drop=True)
    out = load_outcome(aid, "H5MN1")
    assert out.name == "H5MN1"
    assert len(out) == 10

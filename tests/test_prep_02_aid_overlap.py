"""Tests for ``scripts/prep/02_aid_overlap.py`` helpers.

Tests the ``pct_of_smaller`` ratio helper. Module is imported via
``importlib`` because the script's filename starts with a digit.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
PREP02 = REPO_ROOT / "scripts" / "prep" / "02_aid_overlap.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("prep02", PREP02)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_pct_of_smaller_basic():
    """50 / min(100, 200) -> 50%."""
    mod = _load_module()
    a = set(range(100))
    b = set(range(50, 250))
    inter_n = 50  # |a & b|
    pct = mod.pct_of_smaller(inter_n, a, b)
    assert pct == 50.0


def test_pct_of_smaller_full_overlap():
    """If a is a subset of b, pct = 100%."""
    mod = _load_module()
    a = set(range(50))
    b = set(range(100))
    pct = mod.pct_of_smaller(50, a, b)
    assert pct == 100.0


def test_pct_of_smaller_zero_when_either_empty():
    """If either set is empty, ratio is 0 (avoids divide-by-zero)."""
    mod = _load_module()
    pct = mod.pct_of_smaller(0, set(), {1, 2, 3})
    assert pct == 0.0


def test_pct_of_smaller_no_overlap():
    """Disjoint sets -> intersection 0 -> 0% of smaller."""
    mod = _load_module()
    a = {1, 2, 3}
    b = {10, 20, 30}
    pct = mod.pct_of_smaller(0, a, b)
    assert pct == 0.0

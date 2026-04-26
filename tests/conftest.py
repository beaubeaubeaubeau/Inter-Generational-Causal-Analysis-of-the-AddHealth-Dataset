"""Shared pytest fixtures for the Add Health analysis library tests.

The tests target ``scripts/analysis/*`` as a package. We add ``scripts/`` to
``sys.path`` here so tests can do ``from analysis.cleaning import clean_var``
without installing the package.

Synthetic fixtures are hand-constructed (~50 rows) with known expected outputs
so individual test assertions can be exact, not just smoke-checks.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Make `scripts/analysis` importable as `analysis` (matches the in-script
# `sys.path.insert(0, str(HERE))` pattern used by every task*.py file).
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def pytest_configure(config):
    """Register custom markers used by the smoke test."""
    config.addinivalue_line(
        "markers",
        "slow: long-running smoke / integration tests "
        "(deselect with -m 'not slow')",
    )


@pytest.fixture
def synthetic_w1_df() -> pd.DataFrame:
    """Hand-constructed 50-row W1-shaped frame.

    Columns cover what task05 / task14 / the derivation helpers consume.
    Designed so individual rows have known correct outputs:
      - row 0: all-valid baseline (CES-D items all 0 -> sum = 0 after reverse)
      - row 1: a respondent with reserve codes (96, 99) sprinkled in, to test
        that ``clean_var`` strips them.
      - row 2: missing all CES-D items -> sum = NaN (min_count=19).
      - row 3-9: vary belonging items, friendship grid, race, parent-ed.
      - rows 10-49: random-but-deterministic filler so weighted_mean_se has
        enough non-degenerate variance.
    """
    rng = np.random.default_rng(20260425)
    n = 50

    df = pd.DataFrame({"AID": [f"A{i:04d}" for i in range(n)]})

    # CES-D items H1FS1..H1FS19, valid 0-3
    for i in range(1, 20):
        df[f"H1FS{i}"] = rng.integers(0, 4, size=n).astype(float)
    # Row 0: all zeros -> after reversing items 4/8/11/15: sum = 4 * 3 = 12
    for i in range(1, 20):
        df.at[0, f"H1FS{i}"] = 0.0
    # Row 1: introduce reserve codes (96, 99) — should be dropped
    df.at[1, "H1FS1"] = 96.0
    df.at[1, "H1FS2"] = 99.0
    # Row 2: all NaN -> sum NaN
    for i in range(1, 20):
        df.at[2, f"H1FS{i}"] = np.nan

    # Demographics
    df["BIO_SEX"] = rng.choice([1.0, 2.0], size=n)
    df["H1GI4"] = rng.integers(0, 2, size=n).astype(float)         # Hispanic indicator
    df["H1GI6A"] = rng.integers(0, 2, size=n).astype(float)        # White
    df["H1GI6B"] = rng.integers(0, 2, size=n).astype(float)        # Black
    df["H1GI6C"] = rng.integers(0, 2, size=n).astype(float)
    df["H1GI6D"] = rng.integers(0, 2, size=n).astype(float)
    df["H1GI6E"] = rng.integers(0, 2, size=n).astype(float)
    # Pin specific race rows for derive_race_ethnicity:
    df.loc[3, ["H1GI4", "H1GI6A", "H1GI6B"]] = [1.0, 0.0, 0.0]  # Hispanic
    df.loc[4, ["H1GI4", "H1GI6A", "H1GI6B"]] = [0.0, 1.0, 0.0]  # NH-White
    df.loc[5, ["H1GI4", "H1GI6A", "H1GI6B"]] = [0.0, 0.0, 1.0]  # NH-Black
    df.loc[6, ["H1GI4", "H1GI6A", "H1GI6B"]] = [0.0, 0.0, 0.0]  # Other (all set)

    # Parent ed (1-11 range; reserves stripped)
    df["H1RM1"] = rng.integers(1, 12, size=n).astype(float)
    df["H1RF1"] = rng.integers(1, 12, size=n).astype(float)
    df.at[7, "H1RM1"] = 7.0   # college grad -> recoded 5
    df.at[7, "H1RF1"] = 4.0   # HS grad      -> recoded 2
    df.at[8, "H1RM1"] = 9.0   # never went   -> recoded 0
    df.at[8, "H1RF1"] = 9.0
    df.at[9, "H1RM1"] = 99.0  # reserve -> NaN -> max ignores
    df.at[9, "H1RF1"] = 4.0   # HS grad -> recoded 2

    # School belonging items (1-5; reverse-scored so higher = belonging)
    for c in ["H1ED19", "H1ED20", "H1ED21", "H1ED22", "H1ED23", "H1ED24"]:
        df[c] = rng.integers(1, 6, size=n).astype(float)
    # Pin row 0: all 1s -> after reverse 5*5 + (6-1)=5 -> sum = 30
    for c in ["H1ED19", "H1ED20", "H1ED21", "H1ED22", "H1ED23", "H1ED24"]:
        df.at[0, c] = 1.0

    # Friendship grid: H1MF{item}{slot}, H1FF{item}{slot}; nominees row 0 has 1
    # nominated male friend with all contact items = 1.
    for prefix in ["H1MF", "H1FF"]:
        for slot in "ABCDE":
            for item in [2, 3, 4, 5, 6, 7, 8, 9, 10]:
                df[f"{prefix}{item}{slot}"] = 7.0  # legit-skip everywhere by default
    # Row 0: 1 male friend, slot A, in school, all 5 contact items = 1
    df.at[0, "H1MF2A"] = 1.0  # in your school
    for item in [6, 7, 8, 9, 10]:
        df.at[0, f"H1MF{item}A"] = 1.0
    # Row 1: 7 (skip) for in_school -> not nominated regardless of other items
    df.at[1, "H1MF2A"] = 7.0
    df.at[1, "H1MF6A"] = 1.0  # contact present but slot not nominated -> 0

    return df


@pytest.fixture
def synthetic_w4_df() -> pd.DataFrame:
    """Hand-constructed 50-row W4-shaped frame for cognitive-composite tests.

    Columns:
      - C4WD90_1 / C4WD60_1: word recall (0-15)
      - C4NUMSCR: backward digit span score (0-7)
      - H4GH5F / H4GH5I: feet/inches for HEIGHT_IN aggregation
    Pinned rows:
      - row 0: all components valid
      - row 1: all components NaN (used to assert NaN propagation)
      - row 2: only one of {C4WD90_1, C4WD60_1, C4NUMSCR} non-NaN — composite
        is mean-with-skipna=False so should propagate NaN.
      - row 3: H4GH5F=5, H4GH5I=6 -> HEIGHT_IN = 66
      - row 4: H4GH5F=6, H4GH5I=NaN -> HEIGHT_IN = NaN (inches missing)
      - row 5: both H4GH5F and H4GH5I NaN -> HEIGHT_IN = NaN
    """
    rng = np.random.default_rng(20260425)
    n = 50
    df = pd.DataFrame({"AID": [f"A{i:04d}" for i in range(n)]})
    df["C4WD90_1"] = rng.integers(0, 16, size=n).astype(float)
    df["C4WD60_1"] = rng.integers(0, 16, size=n).astype(float)
    df["C4NUMSCR"] = rng.integers(0, 8, size=n).astype(float)
    df["H4GH5F"] = rng.integers(4, 8, size=n).astype(float)
    df["H4GH5I"] = rng.integers(0, 12, size=n).astype(float)
    # Row 1 all-NaN cog
    for c in ["C4WD90_1", "C4WD60_1", "C4NUMSCR"]:
        df.at[1, c] = np.nan
    # Row 2 one-component-only
    df.at[2, "C4WD90_1"] = 10.0
    df.at[2, "C4WD60_1"] = np.nan
    df.at[2, "C4NUMSCR"] = np.nan
    # Row 3: H4GH5F=5, H4GH5I=6 -> 66
    df.at[3, "H4GH5F"] = 5.0
    df.at[3, "H4GH5I"] = 6.0
    # Row 4: feet ok, inches NaN
    df.at[4, "H4GH5F"] = 6.0
    df.at[4, "H4GH5I"] = np.nan
    # Row 5: both NaN
    df.at[5, "H4GH5F"] = np.nan
    df.at[5, "H4GH5I"] = np.nan
    return df


@pytest.fixture
def synthetic_w5_df() -> pd.DataFrame:
    """Hand-constructed 30-row W5-shaped frame for BDS / W5 cognitive tests.

    Columns:
      - H5MH3A..H5MH9B: BDS items (per-trial 0/1 valid)
      - C5WD90_1, C5WD60_1: W5 word recall (0-15)
      - MODE: W5 administration mode (I/T eligible for cognitive)
    """
    rng = np.random.default_rng(20260425)
    n = 30
    df = pd.DataFrame({"AID": [f"A{i:04d}" for i in range(n)]})
    for L in range(3, 10):
        for s in "AB":
            df[f"H5MH{L}{s}"] = rng.integers(0, 2, size=n).astype(float)
    df["C5WD90_1"] = rng.integers(0, 16, size=n).astype(float)
    df["C5WD60_1"] = rng.integers(0, 16, size=n).astype(float)
    df["MODE"] = ["I"] * 15 + ["T"] * 10 + ["W"] * 5
    return df


@pytest.fixture
def mock_weights() -> np.ndarray:
    """50 sampling weights — 1.0 with a few outliers for variance."""
    w = np.ones(50, dtype=float)
    w[:5] = 2.5
    w[-5:] = 0.5
    return w


@pytest.fixture
def mock_psu() -> np.ndarray:
    """50 PSU labels across 5 clusters of 10 each."""
    return np.repeat(np.arange(5), 10)

"""Meta-test for the ``analysis`` package path constants.

ROOT, DATA, CACHE are exposed at package level. They must resolve to existing
directories on disk; if they don't, every downstream import that uses them
will fail in a confusing way.
"""
from __future__ import annotations

from pathlib import Path

from analysis import CACHE, DATA, ROOT


def test_root_is_repo_root():
    """ROOT.parent.parent should match the package's grandparent."""
    assert ROOT.exists()
    assert ROOT.is_dir()
    # Sentinel files at repo root that should always exist
    assert (ROOT / "scripts").is_dir()
    assert (ROOT / "experiments").is_dir()


def test_data_path_is_under_root():
    assert DATA == ROOT / "data"


def test_cache_path_is_under_root():
    assert CACHE == ROOT / "cache"


def test_root_data_cache_are_pathlib():
    assert isinstance(ROOT, Path)
    assert isinstance(DATA, Path)
    assert isinstance(CACHE, Path)

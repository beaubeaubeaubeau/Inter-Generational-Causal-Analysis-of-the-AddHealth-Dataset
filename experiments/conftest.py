"""Conftest for experiment-level smoke tests.

Each experiment's ``tests/test_smoke.py`` does ``sys.path.insert(0, EXP_DIR)``
and then ``import run`` (and ``import figures``). When pytest collects across
multiple experiments in one bulk run, two collisions arise:

1. **Module-name collision in ``sys.modules``.** ``run`` and ``figures`` are
   bare module names; once one experiment's ``run.py`` is imported it caches
   under ``sys.modules['run']`` and subsequent ``import run`` calls in other
   experiments return the cached (wrong) module.
2. **``sys.path`` ordering collision.** Each test file's module-level
   ``sys.path.insert(0, EXP_DIR)`` runs at collection time. After all test
   files collect, ``sys.path[0]`` holds whichever ``EXP_DIR`` was inserted
   last — so every test's ``import run`` finds *that* experiment's run.py.

This conftest fixes both via an ``autouse`` fixture that:
  - pops cached ``run`` / ``figures`` from ``sys.modules`` before each test;
  - inserts the *current test's own* ``EXP_DIR`` at ``sys.path[0]`` for the
    duration of the test (via ``monkeypatch.syspath_prepend``);
  - cleans up after.

Per-folder runs (``pytest experiments/<name>/tests/``) work fine without
this fixture; it only matters during bulk collection.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest


_EXPERIMENT_LOCAL_MODULES = ("run", "figures")


@pytest.fixture(autouse=True)
def _reset_experiment_local_imports(request, monkeypatch):
    """Pop cached ``run`` / ``figures`` and prepend the current test's
    own ``EXP_DIR`` to ``sys.path``.
    """
    # Compute the test's own EXP_DIR: experiments/<name>/tests/test_smoke.py
    # -> EXP_DIR = experiments/<name>
    test_file = Path(request.fspath)
    exp_dir = test_file.parent.parent
    monkeypatch.syspath_prepend(str(exp_dir))

    for name in _EXPERIMENT_LOCAL_MODULES:
        sys.modules.pop(name, None)
    yield
    for name in _EXPERIMENT_LOCAL_MODULES:
        sys.modules.pop(name, None)

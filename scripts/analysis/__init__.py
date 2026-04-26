"""Shared analysis library for the Add Health inter-generational causal project.

Submodules:
  - cleaning:        ``VALID_RANGES``, ``clean_var``, ``neg_control_outcome``
  - data_loading:    ``load_outcome``, ``load_w1_*``, ``load_w4_*``, ``load_w5*``
  - derivation:      ``derive_*`` functions and CES-D / friendship-grid constants
  - wls:             ``weighted_ols``, ``quintile_dummies``
  - weighted_stats:  ``weighted_mean_se``, ``weighted_prop_ci``
  - plot_style:      shared matplotlib/seaborn setup + ``GROUP_COLORS``
  - diagnostics:     (stub) D1-D9 screening diagnostics; populated in Phase 2
  - ipw:             (stub) IPAW / inverse-probability-of-attrition weighting
  - frontdoor:       (stub) three-equation front-door decomposition
  - sensitivity:     (stub) E-value, placebo permutation, leave-one-out, balance

Path constants (``ROOT``, ``DATA``, ``CACHE``) are re-exported from this package
so existing consumers can keep importing them with a single line. We chose this
approach because all 23 task scripts already import ``ROOT`` and ``CACHE`` from
``analysis_utils``; re-exporting them here is the smallest delta. Consumers may
write either of:

    from analysis import ROOT, CACHE
    from analysis.cleaning import clean_var

or, equivalently:

    from analysis.cleaning import clean_var
    from analysis import ROOT, CACHE
"""
from __future__ import annotations

from pathlib import Path

# Repo root = parent of `scripts/`. This module lives at scripts/analysis/__init__.py,
# so .parent.parent.parent climbs analysis/ -> scripts/ -> repo root.
ROOT = Path(__file__).resolve().parent.parent.parent
DATA = ROOT / "data"
CACHE = ROOT / "cache"

__all__ = ["ROOT", "DATA", "CACHE"]

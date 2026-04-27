"""Tests for ``analysis.sensitivity``.

Covers three planned helpers (currently un-implemented; module raises
``NotImplementedError`` on import, so these tests fail by design under TDD):

  - ``evalue(rr)``           VanderWeele E-value, RR scale, with the protective
                             transform ``1/rr`` for rr < 1.
  - ``cornfield_bound(rr_au, rr_uy)``
                             Bias factor ``B = (RR_AU * RR_UY) / (RR_AU + RR_UY - 1)``
                             from Ch. 6 Theorem 2.1 (Hernan & Robins-style).
  - ``eta_tilt(eta_1, eta_0, mu_1, mu_0, A)``
                             Sensitivity-tilted ATE from reading.tex line 1331:
                             ``(1/n) * sum_i [A_i*mu_1 + (1-A_i)*mu_1/eta_1
                                             - A_i*mu_0*eta_0 - (1-A_i)*mu_0]``
                             which collapses to the plain ATE when
                             ``eta_1 = eta_0 = 1`` (Remark 6).

The import is performed inside each test so the file at least *collects*
even while the module is a NotImplementedError stub.
"""
from __future__ import annotations

import math

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# evalue
# ---------------------------------------------------------------------------

def test_evalue_null_effect_returns_one():
    """rr = 1 -> E-value = 1 (null effect needs no unmeasured confounding)."""
    from analysis.sensitivity import evalue
    assert evalue(1.0) == pytest.approx(1.0, abs=1e-12)


def test_evalue_rr_two_matches_formula():
    """rr = 2 -> evalue = 2 + sqrt(2 * 1) = 2 + sqrt(2) ~ 3.4142136."""
    from analysis.sensitivity import evalue
    expected = 2.0 + math.sqrt(2.0)  # ~3.41421356
    assert evalue(2.0) == pytest.approx(expected, abs=1e-5)


def test_evalue_protective_rr_transforms_via_reciprocal():
    """rr = 0.5 -> evalue should equal evalue(1/0.5) = evalue(2.0).

    Per VanderWeele & Ding (2017), protective effects (rr<1) are flipped
    to 1/rr before applying the formula.
    """
    from analysis.sensitivity import evalue
    assert evalue(0.5) == pytest.approx(evalue(2.0), abs=1e-12)


def test_evalue_nonpositive_rr_raises():
    """rr <= 0 is undefined for the E-value formula -> ValueError."""
    from analysis.sensitivity import evalue
    with pytest.raises(ValueError):
        evalue(0.0)
    with pytest.raises(ValueError):
        evalue(-1.5)


# ---------------------------------------------------------------------------
# cornfield_bound
# ---------------------------------------------------------------------------

def test_cornfield_bound_symmetric_case():
    """rr_au = rr_uy = 2 -> B = (2*2) / (2+2-1) = 4/3."""
    from analysis.sensitivity import cornfield_bound
    assert cornfield_bound(2.0, 2.0) == pytest.approx(4.0 / 3.0, abs=1e-12)


def test_cornfield_bound_one_arg_unity_collapses_to_one():
    """When either RR = 1, the bias factor must equal 1 (no confounding).

    rr_au=1, rr_uy=5 -> (1*5) / (1+5-1) = 5/5 = 1.
    """
    from analysis.sensitivity import cornfield_bound
    assert cornfield_bound(1.0, 5.0) == pytest.approx(1.0, abs=1e-12)
    assert cornfield_bound(5.0, 1.0) == pytest.approx(1.0, abs=1e-12)


def test_cornfield_bound_arg_below_one_raises():
    """RR < 1 inputs are not allowed by the bound's domain -> ValueError."""
    from analysis.sensitivity import cornfield_bound
    with pytest.raises(ValueError):
        cornfield_bound(0.5, 2.0)
    with pytest.raises(ValueError):
        cornfield_bound(2.0, 0.9)


# ---------------------------------------------------------------------------
# eta_tilt
# ---------------------------------------------------------------------------

def test_eta_tilt_identity_etas_recovers_plain_ate():
    """With eta_1 = eta_0 = 1 everywhere and a constant treatment effect of
    0.5, the tilted estimator collapses to the plain ATE = 0.5 (Remark 6).
    """
    from analysis.sensitivity import eta_tilt
    rng = np.random.default_rng(2026)
    n = 200
    A = rng.integers(0, 2, size=n).astype(float)
    mu_0 = rng.normal(loc=1.0, scale=0.5, size=n)
    mu_1 = mu_0 + 0.5  # constant treatment effect of 0.5
    eta_1 = np.ones(n)
    eta_0 = np.ones(n)
    est = eta_tilt(eta_1, eta_0, mu_1, mu_0, A)
    assert est == pytest.approx(0.5, abs=1e-10)


def test_eta_tilt_eta1_above_one_biases_estimate_downward():
    """With eta_1 > 1 (treated outcome model under-estimates among controls),
    the (1-A) * mu_1 / eta_1 term shrinks, pulling the ATE estimate *down*
    relative to the eta=1 baseline. Hand-checked sign of the perturbation.
    """
    from analysis.sensitivity import eta_tilt
    rng = np.random.default_rng(7)
    n = 200
    A = rng.integers(0, 2, size=n).astype(float)
    mu_0 = rng.normal(loc=1.0, scale=0.5, size=n)
    mu_1 = mu_0 + 0.5
    baseline = eta_tilt(np.ones(n), np.ones(n), mu_1, mu_0, A)
    tilted = eta_tilt(np.full(n, 1.5), np.ones(n), mu_1, mu_0, A)
    assert tilted < baseline


def test_eta_tilt_known_synthetic_truth():
    """Hand-computed reference: n=4, all-treated and all-control mix.

    A      = [1, 1, 0, 0]
    mu_1   = [2, 2, 2, 2]
    mu_0   = [1, 1, 1, 1]
    eta_1  = [2, 2, 2, 2]   (so mu_1/eta_1 = 1 for the (1-A) terms)
    eta_0  = [0.5, 0.5, 0.5, 0.5]   (so mu_0*eta_0 = 0.5 for the A terms)

    Per i, the contribution is:
      i=0 (A=1): A*mu_1 + 0          - A*mu_0*eta_0 - 0           = 2 - 0.5 = 1.5
      i=1 (A=1): same                                               = 1.5
      i=2 (A=0): 0 + (1-A)*mu_1/eta_1 - 0           - (1-A)*mu_0   = 1 - 1   = 0.0
      i=3 (A=0): same                                               = 0.0

    Mean = (1.5 + 1.5 + 0 + 0) / 4 = 0.75.
    """
    from analysis.sensitivity import eta_tilt
    A = np.array([1.0, 1.0, 0.0, 0.0])
    mu_1 = np.array([2.0, 2.0, 2.0, 2.0])
    mu_0 = np.array([1.0, 1.0, 1.0, 1.0])
    eta_1 = np.array([2.0, 2.0, 2.0, 2.0])
    eta_0 = np.array([0.5, 0.5, 0.5, 0.5])
    est = eta_tilt(eta_1, eta_0, mu_1, mu_0, A)
    assert est == pytest.approx(0.75, abs=1e-12)

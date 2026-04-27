"""Sensitivity-analysis primitives for unmeasured-confounding bounds.

Three pure-numpy helpers (see ``reference/methods.md`` §"Sensitivity"
forthcoming for the prose write-up and citations):

  - ``evalue(rr)``
        VanderWeele & Ding (2017) E-value on the risk-ratio scale.
        For ``rr >= 1``: ``rr + sqrt(rr * (rr - 1))``. Protective effects
        (``0 < rr < 1``) are mapped through the reciprocal (``1/rr``) before
        applying the same formula. ``rr <= 0`` raises ``ValueError``.

  - ``cornfield_bound(rr_au, rr_uy)``
        Bias factor ``B = (RR_AU * RR_UY) / (RR_AU + RR_UY - 1)`` from
        Ch. 6 Theorem 2.1. Both arguments must be ``>= 1`` (the bound's
        relabeling preamble assumes the larger arm of each RR is on top);
        sub-unity inputs raise ``ValueError``.

  - ``eta_tilt(eta_1, eta_0, mu_1, mu_0, A)``
        η-tilt sensitivity ATE estimator (Ch. 6 §3, reading.tex line 1331):

            (1/n) * Σ_i  [ A_i * mu_1_i + (1 - A_i) * mu_1_i / eta_1_i
                         - A_i * mu_0_i * eta_0_i - (1 - A_i) * mu_0_i ]

        Collapses to ``mean(mu_1) - mean(mu_0)`` when ``eta_1 ≡ eta_0 ≡ 1``
        (Remark 6). ``A`` is documented as 0/1 binary but is NOT validated;
        callers passing continuous ``A`` get the natural broadcast.
"""
from __future__ import annotations

import math

import numpy as np

__all__ = ["evalue", "cornfield_bound", "eta_tilt"]


def evalue(rr: float) -> float:
    """VanderWeele-Ding E-value on the risk-ratio scale.

    For ``rr >= 1``: ``rr + sqrt(rr * (rr - 1))``.
    For ``0 < rr < 1``: apply the formula to ``1/rr`` (protective transform).
    For ``rr <= 0``: raise ``ValueError``.
    """
    if rr <= 0:
        raise ValueError(f"evalue requires rr > 0; got {rr!r}")
    r = 1.0 / rr if rr < 1.0 else float(rr)
    return r + math.sqrt(r * (r - 1.0))


def cornfield_bound(rr_au: float, rr_uy: float) -> float:
    """Bias factor B from Ch. 6 Theorem 2.1.

    ``B = (rr_au * rr_uy) / (rr_au + rr_uy - 1)``. Both inputs must be
    ``>= 1``; sub-unity inputs raise ``ValueError`` because the bound's
    relabeling preamble (larger arm of each RR on top) is then violated.
    """
    if rr_au < 1.0 or rr_uy < 1.0:
        raise ValueError(
            f"cornfield_bound requires rr_au >= 1 and rr_uy >= 1; "
            f"got rr_au={rr_au!r}, rr_uy={rr_uy!r}"
        )
    return (rr_au * rr_uy) / (rr_au + rr_uy - 1.0)


def eta_tilt(
    eta_1: np.ndarray,
    eta_0: np.ndarray,
    mu_1: np.ndarray,
    mu_0: np.ndarray,
    A: np.ndarray,
) -> float:
    """η-tilt sensitivity ATE estimator (Ch. 6 §3).

    Per-i contribution::

        A_i * mu_1_i + (1 - A_i) * mu_1_i / eta_1_i
            - A_i * mu_0_i * eta_0_i - (1 - A_i) * mu_0_i

    Returned value is the sample mean of those contributions. Inputs are
    cast to ``np.ndarray`` of dtype float; ``A`` is documented as 0/1 but
    is not validated (continuous-A use is left to the caller's discretion).
    """
    eta_1 = np.asarray(eta_1, dtype=float)
    eta_0 = np.asarray(eta_0, dtype=float)
    mu_1 = np.asarray(mu_1, dtype=float)
    mu_0 = np.asarray(mu_0, dtype=float)
    A = np.asarray(A, dtype=float)
    contrib = (
        A * mu_1
        + (1.0 - A) * mu_1 / eta_1
        - A * mu_0 * eta_0
        - (1.0 - A) * mu_0
    )
    return float(np.mean(contrib))

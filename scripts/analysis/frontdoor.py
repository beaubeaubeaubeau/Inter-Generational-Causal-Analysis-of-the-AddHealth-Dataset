"""Three-equation front-door decomposition (Pearl 2009 §3.3.2).

The front-door criterion identifies the X → Y causal effect through a
fully-mediating M when back-door adjustment fails (because of unmeasured
X ↔ Y confounding). It requires:

1. X → M → Y with no direct X → Y arrow.
2. All of the X → Y effect passes through M.
3. No unmeasured M ↔ Y confounders.

Implementation (Pearl's three-step formula for the linear-Gaussian /
linear-additive case):

  E[Y | do(X = x)] = Σ_m P(M = m | X = x) · Σ_x' E[Y | M = m, X = x'] · P(X = x')

For continuous X, M, Y under linearity this collapses to:

  total_effect = β_X→M × β_M→Y(adjusted for X)

We estimate two regressions:

  1. M | X model: ``M ~ X + X_to_M_adj`` → β_X→M from the X coefficient.
  2. Y | M, X model: ``Y ~ M + X + MY_adj`` → β_M→Y(|X) from the M coefficient.

The product β_X→M × β_M→Y is the front-door estimate of the total causal
effect of X on Y.

In this project: applied to the AHPVT mediator path inside
``cognitive-frontdoor`` as a sensitivity bound on the trajectory β —
see ``methods.md §3 Front-door decomposition (three-equation)``.
"""
from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd

__all__ = ["frontdoor_decompose"]


def _ols(y: np.ndarray, X: np.ndarray):
    """Plain OLS via numpy.lstsq; returns (beta, residual_var, n)."""
    n = X.shape[0]
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ beta
    if n > X.shape[1]:
        rss = float(np.sum(resid ** 2))
        sigma2 = rss / (n - X.shape[1])
    else:
        sigma2 = float("nan")
    return beta, sigma2, n


def frontdoor_decompose(
    X: np.ndarray,
    M: np.ndarray,
    Y: np.ndarray,
    X_to_M_adj: Optional[np.ndarray] = None,
    MY_adj: Optional[np.ndarray] = None,
):
    """Three-step front-door decomposition for linear-Gaussian models.

    Parameters
    ----------
    X : 1-D array (n,)
        Treatment / exposure.
    M : 1-D array (n,)
        Mediator (the "front-door" variable).
    Y : 1-D array (n,)
        Outcome.
    X_to_M_adj : 2-D array (n × p1) or None
        Front-door confounders to adjust for in the M | X regression.
        Should NOT include X (it's added internally).
    MY_adj : 2-D array (n × p2) or None
        Confounders to adjust for in the Y | M, X regression. **Should
        include X** (Pearl's formula conditions on X' separately when
        averaging) — typically users pass [X, additional covariates].

    Returns
    -------
    dict
        Keys: total_effect (= β_X→M × β_M→Y(|X)), beta_xm, beta_my, n.
    """
    X = np.asarray(X, dtype=float).ravel()
    M = np.asarray(M, dtype=float).ravel()
    Y = np.asarray(Y, dtype=float).ravel()
    n = len(X)
    if X_to_M_adj is None:
        X_to_M_adj = np.zeros((n, 0))
    else:
        X_to_M_adj = np.asarray(X_to_M_adj, dtype=float)
        if X_to_M_adj.ndim == 1:
            X_to_M_adj = X_to_M_adj.reshape(-1, 1)
    if MY_adj is None:
        MY_adj = np.zeros((n, 0))
    else:
        MY_adj = np.asarray(MY_adj, dtype=float)
        if MY_adj.ndim == 1:
            MY_adj = MY_adj.reshape(-1, 1)

    # Drop rows with any NaN.
    mat = np.column_stack([X, M, Y, X_to_M_adj, MY_adj])
    mask = ~np.isnan(mat).any(axis=1)
    X = X[mask]; M = M[mask]; Y = Y[mask]
    X_to_M_adj = X_to_M_adj[mask]
    MY_adj = MY_adj[mask]
    n_eff = len(X)
    if n_eff < 5:
        return {"total_effect": float("nan"), "beta_xm": float("nan"),
                "beta_my": float("nan"), "n": int(n_eff)}

    # Step 1: M ~ const + X + X_to_M_adj. β_X→M = coefficient on X (index 1).
    DM = np.column_stack([np.ones(n_eff), X, X_to_M_adj])
    beta_m, _, _ = _ols(M, DM)
    beta_xm = float(beta_m[1])

    # Step 2: Y ~ const + M + MY_adj. β_M→Y = coefficient on M (index 1).
    # Pearl's formula conditions on X' (which is in MY_adj per the docstring).
    DY = np.column_stack([np.ones(n_eff), M, MY_adj])
    beta_y, _, _ = _ols(Y, DY)
    beta_my = float(beta_y[1])

    total = beta_xm * beta_my
    return {
        "total_effect": total,
        "beta_xm": beta_xm,
        "beta_my": beta_my,
        "n": int(n_eff),
    }

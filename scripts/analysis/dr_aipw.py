"""Doubly-robust Augmented IPW (DR-AIPW) ATE estimator with cross-fitting.

Implements the Robins-Rotnitzky-Zhao (1994) augmented IPW doubly-robust
estimator with K-fold cross-fitting for the nuisance functions. The
estimator is consistent if *either* the propensity model or the outcome
regression is correctly specified.

For each unit i with observed treatment ``A_i`` and outcome ``Y_i``, given
out-of-fold predictions ``p_hat_i = P(A=1 | X_i)``, ``mu_1_hat_i = E[Y | A=1, X_i]``,
``mu_0_hat_i = E[Y | A=0, X_i]``, the DR-AIPW influence function is::

    phi_i = mu_1_hat_i - mu_0_hat_i
            + (A_i / p_hat_i) * (Y_i - mu_1_hat_i)
            - ((1 - A_i) / (1 - p_hat_i)) * (Y_i - mu_0_hat_i)

with point estimate ``ATE = mean(phi)`` and variance ``Var(ATE) = var(phi) / n``.
"""
from __future__ import annotations

from typing import Callable, Optional

import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.model_selection import KFold


__all__ = ["dr_aipw"]


def dr_aipw(
    Y: np.ndarray,
    A: np.ndarray,
    X: np.ndarray,
    prop_fn: Optional[Callable] = None,
    out_fn: Optional[Callable] = None,
    n_splits: int = 2,
    random_state: int = 0,
) -> dict:
    """Cross-fit DR-AIPW estimator of the average treatment effect (ATE).

    Parameters
    ----------
    Y : (n,) float array
        Continuous outcome.
    A : (n,) {0, 1} array
        Binary treatment indicator.
    X : (n, p) float array
        Pre-treatment covariates used by both nuisance models.
    prop_fn : callable, optional
        ``(X_train, A_train) -> fitted_model`` exposing
        ``.predict_proba(X_test)`` whose second column is ``P(A=1 | X)``.
        Defaults to a fresh ``LogisticRegression(max_iter=1000)`` fitted on
        ``(X_train, A_train)`` per fold.
    out_fn : callable, optional
        ``(X_train, Y_train) -> fitted_model`` exposing ``.predict(X_test)``.
        Used twice per fold (once on the A=1 training subset, once on the
        A=0 training subset). Defaults to a fresh ``LinearRegression()``
        fitted on ``(X_train, Y_train)``.
    n_splits : int, default 2
        Number of cross-fitting folds.
    random_state : int, default 0
        Seed for the ``KFold`` shuffle.

    Returns
    -------
    dict
        ``{"ate", "se", "ci_lo", "ci_hi", "n", "n_treated", "n_control"}``
        with normal-approximation 95% CI ``ate ± 1.96 * se``.
    """
    Y = np.asarray(Y, dtype=float)
    A = np.asarray(A, dtype=float)
    X = np.asarray(X, dtype=float)
    n = len(Y)

    if prop_fn is None:
        def prop_fn(X_train, A_train):
            return LogisticRegression(max_iter=1000).fit(X_train, A_train)
    if out_fn is None:
        def out_fn(X_train, Y_train):
            return LinearRegression().fit(X_train, Y_train)

    p_hat = np.empty(n, dtype=float)
    mu1_hat = np.empty(n, dtype=float)
    mu0_hat = np.empty(n, dtype=float)

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=random_state)
    for train_idx, test_idx in kf.split(X):
        X_tr, A_tr, Y_tr = X[train_idx], A[train_idx], Y[train_idx]
        X_te = X[test_idx]

        # Propensity model — fit on full training subset of this fold.
        prop_model = prop_fn(X_tr, A_tr)
        p_te = prop_model.predict_proba(X_te)[:, 1]
        p_hat[test_idx] = np.clip(p_te, 1e-3, 1.0 - 1e-3)

        # Outcome model on A==1 training subset; fall back to marginal mean
        # if the subset is empty (cannot fit a regressor with zero rows).
        treated_mask = A_tr == 1
        if treated_mask.any():
            out_model_1 = out_fn(X_tr[treated_mask], Y_tr[treated_mask])
            mu1_hat[test_idx] = out_model_1.predict(X_te)
        else:
            mu1_hat[test_idx] = float(Y_tr.mean()) if len(Y_tr) else 0.0

        control_mask = A_tr == 0
        if control_mask.any():
            out_model_0 = out_fn(X_tr[control_mask], Y_tr[control_mask])
            mu0_hat[test_idx] = out_model_0.predict(X_te)
        else:
            mu0_hat[test_idx] = float(Y_tr.mean()) if len(Y_tr) else 0.0

    # AIPW influence function (per unit).
    phi = (
        mu1_hat - mu0_hat
        + (A / p_hat) * (Y - mu1_hat)
        - ((1.0 - A) / (1.0 - p_hat)) * (Y - mu0_hat)
    )

    ate = float(np.mean(phi))
    var = float(np.var(phi, ddof=1)) / n
    se = float(np.sqrt(var))
    ci_lo = ate - 1.96 * se
    ci_hi = ate + 1.96 * se

    return {
        "ate": ate,
        "se": se,
        "ci_lo": float(ci_lo),
        "ci_hi": float(ci_hi),
        "n": int(n),
        "n_treated": int((A == 1).sum()),
        "n_control": int((A == 0).sum()),
    }

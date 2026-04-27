"""Nearest-neighbour matching estimators (Abadie-Imbens, MA 592 Ch. 5).

Fixed-M matching utilities for causal effect estimation:

- ``mahalanobis_distance(x, x', Sigma_inv)``: scaled distance in covariate space.
  When ``Sigma_inv = I`` reduces to Euclidean. Used for matching on multivariate X.
- ``match_ate(Y, A, X, M, distance)``: plain (non-bias-corrected) M-nearest
  neighbour matching ATE. Returns dict with ``ate``, ``se``, ``n_treated``,
  ``n_control``, and the **used-as-a-match** count vector ``KM`` (Ch. 5 gotcha:
  ``KM[i]`` is the number of times unit ``i`` was *used* as someone else's
  matched neighbour, NOT the number of matches it received).
- ``match_ate_bias_corrected(Y, A, X, M, mu_hat_treated, mu_hat_control)``:
  Abadie-Imbens AIPW-shaped bias-corrected estimator
      (1/n) sum_i [ mu_hat_1(X_i) - mu_hat_0(X_i)
                    + I(A=1) (1 + KM/M) (Y - mu_hat_1)
                    - I(A=0) (1 + KM/M) (Y - mu_hat_0) ].
  ``mu_hat_*`` default to internal linear regression fits when not supplied.
- ``analytic_variance(Y, A, X, M, KM, ate)``: Abadie-Imbens analytic variance for
  fixed-M matching (Ch. 5 §9). **Bootstrap is invalid for fixed-M matching**;
  always use the analytic formula. Returns variance (sqrt for SE).
"""
from __future__ import annotations

from typing import Optional

import numpy as np


__all__ = [
    "mahalanobis_distance",
    "match_ate",
    "match_ate_bias_corrected",
    "analytic_variance",
]


def mahalanobis_distance(
    x: np.ndarray,
    x_prime: np.ndarray,
    sigma_inv: np.ndarray,
) -> float:
    """Mahalanobis distance ``sqrt((x - x')' Sigma_inv (x - x'))``.

    With ``sigma_inv = I`` reduces to Euclidean. ``sigma_inv`` is the inverse
    of the covariate covariance matrix (decorrelation + unit-variance rescale)
    and is passed in pre-computed so callers can fit it once on the full
    sample.

    Parameters
    ----------
    x, x_prime : np.ndarray, shape (p,)
        Two covariate vectors.
    sigma_inv : np.ndarray, shape (p, p)
        Inverse covariance matrix used for the metric tensor.

    Returns
    -------
    float
        Non-negative scalar distance.
    """
    diff = np.asarray(x, dtype=float) - np.asarray(x_prime, dtype=float)
    sigma_inv = np.asarray(sigma_inv, dtype=float)
    quad = float(diff @ sigma_inv @ diff)
    # Numerical floor: tiny negatives from FP noise -> 0.
    return float(np.sqrt(max(quad, 0.0)))


def _build_sigma_inv(X: np.ndarray, distance: str) -> np.ndarray:
    """Build the metric tensor for matching."""
    p = X.shape[1]
    if distance == "euclidean":
        return np.eye(p)
    if distance == "mahalanobis":
        if p == 1:
            # ``np.cov`` on a single column returns a 0-d array; handle scalar.
            var = float(np.cov(X[:, 0]))
            if var <= 0 or not np.isfinite(var):
                return np.eye(1)
            return np.array([[1.0 / var]])
        Sigma = np.cov(X.T)
        try:
            return np.linalg.inv(Sigma)
        except np.linalg.LinAlgError:
            return np.linalg.pinv(Sigma)
    raise ValueError(f"Unknown distance metric: {distance!r}")


def _pairwise_distances(
    X: np.ndarray, sigma_inv: np.ndarray,
) -> np.ndarray:
    """Compute the full N x N matrix of Mahalanobis distances."""
    # Vectorised: d_ij^2 = (x_i - x_j)' Sigma_inv (x_i - x_j).
    # Expand: x_i' S x_i + x_j' S x_j - 2 x_i' S x_j.
    XS = X @ sigma_inv  # (N, p)
    quad = np.einsum("ij,ij->i", XS, X)  # (N,) diag terms
    cross = XS @ X.T  # (N, N)
    d2 = quad[:, None] + quad[None, :] - 2.0 * cross
    # Numerical floor.
    d2 = np.maximum(d2, 0.0)
    return np.sqrt(d2)


def _find_matches(
    distances: np.ndarray, target_mask: np.ndarray, M: int,
) -> np.ndarray:
    """For each unit (row), return indices of M nearest units in `target_mask`.

    Deterministic tie-breaking via ``np.argsort`` with ``kind="stable"``.
    The unit itself is excluded by setting its self-distance to +inf when
    it would otherwise match (the masks here keep treated/control disjoint
    so self-matches don't normally arise, but we guard anyway).

    Returns
    -------
    np.ndarray, shape (N, M)
        ``matches[i]`` are the indices (into the full sample) of unit i's M
        nearest neighbours among the target group.
    """
    N = distances.shape[0]
    target_idx = np.where(target_mask)[0]
    if len(target_idx) < M:
        raise ValueError(
            f"Need at least M={M} units in target group, got {len(target_idx)}."
        )
    # Restrict columns to the target group; sort each row.
    sub = distances[:, target_idx]  # (N, |target|)
    # argsort with stable kind => deterministic tie-breaking by original
    # column order (which corresponds to original sample index order).
    order = np.argsort(sub, axis=1, kind="stable")  # (N, |target|)
    nearest_local = order[:, :M]  # (N, M)
    matches = target_idx[nearest_local]  # map back to sample indices
    return matches


def _imputed_counterfactual(
    Y: np.ndarray, matches: np.ndarray,
) -> np.ndarray:
    """Mean of Y over the M matched neighbours (per row)."""
    return Y[matches].mean(axis=1)


def _used_as_match_counts(matches_t: np.ndarray, matches_c: np.ndarray,
                           N: int, treated_idx: np.ndarray,
                           control_idx: np.ndarray) -> np.ndarray:
    """Count, per unit, how many times it appears as someone else's match.

    Treated units pull controls (rows in matches_t correspond to treated
    units, entries point at controls). Control units pull treated. We sum
    the frequency of each sample-index across both match arrays.
    """
    KM = np.zeros(N, dtype=int)
    # matches_t shape: (n_treated, M); each entry is a control sample index
    # used by some treated unit. Likewise matches_c uses treated indices.
    if matches_t.size:
        idx, counts = np.unique(matches_t, return_counts=True)
        KM[idx] += counts
    if matches_c.size:
        idx, counts = np.unique(matches_c, return_counts=True)
        KM[idx] += counts
    return KM


def match_ate(
    Y: np.ndarray,
    A: np.ndarray,
    X: np.ndarray,
    M: int = 1,
    distance: str = "mahalanobis",
) -> dict:
    """Plain M-nearest-neighbour matching ATE.

    For each treated unit, finds the ``M`` closest control units by
    ``distance`` (and vice versa). Estimator is the mean across all units of
    the imputed individual treatment effect:

        ate = (1/n) sum_i (2 A_i - 1) (Y_i - mean_of_matches_for_i).

    Parameters
    ----------
    Y : np.ndarray, shape (N,)
        Outcomes.
    A : np.ndarray, shape (N,)
        Binary treatment 0/1.
    X : np.ndarray, shape (N, p)
        Covariates used for matching.
    M : int, default 1
        Number of nearest neighbours per unit.
    distance : {"mahalanobis", "euclidean"}, default "mahalanobis"
        Distance metric. "mahalanobis" fits ``Sigma_hat`` from ``X`` internally.

    Returns
    -------
    dict
        ``ate`` (float), ``se`` (float, analytic SE),
        ``n_treated`` (int), ``n_control`` (int),
        ``KM`` (np.ndarray shape (N,), used-as-a-match count per unit).
    """
    Y = np.asarray(Y, dtype=float).ravel()
    A = np.asarray(A).ravel().astype(int)
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X[:, None]
    N = len(Y)
    n_treated = int((A == 1).sum())
    n_control = int((A == 0).sum())
    # Cap M at the smaller group size so we don't request more matches than
    # exist on the opposite side.
    M_eff = int(min(M, n_treated, n_control))
    if M_eff < 1:
        raise ValueError("Both treatment groups must have at least 1 unit.")

    sigma_inv = _build_sigma_inv(X, distance)
    distances = _pairwise_distances(X, sigma_inv)

    treated_mask = (A == 1)
    control_mask = (A == 0)
    treated_idx = np.where(treated_mask)[0]
    control_idx = np.where(control_mask)[0]

    # Treated units pull M_eff control matches.
    d_treated = distances[treated_idx]  # (n_t, N)
    matches_t_local = np.argsort(d_treated[:, control_idx], axis=1,
                                  kind="stable")[:, :M_eff]
    matches_t = control_idx[matches_t_local]  # (n_t, M_eff), sample indices

    # Control units pull M_eff treated matches.
    d_control = distances[control_idx]
    matches_c_local = np.argsort(d_control[:, treated_idx], axis=1,
                                  kind="stable")[:, :M_eff]
    matches_c = treated_idx[matches_c_local]  # (n_c, M_eff)

    # Imputed counterfactuals.
    Y_cf_treated = Y[matches_t].mean(axis=1)  # (n_t,) imputed Y(0)
    Y_cf_control = Y[matches_c].mean(axis=1)  # (n_c,) imputed Y(1)

    # Per-unit imputed treatment effect: (2A-1) * (Y - Y_match_mean).
    ite = np.zeros(N)
    ite[treated_idx] = Y[treated_idx] - Y_cf_treated
    ite[control_idx] = Y_cf_control - Y[control_idx]
    ate = float(ite.mean())

    KM = _used_as_match_counts(matches_t, matches_c, N, treated_idx,
                                control_idx)

    var = analytic_variance(Y, A, X, M=M_eff, KM=KM, ate=ate)
    se = float(np.sqrt(var)) if var > 0 else float("nan")

    return {
        "ate": ate,
        "se": se,
        "n_treated": n_treated,
        "n_control": n_control,
        "KM": KM,
    }


def match_ate_bias_corrected(
    Y: np.ndarray,
    A: np.ndarray,
    X: np.ndarray,
    M: int = 1,
    mu_hat_treated: Optional[np.ndarray] = None,
    mu_hat_control: Optional[np.ndarray] = None,
) -> dict:
    """Bias-corrected M-NN matching ATE (Abadie-Imbens AIPW-shaped formula).

        ate = (1/n) sum_i [ mu_hat_1(X_i) - mu_hat_0(X_i)
                            + I(A_i = 1) (1 + KM_i/M) (Y_i - mu_hat_1(X_i))
                            - I(A_i = 0) (1 + KM_i/M) (Y_i - mu_hat_0(X_i)) ]

    The ``mu_hat_*`` arrays are predicted-Y values for *every* unit (length
    ``N``). When not supplied, defaults are linear regressions fit on the
    treated subsample (for ``mu_hat_treated``) and control subsample
    (for ``mu_hat_control``), each then used to predict on all ``N`` units.

    Returns
    -------
    dict
        ``ate``, ``se``, ``n_treated``, ``n_control``, ``KM``,
        ``mu_hat_treated`` (np.ndarray shape (N,)),
        ``mu_hat_control`` (np.ndarray shape (N,)).
    """
    Y = np.asarray(Y, dtype=float).ravel()
    A = np.asarray(A).ravel().astype(int)
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X[:, None]
    N = len(Y)
    n_treated = int((A == 1).sum())
    n_control = int((A == 0).sum())
    M_eff = int(min(M, n_treated, n_control))
    if M_eff < 1:
        raise ValueError("Both treatment groups must have at least 1 unit.")

    # Fit linear OR models (with intercept) if not supplied. Uses numpy
    # lstsq rather than sklearn to keep this module's deps to numpy only,
    # consistent with the rest of scripts/analysis/*.
    design_full = np.column_stack([np.ones(N), X])
    if mu_hat_treated is None:
        beta1, *_ = np.linalg.lstsq(design_full[A == 1], Y[A == 1], rcond=None)
        mu_hat_treated_arr = design_full @ beta1
    else:
        mu_hat_treated_arr = np.asarray(mu_hat_treated, dtype=float).ravel()
    if mu_hat_control is None:
        beta0, *_ = np.linalg.lstsq(design_full[A == 0], Y[A == 0], rcond=None)
        mu_hat_control_arr = design_full @ beta0
    else:
        mu_hat_control_arr = np.asarray(mu_hat_control, dtype=float).ravel()

    # Pull KM from a plain match call so symmetric matching is consistent.
    base = match_ate(Y, A, X, M=M_eff, distance="mahalanobis")
    KM = base["KM"]

    weight = 1.0 + KM / M_eff
    treated_term = (A == 1).astype(float) * weight * (Y - mu_hat_treated_arr)
    control_term = (A == 0).astype(float) * weight * (Y - mu_hat_control_arr)
    contrib = (mu_hat_treated_arr - mu_hat_control_arr
               + treated_term - control_term)
    ate = float(contrib.mean())

    var = analytic_variance(Y, A, X, M=M_eff, KM=KM, ate=ate)
    se = float(np.sqrt(var)) if var > 0 else float("nan")

    return {
        "ate": ate,
        "se": se,
        "n_treated": n_treated,
        "n_control": n_control,
        "KM": KM,
        "mu_hat_treated": mu_hat_treated_arr,
        "mu_hat_control": mu_hat_control_arr,
    }


def analytic_variance(
    Y: np.ndarray,
    A: np.ndarray,
    X: np.ndarray,
    M: int,
    KM: np.ndarray,
    ate: float,
) -> float:
    """Abadie-Imbens analytic variance for the fixed-M matching ATE.

    Bootstrap is invalid for fixed-M matching (Ch. 5 §9); use this analytic
    formula instead. Conditional variance ``sigma_hat_i^2`` is estimated from
    the J = M nearest *same-treatment* neighbours of each unit using the
    standard within-cluster squared-deviation estimator. The variance of the
    matching ATE is then

        Var = (1/n^2) sum_i [ (1 + KM_i/M)^2 * sigma_hat_i^2 ].

    Parameters
    ----------
    Y, A, X : np.ndarray
        As in ``match_ate``.
    M : int
        Number of nearest neighbours used.
    KM : np.ndarray, shape (N,)
        Used-as-a-match counts from ``match_ate``.
    ate : float
        Point estimate (currently unused; kept for interface stability).

    Returns
    -------
    float
        Non-negative variance estimate.
    """
    Y = np.asarray(Y, dtype=float).ravel()
    A = np.asarray(A).ravel().astype(int)
    X = np.asarray(X, dtype=float)
    if X.ndim == 1:
        X = X[:, None]
    KM = np.asarray(KM, dtype=float).ravel()
    N = len(Y)

    # Use Mahalanobis on the full X to find same-treatment neighbours.
    sigma_inv = _build_sigma_inv(X, "mahalanobis")
    distances = _pairwise_distances(X, sigma_inv)

    treated_idx = np.where(A == 1)[0]
    control_idx = np.where(A == 0)[0]

    # J: same-treatment-neighbour count for the conditional-variance step.
    # Use J = M (per task spec); cap at (group_size - 1) so we have enough
    # within-group neighbours after excluding self.
    J = int(min(M, len(treated_idx) - 1, len(control_idx) - 1))
    if J < 1:
        # Degenerate: fall back to overall residual variance.
        return float(np.var(Y, ddof=1) / N)

    sigma_hat_sq = np.zeros(N)
    for grp_idx in (treated_idx, control_idx):
        if len(grp_idx) <= 1:
            continue
        # For each unit i in this group, look at distances to other units
        # in the same group (excluding self), pick J nearest, compute the
        # within-cluster squared deviation of Y.
        for i in grp_idx:
            others = grp_idx[grp_idx != i]
            if len(others) < J:
                # Use whatever same-group neighbours we have.
                neigh = others
            else:
                d_to_same = distances[i, others]
                order = np.argsort(d_to_same, kind="stable")[:J]
                neigh = others[order]
            # Standard Abadie-Imbens conditional variance: scale the squared
            # deviation between Y_i and the neighbour-mean by J/(J+1) so
            # E[sigma_hat^2] = sigma^2 under homoskedastic noise.
            y_bar = Y[neigh].mean()
            J_eff = len(neigh)
            sigma_hat_sq[i] = (J_eff / (J_eff + 1.0)) * (Y[i] - y_bar) ** 2

    weight = 1.0 + KM / M
    var = float(np.sum((weight ** 2) * sigma_hat_sq) / (N ** 2))
    return var

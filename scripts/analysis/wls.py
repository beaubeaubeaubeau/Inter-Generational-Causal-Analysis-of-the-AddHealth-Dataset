"""Weighted ordinary least squares with cluster-robust variance + helpers.

``weighted_ols`` fits ``statsmodels.WLS`` with cluster-robust covariance on
``CLUSTER2`` (``use_correction=True``, ``use_t=True``). t-stats / CIs use
statsmodels' default ``df = n - k`` (decision 2026-04-26: trust the
package's built-in small-sample correction rather than mixing two
correction philosophies). Survey weights are normalised to mean 1 so that
``use_correction=True`` operates on the right ``σ̂²`` scale.

``quintile_dummies`` cuts a continuous series into ``n`` rank-equal bins and
returns ``(k-1 dummies, integer trend)``.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
import pandas as pd


def weighted_ols(
    y: np.ndarray, X: np.ndarray, w: np.ndarray, psu: np.ndarray,
    column_names: Optional[List[str]] = None,
):
    """Weighted OLS with cluster-robust variance on `psu`.

    Returns a dict with beta (pd.Series), se, t, p, ci_lo, ci_hi,
    n, n_psu, df_resid, rsquared, model. Uses statsmodels' WLS fit with
    weights, ``cov_type='cluster'``, ``use_correction=True``, and
    ``use_t=True``. t-stats / CIs come from statsmodels' default
    ``df = n - k`` (no manual H-1 override).

    X must include a constant column.
    """
    import statsmodels.api as sm

    y = np.asarray(y, dtype=float)
    X = np.asarray(X, dtype=float)
    w = np.asarray(w, dtype=float)
    psu = np.asarray(psu)
    # Drop NaN PSU rows: pandas groupby and statsmodels' cluster grouping
    # both handle NaN keys inconsistently; explicit filter keeps SE math honest.
    psu_valid = ~pd.Series(psu).isna().values
    mask = (
        ~np.isnan(y)
        & ~np.isnan(w)
        & (w > 0)
        & ~np.isnan(X).any(axis=1)
        & psu_valid
    )
    y, X, w, psu = y[mask], X[mask], w[mask], psu[mask]
    n = len(y)
    H = len(np.unique(psu))
    if n == 0 or H < 2:
        return None
    # Normalise survey weights to mean 1. Point estimate is invariant; this
    # makes statsmodels' use_correction=True small-sample factor (which divides
    # by σ̂² implicitly assuming E[w·e²] = σ²) operate on the right scale.
    w_normalized = w * len(w) / w.sum()
    model = sm.WLS(y, X, weights=w_normalized)
    res = model.fit(
        cov_type="cluster",
        cov_kwds={"groups": psu, "use_correction": True},
        use_t=True,
    )
    # Use statsmodels' built-in t-stats/p-values/CIs (df = n - k). The
    # use_correction=True kwarg already applies the cluster small-sample
    # factor; we don't double-correct with a manual H-1 override.
    ci = res.conf_int(alpha=0.05)
    if isinstance(ci, pd.DataFrame):
        ci_lo = ci.iloc[:, 0].to_numpy()
        ci_hi = ci.iloc[:, 1].to_numpy()
    else:
        ci_lo = np.asarray(ci)[:, 0]
        ci_hi = np.asarray(ci)[:, 1]

    names = column_names if column_names is not None else [f"x{i}" for i in range(X.shape[1])]
    return {
        "beta": pd.Series(res.params, index=names),
        "se": pd.Series(res.bse, index=names),
        "t": pd.Series(res.tvalues, index=names),
        "p": pd.Series(res.pvalues, index=names),
        "ci_lo": pd.Series(ci_lo, index=names),
        "ci_hi": pd.Series(ci_hi, index=names),
        "n": int(n),
        "n_psu": int(H),
        "df_resid": int(res.df_resid),
        "rsquared": float(res.rsquared),
        "model": res,
    }


def quintile_dummies(
    s: pd.Series, n: int = 5,
) -> Tuple[pd.DataFrame, pd.Series]:
    """Cut `s` into `n` equal-count bins by rank; return (k-1 dummies, trend).

    - Dummies reference Q1 (lowest): columns named `q2`, `q3`, ..., `qn`.
    - Trend is the integer quintile index 1..n (NaN outside valid values).
    """
    s = pd.to_numeric(s, errors="coerce")
    mask = s.notna()
    q = pd.Series(np.nan, index=s.index, dtype=float)
    if mask.sum() > 0:
        ranks = s[mask].rank(method="first")
        bins = pd.qcut(ranks, q=n, labels=False, duplicates="drop") + 1
        q.loc[mask] = bins.values
    dummies = pd.DataFrame(index=s.index)
    for k in range(2, n + 1):
        dummies[f"q{k}"] = (q == k).astype(float)
        dummies.loc[q.isna(), f"q{k}"] = np.nan
    return dummies, q

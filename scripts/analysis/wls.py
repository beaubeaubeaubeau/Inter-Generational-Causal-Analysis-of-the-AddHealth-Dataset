"""Weighted ordinary least squares with cluster-robust variance + helpers.

``weighted_ols`` fits ``statsmodels.WLS`` with cluster-robust covariance on
``CLUSTER2`` (use_t=True) and overrides t-stats / CIs against ``df = H - 1``
(common cluster-robust convention) instead of statsmodels' default ``n - k``.

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
    n, n_psu, r2_weighted, df_resid. Uses statsmodels OLS fit with weights
    and cov_type='cluster', use_t=True, df adjustment = (n_psu - 1).

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
    # statsmodels uses df = n - k by default. For cluster-robust inference
    # we override t-stats against df = H - 1 (common convention).
    import scipy.stats as stats
    df_cluster = H - 1
    t_stats = res.params / res.bse
    p_vals = 2 * (1 - stats.t.cdf(np.abs(t_stats), df=df_cluster))
    crit = stats.t.ppf(0.975, df=df_cluster)
    ci_lo = res.params - crit * res.bse
    ci_hi = res.params + crit * res.bse

    names = column_names if column_names is not None else [f"x{i}" for i in range(X.shape[1])]
    return {
        "beta": pd.Series(res.params, index=names),
        "se": pd.Series(res.bse, index=names),
        "t": pd.Series(t_stats, index=names),
        "p": pd.Series(p_vals, index=names),
        "ci_lo": pd.Series(ci_lo, index=names),
        "ci_hi": pd.Series(ci_hi, index=names),
        "n": int(n),
        "n_psu": int(H),
        "df_resid": int(df_cluster),
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

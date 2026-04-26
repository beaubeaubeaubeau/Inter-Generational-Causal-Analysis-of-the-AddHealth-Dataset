"""Weighted means / proportions with cluster-robust linearised standard errors.

``weighted_mean_se``: weighted mean + SD + linearised SE on PSU clusters.
``weighted_prop_ci``: weighted proportion with logit-scale 95 % CI.
"""
from __future__ import annotations

from typing import Tuple

import numpy as np
import pandas as pd


def weighted_mean_se(y, w, psu) -> Tuple[float, float, float, int, int]:
    y = np.asarray(y, dtype=float)
    w = np.asarray(w, dtype=float)
    psu = np.asarray(psu)
    mask = ~np.isnan(y) & ~np.isnan(w) & (w > 0)
    y, w, psu = y[mask], w[mask], psu[mask]
    n = len(y)
    if n == 0:
        return (np.nan, np.nan, np.nan, 0, 0)
    W = w.sum()
    mean = float(np.sum(w * y) / W)
    sd = float(np.sqrt(np.sum(w * (y - mean) ** 2) / W))
    u_i = w * (y - mean)
    df = pd.DataFrame({"u": u_i, "psu": psu})
    u_h = df.groupby("psu")["u"].sum().values
    H = len(u_h)
    if H < 2:
        return (mean, sd, np.nan, n, H)
    u_bar = u_h.mean()
    var_mean = (H / (H - 1.0)) * np.sum((u_h - u_bar) ** 2) / (W ** 2)
    se = float(np.sqrt(max(var_mean, 0.0)))
    return (mean, sd, se, n, H)


def weighted_prop_ci(ind, w, psu) -> Tuple[float, float, float, float, int, int]:
    p, _sd, se, n, H = weighted_mean_se(np.asarray(ind, dtype=float), w, psu)
    if np.isnan(p) or np.isnan(se) or p <= 0 or p >= 1:
        lo = np.nan if np.isnan(p) else max(0.0, p - 1.96 * (se if not np.isnan(se) else 0.0))
        hi = np.nan if np.isnan(p) else min(1.0, p + 1.96 * (se if not np.isnan(se) else 0.0))
        return (p, se, lo, hi, n, H)
    logit = np.log(p / (1 - p))
    se_logit = se / (p * (1 - p))
    lo = 1 / (1 + np.exp(-(logit - 1.96 * se_logit)))
    hi = 1 / (1 + np.exp(-(logit + 1.96 * se_logit)))
    return (p, se, lo, hi, n, H)

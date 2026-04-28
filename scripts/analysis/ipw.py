"""Inverse-probability-of-attrition weighting (IPAW) for W5 outcomes.

The IPAW correction reweights respondents who *remained* at follow-up to
also represent comparable respondents who attrited, under the assumption
that attrition is independent of the outcome conditional on observed
pre-attrition covariates (missing-at-random).

Implementation follows Cole & Hernán (2008), "Constructing inverse
probability weights for marginal structural models," AJE 168(6): 656-664:
the *stabilised* multiplier is ``P(retain) / P(retain | covariates)``,
not the un-stabilised ``1 / P(retain | covariates)``. Stabilisation
yields lower-variance estimators with the same expected value.

Usage in this project: layered on top of ``GSW5`` for any W5-outcome
formal estimation. See ``methods.md §3 Inverse-probability-of-attrition
weighting (IPAW)`` and ``TODO §A3``.
"""
from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd

__all__ = ["fit_ipaw"]


def fit_ipaw(
    design_frame: pd.DataFrame,
    outcome_frame: pd.DataFrame,
    covariates: Sequence[str],
    *,
    retain_indicator: str = "retained",
    base_weight_col: str = "GSW5",
    outcome_col: str | None = None,
    stabilise: bool = True,
    trim_pct: float = 0.95,
    aid_col: str = "AID",
) -> pd.Series:
    """Stabilised inverse-probability-of-attrition weights, layered on a base weight.

    Parameters
    ----------
    design_frame : pd.DataFrame
        Full pre-attrition design frame (e.g. all W4 respondents). Must
        include ``retain_indicator`` (1 if retained at follow-up wave),
        all ``covariates``, and optionally ``base_weight_col``.
    outcome_frame : pd.DataFrame
        The retained subsample (subset of design_frame). The returned
        Series is aligned to this frame's index.
    covariates : Sequence[str]
        Column names in ``design_frame`` to use in the propensity model.
    retain_indicator : str
        Column name in ``design_frame`` for the 0/1 retention flag.
    base_weight_col : str
        Column name in ``outcome_frame`` for the base survey weight
        (e.g. ``GSW5``). The IPAW multiplier is multiplied into this.
    outcome_col : str, optional
        Currently unused; reserved for an outcome-aware variant.
    stabilise : bool
        If True (default; recommended), use stabilised form
        P(retain) / P(retain | X). If False, use 1 / P(retain | X).
    trim_pct : float
        Percentile cap. Weights above this percentile are clamped to it.
        Default 0.95 (cap at the 95th percentile).
    aid_col : str
        Column name for the respondent ID (used for alignment between
        design and outcome frames).

    Returns
    -------
    pd.Series
        Final weights = mean-1-rescaled (base_weight × IPAW_multiplier),
        aligned to ``outcome_frame.index``. NaN for rows missing any
        covariate or the base weight.
    """
    from sklearn.linear_model import LogisticRegression

    # Drop rows in design frame missing required columns.
    needed_design = [retain_indicator, *covariates]
    if base_weight_col in design_frame.columns:
        needed_design.append(base_weight_col)
    train = design_frame[needed_design + [aid_col]].dropna(
        subset=[retain_indicator, *covariates]
    )
    X_train = train[covariates].astype(float).to_numpy()
    A_train = train[retain_indicator].astype(int).to_numpy()
    if A_train.sum() == 0 or A_train.sum() == len(A_train):
        # Degenerate: everyone retained or everyone dropped.
        # Return base weights mean-1-rescaled.
        if base_weight_col in outcome_frame.columns:
            base = outcome_frame[base_weight_col].astype(float)
        else:
            base = pd.Series(1.0, index=outcome_frame.index)
        finite = base.dropna()
        if finite.sum() > 0:
            scale = len(finite) / finite.sum()
            return (base * scale).reindex(outcome_frame.index)
        return base.reindex(outcome_frame.index)

    # Marginal P(retain) for stabilisation numerator.
    p_marg = float(A_train.mean())

    # Fit logistic regression for P(retain | X) on the FULL design frame.
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, A_train)

    # Predict P(retain | X) on the OUTCOME frame.
    needed_out = [aid_col, *covariates]
    if base_weight_col in outcome_frame.columns:
        needed_out.append(base_weight_col)
    out = outcome_frame[needed_out].copy()
    cov_complete = out[list(covariates)].notna().all(axis=1)
    weights = pd.Series(np.nan, index=outcome_frame.index, dtype=float)
    if cov_complete.sum() > 0:
        X_out = out.loc[cov_complete, list(covariates)].astype(float).to_numpy()
        # Clip propensity to [1e-3, 1 - 1e-3] for numerical stability.
        p_hat = np.clip(model.predict_proba(X_out)[:, 1], 1e-3, 1.0 - 1e-3)
        if stabilise:
            ipaw_mult = p_marg / p_hat
        else:
            ipaw_mult = 1.0 / p_hat
        # Layer on base weight if present (else 1).
        if base_weight_col in outcome_frame.columns:
            base_vals = out.loc[cov_complete, base_weight_col].astype(float).to_numpy()
        else:
            base_vals = np.ones_like(ipaw_mult)
        raw_w = base_vals * ipaw_mult
        # Trim at trim_pct.
        if 0 < trim_pct < 1:
            cap = float(np.quantile(raw_w[np.isfinite(raw_w)], trim_pct))
            raw_w = np.minimum(raw_w, cap)
        # Mean-1 rescale (canonical wls.py convention).
        if raw_w.sum() > 0:
            raw_w = raw_w * len(raw_w) / raw_w.sum()
        weights.loc[cov_complete] = raw_w
    return weights

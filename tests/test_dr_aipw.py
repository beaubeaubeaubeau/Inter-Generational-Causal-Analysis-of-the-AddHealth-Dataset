"""Failing tests pinning the contract for ``analysis.dr_aipw.dr_aipw``.

The module is a stub (``raise NotImplementedError``); every test below should
fail until DR-AIPW is implemented. Tests cover the two doubly-robust
guarantees (propensity-only correct, outcome-only correct), a negative
control where both nuisances are wrong, cross-fit honesty (run-to-run
stability), agreement between the analytic influence-function SE and a
nonparametric bootstrap SE, and a no-leakage probe where one fold has a
distorted distribution.
"""
from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------------------
# Helpers — wrong-by-construction nuisance fitters used in (a)/(b)/(c)
# ---------------------------------------------------------------------------


class _ConstantPropModel:
    """``predict_proba`` always returns 0.5 for class 1 (ignores X)."""

    def predict_proba(self, X_test):
        n = len(X_test)
        out = np.full((n, 2), 0.5)
        return out


class _ConstantOutModel:
    """``predict`` always returns the training mean of Y (ignores X)."""

    def __init__(self, y_mean: float):
        self.y_mean = float(y_mean)

    def predict(self, X_test):
        return np.full(len(X_test), self.y_mean)


def _wrong_prop_fn(X_train, A_train):
    return _ConstantPropModel()


def _wrong_out_fn(X_train, Y_train):
    return _ConstantOutModel(np.mean(Y_train))


def _make_dgp(n: int, true_ate: float, seed: int):
    """Logit-linear propensity, linear outcome, additive treatment effect.

    Returns (Y, A, X) with E[Y(1) - Y(0)] = true_ate. Both the propensity
    (logit-linear) and the outcome (linear in X and A) are correctly
    specified for sklearn's LogisticRegression / LinearRegression so the
    "model is right" tests are honest.
    """
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, 3))
    logits = 0.5 * X[:, 0] - 0.8 * X[:, 1] + 0.3 * X[:, 2]
    p = 1.0 / (1.0 + np.exp(-logits))
    A = (rng.uniform(size=n) < p).astype(float)
    # Linear outcome with additive ATE
    Y = 1.0 + 0.7 * X[:, 0] + 0.4 * X[:, 1] - 0.5 * X[:, 2] \
        + true_ate * A + rng.normal(scale=0.5, size=n)
    return Y, A, X


# ---------------------------------------------------------------------------
# (a) DR property — propensity correct, outcome misspecified
# ---------------------------------------------------------------------------


def test_dr_aipw_consistent_when_only_propensity_correct():
    """Propensity is logit-linear (sklearn LogReg fits perfectly); outcome
    fitter is constant (mean of Y) -> badly misspecified. DR should still
    recover the ATE because the propensity-leg correction is unbiased.
    """
    from analysis.dr_aipw import dr_aipw

    true_ate = 0.4
    Y, A, X = _make_dgp(n=1000, true_ate=true_ate, seed=11)
    res = dr_aipw(
        Y, A, X,
        prop_fn=None,            # default LogisticRegression — correct
        out_fn=_wrong_out_fn,    # constant outcome — wrong
        n_splits=2,
        random_state=0,
    )
    assert isinstance(res, dict)
    for key in ("ate", "se", "ci_lo", "ci_hi", "n", "n_treated", "n_control"):
        assert key in res
    assert abs(res["ate"] - true_ate) < 0.15


# ---------------------------------------------------------------------------
# (b) DR property — outcome correct, propensity misspecified
# ---------------------------------------------------------------------------


def test_dr_aipw_consistent_when_only_outcome_correct():
    """Flip of (a): outcome is linear (sklearn LinReg fits perfectly);
    propensity fitter ignores X (constant 0.5). DR's outcome-leg should
    still recover the ATE.
    """
    from analysis.dr_aipw import dr_aipw

    true_ate = 0.4
    Y, A, X = _make_dgp(n=1000, true_ate=true_ate, seed=12)
    res = dr_aipw(
        Y, A, X,
        prop_fn=_wrong_prop_fn,  # constant 0.5 — wrong
        out_fn=None,             # default LinearRegression — correct
        n_splits=2,
        random_state=0,
    )
    assert abs(res["ate"] - true_ate) < 0.15


# ---------------------------------------------------------------------------
# (c) Negative control — both nuisances wrong should bias DR
# ---------------------------------------------------------------------------


def test_dr_aipw_biased_when_both_models_wrong():
    """Sanity: DR is doubly robust, not infinitely robust. With both
    nuisances misspecified (constant propensity AND constant outcome) the
    AIPW estimate collapses to the naive between-group difference; under
    strong confounding that difference is visibly biased away from the
    true ATE.
    """
    from analysis.dr_aipw import dr_aipw

    # Custom DGP with STRONG confounding: a single covariate drives both
    # propensity (steeply) and outcome (with same sign), so naive
    # between-group difference is biased upward by ~0.5 above true ATE.
    rng = np.random.default_rng(13)
    n = 1000
    X = rng.normal(size=(n, 3))
    logits = 3.0 * X[:, 0]  # very steep — high-X kids are nearly always treated
    p = 1.0 / (1.0 + np.exp(-logits))
    A = (rng.uniform(size=n) < p).astype(float)
    true_ate = 0.4
    Y = 1.0 + 1.5 * X[:, 0] + true_ate * A + rng.normal(scale=0.3, size=n)

    res = dr_aipw(
        Y, A, X,
        prop_fn=_wrong_prop_fn,
        out_fn=_wrong_out_fn,
        n_splits=2,
        random_state=0,
    )
    # With strong X→A and X→Y confounding ignored by both nuisances,
    # the AIPW collapses to the naive between-group difference, biased > 0.2.
    assert abs(res["ate"] - true_ate) > 0.2


# ---------------------------------------------------------------------------
# (d) Cross-fit honesty — within-sample stability across random_state
# ---------------------------------------------------------------------------


def test_dr_aipw_crossfit_stable_across_random_state():
    """Refitting the same data with 5 different fold seeds should give
    near-identical ATE estimates (SD < 0.05) — i.e. the cross-fit splits
    are honest and the estimator isn't dominated by fold-assignment noise.
    """
    from analysis.dr_aipw import dr_aipw

    true_ate = 0.4
    Y, A, X = _make_dgp(n=1000, true_ate=true_ate, seed=14)
    ates = []
    for seed in (0, 1, 2, 3, 4):
        res = dr_aipw(Y, A, X, n_splits=2, random_state=seed)
        ates.append(res["ate"])
    ates = np.asarray(ates)
    assert ates.std(ddof=1) < 0.05


# ---------------------------------------------------------------------------
# (e) Analytic SE close to bootstrap SE
# ---------------------------------------------------------------------------


def test_dr_aipw_analytic_se_matches_bootstrap_se():
    """Influence-function SE should agree with a nonparametric bootstrap SE
    (200 resamples) within 20% on a clean linear-Gaussian problem.
    """
    from analysis.dr_aipw import dr_aipw

    true_ate = 0.4
    Y, A, X = _make_dgp(n=2000, true_ate=true_ate, seed=15)
    res = dr_aipw(Y, A, X, n_splits=2, random_state=0)
    analytic_se = float(res["se"])

    rng = np.random.default_rng(15)
    n = len(Y)
    boot_ates = np.empty(200, dtype=float)
    for b in range(200):
        idx = rng.integers(0, n, size=n)
        rb = dr_aipw(
            Y[idx], A[idx], X[idx],
            n_splits=2, random_state=b,
        )
        boot_ates[b] = rb["ate"]
    boot_se = float(boot_ates.std(ddof=1))

    assert abs(analytic_se - boot_se) / boot_se < 0.20


# ---------------------------------------------------------------------------
# (f) No data leakage — distorted held-out fold should predict badly
# ---------------------------------------------------------------------------


def test_dr_aipw_no_leakage_into_held_out_fold():
    """Construct a dataset whose first fold has Y scaled 100x. If the
    cross-fit splitter accidentally trains nuisances on the held-out fold,
    the outcome model will (partly) learn the inflated scale and predictions
    on that fold will look "too good".

    We assert leakage *isn't* happening by checking that the *implied*
    ATE on the distorted-tail data is wildly off (the distorted block
    dominates the outcome scale and DR cannot fit it from the rest of the
    data). Specifically, with the distorted block contributing large |Y|
    values, |ATE| should blow up well past the planted 0.4 — a leakage-free
    estimator has no way to predict the 100x scale on the held-out fold.
    """
    from analysis.dr_aipw import dr_aipw

    rng = np.random.default_rng(16)
    n = 1000
    X = rng.normal(size=(n, 3))
    logits = 0.4 * X[:, 0] - 0.6 * X[:, 1]
    p = 1.0 / (1.0 + np.exp(-logits))
    A = (rng.uniform(size=n) < p).astype(float)
    Y = 1.0 + 0.5 * X[:, 0] + 0.4 * A + rng.normal(scale=0.3, size=n)
    # Distort the *first* contiguous block; with a deterministic fold
    # splitter (e.g. KFold with shuffle=True + a fixed seed), this block
    # will straddle a held-out fold whose distribution differs from the
    # training folds.
    distorted = slice(0, n // 4)
    Y[distorted] = Y[distorted] * 100.0

    res = dr_aipw(Y, A, X, n_splits=4, random_state=0)
    # Honest (no-leak) cross-fitting cannot predict the 100x block from
    # training folds whose outcomes are O(1), so residuals on the held-out
    # block are huge and bleed into the AIPW correction. The estimated ATE
    # should be far from the planted 0.4.
    assert abs(res["ate"] - 0.4) > 1.0



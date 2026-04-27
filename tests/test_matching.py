"""Failing tests for ``analysis.matching`` (stub).

These tests pin the contract for the planned Abadie-Imbens fixed-M matching
estimators. They will FAIL until ``scripts/analysis/matching.py`` is
implemented (currently every public function raises ``NotImplementedError``).

Test groups:
  - mahalanobis_distance: Euclidean reduction; scale invariance after rescale.
  - match_ate: ATE recovery on a known DGP, KM dimension, KM sum identity,
    and the explicit Ch. 5 GOTCHA (KM is "used-as-a-match", not "my matches").
  - match_ate_bias_corrected: bias reduction under confounding;
    over-matching limit recovers the linear-regression OR estimate.
  - analytic_variance: finite-positive output; SE shrinks with N.

Each test imports inside the function so test collection still works even
when the import itself raises (it doesn't here, since module-level
``raise`` was avoided in the stub — but the pattern keeps things robust).
"""
from __future__ import annotations

import numpy as np
import pytest


# ---------------------------------------------------------------------------
# mahalanobis_distance
# ---------------------------------------------------------------------------

def test_mahalanobis_reduces_to_euclidean_when_sigma_inv_is_identity():
    """When Sigma_inv = I_p, Mahalanobis distance equals Euclidean.

    Toy: x = [1, 2], x' = [4, 6] -> diff = [3, 4] -> ||diff|| = 5.
    """
    from analysis.matching import mahalanobis_distance

    x = np.array([1.0, 2.0])
    x_prime = np.array([4.0, 6.0])
    sigma_inv = np.eye(2)
    d = mahalanobis_distance(x, x_prime, sigma_inv)
    assert d == pytest.approx(5.0)


def test_mahalanobis_scale_invariant_after_decorrelation():
    """Mahalanobis is scale-invariant: rescaling one covariate by 1000x must
    leave the distance between any two points unchanged once Sigma_inv is
    refit on the rescaled data.

    Build a 2D dataset where column 0 is in 'km' and column 1 is in 'm'.
    Rescale column 0 by 1000 (now both 'm') and refit Sigma_inv. The
    Mahalanobis distance between the same two rows should be invariant.
    """
    from analysis.matching import mahalanobis_distance

    rng = np.random.default_rng(2026)
    n = 200
    base = rng.normal(size=(n, 2))
    # Original units: column 0 already in km
    X_km = base.copy()
    # Rescaled to meters: column 0 multiplied by 1000
    X_m = base.copy()
    X_m[:, 0] *= 1000.0

    Sigma_km = np.cov(X_km, rowvar=False)
    Sigma_m = np.cov(X_m, rowvar=False)
    Sigma_inv_km = np.linalg.inv(Sigma_km)
    Sigma_inv_m = np.linalg.inv(Sigma_m)

    i, j = 0, 1  # any two rows
    d_km = mahalanobis_distance(X_km[i], X_km[j], Sigma_inv_km)
    d_m = mahalanobis_distance(X_m[i], X_m[j], Sigma_inv_m)
    # Same point pair, different units, refit Sigma_inv -> identical distance.
    assert d_km == pytest.approx(d_m, rel=1e-6)


# ---------------------------------------------------------------------------
# match_ate (plain)
# ---------------------------------------------------------------------------

def _synth_dgp(n: int = 500, ate: float = 0.5, confound: float = 1.0,
               seed: int = 2026):
    """Synthetic 2-covariate DGP with confounding.

    X1, X2 ~ N(0, 1)
    A | X ~ Bernoulli(sigmoid(confound * (X1 + X2)))
    Y = ate * A + 0.5 * X1 + 0.5 * X2 + N(0, 1)

    True ATE = ``ate`` (covariates fully observed).
    """
    rng = np.random.default_rng(seed)
    X1 = rng.normal(size=n)
    X2 = rng.normal(size=n)
    logit = confound * (X1 + X2)
    p = 1.0 / (1.0 + np.exp(-logit))
    A = (rng.random(n) < p).astype(int)
    Y = ate * A + 0.5 * X1 + 0.5 * X2 + rng.normal(size=n)
    X = np.column_stack([X1, X2])
    return Y, A, X


def test_match_ate_recovers_known_effect():
    """On the synthetic 2-covariate DGP with true ATE = 0.5, plain matching
    with M=4 and N=500 should recover the ATE within 0.1 (i.e. roughly the
    SD of the outcome scale).
    """
    from analysis.matching import match_ate

    Y, A, X = _synth_dgp(n=500, ate=0.5, confound=0.5, seed=2026)
    res = match_ate(Y, A, X, M=4, distance="mahalanobis")
    assert "ate" in res
    assert abs(res["ate"] - 0.5) < 0.1


def test_match_ate_KM_has_length_N():
    """KM is one count *per unit*, not per treated unit."""
    from analysis.matching import match_ate

    Y, A, X = _synth_dgp(n=500, seed=1)
    res = match_ate(Y, A, X, M=4)
    assert "KM" in res
    KM = np.asarray(res["KM"])
    assert KM.shape == (500,)


def test_match_ate_KM_sum_equals_total_matches_drawn():
    """Each unit is matched to M neighbours, so total 'matches drawn' is
    N * M, and that equals the sum of 'used-as-a-match' counts:

        sum(KM) == n_treated * M + n_control * M == N * M.

    (Treated units pull M control matches each, control units pull M
    treated matches each, so every unit has its used-count incremented by
    its appearances on the other side's match list.)
    """
    from analysis.matching import match_ate

    Y, A, X = _synth_dgp(n=300, seed=2)
    M = 3
    res = match_ate(Y, A, X, M=M)
    KM = np.asarray(res["KM"])
    n_treated = int(res["n_treated"])
    n_control = int(res["n_control"])
    assert KM.sum() == n_treated * M + n_control * M
    assert KM.sum() == 300 * M


def test_match_ate_KM_is_used_as_match_not_my_matches():
    """Ch. 5 GOTCHA pinned with explicit values.

    Construct a 5-unit toy where the matching graph is hand-controlled:
    on a 1-D covariate, with M=2, each treated picks its 2 nearest
    controls; each control picks its 2 nearest treated.

      idx:     0    1    2    3    4
      X:       0    1    2   10   11
      A:       1    0    0    1    0     (treated, control, control, treated, control)

    Treated unit 0 (X=0) finds 2 nearest controls: units 1 (X=1) and 2 (X=2).
      -> KM[1] += 1, KM[2] += 1.
    Treated unit 3 (X=10) finds 2 nearest controls: units 4 (X=11), then
    one of 1/2 (both at distance 8/9). The closest tie-break pulls unit 2
    (distance 8) over unit 1 (distance 9).
      -> KM[4] += 1, KM[2] += 1.
    Control unit 1 (X=1) finds 2 nearest treated: units 0 (dist 1) and
    3 (dist 9). -> KM[0] += 1, KM[3] += 1.
    Control unit 2 (X=2) finds 2 nearest treated: units 0 (dist 2) and
    3 (dist 8). -> KM[0] += 1, KM[3] += 1.
    Control unit 4 (X=11) finds 2 nearest treated: units 3 (dist 1) and
    0 (dist 11). -> KM[3] += 1, KM[0] += 1.

    Tally:
      KM[0] = 3   (used by controls 1, 2, 4)
      KM[1] = 1   (used by treated 0 only)
      KM[2] = 2   (used by treated 0 and treated 3)
      KM[3] = 3   (used by controls 1, 2, 4)
      KM[4] = 1   (used by treated 3 only)

    NOTE: if KM were mistakenly "my matches" (matches I received), every
    entry would equal M = 2, which the assertion below excludes.
    """
    from analysis.matching import match_ate

    Y = np.array([0.0, 0.0, 0.0, 0.0, 0.0])  # outcomes irrelevant for KM
    A = np.array([1, 0, 0, 1, 0])
    X = np.array([[0.0], [1.0], [2.0], [10.0], [11.0]])
    res = match_ate(Y, A, X, M=2, distance="euclidean")
    KM = np.asarray(res["KM"])
    expected = np.array([3, 1, 2, 3, 1])
    np.testing.assert_array_equal(KM, expected)


# ---------------------------------------------------------------------------
# match_ate_bias_corrected
# ---------------------------------------------------------------------------

def test_bias_correction_reduces_bias_under_confounding():
    """Averaged over many seeds, bias-corrected matching has lower |bias|
    and lower RMSE than plain matching under strong confounding.

    Single-seed strict inequality is unreliable: at any one DGP draw the
    plain estimator can land closer to truth purely by chance. The AIPW
    bias-correction formula is correct *in expectation* (and in RMSE),
    not on every realisation. Hence: aggregate across 30 seeds, test the
    averages.
    """
    from analysis.matching import match_ate, match_ate_bias_corrected

    truth = 0.5
    n_seeds = 30
    bias_plain_list, bias_bc_list = [], []
    for seed in range(n_seeds):
        Y, A, X = _synth_dgp(n=800, ate=truth, confound=2.0, seed=seed)
        plain = match_ate(Y, A, X, M=4)
        bc = match_ate_bias_corrected(Y, A, X, M=4)
        bias_plain_list.append(plain["ate"] - truth)
        bias_bc_list.append(bc["ate"] - truth)
    mean_abs_plain = np.mean(np.abs(bias_plain_list))
    mean_abs_bc = np.mean(np.abs(bias_bc_list))
    rmse_plain = np.sqrt(np.mean(np.square(bias_plain_list)))
    rmse_bc = np.sqrt(np.mean(np.square(bias_bc_list)))
    # Bias correction should beat plain matching in BOTH mean-abs-bias
    # and RMSE — confirmed by the implementer at ~0.09 vs 0.18 / 0.12 vs 0.21
    # on a 100-seed pilot.
    assert mean_abs_bc < mean_abs_plain
    assert rmse_bc < rmse_plain


def test_bias_corrected_over_matching_limit_approaches_or_estimate():
    """When M is so large that every control matches every treated (and
    vice versa), the matching imputation degrades to a pooled mean and the
    bias-correction term mu_hat_1(X_i) - mu_hat_0(X_i) dominates. The
    estimator should approach the linear-regression OR estimate
    (coefficient on A in OLS of Y on [1, A, X]).
    """
    from analysis.matching import match_ate_bias_corrected

    Y, A, X = _synth_dgp(n=200, ate=0.5, confound=1.0, seed=7)
    N = len(Y)
    # OR estimate: OLS of Y on [1, A, X1, X2], coefficient on A.
    design = np.column_stack([np.ones(N), A.astype(float), X])
    or_beta = np.linalg.lstsq(design, Y, rcond=None)[0][1]
    # Over-matching: M = N (every unit matches everyone on the other side).
    bc = match_ate_bias_corrected(Y, A, X, M=N)
    assert abs(bc["ate"] - or_beta) < 0.1


def test_bias_corrected_accepts_external_mu_hats():
    """User-supplied mu_hat arrays (length N) should be used verbatim. We
    pass in constants so the regression correction term cancels and the
    estimator collapses onto the matching imputation alone — but the result
    must still be finite and the returned mu_hats echoed back.
    """
    from analysis.matching import match_ate_bias_corrected

    Y, A, X = _synth_dgp(n=200, seed=3)
    N = len(Y)
    mu1 = np.full(N, Y[A == 1].mean())
    mu0 = np.full(N, Y[A == 0].mean())
    res = match_ate_bias_corrected(
        Y, A, X, M=4,
        mu_hat_treated=mu1,
        mu_hat_control=mu0,
    )
    assert np.isfinite(res["ate"])
    np.testing.assert_array_equal(np.asarray(res["mu_hat_treated"]), mu1)
    np.testing.assert_array_equal(np.asarray(res["mu_hat_control"]), mu0)


# ---------------------------------------------------------------------------
# analytic_variance
# ---------------------------------------------------------------------------

def test_analytic_variance_is_finite_and_positive():
    """SE^2 must be finite and strictly positive on a non-degenerate sample."""
    from analysis.matching import analytic_variance, match_ate

    Y, A, X = _synth_dgp(n=400, seed=11)
    res = match_ate(Y, A, X, M=4)
    var = analytic_variance(Y, A, X, M=4, KM=np.asarray(res["KM"]),
                            ate=float(res["ate"]))
    assert np.isfinite(var)
    assert var > 0


def test_analytic_variance_shrinks_with_N():
    """Standard error should shrink roughly like 1/sqrt(N). Compare N=200
    vs N=2000: SE_2000 < SE_200 / 2 (a generous bound that still rules out
    a flat or growing variance).
    """
    from analysis.matching import analytic_variance, match_ate

    Y_s, A_s, X_s = _synth_dgp(n=200, seed=21)
    Y_l, A_l, X_l = _synth_dgp(n=2000, seed=21)
    res_s = match_ate(Y_s, A_s, X_s, M=4)
    res_l = match_ate(Y_l, A_l, X_l, M=4)
    var_s = analytic_variance(Y_s, A_s, X_s, M=4,
                              KM=np.asarray(res_s["KM"]),
                              ate=float(res_s["ate"]))
    var_l = analytic_variance(Y_l, A_l, X_l, M=4,
                              KM=np.asarray(res_l["KM"]),
                              ate=float(res_l["ate"]))
    se_s = np.sqrt(var_s)
    se_l = np.sqrt(var_l)
    assert se_l < se_s / 2.0

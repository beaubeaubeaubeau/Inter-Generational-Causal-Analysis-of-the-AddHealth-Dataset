# popularity-vs-sociability — EXP-POPSOC

Two-exposure contrast experiment: popularity (in-degree, peer-conferred) vs.
sociability (out-degree, self-driven) across all 13 outcomes used by the
project. Tests whether the two W1 network exposures have **different effect
signatures** by outcome domain — popularity dominating status-mediated
outcomes (earnings, BMI/waist), sociability dominating agency-mediated
outcomes (mental health, sleep). Pairs with
[multi-outcome-screening](../multi-outcome-screening/README.md) but flips the
analytic axis from "broad exposure scan vs. broad outcome scan" to "two
focused exposures vs. their per-outcome contrast."

| Field | Value |
|---|---|
| Status | planned |
| Exposure | `IDGX2` (in-degree, popularity) and `ODGX2` (out-degree, sociability). `BCENT10X` is **dropped** per user feedback (collinear with `IDGX2`, no incremental signal in cognitive-screening D1). |
| Outcome | All 13 outcomes: `W4_COG_COMP` (cognitive); `H4BMI`, `H4WAIST`, `H4SBP`, `H4DBP`, `H4BMICLS` (cardiometabolic); `H5MN1`, `H5MN2` (mental health); `H5ID1`, `H5ID4`, `H5ID16` (functional); `H5LM5`, `H5EC1` (SES). |
| DAG | [`DAG-Pop-vs-Soc`](dag.md) — per-outcome inheritance: `DAG-Cog v1.0` for `W4_COG_COMP`; `DAG-CardioMet` for the 5 cardiometabolic outcomes; `DAG-Mental` for `H5MN1`/`H5MN2`; `DAG-Functional` for `H5ID*`; `DAG-SES` (drops AHPVT) for `H5LM5`/`H5EC1`. |
| Method | Per-outcome WLS (`weighted_ols`) with `GSWGT4_2` and cluster-robust SE on `CLUSTER2` (132 PSUs). For each outcome, fit `IDGX2` and `ODGX2` in **separate** regressions to keep the marginal-effect interpretation clean (the two are correlated; a joint fit would estimate residualized "popularity above and beyond sociability," which is a different estimand). The cross-comparison is then `Δβ = β_in − β_out`, evaluated per outcome via paired cluster-bootstrap (200 iterations, cluster-resampling on `CLUSTER2`). |
| Adjustment | Per-outcome inheritance (see DAG): L0+L1+AHPVT for cognitive and cardiometabolic; L0+L1 (drop AHPVT) for SES; L0+L1 for mental/functional with the `H1GH1` and `CESD_SUM` retention decision documented in [dag.md](dag.md). All 16 network exposures are restricted to within-saturated-schools (positivity = 0 outside; same rule as cognitive-screening). |
| Restriction | Within-saturated-schools (network exposures) on the W4 analytic frame (`cache/analytic_w4.parquet`). W5 outcomes attach via `load_outcome` and inherit `GSWGT4_2` for the screen; formal causal estimation should switch to `GSW5` × IPAW per the planned `IPAW-W5` work. |
| Sensitivity | (1) Quintile dose-response per exposure using `quintile_dummies` from `analysis.wls`, with linear-trend test on the integer-quintile variable; (2) Polysocial-PCA-PC1 — fit `sklearn.decomposition.PCA(n_components=5)` on the 24 z-standardized exposures used by cognitive-screening, take PC1, refit primary spec with PC1 as the lone exposure; (3) E-value per significant β via `analysis.sensitivity:evalue`. |
| Outputs | `tables/primary/popsoc_primary.csv` (26 rows = 2 exposures × 13 outcomes), `tables/primary/popsoc_primary.md`, `tables/primary/popsoc_paired_bootstrap.csv` (13 rows, one per outcome), `tables/sensitivity/popsoc_quintile.csv`, `tables/sensitivity/popsoc_polysocial_pca.csv`, `tables/sensitivity/popsoc_evalue.csv`. |
| Plots | `figures/primary/popsoc_beta_heatmap.png` (2 × 13 standardized-β heatmap with significance markers), `figures/primary/popsoc_pairedboot_forest.png` (forest of `Δβ = β_in − β_out` per outcome with 95% bootstrap CI). |
| Estimand wording | "Among Add Health respondents in saturated schools (network-exposure positivity), conditional on each outcome's per-DAG adjustment set (see [dag.md](dag.md)), a one-unit increase in `IDGX2` (resp. `ODGX2`) is associated with a β-unit change in outcome *Y*. The cross-exposure contrast `Δβ = β_in − β_out` per outcome is the experiment's primary inferential target; its sign indicates whether the outcome is dominated by peer-conferred status (`Δβ > 0`) or self-driven sociability (`Δβ < 0`)." |
| Notes | Subsumes the prior idea of fitting both exposures jointly. Per user feedback, the **separate-regression + paired-bootstrap of Δβ** design is preferred: the joint fit's β coefficients are not the constructs we want to compare. Drop `BCENT10X` per user feedback. |

## Files

- `run.py` — orchestration: load `analytic_w4.parquet`, attach W5 outcomes via `load_outcome`, build per-outcome adjustment sets per `DAG-Pop-vs-Soc`, fit WLS, compute paired-bootstrap `Δβ` per outcome, write tables under `tables/primary/` and `tables/sensitivity/`.
- `figures.py` — heatmap (2 × 13) and paired-bootstrap forest plot.
- `report.md` — narrative; chart-explanation convention applies (caption + prose + linked methods).
- `tests/test_smoke.py` — pytest smoke test on synthetic fixture.

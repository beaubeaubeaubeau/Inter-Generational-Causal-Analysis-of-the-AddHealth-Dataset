# friendship-quality-vs-quantity — EXP-QVQ

Quality-vs-quantity friendship contrast. Tests the hypothesis that **having
one close friend to confide in** (quality) outpredicts **having many friends**
(quantity) on mental-health outcomes, while the reverse holds for SES (network
breadth wins for information access and labor-market signals). Unlike the
network-derived experiments, the three exposures here come from the W1 in-home
interview's friendship-grid module, so the analytic frame is the **full W1
in-home cohort** (N ≈ 4,700) rather than the within-saturated-schools subset.

| Field | Value |
|---|---|
| Status | planned |
| Exposure | `FRIEND_DISCLOSURE_ANY` (binary; quality — at least one nominated friend the respondent has talked to about a problem in the past week), `FRIEND_N_NOMINEES` (count 0–10; quantity), `FRIEND_CONTACT_SUM` (sum across nominees of W1 friendship-grid contact items; frequency). All three are derived in `scripts/analysis/derivation.py` and present on `analytic_w1_full.parquet`. |
| Outcome | All 13 outcomes: `W4_COG_COMP`; `H4BMI`, `H4WAIST`, `H4SBP`, `H4DBP`, `H4BMICLS`; `H5MN1`, `H5MN2`; `H5ID1`, `H5ID4`, `H5ID16`; `H5LM5`, `H5EC1`. |
| DAG | [`DAG-QvQ`](dag.md) — sample-wide variant of the per-outcome DAGs (no within-saturated-schools restriction; survey exposures are universal in W1 in-home). Per-outcome adjustment-set inheritance same as `popularity-vs-sociability`. |
| Method | **Same-spec head-to-head WLS**: each outcome is fit ONCE with all three exposures in the regression, plus the per-outcome adjustment set. Each β is the marginal effect of its exposure conditional on the other two. This is the load-bearing identification choice — the three exposures are theoretically orthogonal (quality ≠ quantity ≠ frequency) but empirically correlated; the joint fit makes the contrast a within-respondent decomposition. |
| Adjustment | Per-outcome inheritance: `DAG-Cog v1.0` (L0+L1+AHPVT) for `W4_COG_COMP`; `DAG-CardioMet` (L0+L1+AHPVT) for cardiometabolic; `DAG-Mental` (L0+L1) for mental health; `DAG-Functional` (L0+L1) for functional; `DAG-SES` (L0+L1, no AHPVT) for SES. |
| Restriction | Full W1 in-home cohort (no saturation gate). Use `cache/analytic_w1_full.parquet` for the W1 covariates and exposures; merge W4 outcomes via `load_outcome` against `cache/w4inhome.parquet`, W5 outcomes via `load_outcome` against `cache/pwave5.parquet`. Weight: `GSWGT4_2` for cross-outcome comparability with the screening experiments; report a parallel `GSW5`-weighted sensitivity row for W5 outcomes. |
| Sensitivity | (1) Quintile dose-response on `FRIEND_N_NOMINEES` only (it is the only continuous-meaningful integer exposure; `FRIEND_DISCLOSURE_ANY` is binary, `FRIEND_CONTACT_SUM` is a multi-item sum dominated by the nominee count). Use `quintile_dummies` from `analysis.wls`, with linear-trend test; (2) E-value per significant β via `analysis.sensitivity:evalue`; (3) **Drop-one-exposure sensitivity**: refit each outcome without each of the three exposures in turn, to see how much each `β` shifts when its competitor is uncontrolled. |
| Outputs | `tables/primary/qvq_primary.csv` (39 rows = 3 exposures × 13 outcomes), `tables/primary/qvq_primary.md`, `tables/sensitivity/qvq_quintile.csv`, `tables/sensitivity/qvq_evalue.csv`, `tables/sensitivity/qvq_drop_one.csv`. |
| Plots | `figures/primary/qvq_beta_heatmap.png` (3 × 13 standardized-β heatmap with significance markers). |
| Estimand wording | "Among Add Health respondents in the full W1 in-home cohort, conditional on each outcome's per-DAG adjustment set, a one-unit increase in `FRIEND_DISCLOSURE_ANY` (resp. `FRIEND_N_NOMINEES`, resp. `FRIEND_CONTACT_SUM`) — **holding the other two friendship measures fixed** — is associated with a β-unit change in outcome *Y*." |
| Notes | The same-spec head-to-head fit is the cleanest implementation of the user's hypothesis. The three exposures are intentionally NOT fit in separate regressions; the marginal-conditional interpretation is what makes the quality-vs-quantity contrast identified within-respondent. Survey-exposure sample frame ≠ network-exposure sample frame: do not merge β estimates from this experiment with the network-exposure results without explicit reweighting. |

## Files

- `run.py` — orchestration: load `analytic_w1_full.parquet`, attach W4 + W5 outcomes via `load_outcome`, build per-outcome adjustment sets, fit one WLS per outcome with all three exposures jointly, write primary + sensitivity tables.
- `figures.py` — primary heatmap.
- `report.md` — narrative.
- `tests/test_smoke.py` — pytest smoke test.

# Experiments register

A single-source-of-truth mapping for **experiment ↔ DAG ↔ method ↔ adjustment set ↔ output ↔ plot**, so that any chart or coefficient cited in the final report or presentation can be traced back to its causal model and method without leaving this file.

**Conventions:**

- An **experiment** is the unit at which an include/exclude decision for the report is made. Most experiments are *(exposure family) × (outcome) × (DAG) × (method)* combinations. Sensitivity audits and mass-screens are first-class experiments too.
- Experiment IDs follow `EXP-<task>-<short-name>` (e.g. `EXP-14-COG`). Stable across edits.
- **Status:** `complete` (data exists, plots rendered) | `planned` (Task-16 work, scoped but not run) | `deprecated` (superseded; kept for traceability).
- **DAG** column points by ID into [dag_library.md](dag_library.md). Method column names the estimator. **Estimand wording** is the verbatim sentence to use in plot captions and report prose.
- For mass-screens (24 exposures × N outcomes), the experiment ID is the screen, not the individual cells. Per-cell results live in the linked CSV.

---

## Active experiments (data + outputs exist on disk as of 2026-04-25)

### EXP-14-COG — Cognition causal-screening battery

| Field | Value |
|---|---|
| Status | complete |
| Exposure | 24 W1 social exposures (16 network-derived + 8 survey-derived); see [task14_causal_screening.py `EXPOSURES`](../scripts/task14_causal_screening.py) |
| Outcome | `W4_COG_COMP` (z-mean of `C4WD90_1`, `C4WD60_1`, `C4NUMSCR`) |
| DAG | [`DAG-Cog`](dag_library.md#dag-cog-v10--w1-social-integration--w4-cognitive-outcome) |
| Method | Weighted OLS (`statsmodels.WLS`) with `GSWGT4_2`, cluster-robust SE on `CLUSTER2` (132 PSUs) |
| Adjustment | L0+L1+AHPVT (primary), with L0 and L0+L1 as D4-stability reductions |
| Restriction | **For 16 network exposures: within-saturated-schools only** (positivity = 0 outside; see [synthesis §5.6](addhealth_synthesis.md#56-identification-assumptions-and-target-estimand)). For 8 survey exposures: full W1 in-home cohort. |
| Diagnostics | Full D1–D9 battery (see [synthesis §6.5](addhealth_synthesis.md#65-causal-screening-diagnostic-battery-d1d9)) |
| Outputs | [outputs/14_screening_matrix.csv](../outputs/14_screening_matrix.csv), [outputs/14_shortlist.csv](../outputs/14_shortlist.csv), [outputs/14_screening.md](../outputs/14_screening.md) |
| Plots | [img/causal/screening_heatmap.png](../img/causal/screening_heatmap.png) (D1–D9 grid), [img/causal/adjustment_stability.png](../img/causal/adjustment_stability.png) (D4), [img/causal/sibling_dissociation.png](../img/causal/sibling_dissociation.png) (D3), [img/causal/component_consistency.png](../img/causal/component_consistency.png) (D5), [img/causal/negctrl_failure_grid.png](../img/causal/negctrl_failure_grid.png) (D2 — informational, contaminated NC) |
| Estimand wording | "Among Add Health respondents in saturated schools (network exposures) or the full W1 in-home cohort (survey exposures), conditional on baseline W1 verbal IQ, demographics, and W1 affective/somatic state, exposure *X* is associated with a β-unit change in W4 cognition relative to its baseline-predicted level." |

### EXP-15-MULTI — Multi-outcome screen (12 non-cognitive outcomes)

| Field | Value |
|---|---|
| Status | complete |
| Exposure | Same 24 as EXP-14-COG |
| Outcome | 12 outcomes in 4 groups: cardiometabolic (5: `H4BMI`, `H4SBP`, `H4DBP`, `H4WAIST`, `H4BMICLS`), functional (3: `H5ID1`, `H5ID4`, `H5ID16`), mental health (2: `H5MN1`, `H5MN2`), SES (2: `H5LM5`, `H5EC1`) |
| DAG | **`DAG-Cog` applied uniformly as a screening approximation**, despite three of the per-outcome DAGs (`DAG-CardioMet`, `DAG-SES`, `DAG-Mental`) requiring different adjustment sets. This is the load-bearing screening compromise: ranking is preserved across outcomes but per-outcome point estimates are biased relative to their proper DAG. |
| Method | Same WLS + cluster-SE as EXP-14-COG |
| Adjustment | L0+L1+AHPVT uniformly (incorrect for `H5EC1`/`H5LM5`/`H4BMI` — Task 16 fixes this per-outcome) |
| Restriction | Same saturation rule as EXP-14-COG; W5 outcomes additionally subject to mode restriction implicit in `pwave5.parquet` cells |
| Diagnostics | D1 + D4 only (D2 / D6 / D7 / D8 / D9 inherited from EXP-14-COG; D3 / D5 cognition-only and skipped) |
| Outputs | [outputs/15_multi_outcome_matrix.csv](../outputs/15_multi_outcome_matrix.csv) (288 rows = 24 × 12), [outputs/15_multi_outcome.md](../outputs/15_multi_outcome.md) |
| Plots | [img/causal/multi_outcome_beta_heatmap.png](../img/causal/multi_outcome_beta_heatmap.png) (z-standardized β grid), [img/causal/multi_outcome_sig_heatmap.png](../img/causal/multi_outcome_sig_heatmap.png) (−log10 p), [img/causal/15_per_outcome_pcount.png](../img/causal/15_per_outcome_pcount.png) (breadth), [img/causal/15_handoff_forest.png](../img/causal/15_handoff_forest.png) (4 handoff pairs) |
| Estimand wording | "Same population restrictions as EXP-14-COG; **screening-only** β estimates use the cognitive DAG's adjustment set across all 12 outcomes for cross-outcome ranking comparability. Per-outcome handoffs (EXP-16-*) re-estimate under outcome-specific DAGs." |

### EXP-11-SENS — Sensitivity / falsification audits on EXP-14-COG

| Field | Value |
|---|---|
| Status | complete |
| Scope | Collinearity, leave-one-out permutation, saturated-school balance, AHPVT-shift audit, placebo permutation, reserve-code sensitivity |
| DAG | Same `DAG-Cog` as EXP-14-COG; this is meta-analysis of EXP-14-COG, not a separate identification claim |
| Method | Various; per-figure detail in [scripts/task11_sensitivity.py](../scripts/task11_sensitivity.py) and [scripts/task12_regression_plots.py](../scripts/task12_regression_plots.py) |
| Outputs | [outputs/11_sensitivity.md](../outputs/11_sensitivity.md), [outputs/11_ahpvt_shift.csv](../outputs/11_ahpvt_shift.csv), [outputs/11_collinearity.csv](../outputs/11_collinearity.csv), [outputs/11_correlation.csv](../outputs/11_correlation.csv), [outputs/11_placebo_permutation.csv](../outputs/11_placebo_permutation.csv), [outputs/11_saturated_balance.csv](../outputs/11_saturated_balance.csv) |
| Plots | [img/regressions/coefficient_forest.png](../img/regressions/coefficient_forest.png), [img/regressions/quintile_dose_response.png](../img/regressions/quintile_dose_response.png), [img/sensitivity/ahpvt_with_without.png](../img/sensitivity/ahpvt_with_without.png), [img/sensitivity/saturated_vs_full.png](../img/sensitivity/saturated_vs_full.png), [img/sensitivity/attrition_balance.png](../img/sensitivity/attrition_balance.png), [img/sensitivity/mode_selection_balance.png](../img/sensitivity/mode_selection_balance.png), and four others under [img/regressions/](../img/regressions/) |
| Estimand wording | "Sensitivity audit of EXP-14-COG. Each figure asks whether the EXP-14-COG β survives a specific challenge (collinearity, alternate weighting, placebo permutation, etc.); none of these are independent causal estimates." |

### EXP-13-VERIFY — Verification pack on EXP-14-COG / EXP-15-MULTI

| Field | Value |
|---|---|
| Status | complete |
| Scope | Benjamini–Hochberg FDR adjustment, attrition IPAW (preliminary), negative-control sweeps, design-effect estimates, PSU counts, reserve-code leakage check |
| DAG | Meta-analysis of EXP-14-COG / EXP-15-MULTI; no new DAG |
| Outputs | [outputs/13_verification.md](../outputs/13_verification.md) + 9 CSVs in `outputs/13_*.csv` |
| Plots | None embedded in the reference docs (internal QA) |

---

## Planned experiments (Task 16; see [TODO.md §A](../TODO.md))

### EXP-16-FD-COG — Front-door decomposition for AHPVT-cognition path

| Field | Value |
|---|---|
| Status | planned |
| Purpose | **Sensitivity check for the trajectory framing**, not a load-bearing alternative model. Quantifies how much the EXP-14-COG β shifts if AHPVT is on the causal path from W1 social integration to W4 cognition (the strict mediator reading). |
| Exposure / outcome | `IDGX2` → `W4_COG_COMP` (highest-priority pair for the front-door check, since IDGX2 has the largest D4 drift) |
| DAG | [`DAG-Cog-FrontDoor`](dag_library.md#dag-cog-frontdoor-planned-task-16-sensitivity) (planned) |
| Method | Three-equation front-door: (a) `IDGX2 → AHPVT \| L0+L1`, (b) `AHPVT → W4_COG_COMP \| L0+L1, IDGX2`, (c) total-effect = sum over AHPVT levels |
| Adjustment | L0+L1 (drops AHPVT from the back-door set since AHPVT is now treated as the mediator) |
| Outputs | TBD: `outputs/16_frontdoor_cog.csv`, `outputs/16_frontdoor_cog.md` |
| Plots | TBD: `img/causal/16_frontdoor_decomp.png` (bar chart: trajectory β vs. front-door-implied total effect, with the gap as the trajectory caveat magnitude) |
| Estimand wording (when complete) | "Under the strict mediator reading of `AHPVT`, the total effect of `IDGX2` on `W4_COG_COMP` would be β_FD; the trajectory-adjusted estimate from EXP-14-COG is β_traj; the gap β_FD − β_traj is the magnitude by which the trajectory framing under-estimates if mediation is real." |

### EXP-16-NC — Clean negative-control battery

| Field | Value |
|---|---|
| Status | planned |
| Purpose | Replace the contaminated `HEIGHT_IN` D2 with a battery of NC outcomes that don't share the height ↔ peer-status mechanism. Tests the unmeasured-confounder assumption in `DAG-Cog`. |
| Candidate outcomes | Blood type, age at menarche (or W1 pubertal-development index), hand-dominance, residential stability pre-W1. **Pre-flight required**: confirm public-use availability of each. |
| Exposure | All 24 EXP-14-COG exposures, in the cognition outcome's adjustment set |
| DAG | `DAG-Cog` with each NC outcome substituted for `Y` |
| Method | Same WLS + cluster-SE as EXP-14-COG |
| Outputs | TBD: `outputs/16_nc_battery.csv`, `outputs/16_nc_battery.md` |
| Plots | TBD: NC-failure forest plot per exposure |

### EXP-16-IPAW-W5 — IPAW for W5 outcome estimation

| Field | Value |
|---|---|
| Status | planned |
| Purpose | Convert the W5-outcome screening estimates (currently using `GSWGT4_2`) into estimation-grade `GSW5` + IPAW. Required before any W5 point estimate is reported in the final paper. |
| Exposure / outcome | All EXP-15-MULTI W5 outcomes (`H5EC1`, `H5ID1`, `H5ID4`, `H5ID16`, `H5MN1`, `H5MN2`, `H5LM5`) |
| Helper to write | `analysis_utils.fit_ipaw(design_frame, outcome_frame, covariates)` returning stabilised inverse-probability-of-attrition weights, trimmed at 95th percentile |
| DAG | Outcome-specific (see DAG-CardioMet / SES / Mental / Functional planned entries) |
| Method | WLS + cluster-SE on `CLUSTER2`, weights = `GSW5 × IPAW` |
| Outputs | TBD: `outputs/16_ipaw_w5_<outcome>.csv` per outcome |
| Plots | TBD: side-by-side comparison of EXP-15-MULTI screening β vs. EXP-16-IPAW-W5 estimation β |

### EXP-16-HAND-* — Per-handoff formal estimation

One experiment per Task-16 handoff pair from EXP-15-MULTI:

| ID | Exposure | Outcome | DAG | Method |
|---|---|---|---|---|
| EXP-16-HAND-IDGX2-WAIST | `IDGX2` | `H4WAIST` | `DAG-CardioMet` | WLS + cluster-SE |
| EXP-16-HAND-IDGX2-BMI | `IDGX2` | `H4BMI` | `DAG-CardioMet` | WLS + cluster-SE |
| EXP-16-HAND-IDGX2-BMICLS | `IDGX2` | `H4BMICLS` | `DAG-CardioMet` | Ordered logit |
| EXP-16-HAND-ODGX2-EARN | `ODGX2` | `H5EC1` | `DAG-SES` | Interval regression on bracket midpoints + IPAW (via EXP-16-IPAW-W5) |

Each handoff also pairs with an E-value sensitivity bound (per [TODO.md A7](../TODO.md)) to characterise the unmeasured-confounder strength required to explain the result away.

### EXP-16-SAT-BAL — Saturation-balance table

| Field | Value |
|---|---|
| Status | planned |
| Purpose | Make the within-saturated-schools estimand's external-validity gap concrete. Per the [§5.6 decision](addhealth_synthesis.md#56-identification-assumptions-and-target-estimand) we do not extrapolate; this table lets the reader judge how transportable the network-exposure results are. |
| Method | Survey-weighted (using `GSWGT1`) means and proportions of L0+L1+AHPVT covariates within saturated vs. non-saturated schools, with standardised-mean-difference column for visual scan. |
| Outputs | TBD: `outputs/16_saturation_balance.csv`, `outputs/16_saturation_balance.md` |
| Plots | TBD: side-by-side covariate forest plot |

---

## Deprecated / archived experiments

(none yet)

---

## How to add a new experiment

1. Pick an `EXP-<task>-<short-name>` ID. Keep `<short-name>` descriptive (`HAND-IDGX2-WAIST`, not `H1`).
2. Decide the DAG. If a new DAG is needed, add it to [dag_library.md](dag_library.md) **first**, lock the version, then reference it here.
3. Fill the field table above. The **Estimand wording** field is mandatory — that's the one-sentence prose that appears under any plot or in any brief paragraph that uses this experiment's results. If you can't write the sentence cleanly, the experiment design isn't done.
4. Add row(s) to TODO.md (`A.` for new analysis, `B.` for bug-fix experiments).

---

## Changelog

- **2026-04-25** — File created. EXP-14-COG, EXP-15-MULTI, EXP-11-SENS, EXP-13-VERIFY registered as `complete`; six EXP-16-* experiments scoped as `planned` to align with [TODO.md §A](../TODO.md).

# cardiometabolic-handoff — EXP-16-HAND-IDGX2-{WAIST,BMI,BMICLS} (planned)

Per-outcome formal estimation of the IDGX2 → adult-adiposity handoff pairs
flagged by [multi-outcome-screening](../multi-outcome-screening/README.md).
Three (exposure, outcome) tuples share a single planned DAG (`DAG-CardioMet`)
and live together in this folder; each estimator differs by the outcome's
measurement scale.

| Field | Value |
|---|---|
| Status | planned (stub created Phase 2 of restructure; analytic work not yet started) |
| DAG | [`DAG-CardioMet`](../../reference/dag_library.md) (planned) |
| Estimand wording | Among Add Health respondents in saturated schools (network exposures) or the full W1 in-home cohort (survey exposures), conditional on baseline W1 demographics, W1 affective/somatic state, and AHPVT, exposure *X* is associated with a β-unit change in [outcome: BMI, waist circumference, BMI category] at W4 relative to its baseline-predicted level. **Note:** AHPVT may be over-adjusted for cardiometabolic outcomes; the per-outcome DAG (`DAG-CardioMet`, planned) will refine the adjustment set. |

## Handoff pairs

| ID | Exposure | Outcome | Method |
|---|---|---|---|
| EXP-16-HAND-IDGX2-WAIST  | `IDGX2` | `H4WAIST`   | WLS + cluster-SE on `CLUSTER2` |
| EXP-16-HAND-IDGX2-BMI    | `IDGX2` | `H4BMI`     | WLS + cluster-SE on `CLUSTER2` |
| EXP-16-HAND-IDGX2-BMICLS | `IDGX2` | `H4BMICLS`  | Ordered logit |

Each handoff also pairs with an E-value sensitivity bound (per
[TODO.md A7](../../TODO.md)) to characterise the unmeasured-confounder
strength required to explain the result away.

## Notes

The screening β estimates for these three cells live in
[../multi-outcome-screening/tables/primary/15_multi_outcome_matrix.csv](../multi-outcome-screening/tables/primary/15_multi_outcome_matrix.csv);
the bridge plot is
[../multi-outcome-screening/figures/handoff/15_handoff_forest.png](../multi-outcome-screening/figures/handoff/15_handoff_forest.png).
This experiment will re-estimate under the cardiometabolic-specific DAG
(per-outcome adjustment set, not the screening's uniform `DAG-Cog`).

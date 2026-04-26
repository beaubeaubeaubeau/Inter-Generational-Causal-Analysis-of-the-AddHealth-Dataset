# multi-outcome-screening — EXP-15-MULTI

Multi-outcome causal screen across 12 non-cognitive outcomes (cardiometabolic
W4 + functional / mental-health / SES W5), reusing the same 24 W1 social
exposures and the same DAG-Cog adjustment set as
[cognitive-screening](../cognitive-screening/README.md). This is the
**screening** layer that produces the (exposure, outcome) handoff list fed
into the planned formal-estimation experiments
([cardiometabolic-handoff](../cardiometabolic-handoff/README.md),
[ses-handoff](../ses-handoff/README.md)).

| Field | Value |
|---|---|
| Status | complete |
| Exposure | Same 24 as EXP-14-COG (16 network-derived + 8 survey-derived; see [run.py `EXPOSURES`](run.py)) |
| Outcome | 12 outcomes in 4 groups: cardiometabolic (5: `H4BMI`, `H4SBP`, `H4DBP`, `H4WAIST`, `H4BMICLS`), functional (3: `H5ID1`, `H5ID4`, `H5ID16`), mental health (2: `H5MN1`, `H5MN2`), SES (2: `H5LM5`, `H5EC1`) |
| DAG | **`DAG-Cog` applied uniformly as a screening approximation**, despite three of the per-outcome DAGs (`DAG-CardioMet`, `DAG-SES`, `DAG-Mental`) requiring different adjustment sets. This is the load-bearing screening compromise: ranking is preserved across outcomes but per-outcome point estimates are biased relative to their proper DAG. |
| Method | Same WLS + cluster-SE as EXP-14-COG |
| Adjustment | L0+L1+AHPVT uniformly (incorrect for `H5EC1`/`H5LM5`/`H4BMI` — Task 16 fixes this per-outcome) |
| Restriction | Same saturation rule as EXP-14-COG; W5 outcomes additionally subject to mode restriction implicit in `pwave5.parquet` cells |
| Diagnostics | D1 + D4 only (D2 / D6 / D7 / D8 / D9 inherited from EXP-14-COG; D3 / D5 cognition-only and skipped) |
| Outputs | [tables/primary/15_multi_outcome_matrix.csv](tables/primary/15_multi_outcome_matrix.csv) (288 rows = 24 × 12), [tables/primary/15_multi_outcome.md](tables/primary/15_multi_outcome.md) |
| Plots | [figures/primary/multi_outcome_beta_heatmap.png](figures/primary/multi_outcome_beta_heatmap.png) (z-standardized β grid), [figures/primary/multi_outcome_sig_heatmap.png](figures/primary/multi_outcome_sig_heatmap.png) (−log10 p), [figures/primary/15_per_outcome_pcount.png](figures/primary/15_per_outcome_pcount.png) (breadth), [figures/handoff/15_handoff_forest.png](figures/handoff/15_handoff_forest.png) (4 handoff pairs) |
| Estimand wording | "Same population restrictions as EXP-14-COG; **screening-only** β estimates use the cognitive DAG's adjustment set across all 12 outcomes for cross-outcome ranking comparability. Per-outcome handoffs (EXP-16-*) re-estimate under outcome-specific DAGs." |

## Files

- `run.py` — orchestration: builds the 24×12 (exposure, outcome) matrix using
  D1 (baseline WLS) and D4 (adjustment-set stability), writes the matrix CSV
  and the narrative markdown.
- `figures.py` — cross-outcome figures: per-outcome significance count and
  the four-pair handoff forest plot. Reads `tables/primary/15_multi_outcome_matrix.csv`
  and the cognitive-screen primary matrix from
  `../cognitive-screening/tables/primary/14_screening_matrix.csv`.
- `report.md` — narrative; embeds every chart with a caption + prose
  paragraph linking back to [methods.md](../../reference/methods.md) and
  [glossary.md](../../reference/glossary.md).

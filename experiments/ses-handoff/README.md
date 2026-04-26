# ses-handoff — EXP-16-HAND-ODGX2-EARN (planned)

Per-outcome formal estimation of the ODGX2 → adult earnings handoff pair
flagged by [multi-outcome-screening](../multi-outcome-screening/README.md).
Single (exposure, outcome) tuple under the planned `DAG-SES`; estimator is
interval regression on bracket midpoints to handle the bracketed-income
scale of `H5EC1`, combined with IPAW (via planned EXP-16-IPAW-W5) for W5
attrition.

| Field | Value |
|---|---|
| Status | planned (stub created Phase 2 of restructure; analytic work not yet started) |
| Exposure | `ODGX2` |
| Outcome | `H5EC1` (S4Q1 INCOME PERS EARNINGS [W4–W5]—W5; bracketed-1-13) |
| DAG | [`DAG-SES`](../../reference/dag_library.md) (planned) |
| Method | Interval regression on bracket midpoints + IPAW (via planned EXP-16-IPAW-W5) |
| Sensitivity | E-value bound on the unmeasured-confounder strength required to explain the result away (per [TODO.md A7](../../TODO.md)) |

## Notes

The screening β estimate for this cell lives in
[../multi-outcome-screening/tables/primary/15_multi_outcome_matrix.csv](../multi-outcome-screening/tables/primary/15_multi_outcome_matrix.csv);
the bridge plot is
[../multi-outcome-screening/figures/handoff/15_handoff_forest.png](../multi-outcome-screening/figures/handoff/15_handoff_forest.png).
This experiment will re-estimate under the SES-specific DAG (per-outcome
adjustment set, not the screening's uniform `DAG-Cog`) and substitute the
W5 design weight `GSW5` × IPAW for the screening's `GSWGT4_2`.

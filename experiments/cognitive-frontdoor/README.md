# cognitive-frontdoor — EXP-16-FD-COG (planned)

Front-door decomposition for the AHPVT-cognition path. Sensitivity check on
the trajectory framing used by [cognitive-screening](../cognitive-screening/README.md):
quantifies how much the EXP-14-COG β shifts if AHPVT is on the causal path
from W1 social integration to W4 cognition (the strict mediator reading).

| Field | Value |
|---|---|
| Status | planned (stub created Phase 2 of restructure; analytic work not yet started) |
| Purpose | **Sensitivity check for the trajectory framing**, not a load-bearing alternative model. Quantifies how much the EXP-14-COG β shifts if AHPVT is on the causal path from W1 social integration to W4 cognition (the strict mediator reading). |
| Exposure / outcome | `IDGX2` → `W4_COG_COMP` (highest-priority pair for the front-door check, since IDGX2 has the largest D4 drift) |
| DAG | [`DAG-Cog-FrontDoor`](../../reference/dag_library.md#dag-cog-frontdoor-planned-task-16-sensitivity) (planned) |
| Method | Three-equation front-door: (a) `IDGX2 → AHPVT \| L0+L1`, (b) `AHPVT → W4_COG_COMP \| L0+L1, IDGX2`, (c) total-effect = sum over AHPVT levels |
| Adjustment | L0+L1 (drops AHPVT from the back-door set since AHPVT is now treated as the mediator) |
| Outputs | TBD: `tables/primary/16_frontdoor_cog.csv`, `tables/primary/16_frontdoor_cog.md` |
| Plots | TBD: `figures/primary/16_frontdoor_decomp.png` (bar chart: trajectory β vs. front-door-implied total effect, with the gap as the trajectory caveat magnitude) |
| Estimand wording (when complete) | "Under the strict mediator reading of `AHPVT`, the total effect of `IDGX2` on `W4_COG_COMP` would be β_FD; the trajectory-adjusted estimate from EXP-14-COG is β_traj; the gap β_FD − β_traj is the magnitude by which the trajectory framing under-estimates if mediation is real." |

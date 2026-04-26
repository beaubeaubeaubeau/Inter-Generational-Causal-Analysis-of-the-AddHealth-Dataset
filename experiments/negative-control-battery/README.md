# negative-control-battery — EXP-16-NC (planned)

Replacement battery for the contaminated `HEIGHT_IN` D2 negative-control
outcome. Tests the unmeasured-confounder assumption in `DAG-Cog` against
outcomes that don't share the height ↔ peer-status mechanism.

| Field | Value |
|---|---|
| Status | planned (stub created Phase 2 of restructure; analytic work not yet started) |
| Purpose | Replace the contaminated `HEIGHT_IN` D2 with a battery of NC outcomes that don't share the height ↔ peer-status mechanism. Tests the unmeasured-confounder assumption in `DAG-Cog`. |
| Candidate outcomes | Blood type, age at menarche (or W1 pubertal-development index), hand-dominance, residential stability pre-W1. **Pre-flight required**: confirm public-use availability of each. |
| Exposure | All 24 EXP-14-COG exposures, in the cognition outcome's adjustment set |
| DAG | `DAG-Cog` with each NC outcome substituted for `Y` |
| Method | Same WLS + cluster-SE as EXP-14-COG |
| Estimand wording | Per-NC null: among the cognitive-screening cohort, the W1 social-integration exposures should not predict the negative-control outcome (blood type / age at menarche / hand-dominance / pre-W1 residential stability) under the null of no unmeasured confounding. The estimand is a placebo β (target value 0); a non-zero β indicates an unblocked back-door path. |
| Outputs | TBD: `tables/primary/16_nc_battery.csv`, `tables/primary/16_nc_battery.md` |
| Plots | TBD: NC-failure forest plot per exposure |

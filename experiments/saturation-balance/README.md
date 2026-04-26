# saturation-balance — EXP-16-SAT-BAL (planned)

Saturation-balance table making the within-saturated-schools estimand's
external-validity gap concrete. Per the §5.6 identification decision we do
not extrapolate; this table lets the reader judge how transportable the
network-exposure results are.

| Field | Value |
|---|---|
| Status | planned (stub created Phase 2 of restructure; analytic work not yet started) |
| Purpose | Make the within-saturated-schools estimand's external-validity gap concrete. Per the [identification decision in methods.md §1](../../reference/methods.md#1-identification-assumptions-and-target-estimand) we do not extrapolate; this table lets the reader judge how transportable the network-exposure results are. |
| Method | Survey-weighted (using `GSWGT1`) means and proportions of L0+L1+AHPVT covariates within saturated vs. non-saturated schools, with standardised-mean-difference column for visual scan. |
| Estimand wording | Descriptive estimand only — no causal claim. The estimand is the standardised-mean-difference for each L0+L1+AHPVT covariate between saturated-school and non-saturated-school respondents (using `GSWGT1`), reported with bootstrap-SE 95% CIs. Quantifies the external-validity gap of the within-saturated-schools estimand from `cognitive-screening` and `multi-outcome-screening`. |
| Outputs | TBD: `tables/primary/16_saturation_balance.csv`, `tables/primary/16_saturation_balance.md` |
| Plots | TBD: side-by-side covariate forest plot |

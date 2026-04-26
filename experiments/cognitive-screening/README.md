# Cognitive screening (EXP-14-COG)

| Field | Value |
|---|---|
| Status | complete |
| Exposure | 24 W1 social exposures (16 network-derived + 8 survey-derived); see `EXPOSURES` in [run.py](run.py) |
| Outcome | `W4_COG_COMP` (z-mean of `C4WD90_1`, `C4WD60_1`, `C4NUMSCR`) |
| DAG | [`DAG-Cog`](../../reference/dag_library.md#dag-cog-v10--w1-social-integration--w4-cognitive-outcome) |
| Method | Weighted OLS (`statsmodels.WLS`) with `GSWGT4_2`, cluster-robust SE on `CLUSTER2` (132 PSUs) |
| Adjustment | L0+L1+AHPVT (primary), with L0 and L0+L1 as D4-stability reductions |
| Restriction | **For 16 network exposures: within-saturated-schools only** (positivity = 0 outside; see [methods.md §1](../../reference/methods.md#1-identification-assumptions-and-target-estimand)). For 8 survey exposures: full W1 in-home cohort. |
| Diagnostics | Full D1–D9 battery (see [methods.md §2](../../reference/methods.md#2-causal-screening-diagnostic-battery-d1d9)) |
| Outputs | [tables/primary/14_screening_matrix.csv](tables/primary/14_screening_matrix.csv), [tables/primary/14_shortlist.csv](tables/primary/14_shortlist.csv), [tables/primary/14_screening.md](tables/primary/14_screening.md), [tables/primary/10_regressions.csv](tables/primary/10_regressions.csv), [tables/primary/10_regressions.md](tables/primary/10_regressions.md) |
| Plots | [figures/primary/screening_heatmap.png](figures/primary/screening_heatmap.png) (D1–D9 grid), [figures/primary/adjustment_stability.png](figures/primary/adjustment_stability.png) (D4), [figures/diagnostics/sibling_dissociation.png](figures/diagnostics/sibling_dissociation.png) (D3), [figures/diagnostics/component_consistency.png](figures/diagnostics/component_consistency.png) (D5), [figures/diagnostics/negctrl_failure_grid.png](figures/diagnostics/negctrl_failure_grid.png) (D2 — informational, contaminated NC), plus regression-result figures under [figures/primary/](figures/primary/) |
| Estimand wording | "Among Add Health respondents in saturated schools (network exposures) or the full W1 in-home cohort (survey exposures), conditional on baseline W1 verbal IQ, demographics, and W1 affective/somatic state, exposure *X* is associated with a β-unit change in W4 cognition relative to its baseline-predicted level." |

## Scope

This folder subsumes what was previously tracked as three separate register entries — **EXP-14-COG**, **EXP-11-SENS**, and **EXP-13-VERIFY** — per the restructure decision to collapse meta-analysis artifacts (sensitivity audits and verification packs) into the experiment they audit. EXP-11-SENS and EXP-13-VERIFY were never independent identification claims; they were always meta-analyses of EXP-14-COG. The folder layout reflects that:

- `tables/primary/` and `figures/primary/` — EXP-14-COG screening matrix, shortlist, and the 8 baseline-regression figures.
- `tables/sensitivity/` and `figures/sensitivity/` — EXP-11-SENS audits (collinearity, AHPVT shift, placebo permutation, saturated-school balance, etc.).
- `tables/verification/` and `figures/verification/` — EXP-13-VERIFY (BH-FDR, attrition IPW, negative-control sweeps, DEFF, PSU counts, reserve-code leakage, etc.).
- `figures/diagnostics/` — the D-code diagnostic figures from the screening battery (D2 negative-control grid, D3 sibling, D5 component consistency).

Run `python run.py` to (re)produce all tables; `python figures.py` to (re)produce all PNGs.

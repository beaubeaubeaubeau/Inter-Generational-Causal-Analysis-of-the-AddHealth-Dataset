# popularity-and-substance-use — dark-side of popularity (planned)

Tests whether the same `IDGX2` popularity exposure that yields *protective*
cardiometabolic associations in [`multi-outcome-screening`](../multi-outcome-screening/)
flips sign for substance-use outcomes. A confirmed positive β on substance-use
outcomes paired with negative β on cardiometabolic ones would be a striking
example of outcome-specificity — popularity is health-protective in some
domains and risk-elevating in others. That asymmetry constrains any unified
"social integration → adult health" story.

| Field | Value |
|---|---|
| Status | planned (skeleton only — no analytic results yet) |
| Hypothesis | High W1 in-degree popularity (`IDGX2`) predicts MORE substance-use in adolescence (W4) and adulthood (W5). Inverts the protective cardiometabolic signal. |
| Exposure | `IDGX2` (W1 in-degree, social-network popularity, continuous) |
| Outcomes (W4 substance use) | `H4TO5` (smoking days past 30d, N≈3,515), `H4TO39` (drinking days past 30d, N≈3,553), `H4TO70` (marijuana days past year, N≈1,946), `H4TO65B` (ever marijuana, N≈5,078), `H4TO65C` (ever cocaine, N≈5,086) |
| Outcomes (W5 substance use) | `H5TO2` (smoking days, N≈4,138), `H5TO12` (alcohol days past year, N≈3,701), `H5TO15` (binge days past year, N≈3,465) |
| DAG | [`DAG-DarkSide-Subst`](dag.md) — inherits L0+L1+AHPVT adjustment from `DAG-Cog`; new substance-use outcome arrows. |
| Method | WLS via `analysis.wls:weighted_ols`; `GSWGT4_2` weights for W4 outcomes, `GSW5` (with attrition caveat — see TODO §A3) for W5 outcomes; cluster-robust SE on `CLUSTER2`. |
| Adjustment | Primary: L0+L1+AHPVT (mirror cognitive-screening). Sensitivity: L0 and L0+L1 for D4-style stability. |
| Reserve-code handling | All outcome columns processed through `analysis.cleaning:clean_var` before fitting (per project convention; never paraphrase reserve codes). |
| Sensitivity | (a) Quintile dose-response via `analysis.wls:quintile_dummies` to test whether the substance-use elevation is concentrated in the popularity-tail vs. linear across the distribution. (b) E-value bound via `analysis.sensitivity:evalue` per significant pair (TODO §A7). |
| Predicted result | β > 0 on smoking / drinking / marijuana frequency outcomes; especially elevated in the top quintile (Q5 vs Q1). Confirms the hypothesised inversion. |
| Outputs (planned) | `tables/primary/popularity_subst_matrix.csv`, `tables/primary/popularity_subst.md`, `tables/sensitivity/popularity_subst_quintiles.csv`, `tables/sensitivity/popularity_subst_evalues.csv` |
| Plots (planned) | [figures/primary/outcome_specificity_heatmap.png](figures/primary/outcome_specificity_heatmap.png) (substance-use β vs. cardiometabolic β side-by-side, signed colour map), [figures/primary/popularity_subst_forest.png](figures/primary/popularity_subst_forest.png), [figures/sensitivity/popularity_subst_quintiles.png](figures/sensitivity/popularity_subst_quintiles.png) |
| Estimand wording | "Among Add Health respondents in saturated schools, conditional on baseline W1 verbal IQ, demographics, and W1 affective/somatic state, a one-unit increase in `IDGX2` popularity is associated with a β-unit change in the substance-use outcome (frequency-of-use scale per outcome label)." |

## Pre-flight findings (locked into `run.py`)

The substance-use variable list above is hardcoded from a 2026-04-26 pre-flight
inventory. All eight outcomes have N > 1,900 (W4) or > 3,400 (W5) before
modelling losses; all are valid public-use codebook codes. `clean_var` strips
reserve codes (typically 96/97/98/99 or 6/7/8 depending on the variable
range) per the rules in `scripts/analysis/cleaning.py:VALID_RANGES`.

## Why this experiment exists

The cognitive and cardiometabolic-handoff results frame popularity as a
broadly protective adolescent exposure. A positive substance-use β would be
the cleanest "outcome inversion" the dataset can produce, because:

1. it shares the SAME exposure (`IDGX2`) and the SAME baseline cohort, so
   the contrast is internal to the project — no apples-to-oranges issue;
2. peer-influence theory has a well-known "popular kids drink earlier"
   prediction that the cardiometabolic line ignores;
3. it disciplines any future "social integration is good for you" framing
   in the manuscript narrative.

If the substance-use β is null, the protective interpretation gets stronger.
If it is positive (predicted), the manuscript must shift to a
domain-specific framing.

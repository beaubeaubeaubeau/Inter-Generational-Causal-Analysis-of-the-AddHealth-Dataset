# lonely-at-the-top — popularity × loneliness paradox (planned)

Tests whether the *combination* of high adolescent popularity (`IDGX2`)
AND high adolescent loneliness (`H1FS13`) carries a worse mid-life
signature than either high-popularity alone or high-loneliness alone.
The hypothesised paradox: being well-positioned in the network but
emotionally disconnected within it (the "lonely-at-the-top" condition)
is the worst of both worlds.

| Field | Value |
|---|---|
| Status | planned (skeleton only — no analytic results yet) |
| Hypothesis | Adolescents simultaneously high on `IDGX2` (popularity) and high on `H1FS13` (loneliness) face mid-life cardiometabolic / mental-health outcomes worse than the high-pop-low-lonely or low-pop-high-lonely cells. The interaction term `z(IDGX2) × z(H1FS13)` is significantly non-zero in the *worsening* direction. |
| Exposure (primary) | **Continuous interaction term** `z(IDGX2) × z(H1FS13)` (z-scored within the analytic frame). The primary spec is `IDGX2 + H1FS13 + (z(IDGX2) × z(H1FS13))` so the interaction coefficient is the *adjusted* paradox test. |
| Why not 2x2 | Pre-flight (2026-04-26) confirmed minimum cell N = 73 in the median-split 2x2 of `IDGX2 × H1FS13`, well below the project's N≥150 floor. The 2x2 is therefore reported only for descriptive cell means under "Sensitivity"; the design point estimate is the continuous interaction. |
| Outcomes | `H4BMI`, `H4WAIST` (cardiometabolic, W4), `H5MN1`, `H5MN2` (mental health, W5), `H5ID1` (functional / self-rated health, W5) |
| DAG | [`DAG-Lonely-Top`](dag.md) — inherits L0+L1+AHPVT adjustment, with the loneliness × popularity interaction as the new structural element. |
| Method | WLS via `analysis.wls:weighted_ols` with the three exposure terms (`IDGX2`, `H1FS13`, `IDGX2_x_H1FS13`); `GSWGT4_2` for W4, `GSW5` for W5; cluster-robust SE on `CLUSTER2`. The interaction coefficient β₃ is the headline test. |
| Adjustment | L0+L1+AHPVT primary, with L0 and L0+L1 stability cuts. |
| Sensitivity | (a) Descriptive 4-cell weighted means (median-split) reported for narrative purposes — explicitly flagged as under-powered per the pre-flight (min cell N = 73 < 150). (b) Continuous-by-continuous interaction surface plot for visual diagnostic. |
| Outputs (planned) | `tables/primary/lonely_top_matrix.csv`, `tables/primary/lonely_top.md`, `tables/sensitivity/lonely_top_2x2_descriptive.csv`, `tables/sensitivity/lonely_top_interaction_surface.csv` |
| Plots (planned) | [figures/primary/paradox_interaction.png](figures/primary/paradox_interaction.png), [figures/primary/lonely_top_forest.png](figures/primary/lonely_top_forest.png), [figures/sensitivity/lonely_top_4cell_descriptive.png](figures/sensitivity/lonely_top_4cell_descriptive.png) |
| Estimand wording | "Among Add Health respondents in saturated schools, conditional on baseline W1 verbal IQ, demographics, and W1 affective/somatic state, *and* on the main effects of `IDGX2` and `H1FS13`, a one-SD-by-one-SD increase in the (popularity, loneliness) joint position is associated with a β-unit change in the outcome." |

## Pre-flight (locked into `run.py`)

A 2026-04-26 pre-flight tested the median-split 2x2 of `IDGX2 × H1FS13`
within the W4 saturated-school analytic frame. **Minimum cell N = 73**,
versus the project floor of N ≥ 150 per [methods.md](../../reference/methods.md)
positivity rules. The 2x2 design was therefore *abandoned* for
identification purposes; the experiment falls back to a continuous
interaction term. The 2x2 cell means are still reported descriptively
because they are the most intuitive paradox visual, but they are
explicitly flagged as informational rather than inferential.

## Why this experiment exists

If `IDGX2 → outcome` is uniformly protective (the cardiometabolic story)
and `H1FS13 → outcome` is uniformly harmful (loneliness literature),
then the additive prediction is "popular-and-lonely cancels out". The
paradox claim says this cancellation does NOT happen — the joint
condition is unique. A non-zero interaction β₃ is the cleanest way to
test that claim, with the additional advantage that it remains
identified even in cell counts too thin for stratified estimation.

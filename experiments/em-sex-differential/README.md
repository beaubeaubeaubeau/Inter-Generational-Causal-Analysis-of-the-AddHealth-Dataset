# EM-Sex-Differential — Effect modification of `IDGX2` by `BIO_SEX`

| Field | Value |
|---|---|
| Status | scaffold (not run) |
| Hypothesis | Peer status policing of body weight is stronger for girls than for boys (sex-asymmetric). The W1 popularity (`IDGX2`) effect on adult cardiometabolic outcomes is **larger in absolute magnitude** for female respondents. Mental-health outcomes are a secondary, exploratory test of the same modifier. |
| Exposure | `IDGX2` (W1 in-degree, continuous) **interacted with** `BIO_SEX` (binary, 1=male / 2=female; coded as `male = (BIO_SEX == 1)` for the regression) |
| Outcomes | **Primary (cardiometabolic):** `H4BMI`, `H4WAIST`, `H4BMICLS`. **Secondary (mental health):** `H5MN1`, `H5MN2`. |
| Method | **Primary:** WLS via `analysis.wls.weighted_ols` with explicit `IDGX2 × male` interaction term, cluster-robust on `CLUSTER2`, weighted by `GSWGT4_2` (cardiometabolic) or `GSW5` (mental-health, placeholder until IPAW). **Robustness:** bias-corrected nearest-neighbour matching via `analysis.matching.match_ate_bias_corrected` for top-quintile-`IDGX2` vs bottom-quintile-`IDGX2`, **stratified by sex** (one matching contrast for boys, one for girls; no matching across sexes). |
| Estimand wording | Among Add Health respondents in saturated schools, conditional on the per-outcome adjustment set (DAG-CardioMet for cardiometabolic; DAG-Mental for `H5MN1`/`H5MN2`), the **interaction coefficient** β_{IDGX2 × male} is the additive change in the marginal effect of a one-unit increase in `IDGX2` going from female (`male=0`) to male (`male=1`). The hypothesis predicts β_{IDGX2 × male} differs from zero in the direction implied by greater female sensitivity. |
| DAG | [`DAG-EM-Sex`](dag.md). Inherits `DAG-CardioMet` for cardiometabolic outcomes and `DAG-Mental` for `H5MN1`/`H5MN2`. Adds an explicit `IDGX2 × BIO_SEX` product term as the estimand of interest. `BIO_SEX` is **already in the adjustment set** as L0; the interaction coefficient is identifiable. |
| Sample frame | Saturated-school sub-cohort (network exposures require `IDGX2` to be defined). W4 frame (`analytic_w4.parquet`) for cardiometabolic outcomes; W4 frame with attached `H5MN1`/`H5MN2` for mental-health outcomes. |
| Notes | Sex is binary so the interaction is fully captured by the product term; no need for tertile-ised contrasts as in [`em-compensatory-by-ses`](../em-compensatory-by-ses/). Both sex-stratified subgroup forests AND the single-coefficient interaction forest are reported (see [`figures.py`](figures.py)). The matching contrast is **stratified by sex** rather than restricted to one sex, because both directions of the hypothesis (boys + girls) are theoretically interesting and overlap is plausible within each sex. |

## Files

- [`dag.md`](dag.md) — DAG-EM-Sex, mermaid diagram, adjustment set, weak points, index entry.
- [`run.py`](run.py) — analysis orchestration: WLS interaction fits per outcome, sex-stratified matching, sensitivity.
- [`figures.py`](figures.py) — interaction-coefficient forest, sex-stratified subgroup forests, sex-stratified dose-response.
- [`report.md`](report.md) — narrative with TBD placeholders.
- [`tests/test_smoke.py`](tests/test_smoke.py) — smoke tests for the analysis primitives.
- `tables/` — primary, sensitivity, verification, diagnostics, handoff CSVs.
- `figures/` — same five sub-folder buckets as tables.

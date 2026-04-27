# EM-Compensatory-by-SES — Effect modification of `IDGX2` by `PARENT_ED`

| Field | Value |
|---|---|
| Status | scaffold (not run) |
| Hypothesis | Low-SES adolescents benefit more from peer popularity than high-SES adolescents — network capital substitutes for missing family capital. The effect of W1 popularity (`IDGX2`) on adult cardiometabolic and SES outcomes is **larger in absolute magnitude** at low `PARENT_ED`. |
| Exposure | `IDGX2` (W1 in-degree, continuous) **interacted with** `PARENT_ED` (parental education, ordinal 0–6) |
| Outcomes | 5 outcomes split across two domains: cardiometabolic (`H4BMI`, `H4WAIST`, `H4BMICLS`) and SES (`H5LM5`, `H5EC1`) |
| Method | **Primary:** WLS via `analysis.wls.weighted_ols` with explicit `IDGX2 × PARENT_ED` interaction term, cluster-robust on `CLUSTER2`, weighted by `GSWGT4_2` (W4) or `GSW5` (W5). **Robustness:** bias-corrected nearest-neighbour matching via `analysis.matching.match_ate_bias_corrected` for a binary subgroup contrast (top-quintile-`IDGX2` vs bottom-quintile-`IDGX2`) **within** the bottom tertile of `PARENT_ED`. **(This is the first use of matching anywhere in the project.)** |
| Estimand wording | Among Add Health respondents in saturated schools, conditional on the per-outcome adjustment set (DAG-CardioMet for cardiometabolic outcomes, DAG-SES for SES outcomes), and assuming linearity of the `IDGX2`-by-`PARENT_ED` interaction on the outcome scale, the **interaction coefficient** β_{IDGX2 × PARENT_ED} is the change in the marginal effect of a one-unit increase in `IDGX2` per one-unit increase in `PARENT_ED`. The hypothesis predicts β_{IDGX2 × PARENT_ED} > 0 for "bad" outcomes (BMI, waist) and < 0 for desirable outcomes (work, earnings) when `IDGX2` is protective at low SES. |
| DAG | [`DAG-EM-SES`](dag.md). Inherits the per-outcome adjustment set: `DAG-CardioMet` for cardiometabolic outcomes, `DAG-SES` for SES outcomes. Adds an explicit `IDGX2 × PARENT_ED` product term as the estimand of interest. `PARENT_ED` is **already in the adjustment set** as L0; the interaction coefficient is identifiable provided the no-unmeasured-effect-modifier assumption holds (see weak points). |
| Sample frame | Saturated-school sub-cohort (network exposures require `IDGX2` to be defined). Cardiometabolic outcomes: W4 frame (`analytic_w4.parquet`). SES outcomes: also W4 frame for `H5LM5` / `H5EC1` linkage; weights are `GSWGT4_2` for screening-style estimates and `GSW5` × IPAW(W4 → W5) for the SES outcomes per `DAG-SES` (planned, not yet implemented in this scaffold). |
| Notes | The matching-robustness step is intentionally restricted to the **bottom-tertile-`PARENT_ED`** sub-population: it estimates "among low-SES kids, what is the ATE of being a top-quintile-popular adolescent versus a bottom-quintile-popular adolescent on the chosen outcome?" The contrast is a sharp local test of the substitution hypothesis. We do not run matching in the high-SES tertile because the hypothesis predicts a near-null effect there (negative result is uninformative under matching's local-overlap assumption). Sensitivity bounds: E-value via `analysis.sensitivity.evalue` is computed on the interaction coefficient itself (treating the within-stratum risk-ratio analogue as the input). |

## Files

- [`dag.md`](dag.md) — DAG-EM-SES, mermaid diagram, adjustment set, weak points, index entry.
- [`run.py`](run.py) — analysis orchestration: WLS interaction fits per outcome, quintile dose-response within tertile, matching contrast.
- [`figures.py`](figures.py) — interaction-coefficient forest plot, subgroup-stratified β forest, dose-response panels.
- [`report.md`](report.md) — narrative with TBD placeholders.
- [`tests/test_smoke.py`](tests/test_smoke.py) — smoke tests for the analysis primitives.
- `tables/` — primary, sensitivity, verification, diagnostics, handoff CSVs.
- `figures/` — same five sub-folder buckets as tables.

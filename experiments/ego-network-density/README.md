# ego-network-density — EXP-EGODEN

Ego-network-density experiment, framed against Burt's structural-holes
hypothesis: high ego-network density (closed triads, redundant ties)
predicts mental-health *protection* through close-tie social support, while
low density (brokerage / open triads) predicts SES *advantage* through
non-redundant information access. Methodologically, the load-bearing move
is **conditioning on egonet size** (`REACH3`) so each density β is
interpretable as "density at constant network size" — the structural-holes
literature is otherwise easily confounded by sheer network breadth.

| Field | Value |
|---|---|
| Status | planned |
| Exposure | Four W1 ego-network-density measures: `RCHDEN` (reach-density), `ESDEN` (ego-send density), `ERDEN` (ego-receive density), `ESRDEN` (ego send-or-receive density). All from the W1 network file (`w1network.parquet`); already on `analytic_w4.parquet`. |
| Outcome | Focused 6: mental health (`H5MN1`, `H5MN2`, `H5ID16`); SES (`H5LM5`, `H5EC1`); cognitive (`W4_COG_COMP`). Cardiometabolic and the other functional outcomes are deliberately excluded — the structural-holes hypothesis predicts opposing signs in mental-health vs. SES specifically; cardiometabolic is downstream of both and would dilute the contrast. |
| DAG | [`DAG-EgoNet`](dag.md) — per-outcome inheritance with **`REACH3` added to every adjustment set** as the size-control covariate. The estimand is explicitly "density holding egonet size fixed," which is the only causally-coherent reading of the structural-holes hypothesis. Any β reported without `REACH3` conditioning is structural-confounded. |
| Method | Per-outcome WLS (`weighted_ols`) with `GSWGT4_2` and cluster-robust SE on `CLUSTER2`. The four density exposures are fit in **separate** regressions (each with `REACH3` plus the per-outcome DAG covariates) — the four are highly collinear by construction (overlap in their numerator/denominator), so a joint fit is uninterpretable. |
| Adjustment | Per-outcome inheritance: `DAG-Cog v1.0` (L0+L1+AHPVT) for `W4_COG_COMP`; `DAG-Mental` (L0+L1) for `H5MN1`/`H5MN2`/`H5ID16`; `DAG-SES` (L0+L1, no AHPVT) for `H5LM5`/`H5EC1`. **All adjustment sets additionally include `REACH3`** per the size-conditioning estimand. |
| Restriction | Within-saturated-schools (positivity = 0 outside; same rule as cognitive-screening). W5 outcomes attach via `load_outcome`. |
| Sensitivity | (1) Quintile dose-response per density exposure (`quintile_dummies`, with linear-trend test on the integer quintile); (2) E-value per significant β (`analysis.sensitivity:evalue`); (3) **No-REACH3 negative parallel** — refit primary spec without `REACH3` to demonstrate the size confound and quantify the size-controlled vs. raw-density bias. |
| Outputs | `tables/primary/egoden_primary.csv` (24 rows = 4 exposures × 6 outcomes), `tables/primary/egoden_primary.md`, `tables/sensitivity/egoden_quintile.csv`, `tables/sensitivity/egoden_evalue.csv`, `tables/sensitivity/egoden_no_reach3.csv`. |
| Plots | `figures/primary/egoden_beta_heatmap.png` (4 × 6 standardized-β heatmap with significance markers), `figures/sensitivity/egoden_size_conditioning.png` (REACH3-vs-no-REACH3 paired bars to make the size-confound visible). |
| Estimand wording | "Among Add Health respondents in saturated schools, conditional on each outcome's per-DAG adjustment set **and on `REACH3` (egonet size)**, a one-unit increase in density measure *X* is associated with a β-unit change in outcome *Y*. The conditioning on `REACH3` makes the estimand 'density at constant network size'; β estimates without this conditioning are structural-holes-incompatible." |
| Notes | The four density exposures are deliberately fit in parallel (separate regressions) rather than jointly; their construction overlaps and a joint fit would yield uninterpretable residualised coefficients. The `REACH3`-conditioning is the load-bearing methodological move per user feedback — make it explicit in the report. |

## Files

- `run.py` — orchestration: load `analytic_w4.parquet`, attach W5 outcomes, build per-outcome adjustment sets per `DAG-EgoNet` (always with `REACH3`), fit WLS per (density-exposure, outcome) cell, write primary + sensitivity tables.
- `figures.py` — primary heatmap and the size-conditioning sensitivity bar pair.
- `report.md` — narrative.
- `tests/test_smoke.py` — pytest smoke test.

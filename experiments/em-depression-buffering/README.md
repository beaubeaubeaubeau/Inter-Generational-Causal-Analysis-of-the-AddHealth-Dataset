# EM-Depression-Buffering — Effect modification of `IDGX2` by `CESD_SUM`

| Field | Value |
|---|---|
| Status | scaffold (not run) |
| Hypothesis | Peer popularity buffers pre-existing depression. Adolescents with higher W1 depressive symptoms (`CESD_SUM`) gain *more* from W1 popularity (`IDGX2`) on adult mental-health outcomes than non-depressed adolescents do. The interaction coefficient β_{IDGX2 × CESD_SUM} is signed in the buffering direction (e.g., positive for the "currently feel in control" Likert item `H5MN1`, where higher = better). |
| Exposure | `IDGX2` (W1 in-degree, continuous) **interacted with** `CESD_SUM` (W1 CES-D 19-item sum, continuous 0–57). |
| Outcomes | 3 W5 mental-health outcomes: `H5MN1` (S13Q1 LAST MO NO CNTRL IMPORT THINGS), `H5MN2` (S13Q2 LAST MO CONFID HANDLE PERS PBMS), `H5ID1` (S5Q1 HOW IS GEN PHYSICAL HEALTH). |
| Method | **Primary:** WLS via `analysis.wls.weighted_ols` with explicit `IDGX2 × CESD_SUM` interaction term, cluster-robust on `CLUSTER2`, weighted by `GSWGT4_2` (placeholder until IPAW(W4→W5) lands). **Two specifications run side-by-side per outcome (D9 collider check):** (a) **conservative** — `CESD_SUM` retained in the main-effects adjustment set AND used as the moderator in the interaction; (b) **clean** — `CESD_SUM` dropped from the main-effects set when used as the moderator (avoids collider double-use). The two specs answer different identification questions; both are reported in the primary table. |
| Estimand wording | Among Add Health respondents in saturated schools, conditional on the per-outcome adjustment set, β_{IDGX2 × CESD_SUM} is the additive change in the marginal effect of a one-unit increase in `IDGX2` per one-unit increase in `CESD_SUM`. The buffering hypothesis predicts β_{IDGX2 × CESD_SUM} > 0 for the W5 mental-health outcomes (assuming higher = better Likert orientation) — popularity helps more for adolescents who start out more depressed. |
| DAG | [`DAG-EM-Dep`](dag.md). Inherits Mental-DAGs from `multi-outcome-screening/dag.md`. **`CESD_SUM` appears in BOTH the L1 adjustment set AND as the moderator** — this is the load-bearing identification issue documented in `dag.md` §"D9 collider check." |
| Sample frame | Saturated-school sub-cohort (network exposure `IDGX2` requires saturation). Outcomes from W5; weights = `GSWGT4_2` for cross-experiment comparability with the screening battery (placeholder for `GSW5 × IPAW`). |
| Sensitivity | (1) Within-tertile-`CESD_SUM` quintile dose-response of `IDGX2` (linearity diagnostic for the linear-in-`CESD_SUM` interaction); (2) Bias-corrected nearest-neighbour matching of top-`IDGX2`-quintile vs bottom-`IDGX2`-quintile **within** the top tertile of `CESD_SUM` — the sharpest local test of the buffering hypothesis where it should be strongest; (3) E-value on the interaction coefficient via `analysis.sensitivity.evalue`. |
| Outputs | `tables/primary/em_dep_interaction.csv` (one row per outcome × spec — 6 rows), `tables/primary/em_dep_stratified_betas.csv` (one row per outcome × CESD tertile), `tables/sensitivity/em_dep_quintile_by_tertile.csv`, `tables/sensitivity/em_dep_evalue.csv`, `tables/handoff/em_dep_matching_high_cesd.csv`. |
| Plots | `figures/primary/em_dep_interaction_forest.png` (forest of β_{IDGX2 × CESD_SUM} per outcome × spec), `figures/primary/em_dep_subgroup_forest.png` (per-outcome panel of β_IDGX2 within each `CESD_SUM` tertile), `figures/sensitivity/em_dep_dose_response_panels.png` (linearity diagnostic). |
| Notes | The D9 collider double-use of `CESD_SUM` is the methodologically novel issue this experiment surfaces. The conservative spec (a) is the screening-style choice — keep `CESD_SUM` in the L1 adjustment set as a confounder regardless of its moderator role; the clean spec (b) is theoretically preferred because conditioning on a variable AND interacting it AND using it as a confounder simultaneously can introduce subtle bias when the moderator is itself a downstream collider on a backdoor path. The two-spec comparison is what makes the buffering claim defensible. |

## Files

- [`dag.md`](dag.md) — DAG-EM-Dep, the CESD double-use issue, weak points, index entry.
- [`run.py`](run.py) — analysis orchestration: WLS interaction fits per outcome (both specs), tertile-stratified fits, matching contrast in high-CESD subset.
- [`figures.py`](figures.py) — interaction-coefficient forest plot, subgroup-stratified β forest, dose-response panels.
- [`report.md`](report.md) — narrative with TBD placeholders.
- [`tests/test_smoke.py`](tests/test_smoke.py) — smoke tests for the analysis primitives.
- `tables/` — primary, sensitivity, handoff CSVs.
- `figures/` — primary + sensitivity figure buckets.

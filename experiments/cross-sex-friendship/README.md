# cross-sex-friendship — sex × friend-sex stratification (planned)

Tests whether having a best friend of the *opposite* sex in adolescence
leaves a different mid-life signature than same-sex friendship — and
whether that contrast varies by respondent sex. The directional claim:
girls with male best friends gain instrumental access (information,
status), boys with female best friends gain emotional disclosure space;
neither pattern is captured by the standard same-sex friendship literature.

| Field | Value |
|---|---|
| Status | planned (skeleton only — no analytic results yet) |
| Hypothesis | Cross-sex best-friend ties (`HAVEBMF` for girls, `HAVEBFF` for boys) carry a different mid-life-outcome signature than same-sex ties (`HAVEBFF` for girls, `HAVEBMF` for boys). The contrast is asymmetric: instrumental gains for girls-with-male-friends, emotional gains for boys-with-female-friends. |
| Exposure stratifications | Two 4-cell stratifications, 8 cells total: (a) `BIO_SEX × HAVEBMF` (have a male best friend, by sex) and (b) `BIO_SEX × HAVEBFF` (have a female best friend, by sex). |
| Outcomes | All 13 outcomes from cognitive-screening + multi-outcome-screening: `W4_COG_COMP`, `H4BMI`, `H4SBP`, `H4DBP`, `H4WAIST`, `H4BMICLS`, `H5MN1`, `H5MN2`, `H5ID1`, `H5ID4`, `H5ID16`, `H5LM5`, `H5EC1`. |
| DAG | [`DAG-CrossSex`](dag.md) — inherits per-outcome adjustment sets from existing experiments (DAG-Cog for cognition, DAG-CardioMet for cardiometabolic, DAG-SES for SES, etc.). |
| Method | WLS via `analysis.wls:weighted_ols` *within each cell*, with appropriate per-outcome weights and cluster-robust SE on `CLUSTER2`. The per-outcome forest plot has 8 rows × 13 outcomes = **104 cell estimates**; the report narrows to cells with the strongest contrasts. |
| Adjustment | Per-outcome (inherited): cognition uses L0+L1+AHPVT; cardiometabolic uses DAG-CardioMet adjustment; SES uses L0+L1 (no AHPVT, per DAG-SES). |
| Sensitivity | Re-fit each cell using `FRIEND_*` derived friendship-grid exposures (e.g. `FRIEND_N_NOMINEES`, `FRIEND_DISCLOSURE_ANY`) as alternative exposure-coding. Robustness test against the simplification of "have a best friend of sex S" as binary. |
| Outputs (planned) | `tables/primary/cross_sex_matrix.csv` (long-format: 8 cells × 13 outcomes), `tables/primary/cross_sex.md`, `tables/sensitivity/cross_sex_friendcoding_alt.csv` |
| Plots (planned) | [figures/primary/cross_sex_forest.png](figures/primary/cross_sex_forest.png) (per-outcome 4-cell forest, faceted by stratification scheme), [figures/primary/cross_sex_heatmap.png](figures/primary/cross_sex_heatmap.png) (8 × 13 signed-β heatmap) |
| Estimand wording | "Within sex × friend-sex cell *c*, conditional on the per-outcome adjustment set, having a best friend of the indicated sex (vs. not) is associated with a β-unit change in outcome `Y`. The contrast of interest is between cross-sex and same-sex cells *within sex*." |

## Why this experiment exists

The 24-exposure screening treats `HAVEBMF` and `HAVEBFF` as separate
exposures with main-effect coefficients pooled across sex. That collapses
exactly the asymmetry this experiment is designed to surface: the
hypothesis is fundamentally about a *sex × friend-sex* interaction.
Stratifying makes that interaction visible without pretending the cell-N
budget supports a 4-way test in a single regression.

## Pre-flight expectations (locked into `run.py`)

- Cell N for the four primary cells (`female × HAVEBMF=0/1`,
  `male × HAVEBFF=0/1`) is expected to be in the low thousands, well
  above the project N ≥ 150 floor. Per-cell positivity is therefore
  not a concern.
- Outcome columns are processed through `clean_var` (per project
  convention; never paraphrase reserve codes).
- The two stratifications are reported side by side because they are
  *not* redundant — a respondent can have both a male AND a female best
  friend, neither, or one of each. Cross-tab of `HAVEBMF × HAVEBFF`
  within each sex is reported as a sanity-check table.

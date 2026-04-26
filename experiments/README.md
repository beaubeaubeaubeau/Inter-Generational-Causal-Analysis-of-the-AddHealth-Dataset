# Experiments

One folder per experiment under this directory. Each folder is self-contained: a `README.md` with the standard field table, `run.py` for the analytic orchestration, `figures.py` for plotting, `report.md` for the narrative (every chart explained inline), `figures/` (PNGs grouped by sub-folder: `primary/`, `sensitivity/`, `verification/`, `diagnostics/`, `handoff/`), and `tables/` (CSVs and markdown grouped the same way).

## Hypothesis: cognitive trajectory

| Experiment | Status | Exposure | Outcome | Method | Notes |
|---|---|---|---|---|---|
| [cognitive-screening](cognitive-screening/) | complete | 24 W1 social exposures (16 network + 8 survey) | `W4_COG_COMP` (z-mean of `C4WD90_1`, `C4WD60_1`, `C4NUMSCR`) | WLS + cluster-SE on `CLUSTER2`; full D1-D9 diagnostic battery; sensitivity audits; verification (BH-FDR, attrition IPW, NC, DEFF) | Subsumes prior EXP-14-COG, EXP-11-SENS, EXP-13-VERIFY (collapsed per restructure) |
| [cognitive-frontdoor](cognitive-frontdoor/) | planned | `IDGX2` | `W4_COG_COMP` | Three-equation front-door decomposition (sensitivity check on the AHPVT trajectory framing of EXP-14-COG) | Stub only; planned `DAG-Cog-FrontDoor` |

## Hypothesis: multi-outcome (cardiometabolic / functional / mental / SES)

| Experiment | Status | Exposure | Outcome | Method | Notes |
|---|---|---|---|---|---|
| [multi-outcome-screening](multi-outcome-screening/) | complete | Same 24 W1 social exposures as cognitive-screening | 12 outcomes: 5 cardiometabolic (`H4BMI`, `H4SBP`, `H4DBP`, `H4WAIST`, `H4BMICLS`), 3 functional (`H5ID1`, `H5ID4`, `H5ID16`), 2 mental (`H5MN1`, `H5MN2`), 2 SES (`H5LM5`, `H5EC1`) | WLS + cluster-SE; **`DAG-Cog` applied uniformly as a screening approximation** (preserves cross-outcome ranking but biases per-outcome point estimates relative to each outcome's proper DAG) | Identifies four (exposure, outcome) handoff pairs for formal estimation |

## Hypothesis: cardiometabolic (formal estimation)

| Experiment | Status | Exposure → Outcome | Method | Notes |
|---|---|---|---|---|
| [cardiometabolic-handoff](cardiometabolic-handoff/) | planned | `IDGX2` → `H4WAIST`; `IDGX2` → `H4BMI`; `IDGX2` → `H4BMICLS` | WLS + cluster-SE on `CLUSTER2` for `H4WAIST` and `H4BMI`; ordered logit for `H4BMICLS` | Per-outcome DAG `DAG-CardioMet` (planned); E-value sensitivity bound per [TODO.md A7](../TODO.md) |

## Hypothesis: SES (formal estimation)

| Experiment | Status | Exposure → Outcome | Method | Notes |
|---|---|---|---|---|
| [ses-handoff](ses-handoff/) | planned | `ODGX2` → `H5EC1` (W4-W5 personal earnings, bracketed 1-13) | Interval regression on bracket midpoints + IPAW (W4 → W5 attrition, via planned EXP-16-IPAW-W5), with `GSW5` × IPAW substituted for the screening's `GSWGT4_2` | Per-outcome DAG `DAG-SES` (planned); E-value sensitivity bound per [TODO.md A7](../TODO.md) |

## Cross-cutting / methodological

| Experiment | Status | Purpose |
|---|---|---|
| [negative-control-battery](negative-control-battery/) | planned | Replace contaminated `HEIGHT_IN` D2 negative-control outcome with a battery of clean NC outcomes (blood type, age at menarche or W1 pubertal-development index, hand-dominance, residential stability pre-W1; pre-flight required to confirm public-use availability). Tests the unmeasured-confounder assumption in `DAG-Cog`. |
| [saturation-balance](saturation-balance/) | planned | Survey-weighted (`GSWGT1`) covariate balance table for L0 + L1 + AHPVT inside vs. outside saturated schools, with a standardized-mean-difference column. Quantifies the external-validity gap of the within-saturated-schools estimand used by the network exposures. |

## Conventions

- **Naming.** Lowercase, hyphenated, no caps. Hypothesis-prefix or domain-prefix + descriptive scope-suffix (e.g. `cognitive-screening`, `cardiometabolic-handoff`).
- **Adding an experiment.** See ["Adding a new experiment" in the top-level README](../README.md#adding-a-new-experiment). Mandatory order: lock the DAG in [`reference/dag_library.md`](../reference/dag_library.md) first, then write the field-table `README.md` with the estimand wording, then any analytic code.
- **Chart-explanation convention.** Every chart in any experiment's `report.md` includes (1) a 1-3 sentence descriptive caption immediately under the image, (2) a prose paragraph explaining why the chart matters, how to read it, and which method produced it, and (3) method names linked on first use within the report to [`../reference/methods.md`](../reference/methods.md) or [`../reference/glossary.md`](../reference/glossary.md).
- **Meta-analysis collapse.** Sensitivity audits and verification packs are not separate experiments — they live as artifacts inside the experiment they sensitize. For example, the EXP-11-SENS audits and EXP-13-VERIFY pack live as `cognitive-screening/figures/sensitivity/`, `cognitive-screening/tables/sensitivity/`, `cognitive-screening/figures/verification/`, and `cognitive-screening/tables/verification/`.

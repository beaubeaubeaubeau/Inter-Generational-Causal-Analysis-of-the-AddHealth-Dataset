# Experiments

One folder per experiment under this directory. Each folder is self-contained: a `README.md` with the standard field table, `run.py` for the analytic orchestration, `figures.py` for plotting, `report.md` for the narrative (every chart explained inline), `figures/` (PNGs grouped by sub-folder: `primary/`, `sensitivity/`, `verification/`, `diagnostics/`, `handoff/`), and `tables/` (CSVs and markdown grouped the same way).

## Hypothesis: cognitive trajectory

| Experiment | Status | Exposure | Outcome | Method | Notes |
|---|---|---|---|---|---|
| [cognitive-screening](cognitive-screening/) | complete | 24 W1 social exposures (16 network + 8 survey) | `W4_COG_COMP` (z-mean of `C4WD90_1`, `C4WD60_1`, `C4NUMSCR`) | WLS + cluster-SE on `CLUSTER2`; full D1-D9 diagnostic battery; sensitivity audits; verification (BH-FDR, attrition IPW, NC, DEFF) | Subsumes prior EXP-14-COG, EXP-11-SENS, EXP-13-VERIFY (collapsed per restructure) |
| [cognitive-frontdoor](cognitive-frontdoor/) | **complete (2026-04-27)** | `IDGX2`, `ODGX2`, `BCENT10X` | `W4_COG_COMP` | Three-equation Pearl front-door (`analysis.frontdoor`) treating `AH_PVT` as mediator; sensitivity bound on the trajectory β | All 3 exposures show ~70% trajectory β reduction under the strict-mediator reading (IDGX2 −74%, ODGX2 −69%, BCENT10X −73%). Reported as a sensitivity bound, not a competing primary estimate. Supports top-level claim **C3**. |

## Hypothesis: multi-outcome (cardiometabolic / functional / mental / SES)

| Experiment | Status | Exposure | Outcome | Method | Notes |
|---|---|---|---|---|---|
| [multi-outcome-screening](multi-outcome-screening/) | complete | Same 24 W1 social exposures as cognitive-screening | 12 outcomes: 5 cardiometabolic (`H4BMI`, `H4SBP`, `H4DBP`, `H4WAIST`, `H4BMICLS`), 3 functional (`H5ID1`, `H5ID4`, `H5ID16`), 2 mental (`H5MN1`, `H5MN2`), 2 SES (`H5LM5`, `H5EC1`) | WLS + cluster-SE; **`DAG-Cog` applied uniformly as a screening approximation** (preserves cross-outcome ranking but biases per-outcome point estimates relative to each outcome's proper DAG) | Identifies four (exposure, outcome) handoff pairs for formal estimation |

## Hypothesis: cardiometabolic (formal estimation)

| Experiment | Status | Exposure → Outcome | Method | Notes |
|---|---|---|---|---|
| [cardiometabolic-handoff](cardiometabolic-handoff/) | **complete (2026-04-27)** | `IDGX2` → `H4WAIST`; `IDGX2` → `H4BMI`; `IDGX2` → `H4BMICLS` | WLS + cluster-SE for waist/BMI; **ordered logit** (via `analysis.ordered_logit`) for BMICLS; **DR-AIPW Q5-vs-Q1** binarised contrast as doubly-robust check; E-value (Chinn-2000) + **explained-away contour curve** (handoff convention) + η-tilt sweep | All 3 outcomes sign-stable, CI excludes 0 in DR-AIPW. E-values 1.35–1.49 (waist/BMI) and 2.03 on the DR-AIPW row. Supports top-level claim **C1**. |

## Hypothesis: SES (formal estimation)

| Experiment | Status | Exposure → Outcome | Method | Notes |
|---|---|---|---|---|
| [ses-handoff](ses-handoff/) | **complete (2026-04-27)** | `ODGX2` → `H5EC1` (W4-W5 personal earnings, bracketed 1-13) | THREE estimators side-by-side per cell: WLS (linear-on-bracket baseline), **interval regression** on bracket midpoints (`analysis.interval_regression`) layered on `GSW5` × **IPAW** (`analysis.ipw`), and **DR-AIPW Q5-vs-Q1** doubly-robust check | All 3 estimators sign-coherent. WLS β = +0.080 bracket-units (E 1.35); interval+IPAW β = +1.09 k$/unit (E 1.28); DR-AIPW Q5-vs-Q1 ATE = +6.65 k$ (E **2.03**). Supports top-level claim **C4**. |

## Hypothesis: type-of-tie (Phase 6 mechanism experiments)

| Experiment | Status | Exposure | Outcome | Method | Notes |
|---|---|---|---|---|---|
| [popularity-vs-sociability](popularity-vs-sociability/) | planned | `IDGX2` (popularity), `ODGX2` (sociability) | all 13 | WLS β per cell + paired-bootstrap (β_in − β_out) per outcome with cluster-resampling on `CLUSTER2` | Tests asymmetric mechanism prediction: popularity dominates status outcomes; sociability dominates agency outcomes |
| [ego-network-density](ego-network-density/) | planned | `RCHDEN`, `ESDEN`, `ERDEN`, `ESRDEN` (4 ego-density measures) | mental health + SES + cognitive subset | Size-conditioned WLS (include `REACH3` as covariate); estimand is "density at constant network size" | Burt structural-holes hypothesis: high density → mental health protection; low density → SES advantage |
| [friendship-quality-vs-quantity](friendship-quality-vs-quantity/) | planned | `FRIEND_DISCLOSURE_ANY`, `FRIEND_N_NOMINEES`, `FRIEND_CONTACT_SUM` (head-to-head in same regression) | all 13 | WLS sample-wide (no saturation gate, N≈4,700) | Quality-vs-quantity test; one-confidant vs many-friends |

## Hypothesis: effect modification (Phase 6 mechanism experiments)

| Experiment | Status | Exposure | Outcome | Method | Notes |
|---|---|---|---|---|---|
| [em-compensatory-by-ses](em-compensatory-by-ses/) | planned | `IDGX2 × PARENT_ED` interaction | cardiometabolic + SES | WLS interaction primary; bias-corrected matching for binary subgroup contrast (first project use of `analysis.matching`) | Compensatory hypothesis: low-SES kids benefit more from popularity |
| [em-sex-differential](em-sex-differential/) | planned | `IDGX2 × BIO_SEX` interaction | cardiometabolic primarily; mental-health secondary | WLS interaction; sex-stratified forests; matching as robustness | Peer status policing of body weight stronger for girls hypothesis |
| [em-depression-buffering](em-depression-buffering/) | planned | `IDGX2 × CESD_SUM` interaction | W5 mental health (`H5MN1`, `H5MN2`, `H5ID1`) | WLS interaction; D9 collider check (CESD_SUM in adjustment AND moderator); two-spec sensitivity | Popularity buffers pre-existing depression hypothesis |

## Hypothesis: dark-side-of-popularity (Phase 6 mechanism experiments)

| Experiment | Status | Exposure | Outcome | Method | Notes |
|---|---|---|---|---|---|
| [popularity-and-substance-use](popularity-and-substance-use/) | planned | `IDGX2` | substance-use outcomes (W4: H4TO5/H4TO39/H4TO70/H4TO65*; W5: H5TO2/H5TO12/H5TO15) | WLS L0+L1+AHPVT; predicted *positive* β = striking outcome-specificity inversion vs cardiometabolic protective signal | Tests "dark side" of popularity hypothesis |
| [lonely-at-the-top](lonely-at-the-top/) | planned | `IDGX2 + H1FS13 + (z(IDGX2) × z(H1FS13))` continuous-interaction | cardiometabolic + mental-health subset | WLS continuous interaction; **2x2 design abandoned per pre-flight** (min cell N=73, < 150 threshold) | Paradox subgroup: high popularity + high loneliness predicts worse mid-life outcomes |

## Hypothesis: cross-sex friendship (Phase 6 mechanism experiments)

| Experiment | Status | Exposure | Outcome | Method | Notes |
|---|---|---|---|---|---|
| [cross-sex-friendship](cross-sex-friendship/) | planned | `BIO_SEX × HAVEBMF` and `BIO_SEX × HAVEBFF` (8 cells total) | all 13 | WLS within each cell; full forest plot per outcome (8 × 13 cells); narrative narrowing in report | Tests instrumental-vs-emotional cross-sex friendship hypotheses |

## Cross-cutting / methodological

| Experiment | Status | Purpose |
|---|---|---|
| [negative-control-battery](negative-control-battery/) | **complete (2026-04-27)** | **Two null directions in one experiment.** Direction 1 — exposure-side: blood type, age at menarche or W1 pubertal-development index, hand-dominance, residential stability pre-W1 (pre-flight skip-with-warning guards used; some still missing in public-use). Direction 2 — outcome-side: sensory (`H5EL6D`, `H5EL6F`, `H5DA9`), allergy/asthma (`H5EL6A`, `H5EL6B`). Tests the unmeasured-confounder assumption underlying every other DAG. 125-row matrix produced; outcome-side cells the load-bearing portion. |
| [saturation-balance](saturation-balance/) | **complete (2026-04-27)** | Survey-weighted (`GSWGT1`) covariate balance table for L0 + L1 + AHPVT inside (N=3,511) vs. outside saturated schools (N=1,603). Quantifies the external-validity gap of the within-saturated-schools estimand. **Top SMD-flagged covariates: AHPVT 0.20, Hispanic 0.20, AH_RAW 0.15, CESD 0.11.** Joint-stratum positivity holds (smallest cell N=15, no cell <10). Cited as transportability footnote by every network-exposure claim. |

## Conventions

- **Naming.** Lowercase, hyphenated, no caps. Hypothesis-prefix or domain-prefix + descriptive scope-suffix (e.g. `cognitive-screening`, `cardiometabolic-handoff`).
- **Adding an experiment.** See ["Adding a new experiment" in the top-level README](../README.md#adding-a-new-experiment). Mandatory order: lock the DAG in [`reference/dag_library.md`](../reference/dag_library.md) first, then write the field-table `README.md` with the estimand wording, then any analytic code.
- **Chart-explanation convention.** Every chart has a **descriptive title baked into the figure itself** (set via `ax.set_title(...)` / `fig.suptitle(...)` in `figures.py`). In the experiment's `report.md`, every embedded chart additionally gets (1) a 1-3 sentence descriptive caption immediately under the image, (2) a prose paragraph explaining why the chart matters, how to read it, and which method produced it, and (3) method names linked on first use within the report to [`../reference/methods.md`](../reference/methods.md) or [`../reference/glossary.md`](../reference/glossary.md). Updated 2026-04-26: titles now belong on the chart (the prior "no baked-in titles" convention is reversed).
- **Meta-analysis collapse.** Sensitivity audits and verification packs are not separate experiments — they live as artifacts inside the experiment they sensitize. For example, the EXP-11-SENS audits and EXP-13-VERIFY pack live as `cognitive-screening/figures/sensitivity/`, `cognitive-screening/tables/sensitivity/`, `cognitive-screening/figures/verification/`, and `cognitive-screening/tables/verification/`.

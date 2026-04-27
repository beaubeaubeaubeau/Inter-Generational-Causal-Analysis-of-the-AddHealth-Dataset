# DAG library — index

This file is an **index** of every causal DAG used in the project. The ground-truth DAG lives in each experiment's own folder as `dag.md`; this index gives a one-paragraph summary and a link, so a reader navigating from `reference/` can find the per-experiment causal model in one hop.

**Convention (locked 2026-04-27):**
- Each experiment that makes a causal claim ships a `dag.md` next to its `README.md` / `run.py`. The `dag.md` is the canonical specification of the causal model — Mermaid graph + adjustment set + estimand wording + weak points.
- This index is the navigation layer. Updates to a DAG happen in the experiment folder; this index gets a one-line update when a new DAG is added or an existing one is renamed/version-bumped.
- For plain-language definitions of *back-door path*, *positivity*, *negative control*, and *confounder vs. mediator*, see [glossary.md](glossary.md).
- For the experiment ↔ DAG ↔ method ↔ output map, see [experiments/README.md](../experiments/README.md).
- For the identifying assumptions and target estimands the DAGs encode, see [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand).

---

## Hypothesis: cognitive trajectory

| DAG | Used by | Adjustment | Status | Link |
|---|---|---|---|---|
| **DAG-Cog v1.0** | cognitive-screening; cognitive-outcome column of multi-outcome-screening | L0+L1+AHPVT (= `{BIO_SEX, RACE, PARENT_ED, CESD_SUM, H1GH1, AH_PVT}`); plus `L_partner = {BIO_SEX, H1GI1M}` placeholder for partner-comparable analysis | locked 2026-04-25 | [`experiments/cognitive-screening/dag.md`](../experiments/cognitive-screening/dag.md) |
| **DAG-Cog-FrontDoor** | cognitive-frontdoor | Same as `DAG-Cog v1.0` for back-door arm; treats `AH_PVT` as mediator for the front-door arm | planned (sensitivity check, not load-bearing) | [`experiments/cognitive-frontdoor/dag.md`](../experiments/cognitive-frontdoor/dag.md) |

**Trajectory framing.** `DAG-Cog v1.0` adjusts for `AH_PVT` (W1 verbal IQ) as the W1 baseline cognitive measure → reports a **trajectory-adjusted** β ("where you ended up cognitively, given where you started"). The strict-mediator interpretation is downgraded to the front-door sensitivity check in `DAG-Cog-FrontDoor`. See [methods.md §1 AHPVT callout](methods.md#1-identification-assumptions-and-target-estimand) for the full caveats.

---

## Hypothesis: cardiometabolic

| DAG | Used by | Adjustment | Status | Link |
|---|---|---|---|---|
| **DAG-CardioMet** | cardiometabolic-handoff (`IDGX2 → H4WAIST/H4BMI/H4BMICLS`); cardiometabolic outcomes column of multi-outcome-screening | L0 + L1 (extended with `H1GH28` W1 self-reported weight) + AHPVT (here a general-ability confounder, not a baseline) | planned; locking session pending | [`experiments/cardiometabolic-handoff/dag.md`](../experiments/cardiometabolic-handoff/dag.md) |

`H4BMICLS` ordinal → ordered logit. `H4SBP`/`H4DBP` need anti-hypertensive medication flags brought in (`H4TO*`, see [TODO §A9](../TODO.md)).

---

## Hypothesis: SES

| DAG | Used by | Adjustment | Status | Link |
|---|---|---|---|---|
| **DAG-SES** | ses-handoff (`ODGX2 → H5EC1`); SES outcomes column of multi-outcome-screening | L0 + L1; **AHPVT dropped** (mediator on the educational-credentialism path); IPAW layered on `GSW5` for W4→W5 attrition | planned; locking session pending | [`experiments/ses-handoff/dag.md`](../experiments/ses-handoff/dag.md) |

`H5EC1` (bracketed earnings) → interval regression on bracket midpoints. `H5LM5` (3-level employment) → ordered logit.

---

## Hypothesis: mental health & functional (multi-outcome screening cells)

| DAG | Used by | Adjustment | Status | Link |
|---|---|---|---|---|
| **DAG-Mental** *(stub)* | `H5MN1`, `H5MN2` (PSS-4 components at W5) in multi-outcome-screening | L0 + L1 + AHPVT (decision pending: condition on `CESD_SUM` or drop it — over-adjustment vs. confounding tradeoff) | planned stub | [`experiments/multi-outcome-screening/dag.md`](../experiments/multi-outcome-screening/dag.md) |
| **DAG-Functional** *(stub)* | `H5ID1`, `H5ID4`, `H5ID16` (functional / sleep at W5) in multi-outcome-screening | L0 + L1 + AHPVT; `H1GH1` doubles as confounder + outcome-construct precursor; do not condition on `H4BMI` (mediator) | planned stub | [`experiments/multi-outcome-screening/dag.md`](../experiments/multi-outcome-screening/dag.md) |

---

## Cross-cutting

| DAG | Used by | Purpose | Status | Link |
|---|---|---|---|---|
| **Saturation balance** *(descriptive)* | saturation-balance | Quantifies the external-validity gap between saturated vs. non-saturated school respondents on L0+L1+AHPVT. No causal estimand. | planned | [`experiments/saturation-balance/dag.md`](../experiments/saturation-balance/dag.md) |
| **Negative-control battery** | negative-control-battery | Tests the unmeasured-confounder assumption via (Direction 1) exposure-side NCs (blood type, age at menarche, hand-dominance, residential stability) AND (Direction 2) outcome-side NCs (sensory: `H5EL6D`, `H5EL6F`, `H5DA9`; allergy/asthma: `H5EL6A`, `H5EL6B`). | planned, broadened 2026-04-27 | [`experiments/negative-control-battery/dag.md`](../experiments/negative-control-battery/dag.md) |

---

## Hypothesis: type-of-tie (Phase 6 mechanism experiments)

| DAG | Used by | Adjustment | Status | Link |
|---|---|---|---|---|
| **DAG-Pop-vs-Soc** | popularity-vs-sociability | L0+L1+AHPVT per outcome; parallel exposures `IDGX2` vs `ODGX2`; estimand is paired-difference | planned | [`experiments/popularity-vs-sociability/dag.md`](../experiments/popularity-vs-sociability/dag.md) |
| **DAG-EgoNet** | ego-network-density | L0+L1+AHPVT + size-conditioning on `REACH3`; estimand is "density at constant network size" | planned | [`experiments/ego-network-density/dag.md`](../experiments/ego-network-density/dag.md) |
| **DAG-QvQ** | friendship-quality-vs-quantity | L0+L1+AHPVT per outcome; sample-wide (no saturation gate); 3 exposures in same regression | planned | [`experiments/friendship-quality-vs-quantity/dag.md`](../experiments/friendship-quality-vs-quantity/dag.md) |

---

## Hypothesis: effect modification

| DAG | Used by | Adjustment | Status | Link |
|---|---|---|---|---|
| **DAG-EM-SES** | em-compensatory-by-ses | L0+L1+AHPVT + `IDGX2 × PARENT_ED` interaction; estimand is the interaction coefficient | planned | [`experiments/em-compensatory-by-ses/dag.md`](../experiments/em-compensatory-by-ses/dag.md) |
| **DAG-EM-Sex** | em-sex-differential | L0+L1+AHPVT + `IDGX2 × BIO_SEX` interaction | planned | [`experiments/em-sex-differential/dag.md`](../experiments/em-sex-differential/dag.md) |
| **DAG-EM-Dep** | em-depression-buffering | L0+L1+AHPVT + `IDGX2 × CESD_SUM` interaction; D9 collider check (CESD as both confounder feed and moderator) | planned | [`experiments/em-depression-buffering/dag.md`](../experiments/em-depression-buffering/dag.md) |

---

## Hypothesis: dark side of popularity

| DAG | Used by | Adjustment | Status | Link |
|---|---|---|---|---|
| **DAG-DarkSide-Subst** | popularity-and-substance-use | L0+L1+AHPVT; new substance-use outcomes (`H4TO5`, `H4TO39`, `H4TO70`, `H5TO2`, `H5TO12`); predicted *positive* β = outcome-specificity inversion | planned | [`experiments/popularity-and-substance-use/dag.md`](../experiments/popularity-and-substance-use/dag.md) |
| **DAG-Lonely-Top** | lonely-at-the-top | L0+L1+AHPVT + continuous interaction `IDGX2 × H1FS13` (2×2 design abandoned per pre-flight: min cell N=73, < 150 threshold) | planned | [`experiments/lonely-at-the-top/dag.md`](../experiments/lonely-at-the-top/dag.md) |

---

## Hypothesis: cross-sex friendship

| DAG | Used by | Adjustment | Status | Link |
|---|---|---|---|---|
| **DAG-CrossSex** | cross-sex-friendship | Per outcome (inherits cog/cardiometabolic/SES/mental/functional); 4-cell stratification on `BIO_SEX × {HAVEBMF, HAVEBFF}` | planned | [`experiments/cross-sex-friendship/dag.md`](../experiments/cross-sex-friendship/dag.md) |

---

## Changelog

- **2026-04-27** — File converted from canonical-DAG-spec to **index** per the per-experiment-DAG convention. All ground-truth DAG content moved to `experiments/<name>/dag.md`. Added 9 new mechanism-experiment DAG entries (Phase 6 plan). Added `L_partner` placeholder note to `DAG-Cog v1.0` row.
- **2026-04-25** — File created. `DAG-Cog v1.0` locked with the user; planned-DAG stubs drafted for `DAG-CardioMet`, `DAG-SES`, `DAG-Mental`, `DAG-Functional`, `DAG-Cog-FrontDoor`. (Content subsequently migrated to per-experiment files on 2026-04-27.)

# Multi-outcome screening — per-outcome DAG inheritance

**Used by:** [multi-outcome-screening](README.md). **Status:** screen complete; per-outcome DAGs are drawn from the per-handoff DAG library and applied as-needed.

## Screening shortcut

For comparability across the 12 secondary outcomes plus the cognitive composite, the multi-outcome screen applies **`DAG-Cog v1.0` adjustment uniformly** (L0 + L1 + AHPVT) — a screening approximation that preserves cross-outcome ranking but **biases per-outcome point estimates** relative to each outcome's proper DAG.

This is intentional: the screen ranks exposures cross-outcome; formal per-outcome estimation lives in the handoff experiments.

## Per-outcome DAGs (used in formal estimation)

| Outcome group | Outcomes | DAG | Location |
|---|---|---|---|
| Cognitive | `W4_COG_COMP` | `DAG-Cog v1.0` | [`../cognitive-screening/dag.md`](../cognitive-screening/dag.md) |
| Cardiometabolic | `H4BMI`, `H4SBP`, `H4DBP`, `H4WAIST`, `H4BMICLS` | `DAG-CardioMet` | [`../cardiometabolic-handoff/dag.md`](../cardiometabolic-handoff/dag.md) |
| Mental health | `H5MN1`, `H5MN2` | `DAG-Mental` *(planned, see below)* | this file |
| Functional | `H5ID1`, `H5ID4`, `H5ID16` | `DAG-Functional` *(planned, see below)* | this file |
| SES | `H5LM5`, `H5EC1` | `DAG-SES` | [`../ses-handoff/dag.md`](../ses-handoff/dag.md) |

## DAG-Mental (planned stub)

**Used by:** `H5MN1`, `H5MN2` (Perceived Stress Scale items at W5).

**Distinguishing arrows from `DAG-Cog v1.0`:** `CESD_SUM` becomes an **outcome-side construct**, not a confounder, since W1 depressive symptoms predict W5 perceived-stress *through the construct itself* (PSS at W5 is a similar latent affective/stress construct to CES-D at W1).

**Decision pending:**
- **Option A** (condition on CESD_SUM): closes confounding from W1 affective state but blocks any "early depression → adult stress" mechanism we might want to estimate.
- **Option B** (drop CESD_SUM): preserves the affective-trajectory mechanism but may leave back-door confounding (CESD → SOC → PSS).

To be worked in Task 16. The screen uses Option A (condition on CESD) for comparability.

## DAG-Functional (planned stub)

**Used by:** `H5ID1` (self-rated physical health), `H5ID4` (stair-climbing limitation), `H5ID16` (sleep trouble).

**Distinguishing arrows:** add `H1GH1` (W1 self-rated health) as both confounder and possible outcome-construct precursor. Consider adding adolescent-fitness proxy if any public-use measure is identifiable.

`H4BMI` (W4 measured BMI) is a plausible mediator of `SOC → H5ID4` (stair-climbing limitation has obvious BMI dependence) — do **not** condition on `H4BMI` when estimating SOC → H5ID4 if total effect is the target.

## Estimand wording — screen-level (use verbatim)

> The multi-outcome screen reports cross-outcome rankings under a uniform `DAG-Cog v1.0` adjustment. Per-outcome point estimates are intended for ranking only — each handoff candidate is re-estimated under its outcome-specific DAG (cardiometabolic, SES, mental, functional) before formal claims are made.

## Index entry (in `reference/dag_library.md`)

> **Multi-outcome-screening DAGs** — applies `DAG-Cog v1.0` uniformly as a screening approximation; per-outcome DAGs (`DAG-CardioMet`, `DAG-SES`, `DAG-Mental`, `DAG-Functional`) live here and in the per-handoff experiments. → [`experiments/multi-outcome-screening/dag.md`](../../experiments/multi-outcome-screening/dag.md)

## Changelog
- **2026-04-27** — Created. DAG-Mental and DAG-Functional stubs migrated from `reference/dag_library.md`. Per-outcome lookup table cross-referencing handoff experiments.

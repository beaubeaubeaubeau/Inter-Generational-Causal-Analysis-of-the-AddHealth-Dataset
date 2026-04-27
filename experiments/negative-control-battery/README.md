# negative-control-battery — exposure-side AND outcome-side null controls (planned)

Two null directions in one experiment, side by side. Tests the
unmeasured-confounder assumption in `DAG-Cog` (and its sibling per-outcome
DAGs) via two independent placebo strategies.

| Field | Value |
|---|---|
| Status | planned (broadened 2026-04-27 to cover both null directions; original exposure-side scope from 2026-04-25 is preserved) |
| Purpose | (a) Replace the contaminated `HEIGHT_IN` D2 negative-control outcome from cognitive-screening with a battery of clean NC outcomes; (b) ALSO add NC exposures (blood type, age at menarche, hand-dominance, residential stability pre-W1) so the experiment covers both null directions. |
| Direction 1 — NC exposures | Variables that should NOT predict mid-life outcomes: blood type (genetic), age at menarche (biological timing), hand-dominance (lateralisation), residential stability pre-W1 (pre-baseline mobility). **Pre-flight required for each per [TODO §A2](../../TODO.md)** — public-use availability is uncertain. |
| Direction 2 — NC outcomes | Variables that should NOT be moved by W1 social integration: `H5EL6D` (sight problem before 16, N≈4,168), `H5EL6F` (hearing problem before 16, N≈4,166), `H5DA9` (hearing quality, N≈4,082), `H5EL6A` (asthma before 16, N≈4,171), `H5EL6B` (allergy before 16, N≈4,168). All confirmed via 2026-04-27 pre-flight inventory. **Avoid** `H5ID1` (self-rated general health — too socially confounded, fails the "biology-only" sniff test). |
| Real exposure (for outcome-side direction) | All 24 EXP-14-COG exposures, in the cognition outcome's adjustment set. Headline test is `IDGX2` (popularity) → each NC outcome. |
| Real outcome (for exposure-side direction) | `W4_COG_COMP` and the cardiometabolic outcomes from `multi-outcome-screening`. |
| DAG | [`DAG-NC-Battery`](dag.md) — both null directions in one diagram. |
| Method | WLS via `analysis.wls:weighted_ols`, `GSWGT4_2` weights, cluster-SE on `CLUSTER2`. Pre-flight assertions inside `run.py` (skip + warn if a candidate exposure-side NC variable is missing rather than crash). Same primary spec L0+L1+AHPVT as cognitive-screening for direct comparability. |
| Adjustment | L0+L1+AHPVT (mirror cognitive-screening) for both directions. The whole point is "if we ran the exact same WLS spec but swapped one side for a placebo, would the β still come back?". |
| Outputs (planned) | `tables/primary/nc_battery_matrix.csv` (long-format: direction, exposure, outcome, β, SE, p, expected ≈ 0), `tables/primary/nc_battery.md`, `tables/sensitivity/nc_preflight_availability.csv` |
| Plots (planned) | [figures/primary/nc_comparison.png](figures/primary/nc_comparison.png) (real vs. NC β side-by-side, both directions), [figures/primary/nc_failure_grid.png](figures/primary/nc_failure_grid.png) (per-exposure × per-outcome NC heatmap with significance hatch), [figures/sensitivity/nc_availability_diagram.png](figures/sensitivity/nc_availability_diagram.png) |
| Estimand wording | "**Direction 1**: Conditional on L0+L1+AHPVT, a one-unit increase in NC exposure is associated with a β-unit change in real outcome `Y`. Under the assumed DAG, β should be ≈ 0; non-zero β indicates an unblocked back-door. **Direction 2**: Conditional on L0+L1+AHPVT, a one-unit increase in real exposure (e.g. `IDGX2`) is associated with a β-unit change in NC outcome (e.g. `H5EL6D` sight-before-16). Under the assumed DAG, β should be ≈ 0 (social integration cannot retroactively cause childhood vision); non-zero β is unmeasured-confounder evidence." |

## Pre-flight findings (locked into `run.py`)

**Outcome-side NCs (Direction 2)** — all confirmed via 2026-04-27 inventory
with N > 4,000 each:

| Variable | Codebook wording | N |
|---|---|---|
| `H5EL6D` | TOLD OF SIGHT PROBLEM BEFORE AGE 16—W5 | 4,168 |
| `H5EL6F` | TOLD OF HEARING PROBLEM/DEAF BEFORE AGE 16—W5 | 4,166 |
| `H5DA9`  | HEARING QUALITY WITHOUT AIDS—W5 | 4,082 |
| `H5EL6A` | TOLD OF ASTHMA BEFORE AGE 16—W5 | 4,171 |
| `H5EL6B` | TOLD OF ALLERGY BEFORE AGE 16—W5 | 4,168 |

**Avoided:** `H5ID1` — self-rated general health is socially confounded
and fails the "biology-only" sniff test for an outcome-side NC.

**Exposure-side NCs (Direction 1)** — pre-flight outstanding per [TODO §A2](../../TODO.md):

| Candidate | Public-use availability | Status |
|---|---|---|
| Blood type | Uncertain; may be in restricted-use only | Pre-flight required |
| Age at menarche | Likely on W1 in-home (girls only) | Pre-flight required |
| Hand-dominance | Likely on W1 in-home or W4 in-home | Pre-flight required |
| Residential stability pre-W1 | Constructible from W1 in-home items | Pre-flight required |

`run.py` includes per-candidate `assert / warn` guards: if a candidate
column is missing from the cached parquets, the script skips it with a
warning rather than crashing.

## Why this experiment exists

Every causal claim in this project rests on the assumption that the
adjustment set closes all relevant back-door paths from the exposure to
the outcome. NC tests are the project's primary empirical check on that
assumption:

- **Direction 1 (NC exposure → real outcome).** If a placebo exposure
  predicts the real outcome under the same WLS spec, the spec is
  picking up unmeasured confounding that the real exposure also picks up.
- **Direction 2 (real exposure → NC outcome).** If `IDGX2` predicts
  childhood vision problems (which W1 in-school popularity cannot
  retroactively cause), the same logic applies in reverse.

Running both directions side by side is more informative than either
alone — they fail in different ways under different confounder structures.

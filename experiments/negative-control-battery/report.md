# negative-control-battery — report (TEMPLATE / TBD)

> **Status:** skeleton (broadened 2026-04-27). No analytic results have
> been produced yet. Replace `TBD` cells once `run.py` and `figures.py`
> have run.

## Question

Does the assumed DAG (`DAG-Cog` and its sibling per-outcome DAGs) close
all relevant back-door paths between exposure and outcome? The whole
project rests on this assumption; NC tests are the empirical check.

This experiment runs **two null directions side by side**:

- **Direction 1.** Replace exposure with a placebo (NC exposure: blood
  type, age at menarche, hand-dominance, residential stability pre-W1).
  If the placebo still predicts the real outcome under the same WLS
  spec, the spec is picking up unmeasured confounding.
- **Direction 2.** Replace outcome with a placebo (NC outcome: sensory
  / asthma / allergy variables locked from 2026-04-27 pre-flight). If
  the real exposure still predicts the placebo outcome, the same logic
  applies in reverse.

See [DAG-NC-Battery](dag.md) for the identification claim.

## Pre-flight findings

**Outcome-side NCs (Direction 2)** — confirmed 2026-04-27, all N > 4,000:

- `H5EL6D` (sight problem before 16, N = 4,168)
- `H5EL6F` (hearing problem before 16, N = 4,166)
- `H5DA9` (hearing quality without aids, N = 4,082)
- `H5EL6A` (asthma before 16, N = 4,171)
- `H5EL6B` (allergy before 16, N = 4,168)

**Excluded:** `H5ID1` (self-rated general health) — too socially confounded,
fails the "biology-only" sniff test.

**Exposure-side NCs (Direction 1)** — pre-flight outstanding per
[TODO §A2](../../TODO.md). Candidates: blood type, age at menarche,
hand-dominance, residential stability pre-W1. `run.py` includes
per-candidate guards: missing columns are skipped with a warning rather
than crashing the script. `tables/sensitivity/nc_preflight_availability.csv`
records which candidates survived availability checks.

## Method (one-liner)

WLS via [`weighted_ols`](../../reference/methods.md), L0+L1+AHPVT
adjustment (mirror cognitive-screening for direct comparability),
`GSWGT4_2` weights, cluster-SE on `CLUSTER2`. A "pass" of the null
test = p ≥ 0.05; a FAIL = unmeasured-confounder evidence.

## Results

### 1. NC comparison (positive control + both null directions)

![NC comparison](figures/primary/nc_comparison.png)

*Caption.* TBD — three panels: (A) positive control = real exposures
→ real cognition β from `cognitive-screening` (β should be substantively
non-zero); (B) Direction 2 = real exposures → NC outcomes (β should be
≈ 0); (C) Direction 1 = NC exposures → real outcomes (β should be ≈ 0).

*Why it matters.* The visual headline. If panel A shows non-zero β AND
panels B and C cluster around zero, the assumed DAG survives the NC
challenge. Any panel-B or panel-C bar that visibly departs from zero
is a candidate failure point. Method: WLS β under matched specs.

### 2. NC failure grid

![NC failure grid](figures/primary/nc_failure_grid.png)

*Caption.* TBD — two panels (one per direction). Cells coloured by
−log10(p); cells with p < 0.05 (= null test FAIL) hatched.

*Why it matters.* Per-cell view. A diffuse pattern of hatched cells in
either panel indicates a structural problem (unmeasured confounder
correlated with both sides); a single hatched cell may just be type-I
error (5% expected by chance). Method: WLS p-values, displayed as
−log10(p) for visual contrast.

### 3. NC availability diagram

![NC availability](figures/sensitivity/nc_availability_diagram.png)

*Caption.* TBD — bar chart of non-null N per NC exposure candidate;
green = passed pre-flight, grey = missing or all-NaN.

*Why it matters.* Documents which Direction 1 NC exposures actually made
it into the analysis. The script tolerates missing candidates by design;
this chart makes the *which-tests-actually-ran* explicit. Method: column
existence + non-null count from the cached parquets.

## Sensitivity / pre-flight

- **Pre-flight availability table**:
  `tables/sensitivity/nc_preflight_availability.csv`. The exposure-side
  battery's N depends on which candidates the public-use file actually
  contains.
- **Multiple-testing context.** With `K` null tests per direction, the
  expected number of p < 0.05 cells under the global null is `0.05 × K`.
  Compare the observed FAIL count to this expectation in the narrative.

## Conclusion (TBD)

TBD — the assumed DAG passes if both panels B and C of the comparison
chart show β ≈ 0 across the great majority of cells, with FAIL cell
counts within type-I-error expectation. Failure modes:

- Direction 1 systematic FAIL ⇒ unmeasured confounder correlated with
  the placebo exposure category (e.g. blood type → outcome via
  population stratification not in adjustment set).
- Direction 2 systematic FAIL ⇒ unmeasured confounder correlated with
  social integration AND the placebo outcome (e.g. school-level
  socioeconomic intensity affecting both peer position AND childhood
  asthma diagnosis rates).

## Checklist before declaring `Status: complete`

- [ ] Pre-flight for Direction 1 NC exposures completed; availability
      table populated.
- [ ] `run.py` produces both CSVs without crashing on any candidate.
- [ ] `figures.py` produces all three PNGs.
- [ ] All `TBD` placeholders replaced.
- [ ] FAIL count compared to type-I-error expectation in narrative.
- [ ] Cross-reference paragraph linking to cognitive-screening D2 result
      (which this experiment supersedes).

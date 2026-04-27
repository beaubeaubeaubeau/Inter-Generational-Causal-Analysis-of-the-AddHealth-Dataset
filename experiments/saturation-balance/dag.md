# Saturation balance — descriptive (no causal estimand)

**Used by:** [saturation-balance](README.md). **Status:** planned. **Note:** this experiment is *descriptive*, not causal — it has no DAG-style estimand, just a balance table.

## Purpose

Quantify the external-validity gap between **respondents in saturated schools** (where network exposures like `IDGX2`, `BCENT10X` are *defined*) and respondents in **non-saturated schools** (where those exposures are structurally NaN — positivity = 0).

Per [methods.md §1 positivity discussion](../../reference/methods.md#1-identification-assumptions-and-target-estimand), the network-exposure ATE is identified **only within saturated schools** — no extrapolation. This experiment characterises the population gap a reader needs to know about when generalising.

## Method

A weighted (`GSWGT1`) covariate balance table for L0 + L1 + AHPVT comparing two groups:

- **Group A (in scope of network estimand):** respondents in saturated schools.
- **Group B (out of scope):** respondents in non-saturated schools.

For each covariate, report:
- Weighted mean (continuous) or proportion (binary) in each group.
- Standardized mean difference (SMD): `|mean_A - mean_B| / pooled_SD`.
- Flag: SMD > 0.10 → meaningful imbalance (conventional cutoff per Stuart 2010).

Plus a **joint-stratum positivity diagnostic** per [TODO §A14](../../TODO.md): tabulate joint covariate-stratum cell counts WITHIN saturated schools, flag any cell with N < 10 or no exposure variation. The "ATE within saturated schools" estimand is identified only if positivity holds at every level of L0+L1+AHPVT — D7 in the screen only checks one slice.

## Output

A two-column balance table + a positivity-diagnostic table. No regression; no causal estimand. Used as a **transportability footnote** in network-exposure plot captions and brief paragraphs.

## Why no causal DAG?

This experiment compares two subpopulations on **observable covariates only** — it does not estimate any causal effect of saturation on anything. The "DAG" (if drawn) would just be:

```
saturated_school_assignment → membership in Group A
{covariates} ← unobserved school selection mechanism → saturated_school_assignment
```

…which is descriptive, not identifying. Hence: no formal DAG; this file documents the experiment's role and method.

## Index entry (in `reference/dag_library.md`)

> **Saturation balance** *(descriptive, no causal estimand)* — covariate balance table comparing saturated vs. non-saturated school respondents. Quantifies the external-validity gap of the within-saturated-schools estimand used by network exposures. Used by `saturation-balance`. → [`experiments/saturation-balance/dag.md`](../../experiments/saturation-balance/dag.md)

## Changelog
- **2026-04-27** — Created. Documents the descriptive purpose; no causal DAG drawn.

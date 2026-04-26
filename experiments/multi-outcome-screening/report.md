# Multi-outcome screening — report

## Overview

The same 24 W1 social exposures used in
[cognitive-screening](../cognitive-screening/report.md) are applied uniformly
across 12 non-cognitive outcomes in 4 groups — cardiometabolic (5), mental
health (2), functional (3), and SES (2) — under DAG-Cog as a screening
approximation. Per-outcome point estimates are biased relative to their
proper DAGs (`DAG-CardioMet`, `DAG-Mental`, `DAG-SES`); cross-outcome
*ranking* is what this experiment delivers, not load-bearing β values.
Outcome-dependent diagnostics D1 (baseline WLS) and D4 (adjustment-set
stability) run per (exposure, outcome) cell. Outcome-independent diagnostics
(D2, D6–D9) are inherited from cognitive-screening; sibling D3 and
component-consistency D5 are cognition-specific and skipped.

<!-- Chart-explanation convention: every chart embedded in this report must include
     (1) a descriptive caption under the image (1-3 sentences),
     (2) a prose paragraph explaining why the chart was generated, how to read it,
         and what method produced it,
     (3) method names linked to ../../reference/methods.md or ../../reference/glossary.md.
     Stripped baked-in PNG titles per TODO §E. -->

## Primary results

<!-- TODO: prose around figures/primary/multi_outcome_beta_heatmap.png, multi_outcome_sig_heatmap.png, 15_per_outcome_pcount.png -->

## Handoff to formal estimation

<!-- TODO: prose around figures/handoff/15_handoff_forest.png; explain that this is the bridge to cardiometabolic-handoff and ses-handoff experiments; link to glossary.md#handoff-in-this-project -->

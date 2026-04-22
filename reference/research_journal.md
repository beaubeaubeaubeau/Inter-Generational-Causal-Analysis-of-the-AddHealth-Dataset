# Research journal — Inter-generational causal analysis of AddHealth

Chronological log of analytic steps, headline findings, and outstanding
uncertainties. Intended as a narrative companion to the numbered task outputs
in [outputs/](outputs/); each phase below corresponds to one or more scripts
in [scripts/](scripts/) and artefacts in [outputs/](outputs/) + [img/](img/).

---

## Phase 0 — Data inventory and AID reconciliation

**Tasks:** 01, 02. **Scripts:** [task01_file_inventory.py](scripts/task01_file_inventory.py), [task02_aid_overlap.py](scripts/task02_aid_overlap.py).

Catalogued every SAS7BDAT shipped in ICPSR 21600 v26; built the AID-by-wave
overlap matrix to understand the analytic ceilings. W1 in-home N = 6,504; W1
in-school N = 20,745. W1→W4 retention 4,882 (75% of W1 in-home). W1→W5
retention 4,196 mode-unrestricted / 3,553 mode-restricted ("high-quality"
W5 subsample flagged as `MODEOK5=1`).

**Uncertainty logged.** Whether to cap N at mode-restricted W5 or accept the
larger mode-inclusive cell. Deferred; both evaluated downstream and the
restriction kept as a sensitivity variant, not a primary.

---

## Phase 1 — Variable selection and curation

**Tasks:** 03a/b/c/de/fgh, 04, 05. **Scripts:** `task03*`, [task04_missingness.py](scripts/task04_missingness.py), [task05_weighted_descriptives.py](scripts/task05_weighted_descriptives.py).

Curated:
- W1 friendship grid (10-column nomination matrix → derived aggregates
  `FRIEND_N_NOMINEES`, `FRIEND_CONTACT_SUM`, `FRIEND_DISCLOSURE_ANY`).
- W1 network frame via `w1network.sas7bdat` — isolates, density, reach,
  centrality (raw `IDGX2`/`ODGX2`, Bonacich `BCENT10X`, reach-based
  `REACH`/`REACH3`, proximity prestige `PRXPREST`, ego-network
  `ESDEN`/`ERDEN`/`ESRDEN`/`RCHDEN`, influence domain `INFLDMN`/`IGDMEAN`).
- W4 cognitive composite `W4_COG_COMP` (z-standardized mean of
  `C4WD90_1`, `C4WD60_1`, `C4NUMSCR`; mode-restricted).
- W5 cognitive variants (documented but deprioritized as primary outcome).
- W3 PVT for `AH_PVT` covariate.
- Demographics (`BIO_SEX`, `H1GI1Y`, `H1GI4`, `H1WP1` et al.) built into the L0
  adjustment bundle.

Wrote weighted descriptives with `GSWGT4_2` and documented missingness by
variable and by pattern. Reserve-code conventions (6/7/8/9, 96/97/98/99, 995/
9995) codified in `analysis_utils.clean_var` + `VALID_RANGES`.

**Main finding.** The intersection of the W1 in-home network sample with a
non-missing W4 cognitive composite and full L0+L1+AHPVT covariates stabilizes
around N ≈ 3,200. Friendship-grid exposures (not network-frame-gated) reach
N ≈ 4,600–4,700.

**Uncertainty logged.** Whether to treat H1FS13/H1FS14 (loneliness items)
as exposures or as mediator/covariate; provisionally treated as exposures
since they pre-date the outcome and are ubiquitously used as adolescent
social indicators in the literature.

---

## Phase 2 — Attrition and analytic-frame construction

**Tasks:** 06, 07, 08. **Scripts:** [task06_attrition.py](scripts/task06_attrition.py), [task07_analytic_n.py](scripts/task07_analytic_n.py), [task08_build_analytic_frame.py](scripts/task08_build_analytic_frame.py).

Wave-conditional attrition patterns show mild selection on early SES and
baseline cognition (visualised in [img/regressions/06_attrition_stacked_bar.png](img/06_attrition_stacked_bar.png) — misfiled under `img/` at root).
Stored analytic frames in [outputs/cache/](outputs/cache/):

- `w1inhome.parquet`, `w1network.parquet`, `w1friendship.parquet`
- `w3pvt.parquet`
- `w4inhome.parquet`
- `pwave5.parquet`
- `analytic_primary.parquet` (W1 ∩ W4-mode-restricted, with L0+L1+AHPVT attached)

**Main finding.** Primary analytic frame N = 3,238 after the tightest
restriction (mode-OK W4 cognitive + full covariate vector). Network-frame
gating costs ≈ 32% of W1 in-home respondents; documented in the task14
D8 column as the "saturated-school selection" penalty.

---

## Phase 3 — Baseline associations and sensitivity

**Tasks:** 10, 11, 12, 13. **Scripts:** [task10_baseline_regressions.py](scripts/task10_baseline_regressions.py), [task11_sensitivity.py](scripts/task11_sensitivity.py), [task12_regression_plots.py](scripts/task12_regression_plots.py), [task13_verification.py](scripts/task13_verification.py).

Ran weighted OLS on each exposure against `W4_COG_COMP` under nested
adjustment sets L0 → L0+L1 → L0+L1+AHPVT. Cluster-robust SEs on `CLUSTER2`
(132 PSUs). task11 added collinearity checks, leave-one-out permutation,
saturated balance, AHPVT shift audits, placebo permutation, reserve-code
sensitivity. task13 verified Benjamini–Hochberg FDR, attrition IPAW,
negative-control exposures/outcomes, design-effect estimates, PSU counts.

**Headline pattern.** Across exposures, adjusting for `AH_PVT` attenuates
network-centrality → cognition associations by 30–50%. `ODGX2` (friend-
nominations sent by the respondent) survives AHPVT adjustment with the
largest stable effect among network measures; `IDGX2` (in-degree) attenuates
heavily but remains significant; `BCENT10X` (Bonacich) is strongest in raw β
but attenuates the most.

**Uncertainty logged.** The L0+L1+AHPVT primary spec assumes AHPVT is a
confounder (verbal IQ predicts both social integration and adult cognition).
If AHPVT is instead a mediator of the social-integration-on-cognition path,
adjusting for it under-estimates the total effect. Flagged but not resolved
at this phase.

---

## Phase 4 — Preliminary causal screening (D1–D9)

**Task:** 14. **Script:** [task14_causal_screening.py](scripts/task14_causal_screening.py). **Outputs:** [outputs/14_screening.md](outputs/14_screening.md), [outputs/14_screening_matrix.csv](outputs/14_screening_matrix.csv), [outputs/14_shortlist.csv](outputs/14_shortlist.csv), [img/causal/](img/causal/).

Ran a 9-diagnostic screen over 24 W1 social exposures:

- **D1** baseline significance (primary spec)
- **D2** height (`HEIGHT_IN`) negative control
- **D3** sibling dissociation
- **D4** adjustment-set stability (L0 / L0+L1 / L0+L1+AHPVT)
- **D5** outcome-component consistency (C4WD90/C4WD60/C4NUMSCR)
- **D6** dose-response monotonicity (continuous only)
- **D7** positivity/overlap (Q5-vs-Q1 logit)
- **D8** saturated-school selection penalty (informational)
- **D9** hard-coded collider/double-adjustment red flags

Emitted a 5-figure visual battery:
[screening_heatmap.png](img/causal/screening_heatmap.png),
[sibling_dissociation.png](img/causal/sibling_dissociation.png),
[adjustment_stability.png](img/causal/adjustment_stability.png),
[component_consistency.png](img/causal/component_consistency.png),
[negctrl_failure_grid.png](img/causal/negctrl_failure_grid.png).

**Initial shortlist (pre-audit):** `BCENT10X` (score 8), `ODGX2` (score 6),
`RCHDEN` / `REACH3` (score 5), `IGDMEAN` / `PRXPREST` / `ESDEN` (score 4) as
"Mixed" / "Weakened". `IDGX2` scored 4 but was tagged **Drop** on D2 height
failure. `SCHOOL_BELONG` dropped on D9 red flag + D2 fail.

### Phase 4.5 — Adversarial review of the screen

A subagent audited the 24 `kind` tags, the D3 sibling logic, and the
D4/D5/D6/D7/D9 bodies. Two real bugs surfaced:

1. **PRXPREST mis-classified as `binary`** (line 78 of task14).
   Raw data dtype float64, range 0.00045–0.774, 3,920 unique values across
   N=4,020 non-null. D6 (dose-response) was being skipped and D7 (overlap)
   ran a degenerate logit with numerically zero p-hats. Root cause: a
   contradiction in [reference/addhealth_synthesis.md](reference/addhealth_synthesis.md) — line 419 (pitfall #7) erroneously claimed
   PRXPREST is binary 0/1, contradicting line 117 which correctly listed
   the continuous range. The synthesis doc was edited and re-annotated;
   task14 was re-run.

2. **D3 accepts opposite-sign siblings.**
   The sibling-dissociation test required `|β_target| > |β_sibling|` and
   `|β_target − β_sibling| > pooled SE`, but omitted a sign-agreement
   check. A target with β = −0.5 and sibling with β = +0.3 would PASS,
   even though the sibling pointing the opposite way is a confounding
   signature (not specificity evidence). None of the current 24 exposures
   triggered this in the observed data, but fixed by adding
   `np.sign(b_t) == np.sign(b_s)` to the pass condition before the bug
   could bite future candidates.

**Rerun verified:**
- PRXPREST now has `kind=continuous`, D6 trend_rho = 0.8 (PASS), D7 overlap
  `[0.15, 0.78]`, eff_n = 1204 (PASS). Re-categorised as **Weakened**
  (score 4).
- IDGX2 D3 correctly fails (|β_IDGX2| = 0.0093 < |β_ODGX2| = 0.0142, same
  sign — dissociation not present).
- BCENT10X D3 still passes (β_BC = 0.091 dwarfs sibling β_OD = 0.014, same
  sign, |delta| > pooled SE).

**Main finding.** On the primary cognitive outcome (`W4_COG_COMP`), the
social-exposure signal is dominated by two mechanisms — local friendship
presence (`ODGX2`, `FRIEND_*`) and structural centrality (`BCENT10X`,
`REACH3`) — but all exposures fail D4 adjustment stability, with AHPVT
contributing the bulk of the shift. Combined with D2 height-NC failures for
`IDGX2` and several egonet exposures, this argues the L0+L1+AHPVT primary
spec is not adequate to close back-door paths, rather than arguing the
exposures are non-causal.

**Critique raised by user and partially addressed.**
The height-NC interpretation (D2) is itself questionable: there is a
well-known positive correlation between adolescent height and peer
popularity (anthropology / developmental psychology literature), which
means HEIGHT_IN is not an unambiguously "non-causal" outcome relative to
`IDGX2`/`BCENT10X`. D2 failure on those exposures may indicate an
unblocked back-door path through height-mediated peer status, not that the
exposure is non-causal on cognition. A cleaner battery of NCs (blood type,
age at menarche, parental eye colour) was discussed but not implemented
in this screen.

---

## Phase 5 — Multi-outcome screening pivot

**Task:** 15. **Script:** [task15_multi_outcome.py](scripts/task15_multi_outcome.py). **Outputs:** [outputs/15_multi_outcome.md](outputs/15_multi_outcome.md), [outputs/15_multi_outcome_matrix.csv](outputs/15_multi_outcome_matrix.csv), [img/causal/multi_outcome_beta_heatmap.png](img/causal/multi_outcome_beta_heatmap.png), [img/causal/multi_outcome_sig_heatmap.png](img/causal/multi_outcome_sig_heatmap.png).

Motivated by the user's observation that a cognition-only outcome may over-
weight the AHPVT-mediation path. Extended the outcome-dependent diagnostics
(D1 baseline, D4 stability) across 12 alternative outcomes: cardiometabolic
(`H4BMI`, `H4WAIST`, `H4SBP`, `H4DBP`, `H4BMICLS`), mental health
(`H5MN1`, `H5MN2`), functional (`H5ID1`, `H5ID4`, `H5ID16`), and SES
(`H5LM5`, `H5EC1`). D2/D6/D7/D8/D9 are outcome-agnostic and inherited from
the task14 rerun; D3 (sibling) and D5 (component-consistency) remain
cognition-only.

**Sample sizes per outcome.** W4 cardiometabolic: median N ≈ 3,200 for
network-gated exposures, ≈ 4,600 for friendship-grid exposures. W5
outcomes: median N ≈ 2,400 for network-gated, ≈ 3,400 for friendship-grid.
Acceptable across the full 24 × 12 matrix (288 fits); no cell dropped for
insufficient data.

**Per-outcome p<0.05 counts:** `H5EC1` 12/24 (strongest signal), `H5ID1`
11/24, `H5ID4` 8/24, `H4WAIST` 7/24, `H4BMI` 6/24, `H4BMICLS` 5/24,
`H5LM5` 5/24, `H5MN1`/`H5MN2` 3/24 each, `H5SBP` 2/24, `H5ID16` 2/24,
`H4DBP` 0/24.

**Cross-outcome-robust exposures (top-3 by p for ≥3 outcomes):**

- **IDGX2** (7 outcomes): H4BMI, H4WAIST, H4BMICLS, H5ID1, H5ID4, H5LM5, H5EC1
- **SCHOOL_BELONG** (5 outcomes): H5MN1, H5MN2, H5ID1, H5ID4, H5ID16
- **IDG_LEQ1** (4 outcomes): H4BMI, H4WAIST, H4BMICLS, H5ID4
- **IDG_ZERO** (4 outcomes): H4BMI, H4WAIST, H4BMICLS, H5MN2

**Main finding.** Social integration at W1 shows a robust signal on adult
cardiometabolic and economic outcomes that is **not** dominated by AHPVT,
unlike the cognitive outcome: on these outcomes D4 typically passes
(rel-shift < 30%). `IDGX2` (in-degree) is the most broadly active exposure
across non-cognitive endpoints — consistent with a "social-integration →
downstream health and attainment" hypothesis. `SCHOOL_BELONG` dominates the
mental-health and functional-health outcomes but fails D4 on several of
them, suggesting mediator leakage.

### Task16 handoff

**Recommended (exposure, outcome) pairs for formal causal estimation:**

- **IDGX2 → H4WAIST** (β = −0.51 cm per in-degree unit, p = 1.9×10⁻¹¹,
  N = 3,250, D4 passes rel-shift 18%)
- **IDGX2 → H4BMI** (β = −0.20, p = 6.8×10⁻⁹, D4 passes rel-shift 21%)
- **IDGX2 → H4BMICLS** (β = −0.032, p = 5.0×10⁻⁸, D4 passes)
- **ODGX2 → H5EC1** (β = 0.10 on log1p-income, p = 1.4×10⁻⁴, D4 passes)

All four pass D1 and D4 on the non-cognitive outcome, and none are covered
by AHPVT as primary confounder in a way that D4 could detect. Cross-
reference with task14's D2/D6/D7 before committing.

---

## Outstanding uncertainties

1. **AHPVT's role.** Still ambiguous whether it's a confounder or a
   mediator of social-exposure → outcome. Plan for task16: run a
   front-door / instrumental-variable decomposition with AHPVT as the
   mediator, compare to the current covariate-adjusted estimate. Likely
   bounds the true effect.

2. **Height as a negative-control outcome is contaminated.** The
   literature on adolescent height-popularity correlation is strong enough
   that D2 failures for `IDGX2`/`BCENT10X` should not be read as evidence
   the exposures are non-causal. A cleaner NC battery (blood type, age at
   menarche, hand-dominance, residential stability pre-W1) should be
   built; this is queued for task16.

3. **Weight choice for W5 outcomes.** The task15 screen uses `GSWGT4_2`
   uniformly because `GSW5` is only populated on the mode-restricted W5
   subsample (N=824 in `analytic_w5`). Formal estimation on W5 outcomes
   should substitute `GSW5` and handle the W4→W5 attrition (IPAW or
   bounding); the screen may be modestly biased toward W4-retained
   respondents.

4. **H5EC1 is bracketed ordinal, not continuous earnings.** Coded as 13
   income brackets, not log-dollars. Treated linearly in the screen
   (acceptable for D1/D4 ranking), but formal estimation should use
   ordered-logit or interval regression. Same caveat applies to `H5LM5`
   (3-level, not strictly binary).

5. **Sibling dissociation is cognition-specific.** The current D3 pairs
   are tuned to the cognitive outcome (ODGX2 as sibling for the peer-
   network exposures). For non-cognitive outcomes, the sibling pairing
   would differ. Not done; flagged as a task16 consideration for
   candidates that survive the initial handoff.

6. **School-level saturation.** task14 D8 is informational only. The
   network-frame respondents are drawn from "saturated" schools where
   ≥75% of roster participated, which differs systematically from the
   full W1 sample on urbanicity and school size. Formal estimation should
   stratify or weight on school saturation.

7. **Outcome-dependent adjustment sets.** task15 uses L0+L1+AHPVT
   uniformly across all 12 outcomes for comparability; in the task16
   formal stage, the adjustment set should be designed per-outcome based
   on a DAG explicitly drawn for that outcome (e.g. BMI may need the
   `H1GH28` W1 self-reported weight covariate in L1; `H5EC1` should drop
   AHPVT and instead condition on `H1GI20` parental education).

---

## Files produced in this session

**Modified:**
- [scripts/task14_causal_screening.py](scripts/task14_causal_screening.py) (2-line bug fix)
- [reference/addhealth_synthesis.md](reference/addhealth_synthesis.md) (pitfall #7 rewrite)
- [scripts/analysis_utils.py](scripts/analysis_utils.py) (+12 VALID_RANGES entries, +`load_outcome()` helper)

**New:**
- [scripts/task15_multi_outcome.py](scripts/task15_multi_outcome.py)
- [outputs/15_multi_outcome_matrix.csv](outputs/15_multi_outcome_matrix.csv) (288 rows)
- [outputs/15_multi_outcome.md](outputs/15_multi_outcome.md)
- [img/causal/multi_outcome_beta_heatmap.png](img/causal/multi_outcome_beta_heatmap.png)
- [img/causal/multi_outcome_sig_heatmap.png](img/causal/multi_outcome_sig_heatmap.png)
- [research_journal.md](research_journal.md) (this file)

**Regenerated (bug-fix rerun):**
- [outputs/14_screening.md](outputs/14_screening.md), [outputs/14_screening_matrix.csv](outputs/14_screening_matrix.csv), [outputs/14_shortlist.csv](outputs/14_shortlist.csv)
- 5 figures in [img/causal/](img/causal/) except the two new multi-outcome ones

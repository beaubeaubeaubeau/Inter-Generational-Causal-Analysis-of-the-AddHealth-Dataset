# TODO — Inter-Generational Causal Analysis of Add Health

Exhaustive backlog as of 2026-04-26. Organised by kind, prioritised within each section (P0 = blocker / correctness; P1 = important / near-term; P2 = polish / quality-of-life).

Conventions:
- **Bullet IDs** — every open bullet is numbered `<Section><N>` (e.g. `A3`, `B11`). Stable references for cross-doc citation. New items append to the next free number; do not renumber when items resolve.
- **Ref** — where the issue was surfaced or where the fix belongs.
- Strikethrough marks items resolved and left for traceability; resolved items still hold their original ID.
- `[JUDGMENT REQUIRED]` — fix is not mechanical; the user must choose between defensible alternatives. Auto-fix agents skip these.

---

## A. Research pipeline — Task 16 and beyond

The following are the analytic next steps called out in [reference/research_journal.md](reference/research_journal.md#outstanding-uncertainties) and [reference/methods.md §1](reference/methods.md#1-identification-assumptions-and-target-estimand). Each item that has an associated experiment is registered in [experiments/README.md](experiments/README.md) with an `EXP-16-*` ID; cross-references below. Ordered roughly by sequencing — later items assume earlier items are done. Open conceptual brainstorming for new RQs lives in [reference/research-plan.md](reference/research-plan.md).

- **A1.** **[P1, downgraded from P0] Front-door / IV decomposition for AHPVT — now a SENSITIVITY check.** Per the 2026-04-25 trajectory-framing decision ([methods.md §1](reference/methods.md#1-identification-assumptions-and-target-estimand)), AHPVT serves as the W1 baseline cognitive measure; the front-door is no longer load-bearing. **Purpose:** quantify how much the EXP-14-COG trajectory β shifts under the strict-mediator reading of AHPVT. Registered as [`EXP-16-FD-COG`](experiments/cognitive-frontdoor/README.md); DAG stub `DAG-Cog-FrontDoor` in [dag_library.md](reference/dag_library.md).
- **A2.** **[P0] Clean negative-control battery.** Registered as [`EXP-16-NC`](experiments/negative-control-battery/README.md). Pre-flight: verify which candidates (blood type, age at menarche, hand-dominance, residential stability pre-W1) are actually in public-use before drafting the DAG addendum.
- **A3.** **[P0] IPAW for W5 outcomes — implement as shared method, NOT a separate experiment.** Implement `scripts/analysis/ipw.py:fit_ipaw(design_frame, outcome_frame, covariates)` returning stabilised inverse-probability-of-attrition weights, trimmed at 95th percentile, layered onto `GSW5`. The handoff experiments (cardiometabolic-handoff, ses-handoff) call this helper; IPAW is library code, not its own experiment. Required before any W5 point estimate is reported. **Update**: phantom `EXP-16-IPAW-W5` references in `experiments/ses-handoff/README.md` and `experiments/README.md` should be replaced with "(via the planned IPAW utility, see TODO §A3)".
- **A4.** **[P1] Per-outcome adjustment sets / DAGs.** Stubs in [dag_library.md](reference/dag_library.md): `DAG-CardioMet`, `DAG-SES`, `DAG-Mental`, `DAG-Functional`. Each needs to be locked in a working session with the user before associated EXP-16-HAND-* experiments execute. See [reference/research-plan.md §I](reference/research-plan.md) for the proposed DAGs.
- **A5.** **[P1] Sibling-dissociation pairs for non-cognitive outcomes.** Extend `SIBLINGS` in [experiments/cognitive-screening/run.py](experiments/cognitive-screening/run.py) (causal-screening block) with per-outcome overrides; re-run [experiments/multi-outcome-screening/run.py](experiments/multi-outcome-screening/run.py) with D3 active. The four EXP-16-HAND-* experiments need this.
- ~~**A6.** **[P1] Saturated-school stratification / sensitivity.**~~ **Resolved 2026-04-25:** decided to **restrict** the network-exposure estimand to within-saturated-schools (no extrapolation, no saturation-propensity weighting). Registered as [`EXP-16-SAT-BAL`](experiments/saturation-balance/README.md) for the balance table that quantifies external-validity gap.
- **A7.** **[P1] E-value / VanderWeele sensitivity bounds on the 4 handoff pairs.** Pairs registered as `EXP-16-HAND-IDGX2-WAIST`, `EXP-16-HAND-IDGX2-BMI`, `EXP-16-HAND-IDGX2-BMICLS` in [experiments/cardiometabolic-handoff/README.md](experiments/cardiometabolic-handoff/README.md), and `EXP-16-HAND-ODGX2-EARN` in [experiments/ses-handoff/README.md](experiments/ses-handoff/README.md). Each gets an E-value column for its primary β.
- **A8.** **[P1] Ordered-logit / interval-regression for `H5EC1`, `H5LM5`, `H4BMICLS`.** Folded into the per-handoff registrations: `EXP-16-HAND-IDGX2-BMICLS` uses ordered logit, `EXP-16-HAND-ODGX2-EARN` uses interval regression on bracket midpoints (combined with IPAW for W5 attrition).
- **A9.** **[P1] Bring `H4TO*` medication flags into the L1 covariate set for `H4SBP` / `H4DBP`.** Anti-hypertensive use is not currently adjusted; the null D4 on blood-pressure outcomes could be mechanical. Audit which `H4TO*` items are public-use and test sensitivity.
- ~~**A10.** **[P1] [JUDGMENT REQUIRED] Cluster-robust SE convention — pick one of three.**~~ **Resolved 2026-04-26:** trust statsmodels' built-in `use_correction=True` and use its default `df = n − k`. Manual `H − 1` t-quantile override removed from `scripts/analysis/wls.py`; methods.md §3 updated. Survey weights are now normalised to mean 1 before WLS so `use_correction` operates on the right σ̂² scale.
- **A11.** **[P1] [JUDGMENT REQUIRED] Sibling/twin within-school dependence is unaccounted-for.** Add Health public-use ships approximate sibling/twin pairs (Wave I oversampled twins, full siblings, half siblings). Cluster-robust SE on `CLUSTER2` only handles between-school clustering, not within-household sibling correlation. Three options: (a) document explicitly that sibling correlation is assumed inside the school PSU and audit how many sibling pairs cross PSUs; (b) implement two-way clustering on `(CLUSTER2, family_id)` if a household-id variable is in public-use; (c) one-respondent-per-family sensitivity. User chose to start with (a) — audit is pending.
- ~~**A12.** **[P1] Apply BH-FDR within each outcome on the D1 grid.**~~ **Resolved 2026-04-26:** `d1_q` column added to both `14_screening_matrix.csv` (cognitive screen) and `15_multi_outcome_matrix.csv` (multi-outcome) using `scipy.stats.false_discovery_control` (with manual fallback).
- ~~**A13.** **[P1] Add side-by-side AHPVT-dropped column for SES outcomes in multi-outcome screen.**~~ **Resolved 2026-04-26:** `beta_no_ahpvt`, `se_no_ahpvt`, `p_no_ahpvt` columns added for `H5EC1` and `H5LM5` in the multi-outcome matrix. Empirically the AHPVT-dropped p-values are smaller for several network exposures (REACH: 0.005 → 0.0005; INFLDMN: 0.015 → 0.00056), confirming the over-adjustment was real.
- **A14.** **[P1] Add saturated-school × covariate-stratum positivity diagnostic to `saturation-balance` experiment.** The "ATE within saturated schools" estimand is identified only if positivity holds at every level of L0+L1+AHPVT. D7 in the screen only checks one slice. Tabulate joint covariate-stratum cell counts within saturated schools, flag any cell with N < 10 or no exposure variation. Costs nothing additional.
- **A15.** **[P1] AHPVT trajectory framing: empirical sanity check W1 → W3.** Add Health ships a W3 AHPVT (`w3pvt.sas7bdat`) — the cheapest possible test of trajectory framing. Regress (W3_PVT − W1_PVT) on W1 social integration with L0+L1 adjustment. Add to `cognitive-frontdoor` or as a standalone diagnostic.
- **A16.** **[P1] [JUDGMENT REQUIRED] D3 sibling-dissociation pairs for cognitive screen are dependent constructs, not independent siblings.** Using `ODGX2` as the sibling for `IDGX2`, and `ODGX2` again as the sibling for `BCENT10X`, is low-power because they share the friendship roster (empirical r ≈ 0.5+). Re-pair with structurally orthogonal exposures (e.g. `IDGX2` vs `ESDEN`; `BCENT10X` vs `INFLDMN`), or skip D3 for these.
- ~~**A17.** **[P1] [JUDGMENT REQUIRED] D6 dose-response 0.7 threshold.**~~ **Resolved 2026-04-26:** loosened to the conventional 0.6 cutoff. Code and methods.md updated.
- **A18.** **[P1] [JUDGMENT REQUIRED] D4 30% threshold computed against post-AHPVT β as denominator.** When AHPVT shrinks β toward 0 (the headline finding), the divisor is tiny and rel-shift blows up — D4 *automatically* fails any exposure where AHPVT eats most of the signal. User noted: "it's pretty obvious AHPVT will eat up most of the signal" (so this isn't surprising), but the metric is partially circular as a "hidden confounding" detector. Open: add a parallel D4 metric (absolute shift / L0-β SE) to the matrix; or add a journal footnote framing the failure as expected.
- **A19.** **[P2] Wild-cluster bootstrap on W5 cells in handoff experiments.** W5 cells hit N as low as ~394 (network-gated). Add Cameron–Gelbach–Miller wild-cluster bootstrap as sensitivity row in handoff forest.
- **A20.** **[P2] Expand W5 mode-selection probit covariate set.** Per `dataset_manual.md §4.5`, W5 mode is mostly Add-Health field choice (Web default, In-person/Telephone for non-respondents to cheaper modes), making it endogenous to SES, geographic accessibility, and prior-wave engagement. Expand probit to include all L0+L1 plus a "prior-wave engagement" proxy. Note: the audit's separate "expand to full cohort, drop the IDGX2 ∩ subsample restriction" framing was rejected — IDGX2 is structurally undefined outside saturated schools, the subsample restriction is correct.
- **A21.** **[P2] W6 self-reported memory (`H6DA18B`–`H6DA18F`) as a tertiary cognitive outcome.** Public-use W6 has no performance cognition but does have self-reported memory items.
- **A22.** **[P2] Manski bounds as a fallback when IPAW is not credible.** Keep in the back pocket for handoff pairs whose IPAW fit is noisy.

---

## B. Correctness / real bugs

- ~~**B1.** **[P0] `derive_w5_bds` NaN handling.**~~ **Resolved 2026-04-26 (keep current behaviour):** empirical investigation showed 100 % of in-person/phone W5 respondents (N = 625) have at least one NaN trial item, by design — the BDS protocol terminates after failing both trials at a length, leaving higher-L items as legitimate skip. The current "NaN as fail" semantic is correct for the terminate-after-failure case (≈ 99 % of NaNs). Edge case (real missing inside an attempted sequence) is rare and currently mis-scored as "highest-passed" rather than "indeterminate"; documented in the function docstring. The xfail test in `tests/test_derivation.py` documents the alternative semantic and stays xfail by user decision.
- ~~**B2.** **[P0] D6 threshold drift.**~~ **Resolved 2026-04-26:** code updated to `|ρ| > 0.6` (the conventional cutoff); methods.md §2 updated to match.
- ~~**B3.** **[P0] Reserve-code stripping is opt-in via `VALID_RANGES`.**~~ **Resolved 2026-04-26:** `clean_var` now emits a `UserWarning` when called on a name absent from `VALID_RANGES`. Surfaces silent pass-through immediately (e.g. confirmed `H1PR4` is missing from `VALID_RANGES` — a separate fix).
- ~~**B4.** **[P0] `weighted_mean_se` and `weighted_ols` do not filter NaN PSU values.**~~ **Resolved 2026-04-26:** both masks now include `~pd.isna(psu)`. NaN cluster IDs no longer contribute to numerator while vanishing from cluster-variance.
- ~~**B5.** **[P0] Verification block re-derives `PARENT_ED` on raw 1-9 codes; race uses `.fillna(0)` then exclusion-to-Other.**~~ **Resolved 2026-04-26:** `experiments/cognitive-screening/run.py` verification block now calls `derive_parent_ed(w1race)` and `derive_race_ethnicity(w1race)` from the canonical helpers.
- ~~**B6.** **[P0] [JUDGMENT REQUIRED] `derive_parent_ed` recodes "don't know / other" parent-ed codes (10, 11) as post-grad (6).**~~ **Resolved 2026-04-26 (NaN throughout):** `VALID_RANGES["H1RM1"]` and `["H1RF1"]` tightened from `(1, 11)` to `(1, 9)` so codes 10/11/12 strip to NaN at the `clean_var` stage. The recode now maps **only code 8** (professional training beyond a 4-year college, which is genuinely post-bachelor's) to ordinal 6. Tests updated.
- ~~**B7.** **[P0] [JUDGMENT REQUIRED] `report.md` claim C1 ("strong") rests on a screening estimate.**~~ **Resolved 2026-04-26:** C1 demoted to **provisional** with explicit "re-rate after handoff lands" caveat in the Evidence column. The H4BMICLS sub-pair (linear-on-ordinal screening β) is also flagged in the C1 evidence note pending ordered-logit re-estimation.
- ~~**B8.** **[P0] [JUDGMENT REQUIRED] DAG-Cog adjustment-set justification doesn't match the drawn DAG: `PED → SOC` arrow missing.**~~ **Verified 2026-04-26:** the diagram already has `PED --> SOC` (line 45 of `dag_library.md`). Audit was incorrect.
- ~~**B9.** **[P1] `weighted_ols` does not normalise survey weights.**~~ **Resolved 2026-04-26:** weights now normalised to mean 1 (`w * len(w) / w.sum()`) before being passed to `sm.WLS`. Point estimate is invariant; `use_correction=True` now operates on the right σ̂² scale.
- ~~**B10.** **[P1] Verification IPW comparison row uses hardcoded β/p/N for the "Primary" baseline.**~~ **Resolved 2026-04-26:** the Primary row now refits the anchor model live and pulls β/p/N from the fresh result.
- ~~**B11.** **[P1] `scripts/prep/05_weighted_descriptives.py` re-implements analysis helpers.**~~ **Resolved 2026-04-26:** prep/05 now imports `VALID_RANGES`, `clean_var`, `weighted_mean_se`, `weighted_prop_ci`, `derive_cesd_sum`, `derive_w5_bds`, and `CESD_ITEMS` from the analysis package. ~150 lines of duplication deleted.
- ~~**B12.** **[P1] [JUDGMENT REQUIRED] `derive_cesd_sum` strict listwise zeros respondents with one missing item.**~~ **Resolved 2026-04-26 (relax to min_valid=15 + scaling):** `derive_cesd_sum` now defaults to `min_valid=15`; respondents with 15-19 valid items get a *scaled* sum (`raw * 19 / n_valid`) on the canonical 0-57 scale. Below 15 valid → NaN. Tests updated.
- ~~**B13.** **[P1] D1/D2 NaN vs FAIL conflation.**~~ **Resolved 2026-04-26:** `_d1_baseline` and `_d2_negctrl` now return `pass: None` for degenerate fits (n=0 or H<2 or NaN p), distinguished from `pass: False` in `_classify_screening`'s scoring.
- ~~**B14.** **[P1] `_classify_screening` references `r["d2_p"] < 0.05` without NaN guard.**~~ **Resolved 2026-04-26:** `pd.notna()` guards added before all D2/D3 p-comparisons.
- ~~**B15.** **[P1] D2 (`HEIGHT_IN`) drives "Drop" classification, contradicting `dataset_manual.md`'s "do not drop on D2 alone" rule.**~~ **Resolved 2026-04-26:** D2-Drop branch removed from `_classify_screening`. D2 fails are now an annotation rather than a classification driver.
- ~~**B16.** **[P1] [JUDGMENT REQUIRED] `derive_friendship_grid` silently maps NaN-anchor to "not nominated".**~~ **Resolved 2026-04-26 (propagate NaN):** the helper now tracks an "any anchor observed" mask. Respondents with NaN at every `H1MF2*`/`H1FF2*` item now get NaN for all three returned columns instead of silently 0/0/0.
- ~~**B17.** **[P1] [JUDGMENT REQUIRED] `derive_friendship_grid` double-counts item 9.**~~ **Resolved 2026-04-26 (drop item 9 from CONTACT):** `FRIEND_ITEMS_CONTACT` is now `[6, 7, 8, 10]` (item 9 is the disclosure anchor and is no longer counted in contact-sum). Tests updated.
- **B18.** **[P1] [JUDGMENT REQUIRED — REJECTED] `_w5_mode_selection` Probit silently drops every NaN-IDGX2 row.** **Decision 2026-04-26:** keep current behaviour. The audit's "expand to full cohort" framing is incoherent — IDGX2 is structurally undefined outside saturated schools (positivity = 0); the probit *correctly* operates within the network sample. Title may benefit from clarifying "within the W1-network subsample" — see A20 for a separate covariate-set expansion task.
- ~~**B19.** **[P1] Dead `np` import in cleaning.py; dead `os` import in prep/05.**~~ **Resolved 2026-04-26:** both deleted.
- ~~**B20.** **[P1] `prep/06_attrition.py:_df_to_md` renders NaN as the string "nan".**~~ **Resolved 2026-04-26:** branch ordering fixed; `pd.isna(v)` runs before `isinstance(v, float)`. Test renamed `test_df_to_md_handles_nan_renders_as_empty` and updated.
- **B21.** **[P1] `prep/05_weighted_descriptives.py:summarize_block` binary heuristic still misclassifies PRXPREST without the explicit override.** Test-coverage agent surfaced 2026-04-25; pinned with `test_summarize_block_prxprest_default_misclassified_binary`. Workaround (explicit `kinds={"PRXPREST": "continuous"}` override) is in place; harden the heuristic itself when convenient (check unique-value count or dtype, not just `(lo, hi) == (0, 1)`).

---

## C. Documentation errors / discrepancies

Cross-checked across [reference/dataset_manual.md](reference/dataset_manual.md), [reference/research_journal.md](reference/research_journal.md), and [reference/variable_dictionary.md](reference/variable_dictionary.md).

- ~~**C1.** **[P0] Cognitive-screening shortlist contradicts the project's actual handoff plan.**~~ **Resolved 2026-04-26:** `experiments/cognitive-screening/run.py` now emits an explicit "this is the cognitive-only shortlist; cross-outcome handoff candidates come from `experiments/multi-outcome-screening`" callout in `14_screening.md`. The full handoff plan (with proposed DAGs) lives in [reference/research-plan.md §I](reference/research-plan.md).
- ~~**C2.** **[P0] "Estimand wording" missing from 4 of 7 experiment field tables.**~~ **Resolved 2026-04-26:** Phase 4 Agent E added Estimand wording rows to cardiometabolic-handoff, ses-handoff, negative-control-battery, and saturation-balance READMEs.
- ~~**C3.** **[P1] [JUDGMENT REQUIRED] Phantom experiment ID `EXP-16-IPAW-W5`.**~~ **Resolved 2026-04-26:** decision (per A3) is that IPAW is shared library code (`scripts/analysis/ipw.py`), not a separate experiment. Action items: replace the two `EXP-16-IPAW-W5` references in `experiments/ses-handoff/README.md` and `experiments/README.md` with "(via the IPAW utility, see TODO §A3)". Pending text edits.
- ~~**C4.** **[P1] [JUDGMENT REQUIRED] `H1FS13`/`H1FS14`/`H1DA7`/`H1PR4` `kind` mismatch.**~~ **Resolved 2026-04-26:** code retagged `ordinal` (was `continuous`) in both cognitive-screening and multi-outcome-screening run.py files. Aligned with variable-dictionary labels. Behaviour unchanged for now (current D6/D7 logic treats ordinal and continuous the same), but tagging is consistent for documentation and future ordinal-aware logic.
- ~~**C5.** **[P1] D5 pass criterion in `methods.md` omits the `n_sig ≥ 2` requirement.**~~ **Resolved 2026-04-26:** Phase 4 Agent E added the `n_sig ≥ 2` clause to methods.md §2 D5 row.
- ~~**C6.** **[P1] W5 cognitive cell N described inconsistently across docs.**~~ **Resolved 2026-04-26:** Phase 4 Agent E unified the wording (824 / ~620 / ~394 cascade documented in methods.md, glossary.md, dataset_manual.md, variable_dictionary.md).
- ~~**C7.** **[P1] [JUDGMENT REQUIRED] `report.md` cites IDGX2 → H4BMICLS as Strong but the screen treats it as linear-on-ordinal.**~~ **Resolved 2026-04-26 (provisional):** subsumed under B7 — C1 is now globally provisional. The H4BMICLS-specific caveat is folded into the Evidence-column note pending the ordered-logit re-estimation in `cardiometabolic-handoff`.
- **C8.** **[P1] `dataset_eda.ipynb` is described as moved but lives at repo root.** **Decision 2026-04-26:** leave at root — it's the user's project partner's code and is not part of the active pipeline.
- ~~**C9.** **[P1] `ATE` undefined in glossary.**~~ **Resolved 2026-04-26:** Phase 4 Agent E added an ATE entry to glossary.md alphabetically.
- ~~**C10.** **[P1] Stale "task14"/"task10"/"task15" jargon in auto-generated outputs and variable_dictionary.**~~ **Resolved 2026-04-26:** Phase 4 Agent E swept variable_dictionary.md; cognitive-screening/run.py and multi-outcome-screening/run.py prose updated; both screens re-run.
- ~~**C11.** **[P1] Broken anchor: research_journal cites a missing variable_dictionary heading.**~~ **Resolved 2026-04-26:** Phase 4 Agent E updated the journal link to the correct anchor.
- ~~**C12.** **[P1] `prep/04_missingness.py:infer_scheme` more conservative than its docstring.**~~ **Resolved 2026-04-26:** Phase 4 Agent E updated the docstring.
- **C13.** **[P2] Variable dictionary lists families but not their full members.** Decide whether to (a) link to the existing per-family files, or (b) accept the current state.
- **C14.** **[P2] dataset_manual.md §6 "Analytic feasibility" table** still uses "W5 imm" and "W5 backward digit span (derived)" language that conflicts with the multi-outcome framing. One-line note tying §6 row to [variable_dictionary.md §2.5](reference/variable_dictionary.md#25-secondary-outcomes--task-15-multi-outcome-extension-12) would help.
- **C15.** **[P2] N drift between docs.** Synthesis §3.1 quotes 4,397; journal Phase 2 quotes 3,238; dictionary quotes 3,268 — all correct for different stages. One-line note explaining the cascade would remove confusion.
- ~~**C16.** **[P2] [JUDGMENT REQUIRED] `[TODO.md A7]` style links are informal — TODO.md unnumbered.**~~ **Resolved 2026-04-26:** TODO.md is now numbered (this rewrite). Bullet IDs are stable across additions; resolved items keep their ID.
- ~~**C17.** **[P2] Variable dictionary quick-ref omits `C5WD60_1`.**~~ **Resolved 2026-04-26:** Phase 4 Agent E added the row.
- ~~**C18.** **[P2] dataset_manual.md Changelog references stale path `scripts/task05_weighted_descriptives.py`.**~~ **Resolved 2026-04-26:** Phase 4 Agent E trimmed the parenthetical.

---

## D. Reproducibility / infrastructure

- **D1.** **[P1] No top-level orchestrator.** Write a minimal `run_all.py` that invokes the prep pipeline ([scripts/prep/01_file_inventory.py](scripts/prep/01_file_inventory.py) → … → [scripts/prep/09_distribution_plots.py](scripts/prep/09_distribution_plots.py)) followed by [experiments/cognitive-screening/run.py](experiments/cognitive-screening/run.py) and [experiments/multi-outcome-screening/run.py](experiments/multi-outcome-screening/run.py) with `--skip-if-fresh` semantics.
- **D2.** **[P2] Print-based logging throughout.** Swap to `logging` module with a configurable level when the repo gets a CI or long-running orchestrator.
- ~~**D3.** **[P2] SCC deployment path.**~~ **Removed 2026-04-26 (out of scope):** project runs locally; SCC support not pursued.
- ~~**D4.** **[P2] Stub modules `analysis.diagnostics`/`frontdoor`/`ipw`/`sensitivity` advertised in __init__.py but only contain docstrings.**~~ **Resolved 2026-04-26:** each stub now `raise NotImplementedError("...see TODO §A...")` at import.
- **D5.** **[P2] EXPOSURES registry duplicated between cognitive-screening and multi-outcome-screening.** Move `NETWORK_EXPOSURES`, `SURVEY_EXPOSURES`, `EXPOSURES`, `RED_FLAGS`, `SIBLINGS`, `RACE_LEVELS`, `_adj_*`, `ADJ_BUILDERS` into `scripts/analysis/diagnostics.py`. Both experiments import from there. Kills the duplicated-stub problem too.
- ~~**D6.** **[P2] `analysis.plot_style.IMG` and `plot_style.save` are dead code.**~~ **Resolved 2026-04-26:** both deleted.
- **D7.** **[P2] `_save` helper duplicated in three figure modules.** Refactor `analysis.plot_style.save` to take an absolute destination Path, then have all three callers import it.

---

## E. Plot & output hygiene

- ~~**E1.** **[P1] D9 column header in screening heatmap reads "D9 red flag" but green = no red flag.**~~ **Resolved 2026-04-26:** column header renamed `"D9 (no red flag)"`; green-means-good now lines up with the visual convention.
- **E2.** **[P2] `derive_w5_bds` `dtype=float` cast is load-bearing but undocumented.** A maintainer who tightens to int will silently break the all-missing-NaN case. Add a one-line comment.

---

## F. Nice-to-haves / stretch

- **F1.** **[P2] Plain-text DAG diagram** in [methods.md §1](reference/methods.md#1-identification-assumptions-and-target-estimand). Described textually; rendering as a `mermaid` block or PNG would help briefings (note: [dag_library.md](reference/dag_library.md) already has the canonical Mermaid `DAG-Cog` block).
- **F2.** **[P2] Pre-commit hook or CI check** that re-runs the reference-doc cross-consistency audit and fails on broken anchors / missing variable entries.
- **F3.** **[P2] Dictionary quick-ref by-role index.** Right now alphabetical; a reader looking at a forest plot wants *all exposures in that forest plot's cluster*. A secondary by-role index at the bottom of the quick-ref would help.

---

## G. Session-completed items (chronological, for traceability)

- ~~PRXPREST binary-vs-continuous miscoding fixed in [scripts/prep/05_weighted_descriptives.py](scripts/prep/05_weighted_descriptives.py).~~ **Done 2026-04-22.**
- ~~D3 sibling-dissociation sign-agreement bug.~~ **Fixed earlier in this conversation; verified.**
- ~~Baked-in titles stripped from PNGs embedded in `research_journal.md`.~~ **Done 2026-04-22.**
- ~~Variable dictionary restructured into quick-ref + detailed sections.~~ **Done 2026-04-22.**
- ~~Synthesis §5.6 / §6.5 / Glossary additions.~~ **Done 2026-04-22.** (Subsequently moved to `methods.md` / `glossary.md` by Phase 3 demolition.)
- ~~Stata/R recipes removed from synthesis §2.4.~~ **Done 2026-04-22.**
- ~~Broken anchor `#45-wave-v-cognitive-battery-...` fixed.~~ **Done 2026-04-22.**
- ~~Stale "earlier notes were wrong" self-references audited.~~ **Done 2026-04-22.**
- ~~`requirements.txt` was incomplete.~~ **Done 2026-04-25.**
- ~~Hardcoded absolute path in 10+ files.~~ **Done 2026-04-25 — replaced with `Path(__file__).resolve().parent.parent`.**
- ~~README was effectively empty.~~ **Done 2026-04-26 — Phase 4 Agent F.**
- ~~No test suite.~~ **Done 2026-04-26 — Phase 1 created `tests/`; test-coverage agent expanded to 133 tests covering 90% of `scripts/analysis/`.**
- ~~Repo restructure (5 phases).~~ **Done 2026-04-25 / 2026-04-26.**
- ~~Add `tabulate` to requirements.txt.~~ **Done 2026-04-25.**
- ~~Cache directory move from `outputs/cache/` to top-level `cache/`.~~ **Done 2026-04-26.**
- ~~Misleading comment in `derive_school_belonging`.~~ **Done 2026-04-25.**
- ~~Hardcoded saturation fraction `0.324` replaced with `SATURATED_LOSS_FRAC`.~~ **Done 2026-04-25.**
- ~~Variable dictionary missing `C5WD90_1`, `H1FS1`, `W5_COG_COMP`.~~ **Done 2026-04-25.**
- ~~Missing dictionary entries for `C4WD60`, `C4WD90`, `H1GH28`.~~ **Done 2026-04-25.**
- ~~Synthesis deliverables index missing task09, task12, task15_journal_figs.~~ **Done 2026-04-25.**
- ~~`outputs/cache/` ignored by git correctly.~~ **Verified 2026-04-25.**
- ~~Re-run prep distribution plots + cognitive-screening figures to confirm no baked-in titles.~~ **Done 2026-04-25.**
- ~~`H5LM5` "despite earlier notes" caveat cleanup.~~ **Done 2026-04-25.**
- ~~Consistent colourmap for outcome groups across charts.~~ **Done 2026-04-25.**
- ~~Repo's canonical citation in `CITATION.cff`.~~ **Done 2026-04-25.**

---

## Audit pass (2026-04-26) summary

A three-agent audit on 2026-04-26 (scientific methodology, code correctness, cross-doc consistency) plus a test-coverage expansion surfaced 53 new findings folded into the sections above. After the round-2 user decisions were implemented:

- **A (research pipeline):** A6, A10, A12, A13, A17 resolved; 5 open `[JUDGMENT REQUIRED]` (A11 sibling-dependence, A16 D3 siblings, A18 D4 metric, plus methodology brainstorms in research-plan.md).
- **B (correctness):** 14 of 21 items resolved (B1-B6, B7-B11, B13-B17, B19-B20). 1 explicitly rejected (B18). 6 open / pending (B12 absorbed by A11/A16/A18 judgment chains; B21 hardening of summarize_block heuristic; etc.).
- **C (docs):** 12 of 18 items resolved. 1 rejected (C8 `dataset_eda.ipynb` stays at root). 5 open as P2 polish.
- **D (infrastructure):** 1 dropped (D3 SCC). 2 resolved. 4 open as P2.
- **E (plot hygiene):** 1 of 2 resolved.

133 passing pytest cases + 1 xfail (the `derive_w5_bds` xfail, retained per B1's keep-current-behaviour decision).

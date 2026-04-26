# Research plan — handoffs and future questions

A working document that complements the experiment-folder field tables. **Part I** spells out the concrete next steps for each registered handoff experiment, the proposed per-outcome DAGs, and the open methodological calls. **Part II** is an open brainstorm of new research questions worth pursuing once the current handoff slate lands.

This is a *plan*, not a deliverable. Treat it as a living scratchpad — additions welcome; everything is subject to revision before any experiment runs.

---

## Part I — Concrete handoff plan

### Recap: what the screen handed us

The cognitive screen's classifier ranks exposures on the `W4_COG_COMP` outcome, where (per the trajectory framing) AHPVT eats most of the signal. The cognitive-only "shortlist" emitted by `14_screening.md` is `BCENT10X`, `ODGX2` — those are the cognitive winners.

The **multi-outcome screen** is what produced the genuinely interesting handoff candidates — exposures whose β survives the L0+L1+AHPVT adjustment on *non-cognitive* outcomes, where AHPVT is not a load-bearing covariate. The four pairs that passed both D1 (β significantly non-zero) and D4 (β stable across L0 / L0+L1 / L0+L1+AHPVT to within 30 %) are:

| Exposure | Outcome | Screen β | Screen p | D4 rel-shift |
|---|---|---|---|---|
| `IDGX2` | `H4WAIST` (waist circumference, cm) | -0.51 | 1.9 × 10⁻¹¹ | 18 % |
| `IDGX2` | `H4BMI` (BMI, kg/m²) | -0.20 | 6.8 × 10⁻⁹ | 21 % |
| `IDGX2` | `H4BMICLS` (BMI class, 1-6 ordinal) | -0.032 | 5.0 × 10⁻⁸ | passes |
| `ODGX2` | `H5EC1` (W4-W5 personal earnings, bracketed 1-13) | +0.10 | 1.4 × 10⁻⁴ | passes |

These four were registered as planned experiments back in Phase 2:

- `experiments/cardiometabolic-handoff/` — three IDGX2 → cardiometabolic pairs, one folder.
- `experiments/ses-handoff/` — ODGX2 → earnings.
- `experiments/cognitive-frontdoor/` — sensitivity check on the AHPVT trajectory framing (IDGX2 → W4_COG_COMP via the strict-mediator reading).
- `experiments/negative-control-battery/` — replace the contaminated `HEIGHT_IN` D2 with cleaner NCs.
- `experiments/saturation-balance/` — within/between saturated-school covariate balance table.

Plus a few candidate pairs that **did not** make the original handoff list but are worth revisiting under the AHPVT-dropped multi-outcome columns we just added (`beta_no_ahpvt`/`p_no_ahpvt`):

- `REACH → H5EC1` (AHPVT-adjusted p = 0.005, AHPVT-dropped p = 0.0005 — nearly an order of magnitude tighter)
- `INFLDMN → H5EC1` (p = 0.015 → 0.00056)
- `REACH3 → H5EC1` (p = 0.00037 → 0.00011)

That's a hint that the SES-DAG over-adjustment for AHPVT may have been hiding a broader pattern — multiple network-position measures predict adult earnings under the methodologically-correct adjustment set.

### Per-experiment plan

#### 1. `cognitive-frontdoor/` — sensitivity check on the trajectory framing

**Status:** stub (registered, not started).
**Question:** under the strict mediator reading (W1 social integration → AHPVT → W4 cognition), how much does the cognitive-screening β shift?

**Proposed DAG (`DAG-Cog-FrontDoor`):**

```
       SEX, RACE, PED ──────┐
                            ├──→ AHPVT ──→ W4_COG_COMP
                            │     ▲
   W1 social integration ───┘     │
       (e.g. IDGX2)               │
                                  │
   PED, CESD, SRH ─────────────── ┘
   (front-door confounders of M → Y)
```

The front-door criterion identifies the SOC → Y total effect through the fully-mediating M = AHPVT *if and only if* (i) all of the SOC → Y effect goes through AHPVT, (ii) no unmeasured confounders between M and Y. Both assumptions are a stretch for this design — that's why the result is a sensitivity check, not a primary identification.

**Method:**
1. Stage 1: regress AHPVT on W1 social integration (the SOC-to-M arrow), adjusting for L0 (= front-door's PED + SEX + RACE).
2. Stage 2: regress W4_COG_COMP on AHPVT and W1 social integration (the M-to-Y arrow with X residualised in), adjusting for L0+L1 (= the M-to-Y back-door set; AHPVT is not in this set since it's the mediator).
3. Combine via Pearl's front-door formula `E[Y | do(SOC=x)] = Σ_m P(M=m | SOC=x) · Σ_x' E[Y | M=m, SOC=x'] · P(SOC=x')`.

**Compare:** β_FD (front-door total effect) vs β_traj (trajectory-adjusted from cognitive-screening, which conditions on AHPVT). The **gap** β_FD − β_traj is the magnitude by which the trajectory framing under-estimates the SOC effect *if* the strict mediator reading is correct.

**Pre-flight sanity check (per TODO §A15):** regress (W3_PVT − W1_PVT) on W1 social integration with L0+L1 adjustment. If this slope is significantly non-zero, the strict mediator reading is empirically supported and the front-door gap will be more interpretable. If it's null, the trajectory framing is corroborated and the front-door is the looser-bound sensitivity reading.

**Open methodological calls:** none of the front-door's three identifying assumptions can be empirically tested with public-use data. The result is interpretable only as "if the strict mediator reading is true, the SOC effect would be β_FD."

---

#### 2. `cardiometabolic-handoff/` — three IDGX2 → adult adiposity pairs

**Status:** stub.
**Pairs:** IDGX2 → `H4WAIST`, `H4BMI`, `H4BMICLS`.

**Proposed DAG (`DAG-CardioMet`, draft):**

```
       SEX, RACE, PED ──────────────┐
       AHPVT (baseline cog) ────────┤
       CESD (W1 affect) ────────────┤
       SRH (W1 health) ─────────────┤
                                    │
   IDGX2 (W1 social int.) ──────────┼──→ adult adiposity
                                    │    (BMI / waist / class)
       H1GH28 (W1 self-rep weight) ─┘    
       Mediators (NOT adjusted):
         • adult diet / activity / SES
         • adult mental health
         • adult smoking
```

Key differences from `DAG-Cog`:
- **Add `H1GH28` (W1 self-reported weight)** to the L1 covariate set. Adult adiposity is strongly autocorrelated from adolescence; not adjusting for baseline weight inflates the SOC β.
- **Keep AHPVT** (debatable; AHPVT predicts educational attainment which predicts adult adiposity via multiple pathways — could be confounder). Run sensitivity with AHPVT-dropped to bracket the bias direction.
- **Do NOT adjust for** adult diet, physical activity, smoking, or mental health: these are post-W1 mediators of the SOC → adiposity pathway. Adjusting for them blocks the very channels we're trying to measure.

**Method:**
- `H4WAIST`, `H4BMI`: WLS + cluster-robust SE (same as cognitive screen). Continuous outcomes; the screen's linear-in-Y assumption is fine.
- `H4BMICLS` (1-6 ordinal): **ordered logit** with cluster-robust SE on `CLUSTER2`. The screen's β = -0.032 on the linear-in-Y treatment is interpretable only as "the BMI-class drops on average by 0.032 per IDGX2 unit" — not a real ordered-effect magnitude. Ordered logit gives proportional-odds coefficients you can defend.

**E-value (per TODO §A7):** for each pair, compute the VanderWeele E-value — the minimum strength of association (with both IDGX2 and the outcome) an unmeasured confounder would need to fully explain away the observed β. Report alongside the point estimate. Big E-value → causal claim is robust; small E-value → claim is fragile to even modest unmeasured confounding.

**N considerations:** IDGX2 ∩ H4WAIST/H4BMI ≈ 3,250 (network-gated). Plenty of cluster mass.

**Open methodological calls:**
- **Should AHPVT stay in the cardiometabolic adjustment set?** The case *for*: AHPVT proxies childhood verbal exposure / family environment, which independently predicts adult adiposity. The case *against*: AHPVT could be a mediator of SOC → SES → adiposity. Compromise: report both βs.
- **What about H1GH28's reverse causation?** If high-IDGX2 adolescents are *already* slimmer at W1 (popularity correlates with looks), conditioning on H1GH28 is conditioning on a partial outcome. Need to check the W1 baseline weight × IDGX2 partial correlation before deciding. If the correlation is small, H1GH28 is a clean confounder; if large, treat carefully.

---

#### 3. `ses-handoff/` — ODGX2 → adult earnings

**Status:** stub.
**Pair:** ODGX2 → H5EC1 (bracketed 1-13 personal earnings, W4-W5).

**Proposed DAG (`DAG-SES`, draft):**

```
       SEX, RACE, PED ──────────────┐
       CESD (W1 affect) ────────────┤
       SRH (W1 health) ─────────────┤
                                    │
   ODGX2 (W1 out-degree) ───────────┼──→ H5EC1
                                    │    (adult earnings)
       Mediators (NOT adjusted):
         • educational attainment
         • adult cognition (AHPVT-related)
         • adult occupation
```

Key differences from `DAG-Cog`:
- **Drop AHPVT** from the adjustment set. AHPVT predicts educational attainment which predicts earnings — it sits on the SOC → SES causal path. Conditioning on AHPVT blocks the channel we're trying to measure (already confirmed empirically: AHPVT-dropped β is ~3× larger and an order of magnitude more significant for many network exposures).
- **Add IPAW** (per TODO §A3) for W4→W5 attrition. W5 retention is sex × race patterned; female retention 64-76 % vs male 43-63 % within race strata. The screening pass uses `GSWGT4_2` uniformly — that's a comparability shortcut, not an estimation-grade weight. Layer IPAW × `GSW5` per the canonical W5 weighting protocol.

**Method:**
- **Interval regression** on the bracket midpoints: H5EC1 is observed only as one of 13 earnings brackets, not as continuous earnings. Treat the latent log-earnings as continuous within each bracket; the likelihood is the integral of the conditional log-earnings density over the bracket interval.
- Cluster-robust SE on `CLUSTER2`.
- IPAW × `GSW5` weights, trimmed at 95th percentile.

**E-value:** same as cardiometabolic.

**N considerations:** ODGX2 ∩ H5EC1 ≈ 1,200 (network-gated and W5-administered with mode restriction). Smaller cell — wild-cluster bootstrap (TODO §A19) probably worth running here.

**Open methodological calls:**
- **Should we also fit the linear-in-Y screening β alongside the interval regression?** Yes — for direct comparison with the screening output. Don't only report the interval regression.
- **What pre-W1 confounders should we worry about?** Family SES, neighbourhood, parental social network — all unmeasured. NC battery (cardiometabolic-handoff doesn't share the same NC) needs to bear weight here.

---

#### 4. `negative-control-battery/` — clean NC outcomes

**Status:** stub.
**Purpose:** the current D2 negative-control outcome (`HEIGHT_IN`) is contaminated by adolescent-height-popularity literature; D2 fails on `IDGX2`/`BCENT10X` are not unambiguously evidence of unmeasured confounding. Replace with a battery of structurally unrelated outcomes that *should* be null under causal-IDGX2-on-cognition.

**Candidate NC outcomes (from the audit; pre-flight required):**
- **Blood type** — biologically determined at conception, no plausible exposure-outcome path.
- **Age at menarche** — biologically determined by genes + early-childhood factors, well before W1 social integration is observed.
- **Hand-dominance** — neurodevelopmental, fixed by toddlerhood.
- **Residential stability pre-W1** — number of residential moves before age 12, predates W1 friendship roster.

**Pre-flight (must run before any analytic work):** verify each NC is in the public-use distribution. ICPSR 21600 v26 may have one or two of these in restricted-use only. Document availability + recode in `variable_dictionary.md` before drafting the DAG addendum.

**Method:**
- For each available NC, run the same WLS + cluster-SE spec as the cognitive screen, with all 24 W1 social exposures.
- Report per-exposure NC-failure forest (β, p, E-value).
- An exposure that fails *multiple* NCs is far more suspect than one that fails the contaminated `HEIGHT_IN` alone.

**Open methodological calls:**
- **What does "fail" mean here?** Audit's threshold was p < 0.10 on any NC. Probably acceptable, but with multiple NCs we should also apply BH-FDR within exposure across the NC set.

---

#### 5. `saturation-balance/` — within/between saturated-school covariate balance

**Status:** stub.
**Purpose:** the network-exposure estimand is "ATE within saturated schools." Make the external-validity gap empirically visible.

**Method:**
- Compute survey-weighted (using `GSWGT1`) means and proportions of every L0+L1+AHPVT covariate, within saturated vs. non-saturated schools.
- Add SMD (standardised mean difference) column for visual scan.
- Plus the joint covariate-stratum positivity diagnostic per TODO §A14.

**Output:**
- `saturation-balance/tables/primary/balance.csv` — covariate × school-saturation cell × (mean, SMD).
- `saturation-balance/figures/primary/balance_forest.png` — SMD forest plot.

**Estimand wording:** "Survey-weighted comparison of L0+L1+AHPVT covariate distributions across saturated- vs non-saturated schools, within the W1 in-home sample." Descriptive — there is no causal estimand here.

---

### Cross-cutting: shared method library work

Before any handoff experiment runs, three pieces of `scripts/analysis/` need real implementations (currently stubs):

1. **`scripts/analysis/ipw.py`** (TODO §A3): `fit_ipaw(design_frame, outcome_frame, covariates, trim_pct=0.05)` returning stabilised IPAW weights × `GSW5`. Used by ses-handoff and any W5-outcome handoff.
2. **`scripts/analysis/sensitivity.py`** (TODO §A7): `e_value(beta, se, outcome_sd)` — VanderWeele's formula for the unmeasured-confounder bound. Used by every handoff.
3. **`scripts/analysis/frontdoor.py`** (cognitive-frontdoor): three-equation decomposition utility. Used only by cognitive-frontdoor.

All three should land before the first handoff experiment runs, so the pattern is shared across handoffs.

---

## Part II — Open RQ brainstorm

Below: ~15 angles worth thinking about, beyond the registered handoffs. Each entry: what it asks, why it's interesting, what variables to use, rough method, why this dataset is or isn't a good fit. Some overlap with the existing four registered experiments — flagged where they do.

### Theme A: Indegree vs outdegree (your RQ #1)

#### A.i Mechanism asymmetry: what does being-chosen do that doing-the-choosing doesn't?

**Question.** For a single outcome, is the SOC effect driven primarily by IDGX2 (others choose you) or ODGX2 (you choose others)? Theoretically these encode different mechanisms: IDGX2 = received social status (peer validation, resource access); ODGX2 = self-perceived sociability (engagement, opportunity-seeking).

**Why it's interesting.** A pure popularity-status story predicts IDGX2 dominance (especially for outcomes mediated by self-concept / mental health). A social-engagement-skill story predicts ODGX2 dominance (especially for outcomes mediated by behavioural agency / earnings). The empirical pattern across outcome families is itself the finding.

**Operational test.** For each outcome family (cardiometabolic, mental, SES, functional), fit two parallel models — one with IDGX2 alone (controlling for ODGX2 and L0+L1+AHPVT), one with ODGX2 alone (controlling for IDGX2 and L0+L1+AHPVT). Compare the partial β's. The screen already has these cells, but no one has plotted IDGX2 β vs ODGX2 β for the same outcome to make the asymmetry visible.

**Method.** WLS + cluster-SE; same adjustment as the per-outcome handoff DAG. Plot the (IDGX2 β, ODGX2 β) point per outcome with a 45° reference line.

**Status.** Could be done as a one-figure addition to multi-outcome-screening's report.md without a new experiment folder. Cheap.

#### A.ii Do reciprocated nominations (mutual friendships) matter more than unreciprocated?

**Question.** `BMFRECIP` and `BFFRECIP` are the proportion of male / female nominations that are mutual. Reciprocated ties are theoretically the trust-and-disclosure channel; unreciprocated ties signal aspirational hierarchy or social desire. Different mechanisms → different outcomes.

**Why it's interesting.** Two respondents with IDGX2 = 5 are not equivalent if one has 5 mutual ties and the other has 5 unreciprocated nominations from social-aspirational peers. The latter may signal status anxiety; the former, social support.

**Operational test.** Decompose IDGX2 into reciprocated and unreciprocated components; rerun the multi-outcome screen with both columns. Compare β-by-outcome.

**Method.** WLS as above. Caveat: `BMFRECIP`/`BFFRECIP` are *proportions*, not counts; algebraically interacting them with IDGX2 captures the count of reciprocated ties.

### Theme B: Outcome-specific sensitivity (your RQ #2)

#### B.i Which adult outcomes are *most* moved by adolescent popularity?

**Question.** Cross-outcome ranking of IDGX2's standardised β under the per-outcome correct DAG.

**Why it's interesting.** The multi-outcome screen ran 24 × 12 cells under DAG-Cog (uniformly), so the cross-outcome ranking is biased by the over-adjustment for outcomes that should drop AHPVT (SES, possibly cardiometabolic). The "strongest" outcomes per the screen may shuffle once we use per-outcome DAGs.

**Operational test.** For each of the 12 outcomes, refit IDGX2 → outcome under the per-outcome DAG (cardiometabolic / SES / mental / functional). Z-score the β within outcome's natural SD. Rank.

**Method.** Per-outcome WLS spec. Need each per-outcome DAG locked first (TODO §A4).

**Status.** Effectively the union of cardiometabolic-handoff + ses-handoff + a future mental-health-handoff + functional-handoff. Could fold all four handoff folders + extensions into a single "primary handoff comparison" report.

#### B.ii Which mental-health outcomes does adolescent SOC predict, controlling for adolescent CES-D?

**Question.** Mental-health outcomes (`H5MN1`, `H5MN2`) are the ones where school-belonging shows D4 instability — suggesting AHPVT or CES-D mediates the relationship. But what's the SOC effect *net of* W1 mental health?

**Why it's interesting.** "Lonely teens become depressed adults" is intuitive; a more interesting question is whether the network-position dimension of social integration adds explanatory power *beyond* the affective dimension already captured in CES-D.

**Operational test.** For H5MN1, H5MN2, fit IDGX2 + ODGX2 + SCHOOL_BELONG + (subset of CES-D items, NOT the full sum), adjusting for L0 + AHPVT. Are the network-position coefficients still significant?

**Method.** WLS. Caveat: subsetting CES-D items risks information loss; alternative is using the residual of CES-D after regressing on the social variables, but that's circular. Maybe better is to use only the "non-loneliness" CES-D items (drop `H1FS13`, `H1FS14`).

#### B.iii Cognitive trajectory under fluid-vs-crystallized decomposition

**Question.** AHPVT is crystallized vocabulary; W4 cognition is fluid memory + working memory. Does W1 social integration predict the *fluid* component (W4 cog residualised against AHPVT) more or less than the residual?

**Why it's interesting.** This is essentially the trajectory framing made explicit. If SOC predicts the fluid residual but not crystallized, the trajectory story holds; if SOC predicts both equally, the trajectory framing is conservative.

**Operational test.** Fit two nested regressions: (i) W4_COG_COMP ~ SOC + L0+L1; (ii) W4_COG_COMP ~ SOC + L0+L1 + AHPVT (the trajectory spec). Report the (β_naive − β_trajectory) decomposition explicitly per exposure.

**Status.** This is basically what cognitive-frontdoor does, but presented as a regression-decomposition rather than a Pearl front-door. Worth running both presentations.

### Theme C: Demographic moderation (your RQ #3)

#### C.i Sex × popularity

**Question.** Does popularity predict adult outcomes differently for boys and girls?

**Why it's interesting.** Adolescent gendered status hierarchies are documented; girls' popularity correlates more with relational aggression, boys' with athletic prowess. Different mechanisms → different downstream pathways. For outcomes like adult depression, the sign or magnitude of the SOC effect could plausibly differ by sex.

**Operational test.** For each handoff outcome, fit an `IDGX2 × SEX` interaction (centred IDGX2 × indicator for female). Test whether interaction is significant; if yes, report sex-stratified β with bootstrap CIs.

**Method.** WLS with interaction. Power: at N ~ 3,200 with sex roughly balanced, interaction power for a moderate effect (Δβ ≈ 0.3 SD) is decent.

**Caveat.** With handoff E-values, you'd need to compute the E-value for the *stratum-specific* β, not the marginal — different threshold for "robustly causal in girls" vs "in boys."

#### C.ii Race / ethnicity × popularity

**Question.** Same as above but for race.

**Why it's interesting.** Plus a cross-race-friendship dimension: do adolescents with mostly cross-race friends (high `PRXPREST` for own-school or other diversity measures) have different adult outcomes from same-race-friends adolescents, conditional on their popularity level?

**Operational test.** Two stages. Stage 1: fit interaction `IDGX2 × RACE` (4-level). Stage 2: among IDGX2 quintile, partition by friend-roster racial homogeneity; compare adult outcomes.

**Caveat.** Subgroup N's get small fast, especially for NH-Black and Native American strata. Wild-cluster bootstrap CIs essential.

#### C.iii Parent-ed × popularity

**Question.** Does popularity matter more or less for adolescents from low-PED households? A "compensating mechanism" hypothesis predicts SOC matters *more* for low-PED kids (they have fewer family-based resources to fall back on); a "complement" hypothesis predicts the opposite (popularity amplifies pre-existing SES advantages).

**Operational test.** `IDGX2 × PARENT_ED` interaction, stratified per outcome.

**Why it's interesting.** This is Bourdieu vs Coleman in one regression. If the interaction is sign-discordant across outcome families (compensating for cardiometabolic, complement for SES), that itself is a publication-worthy finding.

### Theme D: Negative effects (your RQ #4)

#### D.i Does popularity *increase* anxiety / status anxiety?

**Question.** The audit-and-handoff framing assumes higher IDGX2 is protective. But popularity carries social-comparison and maintenance costs. Does IDGX2 predict adult anxiety / depression in the *opposite* direction at high quintiles?

**Operational test.** For mental-health outcomes (`H5MN1` distressed, `H5MN2` depression), fit a quintile-dummy spec instead of linear. Is the Q5 (highest IDGX2) coefficient significantly *positive* (higher distress) relative to Q1?

**Method.** WLS with quintile dummies. The screen already runs this (D6 dose-response). Look at the actual quintile βs, not just Spearman ρ.

**Why it's interesting.** A non-monotonic relationship — middle-popular kids do best, very-popular and isolated kids do worst — would be theoretically rich and would explain why the linear screen finds null effects (the linear model averages over a U-shape).

#### D.ii Does popularity predict riskier health behaviours (smoking, drinking) in adulthood?

**Question.** W4 has self-reported smoking and drinking. Does adolescent popularity predict W4 substance use, controlling for L0+L1+AHPVT?

**Operational test.** Run `IDGX2 → smoking_W4`, `IDGX2 → drinking_W4` regressions. Adjust for the standard confounder set. Report β + E-value.

**Why it's interesting.** Mediator question for cardiometabolic outcomes — if popularity protects against adiposity but predicts higher smoking, the adiposity benefit may be partly cancelled by other-domain harms.

**Caveat.** Depending on which W4 substance-use items are public-use; verify before scoping.

### Theme E: New angles beyond your RQ list

#### E.i Density vs sparseness (bonding vs bridging)

**Question.** Ego-network density (`ESDEN`, `ERDEN`, `ESRDEN`, `RCHDEN`) measures how interconnected a respondent's friends are. Dense networks = social closure → behavioural conformity; sparse networks = brokerage → access to non-redundant information.

**Hypothesis.** Dense networks predict mental health (social support, identity confirmation); sparse networks predict SES (access to opportunity, weak-tie information).

**Operational test.** Multi-outcome screen with density measures alongside IDGX2/ODGX2. Already in the EXPOSURES registry; just rerun and compare β-pattern by outcome family.

**Why it's interesting.** Granovetter's "strength of weak ties" applied to adolescent networks. Different kinds of network capital → different downstream outcomes.

#### E.ii Out-of-school friendships

**Question.** `PRXPREST` = proportion of friend nominations that are in the respondent's school. Low `PRXPREST` means the respondent has many out-of-school friends — could indicate residential mobility, family-network ties, or non-academic affiliations (church, sports, work).

**Hypothesis.** Low-PRXPREST adolescents may have wider opportunity structures (broader information networks) → better adult SES outcomes. Or alternatively, low-PRXPREST may signal isolation from school context → worse academic outcomes.

**Operational test.** Run `PRXPREST → H5EC1`, `PRXPREST → educational attainment`. Compare to in-school network metrics.

#### E.iii Mediation through educational attainment

**Question.** How much of the SOC → adult-outcome effect is mediated through educational attainment vs direct?

**Why it's interesting.** Splitting the total effect into "popularity → schooling → adult outcome" vs "popularity → adult outcome (other mechanism)" tells you whether the policy lever is "promote schooling" or something else.

**Operational test.** Causal mediation analysis (Imai et al.): fit M = educational attainment on SOC + L0+L1, then Y on M + SOC + L0+L1 + AHPVT. Average natural direct vs natural indirect effect.

**Method.** Simulation-based mediation (`mediation` R package equivalent in Python; or hand-roll). Critical: requires the sequential-ignorability assumption, which is hard to defend.

**Caveat.** Methodologically heavy; may be more useful as an exploratory exercise than a primary deliverable.

#### E.iv Critical-period effects: Wave 1 vs Wave 2

**Question.** Add Health Wave II also has friendship data (1996, ~1 year after W1). Does W1-and-W2 stable popularity matter more than transient popularity?

**Operational test.** Construct `MEAN_IDGX2` and `Δ IDGX2` from W1 + W2. Fit handoff outcomes against both; partial out the persistent vs change components.

**Caveat.** W2 sample is much smaller (~4,800 vs 6,504 W1 in-home). Power tighter.

#### E.v Status incongruence

**Question.** Being academically successful but socially marginal (or vice versa). Does the *combination* predict different outcomes than either alone?

**Operational test.** Tag respondents with their (W1 academic-grade quintile × W1 IDGX2 quintile) combination. Compare adult outcomes for the four corner cells: high-grades-high-IDGX2, high-grades-low-IDGX2, low-grades-high-IDGX2, low-grades-low-IDGX2.

**Why it's interesting.** Sociologically classic (Merton's status-strain theory). The "popular but failing" cell (high-IDGX2-low-grades) is hypothesised to have particularly bad mental-health outcomes — internal status conflict.

#### E.vi Threshold effects: any-friend vs many-friends

**Question.** Is the dose-response continuous, or is there a "having any nominator" threshold beyond which more friends doesn't add much?

**Operational test.** Run dummies: `IDG_ZERO` (isolates), `IDG_LEQ1` (one or fewer nominators), `IDGX2 ≥ 2` reference. Compare β-pattern.

**Why it's interesting.** Health-policy implication: if the "any friend" threshold is what matters, intervention design is different from "more friends is always better."

#### E.vii Network change between W1 and W4: does friendship persistence matter?

**Question.** W4 has self-reported number of close friends in adulthood. Does the *change* (W1 IDGX2 - W4 close-friends-count) predict outcomes beyond W1 IDGX2 alone?

**Operational test.** Already-popular-and-stayed-popular vs already-popular-but-declined vs always-isolated, etc. Four-cell stability classification.

#### E.viii Family structure × peer integration interaction

**Question.** Does popularity protect adolescents from single-parent households more than two-parent households (compensating mechanism), or less (complementary)?

**Operational test.** `IDGX2 × FAMILY_STRUCTURE` interaction across handoff outcomes.

**Caveat.** Add Health W1 family-structure variable needs verification (`H1HR1*`/`H1WP*` series).

### Themes worth at least one paragraph each (low priority but worth listing)

- **Romantic-network ties** — W1 has romantic-partner data (Section 26); does adolescent romantic involvement predict adult outcomes?
- **Long-term loneliness** — W1 lonely (`H1FS13`/`H1FS14`) vs W4 lonely. Persistent loneliness vs adolescent-only.
- **Genetic moderation (G×E)** — Add Health twin sample lets you test gene × environment interactions for cognition. Mostly restricted-use.
- **Cross-race friendship and bridge-building social capital** — beyond the demographic-moderation question, does *who* you're friends with predict different outcomes than *how many*?
- **Deviant peer association** — friends who skip school, fight, smoke. Content of ties matters as much as count of ties.

---

## How to use this document

1. **For the planned handoff experiments**, the per-experiment plan in Part I is the working brief. Each section can be lifted into the corresponding `experiments/<name>/README.md` once the DAG is locked.
2. **For the brainstorm in Part II**, treat each entry as a candidate seed. Which ones survive contact with the data, and which are interesting enough to formalise into new experiment folders, is a separate prioritisation conversation.
3. Keep additions in this doc unless / until they justify their own folder.

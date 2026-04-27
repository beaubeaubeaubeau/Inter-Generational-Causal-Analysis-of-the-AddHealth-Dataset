# Glossary

Plain-language definitions of the causal-inference and survey-statistics vocabulary used throughout the reference set. Each entry points to the section in this document where the concept first appears and explains *why* it matters for the project. Alphabetical.

### ATE (Average Treatment Effect)
E[Y(1) − Y(0)] across a defined target population — the average causal effect of exposure on outcome if everyone were treated vs. everyone untreated.
**Why it matters here:** the project's target estimand is an ATE *within saturated schools* for network exposures and an ATE within the analytic cell for non-network exposures (see [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand)).

### Back-door path
<a id="glossary-back-door-path"></a>
An indirect route from the exposure X to the outcome Y through a common ancestor C (C → X and C → Y), rather than through the intended causal channel X → Y. Back-door paths create *spurious* associations that look like causation. **Why it matters**: every unblocked back-door path biases the causal estimate. The job of the adjustment set ([methods.md §1](methods.md#1-identification-assumptions-and-target-estimand)) is to "close" all back-door paths by conditioning on at least one variable on each path. First used in [dataset_manual.md §7 pitfall #1 context](dataset_manual.md#7-data-quality-gotchas); formalised in [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand).

### CASI (Computer-Assisted Self-Interview)
Sensitive items (drug use, sexual behaviour, mental-health items under `H5MN*`) are delivered via respondent-controlled screen so an interviewer is not in the loop. Higher truth-telling but more item non-response. First used in [dataset_manual.md §5.4](dataset_manual.md#54-wave-v-adult-contemporaneous-covariates).

### Cluster-robust standard error
A standard error that accounts for within-PSU correlation by treating each cluster (school pair = `CLUSTER2`) as a unit for variance computation. **Why it matters**: nominal OLS SEs assume independent observations. Add Health is school-clustered, so nominal SEs are too small; cluster-robust SEs are wider and more honest. First used in [dataset_manual.md §2.1](dataset_manual.md#21-design).

### Collider
A variable jointly *caused* by two others (X → C ← Z). **Why it matters**: conditioning on a collider *opens* a spurious association between its causes, the opposite of what you want. Example: if peer centrality and depression both cause school belonging, adjusting for school belonging creates a spurious centrality–depression correlation. D9 in the diagnostic battery ([methods.md §2](methods.md#2-causal-screening-diagnostic-battery-d1d9)) flags known-collider exposure choices.

### Confounder
A common cause of both exposure and outcome — adjusting for it is *required* to identify the causal effect. **Why it matters**: contrast with mediator — the two look the same empirically (both shift β when added to the model) but call for opposite treatment. The [AHPVT callout](methods.md#1-identification-assumptions-and-target-estimand) is the project's load-bearing confounder-vs-mediator ambiguity. First used in [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand).

### DAG (Directed Acyclic Graph)
A flowchart where nodes are variables and arrows run from causes to effects, with no cycles. **Why it matters**: drawing a DAG forces you to make causal assumptions explicit, and once it's drawn, graph-theoretic rules tell you which covariates to adjust for. This project does not render a full DAG but describes one textually in [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand).

### Design effect (DEFF)
Ratio of the true variance under the complex design to the variance under simple random sampling of the same N. **Why it matters**: DEFF > 1 means your 3,500-observation sample behaves like a smaller SRS sample for inference purposes. Audited in `experiments/cognitive-screening/tables/verification/13_deff.csv`.

### Dose-response monotonicity
The expectation that as exposure increases, the outcome changes in a consistent direction — no plateaus, inversions, or threshold effects. **Why it matters**: D6 in the diagnostic battery. A non-monotonic dose-response can signal non-linearity, effect heterogeneity, or misspecification of the linear-in-X model.

### Effective N (eff N)
Sample size adjusted for design effect and, where relevant, weight dispersion: `eff_N = N / DEFF` or more generally `eff_N = (Σw)² / Σw²`. **Why it matters**: D7 positivity check requires eff_N ≥ 500 post-trimming, not raw N. See [methods.md §2](methods.md#2-causal-screening-diagnostic-battery-d1d9).

### E-value
VanderWeele's metric for the minimum strength of unmeasured-confounder association (with both exposure and outcome) needed to fully explain away an observed effect. Used in our handoff experiments to characterize causal-claim robustness. A small E-value means a weak unmeasured confounder could explain the result; a large E-value means the result would survive even very strong unmeasured confounding. Reference: VanderWeele & Ding (2017), "Sensitivity Analysis in Observational Research: Introducing the E-Value," *Annals of Internal Medicine*.

### Front-door criterion
A causal identification strategy that bounds the X → Y effect through a mediator M when back-door adjustment fails (because unmeasured confounders exist). Requires X → M → Y with no direct X → Y, M fully mediating, and no unmeasured M–Y confounders. **Why it matters**: Task 16's plan for distinguishing whether AHPVT is a confounder or mediator of the social-integration → cognition path.

### HTE (Heterogeneous Treatment Effects)
The proposition that the causal effect of X on Y differs across subgroups defined by covariates V — i.e. the treatment effect is a *function* of V, not a single number. ATE collapses across V; HTE preserves it. **Why it matters**: HTE is what the project's effect-modification experiments (`em-compensatory-by-ses`, `em-sex-differential`, `em-depression-buffering`) test. "Effect modification" in epi, "moderation" in psych, "HTE" in econometrics — same construct, different vocabularies.

### Handoff (in this project)
The transition from the **screening phase** (24 exposures × 12 outcomes, fast WLS sweep, ranking-purpose only — biased point estimates but consistent ranking) to **formal estimation** (per-outcome DAG, IPAW where attrition demands it, ordered logit / interval regression for ordinal outcomes, E-value sensitivity bounds). A "handoff pair" is an (exposure, outcome) cell the screen flagged as worth formal estimation. The four current handoff pairs (IDGX2→H4WAIST, IDGX2→H4BMI, IDGX2→H4BMICLS, ODGX2→H5EC1) each have a planned experiment folder (`cardiometabolic-handoff/`, `ses-handoff/`).

### Identification (identifying assumption, identification strategy)
The set of causal assumptions under which a statistical estimand (e.g. a regression coefficient) equals the causal estimand of interest (e.g. E[Y|do(X)]). **Why it matters**: β̂ is always estimable; whether it equals the causal effect depends on whether the identifying assumptions hold. [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand) lists this project's assumptions.

### Interval regression
Regression for outcomes observed only as bracketed intervals (e.g., bracketed income reported as "$15,000–24,999"). Treats the latent value as continuous within each bracket, modelling it as if observed at the bracket midpoint with adjusted likelihood. In this project: H5EC1 (bracketed adult earnings) will use interval regression in ses-handoff.

### IPAW (Inverse-Probability-of-Attrition Weighting)
A reweighting scheme that inflates the weight on respondents who *remained* in the study to compensate for attrition of similar respondents. Computed as `w_IPAW = 1 / Prob(remain | covariates)`. **Why it matters**: W4 → W5 attrition is sex-patterned; cross-sectional W5 weights `GSW5` only partially correct for it. Formal W5 estimation should apply IPAW on top of `GSW5`. See [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand) and outstanding uncertainty #3 in [research_journal.md](research_journal.md).

### IPAW vs IPTW
IPAW is inverse-probability-of-attrition weighting (corrects for selective dropout between waves; reweights respondents to represent their attritted counterparts). IPTW is inverse-probability-of-treatment weighting (corrects for confounding via propensity scores; reweights to balance treated vs. control on covariates). Both reweight a sample to a target population, but they address different missingness mechanisms — IPAW for missing outcomes, IPTW for unbalanced exposure assignment. In this project: IPAW is planned for W5 outcomes (W4→W5 attrition); IPTW is not currently planned.

### IV (Instrumental Variable)
A variable Z that affects the exposure X but not the outcome Y except through X, and shares no common cause with Y. Used to identify X → Y even under unmeasured confounding. **Why it matters**: a fallback identification strategy for Task 16 if front-door is not credible.

### Mediator
A variable on the causal path X → M → Y. **Why it matters**: adjusting for M blocks part of the total effect, *shrinking β toward zero*. This is the opposite of what adjusting for a confounder does (which should reveal the true β by removing bias). The two operations look identical in a regression table — only a DAG (or a front-door / IV decomposition) can tell them apart. See [AHPVT callout, methods.md §1](methods.md#1-identification-assumptions-and-target-estimand).

### Mediator leakage
A regression bug: you accidentally include a variable that lies on the causal pathway X → M → Y in your adjustment set. Conditioning on M *blocks* part of the true X → Y effect, shrinking β toward zero. Diagnostically the symptom is the same as confounding-detection (β moves when you add the covariate), but the *interpretation* is opposite. **Why it matters**: D9 in the diagnostic battery flags known cases (e.g. using `H1FS13` as exposure while adjusting for `CESD_SUM` which contains `H1FS13`). `SCHOOL_BELONG` failing D4 on mental-health outcomes is suspected mediator leakage — popularity → belonging → mental health, with belonging mistakenly conditioned on. See [methods.md §2 D9 row](methods.md#2-causal-screening-diagnostic-battery-d1d9).

### Mode (W5 survey mode)
The channel through which the W5 interview was administered: W = Web, I = In-person, M = Mail, T = Telephone, S = Spanish CAPI. **Why it matters**: cognitive items were administered only in I + T, restricting the W5 cognitive analytic cell to ~620 of 4,196. See [dataset_manual.md §4.5](dataset_manual.md#wave-v-cognitive-battery).

### Negative-control outcome (NC)
An outcome Y* that, under the assumed causal model, should **not** be affected by X. If X still predicts Y*, unmeasured confounding is implicated. **Why it matters**: D2 in the diagnostic battery uses `HEIGHT_IN`. The NC is contaminated (adolescent height correlates with peer popularity), so failures on network exposures are ambiguous. See [dataset_manual.md §9](dataset_manual.md#9-outcome-battery-primary--multi-outcome-extension).

### Ordered logit
Regression for ordinal outcomes (categories with meaningful order but no metric distance, e.g., a 5-level "low / med-low / med / med-high / high" scale). Estimates a single coefficient under a proportional-odds assumption (the effect of a one-unit exposure shift is the same across category boundaries). In this project: H4BMICLS uses ordered logit; H5LM5 may.

### Positivity (overlap)
The assumption that every level of the exposure has non-zero probability of occurring at every level of the covariates. Formally: P(X = x | C = c) > 0 for all (x, c). **Why it matters**: without positivity, causal estimates in the violated region are extrapolations beyond the data, not causal effects. D7 in the diagnostic battery tests positivity empirically. Structural positivity violations (saturated-school gating, W5 mode restriction) are documented in [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand).

### Polysocial score
By analogy with polygenic scores in genetics: a single composite index built from many social-integration variables (24 in this project) by either an unsupervised PCA (PC1 of the standardized exposure matrix), a theory-driven weighted sum (e.g. equal weights on popularity-coded vs sociability-coded variables), or a supervised LASSO with cross-fit weights. **Why it matters**: collapsing redundant exposures into one index reduces multiple-testing burden and asks whether the per-variable signal is driven by one underlying social-integration latent factor. In this project, the polysocial-PCA-PC1 sensitivity column appears in every Phase 6 mechanism experiment.

### Post-stratification weight
A weight that re-scales the sample so that known marginal distributions (e.g. age × sex × race) match the population. **Why it matters**: `GSWGT4_2` is a post-stratified weight. Post-stratification corrects for differential sampling and non-response, not for unmeasured confounding.

### PSU (Primary Sampling Unit)
The first-stage unit in a multistage sample; for Add Health this is the high-school / feeder-middle-school pair (`CLUSTER2`, 132 PSUs). **Why it matters**: cluster-robust SEs, design effects, and `svyset` all reference the PSU. First used in [dataset_manual.md §2.2](dataset_manual.md#22-design-variables-in-public-use).

### Reserve code
Non-substantive codes on a variable indicating refusal, don't know, skip, or not-administered (W1–W4: 6/96/996 etc.; W5 adds 95/995/9995 for "not asked"). **Why it matters**: treating reserve codes as substantive values (e.g., summing them into a scale) silently corrupts every downstream statistic. `analysis.cleaning.clean_var` + `VALID_RANGES` strip them. See [dataset_manual.md §7 pitfall #5](dataset_manual.md#7-data-quality-gotchas).

### Saturated school
A school where ≥ 75 % of the student roster participated in the W1 In-School Questionnaire. **Why it matters**: network centralities (in-degree, etc.) require knowing who nominated the respondent, so they are only defined in saturated schools. ~32 % of W1 respondents are in non-saturated schools; their network variables are structurally missing. First used in [dataset_manual.md §3.1](dataset_manual.md#31-wave-i-public-use-network-file--pre-computed-sociometric-measures); positivity consequences in [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand).

### Sibling dissociation (D3)
A specificity check: the *target* exposure should have a larger effect than a *sibling* exposure (a related variable expected to carry less of the causal signal), and both should move in the same direction. **Why it matters**: a target with a smaller or opposite-signed effect than its sibling is probably not capturing exposure-specific signal. Formalised in [methods.md §2](methods.md#2-causal-screening-diagnostic-battery-d1d9).

### Stratum
The second design dimension (after clustering) in a complex survey. **Why it matters**: stratum information is *not* in the public-use Add Health distribution. Per the Add Health user guide, omitting stratum "only minimally affects the standard errors," so this project sets stratum to empty in `svyset`. First used in [dataset_manual.md §2.2](dataset_manual.md#22-design-variables-in-public-use).

### TFN (Total Friendship Nominations)
The W1 In-School Questionnaire asked each student to nominate up to 5 male + 5 female friends from the school roster. Centralities tagged with "TFN" (e.g. `IDGX2` "In-Degree: TFN") are computed on this 10-nomination-cap network. See [dataset_manual.md §3.1](dataset_manual.md#31-wave-i-public-use-network-file--pre-computed-sociometric-measures).

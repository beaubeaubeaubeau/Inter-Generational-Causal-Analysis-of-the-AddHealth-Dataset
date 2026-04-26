# Add Health Public-Use Reference — Adolescent Friendship/Network → Mid-Life Cognition

*Merged synthesis of the prior feasibility report (v2), documentation report, and empirical feasibility summary. Ground-truth variable labels are quoted verbatim from the shipped SAS/XPT files (ICPSR 21600 v26, 2026-03-03). Where a label in this document is in quotes, it is the exact string attached to the variable in the data file.*

---

## 1. Scope and access

**Research question.** Which adolescent friendship / social-connection factors are causally relevant to maintaining cognitive performance through middle age?

**Access.** Public-use Add Health only (ICPSR 21600 v26). Restricted-use data requires a CPC data-use contract and is out of scope. This has three hard consequences:

- No friend / sibling / partner IDs → no custom network construction, no peer-characteristic linkage.
- No contextual / neighborhood data, no genetics, no Wave V cytokine panel or neurodegeneration biomarkers.
- **The entire Wave VI Add CAPS cognitive battery (TestMyBrain, NIH Toolbox, Animal Naming, Word Recall, Backward Digit Span, Physical Function, Sensory Function) is restricted-use only.** Public-use Wave VI has only *self-reported* memory items.

**Sample sizes across waves** (public-use, empirically confirmed from the shipped weight files unless noted):

| Wave | Years | Age | Public-use N | Mode |
|------|-------|-----|--------------|------|
| I | 1994–95 | 12–19 | **6,504** | In-home CAPI/CASI + parent questionnaire + AHPVT |
| II | 1996 | 13–20 | **4,834** | In-home CAPI/CASI |
| III | 2001–02 | 18–26 | **4,882** | In-home CAPI/CASI; AHPVT repeat |
| IV | 2008–09 | 24–32 | **5,114** | In-home CAPI/CASI; dried-blood biomarkers; cognitive battery |
| V | 2016–18 | 33–43 | **4,196** | Mixed-mode (W/I/T/M/S); cognitive battery **only in I + T** |
| VI | 2022–25 | 39–51 | **3,937** | Mixed-mode; Add CAPS cognitive battery restricted-only |

Public-use is **nested**: every later-wave AID is a subset of Wave I AIDs. The "independent redraw per wave" warning in older Add Health documentation does not apply to the public-use distribution.

---

## 2. Sampling design and survey-aware estimation

### 2.1 Design

School-based, stratified, clustered, with unequal probability of selection. 80 high schools selected with probability proportional to size from the QED frame, stratified by region / urbanicity / school type / ethnic mix / size; one feeder middle school per high school (132 schools total). ~17 students per grade-sex stratum per school pair. Observations are **not i.i.d.** — ignoring the design biases both point estimates and SEs.

### 2.2 Design variables in **public-use**

| Element | Variable | Label (verbatim) | Notes |
|---|---|---|---|
| Cluster / PSU | `CLUSTER2` | "SAMPLE CLUSTER" | Ships in every weight file (W1–W6). Public-use PSU. |
| Stratum | — | — | Not available in public-use. Per Add Health's own guidelines, omitting stratum "only minimally affects the standard errors." |

Always set design type **with replacement**. Finite population correction is not available.

### 2.3 Weight variables (public-use, empirically verified)

| Wave | File | Variable | Label (verbatim) | N |
|---|---|---|---|---:|
| I | `w1weight.sas7bdat` | `GSWGT1` | "GRAND SAMPLE WEIGHT-W1" | 6,504 |
| II | `w2weight.sas7bdat` | `GSWGT2` | "GRAND SAMPLE WEIGHT-W2" | 4,834 |
| III (main) | `w3weight.sas7bdat` | `GSWGT3_2` | "POSTSTRAT GS CROSS-SECTIONAL WGT-W3" | 4,882 |
| III (main) | `w3weight.sas7bdat` | `GSWGT3` | "POSTSTRAT GS LONGITUDINAL WGT-W3" | 3,844 |
| III (edu) | `w3eduwgt.sas7bdat` | `PTWGT3_2` | "TRANSCRIPT CROSS-SECTIONAL WEIGHT-PUBLIC" | 3,964 |
| III (edu) | `w3eduwgt.sas7bdat` | `PTWGT3` | "TRANSCRIPT LONGITUDINAL WEIGHT-PUBLIC" | 3,129 |
| IV | `w4weight.sas7bdat` | `GSWGT4_2` | "POSTSTRAT GS CROSS_SECT WGT-PUBLIC-W4" | 5,114 |
| IV | `w4weight.sas7bdat` | `GSWGT4` | "POSTSTRAT GS LONGIT WGT-PUBLIC-W4" | 3,342 |
| IV | `w4weight.sas7bdat` | `GSWGT134` | "POSTSTRAT GS UNTRIMMED LONGIT WGT-W134" | 4,208 |
| V | `p5weight.xpt` | `GSW5` | "CROSS-SECTION WGT WV ALL SP" | 4,196 |
| V | `p5weight.xpt` | `GSW145` | "LONGTDNL WGT WI-IV-V ALL SP" | 3,713 |
| V | `p5weight.xpt` | `GSW1345` | "LONGTDNL WGT WI-III-IV-V ALL SP" | 3,147 |
| V | `p5weight.xpt` | `GSW12345` | "LONGTDNL WGT WI-II-III-IV-V ALL SP" | 2,499 |
| VI | `p6weight.sas7bdat` | `GSW6` | "WAVE 6 PUF CROSSSECTIONAL OPTIMIZED WEIGHT" | 3,937 |
| VI | `p6weight.sas7bdat` | `GSW1456` | "WAVE 6 PUF LONGITUDINAL OPTIMIZED WEIGHT (I-IV-V-VI)" | 2,996 |
| VI | `p6weight.sas7bdat` | `GSW13456` | "WAVE 6 PUF LONGITUDINAL OPTIMIZED WEIGHT (I-III-IV-V-VI)" | 2,571 |

**Names that do NOT exist in public-use** (older companion reports cite them in error): `CORE1`, `CORE2`, `HIEDBLK`, `PSUSCID`, `REGION`.

**Weight-selection rule of thumb.** If the outcome is measured at a single wave and you want Grades 7–12 as the target population, use that wave's cross-sectional weight. If the design is genuinely longitudinal, use the longitudinal weight matching the waves used. Longitudinal weights that trace through Wave II restrict the target population to Grades 7–11 (Wave I seniors were generally not re-interviewed at W2) — for a W1→W4 or W1→W5 analysis, use `GSW145`/`GSW1345` to retain Grades 7–12.

**Biomarker files ship with no weight** — use the corresponding survey-wave weight and flag the biomarker subsample as non-representative.

### 2.4 Sample setup

This project is Python-only. Survey-weighted WLS with cluster-robust SEs on `CLUSTER2` is implemented in [scripts/analysis/wls.py](../scripts/analysis/wls.py) (`weighted_ols` / `_fit`) using `statsmodels`' `WLS` + `.get_robustcov_results(cov_type="cluster", groups=cluster)`. Subpopulation analysis is done by **keeping the full design frame and passing a subpop mask**, not by pre-filtering rows (pre-filtering biases cluster-level variance estimation). The `samplics` library is a more complete survey-analysis option but is not a dependency of this project.

### 2.5 Merging

All files merge one-to-one on **`AID`** (label: "RESPONDENT IDENTIFIER"). Base = Wave I in-home; left-join Wave I network, Wave III PVT, Wave IV in-home, Wave V mixed-mode, Wave V/VI biomarker files as needed. After each merge, verify N against the source file.

> **Variable-code lookup.** Every code used in the screening pipeline (exposures, outcomes, covariates, weights, design) is catalogued in [reference/variable_dictionary.md](variable_dictionary.md) with verbatim codebook labels, valid-N counts, caveats, and cross-references back to this synthesis. Start there when reading a chart caption or script that names a code you don't recognise.

---

## 3. Primary exposure: adolescent friendship / social connection

Three data sources. Use in combination where possible.

### 3.1 Wave I Public-Use Network File — pre-computed sociometric measures

`data/W1/w1network.sas7bdat` — 6,504 rows × 439 variables, constructed from the Wave I In-School Questionnaire nomination roster (full-sample N≈90,118 students). No raw nominations, no friend IDs. No weight variable ships with this file — apply `GSWGT1` + `CLUSTER2` after merging to Wave I in-home.

**Structural 32.4% missingness.** All centrality measures are NA for non-saturated-schools respondents. Only **4,397 of the 6,504 public-use respondents** have any network measures. This is by design (centralities require saturated-school nominations) but halves effective N before any outcome is merged.

The network file ships nine pre-computed centrality measures (in-degree, out-degree, Bonacich, reach, reach-3, mean distance, proximity prestige, influence domain, density at max reach), a small set of local-structure / isolation flags (best-male / best-female friendship presence and reciprocity, ego-network send/receive density), and ~400 school-level aggregates and auxiliary variables. "TFN" in centrality labels = "Total Friendship Nominations" (up to 5 male + 5 female per respondent on the In-School roster). Reciprocity flags are 64–70% missing because they require the nominated friend to be in-sample, so they are not reliable standalone exposures. **No clustering coefficient variable exists by name** in the public-use file — the ego-network density variables are clustering-adjacent but not the canonical coefficient.

(Variable codes, verbatim labels, valid Ns, and ranges: see [variable_dictionary.md §2.3.1 Peer-network centrality](variable_dictionary.md#231-peer-network-centrality-8), [§2.3.2 Isolation](variable_dictionary.md#232-isolation-4), and [§2.3.3 Ego-network density](variable_dictionary.md#233-ego-network-density-4). Full 439-variable catalog including the 186 school-level aggregates and 216 auxiliaries is generated by [scripts/prep/03ab_wave1_friendship_and_network.py](../scripts/prep/03ab_wave1_friendship_and_network.py).)

### 3.2 Wave I In-Home Interview — Section 20 friendship roster (self-report)

`data/W1/w1inhome.sas7bdat`. Section 20 splits into two parallel 45-variable blocks: a male-friend block and a female-friend block, each 5 friends × 9 items per friend (school attended, grade, sample-school flag, sister-school flag, visited friend's house, met after school, time spent last weekend, talked about a problem, talked on phone). The female block uses the same structure with minor textual drift in the codebook (e.g. "DISCUSS A PROB" vs "TALK ABOUT A PROB").

**Absent-slot encoding warning.** Unnominated friend-2…friend-5 slots are populated with zeros, blanks, or reserve code 7 — *not* NA. Nomination must be inferred from non-missingness on the friend-1 block. There is no friend-1-specific question prefix; the first slot's variables are themselves the per-friend item names with the "A" suffix (the codebook starts the per-friend grid at item 2). The repo derives three friendship-grid scalars from this raw 90-variable block (nomination count, contact-frequency sum, disclosure-any flag) — full enumeration is generated by [scripts/prep/03ab_wave1_friendship_and_network.py](../scripts/prep/03ab_wave1_friendship_and_network.py).

(Derived friendship-grid variable codes and verbatim labels: see [variable_dictionary.md §2.3.4 Friendship grid derived](variable_dictionary.md#234-friendship-grid-derived-3). Raw `H1MF*` / `H1FF*` codes are not catalogued individually — they are inputs to the derivations, not project-level exposures.)

### 3.3 Wave I School Belonging scale (Section 5)

A 6-item 1–5 Likert scale from the in-home interview's education section: feeling close to people at school, feeling part of the school, perceived student prejudice (reverse-then-invert), happiness at school, perceived teacher fairness, and feeling safe at school. Sample-wide (~6,350 valid per item, no saturation gating). The repo derives a single composite scalar `SCHOOL_BELONG`; one item (perceived prejudice) is double-reverse-scored to align valence with the rest of the scale.

(Item-level variable codes, verbatim labels, valid Ns, and the composite derivation: see [variable_dictionary.md §2.3.5 Belonging](variable_dictionary.md#235-belonging-1) and [§2.8 Derived / composite cheat-sheet](variable_dictionary.md#28-derived--composite-cheat-sheet).)

### 3.4 Other Wave I adolescent-social variables

A handful of single-item social-connection signals scattered across other Wave I sections: a daily-activity "hang out with friends" frequency, two CES-D loneliness / unfriendly-treatment items that double as exposures (the loneliness item is also a CES-D component, which forces a collider check — see D9 in [methods.md §2](methods.md#2-causal-screening-diagnostic-battery-d1d9)), a protective-factors "friends care about you" item, and a design variable indicating how many friend nominations the respondent was actually asked for.

(Variable codes, verbatim labels, valid Ns, and intended role in the screen: see [variable_dictionary.md §2.3.6 Loneliness](variable_dictionary.md#236-loneliness-2) and [§2.3.7 Qualitative](variable_dictionary.md#237-qualitative-2).)

### 3.5 What is *not* available

- Friend-level characteristics (restricted: friend IDs)
- Custom network measures beyond the 439 pre-computed (restricted: raw nominations)
- Peer-network changes across waves (no network data after Wave I)
- School-level administrator context (restricted)

---

## 4. Primary outcome: cognitive performance

### 4.1 Battery across waves (public-use only)

| Test | Wave I | Wave III | Wave IV | Wave V | Wave VI |
|---|:-:|:-:|:-:|:-:|:-:|
| AHPVT (crystallized ability / receptive vocabulary) | ✅ | ✅ | — | — | — |
| Immediate Word Recall (90 s) | — | — | ✅ | ✅ mode-restricted | ❌ restricted |
| Delayed Word Recall (60 s) | — | — | ✅ | ✅ mode-restricted | ❌ restricted |
| Backward Digit Span | — | — | ✅ | ✅ derived, mode-restricted | ❌ restricted |
| TMB / NIH Toolbox / Animal Naming | — | — | — | — | ❌ restricted |

### 4.2 Wave I AHPVT (baseline crystallized ability)

The Add Health Picture Vocabulary Test ships in `data/W1/w1inhome.sas7bdat` in two forms: a standardized score (mean 100, SD 15 by design) and a raw score (number of items correct, max 87). The standardized form has ~15% combined missing (4% NA + 11% reserve codes); the raw form is cleaner (~4% NA). **Recommendation: re-standardize from the raw score if you need a z-score baseline.** AHPVT measures crystallized vocabulary, not the fluid memory / working memory constructs probed at W4–W6 — when used as an L0+L1+AHPVT baseline covariate it is a *proxy* for general cognitive ability, not an identical-construct pre-test (see the construct-mismatch caveat in [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand)).

(Variable codes, verbatim labels, and valid Ns: see [variable_dictionary.md §2.6.3 L0+L1+AHPVT — baseline cognition](variable_dictionary.md#263-l0l1ahpvt--baseline-cognition).)

### 4.3 Wave III AHPVT repeat

`data/W3/w3pvt.sas7bdat` carries a W3 re-administration of the AHPVT plus a re-standardized W1 score for direct W1-vs-W3 comparison. It includes the W3 raw score (re-using the same variable name as W1 but in a different file), W3 cross-sectional and longitudinal standardized scores (~mean 100, SD 15 after reserve-code strip), W3 percentile ranks, and W1 re-standardized scores and percentiles. The W3 file is the only place a W1-comparable W3 standardized score lives.

(Variable codes and verbatim labels: see [variable_dictionary.md §2.6.3](variable_dictionary.md#263-l0l1ahpvt--baseline-cognition).)

### 4.4 Wave IV cognitive battery (`data/W4/w4inhome.sas7bdat`)

All scored cognitive outcomes are under the `C4` (constructed score) prefix — **not** `H4MH` (the `H4MH*` variables are interviewer-interruption flags). Three performance tests: 90-second immediate word recall, 60-second delayed word recall, and a backward digit span score. Each is near-complete (~5,100 valid out of 5,114 W4 respondents); ranges are 0–15 for the recall tests and 0–7 for digit span.

**Protocol** (identical across Waves IV, V, VI per the Wave VI user guide Aiello et al. 2025):
- **Word Recall.** Interviewer reads 15 unrelated nouns at ~1 word/sec. Respondent has 90 s for immediate recall, then after a ~1–2 min distractor has 60 s for delayed recall. Score = # correct (0–15).
- **Backward Digit Span.** Interviewer reads digit sequences of increasing length (2 → 8); respondent repeats in reverse. Two trials per length; ends after two wrong at same length. Score = longest length correctly reversed on either trial (0–7).

Diagnostic variants ("# WORDS NOT ON LIST NAMED" / "# WORDS REPEATED") are available in the same file for error analyses. The same 15-word list is used at W4/W5/W6 — allows longitudinal comparison but introduces potential learning effects.

(Variable codes and verbatim labels for the three performance tests and the project's `W4_COG_COMP` z-composite: see [variable_dictionary.md §2.4 Primary outcome — W4 cognition](variable_dictionary.md#24-primary-outcome--w4-cognition).)

<a id="wave-v-cognitive-battery"></a>
### 4.5 Wave V cognitive battery (`data/W5/pwave5.xpt`)

**Section 19 of the Wave V instrument.** Two pre-computed word-recall scores (immediate 90-second, delayed 60-second) plus 14 per-trial backward-digit-span pass/fail items spanning lengths L ∈ {2,…,8} with two trials per length.

**No pre-computed backward-digit-span score exists at Wave V.** Must be derived: for each length L the trial pair is the L-A and L-B items; the respondent passes length L if either trial scored 1. Digit-span score = max L passed, else 0. The repo's `derive_w5_bds` lives in [scripts/analysis/derivation.py](../scripts/analysis/derivation.py).

(Variable codes and verbatim labels for the W5 word-recall scores, the 14 per-trial digit-span items, and the derived `W5_COG_COMP`: see [variable_dictionary.md §2.4 Primary outcome — W4 cognition](variable_dictionary.md#24-primary-outcome--w4-cognition) and [§2.8 Derived / composite cheat-sheet](variable_dictionary.md#28-derived--composite-cheat-sheet).)

#### Mode restriction — the dominant constraint

The W5 survey mode variable takes values W = Web (self-administered online), I = In-person (CAPI), M = Mail (paper self-administered), T = Telephone (CATI), S = Spanish CAPI / other. Frequencies: W 76.8%, I 17.2%, M 3.5%, T 2.4%, S 0.1% (total 4,196).

**Empirically confirmed: cognitive items were administered only in In-person + Telephone modes.** Web/Mail/Spanish respondents receive reserve code 95/995/9995 ("question not asked") on every Section-19 item. Administered public-use Ns are ~620–625 per test (in-person ~520, telephone ~100).

This 95/995/9995 family means "not asked" — distinct from true NA and from legacy reserve codes 96/996/9996 (refused) etc. Missing-data operations must separate them before computing statistics.

(The mode variable is catalogued in [variable_dictionary.md](variable_dictionary.md) under design variables; the W5 cognitive variable codes are in §2.4 / §2.8.)

### 4.6 Wave VI — public-use has no cognitive performance tests

The Add CAPS battery is restricted-only. Public-use Wave VI (`pwave6.sas7bdat`, 3,937 × 1,002) does contain *self-reported* memory items per the codebook (H6DA18B–H6DA18F per the Wave VI cognitive user guide). These are subjective memory complaints, not performance measures.

---

## 5. Confounders and covariates (public-use)

### 5.1 Wave I demographics

The L0 demographic tier covers biological sex, date of birth (month and year only — day 15 is imputed because day was not collected), Hispanic-origin flag, and five separate race indicators (white, African American, American Indian, Asian, other). Add Health's default constructed `RACE` variable uses a hierarchical rule (Hispanic → Black → Asian → Native → Other → White) that collapses multi-racial respondents. For flexible coding, the project builds from the raw race-component flags rather than the collapsed default; the derived race / ethnicity variable lives in `scripts/analysis/derivation.py`.

(Variable codes, verbatim labels, and valid Ns: see [variable_dictionary.md §2.6.1 L0 — demographics](variable_dictionary.md#261-l0--demographics).)

### 5.2 Wave I socioeconomic status (parent questionnaire + self-report)

The W1 SES tier draws from two sources: (a) the parent questionnaire (PQ) for total household income, parent-respondent's education, and partner/spouse's education; and (b) the teen self-report for resident-mom and resident-dad education. The PQ income variable is the only direct income measure; education is collected redundantly across PQ + teen-report so the project derives a maximum-of-available `PARENT_ED` scalar to handle missing-PQ cases. Two non-resident-parent education items also exist but are 65–89% skip (no contact / no biological parent in scope) and are not used as primary SES proxies.

A common error in the older companion reports cited `PA12A` (does not exist) and `PC13` (which is actually "INFLUENCE OF BEST FRIEND-PQ", not parental education). The project's L0+L1 spec uses the documented PQ + teen-report set only.

(Variable codes, verbatim labels, valid Ns, reserve-code rates, and the `PARENT_ED` derivation: see [variable_dictionary.md §2.6.1 L0 — demographics](variable_dictionary.md#261-l0--demographics) and [§2.8 Derived / composite cheat-sheet](variable_dictionary.md#28-derived--composite-cheat-sheet).)

### 5.3 Wave I CES-D depression scale (19 items)

Section 10 of the in-home interview carries the 19-item Center for Epidemiologic Studies — Depression scale (CES-D). All items are 0–3 Likert. **Standard scoring:** reverse items 4, 8, 11, 15 (`3 - x`); sum all 19. Expected range 0–57. All items have separate reserve codes 6/7/8 — treat those as missing before summing. The project enforces a `min_count=19` rule when computing the sum (any item missing → `NaN`); the `derive_cesd_sum` function lives in `scripts/analysis/derivation.py`.

Two of the 19 items (loneliness, "people unfriendly to you") double as exposures in the friendship/network screen — adjusting for the full CES-D sum while exposing on these items would be a collider / double-counting bug. D9 in [methods.md §2](methods.md#2-causal-screening-diagnostic-battery-d1d9) catches that combination.

(Per-item variable codes and verbatim labels for all 19 CES-D items, plus the four reverse-scored item flags and the `CESD_SUM` derivation: see [variable_dictionary.md §2.6.2 L1 — W1 mental + health state](variable_dictionary.md#262-l1--w1-mental--health-state) and [§2.8 Derived / composite cheat-sheet](variable_dictionary.md#28-derived--composite-cheat-sheet).)

### 5.4 Wave V adult-contemporaneous covariates

Wave V (`data/W5/pwave5.xpt`) is organized by section-prefix: background/demographics, household roster, military and employment, income, health and healthcare, sexual experiences (CASI), tobacco/alcohol/substances (CASI), early-life retrospective, personality, social support, parents and siblings, religion and spirituality, mental-health feelings and experiences (CASI), criminal justice (CASI), relationships (CASI), pregnancy / children / parenting (CASI), and illness / physical limitations.

**Adult social support** is the adult-contemporary analog of the adolescent friendship exposure. Treat as (a) a mediator of the adolescent → adult pathway — adjusting for it blocks part of the target effect; (b) a contemporaneous confounder of W5 outcomes; or (c) an independent adulthood exposure for a separate hypothesis — depending on your identification strategy. The screen treats it as downstream of X and *deliberately does not adjust for it* (see [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand) on adjustment-set construction).

(Codes, verbatim labels, and screen-role for the W5 functional / mental-health / socioeconomic outcomes drawn from these sections: see [variable_dictionary.md §2.5.2 Functional + mental health](variable_dictionary.md#252-functional--mental-health-5) and [§2.5.3 Socioeconomic](variable_dictionary.md#253-socioeconomic-2).)

### 5.5 Wave III BEM Sex-Role Inventory (embedded in `w3inhome.sas7bdat`)

18 adjective items from the Wave III BEM Sex-Role Inventory are visible in public-use as raw item-level Likert scores (Section 20 of Wave III). Derived scale scores (the BEM masculinity / femininity composites) are **not** in public-use — projects that need the standard BEM scoring must construct it from the items. The repo currently does not use BEM in the primary screen; it is documented here for completeness.

(Variable codes for the 18 BEM items are not catalogued in `variable_dictionary.md` because they are not in the project's exposure / outcome / covariate set; refer to the W3 codebook directly if you need them.)

### 5.6 Identification assumptions and target estimand

**§5.6 Identification assumptions and target estimand** — see [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand). Covers the AHPVT trajectory-adjustment callout, the target estimand, the assumed causal DAG sketch, the L0 / L0+L1 / L0+L1+AHPVT adjustment-set ladder, structural positivity violations (saturated-school gating, W5 mode restriction, W4→W5 attrition), and what the screen does not identify without additional assumptions.

---

## 6. Analytic feasibility — joint-complete sample sizes

These are the actual usable Ns after AID overlap + exposure non-missing + outcome non-missing (excluding reserve codes). Computed by [scripts/prep/07_analytic_n.py](../scripts/prep/07_analytic_n.py).

| Design configuration | Analytic N | Feasibility |
|---|---:|---|
| W1 network (observed) ∩ W4 immediate recall | **3,505** | ✅ Strong |
| W1 network ∩ W4 backward digit span | **3,506** | ✅ Strong |
| W1 `AH_PVT` (baseline cog) ∩ W4 immediate recall | 4,883 | ✅ Strong (network not required) |
| W1 network ∩ W1 `AH_PVT` ∩ W4 immediate recall | **3,353** | ✅ Strong with baseline |
| W1 network ∩ W5 immediate recall | **394** | ⚠ Below N ≥ 500 red-line |
| W1 network ∩ W5 backward digit span (derived) | 394 | ⚠ Below red-line |
| W1 `AH_PVT` ∩ W5 immediate recall | 594 | ⚠ Marginal (above 500 without network) |
| W1 network ∩ W4 imm ∩ W5 imm (longitudinal change) | **334** | ⚠ Below red-line |
| Full longitudinal: W1 net ∩ W1 `AH_PVT` ∩ W4 imm ∩ W5 imm | 316 | ⚠ Too small |
| W1 network ∩ W4 ∩ W5 ∩ W6 (four-wave AID only) | 2,996 | N/A — W6 cognitive restricted |

**Usable designs (N ≥ 500):**
- W1 network/survey exposures → W4 cognitive (N ≈ 3,500 with network, ≈ 4,900 without)
- W1 **survey-based** friendship exposures → W5 cognitive (N ≈ 594 with baseline)

**Red-lined (< 500):** any design combining W1 network with W5 cognitive (~394); any W4→W5 change score with network (~334).

**Impossible in public-use:** W6 as a cognitive outcome; friend-level characteristics; custom networks beyond the 439 pre-computed.

### 6.5 Causal-screening diagnostic battery (D1–D9)

**§6.5 Causal-screening diagnostic battery (D1–D9)** — see [methods.md §2](methods.md#2-causal-screening-diagnostic-battery-d1d9). Covers each diagnostic (D1 baseline significance through D9 collider / double-adjustment red flags) with formal pass criteria, the composite-score categorisation (Strong / Mixed / Weakened / Drop), and the "passing D1–D9 is necessary but not sufficient" caveat.

---

## 7. Data-quality gotchas

1. **Network file structural 32.4% missingness.** Saturated-schools artifact; affects every centrality measure.
2. **Reciprocity variables `BMFRECIP`/`BFFRECIP`** are 64–70% missing (require nominated friend in-sample) — not a reliable standalone exposure.
3. **Section 20 absent-slot encoding** — unnominated friend slots get 0/blank/7, not NA. Infer nomination from friend-1 block non-missingness.
4. **Wave V mode restriction** on cognitive tests: In-person + Telephone only. 95% of non-administration is the `995` / `9995` "question not asked" reserve code.
5. **Reserve-code heterogeneity.** W1–W4 use 6/96/996 (refused), 7/97/997 (skip), 8/98/998 (DK), 9/99/999 (NA). W5 adds 95/995/9995 ("not asked") and Web/Mail modes have no DK option — DK arrives as silent NA.
6. **`AH_PVT` ~15% missing.** Use `AH_RAW` (~4.3% missing) and re-standardize.
7. **`PRXPREST` is continuous in public-use.** Range 0.00045–0.774, mean 0.161, std 0.070, 3,920 unique values across N=4,020 non-null in `w1network.sas7bdat`. Treat as a continuous centrality measure.
8. **Attrition is strongly sex-patterned.** At W5, female retention 64–76% vs male 43–63% within race strata. `GSW5`/`GSW6` correct partially for observed-cause attrition; [IPAW](glossary.md#ipaw-inverse-probability-of-attrition-weighting) or bounding is advisable for longitudinal claims (see [methods.md §1](methods.md#1-identification-assumptions-and-target-estimand)).
9. **Race construction is hierarchical** in the default `RACE` variable — build from `H1GI6A–E` for flexible coding.
10. **Age uses month + year only** (day 15 imputed). Use the most recent wave's birthdate for discrepancies.

---

## 9. Outcome battery: primary + multi-outcome extension

The primary design targets W4 cognition (`W4_COG_COMP`, a z-score composite of `C4WD90_1` + `C4WD60_1` + `C4NUMSCR`; see §4.4). Task 15 extends the screen to **12 non-cognitive outcomes** so that signal can be checked for outcome specificity (is this a cognition-specific effect?) versus cross-outcome robustness (does adolescent connectedness track everything that happens to a person, or only some domains?).

**Motivation.** The cognitive-screening experiment found that AHPVT (W1 verbal IQ) absorbs most of the baseline network→cognition signal — peer centrality survives only the L0/L0+L1 specs, collapsing under the full L0+L1+AHPVT adjustment (β shrinks 50–70 %; see the D4 column in [experiments/cognitive-screening/](../experiments/cognitive-screening/)). That finding is specific to cognition and partly mechanistic: a network kid with a 1994 crystallized-ability head start is both more central and better-scoring at W4. The multi-outcome extension side-steps the AHPVT over-shadowing problem by asking whether the same exposures predict outcomes where verbal IQ should *not* be mechanistically on-path — cardiometabolic status, functional limitation, mental health, adult SES.

### Outcome table

The screen evaluates 14 outcomes: the primary W4 cognitive composite, 12 non-cognitive secondary outcomes (cardiometabolic, functional, mental-health, socioeconomic), and 1 contaminated negative control. Each outcome is uniformly screened with the W4 cross-sectional weight as a rank-preserving shortcut (W4-retained median Ns ~3,200; W5-retained median Ns ~2,400). Three outcome-specific caveats matter at the dataset-manual level:

- **Cardiometabolic outcomes** are right-skewed (BMI especially); trimming at the 99th percentile is advised pre-estimation. Blood-pressure outcomes need anti-hypertensive medication flags brought in for formal estimation. BMI and waist circumference are highly collinear (r ≈ 0.9); BMI-class is treated as numeric for the screen but recast as ordinal logit in formal estimation. (See [methods.md §3 Ordered logit and interval regression](methods.md#ordered-logit-and-interval-regression).)
- **Mental-health outcomes** include two PSS-4 components in *opposite* scoring direction (one item phrased negatively, one positively reverse-scored) — composite construction must align valence first.
- **Socioeconomic outcomes** include current-work status (3-level, not binary — "no, temporarily absent" is its own category) and personal earnings (bracketed 1–13, not raw dollars — treat as ordinal, fit with interval regression).

(Variable codes, verbatim labels, and per-outcome valid Ns: see [variable_dictionary.md §2.4 Primary outcome — W4 cognition](variable_dictionary.md#24-primary-outcome--w4-cognition), [§2.5 Secondary outcomes](variable_dictionary.md#25-secondary-outcomes--task-15-multi-outcome-extension-12), and [§2.7 Negative-control outcome](variable_dictionary.md#27-negative-control-outcome).)

> **How to read D2 results given the contaminated NC.** The screen's D2 column (negative-control outcome = adolescent-derived adult height) is reported for transparency but is **not load-bearing** for the shortlist. We do not drop an exposure from the Strong / Mixed category on the basis of D2 alone; we *do* report D2 passes as weak corroboration of no NC-level confounding. A D2 fail on network-centrality exposures is treated as ambiguous — it could indicate unblocked confounding, **or** it could reflect the known height → peer-status pathway. The planned negative-control battery experiment introduces a cleaner NC set (blood type, age at menarche, hand-dominance, residential stability pre-W1) to resolve this; until then any handoff recommendation should be caveated as "D2-unverified." See [research_journal.md](research_journal.md) for the chronological critique.

> **Weight caveat and IPAW for W5 outcomes.** The W4 cross-sectional weight is used uniformly across all 14 outcomes for screening — a comparability shortcut that preserves rank-order across outcomes for a *screen*, but **not** an estimation-grade weight for W5 outcomes. Formal causal estimation should:
>
> 1. **Use the W5 cross-sectional weight for W5 outcomes, the W4 weight for pure-W4 outcomes.** Each wave's cross-sectional weight targets a specific population (W4-retained respondents vs. W5-retained respondents). Variable codes for both are in [variable_dictionary.md §2.2 Sampling weights](variable_dictionary.md#22-sampling-weights).
> 2. **Layer IPAW on top of the W5 weight.** The W5 weight corrects for **observed** attrition patterns the Add Health team modeled (sex, race, region), but not for attrition that is differential on W1 covariates or exposure. [IPAW](glossary.md#ipaw-inverse-probability-of-attrition-weighting) = fit a logistic model for "appears in W5 mode-eligible cell" on L0+L1+AHPVT + exposure, compute the inverse fitted probability, and multiply into the W5 weight. This targets the W5 cognition/SES/mental-health outcome's ATE in the broader population that W4 respondents were drawn from. See [methods.md §3 Inverse-probability-of-attrition weighting (IPAW)](methods.md#inverse-probability-of-attrition-weighting-ipaw).
> 3. **Re-check positivity under W5-weight + IPAW.** Extreme IPAW weights (> 95th percentile) should be trimmed or stabilized; document stabilized effective N.
> 4. **Bound, don't adjust**, when the full covariate set for a proper IPAW fit isn't observed (e.g. school saturation). Prefer Manski-style bounds to a speculative weight.

### Key task-15 findings

- **Breadth of signal varies sharply by outcome group.** Adult earnings had the widest hit, with 12/24 exposures at p < 0.05; most cardiometabolic outcomes saw 2–6 hits; diastolic BP had 0. The primary cognitive outcome was mid-pack at 5/24.
- **4 handoff pairs recommended for formal causal estimation:** in-degree → waist, in-degree → BMI, in-degree → BMI-class, out-degree → adult earnings. The bridge to the planned `cardiometabolic-handoff/` and `ses-handoff/` formal-estimation experiments lives at [experiments/multi-outcome-screening/](../experiments/multi-outcome-screening/).
- **Direction coherence.** In-degree (popularity) is protective for cardiometabolic outcomes (β < 0 on BMI/waist) and positive for adult earnings. The diastolic BP null is itself informative — vascular pressure is not the primary channel.

(Per-exposure variable codes, the verbatim handoff-pair specifications, and the per-outcome significance counts live in [experiments/multi-outcome-screening/](../experiments/multi-outcome-screening/) as the canonical artifact.)

---

*Sources: ICPSR 21600 v26 (2026-03-03). All variable labels quoted verbatim from the shipped SAS/XPT files. Analytic Ns and missingness rates from the feasibility-profiling outputs. Protocol descriptions from the Wave VI Interviewer-Administered Word Recall and Backward Digit Span User Guide (Aiello et al. 2025) and the Add Health Guidelines for Analyzing Add Health Data.*

---

## Glossary

**Glossary** — see [reference/glossary.md](glossary.md).

---

## Changelog

Reverse-chronological. Only entries that can be verified from the repo / git history or the current session.

- **2026-04-25** — File renamed from `addhealth_synthesis.md` to `dataset_manual.md` as part of the repo restructure. §5.6 (identification assumptions) and §6.5 (D1–D9 diagnostic battery) moved to `reference/methods.md`. Glossary moved to `reference/glossary.md`. §8 (recommended designs) and §10 (deliverables index) deleted — subsumed by `experiments/README.md` and `report.md`. Variable code listings stripped from §3, §4, §5 — single source of truth is now `reference/variable_dictionary.md`.
- **2026-04-21** — Reviewer-feedback pass (causal-inference PhD student + math/CS undergrad): added §5.6 "Identification assumptions and target estimand" with starred AHPVT confounder-vs-mediator callout and the assumed-DAG / positivity / IPAW narrative; added §6.5 "Causal-screening diagnostic battery (D1–D9)" with formal pass/fail thresholds and plain-language intuition per diagnostic; expanded the §9 weight caveat into an explicit IPAW recipe and added a "how to read D2 under the contaminated NC" callout; added a plain-language Glossary appendix with anchor links used throughout the reference set. Pitfall #7 (PRXPREST) trimmed — the stale "earlier notes were incorrect" apology is removed now that the root cause is fixed in the prep script ([scripts/prep/05_weighted_descriptives.py](../scripts/prep/05_weighted_descriptives.py)) and the regenerated [scripts/prep/outputs/05_weighted_descriptives.md](../scripts/prep/outputs/05_weighted_descriptives.md).
- **2026-04-21** — §9 rewritten from "Pivot option — cardiometabolic / vascular outcomes" to "Outcome battery: primary + multi-outcome extension" covering the 12 Task 15 outcomes + primary cognition + height NC (14-row outcome table with weight caveat callout). §10 deliverables index extended from task 7 through task 15. §2.5 now points readers to the new [variable_dictionary.md](variable_dictionary.md). This Changelog section added.
- **2026-04-20** — Pitfall #7 (§7) corrected: `PRXPREST` was previously described as a binary 0/1 variable, which contradicted §3.1 line 117 showing the continuous range [0, 0.77]. Corrected to "continuous in public-use" with empirical range / mean / std and an explicit note that earlier binary descriptions were wrong.
- **Earlier** — Initial merged synthesis from v2 feasibility report + documentation report + empirical feasibility summary. See `git log reference/addhealth_synthesis.md` for prior history.

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

```stata
* Stata (public-use, Wave V outcome, cross-sectional)
svyset CLUSTER2 [pweight=GSW5], strata() vce(linearized) singleunit(missing)
svy, subpop(analysis_sample): regress outcome exposure i.covariates
```

```r
# R (public-use)
library(survey); library(haven)
design <- svydesign(ids=~CLUSTER2, weights=~GSW5, data=df, nest=FALSE)
design_sub <- subset(design, analysis_sample == 1)   # never pre-filter rows
```

Python's survey-aware ecosystem is thinner; `samplics` is the most complete, or approximate with `statsmodels` GEE + cluster-robust SEs.

### 2.5 Merging

All files merge one-to-one on **`AID`** (label: "RESPONDENT IDENTIFIER"). Base = Wave I in-home; left-join Wave I network, Wave III PVT, Wave IV in-home, Wave V mixed-mode, Wave V/VI biomarker files as needed. After each merge, verify N against the source file.

---

## 3. Primary exposure: adolescent friendship / social connection

Three data sources. Use in combination where possible.

### 3.1 Wave I Public-Use Network File — pre-computed sociometric measures

`data/W1/w1network.sas7bdat` — 6,504 rows × 439 variables, constructed from the Wave I In-School Questionnaire nomination roster (full-sample N≈90,118 students). No raw nominations, no friend IDs. No weight variable ships with this file — apply `GSWGT1` + `CLUSTER2` after merging to Wave I in-home.

**Structural 32.4% missingness.** All centrality measures are NA for non-saturated-schools respondents. Only **4,397 of the 6,504 public-use respondents** have any network measures. This is by design (centralities require saturated-school nominations) but halves effective N before any outcome is merged.

#### Centrality variables (9 total, verbatim labels)

| Variable | Label | N valid | Range | Mean |
|---|---|---:|---|---:|
| `IDGX2` | "In-Degree: TFN" | 4,397 | 0–30 | 4.55 |
| `ODGX2` | "Out-Degree: TFN" | 4,397 | 0–10 | 4.46 |
| `BCENT10X` | "Bonacich Centrality P=.1" | 4,397 | 0–4.29 | 0.79 |
| `REACH` | "N reachable alters: TFN" | 4,397 | 0–1,791 | 474.6 |
| `REACH3` | "N reachable alters 3 steps: TFN" | 4,328 | 0–264 | 56.0 |
| `IGDMEAN` | "mean dist to reachable alters" | 3,705 | 1.00–21.39 | 5.28 |
| `PRXPREST` | "Proximity Prestige" | 4,020 | 0–0.77 | 0.16 |
| `INFLDMN` | "Influence Domain" | 4,397 | 0–1,705 | 474.3 |
| `RCHDEN` | "Density at maximum Reach" | 4,397 | 0.16–0.96 | 0.71 |

"TFN" = "Total Friendship Nominations" (up to 5 male + 5 female per respondent on the In-School roster).

#### Local-structure and isolation variables (selected)

| Variable | Label | N valid | Notes |
|---|---|---:|---|
| `HAVEBMF` | "R has a Best Male Friend" | 4,397 | Isolation flag |
| `HAVEBFF` | "R has a best Female friend" | 4,397 | Isolation flag |
| `BMFRECIP` | "Best Male Frnd Recip (any)" | 1,963 | **69.8% missing** (requires friend in-sample) |
| `BFFRECIP` | "Best Female Frnd Recip.(any)" | 2,313 | **64.4% missing** (same reason) |
| `ESDEN`/`ERDEN`/`ESRDEN` | "Density: Ego Send / Receive / S&R Net" | varies | Clustering-adjacent; not a canonical clustering coefficient |

**No clustering coefficient variable exists by name.** Network-file deliverables catalog the remaining 186 school-level aggregates (`SIZE`, `NOUTNOM`, `AX*` alter-mean variables) and 216 auxiliary variables — see [03b_network_variable_catalog.md](../outputs/03b_network_variable_catalog.md).

### 3.2 Wave I In-Home Interview — Section 20 friendship roster (self-report)

`data/W1/w1inhome.sas7bdat`. Section 20 splits into two parallel 45-variable blocks:

- `H1MF*` — male-friend nominations (5 friends × 9 items)
- `H1FF*` — female-friend nominations (5 friends × 9 items)

The 9 items per nominated friend (shown for male-friend-1; the grid repeats A/B/C/D/E for friends 1–5):

| Variable | Exact codebook label |
|---|---|
| `H1MF2A` | "S20Q1A MALE FRIEND1- SCHOOL-W1" |
| `H1MF3A` | "S20Q2A MALE FRIEND1-GRADE-W1" |
| `H1MF4A` | "S20Q3A MALE FRIEND1-SAMPLE SCHOOL-W1" |
| `H1MF5A` | "S20Q4A MALE FRIEND1-SISTER SCHOOL-W1" |
| `H1MF6A` | "S20Q6A MALE FRIEND 1-FRIENDS HOUSE-W1" |
| `H1MF7A` | "S20Q7A MALE FRIEND1-MEET AFTER SCHOOL-W1" |
| `H1MF8A` | "S20Q8A MALE FRIEND1-TIME LAST WEEKEND-W1" |
| `H1MF9A` | "S20Q9A MALE FRIEND1-TALK ABOUT A PROB-W1" |
| `H1MF10A` | "S20Q10A MALE FRIEND1-TALK ON PHONE-W1" |

Female block (`H1FF2A`…`H1FF10E`) uses the same structure; item 9 is labeled "DISCUSS A PROB" instead of "TALK ABOUT A PROB" and "MEET AFTER SCHL" rather than "MEET AFTER SCHOOL" — minor textual drift in the codebook.

**Absent-slot encoding warning.** Unnominated friend-2…friend-5 slots are populated with zeros, blanks, or reserve code 7 — *not* NA. Nomination must be inferred from non-missingness on the friend-1 block (`H1MF2A`/`H1FF2A` etc.). There is no `H1MF1` / `H1FF1`. See [03a_wave1_friendship_items.md](../outputs/03a_wave1_friendship_items.md) for the full 90-variable enumeration.

### 3.3 Wave I School Belonging scale (Section 5 — `H1ED19–24`)

| Variable | Exact label | N valid | Scale |
|---|---|---:|---|
| `H1ED19` | "S5Q19 FEEL CLOSE TO PEOPLE AT SCHOOL-W1" | 6,366 | 1–5 Likert |
| `H1ED20` | "S5Q20 FEEL PART OF YOUR SCHOOL-W1" | 6,366 | 1–5 |
| `H1ED21` | "S5Q21 STUDENTS AT SCHOOL PREJUDICED-W1" | 6,347 | 1–5 |
| `H1ED22` | "S5Q22 HAPPY AT YOUR SCHOOL-W1" | 6,365 | 1–5 |
| `H1ED23` | "S5Q23 TEACHERS TREAT STUDENTS FAIRLY-W1" | 6,367 | 1–5 |
| `H1ED24` | "S5Q24 FEEL SAFE IN YOUR SCHOOL-W1" | 6,367 | 1–5 |

### 3.4 Other Wave I adolescent-social variables

| Variable | Exact label | Notes |
|---|---|---|
| `H1DA7` | "S2Q7 HANG OUT WITH FRIENDS-W1" | Daily-activity item; 6,498 valid |
| `H1FS13` | "S10Q13 FELT LONELY-W1" | CES-D item, relevant to loneliness |
| `H1FS14` | "S10Q14 PEOPLE UNFRIENDLY TO YOU-W1" | CES-D item |
| `H1PR4` | "S35Q4 FRIENDS CARE ABOUT YOU-W1" | Protective-factors section |
| `FR_FLAG` | "NUMBER OF FRIENDS ASKED TO NOMINATE-W1" | Design variable |

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

`data/W1/w1inhome.sas7bdat`:

| Variable | Exact label | N valid | Mean (SD) |
|---|---|---:|---|
| `AH_PVT` | "ADD HEALTH PICTURE VOCABULARY TEST SCORE" | 5,503 | 101.0 (SD 15.1) |
| `AH_RAW` | "RAW PICTURE VOCABULARY TEST SCORE" | 6,223 | 64.8 (SD 11.1) |

`AH_PVT` has **~15% combined missing** (4.3% NA + 11.1% reserve codes). `AH_RAW` is cleaner (~4.3% NA). Recommendation: re-standardize from `AH_RAW` if you need a z-score baseline.

### 4.3 Wave III AHPVT repeat

`data/W3/w3pvt.sas7bdat`:

| Variable | Exact label | N valid | Notes |
|---|---|---:|---|
| `AH_RAW` | "RAW AH_PVT SCORE" | 4,874 | W3 raw score (note: different file than W1 but same variable name) |
| `PVTSTD3C` | "CROSS-SECTIONAL STANDARDIZED SCORE-W3" | 4,703 | Mean 99.8, SD ~15 after reserve-code strip |
| `PVTSTD3L` | "LONGITUDINAL STANDARDIZED SCORE-W3" | 4,703 | Mean 101.7, SD ~15 |
| `PVTPCT3` | "CROSS-SECT/LONG PVT PERCENTILE RANK-W3" | 4,874 | |
| `PVTSTD1` | "CROSS-SECT/LONG PVT STANDRDIZED SCORE-W1" | 4,680 | W1 re-standardized for comparability; mean 100.37, SD 15.11 |
| `PVTPCT1C` | "CROSS-SECTIONAL PVT PERCENTILE RANK-W1" | 4,680 | |
| `PVTPCT1L` | "LONGITUDINAL PVT PERCENTILE RANK-W1" | 4,512 | |

### 4.4 Wave IV cognitive battery (`data/W4/w4inhome.sas7bdat`)

All scored outcomes are under the `C4` (constructed score) prefix — **not** `H4MH` (the `H4MH*` variables are interviewer-interruption flags, e.g. `H4MH1` "S14Q1 INTERRUPTD DURING 90 SEC RECALL-W4"). The three performance tests are:

| Variable | Exact label | N valid (substantive) | Range | Mean (SD) |
|---|---|---:|---|---|
| `C4WD90_1` | "S14 # WORDS ON LIST RECALLED 90 SEC-W4" | 5,101 | 0–15 | 6.66 (2.00) |
| `C4WD60_1` | "S14 # WORDS ON LIST RECALLED 60 SEC-W4" | 5,097 | 0–15 | 5.22 (2.07) |
| `C4NUMSCR` | "TOTAL SCORE ON NUMBER RECALL TASK-W4" | 5,102 | 0–7 | 4.19 (1.54) |

**Protocol** (identical across Waves IV, V, VI per the Wave VI user guide Aiello et al. 2025):
- **Word Recall.** Interviewer reads 15 unrelated nouns at ~1 word/sec. Respondent has 90 s for immediate recall, then after a ~1–2 min distractor has 60 s for delayed recall. Score = # correct (0–15).
- **Backward Digit Span.** Interviewer reads digit sequences of increasing length (2 → 8); respondent repeats in reverse. Two trials per length; ends after two wrong at same length. Score = longest length correctly reversed on either trial (0–7).

Diagnostic variants (`C4WD90_2`, `C4WD90_3`, `C4WD60_2`, `C4WD60_3` — "# WORDS NOT ON LIST NAMED" / "# WORDS REPEATED") are available for error analyses. The same 15-word list is used at W4/W5/W6 — allows longitudinal comparison but introduces potential learning effects.

### 4.5 Wave V cognitive battery (`data/W5/pwave5.xpt`)

**Section 19 of the Wave V instrument.** Two pre-computed word-recall scores + 14 per-trial backward-digit-span pass/fail items.

| Variable | Exact label |
|---|---|
| `C5WD90_1` | "S19 # WORDS ON LIST RECALLED 90 SEC-W5" |
| `C5WD60_1` | "S19 # WORDS ON LIST RECALLED 60 SEC-W5" |
| `H5MH3A` | "S19Q3A NUMBER STRING/2-4-W5" |
| `H5MH3B` | "S19Q3B NUMBER STRING/5-7-W5" |
| `H5MH4A` | "S19Q4A NUMBER STRING/6-2-9-W5" |
| `H5MH4B` | "S19Q4B NUMBER STRING/4-1-5-W5" |
| `H5MH5A` | "S19Q5A NUMBER STRING/3-2-7-9-W5" |
| `H5MH5B` | "S19Q5B NUMBER STRING/4-9-6-8-W5" |
| `H5MH6A` | "S19Q6A NUMBER STRING/1-5-2-8-6-W5" |
| `H5MH6B` | "S19Q6B NUMBER STRING/6-1-8-4-3-W5" |
| `H5MH7A` | "S19Q7A NUMBER STRING/5-3-9-4-1-8-W5" |
| `H5MH7B` | "S19Q7B NUMBER STRING/7-2-4-8-5-6-W5" |
| `H5MH8A` | "S19Q8A NUMBER STRING/8-1-2-9-3-6-5-W5" |
| `H5MH8B` | "S19Q8B NUMBER STRING/4-7-3-9-1-2-8-W5" |
| `H5MH9A` | "S19Q9A NUMBER STRING/9-4-3-7-6-2-5-8-W5" |
| `H5MH9B` | "S19Q9B NUMBER STRING/7-2-8-1-9-6-5-3-W5" |

**No pre-computed backward-digit-span score exists at Wave V.** Must be derived: for each length L ∈ {2,…,8}, the trial pair is (`H5MHLA`, `H5MHLB`); respondent passes length L if either trial scored 1. Digit-span score = max L passed, else 0. See derivation in [04_missingness_profile.md](../outputs/04_missingness_profile.md#block-w5-cognitive-overall).

#### Mode restriction — the dominant constraint

| Variable | Exact label |
|---|---|
| `MODE` | "SURVEY MODE" |

Values: W = Web (self-administered online), I = In-person (CAPI), M = Mail (paper self-administered), T = Telephone (CATI), S = Spanish CAPI / other. Frequencies: W 76.8%, I 17.2%, M 3.5%, T 2.4%, S 0.1% (total 4,196).

**Empirically confirmed: cognitive items were administered only in In-person + Telephone modes.** Web/Mail/Spanish respondents receive reserve code 95/995/9995 ("question not asked") on every Section-19 item. Administered public-use Ns:

| Test | Variable | N administered | From modes |
|---|---|---:|---|
| Immediate Word Recall | `C5WD90_1` | **623** | I=523, T=100 |
| Delayed Word Recall | `C5WD60_1` | **620** | I=520, T=100 |
| Digit Span (any trial attempted) | `H5MH3A`…`H5MH9B` | **625** | I=525, T=100 |

This 95/995/9995 family means "not asked" — distinct from true NA and from legacy reserve codes 96/996/9996 (refused) etc. Missing-data operations must separate them before computing statistics.

### 4.6 Wave VI — public-use has no cognitive performance tests

The Add CAPS battery is restricted-only. Public-use Wave VI (`pwave6.sas7bdat`, 3,937 × 1,002) does contain *self-reported* memory items per the codebook (H6DA18B–H6DA18F per the Wave VI cognitive user guide). These are subjective memory complaints, not performance measures.

---

## 5. Confounders and covariates (public-use)

### 5.1 Wave I demographics

| Variable | Exact label | N valid | Notes |
|---|---|---:|---|
| `BIO_SEX` | "BIOLOGICAL SEX-W1" | 6,503 | 1=M, 2=F |
| `H1GI1M` | "S1Q1 BIRTHDAY-MONTH-W1" | — | Day 15 is imputed for DOB (day not collected) |
| `H1GI1Y` | "S1Q1 BIRTHDAY-YEAR-W1" | — | |
| `H1GI4` | "S1Q4 ARE YOU OF HISPANIC ORIGIN-W1" | 6,481 | |
| `H1GI6A` | "S1Q6A RACE-WHITE-W1" | 6,485 | |
| `H1GI6B` | "S1Q6B RACE-AFRICAN AMERICAN-W1" | 6,485 | |
| `H1GI6C` | "S1Q6C RACE-AMERICAN INDIAN-W1" | 6,485 | |
| `H1GI6D` | "S1Q6D RACE-ASIAN-W1" | 6,485 | |
| `H1GI6E` | "S1Q6E RACE-OTHER-W1" | 6,485 | |

Add Health's default constructed `RACE` variable uses a hierarchical rule (Hispanic → Black → Asian → Native → Other → White) that collapses multi-racial respondents. For flexible coding, build from the raw `H1GI6A–E` flags.

### 5.2 Wave I socioeconomic status (parent questionnaire + self-report)

| Variable | Exact label | N valid | Reserve | Notes |
|---|---|---:|---:|---|
| `PA55` | "A55 TOTAL HOUSEHOLD INCOME-PQ" | 4,929 | 9.2% refused | Primary SES variable |
| `PA12` | "A12 LEVEL OF EDUCATION-PQ" | 5,613 | — | Parent-respondent education |
| `PB8` | "B8 EDUCATION LEVEL OF PARTNER-PQ" | 4,120 | 22.2% skip (no partner) | Partner/spouse education |
| `H1RM1` | "S14Q1 RES MOM-EDUCATION LEVEL-W1" | 6,077 | 5.7% skip | Teen-reported resident-mom education |
| `H1RF1` | "S15Q1 RES DAD-EDUCATION LEVEL-W1" | 4,494 | 30.0% skip (absent father) | Teen-reported resident-dad education |
| `H1NM4` | "S12Q4 EDUCATION LEVEL OF BIO MOM-W1" | 727 | 88.6% skip | Biological-mom education (almost all skipped) |
| `H1NF4` | "S13Q4 EDUCATION LEVEL OF BIO DAD-W1" | 2,165 | 65.8% skip | Biological-dad education |

Variables `PA12A` and `PC13` do not correspond to parental education (the former doesn't exist; `PC13` is "C13 INFLUENCE OF BEST FRIEND-PQ").

### 5.3 Wave I CES-D depression scale (19 items)

Section 10 of the in-home interview, prefix `H1FS`:

| Variable | Exact label |
|---|---|
| `H1FS1` | "S10Q1 BOTHERED BY THINGS-W1" |
| `H1FS2` | "S10Q2 POOR APPETITE-W1" |
| `H1FS3` | "S10Q3 HAD THE BLUES-W1" |
| `H1FS4` | "S10Q4 JUST AS GOOD AS OTHER PEOPLE-W1" *(reverse-scored)* |
| `H1FS5` | "S10Q5 TROUBLE KEEPING MIND FOCUSED-W1" |
| `H1FS6` | "S10Q6 FELT DEPRESSED-W1" |
| `H1FS7` | "S10Q7 TOO TIRED TO DO THINGS-W1" |
| `H1FS8` | "S10Q8 HOPEFUL ABOUT THE FUTURE-W1" *(reverse-scored)* |
| `H1FS9` | "S10Q9 LIFE HAD BEEN A FAILURE-W1" |
| `H1FS10` | "S10Q10 FEARFUL-W1" |
| `H1FS11` | "S10Q11 HAPPY-W1" *(reverse-scored)* |
| `H1FS12` | "S10Q12 TALKED LESS THAN USUAL-W1" |
| `H1FS13` | "S10Q13 FELT LONELY-W1" |
| `H1FS14` | "S10Q14 PEOPLE UNFRIENDLY TO YOU-W1" |
| `H1FS15` | "S10Q15 ENJOYED LIFE-W1" *(reverse-scored)* |
| `H1FS16` | "S10Q16 FELT SAD-W1" |
| `H1FS17` | "S10Q17 FELT PEOPLE DISLIKE YOU-W1" |
| `H1FS18` | "S10Q18 HARD TO START DOING THINGS-W1" |
| `H1FS19` | "S10Q19 LIFE NOT WORTH LIVING-W1" |

Standard scoring: reverse items 4, 8, 11, 15 (`3 - x`); sum all 19. Expected range 0–57. All items are 0–3 Likert with separate reserve codes 6/7/8; treat those as missing before summing.

### 5.4 Wave V adult-contemporaneous covariates

Wave V prefix structure (`data/W5/pwave5.xpt`):

| Prefix | Section | Content |
|---|---|---|
| H5OD | 1 | Background/demographics |
| H5HR | 2 | Household roster |
| H5LM | 3 | Military and employment |
| H5EC | 4 | Income |
| H5ID | 5 | Health and healthcare |
| H5SE | 6 | Sexual experiences, pregnancy (CASI) |
| H5TO | 7 | Tobacco/alcohol/substances (CASI) |
| H5EL | 8 | Early life (retrospective) |
| H5PE | 9 | Personality |
| H5SS | 10 | Social support |
| H5WP | 11 | Parents and siblings |
| H5RE | 12 | Religion and spirituality |
| H5MN | 13 | Feelings and experiences / mental health (CASI) |
| H5CJ | 14 | Criminal justice (CASI) |
| H5TR | 15 | Relationships (CASI) |
| H5PG | 16 | Pregnancy / children / parenting (CASI) |
| H5DA | 17 | Illness and physical limitations |

**Section 10 (`H5SS*`) social support** is the adult-contemporary analog of the adolescent friendship exposure. Treat either as (a) a mediator of the adolescent → adult pathway, (b) a contemporaneous confounder, or (c) an independent adulthood exposure — depending on your identification strategy.

### 5.5 Wave III BEM Sex-Role Inventory (embedded in `w3inhome.sas7bdat`)

18 adjective items under `H3BM*` (Section 20 of Wave III) are visible in public-use. Exact labels for the retained items: `H3BM8` "S20Q8 TRADITIONAL SEX ROLES BEST-W3", `H3BM9` "S20Q9 R DEFENDS BELIEFS-W3", `H3BM10` "S20Q10 R IS AFFECTIONATE-W3", …, `H3BM36` "S20Q36 R IS AGGRESSIVE-W3". Derived scale scores are not in public-use.

---

## 6. Analytic feasibility — joint-complete sample sizes

These are the actual usable Ns after AID overlap + exposure non-missing + outcome non-missing (excluding reserve codes). Computed in [07_analytic_n.csv](../outputs/07_analytic_n.csv).

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

---

## 7. Data-quality gotchas

1. **Network file structural 32.4% missingness.** Saturated-schools artifact; affects every centrality measure.
2. **Reciprocity variables `BMFRECIP`/`BFFRECIP`** are 64–70% missing (require nominated friend in-sample) — not a reliable standalone exposure.
3. **Section 20 absent-slot encoding** — unnominated friend slots get 0/blank/7, not NA. Infer nomination from friend-1 block non-missingness.
4. **Wave V mode restriction** on cognitive tests: In-person + Telephone only. 95% of non-administration is the `995` / `9995` "question not asked" reserve code.
5. **Reserve-code heterogeneity.** W1–W4 use 6/96/996 (refused), 7/97/997 (skip), 8/98/998 (DK), 9/99/999 (NA). W5 adds 95/995/9995 ("not asked") and Web/Mail modes have no DK option — DK arrives as silent NA.
6. **`AH_PVT` ~15% missing.** Use `AH_RAW` (~4.3% missing) and re-standardize.
7. **`PRXPREST` is continuous in public-use.** Range 0.00045–0.774, mean 0.161, std 0.070, 3,920 unique values across N=4,020 non-null in `w1network.sas7bdat`. Treat as a continuous centrality measure (earlier notes in this doc that described it as binary 0/1 were incorrect and have been corrected; see also §2 variable table line for PRXPREST which shows the continuous range).
8. **Attrition is strongly sex-patterned.** At W5, female retention 64–76% vs male 43–63% within race strata. `GSW5`/`GSW6` correct partially for observed-cause attrition; IPAW or bounding is advisable for longitudinal claims.
9. **Race construction is hierarchical** in the default `RACE` variable — build from `H1GI6A–E` for flexible coding.
10. **Age uses month + year only** (day 15 imputed). Use the most recent wave's birthdate for discrepancies.

---

## 8. Recommended designs (ranked by feasibility)

### Primary — W1 social exposure → W4 cognitive (cross-sectional ages 24–32)

- **Exposures.** Network-file centralities (`IDGX2`, `ODGX2`, `BCENT10X`) on the saturated-schools subsample (N ≈ 4,397) OR the Section-20 self-report grid (`H1MF*`/`H1FF*`) plus `H1ED19–24` school belonging on the full Wave I sample (N = 6,504).
- **Outcomes.** `C4WD90_1`, `C4WD60_1`, `C4NUMSCR` — all near-complete at W4.
- **Baseline cognitive covariate.** `AH_PVT` or re-standardized `AH_RAW`.
- **Confounders.** `BIO_SEX`, Hispanic + race components, `PA55` (household income), `PA12`/`H1RM1`/`H1RF1` (parental education), CES-D sum derived from `H1FS1–19`.
- **Weights.** `svyset CLUSTER2 [pweight=GSWGT4_2]` for a cross-sectional W4 outcome, or `GSW145` / `GSW1345` for panel inference.
- **Analytic N ≈ 3,500 with network; ≈ 4,900 without.**

### Tertiary — W1 survey friendship → W5 cognitive with mode restriction (N ≈ 600)

- Use self-report (`H1MF*`/`H1FF*`/`H1ED*`); not the network file (collapses N to 394).
- Outcomes restricted to `MODE ∈ {I, T}`; apply `GSW5`.
- Most directly answers the "through middle age" framing but powered only for large effects.

### Not recommended

- W4 → W5 change-score with network exposure (N = 334): too small for credible identification.
- Any W6 cognitive outcome: restricted-use only.

---

## 9. Pivot option — cardiometabolic / vascular outcomes

If the primary cognition design becomes infeasible (e.g. stronger-than-expected network-file attrition after adding covariates), substitute a cardiometabolic outcome as a documented vascular-precursor pathway to late-life cognitive decline:

- **Wave IV biomarkers** (glucose, lipids, hsCRP, cardiovascular) — subset of N = 5,114
- **Wave V biomarkers** — N = 1,839 (3,883 for medications); hsCRP, renal, lipids, glucose
- **Wave VI biomarkers** — N = 2,010 biomarker subset; **hepatic injury (AST/ALT) is new in public-use at W6** (was restricted at W5)

The outcome is not cognition proper, but each captures a well-documented downstream dimension of adolescent social connection. Apply the same exposure/confounder specification from Section 8.

---

## 10. Deliverables index

| Task | File | Contents |
|---|---|---|
| 1 | [01_file_inventory.md](../outputs/01_file_inventory.md) | All 50 public-use data files: wave, N, columns, AID presence |
| 2 | [02_aid_overlap_focused.md](../outputs/02_aid_overlap_focused.md) | 50×50 AID intersection matrix + critical overlaps |
| 3a | [03a_wave1_friendship_items.md](../outputs/03a_wave1_friendship_items.md) | Section 20 `H1MF*`/`H1FF*` resolution, full 90-variable enumeration |
| 3b | [03b_network_variable_catalog.md](../outputs/03b_network_variable_catalog.md) | 439-variable network-file catalog with categorical breakdown |
| 3c | [03c_wave4_cognitive.md](../outputs/03c_wave4_cognitive.md) | W4 `C4WD90_1`, `C4WD60_1`, `C4NUMSCR` with distributions |
| 3d/e | [03de_wave5_cognitive_and_mode.md](../outputs/03de_wave5_cognitive_and_mode.md) | W5 cognitive vars, MODE, by-mode administration table |
| 3f/g/h | [03fgh_wave3_pvt_bem_weights.md](../outputs/03fgh_wave3_pvt_bem_weights.md) | W3 PVT, BEM items, full weight-variable map |
| 4 | [04_missingness_profile.md](../outputs/04_missingness_profile.md) | Per-variable missingness with reserve-code decomposition |
| 5 | [05_weighted_descriptives.md](../outputs/05_weighted_descriptives.md) | Survey-weighted univariate summaries |
| 6 | [06_attrition_summary.md](../outputs/06_attrition_summary.md) | Wave-by-wave appearance patterns; sex × race × parental-ed tertile stratification |
| 7 | [07_analytic_n.csv](../outputs/07_analytic_n.csv) | Joint-complete analytic Ns for each design configuration |

See also: [feasibility_summary.md](feasibility_summary.md) for the empirical profiling summary that supersedes the v2 feasibility report and the older documentation report.

---

*Sources: ICPSR 21600 v26 (2026-03-03). All variable labels quoted verbatim from the shipped SAS/XPT files. Analytic Ns and missingness rates from the feasibility-profiling outputs. Protocol descriptions from the Wave VI Interviewer-Administered Word Recall and Backward Digit Span User Guide (Aiello et al. 2025) and the Add Health Guidelines for Analyzing Add Health Data.*

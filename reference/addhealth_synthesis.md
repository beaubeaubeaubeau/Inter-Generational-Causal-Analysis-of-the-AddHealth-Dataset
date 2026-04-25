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

This project is Python-only. Survey-weighted WLS with cluster-robust SEs on `CLUSTER2` is implemented in [scripts/analysis_utils.py](../scripts/analysis_utils.py) (`_fit`) using `statsmodels`' `WLS` + `.get_robustcov_results(cov_type="cluster", groups=cluster)`. Subpopulation analysis is done by **keeping the full design frame and passing a subpop mask**, not by pre-filtering rows (pre-filtering biases cluster-level variance estimation). The `samplics` library is a more complete survey-analysis option but is not a dependency of this project.

### 2.5 Merging

All files merge one-to-one on **`AID`** (label: "RESPONDENT IDENTIFIER"). Base = Wave I in-home; left-join Wave I network, Wave III PVT, Wave IV in-home, Wave V mixed-mode, Wave V/VI biomarker files as needed. After each merge, verify N against the source file.

> **Variable-code lookup.** Every code used in the screening pipeline (exposures, outcomes, covariates, weights, design) is catalogued in [reference/variable_dictionary.md](variable_dictionary.md) with verbatim codebook labels, valid-N counts, caveats, and cross-references back to this synthesis. Start there when reading a chart caption or script that names a code you don't recognise.

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

<a id="wave-v-cognitive-battery"></a>
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

### 5.6 Identification assumptions and target estimand

This is the single most important section for anyone reading coefficient tables or handoff recommendations. What follows is the causal model the screen assumes, the estimand we are targeting, and where the assumption is load-bearing.

> ⚠ **AHPVT serves as the W1 baseline cognitive measure; cognition-outcome estimands are trajectory-adjusted, not level-on-level.** Adjusting for `AH_PVT` (W1 verbal IQ) in a regression of `W4_COG_COMP` on adolescent social integration converts a level-on-level association into an approximate change-from-baseline contrast — i.e. "where you ended up cognitively, *given where you started*." Under the project's research question (cognitive **trajectory** from adolescence into mid-life), this is the right adjustment. The earlier confounder-vs-mediator framing is downgraded: only the strict mediation reading (years-of-pre-W1 social integration → AHPVT → adult cognition) would invalidate it, and that reading requires social experiences before age 12–19 to have causally moved verbal IQ measurably — implausible-but-not-impossible. The trajectory interpretation also rests on three explicit caveats:
>
> 1. **Construct mismatch.** AHPVT measures crystallized vocabulary; `W4_COG_COMP` measures fluid memory (word recall) + working memory (digit span). The two are correlated (literature: r ≈ 0.5–0.7) but not identical. AHPVT is a *proxy* baseline for general cognitive ability, not an identical-construct pre-test. Treat the trajectory β as "trajectory under a vocabulary-anchored baseline."
> 2. **Vocabulary-as-baseline assumes general-g loading.** The interpretation rests on AHPVT being a stable-trait measure of general cognitive ability (g-loaded) rather than a domain-specific verbal skill. If AHPVT picks up specifically verbal experience that is itself shaped by social integration, the proxy leaks.
> 3. **Task 16 front-door** is now a *sensitivity* check, not a load-bearing alternative model. It quantifies how much the trajectory β changes if you assume the strict mediator reading; the *primary* report is the trajectory-adjusted β.

**Target estimand.** The **total effect of W1 social integration on the W4 / W5 outcome's deviation from its baseline-cognition prediction** — i.e. for cognitive outcomes, the trajectory contrast E[Y(x₁) − Y(x₀) | baseline = AHPVT]; for non-cognitive outcomes, the population total effect E[Y(x₁) − Y(x₀)] in the analytic cell. Throughout the project the estimand is **partial / conditional on baseline**, not a population ATE on cognition level.

**Assumed causal structure** (the [DAG library](dag_library.md) renders this graphically per outcome family; the textual sketch is here):

- **Common causes** C flow into both X and Y: demographics (`BIO_SEX`, `RACE`, `PARENT_ED`), W1 mental/health state (`CESD_SUM`, `H1GH1`), and W1 baseline cognition (`AH_PVT`).
- **Assumed adjacencies**: C → X, C → Y, X → Y. No reverse adolescent → adolescent arrow (X is measured at W1, Y at W4 or W5).
- **Assumed absent (unmeasured)**: school climate / context, prenatal & perinatal factors, adolescent diet & physical fitness, family genetic variants. The clean NC battery (Task 16) is what makes this assumption testable; the contaminated `HEIGHT_IN` NC is reported but not load-bearing (see [§9](#9-outcome-battery-primary--multi-outcome-extension)).
- **Deliberately unadjusted (downstream of X)**: W5 social support (`H5SS*`), W4 biomarker state (CRP, glucose) when outcome is W5. Adjusting for these would block part of the target effect.

**Adjustment-set ladder.** L0 → L0+L1 → L0+L1+AHPVT is designed so the β drift across the three (D4) measures *how much* of the raw signal each tier explains. It is one primary (L0+L1+AHPVT) with two diagnostic reductions.

| Set | Closes back-doors through | Identification role |
|---|---|---|
| L0 | Demographics (sex, race, parental ed) | Minimum acceptable adjustment; most β estimates move substantially when L1 is added if W1 affective state is a confounder |
| L0+L1 | + CES-D + self-rated health at W1 | Blocks confounding via W1 affective / somatic state |
| L0+L1+AHPVT | + W1 verbal IQ as baseline cognition | **Primary spec.** Identifies the trajectory-adjusted effect on cognitive outcomes; for non-cognitive outcomes acts as a general-ability confounder |

**Positivity / overlap.** Required for every stratum of the adjustment set at every level of X. D7 in the diagnostic battery checks this empirically (pass = p̂ ∈ (0.02, 0.98) and eff_N ≥ 500). The screen also has two **structural positivity violations** that are settled by restricting the estimand, *not* by re-weighting:

- **Saturated-school gating** (16 of 24 exposures, all the network-derived ones): centralities (`IDGX2`, `BCENT10X`, etc.) are *structurally undefined* outside saturated schools — there are no peer-roster nominations to compute on. This is positivity = 0, not low overlap. **Decision: do not extrapolate.** The reported estimand for every network exposure is **"ATE within saturated schools"** — full stop. We do not weight up to a counterfactual "if all schools were saturated" estimand, because the saturation-propensity model would be fitting on a structural zero. To make the external-validity gap visible, Task 16 will produce a **saturation-balance table** comparing weighted L0+L1+AHPVT means in saturated vs. non-saturated schools so a reader can judge transportability. Network-exposure plot captions and brief paragraphs must say "within saturated schools" explicitly.
- **Non-network exposures** (8 of 24: `FRIEND_*`, `SCHOOL_BELONG`, `H1FS13`, `H1FS14`, `H1DA7`, `H1PR4`) — sourced from the W1 in-home interview, sample-wide. No saturation restriction; positivity holds.
- **Mode restriction** (W5 cognitive outcomes): only W5 respondents in modes {I, T} received the cognitive battery (~824 of 4,196 once intersected with network data). The estimand is the ATE within the mode-eligible subpopulation; generalisability needs IPAW.
- **W4 → W5 attrition.** Differential retention by sex × race. Formal W5-outcome estimation needs **inverse-probability-of-attrition weighting (IPAW)** layered on `GSW5`. Screen uses `GSWGT4_2` uniformly as a comparability shortcut; not estimation-grade.

**What the screen does NOT identify without additional assumptions:**

- Population ATE across non-saturated schools for any network exposure (positivity = 0 by design; the saturation-balance table characterises but does not estimate).
- Direct-only or indirect-only effects through W5 social support (mediator-formula territory; not currently planned).
- Any W6 outcome (Add CAPS cognitive battery is restricted-use; no public-use W6 outcome maps cleanly to the W1 exposure set).

See the [Glossary](#glossary) for *back-door path*, *positivity*, *negative-control outcome*, *IPAW*; the [DAG library](dag_library.md) for the per-outcome causal graphs; the [experiments register](experiments_register.md) for the experiment ↔ DAG ↔ method ↔ output mapping.

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

### 6.5 Causal-screening diagnostic battery (D1–D9)

Every exposure in task 14 passes through nine diagnostics. Each D tests a specific identification assumption or data-quality condition; passing them together is necessary but not sufficient for a causal interpretation. Full implementation: [scripts/task14_causal_screening.py](../scripts/task14_causal_screening.py). Per-exposure pass/fail grid: [outputs/14_screening_matrix.csv](../outputs/14_screening_matrix.csv). Narrative walk-through: [research_journal.md §Phase 4](research_journal.md#phase-4--preliminary-causal-screening-d1d9).

Terms used below (see [Glossary](#glossary) for plain-language intuition): *back-door path*, *confounder vs. mediator*, *negative-control outcome*, *positivity*, *collider*.

| # | Name | What it checks | Formal pass criterion | Fail means |
|:-:|---|---|---|---|
| **D1** | Baseline significance | Is there any signal at the primary spec (L0+L1+AHPVT) before stability / specificity checks? | p < 0.05 on the exposure coefficient in a WLS fit with `GSWGT4_2` + cluster-robust SE on `CLUSTER2` | No detectable marginal association; later diagnostics are informational only |
| **D2** | Negative-control outcome | Does the exposure predict an outcome it *shouldn't* (`HEIGHT_IN`)? If yes, unmeasured confounding is likely. | p ≥ 0.10 on exposure → adult height, under the primary adjustment set | NC-level confounding is detected — but see the contamination caveat in [§9](#9-outcome-battery-primary--multi-outcome-extension) |
| **D3** | Sibling dissociation | Is the target effect larger than a "related but weaker" sibling exposure, and in the same sign? Same-school / same-grid contrast. | `sign(β_target) == sign(β_sibling)` **AND** `\|β_target\| > \|β_sibling\|` **AND** `\|β_target − β_sibling\| > sqrt(se_t² + se_s²)` | Target and sibling are indistinguishable → target probably isn't capturing exposure-specific signal |
| **D4** | Adjustment-set stability | How much does β drift as the adjustment set expands L0 → L0+L1 → L0+L1+AHPVT? Large drift = hidden confounding OR hidden mediation. | Relative shift `(max − min) / \|β_primary\| < 0.30` **AND** sign stable across all three | β depends on which covariates you include — causal identification is not closed by the assumed DAG |
| **D5** | Outcome-component consistency | Do the three W4 cognitive sub-tests (immediate/delayed word recall, digit span) line up in sign? Cognition only. | All three component β in the same direction as the composite, no opposite-sign dissent | Composite signal is driven by one sub-test; spurious or narrow construct |
| **D6** | Dose-response monotonicity | For a continuous exposure, does the outcome move monotonically across exposure quintiles? | `|Spearman ρ| > 0.7` across quintile means **AND** `monotone_sign` holds (no mid-range inversion); the signed Spearman's absolute value captures monotonicity in either direction | Non-monotonic response — linear-in-X spec is mis-specified |
| **D7** | Positivity / overlap | Is there non-zero probability of every exposure level at every covariate stratum? Q5-vs-Q1 logit (continuous) or binary balance (binary). | Fitted p̂ ∈ (0.02, 0.98) AND effective N ≥ 500 after overlap trimming | No usable comparison group in parts of covariate space; estimate is extrapolation |
| **D8** | Saturated-school selection penalty | Informational. How much of W1 is lost to the network-file saturation gate for this specific exposure? | Reports N(analytic) / N(W1) ratio; no pass/fail threshold | External-validity caveat — estimand is within-saturated-schools |
| **D9** | Collider / double-adjustment red flags | Hard-coded list of known bad-combination exposures (e.g. using `H1FS13` as exposure while adjusting for `CESD_SUM`, which contains `H1FS13`). | Not on the red-flag list | Collider bias or mechanical double-counting; drop from shortlist |

**Composite score.** Each exposure is scored 0–8 based on passes across D1–D9 (D8 is informational; red-flags discount the score). Categories: **Strong** (score ≥ 7), **Mixed** (5–6), **Weakened** (3–4), **Drop** (< 3 or D9 red flag). The task-16 handoff is drawn from Strong + Mixed, never from Drop.

**Why the battery is not sufficient.** Passing D1–D9 does *not* prove a causal effect — it only rules out nine specific failure modes. Unmeasured confounders outside the L0+L1+AHPVT set (school climate, early-childhood cognition, family SES beyond parental education) are still possible. Task 16's job is to bound those via front-door decomposition, E-value-style sensitivity, and a cleaner NC battery.

---

## 7. Data-quality gotchas

1. **Network file structural 32.4% missingness.** Saturated-schools artifact; affects every centrality measure.
2. **Reciprocity variables `BMFRECIP`/`BFFRECIP`** are 64–70% missing (require nominated friend in-sample) — not a reliable standalone exposure.
3. **Section 20 absent-slot encoding** — unnominated friend slots get 0/blank/7, not NA. Infer nomination from friend-1 block non-missingness.
4. **Wave V mode restriction** on cognitive tests: In-person + Telephone only. 95% of non-administration is the `995` / `9995` "question not asked" reserve code.
5. **Reserve-code heterogeneity.** W1–W4 use 6/96/996 (refused), 7/97/997 (skip), 8/98/998 (DK), 9/99/999 (NA). W5 adds 95/995/9995 ("not asked") and Web/Mail modes have no DK option — DK arrives as silent NA.
6. **`AH_PVT` ~15% missing.** Use `AH_RAW` (~4.3% missing) and re-standardize.
7. **`PRXPREST` is continuous in public-use.** Range 0.00045–0.774, mean 0.161, std 0.070, 3,920 unique values across N=4,020 non-null in `w1network.sas7bdat`. Treat as a continuous centrality measure.
8. **Attrition is strongly sex-patterned.** At W5, female retention 64–76% vs male 43–63% within race strata. `GSW5`/`GSW6` correct partially for observed-cause attrition; [IPAW](#glossary) or bounding is advisable for longitudinal claims (see [§5.6](#56-identification-assumptions-and-target-estimand)).
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

## 9. Outcome battery: primary + multi-outcome extension

The primary design targets W4 cognition (`W4_COG_COMP`, a z-score composite of `C4WD90_1` + `C4WD60_1` + `C4NUMSCR`; see §4.4). Task 15 extends the screen to **12 non-cognitive outcomes** so that signal can be checked for outcome specificity (is this a cognition-specific effect?) versus cross-outcome robustness (does adolescent connectedness track everything that happens to a person, or only some domains?).

**Motivation.** Task 14 found that AHPVT (`AH_PVT`, W1 verbal IQ) absorbs most of the baseline network→cognition signal — peer centrality survives only the L0/L0+L1 specs, collapsing under the full L0+L1+AHPVT adjustment (β shrinks 50–70 %; see [outputs/14_screening_matrix.csv](../outputs/14_screening_matrix.csv) D4 column). That finding is specific to cognition and partly mechanistic: a network kid with a 1994 crystallized-ability head start is both more central and better-scoring at W4. The multi-outcome extension side-steps the AHPVT over-shadowing problem by asking whether the same exposures predict outcomes where verbal IQ should *not* be mechanistically on-path — cardiometabolic status, functional limitation, mental health, adult SES.

### Outcome table

14 rows: primary cognition + 12 task-15 outcomes + 1 negative control. Columns: code, verbatim label, wave, kind, weight used in screening, median N across 24 exposures, role, caveat.

| Code | Label (verbatim) | Wave | Kind | Weight (screen) | N (median) | Role | Caveat |
|---|---|:-:|---|---|:-:|---|---|
| `W4_COG_COMP` | derived: z(`C4WD90_1`)+z(`C4WD60_1`)+z(`C4NUMSCR`) | W4 | continuous | `GSWGT4_2` | 3,409 | primary | AHPVT over-shadows network effects (D4 collapse); composite aids power vs. single-test variants |
| `H4BMI` | "S27 BMI—W4" | W4 | continuous | `GSWGT4_2` | 3,234 | secondary screen | Right-skewed; trimming at 99th percentile advised pre-estimation |
| `H4SBP` | "S27 SYSTOLIC BLOOD PRESSURE—W4" | W4 | continuous | `GSWGT4_2` | 3,197 | secondary screen | Anti-hypertensive use is unadjusted in task15; task16 should bring in `H4TO*` medication flags |
| `H4DBP` | "S27 DIASTOLIC BLOOD PRESSURE—W4" | W4 | continuous | `GSWGT4_2` | 3,197 | secondary screen | Same medication caveat as `H4SBP` |
| `H4WAIST` | "S27 MEASURED WAIST (CM)—W4" | W4 | continuous | `GSWGT4_2` | 3,250 | secondary screen | Collinear with `H4BMI` (r ≈ 0.9); handoff pair overlaps |
| `H4BMICLS` | "S27 BMI CLASS—W4" | W4 | ordinal 1–6 | `GSWGT4_2` | 3,234 | secondary screen | CDC weight-class categorical; task15 treats as numeric for the screen, recast as ordinal logit in task16 |
| `H5ID1` | "S5Q1 HOW IS GEN PHYSICAL HEALTH—W5" | W5 | 5-point Likert | `GSWGT4_2` | 2,438 | secondary screen | Self-rated health; 1=excellent → 5=poor (higher = worse) |
| `H5ID4` | "S5Q4 LIMIT CLIMB SEV. FLIGHT STAIRS—W5" | W5 | 3-level | `GSWGT4_2` | 2,439 | secondary screen | 1=not at all → 3=a lot limited; floor-effect at younger ages |
| `H5ID16` | "S5Q16 HOW OFTEN TROUBLE SLEEPING—W5" | W5 | 5-point Likert | `GSWGT4_2` | 2,437 | secondary screen | Higher = more trouble |
| `H5MN1` | "S13Q1 LAST MO NO CNTRL IMPORT THINGS—W5" | W5 | 5-point Likert | `GSWGT4_2` | 2,387 | secondary screen | Perceived Stress Scale item (PSS-4 component); CASI-administered |
| `H5MN2` | "S13Q2 LAST MO CONFID HANDLE PERS PBMS—W5" | W5 | 5-point Likert | `GSWGT4_2` | 2,380 | secondary screen | PSS-4 component, **reverse-scored direction** vs `H5MN1` |
| `H5LM5` | "S3Q5 CURRENTLY WORK—W5" | W5 | 3-level | `GSWGT4_2` | 2,436 | secondary screen | Not binary: {1=yes, 2=no temp absent, 3=no not employed}. Task16 should recode before logistic estimation |
| `H5EC1` | "S4Q1 INCOME PERS EARNINGS [W4–W5]—W5" | W5 | bracketed 1–13 | `GSWGT4_2` | 2,413 | secondary screen | **Bracketed dollars, not raw income** (1 = <$5k, 13 = $250k+). Treat as ordinal |
| `HEIGHT_IN` | derived in inches from `H4SE2`/`H4SE3` | W4 | continuous | `GSWGT4_2` | 3,392 | negative control (contaminated) | D2 diagnostic. Adolescent height is known to correlate with peer popularity, so D2 failure on centralities is *not* conclusive proof of confounding |

> **How to read D2 results given the contaminated NC.** The task 14 D2 column is reported for transparency but is **not load-bearing** for the shortlist. We do not drop an exposure from the Strong / Mixed category on the basis of D2 alone; we *do* report D2 passes as weak corroboration of no NC-level confounding. A D2 fail on network-centrality exposures (`IDGX2`, `BCENT10X`) is treated as ambiguous — it could indicate unblocked confounding, **or** it could reflect the known height → peer-status pathway. Task 16 will introduce a cleaner NC battery (blood type, age at menarche, hand-dominance, residential stability pre-W1) to resolve this; until then any handoff recommendation should be caveated as "D2-unverified." See also [research_journal.md §Phase 4 critique](research_journal.md#phase-4--preliminary-causal-screening-d1d9).

> **Weight caveat and IPAW for W5 outcomes.** `GSWGT4_2` is used uniformly across all 14 outcomes for screening — this is a comparability shortcut that preserves rank-order across outcomes for a *screen*, but is not an estimation-grade weight for W5 outcomes. Formal causal estimation in Task 16 should:
>
> 1. **Use `GSW5` for W5 outcomes, `GSWGT4_2` for pure-W4 outcomes.** Each wave's cross-sectional weight targets a specific population (W4-retained respondents vs. W5-retained respondents).
> 2. **Layer IPAW on top of `GSW5`.** `GSW5` corrects for **observed** attrition patterns the Add Health team modeled (sex, race, region), but not for attrition that is differential on W1 covariates or exposure. [IPAW](#glossary) = fit a logistic model for "appears in W5 mode-eligible cell" on L0+L1+AHPVT + exposure, compute the inverse fitted probability, and multiply into `GSW5`. This targets the W5 cognition/SES/mental-health outcome's ATE in the broader population that W4 respondents were drawn from.
> 3. **Re-check positivity under `GSW5` + IPAW.** Extreme IPAW weights (> 95th percentile) should be trimmed or stabilized; document stabilized effective N.
> 4. **Bound, don't adjust**, when the full covariate set for a proper IPAW fit isn't observed (e.g. school saturation). Prefer Manski-style bounds to a speculative weight.

### Key task-15 findings

- **Breadth of signal varies sharply by outcome group.** `H5EC1` (adult earnings) had the widest hit, with 12/24 exposures at p < 0.05; most cardiometabolic outcomes saw 2–6 hits; `H4DBP` had 0. The primary cognitive outcome was mid-pack at 5/24 (visual: [img/causal/15_per_outcome_pcount.png](../img/causal/15_per_outcome_pcount.png)).
- **4 handoff pairs recommended to Task 16** for formal causal estimation: `IDGX2 → H4WAIST`, `IDGX2 → H4BMI`, `IDGX2 → H4BMICLS`, `ODGX2 → H5EC1` (visual: [img/causal/15_handoff_forest.png](../img/causal/15_handoff_forest.png); rationale and shortlist: [outputs/15_multi_outcome.md](../outputs/15_multi_outcome.md)).
- **Direction coherence.** `IDGX2` (in-degree, i.e. popularity) is protective for cardiometabolic outcomes (β < 0 on BMI/waist) and positive for `H5EC1` earnings. `H4DBP` null is itself informative — vascular pressure is not the primary channel.

See also the per-exposure z-standardized β heatmap at [img/causal/multi_outcome_beta_heatmap.png](../img/causal/multi_outcome_beta_heatmap.png).

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
| 8 | [08_analytic_frame_n.md](../outputs/08_analytic_frame_n.md) | Canonical analytic frame (AID × key variables) post-overlap + after-reserve-strip Ns per exposure/outcome pair |
| 9 | [img/distributions/](../img/distributions/) (treatments, outcomes, covariates, conditional subdirs) | Univariate + conditional distribution plots for the 24 exposures, 13 outcomes, and L0/L1/AHPVT covariates. Generator: [scripts/task09_distribution_plots.py](../scripts/task09_distribution_plots.py) |
| 10 | [10_regressions.md](../outputs/10_regressions.md), [10_regressions.csv](../outputs/10_regressions.csv) | First-pass survey-weighted regressions, 24 exposures × 3 adjustment sets on `W4_COG_COMP` |
| 11 | [11_sensitivity.md](../outputs/11_sensitivity.md), [11_ahpvt_shift.csv](../outputs/11_ahpvt_shift.csv), [11_collinearity.csv](../outputs/11_collinearity.csv), [11_correlation.csv](../outputs/11_correlation.csv), [11_placebo_permutation.csv](../outputs/11_placebo_permutation.csv), [11_saturated_balance.csv](../outputs/11_saturated_balance.csv) | Sensitivity + stability audit: AHPVT shift, collinearity, permutation nulls, saturated-school balance |
| 12 | [img/regressions/](../img/regressions/) (coefficient_forest, composite_vs_components, heterogeneity_interactions, partial_residual_IDGX2, placebo_panel, quintile_dose_response, weighted_vs_unweighted) + [img/sensitivity/](../img/sensitivity/) (ahpvt_with_without). | Regression-diagnostic figures backing tasks 10–11: coefficient forests, partial-residual plots, dose-response, AHPVT shift. Generator: [scripts/task12_regression_plots.py](../scripts/task12_regression_plots.py) |
| 13 | [13_verification.md](../outputs/13_verification.md), plus 9 CSVs (`13_attrition_ipw.csv`, `13_benchmarks.csv`, `13_bh_fdr.csv`, `13_deff.csv`, `13_negctrl_exposure.csv`, `13_negctrl_outcome.csv`, `13_psu_counts.csv`, `13_reserve_code_sensitivity.csv`, `13_reserve_leakage.csv`) | Verification pack: benchmarking, FDR adjustment, design-effect audit, negative-control sweeps, reserve-code sensitivity |
| 14 | [14_screening.md](../outputs/14_screening.md), [14_screening_matrix.csv](../outputs/14_screening_matrix.csv), [14_shortlist.csv](../outputs/14_shortlist.csv) | D1–D9 causal-screening battery on `W4_COG_COMP` for all 24 exposures; pass/fail matrix + ranked shortlist |
| 15 | [15_multi_outcome.md](../outputs/15_multi_outcome.md), [15_multi_outcome_matrix.csv](../outputs/15_multi_outcome_matrix.csv) | Multi-outcome extension: D1 + D4 re-run across 12 non-cognitive outcomes; 4 handoff pairs shortlisted for Task 16 |
| 15 (figs) | [img/causal/15_per_outcome_pcount.png](../img/causal/15_per_outcome_pcount.png), [img/causal/15_handoff_forest.png](../img/causal/15_handoff_forest.png) | Journal-embedded figures for Phase 5: per-outcome significant-exposure counts and the four-pair Task-16 handoff forest. Generator: [scripts/task15_journal_figs.py](../scripts/task15_journal_figs.py) |

Headline figures: [img/causal/screening_heatmap.png](../img/causal/screening_heatmap.png), [img/causal/adjustment_stability.png](../img/causal/adjustment_stability.png), [img/causal/multi_outcome_beta_heatmap.png](../img/causal/multi_outcome_beta_heatmap.png), [img/causal/15_per_outcome_pcount.png](../img/causal/15_per_outcome_pcount.png), [img/causal/15_handoff_forest.png](../img/causal/15_handoff_forest.png).

See also: [feasibility_summary.md](feasibility_summary.md) for the empirical profiling summary that supersedes the v2 feasibility report and the older documentation report.

---

*Sources: ICPSR 21600 v26 (2026-03-03). All variable labels quoted verbatim from the shipped SAS/XPT files. Analytic Ns and missingness rates from the feasibility-profiling outputs. Protocol descriptions from the Wave VI Interviewer-Administered Word Recall and Backward Digit Span User Guide (Aiello et al. 2025) and the Add Health Guidelines for Analyzing Add Health Data.*

---

## Glossary

Plain-language definitions of the causal-inference and survey-statistics vocabulary used throughout the reference set. Each entry points to the section in this document where the concept first appears and explains *why* it matters for the project. Alphabetical.

### Back-door path
<a id="glossary-back-door-path"></a>
An indirect route from the exposure X to the outcome Y through a common ancestor C (C → X and C → Y), rather than through the intended causal channel X → Y. Back-door paths create *spurious* associations that look like causation. **Why it matters**: every unblocked back-door path biases the causal estimate. The job of the adjustment set ([§5.6](#56-identification-assumptions-and-target-estimand)) is to "close" all back-door paths by conditioning on at least one variable on each path. First used in [§7 pitfall #1 context](#7-data-quality-gotchas); formalised in [§5.6](#56-identification-assumptions-and-target-estimand).

### CASI (Computer-Assisted Self-Interview)
Sensitive items (drug use, sexual behaviour, mental-health items under `H5MN*`) are delivered via respondent-controlled screen so an interviewer is not in the loop. Higher truth-telling but more item non-response. First used in [§5.4](#54-wave-v-adult-contemporaneous-covariates).

### Cluster-robust standard error
A standard error that accounts for within-PSU correlation by treating each cluster (school pair = `CLUSTER2`) as a unit for variance computation. **Why it matters**: nominal OLS SEs assume independent observations. Add Health is school-clustered, so nominal SEs are too small; cluster-robust SEs are wider and more honest. First used in [§2.1](#21-design).

### Collider
A variable jointly *caused* by two others (X → C ← Z). **Why it matters**: conditioning on a collider *opens* a spurious association between its causes, the opposite of what you want. Example: if peer centrality and depression both cause school belonging, adjusting for school belonging creates a spurious centrality–depression correlation. D9 in the diagnostic battery ([§6.5](#65-causal-screening-diagnostic-battery-d1d9)) flags known-collider exposure choices.

### Confounder
A common cause of both exposure and outcome — adjusting for it is *required* to identify the causal effect. **Why it matters**: contrast with mediator — the two look the same empirically (both shift β when added to the model) but call for opposite treatment. The [AHPVT callout](#56-identification-assumptions-and-target-estimand) is the project's load-bearing confounder-vs-mediator ambiguity. First used in [§5.6](#56-identification-assumptions-and-target-estimand).

### DAG (Directed Acyclic Graph)
A flowchart where nodes are variables and arrows run from causes to effects, with no cycles. **Why it matters**: drawing a DAG forces you to make causal assumptions explicit, and once it's drawn, graph-theoretic rules tell you which covariates to adjust for. This project does not render a full DAG but describes one textually in [§5.6](#56-identification-assumptions-and-target-estimand).

### Design effect (DEFF)
Ratio of the true variance under the complex design to the variance under simple random sampling of the same N. **Why it matters**: DEFF > 1 means your 3,500-observation sample behaves like a smaller SRS sample for inference purposes. Audited in [outputs/13_deff.csv](../outputs/13_deff.csv).

### Dose-response monotonicity
The expectation that as exposure increases, the outcome changes in a consistent direction — no plateaus, inversions, or threshold effects. **Why it matters**: D6 in the diagnostic battery. A non-monotonic dose-response can signal non-linearity, effect heterogeneity, or misspecification of the linear-in-X model.

### Effective N (eff N)
Sample size adjusted for design effect and, where relevant, weight dispersion: `eff_N = N / DEFF` or more generally `eff_N = (Σw)² / Σw²`. **Why it matters**: D7 positivity check requires eff_N ≥ 500 post-trimming, not raw N. See [§6.5](#65-causal-screening-diagnostic-battery-d1d9).

### Front-door criterion
A causal identification strategy that bounds the X → Y effect through a mediator M when back-door adjustment fails (because unmeasured confounders exist). Requires X → M → Y with no direct X → Y, M fully mediating, and no unmeasured M–Y confounders. **Why it matters**: Task 16's plan for distinguishing whether AHPVT is a confounder or mediator of the social-integration → cognition path.

### Identification (identifying assumption, identification strategy)
The set of causal assumptions under which a statistical estimand (e.g. a regression coefficient) equals the causal estimand of interest (e.g. E[Y|do(X)]). **Why it matters**: β̂ is always estimable; whether it equals the causal effect depends on whether the identifying assumptions hold. [§5.6](#56-identification-assumptions-and-target-estimand) lists this project's assumptions.

### IPAW (Inverse-Probability-of-Attrition Weighting)
A reweighting scheme that inflates the weight on respondents who *remained* in the study to compensate for attrition of similar respondents. Computed as `w_IPAW = 1 / Prob(remain | covariates)`. **Why it matters**: W4 → W5 attrition is sex-patterned; cross-sectional W5 weights `GSW5` only partially correct for it. Formal W5 estimation should apply IPAW on top of `GSW5`. See [§5.6](#56-identification-assumptions-and-target-estimand) and outstanding uncertainty #3 in [research_journal.md](research_journal.md).

### IV (Instrumental Variable)
A variable Z that affects the exposure X but not the outcome Y except through X, and shares no common cause with Y. Used to identify X → Y even under unmeasured confounding. **Why it matters**: a fallback identification strategy for Task 16 if front-door is not credible.

### Mediator
A variable on the causal path X → M → Y. **Why it matters**: adjusting for M blocks part of the total effect, *shrinking β toward zero*. This is the opposite of what adjusting for a confounder does (which should reveal the true β by removing bias). The two operations look identical in a regression table — only a DAG (or a front-door / IV decomposition) can tell them apart. See [AHPVT callout, §5.6](#56-identification-assumptions-and-target-estimand).

### Mode (W5 survey mode)
The channel through which the W5 interview was administered: W = Web, I = In-person, M = Mail, T = Telephone, S = Spanish CAPI. **Why it matters**: cognitive items were administered only in I + T, restricting the W5 cognitive analytic cell to ~624 of 4,196. See [§4.5](#wave-v-cognitive-battery).

### Negative-control outcome (NC)
An outcome Y* that, under the assumed causal model, should **not** be affected by X. If X still predicts Y*, unmeasured confounding is implicated. **Why it matters**: D2 in the diagnostic battery uses `HEIGHT_IN`. The NC is contaminated (adolescent height correlates with peer popularity), so failures on network exposures are ambiguous. See [§9](#9-outcome-battery-primary--multi-outcome-extension).

### Positivity (overlap)
The assumption that every level of the exposure has non-zero probability of occurring at every level of the covariates. Formally: P(X = x | C = c) > 0 for all (x, c). **Why it matters**: without positivity, causal estimates in the violated region are extrapolations beyond the data, not causal effects. D7 in the diagnostic battery tests positivity empirically. Structural positivity violations (saturated-school gating, W5 mode restriction) are documented in [§5.6](#56-identification-assumptions-and-target-estimand).

### Post-stratification weight
A weight that re-scales the sample so that known marginal distributions (e.g. age × sex × race) match the population. **Why it matters**: `GSWGT4_2` is a post-stratified weight. Post-stratification corrects for differential sampling and non-response, not for unmeasured confounding.

### PSU (Primary Sampling Unit)
The first-stage unit in a multistage sample; for Add Health this is the high-school / feeder-middle-school pair (`CLUSTER2`, 132 PSUs). **Why it matters**: cluster-robust SEs, design effects, and `svyset` all reference the PSU. First used in [§2.2](#22-design-variables-in-public-use).

### Reserve code
Non-substantive codes on a variable indicating refusal, don't know, skip, or not-administered (W1–W4: 6/96/996 etc.; W5 adds 95/995/9995 for "not asked"). **Why it matters**: treating reserve codes as substantive values (e.g., summing them into a scale) silently corrupts every downstream statistic. `analysis_utils.clean_var` + `VALID_RANGES` strip them. See [§7 pitfall #5](#7-data-quality-gotchas).

### Saturated school
A school where ≥ 75 % of the student roster participated in the W1 In-School Questionnaire. **Why it matters**: network centralities (in-degree, etc.) require knowing who nominated the respondent, so they are only defined in saturated schools. ~32 % of W1 respondents are in non-saturated schools; their network variables are structurally missing. First used in [§3.1](#31-wave-i-public-use-network-file--pre-computed-sociometric-measures); positivity consequences in [§5.6](#56-identification-assumptions-and-target-estimand).

### Sibling dissociation (D3)
A specificity check: the *target* exposure should have a larger effect than a *sibling* exposure (a related variable expected to carry less of the causal signal), and both should move in the same direction. **Why it matters**: a target with a smaller or opposite-signed effect than its sibling is probably not capturing exposure-specific signal. Formalised in [§6.5](#65-causal-screening-diagnostic-battery-d1d9).

### Stratum
The second design dimension (after clustering) in a complex survey. **Why it matters**: stratum information is *not* in the public-use Add Health distribution. Per the Add Health user guide, omitting stratum "only minimally affects the standard errors," so this project sets stratum to empty in `svyset`. First used in [§2.2](#22-design-variables-in-public-use).

### TFN (Total Friendship Nominations)
The W1 In-School Questionnaire asked each student to nominate up to 5 male + 5 female friends from the school roster. Centralities tagged with "TFN" (e.g. `IDGX2` "In-Degree: TFN") are computed on this 10-nomination-cap network. See [§3.1](#31-wave-i-public-use-network-file--pre-computed-sociometric-measures).

---

## Changelog

Reverse-chronological. Only entries that can be verified from the repo / git history or the current session.

- **2026-04-21** — Reviewer-feedback pass (causal-inference PhD student + math/CS undergrad): added §5.6 "Identification assumptions and target estimand" with starred AHPVT confounder-vs-mediator callout and the assumed-DAG / positivity / IPAW narrative; added §6.5 "Causal-screening diagnostic battery (D1–D9)" with formal pass/fail thresholds and plain-language intuition per diagnostic; expanded the §9 weight caveat into an explicit IPAW recipe and added a "how to read D2 under the contaminated NC" callout; added a plain-language [Glossary](#glossary) appendix with anchor links used throughout the reference set. Pitfall #7 (PRXPREST) trimmed — the stale "earlier notes were incorrect" apology is removed now that the root cause is fixed in [scripts/task05_weighted_descriptives.py](../scripts/task05_weighted_descriptives.py) and the regenerated [outputs/05_weighted_descriptives.md](../outputs/05_weighted_descriptives.md).
- **2026-04-21** — §9 rewritten from "Pivot option — cardiometabolic / vascular outcomes" to "Outcome battery: primary + multi-outcome extension" covering the 12 Task 15 outcomes + primary cognition + height NC (14-row outcome table with weight caveat callout). §10 deliverables index extended from task 7 through task 15. §2.5 now points readers to the new [variable_dictionary.md](variable_dictionary.md). This Changelog section added.
- **2026-04-20** — Pitfall #7 (§7) corrected: `PRXPREST` was previously described as a binary 0/1 variable, which contradicted §3.1 line 117 showing the continuous range [0, 0.77]. Corrected to "continuous in public-use" with empirical range / mean / std and an explicit note that earlier binary descriptions were wrong.
- **Earlier** — Initial merged synthesis from v2 feasibility report + documentation report + empirical feasibility summary. See `git log reference/addhealth_synthesis.md` for prior history.

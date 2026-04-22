# Variable dictionary — Inter-Generational Causal Analysis of AddHealth

Lookup for every variable code that appears in this project's analyses, charts, or output files.

This document has two sections:

1. **[Quick reference](#1-quick-reference-alphabetical)** — alphabetical lookup for humans reading plots and briefs. For every code: verbatim codebook label + one-line plain-English gloss of what the variable *measures*.
2. **[Detailed reference](#2-detailed-reference-by-role)** — organised by role in the analysis (design, weights, exposures, outcomes, covariates, negative control, derivations). Includes N, kind, findings, caveats, uncertainties, and links into [research_journal.md](research_journal.md).

For wave-level design context and sampling-frame discussion, see [addhealth_synthesis.md](addhealth_synthesis.md).

---

## 1. Quick reference (alphabetical)

Conventions: labels in quotes are quoted verbatim from the shipped SAS/XPT files (ICPSR 21600 v26). `[derived]` = constructed in this repo. "TFN" = Total Friendship Nominations (up to 5 male + 5 female per respondent on the W1 In-School roster).

| Code | Wave | Label | What it measures |
|---|:-:|---|---|
| `AH_PVT` | W1 | "ADD HEALTH PICTURE VOCABULARY TEST SCORE" | Age-standardized receptive-vocabulary score (≈ verbal IQ, mean 100 / SD 15); respondent hears a word and picks 1 of 4 pictures that matches. |
| `AH_RAW` | W1 | "RAW PICTURE VOCABULARY TEST SCORE" | Un-standardized count of correct PVT items (0–87); preferred over `AH_PVT` in this project because it has less missingness. |
| `AID` | W1–W6 | "RESPONDENT IDENTIFIER" | Respondent ID; links records across waves. Public-use IDs only — no friend, sibling, or partner linkage. |
| `BCENT10X` | W1 | "Bonacich Centrality P=.1" | Eigenvector-style centrality weighted by how central your friends are, with decay β = 0.1; "centrality by association". |
| `BFFRECIP` | W1 | "Best Female Frnd Recip.(any)" | Binary: is the best-female-friend nomination reciprocated? (NA if that friend isn't in the sample — ~64 % missing.) |
| `BIO_SEX` | W1 | "BIOLOGICAL SEX-W1" | Sex at W1: 1 = male, 2 = female. |
| `BMFRECIP` | W1 | "Best Male Frnd Recip (any)" | Binary reciprocity flag for the best-male-friend nomination; ~70 % missing for the in-sample-friend reason. |
| `C4NUMSCR` | W4 | "TOTAL SCORE ON NUMBER RECALL TASK-W4" | Backward digit span: longest digit string (2–8 digits) the respondent repeated in reverse order. Range 0–7. |
| `C4WD60_1` | W4 | "S14 # WORDS ON LIST RECALLED 60 SEC-W4" | Delayed word recall: # of 15 words recalled in 60 s after a 1–2 min distractor. |
| `C4WD90_1` | W4 | "S14 # WORDS ON LIST RECALLED 90 SEC-W4" | Immediate word recall: # of 15 read-aloud nouns recalled in 90 s. |
| `CESD_SUM` | `[derived]` | `[derived]` | W1 depressive-symptoms scale: sum of 19 CES-D Likert items (0–57), items {4, 8, 11, 15} reverse-scored. |
| `CLUSTER2` | W1–W6 | "SAMPLE CLUSTER" | School-pair primary sampling unit (132 PSUs). Used as the clustering variable for cluster-robust standard errors. |
| `ERDEN` | W1 | "Density: Ego Receive Net" | Among people who nominated the respondent as a friend, how connected are those nominators to each other (0 = disjoint, 1 = clique). |
| `ESDEN` | W1 | "Density: Ego Send Net" | Among the friends the respondent nominated, how connected are those nominees to each other. |
| `ESRDEN` | W1 | "Density: Ego Send & Receive Net" | Density of the union (sent ∪ received nominations) ego network. |
| `FR_FLAG` | W1 | "NUMBER OF FRIENDS ASKED TO NOMINATE-W1" | Design flag: how many friend-nomination slots the respondent was offered at W1. |
| `FRIEND_CONTACT_SUM` | `[derived]` | `[derived]` | Sum of past-7-day interaction flags (Section-20 items 6–10: house visits, after-school meets, weekend time, phone calls, problem talks) across all nominated friends. |
| `FRIEND_DISCLOSURE_ANY` | `[derived]` | `[derived]` | Binary: did the respondent say they "talked about a problem" (item 9) with *any* of their 10 nominated friends? |
| `FRIEND_N_NOMINEES` | `[derived]` | `[derived]` | Number of friend slots (0–10) the respondent filled in the W1 in-home Section-20 nomination grid. |
| `GSW5` | W5 | "CROSS-SECTION WGT WV ALL SP" | W5 cross-sectional sample weight; drops to N ≈ 824 once intersected with mode-restricted cognitive data. |
| `GSW6` | W6 | "WAVE 6 PUF CROSSSECTIONAL OPTIMIZED WEIGHT" | W6 cross-sectional weight (not used in this project — W6 cognitive battery is restricted-use). |
| `GSW12345` | W5 | "LONGTDNL WGT WI-II-III-IV-V ALL SP" | Five-wave longitudinal weight; restricts to Grades 7–11 because W2 dropped seniors. |
| `GSW145` | W5 | "LONGTDNL WGT WI-IV-V ALL SP" | W1 → W4 → W5 longitudinal weight; retains Grades 7–12. |
| `GSW1345` | W5 | "LONGTDNL WGT WI-III-IV-V ALL SP" | W1 → W3 → W4 → W5 longitudinal weight. |
| `GSWGT1` | W1 | "GRAND SAMPLE WEIGHT-W1" | W1 cross-sectional weight. |
| `GSWGT4` | W4 | "POSTSTRAT GS LONGIT WGT-PUBLIC-W4" | W4 longitudinal (W1 → W4) post-stratified weight. |
| `GSWGT4_2` | W4 | "POSTSTRAT GS CROSS_SECT WGT-PUBLIC-W4" | **Primary weight for this project.** W4 cross-sectional weight; used for all task 10–15 fits. |
| `H1DA7` | W1 | "S2Q7 HANG OUT WITH FRIENDS-W1" | Past-week frequency of hanging out with friends, 0 = not at all → 3 = 5 or more times. |
| `H1ED19` | W1 | "S5Q19 FEEL CLOSE TO PEOPLE AT SCHOOL-W1" | Likert 1–5 (higher = stronger agreement) with "you feel close to people at your school". |
| `H1ED20` | W1 | "S5Q20 FEEL PART OF YOUR SCHOOL-W1" | Likert 1–5 with "you feel like you are part of your school". |
| `H1ED21` | W1 | "S5Q21 STUDENTS AT SCHOOL PREJUDICED-W1" | Likert 1–5 with "students at your school are prejudiced"; reverse-scored in `SCHOOL_BELONG`. |
| `H1ED22` | W1 | "S5Q22 HAPPY AT YOUR SCHOOL-W1" | Likert 1–5 with "you are happy to be at your school". |
| `H1ED23` | W1 | "S5Q23 TEACHERS TREAT STUDENTS FAIRLY-W1" | Likert 1–5 with "teachers at your school treat students fairly". |
| `H1ED24` | W1 | "S5Q24 FEEL SAFE IN YOUR SCHOOL-W1" | Likert 1–5 with "you feel safe in your school". |
| `H1FS13` | W1 | "S10Q13 FELT LONELY-W1" | CES-D loneliness item: "How often during the past week did you feel lonely?" 0 = never/rarely → 3 = most/all of the time. |
| `H1FS14` | W1 | "S10Q14 PEOPLE UNFRIENDLY TO YOU-W1" | CES-D unfriendliness item: "People were unfriendly to you." Scale 0–3 as above. |
| `H1GH1` | W1 | "S1Q1 GENL HLTH-W1" | W1 self-rated health, 1 = excellent → 5 = poor. |
| `H1GI4` | W1 | "S1Q4 ARE YOU OF HISPANIC ORIGIN-W1" | Hispanic-ethnicity indicator. |
| `H1GI6A` | W1 | "S1Q6A RACE-WHITE-W1" | Race flag: respondent identified as White. |
| `H1GI6B` | W1 | "S1Q6B RACE-AFRICAN AMERICAN-W1" | Race flag: respondent identified as Black/African American. |
| `H1PR4` | W1 | "S35Q4 FRIENDS CARE ABOUT YOU-W1" | "How much do you feel your friends care about you?" 1 = not at all → 5 = very much. |
| `H1RF1` | W1 | "S15Q1 RES DAD-EDUCATION LEVEL-W1" | Teen-reported resident father's education (11-point scale); 30 % skip because father is absent from household. |
| `H1RM1` | W1 | "S14Q1 RES MOM-EDUCATION LEVEL-W1" | Teen-reported resident mother's education (11-point scale). |
| `H4BMI` | W4 | "S27 BMI—W4" | Body mass index measured at W4 in-home visit (kg / m²); interviewer-taken weight and height, not self-report. |
| `H4BMICLS` | W4 | "S27 BMI CLASS—W4" | CDC weight category from `H4BMI`: 1 = underweight, 2 = normal, 3 = overweight, 4 = obese I, 5 = obese II, 6 = morbidly obese. |
| `H4DBP` | W4 | "S27 DIASTOLIC BLOOD PRESSURE—W4" | Diastolic BP (mmHg, "bottom number"), measured at W4 visit. |
| `H4SBP` | W4 | "S27 SYSTOLIC BLOOD PRESSURE—W4" | Systolic BP (mmHg, "top number"), measured at W4 visit. |
| `H4WAIST` | W4 | "S27 MEASURED WAIST (CM)—W4" | Waist circumference in cm, tape-measured at W4. |
| `H5EC1` | W5 | "S4Q1 INCOME PERS EARNINGS [W4–W5]—W5" | Personal earnings over the W4 → W5 period, bracketed 1–13: 1 = <$5k, 7 ≈ $40–50k, 13 = $250k+. Not raw dollars. |
| `H5ID1` | W5 | "S5Q1 HOW IS GEN PHYSICAL HEALTH—W5" | Self-rated physical health, 1 = excellent → 5 = poor (higher = worse). |
| `H5ID4` | W5 | "S5Q4 LIMIT CLIMB SEV. FLIGHT STAIRS—W5" | Functional limitation: "Does your health now limit you in climbing several flights of stairs?" 1 = not at all → 3 = limited a lot. |
| `H5ID16` | W5 | "S5Q16 HOW OFTEN TROUBLE SLEEPING—W5" | Frequency of trouble sleeping in the past four weeks, 0 = never → 4 = every night. |
| `H5LM5` | W5 | "S3Q5 CURRENTLY WORK—W5" | Labor-market status: 1 = currently working for pay, 2 = not working but temporarily absent from a job, 3 = not employed. Three-level — **not** binary. |
| `H5MN1` | W5 | "S13Q1 LAST MO NO CNTRL IMPORT THINGS—W5" | Perceived Stress Scale item: "In the last month, how often felt unable to control the important things in your life?" 1 = never → 5 = very often. |
| `H5MN2` | W5 | "S13Q2 LAST MO CONFID HANDLE PERS PBMS—W5" | PSS item: "…how often felt confident about handling personal problems?" 1 = never → 5 = very often. Direction is reverse of `H5MN1` (higher = better coping). |
| `HAVEBFF` | W1 | "R has a best Female friend" | Binary: respondent identified at least one best female friend. |
| `HAVEBMF` | W1 | "R has a Best Male Friend" | Binary: respondent identified at least one best male friend. |
| `HEIGHT_IN` | `[derived]` | `[derived]` | W4 measured height in inches (`feet × 12 + inches`); used as the negative-control outcome in task 14 D2. |
| `IDG_LEQ1` | `[derived]` | `[derived]` | Binary isolation flag: 1 if the respondent was nominated as a friend by ≤ 1 classmate (`IDGX2 ≤ 1`). |
| `IDG_ZERO` | `[derived]` | `[derived]` | Binary isolation flag: 1 if no classmate nominated the respondent as a friend (`IDGX2 == 0`). |
| `IDGX2` | W1 | "In-Degree: TFN" | Incoming friendship nominations: how many classmates named this respondent as a friend on the In-School roster (0–30). Reads as peer-conferred status / popularity. |
| `IGDMEAN` | W1 | "mean dist to reachable alters" | Average shortest-path distance (in friendship hops) from the respondent to every reachable peer in the school network. Larger = more peripheral. |
| `INFLDMN` | W1 | "Influence Domain" | Count of classmates from whom the respondent is reachable via any number of hops (mirror of `REACH`). |
| `MODE` | W5 | "SURVEY MODE" | W5 interview mode: W = web, I = in-person, T = telephone, M = mail, S = Spanish CAPI. Cognitive items administered only in modes I + T. |
| `MODEOK5` | `[derived]` | `[derived]` | Binary flag: 1 if the W5 interview was in a cognitive-eligible mode (I or T), else 0. |
| `ODGX2` | W1 | "Out-Degree: TFN" | Outgoing friendship nominations: how many classmates this respondent named as a friend (0–10; up to 5 male + 5 female slots). Reads as self-reported sociability. |
| `PARENT_ED` | `[derived]` | `[derived]` | Max of teen-reported mother and father education, collapsed to an ordinal 0–6 scale. |
| `PRXPREST` | W1 | "Proximity Prestige" | Wasserman–Faust prestige: (fraction of school that can reach you) ÷ (mean distance to those reachers). Continuous in [0, 0.77]; higher = more prestigious. |
| `RACE` | `[derived]` | `[derived]` | 4-level: NH-White (reference), NH-Black, Hispanic, Other. Built from `H1GI4` + `H1GI6A`/`H1GI6B`; multi-racial respondents collapsed under an explicit hierarchy. |
| `RCHDEN` | W1 | "Density at maximum Reach" | Density of the respondent's full reachable subgraph — how interconnected is the set of classmates they can reach at any distance. |
| `REACH` | W1 | "N reachable alters: TFN" | Total classmates reachable via any number of friendship hops (0–1,791). Unbounded; tracks school size. |
| `REACH3` | W1 | "N reachable alters 3 steps: TFN" | Classmates reachable within ≤ 3 friendship hops. More local than `REACH`. |
| `SCHOOL_BELONG` | `[derived]` | `[derived]` | Sum of 6 W1 Section-5 Likert items (`H1ED19`–`H1ED24`, with `H1ED21` reverse-scored). Higher = stronger sense of belonging at school. |
| `W4_COG_COMP` | `[derived]` | `[derived]` | Primary cognitive outcome: mean of individually z-scored `C4WD90_1` + `C4WD60_1` + `C4NUMSCR`. |

---

## 2. Detailed reference (by role)

Everything below is organised by the variable's role in the analysis, not by wave. Each subsection adds **N**, **kind**, **findings from this project's screens**, and **caveats / uncertainties** on top of the quick-ref gloss. Cross-references into [research_journal.md](research_journal.md) point to the phase where the variable's behaviour was investigated.

**How to read the N column.** For exposures and outcomes this is the effective N in the task 14 / task 15 analytic frame (already network-gated or mode-gated, reserve codes stripped via [scripts/analysis_utils.py](../scripts/analysis_utils.py) `VALID_RANGES`). For raw codebook variables it's the shipped non-missing N.

**Diagnostic codes** (used throughout; full definitions in [research_journal.md §Phase 4](research_journal.md#phase-4--preliminary-causal-screening-d1d9)):
- **D1** baseline significance at the primary spec (L0+L1+AHPVT)
- **D2** height negative-control outcome (contaminated — see [§7](#7-negative-control-outcome))
- **D3** sibling-dissociation specificity check
- **D4** adjustment-set stability (β drift across L0 / L0+L1 / L0+L1+AHPVT)
- **D5** outcome-component consistency (across the 3 W4 cognitive tests)
- **D6** dose-response monotonicity (continuous only)
- **D7** positivity / overlap
- **D8** saturated-school selection penalty (informational)
- **D9** collider / double-adjustment red flags (hardcoded)

---

### 2.1. Design variables

| Code | Label | Wave | N | Kind | Caveats |
|---|---|:-:|---:|---|---|
| `AID` | "RESPONDENT IDENTIFIER" | W1–W6 | 6,504 (W1 base) | string | Public-use IDs. No mapping to friend / sibling / partner IDs. |
| `CLUSTER2` | "SAMPLE CLUSTER" | W1–W6 | 132 PSUs | categorical | Always `svyset CLUSTER2` with replacement. Stratum is not in public-use. See [addhealth_synthesis.md §2.2](addhealth_synthesis.md#22-design-variables-in-public-use). |
| `MODE` | "SURVEY MODE" | W5 | 4,196 | categorical (W/I/T/M/S) | Cognitive items only administered in modes I + T; other modes get reserve code 95/995/9995 ("not asked"). |
| `MODEOK5` | mode-restricted flag | `[derived]` | 3,553 | binary | Derived in [scripts/task03de_wave5_cognitive.py](../scripts/task03de_wave5_cognitive.py). Gates `W4_COG_COMP` construction. |
| `FR_FLAG` | "NUMBER OF FRIENDS ASKED TO NOMINATE-W1" | W1 | ~6,500 | ordinal | Used in task 11 sensitivity checks on the friendship grid. |

---

### 2.2. Sampling weights

| Code | Label | Wave | N | Used in this project | Caveats |
|---|---|:-:|---:|---|---|
| `GSWGT4_2` | "POSTSTRAT GS CROSS_SECT WGT-PUBLIC-W4" | W4 | 5,114 | **Primary weight** for tasks 10–15. All D1 baselines, D4 adjustment-stability fits, and the task 15 multi-outcome screen use this weight. | For W5 outcomes this is a screening-only approximation; formal estimation should switch to `GSW5` + IPAW for W4 → W5 attrition. |
| `GSW5` | "CROSS-SECTION WGT WV ALL SP" | W5 | 4,196 (824 in the mode-restricted cognitive cell) | Held in reserve for task 16. | Mode-restriction cost is severe once W5 cognition is required. |
| `GSW145` / `GSW1345` | "LONGTDNL WGT WI-IV-V" / "… WI-III-IV-V" | W5 | 3,713 / 3,147 | Recommended for any longitudinal W1 → W4 → W5 claim after the screen. | Corrects partially for observed-cause attrition. |
| `GSWGT1`, `GSWGT4`, `GSW12345`, `GSW6`, … | see [addhealth_synthesis.md §2.3](addhealth_synthesis.md#23-weight-variables-public-use-empirically-verified) | W1 / W4 / W5 / W6 | various | Not used in this project's outputs; listed in the synthesis for completeness. |

---

### 2.3. Exposures (24 total)

All exposures are W1 measurements. 16 come from the W1 Public-Use Network File (`w1network.sas7bdat`); 8 come from the W1 In-Home Questionnaire or derived constructs. Structure and rationale in [addhealth_synthesis.md §3](addhealth_synthesis.md#3-primary-exposure-adolescent-friendship--social-connection).

Exposure-level findings from the task 14 primary screen are summarised in [outputs/14_screening.md](../outputs/14_screening.md) and the task 15 cross-outcome pattern in [outputs/15_multi_outcome.md](../outputs/15_multi_outcome.md); see [research_journal.md §Phase 4](research_journal.md#phase-4--preliminary-causal-screening-d1d9) and [§Phase 5](research_journal.md#phase-5--multi-outcome-screening-pivot) for narrative context.

#### 2.3.1 Peer-network centrality (8)

All require the respondent to be in a saturated school (≥ 75 % roster participation), which costs ~32 % of W1 respondents.

| Code | Wave | N (task 14) | Kind | Findings | Caveats & uncertainties |
|---|:-:|---:|---|---|---|
| `IDGX2` | W1 | 3,268 | continuous (0–30) | D1 PASS on cognition (β shrinks sharply after L0+L1+AHPVT); **cross-outcome robust** on 7 non-cognitive outcomes in task 15 (BMI, waist, BMICLS, H5ID1, H5ID4, H5LM5, H5EC1). D2 height-NC fails. | Top Task-16 handoff candidate for H4WAIST / H4BMI / H4BMICLS. D2 fail is not conclusive because the height NC is contaminated (see [§2.7](#27-negative-control-outcome)). |
| `ODGX2` | W1 | 3,268 | continuous (0–10) | Largest stable β on cognition post-AHPVT; D3 sibling for `IDGX2` / `BCENT10X`. Hands off to H5EC1 for task 16. | Reads as self-reported sociability (you name up to 10 peers), distinct from peer-conferred status (`IDGX2`). |
| `BCENT10X` | W1 | 3,268 | continuous (0–4.29) | Highest raw β on cognition but D4 rel-shift ≈ 39 % — the exposure most attenuated by AHPVT adjustment. | Makes AHPVT-as-confounder-vs-mediator ambiguity most consequential here. |
| `REACH` | W1 | 3,268 | continuous (0–1,791) | D1 FAIL on cognition (p = 0.48); activates on `H5MN1` and `H5LM5` in task 15. | Tracks school size closely, limiting within-school variance. |
| `REACH3` | W1 | 3,268 | continuous (0–264) | D1 PASS on cognition and H5EC1 in task 15. | More local than `REACH`; less school-size confounded. |
| `INFLDMN` | W1 | 3,268 | continuous (0–1,705) | D1 FAIL on cognition (p = 0.70). Near-duplicate of `REACH`. | Redundant with `REACH` — keep only one in any formal model. |
| `PRXPREST` | W1 | 3,006 | continuous (0.00045–0.774) | D1 PASS on cognition after re-tag; re-categorised as Weakened (score 4). Strong on `H4WAIST`, `H4BMI`. | Earlier miscoding as binary (fixed 2026-04-20) logged in [research_journal.md §Phase 4.5](research_journal.md#phase-45--adversarial-review-of-the-screen). |
| `IGDMEAN` | W1 | 2,783 | continuous (1.00–21.39) | Mixed — inverse of prestige. | Higher missingness than other centralities; interpret with care. |

#### 2.3.2 Isolation (4)

| Code | Wave | N | Kind | Findings | Caveats |
|---|:-:|---:|---|---|---|
| `IDG_ZERO` | `[derived]` | 3,268 | binary | PASS on H4BMI / H4WAIST / H4BMICLS / H5MN2 in task 15. | `= (IDGX2 == 0)`. Derivation: [task08_build_analytic_frame.py:88](../scripts/task08_build_analytic_frame.py#L88). |
| `IDG_LEQ1` | `[derived]` | 3,268 | binary | PASS on H4BMI / H4WAIST / H4BMICLS / H5ID4. | `= (IDGX2 <= 1)`. Derivation: [task08_build_analytic_frame.py:90](../scripts/task08_build_analytic_frame.py#L90). |
| `HAVEBMF` | W1 | 3,268 | binary | D3 sibling for `HAVEBFF`. | Network-file flag. |
| `HAVEBFF` | W1 | 3,268 | binary | D3 sibling for `HAVEBMF`. | |

#### 2.3.3 Ego-network density (4)

Wasserman–Faust density definitions. All require network frame.

| Code | Wave | N | Kind | Caveats |
|---|:-:|---:|---|---|
| `ESDEN` | W1 | 2,783 | continuous (0–1) | Density of the send-net only (what the respondent nominated). |
| `ERDEN` | W1 | 3,006 | continuous (0–1) | Density of the receive-net only (who nominated the respondent). |
| `ESRDEN` | W1 | 3,167 | continuous (0–1) | Union of sends + receives. |
| `RCHDEN` | W1 | 3,268 | continuous (0.16–0.96) | Most fully populated of the 4 density vars; best task-15 coverage. |

#### 2.3.4 Friendship grid derived (3)

From the W1 Section-20 self-reported 10-friend nomination grid (`H1MF*`/`H1FF*`). Not network-gated — larger N than centrality variables. Derivation: [scripts/analysis_utils.py:428](../scripts/analysis_utils.py#L428) (`derive_friendship_grid`).

| Code | Wave | N | Kind | Caveats |
|---|:-:|---:|---|---|
| `FRIEND_N_NOMINEES` | `[derived]` | 4,710 | continuous (0–10) | Count across male + female slots. D3 sibling pair with `FRIEND_DISCLOSURE_ANY`. |
| `FRIEND_CONTACT_SUM` | `[derived]` | 4,710 | continuous | Weekly-contact aggregate across all nominated slots. |
| `FRIEND_DISCLOSURE_ANY` | `[derived]` | 4,710 | binary | "Any friend with whom R talked about a problem (item 9)". |

#### 2.3.5 Belonging (1)

| Code | Wave | N | Kind | Findings | Caveats |
|---|:-:|---:|---|---|---|
| `SCHOOL_BELONG` | `[derived]` | 4,629 | continuous (6–30) | **Dominates mental-health and functional outcomes in task 15** (H5MN1, H5MN2, H5ID1, H5ID4, H5ID16). | **D9 red flag**: mixes individual disposition with school-level context; possible collider given W1 `CESD_SUM` / `H1GH1`. Fails D4 on several of its activations → mediator leakage suspected. Derivation: [scripts/analysis_utils.py:304](../scripts/analysis_utils.py#L304). |

#### 2.3.6 Loneliness (2)

Both items are D9 red-flagged because they are components of the `CESD_SUM` L1 covariate — using them as exposure while adjusting for `CESD_SUM` double-adjusts.

| Code | Wave | N | Kind | Caveats |
|---|:-:|---:|---|---|
| `H1FS13` | W1 | 4,710 | ordinal 0–3 | D9: contained in `CESD_SUM`. |
| `H1FS14` | W1 | 4,710 | ordinal 0–3 | D9: contained in `CESD_SUM`. |

#### 2.3.7 Qualitative (2)

| Code | Wave | N | Kind | Caveats |
|---|:-:|---:|---|---|
| `H1DA7` | W1 | 4,710 | ordinal 0–3 | Plausible low-specificity exposure; D1 PASS on `H4SBP`. |
| `H1PR4` | W1 | 4,697 | ordinal 1–5 | Protective-factors section. Not in the cache by default; task 14 re-attaches from `w1inhome.parquet`. |

---

### 2.4. Primary outcome — W4 cognition

| Code | Label | Wave | N | Kind | Findings | Caveats |
|---|---|:-:|---:|---|---|---|
| `W4_COG_COMP` | `[derived]` | W4 | 3,238 (primary frame) | continuous (z-scored) | Used as `y` in every task 10–14 analysis and as the "cognitive" outcome in task 15 (mid-pack at 5/24 significant exposures). | Every exposure fails D4 adjustment stability, with AHPVT contributing most of the drift. See [research_journal.md §Phase 4 main finding](research_journal.md#phase-4--preliminary-causal-screening-d1d9). |
| `C4WD90_1` | "S14 # WORDS ON LIST RECALLED 90 SEC-W4" | W4 | 5,101 | continuous (0–15) | Immediate-recall component. | Protocol in [addhealth_synthesis.md §4.4](addhealth_synthesis.md#44-wave-iv-cognitive-battery-datawaw4w4inhomesas7bdat). |
| `C4WD60_1` | "S14 # WORDS ON LIST RECALLED 60 SEC-W4" | W4 | 5,097 | continuous (0–15) | Delayed-recall component. | |
| `C4NUMSCR` | "TOTAL SCORE ON NUMBER RECALL TASK-W4" | W4 | 5,102 | continuous (0–7) | Backward-digit-span component. | |

---

### 2.5. Secondary outcomes — task 15 multi-outcome extension (12)

Added in task 15 to test whether the social-exposure signal is cognition-specific or broader. Loaded via [scripts/analysis_utils.py:91](../scripts/analysis_utils.py#L91) (`load_outcome`) with reserve-code stripping. See [addhealth_synthesis.md §9](addhealth_synthesis.md#9-outcome-battery-primary--multi-outcome-extension) for the full outcome-battery table and [research_journal.md §Phase 5](research_journal.md#phase-5--multi-outcome-screening-pivot) for narrative.

#### 2.5.1 Cardiometabolic (5)

| Code | Label | Wave | Kind | Findings (p<0.05 exposures / 24) | Caveats |
|---|---|:-:|---|:-:|---|
| `H4BMI` | "S27 BMI—W4" | W4 | continuous (10–80) | 6 | Measured (not self-report). Task-16 handoff pair with `IDGX2` (β = −0.20, D4 rel-shift 21 %). |
| `H4SBP` | "S27 SYSTOLIC BLOOD PRESSURE—W4" | W4 | continuous (50–250) | 2 | Anti-hypertensive medication unadjusted in the screen — Task 16 should bring in `H4TO*` medication flags. |
| `H4DBP` | "S27 DIASTOLIC BLOOD PRESSURE—W4" | W4 | continuous (30–180) | 0 | Null-across-the-board result is itself informative: vascular pressure is not the primary channel. |
| `H4WAIST` | "S27 MEASURED WAIST (CM)—W4" | W4 | continuous (40–200) | 7 | Strongest cardiometabolic signal; task-16 handoff pair with `IDGX2` (β = −0.51, D4 rel-shift 18 %). Highly collinear with `H4BMI` (r ≈ 0.9). |
| `H4BMICLS` | "S27 BMI CLASS—W4" | W4 | ordinal 1–6 | 5 | Treated linearly in the screen; formal estimation should use ordered-logit. Task-16 handoff pair with `IDGX2`. |

#### 2.5.2 Functional + mental health (5)

All W5 outcomes. Median N ≈ 2,400 network-gated, ≈ 3,400 grid-gated. Screen uses `GSWGT4_2` (see uncertainty #3 in [research_journal.md](research_journal.md#outstanding-uncertainties)).

| Code | Label | Wave | Kind | Findings (p<0.05 / 24) | Caveats |
|---|---|:-:|---|:-:|---|
| `H5ID1` | "S5Q1 HOW IS GEN PHYSICAL HEALTH—W5" | W5 | likert 1–5 (higher = worse) | 11 | Second-broadest signal in task 15. |
| `H5ID4` | "S5Q4 LIMIT CLIMB SEV. FLIGHT STAIRS—W5" | W5 | ordinal 1–3 | 8 | Functional-limitation item; floor effect at younger ages. |
| `H5ID16` | "S5Q16 HOW OFTEN TROUBLE SLEEPING—W5" | W5 | ordinal 0–4 | 2 | |
| `H5MN1` | "S13Q1 LAST MO NO CNTRL IMPORT THINGS—W5" | W5 | likert 1–5 | 3 | Perceived Stress Scale item (CASI-administered). |
| `H5MN2` | "S13Q2 LAST MO CONFID HANDLE PERS PBMS—W5" | W5 | likert 1–5 | 3 | PSS item in reverse direction from `H5MN1` (higher = better coping). |

#### 2.5.3 Socioeconomic (2)

| Code | Label | Wave | Kind | Findings (p<0.05 / 24) | Caveats |
|---|---|:-:|---|:-:|---|
| `H5LM5` | "S3Q5 CURRENTLY WORK—W5" | W5 | ordinal 1–3 | 5 | Three-level (yes / temp-absent / not-employed); task 16 should recode before logistic estimation. |
| `H5EC1` | "S4Q1 INCOME PERS EARNINGS [W4–W5]—W5" | W5 | bracketed 1–13 | 12 | **Broadest signal of any outcome.** Bracketed dollars, not raw income — treat as ordinal in formal estimation. Task-16 handoff pair with `ODGX2` (β = +0.10 on the bracket scale). |

---

### 2.6. Covariates — three-tier adjustment sets

Defined in [scripts/task14_causal_screening.py:128–169](../scripts/task14_causal_screening.py#L128). The screen runs nested L0 → L0+L1 → L0+L1+AHPVT to measure D4 adjustment-set stability.

#### 2.6.1 L0 — demographics

| Code | Label | Wave | N | Kind | Caveats |
|---|---|:-:|---:|---|---|
| `BIO_SEX` | "BIOLOGICAL SEX-W1" | W1 | 6,503 | binary (1=M, 2=F) | Encoded as `male = (BIO_SEX == 1)` in the fits. |
| `RACE` | `[derived]` | W1 | 4-level | categorical | Built from `H1GI4` + `H1GI6A` / `H1GI6B`. Multi-racial respondents collapsed. Derivation: [analysis_utils.py:321](../scripts/analysis_utils.py#L321). |
| `PARENT_ED` | `[derived]` | W1 | ~5,900 | ordinal 0–6 | Max of teen-reported mother and father education, collapsed. Derivation: [analysis_utils.py:334](../scripts/analysis_utils.py#L334). |

Raw feeds for the derivations:

| Code | Label | Wave | N | Caveats |
|---|---|:-:|---:|---|
| `H1GI4` | "S1Q4 ARE YOU OF HISPANIC ORIGIN-W1" | W1 | 6,481 | |
| `H1GI6A` | "S1Q6A RACE-WHITE-W1" | W1 | 6,485 | |
| `H1GI6B` | "S1Q6B RACE-AFRICAN AMERICAN-W1" | W1 | 6,485 | |
| `H1RM1` | "S14Q1 RES MOM-EDUCATION LEVEL-W1" | W1 | 6,077 | 11-point scale + reserves. |
| `H1RF1` | "S15Q1 RES DAD-EDUCATION LEVEL-W1" | W1 | 4,494 | 30 % skip (absent father). |

#### 2.6.2 L1 — W1 mental + health state

Adds CES-D sum and self-rated health to L0.

| Code | Label | Wave | N | Kind | Caveats |
|---|---|:-:|---:|---|---|
| `CESD_SUM` | `[derived]` | W1 | ~6,300 | continuous (0–57) | Sum of 19 CES-D items with {4, 8, 11, 15} reverse-scored. Derivation: [analysis_utils.py:255](../scripts/analysis_utils.py#L255). `H1FS13` / `H1FS14` are components — using them as exposure triggers D9 double-adjustment. |
| `H1GH1` | "S1Q1 GENL HLTH-W1" (self-rated health) | W1 | 6,490 | likert 1–5 | Used as-is. |

#### 2.6.3 L0+L1+AHPVT — baseline cognition

| Code | Label | Wave | N | Kind | Caveats |
|---|---|:-:|---:|---|---|
| `AH_RAW` | "RAW PICTURE VOCABULARY TEST SCORE" | W1 | 6,223 | continuous (0–87) | **Preferred** over `AH_PVT` (~4 % missing vs. ~15 %). |
| `AH_PVT` | "ADD HEALTH PICTURE VOCABULARY TEST SCORE" | W1 | 5,503 | continuous (mean ≈ 101, SD 15) | Standardised but ~15 % missing. |

> ⚠ **Interpretation caveat.** Adjusting for AH_RAW attenuates network-centrality β on `W4_COG_COMP` by 30–50 %. This can mean either (a) AHPVT is a *confounder* (verbal IQ predicts both social integration and adult cognition — the analysis is correct to adjust), **or** (b) AHPVT is a *mediator* of the integration → cognition path (adjustment under-estimates the total effect). D4 measures this drift but cannot distinguish (a) from (b). See [research_journal.md outstanding uncertainty #1](research_journal.md#outstanding-uncertainties) for the planned Task-16 front-door / IV decomposition.

---

### 2.7. Negative-control outcome

| Code | Label | Wave | N | Kind | Caveats |
|---|---|:-:|---:|---|---|
| `HEIGHT_IN` | `[derived]` | W4 | ~5,100 | continuous (56–84 in) | `feet × 12 + inches` from `H4GH5F` / `H4GH5I`. Used in task 14 D2. Derivation: [analysis_utils.py:406](../scripts/analysis_utils.py#L406). |

> ⚠ **Contaminated NC.** Adolescent height is positively correlated with peer popularity in the developmental-psychology literature. D2 failures on `IDGX2` / `BCENT10X` therefore cannot be read as evidence the exposures are non-causal — they may reflect a back-door path through height-mediated peer status. A cleaner NC battery (blood type, age at menarche, hand-dominance, residential stability pre-W1) is queued for Task 16. See [research_journal.md §Phase 4 critique](research_journal.md#phase-4--preliminary-causal-screening-d1d9).

---

### 2.8. Derived / composite cheat-sheet

Where each repo-internal derivation lives.

| Derived code | Function | Source file | Inputs |
|---|---|---|---|
| `W4_COG_COMP` | `derive_w4_cog_composite` | [analysis_utils.py:287](../scripts/analysis_utils.py#L287) | `C4WD90_1`, `C4WD60_1`, `C4NUMSCR` (mode-gated) |
| `W5_COG_COMP` | `derive_w5_cog_composite` | [analysis_utils.py:296](../scripts/analysis_utils.py#L296) | `C5WD90_1`, `C5WD60_1`, derived backward-digit-span |
| `CESD_SUM` | `derive_cesd_sum` | [analysis_utils.py:255](../scripts/analysis_utils.py#L255) | `H1FS1`–`H1FS19`, reverse {4, 8, 11, 15} |
| `PARENT_ED` | `derive_parent_ed` | [analysis_utils.py:334](../scripts/analysis_utils.py#L334) | `H1RM1`, `H1RF1` (max, collapsed 0–6) |
| `RACE` | `derive_race_ethnicity` | [analysis_utils.py:321](../scripts/analysis_utils.py#L321) | `H1GI4`, `H1GI6A`, `H1GI6B` |
| `SCHOOL_BELONG` | `derive_school_belonging` | [analysis_utils.py:304](../scripts/analysis_utils.py#L304) | `H1ED19`–`H1ED24` (reverse-score `H1ED21`) |
| `FRIEND_N_NOMINEES`, `FRIEND_CONTACT_SUM`, `FRIEND_DISCLOSURE_ANY` | `derive_friendship_grid` | [analysis_utils.py:428](../scripts/analysis_utils.py#L428) | `H1MF*` / `H1FF*` 45-column grids (items 2, 6, 7, 8, 9, 10) |
| `IDG_ZERO`, `IDG_LEQ1` | inline | [task08_build_analytic_frame.py:88](../scripts/task08_build_analytic_frame.py#L88) | `IDGX2` |
| `HEIGHT_IN` | `neg_control_outcome` | [analysis_utils.py:406](../scripts/analysis_utils.py#L406) | W4 `H4GH5F` (feet), `H4GH5I` (inches) |

---

## Changelog

- **2026-04-21** — Split into quick-ref (alphabetical, plain-English "what it measures") + detailed reference (by role, with findings / caveats / journal cross-refs).
- **2026-04-21** — Initial version. Covers all variables referenced in tasks 01–15.

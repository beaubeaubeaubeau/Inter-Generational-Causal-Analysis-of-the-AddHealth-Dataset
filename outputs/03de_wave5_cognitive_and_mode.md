# Task 3 (d)(e): Wave V Cognitive Variables and Mode Stratification

Source: `data/W5/pwave5.xpt` (ICPSR 21600 v26, public-use).
Rows x Cols: 4,196 x 789

## 1. Mode-of-interview variable

**Variable:** `MODE`  
**Label:** SURVEY MODE

**Value labels:**

| Value | Label |
|-------|-------|
| W | Web (self-administered online) |
| I | In-person (CAPI) |
| T | Telephone (CATI) |
| M | Mail (paper self-administered) |
| S | Spanish CAPI / other |

**Frequency table:**

| Value | Label | N | % |
|-------|-------|---|---|
| W | Web (self-administered online) | 3221 | 76.8% |
| I | In-person (CAPI) | 723 | 17.2% |
| M | Mail (paper self-administered) | 147 | 3.5% |
| T | Telephone (CATI) | 101 | 2.4% |
| S | Spanish CAPI / other | 4 | 0.1% |

### Other mode-related candidates considered

| Variable | Label |
|----------|-------|
| `MODE` | SURVEY MODE |
| `SAMPLE` | SAMPLE ASSIGNMENT |
| `PLATFORM` | PLATFORM/DEVICE USED BY WEB RESP-W5 |
| `H5OD10` | S1Q10 CURR/ATTENDING COL/UNIV/VOC SCH-W5 |
| `H5OD11` | S1Q11 HIGHEST EDU ACHIEVED TO DATE-W5 |
| `H5HR3` | S2Q3 HOW MANY PEOPLE RESP LIVES WITH-W5 |
| `H5EC4` | S4Q4 SINCE 08 HOW MUCH MONEY RECVD-W5 |
| `H5ID1` | S5Q1 HOW IS GEN PHYSICAL HEALTH-W5 |
| `H5ID14` | S5Q14 LOCATION HEALTH CARE FACILITY-W5 |
| `H5ID16` | S5Q16 HOW OFTEN TROUBLE SLEEPING-W5 |
| `H5EL5` | S8Q5 HOW WAS HEALTH B/F AGE 16-W5 |
| `H5SS8` | S10Q8 HOW OFTEN USUALLY VOTE-W5 |
| `H5WP14` | S11Q14 HOW CLOSE TO MOM FIG-W5 |
| `H5WP28` | S11Q28 HOW CLOSE TO DAD FIG-W5 |
| `H5RE3` | S12Q3 HOW IMPORT RELIG FAITH-W5 |
| `H5RE4` | S12Q4 HOW OFTEN PRIVATE PRAY-W5 |
| `H5TR10` | S15Q10 HOW MOST RECENT RELAT END-W5 |
| `H5TR15` | S15Q15 R HOW HAPPY IN RELATIONSHIP-W5 |
| `H5PG281` | S16Q281 HOW GOOD HEALTH-KID1-W5 |
| `H5PG282` | S16Q282 HOW GOOD HEALTH-KID2-W5 |
| `H5PG283` | S16Q283 HOW GOOD HEALTH-KID3-W5 |
| `H5PG284` | S16Q284 HOW GOOD HEALTH-KID4-W5 |
| `H5PG285` | S16Q285 HOW GOOD HEALTH-KID5-W5 |
| `H5PG286` | S16Q286 HOW GOOD HEALTH-KID6-W5 |
| `H5DA11` | S17Q11 HOW PROBLEMATIC IS TINNITUS-W5 |
| `H5DA13` | S17Q13 W/CORRECTION HOW IS EYESIGHT-W5 |
| `H5FT1` | S18Q1 HAS A SMARTPHONE-W5 |
| `H5FT2` | S18Q2 TYPE OF SMARTPHONE-W5 |
| `H5FT3` | S18Q3 USE SMARTPHONE FITNESS APPS-W5 |
| `H5FT4I` | S18Q4I TRACKED MEDICATIONS-W5 |
| `H5FT5E` | S18Q5E HOW OFTEN WEAR TRACKER-W5 |

## 2. Cognitive variable search

Searched labels for: ['recall', 'word', 'digit', 'memory', 'span', 'cognitive', 'cognition', 'backward']  
Searched names for: ['RECALL', 'WORD', 'DIGIT', 'SPAN', 'MEM', '^H5MN', 'COG']

### All hits

| Variable | Label |
|----------|-------|
| `H5OD4C` | S1Q4C RACE-HISPANIC-W5 |
| `H5OD5A` | S1Q5A HISPANIC-MEXICAN/CHICANO-W5 |
| `H5OD5B` | S1Q5B HISPANIC-PUERTO RICAN-W5 |
| `H5OD5C` | S1Q5C HISPANIC-CUBAN-W5 |
| `H5OD5D` | S1Q5D HISPANIC-CENTRAL AMERICAN-W5 |
| `H5OD5E` | S1Q5E HISPANIC-SOUTH AMERICAN-W5 |
| `H5OD5F` | S1Q5F HISPANIC-OTHER-W5 |
| `H5MN1` | S13Q1 LAST MO NO CNTRL IMPORT THINGS-W5 |
| `H5MN2` | S13Q2 LAST MO CONFID HANDLE PERS PBMS-W5 |
| `H5MN3` | S13Q3 LAST MO FELT THINGS GO YOUR WAY-W5 |
| `H5MN4` | S13Q4 LAST MO DIFFS OVERWHELM-W5 |
| `H5MN5A` | S13Q5A TREATED LESS COURTSY RESPECT-W5 |
| `H5MN5B` | S13Q5B GET POORER SVS THAN OTHERS-W5 |
| `H5MN5C` | S13Q5C THINK YOU NOT SMART-W5 |
| `H5MN5D` | S13Q5D ACT AFRAID OF YOU-W5 |
| `H5MN5E` | S13Q5E ARE THREATENED HARRASSED-W5 |
| `H5MN6A` | S13Q6A REASON: ANCEST-NAT ORIG-W5 |
| `H5MN6B` | S13Q6B REASON: BIOLOGICAL SEX-W5 |
| `H5MN6C` | S13Q6C REASON: GENDER IDENT-W5 |
| `H5MN6D` | S13Q6D REASON: RACE-W5 |
| `H5MN6E` | S13Q6E REASON: AGE-W5 |
| `H5MN6F` | S13Q6F REASON: RELIGION-W5 |
| `H5MN6G` | S13Q6G REASON: WEIGHT-W5 |
| `H5MN6H` | S13Q6H REASON: PHYS DISABILITY-W5 |
| `H5MN6I` | S13Q6I REASON: PHYS APPEARANCE-W5 |
| `H5MN6J` | S13Q6J REASON: SEXUAL ORIENT-W5 |
| `H5MN6K` | S13Q6K REASON: FIN STATUS-W5 |
| `H5MN6L` | S13Q6L REASON: OTHS ATT/PERSONALITY-W5 |
| `H5MN6M` | S13Q6M REASON: YOUR OCCUPATION-W5 |
| `H5MN6N` | S13Q6N REASON: YOUR ATT/PERSONALITY-W5 |
| `H5MN6O` | S13Q6O SPECIFY OTHER REASON-W5 |
| `H5MN7` | S13Q7 UNFAIR COP STOP SRCH-W5 |
| `H5MN8` | S13Q8 SERIOUSLY THINK SUICIDE PAST YR-W5 |
| `H5MN9` | S13Q9 PAST YEAR TRY SUICIDE-W5 |
| `H5MN10` | S13Q10 SUICIDE ATTEMPT DOCTOR TREAT-W5 |
| `H5MN11` | S13Q11 FAM/FRIEND TRY SUICIDE-W5 |
| `H5MN12` | S13Q12 FAM/FRIEND SUICIDE DEATH-W5; |
| `H5TR13C` | S15Q13_3 PTNR RACE-HISPANIC-W5 |
| `H5MH1` | S19Q1 INTERRUPTD DURING 90 SEC RECALL-W5 |
| `C5WD90_1` | S19 # WORDS ON LIST RECALLED 90 SEC-W5 |
| `C5WD90_2` | S19 # WORDS NOT ON LIST NAMED 90 SEC-W5 |
| `C5WD90_3` | S19 # WORDS REPEATED 90 SEC-W5 |
| `H5MH2` | S19Q2 INTERRUPTD DURNG 60 SEC RECALL-W5 |
| `C5WD60_1` | S19 # WORDS ON LIST RECALLED 60 SEC-W5 |
| `C5WD60_2` | S19 # WORDS NOT ON LIST NAMED 60 SEC-W5 |
| `C5WD60_3` | S19 # WORDS REPEATED 60 SEC-W5 |

### Primary cognitive variables (selected)

| Variable | Label | N non-missing | min | max | mean | median | SD |
|----------|-------|--------------|-----|-----|------|--------|-----|
| `H5MH1` | S19Q1 INTERRUPTD DURING 90 SEC RECALL-W5 | 4196 | 0.00 | 95.00 | 80.81 | 95.00 | 33.86 |
| `C5WD90_1` | S19 # WORDS ON LIST RECALLED 90 SEC-W5 | 4194 | 1.00 | 999.00 | 848.12 | 995.00 | 351.70 |
| `C5WD90_2` | S19 # WORDS NOT ON LIST NAMED 90 SEC-W5 | 4194 | 0.00 | 99.00 | 80.98 | 95.00 | 33.58 |
| `C5WD90_3` | S19 # WORDS REPEATED 90 SEC-W5 | 4194 | 0.00 | 999.00 | 847.32 | 995.00 | 353.62 |
| `H5MH2` | S19Q2 INTERRUPTD DURNG 60 SEC RECALL-W5 | 4196 | 0.00 | 95.00 | 80.81 | 95.00 | 33.87 |
| `C5WD60_1` | S19 # WORDS ON LIST RECALLED 60 SEC-W5 | 4194 | 0.00 | 999.00 | 848.60 | 995.00 | 351.55 |
| `C5WD60_2` | S19 # WORDS NOT ON LIST NAMED 60 SEC-W5 | 4194 | 0.00 | 99.00 | 81.08 | 95.00 | 33.43 |
| `C5WD60_3` | S19 # WORDS REPEATED 60 SEC-W5 | 4194 | 0.00 | 99.00 | 81.01 | 95.00 | 33.60 |
| `H5MH3A` | S19Q3A NUMBER STRING/2-4-W5 | 4194 | 0.00 | 95.00 | 80.99 | 95.00 | 33.48 |
| `H5MH3B` | S19Q3B NUMBER STRING/5-7-W5 | 4194 | 0.00 | 97.00 | 95.25 | 95.00 | 2.20 |
| `H5MH4A` | S19Q4A NUMBER STRING/6-2-9-W5 | 4192 | 0.00 | 97.00 | 81.06 | 95.00 | 33.44 |
| `H5MH4B` | S19Q4B NUMBER STRING/4-1-5-W5 | 4193 | 0.00 | 97.00 | 93.55 | 95.00 | 12.62 |
| `H5MH5A` | S19Q5A NUMBER STRING/3-2-7-9-W5 | 4192 | 0.00 | 97.00 | 81.41 | 95.00 | 33.11 |
| `H5MH5B` | S19Q5B NUMBER STRING/4-9-6-8-W5 | 4193 | 0.00 | 97.00 | 92.40 | 95.00 | 16.20 |
| `H5MH6A` | S19Q6A NUMBER STRING/1-5-2-8-6-W5 | 4192 | 0.00 | 97.00 | 82.94 | 95.00 | 31.60 |
| `H5MH6B` | S19Q6B NUMBER STRING/6-1-8-4-3-W5 | 4193 | 0.00 | 97.00 | 89.22 | 95.00 | 23.03 |
| `H5MH7A` | S19Q7A NUMBER STRING/5-3-9-4-1-8-W5 | 4191 | 0.00 | 97.00 | 86.45 | 95.00 | 27.32 |
| `H5MH7B` | S19Q7B NUMBER STRING/7-2-4-8-5-6-W5 | 4191 | 0.00 | 97.00 | 90.50 | 95.00 | 20.61 |
| `H5MH8A` | S19Q8A NUMBER STRING/8-1-2-9-3-6-5-W5 | 4189 | 0.00 | 97.00 | 89.46 | 95.00 | 22.60 |
| `H5MH8B` | S19Q8B NUMBER STRING/4-7-3-9-1-2-8-W5 | 4189 | 0.00 | 97.00 | 91.46 | 95.00 | 18.53 |
| `H5MH9A` | S19Q9A NUMBER STRING/9-4-3-7-6-2-5-8-W5 | 4188 | 0.00 | 97.00 | 92.18 | 95.00 | 16.80 |
| `H5MH9B` | S19Q9B NUMBER STRING/7-2-8-1-9-6-5-3-W5 | 4156 | 0.00 | 97.00 | 92.88 | 95.00 | 14.80 |

### Frequency tables (reserve codes flagged)

#### `H5MH1` — S19Q1 INTERRUPTD DURING 90 SEC RECALL-W5

N total = 4196, non-missing = 4196, missing (.) = 0

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 613 |  |
| 1.0 | 14 |  |
| 95.0 | 3569 | YES |

#### `C5WD90_1` — S19 # WORDS ON LIST RECALLED 90 SEC-W5

N total = 4196, non-missing = 4194, missing (.) = 2

| Value | Count | Reserve? |
|-------|-------|----------|
| 1.0 | 2 |  |
| 2.0 | 10 |  |
| 3.0 | 44 |  |
| 4.0 | 71 |  |
| 5.0 | 111 |  |
| 6.0 | 131 |  |
| 7.0 | 101 |  |
| 8.0 | 83 |  |
| 9.0 | 29 |  |
| 10.0 | 17 |  |
| 11.0 | 13 |  |
| 12.0 | 8 |  |
| 13.0 | 1 |  |
| 14.0 | 1 |  |
| 15.0 | 1 |  |
| 995.0 | 3569 | YES |
| 996.0 | 1 | YES |
| 999.0 | 1 | YES |
| MISSING (.) | 2 |  |

#### `C5WD90_2` — S19 # WORDS NOT ON LIST NAMED 90 SEC-W5

N total = 4196, non-missing = 4194, missing (.) = 2

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 377 |  |
| 1.0 | 172 |  |
| 2.0 | 44 |  |
| 3.0 | 16 |  |
| 4.0 | 7 |  |
| 5.0 | 5 |  |
| 6.0 | 1 |  |
| 9.0 | 1 |  |
| 95.0 | 3569 | YES |
| 96.0 | 1 | YES |
| 99.0 | 1 | YES |
| MISSING (.) | 2 |  |

#### `C5WD90_3` — S19 # WORDS REPEATED 90 SEC-W5

N total = 4196, non-missing = 4194, missing (.) = 2

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 395 |  |
| 1.0 | 110 |  |
| 2.0 | 51 |  |
| 3.0 | 30 |  |
| 4.0 | 11 |  |
| 5.0 | 14 |  |
| 6.0 | 8 |  |
| 7.0 | 2 |  |
| 8.0 | 1 |  |
| 12.0 | 1 |  |
| 995.0 | 3569 | YES |
| 996.0 | 1 | YES |
| 999.0 | 1 | YES |
| MISSING (.) | 2 |  |

#### `H5MH2` — S19Q2 INTERRUPTD DURNG 60 SEC RECALL-W5

N total = 4196, non-missing = 4196, missing (.) = 0

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 617 |  |
| 1.0 | 10 |  |
| 95.0 | 3569 | YES |

#### `C5WD60_1` — S19 # WORDS ON LIST RECALLED 60 SEC-W5

N total = 4196, non-missing = 4194, missing (.) = 2

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 7 |  |
| 1.0 | 25 |  |
| 2.0 | 49 |  |
| 3.0 | 103 |  |
| 4.0 | 113 |  |
| 5.0 | 137 |  |
| 6.0 | 83 |  |
| 7.0 | 55 |  |
| 8.0 | 23 |  |
| 9.0 | 13 |  |
| 10.0 | 5 |  |
| 11.0 | 4 |  |
| 12.0 | 3 |  |
| 995.0 | 3569 | YES |
| 996.0 | 4 | YES |
| 999.0 | 1 | YES |
| MISSING (.) | 2 |  |

#### `C5WD60_2` — S19 # WORDS NOT ON LIST NAMED 60 SEC-W5

N total = 4196, non-missing = 4194, missing (.) = 2

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 333 |  |
| 1.0 | 171 |  |
| 2.0 | 67 |  |
| 3.0 | 25 |  |
| 4.0 | 13 |  |
| 5.0 | 2 |  |
| 6.0 | 1 |  |
| 7.0 | 2 |  |
| 8.0 | 2 |  |
| 9.0 | 4 |  |
| 95.0 | 3569 | YES |
| 96.0 | 4 | YES |
| 99.0 | 1 | YES |
| MISSING (.) | 2 |  |

#### `C5WD60_3` — S19 # WORDS REPEATED 60 SEC-W5

N total = 4196, non-missing = 4194, missing (.) = 2

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 509 |  |
| 1.0 | 70 |  |
| 2.0 | 19 |  |
| 3.0 | 5 |  |
| 4.0 | 4 |  |
| 5.0 | 7 |  |
| 6.0 | 3 |  |
| 7.0 | 1 |  |
| 8.0 | 1 |  |
| 9.0 | 1 |  |
| 95.0 | 3569 | YES |
| 96.0 | 4 | YES |
| 99.0 | 1 | YES |
| MISSING (.) | 2 |  |

#### `H5MH3A` — S19Q3A NUMBER STRING/2-4-W5

N total = 4196, non-missing = 4194, missing (.) = 2

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 2 |  |
| 1.0 | 623 |  |
| 95.0 | 3569 | YES |
| MISSING (.) | 2 |  |

#### `H5MH3B` — S19Q3B NUMBER STRING/5-7-W5

N total = 4196, non-missing = 4194, missing (.) = 2

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 2 |  |
| 95.0 | 3569 | YES |
| 97.0 | 623 | YES |
| MISSING (.) | 2 |  |

#### `H5MH4A` — S19Q4A NUMBER STRING/6-2-9-W5

N total = 4196, non-missing = 4192, missing (.) = 4

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 75 |  |
| 1.0 | 546 |  |
| 95.0 | 3569 | YES |
| 97.0 | 2 | YES |
| MISSING (.) | 4 |  |

#### `H5MH4B` — S19Q4B NUMBER STRING/4-1-5-W5

N total = 4196, non-missing = 4193, missing (.) = 3

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 16 |  |
| 1.0 | 60 |  |
| 95.0 | 3569 | YES |
| 97.0 | 548 | YES |
| MISSING (.) | 3 |  |

#### `H5MH5A` — S19Q5A NUMBER STRING/3-2-7-9-W5

N total = 4196, non-missing = 4192, missing (.) = 4

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 125 |  |
| 1.0 | 480 |  |
| 95.0 | 3569 | YES |
| 97.0 | 18 | YES |
| MISSING (.) | 4 |  |

#### `H5MH5B` — S19Q5B NUMBER STRING/4-9-6-8-W5

N total = 4196, non-missing = 4193, missing (.) = 3

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 68 |  |
| 1.0 | 58 |  |
| 95.0 | 3569 | YES |
| 97.0 | 498 | YES |
| MISSING (.) | 3 |  |

#### `H5MH6A` — S19Q6A NUMBER STRING/1-5-2-8-6-W5

N total = 4196, non-missing = 4192, missing (.) = 4

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 263 |  |
| 1.0 | 274 |  |
| 95.0 | 3569 | YES |
| 97.0 | 86 | YES |
| MISSING (.) | 4 |  |

#### `H5MH6B` — S19Q6B NUMBER STRING/6-1-8-4-3-W5

N total = 4196, non-missing = 4193, missing (.) = 3

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 152 |  |
| 1.0 | 112 |  |
| 95.0 | 3569 | YES |
| 97.0 | 360 | YES |
| MISSING (.) | 3 |  |

#### `H5MH7A` — S19Q7A NUMBER STRING/5-3-9-4-1-8-W5

N total = 4196, non-missing = 4191, missing (.) = 5

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 208 |  |
| 1.0 | 176 |  |
| 95.0 | 3569 | YES |
| 97.0 | 238 | YES |
| MISSING (.) | 5 |  |

#### `H5MH7B` — S19Q7B NUMBER STRING/7-2-4-8-5-6-W5

N total = 4196, non-missing = 4191, missing (.) = 5

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 129 |  |
| 1.0 | 79 |  |
| 95.0 | 3569 | YES |
| 97.0 | 414 | YES |
| MISSING (.) | 5 |  |

#### `H5MH8A` — S19Q8A NUMBER STRING/8-1-2-9-3-6-5-W5

N total = 4196, non-missing = 4189, missing (.) = 7

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 166 |  |
| 1.0 | 87 |  |
| 95.0 | 3569 | YES |
| 97.0 | 367 | YES |
| MISSING (.) | 7 |  |

#### `H5MH8B` — S19Q8B NUMBER STRING/4-7-3-9-1-2-8-W5

N total = 4196, non-missing = 4189, missing (.) = 7

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 117 |  |
| 1.0 | 49 |  |
| 95.0 | 3569 | YES |
| 97.0 | 454 | YES |
| MISSING (.) | 7 |  |

#### `H5MH9A` — S19Q9A NUMBER STRING/9-4-3-7-6-2-5-8-W5

N total = 4196, non-missing = 4188, missing (.) = 8

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 105 |  |
| 1.0 | 30 |  |
| 95.0 | 3569 | YES |
| 97.0 | 484 | YES |
| MISSING (.) | 8 |  |

#### `H5MH9B` — S19Q9B NUMBER STRING/7-2-8-1-9-6-5-3-W5

N total = 4196, non-missing = 4156, missing (.) = 40

| Value | Count | Reserve? |
|-------|-------|----------|
| 0.0 | 86 |  |
| 1.0 | 17 |  |
| 95.0 | 3569 | YES |
| 97.0 | 484 | YES |
| MISSING (.) | 40 |  |

## 3. Non-missing N by mode (Task 3e)

Mode variable = `MODE`. Non-missing = raw count of cases with a real value (i.e., not `.`). Reserve codes 95/995/9995 are counted as non-missing because they are explicit survey codes, not blank cells.

### `H5MH1` — S19Q1 INTERRUPTD DURING 90 SEC RECALL-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 723 | 100.0% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 101 | 100.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `C5WD90_1` — S19 # WORDS ON LIST RECALLED 90 SEC-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 721 | 99.7% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 101 | 100.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `C5WD90_2` — S19 # WORDS NOT ON LIST NAMED 90 SEC-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 721 | 99.7% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 101 | 100.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `C5WD90_3` — S19 # WORDS REPEATED 90 SEC-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 721 | 99.7% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 101 | 100.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH2` — S19Q2 INTERRUPTD DURNG 60 SEC RECALL-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 723 | 100.0% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 101 | 100.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `C5WD60_1` — S19 # WORDS ON LIST RECALLED 60 SEC-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 721 | 99.7% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 101 | 100.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `C5WD60_2` — S19 # WORDS NOT ON LIST NAMED 60 SEC-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 721 | 99.7% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 101 | 100.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `C5WD60_3` — S19 # WORDS REPEATED 60 SEC-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 721 | 99.7% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 101 | 100.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH3A` — S19Q3A NUMBER STRING/2-4-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 722 | 99.9% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH3B` — S19Q3B NUMBER STRING/5-7-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 722 | 99.9% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH4A` — S19Q4A NUMBER STRING/6-2-9-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 720 | 99.6% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH4B` — S19Q4B NUMBER STRING/4-1-5-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 721 | 99.7% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH5A` — S19Q5A NUMBER STRING/3-2-7-9-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 720 | 99.6% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH5B` — S19Q5B NUMBER STRING/4-9-6-8-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 721 | 99.7% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH6A` — S19Q6A NUMBER STRING/1-5-2-8-6-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 720 | 99.6% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH6B` — S19Q6B NUMBER STRING/6-1-8-4-3-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 721 | 99.7% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH7A` — S19Q7A NUMBER STRING/5-3-9-4-1-8-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 719 | 99.4% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH7B` — S19Q7B NUMBER STRING/7-2-4-8-5-6-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 719 | 99.4% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH8A` — S19Q8A NUMBER STRING/8-1-2-9-3-6-5-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 718 | 99.3% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 99 | 98.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH8B` — S19Q8B NUMBER STRING/4-7-3-9-1-2-8-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 717 | 99.2% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH9A` — S19Q9A NUMBER STRING/9-4-3-7-6-2-5-8-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 716 | 99.0% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### `H5MH9B` — S19Q9B NUMBER STRING/7-2-8-1-9-6-5-3-W5

| Mode | Total respondents in mode | Non-missing on this var | % administered |
|------|--------------------------|-------------------------|----------------|
| I = In-person (CAPI) | 723 | 688 | 95.2% |
| M = Mail (paper self-administered) | 147 | 147 | 100.0% |
| S = Spanish CAPI / other | 4 | 4 | 100.0% |
| T = Telephone (CATI) | 101 | 96 | 95.0% |
| W = Web (self-administered online) | 3221 | 3221 | 100.0% |

### Stricter view: non-missing AND not in 95/995/9995 reserve family

(This excludes 'question not asked' so the remaining count approximates actual test administration.)

#### `H5MH1` — S19Q1 INTERRUPTD DURING 90 SEC RECALL-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 526 | 72.8% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 101 | 100.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 627**

#### `C5WD90_1` — S19 # WORDS ON LIST RECALLED 90 SEC-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 523 | 72.3% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 623**

#### `C5WD90_2` — S19 # WORDS NOT ON LIST NAMED 90 SEC-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 523 | 72.3% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 623**

#### `C5WD90_3` — S19 # WORDS REPEATED 90 SEC-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 523 | 72.3% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 623**

#### `H5MH2` — S19Q2 INTERRUPTD DURNG 60 SEC RECALL-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 526 | 72.8% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 101 | 100.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 627**

#### `C5WD60_1` — S19 # WORDS ON LIST RECALLED 60 SEC-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 520 | 71.9% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 620**

#### `C5WD60_2` — S19 # WORDS NOT ON LIST NAMED 60 SEC-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 520 | 71.9% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 620**

#### `C5WD60_3` — S19 # WORDS REPEATED 60 SEC-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 520 | 71.9% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 620**

#### `H5MH3A` — S19Q3A NUMBER STRING/2-4-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 525 | 72.6% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 625**

#### `H5MH3B` — S19Q3B NUMBER STRING/5-7-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 2 | 0.3% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 0 | 0.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 2**

#### `H5MH4A` — S19Q4A NUMBER STRING/6-2-9-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 521 | 72.1% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 100 | 99.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 621**

#### `H5MH4B` — S19Q4B NUMBER STRING/4-1-5-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 64 | 8.9% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 12 | 11.9% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 76**

#### `H5MH5A` — S19Q5A NUMBER STRING/3-2-7-9-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 507 | 70.1% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 98 | 97.0% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 605**

#### `H5MH5B` — S19Q5B NUMBER STRING/4-9-6-8-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 111 | 15.4% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 15 | 14.9% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 126**

#### `H5MH6A` — S19Q6A NUMBER STRING/1-5-2-8-6-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 446 | 61.7% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 91 | 90.1% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 537**

#### `H5MH6B` — S19Q6B NUMBER STRING/6-1-8-4-3-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 220 | 30.4% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 44 | 43.6% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 264**

#### `H5MH7A` — S19Q7A NUMBER STRING/5-3-9-4-1-8-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 320 | 44.3% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 64 | 63.4% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 384**

#### `H5MH7B` — S19Q7B NUMBER STRING/7-2-4-8-5-6-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 173 | 23.9% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 35 | 34.7% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 208**

#### `H5MH8A` — S19Q8A NUMBER STRING/8-1-2-9-3-6-5-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 217 | 30.0% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 36 | 35.6% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 253**

#### `H5MH8B` — S19Q8B NUMBER STRING/4-7-3-9-1-2-8-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 140 | 19.4% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 26 | 25.7% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 166**

#### `H5MH9A` — S19Q9A NUMBER STRING/9-4-3-7-6-2-5-8-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 118 | 16.3% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 17 | 16.8% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 135**

#### `H5MH9B` — S19Q9B NUMBER STRING/7-2-8-1-9-6-5-3-W5

| Mode | Total in mode | Administered (real score) | % |
|------|--------------|---------------------------|---|
| I = In-person (CAPI) | 723 | 90 | 12.4% |
| M = Mail (paper self-administered) | 147 | 0 | 0.0% |
| S = Spanish CAPI / other | 4 | 0 | 0.0% |
| T = Telephone (CATI) | 101 | 13 | 12.9% |
| W = Web (self-administered online) | 3221 | 0 | 0.0% |
**Total administered across modes: 103**

## 4. Verdict: does the 'in-person/phone only' claim hold?

### Harmonized cognitive test totals by mode

| Test | Variable | In-person (I) | Telephone (T) | Web (W) | Mail (M) | Spanish/other (S) | Total administered |
|------|----------|---------------|----------------|---------|----------|--------------------|--------------------|
| Immediate Word Recall (90-sec list) | `C5WD90_1` | 523 | 100 | 0 | 0 | 0 | 623 |
| Delayed Word Recall (60-sec list) | `C5WD60_1` | 520 | 100 | 0 | 0 | 0 | 620 |
| Digit Span Backward (any H5MH3-9 trial attempted) | `H5MH3A..H5MH9B` | 525 | 100 | 0 | 0 | 0 | 625 |

### Summary

- The MODE variable partitions the N=4,196 public-use Wave V file into Web (77%), In-person (17%), Mail (3.5%), Telephone (2.4%), and Spanish/other (<0.1%).
- Cognitive test items (C5WD90_*, C5WD60_*, H5MH1-H5MH9B) are present in the file for **every** respondent, but **all** Web and Mail respondents receive reserve code 95/995/9995 ("question not asked").
- After excluding the 95-family reserve codes, administered N is concentrated entirely in In-person and Telephone modes.
- **The claim that cognitive tests were administered only in in-person and phone modes is EMPIRICALLY CONFIRMED** at the public-use level: administered N in Web+Mail+S = 0 across all Section-19 items.
- Public-use administered N for Immediate and Delayed Word Recall ~ 623 and 620, consistent with the proportional expectation (full sample 1,705 of 12,300 -> public-use ~582 at the 34.1% public-use share). Slight excess likely reflects public-use oversampling of genetic twins / cohort strata.

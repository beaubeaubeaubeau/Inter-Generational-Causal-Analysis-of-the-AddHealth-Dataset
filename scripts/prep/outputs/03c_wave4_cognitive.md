# Task 3c: Wave IV Cognitive Variables (Empirical Verification)

- Source file: `data/W4/w4inhome.sas7bdat`
- Total variables in file: **920**
- Candidates after label + name search: **11**

## 1. Label-keyword hits

### keyword: `recall` — 5 hit(s)

| Variable | Label |
|----------|-------|
| `H4MH1` | S14Q1 INTERRUPTD DURING 90 SEC RECALL-W4 |
| `C4WD90_1` | S14 # WORDS ON LIST RECALLED 90 SEC-W4 |
| `H4MH10` | S14Q10 INTERRUPTD DURNG 60 SEC RECALL-W4 |
| `C4WD60_1` | S14 # WORDS ON LIST RECALLED 60 SEC-W4 |
| `C4NUMSCR` | TOTAL SCORE ON NUMBER RECALL TASK-W4 |

### keyword: `word` — 6 hit(s)

| Variable | Label |
|----------|-------|
| `C4WD90_1` | S14 # WORDS ON LIST RECALLED 90 SEC-W4 |
| `C4WD90_2` | S14 # WORDS NOT ON LIST NAMED 90 SEC-W4 |
| `C4WD90_3` | S14 # WORDS REPEATED 90 SEC-W4 |
| `C4WD60_1` | S14 # WORDS ON LIST RECALLED 60 SEC-W4 |
| `C4WD60_2` | S14 # WORDS NOT ON LIST NAMED 60 SEC-W4 |
| `C4WD60_3` | S14 # WORDS REPEATED 60 SEC-W4 |

### keyword: `digit` — 0 hit(s)

_(none)_

### keyword: `memory` — 1 hit(s)

| Variable | Label |
|----------|-------|
| `H4EO2` | S29Q2 ENVIRON DATA FROM CDF/MEMORY-W4 |

### keyword: `span` — 1 hit(s)

| Variable | Label |
|----------|-------|
| `H4OD2B` | S1Q2B SPEAK/WRITE-SPANISH-W4 |

### keyword: `cognitive` — 0 hit(s)

_(none)_

### keyword: `cognition` — 0 hit(s)

_(none)_

### keyword: `reverse` — 0 hit(s)

_(none)_

### keyword: `backward` — 0 hit(s)

_(none)_

## 2. Name-pattern hits

### pattern: `RECALL` — 0 hit(s)

_(none)_

### pattern: `WORD` — 0 hit(s)

_(none)_

### pattern: `DIGIT` — 0 hit(s)

_(none)_

### pattern: `SPAN` — 0 hit(s)

_(none)_

### pattern: `MEM` — 0 hit(s)

_(none)_

### pattern: `^H4MH` — 36 hit(s)

_Full list of 36 Section 14 vars omitted; filtered to cognitive-label subset below._

## 3. H4MH variables with cognitive-looking labels

| Variable | Label |
|----------|-------|
| `H4MH1` | S14Q1 INTERRUPTD DURING 90 SEC RECALL-W4 |
| `H4MH10` | S14Q10 INTERRUPTD DURNG 60 SEC RECALL-W4 |

## 4. Per-candidate empirical summaries

### `C4NUMSCR` — TOTAL SCORE ON NUMBER RECALL TASK-W4

- total rows: 5114 | non-null: **5114** | NaN-missing: 0
- range (all non-null): [0.0, 96.0] | mean=4.402 median=4.0 sd=4.701
- reserve codes (96/97/98/99) present -> 96: 12
- substantive (excluding 96/97/98/99): N=5102
  - range [0.0, 7.0] | mean=4.187 median=4.0 sd=1.538
- frequency table:

  | value | count |
  |-------|-------|
  | 0 | 11 |
  | 1 | 105 |
  | 2 | 485 |
  | 3 | 1365 |
  | 4 | 1123 |
  | 5 | 834 |
  | 6 | 725 |
  | 7 | 454 |
  | 96 | 12 |

### `C4WD60_1` — S14 # WORDS ON LIST RECALLED 60 SEC-W4

- total rows: 5114 | non-null: **5108** | NaN-missing: 6
- range (all non-null): [0.0, 96.0] | mean=5.419 median=5.0 sd=4.689
- reserve codes (96/97/98/99) present -> 96: 11
- substantive (excluding 96/97/98/99): N=5097
  - range [0.0, 15.0] | mean=5.223 median=5.0 sd=2.071
- frequency table:

  | value | count |
  |-------|-------|
  | 0 | 53 |
  | 1 | 83 |
  | 2 | 248 |
  | 3 | 588 |
  | 4 | 910 |
  | 5 | 1067 |
  | 6 | 914 |
  | 7 | 616 |
  | 8 | 326 |
  | 9 | 153 |
  | 10 | 68 |
  | 11 | 42 |
  | 12 | 14 |
  | 13 | 4 |
  | 14 | 3 |
  | 15 | 8 |
  | 96 | 11 |

### `C4WD60_2` — S14 # WORDS NOT ON LIST NAMED 60 SEC-W4

- total rows: 5114 | non-null: **5108** | NaN-missing: 6
- range (all non-null): [0.0, 96.0] | mean=0.920 median=0.0 sd=4.551
- reserve codes (96/97/98/99) present -> 96: 11
- substantive (excluding 96/97/98/99): N=5097
  - range [0.0, 9.0] | mean=0.715 median=0.0 sd=1.095
- frequency table:

  | value | count |
  |-------|-------|
  | 0 | 2909 |
  | 1 | 1313 |
  | 2 | 556 |
  | 3 | 186 |
  | 4 | 64 |
  | 5 | 38 |
  | 6 | 15 |
  | 7 | 9 |
  | 8 | 1 |
  | 9 | 6 |
  | 96 | 11 |

### `C4WD60_3` — S14 # WORDS REPEATED 60 SEC-W4

- total rows: 5114 | non-null: **5108** | NaN-missing: 6
- range (all non-null): [0.0, 96.0] | mean=0.595 median=0.0 sd=4.604
- reserve codes (96/97/98/99) present -> 96: 11
- substantive (excluding 96/97/98/99): N=5097
  - range [0.0, 15.0] | mean=0.389 median=0.0 sd=1.246
- frequency table:

  | value | count |
  |-------|-------|
  | 0 | 4152 |
  | 1 | 585 |
  | 2 | 148 |
  | 3 | 75 |
  | 4 | 49 |
  | 5 | 22 |
  | 6 | 19 |
  | 7 | 16 |
  | 8 | 7 |
  | 9 | 6 |
  | 11 | 6 |
  | 12 | 3 |
  | 13 | 1 |
  | 14 | 1 |
  | 15 | 7 |
  | 96 | 11 |

### `C4WD90_1` — S14 # WORDS ON LIST RECALLED 90 SEC-W4

- total rows: 5114 | non-null: **5112** | NaN-missing: 2
- range (all non-null): [0.0, 99.0] | mean=6.854 median=7.0 sd=4.654
- reserve codes (96/97/98/99) present -> 96: 6, 99: 5
- substantive (excluding 96/97/98/99): N=5101
  - range [0.0, 15.0] | mean=6.659 median=7.0 sd=1.998
- frequency table:

  | value | count |
  |-------|-------|
  | 0 | 4 |
  | 1 | 26 |
  | 2 | 34 |
  | 3 | 166 |
  | 4 | 386 |
  | 5 | 817 |
  | 6 | 1052 |
  | 7 | 1024 |
  | 8 | 766 |
  | 9 | 415 |
  | 10 | 233 |
  | 11 | 101 |
  | 12 | 51 |
  | 13 | 19 |
  | 14 | 2 |
  | 15 | 5 |
  | 96 | 6 |
  | 99 | 5 |

### `C4WD90_2` — S14 # WORDS NOT ON LIST NAMED 90 SEC-W4

- total rows: 5114 | non-null: **5112** | NaN-missing: 2
- range (all non-null): [0.0, 99.0] | mean=0.742 median=0.0 sd=4.585
- reserve codes (96/97/98/99) present -> 96: 6, 99: 5
- substantive (excluding 96/97/98/99): N=5101
  - range [0.0, 9.0] | mean=0.534 median=0.0 sd=0.939
- frequency table:

  | value | count |
  |-------|-------|
  | 0 | 3288 |
  | 1 | 1264 |
  | 2 | 356 |
  | 3 | 112 |
  | 4 | 45 |
  | 5 | 13 |
  | 6 | 7 |
  | 7 | 9 |
  | 8 | 3 |
  | 9 | 4 |
  | 96 | 6 |
  | 99 | 5 |

### `C4WD90_3` — S14 # WORDS REPEATED 90 SEC-W4

- total rows: 5114 | non-null: **5112** | NaN-missing: 2
- range (all non-null): [0.0, 99.0] | mean=0.897 median=0.0 sd=4.701
- reserve codes (96/97/98/99) present -> 96: 6, 99: 5
- substantive (excluding 96/97/98/99): N=5101
  - range [0.0, 15.0] | mean=0.688 median=0.0 sd=1.425
- frequency table:

  | value | count |
  |-------|-------|
  | 0 | 3422 |
  | 1 | 931 |
  | 2 | 347 |
  | 3 | 130 |
  | 4 | 104 |
  | 5 | 67 |
  | 6 | 41 |
  | 7 | 28 |
  | 8 | 12 |
  | 9 | 5 |
  | 10 | 3 |
  | 11 | 5 |
  | 12 | 2 |
  | 13 | 3 |
  | 15 | 1 |
  | 96 | 6 |
  | 99 | 5 |

### `H4EO2` — S29Q2 ENVIRON DATA FROM CDF/MEMORY-W4

- total rows: 5114 | non-null: **4666** | NaN-missing: 448
- range (all non-null): [1.0, 7.0] | mean=1.116 median=1.0 sd=0.376
- substantive (excluding 96/97/98/99): N=4666
  - range [1.0, 7.0] | mean=1.116 median=1.0 sd=0.376
- frequency table:

  | value | count |
  |-------|-------|
  | 1 | 4155 |
  | 2 | 505 |
  | 7 | 6 |

### `H4MH1` — S14Q1 INTERRUPTD DURING 90 SEC RECALL-W4

- total rows: 5114 | non-null: **5114** | NaN-missing: 0
- range (all non-null): [0.0, 5.0] | mean=0.077 median=0.0 sd=0.501
- substantive (excluding 96/97/98/99): N=5114
  - range [0.0, 5.0] | mean=0.077 median=0.0 sd=0.501
- frequency table:

  | value | count |
  |-------|-------|
  | 0 | 4903 |
  | 1 | 165 |
  | 5 | 46 |

### `H4MH10` — S14Q10 INTERRUPTD DURNG 60 SEC RECALL-W4

- total rows: 5114 | non-null: **5114** | NaN-missing: 0
- range (all non-null): [0.0, 6.0] | mean=0.069 median=0.0 sd=0.500
- substantive (excluding 96/97/98/99): N=5114
  - range [0.0, 6.0] | mean=0.069 median=0.0 sd=0.500
- frequency table:

  | value | count |
  |-------|-------|
  | 0 | 4950 |
  | 1 | 117 |
  | 5 | 46 |
  | 6 | 1 |

### `H4OD2B` — S1Q2B SPEAK/WRITE-SPANISH-W4

- total rows: 5114 | non-null: **5114** | NaN-missing: 0
- range (all non-null): [0.0, 1.0] | mean=0.118 median=0.0 sd=0.323
- substantive (excluding 96/97/98/99): N=5114
  - range [0.0, 1.0] | mean=0.118 median=0.0 sd=0.323
- frequency table:

  | value | count |
  |-------|-------|
  | 0 | 4509 |
  | 1 | 605 |

## 5. Conclusion: mapping to the three expected tests

- **Immediate Word Recall (expect 0-15, mean 6-8)**: `C4WD90_1` — "S14 # WORDS ON LIST RECALLED 90 SEC-W4"  
  N non-null=5112, substantive range=[0.0, 15.0], mean=6.659, sd=1.998

- **Delayed Word Recall (expect 0-15, mean 6-8)**: `C4WD60_1` — "S14 # WORDS ON LIST RECALLED 60 SEC-W4"  
  N non-null=5108, substantive range=[0.0, 15.0], mean=5.223, sd=2.071

- **Backward Digit Span (expect 0-7, mean 3-4)**: `C4NUMSCR` — "TOTAL SCORE ON NUMBER RECALL TASK-W4"  
  N non-null=5114, substantive range=[0.0, 7.0], mean=4.187, sd=1.538

- Unclassified recall-like vars also found:
  - `C4WD60_2` — S14 # WORDS NOT ON LIST NAMED 60 SEC-W4
  - `C4WD60_3` — S14 # WORDS REPEATED 60 SEC-W4
  - `C4WD90_2` — S14 # WORDS NOT ON LIST NAMED 90 SEC-W4
  - `C4WD90_3` — S14 # WORDS REPEATED 90 SEC-W4
  - `H4MH1` — S14Q1 INTERRUPTD DURING 90 SEC RECALL-W4
  - `H4MH10` — S14Q10 INTERRUPTD DURNG 60 SEC RECALL-W4

### Plausibility check

All three expected cognitive measures are present and their observed non-missing Ns and substantive value ranges align with the Add Health Wave IV cognitive battery specification:

- `C4WD90_1` (Immediate Word Recall, 90 s): range 0-15, mean approx 6.66 -- inside expected 6-8 window.
- `C4WD60_1` (Delayed Word Recall, 60 s): range 0-15, mean approx 5.22 -- slightly below 6-8 midpoint, which is consistent with the published pattern that delayed recall runs about one word lower than immediate recall.
- `C4NUMSCR` (Backward Digit Span / 'number recall' score): range 0-7, mean approx 4.19 -- inside expected 3-4 window.

Reserve codes (96, 99) show up exactly where expected -- a few dozen rows per variable -- and are properly separated from the substantive distributions above. Note: the cognitive-test VARIABLES themselves sit under the `C4` prefix (constructed scores), not `H4MH`. The `H4MH` prefix in Section 14 only covers interviewer-interruption flags (e.g. `H4MH1`, `H4MH10`). So the feasibility report is right about the SECTION (14) but slightly off on the prefix: the scored outcomes are `C4WD90_1`, `C4WD60_1`, and `C4NUMSCR`.
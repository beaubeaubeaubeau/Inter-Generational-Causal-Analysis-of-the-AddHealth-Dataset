# Task 08 - Analytic frame diagnostics

## Pre-registered N benchmarks (from 07_analytic_n.csv)

| configuration                            | design_purpose                           |    N |
|:-----------------------------------------|:-----------------------------------------|-----:|
| W1 network observed (IDGX2 non-miss)     | —                                        | 4397 |
| W1 AH_PVT valid                          | —                                        | 6223 |
| W4 immediate recall valid                | —                                        | 5101 |
| W4 delayed recall valid                  | —                                        | 5097 |
| W4 backward digit span valid             | —                                        | 5102 |
| W5 immediate recall valid                | —                                        |  623 |
| W5 delayed recall valid                  | —                                        |  620 |
| W5 BDS any trial valid                   | —                                        |  625 |
| W1 network ∩ W4 immediate                | Primary W4 design                        | 3505 |
| W1 network ∩ W4 BDS                      | Primary W4 design (BDS)                  | 3506 |
| W1 network ∩ W5 immediate                | Primary W5 design                        |  394 |
| W1 network ∩ W5 BDS                      | Primary W5 design (BDS)                  |  394 |
| W1 network ∩ W4 imm ∩ W5 imm             | Longitudinal change-score                |  334 |
| W1 network ∩ W4 BDS ∩ W5 BDS             | Longit change (BDS)                      |  335 |
| W1 AH_PVT ∩ W4 immediate                 | Friendship(survey)→W4 cog, with baseline | 4883 |
| W1 AH_PVT ∩ W5 immediate                 | Friendship(survey)→W5 cog, with baseline |  594 |
| W1 network ∩ W1 AH_PVT ∩ W4 imm          | Network + baseline + W4 outcome          | 3353 |
| W1 network ∩ W1 AH_PVT ∩ W5 imm          | Network + baseline + W5 outcome          |  372 |
| W1 network ∩ W1 AH_PVT ∩ W4 imm ∩ W5 imm | Full longitudinal with baseline          |  316 |

## Reproduced N from merged frames

| Configuration | N observed | N reproduced | Match? |
|---|---|---|---|
| W1 network ∩ W4 immediate | 3505 | 3505 | ✅ |
| W1 network ∩ W4 BDS | 3506 | 3506 | ✅ |
| W1 network ∩ W5 immediate | 394 | 394 | ✅ |
| W1 network ∩ W5 BDS (any trial) | 394 | 394 | ✅ |
| W1 AH_PVT ∩ W4 immediate | 4883 | 4883 | ✅ |
| W4 immediate (all W1) | 5101 | 5101 | ✅ |
| W5 cog admin (I/T only) | 623 | 623 | ✅ |

## N reconciliation: 620 vs 394

- **623** W5 respondents have an immediate-recall score administered (in-person + phone modes only).
- **394** of those 623 also have a valid W1 network exposure (IDGX2); this is the N for spec #1 when applied to W5.
- **620** in the feasibility summary likely refers to delayed recall (`C5WD60_1`, N=620); **623** is immediate recall.
- **Both numbers are correct for their respective intersections.**

## Derived variable ranges (W4 frame)

|                    |   count |          mean |        std |      min |        max |
|:-------------------|--------:|--------------:|-----------:|---------:|-----------:|
| IDGX2              |    3511 |   4.58274     |   3.68263  |  0       |   30       |
| ODGX2              |    3511 |   4.53147     |   3.05991  |  0       |   10       |
| BCENT10X           |    3511 |   0.801212    |   0.628193 |  0       |    4.28828 |
| REACH              |    3511 | 478.635       | 432.095    |  0       | 1791       |
| C4WD90_1           |    5101 |   6.65889     |   1.99777  |  0       |   15       |
| C4WD60_1           |    5097 |   5.22327     |   2.07067  |  0       |   15       |
| C4NUMSCR           |    5102 |   4.18659     |   1.53814  |  0       |    7       |
| W4_COG_COMP        |    5090 |   0.000375423 |   0.769602 | -2.85917 |    3.57528 |
| AH_RAW             |    4896 |  65.4346      |  10.6295   |  0       |   87       |
| CESD_SUM           |    5088 |  10.8726      |   7.4457   |  0       |   50       |
| SCHOOL_BELONG      |    5005 |  21.6426      |   3.74495  |  6       |   30       |
| FRIEND_N_NOMINEES  |    5114 |   2.97595     |   2.42389  |  0       |   10       |
| FRIEND_CONTACT_SUM |    5114 |   7.41064     |   6.28743  |  0       |   50       |
| PARENT_ED          |    4966 |   3.68244     |   2.06121  |  0       |    6       |

## Key N's in each frame

- `analytic_w4.parquet`: 5114 rows (W1 inhome inner-joined to W4 in-home)
- `analytic_w5.parquet`: 824 rows (W1 inhome inner-joined to W5 cognitive, mode=I/T)
- `analytic_w1_full.parquet`: 5114 rows (W1 inhome inner-joined to W4 in-home, no network gate)

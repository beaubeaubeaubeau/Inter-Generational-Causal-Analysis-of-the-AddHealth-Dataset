# EXP-15-MULTI — Multi-outcome screening

Re-runs the outcome-dependent part of the cognitive-screening diagnostic battery (D1 baseline WLS on `GSWGT4_2`, cluster-robust on `CLUSTER2`, primary spec L0+L1+AHPVT; D4 adjustment-set stability across L0 / L0+L1 / L0+L1+AHPVT) across 12 non-cognitive outcomes. Outcome-independent diagnostics (D2 height NC, D6/D7 dose-response + overlap, D8 saturation loss, D9 red flags) are inherited from [../cognitive-screening/tables/primary/14_screening_matrix.csv](../../cognitive-screening/tables/primary/14_screening_matrix.csv).

**Weight caveat:** `GSWGT4_2` is used uniformly for screening. Formal causal estimation on W5 outcomes should substitute `GSW5` and handle W4→W5 attrition (IPAW or bounding).

**Adjustment-set caveat:** the primary spec includes `AH_PVT` (verbal IQ at W1) uniformly. For `H5EC1` / `H5LM5` / `H4BMI` this is plausibly a mediator (cognition → attainment / health behaviours → outcome); D4 flags any outcome where adding AHPVT moves β by > 30%. **For SES outcomes (`H5EC1`, `H5LM5`)**, the matrix CSV emits a parallel `beta_no_ahpvt` / `se_no_ahpvt` / `p_no_ahpvt` triple from a L0+L1 (AHPVT-dropped) fit — that is the methodologically-correct screening estimate per `DAG-SES`, since AHPVT lies on the SOC → AHPVT → educational credentialism → earnings causal path. The AHPVT-adjusted β biases the SOC effect downward.

**Multiple-testing caveat:** the `d1_q` column gives Benjamini–Hochberg q-values within each outcome family (24 tests per outcome). Use `d1_q` rather than raw `p` when discussing breadth of significant exposures.

## Per-outcome rankings

### H4BMI — S27 BMI—W4

N range across exposures: 2748–4665. Significant (p<0.05) exposures: 6 / 24.

| exposure           |    n |     beta |      se |        p | d1_pass   |   d4_rel_shift | d4_pass   |
|:-------------------|-----:|---------:|--------:|---------:|:----------|---------------:|:----------|
| IDGX2              | 3234 | -0.1999  | 0.03186 | 6.83e-09 | True      |           0.21 | True      |
| IDG_LEQ1           | 3234 |  1.439   | 0.384   | 0.000283 | True      |           0.16 | True      |
| IDG_ZERO           | 3234 |  2.124   | 0.5909  | 0.000486 | True      |           0.1  | True      |
| ESDEN              | 2748 | -2.545   | 0.9551  | 0.00883  | True      |           0.1  | True      |
| PRXPREST           | 2972 | -3.219   | 1.412   | 0.0245   | True      |           0.21 | True      |
| FRIEND_CONTACT_SUM | 4665 | -0.04391 | 0.02209 | 0.0489   | True      |           0.27 | True      |

### H4SBP — S27 SYSTOLIC BLOOD PRESSURE—W4

N range across exposures: 2721–4609. Significant (p<0.05) exposures: 2 / 24.

| exposure              |    n |     beta |      se |       p | d1_pass   |   d4_rel_shift | d4_pass   |
|:----------------------|-----:|---------:|--------:|--------:|:----------|---------------:|:----------|
| H1DA7                 | 4609 |  0.5349  | 0.1751  | 0.00273 | True      |           0.09 | True      |
| RCHDEN                | 3197 |  4.856   | 1.983   | 0.0159  | True      |           0.14 | True      |
| FRIEND_CONTACT_SUM    | 4609 |  0.05385 | 0.02852 | 0.0612  | False     |           0.19 | True      |
| FRIEND_DISCLOSURE_ANY | 4609 |  0.7315  | 0.487   | 0.135   | False     |           0.16 | True      |
| FRIEND_N_NOMINEES     | 4609 |  0.09792 | 0.07374 | 0.187   | False     |           0.31 | False     |
| BCENT10X              | 3197 | -0.534   | 0.407   | 0.192   | False     |           0.53 | False     |

### H4DBP — S27 DIASTOLIC BLOOD PRESSURE—W4

N range across exposures: 2721–4609. Significant (p<0.05) exposures: 0 / 24.

| exposure              |    n |       beta |        se |      p | d1_pass   |   d4_rel_shift | d4_pass   |
|:----------------------|-----:|-----------:|----------:|-------:|:----------|---------------:|:----------|
| IDGX2                 | 3197 | -0.09308   | 0.05382   | 0.0865 | False     |           0.27 | True      |
| FRIEND_CONTACT_SUM    | 4609 |  0.04018   | 0.02587   | 0.123  | False     |           0.16 | True      |
| ESDEN                 | 2721 | -1.772     | 1.169     | 0.132  | False     |           0.05 | True      |
| RCHDEN                | 3197 |  2.171     | 1.76      | 0.22   | False     |           0.27 | True      |
| REACH                 | 3197 |  0.0005515 | 0.0004495 | 0.222  | False     |           0.19 | True      |
| FRIEND_DISCLOSURE_ANY | 4609 |  0.4306    | 0.3617    | 0.236  | False     |           0.06 | True      |

### H4WAIST — S27 MEASURED WAIST (CM)—W4

N range across exposures: 2765–4689. Significant (p<0.05) exposures: 7 / 24.

| exposure   |    n |      beta |       se |        p | d1_pass   |   d4_rel_shift | d4_pass   |
|:-----------|-----:|----------:|---------:|---------:|:----------|---------------:|:----------|
| IDGX2      | 3250 | -0.5138   | 0.06877  | 1.87e-11 | True      |           0.18 | True      |
| IDG_ZERO   | 3250 |  4.548    | 1.218    | 0.000299 | True      |           0.09 | True      |
| IDG_LEQ1   | 3250 |  3.059    | 0.8352   | 0.000382 | True      |           0.16 | True      |
| PRXPREST   | 2986 | -9.853    | 3.267    | 0.00317  | True      |           0.15 | True      |
| INFLDMN    | 3250 | -0.002861 | 0.001014 | 0.00566  | True      |           0.18 | True      |
| ERDEN      | 2986 |  4.406    | 1.875    | 0.0205   | True      |           0.26 | True      |

### H4BMICLS — S27 BMI CLASS—W4

N range across exposures: 2748–4665. Significant (p<0.05) exposures: 5 / 24.

| exposure           |    n |      beta |        se |        p | d1_pass   |   d4_rel_shift | d4_pass   |
|:-------------------|-----:|----------:|----------:|---------:|:----------|---------------:|:----------|
| IDGX2              | 3234 | -0.03228  | 0.005518  | 4.97e-08 | True      |           0.21 | True      |
| IDG_ZERO           | 3234 |  0.3609   | 0.09334   | 0.000186 | True      |           0.09 | True      |
| IDG_LEQ1           | 3234 |  0.2176   | 0.06386   | 0.000912 | True      |           0.18 | True      |
| ESDEN              | 2748 | -0.4484   | 0.1566    | 0.005    | True      |           0.1  | True      |
| REACH3             | 3234 |  0.00131  | 0.0005743 | 0.0245   | True      |           0.27 | True      |
| FRIEND_CONTACT_SUM | 4665 | -0.007594 | 0.004033  | 0.0619   | False     |           0.25 | True      |

### H5MN1 — S13Q1 LAST MO NO CNTRL IMPORT THINGS—W5

N range across exposures: 2060–3387. Significant (p<0.05) exposures: 3 / 24.

| exposure      |    n |      beta |        se |      p | d1_pass   |   d4_rel_shift | d4_pass   |
|:--------------|-----:|----------:|----------:|-------:|:----------|---------------:|:----------|
| SCHOOL_BELONG | 3331 | -0.01841  | 0.007354  | 0.0136 | True      |           0.66 | False     |
| HAVEBFF       | 2387 | -0.1266   | 0.05672   | 0.0275 | True      |           0.14 | True      |
| REACH         | 2387 | -0.000112 | 5.593e-05 | 0.0476 | True      |           0.01 | True      |
| IDGX2         | 2387 | -0.01326  | 0.006788  | 0.0532 | False     |           0.32 | False     |
| ODGX2         | 2387 | -0.01735  | 0.00894   | 0.0548 | False     |           0.38 | False     |
| BCENT10X      | 2387 | -0.07252  | 0.03867   | 0.0633 | False     |           0.52 | False     |

### H5MN2 — S13Q2 LAST MO CONFID HANDLE PERS PBMS—W5

N range across exposures: 2057–3381. Significant (p<0.05) exposures: 3 / 24.

| exposure           |    n |      beta |       se |       p | d1_pass   |   d4_rel_shift | d4_pass   |
|:-------------------|-----:|----------:|---------:|--------:|:----------|---------------:|:----------|
| FRIEND_CONTACT_SUM | 3381 |  0.008025 | 0.002823 | 0.00519 | True      |           0.23 | True      |
| IDG_ZERO           | 2380 | -0.2047   | 0.08954  | 0.0241  | True      |           0.09 | True      |
| SCHOOL_BELONG      | 3325 |  0.01158  | 0.005739 | 0.0456  | True      |           1.31 | False     |
| IDGX2              | 2380 |  0.0108   | 0.005545 | 0.054   | False     |           0.42 | False     |
| IGDMEAN            | 2057 |  0.03894  | 0.02011  | 0.0553  | False     |           0.24 | True      |
| IDG_LEQ1           | 2380 | -0.1137   | 0.06068  | 0.0637  | False     |           0.32 | False     |

### H5ID1 — S5Q1 HOW IS GEN PHYSICAL HEALTH—W5

N range across exposures: 2099–3457. Significant (p<0.05) exposures: 11 / 24.

| exposure      |    n |       beta |        se |        p | d1_pass   |   d4_rel_shift | d4_pass   |
|:--------------|-----:|-----------:|----------:|---------:|:----------|---------------:|:----------|
| IDGX2         | 2438 | -0.02155   | 0.004864  | 2.19e-05 | True      |           0.41 | False     |
| SCHOOL_BELONG | 3401 | -0.02014   | 0.005495  | 0.000359 | True      |           0.95 | False     |
| INFLDMN       | 2438 | -0.0001627 | 4.971e-05 | 0.00142  | True      |           0.29 | True      |
| BCENT10X      | 2438 | -0.1103    | 0.03586   | 0.00264  | True      |           0.64 | False     |
| IDG_LEQ1      | 2438 |  0.1714    | 0.05609   | 0.00281  | True      |           0.43 | False     |
| PRXPREST      | 2251 | -0.618     | 0.2168    | 0.00519  | True      |           0.35 | False     |

### H5ID4 — S5Q4 LIMIT CLIMB SEV. FLIGHT STAIRS—W5

N range across exposures: 2100–3457. Significant (p<0.05) exposures: 8 / 24.

| exposure      |    n |     beta |       se |       p | d1_pass   |   d4_rel_shift | d4_pass   |
|:--------------|-----:|---------:|---------:|--------:|:----------|---------------:|:----------|
| IDGX2         | 2439 | -0.01068 | 0.002914 | 0.00038 | True      |           0.29 | True      |
| SCHOOL_BELONG | 3401 | -0.01068 | 0.003285 | 0.00147 | True      |           0.59 | False     |
| IDG_LEQ1      | 2439 |  0.1006  | 0.03263  | 0.00259 | True      |           0.24 | True      |
| BCENT10X      | 2439 | -0.05445 | 0.01798  | 0.00305 | True      |           0.4  | False     |
| PRXPREST      | 2252 | -0.3562  | 0.1257   | 0.00544 | True      |           0.21 | True      |
| IDG_ZERO      | 2439 |  0.111   | 0.04226  | 0.00985 | True      |           0.2  | True      |

### H5ID16 — S5Q16 HOW OFTEN TROUBLE SLEEPING—W5

N range across exposures: 2099–3456. Significant (p<0.05) exposures: 2 / 24.

| exposure              |    n |     beta |       se |       p | d1_pass   |   d4_rel_shift | d4_pass   |
|:----------------------|-----:|---------:|---------:|--------:|:----------|---------------:|:----------|
| SCHOOL_BELONG         | 3400 | -0.01961 | 0.007248 | 0.00772 | True      |           0.67 | False     |
| H1DA7                 | 3456 |  0.05439 | 0.02331  | 0.0211  | True      |           0.02 | True      |
| H1PR4                 | 3447 |  0.06331 | 0.03638  | 0.0842  | False     |           0.79 | False     |
| FRIEND_DISCLOSURE_ANY | 3456 |  0.08678 | 0.06187  | 0.163   | False     |           0.83 | False     |
| HAVEBMF               | 2437 |  0.08987 | 0.07042  | 0.205   | False     |           0.21 | True      |
| HAVEBFF               | 2437 | -0.08518 | 0.07125  | 0.234   | False     |           0.18 | True      |

### H5LM5 — S3Q5 CURRENTLY WORK—W5

N range across exposures: 2098–3455. Significant (p<0.05) exposures: 5 / 24.

| exposure           |    n |       beta |        se |      p | d1_pass   |   d4_rel_shift | d4_pass   |
|:-------------------|-----:|-----------:|----------:|-------:|:----------|---------------:|:----------|
| IDGX2              | 2436 | -0.00598   | 0.0023    | 0.0106 | True      |           0.22 | True      |
| REACH              | 2436 | -4.521e-05 | 1.879e-05 | 0.0177 | True      |           0.24 | True      |
| INFLDMN            | 2436 | -5.032e-05 | 2.096e-05 | 0.018  | True      |           0.29 | True      |
| SCHOOL_BELONG      | 3400 | -0.005075  | 0.002213  | 0.0234 | True      |           0.47 | False     |
| IDG_LEQ1           | 2436 |  0.04704   | 0.0236    | 0.0486 | True      |           0.23 | True      |
| FRIEND_CONTACT_SUM | 3455 | -0.002085  | 0.001259  | 0.1    | False     |           0.29 | True      |

### H5EC1 — S4Q1 INCOME PERS EARNINGS [W4–W5]—W5

N range across exposures: 2080–3417. Significant (p<0.05) exposures: 12 / 24.

| exposure           |    n |     beta |       se |        p | d1_pass   |   d4_rel_shift | d4_pass   |
|:-------------------|-----:|---------:|---------:|---------:|:----------|---------------:|:----------|
| ODGX2              | 2413 |  0.09958 | 0.0253   | 0.000144 | True      |           0.22 | True      |
| BCENT10X           | 2413 |  0.4606  | 0.1188   | 0.000179 | True      |           0.27 | True      |
| IDGX2              | 2413 |  0.07177 | 0.01855  | 0.000184 | True      |           0.21 | True      |
| FRIEND_CONTACT_SUM | 3417 |  0.03241 | 0.008431 | 0.000188 | True      |           0.21 | True      |
| REACH3             | 2413 |  0.0063  | 0.001714 | 0.000366 | True      |           0.27 | True      |
| IDG_LEQ1           | 2413 | -0.5272  | 0.1698   | 0.00241  | True      |           0.28 | True      |

## Cross-outcome robust candidates

Exposures appearing in top-3 (by lowest p among significant) for ≥3 outcomes:

- **IDGX2** (7 outcomes): H4BMI, H4WAIST, H4BMICLS, H5ID1, H5ID4, H5LM5, H5EC1
- **SCHOOL_BELONG** (5 outcomes): H5MN1, H5MN2, H5ID1, H5ID4, H5ID16
- **IDG_LEQ1** (4 outcomes): H4BMI, H4WAIST, H4BMICLS, H5ID4
- **IDG_ZERO** (4 outcomes): H4BMI, H4WAIST, H4BMICLS, H5MN2

## Task16 handoff

**Task16 handoff: ['IDGX2 → H4WAIST', 'IDGX2 → H4BMI', 'IDGX2 → H4BMICLS', 'ODGX2 → H5EC1']**

Each pair passes D1 (β significantly non-zero under primary spec) and D4 (β stable across nested adjustment sets to within 30%). Cross-reference with the cognitive-screening D2/D6/D7 results for the chosen exposures before committing to formal causal estimation.

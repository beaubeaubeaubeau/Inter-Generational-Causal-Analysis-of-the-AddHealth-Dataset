# Task 13 — Verification pass

## 1. Published-benchmark weighted means

| metric       |   observed |   published |   abs_diff |
|:-------------|-----------:|------------:|-----------:|
| pct_male     |   0.485741 |       0.508 |  0.0222595 |
| pct_NH_Black |   0.153033 |       0.161 |  0.0079675 |
| mean_AH_PVT  | 101.8      |     100.7   |  1.09976   |
| mean_IDGX2   |   4.64083  |       4.6   |  0.0408258 |

## 2. Reserve-code leakage assertion

- Columns checked: 32
- Columns with any out-of-valid-range values: **0**
- Detailed CSV: `tables/verification/13_reserve_leakage.csv`


## 3. Reserve-code sensitivity (CES-D handling)

| cesd_reserve_mode   |   beta_idgx2 |         se |         p |    n |
|:--------------------|-------------:|-----------:|----------:|-----:|
| na                  |   0.00926382 | 0.00376371 | 0.0153668 | 3268 |
| zero                |   0.00987424 | 0.00379344 | 0.0104925 | 3278 |
| category            |   0.00988658 | 0.00379375 | 0.0104053 | 3278 |

## 4. DEFF and cluster-SE / naive-SE ratio (primary spec)

| spec                      |   naive_se |   cluster_se |   se_ratio |   deff_proxy |
|:--------------------------|-----------:|-------------:|-----------:|-------------:|
| S01C IDGX2 -> W4_COG_COMP | 0.00321288 |   0.00376371 |    1.17145 |      1.37229 |

## 5. Negative-control OUTCOME: adult height (inches)

IDGX2 should not predict adult height if our adjustment set is adequate.

| outcome   |   beta_idgx2 |        se |          p |    n |
|:----------|-------------:|----------:|-----------:|-----:|
| HEIGHT_IN |   -0.0519605 | 0.0177052 | 0.00405062 | 3278 |

## 6. Negative-control EXPOSURE: American-Indian indicator (H1GI6C)

A baseline indicator with no theoretical link to cognitive outcomes — should be null under adjustment.

| exposure       |      beta |        se |        p |    n |
|:---------------|----------:|----------:|---------:|-----:|
| H1GI6C (AI/AN) | -0.058226 | 0.0630906 | 0.357759 | 4700 |

## 7. Attrition IPW re-fit of anchor model (S01C)

Stage-1 logit pseudo-R² = 0.0295, N = 3230.

| spec                    |   beta_idgx2 |         p |    n |
|:------------------------|-------------:|----------:|-----:|
| Primary (GSWGT4_2 only) |    0.00926   | 0.0154    | 3268 |
| With attrition IPW      |    0.0100135 | 0.0114588 | 3210 |

## 8. BH-FDR multiple-testing adjustment (primary family)

| spec              | term            |         beta |           p |   rank |   bh_threshold |        q_BH | reject_at_q0.05   |
|:------------------|:----------------|-------------:|------------:|-------:|---------------:|------------:|:------------------|
| S04_BCENT10X      | bcent10x        |  0.091102    | 3.18895e-05 |      1 |     0.00384615 | 0.000414563 | True              |
| S04_ODGX2_placebo | odgx2_placebo   |  0.0142335   | 0.000697334 |      2 |     0.00769231 | 0.00453267  | True              |
| S01C              | idgx2           |  0.00926382  | 0.0153668   |      3 |     0.0115385  | 0.0529963   | False             |
| S05_LEQ1          | idg_leq1        | -0.0817298   | 0.0163065   |      4 |     0.0153846  | 0.0529963   | False             |
| S10_disclose      | friend_disclose |  0.0399753   | 0.104062    |      5 |     0.0192308  | 0.270562    | False             |
| S04_PRXPREST      | prxprest        |  0.38252     | 0.210293    |      6 |     0.0230769  | 0.422006    | False             |
| S06               | school_belong   |  0.00359194  | 0.264539    |      7 |     0.0269231  | 0.422006    | False             |
| S10_nominees      | friend_n        |  0.00483105  | 0.285633    |      8 |     0.0307692  | 0.422006    | False             |
| S01               | idgx2           |  0.0114587   | 0.292158    |      9 |     0.0346154  | 0.422006    | False             |
| S05_ZERO          | idg_zero        | -0.0441557   | 0.39412     |     10 |     0.0384615  | 0.512355    | False             |
| S10_contact       | friend_contact  |  0.00134161  | 0.439562    |     11 |     0.0423077  | 0.515052    | False             |
| S04_REACH         | reach           |  2.69539e-05 | 0.475432    |     12 |     0.0461538  | 0.515052    | False             |
| S07               | lonely          |  0.00394381  | 0.844739    |     13 |     0.05       | 0.844739    | False             |

## 9. Weight sums and PSU counts

- Sum(GSWGT1) across W1 analytic = **17,595,668**
- Sum(GSWGT4_2) across W4 analytic = **22,014,038**

| frame                     |   n_psu |   n_rows |
|:--------------------------|--------:|---------:|
| W1 (all analytic_w1_full) |     132 |     5114 |
| W4 analytic               |     132 |     5114 |
| W4 with valid cognitive   |     132 |     5101 |
| W5 analytic (I/T modes)   |     131 |      824 |

## 10. CLUSTER2 missingness assertion

- W1 full: **0** rows missing CLUSTER2
- W4: **0** rows missing CLUSTER2
- W5: **0** rows missing CLUSTER2

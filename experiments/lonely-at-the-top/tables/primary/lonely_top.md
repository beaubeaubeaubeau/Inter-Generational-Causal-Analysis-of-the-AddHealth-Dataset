# lonely-at-the-top — primary results

WLS of each mid-life outcome on `[IDGX2_z, H1FS13_z, IDGX2_x_H1FS13, adj]`. Three nested adjustment tiers (L0 / L0+L1 / L0+L1+AHPVT). The interaction coefficient β₃ on `IDGX2_x_H1FS13` is the headline paradox test (β₃ ≠ 0 ⇒ paradox confirmed).


**Pre-flight note:** the median-split 2x2 of (IDGX2, H1FS13) has minimum cell N = 73, below the project positivity floor of N ≥ 150. The 2x2 is therefore abandoned for identification; this script reports the continuous interaction as the primary estimand. The 4-cell weighted means are still produced (`tables/sensitivity/lonely_top_2x2_descriptive.csv`) as a narrative aid, with the under-powered cells flagged.

## Per-outcome interaction β₃ (primary spec L0+L1+AHPVT)

| outcome   | outcome_label                            | outcome_group   |    n |   beta_inter |   se_inter |   p_inter |   ci_lo_inter |   ci_hi_inter | paradox_test_pass   |
|:----------|:-----------------------------------------|:----------------|-----:|-------------:|-----------:|----------:|--------------:|--------------:|:--------------------|
| H4BMI     | S27 BMI—W4                               | cardiometabolic | 3234 |     0.04416  |    0.1492  |     0.768 |      -0.2514  |       0.3397  | False               |
| H4WAIST   | S27 MEASURED WAIST (CM)—W4               | cardiometabolic | 3250 |     0.0984   |    0.3566  |     0.783 |      -0.6081  |       0.8049  | False               |
| H5MN1     | S13Q1 LAST MO NO CNTRL IMPORT THINGS—W5  | mental_health   | 2387 |    -0.00028  |    0.02658 |     0.992 |      -0.05295 |       0.05239 | False               |
| H5MN2     | S13Q2 LAST MO CONFID HANDLE PERS PBMS—W5 | mental_health   | 2380 |    -0.01803  |    0.02419 |     0.458 |      -0.06596 |       0.02991 | False               |
| H5ID1     | S5Q1 HOW IS GEN PHYSICAL HEALTH—W5       | functional      | 2438 |    -0.008622 |    0.02523 |     0.733 |      -0.05861 |       0.04137 | False               |


TBD interpretation: 0 / 5 outcomes show a significant interaction (paradox test passes). Inspect signs to determine whether high-pop/high-lonely is *worse* than additive for each outcome.


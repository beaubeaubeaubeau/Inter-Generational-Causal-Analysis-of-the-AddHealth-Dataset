# Sensitivity analyses

## 1. Weighted vs unweighted (primary exposures)

Any sign flip or |t_w/t_u| > 3 is flagged.

| spec                 |   beta_weighted |   se_weighted |   t_weighted |   p_weighted |   beta_unweighted |   se_unweighted |   t_unweighted |   p_unweighted | sign_flip   |   t_ratio |    n |
|:---------------------|----------------:|--------------:|-------------:|-------------:|------------------:|----------------:|---------------:|---------------:|:------------|----------:|-----:|
| IDGX2 linear         |     0.00926382  |   0.00376371  |      2.46135 |  0.0153668   |       0.0118533   |     0.00357215  |       3.31824  |    0.00122242  | False       |  0.741763 | 3268 |
| ODGX2 placebo        |     0.0142335   |   0.00408114  |      3.48764 |  0.000697334 |       0.0147814   |     0.00373758  |       3.95481  |    0.000134617 | False       |  0.881872 | 3268 |
| BCENT10X             |     0.091102    |   0.0210117   |      4.33577 |  3.18895e-05 |       0.100508    |     0.0197838   |       5.08034  |    1.51848e-06 | False       |  0.853441 | 3268 |
| REACH                |     2.69539e-05 |   3.76409e-05 |      0.71608 |  0.475432    |       5.00356e-05 |     3.78053e-05 |       1.32351  |    0.188362    | False       |  0.541047 | 3268 |
| Isolation (<=1)      |    -0.0817298   |   0.0335122   |     -2.4388  |  0.0163065   |      -0.091706    |     0.0319038   |      -2.87446  |    0.0048444   | False       |  0.848441 | 3268 |
| School belong (full) |     0.00359194  |   0.00320558  |      1.12053 |  0.264539    |       0.00142698  |     0.00285786  |       0.499318 |    0.618393    | False       |  2.24412  | 4629 |

## 2. Collinearity among network centrality measures

Variance-inflation factors:

| variable   |     VIF |
|:-----------|--------:|
| IDGX2      | 1.64379 |
| ODGX2      | 5.62042 |
| BCENT10X   | 5.26831 |
| REACH      | 1.23594 |
| PRXPREST   | 1.80332 |

Pairwise Pearson correlations:

|          |   IDGX2 |   ODGX2 |   BCENT10X |   REACH |   PRXPREST |
|:---------|--------:|--------:|-----------:|--------:|-----------:|
| IDGX2    |   1     |   0.388 |      0.398 |   0.042 |      0.543 |
| ODGX2    |   0.388 |   1     |      0.889 |   0.268 |      0.337 |
| BCENT10X |   0.398 |   0.889 |      1     |   0.251 |      0.219 |
| REACH    |   0.042 |   0.268 |      0.251 |   1     |     -0.216 |
| PRXPREST |   0.543 |   0.337 |      0.219 |  -0.216 |      1     |

## 3. Permutation placebo: IDGX2 within-PSU shuffle (500 reps)

- **Observed β (IDGX2 -> W4_COG_COMP)**: 0.0093
- **Permutation p-value** (two-sided): 0.016
- **Permuted null**: mean=0.0013, SD=0.0035, 95%: [-0.0055, 0.0086]

## 4. AHPVT bad-control shift

Percent shrinkage = (β_without − β_with) / β_without. Values >0.5 are flagged as suggestive of mediation (AHPVT may be on the causal pathway rather than a confounder).

| outcome     | term            |   beta_with_ahpvt |   beta_without_ahpvt |   pct_shrinkage_from_adjustment | flag_large_shift   |
|:------------|:----------------|------------------:|---------------------:|--------------------------------:|:-------------------|
| C4WD90_1    | idgx2           |       0.0114587   |          0.0120632   |                       0.0501086 | False              |
| W4_COG_COMP | bcent10x        |       0.091102    |          0.107946    |                       0.156039  | False              |
| W4_COG_COMP | friend_contact  |       0.00134161  |          0.00395739  |                       0.660985  | True               |
| W4_COG_COMP | friend_disclose |       0.0399753   |          0.118584    |                       0.662895  | True               |
| W4_COG_COMP | friend_n        |       0.00483105  |          0.00923177  |                       0.476693  | False              |
| W4_COG_COMP | idg_leq1        |      -0.0817298   |         -0.101187    |                       0.192286  | False              |
| W4_COG_COMP | idg_zero        |      -0.0441557   |         -0.0602902   |                       0.267615  | False              |
| W4_COG_COMP | idgx2           |       0.00926382  |          0.0103986   |                       0.109129  | False              |
| W4_COG_COMP | odgx2_placebo   |       0.0142335   |          0.017941    |                       0.206646  | False              |
| W4_COG_COMP | prxprest        |       0.38252     |          0.206605    |                      -0.851454  | True               |
| W4_COG_COMP | reach           |       2.69539e-05 |          0.000117276 |                       0.770167  | True               |
| W4_COG_COMP | school_belong   |       0.00359194  |          0.00298452  |                      -0.203525  | False              |

## 5. Saturated-school selection balance

Mean of baseline covariates in respondents with vs. without W1 network data. Large differences imply generalizability caveats.

| variable   |   ('mean', 'in_network') |   ('mean', 'out_network') |   ('n', 'in_network') |   ('n', 'out_network') |
|:-----------|-------------------------:|--------------------------:|----------------------:|-----------------------:|
| AH_RAW     |                   65.541 |                    63.215 |                  4213 |                   2010 |
| BIO_SEX    |                    1.525 |                     1.498 |                  4397 |                   2106 |
| H1GH1      |                    2.073 |                     2.161 |                  4396 |                   2100 |
| H1GI4      |                    0.091 |                     0.164 |                  4385 |                   2096 |
| H1GI6B     |                    0.269 |                     0.208 |                  4389 |                   2096 |
| PA12       |                    5.689 |                     5.339 |                  3830 |                   1780 |
| PA55       |                   45.862 |                    45.715 |                  3360 |                   1557 |

## 6. W5 mode-selection probit

P(cognitive-eligible mode: in-person or phone) ~ IDGX2 + male + AHPVT.
N = 2,819; pseudo-R² = 0.0115

| term   |       coef |         se |        z |           p |
|:-------|-----------:|-----------:|---------:|------------:|
| const  | -0.214474  | 0.175205   | -1.22413 | 0.220904    |
| idgx2  | -0.0229391 | 0.00810315 | -2.83089 | 0.00464185  |
| male   |  0.127516  | 0.0563103  |  2.26452 | 0.0235422   |
| ahpvt  | -0.0101334 | 0.00262775 | -3.85632 | 0.000115106 |

**Interpretation.** If IDGX2's probit coefficient is near zero, W5 mode restriction is unlikely to bias the W1→W5 regression on network position.

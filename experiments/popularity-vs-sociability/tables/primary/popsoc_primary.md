# EXP-POPSOC — popularity vs. sociability primary results

Per-outcome WLS β for `IDGX2` (popularity) and `ODGX2` (sociability), fit in **separate** regressions with cluster-robust SE on `CLUSTER2`. The cross-exposure contrast `Δβ = β_in − β_out` per outcome is from a paired cluster-bootstrap (N=200 iterations, seed=20260427).

**Adjustment-set inheritance:** L0+L1+AHPVT for cognitive + cardiometabolic; L0+L1 for mental / functional / SES (SES drops AHPVT under DAG-SES). See [dag.md](../../dag.md) for the full table.

## Per-(exposure, outcome) cells

| exposure   | outcome     | outcome_group   |    n |      beta |       se |      ci_lo |      ci_hi |        p | sig   |
|:-----------|:------------|:----------------|-----:|----------:|---------:|-----------:|-----------:|---------:|:------|
| IDGX2      | W4_COG_COMP | cognitive       | 3268 |  0.009264 | 0.003764 |  0.001807  |  0.01672   | 0.0154   | True  |
| IDGX2      | H4BMI       | cardiometabolic | 3234 | -0.1999   | 0.03186  | -0.263     | -0.1367    | 6.83e-09 | True  |
| IDGX2      | H4WAIST     | cardiometabolic | 3250 | -0.5138   | 0.06877  | -0.6501    | -0.3776    | 1.87e-11 | True  |
| IDGX2      | H4SBP       | cardiometabolic | 3197 | -0.08417  | 0.07568  | -0.2341    |  0.06578   | 0.268    | False |
| IDGX2      | H4DBP       | cardiometabolic | 3197 | -0.09308  | 0.05382  | -0.1997    |  0.01356   | 0.0865   | False |
| IDGX2      | H4BMICLS    | cardiometabolic | 3234 | -0.03228  | 0.005518 | -0.04321   | -0.02135   | 4.97e-08 | True  |
| IDGX2      | H5MN1       | mental_health   | 2489 | -0.01235  | 0.006614 | -0.02545   |  0.0007562 | 0.0645   | False |
| IDGX2      | H5MN2       | mental_health   | 2482 |  0.01066  | 0.005466 | -0.0001647 |  0.02149   | 0.0535   | False |
| IDGX2      | H5ID1       | functional      | 2542 | -0.02198  | 0.00472  | -0.03133   | -0.01263   | 8.89e-06 | True  |
| IDGX2      | H5ID4       | functional      | 2542 | -0.01047  | 0.002879 | -0.01618   | -0.004767  | 0.000418 | True  |
| IDGX2      | H5ID16      | functional      | 2541 |  0.004763 | 0.008712 | -0.0125    |  0.02202   | 0.586    | False |
| IDGX2      | H5LM5       | ses             | 2537 | -0.00626  | 0.002237 | -0.01069   | -0.001828  | 0.00605  | True  |
| IDGX2      | H5EC1       | ses             | 2515 |  0.0672   | 0.01876  |  0.03003   |  0.1044    | 0.000506 | True  |
| ODGX2      | W4_COG_COMP | cognitive       | 3268 |  0.01423  | 0.004081 |  0.006147  |  0.02232   | 0.000697 | True  |
| ODGX2      | H4BMI       | cardiometabolic | 3234 | -0.008641 | 0.05466  | -0.1169    |  0.09966   | 0.875    | False |
| ODGX2      | H4WAIST     | cardiometabolic | 3250 | -0.1533   | 0.1226   | -0.3962    |  0.08957   | 0.214    | False |
| ODGX2      | H4SBP       | cardiometabolic | 3197 | -0.04473  | 0.08853  | -0.2201    |  0.1307    | 0.614    | False |
| ODGX2      | H4DBP       | cardiometabolic | 3197 | -0.00495  | 0.06719  | -0.1381    |  0.1282    | 0.941    | False |
| ODGX2      | H4BMICLS    | cardiometabolic | 3234 |  0.001625 | 0.009067 | -0.01634   |  0.01959   | 0.858    | False |
| ODGX2      | H5MN1       | mental_health   | 2489 | -0.01673  | 0.008815 | -0.0342    |  0.0007351 | 0.0603   | False |
| ODGX2      | H5MN2       | mental_health   | 2482 |  0.008848 | 0.007232 | -0.00548   |  0.02318   | 0.224    | False |
| ODGX2      | H5ID1       | functional      | 2542 | -0.01842  | 0.007305 | -0.03289   | -0.003944  | 0.0131   | True  |
| ODGX2      | H5ID4       | functional      | 2542 | -0.009385 | 0.00385  | -0.01701   | -0.001757  | 0.0164   | True  |
| ODGX2      | H5ID16      | functional      | 2541 | -0.004779 | 0.0108   | -0.02619   |  0.01663   | 0.659    | False |
| ODGX2      | H5LM5       | ses             | 2537 | -0.004214 | 0.003059 | -0.01027   |  0.001847  | 0.171    | False |
| ODGX2      | H5EC1       | ses             | 2515 |  0.09931  | 0.02505  |  0.04967   |  0.1489    | 0.00013  | True  |

## Paired bootstrap Δβ = β_in − β_out per outcome

| outcome     |   delta_beta |   delta_se_boot |   delta_ci_lo |   delta_ci_hi |   delta_p_boot |   n_boot_valid |
|:------------|-------------:|----------------:|--------------:|--------------:|---------------:|---------------:|
| W4_COG_COMP |    -0.00497  |        0.004156 |     -0.01252  |      0.003273 |          0.22  |            200 |
| H4BMI       |    -0.1912   |        0.05923  |     -0.3019   |     -0.08079  |          0.005 |            200 |
| H4WAIST     |    -0.3605   |        0.1133   |     -0.5951   |     -0.1651   |          0.005 |            200 |
| H4SBP       |    -0.03945  |        0.08042  |     -0.2087   |      0.09444  |          0.45  |            200 |
| H4DBP       |    -0.08813  |        0.06345  |     -0.2033   |      0.05974  |          0.16  |            200 |
| H4BMICLS    |    -0.0339   |        0.009122 |     -0.05157  |     -0.01632  |          0.005 |            200 |
| H5MN1       |     0.004382 |        0.01029  |     -0.01405  |      0.02483  |          0.59  |            200 |
| H5MN2       |     0.001817 |        0.007423 |     -0.01111  |      0.0171   |          0.75  |            200 |
| H5ID1       |    -0.003565 |        0.00646  |     -0.0159   |      0.008091 |          0.56  |            200 |
| H5ID4       |    -0.001086 |        0.003857 |     -0.00864  |      0.006518 |          0.74  |            200 |
| H5ID16      |     0.009541 |        0.01088  |     -0.01258  |      0.02927  |          0.34  |            200 |
| H5LM5       |    -0.002047 |        0.002796 |     -0.008066 |      0.002906 |          0.42  |            200 |
| H5EC1       |    -0.03211  |        0.02194  |     -0.07516  |      0.009517 |          0.12  |            200 |

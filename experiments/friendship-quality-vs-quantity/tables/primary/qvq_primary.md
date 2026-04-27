# EXP-QVQ -- friendship quality vs quantity, head-to-head joint fit

Per-outcome WLS beta for the three friendship-grid exposures, fit **JOINTLY** (same regression) so each beta is the marginal effect conditional on the other two friendship measures. Cluster-robust SE on `CLUSTER2`. Sample frame: full W1 in-home cohort. See [dag.md](../../dag.md) for the per-outcome adjustment-set inheritance.

| exposure              | outcome     | outcome_group   |    n |       beta |       se |     ci_lo |    ci_hi |      p | sig   |
|:----------------------|:------------|:----------------|-----:|-----------:|---------:|----------:|---------:|-------:|:------|
| FRIEND_DISCLOSURE_ANY | W4_COG_COMP | cognitive       | 4706 |  0.04515   | 0.02763  | -0.009506 | 0.0998   | 0.105  | False |
| FRIEND_N_NOMINEES     | W4_COG_COMP | cognitive       | 4706 |  0.008253  | 0.007625 | -0.00683  | 0.02334  | 0.281  | False |
| FRIEND_CONTACT_SUM    | W4_COG_COMP | cognitive       | 4706 | -0.002414  | 0.003198 | -0.008742 | 0.003913 | 0.452  | False |
| FRIEND_DISCLOSURE_ANY | H4BMI       | cardiometabolic | 4661 |  0.3295    | 0.3084   | -0.2806   | 0.9397   | 0.287  | False |
| FRIEND_N_NOMINEES     | H4BMI       | cardiometabolic | 4661 |  0.03738   | 0.08593  | -0.1326   | 0.2074   | 0.664  | False |
| FRIEND_CONTACT_SUM    | H4BMI       | cardiometabolic | 4661 | -0.06232   | 0.03817  | -0.1378   | 0.01319  | 0.105  | False |
| FRIEND_DISCLOSURE_ANY | H4WAIST     | cardiometabolic | 4685 |  0.4346    | 0.7917   | -1.132    | 2.001    | 0.584  | False |
| FRIEND_N_NOMINEES     | H4WAIST     | cardiometabolic | 4685 |  0.1336    | 0.2148   | -0.2914   | 0.5586   | 0.535  | False |
| FRIEND_CONTACT_SUM    | H4WAIST     | cardiometabolic | 4685 | -0.1337    | 0.08976  | -0.3112   | 0.04389  | 0.139  | False |
| FRIEND_DISCLOSURE_ANY | H4SBP       | cardiometabolic | 4605 |  0.4638    | 0.5251   | -0.575    | 1.502    | 0.379  | False |
| FRIEND_N_NOMINEES     | H4SBP       | cardiometabolic | 4605 | -0.01838   | 0.1563   | -0.3276   | 0.2909   | 0.907  | False |
| FRIEND_CONTACT_SUM    | H4SBP       | cardiometabolic | 4605 |  0.05398   | 0.06284  | -0.07034  | 0.1783   | 0.392  | False |
| FRIEND_DISCLOSURE_ANY | H4DBP       | cardiometabolic | 4605 |  0.1753    | 0.3995   | -0.6151   | 0.9657   | 0.662  | False |
| FRIEND_N_NOMINEES     | H4DBP       | cardiometabolic | 4605 | -0.03906   | 0.1324   | -0.301    | 0.2229   | 0.768  | False |
| FRIEND_CONTACT_SUM    | H4DBP       | cardiometabolic | 4605 |  0.05637   | 0.05522  | -0.05287  | 0.1656   | 0.309  | False |
| FRIEND_DISCLOSURE_ANY | H4BMICLS    | cardiometabolic | 4661 |  0.05404   | 0.05278  | -0.05038  | 0.1585   | 0.308  | False |
| FRIEND_N_NOMINEES     | H4BMICLS    | cardiometabolic | 4661 |  0.003811  | 0.01535  | -0.02655  | 0.03418  | 0.804  | False |
| FRIEND_CONTACT_SUM    | H4BMICLS    | cardiometabolic | 4661 | -0.009798  | 0.006487 | -0.02263  | 0.003035 | 0.133  | False |
| FRIEND_DISCLOSURE_ANY | H5MN1       | mental_health   | 3529 |  0.08373   | 0.05204  | -0.01921  | 0.1867   | 0.11   | False |
| FRIEND_N_NOMINEES     | H5MN1       | mental_health   | 3529 | -0.001377  | 0.01588  | -0.0328   | 0.03005  | 0.931  | False |
| FRIEND_CONTACT_SUM    | H5MN1       | mental_health   | 3529 | -0.002875  | 0.007324 | -0.01736  | 0.01161  | 0.695  | False |
| FRIEND_DISCLOSURE_ANY | H5MN2       | mental_health   | 3523 |  0.05328   | 0.04937  | -0.04437  | 0.1509   | 0.282  | False |
| FRIEND_N_NOMINEES     | H5MN2       | mental_health   | 3523 | -0.01045   | 0.01186  | -0.0339   | 0.01301  | 0.38   | False |
| FRIEND_CONTACT_SUM    | H5MN2       | mental_health   | 3523 |  0.009159  | 0.005229 | -0.001184 | 0.0195   | 0.0822 | False |
| FRIEND_DISCLOSURE_ANY | H5ID1       | functional      | 3601 | -0.0616    | 0.04916  | -0.1588   | 0.03565  | 0.212  | False |
| FRIEND_N_NOMINEES     | H5ID1       | functional      | 3601 | -0.01336   | 0.009609 | -0.03237  | 0.005651 | 0.167  | False |
| FRIEND_CONTACT_SUM    | H5ID1       | functional      | 3601 | -0.0007117 | 0.004497 | -0.009608 | 0.008185 | 0.874  | False |
| FRIEND_DISCLOSURE_ANY | H5ID4       | functional      | 3600 | -0.007684  | 0.0259   | -0.05893  | 0.04356  | 0.767  | False |
| FRIEND_N_NOMINEES     | H5ID4       | functional      | 3600 |  0.0006555 | 0.006858 | -0.01291  | 0.01422  | 0.924  | False |
| FRIEND_CONTACT_SUM    | H5ID4       | functional      | 3600 | -0.003776  | 0.002706 | -0.009129 | 0.001576 | 0.165  | False |
| FRIEND_DISCLOSURE_ANY | H5ID16      | functional      | 3600 |  0.1076    | 0.06886  | -0.02866  | 0.2438   | 0.121  | False |
| FRIEND_N_NOMINEES     | H5ID16      | functional      | 3600 | -0.02439   | 0.01526  | -0.05458  | 0.005802 | 0.112  | False |
| FRIEND_CONTACT_SUM    | H5ID16      | functional      | 3600 |  0.005659  | 0.006618 | -0.007433 | 0.01875  | 0.394  | False |
| FRIEND_DISCLOSURE_ANY | H5LM5       | ses             | 3596 | -0.004939  | 0.0185   | -0.04153  | 0.03165  | 0.79   | False |
| FRIEND_N_NOMINEES     | H5LM5       | ses             | 3596 |  0.0008434 | 0.004993 | -0.009034 | 0.01072  | 0.866  | False |
| FRIEND_CONTACT_SUM    | H5LM5       | ses             | 3596 | -0.002786  | 0.001939 | -0.006622 | 0.001049 | 0.153  | False |
| FRIEND_DISCLOSURE_ANY | H5EC1       | ses             | 3559 |  0.4358    | 0.17     |  0.09945  | 0.7722   | 0.0115 | True  |
| FRIEND_N_NOMINEES     | H5EC1       | ses             | 3559 | -0.002272  | 0.0375   | -0.07645  | 0.0719   | 0.952  | False |
| FRIEND_CONTACT_SUM    | H5EC1       | ses             | 3559 |  0.02961   | 0.01421  |  0.001494 | 0.05772  | 0.0392 | True  |

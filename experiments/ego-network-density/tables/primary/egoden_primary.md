# EXP-EGODEN — ego-network density at constant size

Per-outcome WLS β for the four ego-network density measures, fit in **separate** regressions with cluster-robust SE on `CLUSTER2`. **`REACH3` (egonet size) is in every adjustment set** — without this conditioning, β̂ confounds 'density effect' with 'smaller-network effect.' See [dag.md](../../dag.md) for the structural-holes-theoretic estimand.

| exposure   | outcome     | outcome_group   |    n |      beta |      se |    ci_lo |    ci_hi |        p | sig   |   beta_reach3 |   p_reach3 |
|:-----------|:------------|:----------------|-----:|----------:|--------:|---------:|---------:|---------:|:------|--------------:|-----------:|
| RCHDEN     | W4_COG_COMP | cognitive       | 3268 |  0.2113   | 0.142   | -0.07004 |  0.4926  | 0.14     | False |     0.0006291 |   0.0334   |
| RCHDEN     | H5MN1       | mental_health   | 2489 |  0.02806  | 0.2036  | -0.3754  |  0.4315  | 0.891    | False |    -0.0006302 |   0.252    |
| RCHDEN     | H5MN2       | mental_health   | 2482 |  0.006706 | 0.2005  | -0.3906  |  0.4041  | 0.973    | False |     0.0002926 |   0.51     |
| RCHDEN     | H5ID16      | functional      | 2541 |  0.0832   | 0.2346  | -0.3816  |  0.548   | 0.724    | False |     5.713e-05 |   0.931    |
| RCHDEN     | H5LM5       | ses             | 2537 | -0.01404  | 0.08965 | -0.1917  |  0.1636  | 0.876    | False |    -0.0002717 |   0.218    |
| RCHDEN     | H5EC1       | ses             | 2515 |  0.3423   | 0.8182  | -1.279   |  1.963   | 0.676    | False |     0.006831  |   0.000394 |
| ESDEN      | W4_COG_COMP | cognitive       | 2783 |  0.1201   | 0.08762 | -0.05353 |  0.2937  | 0.173    | False |     0.0008598 |   0.0625   |
| ESDEN      | H5MN1       | mental_health   | 2154 | -0.03704  | 0.1407  | -0.3158  |  0.2417  | 0.793    | False |    -0.0006808 |   0.362    |
| ESDEN      | H5MN2       | mental_health   | 2151 |  0.05613  | 0.1356  | -0.2125  |  0.3247  | 0.68     | False |     0.0002603 |   0.702    |
| ESDEN      | H5ID16      | functional      | 2195 | -0.1762   | 0.1807  | -0.5342  |  0.1818  | 0.332    | False |    -0.0009058 |   0.347    |
| ESDEN      | H5LM5       | ses             | 2192 | -0.09553  | 0.04649 | -0.1877  | -0.00341 | 0.0422   | True  |    -0.0005078 |   0.0485   |
| ESDEN      | H5EC1       | ses             | 2174 |  1.515    | 0.4423  |  0.6388  |  2.392   | 0.000859 | True  |     0.01043   |   1.92e-05 |
| ERDEN      | W4_COG_COMP | cognitive       | 3006 | -0.007126 | 0.06584 | -0.1376  |  0.1233  | 0.914    | False |     0.0006729 |   0.0187   |
| ERDEN      | H5MN1       | mental_health   | 2296 |  0.1216   | 0.1363  | -0.1485  |  0.3917  | 0.374    | False |    -0.0002185 |   0.715    |
| ERDEN      | H5MN2       | mental_health   | 2290 | -0.08273  | 0.111   | -0.3026  |  0.1371  | 0.457    | False |     0.0002092 |   0.651    |
| ERDEN      | H5ID16      | functional      | 2346 |  0.062    | 0.1506  | -0.2364  |  0.3604  | 0.681    | False |     0.0002327 |   0.718    |
| ERDEN      | H5LM5       | ses             | 2343 |  0.05836  | 0.04085 | -0.02257 |  0.1393  | 0.156    | False |    -0.0002065 |   0.304    |
| ERDEN      | H5EC1       | ses             | 2323 | -0.05     | 0.3444  | -0.7323  |  0.6323  | 0.885    | False |     0.006288  |   0.000508 |
| ESRDEN     | W4_COG_COMP | cognitive       | 3167 |  0.1623   | 0.1099  | -0.05539 |  0.38    | 0.142    | False |     0.001007  |   0.0056   |
| ESRDEN     | H5MN1       | mental_health   | 2419 |  0.1248   | 0.1923  | -0.2562  |  0.5059  | 0.518    | False |    -0.0002981 |   0.651    |
| ESRDEN     | H5MN2       | mental_health   | 2413 | -0.1127   | 0.1776  | -0.4646  |  0.2391  | 0.527    | False |    -1.059e-05 |   0.984    |
| ESRDEN     | H5ID16      | functional      | 2469 | -0.08943  | 0.2567  | -0.5981  |  0.4193  | 0.728    | False |    -0.0001713 |   0.81     |
| ESRDEN     | H5LM5       | ses             | 2466 |  0.01486  | 0.05917 | -0.1024  |  0.1321  | 0.802    | False |    -0.000251  |   0.22     |
| ESRDEN     | H5EC1       | ses             | 2444 |  1.283    | 0.6188  |  0.05736 |  2.509   | 0.0404   | True  |     0.008522  |   1.97e-06 |

# Task 05 - Survey-weighted univariate descriptives

Weights, PSUs, and formulas are documented in the 'Notes on design' footer.

## Sanity checks (W1, weight = GSWGT1)

| Check | Estimate | SE | 95% CI | N | Expectation |
|---|---|---|---|---|---|
| Weighted % male (BIO_SEX==1) | 0.5082 | 0.0084 | [0.4918, 0.5247] | 6503 | ~0.49-0.51 |
| Weighted % non-Hispanic Black (H1GI4==0 & H1GI6B==1) | 0.1609 | 0.0226 | [0.1214, 0.2101] | 6465 | ~0.14 |
| Weighted mean AH_PVT | 100.735 | 0.698 | [99.367, 102.104] | 6223 | ~100 |

## W1 exposures (network)

| Variable | Label | Kind | N | PSUs | Weighted mean / prop | SD | SE | 95% CI |
|---|---|---|---|---|---|---|---|---|
| IDGX2 | In-Degree: TFN | continuous (mean) | 4397 | 113 | 4.6063 | 3.7704 | 0.1176 | [4.3758, 4.8368] |
| ODGX2 | Out-Degree: TFN | continuous (mean) | 4397 | 113 | 4.5407 | 3.0682 | 0.1057 | [4.3336, 4.7478] |
| BCENT10X | Bonacich Centrality P=.1 | continuous (mean) | 4397 | 113 | 0.8085 | 0.6334 | 0.0117 | [0.7855, 0.8314] |
| REACH | N reachable alters: TFN | continuous (mean) | 4397 | 113 | 473.1927 | 431.2786 | 36.6737 | [401.3122, 545.0733] |
| REACH3 | N reachable alters 3 steps: TFN | continuous (mean) | 4397 | 113 | 57.3236 | 46.9018 | 2.4509 | [52.5199, 62.1273] |
| PRXPREST | Proximity Prestige | continuous (mean) | 4020 | 113 | 0.1672 | 0.0836 | 0.0073 | [0.1528, 0.1815] |
| HAVEBMF | R has a Best Male Friend | binary (prop) | 4397 | 113 | 0.5744 | NA | 0.0135 | [0.5478, 0.6006] |
| HAVEBFF | R has a best Female friend | binary (prop) | 4397 | 113 | 0.6136 | NA | 0.0155 | [0.5828, 0.6435] |
| BMFRECIP | Best Male Frnd Recip (any) | binary (prop) | 1963 | 113 | 0.5614 | NA | 0.0157 | [0.5304, 0.5919] |
| BFFRECIP | Best Female Frnd Recip.(any) | binary (prop) | 2313 | 112 | 0.6243 | NA | 0.0123 | [0.5999, 0.6480] |

## W1 friendship/belonging

| Variable | Label | Kind | N | PSUs | Weighted mean / prop | SD | SE | 95% CI |
|---|---|---|---|---|---|---|---|---|
| H1DA7 | S2Q7 HANG OUT WITH FRIENDS-W1 | continuous (mean) | 6498 | 132 | 1.9845 | 1.0114 | 0.0209 | [1.9435, 2.0256] |
| H1ED19 | S5Q19 FEEL CLOSE TO PEOPLE AT SCHOOL-W1 | continuous (mean) | 6366 | 132 | 2.2879 | 1.0054 | 0.0195 | [2.2497, 2.3261] |
| H1ED20 | S5Q20 FEEL PART OF YOUR SCHOOL-W1 | continuous (mean) | 6366 | 132 | 2.1612 | 1.0224 | 0.0235 | [2.1151, 2.2073] |
| H1ED21 | S5Q21 STUDENTS AT SCHOOL PREJUDICED-W1 | continuous (mean) | 6347 | 132 | 2.8608 | 1.1950 | 0.0448 | [2.7730, 2.9485] |
| H1ED22 | S5Q22 HAPPY AT YOUR SCHOOL-W1 | continuous (mean) | 6365 | 132 | 2.3127 | 1.1387 | 0.0259 | [2.2620, 2.3634] |
| H1ED23 | S5Q23 TEACHERS TREAT STUDENTS FAIRLY-W1 | continuous (mean) | 6367 | 132 | 2.5085 | 1.0837 | 0.0257 | [2.4582, 2.5589] |
| H1ED24 | S5Q24 FEEL SAFE IN YOUR SCHOOL-W1 | continuous (mean) | 6367 | 132 | 2.1960 | 1.0320 | 0.0351 | [2.1272, 2.2647] |

## W1 baseline cognitive & demographics

| Variable | Label | Kind | N | PSUs | Weighted mean / prop | SD | SE | 95% CI |
|---|---|---|---|---|---|---|---|---|
| AH_PVT | ADD HEALTH PICTURE VOCABULARY TEST SCORE | continuous (mean) | 6223 | 132 | 100.7353 | 15.1187 | 0.6980 | [99.3672, 102.1035] |
| BIO_SEX | BIOLOGICAL SEX-W1 | continuous (mean) | 6503 | 132 | 1.4918 | 0.4999 | 0.0084 | [1.4753, 1.5082] |
| H1GI4 | S1Q4 ARE YOU OF HISPANIC ORIGIN-W1 | binary (prop) | 6481 | 132 | 0.1224 | NA | 0.0179 | [0.0914, 0.1619] |
| H1GI6A | S1Q6A RACE-WHITE-W1 | binary (prop) | 6485 | 132 | 0.7385 | NA | 0.0254 | [0.6858, 0.7850] |
| H1GI6B | S1Q6B RACE-AFRICAN AMERICAN-W1 | binary (prop) | 6485 | 132 | 0.1645 | NA | 0.0226 | [0.1249, 0.2137] |
| H1GI6C | S1Q6C RACE-AMERICAN INDIAN-W1 | binary (prop) | 6485 | 132 | 0.0351 | NA | 0.0044 | [0.0274, 0.0448] |
| H1GI6D | S1Q6D RACE-ASIAN-W1 | binary (prop) | 6485 | 132 | 0.0357 | NA | 0.0070 | [0.0243, 0.0523] |
| H1GI6E | S1Q6E RACE-OTHER-W1 | binary (prop) | 6485 | 132 | 0.0709 | NA | 0.0106 | [0.0527, 0.0947] |
| CESD_SUM | DERIVED CES-D SUM (H1FS1-H1FS19, reverse 4/8/11/15) | continuous (mean) | 6457 | 132 | 10.9261 | 7.5016 | 0.1561 | [10.6203, 11.2320] |

## W4 cognitive

| Variable | Label | Kind | N | PSUs | Weighted mean / prop | SD | SE | 95% CI |
|---|---|---|---|---|---|---|---|---|
| C4WD90_1 | S14 # WORDS ON LIST RECALLED 90 SEC-W4 | continuous (mean) | 5101 | 132 | 6.6153 | 1.9889 | 0.0477 | [6.5218, 6.7089] |
| C4WD60_1 | S14 # WORDS ON LIST RECALLED 60 SEC-W4 | continuous (mean) | 5097 | 132 | 5.1805 | 2.0432 | 0.0591 | [5.0646, 5.2964] |
| C4NUMSCR | TOTAL SCORE ON NUMBER RECALL TASK-W4 | continuous (mean) | 5102 | 132 | 4.1516 | 1.5335 | 0.0443 | [4.0649, 4.2384] |

## W5 cognitive (mode-restricted subgroup)

| Variable | Label | Kind | N | PSUs | Weighted mean / prop | SD | SE | 95% CI |
|---|---|---|---|---|---|---|---|---|
| C5WD90_1 | S19 # WORDS ON LIST RECALLED 90 SEC-W5 | continuous (mean) | 623 | 130 | 6.0653 | 2.2394 | 0.1372 | [5.7963, 6.3342] |
| C5WD60_1 | S19 # WORDS ON LIST RECALLED 60 SEC-W5 | continuous (mean) | 620 | 130 | 4.4934 | 2.0672 | 0.1203 | [4.2576, 4.7291] |
| BDS_SCORE | DERIVED BACKWARD DIGIT SPAN (max length correct) | continuous (mean) | 625 | 130 | 4.9884 | 1.5385 | 0.0940 | [4.8041, 5.1727] |

## Notes on design

- **Weights / PSU.** W1 blocks use `GSWGT1` with PSU `CLUSTER2` (`w1weight.sas7bdat`); W4 cognitive uses the cross-sectional `GSWGT4_2` with `CLUSTER2` (`w4weight.sas7bdat`); W5 cognitive uses the cross-sectional `GSW5` with `CLUSTER2` (`p5weight.xpt`). Weights are applied on the pweight scale and are never normalized.
- **Reserve codes.** Values matching the usual Add Health reserve codes (refused / don't know / legitimate skip / NA / W5-not-asked; 6/7/8/9, 96/97/98/99, 995/996/997/998, 95/9995, etc.) are filtered by per-variable valid-range checks before computing any statistic.
- **Stratum.** The Add Health public-use release does not include the stratum identifier. It is therefore treated as None. Per Add Health documentation this has minimal impact on standard errors relative to the cluster-robust linearization that is applied here.
- **SE / CI.** For continuous variables a cluster-robust linearized (Taylor) SE with PSUs = `CLUSTER2` is used and a 95% CI is formed as mean +/- 1.96*SE. For binary indicators the 95% CI uses a logit transformation of the weighted proportion. `samplics` was not available in this environment; the manual implementation in this script is equivalent to Stata `svy, vce(linearized)` with `singleunit(missing)` for an un-stratified single-stage cluster design with pweights.
- **W5 cognitive subgroup.** W5 immediate word recall (`C5WD90_1`, `C5WD60_1`) and the derived backward digit span (`BDS_SCORE`) were administered only in the in-person / phone modes (variable `MODE`). The `GSW5` cross-sectional weight is still applied, so the reported weighted means and CIs describe the mode-eligible subgroup rather than the full W5 respondent population.

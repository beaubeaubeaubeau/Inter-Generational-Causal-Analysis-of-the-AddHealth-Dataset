# Task 3 (f, g, h): Wave III PVT, BEM items, and weights

## Task 3f — Wave III AHPVT repeat (`w3pvt.sas7bdat`)

- File: `data/W3/w3pvt.sas7bdat`
- Shape: 4,882 rows x 8 cols

### All variables

| var | label | dtype | n_nonmiss | min | max | mean | std |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `AID` | RESPONDENT IDENTIFIER | str | 4882 |  |  |  |  |
| `AH_RAW` | RAW AH_PVT SCORE | float64 | 4874 | 0.000 | 996.000 | 102.979 | 170.687 |
| `PVTPCT3` | CROSS-SECT/LONG PVT PERCENTILE RANK-W3 | float64 | 4874 | 0.000 | 996.000 | 84.482 | 176.261 |
| `PVTSTD3C` | CROSS-SECTIONAL STANDARDIZED SCORE-W3 | float64 | 4874 | 7.000 | 996.000 | 131.223 | 165.609 |
| `PVTSTD3L` | LONGITUDINAL STANDARDIZED SCORE-W3 | float64 | 4874 | 9.000 | 996.000 | 133.029 | 165.233 |
| `PVTPCT1C` | CROSS-SECTIONAL PVT PERCENTILE RANK-W1 | float64 | 4680 | 0.000 | 100.000 | 51.823 | 29.323 |
| `PVTPCT1L` | LONGITUDINAL PVT PERCENTILE RANK-W1 | float64 | 4512 | 0.000 | 100.000 | 51.065 | 29.329 |
| `PVTSTD1` | CROSS-SECT/LONG PVT STANDRDIZED SCORE-W1 | float64 | 4680 | 10.000 | 137.000 | 100.369 | 15.112 |

### Candidates

**Standardized AHPVT (analog of W1 `AH_PVT`):**
- `PVTSTD1` (label: 'CROSS-SECT/LONG PVT STANDRDIZED SCORE-W1') — mean=100.37, sd=15.11, range=[10.0, 137.0], n=4680

**Raw AHPVT (analog of W1 `AH_RAW`):**
- `AH_RAW` (label: 'RAW AH_PVT SCORE') — mean=102.98, sd=170.69, range=[0.0, 996.0], n=4874
- `PVTPCT1C` (label: 'CROSS-SECTIONAL PVT PERCENTILE RANK-W1') — mean=51.82, sd=29.32, range=[0.0, 100.0], n=4680
- `PVTPCT1L` (label: 'LONGITUDINAL PVT PERCENTILE RANK-W1') — mean=51.07, sd=29.33, range=[0.0, 100.0], n=4512

### Comparison to Wave I baseline

| var | n_nonmiss | min | max | mean | std |
| --- | ---: | ---: | ---: | ---: | ---: |
| `AH_PVT` | 6223 | 14.000 | 139.000 | 100.624 | 15.080 |
| `AH_RAW` | 6223 | 0.000 | 87.000 | 64.790 | 11.089 |

## Task 3g — Wave III BEM Sex-Role Inventory (`w3inhome.sas7bdat`)

- File: `data/W3/w3inhome.sas7bdat` (1831 variables)
- Keyword hits: 30
- Prefix hits (H3BE*/H3SE*/H3PR*): 87

### Keyword-hit variables (first 80)

| var | label | matched_kw |
| --- | --- | --- |
| `H3WP19` | S3Q19 CURR MOM-WARM/LOVING TO YOU-W3 | warm |
| `H3WP24` | S3Q24 CURR DAD-WARM/LOVING TO YOU-W3 | warm |
| `H3WP31` | S3Q31 PREV MOM-WARM/LOVING TO YOU-W3 | warm |
| `H3WP38` | S3Q38 PREV DAD-WARM/LOVING TO YOU-W3 | warm |
| `H3WP45` | S3Q45 BIO MOM-WARM/LOVING TO YOU-W3 | warm |
| `H3WP52` | S3Q52 BIO DAD-WARM/LOVING TO YOU-W3 | warm |
| `H3WP63` | S3Q63 DAD PRTNR-WARM/LOVING TO YOU-W3 | warm |
| `H3WP71` | S3Q71 MOM PRTNR-WARM/LOVING TO YOU-W3 | warm |
| `H3BM8` | S20Q8 TRADITIONAL SEX ROLES BEST-W3 | sex role |
| `H3BM9` | S20Q9 R DEFENDS BELIEFS-W3 | defend |
| `H3BM10` | S20Q10 R IS AFFECTIONATE-W3 | affection |
| `H3BM12` | S20Q12 R IS INDEPENDENT-W3 | independent |
| `H3BM13` | S20Q13 R IS SYMPATHETIC-W3 | sympath |
| `H3BM15` | S20Q15 R IS ASSERTIVE-W3 | assertive |
| `H3BM16` | S20Q16 R IS SENSITIVE TO OTHERS-W3 | sensitive |
| `H3BM18` | S20Q18 R HAS A STRONG PERSONALITY-W3 | strong personality |
| `H3BM21` | S20Q21 R IS FORCEFUL-W3 | forceful |
| `H3BM22` | S20Q22 R IS COMPASSIONATE-W3 | compassion |
| `H3BM24` | S20Q24 R HAS LEADERSHIP ABILITY-W3 | leadership |
| `H3BM27` | S20Q27 R IS WILLING TO TAKE RISKS-W3 | willing to take risk |
| `H3BM28` | S20Q28 R IS WARM-W3 | warm |
| `H3BM30` | S20Q30 R IS DOMINANT-W3 | dominant |
| `H3BM31` | S20Q31 R IS TENDER-W3 | tender |
| `H3BM33` | S20Q33 R IS WILLING TO TAKE A STAND-W3 | willing to take a stand |
| `H3BM34` | S20Q34 R LOVES CHILDREN-W3 | loves children |
| `H3BM36` | S20Q36 R IS AGGRESSIVE-W3 | aggressive |
| `H3TO72` | S28Q72 BINGE-WHO DOES IS INDEPENDENT-W3 | independent |
| `H3TO98` | S28Q98 SELF-HOW INDEPENDENT-W3 | independent |
| `H3RE17` | S31Q17 INDEPENDENT CHARIS/PENTECTL ID-W3 | independent |
| `H3IR2` | S35Q2 PERSONALITY ATTRACTIVENESS OF R-W3 | personality |

### Variables with label starting 'You are ...' / 'How much do you ...' (n=0)


### Sample H3BE*/H3SE*/H3PR* variables

| var | label |
| --- | --- |
| `H3SE1` | S16Q1 EVER HAVE SEX-W3 |
| `H3SE2` | S16Q2 AGE FIRST TIME SEX-W3 |
| `H3SE3` | S16Q3 TOTAL NUMBER OF SEX PRTNRS-W3 |
| `H3SE4` | S16Q4 PST 12 MTHS-TOT NO SEX PRTNRS-W3 |
| `H3SE5` | S16Q5 PST 12 MTHS-SEX PRTNR HAVE STD-W3 |
| `H3SE6` | S16Q6 PST 12 MTHS-TOT NO SEX INTRCRS-W3 |
| `H3SE7` | S16Q7 PST 12 MTHS-USE BIRTH CONTROL-W3 |
| `H3SE8` | S16Q8 PST 12 MTHS-OFTEN USE CONDOMS-W3 |
| `H3SE9` | S16Q9 MOST RECENT SEX-USE BRTH CTRL-W3 |
| `H3SE10` | S16Q10 MOST RECENT SEX-USE CONDOM |
| `H3SE11` | S16Q11 EVER ATTRACTED TO FEMALE-W3 |
| `H3SE12` | S16Q12 EVER ATTRACTED TO MALE-W3 |
| `H3SE13` | S16Q13 SEXUAL SELF DEFINITION-W3 |
| `H3SE14` | S16Q14 PARENT KNOWLDGE OF SEXUALITY-W3 |
| `H3SE15` | S16Q15 EVER PAID FOR SEX-W3 |
| `H3SE16` | S16Q16 PST 12 MTHS-FREQ OF PD FOR SEX-W3 |
| `H3SE17` | S16Q17 EVER BEEN PD FOR SEX-W3 |
| `H3SE18` | S16Q18 PST 12 MTHS-FREQ BEEN PD SEX-W3 |
| `H3SE19` | S16Q19 EVER HAD SEX W/DRUG NDLE USER-W3 |
| `H3SE20` | S16Q20 FREQ OF SEX W/DRUG NDLE USER-W3 |
| `H3SE21A` | S16Q21A PST 12 MTHS-DIAGN-CHLAMYDIA-W3 |
| `H3SE21B` | S16Q21B PST 12 MTHS-DIAGN-GONORRHEA-W3 |
| `H3SE21C` | S16Q21C PST 12 MTHS-DIAGN-TRICHMSIS-W3 |
| `H3SE21D` | S16Q21D PST 12 MTHS-DIAGN-SYPHILIS-W3 |
| `H3SE21E` | S16Q21E PST 12 MTHS-DIAGN-GEN HRPS-W3 |
| `H3SE21F` | S16Q21F PST 12 MTHS-DIAGN-GEN WRTS-W3 |
| `H3SE21G` | S16Q21G PST 12 MTHS-DIAGN-HPV-W3 |
| `H3SE21H` | S16Q21H PST 12 MTHS-DIAGN-VAGINOSIS-W3 |
| `H3SE21I` | S16Q21I PST 12 MTHS-DIAGN-PID-W3 |
| `H3SE21J` | S16Q21J PST 12 MTHS-DIAGN-CERV/MPC-W3 |
| `H3SE21K` | S16Q21K PST 12 MTHS-DIAGN-URTHRTS-W3 |
| `H3SE21L` | S16Q21L PST 12 MTHS-DIAGN-VAGINTS-W3 |
| `H3SE21M` | S16Q21M PST 12 MTHS-DIAGN-HIV/AIDS-W3 |
| `H3SE21N` | S16Q21N PST 12 MTHS-DIAGN-OTHER-W3 |
| `H3SE22A` | S16Q22A PST 12 MTHS-TEST-CHLAMYDIA-W3 |
| `H3SE22B` | S16Q22B PST 12 MTHS-TEST-GONORRHEA-W3 |
| `H3SE22C` | S16Q22C PST 12 MTHS-TEST-TRICHMSIS-W3 |
| `H3SE22D` | S16Q22D PST 12 MTHS-TEST-SYPHILIS-W3 |
| `H3SE22E` | S16Q22E PST 12 MTHS-TEST-GEN HRPS-W3 |
| `H3SE22F` | S16Q22F PST 12 MTHS-TEST-HPV-W3 |

### Verdict
- Variables with explicit BEM/masculine/feminine/gender-role label tokens: 1
- Variables matching BEM adjective keywords: 28

## Task 3h — Weight variable names across all waves

### Wave I — `data/W1/w1weight.sas7bdat`  (6,504 x 3)

| var | label | dtype | n_nonmiss | min | max | mean |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `AID` | RESPONDENT IDENTIFIER | str | 6504 |  |  |  |
| `CLUSTER2` | SAMPLE CLUSTER | float64 | 6504 | 102.000 | 472.000 | 185.143 |
| `GSWGT1` | GRAND SAMPLE WEIGHT-W1 | float64 | 6504 | 256.059 | 18385.486 | 3422.663 |

### Wave II — `data/W2/w2weight.sas7bdat`  (4,834 x 3)

| var | label | dtype | n_nonmiss | min | max | mean |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `AID` | RESPONDENT IDENTIFIER | str | 4834 |  |  |  |
| `CLUSTER2` | SAMPLE CLUSTER | float64 | 4834 | 102.000 | 472.000 | 189.778 |
| `GSWGT2` | GRAND SAMPLE WEIGHT-W2 | float64 | 4834 | 282.447 | 21107.100 | 3892.700 |

### Wave III (main) — `data/W3/w3weight.sas7bdat`  (4,882 x 4)

| var | label | dtype | n_nonmiss | min | max | mean |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `AID` | RESPONDENT IDENTIFIER | str | 4882 |  |  |  |
| `CLUSTER2` | SAMPLE CLUSTER | float64 | 4882 | 102.000 | 472.000 | 186.579 |
| `GSWGT3_2` | POSTSTRAT GS CROSS-SECTIONAL WGT-W3 | float64 | 4882 | 295.567 | 27327.077 | 4535.913 |
| `GSWGT3` | POSTSTRAT GS LONGITUDINAL WGT-W3 | float64 | 3844 | 324.947 | 27206.729 | 4872.606 |

### Wave III (edu subsample) — `data/W3/w3eduwgt.sas7bdat`  (3,964 x 3)

| var | label | dtype | n_nonmiss | min | max | mean |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `PTWGT3` | TRANSCRIPT LONGITUDINAL WEIGHT-PUBLIC | float64 | 3129 | 429.194 | 27914.030 | 5986.033 |
| `PTWGT3_2` | TRANSCRIPT CROSS-SECTIONAL WEIGHT-PUBLIC | float64 | 3964 | 374.730 | 27824.432 | 5586.359 |
| `AID` | RESPONDENT IDENTIFIER | str | 3964 |  |  |  |

### Wave IV — `data/W4/w4weight.sas7bdat`  (5,114 x 5)

| var | label | dtype | n_nonmiss | min | max | mean |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `AID` | RESPONDENT IDENTIFIER | str | 5114 |  |  |  |
| `CLUSTER2` | SAMPLE CLUSTER | float64 | 5114 | 102.000 | 472.000 | 184.641 |
| `GSWGT4` | POSTSTRAT GS LONGIT WGT-PUBLIC-W4 | float64 | 3342 | 331.797 | 30300.034 | 5543.782 |
| `GSWGT4_2` | POSTSTRAT GS CROSS_SECT WGT-PUBLIC-W4 | float64 | 5114 | 265.371 | 23039.521 | 4304.661 |
| `GSWGT134` | POSTSTRAT GS UNTRIMMED LONGIT WGT-W134 | float64 | 4208 | 303.206 | 30769.556 | 5205.752 |

### Wave V — `data/W5/p5weight.xpt`  (4,196 x 6)

| var | label | dtype | n_nonmiss | min | max | mean |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `AID` | RESPONDENT IDENTIFIER | str | 4196 |  |  |  |
| `CLUSTER2` | SAMPLE CLUSTER | float64 | 4196 | 102.000 | 472.000 | 185.883 |
| `GSW5` | CROSS-SECTION WGT WV ALL SP | float64 | 4196 | 77.415 | 29935.418 | 5167.794 |
| `GSW12345` | LONGTDNL WGT WI-II-III-IV-V ALL SP | float64 | 2499 | 147.531 | 127210.520 | 8677.861 |
| `GSW1345` | LONGTDNL WGT WI-III-IV-V ALL SP | float64 | 3147 | 119.541 | 91436.828 | 6890.999 |
| `GSW145` | LONGTDNL WGT WI-IV-V ALL SP | float64 | 3713 | 101.799 | 74654.867 | 5840.039 |

### Wave VI — `data/W6/p6weight.sas7bdat`  (3,937 x 5)

| var | label | dtype | n_nonmiss | min | max | mean |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `AID` | RESPONDENT IDENTIFIER NUMBER | str | 3937 |  |  |  |
| `CLUSTER2` | SAMPLE CLUSTER | float64 | 3937 | 102.000 | 472.000 | 185.802 |
| `GSW6` | WAVE 6 PUF CROSSSECTIONAL OPTIMIZED WEIGHT | float64 | 3937 | 102.618 | 56400.262 | 5390.082 |
| `GSW1456` | WAVE 6 PUF LONGITUDINAL OPTIMIZED WEIGHT (I-IV-V-VI) | float64 | 2996 | 102.613 | 46200.133 | 7083.029 |
| `GSW13456` | WAVE 6 PUF LONGITUDINAL OPTIMIZED WEIGHT (I-III-IV-V-VI) | float64 | 2571 | 158.044 | 48846.012 | 8253.891 |

### Consolidated weight mapping

| wave | file | var | label | n | mean |
| --- | --- | --- | --- | ---: | ---: |
| Wave I | w1weight.sas7bdat | `CLUSTER2` | SAMPLE CLUSTER | 6504 | 185.14 |
| Wave I | w1weight.sas7bdat | `GSWGT1` | GRAND SAMPLE WEIGHT-W1 | 6504 | 3422.66 |
| Wave II | w2weight.sas7bdat | `CLUSTER2` | SAMPLE CLUSTER | 4834 | 189.78 |
| Wave II | w2weight.sas7bdat | `GSWGT2` | GRAND SAMPLE WEIGHT-W2 | 4834 | 3892.70 |
| Wave III (main) | w3weight.sas7bdat | `CLUSTER2` | SAMPLE CLUSTER | 4882 | 186.58 |
| Wave III (main) | w3weight.sas7bdat | `GSWGT3_2` | POSTSTRAT GS CROSS-SECTIONAL WGT-W3 | 4882 | 4535.91 |
| Wave III (main) | w3weight.sas7bdat | `GSWGT3` | POSTSTRAT GS LONGITUDINAL WGT-W3 | 3844 | 4872.61 |
| Wave III (edu subsample) | w3eduwgt.sas7bdat | `PTWGT3` | TRANSCRIPT LONGITUDINAL WEIGHT-PUBLIC | 3129 | 5986.03 |
| Wave III (edu subsample) | w3eduwgt.sas7bdat | `PTWGT3_2` | TRANSCRIPT CROSS-SECTIONAL WEIGHT-PUBLIC | 3964 | 5586.36 |
| Wave IV | w4weight.sas7bdat | `CLUSTER2` | SAMPLE CLUSTER | 5114 | 184.64 |
| Wave IV | w4weight.sas7bdat | `GSWGT4` | POSTSTRAT GS LONGIT WGT-PUBLIC-W4 | 3342 | 5543.78 |
| Wave IV | w4weight.sas7bdat | `GSWGT4_2` | POSTSTRAT GS CROSS_SECT WGT-PUBLIC-W4 | 5114 | 4304.66 |
| Wave IV | w4weight.sas7bdat | `GSWGT134` | POSTSTRAT GS UNTRIMMED LONGIT WGT-W134 | 4208 | 5205.75 |
| Wave V | p5weight.xpt | `CLUSTER2` | SAMPLE CLUSTER | 4196 | 185.88 |
| Wave V | p5weight.xpt | `GSW5` | CROSS-SECTION WGT WV ALL SP | 4196 | 5167.79 |
| Wave V | p5weight.xpt | `GSW12345` | LONGTDNL WGT WI-II-III-IV-V ALL SP | 2499 | 8677.86 |
| Wave V | p5weight.xpt | `GSW1345` | LONGTDNL WGT WI-III-IV-V ALL SP | 3147 | 6891.00 |
| Wave V | p5weight.xpt | `GSW145` | LONGTDNL WGT WI-IV-V ALL SP | 3713 | 5840.04 |
| Wave VI | p6weight.sas7bdat | `CLUSTER2` | SAMPLE CLUSTER | 3937 | 185.80 |
| Wave VI | p6weight.sas7bdat | `GSW6` | WAVE 6 PUF CROSSSECTIONAL OPTIMIZED WEIGHT | 3937 | 5390.08 |
| Wave VI | p6weight.sas7bdat | `GSW1456` | WAVE 6 PUF LONGITUDINAL OPTIMIZED WEIGHT (I-IV-V-VI) | 2996 | 7083.03 |
| Wave VI | p6weight.sas7bdat | `GSW13456` | WAVE 6 PUF LONGITUDINAL OPTIMIZED WEIGHT (I-III-IV-V-VI) | 2571 | 8253.89 |

### Presence check for names referenced in the companion report

| flagged_name | present? | in_wave/file |
| --- | --- | --- |
| `CORE1` | NO | — |
| `CORE2` | NO | — |
| `GSW12345` | YES | Wave V (p5weight.xpt) |
| `GSW1345` | YES | Wave V (p5weight.xpt) |
| `GSW145` | YES | Wave V (p5weight.xpt) |
| `GSW5` | YES | Wave V (p5weight.xpt) |
| `HIEDBLK` | NO | — |

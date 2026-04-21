# Task 4: Missingness Profile

Per-variable missingness for the Add Health public-use feasibility sweep. Reserve codes (refused / legitimate skip / don't know / not applicable / Wave V 'question not asked') are tallied separately from true NA.

- CSV: `outputs/04_missingness_profile.csv`
- Sources: `w1network.sas7bdat`, `w1inhome.sas7bdat`, `w3pvt.sas7bdat`, `w4inhome.sas7bdat`, `pwave5.xpt`

## Block: W1 network (exposures) — `w1network.sas7bdat`

| variable | label | n_total | n_valid | %miss | %ref | %skip | %dk | %na | %notAsk | min | max | mean | median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `IDGX2` | In-Degree: TFN | 6504 | 4397 | 32.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 30.00 | 4.551 | 4.00 |
| `ODGX2` | Out-Degree: TFN | 6504 | 4397 | 32.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 10.00 | 4.458 | 4.00 |
| `BCENT10X` | Bonacich Centrality P=.1 | 6504 | 4397 | 32.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 4.29 | 0.792 | 0.72 |
| `REACH` | N reachable alters: TFN | 6504 | 4397 | 32.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1791.00 | 474.572 | 387.00 |
| `REACH3` | N reachable alters 3 steps: TFN | 6504 | 4328 | 32.40 | 0.23 | 0.28 | 0.34 | 0.22 | 0.00 | 0.00 | 264.00 | 56.004 | 49.00 |
| `IGDMEAN` | mean dist to reachable alters | 6504 | 3705 | 43.04 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 21.39 | 5.284 | 5.17 |
| `PRXPREST` | Proximity Prestige | 6504 | 4020 | 38.19 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.77 | 0.161 | 0.16 |
| `INFLDMN` | Influence Domain | 6504 | 4397 | 32.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1705.00 | 474.343 | 406.00 |
| `RCHDEN` | Density at maximum Reach | 6504 | 4397 | 32.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.16 | 0.96 | 0.706 | 0.76 |
| `HAVEBMF` | R has a Best Male Friend | 6504 | 4397 | 32.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.548 | 1.00 |
| `HAVEBFF` | R has a best Female friend | 6504 | 4397 | 32.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.605 | 1.00 |
| `BMFRECIP` | Best Male Frnd Recip (any) | 6504 | 1963 | 69.82 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.544 | 1.00 |
| `BFFRECIP` | Best Female Frnd Recip.(any) | 6504 | 2313 | 64.44 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.627 | 1.00 |
| `ISOLATED_derived` | Derived: IDGX2==0 AND ODGX2==0 | 6504 | 4397 | 32.40 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.035 | 0.00 |

### Derived: `ISOLATED_derived` = (IDGX2 == 0 AND ODGX2 == 0)

- Rate among observed: 3.48% of respondents with both IDGX2 and ODGX2 are fully isolated.

## Block: W1 friendship grid (first 5 vars per gender)

Full H1MF* block has 45 variables; H1FF* has 45. These name a 9-item x 5-nominee grid (per gender). The grid starts at `H1MFnA`/`H1FFnA` for friend 1. There is NO `H1MF1` / `H1FF1` — the 'nomination indicator' for friend 1 is the presence of any non-missing value on the first nominee's block (e.g. `H1MF2A`).

Full H1MF variable list:

`H1MF10A`, `H1MF10B`, `H1MF10C`, `H1MF10D`, `H1MF10E`, `H1MF2A`, `H1MF2B`, `H1MF2C`, `H1MF2D`, `H1MF2E`, `H1MF3A`, `H1MF3B`, `H1MF3C`, `H1MF3D`, `H1MF3E`, `H1MF4A`, `H1MF4B`, `H1MF4C`, `H1MF4D`, `H1MF4E`, `H1MF5A`, `H1MF5B`, `H1MF5C`, `H1MF5D`, `H1MF5E`, `H1MF6A`, `H1MF6B`, `H1MF6C`, `H1MF6D`, `H1MF6E`, `H1MF7A`, `H1MF7B`, `H1MF7C`, `H1MF7D`, `H1MF7E`, `H1MF8A`, `H1MF8B`, `H1MF8C`, `H1MF8D`, `H1MF8E`, `H1MF9A`, `H1MF9B`, `H1MF9C`, `H1MF9D`, `H1MF9E`

Full H1FF variable list:

`H1FF10A`, `H1FF10B`, `H1FF10C`, `H1FF10D`, `H1FF10E`, `H1FF2A`, `H1FF2B`, `H1FF2C`, `H1FF2D`, `H1FF2E`, `H1FF3A`, `H1FF3B`, `H1FF3C`, `H1FF3D`, `H1FF3E`, `H1FF4A`, `H1FF4B`, `H1FF4C`, `H1FF4D`, `H1FF4E`, `H1FF5A`, `H1FF5B`, `H1FF5C`, `H1FF5D`, `H1FF5E`, `H1FF6A`, `H1FF6B`, `H1FF6C`, `H1FF6D`, `H1FF6E`, `H1FF7A`, `H1FF7B`, `H1FF7C`, `H1FF7D`, `H1FF7E`, `H1FF8A`, `H1FF8B`, `H1FF8C`, `H1FF8D`, `H1FF8E`, `H1FF9A`, `H1FF9B`, `H1FF9C`, `H1FF9D`, `H1FF9E`

| variable | label | n_total | n_valid | %miss | %ref | %skip | %dk | %na | %notAsk | min | max | mean | median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `H1MF10A` | S20Q10A MALE FRIEND1-TALK ON PHONE-W1 | 6504 | 5967 | 0.00 | 0.02 | 8.24 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.703 | 1.00 |
| `H1MF10B` | S20Q10B MALE FRIEND2-TALK ON PHONE-W1 | 6504 | 6504 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.00 | 5.576 | 7.00 |
| `H1MF10C` | S20Q10C MALE FRIEND3-TALK ON PHONE-W1 | 6504 | 6504 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.00 | 5.861 | 7.00 |
| `H1MF10D` | S20Q10D MALE FRIEND4-TALK ON PHONE-W1 | 6504 | 6504 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.00 | 6.174 | 7.00 |
| `H1MF10E` | S20Q10E MALE FRIEND5-TALK ON PHONE-W1 | 6504 | 6504 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.00 | 6.421 | 7.00 |
| `H1FF10A` | S20Q10A FEMALE FRIEND1-TALK ON PHONE-W1 | 6504 | 5774 | 0.00 | 0.03 | 11.19 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.770 | 1.00 |
| `H1FF10B` | S20Q10B FEMALE FRIEND2-TALK ON PHONE-W1 | 6504 | 6504 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.00 | 5.688 | 7.00 |
| `H1FF10C` | S20Q10C FEMALE FRIEND3-TALK ON PHONE-W1 | 6504 | 6504 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.00 | 5.982 | 7.00 |
| `H1FF10D` | S20Q10D FEMALE FRIEND4-TALK ON PHONE-W1 | 6504 | 6504 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 9.00 | 6.318 | 7.00 |
| `H1FF10E` | S20Q10E FEMALE FRIEND5-TALK ON PHONE-W1 | 6504 | 6504 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.00 | 6.522 | 7.00 |

## Block: W1 in-home activity + school belonging

| variable | label | n_total | n_valid | %miss | %ref | %skip | %dk | %na | %notAsk | min | max | mean | median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `H1DA7` | S2Q7 HANG OUT WITH FRIENDS-W1 | 6504 | 6498 | 0.00 | 0.03 | 0.00 | 0.06 | 0.00 | 0.00 | 0.00 | 3.00 | 1.971 | 2.00 |
| `H1ED19` | S5Q19 FEEL CLOSE TO PEOPLE AT SCHOOL-W1 | 6504 | 6366 | 0.00 | 0.06 | 1.97 | 0.09 | 0.00 | 0.00 | 1.00 | 5.00 | 2.295 | 2.00 |
| `H1ED20` | S5Q20 FEEL PART OF YOUR SCHOOL-W1 | 6504 | 6366 | 0.00 | 0.06 | 1.97 | 0.09 | 0.00 | 0.00 | 1.00 | 5.00 | 2.149 | 2.00 |
| `H1ED21` | S5Q21 STUDENTS AT SCHOOL PREJUDICED-W1 | 6504 | 6347 | 0.00 | 0.06 | 1.97 | 0.38 | 0.00 | 0.00 | 1.00 | 5.00 | 2.907 | 3.00 |
| `H1ED22` | S5Q22 HAPPY AT YOUR SCHOOL-W1 | 6504 | 6365 | 0.00 | 0.08 | 1.97 | 0.09 | 0.00 | 0.00 | 1.00 | 5.00 | 2.321 | 2.00 |
| `H1ED23` | S5Q23 TEACHERS TREAT STUDENTS FAIRLY-W1 | 6504 | 6367 | 0.00 | 0.06 | 1.97 | 0.08 | 0.00 | 0.00 | 1.00 | 5.00 | 2.518 | 2.00 |
| `H1ED24` | S5Q24 FEEL SAFE IN YOUR SCHOOL-W1 | 6504 | 6367 | 0.00 | 0.06 | 1.97 | 0.08 | 0.00 | 0.00 | 1.00 | 5.00 | 2.192 | 2.00 |

## Block: W1 CES-D items (`H1FS1`..`H1FS19`) + derived sum

| variable | label | n_total | n_valid | %miss | %ref | %skip | %dk | %na | %notAsk | min | max | mean | median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `H1FS1` | S10Q1 BOTHERED BY THINGS-W1 | 6504 | 6482 | 0.00 | 0.09 | 0.00 | 0.25 | 0.00 | 0.00 | 0.00 | 3.00 | 0.492 | 0.00 |
| `H1FS2` | S10Q2 POOR APPETITE-W1 | 6504 | 6487 | 0.00 | 0.09 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 3.00 | 0.460 | 0.00 |
| `H1FS3` | S10Q3 HAD THE BLUES-W1 | 6504 | 6480 | 0.00 | 0.09 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 | 3.00 | 0.381 | 0.00 |
| `H1FS4` | S10Q4 JUST AS GOOD AS OTHER PEOPLE-W1 | 6504 | 6483 | 0.00 | 0.09 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 3.00 | 1.932 | 2.00 |
| `H1FS5` | S10Q5 TROUBLE KEEPING MIND FOCUSED-W1 | 6504 | 6485 | 0.00 | 0.11 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 3.00 | 0.807 | 1.00 |
| `H1FS6` | S10Q6 FELT DEPRESSED-W1 | 6504 | 6484 | 0.00 | 0.12 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 3.00 | 0.512 | 0.00 |
| `H1FS7` | S10Q7 TOO TIRED TO DO THINGS-W1 | 6504 | 6487 | 0.00 | 0.09 | 0.00 | 0.17 | 0.00 | 0.00 | 0.00 | 3.00 | 0.724 | 1.00 |
| `H1FS8` | S10Q8 HOPEFUL ABOUT THE FUTURE-W1 | 6504 | 6475 | 0.00 | 0.09 | 0.00 | 0.35 | 0.00 | 0.00 | 0.00 | 3.00 | 1.845 | 2.00 |
| `H1FS9` | S10Q9 LIFE HAD BEEN A FAILURE-W1 | 6504 | 6477 | 0.00 | 0.14 | 0.00 | 0.28 | 0.00 | 0.00 | 0.00 | 3.00 | 0.208 | 0.00 |
| `H1FS10` | S10Q10 FEARFUL-W1 | 6504 | 6487 | 0.00 | 0.11 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 3.00 | 0.318 | 0.00 |
| `H1FS11` | S10Q11 HAPPY-W1 | 6504 | 6489 | 0.00 | 0.09 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | 3.00 | 2.127 | 2.00 |
| `H1FS12` | S10Q12 TALKED LESS THAN USUAL-W1 | 6504 | 6485 | 0.00 | 0.11 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 3.00 | 0.561 | 0.00 |
| `H1FS13` | S10Q13 FELT LONELY-W1 | 6504 | 6485 | 0.00 | 0.11 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 3.00 | 0.464 | 0.00 |
| `H1FS14` | S10Q14 PEOPLE UNFRIENDLY TO YOU-W1 | 6504 | 6489 | 0.00 | 0.09 | 0.00 | 0.14 | 0.00 | 0.00 | 0.00 | 3.00 | 0.403 | 0.00 |
| `H1FS15` | S10Q15 ENJOYED LIFE-W1 | 6504 | 6486 | 0.00 | 0.12 | 0.00 | 0.15 | 0.00 | 0.00 | 0.00 | 3.00 | 2.245 | 2.00 |
| `H1FS16` | S10Q16 FELT SAD-W1 | 6504 | 6490 | 0.00 | 0.09 | 0.00 | 0.12 | 0.00 | 0.00 | 0.00 | 3.00 | 0.564 | 0.00 |
| `H1FS17` | S10Q17 FELT PEOPLE DISLIKE YOU-W1 | 6504 | 6486 | 0.00 | 0.09 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 3.00 | 0.420 | 0.00 |
| `H1FS18` | S10Q18 HARD TO START DOING THINGS-W1 | 6504 | 6484 | 0.00 | 0.11 | 0.00 | 0.20 | 0.00 | 0.00 | 0.00 | 3.00 | 0.615 | 1.00 |
| `H1FS19` | S10Q19 LIFE NOT WORTH LIVING-W1 | 6504 | 6485 | 0.00 | 0.11 | 0.00 | 0.18 | 0.00 | 0.00 | 0.00 | 3.00 | 0.159 | 0.00 |
| `CESD_SUM_derived` | Derived: sum of 19 CES-D items; items 4,8,11,15 reversed | 6504 | 6457 | 0.72 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 50.00 | 10.927 | 9.00 |

### Derived: `CESD_SUM_derived`

**Formula.** For each respondent, recode items **H1FS4, H1FS8, H1FS11, H1FS15** as `3 - x` (reverse-scoring positively-worded items); leave the other 15 items unchanged. Treat any value > 3 (i.e. reserve codes 6/7/8) as missing. The CES-D sum is the sum of all 19 recoded items, and is missing for any respondent with any missing item (strict complete-case). Expected range 0..57.

## Block: W1 cognitive baseline (AHPVT)

| variable | label | n_total | n_valid | %miss | %ref | %skip | %dk | %na | %notAsk | min | max | mean | median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `AH_PVT` | ADD HEALTH PICTURE VOCABULARY TEST SCORE | 6504 | 5503 | 4.32 | 2.64 | 3.61 | 2.34 | 2.48 | 0.00 | 14.00 | 139.00 | 101.044 | 103.00 |
| `AH_RAW` | RAW PICTURE VOCABULARY TEST SCORE | 6504 | 6223 | 4.32 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 87.00 | 64.790 | 65.00 |

## Block: W3 AHPVT

| variable | label | n_total | n_valid | %miss | %ref | %skip | %dk | %na | %notAsk | min | max | mean | median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `AH_RAW` | RAW AH_PVT SCORE | 4882 | 4703 | 0.16 | 3.50 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 87.00 | 70.509 | 74.00 |
| `PVTSTD3C` | CROSS-SECTIONAL STANDARDIZED SCORE-W3 | 4882 | 4703 | 0.16 | 3.50 | 0.00 | 0.00 | 0.00 | 0.00 | 7.00 | 122.00 | 99.780 | 104.00 |
| `PVTSTD3L` | LONGITUDINAL STANDARDIZED SCORE-W3 | 4882 | 4703 | 0.16 | 3.50 | 0.00 | 0.00 | 0.00 | 0.00 | 9.00 | 123.00 | 101.651 | 106.00 |

## Block: W4 cognitive

| variable | label | n_total | n_valid | %miss | %ref | %skip | %dk | %na | %notAsk | min | max | mean | median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `C4WD90_1` | S14 # WORDS ON LIST RECALLED 90 SEC-W4 | 5114 | 5101 | 0.04 | 0.12 | 0.00 | 0.00 | 0.10 | 0.00 | 0.00 | 15.00 | 6.659 | 7.00 |
| `C4WD60_1` | S14 # WORDS ON LIST RECALLED 60 SEC-W4 | 5114 | 5097 | 0.12 | 0.22 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 15.00 | 5.223 | 5.00 |
| `C4NUMSCR` | TOTAL SCORE ON NUMBER RECALL TASK-W4 | 5114 | 5102 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 7.00 | 4.187 | 4.00 |

## Block: W5 cognitive (overall)

| variable | label | n_total | n_valid | %miss | %ref | %skip | %dk | %na | %notAsk | min | max | mean | median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `C5WD90_1` | S19 # WORDS ON LIST RECALLED 90 SEC-W5 | 4196 | 623 | 0.05 | 0.02 | 0.00 | 0.00 | 0.02 | 85.06 | 1.00 | 15.00 | 6.199 | 6.00 |
| `C5WD60_1` | S19 # WORDS ON LIST RECALLED 60 SEC-W5 | 4196 | 620 | 0.05 | 0.10 | 0.00 | 0.00 | 0.02 | 85.06 | 0.00 | 12.00 | 4.650 | 5.00 |
| `H5MH3A` | S19Q3A NUMBER STRING/2-4-W5 | 4196 | 625 | 0.05 | 0.00 | 0.00 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.997 | 1.00 |
| `H5MH3B` | S19Q3B NUMBER STRING/5-7-W5 | 4196 | 2 | 0.05 | 0.00 | 14.85 | 0.00 | 0.00 | 85.06 | 0.00 | 0.00 | 0.000 | 0.00 |
| `H5MH4A` | S19Q4A NUMBER STRING/6-2-9-W5 | 4196 | 621 | 0.10 | 0.00 | 0.05 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.879 | 1.00 |
| `H5MH4B` | S19Q4B NUMBER STRING/4-1-5-W5 | 4196 | 76 | 0.07 | 0.00 | 13.06 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.789 | 1.00 |
| `H5MH5A` | S19Q5A NUMBER STRING/3-2-7-9-W5 | 4196 | 605 | 0.10 | 0.00 | 0.43 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.793 | 1.00 |
| `H5MH5B` | S19Q5B NUMBER STRING/4-9-6-8-W5 | 4196 | 126 | 0.07 | 0.00 | 11.87 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.460 | 0.00 |
| `H5MH6A` | S19Q6A NUMBER STRING/1-5-2-8-6-W5 | 4196 | 537 | 0.10 | 0.00 | 2.05 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.510 | 1.00 |
| `H5MH6B` | S19Q6B NUMBER STRING/6-1-8-4-3-W5 | 4196 | 264 | 0.07 | 0.00 | 8.58 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.424 | 0.00 |
| `H5MH7A` | S19Q7A NUMBER STRING/5-3-9-4-1-8-W5 | 4196 | 384 | 0.12 | 0.00 | 5.67 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.458 | 0.00 |
| `H5MH7B` | S19Q7B NUMBER STRING/7-2-4-8-5-6-W5 | 4196 | 208 | 0.12 | 0.00 | 9.87 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.380 | 0.00 |
| `H5MH8A` | S19Q8A NUMBER STRING/8-1-2-9-3-6-5-W5 | 4196 | 253 | 0.17 | 0.00 | 8.75 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.344 | 0.00 |
| `H5MH8B` | S19Q8B NUMBER STRING/4-7-3-9-1-2-8-W5 | 4196 | 166 | 0.17 | 0.00 | 10.82 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.295 | 0.00 |
| `H5MH9A` | S19Q9A NUMBER STRING/9-4-3-7-6-2-5-8-W5 | 4196 | 135 | 0.19 | 0.00 | 11.53 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.222 | 0.00 |
| `H5MH9B` | S19Q9B NUMBER STRING/7-2-8-1-9-6-5-3-W5 | 4196 | 103 | 0.95 | 0.00 | 11.53 | 0.00 | 0.00 | 85.06 | 0.00 | 1.00 | 0.165 | 0.00 |
| `W5_DIGIT_SPAN_derived` | Derived: max L in 2..8 with A==1 OR B==1, else 0 | 4196 | 625 | 85.10 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 8.00 | 5.142 | 5.00 |

### Derived: `W5_DIGIT_SPAN_derived`

**Formula.** For each length L in {2,3,4,5,6,7,8}, look at trials `H5MHLA` and `H5MHLB`. The score is the **maximum L** such that either trial scored 1 (correct). If no length has a correct trial, the score is 0. The score is missing only if both trials at EVERY length are NA (i.e. the backward digit span task was not administered to that respondent at all).

## Block: W5 cognitive missingness by `MODE`

MODE codes (per W5 codebook): **W=Web, I=In-person, M=Mail, T=Telephone/CATI, S=Spanish**. The Wave V mixed-mode design changed which cognitive items were asked per mode (web/mail had no DK/Refused option, so DK became silent NA).

### `C5WD90_1`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 523 | 72.34 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 100 | 99.01 |
| W | 3221 | 0 | 0.00 |

### `C5WD60_1`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 520 | 71.92 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 100 | 99.01 |
| W | 3221 | 0 | 0.00 |

### `H5MH3A`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 525 | 72.61 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 100 | 99.01 |
| W | 3221 | 0 | 0.00 |

### `H5MH3B`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 2 | 0.28 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 0 | 0.00 |
| W | 3221 | 0 | 0.00 |

### `H5MH4A`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 521 | 72.06 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 100 | 99.01 |
| W | 3221 | 0 | 0.00 |

### `H5MH4B`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 64 | 8.85 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 12 | 11.88 |
| W | 3221 | 0 | 0.00 |

### `H5MH5A`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 507 | 70.12 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 98 | 97.03 |
| W | 3221 | 0 | 0.00 |

### `H5MH5B`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 111 | 15.35 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 15 | 14.85 |
| W | 3221 | 0 | 0.00 |

### `H5MH6A`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 446 | 61.69 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 91 | 90.10 |
| W | 3221 | 0 | 0.00 |

### `H5MH6B`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 220 | 30.43 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 44 | 43.56 |
| W | 3221 | 0 | 0.00 |

### `H5MH7A`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 320 | 44.26 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 64 | 63.37 |
| W | 3221 | 0 | 0.00 |

### `H5MH7B`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 173 | 23.93 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 35 | 34.65 |
| W | 3221 | 0 | 0.00 |

### `H5MH8A`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 217 | 30.01 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 36 | 35.64 |
| W | 3221 | 0 | 0.00 |

### `H5MH8B`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 140 | 19.36 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 26 | 25.74 |
| W | 3221 | 0 | 0.00 |

### `H5MH9A`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 118 | 16.32 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 17 | 16.83 |
| W | 3221 | 0 | 0.00 |

### `H5MH9B`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 90 | 12.45 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 13 | 12.87 |
| W | 3221 | 0 | 0.00 |

### `W5_DIGIT_SPAN_derived`

| MODE | n_total | n_valid | pct_valid |
|---|---:|---:|---:|
| I | 723 | 525 | 72.61 |
| M | 147 | 0 | 0.00 |
| S | 4 | 0 | 0.00 |
| T | 101 | 100 | 99.01 |
| W | 3221 | 0 | 0.00 |

## Block: W1 confounders (sex, race, Hispanic origin)

| variable | label | n_total | n_valid | %miss | %ref | %skip | %dk | %na | %notAsk | min | max | mean | median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `BIO_SEX` | BIOLOGICAL SEX-W1 | 6504 | 6503 | 0.00 | 0.02 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 2.00 | 1.516 | 2.00 |
| `H1GI4` | S1Q4 ARE YOU OF HISPANIC ORIGIN-W1 | 6504 | 6481 | 0.00 | 0.05 | 0.00 | 0.31 | 0.00 | 0.00 | 0.00 | 1.00 | 0.115 | 0.00 |
| `H1GI6A` | S1Q6A RACE-WHITE-W1 | 6504 | 6485 | 0.00 | 0.06 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 1.00 | 0.662 | 1.00 |
| `H1GI6B` | S1Q6B RACE-AFRICAN AMERICAN-W1 | 6504 | 6485 | 0.00 | 0.06 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 1.00 | 0.250 | 0.00 |
| `H1GI6C` | S1Q6C RACE-AMERICAN INDIAN-W1 | 6504 | 6485 | 0.00 | 0.06 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 1.00 | 0.036 | 0.00 |
| `H1GI6D` | S1Q6D RACE-ASIAN-W1 | 6504 | 6485 | 0.00 | 0.06 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 1.00 | 0.042 | 0.00 |
| `H1GI6E` | S1Q6E RACE-OTHER-W1 | 6504 | 6485 | 0.00 | 0.06 | 0.00 | 0.23 | 0.00 | 0.00 | 0.00 | 1.00 | 0.066 | 0.00 |

## Block: W1 household income & parental education (search result)

Searched `w1inhome.sas7bdat` labels for 'household income', 'parental income', 'level of education', and '{mother,father,parent} education'. The hits below show the exact variables found in the merged in-home file (which includes Parent Questionnaire items prefixed `PA*`, `PB*`, `PC*`).

### Candidates from the feasibility report

| variable | present? | label |
|---|---|---|
| `PA55` | yes | A55 TOTAL HOUSEHOLD INCOME-PQ |
| `PA12` | yes | A12 LEVEL OF EDUCATION-PQ |
| `PB8` | yes | B8 EDUCATION LEVEL OF PARTNER-PQ |
| `H1NM4` | yes | S12Q4 EDUCATION LEVEL OF BIO MOM-W1 |
| `H1NF4` | yes | S13Q4 EDUCATION LEVEL OF BIO DAD-W1 |
| `H1RM1` | yes | S14Q1 RES MOM-EDUCATION LEVEL-W1 |
| `H1RF1` | yes | S15Q1 RES DAD-EDUCATION LEVEL-W1 |

### Additional label-search hits

| variable | label |
|---|---|
| `PA12` | A12 LEVEL OF EDUCATION-PQ |
| `PA55` | A55 TOTAL HOUSEHOLD INCOME-PQ |

### Missingness of the SES / parent-ed variables

| variable | label | n_total | n_valid | %miss | %ref | %skip | %dk | %na | %notAsk | min | max | mean | median |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `PA55` | A55 TOTAL HOUSEHOLD INCOME-PQ | 6504 | 4929 | 14.98 | 9.24 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 999.00 | 47.701 | 40.00 |
| `PA12` | A12 LEVEL OF EDUCATION-PQ | 6504 | 5613 | 13.61 | 0.09 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 10.00 | 5.580 | 6.00 |
| `PB8` | B8 EDUCATION LEVEL OF PARTNER-PQ | 6504 | 4120 | 14.31 | 0.15 | 22.19 | 0.00 | 0.00 | 0.00 | 1.00 | 12.00 | 5.681 | 6.00 |
| `H1NM4` | S12Q4 EDUCATION LEVEL OF BIO MOM-W1 | 6504 | 727 | 0.00 | 0.05 | 88.62 | 0.15 | 0.00 | 0.00 | 1.00 | 12.00 | 5.292 | 4.00 |
| `H1NF4` | S13Q4 EDUCATION LEVEL OF BIO DAD-W1 | 6504 | 2165 | 0.00 | 0.03 | 65.82 | 0.86 | 0.00 | 0.00 | 1.00 | 12.00 | 5.790 | 4.00 |
| `H1RM1` | S14Q1 RES MOM-EDUCATION LEVEL-W1 | 6504 | 6077 | 0.00 | 0.06 | 5.69 | 0.81 | 0.00 | 0.00 | 1.00 | 12.00 | 5.739 | 6.00 |
| `H1RF1` | S15Q1 RES DAD-EDUCATION LEVEL-W1 | 6504 | 4494 | 0.00 | 0.11 | 30.01 | 0.77 | 0.02 | 0.00 | 1.00 | 12.00 | 5.921 | 6.00 |

## Callouts

### Variables with > 10% pure-NA missing (excluding reserve codes)

| variable | block | %miss | n_total |
|---|---|---:|---:|
| `W5_DIGIT_SPAN_derived` | W5_cognitive | 85.10 | 4196 |
| `BMFRECIP` | W1_network | 69.82 | 6504 |
| `BFFRECIP` | W1_network | 64.44 | 6504 |
| `IGDMEAN` | W1_network | 43.04 | 6504 |
| `PRXPREST` | W1_network | 38.19 | 6504 |
| `IDGX2` | W1_network | 32.40 | 6504 |
| `ODGX2` | W1_network | 32.40 | 6504 |
| `ISOLATED_derived` | W1_network | 32.40 | 6504 |
| `HAVEBFF` | W1_network | 32.40 | 6504 |
| `HAVEBMF` | W1_network | 32.40 | 6504 |
| `RCHDEN` | W1_network | 32.40 | 6504 |
| `INFLDMN` | W1_network | 32.40 | 6504 |
| `REACH3` | W1_network | 32.40 | 6504 |
| `REACH` | W1_network | 32.40 | 6504 |
| `BCENT10X` | W1_network | 32.40 | 6504 |
| `PA55` | W1_SES | 14.98 | 6504 |
| `PB8` | W1_SES | 14.31 | 6504 |
| `PA12` | W1_SES | 13.61 | 6504 |

### Variables where reserve codes exceed true-missing

| variable | block | %miss | %reserve (all) |
|---|---|---:|---:|
| `H1MF10A` | W1_friendship | 0.00 | 8.26 |
| `H1FF10A` | W1_friendship | 0.00 | 11.22 |
| `H1DA7` | W1_inhome_singles | 0.00 | 0.09 |
| `H1ED19` | W1_inhome_singles | 0.00 | 2.12 |
| `H1ED20` | W1_inhome_singles | 0.00 | 2.12 |
| `H1ED21` | W1_inhome_singles | 0.00 | 2.41 |
| `H1ED22` | W1_inhome_singles | 0.00 | 2.14 |
| `H1ED23` | W1_inhome_singles | 0.00 | 2.11 |
| `H1ED24` | W1_inhome_singles | 0.00 | 2.11 |
| `H1FS1` | W1_CESD | 0.00 | 0.34 |
| `H1FS2` | W1_CESD | 0.00 | 0.26 |
| `H1FS3` | W1_CESD | 0.00 | 0.37 |
| `H1FS4` | W1_CESD | 0.00 | 0.32 |
| `H1FS5` | W1_CESD | 0.00 | 0.29 |
| `H1FS6` | W1_CESD | 0.00 | 0.31 |
| `H1FS7` | W1_CESD | 0.00 | 0.26 |
| `H1FS8` | W1_CESD | 0.00 | 0.45 |
| `H1FS9` | W1_CESD | 0.00 | 0.42 |
| `H1FS10` | W1_CESD | 0.00 | 0.26 |
| `H1FS11` | W1_CESD | 0.00 | 0.23 |
| `H1FS12` | W1_CESD | 0.00 | 0.29 |
| `H1FS13` | W1_CESD | 0.00 | 0.29 |
| `H1FS14` | W1_CESD | 0.00 | 0.23 |
| `H1FS15` | W1_CESD | 0.00 | 0.28 |
| `H1FS16` | W1_CESD | 0.00 | 0.22 |
| `H1FS17` | W1_CESD | 0.00 | 0.28 |
| `H1FS18` | W1_CESD | 0.00 | 0.31 |
| `H1FS19` | W1_CESD | 0.00 | 0.29 |
| `AH_PVT` | W1_cognitive | 4.32 | 11.07 |
| `AH_RAW` | W3_AHPVT | 0.16 | 3.50 |
| `PVTSTD3C` | W3_AHPVT | 0.16 | 3.50 |
| `PVTSTD3L` | W3_AHPVT | 0.16 | 3.50 |
| `C4WD90_1` | W4_cognitive | 0.04 | 0.22 |
| `C4WD60_1` | W4_cognitive | 0.12 | 0.22 |
| `C4NUMSCR` | W4_cognitive | 0.00 | 0.23 |
| `C5WD90_1` | W5_cognitive | 0.05 | 85.10 |
| `C5WD60_1` | W5_cognitive | 0.05 | 85.18 |
| `H5MH3A` | W5_cognitive | 0.05 | 85.06 |
| `H5MH3B` | W5_cognitive | 0.05 | 99.90 |
| `H5MH4A` | W5_cognitive | 0.10 | 85.10 |
| `H5MH4B` | W5_cognitive | 0.07 | 98.12 |
| `H5MH5A` | W5_cognitive | 0.10 | 85.49 |
| `H5MH5B` | W5_cognitive | 0.07 | 96.93 |
| `H5MH6A` | W5_cognitive | 0.10 | 87.11 |
| `H5MH6B` | W5_cognitive | 0.07 | 93.64 |
| `H5MH7A` | W5_cognitive | 0.12 | 90.73 |
| `H5MH7B` | W5_cognitive | 0.12 | 94.92 |
| `H5MH8A` | W5_cognitive | 0.17 | 93.80 |
| `H5MH8B` | W5_cognitive | 0.17 | 95.88 |
| `H5MH9A` | W5_cognitive | 0.19 | 96.59 |
| `H5MH9B` | W5_cognitive | 0.95 | 96.59 |
| `BIO_SEX` | W1_confounders | 0.00 | 0.02 |
| `H1GI4` | W1_confounders | 0.00 | 0.35 |
| `H1GI6A` | W1_confounders | 0.00 | 0.29 |
| `H1GI6B` | W1_confounders | 0.00 | 0.29 |
| `H1GI6C` | W1_confounders | 0.00 | 0.29 |
| `H1GI6D` | W1_confounders | 0.00 | 0.29 |
| `H1GI6E` | W1_confounders | 0.00 | 0.29 |
| `PB8` | W1_SES | 14.31 | 22.34 |
| `H1NM4` | W1_SES | 0.00 | 88.82 |
| `H1NF4` | W1_SES | 0.00 | 66.71 |
| `H1RM1` | W1_SES | 0.00 | 6.57 |
| `H1RF1` | W1_SES | 0.00 | 30.90 |

## Reserve-code scheme legend

- `none`: continuous / constructed score; no reserve codes applied.
- `1digit`: 6=Refused, 7=Skip, 8=DK, 9=NA (Likert scales ≤5).
- `2digit`: 96=Refused, 97=Skip, 98=DK, 99=NA.
- `3digit`: 996=Refused, 997=Skip, 998=DK, 999=NA.
- `4digit`: 9996=Refused, 9997=Skip, 9998=DK, 9999=NA.
- `*_w5` variants add the Wave V 'question not asked' code (95/995/9995).

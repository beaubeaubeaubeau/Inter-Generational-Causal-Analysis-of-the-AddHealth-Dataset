# Baseline regressions (exploratory)

All specifications: WLS on GSWGT4_2, cluster-robust on CLUSTER2, use_t=True, df = (n_psu − 1). Exposures reported per spec; covariates are sex, race dummies (ref NH-White), parent education, CES-D sum, self-rated health, and (unless noted) AHPVT raw.

## Exposure coefficients (primary terms only)

| Spec | Label | Term | β | SE | 95% CI | t | p | N | PSUs | AHPVT-adj |
|---|---|---|---|---|---|---|---|---|---|---|
| S01 | IDGX2 -> C4WD90_1 (linear+AHPVT) | idgx2 | 0.0115 | 0.0108 | [-0.010, 0.033] | 1.06 | 0.292 | 3274 | 113 | yes |
| S01C | IDGX2 -> W4_COG_COMP (linear+AHPVT) | idgx2 | 0.0093 | 0.0038 | [0.002, 0.017] | 2.46 | 0.0154 | 3268 | 113 | yes |
| S01_noAHPVT | IDGX2 -> C4WD90_1 (linear) | idgx2 | 0.0121 | 0.0111 | [-0.010, 0.034] | 1.09 | 0.278 | 3419 | 113 | no |
| S01C_noAHPVT | IDGX2 -> W4_COG_COMP (linear) | idgx2 | 0.0104 | 0.0040 | [0.003, 0.018] | 2.63 | 0.00973 | 3413 | 113 | no |
| S02 | IDGX2 quintiles -> C4WD90_1+AHPVT | idg_q2 | 0.1166 | 0.0840 | [-0.050, 0.283] | 1.39 | 0.167 | 4721 | 132 | yes |
| S02 | IDGX2 quintiles -> C4WD90_1+AHPVT | idg_q3 | 0.1856 | 0.0830 | [0.021, 0.350] | 2.24 | 0.027 | 4721 | 132 | yes |
| S02 | IDGX2 quintiles -> C4WD90_1+AHPVT | idg_q4 | 0.2006 | 0.1126 | [-0.022, 0.423] | 1.78 | 0.0773 | 4721 | 132 | yes |
| S02 | IDGX2 quintiles -> C4WD90_1+AHPVT | idg_q5 | 0.1263 | 0.1034 | [-0.078, 0.331] | 1.22 | 0.224 | 4721 | 132 | yes |
| S02C | IDGX2 quintiles -> W4_COG_COMP+AHPVT | idg_q2 | 0.0822 | 0.0319 | [0.019, 0.145] | 2.58 | 0.0109 | 4710 | 132 | yes |
| S02C | IDGX2 quintiles -> W4_COG_COMP+AHPVT | idg_q3 | 0.0929 | 0.0336 | [0.026, 0.159] | 2.76 | 0.00654 | 4710 | 132 | yes |
| S02C | IDGX2 quintiles -> W4_COG_COMP+AHPVT | idg_q4 | 0.0863 | 0.0422 | [0.003, 0.170] | 2.04 | 0.043 | 4710 | 132 | yes |
| S02C | IDGX2 quintiles -> W4_COG_COMP+AHPVT | idg_q5 | 0.1079 | 0.0375 | [0.034, 0.182] | 2.88 | 0.00468 | 4710 | 132 | yes |
| S02_noAHPVT | IDGX2 quintiles -> C4WD90_1 | idg_q2 | 0.1297 | 0.0908 | [-0.050, 0.309] | 1.43 | 0.155 | 4924 | 132 | no |
| S02_noAHPVT | IDGX2 quintiles -> C4WD90_1 | idg_q3 | 0.2035 | 0.0873 | [0.031, 0.376] | 2.33 | 0.0213 | 4924 | 132 | no |
| S02_noAHPVT | IDGX2 quintiles -> C4WD90_1 | idg_q4 | 0.2554 | 0.1088 | [0.040, 0.471] | 2.35 | 0.0204 | 4924 | 132 | no |
| S02_noAHPVT | IDGX2 quintiles -> C4WD90_1 | idg_q5 | 0.1655 | 0.1102 | [-0.053, 0.383] | 1.50 | 0.136 | 4924 | 132 | no |
| S02C_noAHPVT | IDGX2 quintiles -> W4_COG_COMP | idg_q2 | 0.0905 | 0.0362 | [0.019, 0.162] | 2.50 | 0.0136 | 4913 | 132 | no |
| S02C_noAHPVT | IDGX2 quintiles -> W4_COG_COMP | idg_q3 | 0.1179 | 0.0376 | [0.044, 0.192] | 3.14 | 0.0021 | 4913 | 132 | no |
| S02C_noAHPVT | IDGX2 quintiles -> W4_COG_COMP | idg_q4 | 0.1228 | 0.0411 | [0.041, 0.204] | 2.99 | 0.00337 | 4913 | 132 | no |
| S02C_noAHPVT | IDGX2 quintiles -> W4_COG_COMP | idg_q5 | 0.1332 | 0.0425 | [0.049, 0.217] | 3.13 | 0.00215 | 4913 | 132 | no |
| S03_C4WD90_1 | IDGX2 -> C4WD90_1 (AHPVT adj) | idgx2 | 0.0115 | 0.0108 | [-0.010, 0.033] | 1.06 | 0.292 | 3274 | 113 | yes |
| S03_C4WD60_1 | IDGX2 -> C4WD60_1 (AHPVT adj) | idgx2 | 0.0217 | 0.0108 | [0.000, 0.043] | 2.01 | 0.0465 | 3272 | 113 | yes |
| S03_C4NUMSCR | IDGX2 -> C4NUMSCR (AHPVT adj) | idgx2 | 0.0181 | 0.0071 | [0.004, 0.032] | 2.53 | 0.0128 | 3275 | 113 | yes |
| S03_W4_COG_COMP | IDGX2 -> W4_COG_COMP (AHPVT adj) | idgx2 | 0.0093 | 0.0038 | [0.002, 0.017] | 2.46 | 0.0154 | 3268 | 113 | yes |
| S04_ODGX2_placebo | ODGX2_placebo -> W4_COG_COMP | odgx2_placebo | 0.0142 | 0.0041 | [0.006, 0.022] | 3.49 | 0.000697 | 3268 | 113 | yes |
| S04_BCENT10X | BCENT10X -> W4_COG_COMP | bcent10x | 0.0911 | 0.0210 | [0.049, 0.133] | 4.34 | 3.19e-05 | 3268 | 113 | yes |
| S04_REACH | REACH -> W4_COG_COMP | reach | 0.0000 | 0.0000 | [-0.000, 0.000] | 0.72 | 0.475 | 3268 | 113 | yes |
| S04_PRXPREST | PRXPREST -> W4_COG_COMP | prxprest | 0.3825 | 0.3036 | [-0.219, 0.984] | 1.26 | 0.21 | 3006 | 113 | yes |
| S04_ODGX2_placebo_noAHPVT | ODGX2_placebo -> W4_COG_COMP | odgx2_placebo | 0.0179 | 0.0047 | [0.009, 0.027] | 3.86 | 0.000193 | 3413 | 113 | no |
| S04_BCENT10X_noAHPVT | BCENT10X -> W4_COG_COMP | bcent10x | 0.1079 | 0.0230 | [0.062, 0.153] | 4.70 | 7.42e-06 | 3413 | 113 | no |
| S04_REACH_noAHPVT | REACH -> W4_COG_COMP | reach | 0.0001 | 0.0000 | [0.000, 0.000] | 2.94 | 0.00398 | 3413 | 113 | no |
| S04_PRXPREST_noAHPVT | PRXPREST -> W4_COG_COMP | prxprest | 0.2066 | 0.3218 | [-0.431, 0.844] | 0.64 | 0.522 | 3137 | 113 | no |
| S05_ZERO | I(IDGX2==0) -> W4_COG_COMP | idg_zero | -0.0442 | 0.0516 | [-0.146, 0.058] | -0.86 | 0.394 | 3268 | 113 | yes |
| S05_LEQ1 | I(IDGX2<=1) -> W4_COG_COMP | idg_leq1 | -0.0817 | 0.0335 | [-0.148, -0.015] | -2.44 | 0.0163 | 3268 | 113 | yes |
| S05_ZERO_noAHPVT | I(IDGX2==0) -> W4_COG_COMP | idg_zero | -0.0603 | 0.0557 | [-0.171, 0.050] | -1.08 | 0.282 | 3413 | 113 | no |
| S05_LEQ1_noAHPVT | I(IDGX2<=1) -> W4_COG_COMP | idg_leq1 | -0.1012 | 0.0375 | [-0.175, -0.027] | -2.70 | 0.00799 | 3413 | 113 | no |
| S06 | SCHOOL_BELONG -> W4_COG_COMP (full W1) | school_belong | 0.0036 | 0.0032 | [-0.003, 0.010] | 1.12 | 0.265 | 4629 | 132 | yes |
| S06_noAHPVT | SCHOOL_BELONG -> W4_COG_COMP (full W1) | school_belong | 0.0030 | 0.0032 | [-0.003, 0.009] | 0.94 | 0.351 | 4828 | 132 | no |
| S07 | H1FS13 + H1FS14 -> W4_COG_COMP | lonely | 0.0039 | 0.0201 | [-0.036, 0.044] | 0.20 | 0.845 | 4710 | 132 | yes |
| S07 | H1FS13 + H1FS14 -> W4_COG_COMP | unfriendly | 0.0008 | 0.0226 | [-0.044, 0.046] | 0.04 | 0.971 | 4710 | 132 | yes |
| S07_noAHPVT | H1FS13 + H1FS14 -> W4_COG_COMP | lonely | 0.0532 | 0.0201 | [0.013, 0.093] | 2.64 | 0.00924 | 4913 | 132 | no |
| S07_noAHPVT | H1FS13 + H1FS14 -> W4_COG_COMP | unfriendly | 0.0133 | 0.0264 | [-0.039, 0.065] | 0.50 | 0.616 | 4913 | 132 | no |
| S09_sex | IDGX2 × sex on W4_COG_COMP | idgx2_c | 0.0061 | 0.0056 | [-0.005, 0.017] | 1.10 | 0.276 | 3268 | 113 | yes |
| S09_sex | IDGX2 × sex on W4_COG_COMP | idgx2_x_male | 0.0058 | 0.0080 | [-0.010, 0.022] | 0.72 | 0.471 | 3268 | 113 | yes |
| S09_parented | IDGX2 × parent_ed on W4_COG_COMP | idgx2_c | 0.0091 | 0.0038 | [0.002, 0.017] | 2.41 | 0.0177 | 3268 | 113 | yes |
| S09_parented | IDGX2 × parent_ed on W4_COG_COMP | idgx2_x_parented | 0.0019 | 0.0017 | [-0.001, 0.005] | 1.15 | 0.251 | 3268 | 113 | yes |
| S10_nominees | FRIEND_N_NOMINEES -> W4_COG_COMP (full W1) | friend_n | 0.0048 | 0.0045 | [-0.004, 0.014] | 1.07 | 0.286 | 4710 | 132 | yes |
| S10_contact | FRIEND_CONTACT_SUM -> W4_COG_COMP | friend_contact | 0.0013 | 0.0017 | [-0.002, 0.005] | 0.78 | 0.44 | 4710 | 132 | yes |
| S10_disclose | FRIEND_DISCLOSURE_ANY -> W4_COG_COMP | friend_disclose | 0.0400 | 0.0244 | [-0.008, 0.088] | 1.64 | 0.104 | 4710 | 132 | yes |
| S10_nominees_noAHPVT | FRIEND_N_NOMINEES -> W4_COG_COMP (full W1) | friend_n | 0.0092 | 0.0056 | [-0.002, 0.020] | 1.66 | 0.0995 | 4913 | 132 | no |
| S10_contact_noAHPVT | FRIEND_CONTACT_SUM -> W4_COG_COMP | friend_contact | 0.0040 | 0.0021 | [-0.000, 0.008] | 1.89 | 0.0616 | 4913 | 132 | no |
| S10_disclose_noAHPVT | FRIEND_DISCLOSURE_ANY -> W4_COG_COMP | friend_disclose | 0.1186 | 0.0259 | [0.067, 0.170] | 4.57 | 1.11e-05 | 4913 | 132 | no |

## Full coefficient table

See `10_regressions.csv` for all terms (baseline covariates included).

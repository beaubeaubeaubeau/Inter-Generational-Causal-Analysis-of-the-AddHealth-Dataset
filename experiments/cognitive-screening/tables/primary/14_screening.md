# Preliminary causal screening of social-exposure treatments

Screens each W1 adolescent-social exposure against a battery of falsification / plausibility diagnostics (D1-D9). All diagnostics reuse weighted OLS on `GSWGT4_2`, cluster-robust SEs on `CLUSTER2`, and the same adjustment set conventions used in the baseline-regressions block of this experiment.

## Diagnostics

- **D1** baseline association on W4_COG_COMP (L0+L1+AHPVT); pass: p<0.05.
- **D2** negative-control outcome HEIGHT_IN; pass: p>0.10.
- **D3** sibling-exposure dissociation (where a sibling exists); pass: |beta_t| > |beta_sib| with |diff| > pooled SE.
- **D4** adjustment-set stability across L0 / L0+L1 / L0+L1+AHPVT; pass: relative shift <30% AND sign stable.
- **D5** outcome-component consistency across C4WD90_1 / C4WD60_1 / C4NUMSCR; pass: sign consistent AND >=2/3 with p<0.10.
- **D6** dose-response monotonicity (continuous only); pass: |rho_trend| > 0.7 AND monotone sign.
- **D7** positivity / overlap (Q5 vs Q1 logit, or binary balance); pass: p_hat in (0.02, 0.98) AND eff N >= 500.
- **D8** saturated-school selection penalty (network exposures, informational).
- **D9** collider / double-adjustment red flag (hard-coded lookup).

## Screening matrix

| Exposure | Group | N | D1 | D2 | D3 | D4 | D5 | D6 | D7 | D9 | Category | Score |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| IDGX2 | peer_network | 3268 | PASS | FAIL | FAIL | FAIL | PASS | PASS | PASS | no | Drop | 4 |
| ODGX2 | self_network | 3268 | PASS | PASS | NA | FAIL | PASS | PASS | PASS | no | Mixed | 6 |
| BCENT10X | peer_network | 3268 | PASS | PASS | PASS | FAIL | PASS | PASS | PASS | no | Mixed | 8 |
| REACH | peer_network | 3268 | FAIL | FAIL | NA | FAIL | FAIL | FAIL | PASS | no | Weakened | 1 |
| REACH3 | peer_network | 3268 | PASS | PASS | NA | FAIL | FAIL | PASS | PASS | no | Mixed | 5 |
| INFLDMN | peer_network | 3268 | FAIL | FAIL | NA | FAIL | FAIL | FAIL | PASS | no | Weakened | 1 |
| PRXPREST | peer_network | 3006 | FAIL | PASS | NA | FAIL | FAIL | PASS | PASS | no | Weakened | 4 |
| IGDMEAN | peer_network | 2783 | FAIL | PASS | NA | FAIL | FAIL | PASS | PASS | no | Weakened | 4 |
| IDG_ZERO | isolation | 3268 | FAIL | FAIL | NA | FAIL | FAIL | NA | PASS | no | Weakened | 1 |
| IDG_LEQ1 | isolation | 3268 | PASS | FAIL | NA | FAIL | FAIL | NA | PASS | no | Mixed | 2 |
| HAVEBMF | isolation | 3268 | FAIL | PASS | FAIL | FAIL | FAIL | NA | PASS | no | Drop | 3 |
| HAVEBFF | isolation | 3268 | FAIL | PASS | NA | FAIL | FAIL | NA | PASS | no | Weakened | 3 |
| ESDEN | egonet | 2783 | FAIL | PASS | NA | FAIL | FAIL | FAIL | PASS | no | Weakened | 3 |
| ERDEN | egonet | 3006 | FAIL | FAIL | NA | PASS | FAIL | FAIL | PASS | no | Weakened | 3 |
| ESRDEN | egonet | 3167 | FAIL | FAIL | NA | FAIL | FAIL | FAIL | PASS | no | Weakened | 1 |
| RCHDEN | egonet | 3268 | FAIL | PASS | NA | PASS | FAIL | FAIL | PASS | no | Weakened | 5 |
| FRIEND_N_NOMINEES | friendship_grid | 4710 | FAIL | PASS | NA | FAIL | FAIL | FAIL | PASS | no | Weakened | 3 |
| FRIEND_CONTACT_SUM | friendship_grid | 4710 | FAIL | PASS | NA | FAIL | FAIL | FAIL | PASS | no | Weakened | 3 |
| FRIEND_DISCLOSURE_ANY | friendship_grid | 4710 | FAIL | FAIL | PASS | FAIL | FAIL | NA | FAIL | no | Weakened | 2 |
| SCHOOL_BELONG | belonging | 4629 | FAIL | FAIL | NA | FAIL | FAIL | PASS | FAIL | YES | Weakened | 1 |
| H1FS13 | loneliness | 4710 | FAIL | PASS | NA | FAIL | FAIL | FAIL | FAIL | YES | Weakened | 2 |
| H1FS14 | loneliness | 4710 | FAIL | PASS | NA | FAIL | FAIL | FAIL | FAIL | YES | Weakened | 2 |
| H1DA7 | qualitative | 4710 | FAIL | FAIL | NA | FAIL | FAIL | FAIL | PASS | no | Weakened | 1 |
| H1PR4 | qualitative | 4697 | FAIL | PASS | NA | FAIL | FAIL | PASS | PASS | no | Weakened | 4 |

## Per-exposure commentary

### IDGX2 (peer_network)  --  **Drop** [score 4]

- D1 primary beta = 0.009264 (SE 0.003764, p = 0.0154, N = 3268).
- D2 HEIGHT_IN beta = -0.05196 (p = 0.00405); FAIL.
- D3 sibling ODGX2: beta_sib = 0.01423, delta |beta| = -0.00497; FAIL.
- D4 rel-shift across adj sets = 0.351; sign stable = True; FAIL.
- D5 2/3 components significant at p<0.10; sign consistent = True; PASS.
- D6 trend rho = 0.8; monotone sign = True; PASS.
- D7 overlap: p_hat in [0.118, 0.785]; eff N = 1308; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D3 fails: sibling stronger.

### ODGX2 (self_network)  --  **Mixed** [score 6]

- D1 primary beta = 0.01423 (SE 0.004081, p = 0.000697, N = 3268).
- D2 HEIGHT_IN beta = -0.00899 (p = 0.707); PASS.
- D4 rel-shift across adj sets = 0.505; sign stable = True; FAIL.
- D5 2/3 components significant at p<0.10; sign consistent = True; PASS.
- D6 trend rho = 1; monotone sign = True; PASS.
- D7 overlap: p_hat in [0.106, 0.81]; eff N = 1313; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D4 unstable across adjustment sets.

### BCENT10X (peer_network)  --  **Mixed** [score 8]

- D1 primary beta = 0.0911 (SE 0.02101, p = 3.19e-05, N = 3268).
- D2 HEIGHT_IN beta = -0.04885 (p = 0.636); PASS.
- D3 sibling ODGX2: beta_sib = 0.01423, delta |beta| = 0.07687; PASS.
- D4 rel-shift across adj sets = 0.394; sign stable = True; FAIL.
- D5 3/3 components significant at p<0.10; sign consistent = True; PASS.
- D6 trend rho = 0.8; monotone sign = True; PASS.
- D7 overlap: p_hat in [0.101, 0.825]; eff N = 1311; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D4 unstable across adjustment sets.

### REACH (peer_network)  --  **Weakened** [score 1]

- D1 primary beta = 2.695e-05 (SE 3.764e-05, p = 0.475, N = 3268).
- D2 HEIGHT_IN beta = -0.0003319 (p = 0.028); FAIL.
- D4 rel-shift across adj sets = 3.35; sign stable = True; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = False; FAIL.
- D6 trend rho = 0; monotone sign = True; FAIL.
- D7 overlap: p_hat in [0.0442, 0.831]; eff N = 1302; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D1 association null (p>=0.05).

### REACH3 (peer_network)  --  **Mixed** [score 5]

- D1 primary beta = 0.0008002 (SE 0.0002917, p = 0.00708, N = 3268).
- D2 HEIGHT_IN beta = -0.001795 (p = 0.213); PASS.
- D4 rel-shift across adj sets = 0.639; sign stable = True; FAIL.
- D5 1/3 components significant at p<0.10; sign consistent = True; FAIL.
- D6 trend rho = 0.8; monotone sign = True; PASS.
- D7 overlap: p_hat in [0.0723, 0.809]; eff N = 1311; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D4 unstable across adjustment sets.

### INFLDMN (peer_network)  --  **Weakened** [score 1]

- D1 primary beta = -1.608e-05 (SE 4.137e-05, p = 0.698, N = 3268).
- D2 HEIGHT_IN beta = -0.000424 (p = 0.012); FAIL.
- D4 rel-shift across adj sets = 6.44; sign stable = False; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = False; FAIL.
- D6 trend rho = -1; monotone sign = False; FAIL.
- D7 overlap: p_hat in [0.0376, 0.89]; eff N = 1296; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D1 association null (p>=0.05).

### PRXPREST (peer_network)  --  **Weakened** [score 4]

- D1 primary beta = 0.3825 (SE 0.3036, p = 0.21, N = 3006).
- D2 HEIGHT_IN beta = 0.6719 (p = 0.623); PASS.
- D4 rel-shift across adj sets = 0.46; sign stable = True; FAIL.
- D5 1/3 components significant at p<0.10; sign consistent = True; FAIL.
- D6 trend rho = 0.8; monotone sign = True; PASS.
- D7 overlap: p_hat in [0.15, 0.779]; eff N = 1204; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D1 association null (p>=0.05).

### IGDMEAN (peer_network)  --  **Weakened** [score 4]

- D1 primary beta = -0.0191 (SE 0.01098, p = 0.0847, N = 2783).
- D2 HEIGHT_IN beta = -0.04076 (p = 0.42); PASS.
- D4 rel-shift across adj sets = 1.1; sign stable = False; FAIL.
- D5 1/3 components significant at p<0.10; sign consistent = True; FAIL.
- D6 trend rho = -1; monotone sign = True; PASS.
- D7 overlap: p_hat in [0.102, 0.941]; eff N = 1110; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D1 association null (p>=0.05).

### IDG_ZERO (isolation)  --  **Weakened** [score 1]

- D1 primary beta = -0.04416 (SE 0.05162, p = 0.394, N = 3268).
- D2 HEIGHT_IN beta = 0.418 (p = 0.059); FAIL.
- D4 rel-shift across adj sets = 0.655; sign stable = True; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = True; FAIL.
- D7 overlap: p_hat in [0.0263, 0.302]; eff N = 2419; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D1 association null (p>=0.05).

### IDG_LEQ1 (isolation)  --  **Mixed** [score 2]

- D1 primary beta = -0.08173 (SE 0.03351, p = 0.0163, N = 3268).
- D2 HEIGHT_IN beta = 0.3028 (p = 0.0573); FAIL.
- D4 rel-shift across adj sets = 0.483; sign stable = True; FAIL.
- D5 1/3 components significant at p<0.10; sign consistent = True; FAIL.
- D7 overlap: p_hat in [0.0872, 0.543]; eff N = 3280; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D2 weakly fails (p<=0.10), D4 unstable across adjustment sets.

### HAVEBMF (isolation)  --  **Drop** [score 3]

- D1 primary beta = -0.00225 (SE 0.03075, p = 0.942, N = 3268).
- D2 HEIGHT_IN beta = -0.05245 (p = 0.682); PASS.
- D3 sibling HAVEBFF: beta_sib = 0.02052, delta |beta| = -0.01827; FAIL.
- D4 rel-shift across adj sets = 3.03; sign stable = False; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = False; FAIL.
- D7 overlap: p_hat in [0.345, 0.701]; eff N = 3280; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D3 fails: sibling stronger.

### HAVEBFF (isolation)  --  **Weakened** [score 3]

- D1 primary beta = 0.02052 (SE 0.02704, p = 0.45, N = 3268).
- D2 HEIGHT_IN beta = -0.1548 (p = 0.259); PASS.
- D4 rel-shift across adj sets = 1.1; sign stable = True; FAIL.
- D5 1/3 components significant at p<0.10; sign consistent = False; FAIL.
- D7 overlap: p_hat in [0.347, 0.778]; eff N = 3280; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D1 association null (p>=0.05).

### ESDEN (egonet)  --  **Weakened** [score 3]

- D1 primary beta = 0.01867 (SE 0.06365, p = 0.77, N = 2783).
- D2 HEIGHT_IN beta = 0.2567 (p = 0.459); PASS.
- D4 rel-shift across adj sets = 1.44; sign stable = False; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = False; FAIL.
- D6 trend rho = 0.4; monotone sign = False; FAIL.
- D7 overlap: p_hat in [0.245, 0.743]; eff N = 1123; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D1 association null (p>=0.05).

### ERDEN (egonet)  --  **Weakened** [score 3]

- D1 primary beta = -0.02342 (SE 0.06431, p = 0.716, N = 3006).
- D2 HEIGHT_IN beta = 0.9166 (p = 0.00153); FAIL.
- D4 rel-shift across adj sets = 0.263; sign stable = True; PASS.
- D5 0/3 components significant at p<0.10; sign consistent = False; FAIL.
- D6 trend rho = 0; monotone sign = False; FAIL.
- D7 overlap: p_hat in [0.15, 0.688]; eff N = 1215; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D1 association null (p>=0.05).

### ESRDEN (egonet)  --  **Weakened** [score 1]

- D1 primary beta = 0.01183 (SE 0.09285, p = 0.899, N = 3167).
- D2 HEIGHT_IN beta = 1.235 (p = 0.00707); FAIL.
- D4 rel-shift across adj sets = 2.5; sign stable = False; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = False; FAIL.
- D6 trend rho = 0; monotone sign = False; FAIL.
- D7 overlap: p_hat in [0.316, 0.713]; eff N = 1275; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D1 association null (p>=0.05).

### RCHDEN (egonet)  --  **Weakened** [score 5]

- D1 primary beta = 0.2739 (SE 0.1392, p = 0.0515, N = 3268).
- D2 HEIGHT_IN beta = 0.1964 (p = 0.738); PASS.
- D4 rel-shift across adj sets = 0.198; sign stable = True; PASS.
- D5 1/3 components significant at p<0.10; sign consistent = True; FAIL.
- D6 trend rho = -0.4; monotone sign = True; FAIL.
- D7 overlap: p_hat in [0.115, 0.77]; eff N = 1318; PASS.
- D8 saturated-school selection: 32.4% of W1 is outside the network frame.
- Notes: D1 association null (p>=0.05).

### FRIEND_N_NOMINEES (friendship_grid)  --  **Weakened** [score 3]

- D1 primary beta = 0.004831 (SE 0.004506, p = 0.286, N = 4710).
- D2 HEIGHT_IN beta = 0.005289 (p = 0.844); PASS.
- D4 rel-shift across adj sets = 0.911; sign stable = True; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = True; FAIL.
- D6 trend rho = 0.4; monotone sign = True; FAIL.
- D7 overlap: p_hat in [0.126, 0.729]; eff N = 1872; PASS.
- Notes: D1 association null (p>=0.05).

### FRIEND_CONTACT_SUM (friendship_grid)  --  **Weakened** [score 3]

- D1 primary beta = 0.001342 (SE 0.00173, p = 0.44, N = 4710).
- D2 HEIGHT_IN beta = -0.003605 (p = 0.696); PASS.
- D4 rel-shift across adj sets = 1.95; sign stable = True; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = False; FAIL.
- D6 trend rho = 0; monotone sign = False; FAIL.
- D7 overlap: p_hat in [0.141, 0.852]; eff N = 1870; PASS.
- Notes: D1 association null (p>=0.05).

### FRIEND_DISCLOSURE_ANY (friendship_grid)  --  **Weakened** [score 2]

- D1 primary beta = 0.03998 (SE 0.02442, p = 0.104, N = 4710).
- D2 HEIGHT_IN beta = -0.2687 (p = 0.0153); FAIL.
- D3 sibling FRIEND_N_NOMINEES: beta_sib = 0.004831, delta |beta| = 0.03514; PASS.
- D4 rel-shift across adj sets = 1.97; sign stable = True; FAIL.
- D5 1/3 components significant at p<0.10; sign consistent = True; FAIL.
- D7 overlap: p_hat in [0.0841, 0.983]; eff N = 4697; FAIL.
- Notes: D1 association null (p>=0.05).

### SCHOOL_BELONG (belonging)  --  **Weakened** [score 1]

- D1 primary beta = 0.003592 (SE 0.003206, p = 0.265, N = 4629).
- D2 HEIGHT_IN beta = -0.04021 (p = 0.00392); FAIL.
- D4 rel-shift across adj sets = 2.37; sign stable = True; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = False; FAIL.
- D6 trend rho = 1; monotone sign = True; PASS.
- D7 overlap: p_hat in [0.00694, 0.903]; eff N = 1817; FAIL.
- D9 RED FLAG: Mixes individual disposition with school-level context; possible collider given W1 CESD/SRH.
- Notes: D1 association null (p>=0.05).

### H1FS13 (loneliness)  --  **Weakened** [score 2]

- D1 primary beta = 0.003934 (SE 0.02006, p = 0.845, N = 4710).
- D2 HEIGHT_IN beta = -0.04505 (p = 0.652); PASS.
- D4 rel-shift across adj sets = 26.8; sign stable = False; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = False; FAIL.
- D6 trend rho = 1; monotone sign = False; FAIL.
- D7 overlap: p_hat in [0.0227, 1]; eff N = 1625; FAIL.
- D9 RED FLAG: CES-D item; contained in CESD_SUM covariate -> double-adjustment.
- Notes: D1 association null (p>=0.05).

### H1FS14 (loneliness)  --  **Weakened** [score 2]

- D1 primary beta = 0.0007919 (SE 0.02259, p = 0.972, N = 4710).
- D2 HEIGHT_IN beta = -0.00734 (p = 0.936); PASS.
- D4 rel-shift across adj sets = 84.3; sign stable = False; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = False; FAIL.
- D6 trend rho = -0.2; monotone sign = True; FAIL.
- D7 overlap: p_hat in [0.122, 0.996]; eff N = 1856; FAIL.
- D9 RED FLAG: CES-D item; contained in CESD_SUM covariate -> double-adjustment.
- Notes: D1 association null (p>=0.05).

### H1DA7 (qualitative)  --  **Weakened** [score 1]

- D1 primary beta = 0.006388 (SE 0.01168, p = 0.586, N = 4710).
- D2 HEIGHT_IN beta = 0.08766 (p = 0.0871); FAIL.
- D4 rel-shift across adj sets = 0.802; sign stable = True; FAIL.
- D5 1/3 components significant at p<0.10; sign consistent = False; FAIL.
- D6 trend rho = -0.6; monotone sign = True; FAIL.
- D7 overlap: p_hat in [0.364, 0.641]; eff N = 1877; PASS.
- Notes: D1 association null (p>=0.05).

### H1PR4 (qualitative)  --  **Weakened** [score 4]

- D1 primary beta = 0.02077 (SE 0.01591, p = 0.194, N = 4697).
- D2 HEIGHT_IN beta = 0.01647 (p = 0.802); PASS.
- D4 rel-shift across adj sets = 1.78; sign stable = True; FAIL.
- D5 0/3 components significant at p<0.10; sign consistent = True; FAIL.
- D6 trend rho = 0.8; monotone sign = True; PASS.
- D7 overlap: p_hat in [0.0355, 0.88]; eff N = 1883; PASS.
- Notes: D1 association null (p>=0.05).

## Shortlist

- **Promising (0):** (none)
- **Mixed (4):** BCENT10X, ODGX2, REACH3, IDG_LEQ1
- **Weakened (18):** REACH, INFLDMN, PRXPREST, IGDMEAN, IDG_ZERO, HAVEBFF, ESDEN, ERDEN, ESRDEN, RCHDEN, FRIEND_N_NOMINEES, FRIEND_CONTACT_SUM, FRIEND_DISCLOSURE_ANY, SCHOOL_BELONG, H1FS13, H1FS14, H1DA7, H1PR4
- **Dropped (2):** IDGX2, HAVEBMF

**Shortlist for formal causal estimation: BCENT10X, ODGX2**

> Note: this shortlist is for the **cognitive** outcome only. The cross-outcome handoff list (which includes IDGX2 for cardiometabolic outcomes) comes from `experiments/multi-outcome-screening/`.

- `BCENT10X` (Mixed): D1 beta = 0.0911 (p=3.19e-05); D2 HEIGHT_IN p = 0.636; D4 rel-shift = 0.394.
- `ODGX2` (Mixed): D1 beta = 0.0142 (p=0.000697); D2 HEIGHT_IN p = 0.707; D4 rel-shift = 0.505.

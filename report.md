# Report — Inter-generational causal analysis of Add Health

## Claims

| ID | Claim | Strength | Evidence |
|---|---|---|---|
| C1 | Social integration (IDGX2) protects against adult adiposity (BMI, waist, BMI-class) within saturated schools | **supported** | [cardiometabolic-handoff](experiments/cardiometabolic-handoff/) confirms screening: WLS β = −0.42 cm waist (E-value 1.38), −0.15 BMI (E 1.35); ordered-logit β = −0.045 log-odds BMICLS (E 1.49); DR-AIPW Q5-vs-Q1 ATEs −4.57 cm waist, −1.90 BMI, −0.29 class — all CIs exclude zero. Transportability gap quantified by [saturation-balance](experiments/saturation-balance/) (AHPVT SMD 0.20, Hispanic SMD 0.20). |
| C2 | School belonging → adult mental health is mediator-leaky (D4 instability) | provisional | [multi-outcome-screening](experiments/multi-outcome-screening/) |
| C3 | Network-centrality → cognition β attenuates 30-50% with AHPVT (trajectory framing) | strong (with sensitivity bound) | [cognitive-screening](experiments/cognitive-screening/), [methods.md §1](reference/methods.md#1-identification-assumptions-and-target-estimand). [cognitive-frontdoor](experiments/cognitive-frontdoor/) sensitivity bound: under the strict-mediator reading of AHPVT, the trajectory β shrinks ~70% across all 3 exposures (IDGX2 −74%, ODGX2 −69%, BCENT10X −73%) — i.e., the trajectory framing is a *substantial undercount* IF you accept that interpretation. |
| C4 | ODGX2 → adult earnings is robust to AHPVT adjustment | **supported (with caveats)** | [ses-handoff](experiments/ses-handoff/) three-estimator agreement: WLS β = +0.080 bracket-units (E 1.35), interval+IPAW β = +1.09 k$/unit (E 1.28), DR-AIPW Q5-vs-Q1 ATE = +6.65 k$ (E **2.03** — moderately robust). All sign-coherent; magnitudes coherent across scales. WLS / interval estimates fragile to a strong DAG-SES-specified confounder; DR-AIPW clears the E ≥ 2 threshold. |
| C5 | **Send-side beats receive-side for SES outcomes**: sociability (`ODGX2`, paired-bootstrap p=0.005 vs IDGX2) and send-density (`ESDEN → H5EC1` β=+1.52, E-value 8.57) dominate over popularity / receive-density. Status access ≠ SES success. | provisional | [popularity-vs-sociability](experiments/popularity-vs-sociability/), [ego-network-density](experiments/ego-network-density/) |
| C6 | **Brokerage / structural-holes hypothesis is contradicted, not corroborated.** Denser send-networks predict *higher* earnings, not lower (Burt's prediction was the opposite). The size-conditioning sensitivity is load-bearing — without `REACH3` adjustment, the effect collapses. | provisional | [ego-network-density](experiments/ego-network-density/) |
| C7 | **One confidant beats many friends for SES.** `FRIEND_DISCLOSURE_ANY → H5EC1` β=+0.44 (E-value 2.48) survives a joint-fit with `FRIEND_N_NOMINEES` and `FRIEND_CONTACT_SUM`. Quantity (n-nominees) drives BMI/waist instead. | provisional | [friendship-quality-vs-quantity](experiments/friendship-quality-vs-quantity/) |
| C8 | **Cardiometabolic protection from popularity is sex-differential.** Girls' protective slope ≈ 2× boys' on H4BMI (interaction p=0.004), H4WAIST (p=0.031), H4BMICLS (p=0.020). Mental-health interactions null. **Cross-confirmed by C1 handoff:** the marginal IDGX2 → cardiometabolic effect is real and supported; sex-modifier remains provisional pending a within-handoff sex-stratified analysis. | provisional | [em-sex-differential](experiments/em-sex-differential/), [cardiometabolic-handoff](experiments/cardiometabolic-handoff/) |
| C9 | **Compensatory (low-SES kids benefit more from popularity) NOT supported.** All 5 outcome × IDGX2×PARENT_ED interactions p>0.07; protective popularity effect is roughly uniform across SES, not concentrated at low SES. | null result | [em-compensatory-by-ses](experiments/em-compensatory-by-ses/) |
| C10 | **Depression-buffering by popularity NOT supported**, AND the D9 collider concern is empirically inactive: conservative-vs-clean two-spec contrast gives identical β to four decimals. | null result | [em-depression-buffering](experiments/em-depression-buffering/) |
| C11 | **Dark side of popularity is ALCOHOL-specific, not universal.** Predicted positive β confirmed for adult drinking (`H4TO39` p=0.001, `H5TO12` p<0.001, `H5TO15` p<0.001) but NOT smoking (`H4TO5`/`H5TO2` null) or marijuana (`H4TO70`/`H4TO65B` null/weakly-negative). | provisional | [popularity-and-substance-use](experiments/popularity-and-substance-use/) |
| C12 | **Lonely-at-the-top paradox REJECTED.** All 5 (z(IDGX2) × z(H1FS13)) interactions p>0.05; β₃ near zero. Popularity main-effect protection on cardiometabolic is large and unmodified by loneliness. | null result | [lonely-at-the-top](experiments/lonely-at-the-top/) |
| C13 | **Cross-sex friendship hypothesis NOT supported on cognition / SES / mental-health**, but a striking asymmetric cardiometabolic pattern surfaces in the HAVEBFF stratum: females without a best female friend carry the highest BMI/waist/BMI-class. | provisional | [cross-sex-friendship](experiments/cross-sex-friendship/) |

<!-- Add or revise rows as evidence accumulates. Each row points to the specific experiment(s) that bear on the claim. -->

## Phase 6 mechanism findings — synthesis (2026-04-27)

Across the 9 mechanism experiments, four cross-cutting patterns emerge:

1. **Send-side / agency edges (out-degree, send-density, friendship disclosure) carry the SES signal**; receive-side / status edges (in-degree, receive-density) don't. Three independent experiments concur (C5, C6, C7). The conventional "popularity → earnings via status" story is wrong direction; "sociability → earnings via active outreach" is the supported channel.
2. **Cardiometabolic protection from popularity (C1) is real but sex-differential (C8)** — the protective effect is concentrated in girls. Compensatory-by-SES (C9) and depression-buffering (C10) are *not* the moderators; sex is.
3. **Outcome specificity is sharper than initially expected.** Popularity protects cardiometabolic outcomes (C1) AND predicts adult alcohol use (C11). The "dark side" story is alcohol-only; smoking and marijuana are null. This is a clean outcome-specificity inversion within the substance-use domain.
4. **Several plausible-sounding hypotheses landed null** (C9, C10, C12, the structural-holes hypothesis prediction in C6, the cross-sex emotional/instrumental hypothesis in C13). These are scientifically informative — pre-registered nulls strengthen the claims that DO survive.

**Phase 6 claim status after Stage D handoffs (2026-04-27):**
- **Upgraded to supported**: C1 (cardiometabolic handoff confirms IDGX2 → adiposity), C4 (SES handoff three-estimator agreement; DR-AIPW E-value 2.03).
- **Strong with sensitivity bound**: C3 (cognitive-frontdoor quantifies the trajectory-framing caveat at ~70% shift under strict-mediator reading).
- **Still provisional** (no direct handoff yet): C2, C5, C6, C7, C8 (sex modifier within handoff), C11, C13. C8 is partially backed by C1 handoff but the sex-modifier itself isn't re-estimated at the handoff level.
- **Null results stand**: C9, C10, C12 — pre-registered nulls strengthen the surviving claims.

## Stage D — Handoff estimation summary

Four formal-estimation experiments completed 2026-04-27:

- **[cardiometabolic-handoff](experiments/cardiometabolic-handoff/)** — IDGX2 → H4BMI/H4WAIST/H4BMICLS with WLS + ordered logit + DR-AIPW + E-value + Cornfield contour + η-tilt. All 3 outcomes show sign-stable, CI-excludes-zero ATEs in DR-AIPW.
- **[ses-handoff](experiments/ses-handoff/)** — ODGX2 → H5EC1 with WLS + interval regression on bracket midpoints + IPAW for W4→W5 attrition + DR-AIPW. Three estimators agree on sign; DR-AIPW Q5-vs-Q1 has the highest E-value (2.03).
- **[cognitive-frontdoor](experiments/cognitive-frontdoor/)** — Pearl 3-equation front-door treating AHPVT as mediator. Strict-mediator reading reduces trajectory β by ~70% across all 3 exposures. Reported as a **sensitivity bound**, not a competing primary estimate.
- **[saturation-balance](experiments/saturation-balance/)** — descriptive transparency artifact for the within-saturated-schools estimand. Top SMD-flagged covariates: AHPVT (0.20), Hispanic (0.20), AH_RAW (0.15), CESD (0.11). Positivity holds (smallest joint-stratum cell N = 15 ≥ 10).

**New methods utilities** (TDD-first; under `scripts/analysis/`): `ipw.py` (IPAW with Cole-Hernán stabilisation + 95% trim), `ordered_logit.py` (statsmodels OrderedModel + cluster-robust SE via score-sandwich), `interval_regression.py` (direct scipy.optimize on Tobit-style censored Gaussian + cluster-robust SE), `frontdoor.py` (Pearl 3-step linear-Gaussian decomposition). Combined +16 new utility tests; project total **274 passing tests + 1 xfail** across `tests/` + experiment smoke tests.

## Cognitive trajectory

<!-- TODO: weave figures from experiments/cognitive-screening/ with chart-explanation convention from reference/methods.md -->

(seed prose: per the trajectory framing decision in [methods.md §1](reference/methods.md#1-identification-assumptions-and-target-estimand), AHPVT serves as the W1 baseline cognitive measure; cognitive-outcome estimates report change-from-baseline. Every network-centrality exposure attenuates 30-50% when AHPVT enters the adjustment set — see cognitive-screening/figures/sensitivity/ahpvt_with_without.png. `ODGX2` (nominations sent) holds the largest stable effect post-adjustment; `IDGX2` (in-degree) attenuates heavily but retains significance; `BCENT10X` (Bonacich) has the largest raw β but attenuates the most. No exposure survives L0+L1+AHPVT with D4 rel-shift < 30%, which under the trajectory framing means none of the cognitive screen results closes back-door identification on its own — they are reported as trajectory-adjusted associations, not causal level effects.)

## Cardiometabolic outcomes

<!-- TODO: prose -->

(seed: IDGX2 shows the most consistent protective signal — β = −0.51 cm per in-degree unit on H4WAIST, p = 1.9 × 10⁻¹¹, D4 rel-shift 18 %. Companion handoff pairs: IDGX2 → H4BMI (β = −0.20, p = 6.8 × 10⁻⁹, D4 rel-shift 21%), IDGX2 → H4BMICLS (β = −0.032, p = 5.0 × 10⁻⁸, D4 passes). All three cleared D1 and D4 on the non-cognitive outcome and are not dominated by AHPVT in a way D4 would detect. See multi-outcome-screening for the screen, [cardiometabolic-handoff](experiments/cardiometabolic-handoff/) (planned) for the formal per-outcome DAG estimate using ordered logit on the BMI-class outcome.)

## SES outcomes

<!-- TODO: prose -->

(seed: ODGX2 → H5EC1 (bracketed adult earnings), β = +0.10 on the bracket scale, p = 1.4 × 10⁻⁴, D4 passes. IDGX2 also lands on `H5EC1` and `H5LM5` in the multi-outcome screen, suggesting a broader social-integration → SES channel. Formal estimation requires interval regression + IPAW for W4→W5 attrition; see [ses-handoff](experiments/ses-handoff/) (planned). Adult earnings are reported in income brackets in W5, so the latent continuous earnings level is not directly observed — interval regression handles this correctly.)

## Mental health and functional outcomes

<!-- TODO: prose -->

(seed: SCHOOL_BELONG dominates these outcomes (top across `H5MN1`, `H5MN2`, `H5ID1`, `H5ID4`, `H5ID16`) but fails D4 on several, suggesting mediator leakage rather than confounding — i.e. the W1→adult belonging effect on adult mental health may pass through intermediate adult states (W4 affective state, W5 social support) that the screen treats as covariates. Per-outcome DAGs needed before formal claims can be made; no handoff experiment is currently scoped for these outcomes.)

## Methodological caveats

- **Saturation-restricted estimand for network exposures.** All network-centrality results are "ATE within saturated schools" — no extrapolation, no saturation-propensity weighting. See [methods.md §1](reference/methods.md#1-identification-assumptions-and-target-estimand) and the planned [saturation-balance](experiments/saturation-balance/) experiment.
- **AHPVT trajectory framing.** Cognitive-outcome point estimates are change-from-baseline, not absolute level. Construct-mismatch caveat: AHPVT is crystallized vocabulary; W4_COG_COMP is fluid memory + working memory.
- **W5 outcome attrition.** Screen uses GSWGT4_2; formal estimation needs GSW5 + IPAW. See [methods.md §3 IPAW](reference/methods.md#inverse-probability-of-attrition-weighting-ipaw) and the planned [ses-handoff](experiments/ses-handoff/) experiment.

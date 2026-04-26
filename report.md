# Report — Inter-generational causal analysis of Add Health

## Claims

| ID | Claim | Strength | Evidence |
|---|---|---|---|
| C1 | Social integration (IDGX2) protects against adult adiposity (BMI, waist) | strong | [cardiometabolic-handoff](experiments/cardiometabolic-handoff/), [multi-outcome-screening](experiments/multi-outcome-screening/) |
| C2 | School belonging → adult mental health is mediator-leaky (D4 instability) | provisional | [multi-outcome-screening](experiments/multi-outcome-screening/) |
| C3 | Network-centrality → cognition β attenuates 30-50% with AHPVT (trajectory framing) | strong | [cognitive-screening](experiments/cognitive-screening/), [methods.md §1](reference/methods.md#1-identification-assumptions-and-target-estimand) |
| C4 | ODGX2 → adult earnings is robust to AHPVT adjustment | provisional | [multi-outcome-screening](experiments/multi-outcome-screening/), [ses-handoff](experiments/ses-handoff/) (planned) |

<!-- Add or revise rows as evidence accumulates. Each row points to the specific experiment(s) that bear on the claim. -->

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

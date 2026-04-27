# DAG-Lonely-Top v0.1 — W1 popularity × loneliness paradox

**Used by:** [lonely-at-the-top](README.md). **Date drafted:** 2026-04-26 (planned, not yet locked).

```mermaid
flowchart LR
    %% W1 measured covariates (L0 + L1 + AHPVT baseline)
    SEX[BIO_SEX]
    RACE[RACE]
    PED[PARENT_ED]
    CESD[CESD_SUM]
    SRH[H1GH1<br/>self-rated health]
    AHPVT[AH_PVT / AH_RAW<br/>W1 baseline cognition]

    %% W1 exposures (joint position)
    POP[W1 popularity<br/>IDGX2]
    LONE[W1 loneliness<br/>H1FS13]
    INTER[(interaction term<br/>z(IDGX2) × z(H1FS13))]

    %% Outcomes
    Y[Mid-life outcomes<br/>H4BMI, H4WAIST,<br/>H5MN1, H5MN2, H5ID1]

    %% Unmeasured
    SCHOOL((school climate /<br/>peer composition))
    PERS((stable personality<br/>traits — neuroticism))

    %% Construction of interaction
    POP --> INTER
    LONE --> INTER

    %% Measured-covariate -> exposures
    SEX --> POP
    SEX --> LONE
    RACE --> POP
    RACE --> LONE
    PED --> POP
    PED --> LONE
    CESD --> POP
    CESD --> LONE
    SRH --> POP
    SRH --> LONE
    AHPVT --> POP
    AHPVT --> LONE

    %% Measured-covariate -> outcome
    SEX --> Y
    RACE --> Y
    PED --> Y
    CESD --> Y
    SRH --> Y
    AHPVT --> Y

    %% Targets (main effects + interaction)
    POP --> Y
    LONE --> Y
    INTER --> Y

    %% Unmeasured (open back-doors)
    SCHOOL -.-> POP
    SCHOOL -.-> LONE
    SCHOOL -.-> Y
    PERS -.-> POP
    PERS -.-> LONE
    PERS -.-> Y
```

**Identification claim.** Conditional on L0+L1+AHPVT *and* on both main
effects (`IDGX2`, `H1FS13`), the partial effect of the interaction term
`z(IDGX2) × z(H1FS13)` on the outcome is identified as the test of the
paradox. The two main effects are forced into the model so that the
interaction coefficient measures the *deviation from additivity* rather
than the joint level.

**Adjustment set:** `{BIO_SEX, RACE, PARENT_ED, CESD_SUM, H1GH1, AH_PVT}`
plus both main effects. Identical structural set to `DAG-Cog`; the only
new term is the constructed interaction.

**Adjustment-set tiers used in the screen:**

| Tier | Variables | Identification role |
|---|---|---|
| L0 | `BIO_SEX`, `RACE`, `PARENT_ED`, `IDGX2`, `H1FS13`, `IDGX2_x_H1FS13` | Demographics + the three exposure terms; minimum acceptable |
| L0+L1 | + `CESD_SUM`, `H1GH1` | Blocks W1 affective / somatic state |
| L0+L1+AHPVT | + `AH_PVT` (or `AH_RAW`) | **Primary spec.** Mirrors `DAG-Cog` for cross-experiment comparability |

**Why each measured covariate is in the set:**

| Variable | Closes which back-door |
|---|---|
| `BIO_SEX`, `RACE` | Demographic → both adolescent peer position AND outcomes; loneliness reporting also varies by sex/race |
| `PARENT_ED` | Family SES → both peer position AND mid-life outcomes |
| `CESD_SUM` | W1 depressive symptoms — partial overlap with `H1FS13` (loneliness item is part of CES-D); INCLUDING `CESD_SUM` is intentional, treats the interaction as the residual paradox after accounting for general depressive load |
| `H1GH1` | W1 self-rated health → outcomes |
| `AH_PVT` | Baseline cognition; preserves `DAG-Cog` comparability |

**Pre-flight design decision (2026-04-26):**

> A median-split `IDGX2 × H1FS13` 2x2 produces a minimum cell N of **73**,
> well below the project's N ≥ 150 positivity floor. The stratified
> design is therefore abandoned. The continuous interaction term
> `z(IDGX2) × z(H1FS13)` is identified as the primary estimand because
> it pools across the entire bivariate distribution. Descriptive 2x2
> cell means are still produced as a "sensitivity" / narrative aid but
> are explicitly flagged as under-powered in the report.

**Estimand wording (use verbatim in reports):**

> Among Add Health respondents in saturated schools, conditional on
> baseline W1 verbal IQ, demographics, W1 affective/somatic state, *and*
> on the main effects of `IDGX2` and `H1FS13`, a one-SD-by-one-SD
> increase in the (popularity, loneliness) joint position is associated
> with a β₃-unit change in the outcome. **β₃ ≠ 0 ⇒ paradox confirmed**;
> the sign of β₃ tells us whether the popular-and-lonely combination is
> worse (β₃ in the harmful direction for that outcome) or better than
> additive.

**Known weak points (load-bearing assumptions):**

- Unmeasured `PERS` (stable personality / neuroticism): drives both
  loneliness reporting AND outcomes; can mimic an interaction. The
  CES-D adjustment partly absorbs this, but neuroticism per se is not
  in the public-use file. **Sensitivity bound via E-value** is the
  planned mitigation per [TODO §A7](../../TODO.md).
- Unmeasured `SCHOOL`: school climate / peer composition could
  confound popularity AND loneliness AND outcomes. The
  within-saturated-schools restriction handles between-school but not
  within-school SCHOOL variation.
- `CESD_SUM` × `H1FS13` collinearity: the loneliness item is part of
  the CES-D scale. Adjusting for `CESD_SUM` plausibly attenuates the
  `H1FS13` main effect; the interaction coefficient is more robust to
  this because it is identified off the joint distribution, but the
  interpretation should make the residual-paradox framing explicit.
- N = 73 minimum cell is the literal reason for abandoning 2x2; if a
  future wave or re-derivation pushes that above 150, revisit the
  stratified design.

**Index entry (in `reference/dag_library.md` — to add):**

> **DAG-Lonely-Top v0.1** — W1 popularity × loneliness interaction →
> mid-life outcomes. Adjustment: L0+L1+AHPVT + both main effects;
> identifies the interaction coefficient β₃ as the paradox test. Used
> by `lonely-at-the-top`. → [`experiments/lonely-at-the-top/dag.md`](../../experiments/lonely-at-the-top/dag.md)

## Changelog

- **2026-04-26** — Drafted v0.1 alongside the experiment scaffold. Pre-flight ruled out 2x2 design (min cell N = 73 < 150 floor). Continuous interaction term locked as the primary estimand.

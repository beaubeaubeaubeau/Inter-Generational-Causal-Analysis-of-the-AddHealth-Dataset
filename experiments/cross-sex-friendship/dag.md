# DAG-CrossSex v0.1 — sex × friend-sex stratified friendship effects

**Used by:** [cross-sex-friendship](README.md). **Date drafted:** 2026-04-26 (planned, not yet locked).

```mermaid
flowchart LR
    %% W1 measured covariates (per-outcome adjustment set; inherited from DAG-Cog / DAG-CardioMet / DAG-SES)
    SEX[BIO_SEX]
    RACE[RACE]
    PED[PARENT_ED]
    CESD[CESD_SUM]
    SRH[H1GH1<br/>self-rated health]
    AHPVT[AH_PVT / AH_RAW<br/>W1 baseline cognition]

    %% W1 exposures (sex-stratified friendship indicators)
    HAVEBMF[HAVEBMF<br/>have male best friend]
    HAVEBFF[HAVEBFF<br/>have female best friend]

    %% Cell stratifier (the design effectively conditions on this)
    STRAT{{Stratifier:<br/>BIO_SEX × HAVEBMF<br/>BIO_SEX × HAVEBFF}}

    %% Outcomes
    Y[Outcomes (13)<br/>W4_COG_COMP, H4BMI, H4SBP, H4DBP,<br/>H4WAIST, H4BMICLS, H5MN1, H5MN2,<br/>H5ID1, H5ID4, H5ID16, H5LM5, H5EC1]

    %% Unmeasured
    GENDERROLE((gender-role norms /<br/>school-level dating culture))
    OPP_SEX_OPP((opportunity for cross-sex<br/>contact: school size,<br/>activities))

    %% Stratifier construction
    SEX --> STRAT
    HAVEBMF --> STRAT
    HAVEBFF --> STRAT

    %% Within-cell back-door blockers
    SEX --> Y
    RACE --> Y
    PED --> Y
    CESD --> Y
    SRH --> Y
    AHPVT --> Y

    %% Friendship -> outcomes (the within-cell target)
    HAVEBMF --> Y
    HAVEBFF --> Y

    %% Confounders of friendship
    RACE --> HAVEBMF
    RACE --> HAVEBFF
    PED --> HAVEBMF
    PED --> HAVEBFF
    CESD --> HAVEBMF
    CESD --> HAVEBFF

    %% Unmeasured
    GENDERROLE -.-> HAVEBMF
    GENDERROLE -.-> HAVEBFF
    GENDERROLE -.-> Y
    OPP_SEX_OPP -.-> HAVEBMF
    OPP_SEX_OPP -.-> HAVEBFF
```

**Identification claim.** Within each `(BIO_SEX, friend-sex indicator)`
cell, the per-outcome adjustment set inherited from the relevant existing
DAG (DAG-Cog for `W4_COG_COMP`, DAG-CardioMet for cardiometabolic,
DAG-SES for SES, and screen-default L0+L1+AHPVT for the others) closes
back-door paths to the outcome. The cross-cell *contrast* of interest
is descriptive: comparing the within-cell β across the two cross-sex
cells (`female × HAVEBMF=1`, `male × HAVEBFF=1`) against the two
same-sex cells.

**Per-outcome adjustment set:**

| Outcome | Adjustment set | Source DAG |
|---|---|---|
| `W4_COG_COMP` | L0+L1+AHPVT | DAG-Cog |
| `H4BMI`, `H4SBP`, `H4DBP`, `H4WAIST`, `H4BMICLS` | L0+L1+AHPVT (screen-default until DAG-CardioMet locks) | DAG-CardioMet (planned) |
| `H5MN1`, `H5MN2`, `H5ID1`, `H5ID4`, `H5ID16` | L0+L1+AHPVT (screen-default) | per-outcome DAG TBD |
| `H5LM5`, `H5EC1` | **L0+L1** (drop AHPVT — see `DAG-SES`) | DAG-SES |

**Why each measured covariate is in the set:**

| Variable | Closes which back-door |
|---|---|
| `BIO_SEX` | Stratifier; not adjusted within cell because it is the cell label |
| `RACE` | Cross-sex friendship rates vary by race; race also affects outcomes |
| `PARENT_ED` | Family SES → both friendship choice (parental supervision intensity) AND outcomes |
| `CESD_SUM`, `H1GH1` | W1 affective/somatic state → both peer composition AND outcomes |
| `AH_PVT` | Baseline cognition; included for cognitive/cardiometabolic outcomes, dropped for SES per DAG-SES |

**Cross-cell contrast as the headline:**

> The headline test is not a single coefficient — it is the per-outcome
> *pattern* across 4 cells. For each outcome, the experiment asks: "is
> the β of `HAVEBMF=1 vs 0` *within females* different from the β of
> `HAVEBFF=1 vs 0` *within males*?" A consistent asymmetry across
> several outcomes supports the cross-sex-friendship-is-different claim.
> The 8 × 13 heatmap is the visual summary.

**Estimand wording (use verbatim in reports):**

> Within sex × friend-sex cell *c*, conditional on the per-outcome
> adjustment set, having a best friend of the indicated sex (vs. not)
> is associated with a β-unit change in outcome `Y`. The contrast of
> interest is between cross-sex and same-sex cells *within sex* — for
> example, `β(female, HAVEBMF=1 vs 0)` vs. `β(female, HAVEBFF=1 vs 0)`.

**Known weak points (load-bearing assumptions):**

- Unmeasured `GENDERROLE` (school-level gender-role norms / dating
  culture): could confound cross-sex friendship choice AND outcomes.
  Within-saturated-schools restriction is partial mitigation.
- Unmeasured `OPP_SEX_OPP` (opportunity for cross-sex contact: school
  size, single-sex schooling rare here, after-school activities): drives
  whether a respondent *can* have a best friend of either sex; partly
  absorbed by school fixed-effects only if those are added.
- Binary `HAVEBMF` / `HAVEBFF` is a simplification: a respondent with
  three male best friends is coded the same as one with one male best
  friend. **Sensitivity** re-fits using `FRIEND_*` derived counts.
- N positivity *between* the two stratifications: a respondent appears
  in both `BIO_SEX × HAVEBMF` and `BIO_SEX × HAVEBFF` analyses (since
  they can have both kinds of friends). The cross-stratification
  forest plot displays both side by side rather than summing.

**Index entry (in `reference/dag_library.md` — to add):**

> **DAG-CrossSex v0.1** — sex × friend-sex stratified friendship effects
> on 13 outcomes. Per-outcome adjustment inherited from DAG-Cog /
> DAG-CardioMet / DAG-SES. Used by `cross-sex-friendship`. →
> [`experiments/cross-sex-friendship/dag.md`](../../experiments/cross-sex-friendship/dag.md)

## Changelog

- **2026-04-26** — Drafted v0.1 alongside the experiment scaffold. Two-stratification design (BIO_SEX × HAVEBMF and BIO_SEX × HAVEBFF) locked.

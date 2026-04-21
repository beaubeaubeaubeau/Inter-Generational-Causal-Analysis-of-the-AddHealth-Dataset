# Task 3b: Wave I Public-Use Network File Catalog

Source: `data/W1/w1network.sas7bdat` (N rows = 6504, N vars = 439)

## Totals per category

| Category | Count |
|----------|-------|
| centrality | 9 |
| local_structure | 25 |
| isolation | 2 |
| school_level | 186 |
| id | 1 |
| other | 216 |

## Examples per category (up to 10)

### centrality (9)

| Variable | Label |
|----------|-------|
| `IDGX2` | In-Degree: TFN |
| `ODGX2` | Out-Degree: TFN |
| `BCENT10X` | Bonacich Centrality P=.1 |
| `REACH` | N reachable alters: TFN |
| `REACH3` | N reachable alters 3 steps: TFN |
| `IGDMEAN` | mean dist to reachable alters |
| `PRXPREST` | Proximity Prestige |
| `INFLDMN` | Influence Domain |
| `RCHDEN` | Density at maximum Reach |

### local_structure (25)

| Variable | Label |
|----------|-------|
| `BMFRECIP` | Best Male Frnd Recip (any) |
| `BFFRECIP` | Best Female Frnd Recip.(any) |
| `ESDEN` | Density: Ego Send Net |
| `ERDEN` | Density: Ego Recieve Net |
| `ESRDEN` | Density: Ego S&R net |
| `EHSGRD` | Ego SEND net Heterogeneity: GRADE |
| `ERSNGRD` | Prop. GRD rep in ego network |
| `EHRGRD` | Ego RECV net Heterogeneity: GRD |
| `ERRNGRD` | Prop. GRD rep in ego RECV network |
| `EHGRD` | Ego S&R net Heterogeneity: GRADE |

### isolation (2)

| Variable | Label |
|----------|-------|
| `HAVEBMF` | R has a Best Male Friend |
| `HAVEBFF` | R has a best Female friend |

### school_level (186)

| Variable | Label |
|----------|-------|
| `SIZE` | Number of questionnaires in school |
| `NOUTNOM` | Number of ties sent outside the school |
| `TAB113` | Ties: Matchable to Other School |
| `AXSGPA` | Send alter mean: gpa |
| `AXSNACT` | Send alter mean: numact |
| `AXSS1` | Send alter mean: s1 |
| `AXSS2` | Send alter mean: s2 |
| `AXSS3` | Send alter mean: s3 |
| `AXSS45A` | Send alter mean: s45a |
| `AXSS45B` | Send alter mean: s45b |

### id (1)

| Variable | Label |
|----------|-------|
| `AID` | RESPONDENT IDENTIFIER |

### other (216)

| Variable | Label |
|----------|-------|
| `BMFRECBF` | Best Male Frnd Recip. as BF |
| `BFFRECBF` | Best Female Frnd Recip as BF |
| `NES` | Size: Ego Send Net |
| `NER` | Size: Ego Recieve Net |
| `NESR` | Size: Ego Send & Recv Net |
| `NEHSGRD` | # of cases used: EHSGRD |
| `NEHRGRD` | # of cases used: EHRGRD |
| `NEHGRD` | # of cases used: EHGRD |
| `NEHSRC5` | # of cases used: EHSRC5 |
| `NEHRRC5` | # of cases used: EHRRC5 |

## Bonacich centrality (explicit search)

Hits: **1** variables with 'BON' in name or 'bonacich' in label.

| Variable | Label |
|----------|-------|
| `BCENT10X` | Bonacich Centrality P=.1 |

**Answer: YES, Bonacich centrality variables appear by name.**

## Clustering coefficient (explicit search)

Hits: **0** variables.

**Answer: NO, no clustering-coefficient variables found by name.**

## Nomination-variant scan

Variables whose label or name suggest friend/nomination: **190**.

| Variable | Label |
|----------|-------|
| `NOUTNOM` | Number of ties sent outside the school |
| `HAVEBMF` | R has a Best Male Friend |
| `HAVEBFF` | R has a best Female friend |
| `BMFRECIP` | Best Male Frnd Recip (any) |
| `BMFRECBF` | Best Male Frnd Recip. as BF |
| `BFFRECIP` | Best Female Frnd Recip.(any) |
| `BFFRECBF` | Best Female Frnd Recip as BF |
| `NASGPA` | Ego Net Denominator axsgpa |
| `NASNACT` | Ego Net Denominator axsnact |
| `NASS1` | Ego Net Denominator axss1 |
| `NASS2` | Ego Net Denominator axss2 |
| `NASS3` | Ego Net Denominator axss3 |
| `NASS45A` | Ego Net Denominator axss45a |
| `NASS45B` | Ego Net Denominator axss45b |
| `NASS45C` | Ego Net Denominator axss45c |
| `NASS45D` | Ego Net Denominator axss45d |
| `NASS45E` | Ego Net Denominator axss45e |
| `NASS45F` | Ego Net Denominator axss45f |
| `NASS46A` | Ego Net Denominator axss46a |
| `NASS46B` | Ego Net Denominator axss46b |
| `NASS46C` | Ego Net Denominator axss46c |
| `NASS46D` | Ego Net Denominator axss46d |
| `NASS47` | Ego Net Denominator axss47 |
| `NASS48` | Ego Net Denominator axss48 |
| `NASS49` | Ego Net Denominator axss49 |
| `NASS50` | Ego Net Denominator axss50 |
| `NASS59A` | Ego Net Denominator axss59a |
| `NASS59B` | Ego Net Denominator axss59b |
| `NASS59C` | Ego Net Denominator axss59c |
| `NASS59D` | Ego Net Denominator axss59d |
| `NASS59E` | Ego Net Denominator axss59e |
| `NASS59F` | Ego Net Denominator axss59f |
| `NASS59G` | Ego Net Denominator axss59g |
| `NASS60A` | Ego Net Denominator axss60a |
| `NASS60B` | Ego Net Denominator axss60b |
| `NASS60C` | Ego Net Denominator axss60c |
| `NASS60D` | Ego Net Denominator axss60d |
| `NASS60E` | Ego Net Denominator axss60e |
| `NASS60F` | Ego Net Denominator axss60f |
| `NASS60G` | Ego Net Denominator axss60g |
| `NASS60H` | Ego Net Denominator axss60h |
| `NASS60I` | Ego Net Denominator axss60i |
| `NASS60J` | Ego Net Denominator axss60j |
| `NASS60K` | Ego Net Denominator axss60k |
| `NASS60L` | Ego Net Denominator axss60l |
| `NASS60M` | Ego Net Denominator axss60m |
| `NASS60N` | Ego Net Denominator axss60n |
| `NASS60O` | Ego Net Denominator axss60o |
| `NASS62A` | Ego Net Denominator axss62a |
| `NASS62B` | Ego Net Denominator axss62b |
| `NASS62C` | Ego Net Denominator axss62c |
| `NASS62D` | Ego Net Denominator axss62d |
| `NASS62E` | Ego Net Denominator axss62e |
| `NASS62F` | Ego Net Denominator axss62f |
| `NASS62G` | Ego Net Denominator axss62g |
| `NASS62H` | Ego Net Denominator axss62h |
| `NASS62I` | Ego Net Denominator axss62i |
| `NASS62J` | Ego Net Denominator axss62j |
| `NASS62K` | Ego Net Denominator axss62k |
| `NASS62L` | Ego Net Denominator axss62l |
| `NASS62M` | Ego Net Denominator axss62m |
| `NASS62N` | Ego Net Denominator axss62n |
| `NASS62O` | Ego Net Denominator axss62o |
| `NASS62P` | Ego Net Denominator axss62p |
| `NASS62Q` | Ego Net Denominator axss62q |
| `NASS62R` | Ego Net Denominator axss62r |
| `NASS63` | Ego Net Denominator axss63 |
| `NASS64` | Ego Net Denominator axss64 |
| `NARGPA` | Ego Net Denominator axrgpa |
| `NARNACT` | Ego Net Denominator axrnact |
| `NARS1` | Ego Net Denominator axrs1 |
| `NARS2` | Ego Net Denominator axrs2 |
| `NARS3` | Ego Net Denominator axrs3 |
| `NARS45A` | Ego Net Denominator axrs45a |
| `NARS45B` | Ego Net Denominator axrs45b |
| `NARS45C` | Ego Net Denominator axrs45c |
| `NARS45D` | Ego Net Denominator axrs45d |
| `NARS45E` | Ego Net Denominator axrs45e |
| `NARS45F` | Ego Net Denominator axrs45f |
| `NARS46A` | Ego Net Denominator axrs46a |
| `NARS46B` | Ego Net Denominator axrs46b |
| `NARS46C` | Ego Net Denominator axrs46c |
| `NARS46D` | Ego Net Denominator axrs46d |
| `NARS47` | Ego Net Denominator axrs47 |
| `NARS48` | Ego Net Denominator axrs48 |
| `NARS49` | Ego Net Denominator axrs49 |
| `NARS50` | Ego Net Denominator axrs50 |
| `NARS59A` | Ego Net Denominator axrs59a |
| `NARS59B` | Ego Net Denominator axrs59b |
| `NARS59C` | Ego Net Denominator axrs59c |
| `NARS59D` | Ego Net Denominator axrs59d |
| `NARS59E` | Ego Net Denominator axrs59e |
| `NARS59F` | Ego Net Denominator axrs59f |
| `NARS59G` | Ego Net Denominator axrs59g |
| `NARS60A` | Ego Net Denominator axrs60a |
| `NARS60B` | Ego Net Denominator axrs60b |
| `NARS60C` | Ego Net Denominator axrs60c |
| `NARS60D` | Ego Net Denominator axrs60d |
| `NARS60E` | Ego Net Denominator axrs60e |
| `NARS60F` | Ego Net Denominator axrs60f |
| `NARS60G` | Ego Net Denominator axrs60g |
| `NARS60H` | Ego Net Denominator axrs60h |
| `NARS60I` | Ego Net Denominator axrs60i |
| `NARS60J` | Ego Net Denominator axrs60j |
| `NARS60K` | Ego Net Denominator axrs60k |
| `NARS60L` | Ego Net Denominator axrs60l |
| `NARS60M` | Ego Net Denominator axrs60m |
| `NARS60N` | Ego Net Denominator axrs60n |
| `NARS60O` | Ego Net Denominator axrs60o |
| `NARS62A` | Ego Net Denominator axrs62a |
| `NARS62B` | Ego Net Denominator axrs62b |
| `NARS62C` | Ego Net Denominator axrs62c |
| `NARS62D` | Ego Net Denominator axrs62d |
| `NARS62E` | Ego Net Denominator axrs62e |
| `NARS62F` | Ego Net Denominator axrs62f |
| `NARS62G` | Ego Net Denominator axrs62g |
| `NARS62H` | Ego Net Denominator axrs62h |
| `NARS62I` | Ego Net Denominator axrs62i |
| `NARS62J` | Ego Net Denominator axrs62j |
| `NARS62K` | Ego Net Denominator axrs62k |
| `NARS62L` | Ego Net Denominator axrs62l |
| `NARS62M` | Ego Net Denominator axrs62m |
| `NARS62N` | Ego Net Denominator axrs62n |
| `NARS62O` | Ego Net Denominator axrs62o |
| `NARS62P` | Ego Net Denominator axrs62p |
| `NARS62Q` | Ego Net Denominator axrs62q |
| `NARS62R` | Ego Net Denominator axrs62r |
| `NARS63` | Ego Net Denominator axrs63 |
| `NARS64` | Ego Net Denominator axrs64 |
| `NAGPA` | Ego Net Denominator axgpa |
| `NANUMACT` | Ego Net Denominator axnumact |
| `NAS1` | Ego Net Denominator axs1 |
| `NAS2` | Ego Net Denominator axs2 |
| `NAS3` | Ego Net Denominator axs3 |
| `NAS45A` | Ego Net Denominator axs45a |
| `NAS45B` | Ego Net Denominator axs45b |
| `NAS45C` | Ego Net Denominator axs45c |
| `NAS45D` | Ego Net Denominator axs45d |
| `NAS45E` | Ego Net Denominator axs45e |
| `NAS45F` | Ego Net Denominator axs45f |
| `NAS46A` | Ego Net Denominator axs46a |
| `NAS46B` | Ego Net Denominator axs46b |
| `NAS46C` | Ego Net Denominator axs46c |
| `NAS46D` | Ego Net Denominator axs46d |
| `NAS47` | Ego Net Denominator axs47 |
| `NAS48` | Ego Net Denominator axs48 |
| `NAS49` | Ego Net Denominator axs49 |
| `NAS50` | Ego Net Denominator axs50 |
| `NAS59A` | Ego Net Denominator axs59a |
| `NAS59B` | Ego Net Denominator axs59b |
| `NAS59C` | Ego Net Denominator axs59c |
| `NAS59D` | Ego Net Denominator axs59d |
| `NAS59E` | Ego Net Denominator axs59e |
| `NAS59F` | Ego Net Denominator axs59f |
| `NAS59G` | Ego Net Denominator axs59g |
| `NAS60A` | Ego Net Denominator axs60a |
| `NAS60B` | Ego Net Denominator axs60b |
| `NAS60C` | Ego Net Denominator axs60c |
| `NAS60D` | Ego Net Denominator axs60d |
| `NAS60E` | Ego Net Denominator axs60e |
| `NAS60F` | Ego Net Denominator axs60f |
| `NAS60G` | Ego Net Denominator axs60g |
| `NAS60H` | Ego Net Denominator axs60h |
| `NAS60I` | Ego Net Denominator axs60i |
| `NAS60J` | Ego Net Denominator axs60j |
| `NAS60K` | Ego Net Denominator axs60k |
| `NAS60L` | Ego Net Denominator axs60l |
| `NAS60M` | Ego Net Denominator axs60m |
| `NAS60N` | Ego Net Denominator axs60n |
| `NAS60O` | Ego Net Denominator axs60o |
| `NAS62A` | Ego Net Denominator axs62a |
| `NAS62B` | Ego Net Denominator axs62b |
| `NAS62C` | Ego Net Denominator axs62c |
| `NAS62D` | Ego Net Denominator axs62d |
| `NAS62E` | Ego Net Denominator axs62e |
| `NAS62F` | Ego Net Denominator axs62f |
| `NAS62G` | Ego Net Denominator axs62g |
| `NAS62H` | Ego Net Denominator axs62h |
| `NAS62I` | Ego Net Denominator axs62i |
| `NAS62J` | Ego Net Denominator axs62j |
| `NAS62K` | Ego Net Denominator axs62k |
| `NAS62L` | Ego Net Denominator axs62l |
| `NAS62M` | Ego Net Denominator axs62m |
| `NAS62N` | Ego Net Denominator axs62n |
| `NAS62O` | Ego Net Denominator axs62o |
| `NAS62P` | Ego Net Denominator axs62p |
| `NAS62Q` | Ego Net Denominator axs62q |
| `NAS62R` | Ego Net Denominator axs62r |
| `NAS63` | Ego Net Denominator axs63 |
| `NAS64` | Ego Net Denominator axs64 |

## Possible school-level aggregates

Variables whose label mentions school / mean / grade-level / overall: **187**.

| Variable | Label |
|----------|-------|
| `SIZE` | Number of questionnaires in school |
| `NOUTNOM` | Number of ties sent outside the school |
| `TAB113` | Ties: Matchable to Other School |
| `IGDMEAN` | mean dist to reachable alters |
| `AXSGPA` | Send alter mean: gpa |
| `AXSNACT` | Send alter mean: numact |
| `AXSS1` | Send alter mean: s1 |
| `AXSS2` | Send alter mean: s2 |
| `AXSS3` | Send alter mean: s3 |
| `AXSS45A` | Send alter mean: s45a |
| `AXSS45B` | Send alter mean: s45b |
| `AXSS45C` | Send alter mean: s45c |
| `AXSS45D` | Send alter mean: s45d |
| `AXSS45E` | Send alter mean: s45e |
| `AXSS45F` | Send alter mean: s45f |
| `AXSS46A` | Send alter mean: s46a |
| `AXSS46B` | Send alter mean: s46b |
| `AXSS46C` | Send alter mean: s46c |
| `AXSS46D` | Send alter mean: s46d |
| `AXSS47` | Send alter mean: s47 |
| `AXSS48` | Send alter mean: s48 |
| `AXSS49` | Send alter mean: s49 |
| `AXSS50` | Send alter mean: s50 |
| `AXSS59A` | Send alter mean: s59a |
| `AXSS59B` | Send alter mean: s59b |
| `AXSS59C` | Send alter mean: s59c |
| `AXSS59D` | Send alter mean: s59d |
| `AXSS59E` | Send alter mean: s59e |
| `AXSS59F` | Send alter mean: s59f |
| `AXSS59G` | Send alter mean: s59g |
| `AXSS60A` | Send alter mean: s60a |
| `AXSS60B` | Send alter mean: s60b |
| `AXSS60C` | Send alter mean: s60c |
| `AXSS60D` | Send alter mean: s60d |
| `AXSS60E` | Send alter mean: s60e |
| `AXSS60F` | Send alter mean: s60f |
| `AXSS60G` | Send alter mean: s60g |
| `AXSS60H` | Send alter mean: s60h |
| `AXSS60I` | Send alter mean: s60i |
| `AXSS60J` | Send alter mean: s60j |
| `AXSS60K` | Send alter mean: s60k |
| `AXSS60L` | Send alter mean: s60l |
| `AXSS60M` | Send alter mean: s60m |
| `AXSS60N` | Send alter mean: s60n |
| `AXSS60O` | Send alter mean: s60o |
| `AXSS62A` | Send alter mean: s62a |
| `AXSS62B` | Send alter mean: s62b |
| `AXSS62C` | Send alter mean: s62c |
| `AXSS62D` | Send alter mean: s62d |
| `AXSS62E` | Send alter mean: s62e |
| `AXSS62F` | Send alter mean: s62f |
| `AXSS62G` | Send alter mean: s62g |
| `AXSS62H` | Send alter mean: s62h |
| `AXSS62I` | Send alter mean: s62i |
| `AXSS62J` | Send alter mean: s62j |
| `AXSS62K` | Send alter mean: s62k |
| `AXSS62L` | Send alter mean: s62l |
| `AXSS62M` | Send alter mean: s62m |
| `AXSS62N` | Send alter mean: s62n |
| `AXSS62O` | Send alter mean: s62o |
| `AXSS62P` | Send alter mean: s62p |
| `AXSS62Q` | Send alter mean: s62q |
| `AXSS62R` | Send alter mean: s62r |
| `AXSS63` | Send alter mean: s63 |
| `AXSS64` | Send alter mean: s64 |
| `AXRGPA` | Recieve alter mean: gpa |
| `AXRNACT` | Recieve alter mean: numact |
| `AXRS1` | Recieve alter mean: s1 |
| `AXRS2` | Recieve alter mean: s2 |
| `AXRS3` | Recieve alter mean: s3 |
| `AXRS45A` | Recieve alter mean: s45a |
| `AXRS45B` | Recieve alter mean: s45b |
| `AXRS45C` | Recieve alter mean: s45c |
| `AXRS45D` | Recieve alter mean: s45d |
| `AXRS45E` | Recieve alter mean: s45e |
| `AXRS45F` | Recieve alter mean: s45f |
| `AXRS46A` | Recieve alter mean: s46a |
| `AXRS46B` | Recieve alter mean: s46b |
| `AXRS46C` | Recieve alter mean: s46c |
| `AXRS46D` | Recieve alter mean: s46d |
| `AXRS47` | Recieve alter mean: s47 |
| `AXRS48` | Recieve alter mean: s48 |
| `AXRS49` | Recieve alter mean: s49 |
| `AXRS50` | Recieve alter mean: s50 |
| `AXRS59A` | Recieve alter mean: s59a |
| `AXRS59B` | Recieve alter mean: s59b |
| `AXRS59C` | Recieve alter mean: s59c |
| `AXRS59D` | Recieve alter mean: s59d |
| `AXRS59E` | Recieve alter mean: s59e |
| `AXRS59F` | Recieve alter mean: s59f |
| `AXRS59G` | Recieve alter mean: s59g |
| `AXRS60A` | Recieve alter mean: s60a |
| `AXRS60B` | Recieve alter mean: s60b |
| `AXRS60C` | Recieve alter mean: s60c |
| `AXRS60D` | Recieve alter mean: s60d |
| `AXRS60E` | Recieve alter mean: s60e |
| `AXRS60F` | Recieve alter mean: s60f |
| `AXRS60G` | Recieve alter mean: s60g |
| `AXRS60H` | Recieve alter mean: s60h |
| `AXRS60I` | Recieve alter mean: s60i |
| `AXRS60J` | Recieve alter mean: s60j |
| `AXRS60K` | Recieve alter mean: s60k |
| `AXRS60L` | Recieve alter mean: s60l |
| `AXRS60M` | Recieve alter mean: s60m |
| `AXRS60N` | Recieve alter mean: s60n |
| `AXRS60O` | Recieve alter mean: s60o |
| `AXRS62A` | Recieve alter mean: s62a |
| `AXRS62B` | Recieve alter mean: s62b |
| `AXRS62C` | Recieve alter mean: s62c |
| `AXRS62D` | Recieve alter mean: s62d |
| `AXRS62E` | Recieve alter mean: s62e |
| `AXRS62F` | Recieve alter mean: s62f |
| `AXRS62G` | Recieve alter mean: s62g |
| `AXRS62H` | Recieve alter mean: s62h |
| `AXRS62I` | Recieve alter mean: s62i |
| `AXRS62J` | Recieve alter mean: s62j |
| `AXRS62K` | Recieve alter mean: s62k |
| `AXRS62L` | Recieve alter mean: s62l |
| `AXRS62M` | Recieve alter mean: s62m |
| `AXRS62N` | Recieve alter mean: s62n |
| `AXRS62O` | Recieve alter mean: s62o |
| `AXRS62P` | Recieve alter mean: s62p |
| `AXRS62Q` | Recieve alter mean: s62q |
| `AXRS62R` | Recieve alter mean: s62r |
| `AXRS63` | Recieve alter mean: s63 |
| `AXRS64` | Recieve alter mean: s64 |
| `AXGPA` | S&R alter mean: gpa |
| `AXNUMACT` | S&R alter mean: numact |
| `AXS1` | S&R alter mean: s1 |
| `AXS2` | S&R alter mean: s2 |
| `AXS3` | S&R alter mean: s3 |
| `AXS45A` | S&R alter mean: s45a |
| `AXS45B` | S&R alter mean: s45b |
| `AXS45C` | S&R alter mean: s45c |
| `AXS45D` | S&R alter mean: s45d |
| `AXS45E` | S&R alter mean: s45e |
| `AXS45F` | S&R alter mean: s45f |
| `AXS46A` | S&R alter mean: s46a |
| `AXS46B` | S&R alter mean: s46b |
| `AXS46C` | S&R alter mean: s46c |
| `AXS46D` | S&R alter mean: s46d |
| `AXS47` | S&R alter mean: s47 |
| `AXS48` | S&R alter mean: s48 |
| `AXS49` | S&R alter mean: s49 |
| `AXS50` | S&R alter mean: s50 |
| `AXS59A` | S&R alter mean: s59a |
| `AXS59B` | S&R alter mean: s59b |
| `AXS59C` | S&R alter mean: s59c |
| `AXS59D` | S&R alter mean: s59d |
| `AXS59E` | S&R alter mean: s59e |
| `AXS59F` | S&R alter mean: s59f |
| `AXS59G` | S&R alter mean: s59g |
| `AXS60A` | S&R alter mean: s60a |
| `AXS60B` | S&R alter mean: s60b |
| `AXS60C` | S&R alter mean: s60c |
| `AXS60D` | S&R alter mean: s60d |
| `AXS60E` | S&R alter mean: s60e |
| `AXS60F` | S&R alter mean: s60f |
| `AXS60G` | S&R alter mean: s60g |
| `AXS60H` | S&R alter mean: s60h |
| `AXS60I` | S&R alter mean: s60i |
| `AXS60J` | S&R alter mean: s60j |
| `AXS60K` | S&R alter mean: s60k |
| `AXS60L` | S&R alter mean: s60l |
| `AXS60M` | S&R alter mean: s60m |
| `AXS60N` | S&R alter mean: s60n |
| `AXS60O` | S&R alter mean: s60o |
| `AXS62A` | S&R alter mean: s62a |
| `AXS62B` | S&R alter mean: s62b |
| `AXS62C` | S&R alter mean: s62c |
| `AXS62D` | S&R alter mean: s62d |
| `AXS62E` | S&R alter mean: s62e |
| `AXS62F` | S&R alter mean: s62f |
| `AXS62G` | S&R alter mean: s62g |
| `AXS62H` | S&R alter mean: s62h |
| `AXS62I` | S&R alter mean: s62i |
| `AXS62J` | S&R alter mean: s62j |
| `AXS62K` | S&R alter mean: s62k |
| `AXS62L` | S&R alter mean: s62l |
| `AXS62M` | S&R alter mean: s62m |
| `AXS62N` | S&R alter mean: s62n |
| `AXS62O` | S&R alter mean: s62o |
| `AXS62P` | S&R alter mean: s62p |
| `AXS62Q` | S&R alter mean: s62q |
| `AXS62R` | S&R alter mean: s62r |
| `AXS63` | S&R alter mean: s63 |
| `AXS64` | S&R alter mean: s64 |

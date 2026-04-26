# Task 6 - Public-Use Attrition / Appearance Profile

**Caveat.** The Add Health *public-use* subsample is re-drawn independently at each wave (W5 public-use N=4,196 of restricted-use N~12,300 is a ~1/3 resample; W6 public-use N=3,937 is similar). What looks like 'attrition' from W1 to W5 in this file set is a mixture of **true dropout** and **independent resampling at the wave level**. Without restricted-use participation flags we cannot distinguish the two; this report therefore measures **appearances per W1 AID**, not dropout.

## 1. Wave-by-wave appearance counts (of 6,504 W1 AIDs)

| File | W1 AIDs appearing | Retention % from W1 |
|------|------------------:|--------------------:|
| `w1_inhome` | 6,504 | 100.0% |
| `w1_network` | 6,504 | 100.0% |
| `w2_inhome` | 4,834 | 74.3% |
| `w3_inhome` | 4,882 | 75.1% |
| `w4_inhome` | 5,114 | 78.6% |
| `w4_biomarker` | 5,114 | 78.6% |
| `w5_inhome` | 4,196 | 64.5% |
| `w5_biomarker` | 1,839 | 28.3% |
| `w5_meds` | 1,839 | 28.3% |
| `w6_inhome` | 3,937 | 60.5% |
| `w6_biomarker` | 2,010 | 30.9% |
| `w6_meds` | 2,010 | 30.9% |

## 2. Joint overlaps

Of the N=6,504 W1 public-use respondents:

| Pattern | N | % of W1 |
|---------|--:|--------:|
| W1 | 6,504 | 100.0% |
| W1 & W2 | 4,834 | 74.3% |
| W1 & W3 | 4,882 | 75.1% |
| W1 & W4 | 5,114 | 78.6% |
| W1 & W5 | 4,196 | 64.5% |
| W1 & W6 | 3,937 | 60.5% |
| W1 & W4 & W5 | 3,713 | 57.1% |
| W1 & W5 & W6 | 3,282 | 50.5% |
| W1 & W4 & W5 & W6 | 2,996 | 46.1% |
| W1 & W2 & W3 & W4 & W5 (all 5 waves) | 2,497 | 38.4% |
| W1 all 6 waves (W1-W6 in-home) | 2,048 | 31.5% |
| W1 & W4 biomarker | 5,114 | 78.6% |
| W1 & W4 bio & W5 bio | 1,760 | 27.1% |
| W1 & W4 bio & W5 bio & W6 bio | 1,210 | 18.6% |

## 3. Stratified breakdown: W5 in-home appearance

Rates are '% of W1 AIDs in that cell that appear in the Wave V public-use mixed-mode file.'

| sex | race | parent_ed_tertile | n_w1 | n_appear | pct_appear |
|---|---|---|---|---|---|
| Female | Black-NH | High | 153 | 101 | 66 |
| Female | Black-NH | Low | 280 | 183 | 65.4 |
| Female | Black-NH | Mid | 191 | 138 | 72.3 |
| Female | Black-NH | Missing | 131 | 89 | 67.9 |
| Female | Hispanic | High | 33 | 22 | 66.7 |
| Female | Hispanic | Low | 200 | 126 | 63 |
| Female | Hispanic | Mid | 93 | 59 | 63.4 |
| Female | Hispanic | Missing | 59 | 30 | 50.8 |
| Female | Other-NH | High | 86 | 58 | 67.4 |
| Female | Other-NH | Low | 82 | 51 | 62.2 |
| Female | Other-NH | Mid | 72 | 51 | 70.8 |
| Female | Other-NH | Missing | 52 | 25 | 48.1 |
| Female | Unknown | Low | 2 | 0 | 0 |
| Female | Unknown | Mid | 1 | 0 | 0 |
| Female | White-NH | High | 459 | 389 | 84.7 |
| Female | White-NH | Low | 647 | 477 | 73.7 |
| Female | White-NH | Mid | 581 | 429 | 73.8 |
| Female | White-NH | Missing | 234 | 163 | 69.7 |
| Male | Black-NH | High | 154 | 73 | 47.4 |
| Male | Black-NH | Low | 233 | 96 | 41.2 |
| Male | Black-NH | Mid | 197 | 87 | 44.2 |
| Male | Black-NH | Missing | 125 | 51 | 40.8 |
| Male | Hispanic | High | 40 | 28 | 70 |
| Male | Hispanic | Low | 181 | 93 | 51.4 |
| Male | Hispanic | Mid | 68 | 37 | 54.4 |
| Male | Hispanic | Missing | 69 | 40 | 58 |
| Male | Other-NH | High | 70 | 47 | 67.1 |
| Male | Other-NH | Low | 78 | 47 | 60.3 |
| Male | Other-NH | Mid | 70 | 39 | 55.7 |
| Male | Other-NH | Missing | 44 | 19 | 43.2 |
| Male | Unknown | Low | 2 | 1 | 50 |
| Male | Unknown | Missing | 1 | 0 | 0 |
| Male | White-NH | High | 395 | 281 | 71.1 |
| Male | White-NH | Low | 617 | 382 | 61.9 |
| Male | White-NH | Mid | 625 | 395 | 63.2 |
| Male | White-NH | Missing | 178 | 89 | 50 |
| Unknown | Unknown | Missing | 1 | 0 | 0 |

### 3b. 2-way (sex x race) for W5 in-home

| sex | race | n_w1 | n_appear | pct_appear |
|---|---|---|---|---|
| Female | Black-NH | 755 | 511 | 67.7 |
| Female | Hispanic | 385 | 237 | 61.6 |
| Female | Other-NH | 292 | 185 | 63.4 |
| Female | Unknown | 3 | 0 | 0 |
| Female | White-NH | 1921 | 1458 | 75.9 |
| Male | Black-NH | 709 | 307 | 43.3 |
| Male | Hispanic | 358 | 198 | 55.3 |
| Male | Other-NH | 262 | 152 | 58 |
| Male | Unknown | 3 | 1 | 33.3 |
| Male | White-NH | 1815 | 1147 | 63.2 |
| Unknown | Unknown | 1 | 0 | 0 |

## 4. Stratified breakdown: W6 in-home appearance

| sex | race | parent_ed_tertile | n_w1 | n_appear | pct_appear |
|---|---|---|---|---|---|
| Female | Black-NH | High | 153 | 97 | 63.4 |
| Female | Black-NH | Low | 280 | 181 | 64.6 |
| Female | Black-NH | Mid | 191 | 125 | 65.4 |
| Female | Black-NH | Missing | 131 | 82 | 62.6 |
| Female | Hispanic | High | 33 | 18 | 54.5 |
| Female | Hispanic | Low | 200 | 120 | 60 |
| Female | Hispanic | Mid | 93 | 57 | 61.3 |
| Female | Hispanic | Missing | 59 | 31 | 52.5 |
| Female | Other-NH | High | 86 | 54 | 62.8 |
| Female | Other-NH | Low | 82 | 50 | 61 |
| Female | Other-NH | Mid | 72 | 44 | 61.1 |
| Female | Other-NH | Missing | 52 | 29 | 55.8 |
| Female | Unknown | Low | 2 | 1 | 50 |
| Female | Unknown | Mid | 1 | 0 | 0 |
| Female | White-NH | High | 459 | 343 | 74.7 |
| Female | White-NH | Low | 647 | 438 | 67.7 |
| Female | White-NH | Mid | 581 | 424 | 73 |
| Female | White-NH | Missing | 234 | 155 | 66.2 |
| Male | Black-NH | High | 154 | 85 | 55.2 |
| Male | Black-NH | Low | 233 | 106 | 45.5 |
| Male | Black-NH | Mid | 197 | 90 | 45.7 |
| Male | Black-NH | Missing | 125 | 51 | 40.8 |
| Male | Hispanic | High | 40 | 26 | 65 |
| Male | Hispanic | Low | 181 | 95 | 52.5 |
| Male | Hispanic | Mid | 68 | 40 | 58.8 |
| Male | Hispanic | Missing | 69 | 31 | 44.9 |
| Male | Other-NH | High | 70 | 45 | 64.3 |
| Male | Other-NH | Low | 78 | 42 | 53.8 |
| Male | Other-NH | Mid | 70 | 43 | 61.4 |
| Male | Other-NH | Missing | 44 | 16 | 36.4 |
| Male | Unknown | Low | 2 | 0 | 0 |
| Male | Unknown | Missing | 1 | 0 | 0 |
| Male | White-NH | High | 395 | 259 | 65.6 |
| Male | White-NH | Low | 617 | 341 | 55.3 |
| Male | White-NH | Mid | 625 | 335 | 53.6 |
| Male | White-NH | Missing | 178 | 83 | 46.6 |
| Unknown | Unknown | Missing | 1 | 0 | 0 |

### 4b. 2-way (sex x race) for W6 in-home

| sex | race | n_w1 | n_appear | pct_appear |
|---|---|---|---|---|
| Female | Black-NH | 755 | 485 | 64.2 |
| Female | Hispanic | 385 | 226 | 58.7 |
| Female | Other-NH | 292 | 177 | 60.6 |
| Female | Unknown | 3 | 1 | 33.3 |
| Female | White-NH | 1921 | 1360 | 70.8 |
| Male | Black-NH | 709 | 332 | 46.8 |
| Male | Hispanic | 358 | 192 | 53.6 |
| Male | Other-NH | 262 | 146 | 55.7 |
| Male | Unknown | 3 | 0 | 0 |
| Male | White-NH | 1815 | 1018 | 56.1 |
| Unknown | Unknown | 1 | 0 | 0 |

## 5. Interpretation: resampling vs true dropout

Wave V full-sample N is ~12,300; the public-use release is 4,196 (~34%). Wave VI full-sample N is ~11,000; public-use is 3,937 (~36%). That means roughly two-thirds of the W1->W5 'loss' we observe here is due to the independent public-use draw, not dropout. The 4,196 W5 public-use respondents are themselves a probability sample that overlaps only partially with the W4 public-use sample (5,114) and the W1 public-use sample (6,504). Accordingly, the retention percentages above **understate true Add Health retention** and **overstate attrition**. The stratified breakdown is still informative for detecting *differential* selection on sex / race / parental-education, because the public-use draw is designed to approximately preserve those marginals.

**Parental-education note.** Parental education is taken from `PA12` (Parent Questionnaire item A12, 1=<=8th grade ... 9=professional training beyond college; 10=never went to school, 96=refused). 5,610 of 6,504 W1 AIDs have a valid PA12 response (parent questionnaire was not completed for all adolescents), so parental-ed tertile is 'Missing' for the rest. Cells with 'Missing' parental-ed are retained in the breakdown.

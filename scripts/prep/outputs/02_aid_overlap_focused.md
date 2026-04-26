# Task 2: AID Overlap (Focused)

Source: Add Health public-use ICPSR 21600 v26.

## Reference file sizes (unique AIDs)

| Label | File | Unique AIDs |
|-------|------|-------------|
| W1 In-Home | `w1inhome.sas7bdat` | 6504 |
| W1 Network | `w1network.sas7bdat` | 6504 |
| W2 In-Home | `w2inhome.sas7bdat` | 4834 |
| W3 In-Home | `w3inhome.sas7bdat` | 4882 |
| W4 In-Home | `w4inhome.sas7bdat` | 5114 |
| W5 Mixed-Mode | `pwave5.xpt` | 4196 |
| W6 Mixed-Mode | `pwave6.sas7bdat` | 3937 |
| W5 biomarker (panthro5) | `panthro5.xpt` | 1839 |
| W5 biomarker (pmeds5) | `pmeds5.xpt` | 1839 |
| W6 biomarker (panthro6) | `panthro6.sas7bdat` | 2010 |

## Pairwise overlaps (reference files)

| Pair | Intersection N | % of smaller file |
|------|----------------|-------------------|
| W1 In-Home x W1 Network | 6504 | 100.0% |
| W1 In-Home x W2 In-Home | 4834 | 100.0% |
| W1 In-Home x W3 In-Home | 4882 | 100.0% |
| W1 In-Home x W4 In-Home | 5114 | 100.0% |
| W1 In-Home x W5 Mixed-Mode | 4196 | 100.0% |
| W1 In-Home x W6 Mixed-Mode | 3937 | 100.0% |
| W1 In-Home x W5 biomarker (panthro5) | 1839 | 100.0% |
| W1 In-Home x W5 biomarker (pmeds5) | 1839 | 100.0% |
| W1 In-Home x W6 biomarker (panthro6) | 2010 | 100.0% |
| W1 Network x W2 In-Home | 4834 | 100.0% |
| W1 Network x W3 In-Home | 4882 | 100.0% |
| W1 Network x W4 In-Home | 5114 | 100.0% |
| W1 Network x W5 Mixed-Mode | 4196 | 100.0% |
| W1 Network x W6 Mixed-Mode | 3937 | 100.0% |
| W1 Network x W5 biomarker (panthro5) | 1839 | 100.0% |
| W1 Network x W5 biomarker (pmeds5) | 1839 | 100.0% |
| W1 Network x W6 biomarker (panthro6) | 2010 | 100.0% |
| W2 In-Home x W3 In-Home | 3844 | 79.5% |
| W2 In-Home x W4 In-Home | 3924 | 81.2% |
| W2 In-Home x W5 Mixed-Mode | 3192 | 76.1% |
| W2 In-Home x W6 Mixed-Mode | 3019 | 76.7% |
| W2 In-Home x W5 biomarker (panthro5) | 1451 | 78.9% |
| W2 In-Home x W5 biomarker (pmeds5) | 1451 | 78.9% |
| W2 In-Home x W6 biomarker (panthro6) | 1570 | 78.1% |
| W3 In-Home x W4 In-Home | 4208 | 86.2% |
| W3 In-Home x W5 Mixed-Mode | 3444 | 82.1% |
| W3 In-Home x W6 Mixed-Mode | 3224 | 81.9% |
| W3 In-Home x W5 biomarker (panthro5) | 1593 | 86.6% |
| W3 In-Home x W5 biomarker (pmeds5) | 1593 | 86.6% |
| W3 In-Home x W6 biomarker (panthro6) | 1709 | 85.0% |
| W4 In-Home x W5 Mixed-Mode | 3713 | 88.5% |
| W4 In-Home x W6 Mixed-Mode | 3499 | 88.9% |
| W4 In-Home x W5 biomarker (panthro5) | 1760 | 95.7% |
| W4 In-Home x W5 biomarker (pmeds5) | 1760 | 95.7% |
| W4 In-Home x W6 biomarker (panthro6) | 1889 | 94.0% |
| W5 Mixed-Mode x W6 Mixed-Mode | 3282 | 83.4% |
| W5 Mixed-Mode x W5 biomarker (panthro5) | 1839 | 100.0% |
| W5 Mixed-Mode x W5 biomarker (pmeds5) | 1839 | 100.0% |
| W5 Mixed-Mode x W6 biomarker (panthro6) | 1793 | 89.2% |
| W6 Mixed-Mode x W5 biomarker (panthro5) | 1650 | 89.7% |
| W6 Mixed-Mode x W5 biomarker (pmeds5) | 1650 | 89.7% |
| W6 Mixed-Mode x W6 biomarker (panthro6) | 2010 | 100.0% |
| W5 biomarker (panthro5) x W5 biomarker (pmeds5) | 1839 | 100.0% |
| W5 biomarker (panthro5) x W6 biomarker (panthro6) | 1252 | 68.1% |
| W5 biomarker (pmeds5) x W6 biomarker (panthro6) | 1252 | 68.1% |

## Critical multi-way intersections

| Intersection | N |
|--------------|---|
| W1 Network ∩ W4 In-Home ∩ W5 Mixed-Mode | 3713 |
| W1 Network ∩ W1 In-Home ∩ W5 Mixed-Mode | 4196 |
| W1 In-Home ∩ W4 In-Home ∩ W5 Mixed-Mode | 3713 |
| W1 Network ∩ W4 In-Home ∩ W5 Mixed-Mode ∩ W6 Mixed-Mode | 2996 |
| W1 In-Home ∩ W2 ∩ W3 ∩ W4 ∩ W5 (full panel) | 2497 |

## Red-line flags (project-critical N < 500)

_None of the critical pairs/tuples fall below 500._

Note: the public-use subsample is re-drawn per wave, so any cell <500 implies the corresponding longitudinal design is effectively impossible without restricted-use access.

## Sanity checks

- W1 In-Home ∩ W1 Network = **6504** (expected 6,504). PASS
- W1 core ∩ weight: 6504 / smaller=6504 (PASS)
- W2 core ∩ weight: 4834 / smaller=4834 (PASS)
- W3 core ∩ weight: 4882 / smaller=4882 (PASS)
- W4 core ∩ weight: 5114 / smaller=5114 (PASS)
- W5 core ∩ weight: 4196 / smaller=4196 (PASS)
- W6 core ∩ weight: 3937 / smaller=3937 (PASS)
- W4 biomarker AID sets identical: PASS ({'w4ebv_hscrp.sas7bdat': 5114, 'w4glucose.sas7bdat': 5114, 'w4lipid.sas7bdat': 5114})
- W5 (core 1839 set) biomarker AID sets identical: PASS ({'panthro5.xpt': 1839, 'pcardio5.xpt': 1839, 'pcrp5.xpt': 1839, 'pglua1c5.xpt': 1839, 'plipids5.xpt': 1839, 'prenal5.xpt': 1839})
- W6 biomarker AID sets identical: PASS ({'panthro6.sas7bdat': 2010, 'pbgluaic6.sas7bdat': 2010, 'pbhepat6.sas7bdat': 2010, 'pblipids6.sas7bdat': 2010, 'pcardio6.sas7bdat': 2010})

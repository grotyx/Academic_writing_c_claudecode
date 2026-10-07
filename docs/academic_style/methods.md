# Methods

## Moves
1. Design and setting: design, centres, dates, ethics approval and consent, registration, the
   reporting guideline followed (CONSORT, STROBE, PRISMA, CARE).
2. Participants: eligibility and exclusion criteria, recruitment, how the sample was assembled.
3. Intervention or exposure: what was done, by whom, and how it differed between groups.
4. Outcomes: the primary outcome defined with its instrument and time point; secondary outcomes;
   how and when they were measured, and by whom (blinding of assessors).
5. Sample size: the calculation and its assumptions, or why none was performed.
6. Statistical analysis: models, covariates, handling of missing data, sensitivity analyses,
   multiplicity, significance level, software with version.
Subheadings follow these moves. Detail is sufficient for another team to repeat the study.

## Rules
- Past tense throughout. Passive or "we" as the target journal prefers; keep one choice.
- Define every outcome so that it can be measured again; give units and scale ranges.
- Cite established instruments and methods instead of describing them at length.
- No results and no justification of findings; numbers here describe the protocol only.

## Phrasebank
- Design: "This retrospective cohort study was conducted at ...", "The institutional review
  board approved the study (approval no. ...) and waived the requirement for informed consent.",
  "The study is reported according to the STROBE statement."
- Participants: "Consecutive patients who underwent ... between ... and ... were eligible.",
  "Patients were excluded if they had ...".
- Outcomes: "The primary outcome was ... at ... , defined as ...", "Secondary outcomes included
  ...", "Outcomes were assessed by an observer unaware of group allocation."
- Analysis: "Continuous variables are presented as mean (SD) or median (IQR) and were compared
  with ...", "... was estimated with a mixed-effects model with ... as a random effect.",
  "Missing data were handled by multiple imputation with ... imputations.", "Two-sided *p* <
  0.05 was considered significant. Analyses were performed with R version ...".

## Avoid -> prefer
- "Data were analyzed using appropriate statistical methods" -> name each test and model.
- "Patients were followed up regularly" -> give the visit schedule and time windows.
- "A significance level of 5% was used to determine statistical significance" -> "Two-sided *p*
  < 0.05 was considered significant."

## Model paragraphs
Consecutive patients aged 50 years or older who underwent single-level decompression for lumbar
spinal stenosis at two university hospitals between January 2015 and December 2018 were eligible.
Patients were excluded if they had spondylolisthesis greater than grade 1, previous lumbar
surgery, or a fusion at the index operation. The institutional review boards of both hospitals
approved the study and waived the requirement for informed consent.

The primary outcome was reoperation at the index or an adjacent level within 5 years, ascertained
from the national health insurance claims database. Cumulative incidence was estimated with the
Aalen-Johansen method, treating death as a competing event. The association between technique
and reoperation was estimated with a Fine-Gray model adjusted for age, sex, body mass index and
diabetes. Two-sided *p* < 0.05 was considered significant. Analyses were performed with R version
4.3.1.

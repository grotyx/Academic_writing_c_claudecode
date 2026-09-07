# Study-Type Specific Checklists (v0.2.2)

## Overview
연구 유형에 따른 reporting guideline 체크리스트입니다. 제출 전 해당 연구 유형의 체크리스트를 완료하세요.

### Level 범례

| Level | 의미 | 설명 |
|-------|------|------|
| **필수** | Required | 미포함 시 reject 사유. 반드시 포함 |
| **권장** | Recommended | 리뷰어가 자주 지적. 강력히 권장 |
| **선택** | Optional | 해당 시에만 포함 |

| Study Type | Checklist | Use When |
|------------|-----------|----------|
| Cohort, Case-control, Cross-sectional | STROBE | 관찰 연구 |
| Randomized Controlled Trial | CONSORT | 무작위 대조 시험 |
| Systematic Review / Meta-analysis | PRISMA | 체계적 문헌고찰 |
| Case Report | CARE | 증례 보고 |
| Diagnostic Accuracy | STARD | 진단 검사 연구 |
| Clinical Trial Protocol | SPIRIT | 프로토콜 논문 |
| Quality Improvement | SQUIRE | QI 연구 |

---

## STROBE Checklist (Observational Studies)
*Cohort, Case-control, Cross-sectional studies*

### Title and Abstract
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 1a | Study design in title or abstract | Title/Abstract | 필수 | [ ] |
| 1b | Structured abstract with key elements | Abstract | 필수 | [ ] |

### Introduction
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 2 | Scientific background and rationale | Introduction | 필수 | [ ] |
| 3 | Specific objectives, including pre-specified hypotheses | Introduction | 필수 | [ ] |

### Methods
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 4 | Study design presented early | Methods | 필수 | [ ] |
| 5 | Setting (locations, dates, periods of recruitment/follow-up) | Methods | 필수 | [ ] |
| 6a | Eligibility criteria | Methods | 필수 | [ ] |
| 6b | Sources and methods of selection | Methods | 필수 | [ ] |
| 7 | Outcomes, exposures, predictors clearly defined | Methods | 필수 | [ ] |
| 8 | Data sources and measurement methods | Methods | 필수 | [ ] |
| 9 | Efforts to address potential bias | Methods | 권장 | [ ] |
| 10 | How study size was determined | Methods | 권장 | [ ] |
| 11 | How quantitative variables were handled | Methods | 권장 | [ ] |
| 12a | All statistical methods described | Methods | 필수 | [ ] |
| 12b | Methods for subgroups and interactions | Methods | 선택 | [ ] |
| 12c | How missing data was addressed | Methods | 권장 | [ ] |
| 12d | Loss to follow-up addressed (cohort) | Methods | 권장 | [ ] |
| 12e | Sensitivity analyses | Methods | 선택 | [ ] |

### Results
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 13a | Numbers at each stage (flow diagram recommended) | Results | 필수 | [ ] |
| 13b | Reasons for non-participation | Results | 권장 | [ ] |
| 14a | Characteristics of participants | Results/Table 1 | 필수 | [ ] |
| 14b | Missing data indicated | Results/Tables | 권장 | [ ] |
| 15 | Outcome data | Results | 필수 | [ ] |
| 16a | Unadjusted estimates with CI/p-values | Results | 필수 | [ ] |
| 16b | Adjusted estimates with CI/p-values | Results | 권장 | [ ] |
| 16c | Relative and absolute risk (if applicable) | Results | 선택 | [ ] |
| 17 | Other analyses (subgroup, sensitivity) | Results | 선택 | [ ] |

### Discussion
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 18 | Key results summarized | Discussion | 필수 | [ ] |
| 19 | Limitations discussed | Discussion | 필수 | [ ] |
| 20 | Cautious interpretation | Discussion | 필수 | [ ] |
| 21 | Generalizability | Discussion | 권장 | [ ] |

### Other
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 22 | Funding source | Title page/Acknowledgments | 필수 | [ ] |

---

## CONSORT 2025 (Randomized Controlled Trials)

Verified 2026-09-06 against the [official CONSORT site](https://www.consort-spirit.org/). Use its full 30-item checklist and explanation document, including subitems, for submission. This short index replaces the previous 2010 numbering and is not the full checklist.

| Item | Review topic | Location / completion |
|---|---|---|
| 1 | Trial identification and summary | [ ] |
| 2 | Registration | [ ] |
| 3 | Protocol and analysis-plan access | [ ] |
| 4 | Data-sharing statement | [ ] |
| 5 | Funding and competing interests | [ ] |
| 6 | Scientific rationale | [ ] |
| 7 | Objectives | [ ] |
| 8 | Patient/public involvement | [ ] |
| 9 | Design | [ ] |
| 10 | Protocol changes | [ ] |
| 11 | Setting | [ ] |
| 12 | Eligibility | [ ] |
| 13 | Interventions | [ ] |
| 14 | Outcomes | [ ] |
| 15 | Harm assessment | [ ] |
| 16 | Sample-size rationale | [ ] |
| 17 | Random sequence | [ ] |
| 18 | Concealment | [ ] |
| 19 | Assignment implementation | [ ] |
| 20 | Blinding | [ ] |
| 21 | Analysis methods | [ ] |
| 22 | Participant flow | [ ] |
| 23 | Recruitment and end dates | [ ] |
| 24 | Treatment delivery | [ ] |
| 25 | Baseline characteristics | [ ] |
| 26 | Outcome estimates and denominators | [ ] |
| 27 | Observed harms | [ ] |
| 28 | Additional analyses | [ ] |
| 29 | Interpretation | [ ] |
| 30 | Limitations | [ ] |

For every primary/secondary outcome, record group-specific analysed counts, available observations at the stated time point, group estimates and treatment effects with precision. Binary outcomes need absolute and relative effects. See [Item 26](https://www.consort-spirit.org/item-26-numbers-analysed). In `review/checklist.json`, retain official subitem IDs and locations; document justified non-applicability. A completed short index alone does not establish full reporting compliance.

---

## PRISMA Checklist (Systematic Reviews & Meta-analyses)

### Title
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 1 | "Systematic review" and/or "meta-analysis" in title | Title | 필수 | [ ] |

### Abstract
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 2 | Structured summary (background, objectives, methods, results, conclusions) | Abstract | 필수 | [ ] |

### Introduction
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 3 | Rationale for review | Introduction | 필수 | [ ] |
| 4 | Explicit PICO question | Introduction | 필수 | [ ] |

### Methods
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 5 | Protocol registration (PROSPERO number) | Methods | 필수 | [ ] |
| 6 | Eligibility criteria (PICOS) | Methods | 필수 | [ ] |
| 7 | Information sources (databases, dates, contact with authors) | Methods | 필수 | [ ] |
| 8 | Full search strategy for at least one database | Methods/Appendix | 필수 | [ ] |
| 9 | Study selection process | Methods | 필수 | [ ] |
| 10 | Data extraction process | Methods | 필수 | [ ] |
| 11 | Data items sought | Methods | 권장 | [ ] |
| 12 | Risk of bias assessment methods | Methods | 필수 | [ ] |
| 13 | Summary measures (RR, MD, OR, etc.) | Methods | 필수 | [ ] |
| 14 | Methods of synthesis | Methods | 필수 | [ ] |
| 15 | Risk of bias across studies (publication bias) | Methods | 권장 | [ ] |
| 16 | Additional analyses (sensitivity, subgroup, meta-regression) | Methods | 권장 | [ ] |

### Results
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 17 | Study selection with PRISMA flow diagram | Results/Figure | 필수 | [ ] |
| 18 | Study characteristics table | Results/Table | 필수 | [ ] |
| 19 | Risk of bias within studies | Results | 필수 | [ ] |
| 20 | Results of individual studies | Results/Forest plot | 필수 | [ ] |
| 21 | Synthesis of results | Results | 필수 | [ ] |
| 22 | Risk of bias across studies (publication bias results) | Results | 권장 | [ ] |
| 23 | Additional analyses results | Results | 선택 | [ ] |

### Discussion
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 24 | Summary of evidence | Discussion | 필수 | [ ] |
| 25 | Limitations | Discussion | 필수 | [ ] |
| 26 | Conclusions | Discussion | 필수 | [ ] |

### Funding
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 27 | Sources of funding | Acknowledgments | 필수 | [ ] |

---

## CARE Checklist (Case Reports)

### Title
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 1 | "Case report" in title with interesting findings | Title | 필수 | [ ] |

### Abstract
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 2 | Key information: introduction, case presentation, conclusions | Abstract | 필수 | [ ] |

### Introduction
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 3a | Scientific/clinical importance | Introduction | 필수 | [ ] |
| 3b | Relevant medical literature briefly | Introduction | 필수 | [ ] |

### Patient Information
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 4a | De-identified demographics | Case | 필수 | [ ] |
| 4b | Chief complaints | Case | 필수 | [ ] |
| 4c | Medical, surgical, family history | Case | 권장 | [ ] |
| 4d | Relevant comorbidities | Case | 권장 | [ ] |

### Clinical Findings
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 5 | Physical examination findings | Case | 필수 | [ ] |

### Timeline
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 6 | Dates and times in table or figure | Case/Figure | 권장 | [ ] |

### Diagnostic Assessment
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 7a | Diagnostic methods | Case | 필수 | [ ] |
| 7b | Diagnostic challenges | Case | 권장 | [ ] |
| 7c | Diagnostic reasoning | Case | 권장 | [ ] |
| 7d | Prognostic characteristics | Case | 선택 | [ ] |

### Therapeutic Intervention
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 8a | Types of intervention | Case | 필수 | [ ] |
| 8b | Administration of intervention | Case | 필수 | [ ] |
| 8c | Changes in intervention with rationale | Case | 선택 | [ ] |

### Follow-up and Outcomes
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 9a | Clinician and patient-assessed outcomes | Case | 필수 | [ ] |
| 9b | Important follow-up test results | Case | 필수 | [ ] |
| 9c | Intervention adherence and tolerability | Case | 선택 | [ ] |
| 9d | Adverse events | Case | 권장 | [ ] |

### Discussion
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 10a | Discussion of findings | Discussion | 필수 | [ ] |
| 10b | Relevant literature comparison | Discussion | 필수 | [ ] |
| 10c | Conclusions with learning points | Discussion | 필수 | [ ] |

### Patient Perspective
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 11 | Patient perspective shared (when appropriate) | Case/Discussion | 선택 | [ ] |

### Informed Consent
| # | Item | Location | Level | Done |
|---|------|----------|-------|------|
| 12 | Informed consent statement | Methods/Acknowledgments | 필수 | [ ] |

---

## Additional Checklists Reference

### STARD (Diagnostic Accuracy Studies)
- 30 items covering participants, test methods, analysis, results
- Required for diagnostic test validation studies
- Download: www.equator-network.org/reporting-guidelines/stard

### SPIRIT (Clinical Trial Protocols)
- 33 items for protocol development
- Required before trial registration
- Download: www.spirit-statement.org

### MOOSE (Meta-analyses of Observational Studies)
- Specific for observational study meta-analyses
- Additional items beyond PRISMA
- Download: www.equator-network.org/reporting-guidelines/meta-analysis-of-observational-studies-in-epidemiology-a-proposal-for-reporting-moose-group

### TRIPOD (Prediction Model Studies)
- 22 items for development/validation studies
- Required for clinical prediction models
- Download: www.tripod-statement.org

### CHEERS (Economic Evaluations)
- 24 items for cost-effectiveness studies
- Required for health economic analyses
- Download: www.equator-network.org/reporting-guidelines/cheers

---

## General Submission Checklist

### Pre-submission Requirements
| Item | Level | Done |
|------|-------|------|
| All co-authors reviewed and approved | 필수 | [ ] |
| Corresponding author information complete | 필수 | [ ] |
| ORCID IDs for all authors (if required) | 권장 | [ ] |
| Conflict of interest statements from all authors | 필수 | [ ] |
| Funding disclosure complete | 필수 | [ ] |
| Author contributions defined | 필수 | [ ] |

### Manuscript Components
| Item | Level | Done |
|------|-------|------|
| Cover letter prepared | 필수 | [ ] |
| Title page with all required information | 필수 | [ ] |
| Blinded manuscript (if required) | 권장 | [ ] |
| Abstract within word limit | 필수 | [ ] |
| Main text within word limit | 필수 | [ ] |
| References in correct format | 필수 | [ ] |
| Tables in correct format (Word/Excel) | 필수 | [ ] |
| Figures in required format (TIFF LZW 600+ DPI for submission, PNG for review) | 필수 | [ ] |
| Figure legends complete | 필수 | [ ] |
| Supplementary materials prepared | 선택 | [ ] |

### Journal-Specific
| Item | Level | Done |
|------|-------|------|
| Target journal guidelines reviewed | 필수 | [ ] |
| Manuscript formatted per journal style | 필수 | [ ] |
| Reference style matches journal | 필수 | [ ] |
| Required statements included (ethics, consent, data availability) | 필수 | [ ] |
| Suggested reviewers listed (if required) | 권장 | [ ] |
| Excluded reviewers listed (if applicable) | 선택 | [ ] |
| Key words selected per journal requirements | 필수 | [ ] |

### Final Verification
| Item | Level | Done |
|------|-------|------|
| All QC rounds completed (see qc_guide.md) | 필수 | [ ] |
| Numbers verified across all sections | 필수 | [ ] |
| All references verified | 필수 | [ ] |
| Spell check completed | 필수 | [ ] |
| Read aloud for flow | 권장 | [ ] |
| Co-author final approval obtained | 필수 | [ ] |

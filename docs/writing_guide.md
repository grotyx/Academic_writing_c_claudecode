# Section-by-Section Writing Guide (v0.2)

## General Principles
- Use past tense for completed actions (Methods, Results)
- Use present tense for established facts and conclusions
- Be concise - every sentence should add value
- Follow IMRAD structure strictly

---

## 01. Title
**Length:** 10-15 words typical

**Structure Options:**
- Descriptive: "Outcomes of [Intervention] in [Population]: A [Study Design]"
- Comparative: "[Intervention A] versus [Intervention B] for [Condition]: A [Study Design]"
- Question-based: "Does [Intervention] Improve [Outcome] in [Population]?"

**Checklist:**
- [ ] Includes key intervention/exposure
- [ ] Includes population or condition
- [ ] Indicates study design (if journal requires)
- [ ] No abbreviations (unless universally known: MRI, CT)
- [ ] No unnecessary filler words ("A Study of...", "Investigation into...")
- [ ] Accurate reflection of study content

**Examples:**
- ✅ "Biportal Endoscopic Spine Surgery for Lumbar Stenosis: A Prospective Cohort Study"
- ❌ "A Study Investigating the Effects of a New Surgical Technique"

---

## 02. Abstract
**Write this LAST** - after all other sections complete

**Structured Abstract Format:**
```
Background/Purpose: (2-3 sentences)
- Why this study was needed
- Clear objective statement

Methods: (3-4 sentences)
- Study design and setting
- Patient population and selection
- Key methods/intervention
- Main outcome measures

Results: (4-5 sentences)
- Primary outcome with actual numbers
- Key secondary outcomes
- Important statistical values

Conclusions: (1-2 sentences)
- Main finding restated
- Clinical implication (one sentence)
```

**Rules:**
- Must stand alone - reader should understand without reading full paper
- No citations
- No abbreviations without definition (define on first use)
- Numbers must EXACTLY match Results and Tables
- Include actual data (means, p-values, CIs), not just "significant difference"
- Word limit: typically 250-350 words (check target journal)

**Common Mistakes:**
- ❌ Vague results: "There was a significant difference"
- ✅ Specific results: "VAS decreased from 7.2±1.3 to 2.1±0.8 (p<0.001)"
- ❌ New information not in main text
- ❌ Conclusions that overstate findings

---

## 03. Introduction
**Length:** 3-4 paragraphs (400-600 words typical)

**Structure (Funnel Approach):**

```
Paragraph 1: Broad Context (5-6 sentences)
├── Disease/condition importance and burden
├── Current clinical challenge
└── Why this matters to patients/clinicians

Paragraph 2: Specific Background (5-6 sentences)
├── Current treatment options
├── Existing evidence (with citations)
└── What is already known

Paragraph 3: Knowledge Gap (3-4 sentences)
├── What is NOT known or controversial
├── Why existing evidence is insufficient
└── Clear gap statement

Paragraph 4: Study Purpose (2-3 sentences)
├── "The purpose of this study was to..."
├── Specific, measurable objective
└── Brief hypothesis (if applicable)
```

**Tips:**
- Funnel: broad → narrow → specific gap → your objective
- Cite recent references (prefer last 5-10 years)
- 15-25 references typical for introduction
- Gap statement is CRITICAL - reviewers look for this
- Objective statement: 1-2 sentences MAX, be specific

**Phrases to Use:**
- "However, the evidence regarding X remains limited..."
- "No study has directly compared..."
- "The optimal approach for X remains unclear..."
- "Therefore, the purpose of this study was to..."

**Common Mistakes:**
- ❌ Too much detail that belongs in Discussion
- ❌ Citing your own results in Introduction
- ❌ Vague objectives ("to study...", "to investigate...")
- ❌ Too many paragraphs (keep it focused)

---

## 04. Methods
**Structure for Clinical Studies:**

### 4.1 Study Design and Setting
```
- Study type: prospective/retrospective
- Design: cohort, case-control, RCT, etc.
- Single/multicenter
- Institution name(s)
- Time period of data collection
- IRB approval statement (required)
- Informed consent statement
- Registration number (if clinical trial)
```

### 4.2 Patients/Participants
```
Inclusion Criteria:
- Specific, measurable criteria
- Age range
- Diagnosis criteria
- Indication for treatment

Exclusion Criteria:
- Contraindications
- Missing data thresholds
- Concurrent conditions

Patient Identification:
- How patients were identified
- Screening process
- Final enrollment numbers
```

### 4.3 Intervention/Procedure
```
- Detailed technique description
- Step-by-step if novel technique
- Equipment/materials used
- Who performed (experience level, single vs multiple surgeons)
- Standardization methods
- Comparison group details (if applicable)
```

### 4.4 Outcome Measures
```
Primary Outcome:
- ONE clearly defined primary outcome
- How measured
- When measured (timepoints)
- Definition of success/failure (if applicable)

Secondary Outcomes:
- List all secondary outcomes
- Measurement methods
- Timepoints
```

### 4.5 Data Collection
```
- What data collected
- How collected (chart review, prospective forms, etc.)
- Who collected (blinded?)
- Data validation methods
```

### 4.6 Statistical Analysis
```
- Descriptive statistics (mean±SD, median[IQR], n(%))
- Normality testing method
- Comparative tests with justification:
  - Continuous: t-test vs Mann-Whitney
  - Categorical: Chi-square vs Fisher's exact
- Multiple comparison correction (if applicable)
- Significance level (typically p<0.05)
- Power analysis (if prospective)
- Missing data handling
- Software with version (SPSS 26.0, R 4.2.0, etc.)
```

**Tips:**
- Past tense throughout
- Be specific enough for reproduction
- Justify statistical test choices
- Define all outcome measures before describing analysis

---

## 05. Results
**Structure:** MUST follow Methods order exactly

### 5.1 Patient Flow and Characteristics
```
- How many screened
- How many excluded (with reasons)
- How many included in final analysis
- Reference to flow diagram (if applicable)
- "Demographics are summarized in Table 1"
```

### 5.2 Primary Outcome
```
- State main finding clearly FIRST
- Reference to Table
- Statistical significance
```

### 5.3 Secondary Outcomes
```
- Follow same pattern
- Each outcome in order listed in Methods
```

### 5.4 Additional Analyses
```
- Subgroup analyses (if performed)
- Sensitivity analyses
```

### 5.5 Complications/Adverse Events
```
- Types and frequencies
- Management
- Reference to Table if applicable
```

**Critical Rules:**

**NO Duplication with Tables:**
| Situation | Wrong ❌ | Correct ✅ |
|-----------|---------|-----------|
| Reporting numbers | "Mean age was 54.3±12.1 years" | "Patient demographics are shown in Table 1" |
| Statistical results | "VAS was 3.2±1.4 vs 5.1±1.8 (p=0.023)" | "Group A showed significantly lower VAS scores (Table 2)" |
| Percentages | "Complications occurred in 12 patients (8.3%)" | "Complication rates are detailed in Table 3" |

**When Numbers ARE Acceptable in Results Text:**
- Key primary outcome (one main finding)
- Numbers not in any table
- Flow diagram numbers (enrolled, excluded)

**Tips:**
- Report what you found, not what it means
- NO interpretation - save for Discussion
- Report negative findings too (important for transparency)
- Past tense throughout

---

## 06. Discussion
**Length:** 4-6 paragraphs (800-1200 words typical)

**Structure:**

### Paragraph 1: Main Finding (3-4 sentences)
```
- Start with YOUR key result
- "This study demonstrated that..."
- "The main finding of this study was..."
- Brief significance statement
- NO background repetition here
```

### Paragraphs 2-3: Literature Comparison (6-8 sentences each)
```
- How do your findings compare to existing literature?
- Similar studies: "Consistent with our findings, Kim et al. [X] reported..."
- Different results: "In contrast to our results, Lee et al. [Y] found..."
- Explain why differences might exist:
  - Different patient populations
  - Different techniques
  - Different outcome measures
  - Different follow-up periods
```

### Paragraph 4: Mechanisms/Explanations (4-5 sentences)
```
- Why did you observe these results?
- Biological/clinical plausibility
- Theoretical framework
- "These findings may be explained by..."
```

### Paragraph 5: Clinical Implications (3-4 sentences)
```
- So what? Why does this matter?
- How might this change practice?
- Who would benefit?
- Practical recommendations
```

### Paragraph 6: Limitations (4-6 sentences)
```
- Be honest and specific
- Address each major weakness:
  - Study design limitations
  - Selection bias
  - Sample size
  - Follow-up duration
  - Missing data
- Explain how limitations affect interpretation
- "Despite these limitations, our study..."
```

### Final: Future Directions (1-2 sentences)
```
- What questions remain?
- What future studies are needed?
- Keep brief
```

**Avoiding Redundancy with Introduction:**

| Topic | Introduction (Background) | Discussion (Interpretation) |
|-------|---------------------------|------------------------------|
| Disease burden | "LSS affects 20% of elderly" | (Don't repeat) |
| Current treatments | "Options include X, Y, Z" | "Our technique compares favorably to X" |
| Previous studies | "Studies have shown..." | "Our findings extend those of..." |
| Gap | "No study has compared..." | "We addressed this gap by showing..." |

**Tips:**
- Don't introduce new data
- Don't overstate conclusions
- Acknowledge contradictory evidence fairly
- Limitations: be specific, not generic

---

## 07. Conclusion
**Length:** 1 short paragraph (50-100 words, 3-5 sentences)

**Structure:**
```
Sentence 1: Main finding (answer to objective)
Sentence 2: Key supporting finding (if critical)
Sentence 3: Clinical implication
Sentence 4: Bottom line
```

**Rules:**
- Directly answer the study objective stated in Introduction
- Summarize only MAIN finding(s)
- ONE clinical implication sentence
- NO new information
- NO speculation beyond data
- NO "further studies are needed" (belongs in Discussion)

**Example:**
```
Biportal endoscopic spine surgery demonstrated comparable clinical outcomes 
to conventional microscopic surgery for lumbar stenosis, with significantly 
reduced blood loss and hospital stay. These findings support BESS as a 
viable minimally invasive alternative for appropriately selected patients.
```

---

## 08. References
**Format:** Follow target journal guidelines exactly

**Common Styles:**
- Vancouver (numbered): Most medical journals
- AMA: American Medical Association journals
- APA: Psychology, some health sciences

**Quality Standards:**
- Prefer peer-reviewed original articles
- Recent > old (unless seminal works)
- Prioritize high-impact journals
- Avoid: abstracts-only, non-peer-reviewed, predatory journals

**Verification:**
- EVERY reference must be in knowledge/evidence.md
- EVERY claim must be verified against original source
- Cross-check with PubMed/DOI

---

## 09. Figure Legends
**Structure per Figure:**
```
Figure [#]. [Descriptive title that can stand alone]
[Detailed description of what is shown]
[Panel descriptions if multiple: (A)..., (B)...]
[Arrows/symbols explanation]
[Abbreviation definitions]
[Statistical notes if applicable]
```

**Example:**
```
Figure 2. Comparison of clinical outcomes between groups
(A) Visual analog scale (VAS) scores at baseline, 3 months, and 12 months. 
(B) Oswestry Disability Index (ODI) at the same timepoints. Error bars 
represent standard deviation. *p<0.05, **p<0.01 compared to baseline. 
Abbreviations: BESS, biportal endoscopic spine surgery; MIS, microscopic surgery.
```

---

## 10. Tables
**Standard Table Sequence:**
| Table | Content |
|-------|---------|
| Table 1 | Demographics and baseline characteristics |
| Table 2 | Primary outcome results |
| Table 3 | Secondary outcomes |
| Table 4 | Subgroup analyses (if applicable) |
| Table 5 | Complications/adverse events |

**Formatting Rules:**
- Title: self-explanatory, can stand alone
- Define ALL abbreviations in footnotes
- Indicate statistical tests in footnotes
- P-values: exact (p=0.023) or threshold (p<0.001)
- Align decimal points
- Consistent significant figures (e.g., always 1 decimal)
- Use horizontal lines sparingly (top, header bottom, table bottom)

**Footnote Symbols:** *, †, ‡, §, ‖, ¶ (use in this order)

**Example Table Footer:**
```
Data presented as mean±SD, median [IQR], or n (%).
*Student's t-test; †Mann-Whitney U test; ‡Chi-square test
Abbreviations: BMI, body mass index; VAS, visual analog scale
```

# Section-by-Section Writing Guide (v0.4.0)

## General Principles
- Use past tense for completed actions (Methods, Results)
- Use present tense for established facts and conclusions
- Be concise - every sentence should add value; 장황한 서술 지양, 불필요한 수식어 삭제
- Follow IMRAD structure strictly
- **No bold text in manuscript body** — 본문(Introduction~Conclusion)에서 **bold** 사용 금지. 강조는 문장 구조로 표현
- **Abbreviation: define once, use thereafter** — 약어는 본문에서 최초 등장 시 1회만 정의하고, 이후 섹션에서 재정의하지 않음 (단, Abstract는 독립 문서이므로 별도 정의 필요)
- **Clinical findings as subject** — 통계 분석 방법이 아닌 임상 결과가 문장의 주어가 되어야 함
  - ❌ "The LMM analysis identified a significant difference..."
  - ❌ "The Mann-Whitney U test revealed that..."
  - ✅ "VAS scores improved significantly in Group A..."
  - ✅ "Postoperative pain was significantly lower in the BESS group..."
- **No synonym mixing (동의어 혼용 금지)** — 같은 개념에 대해 하나의 용어를 선택하면 전체 원고에서 일관되게 사용
  - ❌ Methods에서 "dural tear", Discussion에서 "durotomy" → 혼용
  - ✅ 하나를 선택하고 첫 등장 시 "durotomy (dural tear)"로 병기, 이후 선택한 용어만 사용
  - 대상: 진단명, 합병증명, 수술 용어, 중재/그룹명, 환자 호칭 등 모든 의학 용어
  - Drafting 시작 전 draft_plan.md에서 주요 용어 선택을 확정할 것
- **Numerical formatting consistency** — 전체 원고에서 숫자 서식 통일
  - Decimal place: 같은 변수는 동일한 소수점 자리 (예: age를 54.3이면 어디서든 54.3, 54 아님)
  - Units: mg/dL과 mmol/L 중 하나만 (SI 단위 권장, 저널 기준 확인)
  - Tables와 본문 간 서식 일치 (예: Table에 mean±SD면 Abstract도 mean±SD)
- **Sentence-initial numbers** — 숫자로 문장을 시작하지 않음
  - ❌ "10 patients were enrolled."
  - ✅ "Ten patients were enrolled." / "A total of 10 patients were enrolled."

---

## Style Reference Tables

> Phase 5 (Style Polish)에서 주로 적용. Drafting 시에도 참조 가능.

### Voice & Tense by Section

| Section | Tense | Voice | Example |
|---------|-------|-------|---------|
| Abstract | Past (methods/results), Present (conclusions) | Passive preferred | "Patients were enrolled..." |
| Introduction | Present (facts), Past (prior studies) | Mixed, active acceptable | "LSS remains a major issue..." |
| Methods | Past | Passive | "Patients were randomized..." |
| Results | Past | Passive (consistent) | "No significant differences were observed..." |
| Discussion | Present (interpretation), Past (specific findings) | Mixed | "Our findings suggest..." / "The reduction was observed..." |
| Conclusion | Present | Active acceptable | "This technique provides..." |

### Transition Words (접속사/전환어)

| Avoid | Use Instead |
|-------|-------------|
| but | nonetheless, nevertheless, however |
| However (overused) | Nonetheless, Nevertheless |
| In contrast | Conversely |
| therefore | Thus, Accordingly |
| so | Hence, Therefore |

### Verb Upgrades (동사 고급화)

| Basic | Academic |
|-------|----------|
| showed | demonstrated, exhibited, revealed |
| got | obtained, achieved, acquired |
| used | employed, utilized, applied |
| done | performed, conducted, executed |
| is | remains, represents, constitutes |
| has | possesses, exhibits, maintains |

### Common Corrections (빈출 교정 패턴)

| Original | Corrected | Reason |
|----------|-----------|--------|
| is the gold standard | remains the gold standard | 현재 상태 강조 |
| is lacking | remains limited | 부정적 표현 완화 |
| The purpose of this study was to... | This study aimed to... | 더 직접적 (둘 다 사용 가능) |
| are consistent with | align with | 더 간결 |
| elderly patients | older adult patients | 현대적/중립적 (AMA) |
| Due to | Because of | 문법적 정확성* |
| compared to | compared with | AMA 스타일 |

> *"Due to"는 형용사적, "Because of"는 원인을 나타내는 전치사구

### Statistical Notation (통계 표기)

| Item | Format | Example |
|------|--------|---------|
| p-value | lowercase italic *p* | *p* = 0.382, *p* < 0.05 |
| Very small p | threshold notation | *p* < 0.001 (never *p* = 0.000) |
| Exact p preferred | report exact when ≥0.001 | *p* = 0.023 (not *p* < 0.05) |
| Percentage | no space | 83.3% |
| CI | "to" for range | 95% CI: -8.0% to +16.7% |
| Age range | en-dash | 19–80 years |
| Effect size | report with CI | OR 2.3 (95% CI: 1.2–4.5) |

### Hedging Language (Discussion 전용)

Discussion에서 해석·추론을 기술할 때, 근거의 강도에 비례한 hedging 사용:

| 수준 | 표현 | 언제 사용 |
|------|------|-----------|
| Strong | demonstrates, establishes, confirms | 확실한 직접 증거 |
| Moderate | indicates, suggests, supports | 일반적 관찰 연구 결과 |
| Weak | may, might, could, appears to, tends to | 제한점 있는 해석 |
| Very weak | possibly, potentially | 탐색적/가설 생성 단계 |

**원칙**: 관찰 연구·retrospective 연구·작은 표본은 Moderate~Weak hedging이 기본. Strong 주장은 RCT·대규모 연구·확실한 증거에 한함.

---

## Writing Principles (4 Pillars)

### Clarity (명확성)
- One idea per sentence
- Split long sentences
- Avoid ambiguous pronouns ("this" → "this finding", "this result")

### Conciseness (간결성)
- 불필요한 수식어·반복·장황한 서술 삭제
- 한 문장에 하나의 아이디어 — 길어지면 분리
- Discussion에서 Results 숫자/p-value 반복 금지 (Table에 이미 있음); 단, 선행연구 수치와 직접 비교 시 해당 수치 인용은 허용
- 유의하지 않은 p-value를 본문에 나열하지 않음 (Table 참조로 대체); 단, primary outcome의 n.s. 결과는 명시적으로 보고
- ❌ "first-grade students, fifth-grade students, and sixth-grade students"
- ✅ "first-, fifth-, and sixth-grade students"

### Objectivity (객관성)
- ❌ "We believe that..."
- ✅ "The findings suggest that..."
- 과장 금지 표현 목록:
  - ❌ "dramatic improvement", "remarkable difference", "overwhelming evidence"
  - ❌ "most pronounced advantage", "four-fold reduction", "carries direct clinical significance"
  - ❌ "striking", "unprecedented", "groundbreaking"
  - ✅ "notable", "may be clinically relevant", "suggests a potential benefit"
- 결과 해석은 근거에 비례하는 수준으로 제한 — Hedging Language 표 참조

### Consistency (일관성)
- Same term for same concept throughout (synonym mixing 금지 — General Principles 참조)
- Uniform abbreviations and formatting
- Numerical/unit formatting consistency (General Principles 참조)
- Section 간 숫자·용어·약어 교차 검증은 QC Round 1에서 수행 (`docs/qc_guide.md`)

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

> 상세 가이드: `docs/statistical_analysis_guide.md` 참조

```
- Analysis hierarchy: primary → secondary → exploratory 명시
- Descriptive statistics (mean±SD, median[IQR], n(%))
- Normality testing method
- Comparative tests with justification:
  - Continuous: t-test vs Mann-Whitney
  - Categorical: Chi-square vs Fisher's exact
- Effect size measures (Cohen's d, OR, RR, HR 등)
- 95% Confidence intervals for key outcomes
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
- Report effect sizes with CIs, not just p-values
- RCT Table 1: p-value 생략이 원칙 (CONSORT 2010)

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

**Non-significant Results Reporting:**
- ✅ "No significant difference was observed between groups (mean difference 1.2, 95% CI: -0.8 to 3.2, *p* = 0.24)"
- ✅ "The difference did not reach statistical significance"
- ❌ "There was no difference between groups" (absence of evidence ≠ evidence of absence)
- ❌ "The treatment failed to show improvement" (implies expected direction)
- ❌ "The result was insignificant" ("insignificant" ≠ "not significant")

**Non-significant p-values — 본문에서 생략 가능:**
- 유의하지 않은 결과의 p-value를 Results 본문에 일일이 나열하지 않아도 됨
- Table에 모든 p-value가 이미 있으므로, 본문에서는 유의미한 결과 위주로 기술
- ✅ "No significant differences were observed in secondary outcomes (Table 3)"
- ❌ "EQ-5D showed no difference (*p* = 0.382), ODI showed no difference (*p* = 0.541), ..."
- 예외: primary outcome의 n.s. 결과는 p-value 포함하여 명시적으로 보고

**Tips:**
- Report what you found, not what it means
- NO interpretation - save for Discussion
- Report negative findings too (important for transparency)
- Non-significant results: report CI to show precision of estimate
- Past tense throughout
- Clinical findings as subject (see General Principles) — 통계 방법이 아닌 임상 결과가 주어

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

**No Specific Numbers or p-values in Discussion:**
- Discussion은 해석의 공간 — 구체적 숫자와 p-value는 Results/Table에 이미 있으므로 반복하지 않음
- ✅ "Postoperative pain improved significantly in the BESS group"
- ✅ "The complication rate was comparable between groups"
- ❌ "VAS decreased from 7.2±1.3 to 2.1±0.8 (*p*<0.001) in the BESS group"
- ❌ "The infection rate was 2.3% vs 4.1% (*p*=0.34)"
- 예외: 선행연구 수치와 직접 비교할 때는 상대방 수치 인용 가능 ("Kim et al. reported a rate of 3.5%, which aligns with our findings")

**No "Directional Trend" for Non-significant Results:**
- 유의하지 않은 결과를 "trend" 또는 "tendency"로 포장하지 않음
- ❌ "Although not statistically significant, EQ-5D showed a directional trend favoring Group A (*p*=0.058)"
- ❌ "A trend toward improvement was observed"
- ✅ n.s. 결과는 Results에서 보고하고, Discussion에서 굳이 재강조하지 않음
- 예외: 검정력 부족(underpowered)이 명확하고 Limitation에서 언급하는 경우에 한해 간결히 언급 가능

**Neutral Tone — No Exaggeration:**
- 과장 표현을 피하고 중립적 톤 유지
- ❌ "most pronounced advantage", "four-fold reduction", "carries direct clinical significance"
- ❌ "dramatic improvement", "remarkable difference", "overwhelming evidence"
- ✅ "may be clinically relevant", "suggests a potential benefit", "the difference was notable"
- 결과를 사실 그대로 기술하고, 해석은 근거에 비례하는 수준으로 제한

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

**Tips:**

> **Tip 1 — Table 각주와 Methods Statistics 역할 분리**
> 통계 방법론(검정 선택 이유, 모델 가정, 보정 방법 등)은 Methods Statistics 섹션에만 기술. Table 각주에는 심볼 정의·수식 정의·약어·데이터 표기(mean±SD 등)만 포함하고, 통계 검정은 "See Methods for statistical tests" 또는 "Analyzed with linear mixed models (Methods)" 같은 참조 문구로 대체.
> - 장점: 테이블이 가벼워지고, 방법론 중복 제거
> - ✅ 각주: "*Analyzed with linear mixed models (see Methods)"
> - ❌ 각주: "*Linear mixed model with random intercept for patient, adjusted for age, sex, and baseline VAS, with unstructured covariance matrix..."

> **Tip 2 — Pre-specified Sensitivity Analyses는 Supplementary로 분리**
> 사전 계획된 sensitivity analyses·per-protocol analyses·subgroup 세부 결과는 본문 테이블에 섞지 않고 Supplementary Table로 분리. 본문 테이블 각주에는 "see Supplementary Table S1" 참조만 남김.
> - 장점: primary outcome table의 초점 유지, 본문 복잡도 감소
> - Exception: 핵심 sensitivity analysis가 primary 해석을 바꾸는 경우에 한해 본문 포함 고려

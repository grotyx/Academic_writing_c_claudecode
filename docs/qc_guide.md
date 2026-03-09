# Quality Control Guide (v0.3.0)

## Overview
논문 제출 전 **최소 3라운드**의 QC를 수행해야 합니다. 각 라운드는 서로 다른 측면에 집중하며, 모든 검증 결과는 `review/qc_log.md`에 기록합니다.

---

## QC Round Structure

| Round | Focus | Priority |
|-------|-------|----------|
| Round 1 | 숫자 일관성 (Number Consistency) | CRITICAL |
| Round 2 | 참고문헌 검증 (Reference Verification) | CRITICAL |
| Round 3 | 논리적 흐름 (Logic & Flow) | HIGH |
| Round 4 | 용어/약어/시제 일관성 (Terminology, Abbreviation & Tense) | HIGH |
| Round 5 | 통계적 품질 (Statistical Quality) | HIGH |
| Round 6 | 비판적 검토 (Critical Review) | HIGH |
| Round 7+ | 추가 검토 (Optional refinement) | MEDIUM |

---

## Round 1: Number Consistency Check

### 1.1 Patient/Sample Numbers
모든 섹션에서 환자/샘플 수가 일치하는지 확인

**Check Matrix:**
```
                    Abstract  Methods  Results  Tables  Figures
Total enrolled        [ ]      [ ]      [ ]      [ ]     [ ]
Excluded              [ ]      [ ]      [ ]      [ ]     [ ]
Final analyzed        [ ]      [ ]      [ ]      [ ]     [ ]
Group A (n=?)         [ ]      [ ]      [ ]      [ ]     [ ]
Group B (n=?)         [ ]      [ ]      [ ]      [ ]     [ ]
Lost to follow-up     [ ]      [ ]      [ ]      [ ]     [ ]
```

**Verification Process:**
1. Table 1에서 총 환자 수 확인 → 기준값으로 설정
2. Abstract의 환자 수와 비교
3. Methods의 inclusion 후 환자 수와 비교
4. Results 본문의 환자 수와 비교
5. Flow diagram (있는 경우) 숫자 확인
6. 불일치 발견 시 → 즉시 `review/qc_log.md`에 기록

### 1.2 Statistical Values
통계값이 Results 본문과 Tables에서 일치하는지 확인

**Check Items:**
| Value Type | Results Text | Table | Match? |
|------------|--------------|-------|--------|
| Mean ± SD (primary) | | | [ ] |
| Mean ± SD (secondary) | | | [ ] |
| p-value (primary) | | | [ ] |
| p-value (secondary) | | | [ ] |
| 95% CI | | | [ ] |
| Odds/Risk Ratio | | | [ ] |
| Percentages | | | [ ] |

**Common Errors to Check:**
- 반올림 불일치 (예: Table에 3.24, Results에 3.2)
- p-value 표기 불일치 (예: p=0.023 vs p<0.05)
- CI 범위 오기
- 백분율 계산 오류 (분모 확인)
- Effect size와 CI가 p-value와 논리적으로 일치하는지 (예: CI가 0을 포함하면 p>0.05여야 함)

### 1.3 Time/Period Consistency
연구 기간, 추적 기간 등 시간 관련 수치 확인

**Check Items:**
- [ ] Study period (Abstract = Methods)
- [ ] Follow-up duration (Methods = Results = Tables)
- [ ] Assessment timepoints (Methods에 정의된 대로 Results에 보고)

### 1.4 Demographic Consistency
Table 1의 인구통계와 본문 기술 일치 여부

**Check Items:**
- [ ] Age (mean/median, range)
- [ ] Sex distribution
- [ ] BMI
- [ ] Disease severity/grade
- [ ] Comorbidities

---

## Round 2: Reference Verification

### 2.1 Citation Existence Check
모든 인용이 실제 존재하는 문헌인지 확인

**Process:**
1. `08_references.md` 또는 reference list 열기
2. `knowledge/evidence.md`와 대조
3. knowledge/evidence.md에 없는 reference → 검색하여 확인
4. 각 reference에 대해:
   - [ ] 저자명 정확
   - [ ] 연도 정확
   - [ ] 저널명 정확
   - [ ] 제목 일치 (검색으로 확인)
   - [ ] DOI/PMID 유효

**Red Flags (즉시 확인 필요):**
- knowledge/evidence.md에 기록 없는 citation
- 너무 완벽해 보이는 reference (AI 생성 의심)
- 존재하지 않는 저널명
- 연도와 내용 불일치

### 2.2 Citation Accuracy Check
인용된 내용이 원문과 일치하는지 확인

**For Each Citation, Verify:**
```
Citation #[X]:
- Claim in manuscript: "..."
- Original paper states: "..."
- Match: [ ] Yes / [ ] No / [ ] Partial
- Location in original: Page/Section
- Action needed: [ ] None / [ ] Revise / [ ] Remove
```

**Priority Citations to Verify:**
1. Key statistics cited from other studies
2. Methodology citations ("as described by X et al.")
3. Contradictory findings ("unlike X et al., we found...")
4. Recent citations (last 2 years - easy to verify)

### 2.3 Citation Placement Check
인용이 적절한 위치에 있는지 확인

**Rules:**
- Citation은 specific claim 바로 뒤에 위치
- 문단 끝에 여러 citation을 몰아넣지 않음
- 각 citation이 지지하는 내용이 명확해야 함

**Check Pattern:**
```
❌ Wrong: "BESS shows good outcomes with low complications and fast recovery. [1-5]"
✅ Correct: "BESS shows good clinical outcomes [1,2], with complication rates of 2-5% [3,4] and faster recovery compared to open surgery [5]."
```

### 2.4 Reference List Integrity
- [ ] 본문에 인용된 모든 reference가 list에 있음
- [ ] List의 모든 reference가 본문에 인용됨
- [ ] 번호 순서 정확 (순차적)
- [ ] Format이 target journal style과 일치

---

## Round 3: Logic & Flow Check

### 3.1 Introduction → Methods Alignment
Introduction에서 제시한 목적이 Methods에 반영되었는지 확인

**Check:**
| Introduction States | Methods Addresses | Match? |
|---------------------|-------------------|--------|
| Primary objective | Primary outcome measure | [ ] |
| Secondary objective(s) | Secondary outcome(s) | [ ] |
| Target population | Inclusion criteria | [ ] |
| Comparison groups | Group definitions | [ ] |

### 3.2 Methods → Results Alignment
Methods에 기술된 모든 분석이 Results에 보고되었는지 확인

**Check:**
| Methods Describes | Results Reports | Match? |
|-------------------|-----------------|--------|
| Primary outcome analysis | Primary outcome results | [ ] |
| Secondary outcomes | Secondary results | [ ] |
| Subgroup analyses | Subgroup results | [ ] |
| Statistical tests | Test results (with p-values) | [ ] |

**Red Flags:**
- Methods에 있지만 Results에 없는 분석
- Results에 있지만 Methods에 없는 분석
- Methods의 통계 방법과 다른 방법으로 보고된 결과

### 3.3 Results → Discussion Alignment
Results의 주요 발견이 Discussion에서 해석되었는지 확인

**Check:**
| Key Result | Discussed? | Interpretation Appropriate? |
|------------|------------|----------------------------|
| Primary outcome | [ ] | [ ] |
| Secondary outcome 1 | [ ] | [ ] |
| Secondary outcome 2 | [ ] | [ ] |
| Unexpected finding | [ ] | [ ] |
| Negative result | [ ] | [ ] |

### 3.4 Introduction ↔ Discussion Redundancy Check
내용 중복 여부 확인

**Side-by-Side Comparison:**
```
Topic: [specific topic]
Introduction says: "..."
Discussion says: "..."
Redundant? [ ] Yes / [ ] No
Action: [ ] None / [ ] Revise Introduction / [ ] Revise Discussion
```

**Acceptable vs Unacceptable:**
- ✅ Intro: "Previous studies showed complication rates of 5-10%"
  Discussion: "Our complication rate of 3.2% is lower than previously reported 5-10%"
- ❌ Intro: "BESS is a minimally invasive technique..."
  Discussion: "BESS is a minimally invasive technique..." (verbatim repeat)

### 3.5 Results ↔ Tables Redundancy Check
Results 본문이 Table 숫자를 불필요하게 반복하는지 확인

**Check Each Paragraph:**
```
Results paragraph [X]:
- Contains specific numbers? [ ] Yes / [ ] No
- Numbers also in Table? [ ] Yes / [ ] No
- Redundant? [ ] Yes / [ ] No
- Revision needed? [ ] Yes / [ ] No
```

**Acceptable vs Unacceptable:**
- ✅ "Group A showed significantly lower VAS scores (Table 2, p=0.023)"
- ❌ "Mean VAS score was 3.2±1.4 in Group A and 5.1±1.8 in Group B (p=0.023) (Table 2)"

### 3.6 Conclusion Alignment
Conclusion이 Results에 의해 지지되는지 확인

**Check:**
| Conclusion Statement | Supporting Result | Supported? |
|---------------------|-------------------|------------|
| Main conclusion | | [ ] |
| Secondary conclusion | | [ ] |
| Clinical implication | | [ ] |

**Red Flags:**
- Results에 없는 내용을 Conclusion에서 주장
- 과장된 결론 (overstated claims)
- Limitation을 무시한 결론

---

## Round 4: Terminology, Abbreviation & Tense Check (RECOMMENDED)

> Round 1-3이 내용과 숫자에 집중한다면, Round 4는 표현의 일관성을 검증합니다.
> Abbreviation과 Tense 오류는 리뷰어가 자주 지적하는 항목이므로 반드시 수행을 권장합니다.

### 4.1 Terminology Consistency
동일한 개념에 동일한 용어 사용 확인

**Common Issues:**
| Check | Consistent? |
|-------|-------------|
| Procedure name (동일한 명칭) | [ ] |
| Outcome measure names | [ ] |
| Group labels (A/B, intervention/control) | [ ] |
| Abbreviations | [ ] |

### 4.2 Abbreviation Check (HIGH)
- [ ] 모든 약어가 첫 사용 시 풀어서 정의됨
- [ ] Abstract에서 별도로 정의됨 (standalone)
- [ ] Tables/Figures에서 footnote로 정의됨
- [ ] 일관된 약어 사용 (혼용 없음)

### 4.3 Tense Consistency (HIGH)
- [ ] Methods: past tense
- [ ] Results: past tense
- [ ] Discussion (own findings): past tense
- [ ] Discussion (established facts): present tense
- [ ] Conclusion: present tense (implications)

---

## Round 5: Statistical Quality Check (HIGH)

> 통계 분석의 적절성과 보고 품질을 검증합니다.
> 상세 기준: `docs/statistical_analysis_guide.md` 참조

### 5.1 Analysis Hierarchy
- [ ] Primary outcome이 명확히 정의되었는가?
- [ ] Secondary outcomes이 구분되어 있는가?
- [ ] Exploratory analysis가 별도로 표시되었는가?
- [ ] Multiple comparison correction이 필요한 곳에 적용되었는가?

### 5.2 Statistical Parsimony
- [ ] 불필요한 통계 검정이 포함되지 않았는가?
- [ ] RCT인 경우: Table 1에 p-value가 없는가? (CONSORT 2010 원칙)
- [ ] 관찰 연구: Table 1 p-value가 연구 목적에 부합하는가?
- [ ] 모든 통계 검정이 연구 목적과 관련 있는가?

### 5.3 Effect Size & CI
- [ ] 주요 결과에 effect size가 보고되었는가? (Cohen's d, OR, RR, HR 등)
- [ ] 95% CI가 주요 비교에 포함되었는가?
- [ ] p-value만으로 결과를 해석하지 않았는가?

### 5.4 Non-significant Results
- [ ] "No difference" 대신 "no significant difference"로 기술했는가?
- [ ] CI를 통해 추정의 정밀도를 보여주었는가?
- [ ] "insignificant"(하찮은)를 "not significant"와 혼용하지 않았는가?
- [ ] "failed to show" 등 방향성을 암시하는 표현을 사용하지 않았는가?

### 5.5 Subgroup & Sensitivity
- [ ] Subgroup analysis가 사전 지정(pre-specified)되었는가?
- [ ] Interaction test가 수행되었는가? (within-group p-value만으로 해석하지 않았는가?)
- [ ] 필요한 sensitivity analysis가 수행되었는가?

---

## Round 6: Critical Review — 비판적 검토 (HIGH)

> 리뷰어의 시각에서 논문의 논리적 취약점과 과장을 점검합니다.
> "만약 내가 이 논문의 리뷰어라면 무엇을 지적할까?"

### 6.1 Overclaiming Check (과장 여부)

**Conclusion vs Results 비교:**

| Check | Pass? |
|-------|-------|
| Conclusion이 Results에 의해 직접 지지되는가? | [ ] |
| "First study to..." 등 과장된 표현이 없는가? | [ ] |
| 인과관계를 주장하지 않는가? (관찰 연구의 경우) | [ ] |
| "Proves" 대신 "suggests", "demonstrates" 등 적절한 동사를 사용했는가? | [ ] |
| Clinical implication이 데이터 범위를 초과하지 않는가? | [ ] |

**과장 표현 체크:**
- ❌ "This study proves that..." (관찰 연구에서)
- ❌ "The first study to demonstrate..." (확인 불가능한 주장)
- ❌ "Dramatic improvement" → ✅ "Significant improvement"
- ❌ "Clearly superior" → ✅ "Associated with better outcomes"

### 6.2 Logical Fallacy Check (논리적 오류)

| Fallacy | Description | Check |
|---------|-------------|-------|
| Absence of evidence | "차이가 없었다" = "동등하다"로 해석 | [ ] |
| Post hoc reasoning | 사후 분석 결과를 사전 가설처럼 기술 | [ ] |
| Cherry picking | 유리한 결과만 강조, 불리한 결과 축소 | [ ] |
| Ecological fallacy | 그룹 수준 결과를 개인에게 적용 | [ ] |
| Correlation ≠ Causation | 상관관계를 인과관계로 기술 | [ ] |

### 6.3 Bias Acknowledgment (편향 인정)

- [ ] Selection bias가 Limitations에서 다루어졌는가?
- [ ] Information/measurement bias가 언급되었는가?
- [ ] Confounding factors가 식별되고 대응되었는가?
- [ ] Loss to follow-up의 영향이 논의되었는가?
- [ ] 후향적 연구의 한계가 명시되었는가? (해당 시)

### 6.4 Balanced Literature Review (균형 잡힌 문헌 고찰)

- [ ] 우리 결과와 일치하는 문헌만 인용하지 않았는가?
- [ ] 상반된 결과를 보인 연구도 공정하게 인용했는가?
- [ ] 상반된 결과에 대한 합리적 설명이 있는가? (대상군, 방법, 추적기간 차이 등)
- [ ] 최근 문헌이 누락되지 않았는가?

### 6.5 Generalizability (일반화 가능성)

- [ ] 연구 대상군의 특성이 결론의 적용 범위와 일치하는가?
- [ ] 단일 기관 연구의 한계가 논의되었는가?
- [ ] 특정 인구집단 결과를 전체로 일반화하지 않았는가?
- [ ] "All patients" 대신 "patients with [specific criteria]"로 한정했는가?

### 6.6 Reviewer Anticipation (리뷰어 예상 질문)

스스로 답해 보기:

```
Q1: 왜 이 통계 방법을 선택했는가? (다른 방법이 더 적절하지 않은가?)
Q2: Sample size가 충분한가? Power analysis 근거는?
Q3: 이 결과가 confounding 때문은 아닌가?
Q4: Follow-up 기간이 충분한가?
Q5: 이 연구가 기존 연구와 다른 점은 무엇이며, 왜 필요한가?
Q6: Missing data가 결과에 영향을 줄 수 있는가?
```

---

## QC Documentation Template

### review/qc_log.md
```markdown
# QC Log for [Paper Title]

## Round 1: Number Consistency
**Date:** YYYY-MM-DD
**Performed by:** [Name/Claude]

### Findings:
| Issue | Location | Current | Should Be | Fixed? |
|-------|----------|---------|-----------|--------|
| | | | | [ ] |

### Summary:
- Total issues found: X
- Critical issues: X
- Fixed: X / Pending: X

---

## Round 2: Reference Verification
**Date:** YYYY-MM-DD

### Findings:
| Ref # | Issue | Action | Fixed? |
|-------|-------|--------|--------|
| | | | [ ] |

### Summary:
- References checked: X/X
- Issues found: X
- Fixed: X / Pending: X

---

## Round 3: Logic & Flow
**Date:** YYYY-MM-DD

### Findings:
| Section | Issue | Action | Fixed? |
|---------|-------|--------|--------|
| | | | [ ] |

### Summary:
- Redundancy issues: X
- Alignment issues: X
- Fixed: X / Pending: X

---

## Round 5: Statistical Quality
**Date:** YYYY-MM-DD

### Findings:
| Item | Issue | Action | Fixed? |
|------|-------|--------|--------|
| | | | [ ] |

### Summary:
- Parsimony issues: X
- Effect size/CI missing: X
- Fixed: X / Pending: X

---

## Round 6: Critical Review
**Date:** YYYY-MM-DD

### Findings:
| Category | Issue | Severity | Action | Fixed? |
|----------|-------|----------|--------|--------|
| Overclaiming | | | | [ ] |
| Logical fallacy | | | | [ ] |
| Bias | | | | [ ] |
| Literature balance | | | | [ ] |
| Generalizability | | | | [ ] |

### Reviewer Anticipated Questions:
| Q# | Question | Addressed in Manuscript? | Location |
|----|----------|--------------------------|----------|
| | | [ ] | |

### Summary:
- Overclaiming issues: X
- Logic issues: X
- Fixed: X / Pending: X

---

## Final Sign-off
- [ ] All Round 1 issues resolved
- [ ] All Round 2 issues resolved
- [ ] All Round 3 issues resolved
- [ ] All Round 5 issues resolved
- [ ] All Round 6 issues resolved
- [ ] Ready for submission

**Date:** YYYY-MM-DD
**Signed off by:** [Name]
```

---

## QC Commands Reference

| Command | Action |
|---------|--------|
| `Run QC Round 1` | Number consistency check |
| `Run QC Round 2` | Reference verification |
| `Run QC Round 3` | Logic and flow check |
| `Run QC Round 4` | Terminology, abbreviation & tense check |
| `Run QC Round 5` | Statistical quality check |
| `Run QC Round 6` | Critical review (비판적 검토) |
| `Compare [section1] vs [section2]` | Side-by-side comparison |
| `Extract all numbers from [section]` | List all numerical values |
| `Verify reference [#]` | Check specific citation |
| `Check redundancy intro-discussion` | Detailed overlap analysis |
| `Generate QC report` | Summary of all findings |

---

## Quick Reference: What to Check Where

| Check Type | Sections to Compare |
|------------|---------------------|
| Patient numbers | Abstract ↔ Methods ↔ Results ↔ Table 1 ↔ Flow diagram |
| Statistical values | Results ↔ Tables ↔ Abstract |
| Study period | Abstract ↔ Methods |
| Primary outcome definition | Methods ↔ Results ↔ Tables |
| Citation accuracy | Text ↔ knowledge/evidence.md ↔ Original PDF |
| Objective alignment | Introduction (last para) ↔ Methods ↔ Conclusion |
| Terminology | All sections (same terms throughout) |

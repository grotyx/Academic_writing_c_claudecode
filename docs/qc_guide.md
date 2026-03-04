# Quality Control Guide (v0.2.1)

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
| Round 5+ | 추가 검토 (Optional refinement) | MEDIUM |

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

## Final Sign-off
- [ ] All Round 1 issues resolved
- [ ] All Round 2 issues resolved
- [ ] All Round 3 issues resolved
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

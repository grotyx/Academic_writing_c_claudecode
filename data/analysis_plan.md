# Analysis Plan

> 통계 분석 전 반드시 작성하고 사용자 승인 후 진행합니다.
> 상세 통계 가이드: `docs/statistical_analysis_guide.md` 참조

---

## 1. Research Question & Hypothesis (연구 질문 및 가설)

**연구 질문:**
- [연구 질문을 구체적으로 기술]

**가설:**
- H0: [귀무가설]
- H1: [대립가설]

---

## 2. Study Population (대상 선정/제외 기준)

**Design:** `[연구 설계 입력: RCT / Cohort / Case-Control / etc.]`

**Inclusion Criteria:**
- [기준 1]
- [기준 2]

**Exclusion Criteria:**
- [기준 1]
- [기준 2]

**Expected Sample Size:** [N]

---

## 3. Data Overview

### Source File
- **File:** `[filename.csv/xlsx]`
- **Rows:** `[n rows]`
- **Columns:** `[n columns]`

### Variable Summary

| Variable | Type | Description | Role | Missing (%) |
|----------|------|-------------|------|-------------|
| `[var]` | Continuous/Categorical | `[설명]` | Primary/Secondary/Covariate | `[%]` |

---

## 4. Variable Definitions (변수 정의)

### Primary Endpoint
- **Variable:** [변수명]
- **Definition:** [정의]
- **Measurement:** [측정 방법 및 시점]

### Secondary Endpoints
- [변수명]: [정의 및 측정 방법]
- [변수명]: [정의 및 측정 방법]

### Exploratory Endpoints (해당 시)
- [변수명]: [정의]

### Covariates / Confounders
- [변수명]: [정의 및 선정 근거]

---

## 5. Statistical Methods (통계 검정법 선택 및 근거)

### Descriptive Statistics
- Continuous (normal): mean ± SD
- Continuous (non-normal): median [IQR]
- Categorical: n (%)
- Normality test: Shapiro-Wilk (n < 50) / Kolmogorov-Smirnov (n ≥ 50)

### Comparative Analysis

| Comparison | Variable Type | Distribution | Test | Justification |
|------------|---------------|--------------|------|---------------|
| [비교 내용] | Continuous/Categorical | Normal/Non-normal | [검정법] | [선택 근거] |

### Advanced Analysis (해당 시)
- [ ] Linear regression — [목적]
- [ ] Logistic regression — [목적]
- [ ] Cox regression — [목적]
- [ ] Other: [specify]

---

## 6. Significance Level & Multiple Comparison (유의수준 및 다중비교 보정)

| Parameter | Value |
|-----------|-------|
| Significance level (α) | 0.05 |
| Confidence interval | 95% |
| Multiple comparison correction | [None / Bonferroni / Holm / FDR] |
| Correction 적용 대상 | [어떤 비교에 적용할지] |

---

## 7. Output Plan

### Scripts (→ data/py/)
| Script | Purpose |
|--------|---------|
| 01_descriptive.py | Baseline demographics |
| 02_comparative.py | Group comparisons |
| 03_regression.py | Advanced analysis (if needed) |

### Tables (→ drafts/)
| Table | Content | Source |
|-------|---------|--------|
| table_1.md | Demographics & Baseline | results/table1_demographics.csv |
| table_2.md | Primary Outcomes | results/table2_outcomes.csv |
| table_3.md | [Additional Analysis] | results/table3_*.csv |

### Figures (→ drafts/figures/)
| Figure | Content | Type |
|--------|---------|------|
| [fig_N.png] | [내용] | [Bar/Box/Line/Survival/Flow] |

---

## Checklist Before Proceeding

- [ ] 연구 질문과 가설이 명확한가?
- [ ] 선정/제외 기준이 구체적인가?
- [ ] Primary endpoint가 1개로 정의되었는가?
- [ ] 통계 검정법이 데이터 유형에 적합한가?
- [ ] 다중비교 보정이 필요한 곳에 계획되었는가?
- [ ] **사용자 승인 완료** → 분석 진행

# Statistical Analysis Guide (v0.3.0)

> 통계 분석 수행 및 결과 정리를 위한 상세 가이드
> Dr. Statistician의 역할을 기반으로 작성됨

---

## 1. Analysis Workflow Overview

```
Phase 2: Statistical Analysis

Step 1: Data Preparation
├── Place CSV/XLSX in data/
├── Verify data integrity
└── Document missing values

Step 2: Analysis Planning
├── Run "Analyze data" command
├── Auto-generate data/analysis_plan.md
│   ├── Variable types detected
│   ├── Normality assessed
│   ├── Primary/secondary/exploratory endpoints defined
│   └── Appropriate tests selected
└── Review with Dr. Statistician perspective

Step 3: Script Generation
├── Run "Generate analysis scripts"
└── Creates data/py/
    ├── 01_descriptive.py
    ├── 02_comparative.py
    └── 03_regression.py (if needed)

Step 4: Execute Analysis
├── Run "Run analysis"
└── Export to results/
    ├── table1_demographics.csv
    ├── table2_outcomes.csv
    └── statistics_summary.csv

Step 5: Output Generation
├── Run "Generate tables"
├── Run "Generate figures" (if needed)
└── Creates drafts/
    ├── table_1.md, table_2.md, ...
    └── figures/fig_*.png
```

---

## 2. Statistical Parsimony (통계 절제 원칙)

> **핵심: 꼭 필요한 통계만 적절하게 사용한다. 모든 변수에 검정을 하지 않는다.**

### 원칙

1. **연구 질문에 답하는 데 필요한 통계만 사용한다**
   - 변수가 20개라고 20개 모두 검정하지 않는다
   - Primary outcome 비교가 핵심이면, 그것에 집중한다

2. **사전 계획된 분석만 정식 검정한다**
   - 프로토콜이나 analysis plan에 미리 정의된 비교만 p-value 보고
   - 데이터를 본 후 추가한 분석은 "탐색적(exploratory)"으로 명시

3. **p-value와 함께 95% CI를 병행 보고한다**
   - p-value만으로는 효과의 크기와 정밀도를 알 수 없다
   - 95% CI 보고가 점차 표준이 되고 있다 (NEJM, CONSORT 권고)
   - 현재 정형외과 영역에서는 p-value 보고가 표준이지만, CI 병행 보고가 추세

4. **다중 비교 문제를 인식한다**
   - 20개 변수를 검정하면 1개는 우연히 p<0.05 (확률 ~64%)
   - 비교가 많을수록 다중 비교 보정 고려 필요

### Table별 p-value 보고 원칙

| Table | RCT | 관찰 연구 (Cohort, Case-control) |
|-------|-----|----------------------------------|
| **Table 1** (Baseline) | p-value **미사용** (CONSORT 권고: 무작위 배정이므로 차이는 우연) | p-value 사용 가능 (그룹 간 비교가 의미 있음) |
| **Table 2** (Main Results) | p-value 사용 (primary/secondary outcome) | p-value 사용 |
| **Table 3+** (Additional) | 사전 지정된 분석만 p-value | 사전 지정된 분석만 p-value |

### RCT Table 1 대안

p-value 대신 **Standardized Mean Difference (SMD)** 사용 가능:

```markdown
| Variable | Group A (n=XX) | Group B (n=XX) | SMD |
|----------|----------------|----------------|-----|
| Age, years | 54.3 ± 12.1 | 52.1 ± 11.8 | 0.09 |
| Sex, male | 45 (60%) | 42 (56%) | 0.08 |
```

> SMD < 0.1이면 잘 균형 잡힌 것으로 판단 (propensity score matching에서도 사용)

---

## 3. Analysis Hierarchy (분석 위계)

> **모든 분석이 동등하지 않다. 사전에 위계를 정하고, 그에 맞게 보고한다.**

| Level | 특성 | 보고 방법 | 예시 |
|-------|------|----------|------|
| **Primary** | 1개 (최대 2개) 사전 지정 | p-value + 95% CI + effect size | VAS back pain 변화량 |
| **Secondary** | 사전 지정, primary 보조 | p-value + 95% CI | VAS leg pain, ODI |
| **Exploratory** | 사전 미지정 또는 가설 생성 | p-value + 95% CI (exploratory로 명시) | ROM, EQ-5D, 수술 시간 |

### 실무 적용

```
analysis_plan.md 작성 시:

## Endpoints
- Primary: VAS back pain change at 12 months
- Secondary: ODI, VAS leg pain, patient satisfaction
- Exploratory: ROM, operative time, blood loss, hospital stay, EQ-5D
```

**Methods에 기술할 때:**
- "The primary endpoint was the change in VAS back pain score at 12 months."
- "Secondary endpoints included ODI, VAS leg pain, and patient satisfaction."
- "Operative time, blood loss, and length of hospital stay were also compared."

**탐색적 분석 결과 보고 시:**
- "In exploratory analyses, operative time was shorter in Group A (Table 3)."
- Discussion에서 해석 시 "이 결과는 탐색적이며, 향후 확인 연구가 필요하다" 부기

---

## 4. Study Design → Statistics Matching (연구 설계별 통계 매칭)

> **연구 설계에 따라 사용할 통계 방법이 결정된다.**

### 설계별 주요 통계

| Study Design | Primary Statistical Approach | 주요 효과 지표 |
|-------------|------------------------------|----------------|
| **RCT (2 groups)** | t-test / Mann-Whitney (연속형), Chi-square / Fisher (범주형) | Mean difference, RR, NNT |
| **RCT (>2 groups)** | ANOVA / Kruskal-Wallis + post-hoc | Mean difference |
| **Cohort (time-to-event)** | Kaplan-Meier + log-rank, Cox regression | HR, 95% CI |
| **Cohort (비교)** | t-test / Mann-Whitney, multivariable regression | OR, RR, adjusted difference |
| **Case-control** | Logistic regression | OR, 95% CI |
| **Before-after (paired)** | Paired t-test / Wilcoxon signed-rank | Mean difference |
| **Cross-sectional** | Chi-square, logistic regression | OR, prevalence ratio |
| **Correlation** | Pearson (정규) / Spearman (비정규) | r, 95% CI |

### 회귀 분석 선택

| Outcome Type | Model | 결과 지표 |
|-------------|-------|----------|
| 연속형 | Linear regression | β coefficient, 95% CI |
| 이분형 (예/아니오) | Logistic regression | OR, 95% CI |
| 시간-사건 | Cox proportional hazards | HR, 95% CI |
| 반복 측정 | GEE / Mixed-effects model | β, 95% CI |
| 카운트 | Poisson / Negative binomial | IRR, 95% CI |

### Propensity Score Analysis

관찰 연구에서 confounding 보정 시:

| Method | 사용 시점 |
|--------|----------|
| PS matching | 충분한 sample size, 1:1 매칭 가능 시 |
| PS weighting (IPTW) | 전체 sample 보존 필요 시 |
| PS adjustment (covariate) | 가장 단순, 모든 경우 사용 가능 |

---

## 5. Statistical Test Selection

### Dr. Statistician's Decision Tree

```
Is the outcome variable continuous or categorical?

CONTINUOUS:
├── Comparing 2 groups?
│   ├── Data normally distributed?
│   │   ├── Yes → Independent t-test
│   │   └── No → Mann-Whitney U test
│   └── Paired/matched data?
│       ├── Normal → Paired t-test
│       └── Non-normal → Wilcoxon signed-rank
│
├── Comparing >2 groups?
│   ├── Normal → One-way ANOVA
│   │   └── Post-hoc: Tukey or Bonferroni
│   └── Non-normal → Kruskal-Wallis
│       └── Post-hoc: Dunn's test
│
└── Relationship between variables?
    ├── Normal → Pearson correlation
    └── Non-normal → Spearman correlation

CATEGORICAL:
├── 2×2 table?
│   ├── Expected counts ≥5 → Chi-square
│   └── Expected counts <5 → Fisher's exact
│
└── Larger table?
    └── Chi-square test
```

### Normality Testing

```python
# For n < 50
from scipy.stats import shapiro
stat, p = shapiro(data)
normal = p > 0.05

# For n ≥ 50
from scipy.stats import kstest
stat, p = kstest(data, 'norm')
normal = p > 0.05
```

### Multiple Comparison Correction

| # of Comparisons | Correction Method |
|------------------|-------------------|
| 2-3 | Usually not needed |
| 4-10 | Bonferroni |
| >10 | Benjamini-Hochberg (FDR) |

---

## 6. Clinical vs Statistical Significance (임상적 유의성)

> **p < 0.05라고 임상적으로 의미 있는 것은 아니다.**

### 핵심 개념

```
n=500: VAS 차이 0.3점, p=0.02  → 통계적 유의 / 임상적 무의미
n=30:  VAS 차이 2.5점, p=0.08  → 통계적 비유의 / 임상적으로 큰 차이 가능
```

**통계적 유의성은 sample size에 좌우되지만, 임상적 유의성은 효과 크기에 좌우된다.**

### Effect Size (효과 크기)

p-value 옆에 효과 크기를 함께 보고한다:

| Measure | 용도 | 해석 기준 |
|---------|------|----------|
| **Mean Difference** | 두 군 평균 차이 | MCID와 비교 |
| **Cohen's d** | 표준화된 평균 차이 | 0.2 작음, 0.5 중간, 0.8 큼 |
| **Odds Ratio (OR)** | 이분형 결과 (case-control) | 1 = 차이 없음 |
| **Risk Ratio (RR)** | 이분형 결과 (cohort, RCT) | 1 = 차이 없음 |
| **Hazard Ratio (HR)** | 시간-사건 분석 | 1 = 차이 없음 |
| **NNT** | 1명 추가 성공에 필요한 치료 수 | 낮을수록 효과 큼 |

### MCID (Minimal Clinically Important Difference)

> 환자가 실제로 "나아졌다"고 느끼는 최소 변화량

**척추 영역 주요 MCID:**

| Outcome Measure | MCID | 출처 |
|----------------|------|------|
| VAS (0-10) | 1.5-2.0점 | Ostelo et al., Spine 2008 |
| ODI (0-100) | 10-12.8점 | Copay et al., Spine J 2008 |
| SF-36 PCS | 4.9점 | Copay et al., Spine J 2008 |
| EQ-5D | 0.03-0.08 | Parker et al., Spine 2012 |
| NDI (0-100) | 7.5-10점 | Young et al., Spine 2009 |
| JOA (cervical) | 2점 | Hirabayashi et al. |

**활용:** "VAS가 2.8점 감소하여 MCID(1.5점)를 초과하였으므로, 통계적으로 유의할 뿐 아니라 임상적으로도 의미 있는 개선이다."

### NNT (Number Needed to Treat)

```
수술 A 성공률 80%, 수술 B 성공률 60%
→ 차이 = 20% = 0.20
→ NNT = 1 / 0.20 = 5
→ "수술 A로 1명 더 성공시키려면 5명을 A로 수술해야 한다"
```

| NNT | 해석 |
|-----|------|
| < 5 | 매우 효과적 |
| 5-10 | 효과적 |
| > 10 | 제한적 효과 |
| ∞ | 차이 없음 |

> CONSORT에서 이분형 결과에 NNT 보고를 권고함

---

## 7. Subgroup Analysis Guidelines (하위군 분석)

### 하위군 분석을 하면 **안 되는** 경우

- 전체 결과가 명확히 비유의 → 하위군에서 "유의"를 찾는 것은 거의 확실히 false positive
- 사전 지정되지 않은 하위군
- 생물학적/임상적 근거 없는 구분
- 하위군 내 sample size가 너무 작아 의미 있는 검정력 없음
- 5개 이상 다수 하위군 (보정 없이)

### 하위군 분석 규칙 (할 때)

1. **사전 지정** (protocol/analysis plan에 명시)
2. **소수만** (3-5개 이하)
3. **Interaction test 사용** (하위군 내 p-value가 아니라 interaction p-value)
4. **전부 보고** (유의한 것만 선택적으로 보고하지 않음)
5. **탐색적으로 명시** (post-hoc이면 반드시 "exploratory"로 기술)

### Interaction Test vs Within-group Test

```
잘못된 방식:
  남성: p=0.02 (유의) / 여성: p=0.35 (비유의)
  → "남성에서만 효과 있음" ❌

올바른 방식:
  Treatment × Sex interaction p=0.04
  → "성별에 따라 치료 효과가 다를 수 있음 (interaction p=0.04)" ✅
```

---

## 8. Non-significant Results (비유의 결과 보고)

### 사용해야 하는 표현

| 상황 | 올바른 표현 | 잘못된 표현 |
|------|-----------|-----------|
| p > 0.05 | "No statistically significant difference was observed" | "No difference exists" |
| p = 0.06-0.10 | "The difference was not statistically significant (*p* = 0.08)" | "Trending toward significance" |
| CI가 넓음 | "The wide CI suggests insufficient power to detect a difference" | "Nearly significant" |
| CI가 MCID 제외 | "The 95% CI excluded clinically meaningful differences" | "Marginally significant" |

### 비유의 결과 해석 프레임워크

```
p > 0.05일 때 95% CI를 확인:

1. CI가 좁고 0을 포함 → "차이 없음"에 가까움 (underpowered 아님)
   예: mean diff = 0.3, 95% CI: -0.5 to 1.1
   → "임상적으로 의미 있는 차이가 없음을 시사"

2. CI가 넓고 MCID를 포함 → underpowered 가능성
   예: mean diff = 3.2, 95% CI: -1.5 to 7.9
   → "검정력 부족으로 확정적 결론 어려움, 추가 연구 필요"
```

### 절대 사용 금지 표현

- ~~"trending toward significance"~~
- ~~"marginally significant"~~
- ~~"approaching significance"~~
- ~~"borderline significant"~~
- ~~"a trend was noted"~~

---

## 9. Sensitivity Analysis (민감도 분석)

### 민감도 분석이 필요한 경우

| 상황 | 민감도 분석 내용 |
|------|----------------|
| Missing data > 5% | Complete case vs. multiple imputation 비교 |
| Outlier 존재 | Outlier 제외 후 재분석 |
| Outcome 정의 변경 가능 | 대안적 정의로 재분석 |
| Confounder 선택 불확실 | 다른 공변량 조합으로 재분석 |
| Per-protocol vs ITT | 두 population 모두 분석 |
| 관찰 연구 | Unmeasured confounding 평가 (E-value) |

### 보고 방법

Methods에 기술:
> "Sensitivity analyses were performed to assess the robustness of the primary findings."

Results에 기술:
> "Sensitivity analyses excluding outliers (n=3) yielded consistent results (Supplementary Table X)."

또는:
> "Results were robust across all sensitivity analyses (Supplementary Tables X-Y)."

---

## 10. Table Structure Standards

### Standard Table Sequence

| Table # | Content | Purpose |
|---------|---------|---------|
| Table 1 | Baseline Characteristics | Demographics, clinical features at enrollment |
| Table 2 | Main Results | Primary & key secondary outcomes |
| Table 3+ | Additional Analyses | Subgroup, sensitivity, regression results |
| Suppl. Tables | Supporting Data | Detailed breakdowns, exploratory analyses |

### Table 1: Baseline Characteristics

**RCT (p-value 미사용):**

```markdown
| Variable | Group A (n=XX) | Group B (n=XX) |
|----------|----------------|----------------|
| **Demographics** |
| Age, years | XX.X ± X.X | XX.X ± X.X |
| Sex, male | XX (XX.X%) | XX (XX.X%) |
| BMI, kg/m² | XX.X ± X.X | XX.X ± X.X |
| **Clinical Features** |
| Disease duration | XX.X ± X.X | XX.X ± X.X |
| Severity score | XX.X ± X.X | XX.X ± X.X |

Data presented as mean ± SD or n (%).
```

**관찰 연구 (p-value 사용):**

```markdown
| Variable | Group A (n=XX) | Group B (n=XX) | p-value |
|----------|----------------|----------------|---------|
| **Demographics** |
| Age, years | XX.X ± X.X | XX.X ± X.X | 0.XXX |
| Sex, male | XX (XX.X%) | XX (XX.X%) | 0.XXX |
| BMI, kg/m² | XX.X ± X.X | XX.X ± X.X | 0.XXX |
| **Clinical Features** |
| Disease duration | XX.X ± X.X | XX.X ± X.X | 0.XXX |
| Severity score | XX.X ± X.X | XX.X ± X.X | 0.XXX |

Data presented as mean ± SD or n (%).
*Student's t-test; †Chi-square test; ‡Mann-Whitney U test
```

### Table 2: Main Results Template

```markdown
| Outcome | Group A | Group B | Difference (95% CI) | p-value |
|---------|---------|---------|---------------------|---------|
| **Primary Outcome** |
| [Outcome name] | XX.X ± X.X | XX.X ± X.X | X.X (X.X to X.X) | 0.XXX |
| **Secondary Outcomes** |
| [Outcome 2] | XX.X ± X.X | XX.X ± X.X | X.X (X.X to X.X) | 0.XXX |
```

### Table 개수 가이드

> **권장:** 가급적 5개 이하. 단, 논문 흐름상 필수적인 경우 5개 초과도 가능.

| 저널 유형 | 일반적 한도 |
|----------|------------|
| Spine, 정형외과 저널 | Tables + Figures 합계 5-8개 |
| JBJS, Clin Orthop | Tables + Figures 합계 5-7개 |
| 일반 권장 | Tables 5개 이하, 초과분은 Supplement |

**Supplement로 분리 고려:**
- [ ] 꼭 필요하지 않은 세부 분석
- [ ] Detailed subgroup breakdowns
- [ ] Sensitivity analysis results
- [ ] Complete regression model outputs
- [ ] Extended follow-up data
- [ ] Per-protocol vs ITT comparisons

**Main manuscript 유지:**
- [ ] Primary/secondary outcome 이해에 필수적인 내용
- [ ] 논문의 핵심 주장을 뒷받침하는 데이터

### Table Formatting Rules

- Title: 독립적으로 이해 가능하게 (self-explanatory)
- 모든 약어는 footnotes에 정의
- 사용된 통계 검정은 footnotes에 명시
- p-value: exact value (*p* = 0.023) 또는 threshold (*p* < 0.001)
- 소수점 정렬
- 일관된 유효 숫자
- 수평선은 최소한으로 (상단, 헤더 하단, 표 하단)
- **Footnote symbols:** \*, †, ‡, §, ‖, ¶ (이 순서대로)

**Example Table Footer:**
```
Data presented as mean ± SD, median [IQR], or n (%).
*Student's t-test; †Mann-Whitney U test; ‡Chi-square test
Abbreviations: BMI, body mass index; VAS, visual analog scale
```

---

## 11. Figure Guidelines

### Standard Figure Types

| Figure # | Common Content | Best Use Case |
|----------|----------------|---------------|
| Figure 1 | Patient Flow (CONSORT/STROBE) | Always required for clinical studies |
| Figure 2 | Primary Outcome Visualization | When visual comparison adds value |
| Figure 3 | Time-course / Survival | Longitudinal data, KM curves |
| Suppl. Figs | Secondary visualizations | Supporting data |

### Study Design별 필수/권장 Figure

| Study Design | 필수 Figure | 권장 Figure |
|-------------|------------|------------|
| RCT | CONSORT flow diagram | Outcome trend, forest plot (subgroup) |
| Cohort (time-to-event) | Kaplan-Meier curve | Forest plot (multivariate) |
| Cohort (비교) | Flow diagram | Bar/box plot (outcomes) |
| Meta-analysis | Forest plot | Funnel plot |
| Diagnostic study | ROC curve | - |

### Figure vs Table Decision Matrix

**Ask before creating:**
> "이 데이터는 Table로 표현하는 것이 좋을까요, Figure로 표현하는 것이 좋을까요?"

| Data Type | Prefer Table | Prefer Figure |
|-----------|--------------|---------------|
| Exact values needed | ✓ | |
| Trends over time | | ✓ |
| Comparisons (2-3 groups) | ✓ | |
| Comparisons (>3 groups) | | ✓ |
| Distribution shape | | ✓ |
| Survival analysis | | ✓ |
| Correlation patterns | | ✓ |
| Regression coefficients | ✓ | (forest plot) |

### Figure Types by Purpose

```
Comparison:
├── Bar chart (means)
├── Box plot (distributions)
└── Violin plot (detailed distributions)

Trends:
├── Line chart (time series)
├── Kaplan-Meier (survival)
└── Spaghetti plot (individual trajectories)

Relationships:
├── Scatter plot (correlation)
├── Forest plot (effect sizes, subgroups, regression)
└── Heat map (multiple correlations)
```

### Forest Plot 가이드

| 데이터 유형 | X축 스케일 | 기준선 |
|------------|-----------|-------|
| OR, RR, HR | **Logarithmic** | 1.0 |
| Mean difference | Linear | 0 |
| SMD | Linear | 0 |

> 다변량 회귀에서 변수 5개 이상이면 forest plot이 table보다 시각적으로 효과적

### Resolution & Format Requirements

| Element | Minimum DPI | 권장 Format |
|---------|------------|------------|
| Line art (graphs, diagrams) | 1000-1200 | TIFF, EPS |
| Halftone (photos, CT, MRI) | 300 | TIFF, JPEG |
| Combination (line + image) | 500 | TIFF |

**일반 요구사항:**
- Minimum width: 3.5 inches (single column), 7 inches (double column)
- Font size in figures: ≥ 8pt
- Color: RGB for online, CMYK for print (저널 확인)
- Python matplotlib 기본 출력 시: `plt.savefig('fig.tiff', dpi=300, bbox_inches='tight')`

---

## 12. Redundancy Prevention Rules

### Avoid Triple Duplication

The same data should preferably not appear in all three:
1. Results text
2. Table
3. Figure

**Allowed Combinations:**
- Table only (most common)
- Figure only (visual emphasis)
- Table + brief text reference
- Figure + brief text reference

**Avoid (지양):**
- Full numbers in text + same numbers in table
- Bar chart + table with same exact data
- Detailed text description + figure showing same

### Results Text Writing Rules

| Situation | Results Text Should Say | NOT Say |
|-----------|-------------------------|---------|
| Data in Table 1 | "Baseline characteristics are shown in Table 1" | "Mean age was 54.3±12.1..." |
| Data in Table 2 | "Group A showed significantly better outcomes (Table 2)" | "VAS was 3.2±1.4 vs 5.1±1.8 (p=0.023)" |
| Data in Figure | "The trend is illustrated in Figure 2" | Detailed description of visual |

### Acceptable Text Content

Results text SHOULD include:
- Key finding statements (qualitative)
- Direction of effects
- Significance statements
- Reference to tables/figures
- Numbers NOT in any table (e.g., flow diagram numbers)

---

## 13. Methods Statistical Section Checklist

> Methods에 Statistical Analysis 섹션 작성 시 반드시 포함할 항목

| # | Item | Level | Example |
|---|------|-------|---------|
| 1 | Primary endpoint 정의 | 필수 | "The primary endpoint was change in VAS at 12 months" |
| 2 | 기술 통계 방법 | 필수 | "Continuous variables: mean ± SD or median [IQR]; categorical: n (%)" |
| 3 | 정규성 검정 방법 | 필수 | "Normality was assessed using the Shapiro-Wilk test" |
| 4 | 비교 통계 검정명 + 근거 | 필수 | "Between-group comparisons used the independent t-test for normally distributed variables and the Mann-Whitney U test otherwise" |
| 5 | 다중 비교 보정 (해당 시) | 필수 | "Bonferroni correction was applied for multiple comparisons" |
| 6 | 유의 수준 | 필수 | "Statistical significance was set at *p* < 0.05 (two-sided)" |
| 7 | Sample size / power 계산 | 필수 (전향적) | "A sample size of 45 per group was required (α=0.05, power=0.80, effect size=0.6)" |
| 8 | Missing data 처리 | 필수 | "Missing data were handled using multiple imputation" |
| 9 | 소프트웨어 + 버전 | 필수 | "Statistical analyses were performed using R version 4.3.0" |
| 10 | 민감도 분석 (해당 시) | 권장 | "Sensitivity analyses were conducted excluding..." |

---

## 14. Statistical Notation Standards

### Reporting Format

| Statistic | Format | Example |
|-----------|--------|---------|
| Mean ± SD | X.X ± X.X | 54.3 ± 12.1 |
| Median [IQR] | X.X [X.X–X.X] | 52.0 [45.0–61.0] |
| Percentage | XX.X% | 45.2% |
| p-value | *p* = 0.XXX or *p* < 0.001 | *p* = 0.023 |
| 95% CI | (X.X to X.X) | (2.3 to 8.7) |
| Effect size | Cohen's d = X.XX | d = 0.85 |
| OR / RR / HR | X.XX (95% CI: X.XX to X.XX) | OR 2.35 (95% CI: 1.12 to 4.94) |
| NNT | NNT = X | NNT = 5 |

### p-value Reporting (NEJM 기준)

| p-value Range | Report As |
|--------------|-----------|
| > 0.01 | 소수점 2자리 (*p* = 0.24) |
| 0.001-0.01 | 소수점 3자리 (*p* = 0.003) |
| < 0.001 | *p* < 0.001 |

### Decimal Places

| Value Type | Decimal Places |
|------------|----------------|
| Age, BMI | 1 |
| Percentages | 1 |
| p-values | 2-3 (or <0.001) |
| Correlation coefficients | 2-3 |
| Odds/Risk/Hazard ratios | 2 |
| Cohen's d | 2 |
| NNT | 0 (정수) |

---

## 15. Python Analysis Templates

### 01_descriptive.py Template

```python
import pandas as pd
import numpy as np
from scipy import stats

def analyze_descriptive(df, group_var=None):
    """Generate descriptive statistics for Table 1"""
    results = []

    for col in df.select_dtypes(include=[np.number]).columns:
        # Normality test
        _, p_norm = stats.shapiro(df[col].dropna())
        is_normal = p_norm > 0.05

        if is_normal:
            # Mean ± SD
            summary = f"{df[col].mean():.1f} ± {df[col].std():.1f}"
        else:
            # Median [IQR]
            q25, q75 = df[col].quantile([0.25, 0.75])
            summary = f"{df[col].median():.1f} [{q25:.1f}–{q75:.1f}]"

        results.append({'Variable': col, 'Summary': summary})

    return pd.DataFrame(results)
```

### 02_comparative.py Template

```python
def compare_groups(df, outcome_var, group_var):
    """Compare outcomes between groups for Table 2"""
    groups = df[group_var].unique()
    g1 = df[df[group_var] == groups[0]][outcome_var]
    g2 = df[df[group_var] == groups[1]][outcome_var]

    # Normality check
    _, p1 = stats.shapiro(g1.dropna())
    _, p2 = stats.shapiro(g2.dropna())

    if p1 > 0.05 and p2 > 0.05:
        # t-test
        stat, p = stats.ttest_ind(g1, g2)
        test_used = "t-test"
    else:
        # Mann-Whitney
        stat, p = stats.mannwhitneyu(g1, g2)
        test_used = "Mann-Whitney U"

    # Effect size (Cohen's d)
    pooled_sd = np.sqrt((g1.std()**2 + g2.std()**2) / 2)
    cohens_d = (g1.mean() - g2.mean()) / pooled_sd if pooled_sd > 0 else 0

    # 95% CI for mean difference
    diff = g1.mean() - g2.mean()
    se = np.sqrt(g1.var()/len(g1) + g2.var()/len(g2))
    ci_lower = diff - 1.96 * se
    ci_upper = diff + 1.96 * se

    return {
        'outcome': outcome_var,
        'group1_mean': g1.mean(),
        'group1_sd': g1.std(),
        'group2_mean': g2.mean(),
        'group2_sd': g2.std(),
        'mean_diff': diff,
        'ci_95': f"({ci_lower:.1f} to {ci_upper:.1f})",
        'cohens_d': cohens_d,
        'p_value': p,
        'test': test_used
    }
```

---

## 16. Quality Checklist

### Before Analysis
| Item | Level | Done |
|------|-------|------|
| Data file integrity verified | 필수 | [ ] |
| Variable types correctly identified | 필수 | [ ] |
| Missing values documented | 필수 | [ ] |
| Outliers checked | 권장 | [ ] |
| Analysis plan reviewed (endpoints defined) | 필수 | [ ] |
| Primary/secondary/exploratory hierarchy defined | 필수 | [ ] |
| Sample size justification documented (prospective) | 필수 | [ ] |

### After Analysis
| Item | Level | Done |
|------|-------|------|
| All planned analyses completed | 필수 | [ ] |
| Results internally consistent | 필수 | [ ] |
| p-values correctly calculated | 필수 | [ ] |
| 95% CIs provided for primary outcomes | 필수 | [ ] |
| Effect sizes reported for primary outcomes | 권장 | [ ] |
| Sensitivity analyses performed (if applicable) | 권장 | [ ] |
| Multiple comparison correction applied (if applicable) | 필수 | [ ] |

### Table/Figure Review
| Item | Level | Done |
|------|-------|------|
| No redundancy between tables and figures | 필수 | [ ] |
| No redundancy between text and tables | 필수 | [ ] |
| Correct test indicated in footnotes | 필수 | [ ] |
| All abbreviations defined | 필수 | [ ] |
| Consistent decimal places | 필수 | [ ] |
| RCT Table 1: p-value 미사용 확인 | 필수 (RCT) | [ ] |
| Figure resolution ≥ 300 DPI | 필수 | [ ] |
| Supplementary materials appropriately used | 선택 | [ ] |

---

## 17. Common Errors to Avoid

| Error | Correction |
|-------|------------|
| Using t-test on non-normal data | Check normality first |
| Missing multiple comparison correction | Apply Bonferroni when needed |
| p-value without effect size | Report both (p-value + CI + effect size) |
| "Trending toward significance" | **Never use** - report exact p-value, state non-significant |
| Cherry-picking subgroups | Pre-specify all analyses, use interaction tests |
| Numbers in text AND table | Choose one location |
| RCT Table 1에 p-value | RCT는 p-value 불필요 (CONSORT) |
| Confusing statistical vs clinical significance | Report MCID comparison |
| Testing every variable without plan | Define endpoints hierarchy in advance |
| Post-hoc analysis without labeling | Must state "exploratory" |
| Equivalence claim from non-significant result | Non-significance ≠ equivalence |
| Within-group p-values for subgroup analysis | Use interaction test instead |
| Ignoring missing data | Document and explain handling method |

---

*Last updated: v0.3.0*
*Based on Dr. Statistician role from expert_roles.md*
*References: NEJM 2019 statistical guidelines, CONSORT 2010, SAMPL guidelines, ICMJE recommendations*

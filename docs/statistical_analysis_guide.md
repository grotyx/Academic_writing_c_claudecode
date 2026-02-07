# Statistical Analysis Guide (v0.2.1)

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

## 2. Table Structure Standards

### Standard Table Sequence

| Table # | Content | Purpose |
|---------|---------|---------|
| Table 1 | Baseline Characteristics | Demographics, clinical features at enrollment |
| Table 2 | Main Results | Primary & key secondary outcomes |
| Table 3+ | Additional Analyses | Subgroup, sensitivity, regression results |
| Suppl. Tables | Supporting Data | Detailed breakdowns, exploratory analyses |

### Table 1: Baseline Characteristics Template

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

---

## 3. Figure Guidelines

### Standard Figure Types

| Figure # | Common Content | Best Use Case |
|----------|----------------|---------------|
| Figure 1 | Patient Flow (CONSORT/STROBE) | Always required for clinical studies |
| Figure 2 | Primary Outcome Visualization | When visual comparison adds value |
| Figure 3 | Time-course / Survival | Longitudinal data, KM curves |
| Suppl. Figs | Secondary visualizations | Supporting data |

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
├── Forest plot (effect sizes)
└── Heat map (multiple correlations)
```

---

## 4. Redundancy Prevention Rules

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

## 6. Statistical Notation Standards

### Reporting Format

| Statistic | Format | Example |
|-----------|--------|---------|
| Mean ± SD | X.X ± X.X | 54.3 ± 12.1 |
| Median [IQR] | X.X [X.X–X.X] | 52.0 [45.0–61.0] |
| Percentage | XX.X% | 45.2% |
| p-value | *p* = 0.XXX or *p* < 0.001 | *p* = 0.023 |
| 95% CI | (X.X to X.X) | (2.3 to 8.7) |
| Effect size | Cohen's d = X.XX | d = 0.85 |

### Decimal Places

| Value Type | Decimal Places |
|------------|----------------|
| Age, BMI | 1 |
| Percentages | 1 |
| p-values | 3 (or <0.001) |
| Correlation coefficients | 2-3 |
| Odds/Risk ratios | 2 |

---

## 7. Python Analysis Templates

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

    return {
        'outcome': outcome_var,
        'group1_mean': g1.mean(),
        'group1_sd': g1.std(),
        'group2_mean': g2.mean(),
        'group2_sd': g2.std(),
        'p_value': p,
        'test': test_used
    }
```

---

## 8. Quality Checklist

### Before Analysis
| Item | Level | Done |
|------|-------|------|
| Data file integrity verified | 필수 | [ ] |
| Variable types correctly identified | 필수 | [ ] |
| Missing values documented | 필수 | [ ] |
| Outliers checked | 권장 | [ ] |
| Analysis plan reviewed | 필수 | [ ] |

### After Analysis
| Item | Level | Done |
|------|-------|------|
| All planned analyses completed | 필수 | [ ] |
| Results internally consistent | 필수 | [ ] |
| p-values correctly calculated | 필수 | [ ] |
| Effect sizes reported | 권장 | [ ] |
| 95% CIs provided for primary outcomes | 필수 | [ ] |

### Table/Figure Review
| Item | Level | Done |
|------|-------|------|
| No redundancy between tables and figures | 필수 | [ ] |
| No redundancy between text and tables | 필수 | [ ] |
| Correct test indicated in footnotes | 필수 | [ ] |
| All abbreviations defined | 필수 | [ ] |
| Consistent decimal places | 필수 | [ ] |
| Supplementary materials appropriately used | 선택 | [ ] |

---

## 9. Common Errors to Avoid

| Error | Correction |
|-------|------------|
| Using t-test on non-normal data | Check normality first |
| Missing multiple comparison correction | Apply Bonferroni when needed |
| p-value without effect size | Always report both |
| "Trending toward significance" | Avoid - it's not significant |
| Cherry-picking subgroups | Pre-specify all analyses |
| Numbers in text AND table | Choose one location |

---

*Last updated: v0.2.1*
*Based on Dr. Statistician role from expert_roles.md*

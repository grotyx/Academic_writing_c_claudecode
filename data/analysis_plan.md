# Statistical Analysis Guide

> 이 파일은 data/ 폴더의 CSV/XLSX 파일을 분석하여 자동 생성됩니다.
> `Analyze data` 명령으로 데이터에 맞게 업데이트됩니다.

---

## Data Overview

### Source File
- **File:** `[AUTO: filename.csv]`
- **Rows:** `[AUTO: n rows]`
- **Columns:** `[AUTO: n columns]`
- **Last Updated:** `[AUTO: date]`

### Variable Summary

| Variable | Type | Description | Missing (%) |
|----------|------|-------------|-------------|
| `[AUTO]` | Continuous/Categorical | `[AUTO]` | `[AUTO]` |

---

## Study Design

- **Design:** `[FROM claude.md: Study Design]`
- **Groups:** `[AUTO: detected groups or manual input]`
- **Primary Outcome:** `[MANUAL: specify]`
- **Secondary Outcomes:** `[MANUAL: specify]`

---

## Analysis Plan

### 1. Descriptive Statistics (→ table_1.md)

**Continuous Variables:**
- Report as: mean ± SD (normal) or median [IQR] (non-normal)
- Normality test: Shapiro-Wilk (n < 50) or Kolmogorov-Smirnov (n ≥ 50)

**Categorical Variables:**
- Report as: n (%)

**Script:** `data/py/01_descriptive.py`
**Output:** `results/table1_demographics.csv`

### 2. Comparative Analysis (→ table_2.md, table_3.md)

**Between-Group Comparisons:**

| Comparison | Variable Type | Distribution | Test |
|------------|---------------|--------------|------|
| 2 groups | Continuous | Normal | Independent t-test |
| 2 groups | Continuous | Non-normal | Mann-Whitney U |
| 2 groups | Categorical | - | Chi-square / Fisher's exact |
| >2 groups | Continuous | Normal | One-way ANOVA |
| >2 groups | Continuous | Non-normal | Kruskal-Wallis |
| Paired | Continuous | Normal | Paired t-test |
| Paired | Continuous | Non-normal | Wilcoxon signed-rank |

**Script:** `data/py/02_comparative.py`
**Output:** `results/table2_outcomes.csv`

### 3. Advanced Analysis (if applicable)

**Regression Analysis:**
- Linear regression: continuous outcome
- Logistic regression: binary outcome
- Cox regression: time-to-event outcome

**Script:** `data/py/03_regression.py`
**Output:** `results/table3_regression.csv`

---

## Statistical Thresholds

| Parameter | Value |
|-----------|-------|
| Significance level (α) | 0.05 |
| Confidence interval | 95% |
| Multiple comparison correction | Bonferroni (if >3 comparisons) |

---

## Output Files

### Tables (→ drafts/)
| Table | Content | Source |
|-------|---------|--------|
| table_1.md | Demographics & Baseline | results/table1_demographics.csv |
| table_2.md | Primary Outcomes | results/table2_outcomes.csv |
| table_3.md | Secondary Outcomes / Regression | results/table3_*.csv |

### Figures (→ drafts/figures/)
| Figure | Content | Type |
|--------|---------|------|
| fig_1.png | Patient flow (CONSORT) | Flowchart |
| fig_2.png | Primary outcome comparison | Bar/Box plot |
| fig_3.png | Kaplan-Meier (if applicable) | Survival curve |

---

## Python Environment

```python
# Required packages
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# For advanced analysis
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from sklearn.preprocessing import LabelEncoder
```

---

## Checklist Before Analysis

- [ ] Data file placed in data/ folder
- [ ] Variable names are clear and consistent
- [ ] Missing values identified and documented
- [ ] Outcome variables defined
- [ ] Group variable identified (if comparative study)
- [ ] Statistical plan reviewed by Dr. Statistician

---

## Notes

- All p-values reported to 3 decimal places (or <0.001)
- Effect sizes reported where applicable
- 95% CI provided for primary outcomes
- This guide updates automatically when data changes

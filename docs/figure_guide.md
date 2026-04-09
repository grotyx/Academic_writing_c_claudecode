# Figure Generation Guide (v0.3.0)

> 저널 제출용 고품질 Figure 생성을 위한 가이드

---

## 1. 해상도 및 파일 형식

### 저널 표준 요구사항

| 유형 | 최소 DPI | 권장 DPI |
|------|---------|---------|
| Line art (그래프, 다이어그램) | 600 | 1,000-1,200 |
| Halftone (사진, 영상) | 300 | 300-600 |
| Combination (선 + 사진) | 600 | 600 |

### 파일 형식

| 형식 | 용도 | 비고 |
|------|------|------|
| TIFF | 사진, 영상 이미지 | 무손실, 대부분 저널 선호 |
| PDF | 벡터 그래프 | 확대해도 품질 유지 |
| PNG | 웹/초안용 그래프 | 무손실, 파일 크기 작음 |
| SVG | 벡터 원본 보관 | 편집 가능, 저널 제출 전 변환 필요 |
| JPG | 사진 (최후 수단) | 손실 압축, 가능하면 TIFF 사용 |
| EPS | 일부 저널 요구 시 | 레거시 형식 |

### 크기

- 최종 출판 크기로 생성 (축소 시 폰트가 읽기 어려워짐)
- 1-column: 약 8.5 cm (3.3 in)
- 2-column (full width): 약 17.5 cm (6.9 in)

---

## 2. Python 설정 (matplotlib / seaborn)

### 기본 설정 템플릿

```python
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns

# --- 저널용 기본 설정 ---
def setup_journal_style():
    """저널 제출용 matplotlib 스타일 설정"""
    plt.rcParams.update({
        # 폰트
        'font.family': 'Arial',          # 대부분 저널 표준
        'font.size': 9,                   # 본문 폰트
        'axes.titlesize': 10,             # 제목
        'axes.labelsize': 9,              # 축 레이블
        'xtick.labelsize': 8,             # 눈금 레이블
        'ytick.labelsize': 8,
        'legend.fontsize': 8,             # 범례

        # 선 굵기
        'axes.linewidth': 0.8,            # 축 선
        'lines.linewidth': 1.2,           # 데이터 선
        'lines.markersize': 5,            # 마커 크기

        # 눈금
        'xtick.major.width': 0.8,
        'ytick.major.width': 0.8,
        'xtick.direction': 'out',
        'ytick.direction': 'out',

        # 레이아웃
        'figure.dpi': 300,                # 화면 표시용
        'savefig.dpi': 600,               # 저장 시 고해상도
        'savefig.bbox': 'tight',
        'savefig.pad_inches': 0.05,

        # 배경
        'figure.facecolor': 'white',
        'axes.facecolor': 'white',
        'savefig.facecolor': 'white',
    })

    # seaborn 스타일
    sns.set_theme(
        context='paper',
        style='ticks',
        palette='colorblind',     # 색맹 친화 팔레트
    )

setup_journal_style()
```

### 색맹 친화 팔레트

```python
# Okabe-Ito 팔레트 (색맹 친화, 가장 널리 권장)
OKABE_ITO = [
    '#E69F00',  # Orange
    '#56B4E9',  # Sky blue
    '#009E73',  # Bluish green
    '#F0E442',  # Yellow
    '#0072B2',  # Blue
    '#D55E00',  # Vermillion
    '#CC79A7',  # Reddish purple
    '#000000',  # Black
]

# 2-group 비교 시 권장
TWO_GROUP = ['#0072B2', '#D55E00']    # Blue vs Vermillion

# 3-group 비교
THREE_GROUP = ['#0072B2', '#D55E00', '#009E73']
```

### 저장 함수

```python
def save_figure(fig, filename, formats=None):
    """다중 형식으로 Figure 저장

    Args:
        fig: matplotlib figure 객체
        filename: 확장자 제외 파일명
        formats: 저장 형식 리스트 (기본: ['pdf', 'tiff'])
    """
    if formats is None:
        formats = ['pdf', 'tiff']

    for fmt in formats:
        dpi = 1200 if fmt == 'tiff' else 600
        fig.savefig(
            f'drafts/figures/{filename}.{fmt}',
            dpi=dpi,
            bbox_inches='tight',
            pad_inches=0.05,
            facecolor='white',
        )
    plt.close(fig)
```

---

## 3. Figure 유형별 가이드

### 연구 설계별 필수 Figure

| 연구 설계 | 필수 Figure | 선택 Figure |
|----------|------------|------------|
| RCT | CONSORT flow diagram | Kaplan-Meier, Forest plot |
| Cohort | Patient flow diagram | Kaplan-Meier |
| Case-control | Selection flow | Odds ratio forest plot |
| Meta-analysis | PRISMA flow, Forest plot | Funnel plot |
| Case series | Timeline | Before/after images |

### 각 Figure 유형 가이드

#### Box Plot (분포 비교)

```python
fig, ax = plt.subplots(figsize=(3.3, 3.0))
sns.boxplot(data=df, x='group', y='outcome', ax=ax,
            palette=TWO_GROUP, width=0.5, linewidth=0.8,
            flierprops={'markersize': 3})
# 개별 데이터 포인트 추가 (n<30일 때 권장)
sns.stripplot(data=df, x='group', y='outcome', ax=ax,
              color='black', size=2, alpha=0.5, jitter=True)
ax.set_ylabel('VAS Score')
ax.set_xlabel('')
sns.despine()
```

#### Kaplan-Meier 곡선 (생존 분석)

```python
from lifelines import KaplanMeierFitter

fig, ax = plt.subplots(figsize=(4.5, 3.5))
kmf = KaplanMeierFitter()
for i, (name, group) in enumerate(df.groupby('group')):
    kmf.fit(group['duration'], group['event'], label=name)
    kmf.plot_survival_function(ax=ax, color=TWO_GROUP[i],
                                linewidth=1.5)
ax.set_xlabel('Time (months)')
ax.set_ylabel('Survival Probability')
ax.set_ylim(0, 1.05)

# Number at risk 테이블 추가 권장
```

#### Forest Plot (효과 크기 비교)

```python
fig, ax = plt.subplots(figsize=(6.0, 4.0))
y_positions = range(len(studies))

for i, (study, or_val, ci_low, ci_high) in enumerate(data):
    ax.plot([ci_low, ci_high], [i, i], color='black', linewidth=0.8)
    ax.plot(or_val, i, 'D', color=OKABE_ITO[4], markersize=6)

ax.axvline(x=1.0, color='gray', linestyle='--', linewidth=0.5)
ax.set_yticks(y_positions)
ax.set_yticklabels([s[0] for s in data])
ax.set_xlabel('Odds Ratio (95% CI)')

# 스케일: OR/RR → log scale, Mean difference → linear scale
ax.set_xscale('log')
```

#### 시계열 변화 (Line Plot)

```python
fig, ax = plt.subplots(figsize=(4.5, 3.0))
timepoints = ['Baseline', '3mo', '6mo', '12mo']
for i, group in enumerate(groups):
    ax.errorbar(timepoints, means[i], yerr=sds[i],
                color=TWO_GROUP[i], marker='o', markersize=5,
                linewidth=1.2, capsize=3, label=group)
ax.set_ylabel('VAS Score')
ax.legend(frameon=False)
sns.despine()
```

---

## 4. Panel 레이블 규칙

| 항목 | 규칙 |
|------|------|
| 문자 | 대문자 사용: (A), (B), (C) — 일부 저널은 소문자 |
| 위치 | 각 패널 좌상단 |
| 폰트 | Bold, 본문보다 1-2pt 크게 |
| 참조 | Figure legend에서 "(A) ..., (B) ..." 형태로 설명 |

```python
# Multi-panel figure
fig, axes = plt.subplots(1, 2, figsize=(6.9, 3.0))

for i, (ax, label) in enumerate(zip(axes, ['A', 'B'])):
    ax.text(-0.15, 1.05, label, transform=ax.transAxes,
            fontsize=12, fontweight='bold', va='top')
    # ... 각 패널 내용 ...

fig.tight_layout()
```

---

## 5. 색상 전략

### 핵심 원칙

1. **흑백으로도 구분 가능해야 함** — 인쇄 시 흑백일 수 있음
2. **색상만으로 정보를 전달하지 않음** — 패턴, 선 스타일, 마커 형태 병용
3. **Red-Green 조합 금지** — 색맹(약 8% 남성)에게 구분 불가

### 확인 방법

```python
# 흑백 변환 테스트
fig.savefig('test_grayscale.png', dpi=150)
# → Preview에서 흑백으로 변환하여 확인

# 또는 matplotlib에서 직접 확인
from matplotlib.colors import rgb_to_hsv
# 밝기(V) 차이가 충분한지 확인
```

### 선 스타일 조합 (색상 + 형태)

```python
LINE_STYLES = [
    {'color': TWO_GROUP[0], 'linestyle': '-',  'marker': 'o'},  # Group A
    {'color': TWO_GROUP[1], 'linestyle': '--', 'marker': 's'},  # Group B
]
```

---

## 6. Figure vs Table 결정 기준

| 데이터 유형 | Figure | Table |
|------------|--------|-------|
| 시간에 따른 변화 추세 | ✅ Line plot | ❌ |
| 정확한 수치 필요 | ❌ | ✅ |
| 분포/산포도 | ✅ Box/Violin plot | ❌ |
| 그룹간 비교 (2-3개 변수) | ✅ Bar/Box | ❌ |
| 그룹간 비교 (많은 변수) | ❌ | ✅ |
| 상관관계 | ✅ Scatter plot | ❌ |
| 생존 분석 | ✅ Kaplan-Meier | ❌ |
| 메타 분석 결과 | ✅ Forest plot | ❌ (보조용만) |

> **중요:** 동일 데이터를 Table + Figure 모두에 넣지 않음 (중복 방지)

---

## 7. Figure Legend 작성

```markdown
Figure [N]. [독립적으로 이해 가능한 설명적 제목]
[상세 설명: 무엇을 보여주는지, 대상, 기간]
(A) [패널 A 설명]. (B) [패널 B 설명].
[화살표/기호 설명: Arrows indicate..., Asterisks denote...]
[통계 표기: *p < 0.05, **p < 0.01]
Abbreviations: [약어 정의]
```

---

## 체크리스트

### Figure 생성 시
- [ ] 최종 출판 크기로 생성했는가?
- [ ] 폰트가 7pt 이상인가?
- [ ] 색맹 친화 팔레트를 사용했는가?
- [ ] 흑백으로 변환해도 구분 가능한가?
- [ ] 축 레이블과 단위가 명확한가?
- [ ] 불필요한 장식 (3D, 그라데이션, 격자) 을 제거했는가?

### 저장 시
- [ ] Line art: 600+ DPI로 저장했는가?
- [ ] 사진: 300+ DPI로 저장했는가?
- [ ] TIFF 또는 PDF 형식인가?
- [ ] 파일명이 Figure_1, Figure_2 순서인가?

### 제출 전
- [ ] Figure legend가 독립적으로 이해 가능한가?
- [ ] 모든 약어가 legend에 정의되어 있는가?
- [ ] 본문에서 모든 Figure가 순서대로 언급되었는가?
- [ ] Table과 데이터가 중복되지 않는가?
- [ ] 저널의 Figure 개수 제한을 초과하지 않는가?

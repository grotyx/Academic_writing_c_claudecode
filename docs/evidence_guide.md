# Evidence 작성 가이드

> `knowledge/evidence.md` 작성 방법 및 문헌 관리 워크플로우

---

## 개요

`knowledge/evidence.md`는 논문 작성의 근거가 되는 참고문헌들을 **번호별로 정리·요약한 핵심 자료집**이다. 단순 목록이 아니라, 각 논문이 어떤 연구이고 어떤 결과를 보여주는지 파악할 수 있도록 충분히 요약한다.

### knowledge/ 폴더 구조

```
knowledge/
├── evidence.md              ← 전체 참고문헌 요약 정리 (핵심 자료집)
├── pdf/                     ← 원본 PDF 파일
│   └── author_year_keyword.pdf
└── summaries/               ← 개별 논문 full-text 상세 요약
    └── author_year_keyword.md
```

| 파일 | 성격 | 상세도 |
|------|------|--------|
| `pdf/` | 원본 그대로 | 원문 |
| `summaries/*.md` | 개별 논문 상세 요약 | Full-text 수준, 방법론·결과 상세 기술 |
| `evidence.md` | 전체 문헌 종합 정리 | 논문당 핵심 요약 + key points |

**흐름:** PDF (원본) → summaries (개별 상세) → evidence (종합 정리)

---

## 검색 워크플로우

### 새 논문 등록 절차

1. **중복 확인**: `evidence.md`에서 이미 등록된 논문인지 확인
2. **검색**: PubMed, Google Scholar 등으로 논문 검색
3. **검증**: 논문이 실재하는지, 내용이 정확한지 확인
4. **PDF 저장**: `knowledge/pdf/author_year_keyword.pdf`
5. **evidence.md 등록**: 아래 형식에 맞춰 요약 작성
6. **상세 요약** (선택): 핵심 논문은 `knowledge/summaries/`에 별도 상세 요약

### PDF 파일명 규칙

```
첫저자성_연도_키워드.pdf
```

예시:
- `kim_2020_acdf_arthroplasty.pdf`
- `park_2019_cervical_rom.pdf`
- `smith_2023_meta_analysis_fusion.pdf`

---

## Evidence Entry 작성법

### 기본 형식

```markdown
### [번호] 첫저자 et al., 연도
- **Citation:** 전체 서지정보 (저자, 제목, 저널, 연도, 권호, 페이지)
- **DOI:** 10.xxxx/xxxxx
- **PMID:** xxxxxxxx
- **PDF:** knowledge/pdf/파일명.pdf (또는 "No PDF - abstract only")

- **Study Design:** 연구 유형, 대상 수, 추적 기간
- **Objective:** 연구 목적 (1-2문장)
- **Population:** 대상군 특성 (연령, 진단, 포함/제외 기준 등)
- **Intervention/Method:** 주요 중재 또는 연구 방법
- **Main Findings:**
  - 주요 결과 1 (구체적 수치 포함)
  - 주요 결과 2
  - 주요 결과 3
- **Key Points:**
  - 이 논문에서 우리 연구에 중요한 포인트
  - 인용할 만한 핵심 주장이나 데이터
- **Limitations:** 저자가 언급한 한계점 또는 우리가 인지한 한계
- **Relevance:** 우리 논문 어디에 어떻게 활용할지
  - 예: Introduction (배경), Discussion (비교), Methods (참고)
```

### 작성 원칙

#### 1. Summary는 "읽고 바로 이해"할 수 있는 수준으로

**나쁜 예 (너무 짧음):**
```markdown
- **Main Findings:**
  - ACDF가 arthroplasty보다 재수술률 높음
```

**좋은 예 (충분한 정보):**
```markdown
- **Study Design:** RCT, n=200 (ACDF 100 vs Arthroplasty 100), 10년 추적
- **Objective:** 경추 단분절 질환에서 ACDF와 cervical arthroplasty의 장기 임상 성적 비교
- **Population:** 단분절 경추 추간판 탈출증, 18-65세, 6개월 이상 보존 치료 실패
- **Intervention/Method:**
  - ACDF: standalone cage + plate fixation
  - Arthroplasty: Prestige LP disc
  - 평가: NDI, VAS (neck/arm), ROM, 재수술률 (6개월, 1/2/5/10년)
- **Main Findings:**
  - 재수술률: ACDF 8.2% vs Arthroplasty 3.1% (p=0.02)
  - NDI 개선: 양 군 유의한 차이 없음 (p=0.45)
  - 수술 분절 ROM: Arthroplasty 평균 8.2° 유지, ACDF 0°
  - Adjacent segment disease: ACDF 12.0% vs Arthroplasty 5.5% (p=0.04)
  - 합병증: 양 군 유사 (ACDF 4% vs Arthroplasty 3%, p=0.71)
- **Key Points:**
  - 10년 장기 추적에서 arthroplasty의 재수술률 우위 확인
  - ASD 발생률 차이가 재수술률 차이의 주 원인
  - 5년까지는 차이 미미, 7년 이후 벌어지기 시작
- **Limitations:** 단일기관, 단분절만 포함, 탈락률 15%
- **Relevance:**
  - Discussion: 장기 성적 비교 시 핵심 인용
  - Introduction: ASD 문제 제기 근거
```

#### 2. 수치는 반드시 포함

통계값, p-value, 신뢰구간, 평균±SD 등 구체적 수치를 기록한다. 나중에 논문에서 인용할 때 다시 원문을 찾지 않아도 되도록.

#### 3. Key Points는 "우리 논문 관점"에서 작성

객관적 요약(Main Findings)과 별개로, Key Points는 **우리 연구와의 관련성** 중심으로 기록한다.

#### 4. Relevance는 구체적으로

단순히 "Discussion"이 아니라, 어떤 맥락에서 어떻게 활용할지 기록한다.

```markdown
# 나쁜 예
- **Relevance:** Discussion

# 좋은 예
- **Relevance:**
  - Discussion: 우리 연구의 재수술률 결과와 비교 (유사한 경향)
  - Introduction: 장기 추적 연구의 필요성 근거
```

---

## evidence.md vs summaries/ 구분

| 항목 | evidence.md | summaries/*.md |
|------|-------------|----------------|
| **범위** | 전체 참고문헌 | 개별 논문 1편 |
| **분량** | 논문당 15-25줄 | 논문당 1-3페이지 |
| **목적** | 빠른 참조, 전체 조망 | 상세 내용 확인 |
| **작성 대상** | 모든 참고문헌 | 핵심 논문만 (선택) |
| **내용** | 핵심 요약 + key points | Methods 상세, Results 전체, Figure/Table 요약 등 |

**summaries는 선택사항이다.** 모든 논문에 대해 작성할 필요 없고, 자주 인용하거나 방법론을 참고할 핵심 논문에 대해서만 작성한다.

---

## 번호 관리

- 번호는 등록 순서대로 부여: [1], [2], [3], ...
- 최종 manuscript의 reference 번호와 다를 수 있음 (최종 정렬은 Phase 6에서)
- 삭제된 논문의 번호는 재사용하지 않음 (혼동 방지)
- evidence.md 내에서 번호로 상호 참조 가능: "cf. [3]", "[1]과 상반된 결과"

---

## Search Log

evidence.md 하단에 검색 기록을 남겨 중복 검색을 방지한다.

```markdown
## Search Log

| Date | Query | Database | Results | Notes |
|------|-------|----------|---------|-------|
| 2025-01-15 | ACDF vs arthroplasty long-term | PubMed | 45건 | [1]-[5] 등록 |
| 2025-01-16 | cervical ROM preservation | PubMed | 23건 | [6]-[8] 등록 |
```

---

## Checklist: 좋은 Evidence Entry

- [ ] 번호가 순서대로 부여되었는가?
- [ ] Citation 정보가 완전한가? (저자, 제목, 저널, 연도, 권호, 페이지)
- [ ] DOI 또는 PMID가 기록되었는가?
- [ ] Study Design이 명확한가? (연구 유형, 대상 수, 추적 기간)
- [ ] Objective가 1-2문장으로 기술되었는가?
- [ ] Population 특성이 기록되었는가?
- [ ] Main Findings에 구체적 수치가 포함되었는가?
- [ ] Key Points가 우리 연구 관점에서 작성되었는가?
- [ ] Relevance에 활용 섹션과 맥락이 구체적으로 기술되었는가?
- [ ] PDF 파일명이 규칙에 맞게 저장되었는가?

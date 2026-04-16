# Academic Paper Writing Project (v0.5.2)

## Research Configuration
**Topic:** [INSERT YOUR SPECIFIC RESEARCH TOPIC]
**Target Journal:** [INSERT TARGET JOURNAL]
**Study Design:** [RCT / Cohort / Case-Control / Case Series / Meta-analysis / etc.]

> ⚠️ Update this section for each new paper project

---

## Project Structure

### Single Paper Project (기본)
```
project/
├── CLAUDE.md                     # This file - core rules & config
├── docs/                         # Reference guides (read when needed)
│   ├── writing_guide.md          # Section-by-section writing guide
│   ├── expert_roles.md           # Expert team roles & responsibilities
│   ├── checklist_guide.md        # Study-type specific checklists (STROBE, CONSORT, etc.)
│   ├── qc_guide.md               # Quality control & consistency verification
│   ├── statistical_analysis_guide.md  # Statistical analysis guide
│   ├── evidence_guide.md         # Evidence 작성 가이드
│   ├── revision_guide.md        # Revision & reviewer response guide
│   ├── figure_guide.md          # Figure generation guide
│   └── docx_guide.md            # DOCX 변환 가이드 (서식, 테이블, 네이밍)
├── knowledge/                    # Reference materials
│   ├── evidence.md               # 참고문헌 요약 정리 자료집
│   ├── pdf/                      # Original PDF files
│   │   └── author_year_keyword.pdf
│   └── summaries/                # MD summaries of key papers
│       └── author_year_keyword.md
├── data/                         # Statistical analysis
│   ├── raw_data.csv              # Original dataset (CSV/XLSX)
│   ├── analysis_plan.md          # Analysis plan (required before analysis)
│   └── py/                       # Python analysis scripts
│       ├── 01_descriptive.py
│       ├── 02_comparative.py
│       └── 03_regression.py
├── results/                      # Analysis outputs
│   ├── table1_demographics.csv
│   ├── table2_outcomes.csv
│   └── statistics_summary.csv
├── drafts/                       # Manuscript sections & tables
│   ├── draft_plan.md            # Draft plan (required before drafting)
│   ├── 00_cover_letter.md       # Cover letter template
│   ├── 01_title.md ~ 09_figure_legends.md  # Writing guide templates
│   ├── table_*.md               # Table templates
│   └── figures/                 # Generated figures
├── scripts/                      # Utility scripts
│   └── search_pubmed.py          # PubMed search tool (no external deps)
├── review/                       # Review & QC documents
│   └── qc_log.md                 # QC round tracking
└── output/                       # Final compiled manuscript
    ├── title_page_YYMMDD.docx
    ├── manuscript_YYMMDD.docx
    └── table_N_YYMMDD.docx
```

### Multi-Paper Project (하나의 데이터에서 여러 논문 작성 시)

> 동일 데이터셋에서 여러 논문을 작성할 때, 논문별 서브폴더로 정리

```
project/
├── CLAUDE.md
├── docs/                         # 공유 가이드 (모든 논문 공통)
├── knowledge/                    # 공유 참고문헌 (모든 논문 공통)
│   ├── evidence.md
│   ├── pdf/
│   └── summaries/
├── scripts/                      # 공유 스크립트
├── data/
│   ├── raw_data.csv              # 원본 데이터 (공유)
│   ├── paper1_xxx/               # 논문1 분석용 데이터
│   │   ├── analysis_plan.md
│   │   ├── filtered_data.csv     # 해당 논문에 맞게 필터링한 데이터
│   │   └── py/
│   └── paper2_yyy/               # 논문2 분석용 데이터
│       ├── analysis_plan.md
│       ├── filtered_data.csv
│       └── py/
├── results/
│   ├── paper1_xxx/               # 논문1 분석 결과
│   │   ├── table1_demographics.csv
│   │   └── table2_outcomes.csv
│   └── paper2_yyy/               # 논문2 분석 결과
│       ├── table1_demographics.csv
│       └── table2_outcomes.csv
├── drafts/
│   ├── paper1_xxx/               # 논문1 원고
│   │   ├── draft_plan.md         # 논문1 원고 구성 계획
│   │   ├── 01_title.md ~ 09_figure_legends.md
│   │   ├── table_*.md
│   │   └── figures/
│   └── paper2_yyy/               # 논문2 원고
│       ├── draft_plan.md         # 논문2 원고 구성 계획
│       ├── 01_title.md ~ 09_figure_legends.md
│       ├── table_*.md
│       └── figures/
├── review/
│   ├── paper1_xxx/
│   │   └── qc_log.md
│   └── paper2_yyy/
│       └── qc_log.md
└── output/
    ├── paper1_xxx/               # 논문1 최종 DOCX
    │   ├── manuscript_YYMMDD.docx
    │   └── table_N_YYMMDD.docx
    └── paper2_yyy/               # 논문2 최종 DOCX
        ├── manuscript_YYMMDD.docx
        └── table_N_YYMMDD.docx
```

**서브폴더 네이밍:** `paper{N}_{keyword}` (예: `paper1_infection`, `paper2_outcomes`)
- 저자가 선호하는 이름이 있으면 그에 따름
- keyword는 짧고 식별 가능한 단어로

### Revision 구조 (리뷰어 코멘트 수신 후)

> Revision 시에는 각 논문 폴더 내에 `revision/` 서브폴더를 만들어 정리

```
# Single paper인 경우
drafts/
├── 01_title.md ~ (원본 유지)
└── revision/
    ├── REV1/                     # 1차 revision
    │   ├── 01_title_REV1.md
    │   ├── 04_methods_REV1.md    # 수정된 섹션만
    │   ├── response_letter_REV1.md
    │   └── figures/
    └── REV2/                     # 2차 revision
        ├── 04_methods_REV2.md
        └── response_letter_REV2.md

review/
├── qc_log.md
├── reviewer_comments_REV1.md     # 리뷰어 코멘트 원문
└── reviewer_comments_REV2.md     # (필요 시)

output/
├── manuscript_YYMMDD.docx        # 원본 제출본
└── revision/
    ├── REV1/
    │   ├── manuscript_REV1_YYMMDD.docx
    │   ├── table_N_REV1_YYMMDD.docx
    │   └── response_letter_REV1_YYMMDD.docx
    └── REV2/
        ├── manuscript_REV2_YYMMDD.docx
        └── response_letter_REV2_YYMMDD.docx

# Multi-paper인 경우: 동일 구조가 각 paper 서브폴더 안에 적용
drafts/paper1_xxx/revision/REV1/
output/paper1_xxx/revision/REV1/
```

---

## File Roles

| File/Folder | Purpose | When to Use |
|-------------|---------|-------------|
| `CLAUDE.md` | Core rules, project config, writing style | Auto-loaded every session |
| `docs/writing_guide.md` | Detailed section guidelines | When drafting specific sections |
| `docs/expert_roles.md` | Expert team descriptions | When drafting or reviewing (Phase 4-5) |
| `docs/checklist_guide.md` | Study-type checklists (STROBE, CONSORT, PRISMA, CARE) | Phase 6 (QC) and before submission |
| `docs/qc_guide.md` | Consistency & accuracy verification procedures | Phase 6 (QC rounds) |
| `docs/statistical_analysis_guide.md` | Statistical methods, test selection, templates | Phase 2 (analysis) |
| `docs/evidence_guide.md` | Evidence 작성 가이드 (형식, 요약 방법, 워크플로우) | Phase 1 (setup) |
| `docs/revision_guide.md` | Reviewer response guide (응답서 작성, 외교적 표현) | Revision (리뷰어 코멘트 수신 후) |
| `docs/figure_guide.md` | Figure generation guide (DPI, 팔레트, Python 템플릿) | Phase 2 (figure 생성 시) |
| `docs/docx_guide.md` | DOCX 변환 가이드 (서식, 테이블 스타일, 네이밍 규칙) | Phase 7 (DOCX 변환 시 **반드시** 읽고 따를 것) |
| `knowledge/evidence.md` | 참고문헌 요약 정리 자료집 (논문별 요약·핵심·서지정보) | Phase 1 (setup) + 인용 시 참조 |
| `knowledge/pdf/` | Original reference PDFs | When verifying claims |
| `knowledge/summaries/` | 개별 논문 full-text 상세 요약 | 핵심 논문 상세 확인 시 |
| `data/` | Raw data (CSV/XLSX) | Phase 2 (statistical analysis) |
| `data/analysis_plan.md` | 분석 계획 (필수 작성·승인 후 분석 진행) | Phase 2 (before running analysis) |
| `data/py/` | Python analysis scripts | Phase 2 (statistical analysis) |
| `results/` | Analysis output CSV files | Phase 2 (after analysis) |
| `drafts/draft_plan.md` | 원고 구성 계획 (key message, table/figure plan, outline) | Phase 3 (drafting 전 필수) |
| `drafts/` | Individual section files, tables, figures | Phase 4-5 (drafting & polish) |
| `drafts/table_*.md` | Individual formatted tables | Phase 2 (from results CSV) |
| `drafts/figures/` | Generated figure files | Phase 2 (from analysis) |
| `scripts/search_pubmed.py` | PubMed 검색 스크립트 (NCBI E-utilities, 외부 패키지 불필요) | Phase 1 (reference search) |
| `review/qc_log.md` | QC round documentation | Phase 6 (track all QC iterations) |
| `output/` | Final compiled manuscript (docx only) | Phase 7 (finalize) |
| `review/reviewer_comments_REV{N}.md` | 리뷰어 코멘트 원문 | Phase 8 (revision) |
| `drafts/revision/REV{N}/` | Revision별 수정 원고 | Phase 8 (revision) |
| `output/revision/REV{N}/` | Revision별 최종 DOCX + response letter | Phase 8 (revision) |

---

## Critical Rules (MUST FOLLOW)

### 1. Citation Integrity

- **NEVER fabricate or hallucinate references**
- **ALWAYS check `knowledge/evidence.md` first** before searching (avoid duplicate work)
- **New reference workflow:** (상세: `docs/evidence_guide.md`)
  1. Search → verify paper exists
  2. Save PDF to `knowledge/pdf/author_year_keyword.pdf`
  3. Register in `knowledge/evidence.md` with summary & key points
  4. 핵심 논문은 `knowledge/summaries/`에 상세 요약 추가
  5. Then cite in manuscript

### 2. Redundancy Prevention

**Section Content Rules:**

| Section | Contains | Does NOT Contain |
|---------|----------|------------------|
| Introduction | Background, gap, rationale | Your results interpretation |
| Discussion | Your findings interpretation | Repeated background info |
| Results (text) | Narrative of findings | Exact numbers from tables |
| Tables | All numerical data | Narrative interpretation |

**Avoid Triple Duplication**
> 동일 데이터가 Results 본문 + Table + Figure 세 곳에 모두 나타나는 것은 지양

| Recommended | Avoid (지양) |
|-------------|--------------|
| Table only | Text에 상세 숫자 + Table에 같은 숫자 |
| Figure only | Table + Figure에 동일 데이터 |
| Table + brief text reference | Results 본문에 Figure 내용 상세 기술 |

**Results Text Writing:**
- ✅ "Baseline characteristics are shown in Table 1"
- ✅ "Group A showed significantly better outcomes (Table 2, *p*=0.023)"
- ❌ "Mean age was 54.3±12.1 years in Group A and 52.1±11.8 in Group B..."

**Table vs Figure Decision (물어보기):**
> "이 데이터는 Table로 할까요, Figure로 할까요?"
- 정확한 수치 필요 → Table
- 추세/분포 강조 → Figure
- 둘 다 만들지 않음 (중복)

**Standard Table Structure:**

| Table # | Content |
|---------|---------|
| Table 1 | Baseline Characteristics (demographics) |
| Table 2 | Main Results (primary + key secondary) |
| Table 3+ | Additional Analyses (subgroup, regression) |

> **Table 개수 가이드:** 가급적 5개 이하 권장. 꼭 필요하지 않은 세부 분석은 Supplement로 분리. 단, 논문 흐름상 필수적인 경우 5개 초과도 가능.

### 3. Consistency Requirements
These must match across **Abstract ↔ Methods ↔ Results ↔ Tables**:
- Patient/sample numbers
- Statistical values (p-values, CIs, means, SDs)
- Time periods and follow-up duration
- Outcome measure names and definitions

### 4. QC Process (MANDATORY)
- Run **minimum 3 QC rounds** before submission
- Follow `docs/qc_guide.md` for detailed procedures
- Document all checks in `review/qc_log.md`

### 5. File Versioning (파일 버전 관리)

> 최종본, revision, 대규모 변경 시 파일명에 버전을 표기해야 함

**기본 규칙:** 저자가 별도 스타일을 지정하지 않으면 **날짜(YYMMDD)** 를 기본으로 사용

**버전 표기 형식:**

| 형식 | 용도 | 예시 |
|------|------|------|
| `_YYMMDD` | 기본 (날짜 기반) | `manuscript_260414.docx` |
| `_v1`, `_v2` | 저자 요청 시 (순차 버전) | `manuscript_v1.docx` |
| `_REV1`, `_REV2` | Revision 제출본 | `manuscript_REV1_260414.docx` |
| `_FINAL` | 최종 제출본 | `manuscript_FINAL_260414.docx` |

**적용 시점:**
- **Phase 7 (Finalize):** 최초 제출본에 날짜 또는 버전 부여
- **Revision:** `_REV1`, `_REV2` 표기 필수 (+ 날짜 병기 권장)
- **대규모 변경:** 기존 파일 덮어쓰지 않고 새 버전으로 저장
- **Minor 수정:** 동일 파일명 유지 가능 (git으로 추적)

**파일명 패턴:**
```
{내용}_{버전}_{날짜}.{확장자}
```
- 예: `manuscript_REV1_260414.docx`, `table_1_v2.docx`, `response_letter_REV1_260414.docx`
- 저자가 원하는 스타일이 있으면 그에 따름 (저자 지시 우선)

### 6. Multi-Paper Organization (멀티 논문 정리)

> 하나의 데이터에서 여러 논문을 작성할 때 반드시 서브폴더로 분리

**규칙:**
- `data/`, `results/`, `drafts/`, `output/`, `review/` 각각에 논문별 서브폴더 생성
- `docs/`, `knowledge/`, `scripts/`는 공유 (서브폴더 불필요)
- 서브폴더명: `paper{N}_{keyword}` 또는 저자가 지정한 이름
- 원본 데이터는 `data/` 루트에, 논문별 필터링 데이터는 서브폴더에 배치

**Revision 시:**
- 각 논문 서브폴더 안에 `revision/REV1/`, `revision/REV2/` 생성
- 수정된 섹션만 revision 폴더에 저장 (변경 없는 파일은 복사하지 않음)
- Response letter도 해당 revision 폴더에 포함
- output도 동일하게 `output/{paper}/revision/REV1/` 구조

### 7. Analysis Plan Mandatory (분석 계획 필수)

> **통계 분석 전에 반드시 analysis_plan.md를 작성하고 확인받아야 한다**

**규칙:**

- **NEVER run statistical analysis without first creating `analysis_plan.md`**
- `Analyze data` 명령 시 반드시 analysis_plan.md를 먼저 생성
- 사용자가 analysis_plan.md를 확인한 후에만 스크립트 생성/실행 진행
- analysis_plan.md가 존재하지 않으면 분석 스크립트 생성을 거부

**논문별 개별 작성:**

- **Single paper:** `data/analysis_plan.md`
- **Multi-paper:** 각 논문 서브폴더에 개별 작성
  - `data/paper1_xxx/analysis_plan.md`
  - `data/paper2_yyy/analysis_plan.md`
- 같은 데이터라도 논문마다 연구 질문·대상·분석이 다르므로 **반드시 별도 작성**
- 공유 데이터(`data/raw_data.csv`)에 대한 공통 analysis_plan은 만들지 않음

**analysis_plan.md 필수 포함 내용:**

1. 연구 질문 및 가설
2. 대상 선정/제외 기준 (해당 논문에 맞게)
3. 변수 정의 (primary/secondary/exploratory endpoints)
4. 통계 검정법 선택 및 근거
5. 유의수준 및 다중비교 보정 계획

### 8. Draft Plan Mandatory (원고 구성 계획 필수)

> **원고 작성 전에 반드시 draft_plan.md를 작성하고 확인받아야 한다**

**규칙:**

- **NEVER start drafting sections without first creating `draft_plan.md`**
- 분석 결과(results/)를 확인한 후, 원고 작성 전에 전체 구성을 먼저 계획
- 사용자가 draft_plan.md를 확인한 후에만 섹션 작성 진행
- draft_plan.md가 존재하지 않으면 섹션 작성을 거부

**저장 위치:**

- **Single paper:** `drafts/draft_plan.md`
- **Multi-paper:** 각 논문 서브폴더에 개별 작성
  - `drafts/paper1_xxx/draft_plan.md`
  - `drafts/paper2_yyy/draft_plan.md`

**draft_plan.md 필수 포함 내용:**

1. **Key message** — 이 논문의 핵심 메시지 (1-2문장)
2. **Tone & voice** — 논문의 논조/어조 설정
   - 예: "conservative & evidence-based", "novel technique 강조", "기존 방법과 동등성 주장"
   - 전체 원고에서 일관되게 유지할 톤 명시
3. **Essential references** — 반드시 인용해야 할 핵심 참고문헌 목록
   - evidence.md에서 선별하거나, 추가 검색이 필요한 주제 명시
   - 각 reference의 인용 목적 기재 (배경, 방법론 근거, 비교 대상 등)
4. **Evidence gap** — 추가로 필요한 근거 자료 (아직 evidence.md에 없는 것)
   - 검색 키워드 또는 필요한 논문 유형 명시
5. **Table/Figure plan** — 몇 개, 각각 어떤 내용, Table vs Figure 결정
6. **Introduction outline** — Background → Gap → Purpose 흐름
7. **Discussion outline** — 주요 논점 3-5개, 비교할 선행연구 목록
8. **Limitation points** — 예상 한계점 및 대응 논리
9. **Target word count** — 저널 기준에 맞춘 섹션별 목표 분량 (선택)

### 9. Model Selection by Phase (단계별 모델 선택)

> **계획 단계는 high-quality 모델, 작성 단계는 mid-quality 모델도 가능**

**원칙:** Draft plan이 충분히 상세하면, 이후 작성은 plan을 따라가는 것이므로 비용 효율적 모델 사용 가능

| Phase                    | 권장 모델           | 대안 모델         | 이유                                       |
|--------------------------|---------------------|-------------------|--------------------------------------------|
| Phase 1: Setup           | Opus/Sonnet         | —                 | 검색·정리 작업                             |
| **Phase 2: Analysis**    | **Opus (권장)**     | Sonnet (가능)     | analysis_plan 작성은 Opus 권장             |
| **Phase 3: Draft Plan**  | **Opus (권장)**     | —                 | 논문의 방향·논조·구성을 결정하는 핵심 단계 |
| Phase 4: Draft           | Sonnet (기본)       | Opus (가능하면)   | draft_plan + evidence 기반 작성            |
| Phase 5: Style Polish    | Sonnet (기본)       | Opus (가능하면)   | 규칙 기반 작업                             |
| Phase 6: QC              | Sonnet (기본)       | Opus (가능하면)   | 체크리스트 기반 검증                       |
| Phase 7: Finalize        | Sonnet              | —                 | DOCX 변환·서식 작업                        |
| **Phase 8: Revision**    | **Opus (권장)**     | —                 | 리뷰어 대응은 전략적 판단 필요             |

**사용자 안내 (모델 선택 가이드):**

- **Opus 권장 단계:** Phase 2 (Analysis Plan), Phase 3 (Draft Plan), Phase 8 (Revision)
  - 전략적 판단·설계가 필요한 단계 → Opus로 방향을 잡아야 이후 작업 품질이 보장됨
  - Draft Plan 작성 시 Plan Mode(`/plan`) 활용을 권장하여 사용자와 충분한 논의 후 확정
- **Sonnet 기본, Opus 가능하면 사용:** Phase 4-6 (Draft, Polish, QC)
  - draft_plan.md + evidence.md가 잘 갖춰져 있으면 Sonnet으로도 충분
  - 비용 여유가 있으면 Opus 사용이 더 좋은 결과를 냄
- **핵심 원칙:** Plan은 Opus로 잘 잡고 → 작성은 Sonnet으로도 OK

---

## Natural Academic Writing Style

> 사람이 작성한 것처럼 자연스러운 학술 논문을 위한 작문 가이드

### 1. Transition Words (접속사/전환어)

| Avoid | Use Instead |
|-------|-------------|
| but | nonetheless, nevertheless, however |
| However (overused) | Nonetheless, Nevertheless |
| In contrast | Conversely |
| therefore | Thus, Accordingly |
| so | Hence, Therefore |

### 2. Verb Upgrades (동사 고급화)

| Basic | Academic |
|-------|----------|
| showed | demonstrated, exhibited, revealed |
| got | obtained, achieved, acquired |
| used | employed, utilized, applied |
| done | performed, conducted, executed |
| is | remains, represents, constitutes |
| has | possesses, exhibits, maintains |

### 3. Common Corrections (빈출 교정 패턴)

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

### 4. Voice by Section (섹션별 시제/태)

| Section | Voice | Example |
|---------|-------|---------|
| Methods | Passive | "Patients were randomized..." |
| Results | Passive (consistent) | "No significant differences were observed..." |
| Discussion | Mixed | Active for interpretation, passive for facts |

### 5. Statistical Notation (통계 표기)

| Item | Format | Example |
|------|--------|---------|
| p-value | lowercase italic *p* | *p* = 0.382, *p* < 0.05 |
| Percentage | no space | 83.3% |
| CI | "to" for range | 95% CI: -8.0% to +16.7% |
| Age range | en-dash | 19–80 years |

### 6. Writing Principles (작문 원칙)

**Clarity (명확성)**
- One idea per sentence
- Split long sentences
- Avoid ambiguous pronouns

**Conciseness (간결성)**
- Remove redundancy
- ❌ "first-grade students, fifth-grade students, and sixth-grade students"
- ✅ "first-, fifth-, and sixth-grade students"

**Objectivity (객관성)**
- ❌ "We believe that..."
- ✅ "The findings suggest that..."
- Avoid exaggeration — 과장 금지 표현 목록:
  - ❌ "dramatic improvement", "remarkable difference", "overwhelming evidence"
  - ❌ "most pronounced advantage", "four-fold reduction", "carries direct clinical significance"
  - ❌ "striking", "unprecedented", "groundbreaking"
  - ✅ "notable", "may be clinically relevant", "suggests a potential benefit"
- 결과 해석은 근거에 비례하는 수준으로 제한 — hedging 표현 활용: "may", "suggests", "appears to"

**Conciseness (간결성) — 강화**
- 불필요한 수식어·반복·장황한 서술 삭제
- 한 문장에 하나의 아이디어 — 길어지면 분리
- Discussion에서 Results 숫자/p-value 반복 금지 (Table에 이미 있음); 단, 선행연구 수치와 직접 비교 시 해당 수치 인용은 허용
- 유의하지 않은 p-value를 본문에 나열하지 않음 (Table 참조로 대체); 단, primary outcome의 n.s. 결과는 명시적으로 보고
- ❌ "first-grade students, fifth-grade students, and sixth-grade students"
- ✅ "first-, fifth-, and sixth-grade students"

**Consistency (일관성)**
- Same term for same concept throughout
- Uniform abbreviations and formatting
- 약어는 본문 최초 등장 시 1회만 정의, 이후 섹션에서 재정의하지 않음
- **동의어 혼용 금지 (Terminology Consistency):**
  - 같은 개념에 대해 동의어/유의어를 섞어 쓰지 않음 — 하나를 선택하면 전체 원고에서 일관되게 사용
  - 초안 작성 전 draft_plan.md 또는 첫 사용 시 어떤 용어를 쓸지 결정
  - 흔한 혼용 사례:
    - dural tear ↔ durotomy → 하나만 선택
    - complication ↔ adverse event → 맥락에 따라 선택 후 통일
    - postoperative ↔ after surgery → 하나만 선택
    - patient ↔ subject ↔ participant → 하나만 선택
    - recurrence ↔ relapse → 하나만 선택
  - 예외: Introduction에서 "durotomy (dural tear)"처럼 한 번 병기 후, 이후는 선택한 용어만 사용

### 7. Section-Specific Tips

**Introduction**
- Flow: Background → Problem → Gap → Purpose
- End with clear study objective

**Discussion**
- Start with main findings summary
- Structure limitations: "First, ... Second, ... Third, ..."
- Compare with existing literature objectively

**Conclusion**
- Restate findings concisely
- State clinical implications
- Avoid overstatement

---

## Recommended Workflow

```
Phase 1: Setup
├── Define topic, journal, study design in CLAUDE.md
├── Search references: /search-evidence [query] 또는 scripts/search_pubmed.py
├── Import by DOI: /import-doi [doi]
├── Save PDFs to knowledge/pdf/
├── Summarize & register in knowledge/evidence.md (docs/evidence_guide.md 참조)
├── 핵심 논문은 knowledge/summaries/에 상세 요약
└── Read docs/writing_guide.md for target sections

Phase 2: Statistical Analysis — Opus 권장 (analysis_plan)
├── Place raw data (CSV/XLSX) in data/
├── Create data/analysis_plan.md (필수, 사용자 승인 후 진행)
│   └── Claude reads CSV → creates analysis plan → 사용자 확인
├── Generate Python scripts in data/py/
│   ├── 01_descriptive.py (demographics, baseline)
│   ├── 02_comparative.py (group comparisons)
│   └── 03_regression.py (if needed)
├── Run analysis → export results to results/
│   └── table1_demographics.csv, table2_outcomes.csv, etc.
├── Generate drafts/table_*.md from results CSV
└── Generate figures → drafts/figures/

Phase 3: Draft Plan (원고 구성 계획) — Opus 권장
├── Create drafts/draft_plan.md
│   ├── Key message (이 논문의 핵심 메시지 1-2문장)
│   ├── Tone & voice (논조/어조 설정)
│   ├── Essential references (필수 인용 참고문헌 + 인용 목적)
│   ├── Evidence gap (추가 필요 근거 자료)
│   ├── Table/Figure plan (어떤 Table/Figure를 몇 개, 어떤 내용으로)
│   ├── Introduction outline (background → gap → purpose 흐름)
│   ├── Discussion outline (주요 논점 3-5개, 비교할 선행연구)
│   ├── Limitation points (예상 한계점)
│   └── Target word count (저널 기준, 선택)
├── 사용자 확인 후 Phase 4 진행
└── Multi-paper: drafts/paper{N}_xxx/draft_plan.md

Phase 4: Draft (in this order)
├── 04_methods.md      → establishes framework
│   └── Expert: Dr. Researcher B (methodology)
├── 05_results.md      → narrative (refer to drafts/table_*.md)
│   └── Expert: Dr. Researcher B
├── 03_introduction.md → background & gap
│   └── Expert: Dr. Researcher A (clinical)
├── 06_discussion.md   → interpretation (check vs intro)
│   └── Expert: Dr. Researcher A
├── 07_conclusion.md   → brief takeaway
├── 02_abstract.md     → summary (write LAST)
└── 01_title.md        → finalize

Phase 5: Style Polish
├── Apply "Natural Academic Writing Style" rules
│   ├── Upgrade transitions (but → nonetheless)
│   ├── Upgrade verbs (showed → demonstrated)
│   ├── Check voice by section
│   └── Verify statistical notation
└── Expert: Dr. Editor (final polish)

Phase 6: QC (minimum 3 rounds, 6 rounds recommended)
├── Round 1: Number consistency (qc_guide.md)
├── Round 2: Reference verification (qc_guide.md)
├── Round 3: Logic & flow check (qc_guide.md)
├── Round 4: Terminology, abbreviation & tense (권장)
├── Round 5: Statistical quality check (권장)
├── Round 6: Critical review — 비판적 검토 (권장)
├── Document in review/qc_log.md
└── Run study-specific checklist (checklist_guide.md)

Phase 7: Finalize
├── Read docs/docx_guide.md (DOCX 변환 규칙 확인)
├── Compile to DOCX (docs/docx_guide.md 규칙대로)
│   ├── output/title_page_YYMMDD.docx (별도)
│   ├── output/manuscript_YYMMDD.docx (본문 병합, 테이블 제외)
│   └── output/table_N_YYMMDD.docx (각 테이블 별도)
├── 파일명에 버전 표기 (기본: _YYMMDD, 저자 지정 시 _v1 등)
├── Co-author review
└── Final read-through

Phase 8: Revision (리뷰어 코멘트 수신 후)
├── Read docs/revision_guide.md
├── 리뷰어 코멘트 저장: review/reviewer_comments_REV1.md
├── Revision 폴더 생성: drafts/revision/REV1/, output/revision/REV1/
├── 수정된 섹션만 _REV1 접미사로 저장
├── Response letter 작성 → drafts/revision/REV1/response_letter_REV1.md
├── QC re-run (최소 Round 1-2 재수행)
├── Compile revised DOCX → output/revision/REV1/
│   ├── manuscript_REV1_YYMMDD.docx
│   ├── table_N_REV1_YYMMDD.docx (변경된 테이블만)
│   └── response_letter_REV1_YYMMDD.docx
└── 2차 revision 시: REV2/ 폴더에 동일 구조 반복
```

### Phase Completion Criteria

| Phase | Move to Next When |
|-------|-------------------|
| 1 → 2 | knowledge/evidence.md has ≥10 verified refs, topic defined, data ready |
| 2 → 3 | analysis_plan.md created & approved, all analyses complete, tables generated |
| 3 → 4 | draft_plan.md created & approved, key message·table/figure plan·outline 확정 |
| 4 → 5 | All sections drafted, numbers match tables |
| 5 → 6 | Writing style rules applied, Dr. Editor reviewed |
| 6 → 7 | Minimum 3 QC rounds passed (6 recommended), checklist complete |
| 7 → Submit | Co-author approved, journal requirements met, versioned files in output/ |
| Submit → 8 | Reviewer comments received |
| 8 → Resubmit | Revised manuscript + response letter complete, QC re-run passed |

---

## Quick Commands

### Setup & Research
| Command | Action |
|---------|--------|
| `Setup project for [topic]` | Initialize folder structure |
| `Process new PDFs` | Scan knowledge/pdf/, register unprocessed PDFs in evidence.md |
| `/search-evidence [query]` | PubMed 검색 → 선택 → evidence.md 등록 (slash command) |
| `/import-doi [doi]` | DOI로 논문 가져와서 evidence.md 등록 (slash command) |
| `Read writing guide for [section]` | Load section-specific guidance |

### Statistical Analysis
| Command | Action |
|---------|--------|
| `Analyze data` | Read CSV from data/, create analysis_plan.md (필수, 승인 후 진행) |
| `Generate analysis scripts` | Create Python scripts in data/py/ |
| `Run analysis` | Execute Python scripts, export to results/ |
| `Generate tables` | Create drafts/table_*.md from results CSV |
| `Generate figures` | Create figures in drafts/figures/ |
| `Summarize statistics` | Overview of all statistical results |

### Draft Plan

| Command              | Action                                      |
|----------------------|---------------------------------------------|
| `Create draft plan`  | Create drafts/draft_plan.md (Opus 권장)     |
| `Review draft plan`  | draft_plan.md 검토 및 수정 제안             |

### Drafting
| Command | Action |
|---------|--------|
| `Draft [section]` | Write specific section (draft_plan.md 기반) |
| `Draft [section] as Dr. [Expert]` | Write with specific expert perspective |
| `Review as Dr. [Expert]` | Get expert feedback on current draft |
| `Team review [section]` | All experts review section |

### Style & Polish
| Command | Action |
|---------|--------|
| `Apply writing style to [section]` | Apply Natural Academic Writing rules |
| `Check transitions` | Find weak transitions (but, however overuse) |
| `Upgrade verbs in [section]` | Replace basic verbs with academic alternatives |
| `Polish as Dr. Editor` | Final language refinement |

### QC & Verification
| Command | Action |
|---------|--------|
| `Run QC round [1-6]` | Execute specific QC round per qc_guide.md |
| `Check number consistency` | Cross-section number verification |
| `Verify references` | Check all citations against evidence.md |
| `Check logic flow` | Verify narrative consistency |
| `Run checklist for [study type]` | STROBE/CONSORT/PRISMA/CARE checklist |

### Revision (after reviewer comments)
| Command | Action |
|---------|--------|
| `Analyze reviewer comments` | Comment 분류 (Major/Minor) 및 대응 전략 제안 |
| `Draft response to reviewer [N]` | 특정 리뷰어 응답서 초안 작성 |
| `Draft response letter` | 전체 응답서 초안 작성 |
| `Review response letter` | Dr. Editor 관점에서 응답서 검토 |
| `Check response completeness` | 응답서 ↔ 원고 수정 일치 확인 |

### Figures
| Command | Action |
|---------|--------|
| `Generate figure for [data/analysis]` | Read figure_guide.md → Python figure 생성 |
| `Check figure quality` | DPI, 색맹 팔레트, 흑백 구분 확인 |

### Finalize
| Command | Action |
|---------|--------|
| `Compile manuscript` | Read `docs/docx_guide.md` → DOCX 변환 (규칙대로) |
| `Format references for [journal]` | Apply journal citation style |
| `Generate submission checklist` | Pre-submission verification |

---

## Notes

### Key Reminders
- Detailed guides in `docs/` folder - read as needed to save context
- Always verify AI-generated citations against actual sources
- Minimum 3 QC rounds mandatory before submission
- Human expert review mandatory before submission

### PubMed Search Tool

`scripts/search_pubmed.py` - NCBI E-utilities API 직접 호출 (MCP 불필요, 외부 패키지 불필요)

**CLI 직접 사용:**

```bash
python3 scripts/search_pubmed.py search "query"           # 검색 (테이블 출력)
python3 scripts/search_pubmed.py fetch <PMID> [PMID2...]  # PMID로 가져오기
python3 scripts/search_pubmed.py doi <DOI>                # DOI로 가져오기
python3 scripts/search_pubmed.py related <PMID>           # 관련 논문 검색
```

**옵션:**
- `--max N`: 최대 결과 수 (기본 20)
- `--sort relevance|pub_date`: 정렬 기준
- `--format table|evidence|json`: 출력 형식
- `--start-num N`: evidence 형식 시작 번호

**Slash command (Claude 대화 내):**

- `/search-evidence [query]`: 검색 → 선택 → abstract 기반 TODO 채우기 → evidence.md 등록
- `/import-doi [doi]`: DOI → evidence.md 등록

### Expert Simulation
When drafting, invoke experts from `docs/expert_roles.md`:
- **Dr. Researcher A**: Clinical perspective (Introduction, Discussion)
- **Dr. Researcher B**: Methodology (Methods, Results, Tables)
- **Dr. Statistician**: Statistical validation
- **Dr. Editor**: Final polish, consistency check

### Writing Style Priority
Apply "Natural Academic Writing Style" (above) during Phase 5:
1. Transitions: but → nonetheless
2. Verbs: showed → demonstrated
3. Corrections: elderly → older adult
4. Voice: section-appropriate (passive for Methods/Results)
5. Statistical notation: *p* < 0.05

### Statistical Analysis (Phase 2)

> 상세 가이드: `docs/statistical_analysis_guide.md` 참조

**Quick Workflow:**
1. CSV/XLSX → `data/` 폴더에 배치
2. `Analyze data` → analysis_plan.md 작성 (필수, 사용자 승인 후 진행)
3. `Generate analysis scripts` → data/py/ 스크립트 생성
4. `Run analysis` → results/ CSV 출력
5. `Generate tables` → drafts/table_*.md 생성
6. `Generate figures` → drafts/figures/ (필요시, Table과 중복 확인)

**Test Selection (Dr. Statistician):**

| Data Type | Normal | Non-normal |
|-----------|--------|------------|
| 2 groups, continuous | t-test | Mann-Whitney U |
| >2 groups, continuous | ANOVA | Kruskal-Wallis |
| Categorical | Chi-square | Fisher's exact |
| Paired | Paired t-test | Wilcoxon |

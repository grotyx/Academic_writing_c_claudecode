# Academic Paper Writing Project (v0.5.0)

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
│   ├── analysis_plan.md          # Auto-generated analysis plan
│   └── py/                       # Python analysis scripts
│       ├── 01_descriptive.py
│       ├── 02_comparative.py
│       └── 03_regression.py
├── results/                      # Analysis outputs
│   ├── table1_demographics.csv
│   ├── table2_outcomes.csv
│   └── statistics_summary.csv
├── drafts/                       # Manuscript sections & tables
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
│   │   ├── 01_title.md ~ 09_figure_legends.md
│   │   ├── table_*.md
│   │   └── figures/
│   └── paper2_yyy/               # 논문2 원고
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
| `docs/expert_roles.md` | Expert team descriptions | When drafting or reviewing (Phase 2-4) |
| `docs/checklist_guide.md` | Study-type checklists (STROBE, CONSORT, PRISMA, CARE) | Phase 5 (QC) and before submission |
| `docs/qc_guide.md` | Consistency & accuracy verification procedures | Phase 5 (QC rounds) |
| `docs/statistical_analysis_guide.md` | Statistical methods, test selection, templates | Phase 2 (analysis) |
| `docs/evidence_guide.md` | Evidence 작성 가이드 (형식, 요약 방법, 워크플로우) | Phase 1 (setup) |
| `docs/revision_guide.md` | Reviewer response guide (응답서 작성, 외교적 표현) | Revision (리뷰어 코멘트 수신 후) |
| `docs/figure_guide.md` | Figure generation guide (DPI, 팔레트, Python 템플릿) | Phase 2-3 (figure 생성 시) |
| `docs/docx_guide.md` | DOCX 변환 가이드 (서식, 테이블 스타일, 네이밍 규칙) | Phase 6 (DOCX 변환 시 **반드시** 읽고 따를 것) |
| `knowledge/evidence.md` | 참고문헌 요약 정리 자료집 (논문별 요약·핵심·서지정보) | Phase 1 (setup) + 인용 시 참조 |
| `knowledge/pdf/` | Original reference PDFs | When verifying claims |
| `knowledge/summaries/` | 개별 논문 full-text 상세 요약 | 핵심 논문 상세 확인 시 |
| `data/` | Raw data (CSV/XLSX) | Phase 2 (statistical analysis) |
| `data/analysis_plan.md` | Auto-generated analysis plan | Phase 2 (before running analysis) |
| `data/py/` | Python analysis scripts | Phase 2 (statistical analysis) |
| `results/` | Analysis output CSV files | Phase 2 (after analysis) |
| `drafts/` | Individual section files, tables, figures | Phase 3-4 (drafting & polish) |
| `drafts/table_*.md` | Individual formatted tables | Phase 3 (from results CSV) |
| `drafts/figures/` | Generated figure files | Phase 3 (from analysis) |
| `scripts/search_pubmed.py` | PubMed 검색 스크립트 (NCBI E-utilities, 외부 패키지 불필요) | Phase 1 (reference search) |
| `review/qc_log.md` | QC round documentation | Phase 5 (track all QC iterations) |
| `output/` | Final compiled manuscript (docx only) | Phase 6 (finalize) |
| `drafts/revision/REV{N}/` | Revision별 수정 원고 | Phase 7 (revision) |
| `output/revision/REV{N}/` | Revision별 최종 DOCX + response letter | Phase 7 (revision) |

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
- **Phase 6 (Finalize):** 최초 제출본에 날짜 또는 버전 부여
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
- Avoid exaggeration: "dramatic" → "significant"

**Consistency (일관성)**
- Same term for same concept throughout
- Uniform abbreviations and formatting

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

Phase 2: Statistical Analysis
├── Place raw data (CSV/XLSX) in data/
├── Auto-generate data/analysis_plan.md
│   └── Claude reads CSV → creates analysis plan
├── Generate Python scripts in data/py/
│   ├── 01_descriptive.py (demographics, baseline)
│   ├── 02_comparative.py (group comparisons)
│   └── 03_regression.py (if needed)
├── Run analysis → export results to results/
│   └── table1_demographics.csv, table2_outcomes.csv, etc.
├── Generate drafts/table_*.md from results CSV
└── Generate figures → drafts/figures/

Phase 3: Draft (in this order)
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

Phase 4: Style Polish
├── Apply "Natural Academic Writing Style" rules
│   ├── Upgrade transitions (but → nonetheless)
│   ├── Upgrade verbs (showed → demonstrated)
│   ├── Check voice by section
│   └── Verify statistical notation
└── Expert: Dr. Editor (final polish)

Phase 5: QC (minimum 3 rounds, 6 rounds recommended)
├── Round 1: Number consistency (qc_guide.md)
├── Round 2: Reference verification (qc_guide.md)
├── Round 3: Logic & flow check (qc_guide.md)
├── Round 4: Terminology, abbreviation & tense (권장)
├── Round 5: Statistical quality check (권장)
├── Round 6: Critical review — 비판적 검토 (권장)
├── Document in review/qc_log.md
└── Run study-specific checklist (checklist_guide.md)

Phase 6: Finalize
├── Read docs/docx_guide.md (DOCX 변환 규칙 확인)
├── Compile to DOCX (docs/docx_guide.md 규칙대로)
│   ├── output/title_page_YYMMDD.docx (별도)
│   ├── output/manuscript_YYMMDD.docx (본문 병합, 테이블 제외)
│   └── output/table_N_YYMMDD.docx (각 테이블 별도)
├── 파일명에 버전 표기 (기본: _YYMMDD, 저자 지정 시 _v1 등)
├── Co-author review
└── Final read-through

Phase 7: Revision (리뷰어 코멘트 수신 후)
├── Read docs/revision_guide.md
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
| 2 → 3 | analysis_plan.md created, all analyses complete, tables generated |
| 3 → 4 | All sections drafted, numbers match tables |
| 4 → 5 | Writing style rules applied, Dr. Editor reviewed |
| 5 → 6 | Minimum 3 QC rounds passed (6 recommended), checklist complete |
| 6 → Submit | Co-author approved, journal requirements met, versioned files in output/ |
| Submit → 7 | Reviewer comments received |
| 7 → Resubmit | Revised manuscript + response letter complete, QC re-run passed |

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
| `Analyze data` | Read CSV from data/, generate analysis_plan.md |
| `Generate analysis scripts` | Create Python scripts in data/py/ |
| `Run analysis` | Execute Python scripts, export to results/ |
| `Generate tables` | Create drafts/table_*.md from results CSV |
| `Generate figures` | Create figures in drafts/figures/ |
| `Summarize statistics` | Overview of all statistical results |

### Drafting
| Command | Action |
|---------|--------|
| `Draft [section]` | Write specific section |
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
Apply "Natural Academic Writing Style" (above) during Phase 4:
1. Transitions: but → nonetheless
2. Verbs: showed → demonstrated
3. Corrections: elderly → older adult
4. Voice: section-appropriate (passive for Methods/Results)
5. Statistical notation: *p* < 0.05

### Statistical Analysis (Phase 2)

> 상세 가이드: `docs/statistical_analysis_guide.md` 참조

**Quick Workflow:**
1. CSV/XLSX → `data/` 폴더에 배치
2. `Analyze data` → analysis_plan.md 자동 생성
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

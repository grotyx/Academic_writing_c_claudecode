# Academic Paper Writing Project (v1.6.3)

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
├── AGENTS.MD                     # Agent bootstrap rules; points to CLAUDE.md as source of truth
├── .gitattributes                # Line-ending policy (text=auto eol=lf; prevents CRLF churn from OneDrive/Windows sync)
├── docs/                         # Reference guides (read when needed)
│   ├── writing_guide.md          # Section-by-section writing guide
│   ├── drafting_protocol.md      # Mandatory drafting sequence
│   ├── section_templates.md      # Section-specific sentence patterns
│   ├── expert_roles.md           # Expert team roles & responsibilities
│   ├── checklist_guide.md        # Study-type specific checklists (STROBE, CONSORT, etc.)
│   ├── qc_guide.md               # Quality control & consistency verification
│   ├── verification_protocol.md  # 검증 게이트·4 Verifier·자율 루프·게이트 원장
│   ├── verifier_prompt_templates.md  # LLM semantic verifier prompts/output schema
│   ├── statistical_analysis_guide.md  # Statistical analysis guide
│   ├── evidence_guide.md         # Evidence 작성 가이드
│   ├── revision_guide.md        # Revision & reviewer response guide
│   ├── figure_guide.md          # Figure generation guide
│   ├── docx_guide.md            # DOCX 변환 가이드 (서식, 테이블, 네이밍)
│   ├── draft_plan_template.md    # Draft plan 10개 항목 템플릿 (Phase 3에서 복사)
│   ├── debate_protocol.md        # Claude–Codex co-author 토론 절차
│   ├── critical_review_protocol.md  # 외부 멀티모델 적대적 검토 절차
│   ├── style_transform_protocol.md  # /style-pass 변환 + Style Verifier
│   ├── style_spec_template.md    # Style Spec 템플릿 (exemplar 바인딩)
│   ├── citation_assist_protocol.md  # 출처 제안·claim 검증·stance·비교표 (GraphRAG)
│   └── medical_kag_protocol.md   # medical-kag MCP 통합 (KG; evidence.md 정본)
├── knowledge/                    # Reference materials
│   ├── evidence.md               # 참고문헌 요약 정리 자료집
│   ├── pdf/                      # Original PDF files
│   │   └── author_year_keyword.pdf
│   └── summaries/                # MD summaries of key papers
│       └── author_year_keyword.md
├── Style/                        # Writing-style anchors (separate from references)
│   ├── PDF/                      # Source PDFs for style analysis (gitignored)
│   │   ├── own/
│   │   ├── landmark/
│   │   └── target_journal/
│   ├── own/                      # Own-paper style extraction md
│   ├── landmark/                 # Argument/framing anchors
│   ├── target_journal/           # Journal house-style anchors
│   ├── style_guide.md            # Style anchor workflow and extraction rules
│   └── terminology.md            # Preferred/forbidden terminology registry
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
│   ├── lint_manuscript.py        # Manuscript terminology/style lint checks
│   ├── check_citations.py        # Evidence citation gate
│   ├── check_numbers.py          # Results CSV number gate
│   ├── check_gate.py             # Phase gate ledger check
│   ├── check_revision_claims.py  # Revision claim gate
│   ├── compile_response_docx.py  # Author response DOCX compiler
│   ├── search_pubmed.py          # PubMed search tool (no external deps)
│   ├── check_style.py            # Style Spec 대비 측정형 게이트 (문장길이·인용밀도)
│   ├── extract_claims.py         # 초안의 [EVID:id] 문장 추출 (claim 검증 입력)
│   ├── evidence_table.py         # 구조화 study 레코드 → markdown 비교표
│   ├── critical_review.py        # OpenRouter 멀티모델 적대적 검토 호출
│   ├── critical_models.txt       # OpenRouter 모델 목록 (외부화)
│   ├── critical_prompts/         # 적대적 검토 프롬프트 (manuscript.txt, response.txt, editor.txt)
│   ├── verify_all.py             # /verify — citation+number(+gate) 일괄 검증
│   ├── check_coverage.py         # 인용 coverage audit (과잉인용·미등록인용 주신호; 인용밀도; uncited는 중립)
│   ├── format_references.py       # [EVID:id]→저널형 서지목록 + 본문 태그 변환 (MCP 독립; Phase 7)
│   ├── check_abstract.py         # abstract↔본문 수치 일관성 (abstract-only 수치 차단; Phase 6, Rule 3)
│   ├── check_crossrefs.py        # Table/Figure 본문 참조 ↔ 실존 대조 (broken ref·미인용·순서; advisory)
│   ├── check_abbreviations.py    # 약어 첫 사용 정의 검사 (abstract/본문 scope 분리; advisory)
│   ├── check_response_coverage.py # 리뷰어 코멘트 전수 응답 확인 (Phase 8; ghost-revision 보완)
│   └── hooks/                    # 강제 훅 (enforce_gates, session_contract, lint_on_edit, style_intent)
├── tests/                        # pytest suite for the verification scripts
│   └── test_*.py                 # Run: pytest  (python-docx required, see requirements.txt)
├── .github/workflows/tests.yml   # CI: pytest on push to main + PRs (Python 3.10/3.11/3.12)
├── review/                       # Review & QC documents
│   ├── qc_log.md                 # QC round tracking
│   ├── gates/                    # 검증 게이트 원장 (phase_NN_*.GATE.md)
│   ├── debates/                  # Claude–Codex 토론 로그
│   └── critical/                 # 외부 멀티모델 적대적 검토 리포트
└── output/                       # Final compiled manuscript
    ├── title_page_YYMMDD.docx
    ├── manuscript_YYMMDD.docx
    └── table_N_YYMMDD.docx
```

### Multi-Paper Project (하나의 데이터에서 여러 논문 작성 시)

> 동일 데이터셋에서 여러 논문 작성 시 논문별 서브폴더로 정리 (상세 규칙: Rule 6).

기본(Single) 구조에서 **`data/`·`results/`·`drafts/`·`output/`·`review/` 각각에 `paper{N}_{keyword}/` 서브폴더**를 만들어 논문별로 분리한다. `docs/`·`knowledge/`·`scripts/`는 공유. 원본 데이터는 `data/` 루트, 논문별 필터링 데이터·`analysis_plan.md`·`draft_plan.md`는 각 서브폴더에 둔다.

**서브폴더 네이밍:** `paper{N}_{keyword}` (예: `paper1_infection`) — 저자 선호 이름 우선, keyword는 짧고 식별 가능하게.

### Revision 구조 (리뷰어 코멘트 수신 후)

> 각 논문 폴더 내 `revision/REV{N}/` 서브폴더로 정리 (상세 규칙: Rule 6).

- **`drafts/revision/REV{N}/`** — 수정된 섹션만 `_REV{N}` 접미사로 (예: `04_methods_REV1.md`) + `response_letter_REV{N}.md`
- **`review/`** — `reviewer_comments_REV{N}.md`, `gates/phase_08_revision.GATE.md`
- **`output/revision/REV{N}/`** — `manuscript_REV{N}_YYMMDD.docx`, 변경된 table, `response_letter_REV{N}_YYMMDD.docx`
- **Multi-paper:** 동일 구조가 각 `paper{N}_xxx/revision/REV{N}/`에 적용

---

## File Roles

| File/Folder | Purpose | When to Use |
|-------------|---------|-------------|
| `CLAUDE.md` | Core rules, project config, writing style | Auto-loaded every session |
| `.gitattributes` | Line-ending policy (`text=auto eol=lf`) — stores LF, normalizes on compare so OneDrive/Windows CRLF rewrites never produce content-free diffs | Git-managed (no manual edits needed) |
| `docs/writing_guide.md` | Detailed section guidelines | When drafting specific sections |
| `docs/drafting_protocol.md` | Mandatory outline → evidence-bound draft → style pass → QC workflow | Before drafting any section |
| `docs/section_templates.md` | Section-specific paragraph functions and sentence patterns | Phase 4 drafting |
| `docs/expert_roles.md` | Expert team descriptions | When drafting or reviewing (Phase 4-5) |
| `docs/checklist_guide.md` | Study-type checklists (STROBE, CONSORT, PRISMA, CARE) | Phase 6 (QC) and before submission |
| `docs/qc_guide.md` | Consistency & accuracy verification procedures | Phase 6 (QC rounds) |
| `docs/statistical_analysis_guide.md` | Statistical methods, test selection, templates | Phase 2 (analysis) |
| `docs/evidence_guide.md` | Evidence 작성 가이드 (형식, 요약 방법, 워크플로우) | Phase 1 (setup) |
| `docs/revision_guide.md` | Reviewer response guide (응답서 작성, 외교적 표현) | Revision (리뷰어 코멘트 수신 후) |
| `docs/verification_protocol.md` | 검증 게이트·4 Verifier 헌장·자율 루프·게이트 원장 정의 | Phase 3·4·6·8 (게이트 수행 시 **반드시** 참조) |
| `docs/verifier_prompt_templates.md` | LLM semantic verifier prompt와 구조화 출력 schema | Constraint/logic/semantic citation/revision alignment 검증 시 |
| `docs/response_letter_template.md` | Author_response 양식으로 DOCX 변환하기 쉬운 response letter Markdown 템플릿 | Revision 응답서 작성 시작 시 복사 |
| `docs/figure_guide.md` | Figure generation guide (DPI, 팔레트, Python 템플릿) | Phase 2 (figure 생성 시) |
| `docs/docx_guide.md` | DOCX 변환 가이드 (서식, 테이블 스타일, 네이밍 규칙) | Phase 7 (DOCX 변환 시 **반드시** 읽고 따를 것) |
| `docs/draft_plan_template.md` | Draft plan 10개 항목 템플릿 (Phase 3에서 복사하여 사용) | Phase 3 시작 시 복사 → `drafts/draft_plan.md` |
| `docs/debate_protocol.md` | Claude–Codex co-author 토론 절차 (라운드·역할·로그·폴백) | Phase 2·3·4·8 (`/paper-debate` 토론 시) |
| `docs/critical_review_protocol.md` | 외부 멀티모델 적대적 검토 절차 (리뷰어 풀·합의도·폴백) | Phase 6 QC·Phase 8 (`/critical-review`) |
| `profile/authors.md` | 저자 정보 (소속·연락처·ORCID·funding 문구 템플릿) | Title page 작성 시 **반드시** 참조 — 직접 입력 금지 |
| `profile/journals.md` | 저널별 인용 형식 (bracket vs superscript, et al. 기준, volume 형식) | 참고문헌 목록 작성 시 확인 |
| `knowledge/evidence.md` | 참고문헌 요약 정리 자료집 (논문별 요약·핵심·서지정보) | Phase 1 (setup) + 인용 시 참조 |
| `docs/medical_kag_protocol.md` | medical-kag MCP 통합 (KG 발굴·conflict·GRADE·레퍼런스 포맷); evidence.md 정본 유지 규율·fallback | Phase 1·3·4·6·7 (MCP 사용 시) |
| `knowledge/pdf/` | Original reference PDFs (**gitignored**; copyright-protected, local only) | When verifying claims |
| `knowledge/summaries/` | 개별 논문 full-text 상세 요약 | 핵심 논문 상세 확인 시 |
| `Style/` | 논문 스타일 앵커 전용 폴더. `own/`, `landmark/`, `target_journal/` md와 `PDF/` 원본을 분리 보관 | Phase 3-5 (저널 스타일, 팀 voice, 논증 구조 정렬) |
| `Style/terminology.md` | Preferred/forbidden terminology registry (definition, context, notes) | Phase 3-6 (drafting, polish, lint/QC) |
| `data/` | Raw data (CSV/XLSX) | Phase 2 (statistical analysis) |
| `data/analysis_plan.md` | 분석 계획 (필수 작성·승인 후 분석 진행) | Phase 2 (before running analysis) |
| `data/py/` | Python analysis scripts | Phase 2 (statistical analysis) |
| `results/` | Analysis output CSV files | Phase 2 (after analysis) |
| `drafts/draft_plan.md` | 원고 구성 계획 (key message, table/figure plan, outline) | Phase 3 (drafting 전 필수) |
| `drafts/` | Individual section files, tables, figures | Phase 4-5 (drafting & polish) |
| `drafts/table_*.md` | Individual formatted tables | Phase 2 (from results CSV) |
| `drafts/figures/` | Generated figure files | Phase 2 (from analysis) |
| `scripts/search_pubmed.py` | PubMed 검색 스크립트 (NCBI E-utilities, 외부 패키지 불필요) | Phase 1 (reference search) |
| `scripts/compile_response_docx.py` | `response_letter_REV*.md`를 Author_response 양식 DOCX로 변환 | Phase 8 response letter finalize |
| `scripts/check_revision_claims.py` | `response_letter_REV*.md`의 `[CHANGE]` claims를 revised manuscript 파일과 대조 | Phase 8 ghost-revision gate |
| `scripts/check_citations.py` | `[EVID:id]` citations를 `knowledge/evidence.md`와 대조 | Phase 3·4·6 citation gate |
| `scripts/check_coverage.py` | 인용 coverage audit — **과잉인용**(한 문장 과다 인용)·**미등록인용** 주신호, 섹션별 인용밀도; uncited ref/미실현 claim은 중립 정보(낭비 아님) | Phase 6 QC (`Check coverage`) |
| `scripts/format_references.py` | `[EVID:id]` → 저널형 서지목록(numbered/author-year) + 본문 태그 변환(`*_formatted.md`); **MCP 독립**, evidence.md 정본 | Phase 7 (`Format references`) |
| `scripts/check_abstract.py` | abstract↔본문 수치 일관성 — abstract에만 있고 본문에 없는 수치 차단 (Rule 3; p값 기본 제외) | Phase 6 QC Round 1 (`Check abstract`) |
| `scripts/check_crossrefs.py` | 본문 "Table/Figure N" 언급 ↔ `table_*.md`·figure legends 대조 — **broken ref**(없는 것 참조, 주신호)·미인용 항목·첫 언급 순서; advisory 기본, `--fail-on-broken` 등으로 게이트화 | Phase 6 QC (`Check crossrefs`) |
| `scripts/check_abbreviations.py` | 약어 첫 사용 정의 검사 — abstract↔본문 별도 scope (UNDEFINED/DEFINED_AFTER_USE/REDEFINED/SINGLE_USE); 오탐 전제 advisory, `--allow`·`--strict` | Phase 6 QC (`Check abbreviations`) |
| `scripts/check_response_coverage.py` | response letter의 Comment↔Response 전수 매핑 + 원본 코멘트 파일 대조 — 미응답·빈 응답·placeholder 검출 (ghost-revision 게이트의 반대면; 기본 fail) | Phase 8 (`Check response coverage`) |
| `scripts/check_numbers.py` | manuscript/table 수치를 `results/*.csv`와 대조 | Phase 4·6 data gate |
| `scripts/check_gate.py` | `review/gates/*.GATE.md` 원장의 `status: PASS`와 필수 check를 검증 | 모든 phase gate 통과 직전 |
| `scripts/check_style.py` | manuscript를 `drafts/style_spec.md` 목표와 대조 (측정형 스타일 게이트) | Phase 5·6 (`/style-pass`, `Check style`) |
| `scripts/extract_claims.py` | 초안의 `[EVID:id]` 문장 추출 (claim-verification 입력) | Phase 6 (`/verify-claims`) |
| `scripts/evidence_table.py` | 구조화 study 레코드 → markdown 비교표 (included studies) | Phase 6 (`/evidence-table`) |
| `docs/citation_assist_protocol.md` | 출처 제안 + claim 검증 + stance + 비교표 (GraphRAG 주, evidence.md 보조) | Phase 3·4·6 |
| `docs/style_transform_protocol.md` | 초안→bound 학술/저널 스타일 변환 + Style Verifier·자동발동 | Phase 5 (`/style-pass`) |
| `docs/style_spec_template.md` | Style Spec 템플릿 (exemplar 바인딩, 목표 metric) | Phase 5 (Style Spec 작성) |
| `review/qc_log.md` | QC round documentation | Phase 6 (track all QC iterations) |
| `review/gates/` | 검증 게이트 원장 (Verifier PASS/FAIL 기록) | Phase 3·4·8 (게이트 통과 기록) |
| `output/` | Final compiled manuscript (docx only) | Phase 7 (finalize) |
| `review/reviewer_comments_REV{N}.md` | 리뷰어 코멘트 원문 | Phase 8 (revision) |
| `drafts/revision/REV{N}/` | Revision별 수정 원고 | Phase 8 (revision) |
| `output/revision/REV{N}/` | Revision별 최종 DOCX + response letter | Phase 8 (revision) |

---

## Critical Rules (MUST FOLLOW)

### 1. Citation Integrity

- **NEVER fabricate or hallucinate references**
- **ALWAYS check `knowledge/evidence.md` first** before searching (avoid duplicate work)
- **medical-kag MCP is discovery/analysis only, not a citation source:** register anything it surfaces in `knowledge/evidence.md` as `[EVID:id]` (verify PMID/DOI) **before** citing. evidence.md stays the canonical ledger; fall back to `scripts/search_pubmed.py` if the MCP is unavailable. (`docs/medical_kag_protocol.md`)
- **Reference PDFs are local only:** store PDFs under `knowledge/pdf/`; do not commit copyrighted PDFs.
- **Style anchors are separate from references:** keep writing-style material under `Style/`, not `knowledge/`.
- **Style anchor mirror rule:** use matching basenames between PDF and md (e.g., `Style/PDF/landmark/weber_2007_sciatica.pdf` ↔ `Style/landmark/weber_2007_sciatica.md`).
- **Terminology enforcement:** use `Style/terminology.md` as the vocabulary registry. Preferred terms are required; forbidden terms must be replaced unless an exception is documented in `drafts/draft_plan.md`.
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
- **진행 추적(선택):** QC 라운드·게이트 항목을 TodoWrite로 추적해 가시성을 높일 수 있다. 단 이는 **세션용 보조 도구일 뿐 정본(authoritative record)이 아니다** — 영속 기록은 `review/qc_log.md`와 `review/gates/`가 담당한다.

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
- **Step 0 (Socratic 브레인스토밍):** 항목을 채우기 전, 사용자에게 **한 번에 하나씩** 질문해 의도를 정제한다 (`docs/draft_plan_template.md` 상단). 이 답변은 `/paper-debate`의 R0 준비자료로 쓰되 토론 자체와는 별개다.
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
10. **Claim→Citation mapping** — 핵심 주장 ~20개와 그 근거 논문 매핑 (쓰기 전에 확인 필수)
    - Introduction background: 5–8 claims (배경 지식의 근거)
    - Methods rationale: 2–3 claims (방법론 선택 근거)
    - Discussion comparisons: 5–8 claims (선행연구와의 비교 및 contextualisation)
    - 형식: `[Claim 요약] → Author Year (evidence.md 번호)`
    - **규칙:** claim을 작성하기 전에 citation을 먼저 확보할 것 — 없으면 Phase 1로 돌아가 검색

### 9. Verification Gates Mandatory (검증 게이트 필수)

> **각 산출 단계 뒤에 검증 게이트를 통과해야 다음으로 진행할 수 있다.**
> 상세: `docs/verification_protocol.md`

**규칙:**

- **NEVER proceed past a gate without a recorded PASS.** `review/gates/`의 해당 산출물 항목에 `status: PASS`가 없으면 다음 섹션/단계 진행을 거부한다.
- 검증은 **Verifier 서브에이전트**로 수행한다 (Draft: Constraint / Citation / Data / Logic 4종. Revision: Logic을 빼고 Revision-claims·Response-alignment를 더해 Constraint / Citation / Data / Revision-claims / Response-alignment). 외부지식 금지, 소스 오브 트루스(draft_plan·analysis_plan·evidence.md·results CSV)와만 대조.
- FAIL 시 **자율 수정 루프**: 지적사항을 고쳐 재검증. 최대 **2회(N=2)**, 이후 사용자에게 에스컬레이션.
- **Verifier 모델:** Opus 기본. Opus 불가 시 또는 사용자 요청 시 다른 모델(예: GPT-5.5) 허용.
- **인용 grounding:** 초안에서 모든 인용은 `[EVID:author_year]` 태그로 표기 (Phase 7에서 저널 형식 변환).
- **수치 grounding:** 원고 결과 수치는 `results/*.csv`에 존재하는 값만 사용.
- **Hook 강제 (결정적):** `.claude/settings.json`의 PreToolUse 훅(`Write/Edit/MultiEdit`)이 plan-first를 강제 — 완료·승인된 `draft_plan.md` 없이 섹션 작성, 완료·승인된 `analysis_plan.md` 없이 분석 스크립트 생성을 **차단**한다(Rule 7·8, fail-open). 미완성 템플릿/미체크 승인 plan은 plan으로 인정하지 않는다. SessionStart 훅이 본 계약(+활성 Style Spec)을 매 세션 주입. PostToolUse 훅(`lint_on_edit.py`)이 draft 편집마다 용어·표기 lint를 표면화하고, UserPromptSubmit 훅(`style_intent.py`)이 "학술적으로 바꿔줘" 류 입력에 style-pass protocol을 자동 주입한다. 결정적 검증은 `/verify`(`scripts/verify_all.py`)로 일괄 실행.

**게이트 배치·병렬·freshness:** Phase별 게이트(3 Claim→Citation 사전검증 · 4 섹션 게이트 · 6 경량 · 8 응답 게이트), 병렬 검출, freshness 해시 규칙은 `docs/verification_protocol.md` §7/§3.1/§6 참조. PASS 시 산출물 sha256를 `provenance:`에 기록하고, 산출물이 바뀌면 stale로 보고 재검증(`check_gate.py --verify-hash`). **결정적 차원(citation/numbers/revision_claims)은 `check_gate.py --cross-check`로 원장의 `PASS`를 정본 checker 즉석 재실행과 대조** — 안 돌리고 적은 가짜 PASS나 stale PASS를 모순으로 차단(소스 미도달 시 loud FAIL).

### 10. STOP Signals (자기기만 차단)

> Verifier가 잡는 것은 산출물의 결함이다. 이 표는 그 **앞단** — 사람·에이전트가 검증을 건너뛰려는 *합리화의 순간*을 차단한다. 아래 생각이 들면 멈추고(STOP) 오른쪽 행동을 한다.

| 머릿속 생각 (STOP) | 현실 / 해야 할 행동 |
|---|---|
| "이 숫자는 대충 맞을 거야" | `results/*.csv`와 대조. CSV에 없으면 쓰지 않는다. (`check_numbers.py`) |
| "이 인용 어디서 본 것 같은데" | `knowledge/evidence.md`에서 `[EVID:id]` 확인. 없으면 인용 금지. (`check_citations.py`) |
| "medical-kag가 찾았으니 바로 인용해도 돼" | 아니다. evidence.md에 `[EVID:id]`로 등록·PMID/DOI 확인 후에만 인용. (`docs/medical_kag_protocol.md`) |
| "한 번만 더 보면 통과겠지" | 게이트 먼저. `status: PASS` 없이는 다음 섹션 진행 금지. |
| "고친 김에 이 문장도 손봤어" | 검증 중 산출물 수정 금지. 판정을 모두 모은 뒤 한 번에, 그리고 전체 재검증. |
| "리뷰어 말이 맞지만 반박하고 싶다" | 근거 없는 반박 금지. 반박은 1-2개로 제한하고 문헌으로 뒷받침. |
| "이 정도면 novel하다고 써도 돼" | draft_plan의 tone·claim 범위 확인. 데이터가 지지하지 않는 주장 금지. |
| "Constraint는 나중에 봐도 돼" | 명세(scope/tone/forbidden) 위반은 1순위. 곧 폐기될 문장을 다듬지 않는다. |
| "PASS 받았으니 이제 안전해" | 산출물을 바꿨다면 그 PASS는 stale. `provenance` 해시로 재검증. |

### 11. Model Selection by Phase (단계별 모델 선택)

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
| **Verifier (모든 Phase)** | **Opus (기본)**    | GPT-5.5 등 (Opus 불가/요청 시) | 검증 품질이 하네스 신뢰성을 좌우          |

**사용자 안내 (모델 선택 가이드):**

- **Opus 권장 단계:** Phase 2 (Analysis Plan), Phase 3 (Draft Plan), Phase 8 (Revision)
  - 전략적 판단·설계가 필요한 단계 → Opus로 방향을 잡아야 이후 작업 품질이 보장됨
  - Draft Plan 작성 시 Plan Mode(`/plan`) 활용을 권장하여 사용자와 충분한 논의 후 확정
- **Sonnet 기본, Opus 가능하면 사용:** Phase 4-6 (Draft, Polish, QC)
  - draft_plan.md + evidence.md가 잘 갖춰져 있으면 Sonnet으로도 충분
  - 비용 여유가 있으면 Opus 사용이 더 좋은 결과를 냄
- **핵심 원칙:** Plan은 Opus로 잘 잡고 → 작성은 Sonnet으로도 OK

### 12. Documentation & Version Sync + Auto Commit-Push (문서·버전 동기화 + 자동 커밋·푸시)

> **harness(scripts/·hooks/·docs/) 코드·버그·기능 변경 시 항상: (1) 영향받는 문서 갱신 → (2) 버전 bump → (3) 자동 commit+push.** 매번 사용자에게 묻지 않는다.

**규칙:**

- **문서 동기화 (코드 ↔ 문서 동시 변경):** 동작·CLI 플래그·스크립트를 바꾸면 **같은 변경 안에서** 관련 문서를 갱신한다 — `CLAUDE.md`(명령 예시·규칙), `docs/`(해당 protocol), `review/gates/_TEMPLATE.GATE.md`, `AGENTS.MD`, `README.md`/`.ko`/`.ja`/`.zh`(기능 bullet + changelog). **문서 없는 코드 변경 금지.**
- **버전 bump (semver):**
  - **프로젝트 버전** = `CLAUDE.md` 헤더 + README 4종 헤더(`**vX.Y.Z**`). **cadence 느리게:** 개별 스크립트/플래그 추가·개선·문서·버그는 **patch**(1.5.3→1.5.4). minor는 **큰 마일스톤**(여러 기능 묶음, phase 단위 신규 역량, 워크플로 구조 변경)에만. 호환성 깨짐 = major. 작은 기능 하나마다 minor 올리지 말 것.
  - 변경된 **개별 doc**은 자체 헤더 semver도 올린다 (예: `verification_protocol.md` 0.2.0→0.3.0).
  - README 4종 Changelog에 `### vX.Y.Z (YYMMDD)` 항목 추가 (오늘 날짜).
- **자동 commit+push:** 변경이 **검증(테스트 green)되면** 사용자 확인 없이 commit + push 한다. 표준 커밋 메시지 형식 사용. protected 파일(`.gitignore`의 PDF/`profile/`/Style 앵커)은 자동 제외됨.
- **STOP — 자동 push 금지, 먼저 확인:** ① 비공개/민감 데이터가 staged될 위험, ② 대규모 파괴적 변경, ③ 사용자 manuscript 본문(`drafts/` WIP)이 함께 휩쓸릴 때, ④ history 재작성·force-push·revert(명시 요청 시에만). 이 경우 멈추고 사용자에게 확인한다.

---

## Natural Academic Writing Style

> **상세 가이드: `docs/writing_guide.md`**
> 규칙·표·예시는 writing_guide.md에 있음. CLAUDE.md는 워크플로·Phase 조정만 담당 (중복 방지).

**Phase 5 (Style Polish)에서 적용할 writing_guide.md 섹션:**

| 영역 | writing_guide.md 섹션 | 주요 내용 |
|------|----------------------|-----------|
| 전역 규칙 | General Principles | 시제, Bold 금지, 약어 1회 정의, 임상 결과 주어, 동의어 혼용 금지, 숫자 서식, 문두 숫자 |
| 스타일 표 | Style Reference Tables | Voice & Tense / Transition / Verb Upgrades / Common Corrections / Statistical Notation / Hedging |
| AI 군살빼기 | AI-Draft De-bloat | -ing 피상분석·AI어휘·신호어 제거; 충돌 패턴(hedging/copula/passive) 적용 제외 |
| 작문 원칙 | Writing Principles (4 Pillars) | Clarity / Conciseness / Objectivity / Consistency |
| 섹션별 규칙 | 01. Title ~ 10. Tables | 각 섹션 구조·구체 규칙·예시 |

**Phase 5 워크플로:**
1. `docs/writing_guide.md` Style Reference Tables 읽기
2. 섹션별로 Transition/Verb/Corrections 적용
3. AI 초안인 경우 AI-Draft De-bloat 적용 (-ing 피상분석·AI어휘·신호어 제거; 충돌 패턴 제외)
4. Writing Principles (4 Pillars) 기준으로 검토
5. Dr. Editor 최종 polish

---

## Recommended Workflow

```
Phase 1: Setup
├── Define topic, journal, study design in CLAUDE.md
├── Check profile/journals.md — 목표 저널 인용 형식 확인 (et al. 규칙, volume 형식 등)
├── Check Style/own/ — 관련 스타일 앵커 논문 확인 (용어·톤 일관성 참고)
├── Search references: /search-evidence [query] 또는 scripts/search_pubmed.py
├── (선택) medical-kag MCP: search/hybrid_search 발굴 + conflict find로 논쟁 파악 → evidence.md 등록 (docs/medical_kag_protocol.md; evidence.md 정본 유지, 미연결 시 search_pubmed.py로 fallback)
├── Import by DOI: /import-doi [doi]
├── Save PDFs to knowledge/pdf/
├── Summarize & register in knowledge/evidence.md (docs/evidence_guide.md 참조)
├── 핵심 논문은 knowledge/summaries/에 상세 요약
└── Read docs/writing_guide.md for target sections

Phase 2: Statistical Analysis — Opus 권장 (analysis_plan)
├── Read docs/statistical_analysis_guide.md (분석 설계 원칙·검정 선택·보정)
├── Place raw data (CSV/XLSX) in data/
├── (선택) /paper-debate — 분석 접근을 통계 담당 공동 저자(Codex)와 토론 후 plan 작성
├── Create data/analysis_plan.md (필수, 사용자 승인 후 진행)
│   ├── Claude reads CSV → creates analysis plan → 사용자 확인
│   └── 포함 항목: endpoint hierarchy, 검정법, 다중비교 보정, 결측 처리
├── Generate Python scripts in data/py/
│   ├── 01_descriptive.py (demographics, baseline)
│   ├── 02_comparative.py (group comparisons)
│   └── 03_regression.py (if needed)
├── Run analysis → export results to results/
│   └── table1_demographics.csv, table2_outcomes.csv, etc.
├── Generate drafts/table_*.md from results CSV
└── Generate figures → drafts/figures/

Phase 3: Draft Plan (원고 구성 계획) — Opus 권장
├── Step 0: Socratic 브레인스토밍 — 항목을 채우기 전 사용자에게 한 번에 하나씩 질문해 의도(key message) 정제 (draft_plan_template.md 상단; /paper-debate와 별개, R0 준비자료로 활용)
├── (선택) /paper-debate — key message·구조를 전략 담당 공동 저자(Codex)와 토론 후 plan 작성
├── Copy docs/draft_plan_template.md → drafts/draft_plan.md (또는 논문별 서브폴더)
│   ├── Key message (이 논문의 핵심 메시지 1-2문장)
│   ├── Tone & voice (논조/어조 설정)
│   ├── Essential references (필수 인용 참고문헌 + 인용 목적)
│   ├── Evidence gap (추가 필요 근거 자료)
│   ├── Claim→Citation mapping (핵심 주장 ~20개 + 각 근거 논문 — Style/own/ 참조 가능)
│   ├── Table/Figure plan (어떤 Table/Figure를 몇 개, 어떤 내용으로)
│   ├── Introduction outline (background → gap → purpose 흐름)
│   ├── Discussion outline (주요 논점 3-5개, 비교할 선행연구)
│   ├── Limitation points (예상 한계점)
│   └── Target word count (저널 기준, 선택)
├── 🔒 GATE: Claim→Citation 사전검증 (Citation Verifier) — 근거 없는 claim은 글쓰기 전 차단
├── 사용자 확인 후 Phase 4 진행
└── Multi-paper: drafts/paper{N}_xxx/draft_plan.md

Phase 4: Draft (in this order)
├── Read docs/drafting_protocol.md + docs/section_templates.md before drafting
├── Apply Style/terminology.md and relevant Style anchors during drafting
├── (선택) /paper-debate — 핵심 섹션 논증 골격을 논리 담당 공동 저자(Codex)와 토론 후 작성
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
├── 01_title.md        → finalize (profile/authors.md 참조하여 저자·소속·ORCID·funding 기입)
└── 🔒 GATE (각 섹션마다): Constraint + Citation + Data + Logic Verifier 자율 루프 (최대 2회) → review/gates/ 기록

Phase 5: Style Polish
├── /style-pass — 초안을 bound Style Spec/exemplar에 맞춰 섹션별 변환 + Style Verifier (docs/style_transform_protocol.md; "학술적으로 바꿔줘"에 자동 발동)
├── Apply writing_guide.md Style Reference Tables
│   ├── Transition Words 업그레이드 (but → nonetheless)
│   ├── Verb Upgrades (showed → demonstrated)
│   ├── Voice & Tense by Section 확인
│   ├── Common Corrections 적용
│   ├── Statistical Notation 검증 (*p* italic, en-dash 등)
│   └── Hedging Language 적정성 확인
├── Apply docs/section_templates.md sentence-pattern pass
├── Apply Style/terminology.md terminology pass
├── Run `py scripts/lint_manuscript.py drafts --quiet` on Windows and fix high-priority findings
├── Apply writing_guide.md Writing Principles (4 Pillars)
│   └── Clarity / Conciseness / Objectivity / Consistency
└── Expert: Dr. Editor (final polish)

Phase 6: QC (3 rounds CRITICAL, 6 rounds RECOMMENDED)
├── Round 1: Number consistency — Claude 자동 + 사용자 확인 (qc_guide.md)
├── Round 2: Reference verification — Claude + 사용자 (evidence.md 대조)
├── Round 3: Logic & flow check — Dr. Editor (section 간 흐름)
├── Round 4: Terminology/abbreviation/tense + style metrics — Dr. Editor + lint + check_style.py vs Style Spec (권장)
├── (권장) Check crossrefs / Check abbreviations — Table·Figure 참조 정합 + 약어 정의 advisory 점검
├── Round 5: Statistical quality — Dr. Statistician (권장)
├── Round 6: Critical review — 내부(Dr. Editor + Dr. Statistician) + (선택) /critical-review 외부 멀티모델 (overclaiming/bias/일반화, 권장)
├── Round 6.5 (선택): Editorial desk-screen — /editor-review: high-impact 저널 편집장 관점 (임상 타당성·분야 scope fit·추가검증 roadmap·하위저널 추천; advisory, `docs/critical_review_protocol.md` §5)
├── Claim verification (선택): /verify-claims — 인용 문장별 SUPPORTED/PARTIAL/UNSUPPORTED 리포트 (docs/citation_assist_protocol.md; GraphRAG 주, evidence.md 보조)
├── Document all rounds in review/qc_log.md
└── Run study-specific checklist (checklist_guide.md — CONSORT/STROBE/PRISMA/CARE)

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
├── (선택) /paper-debate — 대응 전략을 공동 저자(Codex)와 토론 후 response 작성
├── Response letter 작성 → drafts/revision/REV1/response_letter_REV1.md
├── 🔒 GATE (각 응답마다): ghost-revision 검증 (응답 주장 ↔ 원고 diff 대조) 자율 루프
├── Check response coverage — 모든 리뷰어 코멘트에 응답 존재 확인 (check_response_coverage.py --comments)
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
| 3 → 4 | draft_plan.md created & approved — 10개 필수 항목 완결 (key message, tone/voice, essential refs, evidence gap, claim→citation mapping, table/figure plan, intro/discussion outline, limitation points, target word count) — Rule 8 참조 |
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

### Knowledge Graph (medical-kag MCP)
> evidence.md 정본 유지 — 발굴/분석/포맷 보조. 미연결 시 search_pubmed.py로 fallback. 상세: `docs/medical_kag_protocol.md`

| Command | Action |
|---------|--------|
| `KAG search [topic]` | medical-kag `search`/`hybrid_search` 발굴 → evidence.md 등록 |
| `KAG conflicts [topic/intervention]` | `conflict` find/detect — 상충 연구·overclaim 점검 (Phase 6) |
| `KAG synthesize [intervention] [outcome]` | `conflict synthesize` — GRADE 근거 합성 (Discussion) |
| `KAG compare [interv1] [interv2]` | `compare_interventions` (Discussion 비교) |
| `KAG references [style/journal]` | `reference format_multiple` — 저널 스타일 참고문헌 목록 (Phase 7) |

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
| `Create draft plan`  | Copy docs/draft_plan_template.md → drafts/draft_plan.md, 10개 항목 작성 (Opus 권장) |
| `Review draft plan`  | draft_plan.md 검토 및 수정 제안             |

### Collaboration (Codex)
| Command | Action |
|---------|--------|
| `/paper-debate <주제>` | Claude–Codex co-author 토론 (작성 전, `docs/debate_protocol.md`) |
| `/critical-review <대상>` | 외부 멀티모델 적대적 reviewer 검토 (작성 후, `docs/critical_review_protocol.md`) |
| `/editor-review <대상>` | high-impact 저널 **편집장 desk-screen** — 임상 타당성·분야 scope fit·추가검증·하위저널 추천 (`docs/critical_review_protocol.md` §5) |

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
| `/style-pass [scope]` | 초안→bound 학술/저널 스타일 섹션별 변환 + Style Verifier (docs/style_transform_protocol.md; "학술적으로 바꿔줘"에 자동 발동) |
| `Apply writing style to [section]` | Apply Natural Academic Writing rules |
| `Check transitions` | Find weak transitions (but, however overuse) |
| `Upgrade verbs in [section]` | Replace basic verbs with academic alternatives |
| `Polish as Dr. Editor` | Final language refinement |

### QC & Verification
| Command | Action |
|---------|--------|
| `Run QC round [1-6]` | Execute specific QC round per qc_guide.md |
| `Check number consistency` | `py scripts\check_numbers.py drafts\05_results.md drafts\table_1.md --results results` 실행 |
| `Check abstract` | `py scripts\check_abstract.py drafts\04_methods.md drafts\05_results.md drafts\table_1.md drafts\table_2.md --abstract drafts\02_abstract.md` 실행 (abstract 수치가 본문에 다 있는지; Rule 3 일관성) |
| `Check style` | `py scripts\check_style.py check drafts\05_results.md --spec drafts\style_spec.md` 실행 (Style Spec 대비 측정형 게이트) |
| `Verify references` | `py scripts\check_citations.py drafts\03_introduction.md --evidence knowledge\evidence.md` 실행 |
| `Check coverage` | `py scripts\check_coverage.py drafts\03_introduction.md drafts\06_discussion.md --evidence knowledge\evidence.md --draft-plan drafts\draft_plan.md` 실행 (과잉인용·미등록인용·인용밀도 리포트; uncited는 중립. 기본 advisory, `--fail-on-over-citation`·`--fail-on-unknown`로 게이트화, `--max-citations-per-sentence N`로 임계 조정) |
| `Check phase gate` | `py scripts\check_gate.py review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts\05_results.md --cross-check citation=drafts\05_results.md --cross-check numbers=drafts\05_results.md --results results` 실행 (freshness + ledger↔live cross-check 포함) |
| `/verify [artifacts]` | `py scripts\verify_all.py drafts\05_results.md --results results --evidence knowledge\evidence.md --gate review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts\05_results.md --cross-check citation=drafts\05_results.md --cross-check numbers=drafts\05_results.md` — citation+number+gate freshness+cross-check 일괄 검증 |
| `/suggest-citation [claim]` | claim에 맞는 `[EVID:id]` 출처 제안 (medical-kag GraphRAG 주, evidence.md 보조; `docs/citation_assist_protocol.md`) |
| `/verify-claims [section]` | 인용 문장별 SUPPORTED/PARTIAL/UNSUPPORTED 리포트 → `review/claim_verification.md` (`extract_claims.py` + Semantic-Citation Verifier) |
| `/cite-stance [claim/section]` | 인용이 claim을 지지/반박/언급인지 분류 (Discussion 균형·overclaim 가드; `docs/citation_assist_protocol.md`) |
| `/evidence-table [topic/ids]` | 논문 비교표(included studies) 생성 (`scripts\evidence_table.py`; Discussion/PRISMA supplement) |
| `Check crossrefs` | `py scripts\check_crossrefs.py drafts\05_results.md drafts\06_discussion.md` 실행 (본문 Table/Figure 참조 ↔ 실존 대조 — broken ref·미인용·순서; advisory 기본, `--fail-on-broken`·`--fail-on-unreferenced`·`--fail-on-order`로 게이트화) |
| `Check abbreviations` | `py scripts\check_abbreviations.py drafts\02_abstract.md drafts\03_introduction.md drafts\04_methods.md drafts\05_results.md drafts\06_discussion.md` 실행 (약어 첫 사용 정의 — abstract/본문 scope 분리; advisory, `--allow ABB` 반복 지정·`--strict`) |
| `Check logic flow` | Verify narrative consistency |
| `Run checklist for [study type]` | STROBE/CONSORT/PRISMA/CARE checklist |

### Revision (after reviewer comments)
| Command | Action |
|---------|--------|
| `Analyze reviewer comments` | Comment 분류 (Major/Minor) 및 대응 전략 제안 |
| `Draft response to reviewer [N]` | 특정 리뷰어 응답서 초안 작성 |
| `Draft response letter` | 전체 응답서 초안 작성 |
| `Review response letter` | Dr. Editor 관점에서 응답서 검토 |
| `Check response completeness` | `py scripts\check_revision_claims.py drafts\revision\REV1\response_letter_REV1.md --strict` 실행 |
| `Check response coverage` | `py scripts\check_response_coverage.py drafts\revision\REV1\response_letter_REV1.md --comments review\reviewer_comments_REV1.md` 실행 (모든 리뷰어 코멘트에 실제 응답이 있는지 — 미응답·빈 응답·placeholder 차단) |
| `Compile response letter` | `py scripts\compile_response_docx.py drafts\revision\REV1\response_letter_REV1.md` 실행 |

### Figures
| Command | Action |
|---------|--------|
| `Generate figure for [data/analysis]` | Read figure_guide.md → Python figure 생성 |
| `Check figure quality` | DPI, 색맹 팔레트, 흑백 구분 확인 |

### Finalize
| Command | Action |
|---------|--------|
| `Compile manuscript` | Read `docs/docx_guide.md` → DOCX 변환 (규칙대로) |
| `Format references for [journal]` | `py scripts\format_references.py drafts\03_introduction.md drafts\06_discussion.md --evidence knowledge\evidence.md --style numbered --convert` 실행 → 서지목록 + `*_formatted.md` (저널 스타일은 profile/journals.md 참조; MCP 독립). medical-kag 연결 시 `KAG references`로 KG 기반 포맷도 가능 |
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
py scripts\search_pubmed.py search "query"           # 검색 (테이블 출력)
py scripts\search_pubmed.py fetch <PMID> [PMID2...]  # PMID로 가져오기
py scripts\search_pubmed.py doi <DOI>                # DOI로 가져오기
py scripts\search_pubmed.py related <PMID>           # 관련 논문 검색
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

### Statistical Analysis (Phase 2)

> 워크플로·검정 선택은 Recommended Workflow Phase 2 + `docs/statistical_analysis_guide.md`(§1 워크플로, §5 검정 선택) 참조. 핵심: 분석 전 `analysis_plan.md` 필수(Rule 7, hook 강제) → `data/py/` 스크립트 → `results/` CSV → table/figure (Table↔Figure 중복 확인).

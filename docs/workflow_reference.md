# Workflow Reference (v1.0.3)

Reference catalogs moved out of `WORKFLOW.md` (v1.7.5) so the always-loaded rules stay short. `WORKFLOW.md` remains authoritative for rules; this file is a lookup index. Commands use `python`; on Windows substitute `py` if needed.

## Project Structure

### Single Paper Project (기본)
```
project/
├── WORKFLOW.md                   # This file - shared core rules & config (Claude/Codex/Gemini)
├── CLAUDE.md                     # Claude Code bootstrap; imports this file via @WORKFLOW.md
├── AGENTS.md                     # Codex/agent bootstrap rules; points to WORKFLOW.md as source of truth
├── GEMINI.md                     # Gemini bootstrap; points to WORKFLOW.md
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
│   └── hooks/                    # 강제 훅 (enforce_gates, session_contract, lint_on_edit, style_intent) + run.sh 런처(py→python3 자동 선택)
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


## File Roles

| File/Folder | Purpose | When to Use |
|-------------|---------|-------------|
| `WORKFLOW.md` | Core rules, project config, writing style (shared by every runtime) | Auto-loaded in Claude Code via `@WORKFLOW.md` in `CLAUDE.md`; read first in Codex/Gemini |
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
| `profile/authors.md` | 저자 정보 (소속·연락처·ORCID·funding 문구 템플릿); gitignored — `profile/example_authors.md`를 복사해 작성 | Title page 작성 시 **반드시** 참조 — 직접 입력 금지 |
| `profile/journals.md` | 저널별 인용 형식 (bracket vs superscript, et al. 기준, volume 형식); gitignored — `profile/example_journals.md`를 복사해 작성 | 참고문헌 목록 작성 시 확인 |
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
| `scripts/format_references.py` | `[EVID:id]` → 저널형 서지목록(numbered/author-year, 또는 `--journal` 프리셋: NEJM·JAMA·Lancet·Spine·BJJ·JBJS 등 14종) + 본문 태그 변환(`*_formatted.md`, 인접 인용 묶음); `--fetch` 로 PubMed 전체 서지 캐시; **MCP 독립**, evidence.md 정본 | Phase 7 (`Format references`) |
| `scripts/journal_styles.py` | 저널 프리셋 정의(저자 수 컷오프·위첨자/대괄호·페이지·권호·DOI·정렬) | Phase 7 |
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


## Quick Commands

### Setup & Research
| Command | Action |
|---------|--------|
| `Setup project for [topic]` | Initialize folder structure |
| `Process new PDFs` | Scan knowledge/pdf/, register unprocessed PDFs in evidence.md |
| `/search-evidence [query]` | PubMed 검색 → 선택 → evidence.md 등록 (slash command) |
| `/import-doi [doi]` | DOI로 논문 가져와서 evidence.md 등록 (slash command) |
| `Read writing guide for [section]` | Load section-specific guidance |
| `manuwright rules [keyword]` | Print the workflow rules (or one section); ends with the guides that text cites |
| `manuwright check` | Health report after an update or setup: what is current, and the fix for each ✗ |
| `manuwright guide [name ...]` | Print engine guides cited as `docs/<name>.md` (a paper folder has no `docs/`); no name lists them |

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
| `Check number consistency` | `python scripts/check_numbers.py drafts/05_results.md drafts/table_1.md --results results` 실행 |
| `Check abstract` | `python scripts/check_abstract.py drafts/04_methods.md drafts/05_results.md drafts/table_1.md drafts/table_2.md --abstract drafts/02_abstract.md` 실행 (abstract 수치가 본문에 다 있는지; Rule 3 일관성) |
| `Check style` | `python scripts/check_style.py check drafts/05_results.md --spec drafts/style_spec.md` 실행 (Style Spec 대비 측정형 게이트) |
| `Verify references` | `python scripts/check_citations.py drafts/03_introduction.md --evidence knowledge/evidence.md` 실행 |
| `Check coverage` | `python scripts/check_coverage.py drafts/03_introduction.md drafts/06_discussion.md --evidence knowledge/evidence.md --draft-plan drafts/draft_plan.md` 실행 (과잉인용·미등록인용·인용밀도 리포트; uncited는 중립. 기본 advisory, `--fail-on-over-citation`·`--fail-on-unknown`로 게이트화, `--max-citations-per-sentence N`로 임계 조정) |
| `Check phase gate` | `python scripts/check_gate.py review/gates/phase_04_draft.GATE.md --artifact drafts/05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts/05_results.md --cross-check citation=drafts/05_results.md --cross-check numbers=drafts/05_results.md --results results` 실행 (freshness + ledger↔live cross-check 포함) |
| `/verify [artifacts]` | `python scripts/verify_all.py drafts/05_results.md --results results --evidence knowledge/evidence.md --gate review/gates/phase_04_draft.GATE.md --artifact drafts/05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts/05_results.md --cross-check citation=drafts/05_results.md --cross-check numbers=drafts/05_results.md` — citation+number+gate freshness+cross-check 일괄 검증 |
| `/suggest-citation [claim]` | claim에 맞는 `[EVID:id]` 출처 제안 (medical-kag GraphRAG 주, evidence.md 보조; `docs/citation_assist_protocol.md`) |
| `/verify-claims [section]` | 인용 문장별 SUPPORTED/PARTIAL/UNSUPPORTED 리포트 → `review/claim_verification.md` (`extract_claims.py` + Semantic-Citation Verifier) |
| `/cite-stance [claim/section]` | 인용이 claim을 지지/반박/언급인지 분류 (Discussion 균형·overclaim 가드; `docs/citation_assist_protocol.md`) |
| `/evidence-table [topic/ids]` | 논문 비교표(included studies) 생성 (`scripts/evidence_table.py`; Discussion/PRISMA supplement) |
| `Check crossrefs` | `python scripts/check_crossrefs.py drafts/05_results.md drafts/06_discussion.md` 실행 (본문 Table/Figure 참조 ↔ 실존 대조 — broken ref·미인용·순서; advisory 기본, `--fail-on-broken`·`--fail-on-unreferenced`·`--fail-on-order`로 게이트화) |
| `Check abbreviations` | `python scripts/check_abbreviations.py drafts/02_abstract.md drafts/03_introduction.md drafts/04_methods.md drafts/05_results.md drafts/06_discussion.md` 실행 (약어 첫 사용 정의 — abstract/본문 scope 분리; advisory, `--allow ABB` 반복 지정·`--strict`) |
| `Check logic flow` | Verify narrative consistency |
| `Run checklist for [study type]` | STROBE/CONSORT/PRISMA/CARE checklist |

### Revision (after reviewer comments)
| Command | Action |
|---------|--------|
| `Analyze reviewer comments` | Comment 분류 (Major/Minor) 및 대응 전략 제안 |
| `Draft response to reviewer [N]` | 특정 리뷰어 응답서 초안 작성 |
| `Draft response letter` | 전체 응답서 초안 작성 |
| `Review response letter` | Dr. Editor 관점에서 응답서 검토 |
| `Check response completeness` | `python scripts/check_revision_claims.py drafts/revision/REV1/response_letter_REV1.md --strict` 실행 |
| `Check response coverage` | `python scripts/check_response_coverage.py drafts/revision/REV1/response_letter_REV1.md --comments review/reviewer_comments_REV1.md` 실행 (모든 리뷰어 코멘트에 실제 응답이 있는지 — 미응답·빈 응답·placeholder 차단) |
| `Compile response letter` | `python scripts/compile_response_docx.py drafts/revision/REV1/response_letter_REV1.md` 실행 |

### Figures
| Command | Action |
|---------|--------|
| `Generate figure for [data/analysis]` | Read figure_guide.md → Python figure 생성 |
| `Check figure quality` | DPI, 색맹 팔레트, 흑백 구분 확인 |

### Finalize
| Command | Action |
|---------|--------|
| `Compile manuscript` | Read `docs/docx_guide.md` → DOCX 변환 (규칙대로) |
| `Format references for [journal]` | `python scripts/format_references.py drafts/03_introduction.md drafts/06_discussion.md --evidence knowledge/evidence.md --journal <preset> --fetch --convert` 실행 → 해당 저널 형식 서지목록 + `*_formatted.md` (프리셋 목록: `docs/harness_guide.md`; `project.json` 에 `"journal"` 을 넣으면 build 도 같은 형식; MCP 독립). medical-kag 연결 시 `KAG references`로 KG 기반 포맷도 가능 |
| `Generate submission checklist` | Pre-submission verification |


## Tools

#### PubMed Search Tool

`scripts/search_pubmed.py` - NCBI E-utilities API 직접 호출 (MCP 불필요, 외부 패키지 불필요)

**CLI 직접 사용:**

```bash
python scripts/search_pubmed.py search "query"           # 검색 (테이블 출력)
python scripts/search_pubmed.py fetch <PMID> [PMID2...]  # PMID로 가져오기
python scripts/search_pubmed.py doi <DOI>                # DOI로 가져오기
python scripts/search_pubmed.py related <PMID>           # 관련 논문 검색
```

**옵션:**
- `--max N`: 최대 결과 수 (기본 20)
- `--sort relevance|pub_date`: 정렬 기준
- `--format table|evidence|json`: 출력 형식
- `--start-num N`: evidence 형식 시작 번호

**Slash command (Claude 대화 내):**

- `/search-evidence [query]`: 검색 → 선택 → abstract 기반 TODO 채우기 → evidence.md 등록
- `/import-doi [doi]`: DOI → evidence.md 등록

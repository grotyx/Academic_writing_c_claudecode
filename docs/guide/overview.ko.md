# 전체 안내 (README 에서 옮김)

## 개요

이 프로젝트는 Claude AI의 도움을 받아 의학 학술 논문을 작성하기 위한 종합 프레임워크를 제공합니다:

- **체계적인 프로젝트 구조** — 원고, 데이터, 참고문헌 관리
- **멀티 논문 프로젝트 지원** — 논문별 서브폴더 정리
- **파일 버전 관리 시스템** — 날짜 기본, _v1, _REV1 스타일
- **Revision 워크플로우** — 전용 revision 폴더 및 파일 네이밍
- **전문가 팀 시뮬레이션** — 임상 전문가, 방법론 전문가, 통계학자, 편집자
- **통계 분석 워크플로우** — Python 스크립트 자동 생성
- **품질 관리 절차** — 최소 3라운드 검증 (6라운드 권장) + Revision QC 재수행 워크플로
- **연구 유형별 체크리스트** — STROBE, CONSORT, PRISMA, CARE 등
- **학술 작문 스타일 시스템** — Style Reference Tables (Voice/Tense, Transition, Verb Choice, Common Corrections, Statistical Notation, Hedging) + Writing Principles (Clarity/Conciseness/Objectivity/Consistency)
- **안정적인 스타일 변환** (`/style-pass`) — 거친 초안을 bound 저널 스타일로 변환: 프로젝트별 Style Spec(선택한 exemplar 1개) + 섹션별 변환 + 독립적인 Style-Conformance verifier(자동 수정 루프) + 측정 가능한 `scripts/check_style.py` 게이트(문장 길이, 인용 밀도, hedging) + "make it academic" 의도에 대한 자동 트리거 (`docs/style_transform_protocol.md`)
- **인용 품질 관리** — Claim→Citation Mapping (작성 전 핵심 주장 ~20개와 근거 논문 매핑; write-first, cite-later 방지)
- **스타일 앵커 라이브러리** (`Style/`) — own, landmark, target-journal 앵커로 용어·톤·논증·저널 house style 확보
- **분야 표준 용어 registry** (`Style/terminology.md`) — preferred/forbidden 용어, 정의, context
- **Drafting protocol** (`docs/drafting_protocol.md`) — outline → evidence-bound draft → style pass → QC 강제
- **Manuscript linting** (`scripts/lint_manuscript.py`) — 용어, placeholder, 과장 표현, 섹션별 위반 자동 점검
- **Citation evidence checking** (`scripts/check_citations.py`) — `[EVID:id]` 태그를 `knowledge/evidence.md`와 대조
- **Data number checking** (`scripts/check_numbers.py`) — 원고/표의 숫자를 `results/*.csv`와 대조
- **Phase gate ledger checking** (`scripts/check_gate.py`) — `review/gates/*.GATE.md`에 필수 PASS가 없으면 진행 차단
- **Gate freshness / provenance** (`scripts/check_gate.py --verify-hash`) — PASS 시 검증된 산출물(및 evidence/results)의 sha256을 기록; 이후 편집이 발생하면 게이트가 **stale** 상태가 되어 재검증을 강제하므로, 병렬 verifier의 허점을 차단
- **Gate cross-check** (`scripts/check_gate.py --cross-check`) — 결정적 차원(`citation` / `numbers` / `revision_claims`)에 대해 정본 checker를 즉석 재실행하고, 원장의 기록 상태가 실제와 불일치하면 게이트를 FAIL — 안 돌리고 적은 가짜 PASS나 stale PASS를 차단 (소스 미도달 시 loud FAIL)
- **Revision claim checking** (`scripts/check_revision_claims.py`) — response letter의 `[CHANGE]` claim을 revised manuscript와 대조
- **LLM verifier prompt templates** (`docs/verifier_prompt_templates.md`) — constraint, semantic citation, data, logic/redundancy, style-conformance, citation-stance, revision-alignment 검증 prompt/schema
- **인용 보조** — `/suggest-citation`(claim에 가장 적합한 `[EVID:id]` 탐색), `/verify-claims`(`scripts/extract_claims.py`를 통한 문장별 SUPPORTED/PARTIAL/UNSUPPORTED claim 맵), `/cite-stance`(supporting/contrasting/mentioning, Scite 스타일), `/evidence-table`(`scripts/evidence_table.py`를 통한 "포함된 연구 요약" 표, Elicit 스타일) (`docs/citation_assist_protocol.md`)
- **Knowledge graph 통합** (선택) — medical-kag MCP(GraphRAG)를 상류(upstream)의 discovery / conflict / GRADE 종합 / reference 엔진으로 활용하되, `knowledge/evidence.md`를 정본으로 유지하고 `scripts/search_pubmed.py`를 폴백으로 사용 (`docs/medical_kag_protocol.md`)
- **프로세스 강제 hook** (`scripts/hooks/`) — SessionStart 계약 주입, PreToolUse plan-first 게이트, PostToolUse style/terminology lint, UserPromptSubmit style 자동 트리거
- **일괄 검증** (`/verify`, `scripts/verify_all.py`) — citation + number + gate check를 함께 실행
- **Author response DOCX generation** (`scripts/compile_response_docx.py`) — DOCX-ready Markdown을 `Author_response_220803_Final.docx` house style에 맞춰 변환
- **Author response Markdown template** (`docs/response_letter_template.md`) — reviewer response, 수정 위치, machine-readable `[CHANGE]` block을 정렬
- **Draft plan 템플릿** (`docs/draft_plan_template.md`) — 10개 항목 템플릿 + claim→citation 테이블 + 승인 체크리스트
- **PubMed 검색 도구** — 내장 Python 스크립트 (MCP 및 외부 패키지 불필요)
- **공동 저자 토론** (`/paper-debate`) — 작성 전 Claude–Codex 토론으로 분석 계획·draft plan·논증 구조·리뷰어 응답 설계 (`docs/debate_protocol.md`)
- **멀티모델 비판적 검토** (`/critical-review`) — 작성 후 Claude 서브에이전트·Codex·OpenRouter 모델로 senior reviewer/editor 수준의 적대적 검토, 합의도 × 심각도로 정렬 (`docs/critical_review_protocol.md`)
- **편집장 desk-screen** (`/editor-review`) — 기계적 QC를 넘어선 high-impact 저널 편집장의 실질 평가: 논문의 분야를 식별하고 그 분야 high-impact 저널의 실제 게재물 기준으로 벤치마크해 임상 타당성·scope fit·분석 적절성을 판정 → `SEND FOR PEER REVIEW`/`BORDERLINE`/`DESK REJECT` 판정 + 경쟁력 위해 추가할 것(또는 현실적 하위 저널). 단일 Opus 서브에이전트 또는 멀티모델 panel; medical-kag 벤치마크 선택 (`docs/critical_review_protocol.md` §5)
- **AI-Draft De-bloat** — AI 흔적(피상적 `-ing` 분석·AI 어휘·신호어)을 제거해 disclosure를 유지하면서도 자연스럽게 읽히게 하는 writing-guide 패스 (`docs/writing_guide.md`)
- **슬래시 명령어** — 근거 문헌 등록 (`/search-evidence`, `/import-doi`)

---

## 프로젝트 구조

```
project/
├── WORKFLOW.md                   # 핵심 규칙 및 설정 (Claude/Codex/Gemini 공유)
├── CLAUDE.md                     # Claude Code 부트스트랩; @WORKFLOW.md로 WORKFLOW.md를 import
├── AGENTS.md                     # Codex/agent 시작 규칙; WORKFLOW.md를 source of truth로 참조
├── GEMINI.md                     # Gemini 부트스트랩; WORKFLOW.md 참조
├── README.md                     # 영문 README
├── .gitattributes                # 줄바꿈 정책 (text=auto eol=lf; OneDrive/Windows 동기화의 CRLF 변경 방지)
├── docs/                         # 참조 가이드
│   ├── workflow_reference.md     # Tree, file roles, command catalog (moved from WORKFLOW.md)
│   ├── writing_guide.md          # 섹션별 작성 가이드
│   ├── drafting_protocol.md      # 필수 drafting sequence
│   ├── section_templates.md      # 섹션별 문장 패턴
│   ├── expert_roles.md           # 전문가 팀 역할 및 책임
│   ├── checklist_guide.md        # 연구 유형별 체크리스트
│   ├── qc_guide.md               # 품질 관리 절차
│   ├── verification_protocol.md  # 검증 게이트·4 Verifier·자율 루프·게이트 원장
│   ├── verifier_prompt_templates.md  # LLM verifier prompt와 출력 schema
│   ├── statistical_analysis_guide.md  # 통계 분석 가이드
│   ├── evidence_guide.md         # 근거 문헌 작성 가이드
│   ├── revision_guide.md         # 리뷰어 응답 가이드
│   ├── response_letter_template.md  # DOCX-ready author response 템플릿
│   ├── figure_guide.md           # Figure 생성 가이드
│   ├── docx_guide.md             # DOCX 변환 가이드
│   ├── draft_plan_template.md    # Draft plan 템플릿 (Phase 3에서 복사하여 사용)
│   ├── debate_protocol.md        # Claude–Codex 공동 저자 토론 절차
│   ├── critical_review_protocol.md  # 외부 멀티모델 적대적 검토
│   ├── style_transform_protocol.md  # /style-pass 변환 + Style verifier
│   ├── style_spec_template.md    # Style Spec 템플릿 (exemplar 1개 바인딩)
│   ├── citation_assist_protocol.md  # 인용 제안 / 검증 / stance / 표
│   └── medical_kag_protocol.md   # medical-kag MCP (GraphRAG); evidence.md 정본
├── knowledge/                    # 참고 자료
│   ├── evidence.md               # 참고문헌 요약 정리 자료집
│   ├── pdf/                      # 원본 PDF 파일 — gitignored, 로컬 전용
│   ├── summaries/                # 개별 논문 상세 요약
├── Style/                        # 참고문헌과 분리된 writing-style 앵커
│   ├── PDF/                      # 스타일 분석 원본 PDF — gitignored, 로컬 전용
│   │   ├── own/
│   │   ├── landmark/
│   │   └── target_journal/
│   ├── own/                      # 본인 논문 스타일 앵커
│   ├── landmark/                 # 논증/프레이밍 앵커
│   ├── target_journal/           # 목표 저널 house-style 앵커
│   ├── style_guide.md            # 스타일 앵커 workflow 및 추출 규칙
│   └── terminology.md            # preferred/forbidden 용어 registry
├── profile/                      # 개인 정보 — gitignored, 로컬 전용
│   ├── authors.md                # 저자 소속·연락처·ORCID·funding
│   └── journals.md               # 저널별 인용 형식 (실제 논문 검증)
├── data/                         # 통계 분석
│   ├── raw_data.csv              # 원본 데이터셋
│   ├── analysis_plan.md          # 분석 계획 (분석 전 필수 작성)
│   └── py/                       # Python 분석 스크립트
├── scripts/                      # 유틸리티 스크립트
│   ├── lint_manuscript.py        # 원고 terminology/style lint 점검
│   ├── check_citations.py        # evidence citation gate
│   ├── check_numbers.py          # results CSV number gate
│   ├── check_gate.py             # phase gate ledger check
│   ├── check_revision_claims.py  # revision claim gate
│   ├── compile_response_docx.py  # Author response DOCX compiler
│   ├── search_pubmed.py          # PubMed 검색 도구 (외부 의존성 없음)
│   ├── check_style.py            # Style Spec 대비 측정 가능한 style 게이트
│   ├── extract_claims.py         # [EVID:id] 태그 문장 추출 (claim 검증)
│   ├── evidence_table.py         # 구조화된 연구 레코드 → markdown 비교표
│   ├── verify_all.py             # /verify — citation + number (+ gate) 일괄 실행
│   ├── critical_review.py        # OpenRouter 멀티모델 적대적 검토 호출
│   ├── critical_models.txt       # OpenRouter 모델 목록 (외부화)
│   ├── critical_prompts/         # 적대적 프롬프트 단일 정본 (manuscript.txt, response.txt)
│   └── hooks/                    # 강제 hook (enforce_gates, session_contract, lint_on_edit, style_intent) + run.sh 런처(py→python3 자동 선택)
├── tests/                        # 검증 스크립트용 pytest 스위트
├── results/                      # 분석 결과
├── drafts/                       # 원고 섹션, 테이블, 그림
│   ├── draft_plan.md             # 원고 구성 계획 (작성 전 필수)
│   ├── table_*.md
│   └── figures/
├── review/                       # QC 문서
│   ├── qc_log.md
│   └── gates/                    # 검증 게이트 원장 (phase_NN_*.GATE.md)
└── output/                       # 최종 원고
    ├── title_page_YYMMDD.docx
    ├── manuscript_YYMMDD.docx
    └── table_N_YYMMDD.docx
```

---

## 설치: 두 가지 방식

| | A. 템플릿 (설치 없음) | B. 설치형 엔진 |
|---|---|---|
| 받기 | `git clone` / "Use this template" | `uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@vX.Y.Z` |
| 논문 시작 | 복사한 폴더 안에서 작업 | `manuwright init my-paper` |
| 에이전트 | Claude Code 는 `.claude/`, Codex/Gemini 는 `AGENTS.md`/`GEMINI.md` | `manuwright agents install` (Claude Code, Codex, Antigravity, opencode, Muse) |
| 업데이트 | `git pull`(clone) 또는 공개 엔진 파일 교체 | `manuwright update`; 선택형 `manuwright config set auto-update on`(patch 만, 유효한 리뷰를 stale 로 만들지 않음) |

두 방식 모두 같은 엔진과 규칙을 씀. 자세한 내용: [docs/harness_guide.md](../../docs/harness_guide.md), 이전: [docs/migration_guide.md](../../docs/migration_guide.md), 설계: [docs/distribution_plan.md](../../docs/distribution_plan.md).

## 빠른 시작

1. **설정**: `WORKFLOW.md`에 연구 주제, 목표 저널, 연구 설계를 입력합니다. `profile/journals.md`에서 인용 형식, `Style/`에서 스타일 앵커를 확인합니다.
2. **참고문헌**: `/search-evidence [검색어]` 또는 `python scripts/search_pubmed.py`로 PubMed를 검색하고 `knowledge/evidence.md`에 등록합니다
3. **데이터 분석**: `data/` 폴더에 데이터를 배치 → `analysis_plan.md` 작성 (필수) → 통계 분석 실행
4. **원고 계획**: `docs/draft_plan_template.md`를 `drafts/draft_plan.md`로 복사 → 10개 항목 작성 (**Claim→Citation Mapping 포함**) (Opus 권장)
5. **초안 작성**: `docs/drafting_protocol.md`를 따르고 권장 순서에 따라 섹션 작성
6. **검증 게이트**: citation, number, phase-gate, revision-claim checker를 실행하고 `review/gates/`에 PASS 기록
7. **Revision response**: reviewer response가 필요하면 `docs/response_letter_template.md`로 작성하고 `scripts/compile_response_docx.py`로 DOCX 변환
8. **품질 관리**: 제출 전 최소 3라운드 QC 수행 (6라운드 권장)
9. **최종화**: 원고를 DOCX로 컴파일 (`docs/docx_guide.md` 참조)

---

## 주요 기능

### 전문가 팀 시뮬레이션
- **Dr. Researcher A**: 임상적 관점 (Introduction, Discussion)
- **Dr. Researcher B**: 방법론 (Methods, Results, Tables)
- **Dr. Statistician**: 통계 검증, 절제 원칙, MCID/NNT 평가
- **Dr. Editor**: 최종 교정, 일관성 검토

### 작성 전 필수 계획 (Planning Before Writing)

- **분석 계획** (`data/analysis_plan.md`): 통계 분석 전 필수 — 연구 질문, 평가 변수, 검정법 선택 정의
- **원고 계획** (`drafts/draft_plan.md`): 섹션 작성 전 필수 — 10개 항목 (핵심 메시지, 논조/어조, 필수 참고문헌, 근거 갭, **Claim→Citation Mapping**, Table/Figure 계획, 섹션별 개요)
- 두 계획 모두 사용자 승인 후 다음 단계 진행
- 멀티 논문 시 논문별 개별 계획 작성

### Claim→Citation Mapping (v0.7.0 신규)

초안 작성 전에 핵심 주장 ~20개와 근거 논문을 매핑하는 단계 (draft_plan.md 필수 항목):

- **Introduction background**: 5–8 claims (역학, 선행 근거)
- **Methods rationale**: 2–3 claims (결과 지표 선택 근거, 설계 근거)
- **Discussion comparisons**: 5–8 claims (선행연구와의 비교)

citation을 확보할 수 없는 claim이 있으면 Phase 1로 돌아가 먼저 검색. write-first, cite-later 패턴과 참고문헌 날조를 원천 차단.

### 스타일 앵커 라이브러리 (`Style/`)

참고문헌 관리와 분리된 스타일 앵커입니다. 원본 PDF는 `Style/PDF/`에 두고, 추출된 스타일 노트는 `Style/own/`, `Style/landmark/`, `Style/target_journal/`에 저장합니다.
템플릿: `Style/own/example_YYYY_Journal_keyword.md`

각 요약 파일에는 다음이 포함됩니다:

- 분야 표준 용어 (올바른 vs 잘못된 표현)
- Methods 본문 재사용 패턴 (boilerplate)
- 정확한 데이터가 포함된 핵심 주장 (cross-citation용)
- 논문 간 톤·어조 일관성 유지

### 단계별 모델 선택 (Model Selection by Phase)

- **Opus 권장**: Analysis Plan, Draft Plan, Revision — 전략적 판단이 필요한 단계
- **Sonnet 기본 (Opus 가능하면 사용)**: 초안 작성, Style Polish, QC — 계획 기반 실행
- 핵심 원칙: "Plan은 Opus로 잡고 → 작성은 Sonnet으로도 OK"

### 중복 방지
- 3중 중복 방지 (Results 본문 + Table + Figure)
- Table vs Figure 결정을 위한 명확한 가이드라인
- 표준 테이블 구조 (Table 1: 인구통계, Table 2: 주요 결과)

### 통계 분석 가이드 (v0.3.0)
- 통계적 절제 원칙 (Statistical Parsimony) — RCT Table 1에 p-value 생략
- 분석 위계 — Primary > Secondary > Exploratory
- 임상적 유의성 — Effect size, MCID, NNT
- 하위군 분석 규칙 — Interaction test 필수
- 비유의 결과 보고 가이드

### 품질 관리 (6라운드)
- Round 1: 숫자 일관성
- Round 2: 참고문헌 검증 (+ 등장순 번호, placeholder 감지, 서지 형식 일관성, 인용 분포)
- Round 3: 논리적 흐름
- Round 4: 용어/약어/시제 일관성
- Round 5: 통계적 품질
- Round 6: 비판적 검토 (과장, 논리적 오류, 편향, 일반화 가능성)

### 검증 하네스

이 하네스는 deterministic checker와 제한된 LLM verifier prompt를 함께 사용합니다:

- `scripts/check_citations.py`: 모든 `[EVID:id]` citation을 `knowledge/evidence.md`와 대조하고, 미확인/알 수 없는 근거를 실패 처리합니다.
- `scripts/check_numbers.py`: 원고와 표의 숫자를 `results/*.csv`와 대조합니다.
- `scripts/check_gate.py`: phase gate ledger에 `status: PASS`와 필수 check가 있는지 확인합니다.
- `scripts/check_revision_claims.py`: reviewer response의 `[CHANGE]` block을 revised manuscript 파일과 대조합니다.
- `docs/verifier_prompt_templates.md`: semantic support, logic, redundancy, revision-response alignment 검증 prompt/schema를 제공합니다.

### 공동 저자 협업 (v0.9.3 신규)

Codex/멀티모델을 활용한 두 가지 상호 보완적 기능이 작성 과정의 앞뒤를 감쌉니다:

- **`/paper-debate <주제>`** — 작성 *전*. Claude와 Codex가 공동 저자로서 분석 접근, draft plan의 key message, 논증 구조, 리뷰어 응답 전략을 제한된 라운드(합의 상한 3) 안에서 토론합니다. 토론 로그는 `review/debates/`에 저장되고, 합의된 결론이 다음 산출 단계로 연결됩니다. Codex를 사용할 수 없으면 Claude 단독으로 폴백합니다. `docs/debate_protocol.md` 참조.
- **`/critical-review <대상>`** — 작성 *후*. 완성된 원고(또는 response letter)를 새로운 Claude 서브에이전트, Codex, OpenRouter 모델(기본 `minimax/minimax-m3`, `z-ai/glm-5.2`)의 임의 조합으로 병렬 공격합니다. 각 리뷰어는 **senior peer-reviewer / editor-in-chief 수준**으로 프롬프트되어, 표면적 결함을 넘어 설계 견고성, 데이터가 결론을 뒷받침하는지, 출판 가치를 따집니다. 지적사항은 **합의도 × 심각도**(Critical / Important / Minor)로 통합·정렬되어 `review/critical/`에 저장됩니다. `docs/critical_review_protocol.md` 참조.

적대적 프롬프트는 `scripts/critical_prompts/`(`manuscript.txt`, `response.txt`)에 단일 정본으로 존재하며, OpenRouter 스크립트·Claude 서브에이전트·Codex가 모두 같은 파일을 읽습니다. OpenRouter 접근은 `OPENROUTER_API_KEY`(`.claude/settings.local.json`에 설정, gitignored)를 사용하며, 키가 없으면 OpenRouter만 건너뛰고 나머지 리뷰어로 진행합니다.

### AI-Draft De-bloat (v0.9.3 신규)

AI 산문의 흔적 — 피상적인 `-ing` "표면 분석" 절, AI가 선호하는 어휘, 과도한 신호어(over-signposting) — 을 제거하되, 정당하게 충돌하는 패턴(필요한 hedging, copula, passive voice)은 명시적으로 **제외**하는 `docs/writing_guide.md` 패스입니다 (AI가 작성한 초안에 대해 Phase 5에서 적용). AI 작성 사실은 그대로 disclosure하며, 이 패스는 disclosure된 보조 작성물이 장황하고 지루하게 읽히지 않도록 할 뿐입니다.

### Verification Hardening (v1.0.0 신규)

"superpowers" 스킬 프레임워크에서 가져와 검증 게이트에 맞게 적용한 개선 사항입니다:

- **병렬 verifier + Constraint 우선.** 4개의 섹션 게이트 verifier(Constraint / Citation / Data / Logic)를 동결된(frozen) 산출물에 대해 동시에 dispatch합니다. 검증 도중에는 산출물을 편집하지 않으며, FAIL 시 Constraint(spec 준수) 지적사항을 먼저 수정합니다. `docs/verification_protocol.md` (v0.3.0) 참조.
- **Gate freshness / provenance** (`scripts/check_gate.py`). PASS 시 게이트 원장에 검증된 산출물(및 citation·numbers 관련 게이트의 경우 `evidence` / `results`; revision에서는 필수)의 sha256을 기록합니다. `check_gate.py --verify-hash LABEL=PATH`는 파일을 다시 해싱하여 PASS 이후 파일이 변경되었으면 게이트를 **stale**로 실패 처리합니다 — PASS 이후의 편집이 재점검을 조용히 빠져나가는 허점을 차단합니다. `--compute-hash PATH`는 provenance 필드를 채웁니다. 도구 수준에서는 opt-in이며, 문서화된 게이트 명령에서는 표준으로 사용합니다.
- **STOP 신호.** WORKFLOW.md의 anti-rationalization 표가 verifier로는 잡을 수 없는 사람 수준의 지름길을 포착합니다 ("이 숫자는 아마 괜찮을 거야" → CSV를 확인; "이미 통과했어" → 변경된 산출물은 stale).
- **Socratic draft-plan 브레인스토밍.** `docs/draft_plan_template.md`의 "Step 0"가 plan을 채우기 전에 한 번에 한 질문씩 논문의 의도를 다듬습니다 — `/paper-debate`와는 구분되며, 토론의 R0 사전 준비로 연결됩니다.
- **리뷰어 응답 triage.** `docs/revision_guide.md`가 각 리뷰어 코멘트에 accept / partial / rebut 입장을 부여하고, 이를 `[CHANGE]` 마커 및 ghost-revision 게이트와 연결합니다.
- **명령어 `use-when` 안내.** 각 `.claude/commands/*.md`가 이제 자신을 트리거해야 하는 상황을 명시합니다.

### Author Response DOCX Workflow

Reviewer response는 `docs/response_letter_template.md` 형식으로 작성하고, 각 원고 수정은 `[CHANGE]` block으로 기록합니다. 최종 response letter는 다음 명령으로 컴파일합니다:

```powershell
python scripts/compile_response_docx.py drafts/revision/REV1/response_letter_REV1.md
```

compiler는 `Author_response_220803_Final.docx`의 house style을 재현합니다 — Times New Roman 11 pt, response/위치/수정문 줄은 bold, 본문은 justified. 이 .docx 파일을 템플릿으로 읽지 않으며, 서식은 코드에 내장되어 있습니다.

### PubMed 검색 도구

MCP 없이 참고문헌을 검색할 수 있는 내장 Python 스크립트 (`scripts/search_pubmed.py`):

```bash
python scripts/search_pubmed.py search "endoscopic spine surgery"  # 검색
python scripts/search_pubmed.py fetch 35486828                     # PMID로 가져오기
python scripts/search_pubmed.py doi 10.1016/j.spinee.2023.01.005  # DOI로 가져오기
python scripts/search_pubmed.py related 35486828                   # 관련 논문
```

Claude 통합 슬래시 명령어:

- `/search-evidence [검색어]` - 검색, 선택, evidence.md에 등록
- `/import-doi [doi]` - DOI로 가져와서 evidence.md에 등록

---

## 문서 목록

| 문서 | 목적 |
|------|------|
| [WORKFLOW.md](../../WORKFLOW.md) | 핵심 규칙 및 프로젝트 설정 (모든 런타임 공유) |
| [CLAUDE.md](../../CLAUDE.md) | Claude Code 부트스트랩; WORKFLOW.md를 import |
| [docs/writing_guide.md](../../docs/writing_guide.md) | 섹션별 작성 가이드 + Style Reference Tables + Writing Principles (4 Pillars) |
| [docs/drafting_protocol.md](../../docs/drafting_protocol.md) | outline → evidence-bound draft → style/QC pass 필수 drafting workflow |
| [docs/section_templates.md](../../docs/section_templates.md) | 섹션별 paragraph function과 문장 패턴 |
| [docs/expert_roles.md](../../docs/expert_roles.md) | 전문가 팀 설명 |
| [docs/checklist_guide.md](../../docs/checklist_guide.md) | STROBE, CONSORT, PRISMA, CARE 체크리스트 |
| [docs/qc_guide.md](../../docs/qc_guide.md) | 품질 관리 절차 (6라운드) |
| [docs/verification_protocol.md](../../docs/verification_protocol.md) | 검증 게이트·4 Verifier 헌장·자율 수정 루프·게이트 원장 |
| [docs/verifier_prompt_templates.md](../../docs/verifier_prompt_templates.md) | LLM semantic verifier prompt와 구조화된 출력 schema |
| [docs/statistical_analysis_guide.md](../../docs/statistical_analysis_guide.md) | 통계 분석 가이드 (절제 원칙, MCID, 하위군 분석) |
| [docs/evidence_guide.md](../../docs/evidence_guide.md) | 근거 문헌 작성 가이드 (형식, 요약 방법, 워크플로우) |
| [docs/revision_guide.md](../../docs/revision_guide.md) | 리뷰어 응답 가이드 (응답서 작성, 외교적 표현, QC 재수행 체크리스트) |
| [docs/response_letter_template.md](../../docs/response_letter_template.md) | DOCX-ready author response Markdown 템플릿 |
| [docs/figure_guide.md](../../docs/figure_guide.md) | Figure 생성 가이드 (DPI, 팔레트, Python 템플릿) |
| [docs/docx_guide.md](../../docs/docx_guide.md) | DOCX 변환 가이드 (서식, 테이블 스타일, 네이밍 규칙) |
| [docs/draft_plan_template.md](../../docs/draft_plan_template.md) | Draft plan 템플릿 — 10개 항목 + claim→citation 테이블 + 승인 체크리스트 |
| [docs/debate_protocol.md](../../docs/debate_protocol.md) | Claude–Codex 공동저자 토론 절차 (라운드, 역할, 로깅, fallback) |
| [docs/critical_review_protocol.md](../../docs/critical_review_protocol.md) | 외부 멀티모델 적대적 검토 (리뷰어 풀, 합의도 × 심각도, fallback) |
| [Style/style_guide.md](../../Style/style_guide.md) | 스타일 앵커 워크플로우, 추출 프레임워크, PDF-to-MD 미러 규칙 |
| [Style/terminology.md](../../Style/terminology.md) | preferred/forbidden 용어 registry, 정의, context |
| [Style/own/example_YYYY_Journal_keyword.md](../../Style/own/example_YYYY_Journal_keyword.md) | 본인 논문 스타일 앵커 템플릿 |
| [scripts/lint_manuscript.py](../../scripts/lint_manuscript.py) | 용어, placeholder, 과장 표현, 섹션별 위반 점검 lint 스크립트 |
| [scripts/check_citations.py](../../scripts/check_citations.py) | `[EVID:id]` citation을 `knowledge/evidence.md`와 대조 |
| [scripts/check_coverage.py](../../scripts/check_coverage.py) | 인용 coverage audit — **과잉인용**(한 주장에 과다 인용)·**미등록인용**이 품질 신호, 섹션별 인용밀도; uncited/미실현 claim은 중립(큐레이션, 낭비 아님) |
| [scripts/format_references.py](../../scripts/format_references.py) | `[EVID:id]` → 저널형 서지목록(numbered/author-year) + 본문 태그를 `*_formatted.md`로 변환; **MCP 독립** (Phase 7) |
| [scripts/check_abstract.py](../../scripts/check_abstract.py) | abstract↔본문 수치 일관성 — abstract에만 있고 본문에 없는 수치를 차단 (Rule 3; p값 기본 제외) (Phase 6 QC Round 1) |
| [scripts/check_crossrefs.py](../../scripts/check_crossrefs.py) | Table/Figure 교차참조 검사 — 본문 "Table N"/"Figure N" 언급 ↔ 실제 `table_*.md`·figure legends: **broken reference**(주신호)·미인용 항목·첫 언급 순서; advisory 기본, `--fail-on-*`로 게이트화 (Phase 6 QC) |
| [scripts/check_abbreviations.py](../../scripts/check_abbreviations.py) | 약어 첫 사용 정의 검사 — abstract/본문 별도 scope (UNDEFINED / DEFINED_AFTER_USE / REDEFINED / SINGLE_USE); 오탐 전제 advisory, `--allow`·`--strict` (Phase 6 QC) |
| [scripts/check_response_coverage.py](../../scripts/check_response_coverage.py) | 리뷰어 코멘트 응답 커버리지 — 모든 `Comment N)`에 실제 `Response:` 필수 (미응답·빈 응답·placeholder 차단), `--comments`로 원본 코멘트 파일 대조; ghost-revision 게이트 보완 (Phase 8) |
| [scripts/check_numbers.py](../../scripts/check_numbers.py) | 원고/표의 숫자를 `results/*.csv`와 대조 |
| [scripts/check_gate.py](../../scripts/check_gate.py) | `review/gates/*.GATE.md`의 status와 필수 check 검증 |
| [scripts/check_revision_claims.py](../../scripts/check_revision_claims.py) | response-letter `[CHANGE]` claim을 revised manuscript와 대조 |
| [scripts/compile_response_docx.py](../../scripts/compile_response_docx.py) | `response_letter_REV*.md`를 Author_response 양식 DOCX로 변환 |
| [scripts/search_pubmed.py](../../scripts/search_pubmed.py) | PubMed 검색 스크립트 (NCBI E-utilities, 외부 패키지 불필요) |
| [scripts/critical_review.py](../../scripts/critical_review.py) | OpenRouter 멀티모델 적대적 리뷰어 호출 (모델 1개 실패가 전체를 중단시키지 않음) |

---

## 요구사항

- Claude AI (Claude Code CLI 또는 VSCode 확장)
- Python 3.10+ (구버전이면 `python -m harness doctor` 가 경고; 테스트: `pip install -r requirements-dev.txt`)
- 통계 분석용 Python 패키지: pandas, numpy, scipy, statsmodels, python-docx
- PubMed 검색 스크립트 (`scripts/search_pubmed.py`)는 Python 표준 라이브러리만 사용 (추가 패키지 불필요)

---

## 저자

**박상민 교수, M.D., Ph.D.**

정형외과학교실,
서울대학교 분당서울대학교병원,
서울대학교 의과대학

https://sangmin.me/

---

## 라이선스

이 저작물은 **크리에이티브 커먼즈 저작자표시 4.0 국제 라이선스 (CC BY 4.0)** 에 따라 이용할 수 있습니다.

Copyright (c) 2026 박상민, 서울대학교 분당서울대학교병원

### 이용 허락:
- **공유** — 어떤 매체나 형식으로도 자료를 복제하고 재배포할 수 있습니다
- **변경** — 어떤 목적으로든 자료를 리믹스, 변환, 추가 제작할 수 있습니다

### 이용 조건:
- **저작자표시** — 적절한 출처를 밝히고, 라이선스 링크를 제공하며, 변경 사항이 있을 경우 표시해야 합니다.

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

전체 라이선스 원문: https://creativecommons.org/licenses/by/4.0/legalcode

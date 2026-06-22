🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# Claude를 활용한 의학 학술 논문 작성 워크플로우

Claude AI를 활용한 의학 학술 논문 작성을 위한 체계적인 워크플로우 시스템입니다.

## 버전

**v1.2.0** (2026-06-22)

---

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
- **학술 작문 스타일 시스템** — Style Reference Tables (Voice/Tense, Transition, Verb Upgrades, Common Corrections, Statistical Notation, Hedging) + Writing Principles (Clarity/Conciseness/Objectivity/Consistency)
- **인용 품질 관리** — Claim→Citation Mapping (작성 전 핵심 주장 ~20개와 근거 논문 매핑; write-first, cite-later 방지)
- **스타일 앵커 라이브러리** (`Style/`) — own, landmark, target-journal 앵커로 용어·톤·논증·저널 house style 확보
- **분야 표준 용어 registry** (`Style/terminology.md`) — preferred/forbidden 용어, 정의, context
- **Drafting protocol** (`docs/drafting_protocol.md`) — outline → evidence-bound draft → style pass → QC 강제
- **Manuscript linting** (`scripts/lint_manuscript.py`) — 용어, placeholder, 과장 표현, 섹션별 위반 자동 점검
- **Citation evidence checking** (`scripts/check_citations.py`) — `[EVID:id]` 태그를 `knowledge/evidence.md`와 대조
- **Data number checking** (`scripts/check_numbers.py`) — 원고/표의 숫자를 `results/*.csv`와 대조
- **Phase gate ledger checking** (`scripts/check_gate.py`) — `review/gates/*.GATE.md`에 필수 PASS가 없으면 진행 차단
- **Gate freshness / provenance** (`scripts/check_gate.py --verify-hash`) — PASS 시 검증된 산출물(및 evidence/results)의 sha256을 기록; 이후 편집이 발생하면 게이트가 **stale** 상태가 되어 재검증을 강제하므로, 병렬 verifier의 허점을 차단
- **Revision claim checking** (`scripts/check_revision_claims.py`) — response letter의 `[CHANGE]` claim을 revised manuscript와 대조
- **LLM verifier prompt templates** (`docs/verifier_prompt_templates.md`) — constraint, semantic citation, data, logic/redundancy, revision-alignment 검증 prompt/schema
- **Author response DOCX generation** (`scripts/compile_response_docx.py`) — DOCX-ready Markdown을 `Author_response_220803_Final.docx` house style에 맞춰 변환
- **Author response Markdown template** (`docs/response_letter_template.md`) — reviewer response, 수정 위치, machine-readable `[CHANGE]` block을 정렬
- **Draft plan 템플릿** (`docs/draft_plan_template.md`) — 10개 항목 템플릿 + claim→citation 테이블 + 승인 체크리스트
- **PubMed 검색 도구** — 내장 Python 스크립트 (MCP 및 외부 패키지 불필요)
- **공동 저자 토론** (`/paper-debate`) — 작성 전 Claude–Codex 토론으로 분석 계획·draft plan·논증 구조·리뷰어 응답 설계 (`docs/debate_protocol.md`)
- **멀티모델 비판적 검토** (`/critical-review`) — 작성 후 Claude 서브에이전트·Codex·OpenRouter 모델로 senior reviewer/editor 수준의 적대적 검토, 합의도 × 심각도로 정렬 (`docs/critical_review_protocol.md`)
- **AI-Draft De-bloat** — AI 흔적(피상적 `-ing` 분석·AI 어휘·신호어)을 제거해 disclosure를 유지하면서도 자연스럽게 읽히게 하는 writing-guide 패스 (`docs/writing_guide.md`)
- **슬래시 명령어** — 근거 문헌 등록 (`/search-evidence`, `/import-doi`)

---

## 프로젝트 구조

```
project/
├── CLAUDE.md                     # 핵심 규칙 및 설정
├── AGENTS.MD                     # agent 시작 규칙; CLAUDE.md를 source of truth로 참조
├── README.md                     # 영문 README
├── docs/                         # 참조 가이드
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
│   └── draft_plan_template.md    # Draft plan 템플릿 (Phase 3에서 복사하여 사용)
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
│   ├── critical_review.py        # OpenRouter 멀티모델 적대적 검토 호출
│   ├── critical_models.txt       # OpenRouter 모델 목록 (외부화)
│   └── critical_prompts/         # 적대적 프롬프트 단일 정본 (manuscript.txt, response.txt)
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

## 빠른 시작

1. **설정**: `CLAUDE.md`에 연구 주제, 목표 저널, 연구 설계를 입력합니다. `profile/journals.md`에서 인용 형식, `Style/`에서 스타일 앵커를 확인합니다.
2. **참고문헌**: `/search-evidence [검색어]` 또는 `python3 scripts/search_pubmed.py`로 PubMed를 검색하고 `knowledge/evidence.md`에 등록합니다
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

- **병렬 verifier + Constraint 우선.** 4개의 섹션 게이트 verifier(Constraint / Citation / Data / Logic)를 동결된(frozen) 산출물에 대해 동시에 dispatch합니다. 검증 도중에는 산출물을 편집하지 않으며, FAIL 시 Constraint(spec 준수) 지적사항을 먼저 수정합니다. `docs/verification_protocol.md` (v0.2.0) 참조.
- **Gate freshness / provenance** (`scripts/check_gate.py`). PASS 시 게이트 원장에 검증된 산출물(및 citation·numbers 관련 게이트의 경우 `evidence` / `results`; revision에서는 필수)의 sha256을 기록합니다. `check_gate.py --verify-hash LABEL=PATH`는 파일을 다시 해싱하여 PASS 이후 파일이 변경되었으면 게이트를 **stale**로 실패 처리합니다 — PASS 이후의 편집이 재점검을 조용히 빠져나가는 허점을 차단합니다. `--compute-hash PATH`는 provenance 필드를 채웁니다. 도구 수준에서는 opt-in이며, 문서화된 게이트 명령에서는 표준으로 사용합니다.
- **STOP 신호.** CLAUDE.md의 anti-rationalization 표가 verifier로는 잡을 수 없는 사람 수준의 지름길을 포착합니다 ("이 숫자는 아마 괜찮을 거야" → CSV를 확인; "이미 통과했어" → 변경된 산출물은 stale).
- **Socratic draft-plan 브레인스토밍.** `docs/draft_plan_template.md`의 "Step 0"가 plan을 채우기 전에 한 번에 한 질문씩 논문의 의도를 다듬습니다 — `/paper-debate`와는 구분되며, 토론의 R0 사전 준비로 연결됩니다.
- **리뷰어 응답 triage.** `docs/revision_guide.md`가 각 리뷰어 코멘트에 accept / partial / rebut 입장을 부여하고, 이를 `[CHANGE]` 마커 및 ghost-revision 게이트와 연결합니다.
- **명령어 `use-when` 안내.** 각 `.claude/commands/*.md`가 이제 자신을 트리거해야 하는 상황을 명시합니다.

### Author Response DOCX Workflow

Reviewer response는 `docs/response_letter_template.md` 형식으로 작성하고, 각 원고 수정은 `[CHANGE]` block으로 기록합니다. 최종 response letter는 다음 명령으로 컴파일합니다:

```powershell
py scripts\compile_response_docx.py drafts\revision\REV1\response_letter_REV1.md
```

compiler는 `Author_response_220803_Final.docx`의 house style을 재현합니다 — Times New Roman 11 pt, response/위치/수정문 줄은 bold, 본문은 justified. 이 .docx 파일을 템플릿으로 읽지 않으며, 서식은 코드에 내장되어 있습니다.

### PubMed 검색 도구

MCP 없이 참고문헌을 검색할 수 있는 내장 Python 스크립트 (`scripts/search_pubmed.py`):

```bash
python3 scripts/search_pubmed.py search "endoscopic spine surgery"  # 검색
python3 scripts/search_pubmed.py fetch 35486828                     # PMID로 가져오기
python3 scripts/search_pubmed.py doi 10.1016/j.spinee.2023.01.005  # DOI로 가져오기
python3 scripts/search_pubmed.py related 35486828                   # 관련 논문
```

Claude 통합 슬래시 명령어:

- `/search-evidence [검색어]` - 검색, 선택, evidence.md에 등록
- `/import-doi [doi]` - DOI로 가져와서 evidence.md에 등록

---

## 문서 목록

| 문서 | 목적 |
|------|------|
| [CLAUDE.md](CLAUDE.md) | 핵심 규칙 및 프로젝트 설정 |
| [docs/writing_guide.md](docs/writing_guide.md) | 섹션별 작성 가이드 + Style Reference Tables + Writing Principles (4 Pillars) |
| [docs/drafting_protocol.md](docs/drafting_protocol.md) | outline → evidence-bound draft → style/QC pass 필수 drafting workflow |
| [docs/section_templates.md](docs/section_templates.md) | 섹션별 paragraph function과 문장 패턴 |
| [docs/expert_roles.md](docs/expert_roles.md) | 전문가 팀 설명 |
| [docs/checklist_guide.md](docs/checklist_guide.md) | STROBE, CONSORT, PRISMA, CARE 체크리스트 |
| [docs/qc_guide.md](docs/qc_guide.md) | 품질 관리 절차 (6라운드) |
| [docs/verification_protocol.md](docs/verification_protocol.md) | 검증 게이트·4 Verifier 헌장·자율 수정 루프·게이트 원장 |
| [docs/verifier_prompt_templates.md](docs/verifier_prompt_templates.md) | LLM semantic verifier prompt와 구조화된 출력 schema |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | 통계 분석 가이드 (절제 원칙, MCID, 하위군 분석) |
| [docs/evidence_guide.md](docs/evidence_guide.md) | 근거 문헌 작성 가이드 (형식, 요약 방법, 워크플로우) |
| [docs/revision_guide.md](docs/revision_guide.md) | 리뷰어 응답 가이드 (응답서 작성, 외교적 표현, QC 재수행 체크리스트) |
| [docs/response_letter_template.md](docs/response_letter_template.md) | DOCX-ready author response Markdown 템플릿 |
| [docs/figure_guide.md](docs/figure_guide.md) | Figure 생성 가이드 (DPI, 팔레트, Python 템플릿) |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 변환 가이드 (서식, 테이블 스타일, 네이밍 규칙) |
| [docs/draft_plan_template.md](docs/draft_plan_template.md) | Draft plan 템플릿 — 10개 항목 + claim→citation 테이블 + 승인 체크리스트 |
| [Style/style_guide.md](Style/style_guide.md) | 스타일 앵커 워크플로우, 추출 프레임워크, PDF-to-MD 미러 규칙 |
| [Style/terminology.md](Style/terminology.md) | preferred/forbidden 용어 registry, 정의, context |
| [Style/own/example_YYYY_Journal_keyword.md](Style/own/example_YYYY_Journal_keyword.md) | 본인 논문 스타일 앵커 템플릿 |
| [scripts/lint_manuscript.py](scripts/lint_manuscript.py) | 용어, placeholder, 과장 표현, 섹션별 위반 점검 lint 스크립트 |
| [scripts/check_citations.py](scripts/check_citations.py) | `[EVID:id]` citation을 `knowledge/evidence.md`와 대조 |
| [scripts/check_numbers.py](scripts/check_numbers.py) | 원고/표의 숫자를 `results/*.csv`와 대조 |
| [scripts/check_gate.py](scripts/check_gate.py) | `review/gates/*.GATE.md`의 status와 필수 check 검증 |
| [scripts/check_revision_claims.py](scripts/check_revision_claims.py) | response-letter `[CHANGE]` claim을 revised manuscript와 대조 |
| [scripts/compile_response_docx.py](scripts/compile_response_docx.py) | `response_letter_REV*.md`를 Author_response 양식 DOCX로 변환 |
| [scripts/search_pubmed.py](scripts/search_pubmed.py) | PubMed 검색 스크립트 (NCBI E-utilities, 외부 패키지 불필요) |
| [scripts/critical_review.py](scripts/critical_review.py) | OpenRouter 멀티모델 적대적 리뷰어 호출 (모델 1개 실패가 전체를 중단시키지 않음) |

---

## 요구사항

- Claude AI (Claude Code CLI 또는 VSCode 확장)
- Python 3.x (통계 분석 및 PubMed 검색용)
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

---

## 변경 이력

### v1.2.0 (2026-06-22)

**medical-kag MCP 통합 — evidence.md와 함께 작동하는 knowledge graph**

- **Grounding을 보존하는 KAG 통합** — `medical-kag-remote` MCP(척추 수술 knowledge-augmented graph)가 상류(upstream)의 discovery/analysis/format 엔진으로 연결되지만, `knowledge/evidence.md`는 여전히 단일 정본(canonical) citation ledger로 남습니다. graph가 surface한 모든 것은 인용되기 전에 `[EVID:id]`(PMID/DOI 검증 완료)로 등록되므로, `check_citations.py`가 변함없이 모든 것을 게이트합니다. 신규 `docs/medical_kag_protocol.md`가 도구를 phase에 매핑합니다 — discovery + 구조화 추출(Phase 1), claim과 Discussion을 위한 evidence-chain / intervention-comparison / GRADE 종합(Phase 3-4), conflict / overclaim 가드(Phase 6), 저널 형식 참고문헌 목록(Phase 7).
- **부가적(additive) + 폴백** — 이 MCP는 결코 의존성이 아닙니다: 사용할 수 없는 경우(예: 인증되지 않은 remote 세션) 워크플로는 `scripts/search_pubmed.py` + 수동 evidence.md로 degrade합니다. Codex 동등성을 위해 CLAUDE.md(Rule 1, STOP 신호, Phase 1, Quick Commands)와 AGENTS.MD에 연결되어 있습니다.

### v1.1.2 (2026-06-21)

**수정 — hook이 UTF-8 stdin을 읽도록 (Windows에서 한국어 의도 인식)**

- `UserPromptSubmit` / `PreToolUse` / `PostToolUse` hook이 이제 stdin을 UTF-8로 재설정합니다. Windows(기본 cp949)에서는 Claude Code가 보내는 JSON payload가 잘못 디코딩되어, ASCII가 아닌 프롬프트 — 예: 한국어 자동 트리거 "학술적으로 바꿔줘" — 가 조용히 매칭에 실패했습니다. 종단 간(end-to-end) UTF-8 stdin 테스트를 추가했습니다.

### v1.1.1 (2026-06-21)

**스타일 강제 — 측정 가능한 게이트 + Codex 동등성**

- **결정적 스타일 지표** — `scripts/check_style.py`(`extract` / `check --spec`)가 단어 수, 평균 문장 길이, 문단 수, 인용 밀도, hedging을 측정하고 Style Spec 목표치에서 벗어나는 편차를 표시합니다 — 스타일판 "check_numbers". `lint_on_edit.py`에 연결되어(Style Spec이 존재할 때 각 초안 편집마다 `[STYLE-METRIC]` 편차를 표면화) Phase 5/6 게이트와 함께 작동합니다. 테스트 추가.
- **Codex 동등성 + 보정** — hook은 Claude Code 전용이므로, 이제 `AGENTS.MD`가 Claude가 아닌 런타임에게 style-pass(`check_style.py` + Style-Conformance verifier)를 명시적으로 실행하도록 안내합니다. Style Spec 템플릿에는 before→after 보정 예시가 추가됩니다(few-shot이 추상적 규칙보다 변환을 더 잘 유도함).

### v1.1.0 (2026-06-21)

**스타일 변환 — 거친 초안 → bound 저널 스타일로, 안정적으로**

- **Style Spec + Style-Conformance Verifier** — 하나의 exemplar(`Style/own/` 또는 `Style/target_journal/`)를 항상 로드되는 간결한 `drafts/style_spec.md`(`docs/style_spec_template.md`)로 묶은 뒤, 섹션별로 변환하고 각 섹션을 독립적인 **Style-Conformance Verifier**로 spec과 대조해 검증합니다(자동 수정 루프, 최대 2회; `docs/verifier_prompt_templates.md` + `verification_protocol.md`). 이로써 lint가 닿지 못하는 총체적 스타일 층위(구조, 문장 길이, hedging, 주장 강도, 참고문헌 형식)에 도달합니다. 신규 `/style-pass` 명령 + `docs/style_transform_protocol.md`.
- **의도 기반 자동 트리거** — `UserPromptSubmit` hook(`scripts/hooks/style_intent.py`)이 "make it academic / 학술적으로 바꿔줘"를 감지해 style-pass 프로토콜을 주입하므로, 명령을 기억하지 않아도 변환이 작동합니다. SessionStart도 이제 활성 Style Spec을 함께 표시합니다. Advisory + fail-open. 테스트 추가.

### v1.0.3 (2026-06-20)

**런타임 간 critical review + 모델 선택**

- **Claude-CLI 리뷰어** — `scripts/critical_review.py --include-claude`는 로컬 `claude -p`(headless)를 shell로 호출하므로, Claude Code가 아닌 호출자(Codex나 일반 shell)도 Claude의 적대적 검토를 가져올 수 있습니다. `OPENROUTER_API_KEY`는 이제 OpenRouter 모델을 실제로 요청할 때만 필요합니다. `docs/critical_review_protocol.md` + `AGENTS.MD`에 문서화.
- **더 큰 모델 풀 + ~2개 선택** — `scripts/critical_models.txt`에 MiniMax M3, GLM 5.2, Qwen3-Max, DeepSeek V4 Pro가 추가되었습니다. `/critical-review`는 이들을 개별 `AskUserQuestion` 옵션으로 제시하고 ~2개 선택을 권장하며(비용 + 사각지대 다양성), 이후 `--models <selected>`로 실행합니다.

### v1.0.2 (2026-06-20)

**프로세스 강제 + CLAUDE.md 간결화**

- **Plan-first 강제 (hooks)** — `.claude/settings.json`에 커밋된 hook을 추가: PreToolUse `Write|Edit` 게이트(`scripts/hooks/enforce_gates.py`)는 `drafts/.../draft_plan.md` 없이 섹션을 작성하거나(Rule 8) `data/.../analysis_plan.md` 없이 분석 스크립트를 생성하는 것(Rule 7)을 **차단**하고, SessionStart hook(`scripts/hooks/session_contract.py`)은 매 세션마다 워크플로 계약을 주입합니다. Revision은 예외 처리되고, 멀티 논문 서브폴더를 지원하며, 실패 시 통과(fails open)하고, UTF-8 안전합니다. (Windows는 `py`; macOS/Linux는 `python3` 사용.)
- **`/verify`** — `scripts/verify_all.py`가 게이트 PASS를 기록하기 전에 check_citations + check_numbers(+ 선택적 check_gate)를 한 번의 명령으로 실행합니다. hook 테스트 신규 추가; 스위트 86개 통과.
- **CLAUDE.md 808 → 696줄 (~14%) 간결화** — 멀티 논문/Revision 구조 트리와 Phase 2 Notes / 검정 선택 / 스타일 우선순위 / 게이트 배치 중복을 각 정본 문서에 대한 pointer로 축약; MUST-FOLLOW 규칙은 하나도 제거하지 않음.

### v1.0.1 (2026-06-20)

**릴리스 후 안정화 + 간결화 도구**

- **당일 안정화 (코드 리뷰 + 프로젝트 감사)** — `check_gate.py`의 freshness가 이제 file이 아닌 경로(디렉터리/없는 파일)에 대해 크래시 없이 깔끔하게 실패하고, 상대 경로를 repo `ROOT` 기준으로 해석하며, 비어 있거나 placeholder인 digest를 명확한 메시지와 함께 거부하고, PASS 출력에 `provenance_verified` / `provenance_unverified`를 보고. Phase 8 verifier set 정렬 (Logic은 Draft 전용; Revision은 Revision-claims + Response-alignment 추가)과 게이트 명령의 `--require-check constraint`; "3 verifiers"를 "4"로 정정; Critical Rules를 9/10/11로 재번호; `lint_manuscript.py`가 존재하지 않는 `.md` 인자를 건너뜀(첫 lint 테스트 추가); `check_numbers.py`가 0–1 사이의 임의 비율이 아니라 명시적 p-value를 요구; `search_pubmed.py` evidence 항목에 Evidence ID + Source Status 추가; checker FAIL 출력에 `failure_code` 추가; 테스트 77개로 확장.
- **Concision Pass** — `docs/writing_guide.md`에 저널 단어 수 제한 압축 패스(Phase 5) 추가: 시니어 영문 교정에서 도출한 10개의 Before→After 패턴과 과도 압축 방지 가드레일(primary-outcome 정의, 통계 명세, eligibility, 핵심 limitation은 본문에 유지하거나 Supplement로 이동 — 조용히 삭제 금지).

### v1.0.0 (2026-06-20)

**검증 하네스 강화 (superpowers 기반)**

- **Gate freshness / provenance** — `check_gate.py`에 `provenance:` block(산출물/evidence/results의 sha256), `--verify-hash LABEL=PATH`(검증된 파일이 PASS 이후 변경되면 게이트를 *stale*로 실패 처리), `--compute-hash PATH` 추가. 병렬 검증으로 생긴 stale-PASS 허점을 차단; 하위 호환(opt-in 플래그). `review/gates/_TEMPLATE.GATE.md`와 `docs/verification_protocol.md`(v0.2.0)에 문서화; pytest 커버리지 70개 테스트로 확장.
- **병렬 verifier + Constraint 우선** — 4개의 섹션 게이트 verifier가 동결된 산출물에 대해 동시에 실행; 수정은 Constraint(spec) 위반을 우선; 편집이 발생하면 모든 PASS를 폐기하고 재실행 (`docs/verification_protocol.md`).
- **STOP 신호** — verifier가 놓치는 사람 수준의 지름길을 막는 CLAUDE.md anti-rationalization 표(§10).
- **Socratic draft-plan 브레인스토밍** — `docs/draft_plan_template.md` Step 0(한 번에 한 질문; `/paper-debate`와 구분되며 토론의 R0 사전 준비로 연결), CLAUDE.md Phase 3 + Rule 8에 연결.
- **리뷰어 응답 triage** — `docs/revision_guide.md`의 코멘트별 accept/partial/rebut 입장, `[CHANGE]` + ghost-revision과 연계; Phase 8 verifier set에 Constraint 포함하도록 정렬.
- 각 `.claude/commands/*.md`에 **`use-when`** 줄 추가; TodoWrite를 비권위적(non-authoritative) QC/게이트 추적 수단으로 문서화 (CLAUDE.md Rule 4).

### v0.9.3 (2026-06-19)

**공동 저자 협업 및 멀티모델 비판적 검토**

- **`/paper-debate`** 추가 (`docs/debate_protocol.md`, `.claude/commands/paper-debate.md`) — 작성 전 Claude–Codex 공동 저자 토론(분석 계획·draft plan·논증 구조·리뷰어 응답). 합의 상한 3, 토론 로그 `review/debates/`, Codex 불가 시 Claude 단독 폴백.
- **`/critical-review`** 추가 (`docs/critical_review_protocol.md`, `.claude/commands/critical-review.md`) — 작성 후 Claude 서브에이전트·Codex·OpenRouter 모델(기본 `minimax/minimax-m3`, `z-ai/glm-5.2`)의 적대적 검토. 합의도 × 심각도로 통합·정렬, 리포트 `review/critical/`.
- `scripts/critical_review.py`(OpenRouter 호출; 모델 1개 실패는 skip, 비치명), `scripts/critical_models.txt`(모델 목록 외부화), `scripts/critical_prompts/`(스크립트·Claude 서브·Codex가 공유하는 단일 정본 프롬프트 `manuscript.txt`/`response.txt`) 추가.
- critical-review 프롬프트를 **senior reviewer / editor-in-chief 수준**으로 — 표면 결함이 아니라 설계 견고성·데이터의 결론 지지 여부·출판 가치를 묻도록 구성.
- `build_prompt`를 `str.format` 대신 `str.replace`로 변경 — 프롬프트/대상 텍스트의 중괄호(JSON·LaTeX 예시)가 치환을 깨뜨리지 않음. 회귀 테스트 추가.
- `docs/writing_guide.md`에 **AI-Draft De-bloat** 섹션 추가 — AI 흔적(피상적 `-ing` 분석·AI 어휘·신호어) 제거, 충돌 패턴(hedging/copula/passive)은 제외.
- OpenRouter 접근은 `.claude/settings.local.json`의 `OPENROUTER_API_KEY`(gitignored). 키가 없으면 OpenRouter만 skip하고 나머지 리뷰어로 진행.
- CLAUDE.md에 두 명령어 통합(Collaboration 명령어, Phase 2/3/4/8 토론, Round 6 2단 비판적 검토, File Roles, 구조 트리).

### v0.9.2 (2026-06-18)

**검증 하네스 강화** (버그 수정 + 문서 일관성)

- `check_numbers.py`: 백분율(예: 42.5%)에서 더 이상 crash하지 않음; 무관한 값(예: count 0)만으로 뒷받침되는 p-value는 거부; 천 단위 구분 기호(1,234)를 처리하고 ISO 날짜와 인라인 `code` 구간은 무시.
- `check_gate.py`: 인라인 `# ...` 주석을 제거하여 문서화된 gate 템플릿이 통과하고 round-overflow 에스컬레이션이 동작하도록 함.
- `requirements.txt`(python-docx)와 `tests/` pytest 스위트 추가 (`pytest`로 실행).
- 문서: verifier set을 Constraint / Citation / Data / Logic으로 정정 (Revision은 Revision-claims와 Response-alignment 추가); response compiler 설명 정정 (서식을 재현하며 reference .docx를 읽지 않음).

### v0.9.1 (2026-06-18)

**다국어 README 및 Author Response DOCX 완료**

- 영어, 한국어, 일본어, 중국어 README를 검증 하네스 스크립트와 DOCX response workflow 기준으로 동기화.
- Author response Markdown template과 `compile_response_docx.py` 사용법 추가.
- citation evidence, numeric grounding, phase gate, revision claim deterministic checker 문서화.
- hallucination control, redundancy control, logic check, revision alignment를 위한 LLM verifier prompt-template 문서화.

### v0.9.0 (2026-06-16)

**검증 하네스** — 각 산출 단계 뒤 인라인 produce→verify→fix→re-verify 게이트 (신규 `docs/verification_protocol.md`)

- 각 산출 단계(Phase 3/4/8) 뒤 인라인 검증 게이트 — 끝에 몰린 수동 QC를 produce→verify→fix→re-verify 루프로 전환
- Verifier 서브에이전트: Constraint(지시 준수), Citation(evidence.md 대조 인용 검증), Data(results CSV 대조 수치 검증), Logic(섹션 간 논리/중복); Revision 게이트는 Revision-claims와 Response-alignment 추가
- 자율 수정 루프(최대 2회) 후 사용자 에스컬레이션
- `[EVID:author_year]` 인용 태그 + results CSV 단일 진실 grounding
- 게이트 원장(`review/gates/`)이 `status: PASS` 기록 전 진행을 차단
- `evidence.md` 엔트리에 Source Status 필드 추가; Phase 6 QC는 최종 확인용으로 경량화

### v0.8.1 (2026-06-16)

**Response Letter 서식 규칙 정리** — `docs/revision_guide.md` 내부 버전 v0.3.0 → v0.4.0

- Response letter 서식을 최소 서식(minimal formatting) 기준으로 개편:
  - **"Comment x.x"** 와 **"Response"** 단어만 Bold, 그 외 서식 모두 제거 (heading, 색상, 들여쓰기, 표, bullet/번호 목록 사용 금지)
  - 응답서에 인용한 수정 본문은 *italic* 으로 표기
  - 응답은 번호 없이 줄글(prose)로 작성 — 감사 → 입장 → 근거 → 조치를 한 문단으로 서술
  - 수정 위치는 lead-in 방식 — 위치를 문장 앞쪽에 먼저 밝힌 뒤 수정문을 인용 (뒤에 "(See ...)" 붙이지 않음)
  - hyphen, em-dash 사용 금지
  - reviewer를 설득하는 어조
- 본문 수정 **최소 변경(minimal change) 원칙** 추가 — 각 코멘트 해소에 필요한 최소한의 문장 변경만, 장황하지 않게 concise 하게 처리
- 작성 중 체크리스트를 새 서식 규칙에 맞게 갱신

### v0.8.0 (2026-06-16)

**Style Workflow, Linting, Agent 지침 정리**

- writing-style 자료를 `knowledge/` reference evidence와 분리하여 최상위 `Style/` workflow로 정리.
- `Style/style_guide.md` 추가: style-anchor 추출 규칙, PDF-to-MD mirror 규칙, publisher generic filename 처리 규칙.
- `Style/terminology.md`를 spine surgery, trial, AI/radiomics, reporting context 전반의 preferred/forbidden terminology registry로 확장.
- `docs/drafting_protocol.md`, `docs/section_templates.md` 추가: outline → evidence-bound draft → style pass → QC 작성 순서 강제.
- `scripts/lint_manuscript.py` 추가 및 draft/table template 수정: Windows에서 `py scripts/lint_manuscript.py drafts --quiet` 통과.
- `AGENTS.MD` 추가: agent bootstrap 지침이며 `CLAUDE.md`를 authoritative source of truth로 명시.
- `.gitignore` 업데이트: 저작권 PDF와 private style-anchor summary는 local-only로 유지하고, 공개 workflow 파일과 예시는 commit 가능하게 정리.

### v0.7.1 (2026-05-15)

**용어 사전 및 Draft Plan 템플릿**

- `Style/terminology.md` 추가 — BESS/척추 수술 분야 표준 용어 registry
  - 60개 이상 항목: 수술 기법명, 기구, 결과 지표, 연구 설계, 통계, 합병증 용어
  - 흔한 실수 목록 (creatine phosphokinase vs creatinine kinase; assessor-blind vs double-blind; VAS vs NRS 등)
- `docs/draft_plan_template.md` 추가 — 10개 항목 draft plan 완성형 템플릿
  - Claim→Citation Mapping 테이블 (Introduction/Methods/Discussion)
  - 승인 체크리스트 (Phase 4 진행 전 10개 항목 완결 확인)
- CLAUDE.md Phase 1: 목표 저널 인용 형식 확인 및 Style 앵커 검토 단계 추가
- CLAUDE.md: File Roles 테이블, Phase 3 워크플로우, Quick Commands 업데이트
- 수정: `profile/journals.md` 인용 예시 오류 수정 — TSJ는 6명 후 et al. (기존 3명); BJJ는 전저자 나열, et al. 사용 안 함

### v0.7.0 (2026-05-14)

**인용 품질 및 스타일 일관성**

- `Style/` 추가 — own, landmark, target-journal 스타일 앵커
  - 2018 Spine — 우울증과 만성 요통 단면 연구 (KNHANES)
  - 2020 Spine J — 양방향 내시경 vs 현미경 감압 수술 RCT
  - 2023 Spine J — 양방향 내시경 vs 현미경 디스크 수술 RCT
  - 2024 Neurospine — BESS 안전성 프로파일: 2개 RCT 통합 분석
  - 2025 Bone Joint J — ENDOBH 다기관 RCT (6개 기관)
  - 각 파일: 전체 인용, 핵심 용어 표, methods boilerplate, 데이터 포함 핵심 주장
- CLAUDE.md Rule 8: **Claim→Citation Mapping** 추가 — draft_plan.md 10번째 필수 항목
  - 작성 전 핵심 주장 ~20개와 근거 논문 매핑
  - Introduction background (5–8), Methods rationale (2–3), Discussion comparisons (5–8)
- CLAUDE.md: Phase Completion Criteria 3→4 업데이트 (필수 항목 9→10개)
- `profile/journals.md` 추가 (로컬 전용, gitignored) — 8개 목표 저널 인용 형식 (실제 논문 검증)
  - The Spine Journal: bracket [N], 6명 후 et al.
  - Spine (Phila Pa 1976): superscript, "(Phila Pa 1976)" 필수
  - Bone Joint J: 전저자 나열, Vol-B(issue) 형식
  - Neurospine: 3명 후 et al.
  - 추가: J Neurosurg Spine, Global Spine J, Clin Orthop Relat Res, Asian Spine J
- `profile/authors.md` 5명 ORCID 추가 (로컬 전용, gitignored)

### v0.6.0 (2026-04-18)

**Writing Guide 대규모 리팩터링** — `docs/writing_guide.md` 내부 버전 v0.3.0 → v0.4.0

- CLAUDE.md(orchestrator)와 writing_guide.md(rules)의 **역할 분리**
  - CLAUDE.md "Natural Academic Writing Style" 섹션을 pointer 전용으로 축소 (~115줄 제거)
  - 모든 작문 스타일 규칙, 표, 예시를 writing_guide.md로 통합
- **신규 섹션: Style Reference Tables** (writing_guide.md)
  - Voice & Tense by Section (Abstract/Intro/Methods/Results/Discussion/Conclusion 6개 섹션)
  - Transition Words (but → nonetheless)
  - Verb Upgrades (showed → demonstrated)
  - Common Corrections (elderly → older adult 등)
  - Statistical Notation (italic *p*, 범위에 en-dash, *p* = 0.000 금지)
  - Hedging Language (Discussion용 4단계 가이드: Strong/Moderate/Weak/Very weak)
- **신규 섹션: Writing Principles (4 Pillars)** (writing_guide.md)
  - Clarity, Conciseness, Objectivity, Consistency 및 확장 예시
- **General Principles 6개 규칙 확장**:
  - 원고 본문 bold 텍스트 금지
  - 약어 1회 정의 규칙
  - 통계 방법이 아닌 임상 소견을 문장 주어로
  - 동의어 혼용 금지 (dural tear ↔ durotomy 등) + draft_plan.md 용어 선택
  - 숫자 서식 일관성 (소수점, 단위)
  - 문두 숫자 금지 (풀어 쓰거나 재구성)
- **Results 섹션**: 비유의 p-value 생략 가이드 추가 (primary outcome 예외)
- **Discussion 섹션**: 3개 신규 하위 섹션
  - 구체적 숫자/p-value 금지 (문헌 비교 예외)
  - 비유의 결과에 대한 방향성 추세 프레이밍 금지
  - 과장 금지 목록과 함께 중립적 어조
- **Tables 섹션**: 2개 신규 Tip
  - Methods Statistics와 Table 각주의 역할 분리
  - 사전 지정 민감도 분석은 Supplementary Table로

**파일 간 일관성 수정**

- CLAUDE.md Phase 2: `docs/statistical_analysis_guide.md` 명시적 참조 + `analysis_plan.md` 필수 항목(endpoint 위계, 검정법, 다중비교, 결측 처리)
- CLAUDE.md Phase 6 QC: 라운드별 책임 주석 (Claude / Dr. Editor / Dr. Statistician) + CRITICAL vs RECOMMENDED 표기
- CLAUDE.md Phase 3→4 Completion Criteria: `draft_plan.md` 9개 필수 항목 전체 나열로 확장
- `docs/revision_guide.md`: 라운드별 재수행 체크리스트와 제출 전 체크리스트를 갖춘 "QC Re-run for Revision" 섹션 신규
- `docs/evidence_guide.md`: Search Log 쿼리 예시를 실제 PubMed 문법으로 업데이트 (field tag `[tiab]`/`[MeSH]`, boolean AND/OR/NOT, 따옴표 구문)

### v0.5.2 (2026-04-15)

- 전체 문서의 파일 간 불일치 수정
- Figure 형식 워크플로우 업데이트: 초안용 PNG (300 DPI), 최종 제출용 LZW 압축 TIFF (600+ DPI), PPT/vector는 옵션
- `save_figure()` 템플릿 업데이트: `draft=True`(PNG) / `final=True`(TIFF LZW) 파라미터 분리
- CLAUDE.md revision 구조와 File Roles 표에 `review/reviewer_comments_REV{N}.md` 추가
- `analysis_plan.md` placeholder를 `[FROM CLAUDE.md]`에서 사용자 친화적인 `[연구 설계 입력]`으로 변경
- `revision_guide.md` 파일 구조를 CLAUDE.md와 정렬 (R1→REV1 네이밍 규칙)
- `qc_guide.md` QC 로그와 Final Sign-off에 Round 4 템플릿 추가
- `statistical_analysis_guide.md` figure 출력 형식에 TIFF 포함하도록 업데이트
- `checklist_guide.md` figure 제출 요건 업데이트 (TIFF LZW 600+ DPI)

### v0.5.1 (2026-04-15)

- Analysis Plan Mandatory (Critical Rule #7) 추가 — 통계 분석 실행 전 `analysis_plan.md`를 작성·승인해야 함
  - 멀티 논문 시 논문별 analysis plan (`data/paper{N}_xxx/analysis_plan.md`)
  - 필수 내용: 연구 질문, 선정/제외 기준, 변수 정의, 검정법 선택 근거, 유의수준
- Draft Plan Mandatory (Critical Rule #8) 추가 — 섹션 작성 전 `drafts/draft_plan.md`를 작성·승인해야 함
  - 필수 내용: key message, 톤/voice, 필수 참고문헌, 근거 갭, table/figure 계획, introduction/discussion 개요, limitation point
  - 멀티 논문 시 논문별 draft plan
- Model Selection by Phase (Critical Rule #9) 추가 — 비용 효율적 모델 가이드
  - Opus 권장: Analysis Plan, Draft Plan, Revision (전략적 단계)
  - Sonnet 기본 + Opus 선택: 초안 작성, Style Polish, QC (계획 기반 실행)
  - Draft Plan 작성 시 Plan Mode(`/plan`) 권장
- 워크플로우 단계 재번호 (7 → 8단계): Analysis와 Drafting 사이에 Phase 3 (Draft Plan) 추가
- Phase Completion Criteria에 draft_plan.md 승인 게이트 업데이트

### v0.5.0 (2026-04-14)

- QC Round 2 (참고문헌 검증)에 4개 신규 서브체크 강화:
  - 2.5 Placeholder Reference Detection — 가짜/임시 인용 감지 ([ref1], [TBD], [X] 등)
  - 2.6 Order of Appearance Check — Vancouver 스타일 순서대로 인용 번호 부여 검증
  - 2.7 Reference Format Consistency — 전체 참고문헌의 서지 형식 통일성 점검
  - 2.8 Citation Distribution Check — 섹션별 인용 균형, 자기인용 비율, 최신성
- Reference List Integrity (2.4) 강화 — 번호 연속성 및 중복 번호 점검 추가
- QC 로그 템플릿에 Round 2 강화 섹션 업데이트
- 파일 버전 관리 규칙 (Critical Rule #5) 추가 — 날짜 기본(`_YYMMDD`), `_v1`, `_REV1`, `_FINAL`
- 멀티 논문 조직화 (Critical Rule #6) 추가 — data, results, drafts, output, review의 논문별 서브폴더
- 멀티 논문 프로젝트 구조 다이어그램 추가 (docs/knowledge/scripts 공유, 논문별 폴더 분리)
- Revision 폴더 구조 추가 — `drafts/revision/REV{N}/`, `output/revision/REV{N}/`
- Recommended Workflow에 Phase 7 (Revision)과 QC 재수행 요건 추가
- Phase Completion Criteria에 Submit → Revision 경로 업데이트
- File Roles 표에 revision 폴더 엔트리 업데이트

### v0.4.0 (2026-04-09)

- `docs/revision_guide.md` 추가 — 리뷰어 응답 및 개정 가이드
- `docs/figure_guide.md` 추가 — 출판 품질 figure 생성 가이드
- `drafts/00_cover_letter.md` 추가 — 간결한 cover letter 템플릿
- CLAUDE.md 업데이트: 프로젝트 구조, file roles, revision 및 figure용 Quick Commands
- 프로젝트 구조에서 Spine GraphRAG 프로젝트 고유 참조 제거

### v0.3.0 (2026-03-09)

- `docs/statistical_analysis_guide.md` 대규모 재작성 (v0.2.1 → v0.3.0)
  - Statistical Parsimony, Analysis Hierarchy, Clinical Significance, Subgroup Analysis, Sensitivity Analysis
  - Methods Statistical Section Checklist (ICMJE/SAMPL 기준 10개 필수 항목)
- 통계 일관성을 위해 `docs/writing_guide.md`, `docs/expert_roles.md`, `docs/qc_guide.md` 업데이트

### v0.2.5 (2026-03-09)

- `scripts/search_pubmed.py` 추가 — NCBI E-utilities API 사용 PubMed 검색 도구 (MCP 불필요, 외부 패키지 불필요)
- 슬래시 명령어 추가: `/search-evidence [query]`, `/import-doi [doi]`

### v0.2.4 (2026-03-04)

- LF 줄바꿈 정규화를 위한 `.gitattributes` 추가
- `.DS_Store`, 로컬 설정, IDE 설정에 대한 `.gitignore` 규칙 추가

### v0.2.3 (2026-02-15)

- DOCX 변환 규칙을 위한 `docs/docx_guide.md` 추가
- 날짜 접미사 output 파일, title page와 table DOCX 파일 분리

### v0.2.2 (2026-02-10)

- evidence registry에서 evidence guide 분리
- 상세 요약 지침을 갖춘 `docs/evidence_guide.md` 추가

### v0.2.1 (2026-02-07)

- 다양한 구조적 수정 및 템플릿 개선

### v0.2 (2026-02-03)

- Statistical Analysis Guide 추가
- Table/Figure/Results 중복 방지 규칙 추가

### v0.1 (초기)

- 기본 프로젝트 구조
- Writing guide, expert roles, checklists, QC guide

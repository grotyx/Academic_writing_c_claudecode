🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# Claude를 활용한 의학 학술 논문 작성 워크플로우

Claude AI를 활용한 의학 학술 논문 작성을 위한 체계적인 워크플로우 시스템입니다.

## 버전

**v0.8.1** (2026-06-16)

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
- **Draft plan 템플릿** (`docs/draft_plan_template.md`) — 10개 항목 템플릿 + claim→citation 테이블 + 승인 체크리스트
- **PubMed 검색 도구** — 내장 Python 스크립트 (MCP 및 외부 패키지 불필요)
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
│   ├── statistical_analysis_guide.md  # 통계 분석 가이드
│   ├── evidence_guide.md         # 근거 문헌 작성 가이드
│   ├── revision_guide.md         # 리뷰어 응답 가이드
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
│   └── search_pubmed.py          # PubMed 검색 도구 (외부 의존성 없음)
├── results/                      # 분석 결과
├── drafts/                       # 원고 섹션, 테이블, 그림
│   ├── draft_plan.md             # 원고 구성 계획 (작성 전 필수)
│   ├── table_*.md
│   └── figures/
├── review/                       # QC 문서
│   └── qc_log.md
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
6. **품질 관리**: 제출 전 최소 3라운드 QC 수행 (6라운드 권장)
7. **최종화**: 원고를 DOCX로 컴파일 (`docs/docx_guide.md` 참조)

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
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | 통계 분석 가이드 (절제 원칙, MCID, 하위군 분석) |
| [docs/evidence_guide.md](docs/evidence_guide.md) | 근거 문헌 작성 가이드 (형식, 요약 방법, 워크플로우) |
| [docs/revision_guide.md](docs/revision_guide.md) | 리뷰어 응답 가이드 (응답서 작성, 외교적 표현, QC 재수행 체크리스트) |
| [docs/figure_guide.md](docs/figure_guide.md) | Figure 생성 가이드 (DPI, 팔레트, Python 템플릿) |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 변환 가이드 (서식, 테이블 스타일, 네이밍 규칙) |
| [docs/draft_plan_template.md](docs/draft_plan_template.md) | Draft plan 템플릿 — 10개 항목 + claim→citation 테이블 + 승인 체크리스트 |
| [Style/style_guide.md](Style/style_guide.md) | 스타일 앵커 워크플로우, 추출 프레임워크, PDF-to-MD 미러 규칙 |
| [Style/terminology.md](Style/terminology.md) | preferred/forbidden 용어 registry, 정의, context |
| [Style/own/example_YYYY_Journal_keyword.md](Style/own/example_YYYY_Journal_keyword.md) | 본인 논문 스타일 앵커 템플릿 |
| [scripts/lint_manuscript.py](scripts/lint_manuscript.py) | 용어, placeholder, 과장 표현, 섹션별 위반 점검 lint 스크립트 |
| [scripts/search_pubmed.py](scripts/search_pubmed.py) | PubMed 검색 스크립트 (NCBI E-utilities, 외부 패키지 불필요) |

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

### v0.8.1 (2026-06-16)

**Response Letter 서식 규칙 정리** — `docs/revision_guide.md` 내부 버전 v0.3.0 → v0.4.0

- Response letter 서식을 최소 서식(minimal formatting) 기준으로 개편:
  - **"Comment x.x"** 와 **"Response"** 단어만 Bold, 그 외 서식 모두 제거 (heading, 색상, 들여쓰기, 표, bullet/번호 목록 사용 금지)
  - 응답서에 인용한 수정 본문은 *italic* 으로 표기
  - 응답은 번호 없이 줄글(prose)로 작성 — 감사 → 입장 → 근거 → 조치를 한 문단으로 서술
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

- CLAUDE.md와 writing_guide.md 역할 분리 (orchestrator vs rules)
- Style Reference Tables 신규 추가 (Voice/Tense, Transition, Verb Upgrades, Common Corrections, Statistical Notation, Hedging)
- Writing Principles (4 Pillars) 신규 추가 (Clarity/Conciseness/Objectivity/Consistency)
- General Principles 6개 규칙 확장
- Results/Discussion/Tables 섹션 가이드 강화
- 전 파일 일관성 수정 (CLAUDE.md, revision_guide.md, evidence_guide.md)

### v0.5.2 (2026-04-15)
- 전 파일 교차 일관성 수정
- Figure 형식 워크플로우 업데이트 (PNG 초안 300 DPI / TIFF LZW 최종 600+ DPI)

### v0.5.1 (2026-04-15)
- Analysis Plan Mandatory (Rule #7) 추가
- Draft Plan Mandatory (Rule #8) 추가
- Model Selection by Phase (Rule #9) 추가
- 워크플로우 8단계로 재편 (Phase 3: Draft Plan 추가)

### v0.5.0 (2026-04-14)
- QC Round 2 강화 (4개 새 서브체크: placeholder, 등장순, 형식 일관성, 배포)
- 파일 버전 관리 규칙 (Rule #5) 추가
- 멀티 논문 조직화 규칙 (Rule #6) 추가
- Revision 폴더 구조 추가

### v0.4.0 (2026-04-09)
- `docs/revision_guide.md` 추가 — 리뷰어 응답 및 개정 가이드
- `docs/figure_guide.md` 추가 — 출판용 figure 생성 가이드

### v0.3.0 (2026-03-09)
- `docs/statistical_analysis_guide.md` 대규모 개정 (절제 원칙, 위계, 임상적 유의성, 하위군 분석)

### v0.2.5 (2026-03-09)
- `scripts/search_pubmed.py` 추가 (MCP 없는 PubMed 검색)
- 슬래시 명령어 추가: `/search-evidence`, `/import-doi`

### v0.2.4 ~ v0.2 (2026-02-03 ~ 2026-03-04)
- DOCX 가이드, 근거 문헌 가이드, 통계 분석 가이드 등 기반 문서 구축

### v0.1 (초기)
- 기본 프로젝트 구조, Writing guide, Expert roles, Checklists, QC guide

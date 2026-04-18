🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# Claude를 활용한 의학 학술 논문 작성 워크플로우

Claude AI를 활용한 의학 학술 논문 작성을 위한 체계적인 워크플로우 시스템입니다.

## 버전

**v0.6.0** (2026-04-18)

---

## 개요

이 프로젝트는 Claude AI의 도움을 받아 의학 학술 논문을 작성하기 위한 종합 프레임워크를 제공합니다:

- **체계적인 프로젝트 구조** — 원고, 데이터, 참고문헌 관리
- **멀티 논문 프로젝트 지원** — 논문별 서브폴더 정리
- **파일 버전 관리 시스템** — 날짜 기본, _v1, _REV1 스타일
- **Revision 워크플로우** — 전용 revision 폴더 및 파일 네이밍
- **전문가 팀 시뮬레이션** — 임상 전문가, 방법론 전문가, 통계학자, 편집자
- **통계 분석 워크플로우** — Python 스크립트 자동 생성
- **품질 관리 절차** — 최소 3라운드 검증 (6라운드 권장)
- **연구 유형별 체크리스트** — STROBE, CONSORT, PRISMA, CARE 등
- **PubMed 검색 도구** — 내장 Python 스크립트 (MCP 및 외부 패키지 불필요)
- **슬래시 명령어** — 근거 문헌 등록 (`/search-evidence`, `/import-doi`)

---

## 프로젝트 구조

```
project/
├── CLAUDE.md                     # 핵심 규칙 및 설정
├── README.md                     # 영문 README
├── docs/                         # 참조 가이드
│   ├── writing_guide.md          # 섹션별 작성 가이드
│   ├── expert_roles.md           # 전문가 팀 역할 및 책임
│   ├── checklist_guide.md        # 연구 유형별 체크리스트
│   ├── qc_guide.md               # 품질 관리 절차
│   ├── statistical_analysis_guide.md  # 통계 분석 가이드
│   ├── evidence_guide.md         # 근거 문헌 작성 가이드
│   ├── revision_guide.md        # 리뷰어 응답 가이드
│   ├── figure_guide.md          # Figure 생성 가이드
│   └── docx_guide.md            # DOCX 변환 가이드
├── knowledge/                    # 참고 자료
│   ├── evidence.md               # 참고문헌 요약 정리 자료집
│   ├── pdf/                      # 원본 PDF 파일
│   └── summaries/                # 개별 논문 상세 요약
├── data/                         # 통계 분석
│   ├── raw_data.csv              # 원본 데이터셋
│   ├── analysis_plan.md          # 분석 계획 (분석 전 필수 작성)
│   └── py/                       # Python 분석 스크립트
├── scripts/                      # 유틸리티 스크립트
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

1. **설정**: `CLAUDE.md`에 연구 주제, 목표 저널, 연구 설계를 입력합니다
2. **참고문헌**: `/search-evidence [검색어]` 또는 `python3 scripts/search_pubmed.py`로 PubMed를 검색하고 `knowledge/evidence.md`에 등록합니다
3. **데이터 분석**: `data/` 폴더에 데이터를 배치 → `analysis_plan.md` 작성 (필수) → 통계 분석 실행
4. **원고 계획**: `drafts/draft_plan.md`에 핵심 메시지, 논조, 필수 참고문헌, 개요 작성 (Opus 권장)
5. **초안 작성**: 권장 순서에 따라 섹션을 작성합니다 (Sonnet 가능, draft plan이 충실하면 OK)
6. **품질 관리**: 제출 전 최소 3라운드의 QC를 수행합니다 (6라운드 권장)
7. **최종화**: 원고를 DOCX로 컴파일합니다 (`docs/docx_guide.md` 참조)

---

## 주요 기능

### 전문가 팀 시뮬레이션
- **Dr. Researcher A**: 임상적 관점 (Introduction, Discussion)
- **Dr. Researcher B**: 방법론 (Methods, Results, Tables)
- **Dr. Statistician**: 통계 검증, 절제 원칙, MCID/NNT 평가
- **Dr. Editor**: 최종 교정, 일관성 검토

### 작성 전 필수 계획 (Planning Before Writing)

- **분석 계획** (`data/analysis_plan.md`): 통계 분석 전 필수 — 연구 질문, 평가 변수, 검정법 선택 정의
- **원고 계획** (`drafts/draft_plan.md`): 섹션 작성 전 필수 — 핵심 메시지, 논조/어조, 필수 참고문헌, 근거 갭, Table/Figure 계획, 섹션별 개요
- 두 계획 모두 사용자 승인 후 다음 단계 진행
- 멀티 논문 시 논문별 개별 계획 작성

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
| [docs/writing_guide.md](docs/writing_guide.md) | 섹션별 작성 지침 |
| [docs/expert_roles.md](docs/expert_roles.md) | 전문가 팀 설명 |
| [docs/checklist_guide.md](docs/checklist_guide.md) | STROBE, CONSORT, PRISMA, CARE 체크리스트 |
| [docs/qc_guide.md](docs/qc_guide.md) | 품질 관리 절차 (6라운드) |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | 통계 분석 가이드 (절제 원칙, MCID, 하위군 분석) |
| [docs/evidence_guide.md](docs/evidence_guide.md) | 근거 문헌 작성 가이드 (형식, 요약 방법, 워크플로우) |
| [docs/revision_guide.md](docs/revision_guide.md) | 리뷰어 응답 가이드 (응답서 작성, 외교적 표현) |
| [docs/figure_guide.md](docs/figure_guide.md) | Figure 생성 가이드 (DPI, 팔레트, Python 템플릿) |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 변환 가이드 (서식, 테이블 스타일, 네이밍 규칙) |
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

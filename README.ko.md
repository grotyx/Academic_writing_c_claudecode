🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# Claude를 활용한 의학 학술논문 작성 워크플로우

Claude AI를 활용한 의학 학술논문 작성을 위한 체계적 워크플로우 시스템입니다.

## 버전

**v0.3.0** (2026-03-09)

---

## 개요

이 프로젝트는 Claude AI를 활용한 의학 학술논문 작성을 위한 포괄적 프레임워크를 제공합니다:

- **체계적 프로젝트 구조** — 원고, 데이터, 참고문헌 관리
- **전문가 팀 시뮬레이션** — 임상 전문가, 방법론 전문가, 통계학자, 편집자
- **통계 분석 워크플로우** — Python 스크립트 자동 생성
- **품질 관리 절차** — 최소 3라운드 (6라운드 권장) 검증
- **연구유형별 체크리스트** — STROBE, CONSORT, PRISMA, CARE 등
- **PubMed 검색 도구** — 내장 Python 스크립트 (MCP 및 외부 패키지 불필요)
- **슬래시 명령어** — 근거 문헌 등록 (`/search-evidence`, `/import-doi`)

---

## 프로젝트 구조

```text
project/
├── CLAUDE.md                     # 핵심 규칙 및 설정
├── README.md                     # 영문 README
├── docs/                         # 참조 가이드
│   ├── writing_guide.md          # 섹션별 작성 가이드
│   ├── expert_roles.md           # 전문가 팀 역할 및 책임
│   ├── checklist_guide.md        # 연구유형별 체크리스트
│   ├── qc_guide.md               # 품질 관리 절차
│   ├── statistical_analysis_guide.md  # 통계 분석 가이드
│   ├── evidence_guide.md         # Evidence 작성 가이드
│   └── docx_guide.md            # DOCX 변환 가이드
├── knowledge/                    # 참고 자료
│   ├── evidence.md               # 참고문헌 요약 정리 자료집
│   ├── pdf/                      # 원본 PDF 파일
│   └── summaries/                # 개별 논문 상세 요약
├── data/                         # 통계 분석
│   ├── raw_data.csv              # 원본 데이터셋
│   ├── analysis_plan.md          # 자동 생성 분석 계획
│   └── py/                       # Python 분석 스크립트
├── scripts/                      # 유틸리티 스크립트
│   └── search_pubmed.py          # PubMed 검색 도구 (외부 패키지 불필요)
├── results/                      # 분석 결과물
├── drafts/                       # 원고 섹션, 테이블 및 그림
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

1. **설정**: `CLAUDE.md`에 연구 주제, 목표 저널, 연구 설계 입력
2. **참고문헌**: `/search-evidence [검색어]` 또는 `python3 scripts/search_pubmed.py`로 PubMed 검색 및 `knowledge/evidence.md`에 등록
3. **데이터 분석**: `data/` 폴더에 데이터 배치 후 통계 분석 실행
4. **초안 작성**: 권장 순서로 섹션 작성 (Methods → Results → Introduction → Discussion)
5. **품질 관리**: 제출 전 최소 3라운드 QC 수행 (6라운드 권장)
6. **최종 작업**: 원고를 DOCX로 컴파일 (`docs/docx_guide.md` 참조)

---

## 주요 기능

### 전문가 팀 시뮬레이션

- **Dr. Researcher A**: 임상 관점 (Introduction, Discussion)
- **Dr. Researcher B**: 방법론 (Methods, Results, Tables)
- **Dr. Statistician**: 통계 검증
- **Dr. Editor**: 최종 교정, 일관성 검토

### 중복 방지

- 삼중 중복 방지 (Results 본문 + Table + Figure)
- Table vs Figure 결정을 위한 명확한 가이드라인
- 표준 테이블 구조 (Table 1: 인구통계, Table 2: 주요 결과)

### PubMed 검색 도구

MCP 없이 사용 가능한 내장 Python 스크립트 (`scripts/search_pubmed.py`):

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

| 문서 | 용도 |
| ---- | ---- |
| [CLAUDE.md](CLAUDE.md) | 핵심 규칙 및 프로젝트 설정 |
| [docs/writing_guide.md](docs/writing_guide.md) | 섹션별 작성 지침 |
| [docs/expert_roles.md](docs/expert_roles.md) | 전문가 팀 설명 |
| [docs/checklist_guide.md](docs/checklist_guide.md) | STROBE, CONSORT, PRISMA, CARE 체크리스트 |
| [docs/qc_guide.md](docs/qc_guide.md) | 품질 관리 절차 (6라운드) |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | 통계 분석 워크플로우 |
| [docs/evidence_guide.md](docs/evidence_guide.md) | Evidence 작성 가이드 (형식, 요약 방법, 워크플로우) |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 변환 가이드 (서식, 테이블 스타일, 네이밍 규칙) |
| [scripts/search_pubmed.py](scripts/search_pubmed.py) | PubMed 검색 스크립트 (NCBI E-utilities, 외부 패키지 불필요) |

---

## 요구사항

- Claude AI (Claude Code CLI 또는 VSCode 확장)
- Python 3.x (통계 분석 및 PubMed 검색용)
- Python 패키지 (통계 분석): pandas, numpy, scipy, statsmodels, python-docx
- PubMed 검색 스크립트 (`scripts/search_pubmed.py`)는 Python 표준 라이브러리만 사용 (추가 패키지 불필요)

---

## 저자

**박상민 교수, 의학박사**

서울대학교병원 분당병원 정형외과,
서울대학교 의과대학

<https://sangmin.me/>

---

## 라이선스

이 저작물은 **크리에이티브 커먼즈 저작자표시 4.0 국제 라이선스 (CC BY 4.0)** 하에 제공됩니다.

Copyright (c) 2026 박상민, 서울대학교병원 분당병원

### 이용 허락 사항

- **공유** — 어떤 매체나 형식으로든 자료를 복사하고 재배포할 수 있습니다
- **변경** — 어떤 목적으로든 자료를 리믹스, 변형, 재가공할 수 있습니다

### 이용 조건

- **저작자표시** — 적절한 출처를 밝히고, 라이선스 링크를 제공하며, 변경사항이 있는 경우 이를 표시해야 합니다

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

라이선스 전문: <https://creativecommons.org/licenses/by/4.0/legalcode>

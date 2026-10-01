<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-dark.png">
    <img src="assets/logo.png" width="220" alt="manuwright, the careful senior author">
  </picture>
</p>

<h1 align="center">manuwright</h1>

<p align="center">
  <em>확인하지 않은 논문은 인용하게 두지 않는 사람.</em>
</p>

<p align="center">
  <a href="https://github.com/grotyx/Academic_writing_c_claudecode/actions/workflows/tests.yml"><img src="https://img.shields.io/github/actions/workflow/status/grotyx/Academic_writing_c_claudecode/tests.yml?style=flat-square&color=111111&label=tests" alt="Tests"></a>
  <img src="https://img.shields.io/github/v/tag/grotyx/Academic_writing_c_claudecode?style=flat-square&color=111111&label=release" alt="Release">
  <img src="https://img.shields.io/badge/python-3.10%2B-111111?style=flat-square" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/works%20with-5%20agents-111111?style=flat-square" alt="Works with 5 agents">
  <img src="https://img.shields.io/badge/license-CC%20BY%204.0-111111?style=flat-square" alt="CC BY 4.0">
</p>

<p align="center">
  <strong>계획 먼저 &middot; 모든 인용은 등록된 근거로 &middot; 모든 수치는 데이터에서 &middot; 제출 전 게이트</strong><br>
  <sub>AI 에이전트용 의학 논문 작성 워크플로. Claude Code, Codex, Antigravity, opencode, Muse 가 검증 엔진 하나를 함께 씀.</sub>
</p>

<p align="center">
  <sub><a href="README.md">English</a> &middot; <a href="README.ja.md">日本語</a> &middot; <a href="README.zh.md">中文</a></sub>
</p>

---

어느 연구실에나 한 명씩 있는 그 선배 저자를 떠올려 보자. 초고를 펜을 쥔 채로 읽는다. 한 문장에 동그라미를 치고 조용히 묻는다. *"이건 어느 논문에 나와?"* 숫자에 동그라미를 친다. *"어느 표야?"* 그가 서명하기 전에는 아무것도 연구실 밖으로 나가지 않는다.

manuwright 는 그 사람을 AI 에이전트 안에 넣는다.

## 쓰기 전 / 쓴 후

계획이 정해지기도 전에 에이전트에게 Results 를 써 달라고 한다.

manuwright 가 없으면 에이전트는 매끄러운 문장을 쓰고, 그럴듯하지만 존재하지 않는 논문을 인용하고, 읽어 본 적 없는 평균값을 반올림해 넣는다.

manuwright 가 있으면:

```text
BLOCKED by workflow gate (Rule 8): drafts/draft_plan.md has not been approved.
Create the draft plan first, get author approval, then draft sections.
```

계획이 승인된 뒤에도 모든 주장은 검사기를 통과해야 한다.

```text
$ manuwright citations drafts/03_introduction.md
GATE FAIL
citation: EVID:smith_2021
reason: citation id not found in knowledge/evidence.md

$ manuwright numbers drafts/05_results.md
GATE FAIL
number: 54.3
reason: number not found in results CSV files
```

## 동작 방식

```text
 evidence.md   ┐
 results/*.csv ┼──▶ approved plan ──▶ draft ──▶ gates ──▶ QC ×3 ──▶ signed build
 style spec    ┘                                  ├ citations
                          ▲                       ├ numbers
                    hooks block                   └ semantic review (independent)
                    writes without it
```

| 보장하는 것 | 강제하는 곳 |
|---|---|
| 승인된 draft plan 전에는 섹션을, 승인된 analysis plan 전에는 분석 코드를 쓸 수 없음 | 에이전트 hook (Claude Code, Codex) 과 `manuwright verify` |
| 모든 `[EVID:id]` 가 `knowledge/evidence.md` 에 검증된 출처로 등록돼 있음 | `manuwright citations` |
| 보고하는 모든 수치가 `results/*.csv` 에 있음 | `manuwright numbers` 와 result binding |
| 출처·계획·엔진이 바뀌면 리뷰가 stale 이 됨 | 모든 기록에 sha256 스냅샷 |
| 제출에는 사람의 서명, AI 사용 공개, 완료된 체크리스트가 필요함 | `manuwright verify --profile submission` |

엔진은 승인이나 리뷰를 만들어 내지 않는다. 사람이 내린 결정을 기록할 뿐이다.

## 설치

방법은 두 가지, 엔진은 하나. 하나를 고르면 된다.

**A. 템플릿 (설치 없음).** 저장소를 clone 해서 그 안에서 쓴다. Claude Code 는 `.claude/` 를, Codex 와 Gemini 는 `AGENTS.md` 와 `GEMINI.md` 를 읽는다.

```sh
git clone https://github.com/grotyx/Academic_writing_c_claudecode my-paper
```

**B. 설치형 엔진.** 모든 논문에 CLI 하나, 그리고 에이전트별 어댑터.

```sh
uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@v1.8.19
manuwright agents install --dry-run     # preview, then run without --dry-run
manuwright setup                        # models, reviewers, Word style, updates, Obsidian
manuwright init my-paper
manuwright target                      # inside the paper: target journal + Word style
```

| 에이전트 | `manuwright agents install` 이 추가하는 것 | plan-first 강제 |
|---|---|---|
| Claude Code | plugin `manuwright@manuwright`: skill + hook | hook 이 쓰기를 막음 |
| Codex | plugin `manuwright@manuwright`: skill + hook (처음 한 번 신뢰) | hook 이 `apply_patch` 를 막음 |
| Antigravity (`agy`) | skill 이 든 plugin | `manuwright verify` |
| opencode | `~/.config/opencode/skills` 의 skill | `manuwright verify` |
| Muse | 사용자 skill | `manuwright verify` |

**업데이트.** `manuwright update` 가 최신 릴리스를 설치하고, `manuwright agents update` 가 어댑터를 갱신한다. `manuwright config set auto-update on` 으로 patch 자동 업데이트를 켤 수 있다. 하루 한 번 확인하고, 논문의 현재 리뷰를 무효로 만들 업데이트는 적용하지 않는다. 템플릿 사용자는 `git pull`, 또는 [이전 가이드](docs/migration_guide.md) 참고.

**삭제.** `claude plugin uninstall manuwright@manuwright`, `codex plugin remove manuwright@manuwright`, `agy plugin uninstall manuwright`, `muse skills uninstall manuwright`, 그다음 `uv tool uninstall manuwright`.

## 명령

| 명령 | 하는 일 |
|---|---|
| `manuwright init [folder]` | 논문 폴더 시작: manifest, 계획 템플릿(미승인), 근거 목록, 에이전트 규칙 |
| `manuwright rules [keyword]` | 워크플로 규칙 전체 또는 한 절 출력 |
| `manuwright verify --project project.json --profile draft\|revision\|submission` | 그 단계의 모든 검사 실행 |
| `manuwright citations \| numbers \| abstract \| crossrefs \| lint ...` | 파일 하나에 검사기 하나 실행 |
| `manuwright gate` / `verify-all` | 단계 게이트 기록을 실제 검사 결과와 대조 |
| `manuwright search "<query>"` | PubMed 검색 후 근거 항목 출력 |
| `manuwright packet` / `build` | 로컬 리뷰 packet / 게이트를 통과해야 되는 DOCX 빌드 |
| `manuwright update`, `agents install\|update`, `config` | 릴리스, 에이전트 어댑터, 자동 업데이트, main 모델과 검토자 모델 |
| `manuwright obsidian status\|connect`, `evidence import-obsidian <citekey>` | 선택(권장): Obsidian "[Academic Paper Citation Manager](https://github.com/grotyx/rag-obsidian)" 라이브러리를 모든 에이전트에 연결; vault 참고문헌을 `evidence.md` 로 가져오기 |

템플릿에는 Claude Code 용 slash command 도 들어 있다: `/verify`, `/search-evidence`, `/import-doi`, `/style-pass`, `/verify-claims`, `/suggest-citation`, `/cite-stance`, `/evidence-table`, `/paper-debate`, `/critical-review`, `/editor-review`.

## 내 Obsidian 라이브러리 (선택, 권장)

참고문헌을 Obsidian에서 관리한다면 같은 저자가 만든 플러그인 **[Academic Paper Citation Manager](https://github.com/grotyx/rag-obsidian)**([Obsidian 커뮤니티 플러그인](https://community.obsidian.md/plugins/academic-paper-citation-manager))를 함께 쓰세요. PubMed 가져오기, AI 요약, MeSH 태그, `[@citekey]` 인용을 제공하고, 노트 자체가 데이터베이스입니다. 이 플러그인의 MCP 서버로 모든 에이전트가 원고를 쓰면서 라이브러리를 검색합니다.

```sh
manuwright obsidian install          # plugin into a vault, offers MCP access (skip if installed)
manuwright obsidian connect          # register its MCP server (rag-obsidian) with each agent
manuwright evidence import-obsidian <citekey>
```

볼트는 문헌을 찾는 곳이고, 인용할 수 있는 것은 `knowledge/evidence.md`에 등록된 항목뿐입니다. 가져온 노트는 CSL 필드가 인용 정보가, 플러그인의 AI 요약이 요약 칸이 되며, `[EVID:<citekey>]`로 인용하고, 전문을 읽기 전까지 `abstract-only`로 남습니다. 에이전트가 라이브러리를 쓰는 동안 Obsidian을 열어 두고 MCP 접근을 켜 두세요. 따라 하기: [설명서 3b절](docs/manual.ko.md#3b-내-obsidian-라이브러리-선택-권장).

<p align="center"><img src="docs/images/manual/43_obsidian_import_evidence.png" width="720" alt="Obsidian 라이브러리의 참고문헌을 evidence.md로 가져오기"></p>

## 워크플로

| 단계 | 사람과 에이전트가 하는 일 | 게이트 |
|---|---|---|
| 1 준비 | 주제, 저널, 연구 설계; 참고문헌 등록 | `evidence.md` 에 출처 검증 |
| 2 분석 | 분석 계획, 스크립트, 결과 CSV, 표 | 스크립트 전에 계획 승인 |
| 3 원고 계획 | 핵심 메시지, 주장-인용 매핑, 개요 | 섹션 전에 계획 승인 |
| 4 초고 | Methods, Results, Introduction, Discussion, Conclusion, Abstract | 섹션마다 인용·수치·논리·제약 검사 |
| 5 문체 | 내 논문 exemplar 기반 저널 문체 | 측정 가능한 문체 지표 |
| 6 QC | 최소 3회; 체크리스트 (CONSORT, STROBE, PRISMA, CARE) | `review/qc_log.md` 에 기록 |
| 7 마무리 | DOCX 원고, title page, 표 | submission profile PASS + 사람의 서명 |
| 8 수정 | 응답서, 수정 섹션 | 모든 변경 주장과 모든 리뷰어 코멘트 검사 |

전체 규칙: [WORKFLOW.md](WORKFLOW.md). 예전 README 에 있던 내용(기능, 프로젝트 구조, 문서 목록): [docs/guide/overview.ko.md](docs/guide/overview.ko.md).

## FAQ

**논문을 대신 써 주나?** 에이전트가 정해진 규칙 안에서 초고를 쓰도록 돕는다. 메시지를 정하고, 계획을 승인하고, 서명하는 것은 저자다. 사람과 공동저자의 검토는 계속 필수다.

**내 컴퓨터 밖으로 나가는 게 있나?** 검사는 모두 로컬에서 돈다. 다른 모델에 글을 보내는 일(외부 리뷰, PubMed 검색)은 그 명령을 직접 실행할 때만 일어난다.

**실제 원고는 어디에 두나?** 비공개 폴더나 저장소에 둔다. 이 템플릿의 공개 clone 에는 두지 않는다. `manuwright init` 이 그런 폴더를 만들어 준다.

**왜 "manuwright" 인가?** manuscript + *wright*. wright 는 "만드는 사람"이라는 옛말이다 (playwright 극작가, shipwright 조선공). 원고를 꼼꼼하게 짓는 사람.

## 문서

[사용자 매뉴얼](docs/manual.ko.md) &middot; [Harness 가이드](docs/harness_guide.md) &middot; [Workflow reference](docs/workflow_reference.md) &middot; [검증 프로토콜](docs/verification_protocol.md) &middot; [작성 가이드](docs/writing_guide.md) &middot; [QC 가이드](docs/qc_guide.md) &middot; [배포 설계](docs/distribution_plan.md) &middot; [변경 이력](CHANGELOG.ko.md)

## 저자

**박상민 교수, M.D., Ph.D.**, 정형외과학교실, 분당서울대학교병원, 서울대학교 의과대학. <https://sangmin.me/>

## 라이선스

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Copyright (c) 2026 박상민, 서울대학교 분당서울대학교병원. 출처를 밝히면 어떤 목적으로든 공유·수정할 수 있다.

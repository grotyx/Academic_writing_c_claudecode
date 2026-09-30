# 변경 이력

### v1.8.5 (260930)

합성 임상시험 데이터로 끝까지 돌려 본 시험(init, 분석 계획, 승인, 분석, 표, 검사)에서 발견:

- **템플릿 hook 이 `cd` 후 조용히 꺼지던 문제**: `.claude/settings.json` 이 `sh scripts/hooks/run.sh ...` 를 상대 경로로 불렀음. 에이전트가 셸에서 폴더를 옮기면 모든 hook 이 exit 127 로 실패했고, Claude Code 는 이를 차단이 아닌 오류로 처리해서 plan-first 쓰기가 허용됐음. hook 명령을 `$CLAUDE_PROJECT_DIR` 기준으로 고정. 관계없는 폴더에서 gate 를 돌리는 회귀 테스트 추가.
- `verify` 가 "one or more declared artifacts are missing" 대신 없는 파일 이름을 알려 줌.
- 같은 시험에서 확인: 계획 승인 전에는 분석 스크립트 차단, `record-approval` 후 허용. draft plan 미승인 상태에서 Results 섹션 차단. 표 수치 50개가 결과 CSV 와 일치. 틀린 평균(61.2)을 가장 가까운 실제 값(60.4)과 함께 잡아냄.
- 403 tests 통과.

### v1.8.4 (260930)

- **새 README**: 인기 에이전트 도구 저장소 형식으로 개편. 로고, 한 줄 소개, 배지, 쓰기 전/후, 동작 방식, 에이전트별 설치, 명령, 워크플로, FAQ (영·한·일·중). 예전 README 내용은 그대로 `docs/guide/overview*.md` 로, 변경 이력은 `CHANGELOG*.md` 로 옮김.
- **로고**: 체크 표시로 파낸 만년필 촉(장인 + 검증). Antigravity 로 제작. `assets/logo.png`(기본), `assets/logo-alt.png`(펜촉에서 체크가 뻗어 나가는 버전). 각각 투명 다크 모드 버전과 원본 포함.
- WORKFLOW Rule 12 가 버전·변경 이력 갱신 대상을 plugin manifest, README 설치 태그, `CHANGELOG*.md` 로 가리키도록 수정.

### v1.8.3 (260930)

- 테스트 격리: 설치형 테스트가 임시 프로젝트를 실제 `~/.manuwright/projects.json` 에 등록하고 있었음. 이제 임시 `MANUWRIGHT_HOME` 을 씀. 엔진 변경 없음.

### v1.8.2 (260930)

- **`paperflow` 를 `manuwright` 로 이름 변경** ("manuscript" + "-wright", playwright 처럼 "만드는 장인"). `paperflow` 는 PyPI 와 GitHub 에 이미 있는 이름이었음. 명령 `manuwright`, 패키지 `manuwright/`, plugin `manuwright@manuwright`, skill `manuwright`·`manuwright-verify`, 설정 폴더 `~/.manuwright`, 환경변수 `MANUWRIGHT_*`. 아래 이전 항목은 릴리스 당시 이름을 그대로 둠.
- v1.8.0/1.8.1 에서 올리는 방법: 먼저 기존 설치를 제거(각 에이전트의 `paperflow` plugin·skill, `uv tool uninstall paperflow`)한 뒤 `manuwright` 를 설치하고 `manuwright agents install` 실행. 프로젝트 목록과 설정을 유지하려면 `~/.paperflow` 를 `~/.manuwright` 로 옮김.

### v1.8.1 (260930)

- **Codex 강제 수정**: Codex 는 `apply_patch` 로 파일을 쓰고 patch 를 `tool_input.command` 에 넣음(`file_path` 없음). 그래서 plan-first 게이트가 Codex 에서 전혀 동작하지 않았음. gate·lint hook 이 patch 안의 모든 파일 경로를 읽도록 수정하고, hook matcher 에 `apply_patch` 를 명시함. v1.8.0 설치 후 실제 Codex 세션에서 발견.
- `doctor` 의 pytest 경고는 소스 checkout 에서만 표시. `paperflow agents` 출력이 하위 명령 출력과 섞이지 않게 함.
- 401 tests 통과(Codex patch 테스트 +3).

### v1.8.0 (260930)

마일스톤: **두 방식 배포**. 같은 엔진을 clone 해서 쓰는 템플릿(A, 기존과 동일)으로도, Claude Code·Codex·Antigravity·opencode·Muse 어댑터가 딸린 설치형 `paperflow` CLI(B)로도 쓸 수 있음. v1.7.6~v1.7.10 을 묶고 다음을 추가:

- README "설치: 두 가지 방식" 절, `docs/migration_guide.md`(복사한 폴더의 선택형·비파괴 이전, A 방식 업데이트 파일 목록).
- `docs/distribution_plan.md` 를 구현 완료로 표시.
- `paperflow update` 는 릴리스 태그 `vX.Y.Z` 를 업데이트 채널로 씀.

### v1.7.10 (260930)

- **4단계, 에이전트 어댑터**: 설치 하나에 Claude Code·Codex plugin(skill `paperflow`·`paperflow-verify`, 세션 규칙·plan-first 게이트·lint·style hook), Antigravity(`agy`)용 루트 `plugin.json`, Muse·opencode 용 skill 이 들어 있음. `paperflow agents install|update [--only ...] [--dry-run]` 이 각 에이전트의 기본 명령을 실행함. 설치된 엔진 폴더를 plugin 루트로 쓰므로 어댑터 버전이 항상 CLI 와 같음. plugin hook 은 `paperflow hook <이름>` 을 부르고, 자체 hook 이 있는 템플릿 checkout 에서는 조용히 넘어가며, plugin·CLI 버전이 다르면 경고하고, 자동 업데이트가 켜져 있으면 백그라운드로 어댑터를 갱신함.
- `paperflow init` 이 공용 `docs/agent_bootstrap.md` 규칙을 `CLAUDE.md`/`AGENTS.md`/`GEMINI.md` 에 씀.
- 398 tests 통과(어댑터 +8). `claude plugin validate`·`agy plugin validate`·`muse skills validate` 로 검증.

### v1.7.9 (260930)

- **3단계, 설정과 업데이트**: `paperflow init`(엔진 템플릿으로 논문 폴더 생성, 덮어쓰기·승인 체크 없음), `paperflow rules [키워드]`, `paperflow update [--check|--to]`(태그 릴리스 재설치, 기록 남김, 명령 한 줄로 롤백), 선택형 `paperflow config set auto-update on`. 자동 업데이트는 patch 릴리스만, 하루 최대 1회. 등록된 논문이 엔진을 고정했거나 유효한 semantic review·human signoff 가 있으면 적용하지 않고 기다림.
- manifest `engine` 고정(예: `">=1.8,<1.9"`). 맞지 않으면 `verify` 가 `engine_pin` BLOCKED.
- 390 tests 통과(lifecycle +10).

### v1.7.8 (260930)

- Windows CI 수정: v1.7.5 테스트 2개가 스냅샷 키를 `/` 로 비교했음. 스냅샷 키는 OS 구분자를 씀. 기대값을 `Path` 로 만들도록 수정. 엔진 변경 없음.

### v1.7.7 (260930)

- **설치형 CLI, 2단계(미리보기)**: `pyproject.toml` 로 엔진을 `paperflow` 로 패키징(`uv tool install git+...@태그`). `paperflow doctor|status|verify|packet|build|record-approval` 은 `python -m harness` 와 같음. `paperflow citations|numbers|gate|lint|verify-all|search|...` 는 각 스크립트를 같은 옵션으로 실행하고, 프로젝트 경로를 생략하면 현재 폴더 기준으로 채움. wheel 은 허용 목록만 포함(코드, 용어집, WORKFLOW, docs, gate 템플릿). PDF·profile·원고·데이터는 제외.
- `check_gate.py` / `verify_all.py`: 프로젝트 루트용 `--base-dir` 추가(기본값은 그대로).
- CI 가 wheel 을 빌드·설치한 뒤 패키지 밖에서 설치형 테스트를 실행. 380 tests 통과(설치 전용 +3).

### v1.7.6 (260930)

- **배포 계획** (`docs/distribution_plan.md`): 한 저장소에서 두 방식 제공. A 는 지금처럼 clone 해서 쓰는 템플릿. B(v1.8.0 예정)는 설치형 `paperflow` CLI 와 Claude Code·Codex·Antigravity(`agy`)·opencode·Muse 용 얇은 어댑터. 업데이트는 자동으로 확인하고 적용은 명시적으로 함. 선택형 자동 업데이트는 논문의 유효한 리뷰를 절대 stale 로 만들지 않음. Codex(gpt-6-astra)와 검토했고 Spec Kit·OpenSpec·caveman·ponytail 과 비교함.
- **1단계 호환성 계약** (`tests/test_compat_contract.py`, 22 tests): 모든 스크립트가 설치 없이, 관계없는 폴더(공백·한글 경로)에서, `PYTHONPATH` 없이 실행됨. 기존 citation·number 기본 경로는 엔진 기준 유지. gate hook 은 이벤트 cwd 로 편집 파일을 찾음. 한 프로세스의 manifest 두 개가 서로 섞이지 않음.
- 379 tests 통과.

### v1.7.5 (260929)

Claude + Codex(gpt-6-astra) 공동 리뷰에서 나온 개선.

- **제출 기록 필드 단위 검증**: 체크리스트 항목마다 고유 id 필요, PASS 는 원고 위치, NOT_APPLICABLE 은 사유 필요, 그 외 상태는 실패. 전에는 `{"status":"PASS"}` 만 있어도 통과했음. AI 사용 시 `tools` 항목마다 `tool`·`role` 필요.
- **abstract 일치**: manifest 의 `abstract` 는 출판 `artifacts` 안에 있어야 하고, 출판되는 abstract 파일은 반드시 선언해야 함. 다른 파일을 검사하거나 조용히 건너뛰지 못함.
- **프로젝트 용어집·Style Spec**: manifest 에 선택 키 `terminology`·`style_spec` 추가. lint 가 프로젝트 용어집을 쓰고, `style_metrics` 가 `check_style.py` 를 돌리며, 두 파일이 review snapshot 에 들어감.
- **실패 원인 표시**: harness `detail` 에 `False` 대신 첫 이슈들(파일, 줄, 값)을 보여 줌. packet 에 체크리스트·AI 기록을 넣고, 해시로만 알려진 `omitted_sources` 목록을 줌.
- **사전 점검**: `doctor` 가 `python_supported` 를 보고하고, Claude gate hook 을 실제로 실행해 보며(`hooks.ok`), `warnings` 를 출력함. hook 에러는 조용히 통과하지 않고 WARNING 을 출력. Python 이 없으면 `run.sh` 가 경고. `requirements-dev.txt` 신설(CI 사용).
- **컨텍스트 절감**: 폴더 트리·파일 역할 표·명령 목록·PubMed 옵션을 매 세션 로드되는 `WORKFLOW.md`(56 KB → 30 KB)에서 `docs/workflow_reference.md` 로 이동. 명령 예시는 `python scripts/...` 형식으로 통일. `/verify` 예시에 `--cross-check` 추가.
- 357 tests 통과. `docs/harness_guide.md` v1.0.5.

### v1.7.4 (260908)

- **`profile/` 템플릿 제공**: `profile/example_authors.md`(교신저자·공동저자·funding 보일러플레이트·IRB/임상시험 등록 placeholder 골격)와 `profile/example_journals.md`(저널 13종 완성 예시 — 본문 인용 방식, 저자 cutoff, page range, ORCID 정책, 제출 체크리스트). 복사해서 `profile/authors.md`·`profile/journals.md`로 쓰면 되고, 그 두 파일은 계속 gitignored.
- `.gitignore`: `profile/` → `profile/*` + 부정 패턴. git은 부모 디렉터리가 제외되면 하위 파일을 다시 포함할 수 없어 기존 패턴으로는 템플릿을 올릴 수 없었음. 실제 profile 파일은 여전히 무시됨(실증 확인).
- **테스트 이식성 수정**: `test_cli_verify_hash_resolves_relative_paths_from_project_root`가 이 템플릿 저장소에만 있는 `drafts/05_results.md`를 해싱해서, `drafts/`를 논문별로 나눠 쓰는 실제 프로젝트에서는 항상 실패했음. 하네스가 항상 배포하는 파일을 해싱하도록 변경.

### v1.7.3 (260908)

- 한글 Windows에서 v1.7.2 검증: 344 tests, CI 9/9, 실제 CLI로 합성 오류 주입 시나리오 37개 — v1.7.1의 draft/revision 25개에 더해 `numeric_scope`(numeric_artifacts/예외 없이 결과 외 섹션에 숫자, 빈 사유, 결과 파일 예외 시도, 이미 바인딩된 파일 예외 시도)·`revision_scope`(REVn이 있는데 원본 섹션 나열, CHANGE 대상이 artifacts에 없음, REV2 편지에 REV1 artifacts) 12개 신규. 전부 설계대로 차단/통과.
- `docs/project.example.json`: v1.7.2 신규 필드 `numeric_exemptions` 키를 템플릿 manifest에 추가.
- README ko/ja/zh: v1.7.2 changelog 항목 현지화(영어만 있었음). 헤더 → v1.7.3; `harness/__init__.py`(doctor) → 1.7.3; `docs/harness_guide.md` → v1.0.3.

### v1.7.2 (260907)

- revision claim과 각 섹션의 최신 버전을 실제 제출 파일에 바인딩 (`revision_scope`).
- 수치 검사에서 빠진 원고 파일을 거부; 결과 외 섹션의 제외는 `numeric_exemptions`에 명시적 사유 필요 (`numeric_scope`).
- 헤더에 숫자가 있어도 p값 표 컬럼을 구분자 행으로 인식; 헤더 숫자 검사는 유지.
- doctor 버전 동기화, submission scope 회귀 테스트 추가.

### v1.7.1 (260908)

**v1.7.0(PR #1) merge 후 검증 — 결함 4건 수정, 문서 동기화**

- **v1.7.0에서 CI가 한 번도 돌지 않았음.** `.github/workflows/tests.yml`의 OS 매트릭스 줄이 setup-python `with:` 아래로 잘못 들어가 모든 실행이 YAML 파싱 단계에서 죽었음(0초). 이제 3 OS × 3 Python 매트릭스가 실제로 실행됨(main에서 9/9 통과).
- **Windows cp949:** 신규 `test_harness.py` / `test_review_regressions.py`가 `encoding='utf-8'` 없이 파일을 읽어 한글 Windows에서 3개 실패 — 죽어 있던 CI에 가려져 있었음. 수정; 333개 테스트 통과.
- **빌드 파일명:** `harness build`가 UTC 날짜를 찍어(한국시간 00~09시엔 전날 `_YYMMDD`) revision 패키지에 `_REVn`도 붙이지 않았음(Rule 5). 이제 최초 제출은 `manuscript_YYMMDD.docx`, revision은 `manuscript_REV1_YYMMDD.docx` / `response_letter_REV1_…` / `table_N_REV1_…`. 합성 REV1 빌드 테스트 추가; `docs/harness_guide.md` v1.0.1.
- **`CLAUDE.md`가 `WORKFLOW.md`를 import** (`@WORKFLOW.md`) — "먼저 읽어라"는 지시문에 의존하지 않고 Claude Code가 공유 규칙을 자동 로드. `WORKFLOW.md`/README에 남아 있던 "CLAUDE.md = 핵심 규칙 파일" 참조를 `WORKFLOW.md`로 정정.
- 합성 프로젝트에서 실제 CLI로 종단 검증: draft 프로필 12개·revision 프로필 13개 오류 주입 시나리오(미등록 인용, `todo` evidence, CSV에 없는 수치, 승인 후 plan 수정, ghost revision, 미응답/placeholder 응답, REV2↔REV1 baseline)가 모두 설계대로 차단됨; DOCX 구조는 `docs/docx_guide.md`와 일치.

### v1.7.0 (260906)

- F01–F09 수정: 인용 status/중복 ID, p값 경계, placeholder, 게이트 identity, plan 완결성, revision baseline, reviewer fallback.
- 공유 WORKFLOW.md와 표준 AGENTS.md·GEMINI.md 부트스트랩 추가.
- manifest 기반 검증 프로필, context-bound 결과값, content-bound 승인, review packet/state, 게이트된 DOCX 패키징 추가.
- 설정·마이그레이션·남은 제한 사항은 [shared engine guide](docs/harness_guide.md) 참조.

### v1.6.4 (2026-08-30)

**하네스 전체 리뷰(Claude Fable) — 결함 16건 수정, 회귀 테스트 33개**

- **게이트 false-PASS / false-FAIL / 크래시 (HIGH):** `check_citations.py`가 malformed·비ASCII `[EVID:…]` 태그(`o'brien_2021`, `müller_2020`)를 토큰 0개로 PASS시키던 것을 FAIL로; `search_pubmed.py`는 생성 id를 slugify하고 성(last name) 전체 사용. `check_numbers.py`: results CSV 행에 필드가 남아도 크래시 없음; 원고 `p<0.001`이 CSV 셀 `<0.001`과 매칭(같거나 느슨한 bound); 대문자 `P<0.05`도 p-비교로 인식; `L4-5`·`C5-6`·`COVID-19`·`ICD-10` 같은 접미 숫자는 구조 표기로 제외; ROUND_HALF_UP도 허용(2.675 → 2.68).
- **강제 훅이 실제로 켜짐:** 훅을 신규 `scripts/hooks/run.sh`(`py` 있으면 py, 없으면 `python3`)로 실행 — 이전엔 macOS/Linux에서 모든 훅이 exit 127로 Rule 7·8 강제가 조용히 꺼져 있었음. `enforce_gates.py`는 승인 체크박스가 **아예 없는** plan도 미승인 처리(Rule 9 문구가 실제론 강제되지 않던 것).
- **`check_gate.py`:** artifact 경로를 슬래시 무관 비교(`drafts\05_results.md` == `drafts/05_results.md`, `--verify-hash`/`--cross-check` 포함); 다중 블록 gate 파일을 `artifact:` 단위로 분리해 `--artifact`로 선택 — 앞 블록 FAIL이 뒤 블록 PASS에 가려지지 않음; 블록 여러 개인데 `--artifact` 없으면 loud FAIL. `_TEMPLATE.GATE.md`에 문서화.
- **`check_response_coverage.py`:** 인용형 대괄호(`[12]`, `[3-5]`, `[EVID:id]`)를 placeholder로 안 잡음 — 문헌 인용 반박문 통과.
- **소소:** `check_abstract.py` half-up 반올림; `format_references.py` author-year 모드에서 `author_year_keyword` id 허용(`evidence_guide.md` v0.3.1로 문서 정렬); `compile_response_docx.py`가 "# Response to Reviewers"를 "Response: to Reviewers"로 망가뜨리지 않음; `check_citations`/`check_numbers`/`check_coverage` 코드펜스 뒤 줄번호 정확; `check_coverage.py` 마크다운 표 행별 집계; `check_abbreviations.py` allowlist가 `COVID-19`를 어간으로 매칭; `lint_manuscript.py` 이탤릭 `*p* = .02` 잡고 "group = 30"은 안 잡음.
- 테스트 262 → 295.

### v1.6.3 (2026-07-02)

**기계적 투고 오류 체커 3종 (advisory 우선)**

- **`scripts/check_crossrefs.py`** — 본문 "Table N"/"Figure N" 언급을 실제 `table_*.md`·figure legend 항목과 대조: broken reference(그동안 아무것도 못 잡던 desk-reject 사유)·미인용 table/figure·첫 언급 순서. "Tables 1 and 2"·"Figure 2-4"·"Fig. 1A" 처리; 코드펜스/HTML 주석 무시; inventory 없으면 전부 broken으로 오탐하는 대신 loud하게 건너뜀. advisory 기본, `--fail-on-broken`/`--fail-on-unreferenced`/`--fail-on-order`로 게이트화.
- **`scripts/check_abbreviations.py`** — 약어 첫 사용 정의 audit, abstract/본문 독립 scope(저널이 둘 다 요구). `ABBREV_UNDEFINED`/`ABBREV_DEFINED_AFTER_USE`/`ABBREV_REDEFINED`/항상-advisory `ABBREV_SINGLE_USE`. 의도적으로 advisory — 탐지는 대문자 전용(2-6자, `-숫자`, 복수형 s), 통계 약어 기본 허용(CI, SD, OR, HR...) + `--allow` 확장; `--strict`는 정의 이슈만 게이트화.
- **`scripts/check_response_coverage.py`** — ghost-revision 게이트의 반대면: 응답서가 **모든** 리뷰어 코멘트에 답했는가? `Reviewer #N:`/`Comment N)`/`Response:` 구조 파싱, 미응답·빈 응답·`[placeholder]` 차단, `--comments`로 원본 코멘트 파일 대조(`COMMENT_UNANSWERED` 실패; 원본 파싱 불가 시 경고, `--strict`면 실패). 기본 fail — 코멘트 누락은 이분법적 결함.
- 설계 원칙(저자 피드백 반영): 기계화는 이분법적 사실에만, 판단은 사람+LLM 몫. 문서 갱신(`CLAUDE.md`, `docs/qc_guide.md` §3.7/§4.2, `docs/revision_guide.md`). 테스트 40개(총 262).

### v1.6.2 (2026-07-02)

**Abstract Keywords 강제**

- `drafts/02_abstract.md` 하단의 `**Keywords:**` 자리가 lint·규칙 없이 놓쳐지기 쉬웠음. 3중 강제: (1) 템플릿에 요구사항·예시 명시, (2) `docs/writing_guide.md` § 02. Abstract에 Keywords 규칙 추가(3–6개 MeSH 선호, 세미콜론 구분), (3) `scripts/lint_manuscript.py`가 abstract 파일을 감지해 `KEYWORDS_MISSING`/`KEYWORDS_EMPTY`/`KEYWORDS_TOO_FEW`/`KEYWORDS_TOO_MANY` 발생 — PostToolUse `lint_on_edit` 훅이 이미 편집 시 lint를 표면화하므로, abstract 건드리는 즉시 빈 Keywords가 잡힘. `;`·`,` 둘 다 구분자로 인정. 테스트 7개(총 222).

### v1.6.1 (2026-06-30)

**`/editor-review`가 `/critical-review`와 동일한 리뷰어 피커 사용**

- editorial desk-screen이 이제 `/critical-review`와 같은 모델 선택 UX를 제공: 같은 풀(OpenRouter 4종 `scripts/critical_models.txt` + 로컬 Claude + Codex)에 대한 `AskUserQuestion` 리뷰어 피커, role만 다름(`--role editor`, 프롬프트 `editor.txt`). `Claude`만 선택하면 단일 Opus 서브에이전트(키 불필요). Codex는 `codex:codex-rescue`로 오케스트레이션(critical_review.py 모델 아님 — 스크립트는 OpenRouter + 로컬 Claude만). 커맨드 + protocol §5 갱신; v1.6.0에서 changelog엔 있으나 헤더가 v1.5.10로 남아 있던 ja/zh README도 정정.

### v1.6.0 (2026-06-29)

**Editorial desk-screen — high-impact 저널 편집장 평가 (`/editor-review`)**

- 기계적 QC·reviewer 비판을 넘어선 새 평가: **high-impact tier 편집장·임상 편집자 desk-screen**. 논문의 분야를 식별하고, 그 분야 high-impact 저널이 실제로 싣는 수준으로 벤치마크해 **임상 타당성**(practice 바꾸나? p 말고 MCID/effect?)·**scope/novelty fit**·**방법·분석 적절성**을 판정 → `SEND FOR PEER REVIEW`/`BORDERLINE`/`DESK REJECT` + 경쟁력 위한 **구체적 추가검증**, 또는 bar가 무리면 현실적 하위 저널.
- 정본 프롬프트 `scripts/critical_prompts/editor.txt`(single source). 단일 Opus 서브에이전트(키 불필요) **또는** `scripts/critical_review.py --role editor` 멀티모델 panel; medical-kag/PubMed로 실제 high-impact 문헌 벤치마크 선택. `/editor-review`로 노출, `docs/critical_review_protocol.md` §5 문서화. 판정형(advisory) — grounded 게이트 대체 아님. 테스트 추가.

### v1.5.10 (2026-06-28)

**테스트 커버리지 보강 2라운드 (MEDIUM gap)**

- 전체 리뷰의 남은 커버리지 gap에 테스트 추가: `search_pubmed.py` 순수 포매터(`format_citation` 저자 수 분기, `guess_study_design` ladder); `check_abstract.py`(abstract가 본문보다 정밀 → fail, 정수 매칭, 다중 파일 body 집계, issue에 comparator 보존); `check_numbers.py`(p값 `>` comparator pass/fail, heading/`Table N`/`Figure N`/연도에 대한 `is_structural_number`); `check_style.py`(`mean_sentence_length`/`paragraph_count` tolerance, `split_sentences` 약어/소수 보호); `check_citations.py`(`require_citations`, `fail_abstract_only` 토글); `format_references.py`(`smith_2020a` disambiguation, `--convert` write 경로); `check_coverage.py`(`--fail-on-unrealized`). 총 214 테스트(이전 170).

### v1.5.9 (2026-06-28)

**enforcement 경로 테스트 커버리지 보강**

- 전체 리뷰의 커버리지 분석에서 여러 *enforcement 계약*이 미검증 → 회귀 시 조용히 무력화될 위험 발견. 추가한 테스트: `verify_all.py` 최상위 `OVERALL: PASS` 판정 + `--cross-check`(및 `--evidence`/`--results`)의 `check_gate.py` 전달; `check_coverage.py`의 `--fail-on-over-citation`/`--fail-on-unknown`/`--fail-on-uncited-verified` exit code(기본 advisory vs blocking); `check_revision_claims.py`의 `--strict` escalation(original 누락이 기본은 warning, `--strict`에선 failure). 총 170 테스트(이전 163).

### v1.5.8 (2026-06-28)

**`[EVID:id]` regex 통일 (전체 리뷰 일관성 수정)**

- `extract_claims.py`는 자체 permissive `[EVID:([^\]]+)]` 패턴을 썼고, `check_citations.py`(및 이를 재사용하는 `check_coverage.py`·`format_references.py`)는 restrictive `[A-Za-z0-9_.-]+`를 씀. 유효한 slugified id는 둘 다 동일하게 매칭하나, drift 때문에 malformed 태그가 추출은 되지만 검증/변환은 안 되는 불일치가 있었음. 이제 `extract_claims.py`가 `check_citations.py`의 정본 `EVID_RE`를 import → 4개 스크립트가 single source 공유. 유효 id는 동작 변화 없음; 163 tests green.

### v1.5.7 (2026-06-28)

**전체 코드 감사에서 나온 버그 수정**

- **Gate cross-check가 live FAIL이면 무조건 게이트 FAIL** (`check_gate.py`) — 이전엔 cross-check 차원이 live 재실행에서 FAIL인데 원장도 FAIL을 기록하면 "일치"로 보고 실패를 추가하지 않아, 그 차원을 `--require-check`로 걸지 않은 경우 **깨진 산출물이 통과**할 수 있었음. 이제 live 결정적 실패는 원장과 무관하게 항상 게이트 FAIL.
- **plan-first 훅이 상대 cwd에서 더 이상 fail-open 안 함** (`hooks/enforce_gates.py`, `hooks/lint_on_edit.py`) — 상대/누락 `cwd`가 경로를 `drafts/05_results.md`(앞 슬래시 없음)로 정규화 → `"/drafts/"`/`"/data/.../py/"` 체크 미스 → Rule 7/8 게이트 스킵. 이제 체크 전에 앞 슬래시를 강제. (latent: production은 항상 absolute cwd 전송.)
- 회귀 테스트 +2 (총 163).

### v1.5.6 (2026-06-28)

**Abstract↔본문 수치 일관성 + medical-kag synthesis 워크플로**

- **`scripts/check_abstract.py`** — abstract의 모든 수치가 본문 섹션에도 등장하는지(반올림 허용) 확인 → reviewer 단골 지적인 abstract-only 수치를 잡음. `check_numbers.py`(수치↔`results/*.csv`)를 보완; p값 토큰은 기본 제외(`--include-p-values`로 포함). Rule 3 / QC Round 1의 Abstract↔Methods↔Results↔Tables 일관성을 자동화. 테스트 5개.
- **medical-kag synthesis → Discussion/Limitations 워크플로** (`docs/medical_kag_protocol.md`) — `compare_interventions` / `conflict synthesize` 출력은 풍부하나 noisy(bibliometric outcome, 빈 값, KG 정규화 이름) → 임상 outcome 필터·모든 수치/인용 grounding·게이트 통과 방법 + Discussion/Limitations 골격 문서화.

### v1.5.5 (2026-06-28)

**CI: 모든 push/PR에서 테스트 실행**

- **`.github/workflows/tests.yml`** — GitHub Actions가 `main` push와 PR마다 전체 pytest를 Python 3.10/3.11/3.12에서 실행 → 검증 스크립트를 깨뜨리는 변경을 머지 전에 차단. README 상단에 상태 배지 표시.

### v1.5.4 (2026-06-28)

**MCP 독립 reference formatter (Phase 7)**

- **`scripts/format_references.py`** — 작성 시점의 `[EVID:id]` 태그를 제출용 서지목록 + 본문 인용으로 변환. `knowledge/evidence.md`만 읽음(medical-kag 불필요). 두 스타일: **numbered**(Vancouver — `[EVID:id]` → `[N]` 등장순, 목록도 그 순서로 번호) + **author-year**(`(Author, Year)`, 알파벳 목록). `--convert`는 태그 치환본을 `*_formatted.md`로 출력(in-place 안 함); evidence.md에 없는 인용은 변환 안 하고 보고(+ exit non-zero). 연결 시 medical-kag `reference` 툴과 상호보완. 테스트 7개(총 156).

### v1.5.3 (2026-06-28)

**Coverage audit를 과잉인용 중심으로 재정향 (orphan=낭비 프레이밍 폐기)**

- **과잉인용 탐지** — `check_coverage.py`가 한 문장에 `--max-citations-per-sentence`(기본 4) 초과 `[EVID:id]` 인용을 플래그(인용 남발/padding). 이것과 **미등록인용**이 진짜 품질 신호 → `--fail-on-over-citation` / `--fail-on-unknown`이 의미 있는 차단 플래그.
- **orphan/uncited를 중립으로 재정의** — 등록됐지만 미인용된 ref는 정상 큐레이션(꼭 필요한 것만 인용)이지 **낭비가 아니다.** 기존 "verified work unused" 표현 제거; uncited ref·미실현 draft_plan 항목은 중립 정보로 보고. `--fail-on-uncited-verified` / `--fail-on-unrealized`는 strict full-use 정책 전용, 기본 off. coverage 테스트 8개(전체 149).

### v1.5.2 (2026-06-27)

**인용 coverage / orphan audit**

- **`scripts/check_coverage.py`** — `knowledge/evidence.md` 대비 Phase 6 QC 감사: **orphan reference**(등록됐는데 한 번도 인용 안 됨; verified-but-uncited는 "낭비된 작업"으로 표시), 섹션별 **인용밀도**, **unknown citation**(인용했는데 미등록), 그리고 `--draft-plan` 사용 시 **미실현 claim**(Claim→Citation 매핑에 계획됐으나 본문에 미인용)을 리포트. 기본 advisory, `--fail-on-orphan-verified` / `--fail-on-unrealized` / `--fail-on-unknown`로 차원별 게이트화. `check_citations.py` 파서를 재사용해 둘이 lockstep 유지. 테스트 7개(총 148).

### v1.5.1 (2026-06-26)

**번역 README 문서 표 파리티**

- 한국어/일본어/중국어 README의 File Roles 표에서 누락된 행을 `README.md`와 일치하도록 추가: `docs/debate_protocol.md` · `docs/critical_review_protocol.md` (3개 언어 모두), `scripts/critical_review.py` (ja/zh). 문서만 변경, 코드 변경 없음.

### v1.5.0 (2026-06-26)

**Gate cross-check (원장 ↔ live) + 문서/버전 자동 동기화 정책**

- **Gate cross-check** (`scripts/check_gate.py --cross-check LABEL=PATH`) — 결정적 차원(`citation` / `numbers` / `revision_claims`)에 대해 정본 checker를 즉석 재실행하고, 원장 기록이 양방향 중 어느 쪽으로든 실제와 불일치하면 게이트 FAIL — stale/가짜 `PASS` 차단, 소스 미도달 시 loud FAIL. `scripts/verify_all.py`가 포워딩하고 정본 게이트 명령(`review/gates/_TEMPLATE.GATE.md`, `docs/verification_protocol.md` v0.3.0, CLAUDE.md)에 연결. 회귀 테스트 +6 (총 141).
- **문서/버전 동기화 + 자동 commit-push 정책** (CLAUDE.md Rule 12) — harness 코드/버그 변경 시 버전 bump + 영향받는 문서 갱신 + 자동 커밋/푸시 (민감·파괴적 경우엔 STOP 조건 명시).

### v1.4.1 (2026-06-24)

**Template gate 강화 + `/verify` freshness 전달**

- **Template-aware plan gate** — `scripts/hooks/enforce_gates.py`가 미완성 `analysis_plan.md` / `draft_plan.md` 템플릿이나 미체크 승인 항목을 승인된 plan으로 인정하지 않으며, `Write|Edit|MultiEdit` 모두에 적용됩니다. 정상적인 citation-style `[N]` 문구는 오탐하지 않도록 보수적으로 처리합니다.
- **Fresh `/verify` gate check** — `scripts/verify_all.py`가 `--verify-hash`를 `check_gate.py`로 전달합니다. README/CLAUDE/slash-command 예시에 freshness 입력을 포함했습니다.
- **Windows/template 정리** — PubMed 명령 예시는 `python scripts/search_pubmed.py`로 정리했고, 루트의 생성 DOCX 산출물은 ignore 처리했으며, hook과 freshness 전달 동작은 회귀 테스트로 보호합니다.

### v1.4.0 (2026-06-24)

**Citation stance + 근거 비교표 (GraphRAG 기반)**

- **Citation stance** (`/cite-stance [claim|section]`) — 인용된 각 출처가 claim과 어떤 관계인지(지지 / 반박 / 단순 언급) 분류하여 Discussion의 균형을 유지합니다. 반박 근거(contrasting evidence)가 존재하는데도 인용되지 않은 경우 "one-sided"로 플래그를 표시합니다(누락에 의한 overclaim 가드). 신규 Citation-Stance verifier가 추가되었으며(`docs/verifier_prompt_templates.md`), medical-kag `conflict`가 누락된 반박 근거를 surface하고 evidence.md로 폴백합니다. Scite 스타일의 claim 특화 기능입니다.
- **근거 비교표** (`/evidence-table [topic|ids]`) — Discussion이나 PRISMA supplement를 위한 "포함된 연구 요약(summary of included studies)" 표(study / design / n / intervention / outcome / result / LoE)를 조립합니다. `scripts/evidence_table.py`가 결정적(deterministic) 포매터이며, medical-kag 구조화 데이터를 주(primary)로, evidence.md를 폴백으로 사용합니다. Elicit 스타일입니다. 테스트도 추가되었습니다.

### v1.3.0 (2026-06-24)

**Citation 보조 — 제안 + claim별 검증 (GraphRAG 기반)**

- **Citation 제안** (`/suggest-citation [claim]`) — 초안의 claim을 입력하면 medical-kag knowledge graph(GraphRAG)를 통해 가장 적합한 `[EVID:id]` 후보를 검색하며, MCP를 사용할 수 없을 때는 `knowledge/evidence.md` + `scripts/search_pubmed.py`로 폴백합니다. 선택은 저자가 하고, 신규 출처는 인용 가능해지기 전에 evidence.md에 등록(PMID/DOI 검증 완료)되므로 grounding이 유지됩니다.
- **Claim별 검증 리포트** (`/verify-claims [section]`) — `scripts/extract_claims.py`가 `[EVID:id]` 태그가 붙은 모든 문장을 추출하면, Semantic-Citation Verifier가 각 문장을 SUPPORTED / PARTIAL / UNSUPPORTED로 분류하여 `review/claim_verification.md`에 기록합니다(Phase 6 QC의 "claim map"으로, `check_citations.py`의 존재 여부 확인보다 깊이 들어갑니다). 신규 `docs/citation_assist_protocol.md`가 추가되었으며, 두 작업 모두 evidence.md로 무리 없이(gracefully) degrade합니다. 테스트도 추가되었습니다.

### v1.2.0 (2026-06-22)

**medical-kag MCP 통합 — evidence.md와 함께 작동하는 knowledge graph**

- **Grounding을 보존하는 KAG 통합** — `medical-kag-remote` MCP(척추 수술 knowledge-augmented graph)가 상류(upstream)의 discovery/analysis/format 엔진으로 연결되지만, `knowledge/evidence.md`는 여전히 단일 정본(canonical) citation ledger로 남습니다. graph가 surface한 모든 것은 인용되기 전에 `[EVID:id]`(PMID/DOI 검증 완료)로 등록되므로, `check_citations.py`가 변함없이 모든 것을 게이트합니다. 신규 `docs/medical_kag_protocol.md`가 도구를 phase에 매핑합니다 — discovery + 구조화 추출(Phase 1), claim과 Discussion을 위한 evidence-chain / intervention-comparison / GRADE 종합(Phase 3-4), conflict / overclaim 가드(Phase 6), 저널 형식 참고문헌 목록(Phase 7).
- **부가적(additive) + 폴백** — 이 MCP는 결코 의존성이 아닙니다: 사용할 수 없는 경우(예: 인증되지 않은 remote 세션) 워크플로는 `scripts/search_pubmed.py` + 수동 evidence.md로 degrade합니다. Codex 동등성을 위해 CLAUDE.md(Rule 1, STOP 신호, Phase 1, Quick Commands)와 AGENTS.md에 연결되어 있습니다.

### v1.1.2 (2026-06-21)

**수정 — hook이 UTF-8 stdin을 읽도록 (Windows에서 한국어 의도 인식)**

- `UserPromptSubmit` / `PreToolUse` / `PostToolUse` hook이 이제 stdin을 UTF-8로 재설정합니다. Windows(기본 cp949)에서는 Claude Code가 보내는 JSON payload가 잘못 디코딩되어, ASCII가 아닌 프롬프트 — 예: 한국어 자동 트리거 "학술적으로 바꿔줘" — 가 조용히 매칭에 실패했습니다. 종단 간(end-to-end) UTF-8 stdin 테스트를 추가했습니다.

### v1.1.1 (2026-06-21)

**스타일 강제 — 측정 가능한 게이트 + Codex 동등성**

- **결정적 스타일 지표** — `scripts/check_style.py`(`extract` / `check --spec`)가 단어 수, 평균 문장 길이, 문단 수, 인용 밀도, hedging을 측정하고 Style Spec 목표치에서 벗어나는 편차를 표시합니다 — 스타일판 "check_numbers". `lint_on_edit.py`에 연결되어(Style Spec이 존재할 때 각 초안 편집마다 `[STYLE-METRIC]` 편차를 표면화) Phase 5/6 게이트와 함께 작동합니다. 테스트 추가.
- **Codex 동등성 + 보정** — hook은 Claude Code 전용이므로, 이제 `AGENTS.md`가 Claude가 아닌 런타임에게 style-pass(`check_style.py` + Style-Conformance verifier)를 명시적으로 실행하도록 안내합니다. Style Spec 템플릿에는 before→after 보정 예시가 추가됩니다(few-shot이 추상적 규칙보다 변환을 더 잘 유도함).

### v1.1.0 (2026-06-21)

**스타일 변환 — 거친 초안 → bound 저널 스타일로, 안정적으로**

- **Style Spec + Style-Conformance Verifier** — 하나의 exemplar(`Style/own/` 또는 `Style/target_journal/`)를 항상 로드되는 간결한 `drafts/style_spec.md`(`docs/style_spec_template.md`)로 묶은 뒤, 섹션별로 변환하고 각 섹션을 독립적인 **Style-Conformance Verifier**로 spec과 대조해 검증합니다(자동 수정 루프, 최대 2회; `docs/verifier_prompt_templates.md` + `verification_protocol.md`). 이로써 lint가 닿지 못하는 총체적 스타일 층위(구조, 문장 길이, hedging, 주장 강도, 참고문헌 형식)에 도달합니다. 신규 `/style-pass` 명령 + `docs/style_transform_protocol.md`.
- **의도 기반 자동 트리거** — `UserPromptSubmit` hook(`scripts/hooks/style_intent.py`)이 "make it academic / 학술적으로 바꿔줘"를 감지해 style-pass 프로토콜을 주입하므로, 명령을 기억하지 않아도 변환이 작동합니다. SessionStart도 이제 활성 Style Spec을 함께 표시합니다. Advisory + fail-open. 테스트 추가.

### v1.0.3 (2026-06-20)

**런타임 간 critical review + 모델 선택**

- **Claude-CLI 리뷰어** — `scripts/critical_review.py --include-claude`는 로컬 `claude -p`(headless)를 shell로 호출하므로, Claude Code가 아닌 호출자(Codex나 일반 shell)도 Claude의 적대적 검토를 가져올 수 있습니다. `OPENROUTER_API_KEY`는 이제 OpenRouter 모델을 실제로 요청할 때만 필요합니다. `docs/critical_review_protocol.md` + `AGENTS.md`에 문서화.
- **더 큰 모델 풀 + ~2개 선택** — `scripts/critical_models.txt`에 MiniMax M3, GLM 5.2, Qwen3-Max, DeepSeek V4 Pro가 추가되었습니다. `/critical-review`는 이들을 개별 `AskUserQuestion` 옵션으로 제시하고 ~2개 선택을 권장하며(비용 + 사각지대 다양성), 이후 `--models <selected>`로 실행합니다.

### v1.0.2 (2026-06-20)

**프로세스 강제 + CLAUDE.md 간결화**

- **Plan-first 강제 (hooks)** — `.claude/settings.json`에 커밋된 hook을 추가: PreToolUse `Write|Edit|MultiEdit` 게이트(`scripts/hooks/enforce_gates.py`)는 완료/승인된 `drafts/.../draft_plan.md` 없이 섹션을 작성하거나(Rule 8) 완료/승인된 `data/.../analysis_plan.md` 없이 분석 스크립트를 생성하는 것(Rule 7)을 **차단**하고, SessionStart hook(`scripts/hooks/session_contract.py`)은 매 세션마다 워크플로 계약을 주입합니다. Revision은 예외 처리되고, 멀티 논문 서브폴더를 지원하며, 실패 시 통과(fails open)하고, UTF-8 안전합니다. (Windows는 `py`; macOS/Linux는 `python3` 사용.)
- **`/verify`** — `scripts/verify_all.py`가 게이트 PASS를 기록하기 전에 check_citations + check_numbers(+ 선택적 check_gate)를 한 번의 명령으로 실행하고, 문서화된 freshness 검사가 유지되도록 `--verify-hash`를 전달합니다. hook 동작과 freshness 전달은 회귀 테스트로 보호됩니다.
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
- `scripts/lint_manuscript.py` 추가 및 draft/table template 수정: Windows에서 `python scripts/lint_manuscript.py drafts --quiet` 통과.
- `AGENTS.md` 추가: agent bootstrap 지침이며 `CLAUDE.md`를 authoritative source of truth로 명시.
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

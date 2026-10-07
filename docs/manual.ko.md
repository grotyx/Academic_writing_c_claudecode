# manuwright 사용자 매뉴얼 (v2.5.2)

빈 폴더에서 서명된 DOCX 패키지까지 논문 하나를 따라가는 매뉴얼이다. 합성 임상시험 데이터로 실제로 돌려 본 end-to-end 시험(2026-09-30)의 명령과 출력을 그대로 썼다. 학술 문체 모드(6절), 근거 강도와 참고문헌 재점검(3절), revision 블라인드 재검토(11절)는 v1.9.0 기능이다. 규칙은 [WORKFLOW.md](../WORKFLOW.md), 명령 세부는 [harness_guide.md](harness_guide.md), 영어판은 [manual.md](manual.md).

스크린샷은 시험 중 터미널의 텍스트를 이미지로 렌더링한 것이다(세션에 macOS 화면 기록 권한이 없었음). 도구가 출력한 내용과 같고, 긴 출력은 줄였다고 표시했다. 6절, 8절의 claim-strength, 11절 그림은 v1.9.1 로 새 논문 폴더에서 다시 돌린 시험(2026-10-07)의 출력이다. 회색 `#` 줄은 설명을 위해 붙인 주석이다.

![manuwright 파이프라인](images/manual/01_pipeline_overview.png)

## 한눈에 보기

| 얻는 것 | 강제하는 방법 |
|---|---|
| 승인된 계획 없이는 쓰지 않음 | 에이전트 hook(Claude Code, Codex)과 `manuwright verify` |
| 모든 인용은 등록·검증된 출처에서 | `knowledge/evidence.md` + `manuwright citations`. 출처는 PubMed 또는 내 Obsidian 라이브러리 |
| 모든 숫자는 내 데이터에서 | `results/*.csv` + `manuwright numbers` + 수치 바인딩(데모에서 155개) |
| 실제로 완결된 보고 체크리스트 | 공식 CONSORT/STROBE/PRISMA/CARE 체크리스트를 독립 검토자가 확인 |
| 글쓴 모델이 아닌 다른 모델의 검토 | Codex, Antigravity, opencode, Muse, Claude, OpenRouter 모델을 원하는 대로 조합 |
| 검토·서명한 것과 똑같은 패키지 | sha256 스냅샷. 무엇이든 바뀌면 검토와 서명이 stale 이 됨 |
| AI 말투가 아닌 의학 학술지 말투 | 학술 문체 모드: 섹션 카드 + 편집마다 문장 검사(6절) |
| 근거보다 센 표현이 없음 | evidence.md 의 `Claim Strength` + `manuwright claim-strength` (3절, 8절) |
| 철회 논문·틀린 DOI 가 없음 | `manuwright search audit` (3절) |
| 응답 편지에 끌려가지 않는 revision 재검토 | `manuwright blind-review` (11절) |

## 빠른 시작

```sh
uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@v1.9.3
manuwright agents install                       # 에이전트별 plugin/skill. Obsidian 도 제안
manuwright init my-paper && cd my-paper
manuwright target                              # 이 논문: 목표 저널 + Word 스타일 (메뉴)
manuwright search "연구 주제" --max 10           # 또는: manuwright evidence import-obsidian <citekey>
#  data/analysis_plan.md 작성 -> 저자 승인 -> manuwright record-approval ...
#  분석 스크립트 -> results/*.csv -> 표;  drafts/draft_plan.md -> 승인
#  원하는 에이전트로 섹션 작성 ("서론 써줘": 학술 문체 카드가 자동으로 붙음)
manuwright style learn ~/papers/good              # (선택) 좋은 논문 3편 이상으로 문체 학습
manuwright verify --project project.json --profile draft
manuwright claim-strength drafts                  # 근거보다 센 표현
manuwright search audit                           # 참고문헌 재점검: 철회, DOI
manuwright packet --project project.json        # 독립 semantic review
manuwright critical-review --target drafts/05_results.md --out review/critical
manuwright verify --project project.json --profile submission
manuwright build --project project.json
```

## 1. 설치와 점검

```sh
uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@v1.9.3
manuwright doctor                  # python_supported, hooks.ok, warnings 확인
manuwright agents install --dry-run
manuwright agents install          # Claude Code, Codex, Antigravity, opencode, Muse
```

`agents install` 은 선택 기능인 Obsidian 라이브러리도 제안한다(3b 절). plugin 을 설치·업데이트한 뒤에는 Claude Code 를 재시작한다. Codex 는 폴더에서 처음 실행할 때 plugin hook 을 신뢰할지 묻는다. manuwright hook 5개에 "Trust all" 을 고른다. 설치하지 않는 템플릿 사용자는 clone 한 저장소 안에서 같은 엔진을 `python -m harness ...`, `python scripts/<tool>.py ...` 로 쓴다.

## 2. 논문 시작

```sh
manuwright init my-paper
cd my-paper
```

`init` 이 만드는 것:
- `project.json`
- `data/analysis_plan.md`, `drafts/draft_plan.md` (템플릿, 미승인)
- `knowledge/evidence.md`
- 에이전트 규칙 파일(`AGENTS.md`, `CLAUDE.md`, `GEMINI.md`)
- 빈 `results/`, `review/`, `output/`

파일을 덮어쓰지 않고, 무엇도 승인하지 않는다. 실제 원고는 공개 템플릿 clone 이 아닌 비공개 폴더에 둔다. 데이터는 `data/` 에 넣는다(예: `data/raw_data.csv`, `.xlsx`).

## 3. 근거 등록

```sh
manuwright search "minimally invasive versus open lumbar fusion randomized" --max 8
manuwright search fetch 31476471 34602458 --format evidence
```

나온 항목을 `knowledge/evidence.md` 에 붙이고, 요약 칸은 실제로 읽은 내용으로 채운다. 전문을 읽기 전까지는 `Source Status: abstract-only` 로 둔다. 여기에 등록된 ID 만 `[EVID:miller_2020_pmid31476471]` 형식으로 인용할 수 있다. 새 논문의 evidence.md 에 있는 예시 항목은 주석이라 등록된 것으로 치지 않는다.

**근거 강도.** 항목마다 그 논문으로 어디까지 말할 수 있는지 적는다. `manuwright search` 로 가져온 항목에는 두 칸이 들어 있다.

```text
- **Claim Strength:** observed           (speculative | observed | supported | strong)
- **Allowed Wording:** was associated with
```

| 값 | 보통 이런 근거 | 쓸 수 있는 표현 |
|---|---|---|
| `speculative` | 가설, 증례, 전문가 의견 | may, suggest |
| `observed` | 관찰 연구(코호트, 환자-대조군) | was associated with, observed, reported |
| `supported` | 일관된 관찰 연구, 작은 RCT | showed, reduced, improved |
| `strong` | 대규모 RCT, 메타분석 | demonstrated, prevents 까지 |

어느 값을 줄지는 저자가 정한다. 8절의 `claim-strength` 검사가 이 값을 쓴다. 칸을 비워 두면 그 항목은 검사하지 않는다.

**투고 전 재점검.** `manuwright search audit` 은 PMID 나 DOI 가 있는 모든 항목을 PubMed 에서 다시 가져와 제목·제1저자·연도·저널을 대조하고, 철회(retraction)·우려 표명·정정을 표시한다. 철회됐거나, 다른 논문을 가리키거나, PubMed 에 없는 DOI 인 항목이 있으면 실패로 끝난다(그 DOI 는 doi.org 에서 직접 확인; PubMed 밖 저널도 여기 걸린다). PMID 도 DOI 도 없는 항목은 unchecked 로 표시된다. 인터넷 연결이 필요하다. 채팅으로는 "참고문헌 다시 확인해줘".

### 3b. 내 Obsidian 라이브러리 (선택, 권장)

Obsidian 에서 "Academic Paper Citation Manager" 플러그인(PubMed 가져오기, AI 요약, citekey)으로 참고문헌을 관리한다면, 모든 에이전트가 글을 쓰는 동안 그 라이브러리를 검색할 수 있다. manuwright 는 이것을 요구하지 않는다.

**플러그인 설치** (이미 있으면 건너뜀). 플러그인이 없으면 `manuwright agents install` 이 설치를 제안하고, 직접 실행해도 된다. 고른 vault 에 최신 릴리스를 받아 켜고, 동의하면 MCP 접근도 켠다. Obsidian 앱은 설치돼 있어야 하고 vault 는 Obsidian 에서 한 번 만들어 둬야 한다. Obsidian 이 그 vault 를 처음 열 때 플러그인을 신뢰할지 묻는데, 허용한다.

![Obsidian 플러그인 설치](images/manual/42_obsidian_install.png)

**에이전트에 연결.** `connect` 는 먼저 물어보고, 이미 연결된 에이전트는 건너뛰고, 각 에이전트의 `mcp add` 를 쓰며, 수정하는 JSON 설정 파일(opencode, Muse)은 백업한다.

```sh
manuwright obsidian status
manuwright obsidian connect            # --dry-run 은 명령만 보여 줌, --only 로 에이전트 선택
```

![연결 상태](images/manual/40_obsidian_status.png)

![에이전트 연결 (dry run)](images/manual/41_obsidian_connect.png)

시험에서 Codex, Muse, opencode 가 MCP 로 라이브러리를 읽었다(색인 22,622 청크). Claude Code 는 이미 연결돼 있었다. Antigravity 는 MCP 도구 사용 허가를 물어보는데 headless 모드에서는 허가할 수 없으므로, 대화형 세션에서 첫 호출을 허가한다. 에이전트가 쓰는 동안 Obsidian 이 MCP 를 켠 채로 열려 있어야 한다.

![에이전트가 MCP 로 라이브러리 조회 (요약)](images/manual/44_obsidian_mcp_agents.png)

**참고문헌을 논문으로 가져오기.** 라이브러리는 찾는 용도이고, 인용할 수 있는 것은 `knowledge/evidence.md` 항목뿐이다. citekey 로 가져오면 CSL 필드가 인용 문자열이 되고, 플러그인의 AI 요약이 요약 칸을 채우고, citekey 가 `[EVID:id]` 가 되며, 상태는 `abstract-only` 로 시작한다. 의존하기 전에 요약을 논문과 대조한다.

```sh
manuwright evidence import-obsidian kirtley1985influence
```

![Obsidian 참고문헌 가져오기](images/manual/43_obsidian_import_evidence.png)

## 4. 분석 계획, 승인, 분석

1. `data/analysis_plan.md` 를 쓴다: 연구 질문, 대상, 변수, 통계 방법, 유의수준과 다중비교, 결측 처리.
2. 저자가 읽고 승인한다. `- [x] 사용자 승인 완료` 에 직접 체크하거나, 채팅에서 "승인" 이라고 말하면 된다. 채팅 승인은 에이전트가 `manuwright approve data/analysis_plan.md --kind analysis --approved-by "저자 이름" --quote "승인"` 으로 기록한다(체크 + 누가·언제·무슨 말로 승인했는지 + 해시 영수증). 에이전트가 스스로 승인하지는 않는다.
3. 논문의 분석 환경을 한 번 만든다(`uv` 필요): `manuwright env`. `data/requirements.txt`(기본: pandas, numpy, scipy, statsmodels, matplotlib, openpyxl)로 uv 가 관리하는 Python 3.12 를 `~/.manuwright/envs/<논문>` 에 만들고(클라우드 동기화 폴더 밖), 정확한 버전을 Methods 용으로 `data/environment.lock.txt` 에 남긴다. 스크립트는 `manuwright run data/py/01_descriptive.py` 로 실행한다. 시스템·Homebrew·pyenv Python 이 깨져 있어도 상관없다.
4. 직접 체크한 경우 그 결정을 기록한다:

```sh
manuwright record-approval data/analysis_plan.md --kind analysis \
  --approved-by "저자 이름" --decision-reference "2026-09-30 회의"
```

그 전에는 에이전트가 분석 스크립트를 만들 수 없다:

![Plan-first 게이트](images/manual/04_plan_first_gate.png)

5. 스크립트는 `data/py/` 에 두고, 모든 수치는 `results/*.csv` 로 내보내며, 표는 CSV 에서 생성한다(표에 숫자를 손으로 치지 않는다). 그다음 검사한다:

```sh
manuwright numbers drafts/table_1.md drafts/table_2.md     # 시험에서는 50개, 실패 0
```

틀린 값은 가장 가까운 실제 값과 위치와 함께 잡힌다:

![수치 검사](images/manual/05_numbers_catches_wrong_value.png)

## 5. 원고 계획과 승인

`drafts/draft_plan.md` 를 채운다: 핵심 메시지, 논조, 용어 결정, 필수 참고문헌, 근거 공백, 주장-인용 매핑, 표·그림 계획, 서론·고찰 개요, 한계, 목표 분량. 승인은 같은 방식이다:

```sh
manuwright record-approval drafts/draft_plan.md --kind draft --approved-by "저자 이름" --decision-reference "..."
```

계획이 엔진 용어집의 금지어를 쓰기로 했다면(시험에서는 "MIS") 논문 전용 용어집을 둔다. 엔진의 `Style/terminology.md` 를 논문 폴더 `Style/` 로 복사해 해당 행을 고치고, `project.json` 에 `"terminology": "Style/terminology.md"` 를 넣는다. 그러면 `verify` 와 편집할 때 도는 lint hook 이 모두 그 용어집을 쓴다.

## 6. 학술 문체 모드

에이전트가 쓰는 문장을 처음부터 의학 학술지 말투로 맞추는 기능이다. 기본으로 켜져 있고, 논문 폴더(`manuwright init` 으로 만든 폴더) 안에서만 작동한다. 다른 프로젝트에서는 아무것도 하지 않는다.

**기준은 어디서 왔나.** 2019~2022년(생성형 AI 이전) JAMA Surgery, JAMA Network Open, Lancet, BMJ, Nature 의 공개 라이선스 원저 33편(약 18만 단어)을 측정했다. 프로그램에 든 것은 숫자와 여러 저널에 공통인 짧은 표현뿐이고, 논문 본문은 없다(`docs/academic_style/reference_profile.json`).

| 측정한 것 | 예 |
|---|---|
| 섹션별 평균 문장 길이 | Methods·Results 22~24 단어, Introduction·Discussion 27~28 단어 |
| 섹션별 수동태 비율 | Methods 63%, Results 24%, Introduction·Discussion 약 30% |
| 동사 선택 | "used" 345회 대 "utilized" 1회. "showed" 가 "demonstrated" 의 약 5배 |
| 한 번도 나오지 않은 말 | delve, underscore, showcase, leverage, "it is worth noting", "plays a crucial role" |

**작동 방식.**
1. 세션을 시작하면 핵심 카드가 에이전트에게 들어간다. 대화가 길어져 압축된 뒤와 서브에이전트에도 다시 들어간다.
2. "서론 써줘" 같은 요청에는 그 섹션 카드가 붙는다: 문단 구조(moves), 표현집, 모범 문단, 측정 목표치. 직접 보려면 `manuwright style card introduction` (한국어 `서론` 도 됨).
3. 원고 섹션(`drafts/01_` ~ `07_`)을 고칠 때마다 문장 검사 결과가 줄 번호와 함께 나온다.

![서론 써줘 에 붙는 섹션 카드](images/manual/60_section_card.png)

![편집마다 나오는 학술 문장 검사](images/manual/61_prose_check.png)


*MUST FIX* 는 측정한 논문에 없던 AI 말투, 축약형, 본문 굵은 글씨, 채팅 말투라 고친다. *consider* 는 제안이다(긴 문장, "crucial", "Notably" 등). 의도한 표현이면 그대로 둔다. 같은 내용을 쉬운 말로 쓴 정상 문단에는 아무것도 나오지 않는다.

**채팅으로 쓰는 법.** 명령어를 외울 필요는 없다.

| 이렇게 말하면 | 일어나는 일 |
|---|---|
| "서론 써줘", "고찰 다시 써줘", "제목 후보 몇 개 줘" | 그 섹션 카드를 읽고 씀 |
| "고쳐줘" | 검사 결과대로 수정 |
| "이 문단 학술적으로 바꿔줘" | `/style-pass` 절차로 변환한 뒤 사실이 바뀌지 않았는지 검사 |
| "이 폴더로 내 문체 배워줘" | `manuwright style learn <폴더>` |
| "내가 고친 거 배워줘" | `manuwright style edits` 로 규칙 제안 |
| "과장 표현 검사해줘" | `manuwright claim-strength drafts` |
| "학술 모드 엄격하게 해줘" / "학술 모드 꺼줘" / "학술 모드 켜줘" | 모드 전환(모든 논문에 적용) |

모드 전환은 "학술 모드 …"로 시작하는 짧은 요청에만 반응한다. "학술 모드 꺼지면 어떻게 돼?" 같은 질문이나 "현재 학술 모드는 off" 같은 문장으로는 바뀌지 않는다.

**세 가지 모드.** `manuwright mode` 로 지금 모드를 본다.

| 모드 | 하는 일 |
|---|---|
| `academic` (기본) | 카드를 주고, 편집 뒤 검사 결과를 알려 줌 |
| `strict` | *MUST FIX* 가 든 문장은 쓰기 자체를 막음. 고쳐 쓰면 통과 |
| `off` | 카드와 문장 검사를 끔. 용어 검사는 계속 |

![strict 모드의 차단](images/manual/62_strict_block.png)

**내 문체·목표 저널 문체 더하기 (선택).** 좋은 논문 3편 이상(내 논문, 분야의 landmark 논문, 목표 저널의 최근 논문; PDF·DOCX·MD·TXT)을 한 폴더에 넣는다.

```sh
manuwright style learn ~/papers/good
manuwright style status
```

섹션별 문장 길이, 수동태, hedging, 자주 쓰는 표현, 모범 문단을 측정해 모든 카드에 덧붙인다. 결과는 `~/.manuwright/library/writing/profile/` 에만 저장되고 논문 폴더나 git 으로 가지 않는다. 3편 미만이면 카드에 참고로만 보이고 검사 기준은 바꾸지 않는다. 쓸 수 있는 논문이 없어 학습이 실패해도 이전에 학습한 결과는 그대로 남는다.

**내가 고친 방식에서 배우기 (선택).** 에이전트 초안을 직접 고친 뒤:

```sh
manuwright style edits --git HEAD~1          # git 을 쓸 때. 아니면: manuwright style edits ai_draft.md my_edit.md
```

반복된 단어 바꾸기와 지우기가 `Style/pending_style_rules.md` 에 제안된다(P0 = 2번 이상). 저자가 체크한 규칙만 `manuwright style edits --apply` 로 `Style/terminology.md` 에 들어가고, 그다음부터 검사가 강제한다. 채팅으로 "demonstrated 규칙은 써"라고 승인하면 에이전트가 그 규칙 하나만 체크한다. 에이전트가 스스로 고르지는 않는다.

**문체를 고쳐도 사실은 그대로.** `manuwright style preserve 원문.md 수정본.md` 는 `[EVID:id]`, 숫자, *p* 값, Table/Figure 참조가 하나라도 바뀌면 실패한다. `/style-pass` 가 섹션마다 실행한다.

## 7. 여러 에이전트로 초고 쓰기

에이전트마다 섹션 하나, 같은 규칙, 끝내기 전에 돌릴 검사를 준다. 시험에서 쓴 프롬프트:

```text
Read AGENTS.md, drafts/draft_plan.md, data/analysis_plan.md, results/*.csv, drafts/table_*.md, knowledge/evidence.md.
Write ONLY drafts/05_results.md. Cite only [EVID:id] from evidence.md. Use only numbers from the results/tables.
The primary endpoint was not significant; never call it a trend. When done run
manuwright numbers drafts/05_results.md and manuwright citations drafts/05_results.md and fix until they pass.
```

| 에이전트 | 시험에서 맡은 섹션 | 결과 |
|---|---|---|
| Codex | Methods | 인용 검사 PASS. lint 경고에도 계획이 정한 "MIS" 를 유지함(v1.8.6 에서 수정) |
| Antigravity (`agy`) | Results | 수치 41/41 PASS. 파일을 읽을 때마다 허가를 물음. 논문 폴더 안의 읽기는 허가 |
| Muse | Introduction | 인용 검사 PASS |
| opencode | Discussion | 인용 PASS. 수치 "실패" 10건은 모두 문헌 수치였고, 인용한 초록에 실제로 있는 값 |

![Codex 가 Methods 작성](images/manual/10_codex_methods.png)

![Antigravity 가 Results 작성](images/manual/11_agy_results.png)

![opencode 가 Discussion 작성](images/manual/13_opencode_discussion.png)

Discussion 과 Introduction 에는 다른 논문의 수치가 들어간다. 이 파일들은 사유를 적어 결과 수치 검사에서 예외로 두고, semantic review 가 인용 근거와 대조하게 한다(8절).

승인된 계획 없이 쓰기를 막는 hook 은 Claude Code 와 Codex 에만 있다. Antigravity, opencode, Muse 에서는 `manuwright verify` 가 게이트다.

## 8. 초고 검증

시험의 `project.json` (요약):

```json
{
  "artifacts": ["drafts/01_title.md", "drafts/02_abstract.md", "drafts/03_introduction.md", "drafts/04_methods.md",
                "drafts/05_results.md", "drafts/06_discussion.md", "drafts/07_conclusion.md"],
  "tables": ["drafts/table_1.md", "drafts/table_2.md"],
  "abstract": "drafts/02_abstract.md",
  "numeric_artifacts": ["drafts/02_abstract.md", "drafts/05_results.md", "drafts/table_1.md", "drafts/table_2.md"],
  "numeric_exemptions": {
    "drafts/03_introduction.md": "Literature values; checked against cited evidence in semantic review.",
    "drafts/04_methods.md": "Design parameters (sample size, alpha, follow-up), not results.",
    "drafts/06_discussion.md": "Literature values from cited abstracts plus restated results."
  },
  "terminology": "Style/terminology.md",
  "review_sources": ["results/table1_baseline.csv", "results/table2_outcomes.csv", "results/group_counts.csv"]
}
```

```sh
manuwright verify --project project.json --profile draft
```

![draft profile PASS](images/manual/20_verify_draft_pass.png)

lint 지적(en dash, `p` 표기, Discussion 의 수치 과밀, 금지어)도 실패로 친다. 본문을 고치고, 용어집을 느슨하게 만들지 않는다.

투고 전에 두 가지를 더 돌린다.

```sh
manuwright lint --academic drafts      # 학술 문장 검사를 원고 전체에 한 번에 (6절의 검사와 같음)
manuwright claim-strength drafts       # 인용 문장이 근거 강도(3절)보다 센지
```

![과장 표현 검사](images/manual/63_claim_strength.png)

문장마다 가장 센 동사를 본다: hedged(may, suggest) < associative(was associated with) < directional(showed, reduced) < causal(demonstrated, caused). "차이가 없었다", "효과를 보이지 못했다" 같은 음성 결과는 센 표현으로 치지 않는다. 동사로 추정하는 검사이므로 최종 판단은 저자가 한다.

## 9. 독립 semantic review

결정적 검사는 숫자가 데이터에 있고 인용이 목록에 있다는 것까지만 증명한다. 문장의 의미가 맞는지는 모른다. 그래서 packet 을 만들어 다른 모델이나 사람에게 검토받는다:

```sh
manuwright packet --project project.json
```

검토자는 `review/semantic_review.json` 을 쓴다: status, reviewer, `method: independent`, 6개 검사, 지적 목록, packet 의 `dependencies` 원문. 시험에서 Codex 는 검사기로는 볼 수 없는 문제 13건을 찾았다. 예:
- 기저 ODI 가 50.6 대 46.8 인데 "기저 특성이 균형을 이뤘다"고 쓴 문장
- 초록에 없는 내용을 붙인 Tian 2013 인용
- 감압술 환자의 MCID 로 유합술 결과를 판단한 해석

![1차 검토](images/manual/30_codex_semantic_review.png)

고치고, packet 을 다시 만들고, 다시 검토받는다. Rule 9 는 자동 수정을 2회까지 허용하고, 그 뒤 결정은 저자에게 넘긴다. 시험에서는 2차에 13건 중 12건이 해결됐고, 남은 1건(배정 방식을 packet 으로 확인할 수 없음)은 저자에게 넘겼다.

![2차 검토](images/manual/31_codex_semantic_review_round2.png)

원고, 계획, CSV, 엔진 중 무엇이든 바뀌면 기존 검토는 stale 이 된다. packet 을 다시 만들어 다시 검토받는다.

### 9b. 다중 모델 critical review

위의 semantic review 가 게이트다. critical review 는 여러 검토자가 한꺼번에 가하는 추가 압박이다. 에이전트와 모델을 원하는 대로 고르고, 평소 조합은 한 번 저장해 둔다:

```sh
manuwright config set main-model claude-opus-5-5          # 글을 쓰는 모델
manuwright config set review.reviewers codex,opencode,muse,agy,openrouter
manuwright config set review.opencode-model opencode-go/kimi-k3
manuwright config set review.openrouter-models deepseek/deepseek-v4-pro,qwen/qwen3.7-max
manuwright critical-review --target drafts/05_results.md --out review/critical
# 이번만 다른 조합:  --reviewers codex,agy:<모델>,openrouter:<모델 id>
```

로컬 검토자는 빈 임시 폴더에서 읽기 전용이나 plan 모드로 돌아 논문을 건드리지 않는다. main 모델과 같은 모델을 쓰는 검토자는 `not_independent` 로 표시된다. OpenRouter 모델로 보내는 글은 내 컴퓨터 밖으로 나가므로 저자의 동의를 먼저 받는다. 시험에서 검토자 8명이 모두 전체 검토를 돌려줬고, 모두 reject 였다. 합성 데이터로 만든 소프트웨어 시험 원고이니 올바른 판단이다.

![검토자 8명](images/manual/45_multi_reviewer_run.png)

## 10. 제출

```sh
manuwright verify --project project.json --profile submission
```

![submission profile BLOCKED](images/manual/21_verify_submission_blocked.png)

제출에는 다음이 더 필요하다:
- `result_bindings`: 수치 파일의 모든 숫자를 결과, 군, 시점, 단위와 함께 CSV 칸에 연결한 기록
- `semantic_review`: status PASS 이고 남은 지적이 없는 검토
- `human_signoff`: 실제 사람의 결정과 그 근거
- `ai_usage`: 어떤 AI 가 무엇을 했는지, 사람이 확인한 기록
- `checklist`: 보고 체크리스트(CONSORT, STROBE, PRISMA, CARE)와 항목별 위치

시험에서 가장 손이 많이 간 부분:

- **바인딩.** 숫자 155개를 연결했다. 대부분은 CSV 칸 하나와만 일치했고, 나머지(여러 개의 `120`, `60`, `p < 0.001` 등)는 문장을 읽고 직접 정했다. 수동 지정은 토큰 순서 번호가 아니라 "파일:줄:숫자:몇 번째" 로 적는다. 순서 번호는 문장이 바뀌면 밀린다. 자동으로 연결된 것도 점검한다: 값이 하나뿐이어도 이름표가 틀릴 수 있다. 합계(예: 전체 120명)는 엉뚱한 칸에 연결하지 말고 결과에 합계 행("All")을 추가한다.
- **체크리스트.** 현재 공식 체크리스트를 받아(시험에서는 CONSORT-SPIRIT 사이트의 CONSORT 2025) 항목마다 위치나 사유를 적고, 독립 검토자가 확인하게 한다. 검토자는 26번을 두 번 반려했고, 군별 요약과 위험차·위험비의 CI 를 보고한 뒤에 통과했다. 새 분석은 매번 분석 계획 수정안 승인을 받았고 post hoc 로 표시했다.
- **검토 라운드.** 총 7회였고 마지막 두 번은 지적이 없었다. Rule 9 의 자동 2회를 넘으면 저자의 결정으로만 계속한다.

![6차 검토: 6개 차원 모두 PASS](images/manual/32_codex_semantic_review_round6_pass.png)

그 뒤에 무엇이든 고치면 검토와 서명은 의도대로 stale 이 된다. 시험에서는 서명 뒤 참고문헌 문장부호를 고치자 정확히 그렇게 됐고, 검토와 서명을 다시 받았다.

![수정 후 stale 이 된 검토](images/manual/22_stale_after_edit.png)

그다음 `manuwright build --project project.json` 이 DOCX 패키지를 만든다(원고, 표지, 표별 파일, `verification.json`, 출력 해시). 먼저 모든 것을 다시 검사하고, stale 입력은 거부한다. 제출 전에 파일을 열어 눈으로 확인한다.

![submission PASS 와 빌드](images/manual/23_submission_pass_build.png)

## 11. Revision: 응답 편지를 가린 재검토

리뷰어 코멘트를 받은 뒤의 순서다. 세부 규칙은 [revision_guide.md](revision_guide.md).

1. 코멘트를 `review/reviewer_comments_REV1.md` 에 이 형식으로 저장한다. 번호가 있어야 아래 도구가 코멘트를 하나씩 셀 수 있다.

```text
Reviewer #1:
Comment 1) Please report the follow-up rate.
Comment 2) Define leg pain.
```

2. 고친 섹션만 `drafts/revision/REV1/` 에 `_REV1` 을 붙여 저장한다(예: `04_methods_REV1.md`). 응답 편지는 같은 폴더의 `response_letter_REV1.md` 다. 원고를 고쳤다고 쓰는 응답에는 `[CHANGE]` 블록을 붙인다.

```text
Comment 2) Define leg pain.

[CHANGE]
comment_id: R1-C2
claim: defined the leg pain scale anchors
section: 04_methods
expected_terms: worst pain
[/CHANGE]

Response: We thank the reviewer and defined the scale.

Revised text:
"Leg pain was measured with a 0-10 numeric rating scale (0, no pain; 10, worst pain)."
```

3. **블라인드 재검토.** 검토자가 응답 편지를 먼저 읽으면 저자의 설명에 끌려간다. 그래서 편지를 빼고 먼저 판정한다.

```sh
manuwright blind-review packet --comments review/reviewer_comments_REV1.md \
  --revised drafts/revision/REV1 --out review/blind_REV1
```

packet 에는 코멘트, 원본과 수정본 섹션, diff 가 들어가고 응답 편지는 빠진다. 검토자(다른 모델이나 사람)는 `review/blind_REV1/verdicts.md` 를 단계 순서대로 채운다.

| 단계 | 보는 것 | 적는 것 |
|---|---|---|
| Phase 1 | 코멘트만 | 제대로 고쳤다면 원고에 무엇이 있어야 하는지(`expectation`) |
| Phase 2A | 원본, 수정본, diff (편지 없음) | 판정(FULLY, PARTIALLY, NOT_ADDRESSED, MADE_WORSE, CANNOT_VERIFY)과 원고의 근거 위치(`anchor`) |
| Phase 2B | 이제 편지까지 | 최종 판정. 바꾸면 이유(`author_pointer`, `valid_rebuttal`, `scope_correction`)를, 올렸으면 수정본의 위치(`final_anchor`)를 적음 |

```sh
manuwright blind-review check review/blind_REV1/verdicts.md
```

모든 코멘트가 FULLY 나 PARTIALLY 이고 기록에 빈칸이 없어야 PASS 다. 편지에만 있고 원고에는 없는 변경은 통과하지 못한다. 이 PASS 뒤에 phase 8 게이트에 `response_alignment` 를 기록한다.

![블라인드 재검토: 편지 때문에만 올린 판정은 실패](images/manual/64_blind_review.png)

4. **응답서 점검과 revision 검증.**

```sh
manuwright response-coverage drafts/revision/REV1/response_letter_REV1.md --comments review/reviewer_comments_REV1.md
manuwright revision-claims drafts/revision/REV1/response_letter_REV1.md
manuwright verify --project project.json --profile revision
```

`response-coverage` 는 모든 코멘트에 응답이 있는지, `revision-claims` 는 `[CHANGE]` 로 고쳤다고 한 내용이 수정본에 실제로 있는지 본다. 시험에서는 둘 다 `PASS` 였다.

![응답서 점검](images/manual/65_revision_checks.png)

## 12. 업데이트

```sh
manuwright update --check
manuwright update                         # 설치 후 `manuwright agents update` 까지 실행(--no-agents 로 생략)
manuwright config set auto-update on      # patch 릴리스만, 하루 최대 1회
manuwright init --refresh-rules --all     # 등록된 모든 논문: 에이전트 규칙만 갱신 (update 가 물어봄)
manuwright check                          # 최신 상태를 한 화면에 점검, ✗ 마다 고치는 명령
```

`check` 는 학술 문체 모드와 학습한 문체가 있는지도 보여 준다. 에이전트 규칙(`AGENTS.md`/`CLAUDE.md`/`GEMINI.md`)이 바뀌는 릴리스(v1.9.0 등) 뒤에는 `manuwright init --refresh-rules --all` 을 꼭 실행한다.

등록된 논문이 엔진을 고정했거나(`project.json` 의 `"engine": ">=1.8,<1.9"`), 엔진이 바뀌면 무효가 될 유효한 검토가 있으면 자동 업데이트는 기다린다. 되돌리기: `manuwright update --to <버전>`.

Windows 에서 uv 로 설치했다면 `manuwright update` 는 직접 설치하지 않고 명령을 출력한다(실행 중인 `manuwright.exe` 는 Windows 에서 교체할 수 없다). 에이전트 세션을 닫고 새 PowerShell 창에 붙여 넣는다: `uv tool install --force git+https://github.com/grotyx/Academic_writing_c_claudecode@vX.Y.Z; if ($?) { manuwright agents update }` (설치 후 에이전트 어댑터까지 갱신). 업데이트 후 `manuwright update` 는 `manuwright init --refresh-rules` 가 필요한 등록된 논문 폴더 목록을 보여 준다. 이전 업데이트 후 `ModuleNotFoundError: No module named 'manuwright'` 가 나오면 같은 명령으로 복구된다.

업데이트가 잘 됐는지 확인:

```sh
manuwright --version                 # CLI 버전과 엔진 폴더
manuwright update --check            # 최신 릴리스면 "(up to date)"
claude plugin marketplace list       # manuwright 경로 = --version 이 출력한 엔진 폴더
codex plugin marketplace list        # 같은 경로
```

재설치 때 엔진 폴더가 바뀔 수 있다(예: `.../python3.11/site-packages/manuwright` → `.../python3.12/...`). `manuwright agents update` 는 Claude·Codex marketplace 를 현재 폴더로 다시 등록하므로 지워진 경로를 가리키지 않는다. `agents update` 뒤에도 에이전트가 다른 플러그인 버전을 말하면 그 에이전트를 재시작한다.

### 설정

`manuwright setup` 하나로 아래 설정을 차례로 묻는다. 모델은 입력하지 않고 메뉴에서 고른다. 메인 모델은 목록에서 하나(또는 "other"), 에이전트 검토자(Claude Code, Codex, Muse, Antigravity/Gemini: 로그인한 구독으로 실행, API 비용 없음)·OpenRouter 모델(사용량 과금)·opencode 모델(opencode Go 구독)은 체크리스트다. ↑/↓ 이동, Space 선택, Enter 완료, Esc 는 지금 설정 유지, 숫자 키는 추천 세트로 체크리스트를 채운다(OpenRouter: 1 balanced, 2 budget, 3 strong / opencode: 1 Go, 2 Go budget). 목록은 GLM, Kimi, MiniMax, DeepSeek, Qwen, Xiaomi MiMo, Meituan LongCat 최신 모델이고, 실시간 목록으로 제공 여부와 검토 1회 예상 비용(대부분 약 $0.002–0.05)을 함께 보여 준다. 대화형 터미널이 아니거나 Windows 에서는 같은 세트를 번호로 고른다. 메인 모델 목록은 각 모델을 실행하는 에이전트 CLI 의 설치 여부("Claude Code installed", "Codex not installed")를 표시하고, 실행할 수 있는 모델을 먼저 보여 준다. 번호를 입력하거나, 목록에 없는 모델은 모델 id 를 입력한다. `claude` 같은 에이전트 이름은 모델이 아니므로 안내와 함께 다시 묻는다. OpenRouter 모델을 고르면 OpenRouter API 키를 묻는다(입력은 `****` 로 표시, 입력 후 `sk-or-v1...abcd` 형태로 확인 표시, OpenRouter 로 유효성 확인, `~/.manuwright/secrets.json` 에 본인만 읽을 수 있게 저장, Ctrl+V 로 붙여넣고, 붙여넣기가 전달되지 않는 터미널(PowerShell 을 띄운 Windows Terminal)에서는 키를 복사한 뒤 빈 입력에서 Enter 를 누르면 클립보드에서 읽음; `OPENROUTER_API_KEY` 환경 변수가 있으면 그것을 우선 사용). 같은 세트는 `manuwright models` 로 언제든 볼 수 있다. 무료·contributor 등급은 입력을 학습에 쓸 수 있어 뺐다(검토는 미발표 원고를 보낸다). 그리고(Enter 는 그대로, `-` 는 지움), 마지막에 Obsidian 라이브러리를 제안한다. 하나만 바꿀 때는 `manuwright config set <키> <값>`.

![manuwright setup](images/manual/50_setup.png)

| 키 | 뜻 |
|---|---|
| `main-model` | 원고를 쓰는 모델. 이 모델을 쓰는 검토자는 표시됨 |
| `review.reviewers` | 기본 검토자, 예: `codex,opencode,muse,agy,openrouter` |
| `review.openrouter-models` | `openrouter` 만 적었을 때 쓸 모델들 |
| `review.<agent>-model` | `claude`, `codex`, `opencode`, `muse`, `agy` 각각의 모델 |
| `auto-update` | `on`/`off`: 자동 patch 업데이트 |
| `docx.font`, `docx.size`, `docx.line-spacing`, `docx.margin-inches`, `docx.heading-size`, `docx.subheading-size` | 내 기본 Word 스타일(기본값 Times New Roman 10pt, 줄 간격 2배, 여백 1인치) |
| `docx.line-numbers`, `docx.page-numbers` | `continuous`/`page`/`off`, `center`/`right`/`off` |

`manuwright config` 로 설정을 보고, `manuwright config unset <키>` 로 지운다.

### 논문별 설정: 목표 저널과 Word 스타일

참고문헌 형식과 Word 서식은 전체 설정이 아니라 논문마다 정한다. 논문 폴더 안에서:

```sh
manuwright target
```

메뉴로 두 가지를 묻고 그 논문의 `project.json` 에만 저장한다: 목표 저널(아래 프리셋 중 하나, 또는 없음)과 Word 스타일(그대로 / 기본값 / 이 논문만의 글꼴·크기·줄 간격·여백·줄 번호·쪽 번호). 다른 논문에는 영향이 없다. 검토 뒤에 바꾸면 다른 `project.json` 수정과 마찬가지로 그 검토는 stale 이 된다. `setup` 은 이제 Word 스타일을 묻지 않는다(위 `docx.*` 키는 선택 사항인 개인 기본값으로만 남음).

### 개인 라이브러리: Word 스타일, 팀 정보, 글쓰기 스타일

여러 논문에 다시 쓰는 것은 어느 폴더에서 명령하든 한 곳, `~/.manuwright/library/` 에 모인다. `manuwright library` 로 무엇이 있는지 본다. 넣는 파일은 복사되므로 원본은 옮겨도 된다. 같은 이름이 있으면 `--replace` 를 붙이지 않는 한 덮어쓰지 않는다. 각 논문은 자기 사본을 갖는다(Word 서식 파일은 논문의 `templates/` 로 복사). 그래서 나중에 라이브러리를 바꿔도 기존 논문은 그대로다.

```sh
manuwright library docx add bjj_template.docx --name bjj --journal bjj   # 특정 저널용 Word 서식 파일
manuwright library docx add lab_template.docx --name lab --team          # 또는 팀용(--team)·개인용(--personal)
manuwright library docx save bjj                                         # 또는 지금 논문의 서식을 저장
manuwright library profile --edit                           # 팀 정보: 저자·소속·ORCID·연구비
manuwright library profile --import profile/authors.md      # 기존 파일 재사용
manuwright library writing add my_2024_paper.pdf --kind own   # 내 문체를 보여 주는 논문
manuwright library writing import Style/                      # 기존 Style/ 폴더 가져오기
```

- **Word 스타일.** Word 서식은 보통 목표 저널에 따라 정해지므로 저널용(`--journal`), 팀용(`--team`), 개인용(`--personal`)으로 저장한다. 논문 폴더에서 `docx save` 를 하면 그 논문의 저널에 연결된다. `manuwright target` 에서 저널을 고르면 그 저널용으로 저장한 서식이 맨 위에 미리 선택돼 나오고, 팀·개인 서식이 뒤에 나온다. Word 서식 파일은 그 파일의 글꼴·제목 스타일·여백을 그대로 쓴다(서식 파일 안의 글은 버리고 스타일만 사용). 그 위에 따로 정한 것(예: 줄 번호)만 바꾼다.
- **팀 정보.** 새 논문마다 `profile/authors.md` 로 복사되고 title page 는 이걸로 쓴다. 에이전트에게 "이 CV 로 manuwright 팀 정보 채워줘" 라고 해도 된다. 라이브러리 파일만 고치고, ORCID·연구비 번호는 추측하지 않으며, 모르는 칸은 `[...]` 로 둔다.
- **글쓰기 스타일.** `manuwright library writing import Style/` 에서 `writing` 은 명령어, `Style/` 은 가져올 폴더(여기서는 템플릿 저장소의 Style 폴더)다. 논문에서 문체를 뽑아내는 건 LLM 이 할 일이다. `writing add` 다음 에이전트에게 "manuwright 라이브러리에 내 글쓰기 스타일 등록해줘" 라고 하면 manuwright skill 이 `Style/style_guide.md` 기준으로 패턴과 측정값(문장 길이, 인용 밀도)을 뽑는다. 문단 복사는 하지 않는다. 그 결과로 앵커 파일, `terminology.md`, `style_spec.md` 를 만든다. 새 논문은 이걸 `Style/` 로 받아 `/style-pass` 와 용어 검사에 쓴다. 원본 PDF 는 라이브러리에만 남는다.

### 저널 참고문헌 형식

`manuwright target` 에서 고른 목표 저널(또는 `project.json` 의 `"journal"`)에 맞춰 빌드가 참고문헌 형식과 본문 인용 표시(위첨자를 쓰는 저널은 위첨자)를 만든다.

```sh
manuwright format-references drafts/*.md --journal nejm --fetch   # PubMed 전체 서지를 한 번 캐시하고 목록 미리보기
```

```json
"journal": "nejm"
```

![저널 참고문헌 형식](images/manual/51_journal_references.png)

`--fetch` 를 쓰면 저자를 모두 적는 JBJS 에서 Nakarai 2022 의 저자 11명이 모두 들어간다(등록된 인용문은 6명에서 끊겨 있었음). NEJM 은 3명으로 줄이고 권호를 빼고 페이지를 줄여 쓰며, 붙어 있는 인용 태그는 위첨자 하나로 묶인다.

프리셋: `vancouver`, `ama`(JAMA), `nejm`, `lancet`, `spine`, `spine-j`, `bjj`, `jbjs`, `neurospine`, `jns-spine`, `gsj`, `corr`, `asj`, `esj`. 저널별 규칙은 [harness_guide.md](harness_guide.md) 표 참고. 제출 전에 저널의 최신 투고 규정을 한 번 확인할 것.

## 13. 문제 해결

| 증상 | 원인과 해결 |
|---|---|
| 승인된 계획 없이 섹션이 써짐 | hook 은 Claude Code 와 Codex 에만 있음. 템플릿은 v1.8.5 이상으로 올릴 것(상대 경로 hook 이 `cd` 후 실패했음). Codex 는 plugin hook 신뢰. 나머지는 `manuwright verify` 실행 |
| Codex 의 `Hooks need review` | plugin hook 이 새로 생기거나 바뀜. 확인 후 manuwright hook 신뢰 |
| lint 가 계획에서 정한 용어를 잡음 | 논문 전용 `Style/terminology.md` 를 두고 `project.json` 의 `terminology` 에 지정 |
| `one or more declared artifacts are missing: ...` | `project.json` 이 아직 없는 섹션을 가리킴. `artifacts` 수정 |
| Discussion 의 수치가 실패 | 문헌 수치임. `numeric_exemptions` 에 사유를 적고 semantic review 에서 확인 |
| 검토가 stale 이 됨 | 검토 대상 파일 중 무엇인가 바뀜. packet 을 다시 만들어 재검토 |
| plugin 과 CLI 버전 경고 | `manuwright agents update` 후 에이전트 재시작 |
| `Obsidian MCP is unavailable` | Obsidian 에서 vault 를 열고 Settings > Academic Paper Citation Manager > External AI (MCP) 를 켠 뒤 에이전트의 MCP 연결을 다시 시작 |
| 새 vault 에서 플러그인이 안 뜸 | Obsidian 제한 모드: 그 vault 에서 커뮤니티 플러그인을 허용 |
| agy 가 MCP 나 검토에서 빈 출력 | headless 모드는 도구 허가를 줄 수 없음. 대화형으로 쓰거나, 글로만 답하게 하는 내장 검토 프롬프트에 맡김 |
| 검토자가 `not_independent` | `main-model` 과 같은 모델을 씀. 그 검토자의 모델을 바꿈 |
| `BLOCKED by workflow gate (CLAUDE.md Rule 8): ...draft_plan.md: ...` | 메시지 뒷부분이 이유를 말함: 몇 번째 줄의 빈칸이 남음, 승인 체크가 안 됨, 비어 있는 항목, 승인 뒤 계획서를 고침(바뀐 점을 보여 주고 다시 승인) |
| 섹션 카드나 문장 검사가 안 나옴 | 논문 폴더 밖이거나 모드가 `off`. 논문 폴더에서 `manuwright mode` 확인 |
| `BLOCKED by academic writing mode (strict)` | strict 모드에서 *MUST FIX* 문장을 씀. 고쳐 쓰거나 "학술 모드 켜줘"로 academic 으로 |
| 모드를 바꿨는데 그대로 | 환경 변수 `MANUWRIGHT_WRITING_MODE` 가 우선함. 지우면 저장된 설정이 적용됨 |
| 학습한 문체가 검사에 반영 안 됨 | 3편 미만이거나 섹션 제목을 못 찾음. `manuwright style status` 와 learn 출력의 skipped 줄 확인 |
| `search audit` 이 PubMed 에 접속하지 못함 | 인터넷 연결 확인 후 같은 명령을 다시 실행 |
| `blind-review packet` 이 코멘트가 없다고 함 | 코멘트를 `Reviewer #1:` 아래 `Comment 1) ...` 형식으로 다시 저장 |

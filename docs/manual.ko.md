# manuwright 사용자 매뉴얼 (v1.0.0)

빈 폴더에서 검증된 초고까지 논문 하나를 따라가는 매뉴얼이다. 합성 임상시험 데이터로 실제로 돌려 본 end-to-end 시험(2026-09-30)의 명령과 출력을 그대로 썼다. 규칙은 [WORKFLOW.md](../WORKFLOW.md), 명령 세부는 [harness_guide.md](harness_guide.md), 영어판은 [manual.md](manual.md).

스크린샷은 시험 중 각 에이전트 터미널의 텍스트를 이미지로 렌더링한 것이다(세션에 macOS 화면 기록 권한이 없었음). 도구가 실제로 출력한 내용과 같다.

## 1. 설치와 점검

```sh
uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@v1.8.7
manuwright doctor                  # python_supported, hooks.ok, warnings 확인
manuwright agents install --dry-run
manuwright agents install          # Claude Code, Codex, Antigravity, opencode, Muse
```

plugin 을 설치·업데이트한 뒤에는 Claude Code 를 재시작한다. Codex 는 폴더에서 처음 실행할 때 plugin hook 을 신뢰할지 묻는다. manuwright hook 4개에 "Trust all" 을 고른다. 설치하지 않는 템플릿 사용자는 clone 한 저장소 안에서 같은 엔진을 `python -m harness ...`, `python scripts/<tool>.py ...` 로 쓴다.

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

나온 항목을 `knowledge/evidence.md` 에 붙이고, 요약 칸은 실제로 읽은 내용으로 채운다. 전문을 읽기 전까지는 `Source Status: abstract-only` 로 둔다. 여기에 등록된 ID 만 `[EVID:miller_2020_pmid31476471]` 형식으로 인용할 수 있다.

## 4. 분석 계획, 승인, 분석

1. `data/analysis_plan.md` 를 쓴다: 연구 질문, 대상, 변수, 통계 방법, 유의수준과 다중비교, 결측 처리.
2. 저자가 읽고 `- [x] 사용자 승인 완료` 에 체크한다. 에이전트는 절대 체크하지 않는다.
3. 그 결정을 기록한다:

```sh
manuwright record-approval data/analysis_plan.md --kind analysis \
  --approved-by "저자 이름" --decision-reference "2026-09-30 회의"
```

그 전에는 에이전트가 분석 스크립트를 만들 수 없다:

![Plan-first 게이트](images/manual/04_plan_first_gate.png)

4. 스크립트는 `data/py/` 에 두고, 모든 수치는 `results/*.csv` 로 내보내며, 표는 CSV 에서 생성한다(표에 숫자를 손으로 치지 않는다). 그다음 검사한다:

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

## 6. 여러 에이전트로 초고 쓰기

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

Discussion 과 Introduction 에는 다른 논문의 수치가 들어간다. 이 파일들은 사유를 적어 결과 수치 검사에서 예외로 두고, semantic review 가 인용 근거와 대조하게 한다(7절).

승인된 계획 없이 쓰기를 막는 hook 은 Claude Code 와 Codex 에만 있다. Antigravity, opencode, Muse 에서는 `manuwright verify` 가 게이트다.

## 7. 초고 검증

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

## 8. 독립 semantic review

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

## 9. 제출

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

## 10. 업데이트

```sh
manuwright update --check
manuwright update && manuwright agents update
manuwright config set auto-update on      # patch 릴리스만, 하루 최대 1회
```

등록된 논문이 엔진을 고정했거나(`project.json` 의 `"engine": ">=1.8,<1.9"`), 엔진이 바뀌면 무효가 될 유효한 검토가 있으면 자동 업데이트는 기다린다. 되돌리기: `manuwright update --to <버전>`.

## 11. 문제 해결

| 증상 | 원인과 해결 |
|---|---|
| 승인된 계획 없이 섹션이 써짐 | hook 은 Claude Code 와 Codex 에만 있음. 템플릿은 v1.8.5 이상으로 올릴 것(상대 경로 hook 이 `cd` 후 실패했음). Codex 는 plugin hook 신뢰. 나머지는 `manuwright verify` 실행 |
| Codex 의 `Hooks need review` | plugin hook 이 새로 생기거나 바뀜. 확인 후 manuwright hook 신뢰 |
| lint 가 계획에서 정한 용어를 잡음 | 논문 전용 `Style/terminology.md` 를 두고 `project.json` 의 `terminology` 에 지정 |
| `one or more declared artifacts are missing: ...` | `project.json` 이 아직 없는 섹션을 가리킴. `artifacts` 수정 |
| Discussion 의 수치가 실패 | 문헌 수치임. `numeric_exemptions` 에 사유를 적고 semantic review 에서 확인 |
| 검토가 stale 이 됨 | 검토 대상 파일 중 무엇인가 바뀜. packet 을 다시 만들어 재검토 |
| plugin 과 CLI 버전 경고 | `manuwright agents update` 후 에이전트 재시작 |

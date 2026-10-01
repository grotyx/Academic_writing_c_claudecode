# Critical-Review Protocol (외부 멀티모델 적대적 검토) (v1.1.1)

> 완성된 원고/response를 여러 리뷰어가 적대적으로 공격해 허점을 발굴하는 절차의 단일 기준. `/critical-review` command와 `qc_guide.md`는 이 문서를 참조한다. QC Round 6 Critical Review의 외부 멀티모델 강화판.
> 공개 운영 기준은 이 문서가 원본입니다. 내부 설계 노트 경로는 런타임 의존성으로 두지 않습니다.

## 0. 원칙

- **review-only** — 허점을 발굴만 하고 자동 수정하지 않는다.
- **합의는 검토 우선순위** — 모델들이 같은 오류를 공유할 수 있으므로 사실 판정은 원자료와 대조한다.
- **폴백** — OpenRouter/Codex가 안 돼도 Claude 서브에이전트 단독으로 가능. 막히지 않는다.

## 1. 절차

```
1. 대상 결정    기본 전체 원고 / 지정 부분 / revision: response letter + 원고
2. 리뷰어 선택  AskUserQuestion 멀티 선택 — OpenRouter 4종(MiniMax M3·GLM 5.2·Qwen3-Max·DeepSeek V4 Pro) 중 ~2개 권장 + Claude/Codex. 최소 1개
3. 병렬 공격
     - Claude     → (Claude Code) Agent(새 서브에이전트, fresh context) + §2 적대 프롬프트
                    (Codex/셸) python scripts/critical_review.py --target <file> --include-claude
                    → 로컬 `claude -p` 헤드리스로 Claude 리뷰 호출
     - Codex      → (Claude Code) codex-rescue(read-only) / (셸) codex exec + §2 적대 프롬프트
     - OpenRouter → python scripts/critical_review.py --target <file>
                    --models-file scripts/critical_models.txt --role <role>
                    --out review/critical/<run>/  (필요 시 --include-claude 동시 사용)
4. 종합(메인)   중복 통합(합의도) + 심각도 분류(Critical/Important/Minor)
5. 저장         review/critical/YYYYMMDD_<slug>.md (통합 리포트) + 모델별 원본
```

## 2. 적대 프롬프트 (대상별)

프롬프트 본문은 `scripts/critical_prompts/<role>.txt`에 **단일 정본**으로 둔다 (`manuscript.txt`, `response.txt`). OpenRouter 스크립트·Claude 서브·Codex 모두 이 파일을 출처로 쓴다. 프롬프트를 바꾸려면 이 파일만 수정한다.

- `manuscript.txt` — 원고를 적대적으로 공격 (overclaiming·방법론·논리 비약·일반화·재현성).
- `response.txt` — reviewer rebuttal 검토 (만족 여부·재반박 지점).
- `editor.txt` — **editor desk-screen** (§5).

(스크립트: `--role manuscript|response|editor`로 해당 파일 선택. Claude/Codex 호출 시에도 같은 `.txt` 본문을 프롬프트로 사용.)

## 3. 종합 — 합의도 × 심각도

통합 리포트는 각 허점을 **심각도(Critical/Important/Minor)** 와 **합의도(몇 명의 리뷰어가 지적했는지)** 로 정렬한다. 여러 리뷰어가 동의한 허점을 위로. 단독 지적은 "다양성 참고"로 표기.

## 4. 에러 / 폴백

| 상황 | 처리 |
|------|------|
| `OPENROUTER_API_KEY` 없음 | OpenRouter만 skip, 나머지 리뷰어로 진행 + 알림 |
| 특정 모델 실패 | 그 모델만 skip (스크립트가 처리), 나머지 계속 |
| Codex 실패 | Codex skip, 나머지 계속 |
| 리뷰어 0개 | 에러(최소 1개 필요) |

## 5. Editorial desk-screen (`editor` role, `/editor-review`)

기계적 QC·reviewer 적대 검토를 넘어 **편집장·임상 관점의 실질 평가**다: *이 논문이 임상적으로 타당한가, 분야 high-impact 저널 scope에 맞는가, 무엇을 추가해야 경쟁력이 생기는가, 안 되면 어느 하위 저널이 현실적인가.* 저자가 정한 target 저널이 아니라 **논문 주제 분야를 식별해 그 분야 high-impact 저널의 실제 게재물**을 기준으로 벤치마크한다(상위 tier 기준 = 의도적으로 높은 bar).

- **정본 프롬프트:** `scripts/critical_prompts/editor.txt` (5단계: 분야·벤치마크 식별 → 임상타당성 → scope/novelty → 방법·분석 적절성 → WHAT TO ADD + desk-screen 판정).
- **판정:** `SEND FOR PEER REVIEW` / `BORDERLINE` / `DESK REJECT` (at high-impact tier). DESK REJECT면 현실적 하위·specialty 저널을 근거와 함께 추천.
- **실행 — `/critical-review`와 동일한 리뷰어 선택 UX** (`AskUserQuestion`: OpenRouter ×4 + Claude + Codex, role만 `editor`):
  - `Claude`만 선택 = 단일 **Opus 서브에이전트** (fresh context에 `editor.txt`, API 키 불필요).
  - `Codex` = `codex:codex-rescue` read-only에 `editor.txt`.
  - OpenRouter = `python scripts/critical_review.py --target <file> --role editor --models <…>` (또는 `--include-claude`).
  - 즉 모델 풀·선택 방식은 §1·§2의 reviewer 검토와 같고, 프롬프트만 `editor.txt`다.
- **벤치마크 강화(선택):** medical-kag MCP 연결 시 `search`/`compare_interventions`/`best_evidence`로 해당 분야 high-impact 문헌의 설계·n·근거수준을 끌어와 근거화. 미연결 시 LLM 지식 + `search_pubmed.py`.
- **성격:** grounded 게이트가 **아니라** 판정형 평가(임상·분야 지식 사용). **advisory** — 게이트를 대체하지 않는다. 수치·인용 grounding은 여전히 `check_numbers`/`check_citations` 담당. Phase 6에서 사용.
- 에러·폴백은 §4와 동일.

## v1.7.0 provider execution

See `harness_guide.md`. Missing OpenRouter credentials do not cancel CLI reviewers. `--include-codex` and repeatable `--context` are available. `--out` now creates unique run subdirectories with `run.json` (requested/completed/failures/source hashes). Partial results are advisory, never an automatic gate PASS. Authorize each external destination and input scope before calling it.

## v1.8.8 reviewer choice and settings

Reviewers are `agent[:model]` specs, so any model the user can reach may review:

```sh
python scripts/critical_review.py --target drafts/manuscript.md --role manuscript --out review/critical \
  --reviewers codex,opencode:opencode-go/kimi-k3,muse,agy,openrouter:deepseek/deepseek-v4-pro
```

| Spec | Runs | Safety |
|---|---|---|
| `openrouter:<id>` (or a bare OpenRouter id) | OpenRouter API, any model | needs `OPENROUTER_API_KEY`; text leaves the machine |
| `claude[:model]` | `claude -p --tools ""` | no tools |
| `codex[:model]` | `codex exec --sandbox read-only` | read-only sandbox |
| `opencode[:provider/model]` | `opencode run --agent plan` | read-only plan agent |
| `muse[:model]` | `muse exec` | no read-only mode: empty workspace, web tools and personal context off |
| `agy[:model]` | `agy --mode plan --sandbox -p` | plan mode, sandbox |

Every local CLI runs in an empty temporary folder, so it never sees the paper folder; the prompt asks for a text-only answer (headless CLIs cannot ask for tool permission).

Defaults come from the user's settings, so a plain `--target ... --out ...` uses them:

```sh
manuwright config set main-model claude-opus-5-5                   # the model that writes
manuwright config set review.reviewers codex,opencode,muse,agy,openrouter
manuwright config set review.opencode-model opencode-go/kimi-k3    # any opencode provider/model
manuwright config set review.openrouter-models deepseek/deepseek-v4-pro,qwen/qwen3.7-max
manuwright config set review.codex-model gpt-6-astra                # optional per agent
```

A bare `openrouter` expands to `review.openrouter-models` (default `scripts/critical_models.txt`, the "balanced" set). The OpenRouter key comes from `OPENROUTER_API_KEY` or, if unset, the key `manuwright setup` saved in `~/.manuwright/secrets.json` (owner-only). Recommended sets for OpenRouter and opencode, with live availability and cost per review: `manuwright models`; pick one by number in `manuwright setup`. A reviewer whose model equals `main-model` is reported in `run.json` as `not_independent` with a warning: the writing model reviewing itself is not an independent review. `--models`, `--models-file`, `--include-claude` and `--include-codex` keep working.

Tested 2026-09-30 on the synthetic demo manuscript: Codex, opencode (kimi-k3), Muse, Antigravity and four OpenRouter models all returned full reviews (1,000-2,700 words each).


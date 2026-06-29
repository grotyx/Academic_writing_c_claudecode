---
description: high-impact 저널 편집장 관점 desk-screen 평가 (임상 타당성·scope fit·추가검증; docs/critical_review_protocol.md §5)
args: target
---

**언제 사용:** 작성 후(Phase 6 QC). 기계적 QC를 넘어, **이 논문이 임상적으로 타당한가 / 논문 분야의 high-impact 저널 scope에 맞는가 / 무엇을 추가해야 경쟁력이 생기는가 / 안 되면 어느 하위 저널이 현실적인가**를 편집장·임상 관점에서 평가하고 싶을 때. `/critical-review`(reviewer 적대 검토)의 자매 — 이건 **editor desk-screen(상위 tier 기준)**.

대상: **$ARGUMENTS** (생략 시 전체 원고)

평가 기준은 `scripts/critical_prompts/editor.txt`(정본 프롬프트, `--role editor`)와 `docs/critical_review_protocol.md` §5. 핵심: 저자가 정한 target 저널이 아니라 **논문 주제 분야를 식별해 그 분야 high-impact 저널의 실제 게재물 기준**으로 벤치마크.

절차 (`/critical-review`와 **동일한 리뷰어 선택 UX**, role만 `editor`):

1. 대상 텍스트를 확정한다.
2. (선택·권장) **벤치마크 강화** — medical-kag MCP가 연결돼 있으면 `search`/`compare_interventions`/`best_evidence`로 해당 분야 high-impact 문헌의 설계·n·근거수준을 끌어와 "그 저널들이 실제로 뭘 싣는지"의 근거로 삼는다. 미연결 시 LLM 지식 + `scripts/search_pubmed.py`로 대체.
3. 리뷰어(편집장)를 `AskUserQuestion`으로 선택받는다 (multiSelect, 최소 1개). **`/critical-review`와 같은 풀**을 개별 옵션으로 제시하고 **~2개 선택을 권장**한다(비용·다양성 — 서로 다른 계열로):
   - `minimax/minimax-m3` · `z-ai/glm-5.2` · `qwen/qwen3.7-max` · `deepseek/deepseek-v4-pro` (OpenRouter, `scripts/critical_models.txt`)
   - `Claude` (Claude Code면 서브에이전트 / Codex·셸이면 `--include-claude`) · `Codex`
   - **빠른 단일 평가:** `Claude`만 선택 = 단일 Opus 서브에이전트(API 키 불필요).
4. 병렬 desk-screen — **선택된 리뷰어만**, 전부 `editor.txt` + (있으면 2단계 벤치마크):
   - Claude → (Claude Code) Agent 새 서브에이전트(fresh context)에 `editor.txt` 투입 / (Codex·셸) `--include-claude`.
   - Codex → `codex:codex-rescue` read-only에 `editor.txt` 프롬프트.
   - OpenRouter → `python scripts/critical_review.py --target <file> --role editor --models <선택 모델 콤마구분> --out review/critical/<run>/` (전체 풀: `--models-file scripts/critical_models.txt`).
5. 메인 Claude가 종합(§3): editor.txt 5단계 구조로 통합 — 분야·벤치마크 / 임상타당성 / scope·novelty / 방법·분석 적절성 / **WHAT TO ADD + desk-screen 판정**(SEND / BORDERLINE / DESK REJECT) + (하위 tier가 현실적이면 추천 저널). 합의도 × 심각도로 정렬.
6. `review/critical/`에 통합 리포트 + 모델별 원본 저장.
7. 에러·폴백은 `docs/critical_review_protocol.md` §4 (외부 실패해도 Claude 단독 진행).

> **주의:** 이건 grounded 게이트가 아니라 **판정형 평가**(임상·분야 지식 사용). 결과는 advisory — 게이트를 대체하지 않는다. 수치·인용은 여전히 `check_numbers`/`check_citations`로 grounding.

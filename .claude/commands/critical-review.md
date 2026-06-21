---
description: 외부 멀티모델 적대적 critical review (작성 후, docs/critical_review_protocol.md)
args: target
---

**언제 사용:** 작성 후(Phase 6 QC·Phase 8), 원고나 response letter를 외부 멀티모델 적대적 검토에 부치고 싶을 때.

`docs/critical_review_protocol.md`를 기준으로 critical review를 수행한다.

대상: **$ARGUMENTS** (생략 시 전체 원고; revision 맥락이면 response letter + 원고)

절차:

1. 대상 텍스트를 확정한다(프로토콜 §1).
2. 리뷰어를 `AskUserQuestion`으로 선택받는다 (multiSelect, 최소 1개). **OpenRouter 모델 4종을 개별 옵션으로 제시**하고 **~2개 선택을 권장**한다(비용·다양성 — 서로 다른 계열로):
   - `minimax/minimax-m3` · `z-ai/glm-5.2` · `qwen/qwen3.7-max` · `deepseek/deepseek-v4-pro` (OpenRouter, `scripts/critical_models.txt`)
   - `Claude` (Claude Code면 서브에이전트 / Codex·셸이면 `--include-claude`) · `Codex`
3. 병렬 공격(프로토콜 §1·§2) — **선택된 리뷰어만**:
   - Claude → (Claude Code) Agent 새 서브에이전트(fresh context) / (Codex·셸) `--include-claude`.
   - Codex → `codex:codex-rescue` read-only에 적대 프롬프트.
   - OpenRouter → `python scripts/critical_review.py --target <file> --models <선택 모델 콤마구분> --role <manuscript|response> --out review/critical/<run>/` (전체 풀을 쓰려면 `--models-file scripts/critical_models.txt`).
4. 메인 Claude가 종합(§3): 중복 통합 + 심각도 분류.
5. `review/critical/`에 통합 리포트 + 모델별 원본 저장(§1, 템플릿 `_TEMPLATE.critical.md`).
6. 에러·폴백은 §4를 따른다(외부 실패해도 Claude 단독으로 진행).

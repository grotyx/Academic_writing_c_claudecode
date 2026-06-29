---
description: high-impact 저널 편집장 관점 desk-screen 평가 (임상 타당성·scope fit·추가검증; docs/critical_review_protocol.md §5)
args: target
---

**언제 사용:** 작성 후(Phase 6 QC). 기계적 QC를 넘어, **이 논문이 임상적으로 타당한가 / 논문 분야의 high-impact 저널 scope에 맞는가 / 무엇을 추가해야 경쟁력이 생기는가 / 안 되면 어느 하위 저널이 현실적인가**를 편집장·임상 관점에서 평가하고 싶을 때. `/critical-review`(reviewer 적대 검토)의 자매 — 이건 **editor desk-screen(상위 tier 기준)**.

대상: **$ARGUMENTS** (생략 시 전체 원고)

평가 기준은 `scripts/critical_prompts/editor.txt`(정본 프롬프트)와 `docs/critical_review_protocol.md` §5. 핵심: 저자가 정한 target 저널이 아니라 **논문 주제 분야를 식별해 그 분야 high-impact 저널의 실제 게재물 기준**으로 벤치마크.

절차:

1. 대상 텍스트를 확정한다.
2. (선택·권장) **벤치마크 강화** — medical-kag MCP가 연결돼 있으면 `search`/`compare_interventions`/`best_evidence`로 해당 분야 high-impact 문헌의 설계·n·근거수준을 끌어와 "그 저널들이 실제로 뭘 싣는지"의 근거로 삼는다. 미연결 시 LLM 지식 + `scripts/search_pubmed.py`로 대체.
3. 평가 실행 — 다음 중 하나(또는 둘 다):
   - **단일 Opus 서브에이전트** (API 키 불필요): `editor.txt` 프롬프트 + (있으면) 2단계 벤치마크를 fresh context Agent에 투입.
   - **멀티모델 panel** (다양한 편집장 관점, OpenRouter 키 또는 로컬 Claude CLI 필요): `python scripts/critical_review.py --target <file> --role editor --models <콤마구분> --out review/critical/<run>/` (전체 풀: `--models-file scripts/critical_models.txt`; 키 없으면 `--include-claude`로 로컬 Claude만).
4. 출력은 editor.txt의 5단계 구조를 따른다 — 분야·벤치마크 / 임상타당성 / scope·novelty / 방법·분석 적절성 / **WHAT TO ADD + desk-screen 판정**(SEND / BORDERLINE / DESK REJECT) + (하위 tier가 현실적이면 추천 저널).
5. 종합 리포트를 `review/critical/`에 저장(모델별 원본 포함).
6. 에러·폴백은 `docs/critical_review_protocol.md` §4 (외부 실패해도 Claude 단독 진행).

> **주의:** 이건 grounded 게이트가 아니라 **판정형 평가**(임상·분야 지식 사용). 결과는 advisory — 게이트를 대체하지 않는다. 수치·인용은 여전히 `check_numbers`/`check_citations`로 grounding.

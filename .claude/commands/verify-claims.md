---
description: 초안의 각 [EVID:id] 문장을 근거와 대조해 SUPPORTED/PARTIAL/UNSUPPORTED 분류 리포트 (GraphRAG 주, evidence.md 보조)
args: section
---

**언제 사용:** Phase 6 QC — 인용 문장이 실제로 근거에 의해 지지되는지 **문장별** 점검 (check_citations의 존재 확인보다 한 단계 깊음).

`docs/citation_assist_protocol.md` Operation 2를 따른다.

대상: **$ARGUMENTS** (생략 시 drafts의 본문 섹션들)

1. **claim 추출:** `py scripts\extract_claims.py <section> --json` → `[EVID:id]` 문장 목록.
2. **근거 회수:** 각 `[EVID:id]`의 출처 내용 — medical-kag(KAG 주: 구조화 데이터/chunk) 또는 evidence.md 항목(보조).
3. **분류 (Semantic-Citation Verifier):** `docs/verifier_prompt_templates.md`로 (문장, 근거) → **SUPPORTED / PARTIAL / UNSUPPORTED** + 1줄 사유·조치.
4. **리포트:** `review/claim_verification.md`에 `위치 | claim | [EVID:id] | 판정 | 조치` 표. PARTIAL/UNSUPPORTED는 수정 대상(주장 약화·인용 교체·근거 보강).

---
description: claim에 맞는 [EVID:id] 출처 제안 (medical-kag GraphRAG 주, evidence.md 보조)
args: claim
---

**언제 사용:** Phase 3(claim→citation mapping) / Phase 4(drafting)에서, 어떤 주장에 맞는 근거를 찾을 때.

`docs/citation_assist_protocol.md` Operation 1을 따른다.

대상 claim: **$ARGUMENTS**

1. **검색 (KAG 주):** medical-kag `search` (action `evidence`/`evidence_chain`/`best_evidence`)로 claim 근거 후보 → 근거수준 포함 랭킹.
2. **Fallback (KAG 불가):** `knowledge/evidence.md` 스캔으로 매칭 항목 찾기 → 없으면 `py scripts\search_pubmed.py search "<claim 키워드>"`.
3. **등록 후 인용:** evidence.md에 없는 후보는 `[EVID:author_year]`로 등록(PMID/DOI 확인, `docs/evidence_guide.md`).
4. **출력:** 후보 `[EVID:id]` 랭킹 + 각 1줄 근거(방향·대상·중재·결과). **사용자가 고름 — 자동 삽입 금지.**

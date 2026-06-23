---
description: 논문들을 항목별 비교표(included studies)로 — Discussion/PRISMA supplement (GraphRAG 주, evidence.md 보조)
args: topic_or_ids
---

**언제 사용:** Discussion 비교 작성 또는 systematic review의 "included studies" 표 산출.

`docs/citation_assist_protocol.md` Operation 4를 따른다.

대상: **$ARGUMENTS** (주제 또는 `[EVID:id]` 목록)

1. **구조화 데이터 수집:** KAG 주 — medical-kag `analyze` 필드 / `compare_interventions`(design·n·intervention·outcome·effect·p·근거수준). evidence.md 보조(요약 기반, 거침).
2. **JSON 레코드 → 표:** `py scripts\evidence_table.py <records.json> --columns study,design,n,intervention,outcome,result,loe`.
3. **저장:** `drafts/table_evidence.md`(또는 supplement). **모든 수치는 원문 대조**(grounding — KAG 값은 빈/노이즈 가능, evidence.md/results가 정본).

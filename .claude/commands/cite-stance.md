---
description: 인용 출처가 claim을 지지/반박/언급하는지 분류 (Discussion 균형·overclaim 가드; GraphRAG 주, evidence.md 보조)
args: claim_or_section
---

**언제 사용:** Discussion 작성/QC 시, 인용이 한쪽으로 치우치지 않았는지(균형) 점검.

`docs/citation_assist_protocol.md` Operation 3을 따른다.

대상: **$ARGUMENTS** (claim 한 줄, 또는 섹션 파일)

1. **claim·인용 식별:** 섹션이면 `py scripts\extract_claims.py <section> --json`로 `[EVID:id]` 문장 추출.
2. **근거 회수 + 반박 탐색:** 각 출처 회수(KAG 주/evidence.md 보조). medical-kag `conflict find/detect`로 **빠진 반박 연구** 탐색.
3. **stance 분류:** `docs/verifier_prompt_templates.md`의 Citation-Stance로 각 출처 → **supporting / contrasting / mentioning** + 사유.
4. **출력:** stance 요약 + **one-sided 경고**(반박 근거가 있는데 인용 안 됐으면) = overclaim-by-omission 가드. claim·출처는 모두 evidence.md `[EVID:id]` 기준.

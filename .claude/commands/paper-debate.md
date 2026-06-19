---
description: Claude와 Codex가 co-author로 주제를 토론·합의 (작성 전, docs/debate_protocol.md)
args: topic
---

`docs/debate_protocol.md`를 기준으로 다음 주제에 대해 Claude–Codex co-author 토론을 수행한다.

주제: **$ARGUMENTS**

절차:

1. 인자에서 단계를 추론(planning | stats | logic | revision, 없으면 균형 비평자). `docs/debate_protocol.md` §3 표에서 역할·초점 결정.
2. R0: 주제에 대한 내 접근·골격(입장) + 근거를 작성.
3. 프로토콜 §1·§4에 따라 라운드 진행: 각 라운드에서 `codex:codex-rescue`를 read-only로 호출(§4 프롬프트 템플릿), 1라운드 `--fresh` / 이후 `--resume`. 매 라운드 끝에 §2로 수렴 판정.
4. 합의(또는 상한 도달) 시 §5 형식으로 `review/debates/`에 로그를 남기고, 합의를 바탕으로 산출물을 작성/수정.
5. Codex 실패·미합의 시 §6 폴백을 따른다(워크플로 막지 않음).

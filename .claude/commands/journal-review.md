---
description: 특정 저널 적합성 리뷰(scope fit) 또는 저널 추천 — PubMed 게재 기록 + 저널 규정 + 그 저널 편집자 관점 (docs/critical_review_protocol.md §6)
args: journal
---

**언제 사용:** 투고 전. "이 논문이 Spine J 에 맞나?", "어느 저널에 낼까?" — `/editor-review`(분야 최상위 tier 기준)와 달리 **특정 저널 하나**(또는 후보 목록)를 기준으로 본다.

대상 저널: **$ARGUMENTS** (생략 시 `manuwright target` 으로 정한 저널, 그것도 없으면 추천 모드)

1. 논문의 대상·중재/노출·결과로 PubMed 검색어(4-8 단어)를 만든다.
2. 저널 profile 확인: `manuwright journal fit "<저널>" --no-review` 가 "No journal profile" 을 출력하면 `manuwright journal profile "<NLM 약어>" --url <공식 Aims & Scope / Guide for Authors>` 로 만들고, 공식 페이지를 직접 읽어 Aims and scope · Article types · Limits(숫자) · Required 를 채운다. 저자에게 보여 주고 확인받은 뒤에만 `verified_by_author: yes`.
3. 적합성 리뷰: `manuwright journal fit "<저널>" --query "..."` — 저자가 저장한 리뷰어(`manuwright setup`)로 실행. 리뷰어가 없으면 `review/journal/<run>/packet.md` 를 `scripts/critical_prompts/journal.txt` 로 새 서브에이전트가 검토.
4. 추천: `manuwright journal suggest --query "..." [--mine] [--review]` (`--mine`: 저자 목록 `manuwright journal list` 의 저널만; 목록이 없으면 `manuwright journal list --build --preset ortho-neuro` 로 만든다) — 비슷한 연구가 많이 실린 저널 순위(건수 근거, 저자 목록 표시) → 상위 후보에 `journal fit`.
5. 판정(FIT / BORDERLINE / NOT A FIT), 가장 중요한 수정점, 후보 저널을 건수와 함께 보고한다. profile 에 없는 규정·IF·채택률은 말하지 않는다.

> advisory: 게이트를 대체하지 않는다. PubMed 에는 검색어만 가고, 원고는 저자가 고른 리뷰어에게만 간다.

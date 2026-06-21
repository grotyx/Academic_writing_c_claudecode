---
description: 초안을 bound 학술/저널 스타일로 섹션별 변환 + Style Verifier (docs/style_transform_protocol.md)
args: scope
---

**언제 사용:** Phase 5(Style Polish) 또는 revision 재작성에서, 초안을 지정 exemplar의 학술 스타일로 변환할 때. ("학술적으로 바꿔줘" 류 입력 시 `scripts/hooks/style_intent.py` 훅이 자동으로 이 protocol을 띄운다.)

`docs/style_transform_protocol.md`를 기준으로 수행한다.

대상 범위: **$ARGUMENTS** (생략 시 사용자에게 전체/특정 섹션 확인)

절차:

1. **Style Spec 확인** — `drafts/style_spec.md`(멀티페이퍼는 서브폴더) 없으면 `AskUserQuestion`으로 bind할 exemplar 선택(`Style/own/` 또는 `Style/target_journal/`) → `docs/style_spec_template.md` 복사·작성 → 사용자 확인.
2. **범위 확정** — 전체 vs 특정 섹션. 조용히 전부 갈아엎지 않는다.
3. **섹션별 변환** — 각 섹션마다 Spec + 해당 exemplar 섹션 + `writing_guide` 규칙 로드 → 구조·문장 길이·hedging·claim 강도·레퍼런스 형식·voice 변환. claim·수치는 grounding 유지(날조 금지).
4. **Style Verifier** — 각 섹션을 Spec과 대조(`docs/verifier_prompt_templates.md` Style-Conformance) → FAIL 시 자율 수정 루프(최대 2회) → 미해결은 에스컬레이션. `lint_on_edit.py` 훅이 용어·표기 잔여를 자동 표면화.
5. **기록** — `review/gates/phase_05_style.GATE.md`에 `style` PASS 기록 → `check_gate.py --verify-hash`.

# Gate Ledger Template

> 각 게이트 통과/실패를 기록한다. Phase별로 복사하여 사용:
> `review/gates/phase_04_draft.GATE.md` 등.
> 규칙: 어떤 섹션/단계도 여기에 status: PASS 줄이 없으면 다음으로 진행 금지.

## Entry 형식

```
phase: Phase 4 — Draft Sections
artifact: drafts/05_results.md
status: PASS              # PASS | FAIL
checks:
  constraint: PASS
  citation: PASS
  numbers: PASS
round: 2                  # 1차 FAIL → 수정 → 2차 PASS (최대 2회)
blocking_failures: none   # FAIL 시 미해결 지적사항 요약
verifier_model: opus
timestamp: 2026-06-16T14:30:00+09:00
```

## 예시 (FAIL 후 에스컬레이션)

```
phase: Phase 4 — Draft Sections
artifact: drafts/06_discussion.md
status: FAIL
checks:
  constraint: PASS
  citation: FAIL
  numbers: PASS
round: 2
blocking_failures: EVID:lee_2019 direction mismatch (UNSUPPORTED) — 사용자 확인 필요
verifier_model: opus
timestamp: 2026-06-16T15:10:00+09:00
```

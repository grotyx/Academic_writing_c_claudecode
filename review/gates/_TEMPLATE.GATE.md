# Gate Ledger Template

Copy this file for each phase or artifact gate, for example:

- `review/gates/phase_03_draft_plan.GATE.md`
- `review/gates/phase_04_draft.GATE.md`
- `review/gates/phase_08_revision.GATE.md`

Do not proceed to the next section or phase until the relevant gate file passes
`scripts/check_gate.py`.

## Required Machine-Readable Block

Use one key-value block per artifact. Keep field names unchanged.

```yaml
phase: Phase 4 - Draft Sections
artifact: drafts/05_results.md
status: PASS              # PASS | FAIL
checks:
  constraint: PASS
  citation: PASS
  numbers: PASS
  logic: PASS
round: 2                  # max 2 fix/re-verify attempts
blocking_failures: none
verifier_model: opus
timestamp: 2026-06-18T10:30:00+09:00
```

## Required Check Names

Use these exact keys so `check_gate.py --require-check <name>` can verify them:

| Check key | Source |
|---|---|
| `constraint` | Constraint-Compliance verifier |
| `citation` | `scripts/check_citations.py` plus semantic citation verifier when needed |
| `numbers` | `scripts/check_numbers.py` |
| `logic` | Logic/redundancy verifier |
| `revision_claims` | `scripts/check_revision_claims.py` |
| `response_alignment` | reviewer response vs manuscript alignment verifier |

## Command Examples

Draft section gate:

```powershell
py scripts\check_gate.py review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic
```

Revision gate:

```powershell
py scripts\check_gate.py review\gates\phase_08_revision.GATE.md --require-check revision_claims --require-check response_alignment --require-check citation --require-check numbers
```

## FAIL Example

```yaml
phase: Phase 4 - Draft Sections
artifact: drafts/06_discussion.md
status: FAIL
checks:
  constraint: PASS
  citation: FAIL
  numbers: PASS
  logic: FAIL
round: 2
blocking_failures: unsupported citation in paragraph 3; repeated Results sentence in Discussion
verifier_model: opus
timestamp: 2026-06-18T11:10:00+09:00
```

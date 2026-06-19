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
provenance:               # sha256 of the state this PASS was earned against
  artifact: 0d6f...e3a1   # py scripts\check_gate.py --compute-hash drafts\05_results.md
  evidence: 7b2c...90ff   # sha256 of knowledge/evidence.md at verify time
  results: a14e...c8d2    # sha256 of the results CSV the numbers were traced to
round: 2                  # max 2 fix/re-verify attempts
blocking_failures: none
verifier_model: opus
timestamp: 2026-06-18T10:30:00+09:00
```

> Note: `check_gate.py` parses `status`, `artifact`, `round`, the `checks.*` keys, and the
> `provenance.*` keys. `blocking_failures`, `verifier_model`, and `timestamp` are human-audit
> fields only — keep them for the record, but the script does not read or validate them.

## Freshness / Provenance (stale-gate guard)

A PASS is only valid for the artifact state it was earned against. Without this, a
section can pass the gate, then be edited (e.g. to fix one verifier's finding), and the
old PASS silently survives — its numbers or citations no longer re-checked. This is the
main risk once the four verifiers run **in parallel**: a fix applied after a co-verifier
already returned PASS leaves that PASS stale.

Mechanism:

1. When the gate passes, record the sha256 of each source-of-truth file under `provenance:`.
   Compute hashes with the built-in helper:

   ```powershell
   py scripts\check_gate.py --compute-hash drafts\05_results.md
   ```

2. At gate-check time, re-hash and compare with `--verify-hash LABEL=PATH` (repeatable). A
   changed file fails the gate as a **stale gate**, forcing re-verification:

   ```powershell
   py scripts\check_gate.py review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts\05_results.md
   ```

The `--verify-hash` flag is opt-in at the **tool** level (omit it and the gate behaves exactly as
before — backward compatible). At the **workflow** level it is **standard practice**: the section
and revision gate commands below include `--verify-hash`, so a PASS that no longer matches its
source files fails as stale. Record `provenance.artifact` on every PASS. Also record and verify
`provenance.evidence` (`knowledge/evidence.md`) for citation-bearing gates and `provenance.results`
(the relevant CSV) for numbers-bearing gates. For revision (Phase 8) gates evidence/results are
**required** — a revision round routinely changes the upstream sources a prior PASS depended on.

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

Draft section gate (with freshness — `results` because this section carries numbers):

```powershell
py scripts\check_gate.py review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts\05_results.md --verify-hash results=results\table2_outcomes.csv
```

Revision gate (evidence + results freshness required — a revision round changes both):

```powershell
py scripts\check_gate.py review\gates\phase_08_revision.GATE.md --require-check constraint --require-check revision_claims --require-check response_alignment --require-check citation --require-check numbers --verify-hash artifact=drafts\revision\REV1\05_results_REV1.md --verify-hash evidence=knowledge\evidence.md --verify-hash results=results\table2_outcomes.csv
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

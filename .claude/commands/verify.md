---
description: Run all deterministic verification checks (citations + numbers + gate)
args: artifacts and flags
---

**When to use:** before recording a phase gate `status: PASS` — run the deterministic checkers (citation grounding + number grounding + gate ledger) in one shot.

Run the combined verifier on the given artifacts:

`py scripts\verify_all.py $ARGUMENTS`

Example (Phase 4 section gate):

`py scripts\verify_all.py drafts\05_results.md drafts\table_1.md --results results --evidence knowledge\evidence.md --gate review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts\05_results.md --verify-hash results=results\table2_outcomes.csv`

Report each check's PASS/FAIL and the overall verdict. On FAIL, fix the flagged items first — do **not** record `status: PASS` until every check passes. This complements the LLM verifiers (Constraint/Logic), which `verify_all.py` does not run.

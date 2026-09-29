---
description: Run all deterministic verification checks (citations + numbers + gate)
args: artifacts and flags
---

**When to use:** before recording a phase gate `status: PASS` — run the deterministic checkers (citation grounding + number grounding + gate ledger) in one shot.

Run the combined verifier on the given artifacts:

`python scripts/verify_all.py $ARGUMENTS`

Example (Phase 4 section gate):

`python scripts/verify_all.py drafts/05_results.md drafts/table_1.md --results results --evidence knowledge/evidence.md --gate review/gates/phase_04_draft.GATE.md --artifact drafts/05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts/05_results.md --verify-hash results=results/table2_outcomes.csv --cross-check citation=drafts/05_results.md --cross-check numbers=drafts/05_results.md`

Always pass `--cross-check citation=...` and `--cross-check numbers=...` for the gated artifact: they re-run the live checkers against the ledger, so a PASS written without running them (or gone stale) is rejected. Add a `--verify-hash` for every source the verdict relied on.

Report each check's PASS/FAIL and the overall verdict. On FAIL, fix the flagged items first — do **not** record `status: PASS` until every check passes. This complements the LLM verifiers (Constraint/Logic), which `verify_all.py` does not run.

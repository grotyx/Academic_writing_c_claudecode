---
name: paperflow
description: Medical manuscript workflow with the paperflow engine. Use when planning, drafting, revising or checking a paper in a folder that has project.json, drafts/draft_plan.md or knowledge/evidence.md, or when the user mentions paperflow, draft plan, analysis plan, evidence.md, EVID citations, reviewer response or submission build.
---

# paperflow workflow

1. Load the rules for the current step: `paperflow rules <keyword>` (for example `Citation Integrity`, `Draft Plan`, `Verification Gates`, `Phase 4`). Run `paperflow rules` once for the full workflow when the phase is unclear.
2. Phase order: setup and evidence, then analysis plan (approved), analysis, draft plan (approved), drafting (Methods, Results, Introduction, Discussion, Conclusion, Abstract, Title), style polish, QC (3+ rounds), finalize, revision.
3. Plan first. If `drafts/draft_plan.md` or `data/analysis_plan.md` is missing, incomplete or not approved by the author, stop and help complete it. Never tick `- [x] 사용자 승인 완료` yourself.
4. Grounding. Cite only `[EVID:id]` keys in `knowledge/evidence.md` and use only numbers in `results/*.csv`. Register new sources in `evidence.md` (verified PMID/DOI) before citing them: `paperflow search "<query>"`.
5. Verify before saying a step is done (see the `paperflow-verify` skill).
6. Guides live in the engine: `paperflow rules --path` shows where `WORKFLOW.md` is; the `docs/` folder next to it holds the protocols.

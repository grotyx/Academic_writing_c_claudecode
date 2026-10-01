---
name: manuwright
description: Medical manuscript workflow with the manuwright engine. Use when planning, drafting, revising or checking a paper in a folder that has project.json, drafts/draft_plan.md or knowledge/evidence.md, or when the user mentions manuwright, draft plan, analysis plan, evidence.md, EVID citations, reviewer response or submission build.
---

# manuwright workflow

1. Load the rules for the current step: `manuwright rules <keyword>` (for example `Citation Integrity`, `Draft Plan`, `Verification Gates`, `Phase 4`). Run `manuwright rules` once for the full workflow when the phase is unclear.
2. Phase order: setup and evidence, then analysis plan (approved), analysis, draft plan (approved), drafting (Methods, Results, Introduction, Discussion, Conclusion, Abstract, Title), style polish, QC (3+ rounds), finalize, revision.
3. Plan first. If `drafts/draft_plan.md` or `data/analysis_plan.md` is missing, incomplete or not approved by the author, stop and help complete it. Never tick `- [x] 사용자 승인 완료` yourself.
4. Grounding. Cite only `[EVID:id]` keys in `knowledge/evidence.md` and use only numbers in `results/*.csv`. Register new sources in `evidence.md` (verified PMID/DOI) before citing them: `manuwright search "<query>"`.
5. Verify before saying a step is done (see the `manuwright-verify` skill).
6. Guides live in the engine: `manuwright rules --path` shows where `WORKFLOW.md` is; the `docs/` folder next to it holds the protocols.

## Personal library (reused across papers)

`manuwright library` shows where it is (`~/.manuwright/library/`, or `$MANUWRIGHT_HOME/library`). New papers get copies from it at `manuwright init`; Word styles are chosen per paper in `manuwright target`.

**"Register my writing style"** (the author added papers with `manuwright library writing add <pdf|md> --kind own|landmark|target_journal`):
1. Read the engine's `Style/style_guide.md` (folder next to `manuwright rules --path`) and follow its Extraction Framework and copyright policy: patterns, metrics and short phrases, never copied paragraphs.
2. For each source in `library/writing/PDF/<kind>/` without a matching `library/writing/<kind>/<same basename>.md`, write that markdown anchor.
3. Measure instead of guessing: run `manuwright style extract <text or md files>` for sentence length and citation density, and put those numbers in the anchors.
4. Update `library/writing/terminology.md` (preferred and forbidden terms with context) and write `library/writing/style_spec.md` from the engine's `docs/style_spec_template.md`, bound to the author's own papers.
5. Show the author a short summary of the voice you found and the files you wrote; do not change any paper folder.

**"Fill my team profile"** (from a CV, author list or earlier title page the author gives you): edit `library/profile/authors.md` (`manuwright library profile` creates it from the template). Copy names, degrees, affiliations, ORCID, emails and grant numbers exactly as given; leave `[...]` placeholders for anything not given; never guess an ORCID or grant number. Ask the author to check it. Papers created later copy it to `profile/authors.md`; an existing paper keeps its own copy.

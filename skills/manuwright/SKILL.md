---
name: manuwright
description: Medical manuscript workflow with the manuwright engine. Use when planning, drafting, revising or checking a paper in a folder that has project.json, drafts/draft_plan.md or knowledge/evidence.md, or when the user mentions manuwright, draft plan, analysis plan, evidence.md, EVID citations, reviewer response or submission build.
---

# manuwright workflow

1. Load the rules for the current step: `manuwright rules <keyword>` (for example `Citation Integrity`, `Draft Plan`, `Verification Gates`, `Phase 4`). Run `manuwright rules` once for the full workflow when the phase is unclear.
2. Phase order: setup and evidence, then analysis plan (approved), analysis, draft plan (approved), drafting (Methods, Results, Introduction, Discussion, Conclusion, Abstract, Title), style polish, QC (3+ rounds), finalize, revision.
3. Plan first. If `drafts/draft_plan.md` or `data/analysis_plan.md` is missing, incomplete or not approved by the author, stop and help complete it. Show the plan to the author. When they approve it explicitly in chat ("승인", "approve"), record it with `manuwright approve <plan> --kind analysis|draft --approved-by "<author>" --quote "<their exact words>"` (ticks the box, notes who/when/what, writes the hashed receipt). Never approve on your own judgement or from a general "continue".
4. Grounding. Cite only `[EVID:id]` keys in `knowledge/evidence.md` and use only numbers in `results/*.csv`. Register new sources in `evidence.md` (verified PMID/DOI) before citing them: `manuwright search "<query>"`.
5. Analysis code runs in the paper's own environment: `manuwright env` (once; uv-managed Python with the packages in `data/requirements.txt`), then `manuwright run data/py/<script>.py`. Do not install packages into, or debug, the system/Homebrew/pyenv Python; add packages to `data/requirements.txt` and rerun `manuwright env`. Cite the versions in `data/environment.lock.txt` in Methods.
6. Verify before saying a step is done (see the `manuwright-verify` skill).
7. Academic writing: before drafting or rewriting a section, run `manuwright style card <section>` and write to that card (moves, rules, phrasebank, register of the model paragraphs, the author's learned corpus style). Never reuse the model paragraphs' facts, numbers or citations. Fix the academic-prose findings reported after each edit; in `strict` mode a write with high-severity findings is blocked until rewritten. After a style rewrite of existing text, `manuwright style preserve <before> <after>` must print OK.
8. Guides live in the engine, not in the paper folder: read any `docs/<name>.md` the rules cite with `manuwright guide <name>` (several at once allowed; `manuwright guide` lists them). Every `manuwright rules` output ends with the guides it cites; read the ones for the current step in full before doing it.

## Personal library (reused across papers)

`manuwright library` shows where it is (`~/.manuwright/library/`, or `$MANUWRIGHT_HOME/library`). New papers get copies from it at `manuwright init`; Word styles are chosen per paper in `manuwright target`.

**"Register my writing style"** (the author added papers with `manuwright library writing add <pdf|md> --kind own|landmark|target_journal`):
1. Read the engine's `Style/style_guide.md` (folder next to `manuwright rules --path`) and follow its Extraction Framework and copyright policy: patterns, metrics and short phrases, never copied paragraphs.
2. For each source in `library/writing/PDF/<kind>/` without a matching `library/writing/<kind>/<same basename>.md`, write that markdown anchor.
3. Measure instead of guessing: run `manuwright style learn` (it reads the library PDFs, or pass files) so every section card carries the measured style and model paragraphs, and `manuwright style extract <text or md files>` for sentence length and citation density in the anchors.
4. Update `library/writing/terminology.md` (preferred and forbidden terms with context) and write `library/writing/style_spec.md` from the engine's `docs/style_spec_template.md` (`manuwright guide style_spec_template`), bound to the author's own papers.
5. Show the author a short summary of the voice you found and the files you wrote; do not change any paper folder.

**"Fill my team profile"** (from a CV, author list or earlier title page the author gives you): edit `library/profile/authors.md` (`manuwright library profile` creates it from the template). Copy names, degrees, affiliations, ORCID, emails and grant numbers exactly as given; leave `[...]` placeholders for anything not given; never guess an ORCID or grant number. Ask the author to check it. Papers created later copy it to `profile/authors.md`; an existing paper keeps its own copy.

# Agent Instructions

Before doing any work, read `CLAUDE.md` in full. `CLAUDE.md` is the authoritative project instruction file; this `AGENTS.MD` file only summarizes non-negotiable rules for agent startup.

This repository is an academic manuscript-writing workflow. Treat `CLAUDE.md` as the source of truth for project structure, phase rules, citation integrity, statistical-analysis requirements, drafting order, QC, and finalization. If this file and `CLAUDE.md` ever conflict, follow `CLAUDE.md`.

## Core Rules

- Read and follow `CLAUDE.md` before making workflow, manuscript, analysis, or documentation changes.
- Do not fabricate references, citations, statistics, patient counts, p-values, confidence intervals, or journal requirements.
- Check `knowledge/evidence.md` before citing literature or adding new references.
- Keep reference evidence under `knowledge/`; keep writing-style material under `Style/`.
- Do not commit copyrighted PDFs or private/local style-anchor summaries.
- Commit public workflow files such as `Style/style_guide.md`, `Style/terminology.md`, documentation, templates, and scripts when appropriate.

## Protected Local Files

Never stage or commit these unless the user explicitly overrides the rule:

- `knowledge/pdf/`
- `Style/PDF/**/*.pdf`
- `Style/PDF/**/*.PDF`
- `Style/own/*.md` except `Style/own/example_*.md`
- `Style/landmark/*.md`
- `Style/target_journal/*.md`
- `profile/`

## Manuscript Workflow

- Do not run statistical analysis before an approved `analysis_plan.md` exists.
- Do not draft manuscript sections before an approved `draft_plan.md` exists.
- Draft sections in the order defined by `CLAUDE.md`: Methods, Results, Introduction, Discussion, Conclusion, Abstract, Title.
- Apply terminology rules from `Style/terminology.md` during drafting and polishing.
- Use `docs/drafting_protocol.md`, `docs/section_templates.md`, and `docs/writing_guide.md` for manuscript work.
- Run the manuscript lint script with `py scripts/lint_manuscript.py drafts --quiet` on Windows.
- Pass the verification gate after each produce step (Phase 3/4/8): run the Constraint/Citation/Data verifier subagents per `docs/verification_protocol.md`. Never proceed past a gate without a recorded `status: PASS` in `review/gates/`. On FAIL, fix and re-verify (max 2 retries) before escalating to the user.
- Tag citations as `[EVID:author_year]` during drafting; only cite evidence entries whose Source Status is `verified` or higher. Use only numbers present in `results/*.csv`.
- Complete and document mandatory QC rounds before final submission files are prepared.

## Git Hygiene

- Before committing, inspect `git status`, `git diff`, and recent commits.
- Stage only intentional public workflow files and manuscript templates.
- Verify no PDFs or private anchor summaries are staged before committing.
- Do not rewrite history, amend commits, force-push, or revert user changes unless explicitly requested.

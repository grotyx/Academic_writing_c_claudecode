# Agent Instructions

Before doing any work, read `WORKFLOW.md` in full. `WORKFLOW.md` is the authoritative project instruction file; this `AGENTS.md` file only summarizes non-negotiable rules for agent startup.

This repository is an academic manuscript-writing workflow. Treat `WORKFLOW.md` as the source of truth for project structure, phase rules, citation integrity, statistical-analysis requirements, drafting order, QC, and finalization. If this file and `WORKFLOW.md` ever conflict, follow `WORKFLOW.md`.

## Core Rules

- Read and follow `WORKFLOW.md` before making workflow, manuscript, analysis, or documentation changes.
- Do not fabricate references, citations, statistics, patient counts, p-values, confidence intervals, or journal requirements.
- Check `knowledge/evidence.md` before citing literature or adding new references.
- The `medical-kag-remote` MCP is a discovery/analysis/format assist, not a citation source: register anything it surfaces in `knowledge/evidence.md` (`[EVID:id]`, verify PMID/DOI) before citing. If the MCP is unavailable, fall back to `scripts/search_pubmed.py`. See `docs/medical_kag_protocol.md`.
- Keep reference evidence under `knowledge/`; keep writing-style material under `Style/`.
- Do not commit copyrighted PDFs or private/local style-anchor summaries.
- Commit public workflow files such as `Style/style_guide.md`, `Style/terminology.md`, documentation, templates, and scripts when appropriate.
- Cross-runtime review: from Codex (or any shell) you can pull in Claude's adversarial review with `python scripts/critical_review.py --target <file> --include-claude` (shells out to `claude -p`); OpenRouter models via `--models-file scripts/critical_models.txt`. See `docs/critical_review_protocol.md`.

## Protected Local Files

Never stage or commit these unless the user explicitly overrides the rule:

- `knowledge/pdf/`
- `Style/PDF/**/*.pdf`
- `Style/PDF/**/*.PDF`
- `Style/own/*.md` except `Style/own/example_*.md`
- `Style/landmark/*.md`
- `Style/target_journal/*.md`
- `profile/` — except the tracked public templates `profile/example_authors.md`
  and `profile/example_journals.md`. Never move real author data into them.

## Manuscript Workflow

- Do not run statistical analysis before an approved `analysis_plan.md` exists.
- Do not draft manuscript sections before an approved `draft_plan.md` exists (run the Step 0 Socratic brainstorming in `docs/draft_plan_template.md` before filling it).
- Draft sections in the order defined by `WORKFLOW.md`: Methods, Results, Introduction, Discussion, Conclusion, Abstract, Title.
- Apply terminology rules from `Style/terminology.md` during drafting and polishing.
- Use `docs/drafting_protocol.md`, `docs/section_templates.md`, and `docs/writing_guide.md` for manuscript work.
- Run the manuscript lint script with `python scripts/lint_manuscript.py drafts --quiet` on Windows.
- Style transformation: when asked to make text academic/journal-style, follow `docs/style_transform_protocol.md` — load the bound `drafts/style_spec.md` + its exemplar and transform section-by-section. The auto-trigger/auto-lint hooks are Claude Code-only, so on Codex/shell run the measurable check explicitly (`python scripts/check_style.py check <section> --spec drafts/style_spec.md`) and the Style-Conformance verifier (`docs/verifier_prompt_templates.md`).
- Pass the verification gate after each produce step (Phase 3/4/8): dispatch the Constraint/Citation/Data/Logic verifier subagents **in parallel** against a frozen artifact per `docs/verification_protocol.md` (fix Constraint/spec violations first). Never proceed past a gate without a recorded `status: PASS` in `review/gates/`. On PASS, record a `provenance:` sha256 of the artifact (plus evidence/results where the gate depends on them; required for revision) and re-check freshness with `check_gate.py --verify-hash` — a changed file makes the PASS stale. For the deterministic dimensions (`citation` / `numbers` / `revision_claims`), also cross-check the ledger against a live re-run with `check_gate.py --cross-check LABEL=PATH` — a recorded `PASS` that disagrees with the live checker (stale or fabricated) fails the gate. On FAIL, fix and re-verify (max 2 retries) before escalating to the user.
- Tag citations as `[EVID:author_year]` during drafting; do not cite evidence entries unless Source Status is `verified`, `full-text-reviewed`, or `abstract-only` (the last requires claim-scope review). Use only numbers present in `results/*.csv`.
- Complete and document mandatory QC rounds before final submission files are prepared.

## Git Hygiene

- Before committing, inspect `git status`, `git diff`, and recent commits.
- Stage only intentional public workflow files and manuscript templates.
- Verify no PDFs or private anchor summaries are staged before committing.
- Do not rewrite history, amend commits, force-push, or revert user changes unless explicitly requested.
- **Doc/version sync + auto commit-push (WORKFLOW.md Rule 12):** any harness code/bug change must update the affected docs and bump the version (project header in WORKFLOW.md + README.md/ko/ja/zh, the changed doc's own header, and a README changelog entry) in the same change, then auto-commit and push once tests are green — without asking. STOP and confirm first only when sensitive data could be staged, the change is large/destructive, manuscript WIP (`drafts/`) would be swept in, or history rewrite/force-push is involved.

## Shared commands

See `docs/harness_guide.md`. Use `python -m harness doctor`, then manifest-based `verify`, `packet`, `status`, and gated `build`. Missing required review is BLOCKED, not PASS. Never invent approval receipts or independent review.

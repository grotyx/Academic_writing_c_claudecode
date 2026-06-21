🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# Medical Academic Paper Writing Workflow for Claude

A structured workflow system for academic medical paper writing using Claude AI.

## Version

**v1.1.0** (2026-06-21)

---

## Overview

This project provides a comprehensive framework for writing academic medical papers with Claude AI assistance. It includes:

- **Structured project organization** for manuscripts, data, and references
- **Multi-paper project support** with per-paper subfolder organization
- **File versioning system** (date-based default, _v1, _REV1 styles)
- **Revision workflow** with dedicated revision folders and file naming
- **Expert team simulation** (Clinical Expert, Methodology Expert, Statistician, Editor)
- **Statistical analysis workflow** with Python script generation
- **Quality control procedures** with minimum 3-round verification (6 rounds recommended) plus revision QC re-run workflow
- **Study-type specific checklists** (STROBE, CONSORT, PRISMA, CARE, etc.)
- **Natural Academic Writing Style system** with Style Reference Tables (Voice/Tense, Transition Words, Verb Upgrades, Common Corrections, Statistical Notation, Hedging Language) and Writing Principles (Clarity/Conciseness/Objectivity/Consistency)
- **Citation quality control** — Claim→Citation Mapping (20 key claims mapped to citations before writing starts; prevents write-first, cite-later)
- **Style anchor library** (`Style/`) — own, landmark, and target-journal anchors for terminology, tone, framing, and house style
- **Terminology registry** (`Style/terminology.md`) — preferred/forbidden terms with definitions and context
- **Drafting protocol** (`docs/drafting_protocol.md`) — outline → evidence-bound draft → style pass → QC
- **Manuscript linting** (`scripts/lint_manuscript.py`) — automated checks for terminology, placeholders, overclaiming, and section-specific issues
- **Citation evidence checking** (`scripts/check_citations.py`) — verifies `[EVID:id]` tags against `knowledge/evidence.md`
- **Data number checking** (`scripts/check_numbers.py`) — verifies manuscript/table numbers against `results/*.csv`
- **Phase gate ledger checking** (`scripts/check_gate.py`) — blocks progression unless `review/gates/*.GATE.md` records required PASS checks
- **Gate freshness / provenance** (`scripts/check_gate.py --verify-hash`) — records a sha256 of the verified artifact (and evidence/results) on PASS; a later edit makes the gate **stale** and forces re-verification, closing the parallel-verifier hole
- **Revision claim checking** (`scripts/check_revision_claims.py`) — verifies response-letter `[CHANGE]` claims against revised manuscript files
- **LLM verifier prompt templates** (`docs/verifier_prompt_templates.md`) — structured prompts for constraint, semantic citation, data, logic/redundancy, and revision-alignment checks
- **Author response DOCX generation** (`scripts/compile_response_docx.py`) — converts DOCX-ready Markdown to the `Author_response_220803_Final.docx` house style
- **Author response Markdown template** (`docs/response_letter_template.md`) — keeps reviewer responses, manuscript locations, and machine-readable `[CHANGE]` blocks aligned
- **Draft plan template** (`docs/draft_plan_template.md`) — 10-item template with claim→citation tables and approval checklist
- **PubMed search tool** with built-in Python script (no MCP or external packages required)
- **Co-author debate** (`/paper-debate`) — pre-writing Claude–Codex discussion for analysis plans, draft plans, argument structure, and reviewer responses (`docs/debate_protocol.md`)
- **Multi-model critical review** (`/critical-review`) — post-writing adversarial review at senior reviewer/editor level via Claude subagent, Codex, and/or OpenRouter models, ranked by consensus × severity (`docs/critical_review_protocol.md`)
- **AI-Draft De-bloat** — writing-guide pass that strips AI tells (hollow `-ing` analysis, AI vocabulary, signposting) so disclosed AI assistance still reads naturally (`docs/writing_guide.md`)
- **Slash commands** for evidence registration (`/search-evidence`, `/import-doi`)

---

## Project Structure

```
project/
├── CLAUDE.md                     # Core rules & configuration
├── AGENTS.MD                     # Agent bootstrap rules; points to CLAUDE.md as source of truth
├── README.md                     # This file
├── docs/                         # Reference guides
│   ├── writing_guide.md          # Section-by-section writing guide
│   ├── drafting_protocol.md      # Mandatory drafting sequence
│   ├── section_templates.md      # Section-specific sentence patterns
│   ├── expert_roles.md           # Expert team roles & responsibilities
│   ├── checklist_guide.md        # Study-type specific checklists
│   ├── qc_guide.md               # Quality control procedures
│   ├── verification_protocol.md  # Verification gates, 4 verifiers, autonomous loop
│   ├── verifier_prompt_templates.md  # LLM verifier prompts and output schema
│   ├── statistical_analysis_guide.md  # Statistical analysis guide
│   ├── evidence_guide.md         # Evidence writing guide
│   ├── revision_guide.md         # Reviewer response guide
│   ├── response_letter_template.md  # DOCX-ready author response template
│   ├── figure_guide.md           # Figure generation guide
│   ├── docx_guide.md             # DOCX conversion guide
│   ├── draft_plan_template.md    # Draft plan template (copy to drafts/ for Phase 3)
│   ├── debate_protocol.md        # Claude–Codex co-author debate procedure
│   └── critical_review_protocol.md  # External multi-model adversarial review
├── knowledge/                    # Reference materials
│   ├── evidence.md               # Reference summary collection
│   ├── pdf/                      # Original PDF files — gitignored, local only
│   ├── summaries/                # Detailed full-text paper summaries
├── Style/                        # Writing-style anchors, separate from references
│   ├── PDF/                      # Source PDFs for style analysis — gitignored, local only
│   │   ├── own/
│   │   ├── landmark/
│   │   └── target_journal/
│   ├── own/                      # Own-paper style anchors
│   ├── landmark/                 # Argument/framing anchors
│   ├── target_journal/           # Target-journal house-style anchors
│   ├── style_guide.md            # Style anchor workflow and extraction rules
│   └── terminology.md            # Preferred/forbidden terminology registry
├── profile/                      # Personal info — gitignored, local only
│   ├── authors.md                # Author affiliations, contacts, ORCIDs, funding
│   └── journals.md               # Journal-specific citation formats (verified)
├── data/                         # Statistical analysis
│   ├── raw_data.csv              # Original dataset
│   ├── analysis_plan.md          # Analysis plan (required before analysis)
│   └── py/                       # Python analysis scripts
├── scripts/                      # Utility scripts
│   ├── lint_manuscript.py        # Manuscript terminology/style lint checks
│   ├── check_citations.py        # Evidence citation gate
│   ├── check_numbers.py          # Results CSV number gate
│   ├── check_gate.py             # Phase gate ledger check
│   ├── check_revision_claims.py  # Revision claim gate
│   ├── compile_response_docx.py  # Author response DOCX compiler
│   ├── search_pubmed.py          # PubMed search tool (no external deps)
│   ├── critical_review.py        # OpenRouter multi-model adversarial caller
│   ├── critical_models.txt       # OpenRouter model list (externalized)
│   └── critical_prompts/         # Adversarial prompt single-source (manuscript.txt, response.txt)
├── tests/                        # Pytest suite for the verification scripts
├── results/                      # Analysis outputs
├── drafts/                       # Manuscript sections, tables & figures
│   ├── draft_plan.md             # Manuscript outline & strategy (required before drafting)
│   ├── table_*.md
│   └── figures/
├── review/                       # QC documents
│   ├── qc_log.md
│   ├── gates/                    # Verification gate ledger (phase_NN_*.GATE.md)
│   ├── debates/                  # Claude–Codex debate logs
│   └── critical/                 # External multi-model critical-review reports
└── output/                       # Final compiled manuscript
    ├── title_page_YYMMDD.docx
    ├── manuscript_YYMMDD.docx
    └── table_N_YYMMDD.docx
```

---

## Quick Start

1. **Setup**: Update `CLAUDE.md` with your research topic, target journal, and study design. Check `profile/journals.md` for citation format and `Style/` for style anchors.
2. **References**: Use `/search-evidence [query]` or `python3 scripts/search_pubmed.py` to search PubMed and register in `knowledge/evidence.md`
3. **Data Analysis**: Place data in `data/` folder → create `analysis_plan.md` (required) → run statistical analysis
4. **Draft Plan**: Copy `docs/draft_plan_template.md` → `drafts/draft_plan.md`, fill in all 10 items including **Claim→Citation Mapping** (Opus recommended)
5. **Drafting**: Follow `docs/drafting_protocol.md` and write sections in recommended order (Methods → Results → Introduction → Discussion)
6. **Verification gates**: Run citation, number, phase-gate, and revision-claim checks; record PASS in `review/gates/`
7. **Revision response**: Use `docs/response_letter_template.md` and compile with `scripts/compile_response_docx.py` when reviewer responses are needed
8. **QC**: Run minimum 3 QC rounds before submission
9. **Finalize**: Compile manuscript to DOCX (see `docs/docx_guide.md`)

---

## Key Features

### Expert Team Simulation

- **Dr. Researcher A**: Clinical perspective (Introduction, Discussion)
- **Dr. Researcher B**: Methodology (Methods, Results, Tables)
- **Dr. Statistician**: Statistical validation, parsimony, MCID/NNT assessment
- **Dr. Editor**: Final polish, consistency check

### Mandatory Planning Before Writing

- **Analysis Plan** (`data/analysis_plan.md`): Required before any statistical analysis — defines research questions, endpoints, and test selection
- **Draft Plan** (`drafts/draft_plan.md`): Required before any section drafting — 10 required items including key message, tone/voice, essential references, evidence gaps, **Claim→Citation Mapping**, table/figure plan, and section outlines
- Both plans require user approval before proceeding to the next phase
- Per-paper plans for multi-paper projects

### Claim→Citation Mapping (NEW in v0.7.0)

A pre-writing step in the draft plan that maps ~20 key claims to their supporting citations before any writing begins:

- **Introduction background**: 5–8 claims (epidemiology, prior evidence)
- **Methods rationale**: 2–3 claims (why this outcome measure, why this design)
- **Discussion comparisons**: 5–8 claims (how findings compare to prior work)

If a citation cannot be identified for a claim, go back to Phase 1 and search first. This eliminates the write-first, cite-later anti-pattern and hallucinated references.

### Style Anchor Library (`Style/`)

Style anchors are separated from reference management. Source PDFs stay under `Style/PDF/` and extracted style notes are stored under `Style/own/`, `Style/landmark/`, or `Style/target_journal/`.
A template is provided at `Style/own/example_YYYY_Journal_keyword.md`.

Each summary captures:

- Field-specific terminology (correct vs incorrect)
- Methods boilerplate patterns (reusable text)
- Key claims with exact data (ready for cross-citation)
- Tone and voice consistency across papers

### Model Selection by Phase

- **Opus recommended**: Analysis Plan, Draft Plan, Revision — strategic decisions that determine paper quality
- **Sonnet default (Opus if budget allows)**: Drafting, Style Polish, QC — plan-guided execution
- Core principle: "Plan with Opus → Write with Sonnet"

### Redundancy Prevention

- Avoid triple duplication (Results text + Table + Figure)
- Clear guidelines for Table vs Figure decision
- Standard table structure (Table 1: Demographics, Table 2: Main Results)

### Statistical Analysis Guide (v0.3.0)

- Statistical Parsimony — RCT Table 1 without p-values
- Analysis Hierarchy — Primary > Secondary > Exploratory
- Clinical Significance — Effect size, MCID, NNT
- Subgroup Analysis Rules — Interaction test required
- Non-significant Results Reporting Guide

### Quality Control (6 Rounds)

- Round 1: Number consistency
- Round 2: Reference verification (+ order of appearance, placeholder detection, format consistency, citation distribution)
- Round 3: Logic and flow
- Round 4: Terminology, abbreviation, and tense consistency
- Round 5: Statistical quality
- Round 6: Critical review (overclaiming, logical fallacy, bias, generalizability) — internal experts plus optional external multi-model `/critical-review`

### Verification Harness

The harness combines deterministic checks with constrained LLM verifier prompts:

- `scripts/check_citations.py` verifies every `[EVID:id]` citation against `knowledge/evidence.md` and fails unverified or unknown evidence.
- `scripts/check_numbers.py` verifies manuscript and table numbers against `results/*.csv`.
- `scripts/check_gate.py` verifies that phase gate ledgers contain `status: PASS` and required checks.
- `scripts/check_revision_claims.py` verifies reviewer-response `[CHANGE]` blocks against revised manuscript files.
- `docs/verifier_prompt_templates.md` provides structured prompts for semantic support, logic, redundancy, and revision-response alignment.

### Co-author Collaboration (NEW in v0.9.3)

Two complementary Codex/multi-model features bracket the writing process:

- **`/paper-debate <topic>`** — *before* writing. Claude and Codex act as co-authors and debate analysis approach, draft-plan key message, argument structure, or reviewer-response strategy across bounded rounds (consensus cap 3). The debate log is saved under `review/debates/` and the agreed conclusion feeds the next produce step. Falls back to Claude-solo if Codex is unavailable. See `docs/debate_protocol.md`.
- **`/critical-review <target>`** — *after* writing. The finished manuscript (or response letter) is attacked in parallel by any combination of a fresh Claude subagent, Codex, and OpenRouter models (default `minimax/minimax-m3`, `z-ai/glm-5.2`). Each reviewer is prompted at **senior peer-reviewer / editor-in-chief level** — pushing past surface defects to design soundness, whether the data support the conclusions, and publication-worthiness. Findings are merged and ranked by **consensus × severity** (Critical / Important / Minor) and stored under `review/critical/`. See `docs/critical_review_protocol.md`.

The adversarial prompts live as a single source under `scripts/critical_prompts/` (`manuscript.txt`, `response.txt`); the OpenRouter script, the Claude subagent, and Codex all read the same files. OpenRouter access uses `OPENROUTER_API_KEY` (set in `.claude/settings.local.json`, gitignored); when absent, OpenRouter is skipped and the other reviewers proceed.

### AI-Draft De-bloat (NEW in v0.9.3)

A `docs/writing_guide.md` pass (applied in Phase 5 for AI-written drafts) that removes the tells of AI prose — hollow `-ing` "surface analysis" clauses, AI-favored vocabulary, and over-signposting — while explicitly **excluding** patterns that legitimately conflict (necessary hedging, copula, passive voice). AI authorship is still disclosed; this only keeps disclosed assistance from reading as bloated and tedious.

### Verification Hardening (NEW in v1.0.0)

Improvements adapted from the "superpowers" skills framework, focused on the verification gate:

- **Parallel verifiers + Constraint-first.** The four section-gate verifiers (Constraint / Citation / Data / Logic) are dispatched concurrently against a frozen artifact; the artifact is not edited mid-verification, and on FAIL the Constraint (spec-compliance) findings are fixed first. See `docs/verification_protocol.md` (v0.2.0).
- **Gate freshness / provenance** (`scripts/check_gate.py`). On PASS the gate ledger records a sha256 of the verified artifact (and `evidence` / `results` for citation- and numbers-bearing gates; required for revision). `check_gate.py --verify-hash LABEL=PATH` re-hashes and fails the gate as **stale** if the file changed since the PASS — closing the hole where a post-PASS edit silently survives re-checking. `--compute-hash PATH` fills the provenance fields. Opt-in at the tool level, standard in the documented gate commands.
- **STOP signals.** A CLAUDE.md anti-rationalization table catches the human-level shortcuts the verifiers can't ("this number is probably fine" → check the CSV; "I already passed" → a changed artifact is stale).
- **Socratic draft-plan brainstorming.** A "Step 0" in `docs/draft_plan_template.md` sharpens the paper's intent one question at a time before the plan is filled — distinct from `/paper-debate`, which it feeds as R0 prep.
- **Reviewer-response triage.** `docs/revision_guide.md` assigns each reviewer comment an accept / partial / rebut posture, mapped to the `[CHANGE]` marker and the ghost-revision gate.
- **Command `use-when` guidance.** Each `.claude/commands/*.md` now declares the situation that should trigger it.

### Author Response DOCX Workflow

Reviewer responses should be drafted in `docs/response_letter_template.md` format, with each manuscript edit recorded as a `[CHANGE]` block. Final response letters can be compiled with:

```powershell
py scripts\compile_response_docx.py drafts\revision\REV1\response_letter_REV1.md
```

The compiler reproduces the `Author_response_220803_Final.docx` house style — Times New Roman 11 pt, with bold response / location / revised-text lines and a justified body. It does not read that .docx file as a template; the formatting is built in.

### PubMed Search Tool

Built-in Python script (`scripts/search_pubmed.py`) for reference search without MCP:

```bash
python3 scripts/search_pubmed.py search "endoscopic spine surgery"  # Search
python3 scripts/search_pubmed.py fetch 35486828                     # Import by PMID
python3 scripts/search_pubmed.py doi 10.1016/j.spinee.2023.01.005  # Import by DOI
python3 scripts/search_pubmed.py related 35486828                   # Related articles
```

Slash commands for Claude integration:

- `/search-evidence [query]` - Search, select, and register in evidence.md
- `/import-doi [doi]` - Import by DOI and register in evidence.md

---

## Documentation

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | Core rules and project configuration |
| [docs/writing_guide.md](docs/writing_guide.md) | Section-by-section writing guide + Style Reference Tables + Writing Principles (4 Pillars) |
| [docs/drafting_protocol.md](docs/drafting_protocol.md) | Mandatory drafting workflow from outline to evidence-bound draft to style/QC pass |
| [docs/section_templates.md](docs/section_templates.md) | Section-specific paragraph functions and sentence patterns |
| [docs/expert_roles.md](docs/expert_roles.md) | Expert team descriptions |
| [docs/checklist_guide.md](docs/checklist_guide.md) | STROBE, CONSORT, PRISMA, CARE checklists |
| [docs/qc_guide.md](docs/qc_guide.md) | Quality control procedures |
| [docs/verification_protocol.md](docs/verification_protocol.md) | Verification gates, 4 verifier charters, autonomous fix loop, gate ledger |
| [docs/verifier_prompt_templates.md](docs/verifier_prompt_templates.md) | LLM semantic verifier prompts and structured output schema |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | Statistical analysis workflow |
| [docs/evidence_guide.md](docs/evidence_guide.md) | Evidence writing guide (format, summary methods, workflow) |
| [docs/revision_guide.md](docs/revision_guide.md) | Reviewer response guide (response letter, diplomatic language, QC re-run checklist) |
| [docs/response_letter_template.md](docs/response_letter_template.md) | DOCX-ready author response Markdown template |
| [docs/figure_guide.md](docs/figure_guide.md) | Figure generation guide (DPI, palettes, Python templates) |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX conversion guide (formatting, table style, naming rules) |
| [docs/draft_plan_template.md](docs/draft_plan_template.md) | Draft plan template — 10-item with claim→citation tables and approval checklist |
| [docs/debate_protocol.md](docs/debate_protocol.md) | Claude–Codex co-author debate procedure (rounds, roles, logging, fallback) |
| [docs/critical_review_protocol.md](docs/critical_review_protocol.md) | External multi-model adversarial review (reviewer pool, consensus × severity, fallback) |
| [Style/style_guide.md](Style/style_guide.md) | Style anchor workflow, extraction framework, and PDF-to-MD mirror rules |
| [Style/terminology.md](Style/terminology.md) | Preferred/forbidden terminology registry with definition and context |
| [Style/own/example_YYYY_Journal_keyword.md](Style/own/example_YYYY_Journal_keyword.md) | Own-paper style-anchor template |
| [scripts/lint_manuscript.py](scripts/lint_manuscript.py) | Manuscript lint script for terminology, placeholders, overclaiming, and section issues |
| [scripts/check_citations.py](scripts/check_citations.py) | Verify `[EVID:id]` citations against `knowledge/evidence.md` |
| [scripts/check_numbers.py](scripts/check_numbers.py) | Verify manuscript/table numbers against `results/*.csv` |
| [scripts/check_gate.py](scripts/check_gate.py) | Verify `review/gates/*.GATE.md` status and required checks |
| [scripts/check_revision_claims.py](scripts/check_revision_claims.py) | Verify response-letter `[CHANGE]` claims against revised manuscript files |
| [scripts/compile_response_docx.py](scripts/compile_response_docx.py) | Compile `response_letter_REV*.md` to Author_response-style DOCX |
| [scripts/search_pubmed.py](scripts/search_pubmed.py) | PubMed search script (NCBI E-utilities, no external packages) |
| [scripts/critical_review.py](scripts/critical_review.py) | OpenRouter multi-model adversarial reviewer caller (one model failure does not abort) |

---

## Requirements

- Claude AI (Claude Code CLI or VSCode extension)
- Python 3.x (for statistical analysis and PubMed search)
- Python packages for statistical analysis: pandas, numpy, scipy, statsmodels, python-docx
- PubMed search script (`scripts/search_pubmed.py`) uses only Python standard library (no additional packages)

---

## Author

**Professor Sang-Min Park, M.D., Ph.D.**

Department of Orthopaedic Surgery,
Seoul National University Bundang Hospital,
Seoul National University College of Medicine

https://sangmin.me/

---

## License

This work is licensed under the **Creative Commons Attribution 4.0 International License (CC BY 4.0)**.

Copyright (c) 2026 Sang-Min Park, Seoul National University Bundang Hospital

### You are free to:
- **Share** — copy and redistribute the material in any medium or format
- **Adapt** — remix, transform, and build upon the material for any purpose, even commercially

### Under the following terms:
- **Attribution** — You must give appropriate credit, provide a link to the license, and indicate if changes were made.

[![CC BY 4.0](https://licensebuttons.net/l/by/4.0/88x31.png)](https://creativecommons.org/licenses/by/4.0/)

Full license text: https://creativecommons.org/licenses/by/4.0/legalcode

---

## Changelog

### v1.1.0 (2026-06-21)

**Style transformation — rough draft → bound journal style, reliably**

- **Style Spec + Style-Conformance Verifier** — bind ONE exemplar (`Style/own/` or `Style/target_journal/`) into a compact, always-loaded `drafts/style_spec.md` (`docs/style_spec_template.md`), then transform section-by-section and verify each section against the spec with an independent **Style-Conformance Verifier** (auto-fix loop, max 2; `docs/verifier_prompt_templates.md` + `verification_protocol.md`). This reaches the holistic style layer (structure, sentence length, hedging, claim strength, reference format) that lint cannot. New `/style-pass` command + `docs/style_transform_protocol.md`.
- **Auto-trigger on intent** — a `UserPromptSubmit` hook (`scripts/hooks/style_intent.py`) detects "make it academic / 학술적으로 바꿔줘" and injects the style-pass protocol, so the transform fires without remembering the command. SessionStart now also surfaces the active Style Spec. Advisory + fail-open. Tests added.

### v1.0.3 (2026-06-20)

**Cross-runtime critical review + model selection**

- **Claude-CLI reviewer** — `scripts/critical_review.py --include-claude` shells out to the local `claude -p` (headless) so a non-Claude-Code caller (Codex or a plain shell) can pull in Claude's adversarial review. `OPENROUTER_API_KEY` is now only required when an OpenRouter model is actually requested. Documented in `docs/critical_review_protocol.md` + `AGENTS.MD`.
- **Larger model pool + pick ~2** — `scripts/critical_models.txt` now offers MiniMax M3, GLM 5.2, Qwen3-Max, and DeepSeek V4 Pro; `/critical-review` presents them as individual `AskUserQuestion` options and recommends choosing ~2 (cost + blind-spot diversity), then runs `--models <selected>`.

### v1.0.2 (2026-06-20)

**Process enforcement + CLAUDE.md condensation**

- **Plan-first enforcement (hooks)** — `.claude/settings.json` adds committed hooks: a PreToolUse `Write|Edit` gate (`scripts/hooks/enforce_gates.py`) that BLOCKS drafting a section without `drafts/.../draft_plan.md` (Rule 8) or creating an analysis script without `data/.../analysis_plan.md` (Rule 7), and a SessionStart hook (`scripts/hooks/session_contract.py`) that injects the workflow contract every session. Revisions are exempt; multi-paper subfolders handled; fails open; UTF-8 safe. (Windows `py`; macOS/Linux use `python3`.)
- **`/verify`** — `scripts/verify_all.py` runs check_citations + check_numbers (+ optional check_gate) in one command before recording a gate PASS. New hook tests; suite at 86 passing.
- **CLAUDE.md condensed 808 → 696 lines (~14%)** — collapsed the Multi-Paper/Revision structure trees and the Phase-2 Notes / test-selection / style-priority / gate-placement duplicates into pointers to their canonical docs; no MUST-FOLLOW rule removed.

### v1.0.1 (2026-06-20)

**Post-release hardening + concision tooling**

- **Same-day hardening (code review + project audit)** — `check_gate.py` freshness now fails cleanly on non-file paths (directory/missing) instead of crashing, anchors relative paths on the repo `ROOT`, rejects blank/placeholder digests with a clear message, and reports `provenance_verified` / `provenance_unverified` in PASS output; Phase 8 verifier set aligned (Logic is Draft-only; Revision adds Revision-claims + Response-alignment) with `--require-check constraint` in the gate commands; "3 verifiers" corrected to "4"; Critical Rules renumbered 9/10/11; `lint_manuscript.py` skips nonexistent `.md` arguments (first lint tests added); `check_numbers.py` requires an explicit p-value (not any 0–1 proportion); `search_pubmed.py` evidence entries gain Evidence ID + Source Status; `failure_code` added to checker FAIL output; test suite expanded to 77 tests.
- **Concision Pass** — `docs/writing_guide.md` gains a journal word-limit compression pass (Phase 5): 10 Before→After patterns distilled from a senior English edit, plus an over-compression guardrail (keep primary-outcome definitions, statistical spec, eligibility, and key limitations in text or move to Supplement — never silently delete).

### v1.0.0 (2026-06-20)

**Verification hardening (superpowers-inspired)**

- **Gate freshness / provenance** — `check_gate.py` gains a `provenance:` block (sha256 of artifact/evidence/results), `--verify-hash LABEL=PATH` (fails a gate as *stale* when a verified file changed after PASS), and `--compute-hash PATH`. Closes the stale-PASS hole opened by parallel verification; backward compatible (opt-in flag). `review/gates/_TEMPLATE.GATE.md` and `docs/verification_protocol.md` (v0.2.0) document it; pytest coverage expanded to 70 tests.
- **Parallel verifiers + Constraint-first** — the four section-gate verifiers run concurrently against a frozen artifact; fixes prioritize Constraint (spec) violations; all PASSes are discarded and re-run after any edit (`docs/verification_protocol.md`).
- **STOP signals** — CLAUDE.md anti-rationalization table (§10) guarding the human-level shortcuts verifiers miss.
- **Socratic draft-plan brainstorming** — `docs/draft_plan_template.md` Step 0 (one question at a time; distinct from `/paper-debate`, feeds it as R0 prep), wired into CLAUDE.md Phase 3 + Rule 8.
- **Reviewer-response triage** — `docs/revision_guide.md` accept/partial/rebut posture per comment, tied to `[CHANGE]` + ghost-revision; Phase 8 verifier set aligned to include Constraint.
- **Command `use-when` lines** added to `.claude/commands/*.md`; TodoWrite documented as non-authoritative QC/gate tracking (CLAUDE.md Rule 4).

### v0.9.3 (2026-06-19)

**Co-author collaboration and multi-model critical review**

- Added **`/paper-debate`** (`docs/debate_protocol.md`, `.claude/commands/paper-debate.md`) — pre-writing Claude–Codex co-author debate for analysis plans, draft plans, argument structure, and reviewer responses; bounded rounds with consensus cap 3, debate logs under `review/debates/`, Claude-solo fallback.
- Added **`/critical-review`** (`docs/critical_review_protocol.md`, `.claude/commands/critical-review.md`) — post-writing adversarial review by any combination of a fresh Claude subagent, Codex, and OpenRouter models (default `minimax/minimax-m3`, `z-ai/glm-5.2`), merged and ranked by consensus × severity, reports under `review/critical/`.
- Added `scripts/critical_review.py` (OpenRouter caller; one model's failure is skipped, not fatal), `scripts/critical_models.txt` (externalized model list), and `scripts/critical_prompts/` (single-source adversarial prompts `manuscript.txt` / `response.txt` shared by the script, the Claude subagent, and Codex).
- Critical-review prompts framed at **senior peer-reviewer / editor-in-chief level** — design soundness, data-to-conclusion support, and publication-worthiness, not just surface defects.
- `build_prompt` uses `str.replace` (not `str.format`) so literal braces (JSON/LaTeX examples) in a prompt or target text cannot crash substitution; regression test added.
- Added **AI-Draft De-bloat** section to `docs/writing_guide.md` — strips AI tells (hollow `-ing` analysis, AI vocabulary, signposting) while excluding legitimately conflicting patterns (hedging/copula/passive).
- OpenRouter access via `OPENROUTER_API_KEY` in `.claude/settings.local.json` (gitignored); absent key skips OpenRouter and proceeds with the other reviewers.
- CLAUDE.md integrates both commands (Collaboration commands, Phase 2/3/4/8 debate prompts, Round 6 two-layer critical review, File Roles, structure trees).

### v0.9.2 (2026-06-18)

**Verification harness hardening** (bug fixes + doc consistency)

- `check_numbers.py`: no longer crashes on percentages (e.g. 42.5%); rejects p-values backed only by an unrelated value (e.g. a count of 0); handles thousands separators (1,234) and ignores ISO dates and inline `code` spans.
- `check_gate.py`: strips inline `# ...` comments so the documented gate template passes and round-overflow escalation works.
- Added `requirements.txt` (python-docx) and a `tests/` pytest suite (run with `pytest`).
- Docs: verifier set corrected to Constraint / Citation / Data / Logic (Revision adds Revision-claims and Response-alignment); response compiler description corrected (it reproduces formatting, it does not read a reference .docx).

### v0.9.1 (2026-06-18)

**Multilingual README and Author Response DOCX Completion**

- Synchronized English, Korean, Japanese, and Chinese READMEs with the verification harness scripts and DOCX response workflow.
- Added Author response Markdown template documentation and `compile_response_docx.py` usage.
- Added deterministic checker references for citation evidence, numeric grounding, phase gates, and revision claims.
- Added LLM verifier prompt-template documentation for hallucination control, redundancy control, logic checks, and revision alignment.

### v0.9.0 (2026-06-16)

**Verification Harness** — inline produce→verify→fix→re-verify gates (new `docs/verification_protocol.md`)

- Inline verification gates after each produce step (Phase 3/4/8) — replaces end-loaded manual QC with a produce→verify→fix→re-verify loop
- Verifier subagents: Constraint (instruction compliance), Citation (citation grounding vs evidence.md), Data (numbers vs results CSV), Logic (cross-section logic/redundancy); the Revision gate adds Revision-claims and Response-alignment
- Autonomous fix loop (max 2 retries) then user escalation
- `[EVID:author_year]` citation tags and results-CSV-as-single-source grounding
- Gate ledger (`review/gates/`) blocks progress until `status: PASS` is recorded
- `evidence.md` entries gain a Source Status field; Phase 6 QC lightened to a final-confirmation pass
- Programmatic citation checker: `py scripts\check_citations.py drafts\03_introduction.md --evidence knowledge\evidence.md`
- Programmatic number checker: `py scripts\check_numbers.py drafts\05_results.md drafts\table_1.md --results results`
- Programmatic phase gate checker: `py scripts\check_gate.py review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic --verify-hash artifact=drafts\05_results.md`
- Programmatic ghost-revision checker: `py scripts\check_revision_claims.py drafts\revision\REV1\response_letter_REV1.md --strict`
- LLM semantic verifier schema: `docs/verifier_prompt_templates.md` for logic, redundancy, semantic citation support, and revision-response alignment

### v0.8.1 (2026-06-16)

**Response Letter Formatting Rules** — `docs/revision_guide.md` internal version v0.3.0 → v0.4.0

- Reworked the response letter format to a minimal-formatting standard:
  - Bold only the words **"Comment x.x"** and **"Response"**; all other formatting removed (no headings, colors, indentation, tables, or bullet/numbered lists)
  - Quoted revised manuscript text is set in *italic*
  - Responses are written as prose (no numbered/itemized points), flowing thanks → position → rationale → action in a single paragraph
  - Revision locations use lead-in placement — state the location first, then quote the revised text (no trailing "(See ...)")
  - No hyphens or em-dashes
  - Persuasive, reviewer-convincing tone
- Added a **minimal change principle** for manuscript edits — make only the smallest sentence changes needed to address each comment, keeping revisions concise rather than verbose
- Updated the "during writing" checklist to match the new formatting rules

### v0.8.0 (2026-06-16)

**Style Workflow, Linting, and Agent Instructions**

- Promoted writing-style material into the top-level `Style/` workflow, separate from reference evidence under `knowledge/`.
- Added `Style/style_guide.md` for style-anchor extraction rules, PDF-to-MD mirror rules, and publisher generic filename handling.
- Expanded `Style/terminology.md` into the project terminology registry for preferred/forbidden terms across spine surgery, trials, AI/radiomics, and reporting contexts.
- Added `docs/drafting_protocol.md` and `docs/section_templates.md` to enforce outline → evidence-bound draft → style pass → QC drafting.
- Added `scripts/lint_manuscript.py` and updated draft/table templates so manuscript linting passes with `py scripts/lint_manuscript.py drafts --quiet` on Windows.
- Added `AGENTS.MD` as agent bootstrap instructions, with `CLAUDE.md` as the authoritative source of truth.
- Updated `.gitignore` so copyrighted PDFs and private style-anchor summaries remain local, while public workflow files and examples remain commit-eligible.

### v0.7.1 (2026-05-15)

**Terminology & Template**

- Added `Style/terminology.md` — field-standard terminology registry for BESS/spine surgery
  - Correct vs incorrect usage for 60+ terms across: procedure names, instruments, outcome measures, study design, statistics, complications
  - Common mistake list (creatine phosphokinase vs creatinine kinase; assessor-blind vs double-blind; VAS vs NRS; etc.)
- Added `docs/draft_plan_template.md` — complete 10-item draft plan template
  - Claim→Citation Mapping tables (Introduction/Methods/Discussion)
  - Approval checklist (all 10 items must be complete before Phase 4)
- CLAUDE.md Phase 1: Added journals format check and Style anchor review at project setup
- CLAUDE.md: Updated File Roles table, Phase 3 workflow, and Quick Commands to reference template
- Fix: `profile/journals.md` citation examples corrected — TSJ now shows 6 authors before et al. (not 3); BJJ now lists all 8 authors without et al. (per BJJ policy)

### v0.7.0 (2026-05-14)

**Citation Quality & Style Consistency**

- Added `Style/` — own, landmark, and target-journal style anchors
  - 2018 Spine — Depression & chronic LBP cross-sectional (KNHANES)
  - 2020 Spine J — Biportal endoscopic vs microscopic laminectomy RCT
  - 2023 Spine J — Biportal endoscopic vs microscopic discectomy RCT
  - 2024 Neurospine — BESS safety profile: pooled analysis of 2 RCTs
  - 2025 Bone Joint J — ENDOBH multicentre RCT (6 hospitals)
  - Each file: full citation, key terminology table, methods boilerplate, key claims with data
- CLAUDE.md Rule 8: Added **Claim→Citation Mapping** as required item 10 in draft_plan.md
  - ~20 key claims mapped to citations before writing starts
  - Intro background (5–8), methods rationale (2–3), discussion comparisons (5–8)
- CLAUDE.md: Phase Completion Criteria 3→4 updated (9 → 10 required draft_plan items)
- Added `profile/journals.md` (local only, gitignored) — verified citation formats for 8 target journals
  - The Spine Journal: bracket [N], 6 authors then et al.
  - Spine (Phila Pa 1976): superscript, "(Phila Pa 1976)" required in citation
  - Bone Joint J: all authors listed, Vol-B(issue) format
  - Neurospine: superscript, et al. after 3 authors
  - Also: J Neurosurg Spine, Global Spine J, Clin Orthop Relat Res, Asian Spine J
- Added ORCIDs for 5 co-authors in `profile/authors.md` (local only, gitignored)

### v0.6.0 (2026-04-18)

**Writing Guide Major Refactor** — `docs/writing_guide.md` internal version v0.3.0 → v0.4.0

- **Role separation** between CLAUDE.md (orchestrator) and writing_guide.md (rules)
  - CLAUDE.md "Natural Academic Writing Style" section collapsed to pointer-only (~115 lines removed)
  - All writing style rules, tables, and examples consolidated in writing_guide.md
- **New section: Style Reference Tables** in writing_guide.md
  - Voice & Tense by Section (6 sections: Abstract/Intro/Methods/Results/Discussion/Conclusion)
  - Transition Words (but → nonetheless)
  - Verb Upgrades (showed → demonstrated)
  - Common Corrections (elderly → older adult, etc.)
  - Statistical Notation (italic *p*, en-dash for ranges, never *p* = 0.000)
  - Hedging Language (4-level guide: Strong/Moderate/Weak/Very weak for Discussion)
- **New section: Writing Principles (4 Pillars)** in writing_guide.md
  - Clarity, Conciseness, Objectivity, Consistency with expanded examples
- **General Principles expanded** with 6 new rules:
  - No bold text in manuscript body
  - Abbreviation define-once rule
  - Clinical findings as sentence subject (not statistical method)
  - No synonym mixing (dural tear ↔ durotomy, etc.) with draft_plan.md term selection
  - Numerical formatting consistency (decimals, units)
  - No sentence-initial numbers (spell out or restructure)
- **Results section**: added non-significant p-value omission guideline (primary outcome exception)
- **Discussion section**: three new subsections
  - No specific numbers/p-values (literature comparison exception)
  - No directional-trend framing for non-significant results
  - Neutral tone with banned exaggeration list
- **Tables section**: 2 new Tips
  - Methods Statistics vs Table footnote role separation
  - Supplementary Table for pre-specified sensitivity analyses

**Cross-file Consistency Fixes**

- CLAUDE.md Phase 2: explicit reference to `docs/statistical_analysis_guide.md` + `analysis_plan.md` required items (endpoint hierarchy, tests, multiple comparison, missing data)
- CLAUDE.md Phase 6 QC: per-round responsibility annotation (Claude / Dr. Editor / Dr. Statistician) with CRITICAL vs RECOMMENDED marking
- CLAUDE.md Phase 3→4 Completion Criteria: expanded to list all 9 `draft_plan.md` required items
- `docs/revision_guide.md`: new "QC Re-run for Revision" section with per-round re-run checklist and pre-submission checklist
- `docs/evidence_guide.md`: Search Log query examples updated to actual PubMed syntax (field tags `[tiab]`/`[MeSH]`, boolean AND/OR/NOT, quoted phrases)

### v0.5.2 (2026-04-15)

- Fixed cross-file inconsistencies across all documentation
- Updated figure format workflow: PNG for drafts (300 DPI), TIFF with LZW compression for final submission (600+ DPI), PPT/vector as options
- Updated `save_figure()` template: `draft=True` (PNG) / `final=True` (TIFF LZW) parameter split
- Added `review/reviewer_comments_REV{N}.md` to CLAUDE.md revision structure and File Roles table
- Fixed `analysis_plan.md` placeholder from `[FROM CLAUDE.md]` to user-friendly `[연구 설계 입력]`
- Aligned `revision_guide.md` file structure with CLAUDE.md (R1→REV1 naming convention)
- Added Round 4 template to `qc_guide.md` QC log and Final Sign-off
- Updated `statistical_analysis_guide.md` figure output format to include TIFF
- Updated `checklist_guide.md` figure submission requirements (TIFF LZW 600+ DPI)

### v0.5.1 (2026-04-15)

- Added Analysis Plan Mandatory (Critical Rule #7) — `analysis_plan.md` must be created and approved before running any statistical analysis
  - Per-paper analysis plans for multi-paper projects (`data/paper{N}_xxx/analysis_plan.md`)
  - Required contents: research questions, inclusion/exclusion criteria, variable definitions, test selection rationale, significance level
- Added Draft Plan Mandatory (Critical Rule #8) — `drafts/draft_plan.md` must be created and approved before drafting any sections
  - Required contents: key message, tone/voice, essential references, evidence gaps, table/figure plan, introduction/discussion outlines, limitation points
  - Per-paper draft plans for multi-paper projects
- Added Model Selection by Phase (Critical Rule #9) — cost-efficient model guidance
  - Opus recommended: Analysis Plan, Draft Plan, Revision (strategic phases)
  - Sonnet default with Opus optional: Drafting, Style Polish, QC (plan-guided execution)
  - Plan Mode (`/plan`) recommended for Draft Plan creation
- Workflow phases renumbered (7 → 8 phases): added Phase 3 (Draft Plan) between Analysis and Drafting
- Updated Phase Completion Criteria with draft_plan.md approval gate

### v0.5.0 (2026-04-14)

- Enhanced QC Round 2 (Reference Verification) with 4 new sub-checks:
  - 2.5 Placeholder Reference Detection — detect fake/temporary citations ([ref1], [TBD], [X], etc.)
  - 2.6 Order of Appearance Check — verify citation numbering follows Vancouver style order
  - 2.7 Reference Format Consistency — check bibliographic style uniformity across all references
  - 2.8 Citation Distribution Check — section-wise citation balance, self-citation rate, recency
- Strengthened Reference List Integrity (2.4) — added number continuity and duplicate number checks
- Updated QC Log template with Round 2 enhanced sections
- Added File Versioning rules (Critical Rule #5) — date-based default (`_YYMMDD`), `_v1`, `_REV1`, `_FINAL`
- Added Multi-Paper Organization (Critical Rule #6) — per-paper subfolders for data, results, drafts, output, review
- Added Multi-Paper Project structure diagram (shared docs/knowledge/scripts, separate per-paper folders)
- Added Revision folder structure — `drafts/revision/REV{N}/`, `output/revision/REV{N}/`
- Added Phase 7 (Revision) to Recommended Workflow with QC re-run requirement
- Updated Phase Completion Criteria with Submit → Revision path
- Updated File Roles table with revision folder entries

### v0.4.0 (2026-04-09)

- Added `docs/revision_guide.md` - Reviewer response and revision guide
- Added `docs/figure_guide.md` - Publication-quality figure generation guide
- Added `drafts/00_cover_letter.md` - Concise cover letter template
- Updated CLAUDE.md: project structure, file roles, Quick Commands for revision and figures
- Removed Spine GraphRAG project-specific references from project structure

### v0.3.0 (2026-03-09)

- Major rewrite of `docs/statistical_analysis_guide.md` (v0.2.1 → v0.3.0)
  - Statistical Parsimony, Analysis Hierarchy, Clinical Significance, Subgroup Analysis, Sensitivity Analysis
  - Methods Statistical Section Checklist (10 mandatory items per ICMJE/SAMPL)
- Updated `docs/writing_guide.md`, `docs/expert_roles.md`, `docs/qc_guide.md` for statistical consistency

### v0.2.5 (2026-03-09)

- Added `scripts/search_pubmed.py` - PubMed search tool using NCBI E-utilities API (no MCP, no external packages)
- Added slash commands: `/search-evidence [query]`, `/import-doi [doi]`

### v0.2.4 (2026-03-04)

- Added `.gitattributes` for LF line ending normalization
- Added `.gitignore` rules for `.DS_Store`, local settings, IDE config

### v0.2.3 (2026-02-15)

- Added `docs/docx_guide.md` for DOCX conversion rules
- Date-suffixed output files, separate title page and table DOCX files

### v0.2.2 (2026-02-10)

- Separated evidence guide from evidence registry
- Added `docs/evidence_guide.md` with detailed summarization instructions

### v0.2.1 (2026-02-07)

- Various structural fixes and template improvements

### v0.2 (2026-02-03)

- Added Statistical Analysis Guide
- Added Table/Figure/Results redundancy prevention rules

### v0.1 (Initial)

- Basic project structure
- Writing guide, expert roles, checklists, QC guide

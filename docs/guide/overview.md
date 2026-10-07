# Full guide (moved from README)

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
- **Natural Academic Writing Style system** with Style Reference Tables (Voice/Tense, Transition Words, Verb Choice, Common Corrections, Statistical Notation, Hedging Language) and Writing Principles (Clarity/Conciseness/Objectivity/Consistency)
- **Reliable style transformation** (`/style-pass`) — convert a rough draft to a bound journal style: a per-project Style Spec (one chosen exemplar) + section-by-section transform + an independent Style-Conformance verifier (auto-fix loop) + a measurable `scripts/check_style.py` gate (sentence length, citation density, hedging) + auto-trigger on "make it academic" intent (`docs/style_transform_protocol.md`)
- **Citation quality control** — Claim→Citation Mapping (20 key claims mapped to citations before writing starts; prevents write-first, cite-later)
- **Style anchor library** (`Style/`) — own, landmark, and target-journal anchors for terminology, tone, framing, and house style
- **Terminology registry** (`Style/terminology.md`) — preferred/forbidden terms with definitions and context
- **Drafting protocol** (`docs/drafting_protocol.md`) — outline → evidence-bound draft → style pass → QC
- **Manuscript linting** (`scripts/lint_manuscript.py`) — automated checks for terminology, placeholders, overclaiming, and section-specific issues
- **Citation evidence checking** (`scripts/check_citations.py`) — verifies `[EVID:id]` tags against `knowledge/evidence.md`
- **Data number checking** (`scripts/check_numbers.py`) — verifies manuscript/table numbers against `results/*.csv`
- **Phase gate ledger checking** (`scripts/check_gate.py`) — blocks progression unless `review/gates/*.GATE.md` records required PASS checks
- **Gate freshness / provenance** (`scripts/check_gate.py --verify-hash`) — records a sha256 of the verified artifact (and evidence/results) on PASS; a later edit makes the gate **stale** and forces re-verification, closing the parallel-verifier hole
- **Gate cross-check** (`scripts/check_gate.py --cross-check`) — re-runs the canonical checker live for the deterministic dimensions (`citation` / `numbers` / `revision_claims`) and fails the gate when the ledger's recorded status disagrees, catching a stale or fabricated `PASS` (loud-fails if a source is unreachable)
- **Revision claim checking** (`scripts/check_revision_claims.py`) — verifies response-letter `[CHANGE]` claims against revised manuscript files
- **LLM verifier prompt templates** (`docs/verifier_prompt_templates.md`) — structured prompts for constraint, semantic-citation, data, logic/redundancy, style-conformance, citation-stance, and revision-alignment checks
- **Citation assist** — `/suggest-citation` (find the best `[EVID:id]` for a claim), `/verify-claims` (per-sentence SUPPORTED/PARTIAL/UNSUPPORTED claim map via `scripts/extract_claims.py`), `/cite-stance` (supporting/contrasting/mentioning, Scite-style), and `/evidence-table` (a "summary of included studies" table via `scripts/evidence_table.py`, Elicit-style) (`docs/citation_assist_protocol.md`)
- **Knowledge-graph integration** (optional) — the medical-kag MCP (GraphRAG) as an upstream discovery / conflict / GRADE-synthesis / reference engine, with `knowledge/evidence.md` kept canonical and `scripts/search_pubmed.py` as the fallback (`docs/medical_kag_protocol.md`)
- **Process-enforcement hooks** (`scripts/hooks/`) — SessionStart contract injection, PreToolUse plan-first gate, PostToolUse style/terminology lint, and UserPromptSubmit style auto-trigger
- **One-shot verification** (`/verify`, `scripts/verify_all.py`) — runs citation + number + gate checks together
- **Author response DOCX generation** (`scripts/compile_response_docx.py`) — converts DOCX-ready Markdown to the `Author_response_220803_Final.docx` house style
- **Author response Markdown template** (`docs/response_letter_template.md`) — keeps reviewer responses, manuscript locations, and machine-readable `[CHANGE]` blocks aligned
- **Draft plan template** (`docs/draft_plan_template.md`) — 10-item template with claim→citation tables and approval checklist
- **PubMed search tool** with built-in Python script (no MCP or external packages required)
- **Co-author debate** (`/paper-debate`) — pre-writing Claude–Codex discussion for analysis plans, draft plans, argument structure, and reviewer responses (`docs/debate_protocol.md`)
- **Multi-model critical review** (`/critical-review`) — post-writing adversarial review at senior reviewer/editor level via Claude subagent, Codex, and/or OpenRouter models, ranked by consensus × severity (`docs/critical_review_protocol.md`)
- **Editorial desk-screen** (`/editor-review`) — a high-impact-journal editor's substantive call beyond mechanical QC: identifies the paper's field, benchmarks it against what that field's high-impact journals actually publish, and judges clinical validity, scope fit, and analysis adequacy — then a `SEND FOR PEER REVIEW` / `BORDERLINE` / `DESK REJECT` verdict with what to add to compete (or a realistic lower-tier journal). Single Opus subagent or multi-model panel; optional medical-kag benchmark (`docs/critical_review_protocol.md` §5)
- **AI-Draft De-bloat** — writing-guide pass that strips AI tells (hollow `-ing` analysis, AI vocabulary, signposting) so disclosed AI assistance still reads naturally (`docs/writing_guide.md`)
- **Slash commands** for evidence registration (`/search-evidence`, `/import-doi`)

---

## Project Structure

```
project/
├── WORKFLOW.md                   # Core rules & configuration (shared by Claude/Codex/Gemini)
├── CLAUDE.md                     # Claude Code bootstrap; imports WORKFLOW.md via @WORKFLOW.md
├── AGENTS.md                     # Codex/agent bootstrap rules; points to WORKFLOW.md as source of truth
├── GEMINI.md                     # Gemini bootstrap; points to WORKFLOW.md
├── README.md                     # This file
├── .gitattributes                # Line-ending policy (text=auto eol=lf; prevents CRLF churn from OneDrive/Windows sync)
├── docs/                         # Reference guides
│   ├── workflow_reference.md     # Tree, file roles, command catalog (moved from WORKFLOW.md)
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
│   ├── critical_review_protocol.md  # External multi-model adversarial review
│   ├── style_transform_protocol.md  # /style-pass transform + Style verifier
│   ├── style_spec_template.md    # Style Spec template (bind one exemplar)
│   ├── citation_assist_protocol.md  # Citation suggestion / verification / stance / table
│   └── medical_kag_protocol.md   # medical-kag MCP (GraphRAG); evidence.md canonical
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
│   ├── check_style.py            # Measurable style gate vs the Style Spec
│   ├── extract_claims.py         # Extract [EVID:id]-tagged sentences (claim verification)
│   ├── evidence_table.py         # Structured study records → markdown comparison table
│   ├── verify_all.py             # /verify — citation + number (+ gate) in one run
│   ├── critical_review.py        # OpenRouter multi-model adversarial caller
│   ├── critical_models.txt       # OpenRouter model list (externalized)
│   ├── critical_prompts/         # Adversarial prompt single-source (manuscript.txt, response.txt)
│   └── hooks/                    # Enforcement hooks (enforce_gates, session_contract, lint_on_edit, style_intent) + run.sh launcher (py → python3 fallback)
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

## Installation: two tracks

| | A. Template (no install) | B. Installed engine |
|---|---|---|
| Get it | `git clone` / "Use this template" | `uv tool install git+https://github.com/grotyx/Academic_writing_c_claudecode@vX.Y.Z` |
| Start a paper | work inside the copied folder | `manuwright init my-paper` |
| Agents | Claude Code via `.claude/`; Codex/Gemini via `AGENTS.md`/`GEMINI.md` | `manuwright agents install` (Claude Code, Codex, Antigravity, opencode, Muse) |
| Update | `git pull` (clones) or replace public engine files | `manuwright update`; opt-in `manuwright config set auto-update on` (patch-only, never stales fresh reviews) |

Both tracks run the same engine and rules. Details: [docs/harness_guide.md](../../docs/harness_guide.md), migration: [docs/migration_guide.md](../../docs/migration_guide.md), design: [docs/distribution_plan.md](../../docs/distribution_plan.md).

## Quick Start

1. **Setup**: Update `WORKFLOW.md` with your research topic, target journal, and study design. Check `profile/journals.md` for citation format and `Style/` for style anchors.
2. **References**: Use `/search-evidence [query]` or `python scripts/search_pubmed.py` to search PubMed and register in `knowledge/evidence.md`
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

- **Parallel verifiers + Constraint-first.** The four section-gate verifiers (Constraint / Citation / Data / Logic) are dispatched concurrently against a frozen artifact; the artifact is not edited mid-verification, and on FAIL the Constraint (spec-compliance) findings are fixed first. See `docs/verification_protocol.md` (v0.3.0).
- **Gate freshness / provenance** (`scripts/check_gate.py`). On PASS the gate ledger records a sha256 of the verified artifact (and `evidence` / `results` for citation- and numbers-bearing gates; required for revision). `check_gate.py --verify-hash LABEL=PATH` re-hashes and fails the gate as **stale** if the file changed since the PASS — closing the hole where a post-PASS edit silently survives re-checking. `--compute-hash PATH` fills the provenance fields. Opt-in at the tool level, standard in the documented gate commands.
- **STOP signals.** A WORKFLOW.md anti-rationalization table catches the human-level shortcuts the verifiers can't ("this number is probably fine" → check the CSV; "I already passed" → a changed artifact is stale).
- **Socratic draft-plan brainstorming.** A "Step 0" in `docs/draft_plan_template.md` sharpens the paper's intent one question at a time before the plan is filled — distinct from `/paper-debate`, which it feeds as R0 prep.
- **Reviewer-response triage.** `docs/revision_guide.md` assigns each reviewer comment an accept / partial / rebut posture, mapped to the `[CHANGE]` marker and the ghost-revision gate.
- **Command `use-when` guidance.** Each `.claude/commands/*.md` now declares the situation that should trigger it.

### Author Response DOCX Workflow

Reviewer responses should be drafted in `docs/response_letter_template.md` format, with each manuscript edit recorded as a `[CHANGE]` block. Final response letters can be compiled with:

```powershell
python scripts/compile_response_docx.py drafts/revision/REV1/response_letter_REV1.md
```

The compiler reproduces the `Author_response_220803_Final.docx` house style — Times New Roman 11 pt, with bold response / location / revised-text lines and a justified body. It does not read that .docx file as a template; the formatting is built in.

### PubMed Search Tool

Built-in Python script (`scripts/search_pubmed.py`) for reference search without MCP:

```bash
python scripts/search_pubmed.py search "endoscopic spine surgery"  # Search
python scripts/search_pubmed.py fetch 35486828                     # Import by PMID
python scripts/search_pubmed.py doi 10.1016/j.spinee.2023.01.005  # Import by DOI
python scripts/search_pubmed.py related 35486828                   # Related articles
```

Slash commands for Claude integration:

- `/search-evidence [query]` - Search, select, and register in evidence.md
- `/import-doi [doi]` - Import by DOI and register in evidence.md

---

## Documentation

| Document | Purpose |
|----------|---------|
| [WORKFLOW.md](../../WORKFLOW.md) | Core rules and project configuration (shared by every runtime) |
| [CLAUDE.md](../../CLAUDE.md) | Claude Code bootstrap; imports WORKFLOW.md |
| [docs/writing_guide.md](../../docs/writing_guide.md) | Section-by-section writing guide + Style Reference Tables + Writing Principles (4 Pillars) |
| [docs/drafting_protocol.md](../../docs/drafting_protocol.md) | Mandatory drafting workflow from outline to evidence-bound draft to style/QC pass |
| [docs/section_templates.md](../../docs/section_templates.md) | Section-specific paragraph functions and sentence patterns |
| [docs/expert_roles.md](../../docs/expert_roles.md) | Expert team descriptions |
| [docs/checklist_guide.md](../../docs/checklist_guide.md) | STROBE, CONSORT, PRISMA, CARE checklists |
| [docs/qc_guide.md](../../docs/qc_guide.md) | Quality control procedures |
| [docs/verification_protocol.md](../../docs/verification_protocol.md) | Verification gates, 4 verifier charters, autonomous fix loop, gate ledger |
| [docs/verifier_prompt_templates.md](../../docs/verifier_prompt_templates.md) | LLM semantic verifier prompts and structured output schema |
| [docs/statistical_analysis_guide.md](../../docs/statistical_analysis_guide.md) | Statistical analysis workflow |
| [docs/evidence_guide.md](../../docs/evidence_guide.md) | Evidence writing guide (format, summary methods, workflow) |
| [docs/revision_guide.md](../../docs/revision_guide.md) | Reviewer response guide (response letter, diplomatic language, QC re-run checklist) |
| [docs/response_letter_template.md](../../docs/response_letter_template.md) | DOCX-ready author response Markdown template |
| [docs/figure_guide.md](../../docs/figure_guide.md) | Figure generation guide (DPI, palettes, Python templates) |
| [docs/docx_guide.md](../../docs/docx_guide.md) | DOCX conversion guide (formatting, table style, naming rules) |
| [docs/draft_plan_template.md](../../docs/draft_plan_template.md) | Draft plan template — 10-item with claim→citation tables and approval checklist |
| [docs/debate_protocol.md](../../docs/debate_protocol.md) | Claude–Codex co-author debate procedure (rounds, roles, logging, fallback) |
| [docs/critical_review_protocol.md](../../docs/critical_review_protocol.md) | External multi-model adversarial review (reviewer pool, consensus × severity, fallback) |
| [Style/style_guide.md](../../Style/style_guide.md) | Style anchor workflow, extraction framework, and PDF-to-MD mirror rules |
| [Style/terminology.md](../../Style/terminology.md) | Preferred/forbidden terminology registry with definition and context |
| [Style/own/example_YYYY_Journal_keyword.md](../../Style/own/example_YYYY_Journal_keyword.md) | Own-paper style-anchor template |
| [scripts/lint_manuscript.py](../../scripts/lint_manuscript.py) | Manuscript lint script for terminology, placeholders, overclaiming, and section issues |
| [scripts/check_citations.py](../../scripts/check_citations.py) | Verify `[EVID:id]` citations against `knowledge/evidence.md` |
| [scripts/check_coverage.py](../../scripts/check_coverage.py) | Citation coverage audit — **over-citation** (too many refs on one claim) and **unknown citations** as the quality signals, plus per-section density; uncited/unrealized reported neutrally (curation, not waste) |
| [scripts/format_references.py](../../scripts/format_references.py) | `[EVID:id]` → journal reference list (numbered/author-year) + in-text tag conversion to a sibling `*_formatted.md`; **MCP-independent** (Phase 7) |
| [scripts/check_abstract.py](../../scripts/check_abstract.py) | Abstract ↔ body number consistency — flags any abstract number absent from the body (Rule 3; p-values excluded by default) (Phase 6 QC Round 1) |
| [scripts/check_crossrefs.py](../../scripts/check_crossrefs.py) | Table/Figure cross-reference check — in-text "Table N"/"Figure N" mentions vs actual `table_*.md`/figure legends: **broken references** (primary signal), unreferenced items, out-of-order first mentions; advisory by default, `--fail-on-*` to gate (Phase 6 QC) |
| [scripts/check_abbreviations.py](../../scripts/check_abbreviations.py) | Abbreviation define-at-first-use check — abstract and body as separate scopes (UNDEFINED / DEFINED_AFTER_USE / REDEFINED / SINGLE_USE); advisory by design (false positives expected), `--allow` / `--strict` (Phase 6 QC) |
| [scripts/check_response_coverage.py](../../scripts/check_response_coverage.py) | Reviewer-comment response coverage — every `Comment N)` must have a real `Response:` (missing/empty/placeholder blocked), `--comments` cross-checks against the original comments file; complements the ghost-revision gate (Phase 8) |
| [scripts/check_numbers.py](../../scripts/check_numbers.py) | Verify manuscript/table numbers against `results/*.csv` |
| [scripts/check_gate.py](../../scripts/check_gate.py) | Verify `review/gates/*.GATE.md` status and required checks |
| [scripts/check_revision_claims.py](../../scripts/check_revision_claims.py) | Verify response-letter `[CHANGE]` claims against revised manuscript files |
| [scripts/compile_response_docx.py](../../scripts/compile_response_docx.py) | Compile `response_letter_REV*.md` to Author_response-style DOCX |
| [scripts/search_pubmed.py](../../scripts/search_pubmed.py) | PubMed search script (NCBI E-utilities, no external packages) |
| [scripts/critical_review.py](../../scripts/critical_review.py) | OpenRouter multi-model adversarial reviewer caller (one model failure does not abort) |

---

## Requirements

- Claude AI (Claude Code CLI or VSCode extension)
- Python 3.10+ (`python -m harness doctor` warns on older interpreters; tests: `pip install -r requirements-dev.txt`)
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

🇺🇸 [English](README.md) | 🇰🇷 [한국어](README.ko.md) | 🇯🇵 [日本語](README.ja.md) | 🇨🇳 [中文](README.zh.md)

# Medical Academic Paper Writing Workflow for Claude

A structured workflow system for academic medical paper writing using Claude AI.

## Version

**v0.8.0** (2026-06-16)

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
- **Draft plan template** (`docs/draft_plan_template.md`) — 10-item template with claim→citation tables and approval checklist
- **PubMed search tool** with built-in Python script (no MCP or external packages required)
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
│   ├── statistical_analysis_guide.md  # Statistical analysis guide
│   ├── evidence_guide.md         # Evidence writing guide
│   ├── revision_guide.md         # Reviewer response guide
│   ├── figure_guide.md           # Figure generation guide
│   ├── docx_guide.md             # DOCX conversion guide
│   └── draft_plan_template.md    # Draft plan template (copy to drafts/ for Phase 3)
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
│   └── search_pubmed.py          # PubMed search tool (no external deps)
├── results/                      # Analysis outputs
├── drafts/                       # Manuscript sections, tables & figures
│   ├── draft_plan.md             # Manuscript outline & strategy (required before drafting)
│   ├── table_*.md
│   └── figures/
├── review/                       # QC documents
│   └── qc_log.md
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
6. **QC**: Run minimum 3 QC rounds before submission
7. **Finalize**: Compile manuscript to DOCX (see `docs/docx_guide.md`)

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
- Round 6: Critical review (overclaiming, logical fallacy, bias, generalizability)

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
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | Statistical analysis workflow |
| [docs/evidence_guide.md](docs/evidence_guide.md) | Evidence writing guide (format, summary methods, workflow) |
| [docs/revision_guide.md](docs/revision_guide.md) | Reviewer response guide (response letter, diplomatic language, QC re-run checklist) |
| [docs/figure_guide.md](docs/figure_guide.md) | Figure generation guide (DPI, palettes, Python templates) |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX conversion guide (formatting, table style, naming rules) |
| [docs/draft_plan_template.md](docs/draft_plan_template.md) | Draft plan template — 10-item with claim→citation tables and approval checklist |
| [Style/style_guide.md](Style/style_guide.md) | Style anchor workflow, extraction framework, and PDF-to-MD mirror rules |
| [Style/terminology.md](Style/terminology.md) | Preferred/forbidden terminology registry with definition and context |
| [Style/own/example_YYYY_Journal_keyword.md](Style/own/example_YYYY_Journal_keyword.md) | Own-paper style-anchor template |
| [scripts/lint_manuscript.py](scripts/lint_manuscript.py) | Manuscript lint script for terminology, placeholders, overclaiming, and section issues |
| [scripts/search_pubmed.py](scripts/search_pubmed.py) | PubMed search script (NCBI E-utilities, no external packages) |

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

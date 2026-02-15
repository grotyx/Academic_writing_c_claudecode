# Medical Academic Paper Writing Workflow for Claude

A structured workflow system for academic medical paper writing using Claude AI with MCP (Model Context Protocol) integration.

## Version

**v0.2.3** (2026-02-15)

---

## Overview

This project provides a comprehensive framework for writing academic medical papers with Claude AI assistance. It includes:

- **Structured project organization** for manuscripts, data, and references
- **Expert team simulation** (Clinical Expert, Methodology Expert, Statistician, Editor)
- **Statistical analysis workflow** with Python script generation
- **Quality control procedures** with minimum 3-round verification
- **Study-type specific checklists** (STROBE, CONSORT, PRISMA, CARE, etc.)
- **MCP integration** for PubMed search and reference management

---

## Project Structure

```
project/
├── CLAUDE.md                     # Core rules & configuration
├── README.md                     # This file
├── docs/                         # Reference guides
│   ├── writing_guide.md          # Section-by-section writing guide
│   ├── expert_roles.md           # Expert team roles & responsibilities
│   ├── checklist_guide.md        # Study-type specific checklists
│   ├── qc_guide.md               # Quality control procedures
│   ├── statistical_analysis_guide.md  # Statistical analysis guide
│   ├── evidence_guide.md         # Evidence 작성 가이드
│   └── docx_guide.md            # DOCX 변환 가이드
├── knowledge/                    # Reference materials
│   ├── evidence.md               # 참고문헌 요약 정리 자료집
│   ├── pdf/                      # Original PDF files
│   └── summaries/                # 개별 논문 full-text 상세 요약
├── data/                         # Statistical analysis
│   ├── raw_data.csv              # Original dataset
│   ├── analysis_plan.md          # Auto-generated analysis plan
│   └── py/                       # Python analysis scripts
├── results/                      # Analysis outputs
├── drafts/                       # Manuscript sections, tables & figures
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

1. **Setup**: Update `CLAUDE.md` with your research topic, target journal, and study design
2. **References**: Search PubMed, summarize & register in `knowledge/evidence.md` (see `docs/evidence_guide.md`)
3. **Data Analysis**: Place data in `data/` folder and run statistical analysis
4. **Drafting**: Write sections in recommended order (Methods → Results → Introduction → Discussion)
5. **QC**: Run minimum 3 QC rounds before submission
6. **Finalize**: Compile manuscript to DOCX (see `docs/docx_guide.md`)

---

## Key Features

### Expert Team Simulation
- **Dr. Researcher A**: Clinical perspective (Introduction, Discussion)
- **Dr. Researcher B**: Methodology (Methods, Results, Tables)
- **Dr. Statistician**: Statistical validation
- **Dr. Editor**: Final polish, consistency check

### Redundancy Prevention
- Avoid triple duplication (Results text + Table + Figure)
- Clear guidelines for Table vs Figure decision
- Standard table structure (Table 1: Demographics, Table 2: Main Results)

### MCP Integration
- PubMed search and import
- DOI-based paper retrieval
- Reference formatting (Vancouver, AMA, APA, etc.)

---

## Documentation

| Document | Purpose |
|----------|---------|
| [CLAUDE.md](CLAUDE.md) | Core rules and project configuration |
| [docs/writing_guide.md](docs/writing_guide.md) | Section-by-section writing instructions |
| [docs/expert_roles.md](docs/expert_roles.md) | Expert team descriptions |
| [docs/checklist_guide.md](docs/checklist_guide.md) | STROBE, CONSORT, PRISMA, CARE checklists |
| [docs/qc_guide.md](docs/qc_guide.md) | Quality control procedures |
| [docs/statistical_analysis_guide.md](docs/statistical_analysis_guide.md) | Statistical analysis workflow |
| [docs/evidence_guide.md](docs/evidence_guide.md) | Evidence 작성 가이드 (형식, 요약 방법, 워크플로우) |
| [docs/docx_guide.md](docs/docx_guide.md) | DOCX 변환 가이드 (서식, 테이블 스타일, 네이밍 규칙) |

---

## Requirements

- Claude AI with MCP support
- Python 3.x (for statistical analysis)
- Required Python packages: pandas, numpy, scipy, statsmodels, python-docx

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

### v0.2.3 (2026-02-15)

- Added `docs/docx_guide.md` for DOCX conversion rules (formatting, table style, file naming)
- Output files now include date suffix: `manuscript_YYMMDD.docx`, `title_page_YYMMDD.docx`, `table_N_YYMMDD.docx`
- Title page generated as separate DOCX file
- Tables generated as individual DOCX files with three-line style (no background, no vertical borders)
- Manuscript body: 10pt font, continuous line numbering, page numbers, no heading styles (prevents collapse/expand)
- Updated CLAUDE.md Phase 6 workflow and Quick Commands to reference docx_guide.md
- Added python-docx to requirements

### v0.2.2 (2026-02-10)
- Separated evidence guide from evidence registry
- Added `docs/evidence_guide.md` with detailed summarization instructions (entry format, good/bad examples, checklist)
- Refactored `knowledge/evidence.md` to pure data template (guide content moved to docs)
- Updated `knowledge/` folder role hierarchy: PDF (원본) → summaries (개별 상세) → evidence (종합 정리)

### v0.2.1 (2026-02-07)
- Fixed Introduction phrase contradiction (`"The purpose of this study was to..."` marked as both acceptable)
- Removed unused `review/consistency_check.md` from project structure (merged into `qc_log.md`)
- Renamed `data/statistical_guide.md` to `data/analysis_plan.md` for naming clarity
- Moved tables and figures from `output/` to `drafts/` (`output/` now contains only final docx)
- Created draft section templates (`drafts/01_title.md` ~ `09_figure_legends.md`)
- Created table templates (`drafts/table_1.md` ~ `table_3.md`)
- Upgraded QC Round 4 (Abbreviation/Tense) from Optional to RECOMMENDED (HIGH)
- Added level tags (필수/권장/선택) to all checklists (STROBE, CONSORT, PRISMA, CARE)
- Added level tags to General Submission Checklist
- Added level tags to Statistical Analysis Guide quality checklist
- Deleted stray `_ul` file
- Fixed `claude.md` → `CLAUDE.md` case mismatch in CLAUDE.md project structure tree
- Added missing `statistical_analysis_guide.md` to CLAUDE.md project structure tree
- Fixed `statistical_analysis_guide.md` header version from v0.2 to v0.2.1
- Fixed stale `output/` → `drafts/` path reference in `statistical_analysis_guide.md` Step 5

### v0.2 (2026-02-03)
- Added Statistical Analysis Guide (`docs/statistical_analysis_guide.md`)
- Added Table/Figure/Results redundancy prevention rules
- Added standard table structure guidelines
- Updated expert roles with Dr. Statistician responsibilities
- Reorganized documentation structure

### v0.1 (Initial)
- Basic project structure
- Writing guide, expert roles, checklists, QC guide
- MCP integration for PubMed and references

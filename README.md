# Academic Paper Writing Workflow for Claude

A structured workflow system for academic medical paper writing using Claude AI with MCP (Model Context Protocol) integration.

## Version

**v0.2** (2026-02-03)

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
│   └── statistical_analysis_guide.md  # Statistical analysis guide
├── knowledge/                    # Reference materials
│   ├── evidence.md               # Master reference registry
│   ├── pdf/                      # Original PDF files
│   └── summaries/                # Key paper summaries
├── data/                         # Statistical analysis
│   ├── raw_data.csv              # Original dataset
│   ├── statistical_guide.md      # Auto-generated analysis plan
│   └── py/                       # Python analysis scripts
├── results/                      # Analysis outputs
├── drafts/                       # Manuscript sections
├── review/                       # QC documents
│   ├── consistency_check.md
│   └── qc_log.md
└── output/                       # Final compiled manuscript
    ├── table_*.md
    ├── figures/
    └── manuscript_final.docx
```

---

## Quick Start

1. **Setup**: Update `CLAUDE.md` with your research topic, target journal, and study design
2. **References**: Search PubMed and register papers in `knowledge/evidence.md`
3. **Data Analysis**: Place data in `data/` folder and run statistical analysis
4. **Drafting**: Write sections in recommended order (Methods → Results → Introduction → Discussion)
5. **QC**: Run minimum 3 QC rounds before submission
6. **Finalize**: Compile manuscript and prepare for submission

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

---

## Requirements

- Claude AI with MCP support
- Python 3.x (for statistical analysis)
- Required Python packages: pandas, numpy, scipy, statsmodels

---

## Author

**Professor Sang-Min Park, M.D., Ph.D.**

Department of Orthopaedic Surgery
Seoul National University Bundang Hospital
Seoul National University College of Medicine

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
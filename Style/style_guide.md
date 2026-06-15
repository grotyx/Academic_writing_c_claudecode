# Style Guide

`Style/` is separate from `knowledge/`.

Use `knowledge/` for manuscript references: reference PDFs, evidence summaries, and citation support. Use `Style/` for writing-style anchors: own papers, landmark papers, and target-journal house style.

PDFs are copyright-protected and must remain local only. Store PDFs under `Style/PDF/`; PDF files in that tree are gitignored.

Use `Style/terminology.md` as the project vocabulary registry. It defines preferred terms, forbidden terms, first-definition rules, and context of use.

---

## Folder Roles

| Location | Role |
|---|---|
| `Style/PDF/own/` | Source PDFs of the author's own published papers |
| `Style/own/` | Extracted own-paper style anchors: terminology, team voice, reusable Methods phrasing, key claims |
| `Style/PDF/landmark/` | Source PDFs of landmark/high-quality papers |
| `Style/landmark/` | Extracted framing anchors: argument structure, gap framing, Discussion logic |
| `Style/PDF/target_journal/` | Source PDFs from the target journal |
| `Style/target_journal/` | Extracted house-style anchors: section flow, sentence rhythm, reporting conventions |
| `Style/terminology.md` | Preferred/forbidden terminology registry used during drafting, polish, and linting |

---

## PDF to MD Mirror Rule

Use matching basenames between PDF and extracted markdown.

```text
Style/PDF/own/park_2025_bjj_bed_md.pdf
Style/own/park_2025_bjj_bed_md.md

Style/PDF/landmark/weber_2007_sciatica.pdf
Style/landmark/weber_2007_sciatica.md

Style/PDF/target_journal/smith_2024_lumbar_rct.pdf
Style/target_journal/smith_2024_lumbar_rct.md
```

Use `author_year_keyword` naming.

If a downloaded PDF already has a generic publisher filename and is not renamed, keep the extracted markdown basename identical to the PDF and record the human-readable citation in `Style/landmark/index.md` or the relevant folder index.

---

## Copyright and Extraction Policy

Style anchor markdown files should extract patterns, not reproduce the paper.

Recommended:
- Short phrases only when necessary
- Generalized sentence patterns with placeholders
- Section flow and paragraph function
- Preferred vocabulary and forbidden vocabulary
- Quantitative style metrics
- Qualitative writing observations

Avoid:
- Full paragraph copying
- Large verbatim excerpts
- Reusing distinctive sentences as-is

---

## Extraction Framework

Each style anchor should include both quantitative and qualitative extraction.

### 1. Own Papers

Purpose: preserve the author's research-team voice and field-specific consistency.

Quantitative extraction:
- Section word counts: Abstract, Introduction, Methods, Results, Discussion
- Sentence length: mean and range by section
- Paragraph count by section
- Abbreviation definitions and first-use pattern
- Preferred terminology frequency, e.g., BESS, ODI, VAS, CPK
- Reusable Methods phrase count, e.g., design, ethics, outcomes, statistics
- Citation density by section, e.g., citations per paragraph
- Table/Figure count and placement

Qualitative extraction:
- Team voice: conservative, direct, clinically oriented, methodological
- Preferred terminology and terms to avoid
- Reusable Methods boilerplate patterns
- Standard outcome definitions
- Standard limitation wording
- Key claims that can support future Claim -> Citation Mapping
- Phrasing that should remain consistent across related papers

### 2. Landmark Papers

Purpose: learn argument quality, framing, and Discussion logic.

Quantitative extraction:
- Introduction paragraph structure, e.g., burden -> treatment -> gap -> aim
- Number of claims per Introduction paragraph
- Citation density and citation clustering
- Discussion paragraph count and function distribution
- Hedging marker frequency, e.g., may, suggests, appears, indicates
- Comparison frequency, e.g., consistent with, differs from, in contrast to
- Limitation count and placement

Qualitative extraction:
- How the clinical problem is framed
- How the evidence gap is made important
- How the study aim follows from the gap
- How prior studies are compared without overclaiming
- How negative or neutral findings are framed
- How limitations are acknowledged without weakening the whole paper
- Argument moves worth adapting, not copying

### 3. Target-Journal Papers

Purpose: match the target journal's house style.

Quantitative extraction:
- Title length and structure
- Abstract word count and subheading style
- Section word counts
- Mean sentence length by section
- Subheading depth and naming conventions
- Reference style: bracket vs superscript, author cutoff, DOI use
- Table/Figure density and caption length
- Results text density, e.g., number of numeric values repeated outside tables
- P-value and CI formatting patterns

Qualitative extraction:
- Title and abstract rhythm
- How early the study design appears
- How sparse or detailed the Results narrative is
- Whether Methods are procedural or concise
- Preferred transition phrases
- Strength of conclusion language
- Journal-specific formatting habits
- Things not to imitate because they are topic-specific rather than journal-style

---

## Recommended Style Anchor Template

```markdown
# Style Anchor: Author Year Journal Keyword

## Source
- PDF: Style/PDF/[own|landmark|target_journal]/author_year_keyword.pdf
- Anchor type: own / landmark / target_journal
- Reason for inclusion:

## Quantitative Metrics
| Metric | Value | Notes |
|---|---:|---|
| Title words | | |
| Abstract words | | |
| Introduction paragraphs | | |
| Methods paragraphs | | |
| Results paragraphs | | |
| Discussion paragraphs | | |
| Mean sentence length | | |
| Tables/Figures | | |
| Citation density | | |

## Qualitative Style Notes
- Overall tone:
- Section flow:
- Claim strength:
- Hedging style:
- Results reporting style:
- Discussion logic:

## Reusable Patterns
| Context | Generalized Pattern |
|---|---|
| Study design | This was a [design] study conducted at [setting] between [dates]. |
| Primary outcome | The primary outcome was [endpoint] at [time point]. |
| Main finding | The principal finding was that [finding], suggesting [cautious interpretation]. |

## Preferred Vocabulary
| Concept | Use | Avoid |
|---|---|---|
| | | |

## Do Not Imitate
-
```

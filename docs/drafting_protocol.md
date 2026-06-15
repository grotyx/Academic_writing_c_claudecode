# Drafting Protocol

> Mandatory workflow for drafting manuscript sections. This protocol prevents unsupported claims, terminology drift, and generic LLM prose.

---

## Required Inputs Before Drafting

Before drafting any section, check these files:

| Input | Purpose |
|---|---|
| `drafts/draft_plan.md` | Key message, tone, table/figure plan, claim-to-citation mapping |
| `data/analysis_plan.md` | Research question, endpoints, statistical methods |
| `results/` and `drafts/table_*.md` | Numerical results and table references |
| `knowledge/evidence.md` | Verified citation support |
| `Style/terminology.md` | Preferred and forbidden terminology |
| `Style/style_guide.md` and relevant `Style/*/*.md` anchors | House style, team voice, argument patterns |
| `docs/section_templates.md` | Section-specific structure and sentence patterns |
| `docs/writing_guide.md` | General academic writing rules |

Do not draft if `drafts/draft_plan.md` is absent or incomplete.

---

## Drafting Sequence

### Step 1. Paragraph-Level Outline

Create a paragraph-level outline before writing prose.

Each paragraph must include:
- Paragraph function
- Source of content: evidence number, table, figure, analysis plan, or style anchor
- Allowed claims
- Forbidden content

Example:

```markdown
Paragraph 2: Evidence gap
- Function: explain limitation of prior studies
- Source: draft_plan claim 4; evidence [7], [9]
- Allowed claim: comparative evidence remains limited for [population]
- Forbidden: claim superiority, mention current study results
```

### Step 2. Evidence-Bound Draft

Convert the outline to prose using only mapped evidence and approved results.

Rules:
- Introduction claims must map to `knowledge/evidence.md` or approved style anchors.
- Methods must match `data/analysis_plan.md`.
- Results must match `drafts/table_*.md` and `results/`.
- Discussion interpretation must be grounded in the actual Results.
- No new citations, numbers, endpoints, or analyses may be invented during drafting.

### Step 3. Section Template Pass

Apply `docs/section_templates.md`.

Rules:
- Use the section's paragraph functions.
- Use sentence patterns as patterns, not copied boilerplate.
- Follow section-specific forbidden content rules.

### Step 4. Terminology Pass

Apply `Style/terminology.md`.

Rules:
- Replace forbidden terms with preferred terms.
- Define abbreviations once in the main text.
- Do not mix synonyms for the same concept.
- If the target journal requires a different term, document the exception in `drafts/draft_plan.md`.

### Step 5. Style Anchor Pass

Apply relevant files under `Style/own/`, `Style/landmark/`, and `Style/target_journal/`.

Rules:
- Use own anchors for team voice and Methods consistency.
- Use landmark anchors for argument structure and framing.
- Use target-journal anchors for house style and reporting density.
- Do not copy full sentences or paragraphs from source papers.

### Step 6. Lint and QC Pass

Run the manuscript lint script:

```bash
python scripts/lint_manuscript.py drafts/
```

Address high-priority findings before considering the section complete.

---

## Section-Specific Guardrails

| Section | Must Use | Must Not Use |
|---|---|---|
| Introduction | Background evidence, gap, purpose | Current study results or interpretation |
| Methods | Approved design, endpoints, analyses | Results, post hoc methods not in analysis plan |
| Results | Tables, figures, analysis outputs | Interpretation, clinical implications, causal claims |
| Discussion | Principal findings, comparison, implications, limitations | New results, unsupported claims, overstatement |
| Conclusion | Brief take-home message | New claims, exact numbers, overgeneralization |

---

## Completion Checklist

- [ ] Paragraph outline was created before prose.
- [ ] Every factual claim has an evidence/table/analysis-plan source.
- [ ] No unsupported citation or placeholder remains.
- [ ] Terminology follows `Style/terminology.md`.
- [ ] Section follows `docs/section_templates.md`.
- [ ] Style anchors were applied without copying source text.
- [ ] `scripts/lint_manuscript.py` was run and findings were addressed or documented.

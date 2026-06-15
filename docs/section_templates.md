# Section Templates and Sentence Patterns

> Use this file during the Section Template Pass in `docs/drafting_protocol.md`.
> Sentence patterns are scaffolds. Replace bracketed content and avoid copying source papers verbatim.

---

## General Rules for All Sections

- Use preferred terminology from `Style/terminology.md`.
- Use one term for one concept throughout the manuscript.
- Keep clinical findings as sentence subjects, not statistical tests.
- Use exact citations only after specific claims.
- Avoid unsupported adjectives such as dramatic, remarkable, groundbreaking, or unprecedented.
- Do not use em dashes in running text.

---

## Title

Purpose: identify population, intervention/exposure, comparator when relevant, and study design.

Preferred patterns:
- `[Intervention] versus [Comparator] for [Condition]: A [Study Design]`
- `[Outcome] After [Intervention] for [Condition]: A [Study Design]`
- `[Intervention] for [Population] With [Condition]: A [Study Design]`

Avoid:
- `A study of...`
- `Investigation into...`
- Unnecessary abbreviations unless universally known

---

## Abstract

Purpose: provide a self-contained summary after the main text is complete.

Paragraph or subheading functions:
1. Background/Purpose: clinical problem and objective
2. Methods: design, setting, population, intervention/comparator, endpoints
3. Results: primary outcome first, then key secondary/safety results
4. Conclusion: cautious take-home statement

Preferred patterns:
- `This study aimed to [objective].`
- `The primary outcome was [endpoint] at [time point].`
- `[Outcome] [improved/differed] in [group/time], whereas [secondary finding].`
- `These findings suggest that [cautious conclusion].`

Avoid:
- Citations unless journal requires them
- Excessive p-value listing
- Claims not present in the main text

---

## Introduction

Purpose: establish background, evidence gap, and study aim.

Paragraph functions:
1. Clinical burden or disease relevance
2. Current treatment or knowledge base
3. Evidence gap or unresolved question
4. Study objective and hypothesis

Preferred patterns:
- `[Condition] remains a major cause of [clinical burden] in [population].`
- `[Intervention] has been increasingly used because [rationale], but [limitation] remains unclear.`
- `Previous studies have reported [known finding]; however, [specific gap] has not been fully established.`
- `Therefore, this study aimed to [objective].`
- `We hypothesized that [predefined hypothesis].`

Citation rule:
- Place citations immediately after the specific claim they support.
- Do not stack unrelated citations at the end of a paragraph.

Avoid:
- Current study results
- Overstating novelty, e.g., first ever, groundbreaking
- Broad textbook background that does not lead to the study question

---

## Methods

Purpose: make the study reproducible.

Subsection functions:
1. Study design and setting
2. Participants or patients
3. Intervention/exposure/comparator
4. Outcome measures
5. Data collection and follow-up
6. Statistical analysis

Preferred patterns:
- `This was a [design] study conducted at [setting] between [dates].`
- `Patients were eligible if they [inclusion criteria].`
- `Patients were excluded if they [exclusion criteria].`
- `The primary outcome was [endpoint] at [time point].`
- `Secondary outcomes included [outcomes].`
- `Continuous variables were summarized as [mean (SD) or median (IQR)] according to distribution.`
- `Between-group comparisons were performed using [test], as appropriate.`

Avoid:
- Results or interpretation
- Post hoc analyses not listed in `data/analysis_plan.md`
- Statistical tests as the main focus when endpoints should be the focus

---

## Results

Purpose: report findings without interpretation.

Subsection functions:
1. Patient flow and baseline characteristics
2. Primary outcome
3. Secondary outcomes
4. Additional or exploratory analyses
5. Adverse events or complications

Preferred patterns:
- `A total of [N] patients were [screened/enrolled/included], of whom [N] were included in the final analysis.`
- `Baseline characteristics are summarized in Table 1.`
- `The primary outcome [improved/differed] [within/between] groups at [time point] (Table 2).`
- `No significant between-group difference was observed in [outcome] (Table 2).`
- `Adverse events are summarized in Table [N].`

Reporting density rule:
- Refer to tables for detailed values.
- In text, report direction, clinical relevance when necessary, and table reference.
- Do not repeat every table value in the Results text.

Avoid:
- `suggests`, `indicates`, `may explain`, `clinically meaningful` unless explicitly reporting a predefined clinical threshold
- Discussion of mechanisms
- New analyses not in tables/results files

---

## Discussion

Purpose: interpret findings in context and define limitations.

Paragraph functions:
1. Principal findings
2. Comparison with prior literature
3. Clinical or methodological implications
4. Secondary findings or safety findings
5. Limitations
6. Conclusion-style final paragraph if journal format allows

Preferred patterns:
- `The principal finding of this study was that [main finding].`
- `This finding aligns with previous studies reporting [comparison].`
- `Conversely, [difference] may be explained by [cautious explanation].`
- `From a clinical perspective, these findings suggest that [implication].`
- `Several limitations should be acknowledged.`
- `First, [limitation]. Second, [limitation].`
- `Further studies are needed to [future direction].`

Hedging rule:
- Observational studies and small samples should use moderate or weak hedging.
- Use strong claims only for direct, well-powered evidence.

Avoid:
- Restating all Results numbers
- New outcomes or subgroup findings not reported in Results
- Overclaiming causality
- Dismissing conflicting studies without explanation

---

## Conclusion

Purpose: provide a brief, cautious take-home message.

Preferred patterns:
- `In conclusion, [intervention/exposure] was associated with [main finding] in [population].`
- `These findings support [cautious implication], although [limitation/future validation] remains necessary.`
- `Further studies with [design/follow-up/sample] are warranted.`

Avoid:
- Exact p-values or detailed numbers
- New limitations not discussed earlier
- Strong practice-changing language unless directly justified

---

## References

Purpose: list only verified citations used in the manuscript.

Rules:
- Every reference must exist in `knowledge/evidence.md` or be verified before use.
- Follow `profile/journals.md` for journal-specific formatting.
- Remove unused references.
- Ensure numbering follows order of appearance if the target journal uses numbered references.

# Verifier Prompt Templates

This file defines the constrained LLM verifier layer used after deterministic
helpers. Run deterministic scripts first; use these prompts only for semantic
checks that cannot be decided by exact matching.

## Non-Negotiable Verifier Rules

All LLM verifiers must follow these rules:

1. Use only the supplied artifact bundle. Do not use outside knowledge.
2. If evidence is absent, incomplete, or ambiguous, return `FAIL`.
3. Do not rewrite the manuscript unless explicitly asked. Identify failures and required actions.
4. Do not accept broad paraphrase when the gate requires a specific manuscript change.
5. Output the exact structured format below. No prose before or after it.

## Common Output Schema

```yaml
verifier: <Constraint-Compliance | Semantic-Citation | Logic-Redundancy | Data-Interpretation | Revision-Alignment>
artifact: <path>
status: <PASS | FAIL>
checked_against:
  - <path or supplied source name>
findings:
  - id: <short id>
    severity: <critical | major | minor>
    location: <section/paragraph/line if available>
    verdict: <SUPPORTED | PARTIALLY_SUPPORTED | UNSUPPORTED | NOT_ENOUGH_INFORMATION | NOT_APPLICABLE>
    reason: <one sentence>
    required_action: <specific action>
gate_check_key: <constraint | citation | numbers | logic | response_alignment>
```

Gate rule: any `critical` or `major` finding makes `status: FAIL`.

## Constraint-Compliance Verifier

Use for: instruction violations, section guardrails, forbidden content, missing required inputs.

Required inputs:

- `CLAUDE.md`
- `docs/drafting_protocol.md`
- `docs/section_templates.md`
- `drafts/draft_plan.md`
- current artifact

Prompt:

```text
You are the Constraint-Compliance verifier for an academic manuscript workflow.
Use only the supplied files. Check whether the artifact violates project rules,
section guardrails, draft_plan constraints, terminology decisions, or required
workflow order. If any required source is absent or the artifact cannot be
verified from the supplied files, return FAIL.

Pay special attention to:
- Results interpretation appearing in Introduction or Results.
- New analyses, endpoints, or inclusion/exclusion criteria not in analysis_plan.
- Claims, citations, or numbers not present in the approved plan/source files.
- Forbidden terminology or synonym drift.
- Manuscript text written in reviewer-response style.

Return only the Common Output Schema.
```

## Semantic-Citation Verifier

Use for: whether a cited source actually supports the sentence after
`scripts/check_citations.py` has confirmed that `[EVID:id]` exists.

Required inputs:

- artifact sentence or paragraph
- `knowledge/evidence.md` entry
- `knowledge/summaries/<id>.md` when available

Prompt:

```text
You are the Semantic-Citation verifier. Use only the supplied evidence entry and
summary. For each cited claim, decide whether the cited evidence supports the
claim direction, population, intervention/comparator, outcome, and certainty.

FAIL if:
- The cited evidence is absent, todo, or abstract-only but the claim exceeds the abstract.
- Direction, population, intervention/comparator, or outcome does not match.
- The manuscript states causality, superiority, safety, or certainty beyond the source.
- The claim needs weakening, replacement, or a different citation.

Return only the Common Output Schema.
```

## Data-Interpretation Verifier

Use for: whether the prose interpretation is consistent with verified results
after `scripts/check_numbers.py` has confirmed exact numeric traceability.

Required inputs:

- artifact paragraph
- relevant `results/*.csv`
- relevant `drafts/table_*.md`
- `data/analysis_plan.md`

Prompt:

```text
You are the Data-Interpretation verifier. Use only the supplied results,
tables, and analysis plan. Check whether the artifact interprets the verified
numbers correctly.

FAIL if:
- A non-significant result is framed as a trend, equivalence, or superiority.
- A secondary/exploratory endpoint is framed as primary.
- The prose omits uncertainty that changes the interpretation.
- The text repeats table numbers unnecessarily instead of summarizing the result.
- A p-value, confidence interval, or effect direction is logically inconsistent.

Return only the Common Output Schema.
```

## Logic-Redundancy Verifier

Use for: duplicated Results/Discussion content, circular logic, verbose
paragraphs, and section-to-section mismatch.

Required inputs:

- current artifact
- adjacent sections when relevant
- `drafts/draft_plan.md`
- relevant tables/results

Prompt:

```text
You are the Logic-Redundancy verifier. Use only the supplied manuscript sections
and plan. Check whether the artifact has coherent academic-paper logic and does
not repeat content across sections.

FAIL if:
- Results and Discussion repeat the same sentence or detailed numeric content.
- Introduction contains current study interpretation.
- Discussion repeats background without connecting to current findings.
- Conclusion includes new claims or exact numbers.
- Paragraphs are verbose, circular, or answer a different question than the section requires.
- The local paragraph logic does not support the stated manuscript argument.

Return only the Common Output Schema.
```

## Revision-Alignment Verifier

Use for: reviewer response vs revised manuscript consistency after
`scripts/check_revision_claims.py` has checked `[CHANGE]` markers.

Required inputs:

- reviewer comment
- response paragraph
- original manuscript section if available
- revised manuscript section
- `[CHANGE]` block

Prompt:

```text
You are the Revision-Alignment verifier. Use only the supplied reviewer comment,
response, and manuscript sections. Check whether the author response directly
answers the reviewer and whether the manuscript revision matches what the
response claims.

FAIL if:
- The response does not directly answer the reviewer question.
- The response claims a change that is absent or materially different in the revised manuscript.
- The response quotes revised text that is not in the manuscript.
- The revised manuscript is written as a reply to the reviewer.
- The response includes manuscript-style text in the wrong place or fails to state the actual revision.
- A prior correction is overwritten or contradicted by a later revision.

Return only the Common Output Schema.
```

## Recording Results In Gate Ledger

After deterministic scripts and LLM verifiers pass, record the result in
`review/gates/phase_NN_<name>.GATE.md` using `review/gates/_TEMPLATE.GATE.md`.
Then run `scripts/check_gate.py`.

Example:

```powershell
py scripts\check_gate.py review\gates\phase_04_draft.GATE.md --artifact drafts\05_results.md --require-check constraint --require-check citation --require-check numbers --require-check logic
```

# Shared manuscript engine (v1.0.0)

Project release: v1.7.0. Python 3.10+; install `requirements.txt` and pytest for development. Run commands from the repository root. On Windows replace `python` with `py` if needed. Real manuscripts belong in a separate private project; the repository's tracked drafts are public templates, and `.gitignore` cannot protect edits to tracked files.

## Runtime setup

`WORKFLOW.md` contains shared rules. Claude reads `CLAUDE.md`, Codex reads the case-sensitive `AGENTS.md`, and Gemini reads `GEMINI.md`; each points to the shared rules. These are bootstrap instructions, not proof that a given CLI loaded them. Claude hooks and slash commands are optional conveniences; no hook can guarantee all shell writes are intercepted.

```sh
python -m harness doctor
python -m harness status --project /path/to/private-paper/project.json
python -m harness verify --project /path/to/private-paper/project.json --profile draft
python -m harness packet --project /path/to/private-paper/project.json
python -m harness verify --project /path/to/private-paper/project.json --profile revision
python -m harness verify --project /path/to/private-paper/project.json --profile submission
python -m harness build --project /path/to/private-paper/project.json
```

Doctor reports installed capabilities only; it does not authenticate CLIs or contact providers. Packet creates a local, size-limited source bundle; it does not send it. For an authorized external review, `scripts/critical_review.py --target FILE --context PACKET --include-claude` or `--include-codex` invokes the chosen CLI. OpenRouter uses `--models`/`--models-file`. Gemini can coordinate the common workflow but has no automated reviewer subprocess here. Live CLI authentication/flag compatibility must be checked in the user's environment. The Codex subprocess uses a read-only filesystem sandbox, which is not a guarantee against all configured network/MCP capabilities.

One unavailable reviewer does not cancel other reviewers. Review output includes requested/completed providers, source hashes, and complete/partial/failed status. Exit 0 means at least one response, not a gate PASS. `--out` creates a unique run directory. Consensus prioritizes investigation; it does not establish correctness. Sources missing from the packet must be reported UNVERIFIABLE.

## Project manifest

Copy `docs/project.example.json` to the private project root as `project.json` and fill it. Paths resolve relative to that manifest and cannot escape its root. `artifacts` is publication order, not drafting order. For revisions, explicitly list the latest submitted overlay: changed REVn files plus unchanged sections from earlier revisions or the initial draft. Do not list both old and new versions of the same section.

Supported study types: original_research, systematic_review, narrative_review, case_report. Non-original studies may provide an explicit `analysis_not_applicable` or `numbers_not_applicable` reason where appropriate. Original research requires analysis and numerical checks. The engine does not decide scientific appropriateness of exemptions.

`numeric_artifacts` declares the scope of result-token verification. Include Results, abstract and result tables as applicable; semantic data review must also check completeness of this declared scope. `dependencies` lists source excerpts, statistical run logs, baseline files outside the conventional revision layout and any other material reviewers relied on. `review_sources` selects additional files from dependencies for the packet. All results CSVs in the declared results directory enter its hash snapshot; never point it at another paper's parent directory.

## Profiles and receipts

- Draft: citations, lint, plan completeness, numbers, optional contextual bindings, abstract if declared, cross-references and bibliography. Missing legacy approval receipt/bindings can be allowed only here; this is not submission clearance.
- Revision: draft checks plus source-bound plan approvals, structured numerical bindings, independent/human semantic review, strict change claims and original-comment coverage. Requires `response` and `comments`.
- Submission: also requires human signoff, AI disclosure record and a completed reporting checklist. Missing/invalid input is BLOCKED; detected violations are FAIL; justified omitted checks are NOT_APPLICABLE. PASS covers the selected profile only.

After an actual human approval, retain the checked approval line and record the exact approved content:

```sh
python -m harness record-approval /path/to/private-paper/data/analysis_plan.md --kind analysis --approved-by 'Actual reviewer' --decision-reference 'Actual decision date/message'
```

The adjacent `.approval.json` contains status, approved_by, decision_reference and sha256. The command records an existing decision; it never grants approval. These JSON receipts are provenance, not authenticated signatures. Changing the approved file invalidates the receipt. Plans require substantive sections, including missing-data handling in analysis plans; checkbox-only plans fail.

Use `packet`'s `dependencies` verbatim in semantic-review and human-signoff records. Semantic record: `status: PASS`, nonempty `reviewer`, `method: independent` or `human`, empty unresolved `findings`, and `checks` mapping constraint, citation_semantics, data_semantics, logic, style, reporting to PASS. Human record: `status: approved`, reviewer, decision_reference, dependencies. Never populate these with invented reviews. Changes to files, dependency membership or checker implementation invalidate reviews. Mandatory QC rounds remain a reviewer responsibility; receipts do not prove work was performed.

## Contextual numeric bindings

`result_bindings` points to JSON containing `results` and `bindings` arrays. Each result contains result_id, paper_id, raw, outcome, timepoint, population, comparison, statistic, unit, and source `{file, row, column, sha256}`. CSV row numbering includes the header as row 1. A cell must contain one numeric value/bound; split mean and SD into distinct columns.

Each binding contains artifact, artifact_sha256, token_index (zero-based checker token order), result_id, and context with the six fields above. Every token in numeric_artifacts must be bound exactly once. Swapped paper/context, edited CSV/artifact and absent tokens fail. This validates the declared connection; it does not infer a sentence's clinical meaning. Independent semantic data review is still required to detect an incorrectly declared mapping.

## Citation and revision migration

Allowed source statuses are verified, full-text-reviewed and abstract-only. Abstract-only is not full-text claim verification. Unknown/empty/todo/retracted statuses fail. Duplicate evidence keys fail before overwriting. New PubMed imports use author_year_pmid identifiers (DOI hash fallback); existing unique IDs remain valid. Do not globally rename old IDs; resolve actual collisions and update only affected citations. Same DOI registered under distinct IDs still requires a registry audit.

P-value comparisons preserve strict/inclusive bounds, reject exact zero, and recognize scientific notation and simple pipe-table p-value columns. Complex HTML/LaTeX tables are outside this parser. XX/TODO/TBD placeholders cannot hide other numbers. Gate artifact hashes and live-check paths must resolve to the ledger artifact.

REVn comparisons search the latest earlier revision containing each section before falling back to the initial draft. Keep previous submissions immutable. Custom baseline arrangements must be documented and explicitly included in dependencies; automatic arbitrary baseline-commit selection is not implemented. Keyword/diff checks still require semantic response-alignment review.

## Submission output and limits

AI JSON: `used` boolean and `reviewed_by`; when used, also tools and disclosure. Record actual tool/model/version/date/role/input scope/human reviewer in tools. Distinguish writing assistance from AI used as a study method. Checklist JSON: guideline, version, source_url, reviewed_by, items with id/status/location (or NOT_APPLICABLE with reason). Use the current applicable official checklist; the engine validates completion records, not official item coverage.

Build re-verifies submission, creates a unique output directory, converts EVID tags, writes separate manuscript/title/table DOCX files, copies figures, and optionally compiles the response. It checks input and approval freshness again before publishing the package and records output hashes. It never edits source drafts. Citation formatting preserves source Citation strings and is not a CSL journal-style engine. Markdown support is intentionally limited to prose, headings and simple pipe tables; code fences, display math and embedded images block conversion. Inspect/render the DOCX and apply journal-specific formatting before submission. A built package is not automatically visually approved or submitted.

The engine is a foundation, not autonomous scientific validation: statistical reproducibility, complete reporting-item coverage, semantic claim support, reviewer identity and final layout still require documented human review. No live provider calls are part of the automated test suite.

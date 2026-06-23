# Medical-KAG Integration Protocol

> Use the `medical-kag-remote` MCP (a spine-surgery knowledge-augmented graph) **alongside**
> `knowledge/evidence.md`, without weakening the grounding guarantees of this workflow.

## The grounding rule (non-negotiable)

`knowledge/evidence.md` stays the **single canonical citation ledger**. medical-kag is an
**upstream discovery / analysis / formatting engine** — never a citation source the manuscript
reads directly.

- A paper surfaced by medical-kag is cited **only after** it is registered in
  `knowledge/evidence.md` as `[EVID:author_year]` (Rule 1). `scripts/check_citations.py` still
  gates every `[EVID:id]`.
- Numbers still come only from `results/*.csv` (Rule, `check_numbers.py`). medical-kag effect
  sizes inform the literature comparison, not the study's own Results.
- STOP signal: "medical-kag가 찾았으니 바로 인용해도 돼" → register in `evidence.md` first,
  verify the PMID/DOI, then cite.

## Availability + fallback

medical-kag is **additive, not a dependency**. If a call fails (e.g. `Invalid or missing
session` — the remote MCP is registered but not authenticated this session), **degrade
gracefully** to the existing workflow: `scripts/search_pubmed.py` for discovery, manual
`evidence.md` registration, `profile/journals.md` for reference style. Never block on the MCP.

## Operational notes (field-tested 2026-06)

Observed behavior against the live graph (~1,150 docs):

- **Canonical node names matter.** The graph normalizes interventions — e.g. "biportal
  endoscopic discectomy" is stored as **`UBE`**. `compare_interventions` / `intervention`
  return empty for a non-canonical name. If a structured call comes back empty, retry with the
  canonical/abbreviated form (UBE, TLIF, ACDF…) before concluding "no data".
- **Structured comparison is a scan, not a clean head-to-head.** `compare_interventions`
  aggregates outcomes across heterogeneous papers, so the set is large and noisy (a lumbar
  query surfaced cervical/thoracic outcomes; baseline traits like "Age" appear as "outcomes").
  Use it to MAP which outcomes favor which technique and which papers support it, then read the
  source papers — do not treat the aggregate as one comparison.
- **Trust direction/rating, verify the numbers.** Effect magnitudes are sparsely populated
  (observed ~21/87 outcomes had a value; `conflict synthesize` returned effect `0.00`). Take the
  GRADE rating / direction / p-value as a lead, but pull the actual numbers from the source paper
  → `knowledge/evidence.md` / `results/*.csv` (grounding rule).
- **Ingestion is server-side.** The remote server cannot read local paths, so `document add_pdf`
  with a local PDF fails ("파일 없음"). Use `pubmed import_by_doi` / `import_by_pmids` (server
  fetches) or `analyze store_paper` (push structured data). DOI import may return abstract-only
  (`text_source: abstract`) — enough for `reference`, not for full structured outcomes.
- **Sessions are short-lived.** The remote session can drop ("Invalid or missing session") after
  a few calls. Verify with `document stats` first, do KAG work in short bursts, and keep the
  `search_pubmed.py` fallback ready — never block on the MCP.
- **Reliable today:** `search`, `conflict find/synthesize` (GRADE), `reference
  format/format_multiple`, and — with canonical names — `compare_interventions`. Taxonomy
  (`intervention hierarchy/comparable`) and per-paper numeric values are sparsely populated.

## Capability map (tool → use)

| Need | medical-kag call |
|---|---|
| Find evidence | `search` action=`search`/`adaptive`/`best_evidence`; `pubmed` action=`hybrid_search` |
| Structured extraction | `analyze` action=`text`; `document` action=`summarize` |
| Claim → evidence chain (multi-hop) | `search`/`graph` action=`evidence_chain`; `graph` action=`multi_hop` |
| Compare two interventions | `search`/`graph` action=`compare_interventions`; `intervention` action=`compare`/`hierarchy` |
| Conflicting studies / GRADE synthesis | `conflict` action=`find`/`detect`/`synthesize` |
| Evidence strength / quality | `extended` action=`quality_metrics` (GRADE, MINORS, Newcastle-Ottawa…) |
| Journal-style reference list | `reference` action=`format_multiple` (style=`jbjs`/`spine`/`vancouver`…, `target_journal`) |

## Per-phase usage

### Phase 1 — Evidence discovery & registration (primary win)
1. Discover with `search`/`pubmed hybrid_search` (local-first, PubMed auto-fallback) by topic.
2. Surface controversies early with `conflict` action=`find` (topic).
3. Extract structure with `analyze` action=`text` (interventions, outcomes, `evidence_level`,
   `study_design`) or `document summarize`.
4. **Bridge:** register each paper to cite in `knowledge/evidence.md` as `[EVID:author_year]`,
   filling the entry from the analyze output. Verify it exists (PMID/DOI). Only then is it
   citable. (See `docs/evidence_guide.md` for the entry format.)

### Phase 3–4 — Claim→Citation mapping & Discussion
- Validate each draft-plan claim with `graph`/`search` action=`evidence_chain` (multi-hop) and
  `search` action=`reason`.
- For the Discussion's comparisons, use `compare_interventions` + `intervention hierarchy`, and
  `conflict synthesize` for a GRADE strength-of-evidence statement.
- `graph draft_citations` (topic, section_type) can suggest citations — but cite only those
  already registered in `evidence.md`. The Rule 8 claim→citation mapping is still authoritative.

### Phase 6 — QC conflict / overclaim guard
- `conflict` action=`detect`/`find` → does the manuscript's claim ignore conflicting evidence?
  An overclaiming guard for the Discussion (complements Round 6 critical review).
- `extended quality_metrics` → is the stated strength of evidence justified?
- Cross-check `evidence.md` entries against the KG for consistency.

### Phase 7 — References
- `reference` action=`format_multiple` with the target journal style (`set_journal_style` /
  `add_custom_style` for a new journal); export `bibtex`/`ris`. Cross-check against
  `profile/journals.md` (the canonical journal-format registry).

## Codex / cross-runtime

From Codex or another runtime, the same MCP tools are reachable via tool search. If medical-kag
is unavailable there, follow the fallback above — `search_pubmed.py` + `evidence.md` keep the
workflow fully functional.

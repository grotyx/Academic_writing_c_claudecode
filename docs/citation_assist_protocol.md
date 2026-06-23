# Citation Assist Protocol (GraphRAG-backed)

> Two evidence operations that speed and harden citation work — citation **suggestion**
> and a per-claim **verification report** — backed by the medical-kag knowledge graph
> (GraphRAG) when available, falling back to `knowledge/evidence.md` when it is not.

## Backend rule (grounding preserved)

- **Primary:** medical-kag MCP (GraphRAG) — semantic retrieval over the graph.
- **Fallback:** `knowledge/evidence.md` (+ `scripts/search_pubmed.py` for new sources) when the
  MCP is unavailable (the remote session can be flaky; see `docs/medical_kag_protocol.md`).
- **Canonical ledger unchanged:** `knowledge/evidence.md` is the only source of `[EVID:id]`.
  Anything the graph surfaces is registered there (PMID/DOI verified) **before** it becomes a
  citable `[EVID:id]`. `scripts/check_citations.py` still gates.

---

## Operation 1 — Citation suggestion (`/suggest-citation [claim]`)

Goal: given a draft claim that needs support, propose the best `[EVID:id]` candidate(s).

1. **Retrieve (KAG primary):** medical-kag `search` action `evidence`/`evidence_chain`/
   `best_evidence` (or `search`) on the claim → candidate papers, ranked, with evidence level.
2. **Fallback (KAG down):** scan `knowledge/evidence.md` for entries whose summary/key points
   match the claim; if nothing fits, `py scripts/search_pubmed.py search "<claim terms>"` for new
   candidates.
3. **Register before citing:** for any candidate not yet in `evidence.md`, register it as
   `[EVID:author_year]` (verify PMID/DOI) per `docs/evidence_guide.md`.
4. **Output:** ranked `[EVID:id]` candidates, each with a one-line reason it supports the claim
   (direction / population / intervention / outcome). The author picks — do not auto-insert silently.

Use in Phase 3 (claim→citation mapping, Rule 8) and Phase 4 (drafting).

---

## Operation 2 — Claim-verification report (`/verify-claims [section]`)

Goal: a per-sentence "claim map" — is each cited sentence actually supported by its evidence?

1. **Extract claims (deterministic):** `py scripts/extract_claims.py <section> --json` → each
   `[EVID:id]`-tagged sentence.
2. **Retrieve evidence:** for each claim's `[EVID:id]`, pull the source content — medical-kag
   (KAG primary: the paper's structured data / chunks) or the `evidence.md` entry (fallback).
3. **Classify (NLI / Semantic-Citation Verifier):** run the Semantic-Citation Verifier
   (`docs/verifier_prompt_templates.md`) on (sentence, evidence) → `SUPPORTED` / `PARTIAL` /
   `UNSUPPORTED` (entailment / partial / not-supported-or-contradicted), with a one-line reason
   and required action.
4. **Report:** write `review/claim_verification.md` — a table of `location | claim | [EVID:id] |
   verdict | action`. Any `UNSUPPORTED`/`PARTIAL` is a fix item (weaken the claim, change the
   citation, or register better evidence).

Use as a **Phase 6 QC round** (claim-level grounding), complementing the deterministic
`check_citations.py` (existence) and the inline Phase-4 draft gates.

---

## Operation 3 — Citation stance (`/cite-stance [claim | section]`)

Goal: tag how each cited source relates to a claim — supporting / contrasting / mentioning —
so the Discussion stays balanced (Scite-style, claim-specific).

1. **Identify** the claim(s) and their `[EVID:id]` (`scripts/extract_claims.py` for a whole section).
2. **Retrieve + find contrasts:** pull each source (KAG primary, evidence.md fallback); use
   medical-kag `conflict find/detect` to surface contrasting studies that may be missing.
3. **Classify** each source with the Citation-Stance verifier (`docs/verifier_prompt_templates.md`):
   supporting / contrasting / mentioning + reason.
4. **Output** a stance summary; flag **one-sided** if contrasting evidence exists but is not
   cited (overclaim-by-omission guard). Use when writing or QC-ing the Discussion.

---

## Operation 4 — Evidence comparison table (`/evidence-table [topic | EVID ids]`)

Goal: a "summary of included studies" table (Elicit-style) for the Discussion or a PRISMA
supplement.

1. **Gather structured records** for the target papers — KAG primary (`analyze` fields /
   `compare_interventions`: design, n, intervention, outcome, effect, p, evidence level);
   evidence.md fallback (from the entry summaries; rougher).
2. **Format:** emit JSON records, then `py scripts/evidence_table.py <records.json> --columns
   study,design,n,intervention,outcome,result,loe` → a markdown table.
3. **Save** to `drafts/table_evidence.md` (or a supplement). Verify every number against the
   source (grounding) — KAG values can be sparse/noisy; `evidence.md` / `results` are canonical.

---

## Guardrails

- Never invent a citation to satisfy a claim — if nothing supports it, weaken or flag the claim
  (CLAUDE.md Rule 1 + STOP signals).
- KAG is discovery/analysis; `evidence.md` stays canonical. Verify KAG numbers from the source
  (`evidence.md` / `results`) before they enter the manuscript.
- Both operations degrade gracefully: with no MCP, `evidence.md` + `search_pubmed.py` keep them
  fully functional.

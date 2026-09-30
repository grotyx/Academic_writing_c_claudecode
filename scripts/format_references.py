#!/usr/bin/env python3
"""Format `[EVID:id]` citations into a journal-style bibliography + convert in-text tags.

**MCP-independent**: reads `knowledge/evidence.md` (the canonical citation ledger)
only -- no medical-kag required. This is the Phase 7 conversion that turns the
drafting-time `[EVID:author_year]` tags into a submission-ready reference list.

Two styles:
  - **numbered** (Vancouver) -- `[EVID:id]` -> `[N]` by order of first appearance
    across the given files; the reference list is numbered in that same order.
  - **author-year** -- `[EVID:id]` -> `(Author, Year)`; the reference list is
    alphabetical by author.

`--journal NAME` renders the list in a target journal's format instead (author cutoff,
superscript or bracket markers, page range, issue, DOI, order; presets in journal_styles.py)
and groups adjacent tags ("[EVID:a] [EVID:b]" -> "[1,2]" or "^1,2^"). `--fetch` first caches
full PubMed metadata for cited entries with a PMID (knowledge/reference_metadata.json).

By default it prints the id->label mapping and the reference list. With
`--convert` it also writes each manuscript file with tags replaced to a sibling
`*_formatted.md` -- **never in place** (the source draft is left untouched).

A cited id absent from evidence.md is left unconverted and reported as a warning
(check_citations.py is the gate that blocks those).

Evidence parsing reuses check_citations.py so the ledger is read identically.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
# author_year[_keyword] id -> (author, year); supports a trailing disambiguation
# letter (2020a) and an optional descriptive suffix (kim_2020_fusion).
ID_AUTHOR_YEAR_RE = re.compile(r"^(.*?)_((?:19|20)\d{2}[a-z]?)(?:_.*)?$")


def _load_sibling(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_cc = _load_sibling("check_citations")
_js = _load_sibling("journal_styles")
STYLES = _js.STYLES
METADATA_NAME = "reference_metadata.json"
parse_evidence_entries = _cc.parse_evidence_entries
iter_evid_tokens = _cc.iter_evid_tokens
EVID_RE = _cc.EVID_RE
strip_code_fences = _cc.strip_code_fences


class FormatResult(NamedTuple):
    style: str
    order: list[str]  # known evidence_ids in first-appearance order
    labels: dict[str, str]  # evidence_id -> in-text label ("[1]" or "(Smith, 2020)")
    references: list[str]  # formatted reference list lines, already ordered
    unknown: list[str]  # cited ids absent from evidence.md (left unconverted)
    missing_citation: list[str]  # known ids whose evidence.md Citation field is empty
    in_text: str = "bracket"  # "bracket" | "superscript" (journal presets)
    incomplete_authors: list[str] = []  # journal mode: author list could not be expanded past "et al."
    unparsed: list[str] = []  # journal mode: Citation string not parseable, used as registered


def author_year(evidence_id: str) -> tuple[str, str] | None:
    """Split an author_year id into (Author, Year); None if it doesn't match."""
    match = ID_AUTHOR_YEAR_RE.match(evidence_id)
    if not match:
        return None
    author = match.group(1).replace("_", " ").strip().title()
    return author or evidence_id, match.group(2)


def collect_order(artifacts: list[Path]) -> list[str]:
    """Evidence ids in order of first appearance across all artifacts."""
    seen: list[str] = []
    seen_set: set[str] = set()
    for artifact in artifacts:
        for citation_id, _line in iter_evid_tokens(artifact):
            if citation_id not in seen_set:
                seen_set.add(citation_id)
                seen.append(citation_id)
    return seen


def reference_string(evidence_id: str, entry) -> str:
    """Best available citation string for an evidence entry."""
    citation = (entry.fields.get("citation") or "").strip()
    if citation:
        return citation
    # Fall back to the heading text, else a flagged placeholder.
    heading = (entry.heading or "").strip()
    heading = re.sub(r"^\[\d+\]\s*", "", heading)  # drop a leading "[3] "
    return heading or f"[EVID:{evidence_id}] (citation missing in evidence.md)"


def metadata_path(evidence_path: Path) -> Path:
    return evidence_path.with_name(METADATA_NAME)


def journal_build(entries, known, unknown, missing, evidence_path: Path, journal: str) -> FormatResult:
    style = STYLES[journal]
    cache = _js.load_cache(metadata_path(evidence_path))
    metas, incomplete, unparsed = {}, [], []
    for eid in known:
        fields = entries[eid].fields
        pmid = (fields.get("pmid") or "").strip()
        meta = cache.get(pmid) or _js.from_citation(fields.get("citation") or "", (fields.get("doi") or "").strip())
        metas[eid] = meta
        if meta is None:
            unparsed.append(eid)
        elif not meta["complete"] and (style["cutoff"] is None or len(meta["authors"]) < style["cutoff"][1]):
            incomplete.append(eid)  # the journal wants more authors than the stored string holds
    order = list(known)
    if style.get("order") == "alphabetical":
        def key(eid):
            meta = metas[eid]
            return ((meta["authors"][0][0].lower() if meta and meta["authors"] else eid), meta["year"] if meta else "")
        order = sorted(order, key=key)
    labels, references = {}, []
    for index, eid in enumerate(order, start=1):
        labels[eid] = str(index)
        text = _js.render(metas[eid], style) if metas[eid] else reference_string(eid, entries[eid])
        references.append(f"{index}. {text}")
    return FormatResult(journal, order, labels, references, unknown, missing, style["in_text"], incomplete, unparsed)


def fetch_metadata(artifacts: list[Path], evidence_path: Path) -> int:
    """Cache full PubMed metadata for cited entries that carry a PMID. Returns the count fetched."""
    entries = parse_evidence_entries(evidence_path.read_text(encoding="utf-8"))
    pmids = sorted({(entries[e].fields.get("pmid") or "").strip() for e in collect_order(artifacts) if e in entries} - {""})
    if not pmids:
        return 0
    pubmed = _load_sibling("search_pubmed")
    cache = _js.load_cache(metadata_path(evidence_path))
    for article in pubmed.fetch_articles(pmids):
        cache[article["pmid"]] = _js.from_pubmed(article)
    metadata_path(evidence_path).write_text(json.dumps(cache, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    return len(pmids)


def build(artifacts: list[Path], *, evidence_path: Path, style: str, journal: str | None = None) -> FormatResult:
    entries = parse_evidence_entries(evidence_path.read_text(encoding="utf-8"))
    order = collect_order(artifacts)

    known = [eid for eid in order if eid in entries]
    unknown = [eid for eid in order if eid not in entries]
    missing_citation = [
        eid for eid in known if not (entries[eid].fields.get("citation") or "").strip()
    ]

    if journal:
        return journal_build(entries, known, unknown, missing_citation, evidence_path, journal)

    labels: dict[str, str] = {}
    references: list[str] = []

    if style == "numbered":
        for index, eid in enumerate(known, start=1):
            labels[eid] = f"[{index}]"
            references.append(f"{index}. {reference_string(eid, entries[eid])}")
    elif style == "author-year":
        for eid in known:
            ay = author_year(eid)
            labels[eid] = f"({ay[0]}, {ay[1]})" if ay else f"({eid})"
        # Reference list alphabetical by (author, year), de-duplicated by id.
        def sort_key(eid: str) -> tuple[str, str]:
            ay = author_year(eid)
            return (ay[0].lower(), ay[1]) if ay else (eid.lower(), "")

        for eid in sorted(set(known), key=sort_key):
            references.append(reference_string(eid, entries[eid]))
    else:  # pragma: no cover - guarded by argparse choices
        raise ValueError(f"unknown style: {style}")

    return FormatResult(style, known, labels, references, unknown, missing_citation)


GROUP_RE = re.compile(r"\[EVID:[^\]]+\](?:[\s,;]*\[EVID:[^\]]+\])*")


def convert_text(text: str, labels: dict[str, str], in_text: str | None = None) -> str:
    """Replace each [EVID:id] with its label; unknown ids are left untouched.

    With `in_text` (journal mode) labels are plain numbers and adjacent tags are grouped
    into one marker: "[1,2]", "[1–3]" or "^1,2^".
    """
    if in_text:
        def group(match: re.Match) -> str:
            ids = EVID_RE.findall(match.group(0))
            if not all(i in labels for i in ids):
                return match.group(0)
            return _js.group_label([int(labels[i]) for i in ids], in_text)
        return GROUP_RE.sub(group, text)

    def repl(match: re.Match) -> str:
        evidence_id = match.group(1)
        return labels.get(evidence_id, match.group(0))

    return EVID_RE.sub(repl, text)


def format_report(result: FormatResult) -> str:
    lines = [
        f"REFERENCES ({result.style})",
        f"cited: {len(result.order)} unique | unknown: {len(result.unknown)} | "
        f"missing citation field: {len(result.missing_citation)}",
        "",
        "reference list:",
    ]
    lines.extend(result.references or ["  (none)"])
    if result.unknown:
        lines.append("")
        lines.append("WARNING -- cited but not in evidence.md (left unconverted):")
        lines.extend(f"  EVID:{eid}" for eid in result.unknown)
    if result.missing_citation:
        lines.append("")
        lines.append("WARNING -- no Citation field in evidence.md (used fallback text):")
        lines.extend(f"  EVID:{eid}" for eid in result.missing_citation)
    if result.incomplete_authors:
        lines.append("")
        lines.append("WARNING -- stored author list ends in 'et al.' but this journal lists more authors; "
                     "run with --fetch (needs a PMID) or complete the Citation field:")
        lines.extend(f"  EVID:{eid}" for eid in result.incomplete_authors)
    if result.unparsed:
        lines.append("")
        lines.append("WARNING -- Citation not in Vancouver form; used as registered (check format by hand):")
        lines.extend(f"  EVID:{eid}" for eid in result.unparsed)
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Format [EVID:id] citations into a reference list and convert in-text tags."
    )
    parser.add_argument("--strict", action="store_true", help="Block invalid source status or incomplete bibliography before conversion")
    parser.add_argument("artifacts", nargs="+", type=Path, help="Manuscript section markdown files.")
    parser.add_argument(
        "--evidence",
        type=Path,
        default=ROOT / "knowledge" / "evidence.md",
        help="evidence.md registry (default knowledge/evidence.md).",
    )
    parser.add_argument(
        "--style",
        choices=("numbered", "author-year"),
        default="numbered",
        help="Citation style (default numbered/Vancouver).",
    )
    parser.add_argument(
        "--journal",
        choices=sorted(STYLES),
        help="Render the reference list in this journal's format (overrides --style); "
             "see journal_styles.py for each preset's rules.",
    )
    parser.add_argument(
        "--fetch",
        action="store_true",
        help="First cache full PubMed metadata (all authors, issue, month) for cited entries with a PMID.",
    )
    parser.add_argument(
        "--convert",
        action="store_true",
        help="Also write each file with tags replaced to a sibling *_formatted.md (never in place).",
    )
    parser.add_argument(
        "--out-suffix",
        default="_formatted",
        help="Filename suffix for --convert output (default _formatted).",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    if args.fetch:
        print(f"fetched PubMed metadata for {fetch_metadata(args.artifacts, args.evidence)} PMID(s) -> "
              f"{metadata_path(args.evidence)}")
    result = build(args.artifacts, evidence_path=args.evidence, style=args.style, journal=args.journal)
    print(format_report(result))
    if args.strict:
        citation_check = _cc.check_citations(args.artifacts, evidence_path=args.evidence)
        if result.unknown or result.missing_citation or not citation_check.passed:
            print("Strict bibliography validation failed; no files written.")
            return 1
    if args.convert and not args.out_suffix:
        print("Output suffix cannot be empty (would overwrite the source).")
        return 2

    if args.convert:
        print("")
        print("converted files:")
        for artifact in args.artifacts:
            text = artifact.read_text(encoding="utf-8")
            converted = convert_text(text, result.labels, result.in_text if args.journal else None)
            out_path = artifact.with_name(f"{artifact.stem}{args.out_suffix}{artifact.suffix}")
            out_path.write_text(converted, encoding="utf-8")
            print(f"  {out_path}")

    # Unknown citations are a real problem (hallucinated/unregistered) -> non-zero.
    return 1 if result.unknown else 0


if __name__ == "__main__":
    raise SystemExit(main())

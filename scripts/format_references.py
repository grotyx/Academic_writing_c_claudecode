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
import re
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent
# author_year id -> (author, year); supports a trailing disambiguation letter (2020a).
ID_AUTHOR_YEAR_RE = re.compile(r"^(.*?)_((?:19|20)\d{2}[a-z]?)$")


def _load_sibling(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_cc = _load_sibling("check_citations")
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


def build(artifacts: list[Path], *, evidence_path: Path, style: str) -> FormatResult:
    entries = parse_evidence_entries(evidence_path.read_text(encoding="utf-8"))
    order = collect_order(artifacts)

    known = [eid for eid in order if eid in entries]
    unknown = [eid for eid in order if eid not in entries]
    missing_citation = [
        eid for eid in known if not (entries[eid].fields.get("citation") or "").strip()
    ]

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


def convert_text(text: str, labels: dict[str, str]) -> str:
    """Replace each [EVID:id] with its label; unknown ids are left untouched."""

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
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Format [EVID:id] citations into a reference list and convert in-text tags."
    )
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
    result = build(args.artifacts, evidence_path=args.evidence, style=args.style)
    print(format_report(result))

    if args.convert:
        print("")
        print("converted files:")
        for artifact in args.artifacts:
            text = artifact.read_text(encoding="utf-8")
            converted = convert_text(text, result.labels)
            out_path = artifact.with_name(f"{artifact.stem}{args.out_suffix}{artifact.suffix}")
            out_path.write_text(converted, encoding="utf-8")
            print(f"  {out_path}")

    # Unknown citations are a real problem (hallucinated/unregistered) -> non-zero.
    return 1 if result.unknown else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Verify draft [EVID:id] citations against knowledge/evidence.md.

This is the deterministic first gate for citation grounding. It does not judge
whether a cited paper semantically supports a sentence. It blocks references
that are absent from the evidence registry or explicitly marked as unverified
(`Source Status: todo`).
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
EVID_RE = re.compile(r"\[EVID:([A-Za-z0-9_.-]+)\]")
HEADING_RE = re.compile(r"^###\s+(.+?)\s*$", flags=re.MULTILINE)
FIELD_RE = re.compile(r"^-\s+\*\*(.+?):\*\*\s*(.*)$")
FENCE_RE = re.compile(r"```.*?```", flags=re.DOTALL)


class EvidenceEntry(NamedTuple):
    evidence_id: str
    heading: str
    source_status: str
    fields: dict[str, str]


class CitationIssue(NamedTuple):
    artifact: Path
    citation_id: str
    line: int
    reason: str
    required_action: str


class CitationCheckResult(NamedTuple):
    passed: bool
    checked_tokens: int
    failures: list[CitationIssue]
    warnings: list[CitationIssue]


def normalize_key(value: str) -> str:
    return value.strip().casefold().replace(" ", "_").replace("-", "_")


def normalize_status(value: str) -> str:
    return value.strip().casefold()


def strip_code_fences(text: str) -> str:
    return FENCE_RE.sub("", text)


def slugify_id(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower())
    return re.sub(r"_+", "_", slug).strip("_")


def parse_fields(block: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw_line in block.splitlines():
        match = FIELD_RE.match(raw_line.strip())
        if not match:
            continue
        fields[normalize_key(match.group(1))] = match.group(2).strip()
    return fields


def derive_id_from_heading_or_citation(heading: str, fields: dict[str, str]) -> str:
    evid_match = re.search(r"\[EVID:([A-Za-z0-9_.-]+)\]", heading)
    if evid_match:
        return evid_match.group(1)

    bracket_match = re.match(r"\[([^\]]+)\]", heading.strip())
    if bracket_match and not bracket_match.group(1).isdigit():
        return slugify_id(bracket_match.group(1))

    candidate = heading
    citation = fields.get("citation", "")
    if citation:
        candidate = citation

    author_match = re.search(r"([A-Z][A-Za-z'-]+)", candidate)
    year_match = re.search(r"(19|20)\d{2}", candidate)
    if author_match and year_match:
        return f"{author_match.group(1).lower()}_{year_match.group(0)}"
    return ""


def parse_evidence_entries(evidence_text: str) -> dict[str, EvidenceEntry]:
    matches = list(HEADING_RE.finditer(evidence_text))
    entries: dict[str, EvidenceEntry] = {}

    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(evidence_text)
        block = evidence_text[start:end]
        fields = parse_fields(block)
        evidence_id = (
            fields.get("evidence_id")
            or fields.get("id")
            or fields.get("evid")
            or derive_id_from_heading_or_citation(heading, fields)
        )
        if not evidence_id:
            continue
        entries[evidence_id] = EvidenceEntry(
            evidence_id=evidence_id,
            heading=heading,
            source_status=normalize_status(fields.get("source_status", "")),
            fields=fields,
        )
    return entries


def iter_evid_tokens(artifact: Path) -> list[tuple[str, int]]:
    text = strip_code_fences(artifact.read_text(encoding="utf-8"))
    tokens: list[tuple[str, int]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for match in EVID_RE.finditer(line):
            tokens.append((match.group(1), line_number))
    return tokens


def check_citations(
    artifacts: list[Path],
    *,
    evidence_path: Path | None = None,
    require_citations: bool = False,
    fail_abstract_only: bool = False,
) -> CitationCheckResult:
    registry_path = evidence_path or ROOT / "knowledge" / "evidence.md"
    evidence_entries = parse_evidence_entries(registry_path.read_text(encoding="utf-8"))
    failures: list[CitationIssue] = []
    warnings: list[CitationIssue] = []
    checked_tokens = 0

    for artifact in artifacts:
        if not artifact.exists():
            failures.append(
                CitationIssue(
                    artifact,
                    "<file>",
                    0,
                    "artifact file not found",
                    "Correct the artifact path and rerun citation verification.",
                )
            )
            continue

        tokens = iter_evid_tokens(artifact)
        checked_tokens += len(tokens)
        if require_citations and not tokens:
            failures.append(
                CitationIssue(
                    artifact,
                    "<none>",
                    0,
                    "no [EVID:id] citations found",
                    "Add evidence-grounded citation tags or rerun without --require-citations.",
                )
            )

        for citation_id, line_number in tokens:
            entry = evidence_entries.get(citation_id)
            if entry is None:
                failures.append(
                    CitationIssue(
                        artifact,
                        citation_id,
                        line_number,
                        "citation id not found in knowledge/evidence.md",
                        "Register the source in evidence.md or replace the citation id.",
                    )
                )
                continue

            if not entry.source_status:
                failures.append(
                    CitationIssue(
                        artifact,
                        citation_id,
                        line_number,
                        "missing Source Status in evidence entry",
                        "Add Source Status: verified | abstract-only | full-text-reviewed | todo.",
                    )
                )
                continue

            if entry.source_status == "todo":
                failures.append(
                    CitationIssue(
                        artifact,
                        citation_id,
                        line_number,
                        "Source Status is todo",
                        "Verify the source and update Source Status before citing it.",
                    )
                )
                continue

            if entry.source_status == "abstract-only":
                issue = CitationIssue(
                    artifact,
                    citation_id,
                    line_number,
                    "Source Status is abstract-only",
                    "Use only claims supported by the abstract or verify the full text.",
                )
                if fail_abstract_only:
                    failures.append(issue)
                else:
                    warnings.append(issue)

    return CitationCheckResult(not failures, checked_tokens, failures, warnings)


def format_result(result: CitationCheckResult, artifacts: list[Path], evidence_path: Path) -> str:
    if result.passed:
        lines = [
            "GATE PASS",
            "verifier: Citation-Grounding",
            f"evidence: {evidence_path}",
            f"artifacts: {len(artifacts)}",
            f"checked: {result.checked_tokens} citation token(s), 0 failures",
        ]
        if result.warnings:
            lines.append(f"warnings: {len(result.warnings)}")
            for warning in result.warnings:
                lines.extend(
                    [
                        "---",
                        f"artifact: {warning.artifact}",
                        f"line: {warning.line}",
                        f"citation: EVID:{warning.citation_id}",
                        f"warning: {warning.reason}",
                        f"required_action: {warning.required_action}",
                    ]
                )
        return "\n".join(lines)

    lines = [
        "GATE FAIL",
        "verifier: Citation-Grounding",
        f"evidence: {evidence_path}",
        f"artifacts: {len(artifacts)}",
        f"checked: {result.checked_tokens} citation token(s), {len(result.failures)} failure(s)",
    ]
    for failure in result.failures:
        lines.extend(
            [
                "---",
                f"artifact: {failure.artifact}",
                f"line: {failure.line}",
                f"citation: EVID:{failure.citation_id}",
                f"reason: {failure.reason}",
                f"required_action: {failure.required_action}",
            ]
        )
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify [EVID:id] citations against knowledge/evidence.md.")
    parser.add_argument("artifacts", nargs="*", type=Path, help="Markdown files to check")
    parser.add_argument("--section", action="append", type=Path, default=[], help="Markdown file to check")
    parser.add_argument("--evidence", type=Path, default=ROOT / "knowledge" / "evidence.md", help="Evidence registry path")
    parser.add_argument("--require-citations", action="store_true", help="Fail artifacts that contain no [EVID:id] tags.")
    parser.add_argument("--fail-abstract-only", action="store_true", help="Fail abstract-only sources instead of warning.")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    artifacts = [*args.artifacts, *args.section]
    if not artifacts:
        parser.error("at least one artifact path is required")
    if not args.evidence.exists():
        parser.error(f"Evidence registry not found: {args.evidence}")

    result = check_citations(
        artifacts,
        evidence_path=args.evidence,
        require_citations=args.require_citations,
        fail_abstract_only=args.fail_abstract_only,
    )
    print(format_result(result, artifacts, args.evidence))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

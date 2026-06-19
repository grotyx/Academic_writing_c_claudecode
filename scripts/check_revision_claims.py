#!/usr/bin/env python3
"""Verify reviewer-response change claims against revised manuscript files.

The checker reads machine-readable [CHANGE] blocks from a response letter and
confirms that each referenced revised section exists and contains the expected
terms. When the original section is available, it also fails if the revised
section is unchanged, which catches ghost revisions.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
CHANGE_RE = re.compile(r"\[CHANGE\](.*?)\[/CHANGE\]", flags=re.IGNORECASE | re.DOTALL)
REV_RE = re.compile(r"REV\d+", flags=re.IGNORECASE)


class ChangeClaim(NamedTuple):
    comment_id: str
    claim: str
    section: str
    expected_terms: list[str]
    revised_text: str
    fields: dict[str, str]


class CheckFailure(NamedTuple):
    comment_id: str
    section: str
    reason: str
    required_action: str


class CheckWarning(NamedTuple):
    comment_id: str
    section: str
    reason: str


class CheckResult(NamedTuple):
    passed: bool
    claims: list[ChangeClaim]
    failures: list[CheckFailure]
    warnings: list[CheckWarning]


def normalize_key(value: str) -> str:
    return value.strip().lower().replace(" ", "_").replace("-", "_")


def split_expected_terms(value: str) -> list[str]:
    clean = value.strip().strip("[]")
    if not clean:
        return []
    separator_pattern = r";"
    if ";" not in clean and "," in clean:
        separator_pattern = r","
    return [term.strip().strip("`\"'") for term in re.split(separator_pattern, clean) if term.strip()]


def clean_revised_text(value: str) -> str:
    clean = value.strip()
    for marker in ("**", "__", "*", "_"):
        if clean.startswith(marker) and clean.endswith(marker) and len(clean) > len(marker) * 2:
            clean = clean[len(marker) : -len(marker)].strip()
    return clean


def is_structural_line(value: str) -> bool:
    return bool(
        re.match(r"^(comment\s+[\w.\-)]+|reviewer\s*#?\d+\s*:?)", value, flags=re.IGNORECASE)
        or re.match(r"^(response|location|reviewer closing)\s*:", value, flags=re.IGNORECASE)
        or value.strip().upper() in {"[CHANGE]", "[/CHANGE]"}
    )


def extract_revised_text(text_after_change: str) -> str:
    lines = text_after_change.splitlines()
    for index, raw_line in enumerate(lines):
        line = raw_line.strip()
        match = re.match(r"^revised text:\s*(.*)$", line, flags=re.IGNORECASE)
        if not match:
            continue

        inline_value = clean_revised_text(match.group(1))
        if inline_value:
            return inline_value

        collected: list[str] = []
        for follow_line in lines[index + 1 :]:
            follow = follow_line.strip()
            if not follow:
                if collected:
                    break
                continue
            if is_structural_line(follow):
                break
            collected.append(follow)
        return clean_revised_text(" ".join(collected))
    return ""


def parse_fields(block_text: str) -> dict[str, str]:
    fields: dict[str, str] = {}
    for raw_line in block_text.splitlines():
        line = raw_line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[normalize_key(key)] = value.strip()
    return fields


def parse_change_blocks(response_text: str) -> list[ChangeClaim]:
    matches = list(CHANGE_RE.finditer(response_text))
    claims: list[ChangeClaim] = []

    for index, match in enumerate(matches):
        fields = parse_fields(match.group(1))
        next_start = matches[index + 1].start() if index + 1 < len(matches) else len(response_text)
        text_after_change = response_text[match.end() : next_start]
        claims.append(
            ChangeClaim(
                comment_id=fields.get("comment_id", ""),
                claim=fields.get("claim", ""),
                section=fields.get("section", ""),
                expected_terms=split_expected_terms(fields.get("expected_terms", "")),
                revised_text=extract_revised_text(text_after_change),
                fields=fields,
            )
        )
    return claims


def infer_revision_id(response_path: Path) -> str:
    for value in [response_path.parent.name, response_path.stem]:
        match = REV_RE.search(value)
        if match:
            return match.group(0).upper()
    return ""


def infer_draft_root(response_path: Path) -> Path:
    parts = list(response_path.resolve().parts)
    lowered = [part.lower() for part in parts]
    if "revision" in lowered:
        revision_index = lowered.index("revision")
        if revision_index > 0:
            return Path(*parts[:revision_index])
    return ROOT / "drafts"


def dedupe_paths(paths: list[Path]) -> list[Path]:
    seen: set[Path] = set()
    deduped: list[Path] = []
    for path in paths:
        key = path.resolve() if path.exists() else path.absolute()
        if key not in seen:
            seen.add(key)
            deduped.append(path)
    return deduped


def normalize_section_stem(section: str, revision_id: str) -> str:
    stem = Path(section).stem if section else ""
    if revision_id:
        stem = re.sub(rf"_{re.escape(revision_id)}$", "", stem, flags=re.IGNORECASE)
    return stem


def resolve_revised_section_path(claim: ChangeClaim, response_path: Path, draft_root: Path) -> Path | None:
    section = claim.section.strip()
    if not section:
        return None

    revision_id = infer_revision_id(response_path)
    section_path = Path(section)
    candidates: list[Path] = []

    if section_path.is_absolute():
        candidates.append(section_path)
    elif section_path.suffix:
        candidates.extend(
            [
                response_path.parent / section_path,
                draft_root / section_path,
                ROOT / section_path,
            ]
        )
    else:
        stem = section_path.as_posix()
        if revision_id:
            candidates.extend(
                [
                    response_path.parent / f"{stem}_{revision_id}.md",
                    draft_root / "revision" / revision_id / f"{stem}_{revision_id}.md",
                ]
            )
        candidates.extend(
            [
                response_path.parent / f"{stem}.md",
                draft_root / "revision" / revision_id / f"{stem}.md" if revision_id else draft_root / f"{stem}.md",
                draft_root / f"{stem}.md",
            ]
        )

    for candidate in dedupe_paths(candidates):
        if candidate.exists():
            return candidate
    return None


def resolve_original_section_path(claim: ChangeClaim, response_path: Path, draft_root: Path) -> Path | None:
    section = claim.section.strip()
    if not section:
        return None

    revision_id = infer_revision_id(response_path)
    base_stem = normalize_section_stem(section, revision_id)
    section_path = Path(section)
    candidates: list[Path] = []

    if section_path.is_absolute():
        candidates.append(draft_root / f"{base_stem}.md")
    elif section_path.suffix:
        candidates.extend(
            [
                draft_root / f"{base_stem}.md",
                draft_root / section_path.name,
            ]
        )
    else:
        candidates.append(draft_root / f"{base_stem}.md")

    for candidate in dedupe_paths(candidates):
        if candidate.exists():
            return candidate
    return None


def normalize_for_compare(value: str) -> str:
    text = value.replace("\u201c", '"').replace("\u201d", '"').replace("\u2018", "'").replace("\u2019", "'")
    text = re.sub(r"[*_`]", "", text).strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {"'", '"'}:
        text = text[1:-1].strip()
    return re.sub(r"\s+", " ", text).casefold()


def check_claim(
    claim: ChangeClaim,
    response_path: Path,
    draft_root: Path,
    *,
    strict: bool = False,
) -> tuple[list[CheckFailure], list[CheckWarning]]:
    failures: list[CheckFailure] = []
    warnings: list[CheckWarning] = []

    missing_fields = [
        name
        for name, value in {
            "comment_id": claim.comment_id,
            "section": claim.section,
            "expected_terms": "; ".join(claim.expected_terms),
        }.items()
        if not value
    ]
    if missing_fields:
        failures.append(
            CheckFailure(
                claim.comment_id or "<missing>",
                claim.section or "<missing>",
                f"missing required [CHANGE] field(s): {', '.join(missing_fields)}",
                "Complete comment_id, section, and expected_terms in the [CHANGE] block.",
            )
        )
        return failures, warnings

    revised_path = resolve_revised_section_path(claim, response_path, draft_root)
    if revised_path is None:
        failures.append(
            CheckFailure(
                claim.comment_id,
                claim.section,
                "revised section file not found",
                "Create the revised section file or correct the section field in the [CHANGE] block.",
            )
        )
        return failures, warnings

    revised_text = revised_path.read_text(encoding="utf-8")
    revised_norm = normalize_for_compare(revised_text)

    for term in claim.expected_terms:
        if normalize_for_compare(term) not in revised_norm:
            failures.append(
                CheckFailure(
                    claim.comment_id,
                    claim.section,
                    f"missing expected term: {term}",
                    "Revise the manuscript section or update expected_terms to match the actual change.",
                )
            )

    if claim.revised_text and normalize_for_compare(claim.revised_text) not in revised_norm:
        failures.append(
            CheckFailure(
                claim.comment_id,
                claim.section,
                "revised text quoted in response was not found in revised section",
                "Copy the final manuscript wording into Revised text or update the manuscript to match it.",
            )
        )

    original_path = resolve_original_section_path(claim, response_path, draft_root)
    if original_path is None:
        warning = CheckWarning(claim.comment_id, claim.section, "original section file not found; diff unchanged check skipped")
        if strict:
            failures.append(
                CheckFailure(
                    claim.comment_id,
                    claim.section,
                    warning.reason,
                    "Provide the original section file under the draft root or rerun without --strict.",
                )
            )
        else:
            warnings.append(warning)
    else:
        original_text = original_path.read_text(encoding="utf-8")
        if normalize_for_compare(original_text) == revised_norm:
            failures.append(
                CheckFailure(
                    claim.comment_id,
                    claim.section,
                    "section unchanged from original",
                    "Apply the claimed manuscript revision or remove the change claim from the response.",
                )
            )

    return failures, warnings


def check_revision_claims(
    response_path: Path,
    *,
    draft_root: Path | None = None,
    strict: bool = False,
    allow_no_changes: bool = False,
) -> CheckResult:
    response_path = response_path.resolve()
    root = draft_root.resolve() if draft_root else infer_draft_root(response_path)
    response_text = response_path.read_text(encoding="utf-8")
    claims = parse_change_blocks(response_text)
    failures: list[CheckFailure] = []
    warnings: list[CheckWarning] = []

    if not claims and not allow_no_changes:
        failures.append(
            CheckFailure(
                "<none>",
                "<none>",
                "no [CHANGE] blocks found",
                "Add [CHANGE] blocks for manuscript changes or rerun with --allow-no-changes.",
            )
        )
        return CheckResult(False, claims, failures, warnings)

    for claim in claims:
        claim_failures, claim_warnings = check_claim(claim, response_path, root, strict=strict)
        failures.extend(claim_failures)
        warnings.extend(claim_warnings)

    return CheckResult(not failures, claims, failures, warnings)


def format_result(result: CheckResult, response_path: Path) -> str:
    lines: list[str] = []
    if result.passed:
        lines.extend(
            [
                "GATE PASS",
                "verifier: Ghost-Revision",
                f"artifact: {response_path}",
                f"checked: {len(result.claims)} change claim(s), 0 failures",
            ]
        )
        if result.warnings:
            lines.append(f"warnings: {len(result.warnings)}")
            for warning in result.warnings:
                lines.extend(
                    [
                        f"comment_id: {warning.comment_id}",
                        f"section: {warning.section}",
                        f"warning: {warning.reason}",
                    ]
                )
        return "\n".join(lines)

    lines.extend(
        [
            "GATE FAIL",
            "failure_code: GATE_FAIL REVISION_CLAIMS",
            "verifier: Ghost-Revision",
            f"artifact: {response_path}",
            f"checked: {len(result.claims)} change claim(s), {len(result.failures)} failure(s)",
        ]
    )
    for failure in result.failures:
        lines.extend(
            [
                "---",
                f"comment_id: {failure.comment_id}",
                f"section: {failure.section}",
                f"reason: {failure.reason}",
                f"required_action: {failure.required_action}",
            ]
        )
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify response-letter [CHANGE] claims against revised manuscript files.")
    parser.add_argument("response", nargs="?", type=Path, help="Path to response_letter_REV*.md")
    parser.add_argument("--response", dest="response_option", type=Path, help="Path to response_letter_REV*.md")
    parser.add_argument("--draft-root", type=Path, help="Draft root that contains original sections and revision/REV*/")
    parser.add_argument("--strict", action="store_true", help="Fail if the original section is unavailable for diff checks.")
    parser.add_argument(
        "--allow-no-changes",
        action="store_true",
        help="Pass when no [CHANGE] blocks are present.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    response_path = args.response_option or args.response
    if response_path is None:
        parser.error("response path is required")
    if not response_path.exists():
        parser.error(f"Response file not found: {response_path}")

    result = check_revision_claims(
        response_path,
        draft_root=args.draft_root,
        strict=args.strict,
        allow_no_changes=args.allow_no_changes,
    )
    print(format_result(result, response_path))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

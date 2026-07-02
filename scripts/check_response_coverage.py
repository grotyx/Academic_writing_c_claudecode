#!/usr/bin/env python3
"""Reviewer-comment response coverage checker (Phase 8).

check_revision_claims.py verifies that claimed manuscript changes are real
(ghost-revision gate). This checker covers the opposite face: **did the
response letter answer every reviewer comment at all?** A skipped comment is
an automatic reject trigger and nothing else in the harness catches it.

Checks the response letter (`Reviewer #N:` / `Comment N)` / `Response:`
structure per docs/response_letter_template.md):
  - **RESPONSE_MISSING** -- a Comment with no Response block before the next
    comment/reviewer boundary.
  - **RESPONSE_EMPTY** -- a Response with no content.
  - **RESPONSE_PLACEHOLDER** -- a Response still containing template
    placeholders like "[Response text.]".
  - **COMMENT_GAP** (warning) -- non-contiguous comment numbering within a
    reviewer (Comment 1, Comment 3 -- likely a lost comment).

With --comments (the reviewer_comments_REV*.md original), it cross-checks:
  - **COMMENT_UNANSWERED** -- a comment present in the original but absent
    from the response letter.
  - **COMMENT_EXTRA** (warning) -- a response-letter comment not in the
    original (numbering drift).
If the original cannot be parsed into reviewer/comment structure the
cross-check is skipped with a loud warning (failure under --strict).

Missing/empty/unanswered responses are binary defects, so unlike the advisory
QC checkers this exits non-zero on failures by default.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]

REVIEWER_RE = re.compile(r"^\s*(?:\*{1,2})?\s*Reviewer\s*#?\s*(\d+)\s*:?", re.IGNORECASE)
COMMENT_RE = re.compile(r"^\s*(?:\*{1,2})?\s*Comment\s+(\d+)\s*[).:\]]", re.IGNORECASE)
RESPONSE_RE = re.compile(r"^\s*(?:\*{1,2})?\s*Response\s*:\s*(.*)$", re.IGNORECASE)
# Structural lines that terminate a response body.
BOUNDARY_RE = re.compile(
    r"^\s*(?:\*{1,2})?\s*(Reviewer\s*#?\s*\d+|Comment\s+\d+\s*[).:\]]|Location\s*:|Revised text\s*:|Reviewer closing\s*:|\[CHANGE\])",
    re.IGNORECASE,
)
PLACEHOLDER_RE = re.compile(r"\[[^\]]*\]")


class CommentEntry(NamedTuple):
    reviewer: int
    number: int
    line: int
    response_text: str | None  # None = no Response block at all


class CoverageIssue(NamedTuple):
    code: str
    reviewer: int
    comment: int
    line: int
    message: str


class ResponseCoverageResult(NamedTuple):
    passed: bool
    entries: list[CommentEntry]
    failures: list[CoverageIssue]
    warnings: list[CoverageIssue]


def parse_letter(text: str) -> list[CommentEntry]:
    """Parse Reviewer/Comment/Response structure; [CHANGE] blocks are ignored."""
    text = re.sub(r"\[CHANGE\].*?\[/CHANGE\]", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.IGNORECASE | re.DOTALL)
    lines = text.splitlines()
    entries: list[CommentEntry] = []
    reviewer = 0
    current: dict | None = None  # {"reviewer", "number", "line", "response": str|None}

    def flush() -> None:
        nonlocal current
        if current is not None:
            entries.append(CommentEntry(current["reviewer"], current["number"], current["line"], current["response"]))
            current = None

    index = 0
    while index < len(lines):
        line = lines[index]
        reviewer_match = REVIEWER_RE.match(line)
        comment_match = COMMENT_RE.match(line)
        response_match = RESPONSE_RE.match(line)
        if reviewer_match:
            flush()
            reviewer = int(reviewer_match.group(1))
        elif comment_match:
            flush()
            current = {"reviewer": reviewer, "number": int(comment_match.group(1)), "line": index + 1, "response": None}
        elif response_match and current is not None:
            collected = [response_match.group(1).strip()]
            cursor = index + 1
            while cursor < len(lines):
                follow = lines[cursor]
                if BOUNDARY_RE.match(follow) or RESPONSE_RE.match(follow):
                    break
                collected.append(follow.strip())
                cursor += 1
            current["response"] = " ".join(part for part in collected if part).strip()
            index = cursor - 1
        index += 1
    flush()
    return entries


def parse_original_comments(text: str) -> set[tuple[int, int]]:
    """(reviewer, comment) pairs found in the original reviewer comments file."""
    pairs: set[tuple[int, int]] = set()
    reviewer = 0
    for line in text.splitlines():
        reviewer_match = REVIEWER_RE.match(line)
        if reviewer_match:
            reviewer = int(reviewer_match.group(1))
            continue
        comment_match = COMMENT_RE.match(line)
        if comment_match:
            pairs.add((reviewer, int(comment_match.group(1))))
    return pairs


def check_response_coverage(
    response_path: Path,
    *,
    comments_path: Path | None = None,
    strict: bool = False,
) -> ResponseCoverageResult:
    entries = parse_letter(response_path.read_text(encoding="utf-8"))
    failures: list[CoverageIssue] = []
    warnings: list[CoverageIssue] = []

    if not entries:
        failures.append(CoverageIssue(
            "NO_COMMENTS", 0, 0, 1,
            "No 'Comment N)' entries found in the response letter -- check the structure "
            "against docs/response_letter_template.md.",
        ))
        return ResponseCoverageResult(False, entries, failures, warnings)

    for entry in entries:
        label = f"Reviewer #{entry.reviewer} Comment {entry.number}"
        if entry.response_text is None:
            failures.append(CoverageIssue(
                "RESPONSE_MISSING", entry.reviewer, entry.number, entry.line,
                f"{label} has no Response block.",
            ))
        elif not entry.response_text:
            failures.append(CoverageIssue(
                "RESPONSE_EMPTY", entry.reviewer, entry.number, entry.line,
                f"{label} has an empty Response.",
            ))
        elif PLACEHOLDER_RE.search(entry.response_text):
            failures.append(CoverageIssue(
                "RESPONSE_PLACEHOLDER", entry.reviewer, entry.number, entry.line,
                f"{label} Response still contains a [bracketed] template placeholder.",
            ))

    by_reviewer: dict[int, list[int]] = {}
    for entry in entries:
        by_reviewer.setdefault(entry.reviewer, []).append(entry.number)
    for reviewer, numbers in sorted(by_reviewer.items()):
        expected = list(range(1, max(numbers) + 1))
        missing = sorted(set(expected) - set(numbers))
        if missing:
            warnings.append(CoverageIssue(
                "COMMENT_GAP", reviewer, missing[0], 0,
                f"Reviewer #{reviewer} comment numbering has gap(s): missing "
                f"{', '.join(str(n) for n in missing)}.",
            ))

    if comments_path is not None:
        original = parse_original_comments(comments_path.read_text(encoding="utf-8"))
        if not original:
            issue = CoverageIssue(
                "COMMENTS_UNPARSEABLE", 0, 0, 1,
                f"Could not parse Reviewer/Comment structure from {comments_path}; "
                "cross-check skipped. Structure it as 'Reviewer #N' + 'Comment N)'.",
            )
            (failures if strict else warnings).append(issue)
        else:
            answered = {(entry.reviewer, entry.number) for entry in entries}
            for reviewer, number in sorted(original - answered):
                failures.append(CoverageIssue(
                    "COMMENT_UNANSWERED", reviewer, number, 0,
                    f"Reviewer #{reviewer} Comment {number} exists in the original comments "
                    "but has no entry in the response letter.",
                ))
            for reviewer, number in sorted(answered - original):
                warnings.append(CoverageIssue(
                    "COMMENT_EXTRA", reviewer, number, 0,
                    f"Response letter answers Reviewer #{reviewer} Comment {number}, which is "
                    "not in the original comments file (numbering drift?).",
                ))

    return ResponseCoverageResult(not failures, entries, failures, warnings)


def format_result(result: ResponseCoverageResult, response_path: Path) -> str:
    status = "PASS" if result.passed else "FAIL"
    lines = [
        f"RESPONSE COVERAGE {status}",
        f"artifact: {response_path}",
        f"checked: {len(result.entries)} comment(s), {len(result.failures)} failure(s), "
        f"{len(result.warnings)} warning(s)",
    ]
    for issue in result.failures:
        lines.append(f"[{issue.code}] {issue.message}")
    for issue in result.warnings:
        lines.append(f"[{issue.code}] (warning) {issue.message}")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Verify every reviewer comment in a response letter has a real response."
    )
    parser.add_argument("response", type=Path, help="Path to response_letter_REV*.md")
    parser.add_argument(
        "--comments",
        type=Path,
        default=None,
        help="Original reviewer_comments_REV*.md to cross-check comment coverage against.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail (instead of warn) when the original comments file cannot be parsed.",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    if not args.response.exists():
        print(f"Response file not found: {args.response}")
        return 2
    result = check_response_coverage(args.response, comments_path=args.comments, strict=args.strict)
    print(format_result(result, args.response))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

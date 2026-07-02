#!/usr/bin/env python3
"""Abbreviation definition checker (Phase 6 QC, advisory).

Journals require every abbreviation to be defined at first use -- once in the
abstract and once again in the body (the two are independent scopes). This is a
reviewer-nit magnet that the writing guide states as a rule but nothing
enforces. This checker is deliberately advisory: abbreviation detection has
unavoidable false positives (scale names, gene symbols, all-caps headings), so
it surfaces candidates for a human decision instead of blocking.

Reports, per scope (abstract vs body):
  - **ABBREV_UNDEFINED** -- used but never defined ("full term (ABB)") in scope.
  - **ABBREV_DEFINED_AFTER_USE** -- defined, but first plain use comes earlier.
  - **ABBREV_REDEFINED** -- defined more than once in the same scope.
  - **ABBREV_SINGLE_USE** (always advisory) -- defined but then used at most
    once; journals suggest spelling out abbreviations used fewer than ~3 times.

Detection scope (v1, documented limits): tokens of 2-6 consecutive capitals,
optionally with a numeric suffix (SF-36) or lowercase plural s (ODIs).
Mixed-case abbreviations (mJOA, tDCS) are not detected. A built-in allowlist
covers statistical/common abbreviations that need no definition (CI, SD, OR,
HR, ...); extend with --allow.

Advisory by default (exit 0). --strict exits non-zero on UNDEFINED /
DEFINED_AFTER_USE / REDEFINED (SINGLE_USE never blocks).
"""

from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent

# 2-6 consecutive capitals, optional -digits (SF-36), optional lowercase plural
# s captured OUTSIDE the canonical group so ODIs == ODI but VAS stays VAS.
ABBR_RE = re.compile(r"\b([A-Z]{2,6}(?:-\d+)?)(?:s\b|\b)")

# Statistical / universally-understood abbreviations that journals do not
# require to be defined. Roman numerals are grade/class labels, not acronyms.
DEFAULT_ALLOW = {
    "CI", "SD", "SE", "SEM", "IQR", "OR", "RR", "HR", "ANOVA", "SPSS",
    "USA", "UK", "MD", "COVID",
    "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII", "XIII", "XIV", "XV",
}


def _load_sibling(name: str):
    """Import a sibling script (scripts/<name>.py) by path (no package needed)."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Abstract-file detection stays in lockstep with the manuscript linter.
is_abstract_file = _load_sibling("lint_manuscript").is_abstract_file


class Occurrence(NamedTuple):
    abbrev: str
    artifact: str
    line: int
    is_definition: bool  # token sits right after an opening parenthesis


class AbbrevIssue(NamedTuple):
    code: str
    scope: str  # "abstract" | "body"
    abbrev: str
    artifact: str
    line: int
    message: str


def blank_non_prose(text: str) -> str:
    """Blank code fences, HTML comments, headings and table rows -- all-caps
    headings and table cells are not running text and would false-positive."""

    def keep_newlines(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    text = re.sub(r"```.*?```", keep_newlines, text, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", keep_newlines, text, flags=re.DOTALL)
    lines = [
        "" if line.lstrip().startswith(("#", "|")) else line
        for line in text.splitlines()
    ]
    return "\n".join(lines)


def find_occurrences(artifact: Path, allow: set[str]) -> list[Occurrence]:
    text = blank_non_prose(artifact.read_text(encoding="utf-8"))
    occurrences: list[Occurrence] = []
    for match in ABBR_RE.finditer(text):
        abbrev = match.group(1)
        if abbrev in allow:
            continue
        line = text.count("\n", 0, match.start()) + 1
        before = text[: match.start()].rstrip()
        is_definition = before.endswith("(")
        occurrences.append(Occurrence(abbrev, str(artifact), line, is_definition))
    return occurrences


def audit_scope(scope: str, occurrences: list[Occurrence]) -> list[AbbrevIssue]:
    issues: list[AbbrevIssue] = []
    by_abbrev: dict[str, list[Occurrence]] = {}
    for occ in occurrences:  # occurrences already in manuscript order
        by_abbrev.setdefault(occ.abbrev, []).append(occ)

    for abbrev, occs in sorted(by_abbrev.items()):
        definitions = [o for o in occs if o.is_definition]
        uses = [o for o in occs if not o.is_definition]
        first = occs[0]

        if not definitions:
            issues.append(AbbrevIssue(
                "ABBREV_UNDEFINED", scope, abbrev, first.artifact, first.line,
                f'"{abbrev}" used but never defined in {scope}. '
                f'Define at first use ("full term ({abbrev})") or add --allow {abbrev}.',
            ))
            continue
        # occs is in manuscript order, so "first token is a plain use" ==
        # "used before defined" (string/line comparison across files would lie).
        if uses and not first.is_definition:
            issues.append(AbbrevIssue(
                "ABBREV_DEFINED_AFTER_USE", scope, abbrev, uses[0].artifact, uses[0].line,
                f'"{abbrev}" used before its definition (defined at '
                f"{definitions[0].artifact}:{definitions[0].line}). Move the definition to first use.",
            ))
        if len(definitions) > 1:
            second = definitions[1]
            issues.append(AbbrevIssue(
                "ABBREV_REDEFINED", scope, abbrev, second.artifact, second.line,
                f'"{abbrev}" defined {len(definitions)} times in {scope}; define once at first use.',
            ))
        if len(uses) <= 1:
            issues.append(AbbrevIssue(
                "ABBREV_SINGLE_USE", scope, abbrev, definitions[0].artifact, definitions[0].line,
                f'"{abbrev}" defined but used {len(uses)} time(s) after definition; '
                "consider spelling it out instead.",
            ))
    return issues


def audit(artifacts: list[Path], *, allow: set[str]) -> list[AbbrevIssue]:
    abstract_occ: list[Occurrence] = []
    body_occ: list[Occurrence] = []
    for artifact in artifacts:
        text = artifact.read_text(encoding="utf-8")
        target = abstract_occ if is_abstract_file(artifact, text) else body_occ
        target.extend(find_occurrences(artifact, allow))
    return audit_scope("abstract", abstract_occ) + audit_scope("body", body_occ)


BLOCKING_CODES = {"ABBREV_UNDEFINED", "ABBREV_DEFINED_AFTER_USE", "ABBREV_REDEFINED"}


def format_issues(issues: list[AbbrevIssue]) -> str:
    lines = ["ABBREVIATION REPORT"]
    blocking = sum(1 for issue in issues if issue.code in BLOCKING_CODES)
    lines.append(f"issues: {len(issues)} ({blocking} definition issue(s), advisory unless --strict)")
    for issue in issues:
        lines.append(f"[{issue.code}] ({issue.scope}) {issue.artifact}:{issue.line} {issue.message}")
    if not issues:
        lines.append("all abbreviations defined at first use.")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check abbreviation define-at-first-use per scope (abstract vs body)."
    )
    parser.add_argument("artifacts", nargs="+", type=Path, help="Manuscript section markdown files (in manuscript order).")
    parser.add_argument(
        "--allow",
        action="append",
        default=[],
        metavar="ABB",
        help="Abbreviation that needs no definition (repeatable; extends the built-in allowlist).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero on UNDEFINED / DEFINED_AFTER_USE / REDEFINED (SINGLE_USE never blocks).",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    allow = DEFAULT_ALLOW | {a.strip() for a in args.allow if a.strip()}
    issues = audit(args.artifacts, allow=allow)
    print(format_issues(issues))
    if args.strict and any(issue.code in BLOCKING_CODES for issue in issues):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

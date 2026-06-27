#!/usr/bin/env python3
"""Abstract <-> body number consistency (Phase 6 QC, Rule 3).

CLAUDE.md Rule 3 requires patient counts, statistics, and outcomes to match across
**Abstract <-> Methods <-> Results <-> Tables**. `check_numbers.py` already ties
every number to `results/*.csv`, but it does not specifically catch the classic
reviewer complaint: *a number stated in the abstract that never appears in the body*
(an abstract-only figure -- inconsistent, or summarising something the paper does
not actually report).

This script reads the abstract and the body sections and reports every abstract
number that has **no rounding-tolerant match anywhere in the body**.

p-value tokens are excluded by default: abstract p-values are summaries whose
representation legitimately varies (e.g. `p<0.001` vs `p=0.0004`), and
check_numbers.py already grounds them against the results CSV. Pass
`--include-p-values` to check them too.

Number extraction (and its structural-number filtering) reuses check_numbers.py
so the two read the manuscript identically.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent


def _load_sibling(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_cn = _load_sibling("check_numbers")
iter_artifact_numbers = _cn.iter_artifact_numbers


class AbstractIssue(NamedTuple):
    number: str
    line: int
    context: str


class AbstractCheckResult(NamedTuple):
    passed: bool
    checked: int  # abstract numbers examined (after p-value filtering)
    issues: list[AbstractIssue]  # abstract numbers absent from the body


def body_supports(abstract_token, body_tokens) -> bool:
    """True if any body number equals the abstract number at the abstract's precision."""
    target = round(abstract_token.value, abstract_token.decimals)
    for body in body_tokens:
        if round(body.value, abstract_token.decimals) == target:
            return True
    return False


def check_abstract(
    abstract_path: Path,
    body_paths: list[Path],
    *,
    include_p_values: bool = False,
) -> AbstractCheckResult:
    abstract_tokens = iter_artifact_numbers(abstract_path)
    body_tokens: list = []
    for path in body_paths:
        body_tokens.extend(iter_artifact_numbers(path))

    issues: list[AbstractIssue] = []
    checked = 0
    for token in abstract_tokens:
        if token.is_p_value and not include_p_values:
            continue
        checked += 1
        if not body_supports(token, body_tokens):
            issues.append(
                AbstractIssue(
                    number=f"{token.comparator}{token.number}" if token.comparator else token.number,
                    line=token.line,
                    context=token.context[:90],
                )
            )

    return AbstractCheckResult(not issues, checked, issues)


def format_result(result: AbstractCheckResult, abstract_path: Path) -> str:
    if result.passed:
        return (
            "GATE PASS\n"
            "verifier: Abstract-Body-Consistency\n"
            f"abstract: {abstract_path}\n"
            f"checked: {result.checked} numbers, all present in the body"
        )
    lines = [
        "GATE FAIL",
        "verifier: Abstract-Body-Consistency",
        f"abstract: {abstract_path}",
        f"checked: {result.checked} numbers, {len(result.issues)} absent from the body",
    ]
    for issue in result.issues:
        lines.extend(
            [
                "---",
                f"number: {issue.number} (abstract line {issue.line})",
                f"context: {issue.context}",
                "reason: not found anywhere in the body sections",
                "required_action: align the abstract with the body, or add the value to the body",
            ]
        )
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check that every number in the abstract also appears in the body sections."
    )
    parser.add_argument(
        "--abstract",
        type=Path,
        default=ROOT / "drafts" / "02_abstract.md",
        help="Abstract markdown file (default drafts/02_abstract.md).",
    )
    parser.add_argument(
        "body",
        nargs="+",
        type=Path,
        help="Body section files (e.g. drafts/04_methods.md drafts/05_results.md and tables).",
    )
    parser.add_argument(
        "--include-p-values",
        action="store_true",
        help="Also require abstract p-value tokens to appear in the body (off by default).",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    result = check_abstract(args.abstract, args.body, include_p_values=args.include_p_values)
    print(format_result(result, args.abstract))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

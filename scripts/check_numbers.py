#!/usr/bin/env python3
"""Verify manuscript numbers against results CSV files.

This is the deterministic first gate for data grounding. It checks that
result-like numbers in Markdown artifacts can be traced to numeric values in
`results/*.csv`. It does not judge whether the surrounding interpretation is
correct; that remains a reviewer/verifier task.
"""

from __future__ import annotations

import argparse
import csv
import math
import re
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
FENCE_RE = re.compile(r"```.*?```", flags=re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", flags=re.DOTALL)
DATE_RE = re.compile(r"\b\d{4}-\d{1,2}-\d{1,2}\b|\b\d{1,2}/\d{1,2}/\d{2,4}\b")
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"(?:(?P<p>\*?p\*?)\s*(?P<comp><=|>=|<|>|=)\s*)?"
    r"(?P<num>[-+]?(?:\d+(?:,\d{3})*(?:\.\d+)?|\.\d+))"
    r"(?P<pct>%)?"
)
P_VALUE_COLUMNS = frozenset(
    {"p", "p value", "p_value", "p-value", "pval", "pvalue", "p val"}
)
STRUCTURAL_LABEL_RE = re.compile(
    r"\b(?:Table|Figure|Fig\.?|Section|Phase|Round|Reviewer|Comment|Line|Page|REV)\s*$",
    flags=re.IGNORECASE,
)


class ResultNumber(NamedTuple):
    value: float
    raw: str
    source: Path
    row: int
    column: str


class NumberToken(NamedTuple):
    value: float
    number: str
    line: int
    comparator: str
    is_p_value: bool
    decimals: int
    context: str


class NumberIssue(NamedTuple):
    artifact: Path
    number: str
    line: int
    reason: str
    required_action: str
    closest_ground_truth: str


class NumberCheckResult(NamedTuple):
    passed: bool
    checked_numbers: int
    failures: list[NumberIssue]
    warnings: list[NumberIssue]
    result_count: int = 0


def strip_ignored_text(text: str) -> str:
    text = FENCE_RE.sub("", text)
    text = HTML_COMMENT_RE.sub("", text)
    # Blank inline code spans and dates length-preservingly so example tokens
    # inside them are ignored without shifting line numbers or column offsets.
    text = INLINE_CODE_RE.sub(lambda match: " " * len(match.group()), text)
    return DATE_RE.sub(lambda match: " " * len(match.group()), text)


def to_float(number_text: str) -> float:
    return float(number_text.replace(",", ""))


def decimal_places(number_text: str) -> int:
    if "." not in number_text:
        return 0
    return len(number_text.split(".", 1)[1])


def extract_numbers_from_text(text: str) -> list[float]:
    return [to_float(match.group("num")) for match in NUMBER_RE.finditer(text)]


def load_result_numbers(results_dir: Path) -> list[ResultNumber]:
    numbers: list[ResultNumber] = []
    if not results_dir.exists():
        return numbers

    for csv_path in sorted(results_dir.rglob("*.csv")):
        with csv_path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            for row_index, row in enumerate(reader, start=2):
                for column, value in row.items():
                    if value is None:
                        continue
                    for number in extract_numbers_from_text(value):
                        numbers.append(
                            ResultNumber(
                                value=number,
                                raw=value,
                                source=csv_path,
                                row=row_index,
                                column=column or "<unnamed>",
                            )
                        )
    return numbers


def is_structural_number(
    line: str, start: int, token: str, is_p_value: bool, value: float
) -> bool:
    if is_p_value:
        return False

    before = line[:start]
    after = line[start + len(token) :]
    if value.is_integer() and 1900 <= int(value) <= 2099:
        return True

    # Confidence-level percentages (e.g. "95% CI", "95 % confidence interval")
    # state the interval level, not a result value.
    if re.match(r"\s*%?\s*(?:CI\b|confidence)", after, flags=re.IGNORECASE):
        return True

    # Hyphenated time spans (e.g. "90-day", "36-month", "5-year") are
    # time-point modifiers, not result values. Spaced forms ("63 years") are
    # left alone so ages and durations that ARE results stay checked.
    if re.match(r"-(?:year|month|week|day|hour|min(?:ute)?|second)s?\b", after, flags=re.IGNORECASE):
        return True

    if STRUCTURAL_LABEL_RE.search(before):
        return True

    # Markdown headings and table captions often start with structural labels.
    stripped = line.strip()
    if re.match(r"^#+\s*\d+(?:\.\d+)*\b", stripped):
        return True
    if re.match(r"^Table\s+\d+\b", stripped, flags=re.IGNORECASE):
        return True
    if re.match(r"^Figure\s+\d+\b", stripped, flags=re.IGNORECASE):
        return True

    if value.is_integer() and start == len(line) - len(line.lstrip()) and re.match(r"^\s*[.)]", after):
        return True
    return False


def iter_artifact_numbers(artifact: Path) -> list[NumberToken]:
    text = strip_ignored_text(artifact.read_text(encoding="utf-8"))
    tokens: list[NumberToken] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if "XX" in line:
            continue
        for match in NUMBER_RE.finditer(line):
            raw_number = match.group("num")
            full_token = match.group(0)
            is_p_value = bool(match.group("p"))
            value = to_float(raw_number)
            if is_structural_number(line, match.start(), full_token, is_p_value, value):
                continue
            tokens.append(
                NumberToken(
                    value=value,
                    number=raw_number,
                    line=line_number,
                    comparator=match.group("comp") or "",
                    is_p_value=is_p_value,
                    decimals=decimal_places(raw_number),
                    context=line.strip(),
                )
            )
    return tokens


def result_is_p_value(result_number: ResultNumber) -> bool:
    # A directional p-value claim (e.g. p<0.001) may only be satisfied by a
    # result value that is itself plausibly a p-value: either it comes from a
    # p-value column, or it falls in the (0, 1] probability range. This stops an
    # unrelated value such as a count of 0 from satisfying the inequality.
    if result_number.column.strip().casefold() in P_VALUE_COLUMNS:
        return True
    return 0.0 < result_number.value <= 1.0


def matches_number(token: NumberToken, result_number: ResultNumber) -> bool:
    if token.is_p_value and token.comparator:
        if not result_is_p_value(result_number):
            return False
        if token.comparator == "<":
            return result_number.value < token.value
        if token.comparator == "<=":
            return result_number.value <= token.value
        if token.comparator == ">":
            return result_number.value > token.value
        if token.comparator == ">=":
            return result_number.value >= token.value

    if math.isclose(token.value, result_number.value, rel_tol=0, abs_tol=1e-12):
        return True

    rounded = round(result_number.value, token.decimals)
    return math.isclose(token.value, rounded, rel_tol=0, abs_tol=1e-12)


def closest_result_number(token: NumberToken, result_numbers: list[ResultNumber]) -> str:
    if not result_numbers:
        return "<none>"
    closest = min(result_numbers, key=lambda item: abs(item.value - token.value))
    return f"{closest.value:g} ({closest.source}, row {closest.row}, col {closest.column})"


def check_numbers(
    artifacts: list[Path],
    *,
    results_dir: Path | None = None,
) -> NumberCheckResult:
    source_dir = results_dir or ROOT / "results"
    result_numbers = load_result_numbers(source_dir)
    failures: list[NumberIssue] = []
    warnings: list[NumberIssue] = []
    checked_numbers = 0

    for artifact in artifacts:
        if not artifact.exists():
            failures.append(
                NumberIssue(
                    artifact,
                    "<file>",
                    0,
                    "artifact file not found",
                    "Correct the artifact path and rerun number verification.",
                    "<none>",
                )
            )
            continue

        tokens = iter_artifact_numbers(artifact)
        checked_numbers += len(tokens)
        for token in tokens:
            if any(matches_number(token, result_number) for result_number in result_numbers):
                continue
            failures.append(
                NumberIssue(
                    artifact,
                    token.number,
                    token.line,
                    "number not found in results CSV files",
                    "Replace the number with a value traceable to results/*.csv or remove it.",
                    closest_result_number(token, result_numbers),
                )
            )

    return NumberCheckResult(not failures, checked_numbers, failures, warnings, len(result_numbers))


def format_result(result: NumberCheckResult, artifacts: list[Path], results_dir: Path) -> str:
    status = "GATE PASS" if result.passed else "GATE FAIL"
    lines = [
        status,
        "verifier: Data-Grounding",
        f"results: {results_dir}",
        f"artifacts: {len(artifacts)}",
        f"checked: {result.checked_numbers} number token(s), {len(result.failures)} failure(s)",
    ]
    if result.result_count == 0:
        lines.append(
            "note: no result numbers were loaded from the results directory; "
            "ensure results/*.csv exist and --results points to them"
        )

    if result.passed:
        return "\n".join(lines)

    lines.insert(1, "failure_code: GATE_FAIL NUMBERS")
    for failure in result.failures:
        lines.extend(
            [
                "---",
                f"artifact: {failure.artifact}",
                f"line: {failure.line}",
                f"number: {failure.number}",
                f"closest_ground_truth: {failure.closest_ground_truth}",
                f"reason: {failure.reason}",
                f"required_action: {failure.required_action}",
            ]
        )
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify manuscript numbers against results CSV files.")
    parser.add_argument("artifacts", nargs="*", type=Path, help="Markdown files to check")
    parser.add_argument("--section", action="append", type=Path, default=[], help="Markdown file to check")
    parser.add_argument("--results", type=Path, default=ROOT / "results", help="Directory containing results CSV files")
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()
    artifacts = [*args.artifacts, *args.section]
    if not artifacts:
        parser.error("at least one artifact path is required")

    result = check_numbers(artifacts, results_dir=args.results)
    print(format_result(result, artifacts, args.results))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

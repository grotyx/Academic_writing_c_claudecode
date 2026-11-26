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
import json
import math
import re
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
FENCE_RE = re.compile(r"```.*?```", flags=re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", flags=re.DOTALL)
# Calendar dates only: ISO dates and day/month/year with a four-digit year. A three-group count such as
# "15/28/12" is a result, not a date, and stays checked.
_DM = r"(?:0?[1-9]|[12]\d|3[01])"
DATE_RE = re.compile(r"\b\d{4}-\d{1,2}-\d{1,2}\b|\b" + _DM + "/" + _DM + r"/(?:19|20)\d{2}\b"
                     r"|\b(?:19|20)\d{2}/" + _DM + "/" + _DM + r"\b")  # 2021/03/12 (Korea, Japan, China)
# A unary en dash before a number is a minus sign in Word and statistics exports ("\u20132.5"); a range
# dash ("1.2\u20133.4") follows a digit and is left alone.
UNARY_DASH_RE = re.compile(r"(?<![\w.%)])\u2013(?=\.?\d)")
# Typographic minus and comparison signs mean the same as their ASCII forms; without this a
# "−2.5" lost its sign and "p ≤ 0.05" its comparator.
TYPOGRAPHIC = str.maketrans({"\u2212": "-", "\u2264": "<=", "\u2265": ">=", "\u2a7d": "<=", "\u2a7e": ">="})
INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
NUMBER_RE = re.compile(
    r"(?<![A-Za-z0-9_])"
    r"(?:(?P<p>\*{0,2}[pP]\*{0,2}(?:[\s-]*values?\*{0,2})?)\s*(?P<comp><=|>=|<|>|=)\s*)?"
    r"(?P<num>[-+]?(?:\d+(?:,\d{3})*(?:\.\d+)?|\.\d+)(?:[eE][-+]?\d+)?)"
    r"(?P<pct>%)?"
)
P_VALUE_COLUMNS = frozenset(
    {"p", "p value", "p_value", "p-value", "pval", "pvalue", "p val"}
)
P_VALUE_TEXT_RE = re.compile(r"\b\*?p\*?(?:[\s-]*values?)?\s*(?:<=|>=|<|>|=)", flags=re.IGNORECASE)
# A CSV cell that is itself a bound, e.g. "<0.001" or "p < 0.001".
RESULT_BOUND_RE = re.compile(r"^\s*(?:\*?p\*?(?:[\s-]*values?)?\s*)?(?P<comp><=|>=|<|>)\s*", flags=re.IGNORECASE)
REFERENCE_LIST_RE = re.compile(
    r"\b(?:Tables|Figures|Figs\.?)\s+(\d+[A-Za-z]?(?:\s*(?:[-\u2013,]|and|&|to)\s*\d+[A-Za-z]?)*)", re.IGNORECASE)
STRUCTURAL_LABEL_RE = re.compile(
    r"\b(?:Tables?|Figures?|Figs?\.?|Sections?|Phase|Round|Reviewer|Comment|Line|Page|REV)\s*$",
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


def column_key(name: str) -> str:
    """'*P*-value', '_p_', ' P value ' -> 'p-value', 'p', 'p value' (markdown emphasis dropped)."""
    return name.replace("*", "").replace("_", " ").strip().casefold()


P_COLUMN_RE = re.compile(r"^(?:[a-z-]+\s+)*p(?:[\s-]*val(?:ue)?s?)?(?:\s+for\s+[a-z-]+)?$")


def is_p_column(name: str) -> bool:
    """'P', '*P*-value', 'Adjusted P value', 'P value\u2020', 'P for trend' (footnote marks dropped)."""
    key = re.sub(r"[\u2020\u2021\u00a7\u00b6#\^]+|\s*\[[a-z]\]$", "", column_key(name)).strip()
    return bool(P_COLUMN_RE.match(key))


def strip_ignored_text(text: str) -> str:
    text = UNARY_DASH_RE.sub("-", text.translate(TYPOGRAPHIC))
    # Blank fences and HTML comments keeping their newlines so line numbers
    # reported after them stay correct.
    text = FENCE_RE.sub(lambda match: "\n" * match.group().count("\n"), text)
    text = HTML_COMMENT_RE.sub(lambda match: "\n" * match.group().count("\n"), text)
    # Blank inline code spans and dates length-preservingly so example tokens
    # inside them are ignored without shifting line numbers or column offsets.
    text = INLINE_CODE_RE.sub(lambda match: " " * len(match.group()), text)
    return DATE_RE.sub(lambda match: " " * len(match.group()), text)


def to_float(number_text: str) -> float:
    return float(number_text.replace(",", ""))


def decimal_places(number_text: str) -> int:
    return max(0, -Decimal(number_text.replace(",", "")).as_tuple().exponent)


def extract_numbers_from_text(text: str) -> list[float]:
    return [to_float(match.group("num")) for match in NUMBER_RE.finditer(UNARY_DASH_RE.sub("-", text.translate(TYPOGRAPHIC)))]


def load_result_numbers(results_dir: Path) -> list[ResultNumber]:
    numbers: list[ResultNumber] = []
    if not results_dir.exists():
        return numbers

    base = results_dir.resolve()
    for csv_path in sorted(results_dir.rglob("*.csv")):
        if not csv_path.resolve().is_relative_to(base) or not csv_path.resolve().is_file():
            continue  # a symlink out of results/ is not a result source
        with csv_path.open(newline="", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            for row_index, row in enumerate(reader, start=2):
                for column, value in row.items():
                    # csv.DictReader stores surplus fields of a ragged row as a
                    # list under key None; skip them instead of crashing.
                    if value is None or column is None:
                        continue
                    for number in extract_numbers_from_text(value):
                        numbers.append(
                            ResultNumber(
                                value=number,
                                raw=UNARY_DASH_RE.sub("-", value.translate(TYPOGRAPHIC)),
                                source=csv_path,
                                row=row_index,
                                column=column or "<unnamed>",
                            )
                        )
    return numbers


# Words that may follow a year without making it a count: "the 2019 guideline", "2015 onwards".
YEAR_FOLLOWERS = frozenset("""onward onwards guideline guidelines criteria classification
    edition version revision update consensus statement recommendation recommendations census survey season wave
    report data meta study studies trial trials review cohort registry pandemic randomized randomised systematic
    prospective retrospective multicenter multicentre national nationwide annual outbreak""".split())
# Words after a year-sized integer that make it a count wherever it stands ("in 2019 patients").
COUNT_NOUNS = frozenset("""patients participants subjects cases controls women men children adults adolescents infants
    individuals people persons eyes knees hips shoulders spines levels segments procedures operations surgeries
    fractures events admissions visits hospitals records""".split())
DETERMINERS = frozenset("a an the this that its their our".split())


# Words before a year that make it a date: "in 2019 at a single center", "since 2015".
YEAR_LEADERS = frozenset("""in since from between until till through during before after by early late
    mid year years january february march april may june july august september october november december
    jan feb mar apr jun jul aug sep sept oct nov dec""".split())
YEAR = r"(?:19|20)\d{2}"


def is_year(before: str, after: str, token: str) -> bool:
    """A year-sized integer is checked as a count unless its context makes it a date: a date word before it
    ("in 2019", "since 2015"), a year range ("2015-2020", "between 2015 and 2020", "from 2015 to 2020"), an
    author-year citation ("Weber 2007", "(Smith et al., 2020)", "Smith (2020)"), or a following word that
    continues a date phrase ("the 2019 guideline", "2016 WHO classification"). So "We enrolled 2024 (52%) women",
    "2,048 patients", "n = 2019" and a table cell "| 2024 |" are checked."""
    if not re.fullmatch(YEAR, token):
        return False
    if re.search(r"[=:]\s*$", before):
        return False
    word = re.match(r"\s+([A-Za-z]+)", after)
    if word and word.group(1).casefold() in COUNT_NOUNS:
        return False  # "In Korea, 2024 patients", "in 2019 patients": a count whatever comes before
    if (re.match(r"\s*(?:[-\u2013/]|to|and|through|until)\s*" + YEAR + r"\b", after)
            or re.search(YEAR + r"\s*[-\u2013/]\s*$", before)):
        return True
    if re.search(r"\b(?:between|from)\s+" + YEAR + r"\s+(?:and|to|through|until)\s+$", before, flags=re.IGNORECASE):
        return True
    if re.search(r"\(\s*$", before) and re.match(r"\s*[a-z]?\s*[);,]", after):  # "(2020)", "(2020a;"
        return True
    if re.search(r"\bet\s+al\.?,?\s*$", before) or re.search(r"[A-Z][A-Za-z'\u2019-]+(?: and [A-Z][A-Za-z'\u2019-]+)?,\s*$", before):
        return True  # "(Smith et al., 2020)", "(Smith, 2020)", "Kim and Lee, 2019"
    previous = re.search(r"([A-Za-z]+)\.?[\s(]*$", before)
    if previous and previous.group(1).casefold() in YEAR_LEADERS:
        return True
    if previous and previous.group(1)[0].isupper():
        lead = before[: previous.start()].rstrip()
        if lead and not re.search(r"[.!?]$|^\W*$", lead):
            return True  # "as reported by Weber 2007": a name inside a sentence, not "Of 2024 patients"
    if not word:
        return False
    if word.group(1).casefold() in YEAR_FOLLOWERS:
        return True  # "a 2020 meta-analysis", "the 2019 guideline"
    # "the 2016 WHO classification": a capitalized word after a determiner; "enrolled 2024 MRI-confirmed" is a count
    return word.group(1)[0].isupper() and bool(previous) and previous.group(1).casefold() in DETERMINERS


def is_structural_number(
    line: str, start: int, token: str, is_p_value: bool, value: float
) -> bool:
    if is_p_value:
        return False

    before = line[:start]
    after = line[start + len(token) :]
    if is_year(before, after, token):
        return True

    # Trailing part of a hyphenated label (e.g. "L4-5", "C5-6", "COVID-19",
    # "ICD-10"): the number belongs to the identifier, not to a result.
    if re.search(r"[A-Za-z]\d*[-–]$", before):
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
    for listed in REFERENCE_LIST_RE.finditer(line):  # "Tables 1 and 2", "Figures 1-3"
        if listed.start(1) <= start < listed.end(1):
            return True

    # A heading number ("## 2.1 Methods") is structure. Only that number is exempt: a caption such as
    # "Table 1 summarizes 876 patients" keeps its count checked (the label number is exempt above).
    if re.fullmatch(r"\s*#+\s*(?:\d+\.)*", before):
        return True

    if value.is_integer() and start == len(line) - len(line.lstrip()) and re.match(r"^\s*[.)]", after):
        return True
    return False


# Set by the caller that has already chosen and validated the paper's manifest (harness verify, bind):
# (root, numeric_allow entries). Then no other project.json is consulted, so a stray manifest in a
# subfolder can never add exemptions that the hashed one does not list.
SELECTED: tuple[Path, list] | None = None


def select_manifest(root: Path, entries: list) -> None:
    global SELECTED
    SELECTED = (Path(root).resolve(), list(entries or []))


def _spans_from(folder: Path, entries, artifact: Path) -> list[str]:
    spans = []
    for entry in entries if isinstance(entries, list) else []:
        if not (isinstance(entry, dict) and isinstance(entry.get("text"), str) and entry["text"].strip()
                and isinstance(entry.get("reason"), str) and entry["reason"].strip()):
            continue
        target = entry.get("artifact")
        if target and (folder / target).resolve() != artifact:
            continue
        spans.append(entry["text"].strip().translate(TYPOGRAPHIC).casefold())
    return spans


def allowed_spans(artifact: Path) -> list[str]:
    """Texts of the paper's project.json "numeric_allow" entries that apply to this artifact (lower case).
    A number inside one of these texts is not a result ("12 months" follow-up, "Python 3.12"), so it is
    neither checked against results nor bound; every entry carries a reason and makes reviews stale when
    edited (project.json is a dependency)."""
    artifact = Path(artifact).resolve()
    if SELECTED is not None:
        root, entries = SELECTED
        return _spans_from(root, entries, artifact) if artifact.is_relative_to(root) else []
    # standalone use (`manuwright numbers file.md`): the paper manifest above the file (one with "artifacts")
    for folder in artifact.parents:
        manifest = folder / "project.json"
        if not manifest.is_file():
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []
        if not isinstance(data, dict) or "artifacts" not in data:
            continue
        return _spans_from(folder, data.get("numeric_allow") or [], artifact)
    return []


def allow_report(root: Path, entries: list, artifacts: list[Path]) -> tuple[int, list[str]]:
    """(numbers exempted, entries that match nothing): a stale numeric_allow rule is reported, not ignored."""
    exempted, unmatched = 0, []
    for entry in entries:
        targets = [Path(root, entry["artifact"]).resolve()] if entry.get("artifact") else artifacts
        span = entry["text"].strip().translate(TYPOGRAPHIC).casefold()
        hits = 0
        for artifact in targets:
            for line in strip_ignored_text(Path(artifact).read_text(encoding="utf-8")).splitlines():
                hits += sum(1 for m in NUMBER_RE.finditer(line) if _inside_allowed(line, m.start("num"), [span]))
        exempted += hits
        if not hits:
            unmatched.append(entry["text"])
    return exempted, unmatched


def _inside_allowed(line: str, position: int, spans: list[str]) -> bool:
    folded = line.casefold()
    for span in spans:
        start = folded.find(span)
        while start != -1:
            end = start + len(span)
            bounded = (start == 0 or not folded[start - 1].isalnum()) and (end == len(folded) or not folded[end].isalnum())
            if bounded and start <= position < end:  # "2 months" never matches inside "12 months"
                return True
            start = folded.find(span, start + 1)
    return False


def iter_artifact_numbers(artifact: Path) -> list[NumberToken]:
    text = strip_ignored_text(artifact.read_text(encoding="utf-8"))
    spans = allowed_spans(artifact)
    tokens: list[NumberToken] = []
    p_columns = set()
    lines = text.splitlines()
    for line_number, line in enumerate(lines, start=1):
        if not line.strip().startswith('|'):
            p_columns = set()
        elif line_number < len(lines) and re.fullmatch(
                r'\s*\|(?:\s*:?-{3,}:?\s*\|)+\s*', lines[line_number]):
            # A pipe header is identified by its separator row, not by whether
            # the header contains group sizes or follow-up time points.
            p_columns = {i for i, cell in enumerate(line.split('|')) if is_p_column(cell)}
        for match in NUMBER_RE.finditer(line):
            raw_number = match.group("num")
            full_token = match.group(0)
            table_p = line.strip().startswith('|') and line[:match.start()].count('|') in p_columns
            is_p_value = bool(match.group("p")) or table_p
            table_comparator = re.search(r'(<=|>=|<|>|=)\s*$', line[:match.start()]) if table_p else None
            value = to_float(raw_number)
            if is_structural_number(line, match.start(), full_token, is_p_value, value):
                continue
            if spans and _inside_allowed(line, match.start("num"), spans):
                continue
            tokens.append(
                NumberToken(
                    value=value,
                    number=raw_number,
                    line=line_number,
                    comparator=match.group("comp") or (table_comparator.group(1) if table_comparator else ""),
                    is_p_value=is_p_value,
                    decimals=decimal_places(raw_number),
                    context=line.strip(),
                )
            )
    return tokens


def result_is_p_value(result_number: ResultNumber) -> bool:
    # A directional p-value claim (e.g. p<0.001) may only be satisfied by a
    # result value that is explicitly a p-value. A generic 0-1 proportion/rate
    # is not enough; otherwise clinical rates can falsely satisfy p<threshold.
    if is_p_column(result_number.column):
        return True
    return bool(P_VALUE_TEXT_RE.search(result_number.raw))


def result_bound_comparator(result_number: ResultNumber) -> str:
    match = RESULT_BOUND_RE.match(result_number.raw)
    return match.group("comp") if match else ""


def rounded_candidates(value: float, decimals: int) -> tuple[float, float]:
    # round() is banker's rounding on the binary float (2.675 -> 2.67) while
    # manuscripts round half up on the printed value (2.675 -> 2.68). Accept
    # either so a correctly rounded number is never rejected.
    half_up = Decimal(str(value)).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    return round(value, decimals), float(half_up)


def matches_number(token: NumberToken, result_number: ResultNumber) -> bool:
    if token.is_p_value:
        if not 0 < token.value <= 1 or not result_is_p_value(result_number):
            return False
        bound = result_bound_comparator(result_number)
        comp = token.comparator or "="
        if bound:
            if comp == "=" or bound[0] != comp[0]:
                return False
            if bound[0] == "<":
                return (result_number.value < token.value or
                        (result_number.value == token.value and
                         (bound == "<" or comp == "<=")))
            return (result_number.value > token.value or
                    (result_number.value == token.value and
                     (bound == ">" or comp == ">=")))
        if not 0 <= result_number.value <= 1:
            return False
        if comp == "<":
            return result_number.value < token.value
        if comp == "<=":
            return result_number.value <= token.value
        if comp == ">":
            return result_number.value > token.value
        if comp == ">=":
            return result_number.value >= token.value

    if math.isclose(token.value, result_number.value, rel_tol=0, abs_tol=1e-12):
        return True

    return any(
        math.isclose(token.value, rounded, rel_tol=0, abs_tol=1e-12)
        for rounded in rounded_candidates(result_number.value, token.decimals)
    )


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

        for line_no, line in enumerate(strip_ignored_text(artifact.read_text(encoding="utf-8")).splitlines(), 1):
            if re.search(r"\bXX\b|\[(?:TODO|TBD)\]", line):
                failures.append(NumberIssue(artifact, "<placeholder>", line_no,
                    "unresolved manuscript placeholder", "Complete the draft before verification.", "<none>"))
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

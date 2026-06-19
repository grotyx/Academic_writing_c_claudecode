#!/usr/bin/env python3
"""Rule-based manuscript linting for academic medical drafts.

Checks terminology, placeholders, overclaiming, statistics notation, and
section-specific style issues. Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TERMINOLOGY_FILE = ROOT / "Style" / "terminology.md"


PLACEHOLDER_PATTERNS = [
    re.compile(r"\[(?:TODO|TBD|CITE|REF|INSERT|XX?|\?)\]", re.IGNORECASE),
    re.compile(r"\[ref\s*\d*\]", re.IGNORECASE),
    re.compile(r"\bAuthor et al\.,?\s*year\b", re.IGNORECASE),
]

OVERCLAIM_TERMS = [
    "dramatic",
    "remarkable",
    "groundbreaking",
    "unprecedented",
    "overwhelming evidence",
    "clearly proves",
    "proved that",
    "definitively",
    "most pronounced advantage",
]

RESULTS_INTERPRETATION_TERMS = [
    "suggests",
    "suggest",
    "indicates",
    "indicate",
    "may explain",
    "might explain",
    "clinically meaningful",
    "clinical implication",
    "because",
]

STAT_STYLE_PATTERNS = [
    (re.compile(r"\b[Pp]\s*=\s*0\.000\b"), "Use p < 0.001, not p = 0.000."),
    (re.compile(r"\b[Pp]\s*=\s*NS\b", re.IGNORECASE), "Use exact p-values or state not significant in text."),
    (re.compile(r"\bP\s*[<=>]"), "Use lowercase italic p in manuscript text, e.g., *p* = 0.023."),
    (re.compile(r"\bp\s*[<=>]\s*\.\d+"), "Use a leading zero for p-values, e.g., p = 0.023."),
    (re.compile(r"p\s*[<=>]"), "Use formatted *p* in final manuscript text."),
]


def load_forbidden_terms(path: Path) -> dict[str, str]:
    """Parse Style/terminology.md tables for Forbidden Terms -> Preferred Term."""
    if not path.exists():
        return {}

    forbidden: dict[str, str] = {}
    in_table = False
    headers: list[str] = []
    preferred_idx = forbidden_idx = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            in_table = False
            headers = []
            preferred_idx = forbidden_idx = None
            continue

        cells = [cell.strip() for cell in line.strip("|").split("|")]
        normalized = [re.sub(r"[^a-z]", "", cell.lower()) for cell in cells]

        if "preferredterm" in normalized and "forbiddenterms" in normalized:
            headers = normalized
            preferred_idx = headers.index("preferredterm")
            forbidden_idx = headers.index("forbiddenterms")
            in_table = True
            continue

        if not in_table or set("".join(cells)) <= {"-", ":"}:
            continue

        if preferred_idx is None or forbidden_idx is None:
            continue
        if len(cells) <= max(preferred_idx, forbidden_idx):
            continue

        preferred = cells[preferred_idx].strip()
        forbidden_cell = cells[forbidden_idx].strip()
        if not preferred or not forbidden_cell or forbidden_cell in {"-", "—"}:
            continue

        for term in re.split(r";|,", forbidden_cell):
            term = term.strip()
            if term and term not in {"-", "—"}:
                forbidden[term] = preferred

    return forbidden


def iter_markdown_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
        elif path.is_file() and path.suffix.lower() == ".md":
            files.append(path)
    return files


def is_results_file(path: Path, text: str) -> bool:
    name = path.name.lower()
    return name.startswith("05_") or name == "results.md" or re.search(r"^#\s+Results\b", text, re.I | re.M) is not None


def is_discussion_file(path: Path, text: str) -> bool:
    name = path.name.lower()
    return name.startswith("06_") or name == "discussion.md" or re.search(r"^#\s+Discussion\b", text, re.I | re.M) is not None


def line_collections(text: str):
    for idx, line in enumerate(text.splitlines(), start=1):
        yield idx, line


def add_issue(issues: list[tuple[str, Path, int, str]], code: str, path: Path, line: int, message: str) -> None:
    issues.append((code, path, line, message))


def display_path(path: Path) -> Path:
    try:
        return path.resolve().relative_to(ROOT)
    except ValueError:
        return path


def lint_file(path: Path, forbidden_terms: dict[str, str]) -> list[tuple[str, Path, int, str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    issues: list[tuple[str, Path, int, str]] = []
    results = is_results_file(path, text)
    discussion = is_discussion_file(path, text)

    for line_no, line in line_collections(text):
        stripped = line.strip()
        if not stripped or stripped.startswith("<!--"):
            continue

        for pattern in PLACEHOLDER_PATTERNS:
            if pattern.search(line):
                add_issue(issues, "PLACEHOLDER", path, line_no, "Unresolved placeholder or citation marker found.")

        lower = line.lower()
        for term, preferred in forbidden_terms.items():
            if not term:
                continue
            if re.search(r"\b" + re.escape(term.lower()) + r"\b", lower):
                add_issue(issues, "TERMINOLOGY", path, line_no, f'Forbidden term "{term}"; prefer "{preferred}".')

        for term in OVERCLAIM_TERMS:
            if term in lower:
                add_issue(issues, "OVERCLAIM", path, line_no, f'Potential overstatement: "{term}".')

        for pattern, message in STAT_STYLE_PATTERNS:
            if pattern.search(line):
                add_issue(issues, "STAT_FORMAT", path, line_no, message)

        if "—" in line:
            add_issue(issues, "DASH", path, line_no, "Avoid em dash in running manuscript text.")
        if "–" in line and not re.search(r"\d\s*–\s*\d", line):
            add_issue(issues, "DASH", path, line_no, "Avoid en dash as punctuation in running text.")

        if re.search(r"\bcompared to\b", lower):
            add_issue(issues, "STYLE", path, line_no, 'Use "compared with" for comparisons unless journal style differs.')

        if results:
            for term in RESULTS_INTERPRETATION_TERMS:
                if re.search(r"\b" + re.escape(term) + r"\b", lower):
                    add_issue(issues, "RESULTS_INTERPRETATION", path, line_no, f'Results section may contain interpretation: "{term}".')

        if discussion:
            numeric_tokens = re.findall(r"\b\d+(?:\.\d+)?%?\b", line)
            p_values = re.findall(r"\bp\s*[<=>]", lower)
            if len(numeric_tokens) >= 8 or len(p_values) >= 3:
                add_issue(issues, "DISCUSSION_DENSITY", path, line_no, "Discussion may be repeating too many numeric results; consider referring to tables.")

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint manuscript markdown files for terminology and style issues.")
    parser.add_argument("paths", nargs="*", default=["drafts"], help="Markdown files or directories to lint. Default: drafts")
    parser.add_argument("--terminology", default=str(TERMINOLOGY_FILE), help="Path to terminology registry")
    parser.add_argument("--quiet", action="store_true", help="Only print summary")
    args = parser.parse_args()

    input_paths = [Path(p) for p in args.paths]
    files = iter_markdown_files(input_paths)
    terminology_path = Path(args.terminology)
    forbidden_terms = load_forbidden_terms(terminology_path)

    all_issues: list[tuple[str, Path, int, str]] = []
    for file_path in files:
        all_issues.extend(lint_file(file_path, forbidden_terms))

    if not args.quiet:
        for code, path, line, message in all_issues:
            print(f"[{code}] {display_path(path)}:{line} {message}")

    print(f"Checked {len(files)} markdown file(s); found {len(all_issues)} issue(s).")
    return 1 if all_issues else 0


if __name__ == "__main__":
    sys.exit(main())

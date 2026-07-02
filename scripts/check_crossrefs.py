#!/usr/bin/env python3
"""Table/Figure cross-reference checker (Phase 6 QC).

Verifies that every "Table N" / "Figure N" mentioned in the manuscript text
actually exists (table files / figure-legend entries), and surfaces inventory
items never referenced in the text. Renumbering or deleting a table during
revision silently breaks in-text references -- a classic desk-reject trigger
that nothing else in the harness catches.

Reports:
  - **broken references** -- "Table 5" mentioned in text but no table 5 exists.
    The primary error signal.
  - **unreferenced items** (advisory) -- a table/figure exists but is never
    cited in the text. Journals require every table/figure to be referenced.
  - **out-of-order first mentions** (advisory) -- most journals require tables
    and figures to be first cited in numerical order.

Advisory by default (exit 0). `--fail-on-broken`, `--fail-on-unreferenced`,
and `--fail-on-order` turn the corresponding findings into blocking failures.

Inventory sources:
  - tables: `table_*.md` files in `--tables-dir` (default: the directory of the
    first artifact); number taken from the filename, falling back to the
    `# Table N.` title line.
  - figures: entries in the figure-legends file (`--legends`, default
    `09_figure_legends.md` next to the first artifact), plus files in
    `--figures-dir` if given.
If a kind has mentions but an empty inventory, the checks for that kind are
skipped with a loud note instead of flagging every mention as broken.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]

# "Table 1", "Tables 1 and 2", "Figure 2-4", "Fig. 3". Continuation numbers
# after , / and / & must not look like data ("Figure 1, 25% of ..."), hence the
# negative lookahead for % and decimals on each continued number.
MENTION_RE = re.compile(
    r"\b(Tables?|Fig(?:ures?|s?\.?))\s+"
    r"(\d+(?:[A-Za-z])?(?:\s*(?:[-–,]|and|&)\s*\d+(?!\d|\s*%|\.\d)(?:[A-Za-z])?)*)",
    re.IGNORECASE,
)
RANGE_RE = re.compile(r"(\d+)\s*[-–]\s*(\d+)")
TABLE_FILE_RE = re.compile(r"table[_\- ]?(\d+)", re.IGNORECASE)
TABLE_TITLE_RE = re.compile(r"(?im)^#+\s*Table\s+(\d+)\b")
LEGEND_ENTRY_RE = re.compile(r"(?im)^\s*(?:[-*>]\s*)?(?:\*{1,2}|#+\s*)?\s*Fig(?:ure)?\.?\s+(\d+)\b")
FIGURE_FILE_RE = re.compile(r"fig(?:ure)?[_\- ]?(\d+)", re.IGNORECASE)


class Mention(NamedTuple):
    kind: str  # "table" | "figure"
    number: int
    artifact: str
    line: int
    snippet: str


class CrossrefResult(NamedTuple):
    mentions: list[Mention]
    inventory: dict[str, set[int]]  # kind -> numbers that exist
    broken: list[Mention]  # mentioned but not in inventory
    unreferenced: dict[str, list[int]]  # kind -> existing numbers never mentioned
    out_of_order: dict[str, list[int]]  # kind -> first-mention sequence, if not ascending
    skipped_kinds: list[str]  # kinds with mentions but empty inventory (checks skipped)


def blank_non_prose(text: str) -> str:
    """Blank code fences and HTML comments, preserving line numbers."""

    def keep_newlines(match: re.Match[str]) -> str:
        return "\n" * match.group(0).count("\n")

    text = re.sub(r"```.*?```", keep_newlines, text, flags=re.DOTALL)
    return re.sub(r"<!--.*?-->", keep_newlines, text, flags=re.DOTALL)


def expand_numbers(numstr: str) -> list[int]:
    """'1 and 2' -> [1, 2]; '2-4' -> [2, 3, 4]; '1A' -> [1]."""
    numbers = [int(a) + offset for a, b in RANGE_RE.findall(numstr) for offset in range(int(b) - int(a) + 1)]
    rest = RANGE_RE.sub(" ", numstr)
    numbers.extend(int(n) for n in re.findall(r"\d+", rest))
    return numbers


def find_mentions(artifact: Path) -> list[Mention]:
    text = blank_non_prose(artifact.read_text(encoding="utf-8"))
    mentions: list[Mention] = []
    for match in MENTION_RE.finditer(text):
        kind = "table" if match.group(1).lower().startswith("tab") else "figure"
        line = text.count("\n", 0, match.start()) + 1
        snippet = " ".join(match.group(0).split())[:60]
        for number in expand_numbers(match.group(2)):
            mentions.append(Mention(kind, number, str(artifact), line, snippet))
    return mentions


def collect_table_inventory(tables_dir: Path) -> set[int]:
    numbers: set[int] = set()
    if not tables_dir.is_dir():
        return numbers
    for path in sorted(tables_dir.glob("table*.md")):
        match = TABLE_FILE_RE.search(path.stem)
        if match:
            numbers.add(int(match.group(1)))
            continue
        title = TABLE_TITLE_RE.search(path.read_text(encoding="utf-8"))
        if title:
            numbers.add(int(title.group(1)))
    return numbers


def collect_figure_inventory(legends: Path | None, figures_dir: Path | None) -> set[int]:
    numbers: set[int] = set()
    if legends is not None and legends.is_file():
        text = blank_non_prose(legends.read_text(encoding="utf-8"))
        numbers.update(int(n) for n in LEGEND_ENTRY_RE.findall(text))
    if figures_dir is not None and figures_dir.is_dir():
        for path in figures_dir.iterdir():
            match = FIGURE_FILE_RE.search(path.stem)
            if match:
                numbers.add(int(match.group(1)))
    return numbers


def first_mention_order(mentions: list[Mention], kind: str) -> list[int]:
    """First-mention sequence for a kind, in artifact-list order."""
    seen: list[int] = []
    for mention in mentions:
        if mention.kind == kind and mention.number not in seen:
            seen.append(mention.number)
    return seen


def check_crossrefs(
    artifacts: list[Path],
    *,
    tables_dir: Path | None = None,
    legends: Path | None = None,
    figures_dir: Path | None = None,
) -> CrossrefResult:
    if tables_dir is None and artifacts:
        tables_dir = artifacts[0].resolve().parent
    if legends is None and artifacts:
        candidate = artifacts[0].resolve().parent / "09_figure_legends.md"
        legends = candidate if candidate.is_file() else None

    inventory = {
        "table": collect_table_inventory(tables_dir) if tables_dir else set(),
        "figure": collect_figure_inventory(legends, figures_dir),
    }

    mentions: list[Mention] = []
    for artifact in artifacts:
        mentions.extend(find_mentions(artifact))

    broken: list[Mention] = []
    unreferenced: dict[str, list[int]] = {}
    out_of_order: dict[str, list[int]] = {}
    skipped_kinds: list[str] = []

    for kind in ("table", "figure"):
        kind_mentions = [m for m in mentions if m.kind == kind]
        existing = inventory[kind]
        if kind_mentions and not existing:
            # No inventory found -- flagging every mention as broken would be
            # noise (probably a missing --tables-dir/--legends), so skip loudly.
            skipped_kinds.append(kind)
            continue
        broken.extend(m for m in kind_mentions if m.number not in existing)
        mentioned = {m.number for m in kind_mentions}
        missing_refs = sorted(existing - mentioned)
        if missing_refs:
            unreferenced[kind] = missing_refs
        order = first_mention_order(mentions, kind)
        valid_order = [n for n in order if n in existing]
        if valid_order != sorted(valid_order):
            out_of_order[kind] = valid_order

    return CrossrefResult(mentions, inventory, broken, unreferenced, out_of_order, skipped_kinds)


def format_result(result: CrossrefResult) -> str:
    lines = [
        "CROSSREF REPORT",
        f"inventory: {len(result.inventory['table'])} table(s), {len(result.inventory['figure'])} figure(s) | "
        f"mentions: {len(result.mentions)} | broken: {len(result.broken)}",
    ]

    for kind in result.skipped_kinds:
        lines.append(
            f"NOTE: {kind} mentions found but no {kind} inventory located -- "
            f"{kind} checks skipped (pass --tables-dir/--legends/--figures-dir)."
        )

    if result.broken:
        lines.append("broken references (mentioned in text but item does not exist):")
        for mention in result.broken:
            lines.append(
                f"  {mention.artifact}:{mention.line}  {mention.kind} {mention.number} -> \"{mention.snippet}\""
            )

    if result.unreferenced:
        lines.append("unreferenced items (exist but never cited in text -- journals require a mention):")
        for kind, numbers in sorted(result.unreferenced.items()):
            for number in numbers:
                lines.append(f"  {kind} {number}")

    if result.out_of_order:
        lines.append("out-of-order first mentions (most journals require ascending first citation):")
        for kind, order in sorted(result.out_of_order.items()):
            lines.append(f"  {kind}: first mentioned as {', '.join(str(n) for n in order)}")

    if not (result.broken or result.unreferenced or result.out_of_order or result.skipped_kinds):
        lines.append("all cross-references consistent.")
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check Table/Figure mentions in manuscript text against the actual tables/figures."
    )
    parser.add_argument("artifacts", nargs="+", type=Path, help="Manuscript section markdown files (in manuscript order).")
    parser.add_argument(
        "--tables-dir",
        type=Path,
        default=None,
        help="Directory containing table_*.md files (default: directory of the first artifact).",
    )
    parser.add_argument(
        "--legends",
        type=Path,
        default=None,
        help="Figure legends file declaring 'Figure N.' entries (default: 09_figure_legends.md next to the first artifact).",
    )
    parser.add_argument(
        "--figures-dir",
        type=Path,
        default=None,
        help="Optional directory of figure files (figure_N.*) to add to the figure inventory.",
    )
    parser.add_argument("--fail-on-broken", action="store_true", help="Exit non-zero on broken references.")
    parser.add_argument("--fail-on-unreferenced", action="store_true", help="Exit non-zero on unreferenced tables/figures.")
    parser.add_argument("--fail-on-order", action="store_true", help="Exit non-zero on out-of-order first mentions.")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    result = check_crossrefs(
        args.artifacts,
        tables_dir=args.tables_dir,
        legends=args.legends,
        figures_dir=args.figures_dir,
    )
    print(format_result(result))

    failed = False
    if args.fail_on_broken and result.broken:
        failed = True
    if args.fail_on_unreferenced and result.unreferenced:
        failed = True
    if args.fail_on_order and result.out_of_order:
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Format structured study records into a markdown evidence table (Elicit-style).

Retrieval is the `/evidence-table` command's job (medical-kag structured data primary,
`knowledge/evidence.md` fallback). This script is the deterministic formatting layer: it
takes a JSON list of study records and emits a clean markdown table -- a "summary of
included studies" suitable for the Discussion or a PRISMA supplement.

Columns are taken from --columns, else inferred from the records (union, first-seen order).
Missing values render blank; `|` and newlines in cells are escaped/flattened.

Usage:
  py scripts/evidence_table.py studies.json
  py scripts/evidence_table.py studies.json --columns study,design,n,intervention,outcome,result,loe
  echo '[{...}]' | py scripts/evidence_table.py -
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DEFAULT_COLUMNS = ["study", "design", "n", "intervention", "outcome", "result", "loe"]


def to_records(data) -> list[dict]:
    if isinstance(data, dict):
        for key in ("studies", "records", "rows", "data"):
            if isinstance(data.get(key), list):
                return data[key]
        return [data]
    if isinstance(data, list):
        return data
    raise ValueError("input must be a JSON list (or an object with a list field)")


def infer_columns(records: list[dict]) -> list[str]:
    cols: list[str] = []
    for r in records:
        if isinstance(r, dict):
            for k in r.keys():
                if k not in cols:
                    cols.append(k)
    return cols


def _cell(value) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        value = "; ".join(str(x) for x in value)
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def build_table(records: list[dict], columns: list[str] | None = None) -> str:
    records = [r for r in records if isinstance(r, dict)]
    cols = columns or infer_columns(records) or DEFAULT_COLUMNS
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join("---" for _ in cols) + " |",
    ]
    for r in records:
        lines.append("| " + " | ".join(_cell(r.get(c)) for c in cols) + " |")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Format study records into a markdown evidence table")
    ap.add_argument("file", help="JSON file path, or - for stdin")
    ap.add_argument("--columns", help="comma-separated column order (else inferred)")
    args = ap.parse_args(argv)

    raw = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
    records = to_records(json.loads(raw))
    columns = [c.strip() for c in args.columns.split(",")] if args.columns else None
    print(build_table(records, columns))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

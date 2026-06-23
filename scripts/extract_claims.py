#!/usr/bin/env python3
"""Extract [EVID:id]-tagged claims from a manuscript draft.

Deterministic feed for the claim-verification report (`/verify-claims`): finds each
prose sentence that carries an `[EVID:author_year]` tag, so every cited claim can be
checked against its evidence (medical-kag GraphRAG primary, `knowledge/evidence.md`
fallback). Headings, tables, blockquotes, and code fences are skipped.

Usage:
  py scripts/extract_claims.py drafts/06_discussion.md          # readable table
  py scripts/extract_claims.py drafts/06_discussion.md --json   # JSON for tooling
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EVID_RE = re.compile(r"\[EVID:([^\]]+)\]")
ABBREV = ["vs.", "e.g.", "i.e.", "et al.", "dr.", "fig.", "no.", "cf.", "approx."]


def split_sentences(text: str) -> list[str]:
    protected = re.sub(r"(\d)\.(\d)", r"\1<dot>\2", text)
    for ab in ABBREV:
        protected = re.sub(re.escape(ab), ab.replace(".", "<dot>"), protected, flags=re.I)
    parts = re.split(r"(?<=[.!?])\s+", protected)
    return [p.replace("<dot>", ".").strip() for p in parts if p.strip()]


def _is_prose(line: str) -> bool:
    s = line.lstrip()
    return bool(s) and s[0] not in "#|>" and not s.startswith("```")


def extract_claims(text: str) -> list[dict]:
    """Return [{line, sentence, ids}] for prose sentences carrying [EVID:id]."""
    claims: list[dict] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        if not _is_prose(line) or not EVID_RE.search(line):
            continue
        for sent in split_sentences(line):
            ids = EVID_RE.findall(sent)
            if ids:
                claims.append({"line": lineno, "sentence": sent.strip(), "ids": ids})
    return claims


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Extract [EVID:id]-tagged claims from a draft")
    ap.add_argument("file")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args(argv)

    text = Path(args.file).read_text(encoding="utf-8", errors="replace")
    claims = extract_claims(text)

    if args.json:
        print(json.dumps(claims, ensure_ascii=False, indent=2))
        return 0
    if not claims:
        print("No [EVID:id]-tagged claims found.")
        return 0
    for c in claims:
        tags = ", ".join(f"[EVID:{i}]" for i in c["ids"])
        print(f"L{c['line']}: {c['sentence']}")
        print(f"    -> {tags}")
    print(f"\n{len(claims)} claim(s) to verify.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

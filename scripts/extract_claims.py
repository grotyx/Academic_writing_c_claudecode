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
import importlib.util
import json
import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent


def _load_sibling(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Single source of truth for the [EVID:id] pattern: import the canonical regex
# from check_citations so extract_claims, check_coverage, and format_references
# stay in lockstep (no drift between what is extracted, validated, and converted).
EVID_RE = _load_sibling("check_citations").EVID_RE
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

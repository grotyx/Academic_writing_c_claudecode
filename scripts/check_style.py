#!/usr/bin/env python3
"""Deterministic style metrics -- the measurable half of style enforcement.

The LLM Style-Conformance verifier judges the qualitative layer (flow, claim strength,
"Do Not Imitate"). This script covers the part that is just arithmetic, so it is exact
and cheap and can gate.

Modes:
  extract <file>...                 print metrics (use to fill drafts/style_spec.md targets)
  check <file>... --spec <spec.md>  measure each file and flag deviation from the Spec
                                    "Target Metrics" table (exit 1 if any deviation)

Metrics (dependency-free, approximate): word count, mean sentence length, paragraph
count, citation density ([EVID:...] or [n] per paragraph), hedging per 100 words.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEDGES = [
    "may", "might", "could", "suggests", "suggest", "appears", "appear", "seems",
    "seem", "potentially", "possibly", "likely", "indicates", "indicate", "presumably",
    "relatively", "somewhat", "tend to", "tends to", "probable",
]
SECTIONS = ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]
ABBREV = ["vs.", "dr.", "fig.", "no.", "i.e.", "e.g.", "et al.", "cf.", "approx."]

WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-]*")
CITATION_RE = re.compile(r"\[EVID:[^\]]+\]|\[\d+(?:[-,]\s*\d+)*\]")
NUM_RE = re.compile(r"-?\d+(?:\.\d+)?")

TOLERANCE = {"word_count": 0.25, "mean_sentence_length": 0.25, "paragraph_count": 0.34}


def _strip_markup(text: str) -> str:
    keep = []
    for ln in text.splitlines():
        s = ln.lstrip()
        if not s or s[0] in "#|>" or s.startswith("```") or s.startswith("- ") and s.count("|") > 1:
            continue
        keep.append(ln)
    return "\n".join(keep)


def split_sentences(text: str) -> list[str]:
    protected = re.sub(r"(\d)\.(\d)", r"\1<dot>\2", text)
    for ab in ABBREV:
        protected = re.sub(re.escape(ab), ab.replace(".", "<dot>"), protected, flags=re.I)
    parts = re.split(r"(?<=[.!?])\s+", protected)
    return [p.replace("<dot>", ".").strip() for p in parts if p.strip()]


def count_words(text: str) -> int:
    return len(WORD_RE.findall(text))


def count_paragraphs(text: str) -> int:
    return len([b for b in re.split(r"\n\s*\n", text.strip()) if b.strip()])


def compute_metrics(raw: str) -> dict:
    text = _strip_markup(raw)
    words = count_words(text)
    sents = split_sentences(text)
    n_sent = len(sents) or 1
    paras = count_paragraphs(text) or 1
    citations = len(CITATION_RE.findall(text))
    low = text.lower()
    hedges = sum(len(re.findall(r"\b" + re.escape(h) + r"\b", low)) for h in HEDGES)
    return {
        "word_count": words,
        "sentence_count": len(sents),
        "mean_sentence_length": round(words / n_sent, 1),
        "paragraph_count": paras,
        "citation_density": round(citations / paras, 2),
        "hedging_per_100w": round(hedges / words * 100, 2) if words else 0.0,
    }


def parse_spec_targets(spec_path: Path) -> dict:
    """Best-effort parse of the Spec 'Target Metrics' table -> {section: {metric: value}}."""
    targets: dict = {}
    try:
        lines = spec_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception:
        return targets
    keys = ["word_count", "mean_sentence_length", "paragraph_count"]
    for ln in lines:
        s = ln.strip()
        if not s.startswith("|"):
            continue
        low = s.lower()
        sec = next((x for x in SECTIONS if x in low), None)
        if not sec:
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        nums = []
        for c in cells[1:]:
            m = NUM_RE.search(c)
            nums.append(float(m.group()) if m else None)
        entry = {keys[i]: nums[i] for i in range(min(len(keys), len(nums))) if nums[i]}
        if entry:
            targets[sec] = entry
    return targets


def section_of(path: Path) -> str | None:
    name = path.name.lower()
    return next((s for s in SECTIONS if s in name), None)


def nearest_spec(path: Path) -> Path | None:
    p = path.resolve()
    for parent in [p.parent, *p.parents]:
        cand = parent / "style_spec.md"
        if cand.is_file():
            return cand
        if parent.name == "drafts":
            break
    return None


def check_file(path: Path, targets: dict) -> tuple[dict, list[str]]:
    """Return (metrics, deviation messages) for a draft file vs the Spec targets."""
    metrics = compute_metrics(path.read_text(encoding="utf-8", errors="replace"))
    sec = section_of(path)
    issues: list[str] = []
    if sec and sec in targets:
        for key, tol in TOLERANCE.items():
            target = targets[sec].get(key)
            if not target:
                continue
            actual = metrics[key]
            if abs(actual - target) > tol * target:
                issues.append(
                    f"{sec}: {key} {actual:g} vs target {target:g} (>{int(tol * 100)}%)"
                )
    return metrics, issues


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    parser = argparse.ArgumentParser(description="Deterministic style metrics")
    sub = parser.add_subparsers(dest="mode", required=True)
    ex = sub.add_parser("extract", help="print metrics for files")
    ex.add_argument("files", nargs="+")
    ck = sub.add_parser("check", help="flag deviations from a Style Spec")
    ck.add_argument("files", nargs="+")
    ck.add_argument("--spec", required=True)
    args = parser.parse_args(argv)

    if args.mode == "extract":
        for f in args.files:
            m = compute_metrics(Path(f).read_text(encoding="utf-8", errors="replace"))
            print(f"{f}: " + ", ".join(f"{k}={v}" for k, v in m.items()))
        return 0

    targets = parse_spec_targets(Path(args.spec))
    if not targets:
        print(f"NOTE: no numeric targets parsed from {args.spec} (fill the Target Metrics table).")
    flagged = 0
    for f in args.files:
        metrics, issues = check_file(Path(f), targets)
        print(f"{f}: " + ", ".join(f"{k}={v}" for k, v in metrics.items()))
        for msg in issues:
            print(f"  STYLE-METRIC: {msg}")
            flagged += 1
    if flagged:
        print(f"FAIL: {flagged} style-metric deviation(s).")
        return 1
    print("OK: style metrics within tolerance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

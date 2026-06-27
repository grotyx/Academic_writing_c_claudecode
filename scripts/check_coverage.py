#!/usr/bin/env python3
"""Citation coverage audit (Phase 6 QC).

The real citation risks are **wrong** citations (a source that does not support
the claim -- caught by check_citations.py + the semantic citation verifier) and
**over-citation** (padding a single claim with unnecessary references). Leaving a
registered reference *uncited* is NOT a defect: good literature review cites only
what is necessary, so an "orphan" reference is normal curation, reported here as
neutral information -- not as wasted work.

Reports, against `knowledge/evidence.md`:
  - **over-citation** — sentences citing more `[EVID:id]` than a threshold
    (citation stuffing / padding). This is the primary quality signal.
  - **unknown citations** — `[EVID:id]` cited in the manuscript but absent from
    evidence.md (a hallucinated/unregistered citation; also caught by
    check_citations.py, surfaced here for completeness)
  - **uncited references** (neutral) — registered evidence entries not cited
    anywhere. Informational: review whether each *should* be cited, but uncited
    is a legitimate curation outcome, not an error.
  - **citation density** — `[EVID:id]` count per manuscript section.
  - **unrealized claims** (optional, neutral) — `[EVID:id]` planned in
    `draft_plan.md` but not cited in the drafted body (you may have decided
    against it; a heads-up, not a defect).

Advisory by default (exit 0). `--fail-on-over-citation` and `--fail-on-unknown`
are the meaningful blocking flags; `--fail-on-uncited-verified` and
`--fail-on-unrealized` exist only for workflows that explicitly require full use,
and are off by default because uncited is not a defect.

The evidence/citation parsing reuses check_citations.py so the two stay in lockstep.
"""

from __future__ import annotations

import argparse
import importlib.util
import re
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent

# A "sentence" = a run of text ending in . ! or ? (spanning line breaks). Used to
# count how many citations pile onto one claim (over-citation detection).
SENTENCE_RE = re.compile(r"[^.!?]*[.!?]", re.DOTALL)
# Default: flag a sentence carrying MORE than this many [EVID:id] citations.
DEFAULT_MAX_PER_SENTENCE = 4


def _load_sibling(name: str):
    """Import a sibling script (scripts/<name>.py) by path (no package needed)."""
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / f"{name}.py")
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise ImportError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_cc = _load_sibling("check_citations")
parse_evidence_entries = _cc.parse_evidence_entries
iter_evid_tokens = _cc.iter_evid_tokens
EVID_RE = _cc.EVID_RE
strip_code_fences = _cc.strip_code_fences


class OverCitation(NamedTuple):
    artifact: str
    line: int
    count: int
    snippet: str


class CoverageResult(NamedTuple):
    citation_counts: dict[str, int]  # evidence_id -> total citations across all artifacts
    per_artifact: dict[str, dict[str, int]]  # artifact -> {evidence_id: count}
    density: dict[str, int]  # artifact -> total [EVID:id] tokens
    over_citations: list[OverCitation]  # sentences exceeding the per-sentence citation cap
    uncited: list[tuple[str, str]]  # (evidence_id, source_status) registered but never cited (neutral)
    unknown: list[str]  # cited in manuscript but not registered in evidence.md
    unrealized: list[str]  # planned in draft_plan.md but uncited in the sections (neutral)


def find_over_citations(artifact: Path, max_per_sentence: int) -> list[OverCitation]:
    """Flag sentences carrying more than `max_per_sentence` [EVID:id] citations."""
    text = strip_code_fences(artifact.read_text(encoding="utf-8"))
    hits: list[OverCitation] = []
    for match in SENTENCE_RE.finditer(text):
        sentence = match.group(0)
        count = len(EVID_RE.findall(sentence))
        if count > max_per_sentence:
            line = text.count("\n", 0, match.start()) + 1
            snippet = " ".join(sentence.split())[:90]
            hits.append(OverCitation(str(artifact), line, count, snippet))
    return hits


def audit(
    artifacts: list[Path],
    *,
    evidence_path: Path,
    draft_plan: Path | None = None,
    max_per_sentence: int = DEFAULT_MAX_PER_SENTENCE,
) -> CoverageResult:
    entries = parse_evidence_entries(evidence_path.read_text(encoding="utf-8"))
    counts: dict[str, int] = {eid: 0 for eid in entries}
    per_artifact: dict[str, dict[str, int]] = {}
    density: dict[str, int] = {}
    unknown: set[str] = set()
    over_citations: list[OverCitation] = []

    for artifact in artifacts:
        tokens = iter_evid_tokens(artifact)  # [(evidence_id, line), ...]
        local: dict[str, int] = {}
        for citation_id, _line in tokens:
            local[citation_id] = local.get(citation_id, 0) + 1
            if citation_id in counts:
                counts[citation_id] += 1
            else:
                unknown.add(citation_id)
        per_artifact[str(artifact)] = local
        density[str(artifact)] = len(tokens)
        over_citations.extend(find_over_citations(artifact, max_per_sentence))

    # source_status from check_citations is lowercase ("verified"/"todo"/...).
    # Uncited registered refs are reported neutrally -- curation, not a defect.
    uncited = sorted(
        (eid, entries[eid].source_status or "unspecified")
        for eid, count in counts.items()
        if count == 0
    )

    unrealized: list[str] = []
    if draft_plan is not None and draft_plan.exists():
        planned = {cid for cid, _line in iter_evid_tokens(draft_plan)}
        cited = {eid for eid, count in counts.items() if count > 0}
        # Planned + registered in evidence.md, but never cited in the drafted body.
        unrealized = sorted(p for p in planned if p in entries and p not in cited)

    return CoverageResult(
        counts, per_artifact, density, over_citations, uncited, sorted(unknown), unrealized
    )


def format_result(result: CoverageResult) -> str:
    total_refs = len(result.citation_counts)
    cited = sum(1 for c in result.citation_counts.values() if c > 0)
    lines = [
        "COVERAGE REPORT",
        f"references: {total_refs} registered, {cited} cited "
        f"({len(result.uncited)} uncited) | over-citation: {len(result.over_citations)} | "
        f"unknown: {len(result.unknown)}",
    ]

    # Over-citation -- the primary quality signal: too many refs on one claim.
    if result.over_citations:
        lines.append("over-citation (sentences with too many citations):")
        for oc in sorted(result.over_citations, key=lambda o: (-o.count, o.artifact, o.line)):
            lines.append(f"  {oc.artifact}:{oc.line}  {oc.count} citations -> \"{oc.snippet}\"")

    # Unknown -- a real error (cited but unregistered / hallucinated).
    if result.unknown:
        lines.append("unknown (cited but not in evidence.md -- verify or remove):")
        for cid in result.unknown:
            lines.append(f"  EVID:{cid}")

    # Density per section (informational).
    lines.append("density:")
    for artifact, total in sorted(result.density.items()):
        lines.append(f"  {artifact}: {total} citations")

    # Uncited registered refs -- NEUTRAL. Review, but uncited is fine (curation).
    if result.uncited:
        lines.append("uncited references (review only -- not citing is a valid choice):")
        verified = [o for o in result.uncited if o[1] == "verified"]
        others = [o for o in result.uncited if o[1] != "verified"]
        for eid, status in verified + others:
            lines.append(f"  EVID:{eid} ({status})")

    # Unrealized plan items -- NEUTRAL heads-up.
    if result.unrealized:
        lines.append("unrealized (planned in draft_plan, not cited -- heads-up, not a defect):")
        for cid in result.unrealized:
            lines.append(f"  EVID:{cid}")

    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Citation coverage / orphan audit against knowledge/evidence.md."
    )
    parser.add_argument("artifacts", nargs="+", type=Path, help="Manuscript section markdown files.")
    parser.add_argument(
        "--evidence",
        type=Path,
        default=ROOT / "knowledge" / "evidence.md",
        help="evidence.md registry (default knowledge/evidence.md).",
    )
    parser.add_argument(
        "--draft-plan",
        type=Path,
        default=None,
        help="Optional draft_plan.md to check planned Claim->Citation EVID realization.",
    )
    parser.add_argument(
        "--max-citations-per-sentence",
        type=int,
        default=DEFAULT_MAX_PER_SENTENCE,
        help=f"Flag a sentence carrying more than N citations (default {DEFAULT_MAX_PER_SENTENCE}).",
    )
    # Meaningful blocking flags: real quality defects.
    parser.add_argument(
        "--fail-on-over-citation",
        action="store_true",
        help="Exit non-zero if any sentence exceeds the per-sentence citation cap.",
    )
    parser.add_argument(
        "--fail-on-unknown",
        action="store_true",
        help="Exit non-zero if any cited [EVID:id] is not registered in evidence.md.",
    )
    # Off-by-default: uncited/unrealized are NOT defects; only for strict full-use policies.
    parser.add_argument(
        "--fail-on-uncited-verified",
        action="store_true",
        help="Strict/optional: exit non-zero if any VERIFIED entry is uncited "
        "(uncited is normally a valid curation choice, so this is off by default).",
    )
    parser.add_argument(
        "--fail-on-unrealized",
        action="store_true",
        help="Strict/optional: exit non-zero if any draft_plan-planned citation is uncited.",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    result = audit(
        args.artifacts,
        evidence_path=args.evidence,
        draft_plan=args.draft_plan,
        max_per_sentence=args.max_citations_per_sentence,
    )
    print(format_result(result))

    failed = False
    if args.fail_on_over_citation and result.over_citations:
        failed = True
    if args.fail_on_unknown and result.unknown:
        failed = True
    if args.fail_on_uncited_verified and any(s == "verified" for _e, s in result.uncited):
        failed = True
    if args.fail_on_unrealized and result.unrealized:
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

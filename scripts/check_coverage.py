#!/usr/bin/env python3
"""Citation coverage / orphan audit (Phase 6 QC).

Reports, against `knowledge/evidence.md`:
  - **orphan references** — registered evidence entries never cited by any
    `[EVID:id]` in the manuscript (verified-but-uncited refs are wasted work or
    a missing citation; todo/abstract-only orphans are usually expected)
  - **citation density** — `[EVID:id]` count per manuscript section (Introduction
    and Discussion should carry most; Results usually few)
  - **unknown citations** — `[EVID:id]` cited in the manuscript but absent from
    evidence.md (also caught by check_citations.py; surfaced here for the matrix)
  - **unrealized claims** (optional) — `[EVID:id]` planned in `draft_plan.md`
    (the Claim->Citation mapping) but never cited in the drafted sections

This is an **advisory QC report**, not a hard gate: it exits 0 by default. Use
`--fail-on-orphan-verified`, `--fail-on-unrealized`, or `--fail-on-unknown` to
make any dimension blocking (e.g. in a Phase 6 check).

The evidence/citation parsing reuses check_citations.py so the two stay in lockstep.
"""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = Path(__file__).resolve().parent


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


class CoverageResult(NamedTuple):
    citation_counts: dict[str, int]  # evidence_id -> total citations across all artifacts
    per_artifact: dict[str, dict[str, int]]  # artifact -> {evidence_id: count}
    density: dict[str, int]  # artifact -> total [EVID:id] tokens
    orphans: list[tuple[str, str]]  # (evidence_id, source_status) registered but never cited
    unknown: list[str]  # cited in manuscript but not registered in evidence.md
    unrealized: list[str]  # planned in draft_plan.md but uncited in the sections


def audit(
    artifacts: list[Path],
    *,
    evidence_path: Path,
    draft_plan: Path | None = None,
) -> CoverageResult:
    entries = parse_evidence_entries(evidence_path.read_text(encoding="utf-8"))
    counts: dict[str, int] = {eid: 0 for eid in entries}
    per_artifact: dict[str, dict[str, int]] = {}
    density: dict[str, int] = {}
    unknown: set[str] = set()

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

    # source_status from check_citations is lowercase ("verified"/"todo"/...).
    orphans = sorted(
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

    return CoverageResult(counts, per_artifact, density, orphans, sorted(unknown), unrealized)


def format_result(result: CoverageResult) -> str:
    total_refs = len(result.citation_counts)
    cited = sum(1 for c in result.citation_counts.values() if c > 0)
    lines = [
        "COVERAGE REPORT",
        f"references: {total_refs} registered, {cited} cited, {len(result.orphans)} orphan",
    ]

    # Density per section
    lines.append("density:")
    for artifact, total in sorted(result.density.items()):
        lines.append(f"  {artifact}: {total} citations")

    # Orphans, verified ones first (those are the notable ones)
    if result.orphans:
        lines.append("orphans (registered, never cited):")
        verified = [o for o in result.orphans if o[1] == "verified"]
        others = [o for o in result.orphans if o[1] != "verified"]
        for eid, status in verified + others:
            flag = "  <- verified work unused" if status == "verified" else ""
            lines.append(f"  EVID:{eid} ({status}){flag}")

    if result.unknown:
        lines.append("unknown (cited but not in evidence.md):")
        for cid in result.unknown:
            lines.append(f"  EVID:{cid}")

    if result.unrealized:
        lines.append("unrealized (planned in draft_plan but uncited):")
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
        "--fail-on-orphan-verified",
        action="store_true",
        help="Exit non-zero if any VERIFIED evidence entry is never cited.",
    )
    parser.add_argument(
        "--fail-on-unrealized",
        action="store_true",
        help="Exit non-zero if any draft_plan-planned citation is uncited in the body.",
    )
    parser.add_argument(
        "--fail-on-unknown",
        action="store_true",
        help="Exit non-zero if any cited [EVID:id] is not registered in evidence.md.",
    )
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    result = audit(args.artifacts, evidence_path=args.evidence, draft_plan=args.draft_plan)
    print(format_result(result))

    failed = False
    if args.fail_on_orphan_verified and any(status == "verified" for _eid, status in result.orphans):
        failed = True
    if args.fail_on_unrealized and result.unrealized:
        failed = True
    if args.fail_on_unknown and result.unknown:
        failed = True
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

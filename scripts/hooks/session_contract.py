#!/usr/bin/env python3
"""SessionStart hook: inject the enforced workflow contract into context.

Claude Code injects this hook's stdout into the session context, so the
non-negotiable rules are present every session (the soft half of enforcement;
the hard half is the PreToolUse gate in enforce_gates.py).
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CONTRACT = """\
WORKFLOW CONTRACT (enforced - academic paper template; full rules in CLAUDE.md):
- PLAN-FIRST (hook-enforced): no manuscript section is written without
  drafts/.../draft_plan.md (Rule 8); no analysis script without
  data/.../analysis_plan.md (Rule 7). A PreToolUse hook blocks violations.
- GATES: never proceed past a phase gate without a recorded `status: PASS` in
  review/gates/ (Rule 9). Verify deterministically with `/verify`
  (py scripts/verify_all.py ...).
- GROUNDING: cite only [EVID:id] entries present in knowledge/evidence.md; use
  only numbers present in results/*.csv. Never fabricate references or statistics.
- QC: minimum 3 rounds before submission; human + co-author review mandatory.
"""


def style_spec_addendum(root: Path = ROOT) -> str:
    """Surface any active project Style Spec so it is in context every session."""
    try:
        specs = sorted(p for p in (root / "drafts").rglob("style_spec.md") if p.is_file())
    except Exception:
        return ""
    if not specs:
        return ""
    rels = ", ".join(str(p.relative_to(root)).replace("\\", "/") for p in specs)
    return (
        "STYLE (active Style Spec present - apply it):\n"
        f"- A project Style Spec exists ({rels}). When drafting or transforming prose,\n"
        "  load it and its bound exemplar and match it (structure, sentence length,\n"
        "  hedging, reference format). For 'make it academic' requests follow the\n"
        "  style-pass protocol (docs/style_transform_protocol.md) - do not free-hand."
    )


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # avoid cp949 console crashes
    except Exception:
        pass
    print(CONTRACT)
    addendum = style_spec_addendum()
    if addendum:
        print(addendum)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

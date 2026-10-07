#!/usr/bin/env python3
"""SessionStart hook: inject the enforced workflow contract into context.

Claude Code injects this hook's stdout into the session context, so the
non-negotiable rules are present every session (the soft half of enforcement;
the hard half is the PreToolUse gate in enforce_gates.py). With the academic writing
mode on (the default), it also injects the core academic style card
(docs/academic_style/core.md) so every draft starts in that register.
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
  (python scripts/verify_all.py ...). Hooks fail open: confirm they run with
  `python -m harness doctor` (hooks.ok).
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


def academic_card(root: Path) -> str:
    """The always-on academic writing card, unless the writing mode is off (fails quiet)."""
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import academic_style

        # Only in a paper folder: the plugin hook runs in every project the user opens.
        if academic_style.mode() == "off" or not academic_style.in_paper(root):
            return ""
        return academic_style.core_card(root)
    except Exception:
        return ""


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # avoid cp949 console crashes
    except Exception:
        pass
    print(CONTRACT)
    # Plugin hooks (manuwright hook session) pass the paper folder; a checkout scans itself.
    project = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT
    for extra in (style_spec_addendum(project), academic_card(project)):
        if extra:
            print(extra)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

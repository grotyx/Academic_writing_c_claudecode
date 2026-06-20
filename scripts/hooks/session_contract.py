#!/usr/bin/env python3
"""SessionStart hook: inject the enforced workflow contract into context.

Claude Code injects this hook's stdout into the session context, so the
non-negotiable rules are present every session (the soft half of enforcement;
the hard half is the PreToolUse gate in enforce_gates.py).
"""

import sys

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


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # avoid cp949 console crashes
    except Exception:
        pass
    print(CONTRACT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

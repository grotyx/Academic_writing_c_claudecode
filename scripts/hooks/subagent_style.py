#!/usr/bin/env python3
"""SubagentStart hook: give every subagent the academic writing card.

SessionStart context reaches only the main thread, so a subagent that drafts or rewrites a section
(or a verifier that judges one) would otherwise work without the register (the gap ponytail's
SubagentStart hook closes). With the writing mode on, this prints the core card as
hookSpecificOutput.additionalContext, the form Claude Code reads for SubagentStart. Codex and other
hosts ignore the event. FAILS OPEN: any error prints nothing.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except Exception:
        event = {}
    try:
        import academic_style

        cwd = Path(event["cwd"]) if event.get("cwd") else Path.cwd()
        if academic_style.mode() == "off" or not academic_style.in_paper(cwd):
            return 0  # only inside a paper folder
        context = academic_style.core_card(cwd)
    except Exception:
        return 0
    sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "SubagentStart",
                                                        "additionalContext": context}}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

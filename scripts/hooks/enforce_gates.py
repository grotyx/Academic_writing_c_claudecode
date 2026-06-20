#!/usr/bin/env python3
"""PreToolUse hook: enforce the plan-first gates (CLAUDE.md Rules 7 & 8).

Reads the Claude Code PreToolUse event JSON from stdin and BLOCKS (exit 2) a
Write/Edit that would:
  - draft a manuscript section (`drafts/.../0N_*.md`) without a `draft_plan.md`
    in the same drafts folder (Rule 8), or
  - create an analysis script (`data/.../py/*.py`) without an `analysis_plan.md`
    in the corresponding data folder (Rule 7).

Exit-code contract (Claude Code): 0 = allow, 2 = block (stderr is shown to
Claude). Any other failure is treated as a non-blocking error.

This hook FAILS OPEN: on any parse/logic error it returns 0 (allow). A gate
must never wedge the user's workflow because of a hook bug.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Manuscript section files: 01_title.md ... 09_figure_legends.md (basename only,
# anchored on a leading slash so e.g. draft_plan.md / table_1.md never match).
SECTION_RE = re.compile(r"/0[1-9]_[^/]*\.md$", re.IGNORECASE)
# Analysis scripts: .../data/py/x.py or .../data/<paper>/py/x.py
ANALYSIS_SCRIPT_RE = re.compile(r"/data/(?:[^/]+/)?py/[^/]*\.py$", re.IGNORECASE)


def _norm(value: str) -> str:
    return (value or "").replace("\\", "/")


def decide(event: dict) -> str | None:
    """Return a block reason, or None to allow. Pure function for testing."""
    if event.get("tool_name") not in ("Write", "Edit"):
        return None

    tool_input = event.get("tool_input") or {}
    raw_path = tool_input.get("file_path") or ""
    if not raw_path:
        return None

    cwd = _norm(event.get("cwd") or ".")
    target = Path(_norm(raw_path))
    if not target.is_absolute():
        target = Path(cwd) / target
    spath = _norm(str(target))

    # Rule 8 — drafting a section requires a completed draft plan.
    # Revisions (Phase 8) revise an existing manuscript and are exempt.
    if "/drafts/" in spath and "/revision/" not in spath and SECTION_RE.search(spath):
        plan = target.parent / "draft_plan.md"
        if not plan.exists():
            return (
                "BLOCKED by workflow gate (CLAUDE.md Rule 8): "
                f"{plan} does not exist.\n"
                "Create the draft plan first: copy docs/draft_plan_template.md into "
                "the drafts folder, complete the 10 items, get user approval, then draft sections."
            )

    # Rule 7 — generating an analysis script requires an approved analysis plan.
    if ANALYSIS_SCRIPT_RE.search(spath):
        plan = target.parent.parent / "analysis_plan.md"
        if not plan.exists():
            return (
                "BLOCKED by workflow gate (CLAUDE.md Rule 7): "
                f"{plan} does not exist.\n"
                "Create and get approval on analysis_plan.md before generating analysis scripts."
            )

    return None


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # avoid cp949 console crashes
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0  # fail open
    try:
        reason = decide(event)
    except Exception:
        return 0  # fail open
    if reason:
        sys.stderr.write(reason + "\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""PostToolUse hook: surface style/terminology drift right after a draft edit.

After a Write/Edit to a manuscript section under `drafts/`, this runs the same
checks as `lint_manuscript.py` (terminology registry + style rules) on the edited
file and, if there are findings, feeds them back to Claude (exit 2 + stderr) so it
can fix them immediately -- no need for the author to repeat the same style note.

It is advisory only: it never blocks (the file is already written), is capped, and
FAILS OPEN (exit 0) on any error. draft_plan.md and figures/ are excluded.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # scripts/hooks/ -> repo root
MAX_LINES = 20


def _load_lint():
    spec = importlib.util.spec_from_file_location(
        "lint_manuscript", ROOT / "scripts" / "lint_manuscript.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _load_check_style():
    spec = importlib.util.spec_from_file_location(
        "check_style", ROOT / "scripts" / "check_style.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _style_metric_lines(target: Path) -> list[str]:
    """Measurable-style deviations vs the nearest Style Spec (empty if no spec)."""
    try:
        cs = _load_check_style()
        spec = cs.nearest_spec(target)
        if not spec:
            return []
        _metrics, issues = cs.check_file(target, cs.parse_spec_targets(spec))
        return [f"[STYLE-METRIC] {m}" for m in issues]
    except Exception:
        return []


def _is_manuscript_md(spath: str) -> bool:
    s = spath.replace("\\", "/")
    return (
        "/drafts/" in s
        and s.endswith(".md")
        and "/draft_plan" not in s
        and "/figures/" not in s
    )


def evaluate(event: dict) -> tuple[int, str]:
    """Return (exit_code, stderr_message). Pure function for testing."""
    if event.get("tool_name") not in ("Write", "Edit"):
        return 0, ""
    raw_path = (event.get("tool_input") or {}).get("file_path") or ""
    if not raw_path:
        return 0, ""
    cwd = (event.get("cwd") or ".").replace("\\", "/")
    target = Path(raw_path)
    if not target.is_absolute():
        target = Path(cwd) / target
    if not _is_manuscript_md(str(target)) or not target.is_file():
        return 0, ""

    lint = _load_lint()
    forbidden = lint.load_forbidden_terms(lint.TERMINOLOGY_FILE)
    issues = lint.lint_file(target, forbidden)

    term_lines = [
        f"[{code}] line {line}: {message}" for code, _p, line, message in issues[:MAX_LINES]
    ]
    style_lines = _style_metric_lines(target)
    if not term_lines and not style_lines:
        return 0, ""

    extra = (
        f"\n... and {len(issues) - MAX_LINES} more terminology"
        if len(issues) > MAX_LINES
        else ""
    )
    total = len(issues) + len(style_lines)
    msg = (
        f"Style lint on {target.name}: {total} finding(s) "
        f"(terminology + style metrics vs Style Spec). Fix before finalizing:\n"
        + "\n".join(term_lines + style_lines)
        + extra
        + "\n"
    )
    return 2, msg


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0  # fail open
    try:
        code, message = evaluate(event)
    except Exception:
        return 0  # fail open
    if message:
        sys.stderr.write(message)
    return code


if __name__ == "__main__":
    raise SystemExit(main())

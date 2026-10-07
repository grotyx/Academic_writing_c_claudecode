#!/usr/bin/env python3
"""PreToolUse hook: enforce the plan-first gates (CLAUDE.md Rules 7 & 8).

Reads the Claude Code PreToolUse event JSON from stdin and BLOCKS (exit 2) a
Write/Edit/MultiEdit that would:
  - draft a manuscript section (`drafts/.../0N_*.md`) without a `draft_plan.md`
    in the same drafts folder (Rule 8), or
  - create an analysis script (`data/.../py/*.py`) without an `analysis_plan.md`
    in the corresponding data folder (Rule 7).
A plan only counts when it has no unresolved template placeholders AND carries
a checked `- [x] 사용자 승인 완료` line; a plan missing that line is blocked.

Exit-code contract (Claude Code): 0 = allow, 2 = block (stderr is shown to
Claude). Any other failure is treated as a non-blocking error.

Academic writing mode `strict` (`manuwright mode strict`): a write to a manuscript prose file
under drafts/ is also BLOCKED when the new text has high-severity academic-style findings
(AI-register phrases, trailing "-ing" clauses, contractions, bold in running text, chat
residue); see scripts/academic_style.py. In the default `academic` mode those findings are
reported after the edit instead (lint_on_edit.py).

This hook FAILS OPEN: on any parse/logic error it returns 0 (allow). A gate
must never wedge the user's workflow because of a hook bug.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from plan_validation import validate_plan_content, approval_problem

# Tools that can create or modify files in Claude Code.
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "apply_patch")  # apply_patch = Codex

# Manuscript section files: 01_title.md ... 09_figure_legends.md (basename only,
# anchored on a leading slash so e.g. draft_plan.md / table_1.md never match).
SECTION_RE = re.compile(r"/0[1-9]_[^/]*\.md$", re.IGNORECASE)
# Analysis scripts: .../data/py/x.py or .../data/<paper>/py/x.py
ANALYSIS_SCRIPT_RE = re.compile(r"/data/(?:[^/]+/)?py/[^/]*\.py$", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(
    r"\[[^\]]*(?:작성|기술|입력|기준|변수|검정법|선택 근거|목적|내용|키워드|"
    r"필요|설명|filename|n rows|n columns|var|fig_|Bar/Box|Additional Analysis|"
    r"귀무가설|대립가설)[^\]]*\]",
    re.IGNORECASE,
)
SAMPLE_SIZE_PLACEHOLDER_RE = re.compile(
    r"(?im)^\s*(?:\*\*Expected Sample Size:\*\*\s*)?\[N\]\s*$"
)
PERCENT_PLACEHOLDER_RE = re.compile(r"\[%\]")
UNCHECKED_APPROVAL_RE = re.compile(
    r"-\s*\[\s\]\s*(?:\*\*)?사용자 승인 완료", re.IGNORECASE
)
# A plan counts as approved only with an explicitly CHECKED approval box. A plan
# that omits the line altogether is not approved (CLAUDE.md Rule 9: an unchecked
# or missing approval is not a plan).
CHECKED_APPROVAL_RE = re.compile(
    r"-\s*\[\s*x\s*\]\s*(?:\*\*)?사용자 승인 완료", re.IGNORECASE
)


def _norm(value: str) -> str:
    return (value or "").replace("\\", "/")


def plan_problem(plan: Path) -> str | None:
    """Return why a plan file is not usable as an approved plan, else None."""
    if not plan.exists():
        return "missing"
    try:
        text = plan.read_text(encoding="utf-8")
    except Exception:
        return "unreadable"
    if (
        PLACEHOLDER_RE.search(text)
        or SAMPLE_SIZE_PLACEHOLDER_RE.search(text)
        or PERCENT_PLACEHOLDER_RE.search(text)
        or UNCHECKED_APPROVAL_RE.search(text)
    ):
        return "unresolved template or not approved"
    if not CHECKED_APPROVAL_RE.search(text):
        return "not approved"
    kind = "analysis" if plan.name == "analysis_plan.md" else "draft"
    if validate_plan_content(text, kind):
        return "incomplete plan: required sections are absent or empty"
    return approval_problem(plan)


PATCH_PATH_RE = re.compile(r"^\*\*\* (?:Add File|Update File|Move to): (.+?)\s*$", re.M)


def event_paths(event: dict) -> list[str]:
    """Target paths of a write event: Claude `file_path`, or Codex `apply_patch` headers."""
    if event.get("tool_name") not in WRITE_TOOLS:
        return []
    tool_input = event.get("tool_input") or {}
    if tool_input.get("file_path"):
        return [tool_input["file_path"]]
    return PATCH_PATH_RE.findall(str(tool_input.get("command") or tool_input.get("patch") or ""))


def decide(event: dict) -> str | None:
    """Return a block reason, or None to allow. Pure function for testing."""
    for raw_path in event_paths(event):
        reason = decide_path(event.get("cwd") or ".", raw_path) or strict_style(event, raw_path)
        if reason:
            return reason
    return None


def is_prose_file(raw_path: str) -> bool:
    spath = "/" + _norm(raw_path).lstrip("/")
    name = spath.rsplit("/", 1)[-1].lower()
    return ("/drafts/" in spath and name.endswith(".md") and "/figures/" not in spath
            and name not in ("draft_plan.md", "style_spec.md") and not name.startswith("table"))


def new_text(event: dict, raw_path: str) -> str:
    """The text this write adds: Write content, Edit/MultiEdit replacements, or a patch's + lines."""
    tool_input = event.get("tool_input") or {}
    if tool_input.get("file_path"):
        if "content" in tool_input:
            return str(tool_input.get("content") or "")
        edits = tool_input.get("edits") or [tool_input]
        return "\n\n".join(str(e.get("new_string") or "") for e in edits if isinstance(e, dict))
    patch = str(tool_input.get("command") or tool_input.get("patch") or "")
    added, inside = [], False
    for line in patch.splitlines():
        header = PATCH_PATH_RE.match(line)
        if header or line.startswith("*** "):
            inside = bool(header) and _norm(header.group(1)) == _norm(raw_path)
            continue
        if inside and line.startswith("+"):
            added.append(line[1:])
    return "\n".join(added)


def strict_style(event: dict, raw_path: str) -> str | None:
    """Strict academic writing mode: block new manuscript prose with high-severity findings."""
    if not is_prose_file(raw_path):
        return None
    import academic_style

    if academic_style.mode() != "strict":
        return None
    section = academic_style.section_of(raw_path)
    issues = [i for i in academic_style.prose_issues(new_text(event, raw_path), section)
              if i[0] == academic_style.HIGH]
    if not issues:
        return None
    shown = "\n".join(f"- line {line} of the new text [{code}] {message}" for _, code, line, message in issues[:12])
    return (
        f"BLOCKED by academic writing mode (strict): {len(issues)} high-severity style finding(s) in the "
        f"text written to {raw_path}:\n{shown}\n"
        f"Rewrite those sentences and write again. Section card: `manuwright style card {section or '<section>'}`. "
        "(`manuwright mode academic` reports these after the edit instead of blocking.)"
    )


def decide_path(event_cwd: str, raw_path: str) -> str | None:
    cwd = _norm(event_cwd)
    target = Path(_norm(raw_path))
    if not target.is_absolute():
        target = Path(cwd) / target
    # Force a single leading slash so the slash-anchored dir checks below
    # ("/drafts/", "/data/.../py/") fire even when cwd is relative/missing and
    # the path normalizes to e.g. "drafts/03_results.md" (no leading slash).
    # Without this the plan-first gate would FAIL OPEN on a relative cwd.
    spath = "/" + _norm(str(target)).lstrip("/")

    # Rule 8 — drafting a section requires a completed draft plan.
    # Revisions (Phase 8) revise an existing manuscript and are exempt.
    if "/drafts/" in spath and "/revision/" not in spath and SECTION_RE.search(spath):
        plan = target.parent / "draft_plan.md"
        problem = plan_problem(plan)
        if problem:
            if problem == "missing":
                detail = f"{plan} does not exist."
            else:
                detail = f"{plan} is an unresolved template or has not been approved."
            return (
                "BLOCKED by workflow gate (CLAUDE.md Rule 8): "
                f"{detail}\n"
                "Create the draft plan first: copy docs/draft_plan_template.md into "
                "the drafts folder, complete the 10 items, get the author's approval (they tick the box, or approve in chat and you run "
                "`manuwright approve <plan> --kind draft --approved-by <author> --quote <their words>`), then draft sections."
            )

    # Rule 7 — generating an analysis script requires an approved analysis plan.
    if ANALYSIS_SCRIPT_RE.search(spath):
        plan = target.parent.parent / "analysis_plan.md"
        problem = plan_problem(plan)
        if problem:
            if problem == "missing":
                detail = f"{plan} does not exist."
            else:
                detail = f"{plan} is an unresolved template or has not been approved."
            return (
                "BLOCKED by workflow gate (CLAUDE.md Rule 7): "
                f"{detail}\n"
                "Create analysis_plan.md and get the author's approval first (they tick the box, or approve in chat and you "
                "run `manuwright approve <plan> --kind analysis --approved-by <author> --quote <their words>`)."
            )

    return None


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # avoid cp949 console crashes
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")  # Claude Code emits UTF-8 JSON; Windows default is cp949
    except Exception:
        pass
    try:
        event = json.loads(sys.stdin.read() or "{}")
        reason = decide(event)
    except Exception as exc:
        # Fail open, but never silently: the gate did not run for this edit.
        sys.stderr.write(f"WARNING: workflow gate hook error, plan-first check skipped: {exc!r}\n")
        return 0
    if reason:
        sys.stderr.write(reason + "\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

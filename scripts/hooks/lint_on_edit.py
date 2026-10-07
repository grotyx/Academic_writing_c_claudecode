#!/usr/bin/env python3
"""PostToolUse hook: surface style/terminology drift right after a draft edit.

After a Write/Edit/MultiEdit to a manuscript section under `drafts/`, this runs the same
checks as `lint_manuscript.py` (terminology registry + style rules), plus the academic-prose
checks of `academic_style.py` when the writing mode is on (the default), on the edited
file and, if there are findings, feeds them back to Claude (exit 2 + stderr) so it
can fix them immediately -- no need for the author to repeat the same style note.

It is advisory only: it never blocks (the file is already written), is capped, and
FAILS OPEN (exit 0) on any error. draft_plan.md and figures/ are excluded.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # scripts/hooks/ -> repo root
MAX_LINES = 20
WRITE_TOOLS = ("Write", "Edit", "MultiEdit", "apply_patch")  # apply_patch = Codex


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


def _load_academic():
    spec = importlib.util.spec_from_file_location(
        "academic_style", ROOT / "scripts" / "academic_style.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _academic_lines(target: Path) -> list[str]:
    """Academic-prose findings (writing mode academic/strict), plus a pointer to the section card."""
    try:
        acad = _load_academic()
        section = acad.section_of(target)
        if acad.mode() == "off" or section is None:
            return []  # manuscript sections only: not references, letters, notes or plans
        project = next((p for p in target.resolve().parents if (p / "project.json").is_file()), None)
        issues = acad.prose_issues(
            target.read_text(encoding="utf-8", errors="replace"), section,
            acad.long_limit_for(section, project),
        )
    except Exception:
        return []
    issues = sorted(issues, key=lambda i: i[0] != "high")  # must-fix first
    lines = [f"[ACADEMIC/{'MUST FIX' if sev == 'high' else 'consider'}/{code}] line {line}: {msg}"
             for sev, code, line, msg in issues[:MAX_LINES]]
    if any(sev != "high" for sev, *_ in issues):
        lines.append("('consider' items are suggestions: keep the author's wording when it is deliberate)")
    if lines and section:
        lines.append(f"(section card with moves, phrasebank and model paragraphs: `manuwright style card {section}`)")
    return lines


def _overclaim_lines(target: Path) -> list[str]:
    """Cited sentences worded more strongly than their evidence.md Claim Strength (advisory)."""
    try:
        evidence = next((p / "knowledge" / "evidence.md" for p in target.resolve().parents
                         if (p / "knowledge" / "evidence.md").is_file()), None)
        if evidence is None:
            return []
        spec = importlib.util.spec_from_file_location(
            "check_claim_strength", ROOT / "scripts" / "check_claim_strength.py")
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return [f"[OVERCLAIM] line {line}: {msg}" for _p, line, msg in module.check([target], evidence)[:MAX_LINES]]
    except Exception:
        return []


def _is_manuscript_md(spath: str) -> bool:
    # Force a single leading slash so "/drafts/" matches even for a relative path
    # like "drafts/05_results.md" (cwd relative/missing), consistent with enforce_gates.
    s = "/" + spath.replace("\\", "/").lstrip("/")
    return (
        "/drafts/" in s
        and s.endswith(".md")
        and "/draft_plan" not in s
        and "/figures/" not in s
    )


def project_terminology(target: Path) -> Path | None:
    """The paper's own registry: `terminology` in the nearest project.json above the edited file.

    Mirrors `python -m harness verify`, so the edit-time hook and the manifest profile apply the
    same terms (e.g. an abbreviation the approved draft plan chose deliberately).
    """
    for folder in target.resolve().parents:
        manifest = folder / "project.json"
        if manifest.is_file():
            try:
                name = json.loads(manifest.read_text(encoding="utf-8")).get("terminology")
            except (OSError, ValueError):
                return None
            registry = (folder / name).resolve() if name else None
            return registry if registry and registry.is_file() and folder in registry.parents else None
    return None


def evaluate(event: dict) -> tuple[int, str]:
    """Return (exit_code, stderr_message). Pure function for testing."""
    if event.get("tool_name") not in WRITE_TOOLS:
        return 0, ""
    tool_input = event.get("tool_input") or {}
    patched = re.findall(r"^\*\*\* (?:Add File|Update File|Move to): (.+?)\s*$",
                         str(tool_input.get("command") or ""), re.M)
    raw_path = tool_input.get("file_path") or next(iter(patched), "")
    if not raw_path:
        return 0, ""
    cwd = (event.get("cwd") or ".").replace("\\", "/")
    target = Path(raw_path)
    if not target.is_absolute():
        target = Path(cwd) / target
    if not _is_manuscript_md(str(target)) or not target.is_file():
        return 0, ""

    lint = _load_lint()
    forbidden = lint.load_forbidden_terms(project_terminology(target) or lint.TERMINOLOGY_FILE)
    issues = lint.lint_file(target, forbidden)

    term_lines = [
        f"[{code}] line {line}: {message}" for code, _p, line, message in issues[:MAX_LINES]
    ]
    style_lines = _style_metric_lines(target) + _overclaim_lines(target) + _academic_lines(target)
    if not term_lines and not style_lines:
        return 0, ""

    extra = (
        f"\n... and {len(issues) - MAX_LINES} more terminology"
        if len(issues) > MAX_LINES
        else ""
    )
    total = len(issues) + sum(1 for line in style_lines if line.startswith('['))
    msg = (
        f"Style lint on {target.name}: {total} finding(s) "
        f"(terminology, academic prose, style metrics vs Style Spec). Fix before finalizing:\n"
        + "\n".join(term_lines + style_lines)
        + extra
        + "\n"
    )
    return 2, msg


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")  # Claude Code emits UTF-8 JSON; Windows default is cp949
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

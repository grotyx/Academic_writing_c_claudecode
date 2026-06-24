from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "hooks" / "lint_on_edit.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_on_edit", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def event(cwd, tool: str = "Write", file_path: str = "drafts/04_methods.md") -> dict:
    return {"tool_name": tool, "cwd": str(cwd), "tool_input": {"file_path": file_path}}


class LintOnEditTests(unittest.TestCase):
    def test_flags_lint_issue_in_draft_section(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts"
            drafts.mkdir()
            (drafts / "04_methods.md").write_text(
                "The [TODO] result was dramatic.\n", encoding="utf-8"
            )
            code, msg = m.evaluate(event(tmp, file_path="drafts/04_methods.md"))
        self.assertEqual(code, 2)
        self.assertIn("PLACEHOLDER", msg)

    def test_clean_draft_returns_zero(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts"
            drafts.mkdir()
            (drafts / "04_methods.md").write_text(
                "The study enrolled adults and recorded outcomes.\n", encoding="utf-8"
            )
            code, msg = m.evaluate(event(tmp, file_path="drafts/04_methods.md"))
        self.assertEqual(code, 0)
        self.assertEqual(msg, "")

    def test_ignores_draft_plan_and_non_drafts(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts"
            drafts.mkdir()
            (drafts / "draft_plan.md").write_text("dramatic [TODO]\n", encoding="utf-8")
            self.assertEqual(
                m.evaluate(event(tmp, file_path="drafts/draft_plan.md")), (0, "")
            )
            (Path(tmp) / "README.md").write_text("dramatic [TODO]\n", encoding="utf-8")
            self.assertEqual(m.evaluate(event(tmp, file_path="README.md")), (0, ""))

    def test_ignores_non_write_tools(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "drafts").mkdir()
            self.assertEqual(
                m.evaluate(event(tmp, tool="Read", file_path="drafts/04_methods.md")),
                (0, ""),
            )

    def test_multiedit_flags_lint_issue_in_draft_section(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts"
            drafts.mkdir()
            (drafts / "04_methods.md").write_text(
                "The [TODO] result was dramatic.\n", encoding="utf-8"
            )
            code, msg = m.evaluate(event(tmp, tool="MultiEdit", file_path="drafts/04_methods.md"))
        self.assertEqual(code, 2)
        self.assertIn("PLACEHOLDER", msg)

    def test_fails_open_on_garbage(self) -> None:
        m = load_module()
        self.assertEqual(m.evaluate({}), (0, ""))


if __name__ == "__main__":
    unittest.main()

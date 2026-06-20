from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "hooks" / "enforce_gates.py"


def load_module():
    spec = importlib.util.spec_from_file_location("enforce_gates", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def event(cwd, tool: str = "Write", file_path: str = "drafts/04_methods.md") -> dict:
    return {"tool_name": tool, "cwd": str(cwd), "tool_input": {"file_path": file_path}}


class DecideTests(unittest.TestCase):
    def test_blocks_section_without_draft_plan(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "drafts").mkdir()
            reason = m.decide(event(tmp, file_path="drafts/04_methods.md"))
            self.assertIsNotNone(reason)
            self.assertIn("Rule 8", reason)

    def test_allows_section_with_draft_plan(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts"
            drafts.mkdir()
            (drafts / "draft_plan.md").write_text("x", encoding="utf-8")
            self.assertIsNone(m.decide(event(tmp, file_path="drafts/04_methods.md")))

    def test_allows_draft_plan_file_itself(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "drafts").mkdir()
            self.assertIsNone(m.decide(event(tmp, file_path="drafts/draft_plan.md")))

    def test_allows_non_write_tools(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(
                m.decide(event(tmp, tool="Read", file_path="drafts/04_methods.md"))
            )

    def test_skips_revision_sections(self) -> None:
        # Revisions (Phase 8) revise an existing manuscript; not gated by draft_plan.
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "drafts" / "revision" / "REV1").mkdir(parents=True)
            self.assertIsNone(
                m.decide(event(tmp, file_path="drafts/revision/REV1/04_methods_REV1.md"))
            )

    def test_multipaper_subfolder_plan(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            paper = Path(tmp) / "drafts" / "paper1_x"
            paper.mkdir(parents=True)
            self.assertIn(
                "Rule 8", m.decide(event(tmp, file_path="drafts/paper1_x/04_methods.md"))
            )
            (paper / "draft_plan.md").write_text("x", encoding="utf-8")
            self.assertIsNone(m.decide(event(tmp, file_path="drafts/paper1_x/04_methods.md")))

    def test_blocks_analysis_script_without_plan(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "data" / "py").mkdir(parents=True)
            reason = m.decide(event(tmp, file_path="data/py/01_descriptive.py"))
            self.assertIsNotNone(reason)
            self.assertIn("Rule 7", reason)

    def test_allows_analysis_script_with_plan(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            (data / "py").mkdir(parents=True)
            (data / "analysis_plan.md").write_text("x", encoding="utf-8")
            self.assertIsNone(m.decide(event(tmp, file_path="data/py/01_descriptive.py")))

    def test_fails_open_on_garbage(self) -> None:
        m = load_module()
        self.assertIsNone(m.decide({}))
        self.assertIsNone(m.decide({"tool_name": "Write", "tool_input": {}}))


if __name__ == "__main__":
    unittest.main()

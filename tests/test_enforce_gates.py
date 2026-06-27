from __future__ import annotations

import importlib.util
import os
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

    def test_blocks_section_with_relative_cwd(self) -> None:
        # Regression: a relative/missing cwd normalizes the target to
        # "drafts/04_methods.md" (no leading slash). The plan-first gate must
        # still fire -- it previously FAILED OPEN because "/drafts/" did not match.
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "drafts").mkdir()  # no draft_plan.md
            prev = os.getcwd()
            try:
                os.chdir(tmp)
                reason = m.decide(
                    {
                        "tool_name": "Write",
                        "cwd": ".",  # relative
                        "tool_input": {"file_path": "drafts/04_methods.md"},
                    }
                )
                self.assertIsNotNone(reason)
                self.assertIn("Rule 8", reason)
            finally:
                os.chdir(prev)

    def test_allows_section_with_draft_plan(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts"
            drafts.mkdir()
            (drafts / "draft_plan.md").write_text(
                "# Draft Plan\n\n## 1. Key Message\nA focused approved plan.\n\n"
                "- [x] 사용자 승인 완료\n",
                encoding="utf-8",
            )
            self.assertIsNone(m.decide(event(tmp, file_path="drafts/04_methods.md")))

    def test_blocks_section_with_unresolved_draft_plan_template(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts"
            drafts.mkdir()
            (drafts / "draft_plan.md").write_text(
                "# Draft Plan\n\n## 1. Key Message\n[작성]\n\n- [ ] 사용자 승인 완료\n",
                encoding="utf-8",
            )
            reason = m.decide(event(tmp, file_path="drafts/04_methods.md"))
            self.assertIsNotNone(reason)
            self.assertIn("unresolved template", reason)

    def test_allows_draft_plan_with_literal_citation_style_brackets(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts"
            drafts.mkdir()
            (drafts / "draft_plan.md").write_text(
                "# Draft Plan\n\nCitation style: bracket [N], 6 authors then et al.\n\n"
                "- [x] 사용자 승인 완료\n",
                encoding="utf-8",
            )
            self.assertIsNone(m.decide(event(tmp, file_path="drafts/04_methods.md")))

    def test_multiedit_blocks_section_without_draft_plan(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "drafts").mkdir()
            reason = m.decide(event(tmp, tool="MultiEdit", file_path="drafts/04_methods.md"))
            self.assertIsNotNone(reason)
            self.assertIn("Rule 8", reason)

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
            (data / "analysis_plan.md").write_text(
                "# Analysis Plan\n\nResearch question: compare treatment groups.\n\n"
                "- [x] 사용자 승인 완료\n",
                encoding="utf-8",
            )
            self.assertIsNone(m.decide(event(tmp, file_path="data/py/01_descriptive.py")))

    def test_allows_completed_analysis_plan_with_nonplaceholder_brackets(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            (data / "py").mkdir(parents=True)
            (data / "analysis_plan.md").write_text(
                "# Analysis Plan\n\nExpected sample size: [N=120]. Report median [IQR].\n\n"
                "- [x] 사용자 승인 완료\n",
                encoding="utf-8",
            )
            self.assertIsNone(m.decide(event(tmp, file_path="data/py/01_descriptive.py")))

    def test_blocks_analysis_script_with_unresolved_template_plan(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            (data / "py").mkdir(parents=True)
            (data / "analysis_plan.md").write_text(
                "# Analysis Plan\n\n- [연구 질문을 구체적으로 기술]\n"
                "- [ ] **사용자 승인 완료** -> 분석 진행\n",
                encoding="utf-8",
            )
            reason = m.decide(event(tmp, file_path="data/py/01_descriptive.py"))
            self.assertIsNotNone(reason)
            self.assertIn("unresolved template", reason)

    def test_blocks_analysis_plan_with_sample_size_placeholder(self) -> None:
        m = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp) / "data"
            (data / "py").mkdir(parents=True)
            (data / "analysis_plan.md").write_text(
                "# Analysis Plan\n\n**Expected Sample Size:** [N]\n\n"
                "- [x] 사용자 승인 완료\n",
                encoding="utf-8",
            )
            reason = m.decide(event(tmp, file_path="data/py/01_descriptive.py"))
            self.assertIsNotNone(reason)
            self.assertIn("unresolved template", reason)

    def test_fails_open_on_garbage(self) -> None:
        m = load_module()
        self.assertIsNone(m.decide({}))
        self.assertIsNone(m.decide({"tool_name": "Write", "tool_input": {}}))


if __name__ == "__main__":
    unittest.main()

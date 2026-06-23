from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "hooks" / "session_contract.py"


def load_module():
    spec = importlib.util.spec_from_file_location("session_contract", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class StyleSpecAddendumTests(unittest.TestCase):
    def setUp(self) -> None:
        self.m = load_module()

    def test_empty_when_no_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "drafts").mkdir()
            self.assertEqual(self.m.style_spec_addendum(Path(tmp)), "")

    def test_no_drafts_dir_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(self.m.style_spec_addendum(Path(tmp)), "")

    def test_surfaces_spec_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts"
            drafts.mkdir()
            (drafts / "style_spec.md").write_text("# Style Spec\n", encoding="utf-8")
            out = self.m.style_spec_addendum(Path(tmp))
        self.assertIn("Style Spec", out)
        self.assertIn("drafts/style_spec.md", out)

    def test_finds_multipaper_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp) / "drafts" / "paper1_x"
            sub.mkdir(parents=True)
            (sub / "style_spec.md").write_text("# Style Spec\n", encoding="utf-8")
            out = self.m.style_spec_addendum(Path(tmp))
        self.assertIn("paper1_x/style_spec.md", out)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "lint_manuscript.py"


def load_module():
    spec = importlib.util.spec_from_file_location("lint_manuscript", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class IterMarkdownFilesTests(unittest.TestCase):
    def test_skips_nonexistent_md_path(self) -> None:
        # Regression: a nonexistent .md argument must be skipped, not appended
        # (which later crashed lint_file with FileNotFoundError).
        module = load_module()
        self.assertEqual(module.iter_markdown_files([Path("does_not_exist_xyz.md")]), [])

    def test_collects_real_file_and_directory(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "a.md").write_text("x\n", encoding="utf-8")
            (d / "b.md").write_text("y\n", encoding="utf-8")
            (d / "c.txt").write_text("z\n", encoding="utf-8")

            from_dir = module.iter_markdown_files([d])
            self.assertEqual([p.name for p in from_dir], ["a.md", "b.md"])

            from_file = module.iter_markdown_files([d / "a.md"])
            self.assertEqual([p.name for p in from_file], ["a.md"])


class LoadForbiddenTermsTests(unittest.TestCase):
    def test_parses_preferred_forbidden_table(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            reg = Path(tmp) / "terminology.md"
            reg.write_text(
                "| Preferred Term | Forbidden Terms | Notes |\n"
                "| --- | --- | --- |\n"
                "| compared with | compared to | use with |\n",
                encoding="utf-8",
            )
            forbidden = module.load_forbidden_terms(reg)
            self.assertEqual(forbidden.get("compared to"), "compared with")

    def test_missing_registry_returns_empty(self) -> None:
        module = load_module()
        self.assertEqual(module.load_forbidden_terms(Path("no_such_registry.md")), {})


class LintFileTests(unittest.TestCase):
    @staticmethod
    def _write(tmp: str, name: str, text: str) -> Path:
        path = Path(tmp) / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_flags_placeholder_and_overclaim(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "draft.md", "The [TODO] result was dramatic.\n")
            codes = {code for code, *_ in module.lint_file(path, {})}
            self.assertIn("PLACEHOLDER", codes)
            self.assertIn("OVERCLAIM", codes)

    def test_flags_forbidden_term(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "draft.md", "We use foobar here.\n")
            issues = module.lint_file(path, {"foobar": "preferred"})
            self.assertTrue(any(code == "TERMINOLOGY" for code, *_ in issues))

    def test_clean_text_has_no_issues(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            path = self._write(tmp, "draft.md", "The study enrolled adults and recorded outcomes.\n")
            self.assertEqual(module.lint_file(path, {}), [])


if __name__ == "__main__":
    unittest.main()

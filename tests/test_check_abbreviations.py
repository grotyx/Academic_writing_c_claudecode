from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_abbreviations.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_abbreviations", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def audit_text(module, tmp: Path, body_text: str, *, abstract_text: str | None = None, allow: set[str] | None = None):
    artifacts = []
    if abstract_text is not None:
        abstract = tmp / "02_abstract.md"
        abstract.write_text(abstract_text, encoding="utf-8")
        artifacts.append(abstract)
    body = tmp / "04_methods.md"
    body.write_text(body_text, encoding="utf-8")
    artifacts.append(body)
    return module.audit(artifacts, allow=module.DEFAULT_ALLOW | (allow or set()))


class AbbrevDetectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def _codes(self, issues) -> set[tuple[str, str]]:
        return {(issue.code, issue.abbrev) for issue in issues}

    def test_defined_then_used_is_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = audit_text(
                self.module, Path(tmp),
                "Pain was rated on a visual analogue scale (VAS). "
                "VAS scores improved. VAS remained stable at follow-up.\n",
            )
            self.assertEqual([i for i in issues if i.abbrev == "VAS"], [])

    def test_undefined_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = audit_text(self.module, Path(tmp), "ODI improved after surgery. ODI declined later.\n")
            self.assertIn(("ABBREV_UNDEFINED", "ODI"), self._codes(issues))

    def test_defined_after_use_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = audit_text(
                self.module, Path(tmp),
                "ODI improved. We measured the Oswestry disability index (ODI) at baseline. ODI declined.\n",
            )
            self.assertIn(("ABBREV_DEFINED_AFTER_USE", "ODI"), self._codes(issues))

    def test_redefined_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = audit_text(
                self.module, Path(tmp),
                "The visual analogue scale (VAS) was used. VAS improved and VAS stayed low. "
                "Later the visual analogue scale (VAS) was reused.\n",
            )
            self.assertIn(("ABBREV_REDEFINED", "VAS"), self._codes(issues))

    def test_single_use_advisory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = audit_text(
                self.module, Path(tmp),
                "The Oswestry disability index (ODI) was recorded. ODI was 20.\n",
            )
            self.assertIn(("ABBREV_SINGLE_USE", "ODI"), self._codes(issues))

    def test_allowlist_suppresses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            # CI/SD built-in; MRI via --allow equivalent.
            issues = audit_text(
                self.module, Path(tmp),
                "Mean difference 2.1 (95% CI 1.0-3.2), SD 4.1. MRI confirmed fusion. MRI was repeated.\n",
                allow={"MRI"},
            )
            self.assertEqual(issues, [])

    def test_plural_maps_to_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = audit_text(
                self.module, Path(tmp),
                "Patient-reported outcomes (PROs) were collected. PROs improved and PRO scores held.\n",
            )
            self.assertEqual([i for i in issues if i.abbrev == "PRO"], [])

    def test_numeric_suffix_supported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = audit_text(
                self.module, Path(tmp),
                "Quality of life was measured with the Short Form-36 (SF-36). "
                "SF-36 scores rose. SF-36 physical scores rose most.\n",
            )
            self.assertEqual([i for i in issues if i.abbrev == "SF-36"], [])

    def test_abstract_and_body_are_separate_scopes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = audit_text(
                self.module, Path(tmp),
                # body uses VAS without its own definition
                "VAS improved significantly. VAS stayed low.\n",
                abstract_text=(
                    "# Abstract\n\nPain was rated on a visual analogue scale (VAS). "
                    "VAS improved. VAS stayed low.\n\n**Keywords:** pain; spine; outcome\n"
                ),
            )
            codes = {(issue.code, issue.scope, issue.abbrev) for issue in issues}
            self.assertIn(("ABBREV_UNDEFINED", "body", "VAS"), codes)
            self.assertNotIn(("ABBREV_UNDEFINED", "abstract", "VAS"), codes)

    def test_headings_tables_comments_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            issues = audit_text(
                self.module, Path(tmp),
                "# METHODS\n\n| ODI | 20 |\n|---|---|\n<!-- BMI note -->\n\nPlain text only here.\n",
            )
            self.assertEqual(issues, [])


class AbbrevCliTests(unittest.TestCase):
    def _run(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            capture_output=True, text=True,
        )

    def test_advisory_default_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            body = Path(tmp) / "04_methods.md"
            body.write_text("ODI improved. ODI declined.\n", encoding="utf-8")
            proc = self._run([str(body)])
            self.assertEqual(proc.returncode, 0)
            self.assertIn("ABBREV_UNDEFINED", proc.stdout)

    def test_strict_fails_on_undefined(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            body = Path(tmp) / "04_methods.md"
            body.write_text("ODI improved. ODI declined.\n", encoding="utf-8")
            proc = self._run([str(body), "--strict"])
            self.assertEqual(proc.returncode, 1)

    def test_strict_ignores_single_use_and_allow_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            body = Path(tmp) / "04_methods.md"
            body.write_text(
                "The Oswestry disability index (ODI) was recorded. ODI was 20. BMI was noted. BMI rose.\n",
                encoding="utf-8",
            )
            proc = self._run([str(body), "--strict", "--allow", "BMI"])
            # SINGLE_USE for ODI is advisory; BMI allowed -> strict passes.
            self.assertEqual(proc.returncode, 0)
            self.assertIn("ABBREV_SINGLE_USE", proc.stdout)
            self.assertNotIn("BMI", proc.stdout)


if __name__ == "__main__":
    unittest.main()

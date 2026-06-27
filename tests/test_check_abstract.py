from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_abstract.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_abstract", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CheckAbstractTests(unittest.TestCase):
    def _files(self, tmp: Path, abstract: str, body: str):
        a = tmp / "02_abstract.md"
        a.write_text(abstract, encoding="utf-8")
        b = tmp / "05_results.md"
        b.write_text(body, encoding="utf-8")
        return a, [b]

    def test_passes_when_abstract_numbers_appear_in_body(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            a, body = self._files(
                Path(tmp),
                abstract="We enrolled 120 patients; the mean score was 54.3.\n",
                body="A total of 120 patients were analyzed. The mean score reached 54.32.\n",
            )
            result = module.check_abstract(a, body)
            self.assertTrue(result.passed, [i.number for i in result.issues])
            self.assertGreaterEqual(result.checked, 2)

    def test_flags_abstract_only_number(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            a, body = self._files(
                Path(tmp),
                abstract="Improvement was 88 percent in the cohort of 120.\n",
                body="A total of 120 patients were analyzed.\n",  # 88 never appears
            )
            result = module.check_abstract(a, body)
            self.assertFalse(result.passed)
            self.assertEqual([i.number for i in result.issues], ["88"])

    def test_rounding_tolerance_matches_body(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            a, body = self._files(
                Path(tmp),
                abstract="The mean was 54.3.\n",
                body="Mean value 54.34 was recorded.\n",  # rounds to 54.3
            )
            self.assertTrue(module.check_abstract(a, body).passed)

    def test_p_values_excluded_by_default(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            # abstract p<0.001 not echoed in body, but p-values excluded by default
            a, body = self._files(
                Path(tmp),
                abstract="The difference was significant (p<0.001), n=40.\n",
                body="A total of 40 patients.\n",
            )
            self.assertTrue(module.check_abstract(a, body).passed)
            # with --include-p-values it is now required and missing
            self.assertFalse(module.check_abstract(a, body, include_p_values=True).passed)

    def test_format_fail_lists_missing(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            a, body = self._files(
                Path(tmp),
                abstract="Effect size was 2.5 in 30 patients.\n",
                body="We studied 30 patients.\n",
            )
            result = module.check_abstract(a, body)
            out = module.format_result(result, a)
            self.assertIn("GATE FAIL", out)
            self.assertIn("Abstract-Body-Consistency", out)
            self.assertIn("2.5", out)

    def test_abstract_more_precise_than_body_fails(self) -> None:
        # body_supports rounds the BODY value to the abstract's decimal count.
        # Abstract "54.32" (2 dp) vs body "54.3" -> round(54.3, 2) == 54.3 != 54.32
        # so the abstract number is not supported and the check FAILS.
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            a, body = self._files(
                Path(tmp),
                abstract="The mean was 54.32.\n",
                body="Mean value 54.3 was recorded.\n",
            )
            result = module.check_abstract(a, body)
            self.assertFalse(result.passed)
            self.assertEqual([i.number for i in result.issues], ["54.32"])

    def test_integer_abstract_number_supported_by_identical_body_integer(self) -> None:
        # An integer (0 decimals) abstract value is supported by the same body integer.
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            a, body = self._files(
                Path(tmp),
                abstract="We enrolled 120 patients.\n",
                body="A total of 120 patients were analyzed.\n",
            )
            result = module.check_abstract(a, body)
            self.assertTrue(result.passed, [i.number for i in result.issues])
            self.assertEqual(result.checked, 1)

    def test_body_supports_aggregates_across_multiple_files(self) -> None:
        # Two abstract numbers each live in a different body file; the body token
        # pool is the union of all body_paths, so both are supported.
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            a = tmpdir / "02_abstract.md"
            a.write_text("Enrolled 120 patients; improvement reached 88 percent.\n", encoding="utf-8")
            methods = tmpdir / "04_methods.md"
            methods.write_text("A total of 120 patients were analyzed.\n", encoding="utf-8")
            results = tmpdir / "05_results.md"
            results.write_text("Functional improvement reached 88 percent overall.\n", encoding="utf-8")

            result = module.check_abstract(a, [methods, results])
            self.assertTrue(result.passed, [i.number for i in result.issues])
            self.assertEqual(result.checked, 2)

            # Removing the file that carries 88 leaves it unsupported -> FAIL.
            partial = module.check_abstract(a, [methods])
            self.assertFalse(partial.passed)
            self.assertEqual([i.number for i in partial.issues], ["88"])

    def test_flagged_pvalue_inequality_keeps_comparator_in_issue_number(self) -> None:
        # When a p-value token is checked (--include-p-values) and absent from the
        # body, the issue.number prepends the comparator ("<0.001"), since the
        # NUMBER_RE only captures a comparator on a p-prefixed token.
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            a, body = self._files(
                Path(tmp),
                abstract="The difference was significant (p<0.001), n=40.\n",
                body="A total of 40 patients were analyzed.\n",  # no p-value echoed
            )
            result = module.check_abstract(a, body, include_p_values=True)
            self.assertFalse(result.passed)
            self.assertEqual([i.number for i in result.issues], ["<0.001"])
            out = module.format_result(result, a)
            self.assertIn("number: <0.001", out)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_numbers.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_numbers", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class CheckNumbersTests(unittest.TestCase):
    def test_load_result_numbers_extracts_values_from_csv_cells(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            results_dir = Path(tmp) / "results"
            results_dir.mkdir()
            (results_dir / "table2_outcomes.csv").write_text(
                "endpoint,mean,sd,p_value\n"
                "primary,54.32,12.14,0.0004\n",
                encoding="utf-8",
            )

            numbers = module.load_result_numbers(results_dir)
            values = sorted(number.value for number in numbers)

            self.assertEqual(values, [0.0004, 12.14, 54.32])
            self.assertEqual(numbers[0].source.name, "table2_outcomes.csv")

    def test_check_numbers_passes_when_artifact_number_rounds_to_csv_value(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            (results_dir / "table2_outcomes.csv").write_text(
                "endpoint,treatment_mean\nprimary,54.32\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "The treatment group improved by 54.3 points at follow-up.",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertTrue(result.passed)
            self.assertEqual(result.failures, [])
            self.assertEqual(result.checked_numbers, 1)

    def test_check_numbers_keeps_sentence_final_result_numbers(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            (results_dir / "table2_outcomes.csv").write_text(
                "endpoint,treatment_mean\nprimary,54.32\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "The mean improvement was 54.3.",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertTrue(result.passed)
            self.assertEqual(result.checked_numbers, 1)

    def test_check_numbers_fails_unmatched_number(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            (results_dir / "table2_outcomes.csv").write_text(
                "endpoint,treatment_mean\nprimary,54.32\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "The treatment group improved by 55.1 points at follow-up.",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertFalse(result.passed)
            self.assertEqual(result.failures[0].number, "55.1")
            self.assertIn("not found in results", result.failures[0].reason)

    def test_check_numbers_allows_p_less_than_threshold_when_csv_value_is_below_threshold(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            (results_dir / "table2_outcomes.csv").write_text(
                "endpoint,p_value\nprimary,0.0004\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "The between-group difference was statistically significant (*p*<0.001).",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertTrue(result.passed)
            self.assertEqual(result.failures, [])

    def test_check_numbers_ignores_markdown_comments_placeholders_and_table_labels(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "table_1.md"
            (results_dir / "table1_demographics.csv").write_text(
                "variable,n\nsample_size,42\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "<!-- example: n=99 should not be checked -->\n"
                "Table 1. Baseline characteristics\n"
                "| Variable | Group A |\n"
                "|---|---:|\n"
                "| Sample size | n=XX |\n",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertTrue(result.passed)
            self.assertEqual(result.checked_numbers, 0)

    def test_check_numbers_matches_percentage_value(self) -> None:
        # Regression: a percentage like 42.5% must trace to 42.5 in the CSV and
        # must not crash the script (float("42.5%") previously raised ValueError).
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            (results_dir / "table2_outcomes.csv").write_text(
                "endpoint,rate\nprimary,42.5\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "The response rate was 42.5% in the treatment group.",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertTrue(result.passed)
            self.assertEqual(result.failures, [])

    def test_check_numbers_rejects_pvalue_backed_only_by_unrelated_value(self) -> None:
        # Regression: *p*<0.001 must NOT pass just because some unrelated number
        # (here a count of 0) happens to satisfy the inequality.
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            (results_dir / "table2_outcomes.csv").write_text(
                "endpoint,event_count\nprimary,0\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "The between-group difference was significant (*p*<0.001).",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertFalse(result.passed)

    def test_check_numbers_matches_thousands_separator(self) -> None:
        # Regression: "1,234" must trace to 1234 in the CSV instead of being
        # tokenized into "1" and "234".
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            (results_dir / "table1_demographics.csv").write_text(
                "variable,n\nenrolled,1234\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "A total of 1,234 patients were enrolled.",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertTrue(result.passed)
            self.assertEqual(result.checked_numbers, 1)

    def test_check_numbers_ignores_iso_dates_in_prose(self) -> None:
        # Regression: ISO dates in prose must not be read as result numbers; only
        # the genuine result value (42) should be checked.
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "04_methods.md"
            (results_dir / "table1_demographics.csv").write_text(
                "variable,n\nanalyzed,42\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "Patients enrolled between 2020-01-01 and 2026-06-18 were assessed; "
                "42 were analyzed.",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertTrue(result.passed)
            self.assertEqual(result.checked_numbers, 1)

    def test_check_numbers_ignores_inline_code_spans(self) -> None:
        # Numbers inside inline `code` spans are illustrative and must be ignored.
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            (results_dir / "table1_demographics.csv").write_text(
                "variable,n\nanalyzed,42\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "The placeholder `n=99` is illustrative; 42 patients were analyzed.",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertTrue(result.passed)
            self.assertEqual(result.checked_numbers, 1)

    def test_check_numbers_flags_empty_results_directory(self) -> None:
        # A missing/empty results set must be reported clearly, not as a wall of
        # "not found" failures with no explanation.
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            artifact.write_text("The mean improvement was 54.3 points.", encoding="utf-8")

            result = module.check_numbers([artifact], results_dir=results_dir)
            output = module.format_result(result, [artifact], results_dir)

            self.assertFalse(result.passed)
            self.assertIn("no result numbers", output.lower())

    def test_check_numbers_ignores_confidence_level_percentage(self) -> None:
        # "95% CI" states the confidence level, not a result value; only the
        # interval bounds and other genuine results should be checked.
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            (results_dir / "table2_outcomes.csv").write_text(
                "metric,value,ci_low,ci_high\ndiff,8.7,3.2,14.2\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "The mean difference was 8.7 (95% CI 3.2 to 14.2).",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertTrue(result.passed)
            self.assertNotIn("95", [failure.number for failure in result.failures])
            self.assertEqual(result.checked_numbers, 3)

    def test_check_numbers_ignores_hyphenated_time_spans(self) -> None:
        # "90-day", "36-month", "5-year" are time-point modifiers, not result
        # values; only the genuine result (the rate) should be checked.
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            (results_dir / "table2_outcomes.csv").write_text(
                "metric,value\nreadmission,11.0\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "The 90-day readmission rate was 11.0% over 36-month follow-up.",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertTrue(result.passed)
            self.assertNotIn("90", [failure.number for failure in result.failures])
            self.assertNotIn("36", [failure.number for failure in result.failures])
            self.assertEqual(result.checked_numbers, 1)

    def test_check_numbers_validates_pvalue_without_leading_zero(self) -> None:
        # APA / journal style omits the leading zero ("p<.001"). The value must
        # still be parsed and validated, not silently skipped. With no
        # supporting p-value in results, this must FAIL (not pass vacuously).
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            results_dir = root / "results"
            results_dir.mkdir()
            artifact = root / "05_results.md"
            (results_dir / "table1_demographics.csv").write_text(
                "variable,n\nsample,42\n",
                encoding="utf-8",
            )
            artifact.write_text(
                "The effect was statistically significant (*p*<.001).",
                encoding="utf-8",
            )

            result = module.check_numbers([artifact], results_dir=results_dir)

            self.assertFalse(result.passed)
            self.assertIn(".001", [failure.number for failure in result.failures])


if __name__ == "__main__":
    unittest.main()

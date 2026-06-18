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


if __name__ == "__main__":
    unittest.main()

"""End-to-end gate tests over a realistic manuscript corpus.

Unit tests only exercise inputs the author thought of. These tests instead run
the actual gate scripts over a Results section written the way real medical
manuscripts are — percentages, mean ± SD, 95% CI ranges, p<0.001 / p=0.012,
thousands separators, ISO date ranges, structural Table refs, and an
inline-code placeholder — to confirm the harness passes realistic input and
still catches an unsupported value.
"""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


RESULTS_MD = """# Results

A total of 1,234 patients were enrolled between 2020-01-01 and 2026-06-18, and
1,180 completed follow-up. Mean age was 54.3 ± 12.1 years, and 42.5% were
female (Table 1).

The treatment group improved more than control (mean difference 8.7 points,
95% CI 3.2 to 14.2; *p*<0.001). The response rate was 68.4% versus 45.2%
(*p*=0.012). The adjusted odds ratio was 2.34 (95% CI 1.45 to 3.78), shown in
Table 2. The macro `n=99` is illustrative only.
"""

TABLE1_CSV = (
    "variable,value\n"
    "enrolled,1234\n"
    "completed,1180\n"
    "age_mean,54.3\n"
    "age_sd,12.1\n"
    "female_pct,42.5\n"
)

TABLE2_CSV = (
    "metric,value,ci_low,ci_high,p_value\n"
    "mean_diff,8.7,3.2,14.2,0.0008\n"
    "response_treatment,68.4,,,0.012\n"
    "response_control,45.2,,,\n"
    "odds_ratio,2.34,1.45,3.78,\n"
)


RESULTS_MD_EXTENDED = """# Results

Median follow-up was 5 years (IQR 2 to 8). The 90-day readmission rate was
11.0%, and 36-month survival was 82.0%. The mean change from baseline was
-2.1 points (SD 3.4).

The hazard ratio was 1.23 (95% CI 0.98 to 1.54; *p*=0.071), and the adjusted
odds ratio was 0.85 (95% CI 0.72 to 1.01). A total of n = 1,234 patients with
a median age of 63 years contributed data.
"""

EXTENDED_CSV = (
    "metric,value,low,high,p_value\n"
    "followup_years,5,,,\n"
    "iqr,,2,8,\n"
    "readmission_rate,11.0,,,\n"
    "survival,82.0,,,\n"
    "mean_change,-2.1,,,\n"
    "sd,3.4,,,\n"
    "hazard_ratio,1.23,0.98,1.54,0.071\n"
    "odds_ratio,0.85,0.72,1.01,\n"
    "n_total,1234,,,\n"
    "age_median,63,,,\n"
)


class NumbersE2ETests(unittest.TestCase):
    def _run(self, manuscript: str, table1: str = TABLE1_CSV, table2: str = TABLE2_CSV):
        module = _load("check_numbers")
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        results = root / "results"
        results.mkdir()
        (results / "table1_demographics.csv").write_text(table1, encoding="utf-8")
        (results / "table2_outcomes.csv").write_text(table2, encoding="utf-8")
        artifact = root / "05_results.md"
        artifact.write_text(manuscript, encoding="utf-8")
        return module.check_numbers([artifact], results_dir=results)

    def test_realistic_results_section_passes(self) -> None:
        result = self._run(RESULTS_MD)
        # Every result-like number traces to the CSVs; nothing should fail.
        self.assertEqual([failure.number for failure in result.failures], [])
        self.assertTrue(result.passed)
        self.assertGreaterEqual(result.checked_numbers, 12)

    def test_one_unsupported_number_is_caught(self) -> None:
        manuscript = RESULTS_MD.replace(
            "The adjusted odds ratio was 2.34",
            "The adjusted odds ratio was 9.99",
        )
        result = self._run(manuscript)
        self.assertFalse(result.passed)
        self.assertIn("9.99", [failure.number for failure in result.failures])

    def test_extended_corpus_passes(self) -> None:
        # Broader idioms: hyphenated time spans (90-day, 36-month), spaced
        # durations/ages (5 years, 63 years), IQR range, negative change, SD,
        # hazard/odds ratios with CI and p-value, and a thousands separator.
        result = self._run(
            RESULTS_MD_EXTENDED,
            table1=EXTENDED_CSV,
            table2="metric,value\n",
        )
        self.assertEqual([failure.number for failure in result.failures], [])
        self.assertTrue(result.passed)


class CitationsE2ETests(unittest.TestCase):
    EVIDENCE = (
        "# Evidence Registry\n\n## Reference List\n\n"
        "### [1] Smith et al., 2020\n"
        "- **Evidence ID:** smith_2020\n"
        "- **Source Status:** verified\n\n"
        "### [2] Lee et al., 2021\n"
        "- **Evidence ID:** lee_2021\n"
        "- **Source Status:** verified\n"
    )

    def _run(self, manuscript: str):
        module = _load("check_citations")
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        evidence = root / "evidence.md"
        evidence.write_text(self.EVIDENCE, encoding="utf-8")
        artifact = root / "03_introduction.md"
        artifact.write_text(manuscript, encoding="utf-8")
        return module.check_citations([artifact], evidence_path=evidence)

    def test_registered_citations_pass(self) -> None:
        result = self._run(
            "Prior trials support this approach [EVID:smith_2020], and a recent "
            "cohort agrees [EVID:lee_2021]."
        )
        self.assertTrue(result.passed)
        self.assertEqual(result.checked_tokens, 2)

    def test_unregistered_citation_is_caught(self) -> None:
        result = self._run("This claim is unsupported [EVID:ghost_9999].")
        self.assertFalse(result.passed)
        self.assertEqual(result.failures[0].citation_id, "ghost_9999")


class GateE2ETests(unittest.TestCase):
    GATE = (
        "phase: Phase 4 - Draft Sections\n"
        "artifact: drafts/05_results.md\n"
        "status: PASS              # PASS | FAIL\n"
        "checks:\n"
        "  constraint: PASS\n"
        "  citation: PASS\n"
        "  numbers: PASS\n"
        "  logic: PASS\n"
        "round: 1                  # max 2 fix/re-verify attempts\n"
    )

    def test_draft_gate_ledger_passes(self) -> None:
        module = _load("check_gate")
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        gate = Path(tmp.name) / "phase_04_draft.GATE.md"
        gate.write_text(self.GATE, encoding="utf-8")
        result = module.check_gate(
            gate,
            required_checks=["constraint", "citation", "numbers", "logic"],
            artifact="drafts/05_results.md",
        )
        self.assertTrue(result.passed)


if __name__ == "__main__":
    unittest.main()

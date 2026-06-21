from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_style.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_style", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class MetricsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cs = load_module()

    def test_basic_metrics(self) -> None:
        m = self.cs.compute_metrics(
            "The patients were enrolled. Outcomes were recorded at one year."
        )
        self.assertEqual(m["word_count"], 10)
        self.assertEqual(m["sentence_count"], 2)
        self.assertEqual(m["mean_sentence_length"], 5.0)
        self.assertEqual(m["paragraph_count"], 1)

    def test_citation_density(self) -> None:
        m = self.cs.compute_metrics("Prior work supports this [EVID:smith_2020]. Others agree [1,2].")
        self.assertEqual(m["citation_density"], 2.0)

    def test_hedging(self) -> None:
        m = self.cs.compute_metrics("This may suggest a benefit. Results possibly indicate improvement.")
        self.assertEqual(m["hedging_per_100w"], 44.44)

    def test_decimals_not_split(self) -> None:
        m = self.cs.compute_metrics("The mean was 10.5 units across the cohort overall.")
        self.assertEqual(m["sentence_count"], 1)


class SpecAndCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cs = load_module()

    def _spec(self, tmp: str) -> Path:
        p = Path(tmp) / "style_spec.md"
        p.write_text(
            "## Target Metrics\n"
            "| Section | Word count | Mean sentence length | Paragraphs |\n"
            "|---|---:|---:|---:|\n"
            "| Introduction | 600 | 22 | 5 |\n"
            "| Methods | 800 | 20 | 6 |\n",
            encoding="utf-8",
        )
        return p

    def test_parse_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            targets = self.cs.parse_spec_targets(self._spec(tmp))
        self.assertEqual(targets["introduction"]["word_count"], 600)
        self.assertEqual(targets["methods"]["paragraph_count"], 6)

    def test_section_of(self) -> None:
        self.assertEqual(self.cs.section_of(Path("03_introduction.md")), "introduction")
        self.assertEqual(self.cs.section_of(Path("05_results.md")), "results")
        self.assertIsNone(self.cs.section_of(Path("table_1.md")))

    def test_check_file_flags_deviation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            intro = Path(tmp) / "03_introduction.md"
            intro.write_text("Short intro with very few words here.\n", encoding="utf-8")
            _m, issues = self.cs.check_file(intro, {"introduction": {"word_count": 600.0}})
        self.assertTrue(any("word_count" in i for i in issues))

    def test_check_file_within_tolerance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            intro = Path(tmp) / "03_introduction.md"
            intro.write_text("Short intro with very few words here.\n", encoding="utf-8")
            _m, issues = self.cs.check_file(intro, {"introduction": {"word_count": 7.0}})
        self.assertEqual(issues, [])

    def test_nearest_spec(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts"
            drafts.mkdir()
            (drafts / "style_spec.md").write_text("# s\n", encoding="utf-8")
            section = drafts / "03_introduction.md"
            section.write_text("x\n", encoding="utf-8")
            self.assertEqual(self.cs.nearest_spec(section), (drafts / "style_spec.md").resolve())

    def test_nearest_spec_multipaper(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sub = Path(tmp) / "drafts" / "paper1_x"
            sub.mkdir(parents=True)
            (sub / "style_spec.md").write_text("# s\n", encoding="utf-8")
            section = sub / "03_introduction.md"
            section.write_text("x\n", encoding="utf-8")
            self.assertEqual(self.cs.nearest_spec(section), (sub / "style_spec.md").resolve())

    def test_nearest_spec_absent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            drafts = Path(tmp) / "drafts"
            drafts.mkdir()
            section = drafts / "03_introduction.md"
            section.write_text("x\n", encoding="utf-8")
            self.assertIsNone(self.cs.nearest_spec(section))


if __name__ == "__main__":
    unittest.main()

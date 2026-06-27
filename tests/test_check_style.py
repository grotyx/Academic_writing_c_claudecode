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

    def test_check_file_flags_mean_sentence_length_deviation(self) -> None:
        # Two 12-word sentences -> mean_sentence_length 12; target 5 -> deviation
        # abs(12-5)=7 > 0.25*5=1.25, so it must be flagged.
        with tempfile.TemporaryDirectory() as tmp:
            intro = Path(tmp) / "03_introduction.md"
            intro.write_text(
                "one two three four five six seven eight nine ten eleven twelve. "
                "one two three four five six seven eight nine ten eleven twelve.\n",
                encoding="utf-8",
            )
            metrics, issues = self.cs.check_file(intro, {"introduction": {"mean_sentence_length": 5.0}})
        self.assertEqual(metrics["mean_sentence_length"], 12.0)
        self.assertTrue(any("mean_sentence_length" in i for i in issues), issues)

    def test_check_file_mean_sentence_length_within_tolerance(self) -> None:
        # mean_sentence_length 12 vs target 11 -> abs(12-11)=1 <= 0.25*11=2.75 -> no issue.
        with tempfile.TemporaryDirectory() as tmp:
            intro = Path(tmp) / "03_introduction.md"
            intro.write_text(
                "one two three four five six seven eight nine ten eleven twelve. "
                "one two three four five six seven eight nine ten eleven twelve.\n",
                encoding="utf-8",
            )
            _m, issues = self.cs.check_file(intro, {"introduction": {"mean_sentence_length": 11.0}})
        self.assertEqual([i for i in issues if "mean_sentence_length" in i], [])

    def test_check_file_flags_paragraph_count_deviation(self) -> None:
        # _strip_markup collapses blank lines, so a prose section measures as 1
        # paragraph. Target 5 -> abs(1-5)=4 > 0.34*5=1.7 -> flagged.
        with tempfile.TemporaryDirectory() as tmp:
            intro = Path(tmp) / "03_introduction.md"
            intro.write_text("A single short paragraph of prose with several words here.\n", encoding="utf-8")
            metrics, issues = self.cs.check_file(intro, {"introduction": {"paragraph_count": 5.0}})
        self.assertEqual(metrics["paragraph_count"], 1)
        self.assertTrue(any("paragraph_count" in i for i in issues), issues)

    def test_check_file_paragraph_count_boundary_just_over_34_percent(self) -> None:
        # actual 1 vs target 1.6 -> abs(1-1.6)=0.6 > 0.34*1.6=0.544 -> flagged;
        # vs target 1.4 -> abs(1-1.4)=0.4 <= 0.34*1.4=0.476 -> not flagged.
        with tempfile.TemporaryDirectory() as tmp:
            intro = Path(tmp) / "03_introduction.md"
            intro.write_text("A single short paragraph of prose with several words here.\n", encoding="utf-8")
            _m, over = self.cs.check_file(intro, {"introduction": {"paragraph_count": 1.6}})
            _m2, under = self.cs.check_file(intro, {"introduction": {"paragraph_count": 1.4}})
        self.assertTrue(any("paragraph_count" in i for i in over), over)
        self.assertEqual([i for i in under if "paragraph_count" in i], [])


class SplitSentencesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cs = load_module()

    def test_does_not_split_on_et_al(self) -> None:
        sents = self.cs.split_sentences("Smith et al. reported a benefit in adults. A second claim follows.")
        self.assertEqual(len(sents), 2)
        self.assertTrue(sents[0].startswith("Smith et al. reported"))

    def test_does_not_split_on_eg_and_ie(self) -> None:
        self.assertEqual(
            len(self.cs.split_sentences("We used a drug, e.g. aspirin, in all cases.")), 1
        )
        self.assertEqual(
            len(self.cs.split_sentences("The endpoint, i.e. mortality, was assessed.")), 1
        )

    def test_does_not_split_on_vs(self) -> None:
        self.assertEqual(len(self.cs.split_sentences("Group A vs. group B differed markedly.")), 1)

    def test_does_not_split_on_decimal(self) -> None:
        self.assertEqual(len(self.cs.split_sentences("The mean was 10.5 across the whole cohort.")), 1)

    def test_abbreviation_dots_are_restored_after_protection(self) -> None:
        # The <dot> placeholder must be converted back to a literal "." in output.
        sents = self.cs.split_sentences("Group A vs. group B differed.")
        self.assertIn("vs.", sents[0])
        self.assertNotIn("<dot>", sents[0])


if __name__ == "__main__":
    unittest.main()

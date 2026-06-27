from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "search_pubmed.py"


def load_module():
    spec = importlib.util.spec_from_file_location("search_pubmed", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class SearchPubmedFormattingTests(unittest.TestCase):
    def test_evidence_entry_includes_gate_required_identity_and_source_status(self) -> None:
        module = load_module()
        article = {
            "first_author": "Smith",
            "authors": ["Smith J", "Doe A"],
            "title": "Example randomized trial.",
            "journal_abbr": "Spine",
            "journal": "Spine",
            "year": "2020",
            "volume": "45",
            "issue": "2",
            "pages": "10-20",
            "doi": "10.1000/example",
            "pmid": "12345678",
            "pub_types": ["Randomized Controlled Trial"],
            "abstract": "Objective: test.",
        }

        entry = module.format_evidence_entry(article, 7)

        self.assertIn("- **Evidence ID:** smith_2020", entry)
        self.assertIn("- **Source Status:** abstract-only", entry)

    def test_evidence_entry_without_abstract_is_todo_source_status(self) -> None:
        module = load_module()
        article = {
            "first_author": "Lee",
            "authors": ["Lee J"],
            "title": "No abstract article.",
            "journal_abbr": "Spine J",
            "journal": "Spine Journal",
            "year": "2021",
            "volume": "",
            "issue": "",
            "pages": "",
            "doi": "",
            "pmid": "87654321",
            "pub_types": [],
            "abstract": "",
        }

        entry = module.format_evidence_entry(article, 8)

        self.assertIn("- **Evidence ID:** lee_2021", entry)
        self.assertIn("- **Source Status:** todo", entry)


class FormatCitationAuthorBranchesTests(unittest.TestCase):
    """Cover every author-count branch of format_citation (pure, no network)."""

    def _citation(self, authors):
        module = load_module()
        article = {
            "authors": authors,
            "title": "An example study.",
            "journal_abbr": "Spine",
            "journal": "Spine",
            "year": "2020",
        }
        return module.format_citation(article)

    def test_more_than_six_authors_truncates_with_et_al(self) -> None:
        # >6 authors -> first 6 joined, then ", et al."
        authors = [f"Author{i} X" for i in range(8)]
        citation = self._citation(authors)
        author_str = citation.split(". An example study")[0]
        self.assertEqual(
            author_str,
            "Author0 X, Author1 X, Author2 X, Author3 X, Author4 X, Author5 X, et al.",
        )

    def test_exactly_six_authors_listed_without_et_al(self) -> None:
        # 6 authors is NOT >6, so the 2-6 branch joins all of them, last with ", ".
        authors = [f"Author{i} X" for i in range(6)]
        citation = self._citation(authors)
        author_str = citation.split(". An example study")[0]
        self.assertNotIn("et al.", author_str)
        self.assertEqual(
            author_str,
            "Author0 X, Author1 X, Author2 X, Author3 X, Author4 X, Author5 X",
        )

    def test_two_to_six_authors_join_last_with_comma(self) -> None:
        citation = self._citation(["Smith J", "Doe A", "Roe B"])
        author_str = citation.split(". An example study")[0]
        self.assertEqual(author_str, "Smith J, Doe A, Roe B")

    def test_single_author_used_verbatim(self) -> None:
        citation = self._citation(["Smith J"])
        author_str = citation.split(". An example study")[0]
        self.assertEqual(author_str, "Smith J")

    def test_empty_authors_falls_back_to_unknown(self) -> None:
        citation = self._citation([])
        author_str = citation.split(". An example study")[0]
        self.assertEqual(author_str, "Unknown")


class GuessStudyDesignLadderTests(unittest.TestCase):
    """Cover every rung of the guess_study_design ladder (pure, no network)."""

    def setUp(self) -> None:
        self.module = load_module()

    def test_randomized_controlled_trial_is_rct(self) -> None:
        self.assertEqual(self.module.guess_study_design(["Randomized Controlled Trial"]), "RCT")

    def test_phase_clinical_trial_is_rct(self) -> None:
        # "clinical trial, phase" also resolves to RCT on the first rung.
        self.assertEqual(self.module.guess_study_design(["Clinical Trial, Phase III"]), "RCT")

    def test_meta_analysis(self) -> None:
        self.assertEqual(self.module.guess_study_design(["Meta-Analysis"]), "Meta-analysis")

    def test_systematic_review(self) -> None:
        self.assertEqual(self.module.guess_study_design(["Systematic Review"]), "Systematic Review")

    def test_plain_review(self) -> None:
        self.assertEqual(self.module.guess_study_design(["Review"]), "Review")

    def test_case_reports(self) -> None:
        self.assertEqual(self.module.guess_study_design(["Case Reports"]), "Case Report")

    def test_comparative_study(self) -> None:
        self.assertEqual(self.module.guess_study_design(["Comparative Study"]), "Comparative Study")

    def test_cohort_study(self) -> None:
        self.assertEqual(self.module.guess_study_design(["Cohort Studies"]), "Cohort Study")

    def test_unrecognized_pub_types_fall_back_to_todo(self) -> None:
        self.assertEqual(
            self.module.guess_study_design(["Journal Article"]),
            "[TODO - study type, n=?, follow-up period]",
        )

    def test_empty_pub_types_fall_back_to_todo(self) -> None:
        self.assertEqual(
            self.module.guess_study_design([]),
            "[TODO - study type, n=?, follow-up period]",
        )


if __name__ == "__main__":
    unittest.main()

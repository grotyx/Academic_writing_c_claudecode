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


if __name__ == "__main__":
    unittest.main()

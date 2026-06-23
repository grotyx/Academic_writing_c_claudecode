from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "extract_claims.py"


def load_module():
    spec = importlib.util.spec_from_file_location("extract_claims", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ExtractClaimsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.m = load_module()

    def test_splits_and_tags(self) -> None:
        text = (
            "## Discussion\n\n"
            "BED was equivalent to MD for ODI [EVID:park_2025]. "
            "It also reduced CPK [EVID:ham_2024]. "
            "This sentence has no citation.\n"
        )
        claims = self.m.extract_claims(text)
        self.assertEqual(len(claims), 2)
        self.assertEqual(claims[0]["ids"], ["park_2025"])
        self.assertEqual(claims[1]["ids"], ["ham_2024"])
        self.assertIn("CPK", claims[1]["sentence"])

    def test_multiple_ids_in_one_sentence(self) -> None:
        text = "Prior trials agree [EVID:a_2020][EVID:b_2021].\n"
        claims = self.m.extract_claims(text)
        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0]["ids"], ["a_2020", "b_2021"])

    def test_skips_non_prose_and_uncited(self) -> None:
        text = (
            "# Title [EVID:should_skip_heading]\n"
            "| col | [EVID:should_skip_table] |\n"
            "> quote [EVID:should_skip_quote]\n"
            "Plain background sentence with no tag.\n"
        )
        self.assertEqual(self.m.extract_claims(text), [])


if __name__ == "__main__":
    unittest.main()

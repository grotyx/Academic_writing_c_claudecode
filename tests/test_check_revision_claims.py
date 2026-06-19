from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_revision_claims.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_revision_claims", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SAMPLE_RESPONSE = """# Point-by-point responses to reviewer comments

Reviewer #1:

Comment 1) Please clarify the eligibility criteria.

[CHANGE]
comment_id: R1-C1
claim: eligibility criteria sentence added
section: 04_methods
expected_terms: eligibility criteria; excluded; prior surgery
[/CHANGE]

Response: We thank the reviewer for this comment. We revised the Methods.

Location: Methods, paragraph 2

Revised text:
"Patients were eligible if they met the eligibility criteria and were excluded if they had prior surgery."
"""


class CheckRevisionClaimsTests(unittest.TestCase):
    def test_parse_change_blocks_extracts_fields_terms_and_revised_text(self) -> None:
        module = load_module()

        claims = module.parse_change_blocks(SAMPLE_RESPONSE)

        self.assertEqual(len(claims), 1)
        self.assertEqual(claims[0].comment_id, "R1-C1")
        self.assertEqual(claims[0].section, "04_methods")
        self.assertEqual(claims[0].expected_terms, ["eligibility criteria", "excluded", "prior surgery"])
        self.assertEqual(
            claims[0].revised_text,
            '"Patients were eligible if they met the eligibility criteria and were excluded if they had prior surgery."',
        )

    def test_check_revision_claims_passes_when_revised_section_contains_terms_and_quote(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            draft_root = root / "drafts"
            rev_dir = draft_root / "revision" / "REV1"
            rev_dir.mkdir(parents=True)
            (draft_root / "04_methods.md").write_text(
                "Original Methods text without the requested clarification.",
                encoding="utf-8",
            )
            (rev_dir / "04_methods_REV1.md").write_text(
                "Methods\n\n"
                "Patients were eligible if they met the eligibility criteria and were excluded if they had prior surgery.",
                encoding="utf-8",
            )
            response_path = rev_dir / "response_letter_REV1.md"
            response_path.write_text(SAMPLE_RESPONSE, encoding="utf-8")

            result = module.check_revision_claims(response_path, draft_root=draft_root)

            self.assertTrue(result.passed)
            self.assertEqual(result.failures, [])

    def test_check_revision_claims_fails_when_expected_term_is_missing(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            draft_root = root / "drafts"
            rev_dir = draft_root / "revision" / "REV1"
            rev_dir.mkdir(parents=True)
            (rev_dir / "04_methods_REV1.md").write_text(
                "Patients were eligible if they met the eligibility criteria.",
                encoding="utf-8",
            )
            response_path = rev_dir / "response_letter_REV1.md"
            response_path.write_text(SAMPLE_RESPONSE, encoding="utf-8")

            result = module.check_revision_claims(response_path, draft_root=draft_root)

            self.assertFalse(result.passed)
            self.assertIn("missing expected term", result.failures[0].reason)
            self.assertEqual(result.failures[0].comment_id, "R1-C1")

    def test_format_failure_includes_machine_readable_failure_code(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            draft_root = root / "drafts"
            rev_dir = draft_root / "revision" / "REV1"
            rev_dir.mkdir(parents=True)
            (rev_dir / "04_methods_REV1.md").write_text(
                "Patients were eligible if they met the eligibility criteria.",
                encoding="utf-8",
            )
            response_path = rev_dir / "response_letter_REV1.md"
            response_path.write_text(SAMPLE_RESPONSE, encoding="utf-8")

            result = module.check_revision_claims(response_path, draft_root=draft_root)
            output = module.format_result(result, response_path)

            self.assertIn("failure_code: GATE_FAIL REVISION_CLAIMS", output)

    def test_check_revision_claims_fails_when_revised_section_matches_original(self) -> None:
        module = load_module()

        unchanged_text = (
            "Patients were eligible if they met the eligibility criteria and were excluded "
            "if they had prior surgery."
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            draft_root = root / "drafts"
            rev_dir = draft_root / "revision" / "REV1"
            rev_dir.mkdir(parents=True)
            (draft_root / "04_methods.md").write_text(unchanged_text, encoding="utf-8")
            (rev_dir / "04_methods_REV1.md").write_text(unchanged_text, encoding="utf-8")
            response_path = rev_dir / "response_letter_REV1.md"
            response_path.write_text(SAMPLE_RESPONSE, encoding="utf-8")

            result = module.check_revision_claims(response_path, draft_root=draft_root)

            self.assertFalse(result.passed)
            self.assertIn("section unchanged from original", result.failures[0].reason)


if __name__ == "__main__":
    unittest.main()

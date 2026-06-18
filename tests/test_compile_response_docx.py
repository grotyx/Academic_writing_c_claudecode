from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import pytest

Document = pytest.importorskip("docx").Document


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "compile_response_docx.py"


def load_module():
    spec = importlib.util.spec_from_file_location("compile_response_docx", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SAMPLE_RESPONSE = """# Point-by-point responses to reviewer comments

Reviewer #1:

This is the original reviewer summary paragraph.

Comment 1) Please clarify the eligibility criteria.

[CHANGE]
comment_id: R1-C1
claim: eligibility criteria sentence added
section: 04_methods
expected_terms: eligibility criteria; excluded
[/CHANGE]

Response: We thank the reviewer for this comment. We have revised the Methods accordingly, as follows:

Location: Page 5, Line 12

Revised text:
"Patients were eligible if they met the revised eligibility criteria."

Reviewer closing:
We thank Reviewer #1 for reviewing the manuscript.
"""


class CompileResponseDocxTests(unittest.TestCase):
    def test_parse_response_markdown_drops_change_blocks(self) -> None:
        module = load_module()

        blocks = module.parse_response_markdown(SAMPLE_RESPONSE)
        texts = [block.text for block in blocks]

        self.assertIn("Point-by-point responses to reviewer comments", texts)
        self.assertIn("Reviewer #1:", texts)
        self.assertIn("Comment 1) Please clarify the eligibility criteria.", texts)
        self.assertIn(
            "Response: We thank the reviewer for this comment. We have revised the Methods accordingly, as follows:",
            texts,
        )
        self.assertIn("Page 5, Line 12", texts)
        self.assertIn('"Patients were eligible if they met the revised eligibility criteria."', texts)
        self.assertFalse(any("[CHANGE]" in text or "expected_terms" in text for text in texts))

    def test_compile_response_docx_uses_author_response_style(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            input_path = tmpdir / "response_letter_REV1.md"
            output_path = tmpdir / "response_letter_REV1.docx"
            input_path.write_text(SAMPLE_RESPONSE, encoding="utf-8")

            module.compile_docx(input_path, output_path)

            doc = Document(output_path)
            paragraphs = [p for p in doc.paragraphs if p.text.strip()]
            paragraph_by_text = {p.text: p for p in paragraphs}

            self.assertEqual(paragraphs[0].text, "Point-by-point responses to reviewer comments")
            self.assertTrue(paragraphs[0].runs[0].bold)
            self.assertTrue(paragraph_by_text["Reviewer #1:"].runs[0].bold)
            self.assertFalse(paragraph_by_text["Comment 1) Please clarify the eligibility criteria."].runs[0].bold)
            self.assertTrue(
                paragraph_by_text[
                    "Response: We thank the reviewer for this comment. We have revised the Methods accordingly, as follows:"
                ].runs[0].bold
            )
            self.assertTrue(paragraph_by_text["Page 5, Line 12"].runs[0].bold)
            self.assertTrue(
                paragraph_by_text[
                    '"Patients were eligible if they met the revised eligibility criteria."'
                ].runs[0].bold
            )


if __name__ == "__main__":
    unittest.main()

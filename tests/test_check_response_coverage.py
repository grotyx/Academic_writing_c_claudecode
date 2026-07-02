from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_response_coverage.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_response_coverage", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


COMPLETE_LETTER = """# Point-by-point responses to reviewer comments

Reviewer #1:

The reviewer's general remarks.

Comment 1) The sample size seems small.

Response: We thank the reviewer. We added a post-hoc power analysis showing 85% power.

Location: Page 6, Line 12

Revised text:
"A post-hoc power analysis indicated 85% power."

Comment 2) Please clarify the follow-up duration.

Response: We clarified that follow-up was 24 months in Methods.

Reviewer #2:

Comment 1) The discussion overstates the findings.

Response: We tempered the conclusion and removed the causal wording.
"""


def write_letter(tmp: Path, text: str) -> Path:
    path = tmp / "response_letter_REV1.md"
    path.write_text(text, encoding="utf-8")
    return path


class ParseLetterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_complete_letter_parses_all_entries(self) -> None:
        entries = self.module.parse_letter(COMPLETE_LETTER)
        keys = [(entry.reviewer, entry.number) for entry in entries]
        self.assertEqual(keys, [(1, 1), (1, 2), (2, 1)])
        self.assertTrue(all(entry.response_text for entry in entries))

    def test_change_blocks_ignored(self) -> None:
        letter = (
            "Reviewer #1:\n\nComment 1) A comment.\n\n"
            "[CHANGE]\ncomment_id: R1-C1\nsection: 04_methods\nexpected_terms: power\n[/CHANGE]\n\n"
            "Response: We addressed it fully.\n"
        )
        entries = self.module.parse_letter(letter)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].response_text, "We addressed it fully.")

    def test_multiline_response_collected(self) -> None:
        letter = (
            "Reviewer #1:\n\nComment 1) A comment.\n\n"
            "Response: First sentence.\nSecond sentence continues.\n\nLocation: Page 2\n"
        )
        entries = self.module.parse_letter(letter)
        self.assertEqual(entries[0].response_text, "First sentence. Second sentence continues.")


class CoverageCheckTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def _codes(self, result) -> list[str]:
        return [issue.code for issue in result.failures]

    def test_complete_letter_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_letter(Path(tmp), COMPLETE_LETTER)
            result = self.module.check_response_coverage(path)
            self.assertTrue(result.passed)
            self.assertEqual(result.failures, [])

    def test_missing_response_fails(self) -> None:
        letter = "Reviewer #1:\n\nComment 1) A comment.\n\nComment 2) Another.\n\nResponse: Answered only this one.\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = write_letter(Path(tmp), letter)
            result = self.module.check_response_coverage(path)
            self.assertFalse(result.passed)
            self.assertIn("RESPONSE_MISSING", self._codes(result))

    def test_placeholder_response_fails(self) -> None:
        letter = "Reviewer #1:\n\nComment 1) A comment.\n\nResponse: We thank the reviewer. [Response text.]\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = write_letter(Path(tmp), letter)
            result = self.module.check_response_coverage(path)
            self.assertIn("RESPONSE_PLACEHOLDER", self._codes(result))

    def test_empty_letter_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_letter(Path(tmp), "No structure here at all.\n")
            result = self.module.check_response_coverage(path)
            self.assertIn("NO_COMMENTS", self._codes(result))

    def test_comment_gap_warns(self) -> None:
        letter = (
            "Reviewer #1:\n\nComment 1) First.\n\nResponse: Done.\n\n"
            "Comment 3) Third (2 lost).\n\nResponse: Done as well.\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = write_letter(Path(tmp), letter)
            result = self.module.check_response_coverage(path)
            self.assertTrue(result.passed)
            self.assertIn("COMMENT_GAP", [w.code for w in result.warnings])

    def test_cross_check_unanswered_comment_fails(self) -> None:
        comments = "Reviewer #1:\n\nComment 1) First.\n\nComment 2) Second.\n\nReviewer #2:\n\nComment 1) Other.\n"
        letter = "Reviewer #1:\n\nComment 1) First.\n\nResponse: Answered.\n\nReviewer #2:\n\nComment 1) Other.\n\nResponse: Answered too.\n"
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            path = write_letter(tmp, letter)
            comments_path = tmp / "reviewer_comments_REV1.md"
            comments_path.write_text(comments, encoding="utf-8")
            result = self.module.check_response_coverage(path, comments_path=comments_path)
            self.assertFalse(result.passed)
            unanswered = [i for i in result.failures if i.code == "COMMENT_UNANSWERED"]
            self.assertEqual([(i.reviewer, i.comment) for i in unanswered], [(1, 2)])

    def test_unparseable_comments_warns_default_fails_strict(self) -> None:
        letter = "Reviewer #1:\n\nComment 1) First.\n\nResponse: Answered.\n"
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            path = write_letter(tmp, letter)
            comments_path = tmp / "reviewer_comments_REV1.md"
            comments_path.write_text("A raw email paste without structure.\n", encoding="utf-8")
            default = self.module.check_response_coverage(path, comments_path=comments_path)
            self.assertTrue(default.passed)
            self.assertIn("COMMENTS_UNPARSEABLE", [w.code for w in default.warnings])
            strict = self.module.check_response_coverage(path, comments_path=comments_path, strict=True)
            self.assertFalse(strict.passed)


class ResponseCoverageCliTests(unittest.TestCase):
    def _run(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            capture_output=True, text=True,
        )

    def test_pass_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = write_letter(Path(tmp), COMPLETE_LETTER)
            proc = self._run([str(path)])
            self.assertEqual(proc.returncode, 0)
            self.assertIn("RESPONSE COVERAGE PASS", proc.stdout)

    def test_failure_exit_one(self) -> None:
        letter = "Reviewer #1:\n\nComment 1) A comment with no response.\n"
        with tempfile.TemporaryDirectory() as tmp:
            path = write_letter(Path(tmp), letter)
            proc = self._run([str(path)])
            self.assertEqual(proc.returncode, 1)
            self.assertIn("RESPONSE COVERAGE FAIL", proc.stdout)

    def test_missing_file_exit_two(self) -> None:
        proc = self._run(["/nonexistent/response_letter.md"])
        self.assertEqual(proc.returncode, 2)


if __name__ == "__main__":
    unittest.main()

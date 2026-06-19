from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_gate.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_gate", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


PASS_GATE = """# Phase 4 Draft Gate

phase: Phase 4 - Draft Sections
artifact: drafts/05_results.md
status: PASS
checks:
  constraint: PASS
  citation: PASS
  numbers: PASS
round: 2
blocking_failures: none
verifier_model: opus
timestamp: 2026-06-18T10:30:00+09:00
"""


class CheckGateTests(unittest.TestCase):
    def test_parse_gate_entry_extracts_fields_and_checks(self) -> None:
        module = load_module()

        entry = module.parse_gate_entry(PASS_GATE)

        self.assertEqual(entry.fields["status"], "PASS")
        self.assertEqual(entry.fields["artifact"], "drafts/05_results.md")
        self.assertEqual(entry.checks["constraint"], "PASS")
        self.assertEqual(entry.checks["citation"], "PASS")
        self.assertEqual(entry.checks["numbers"], "PASS")

    def test_check_gate_passes_when_status_and_required_checks_pass(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(PASS_GATE, encoding="utf-8")

            result = module.check_gate(
                gate_path,
                required_checks=["constraint", "citation", "numbers"],
                artifact="drafts/05_results.md",
            )

            self.assertTrue(result.passed)
            self.assertEqual(result.failures, [])

    def test_check_gate_fails_when_status_is_not_pass(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(PASS_GATE.replace("status: PASS", "status: FAIL"), encoding="utf-8")

            result = module.check_gate(gate_path, required_checks=["constraint"])

            self.assertFalse(result.passed)
            self.assertIn("status is FAIL", result.failures[0].reason)

    def test_check_gate_fails_when_required_check_is_missing_or_failed(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(PASS_GATE.replace("citation: PASS", "citation: FAIL"), encoding="utf-8")

            result = module.check_gate(gate_path, required_checks=["citation", "numbers", "logic"])

            self.assertFalse(result.passed)
            reasons = [failure.reason for failure in result.failures]
            self.assertIn("required check citation is FAIL", reasons)
            self.assertIn("required check logic is missing", reasons)

    def test_check_gate_fails_when_artifact_does_not_match(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(PASS_GATE, encoding="utf-8")

            result = module.check_gate(gate_path, artifact="drafts/06_discussion.md")

            self.assertFalse(result.passed)
            self.assertIn("artifact mismatch", result.failures[0].reason)

    def test_check_gate_passes_despite_inline_comments(self) -> None:
        # Regression: the documented template keeps inline "# ..." comments on
        # status/round. The parser must strip them, not read "PASS  # PASS | FAIL".
        module = load_module()

        gate_text = (
            "phase: Phase 4 - Draft Sections\n"
            "artifact: drafts/05_results.md\n"
            "status: PASS              # PASS | FAIL\n"
            "checks:\n"
            "  constraint: PASS\n"
            "  citation: PASS\n"
            "  numbers: PASS\n"
            "  logic: PASS\n"
            "round: 2                  # max 2 fix/re-verify attempts\n"
        )

        with tempfile.TemporaryDirectory() as tmp:
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(gate_text, encoding="utf-8")

            result = module.check_gate(
                gate_path,
                required_checks=["constraint", "citation", "numbers", "logic"],
                artifact="drafts/05_results.md",
            )

            self.assertTrue(result.passed)
            self.assertEqual(result.failures, [])

    def test_check_gate_flags_round_overflow_despite_inline_comment(self) -> None:
        # Regression: "round: 5  # exceeded" must trigger escalation, not be
        # silently swallowed to 0 by int() raising on the trailing comment.
        module = load_module()

        gate_text = (
            "artifact: drafts/05_results.md\n"
            "status: PASS              # PASS | FAIL\n"
            "round: 5  # exceeded the limit\n"
        )

        with tempfile.TemporaryDirectory() as tmp:
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(gate_text, encoding="utf-8")

            result = module.check_gate(gate_path, max_round=2)

            self.assertFalse(result.passed)
            reasons = [failure.reason for failure in result.failures]
            self.assertTrue(any("round 5 exceeds" in reason for reason in reasons))


class FreshnessTests(unittest.TestCase):
    """Provenance hashing: a PASS must go stale when its artifact changes."""

    @staticmethod
    def _gate_with_provenance(artifact_hash: str) -> str:
        return (
            "phase: Phase 4 - Draft Sections\n"
            "artifact: drafts/05_results.md\n"
            "status: PASS\n"
            "checks:\n"
            "  constraint: PASS\n"
            "provenance:\n"
            f"  artifact: {artifact_hash}\n"
        )

    def test_parse_gate_entry_extracts_provenance(self) -> None:
        module = load_module()

        entry = module.parse_gate_entry(self._gate_with_provenance("abc123"))

        self.assertEqual(entry.provenance["artifact"], "abc123")
        # Nested provenance block must not bleed into checks.
        self.assertEqual(entry.checks["constraint"], "PASS")
        self.assertNotIn("artifact", entry.checks)

    def test_verify_hash_passes_when_file_unchanged(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "05_results.md"
            artifact.write_text("primary outcome 54.3\n", encoding="utf-8")
            digest = module.sha256_file(artifact)
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(self._gate_with_provenance(digest), encoding="utf-8")

            result = module.check_gate(
                gate_path,
                required_checks=["constraint"],
                verify_hashes=[("artifact", artifact)],
            )

            self.assertTrue(result.passed)
            self.assertEqual(result.failures, [])

    def test_verify_hash_fails_when_file_changed(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "05_results.md"
            artifact.write_text("primary outcome 54.3\n", encoding="utf-8")
            digest = module.sha256_file(artifact)
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(self._gate_with_provenance(digest), encoding="utf-8")
            # Artifact edited after the gate PASS -> the gate is now stale.
            artifact.write_text("primary outcome 99.9\n", encoding="utf-8")

            result = module.check_gate(
                gate_path,
                required_checks=["constraint"],
                verify_hashes=[("artifact", artifact)],
            )

            self.assertFalse(result.passed)
            self.assertTrue(any("stale gate" in f.reason for f in result.failures))

    def test_verify_hash_fails_when_provenance_missing(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "05_results.md"
            artifact.write_text("anything\n", encoding="utf-8")
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(PASS_GATE, encoding="utf-8")  # no provenance block

            result = module.check_gate(gate_path, verify_hashes=[("artifact", artifact)])

            self.assertFalse(result.passed)
            self.assertTrue(any("not recorded" in f.reason for f in result.failures))

    def test_verify_hash_tolerates_sha256_prefix(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "05_results.md"
            artifact.write_text("payload\n", encoding="utf-8")
            digest = module.sha256_file(artifact)
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(self._gate_with_provenance(f"sha256:{digest}"), encoding="utf-8")

            result = module.check_gate(gate_path, verify_hashes=[("artifact", artifact)])

            self.assertTrue(result.passed)

    def test_parse_gate_entry_provenance_before_checks(self) -> None:
        # Block order must not matter, and a top-level field after a nested
        # block (round) must parse as a field, not leak into the block.
        module = load_module()

        gate_text = (
            "artifact: drafts/05_results.md\n"
            "status: PASS\n"
            "provenance:\n"
            "  artifact: abc\n"
            "checks:\n"
            "  constraint: PASS\n"
            "  numbers: PASS\n"
            "round: 1\n"
        )

        entry = module.parse_gate_entry(gate_text)

        self.assertEqual(entry.provenance["artifact"], "abc")
        self.assertEqual(entry.checks["constraint"], "PASS")
        self.assertEqual(entry.checks["numbers"], "PASS")
        self.assertEqual(entry.fields["round"], "1")
        self.assertNotIn("artifact", entry.checks)
        self.assertNotIn("constraint", entry.provenance)

    def test_verify_hash_fails_when_file_missing(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(self._gate_with_provenance("deadbeef"), encoding="utf-8")
            missing = Path(tmp) / "gone.md"  # recorded in provenance but absent on disk

            result = module.check_gate(gate_path, verify_hashes=[("artifact", missing)])

            self.assertFalse(result.passed)
            self.assertTrue(any("not found" in f.reason for f in result.failures))

    def test_verify_hash_handles_multiple_files_independently(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            art = Path(tmp) / "05_results.md"
            art.write_text("section\n", encoding="utf-8")
            res = Path(tmp) / "table2.csv"
            res.write_text("value\n", encoding="utf-8")
            gate_text = (
                "artifact: drafts/05_results.md\n"
                "status: PASS\n"
                "checks:\n"
                "  numbers: PASS\n"
                "provenance:\n"
                f"  artifact: {module.sha256_file(art)}\n"
                f"  results: {module.sha256_file(res)}\n"
            )
            gate_path = Path(tmp) / "phase_04_draft.GATE.md"
            gate_path.write_text(gate_text, encoding="utf-8")

            both = module.check_gate(
                gate_path, verify_hashes=[("artifact", art), ("results", res)]
            )
            self.assertTrue(both.passed)

            res.write_text("CHANGED\n", encoding="utf-8")  # only results drifts
            after = module.check_gate(
                gate_path, verify_hashes=[("artifact", art), ("results", res)]
            )
            self.assertFalse(after.passed)
            self.assertTrue(any("results changed" in f.reason for f in after.failures))
            # the unchanged artifact must NOT be flagged
            self.assertTrue(all("provenance.artifact" != f.field for f in after.failures))

    def test_parse_verify_hash_rejects_bad_format(self) -> None:
        module = load_module()
        parser = module.build_arg_parser()

        with self.assertRaises(SystemExit):
            module.parse_verify_hash(["noequalssign"], parser)

        pairs = module.parse_verify_hash(["artifact=drafts/05_results.md"], parser)
        self.assertEqual(pairs[0][0], "artifact")
        self.assertEqual(str(pairs[0][1]).replace("\\", "/"), "drafts/05_results.md")


if __name__ == "__main__":
    unittest.main()

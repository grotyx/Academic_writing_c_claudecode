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


if __name__ == "__main__":
    unittest.main()

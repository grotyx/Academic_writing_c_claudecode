from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_all.py"


class VerifyAllTests(unittest.TestCase):
    def test_verify_all_forwards_verify_hash_and_fails_stale_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "artifact.md"
            evidence = root / "evidence.md"
            gate = root / "phase_04_draft.GATE.md"
            artifact.write_text("No citations or result numbers.\n", encoding="utf-8")
            evidence.write_text("# Evidence\n", encoding="utf-8")
            gate.write_text(
                "phase: Phase 4 - Draft Sections\n"
                f"artifact: {artifact}\n"
                "status: PASS\n"
                "checks:\n"
                "  constraint: PASS\n"
                "  citation: PASS\n"
                "  numbers: PASS\n"
                "  logic: PASS\n"
                "provenance:\n"
                "  artifact: 0000000000000000000000000000000000000000000000000000000000000000\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(artifact),
                    "--evidence",
                    str(evidence),
                    "--results",
                    str(root / "results"),
                    "--gate",
                    str(gate),
                    "--artifact",
                    str(artifact),
                    "--require-check",
                    "constraint",
                    "--verify-hash",
                    f"artifact={artifact}",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(completed.returncode, 0)
            output = completed.stdout + completed.stderr
            self.assertIn("--- gate: FAIL ---", output)
            self.assertIn("stale gate", output)

    def test_overall_pass_when_nothing_to_flag(self) -> None:
        # An artifact with no [EVID:id] tags and no result numbers passes both
        # checks -> the top-level verdict must be OVERALL: PASS (rc 0).
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "artifact.md"
            artifact.write_text("Plain prose, no tags or result numbers.\n", encoding="utf-8")
            evidence = root / "evidence.md"
            evidence.write_text("# Evidence\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(artifact),
                    "--evidence",
                    str(evidence),
                    "--results",
                    str(root / "results"),
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertIn("OVERALL: PASS", completed.stdout)

    def test_forwards_cross_check_to_gate(self) -> None:
        # Regression: verify_all must forward --cross-check (and --evidence/--results)
        # to check_gate. Ledger records citation: FAIL while the live citation check
        # PASSES -> the cross-check fires (stale ledger) and fails the gate, even
        # though the standalone citation/number checks pass.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact = root / "05_results.md"
            artifact.write_text("Background is established [EVID:smith_2020].\n", encoding="utf-8")
            evidence = root / "evidence.md"
            evidence.write_text(
                "## Reference List\n\n### [1] Smith et al., 2020\n\n"
                "- **Evidence ID:** smith_2020\n- **Source Status:** verified\n",
                encoding="utf-8",
            )
            gate = root / "phase_04_draft.GATE.md"
            gate.write_text(
                f"artifact: {artifact}\nstatus: PASS\nchecks:\n  citation: FAIL\n",
                encoding="utf-8",
            )

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(artifact),
                    "--evidence",
                    str(evidence),
                    "--results",
                    str(root / "results"),
                    "--gate",
                    str(gate),
                    "--artifact",
                    str(artifact),
                    "--cross-check",
                    f"citation={artifact}",
                ],
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertNotEqual(completed.returncode, 0)
            output = completed.stdout + completed.stderr
            self.assertIn("--- gate: FAIL ---", output)
            self.assertIn("cross_check", output)  # forwarded cross-check ran and fired


if __name__ == "__main__":
    unittest.main()

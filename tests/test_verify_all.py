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


if __name__ == "__main__":
    unittest.main()

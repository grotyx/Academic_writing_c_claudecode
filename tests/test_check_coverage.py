from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_coverage.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_coverage", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


EVIDENCE = """# Evidence Registry

## Reference List

### [1] Smith et al., 2020

- **Evidence ID:** smith_2020
- **Source Status:** verified

### [2] Lee et al., 2021

- **Evidence ID:** lee_2021
- **Source Status:** verified

### [3] Park et al., 2022

- **Evidence ID:** park_2022
- **Source Status:** todo
"""


class CoverageTests(unittest.TestCase):
    def _setup(self, tmp: Path, *, intro: str, draft_plan: str | None = None):
        ev = tmp / "evidence.md"
        ev.write_text(EVIDENCE, encoding="utf-8")
        art = tmp / "03_introduction.md"
        art.write_text(intro, encoding="utf-8")
        plan = None
        if draft_plan is not None:
            plan = tmp / "draft_plan.md"
            plan.write_text(draft_plan, encoding="utf-8")
        return ev, art, plan

    def test_uncited_detection_neutral(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # cite smith only -> lee (verified) + park (todo) are uncited (neutral)
            ev, art, _ = self._setup(tmp, intro="Background established [EVID:smith_2020].\n")
            result = module.audit([art], evidence_path=ev)

            uncited_ids = {eid for eid, _status in result.uncited}
            self.assertEqual(uncited_ids, {"lee_2021", "park_2022"})
            self.assertEqual(result.citation_counts["smith_2020"], 1)
            statuses = dict(result.uncited)
            self.assertEqual(statuses["lee_2021"], "verified")
            self.assertEqual(statuses["park_2022"], "todo")

    def test_over_citation_detection(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # one padded sentence (5 cites) + one fine sentence (1 cite); default cap 4
            intro = (
                "Many studies agree [EVID:smith_2020][EVID:smith_2020]"
                "[EVID:lee_2021][EVID:park_2022][EVID:lee_2021]. "
                "A focused claim is supported [EVID:smith_2020].\n"
            )
            ev, art, _ = self._setup(tmp, intro=intro)
            result = module.audit([art], evidence_path=ev)

            self.assertEqual(len(result.over_citations), 1)
            oc = result.over_citations[0]
            self.assertEqual(oc.count, 5)
            self.assertEqual(oc.line, 1)

    def test_over_citation_threshold_configurable(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            intro = "Three sources [EVID:smith_2020][EVID:lee_2021][EVID:park_2022].\n"
            ev, art, _ = self._setup(tmp, intro=intro)
            # cap 4 -> 3 cites OK
            self.assertEqual(module.audit([art], evidence_path=ev).over_citations, [])
            # cap 2 -> 3 cites flagged
            flagged = module.audit([art], evidence_path=ev, max_per_sentence=2).over_citations
            self.assertEqual(len(flagged), 1)
            self.assertEqual(flagged[0].count, 3)

    def test_density_counts_per_artifact(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art, _ = self._setup(
                tmp,
                intro="A [EVID:smith_2020]. B [EVID:lee_2021]. C [EVID:smith_2020].\n",
            )
            result = module.audit([art], evidence_path=ev)
            self.assertEqual(result.density[str(art)], 3)
            self.assertEqual(result.citation_counts["smith_2020"], 2)
            self.assertEqual(result.citation_counts["lee_2021"], 1)

    def test_unknown_citation_detected(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art, _ = self._setup(tmp, intro="Cites a ghost [EVID:ghost_2099].\n")
            result = module.audit([art], evidence_path=ev)
            self.assertIn("ghost_2099", result.unknown)

    def test_unrealized_claims_from_draft_plan(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # plan promises smith + lee; body cites only smith -> lee is unrealized
            ev, art, plan = self._setup(
                tmp,
                intro="Background [EVID:smith_2020].\n",
                draft_plan="Claim A -> [EVID:smith_2020]\nClaim B -> [EVID:lee_2021]\n",
            )
            result = module.audit([art], evidence_path=ev, draft_plan=plan)
            self.assertEqual(result.unrealized, ["lee_2021"])

    def test_fully_covered_has_no_uncited(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art, _ = self._setup(
                tmp,
                intro="A [EVID:smith_2020] B [EVID:lee_2021] C [EVID:park_2022].\n",
            )
            result = module.audit([art], evidence_path=ev)
            self.assertEqual(result.uncited, [])

    def test_format_result_neutral_uncited_no_waste_language(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art, _ = self._setup(tmp, intro="Only smith [EVID:smith_2020].\n")
            result = module.audit([art], evidence_path=ev)
            out = module.format_result(result)
            self.assertIn("COVERAGE REPORT", out)
            self.assertIn("EVID:lee_2021", out)
            # uncited framed neutrally -- no "waste"/"unused" judgment
            self.assertNotIn("unused", out)
            self.assertNotIn("waste", out.lower())
            self.assertIn("valid choice", out)


class CoverageCliExitTests(unittest.TestCase):
    """The --fail-on-* flags ARE the enforcement contract -- verify their exit codes."""

    def _run(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            text=True,
            capture_output=True,
            check=False,
        )

    def _project(self, tmp: Path, intro: str) -> tuple[Path, Path]:
        ev = tmp / "evidence.md"
        ev.write_text(EVIDENCE, encoding="utf-8")
        art = tmp / "03_introduction.md"
        art.write_text(intro, encoding="utf-8")
        return ev, art

    def test_advisory_by_default_exit_zero(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # cite only smith -> lee/park uncited + cite a ghost (unknown), no flags
            ev, art = self._project(tmp, "Cite [EVID:smith_2020] and ghost [EVID:ghost_2099].\n")
            r = self._run([str(art), "--evidence", str(ev)])
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_fail_on_over_citation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art = self._project(
                tmp,
                "Many [EVID:smith_2020][EVID:lee_2021][EVID:park_2022]"
                "[EVID:smith_2020][EVID:lee_2021].\n",  # 5 in one sentence > default 4
            )
            self.assertEqual(self._run([str(art), "--evidence", str(ev)]).returncode, 0)
            self.assertEqual(
                self._run([str(art), "--evidence", str(ev), "--fail-on-over-citation"]).returncode, 1
            )

    def test_fail_on_unknown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art = self._project(tmp, "Cites a ghost [EVID:ghost_2099].\n")
            self.assertEqual(self._run([str(art), "--evidence", str(ev)]).returncode, 0)
            self.assertEqual(
                self._run([str(art), "--evidence", str(ev), "--fail-on-unknown"]).returncode, 1
            )

    def test_fail_on_uncited_verified(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # cite only smith -> lee_2021 (verified) is uncited
            ev, art = self._project(tmp, "Only [EVID:smith_2020] is cited.\n")
            self.assertEqual(self._run([str(art), "--evidence", str(ev)]).returncode, 0)
            self.assertEqual(
                self._run([str(art), "--evidence", str(ev), "--fail-on-uncited-verified"]).returncode,
                1,
            )


if __name__ == "__main__":
    unittest.main()

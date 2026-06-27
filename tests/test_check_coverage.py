from __future__ import annotations

import importlib.util
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

    def test_orphan_detection_flags_uncited_verified(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # cite smith only -> lee (verified) + park (todo) are orphans
            ev, art, _ = self._setup(tmp, intro="Background established [EVID:smith_2020].\n")
            result = module.audit([art], evidence_path=ev)

            orphan_ids = {eid for eid, _status in result.orphans}
            self.assertEqual(orphan_ids, {"lee_2021", "park_2022"})
            self.assertEqual(result.citation_counts["smith_2020"], 1)
            # lee is the verified orphan (notable); park is todo (expected)
            statuses = dict(result.orphans)
            self.assertEqual(statuses["lee_2021"], "verified")
            self.assertEqual(statuses["park_2022"], "todo")

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

    def test_fully_covered_has_no_orphans(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art, _ = self._setup(
                tmp,
                intro="A [EVID:smith_2020] B [EVID:lee_2021] C [EVID:park_2022].\n",
            )
            result = module.audit([art], evidence_path=ev)
            self.assertEqual(result.orphans, [])

    def test_main_fail_on_orphan_verified_exit_code(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art, _ = self._setup(tmp, intro="Only smith [EVID:smith_2020].\n")
            # simulate CLI via audit + the same predicate main() uses
            result = module.audit([art], evidence_path=ev)
            has_verified_orphan = any(s == "verified" for _e, s in result.orphans)
            self.assertTrue(has_verified_orphan)  # lee_2021 verified + uncited

    def test_format_result_marks_verified_orphan(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art, _ = self._setup(tmp, intro="Only smith [EVID:smith_2020].\n")
            result = module.audit([art], evidence_path=ev)
            out = module.format_result(result)
            self.assertIn("COVERAGE REPORT", out)
            self.assertIn("verified work unused", out)
            self.assertIn("EVID:lee_2021", out)


if __name__ == "__main__":
    unittest.main()

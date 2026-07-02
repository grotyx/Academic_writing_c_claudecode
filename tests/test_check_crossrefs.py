from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_crossrefs.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_crossrefs", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def make_project(tmp: Path, *, tables: list[int], figures: list[int], results_text: str) -> Path:
    for number in tables:
        (tmp / f"table_{number}.md").write_text(f"# Table {number}. Something\n", encoding="utf-8")
    legend_lines = "\n".join(f"**Figure {number}.** A legend." for number in figures)
    (tmp / "09_figure_legends.md").write_text(f"# Figure Legends\n\n{legend_lines}\n", encoding="utf-8")
    results = tmp / "05_results.md"
    results.write_text(results_text, encoding="utf-8")
    return results


class MentionParsingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def _mentions(self, text: str) -> list:
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "05_results.md"
            artifact.write_text(text, encoding="utf-8")
            return self.module.find_mentions(artifact)

    def test_simple_and_compound_mentions(self) -> None:
        mentions = self._mentions("Shown in Table 1. Tables 2 and 3 list outcomes. See Figure 2-4.\n")
        pairs = {(m.kind, m.number) for m in mentions}
        self.assertEqual(
            pairs,
            {("table", 1), ("table", 2), ("table", 3), ("figure", 2), ("figure", 3), ("figure", 4)},
        )

    def test_fig_abbreviation_and_panel_letter(self) -> None:
        mentions = self._mentions("As seen in Fig. 1A, the trend held.\n")
        self.assertEqual([(m.kind, m.number) for m in mentions], [("figure", 1)])

    def test_data_after_comma_not_swallowed(self) -> None:
        # "Figure 1, 25% of patients" must not create a mention of figure 25.
        mentions = self._mentions("In Figure 1, 25% of patients improved.\n")
        self.assertEqual([(m.kind, m.number) for m in mentions], [("figure", 1)])

    def test_html_comments_and_code_fences_ignored(self) -> None:
        text = "<!-- refer to Table 9 -->\n```\nTable 8\n```\nReal mention: Table 1.\n"
        mentions = self._mentions(text)
        self.assertEqual([(m.kind, m.number) for m in mentions], [("table", 1)])


class CrossrefAuditTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module()

    def test_all_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            results = make_project(
                tmp, tables=[1, 2], figures=[1],
                results_text="Baseline in Table 1. Outcomes in Table 2 and Figure 1.\n",
            )
            result = self.module.check_crossrefs([results])
            self.assertEqual(result.broken, [])
            self.assertEqual(result.unreferenced, {})
            self.assertEqual(result.out_of_order, {})

    def test_broken_reference_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            results = make_project(
                tmp, tables=[1], figures=[1],
                results_text="Details in Table 3 and Figure 1.\n",
            )
            result = self.module.check_crossrefs([results])
            self.assertEqual([(m.kind, m.number) for m in result.broken], [("table", 3)])

    def test_unreferenced_item_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            results = make_project(
                tmp, tables=[1, 2], figures=[1, 2],
                results_text="Only Table 1 and Figure 1 are mentioned.\n",
            )
            result = self.module.check_crossrefs([results])
            self.assertEqual(result.unreferenced, {"table": [2], "figure": [2]})

    def test_out_of_order_first_mentions(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            results = make_project(
                tmp, tables=[1, 2], figures=[],
                results_text="Outcomes in Table 2 preceded baseline in Table 1.\n",
            )
            result = self.module.check_crossrefs([results])
            self.assertEqual(result.out_of_order, {"table": [2, 1]})

    def test_missing_inventory_skips_kind_instead_of_flagging(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            artifact = tmp / "05_results.md"
            artifact.write_text("Shown in Table 1.\n", encoding="utf-8")
            result = self.module.check_crossrefs([artifact])
            self.assertEqual(result.broken, [])
            self.assertIn("table", result.skipped_kinds)

    def test_figures_dir_feeds_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            figures_dir = tmp / "figures"
            figures_dir.mkdir()
            (figures_dir / "figure_2.png").write_bytes(b"")
            artifact = tmp / "05_results.md"
            artifact.write_text("Trend in Figure 2.\n", encoding="utf-8")
            result = self.module.check_crossrefs([artifact], figures_dir=figures_dir)
            self.assertEqual(result.broken, [])
            self.assertEqual(result.inventory["figure"], {2})


class CrossrefCliTests(unittest.TestCase):
    def _run(self, args: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            capture_output=True, text=True,
        )

    def test_advisory_default_exit_zero_on_broken(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            results = make_project(tmp, tables=[1], figures=[], results_text="See Table 9.\n")
            proc = self._run([str(results)])
            self.assertEqual(proc.returncode, 0)
            self.assertIn("broken references", proc.stdout)

    def test_fail_on_broken_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            results = make_project(tmp, tables=[1], figures=[], results_text="See Table 9.\n")
            proc = self._run([str(results), "--fail-on-broken"])
            self.assertEqual(proc.returncode, 1)

    def test_fail_on_unreferenced_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            results = make_project(tmp, tables=[1, 2], figures=[], results_text="See Table 1.\n")
            proc = self._run([str(results), "--fail-on-unreferenced"])
            self.assertEqual(proc.returncode, 1)

    def test_clean_manuscript_passes_all_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            results = make_project(
                tmp, tables=[1], figures=[1],
                results_text="See Table 1 and Figure 1.\n",
            )
            proc = self._run([
                str(results), "--fail-on-broken", "--fail-on-unreferenced", "--fail-on-order",
            ])
            self.assertEqual(proc.returncode, 0)
            self.assertIn("all cross-references consistent", proc.stdout)


if __name__ == "__main__":
    unittest.main()

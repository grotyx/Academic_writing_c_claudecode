from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "evidence_table.py"


def load_module():
    spec = importlib.util.spec_from_file_location("evidence_table", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class EvidenceTableTests(unittest.TestCase):
    def setUp(self) -> None:
        self.m = load_module()

    def test_build_table_with_columns(self) -> None:
        records = [
            {"study": "Park 2025", "design": "RCT", "n": 100, "result": "equivalent"},
            {"study": "Kim 2023", "design": "cohort", "n": 80, "result": "BED better"},
        ]
        out = self.m.build_table(records, ["study", "design", "n", "result"])
        lines = out.splitlines()
        self.assertEqual(lines[0], "| study | design | n | result |")
        self.assertEqual(lines[1], "| --- | --- | --- | --- |")
        self.assertIn("| Park 2025 | RCT | 100 | equivalent |", lines)
        self.assertIn("| Kim 2023 | cohort | 80 | BED better |", lines)

    def test_infer_columns_union_order(self) -> None:
        records = [{"a": 1, "b": 2}, {"b": 3, "c": 4}]
        self.assertEqual(self.m.infer_columns(records), ["a", "b", "c"])

    def test_missing_values_blank(self) -> None:
        out = self.m.build_table([{"a": 1}], ["a", "b"])
        self.assertEqual(out.splitlines()[-1], "| 1 |  |")

    def test_cell_escapes_pipe_and_list(self) -> None:
        self.assertEqual(self.m._cell("a | b"), "a \\| b")
        self.assertEqual(self.m._cell(["x", "y"]), "x; y")
        self.assertEqual(self.m._cell(None), "")

    def test_to_records_accepts_wrapper(self) -> None:
        self.assertEqual(self.m.to_records({"studies": [{"a": 1}]}), [{"a": 1}])
        self.assertEqual(self.m.to_records([{"a": 1}]), [{"a": 1}])


if __name__ == "__main__":
    unittest.main()

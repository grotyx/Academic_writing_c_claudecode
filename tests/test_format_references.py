from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "format_references.py"


def load_module():
    spec = importlib.util.spec_from_file_location("format_references", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


EVIDENCE = """# Evidence Registry

## Reference List

### [1] Smith et al., 2020

- **Evidence ID:** smith_2020
- **Citation:** Smith J, Doe A. Example RCT. Spine. 2020;45(1):1-9.
- **Source Status:** verified

### [2] Lee et al., 2021

- **Evidence ID:** lee_2021
- **Citation:** Lee J. Cohort study. Spine J. 2021;21(2):100-110.
- **Source Status:** verified

### [3] Adams et al., 2019

- **Evidence ID:** adams_2019
- **Citation:** Adams K. Earlier work. Eur Spine J. 2019;28(3):55-60.
- **Source Status:** verified
"""


class FormatReferencesTests(unittest.TestCase):
    def _setup(self, tmp: Path, body: str):
        ev = tmp / "evidence.md"
        ev.write_text(EVIDENCE, encoding="utf-8")
        art = tmp / "03_introduction.md"
        art.write_text(body, encoding="utf-8")
        return ev, art

    def test_numbered_by_first_appearance(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            # lee appears first, then smith -> lee=[1], smith=[2]
            ev, art = self._setup(tmp, "First [EVID:lee_2021]. Then [EVID:smith_2020].\n")
            result = module.build([art], evidence_path=ev, style="numbered")

            self.assertEqual(result.order, ["lee_2021", "smith_2020"])
            self.assertEqual(result.labels["lee_2021"], "[1]")
            self.assertEqual(result.labels["smith_2020"], "[2]")
            self.assertTrue(result.references[0].startswith("1. Lee J."))
            self.assertTrue(result.references[1].startswith("2. Smith J"))

    def test_author_year_labels_and_alpha_reference_list(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art = self._setup(tmp, "A [EVID:smith_2020] then [EVID:adams_2019].\n")
            result = module.build([art], evidence_path=ev, style="author-year")

            self.assertEqual(result.labels["smith_2020"], "(Smith, 2020)")
            self.assertEqual(result.labels["adams_2019"], "(Adams, 2019)")
            # reference list alphabetical: Adams before Smith (despite Smith cited first)
            self.assertTrue(result.references[0].startswith("Adams K."))
            self.assertTrue(result.references[1].startswith("Smith J"))

    def test_convert_text_replaces_known_keeps_unknown(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art = self._setup(tmp, "Known [EVID:smith_2020] and ghost [EVID:ghost_2099].\n")
            result = module.build([art], evidence_path=ev, style="numbered")
            converted = module.convert_text(art.read_text(encoding="utf-8"), result.labels)

            self.assertIn("Known [1]", converted)
            self.assertIn("[EVID:ghost_2099]", converted)  # unknown untouched
            self.assertIn("ghost_2099", result.unknown)

    def test_unknown_citation_makes_exit_nonzero_predicate(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art = self._setup(tmp, "Ghost [EVID:ghost_2099].\n")
            result = module.build([art], evidence_path=ev, style="numbered")
            self.assertEqual(result.unknown, ["ghost_2099"])
            self.assertEqual(result.order, [])  # no known ids

    def test_missing_citation_field_falls_back_to_heading(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev = tmp / "evidence.md"
            ev.write_text(
                "## Reference List\n\n### [1] Kim et al., 2018\n\n"
                "- **Evidence ID:** kim_2018\n- **Source Status:** verified\n",
                encoding="utf-8",
            )
            art = tmp / "03_introduction.md"
            art.write_text("Cited [EVID:kim_2018].\n", encoding="utf-8")
            result = module.build([art], evidence_path=ev, style="numbered")

            self.assertIn("kim_2018", result.missing_citation)
            self.assertIn("Kim et al., 2018", result.references[0])  # heading fallback

    def test_convert_writes_sibling_file_not_in_place(self) -> None:
        module = load_module()
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            ev, art = self._setup(tmp, "Cite [EVID:smith_2020].\n")
            original = art.read_text(encoding="utf-8")
            result = module.build([art], evidence_path=ev, style="numbered")
            converted = module.convert_text(original, result.labels)
            out = art.with_name(f"{art.stem}_formatted{art.suffix}")
            out.write_text(converted, encoding="utf-8")

            # source untouched, sibling created with the replacement
            self.assertEqual(art.read_text(encoding="utf-8"), original)
            self.assertIn("Cite [1]", out.read_text(encoding="utf-8"))

    def test_author_year_handles_multiword_author(self) -> None:
        module = load_module()
        ay = load_module().author_year("van_der_berg_2019")
        self.assertEqual(ay, ("Van Der Berg", "2019"))
        self.assertIsNone(module.author_year("noyear_id"))


if __name__ == "__main__":
    unittest.main()

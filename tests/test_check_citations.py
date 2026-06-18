from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "check_citations.py"


def load_module():
    spec = importlib.util.spec_from_file_location("check_citations", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


SAMPLE_EVIDENCE = """# Evidence Registry

## Reference List

### [1] Smith et al., 2020

- **Evidence ID:** smith_2020
- **Citation:** Smith J, Doe A. Example RCT. Spine. 2020.
- **DOI:** 10.1000/example
- **PMID:** 12345678
- **PDF:** knowledge/pdf/smith_2020_example.pdf
- **Source Status:** verified

- **Study Design:** RCT
- **Main Findings:**
  - Treatment improved the outcome.

### [2] Lee et al., 2021

- **Evidence ID:** lee_2021
- **Citation:** Lee J. Pending paper. Spine J. 2021.
- **Source Status:** todo

### [3] Park et al., 2022

- **Evidence ID:** park_2022
- **Citation:** Park J. Abstract-only paper. Eur Spine J. 2022.
- **Source Status:** abstract-only
"""


class CheckCitationsTests(unittest.TestCase):
    def test_parse_evidence_entries_extracts_ids_and_source_status(self) -> None:
        module = load_module()

        entries = module.parse_evidence_entries(SAMPLE_EVIDENCE)

        self.assertEqual(entries["smith_2020"].source_status, "verified")
        self.assertEqual(entries["lee_2021"].source_status, "todo")
        self.assertEqual(entries["park_2022"].heading, "[3] Park et al., 2022")

    def test_check_citations_passes_verified_evidence_token(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            evidence_path = tmpdir / "evidence.md"
            artifact_path = tmpdir / "03_introduction.md"
            evidence_path.write_text(SAMPLE_EVIDENCE, encoding="utf-8")
            artifact_path.write_text("Prior evidence supports this statement [EVID:smith_2020].", encoding="utf-8")

            result = module.check_citations([artifact_path], evidence_path=evidence_path)

            self.assertTrue(result.passed)
            self.assertEqual(result.failures, [])

    def test_check_citations_fails_unknown_evidence_token(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            evidence_path = tmpdir / "evidence.md"
            artifact_path = tmpdir / "06_discussion.md"
            evidence_path.write_text(SAMPLE_EVIDENCE, encoding="utf-8")
            artifact_path.write_text("This claim cites a missing source [EVID:missing_2024].", encoding="utf-8")

            result = module.check_citations([artifact_path], evidence_path=evidence_path)

            self.assertFalse(result.passed)
            self.assertEqual(result.failures[0].citation_id, "missing_2024")
            self.assertIn("not found", result.failures[0].reason)

    def test_check_citations_fails_todo_source_status(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            evidence_path = tmpdir / "evidence.md"
            artifact_path = tmpdir / "06_discussion.md"
            evidence_path.write_text(SAMPLE_EVIDENCE, encoding="utf-8")
            artifact_path.write_text("This claim uses an unverified source [EVID:lee_2021].", encoding="utf-8")

            result = module.check_citations([artifact_path], evidence_path=evidence_path)

            self.assertFalse(result.passed)
            self.assertEqual(result.failures[0].citation_id, "lee_2021")
            self.assertIn("todo", result.failures[0].reason)

    def test_check_citations_warns_abstract_only_by_default(self) -> None:
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            evidence_path = tmpdir / "evidence.md"
            artifact_path = tmpdir / "03_introduction.md"
            evidence_path.write_text(SAMPLE_EVIDENCE, encoding="utf-8")
            artifact_path.write_text("This claim is supported only by an abstract [EVID:park_2022].", encoding="utf-8")

            result = module.check_citations([artifact_path], evidence_path=evidence_path)

            self.assertTrue(result.passed)
            self.assertEqual(result.warnings[0].citation_id, "park_2022")
            self.assertIn("abstract-only", result.warnings[0].reason)

    def test_check_citations_ignores_inline_code_spans(self) -> None:
        # An [EVID:...] token inside an inline `code` span is an example, not a
        # real citation, and must not be verified against the registry.
        module = load_module()

        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            evidence_path = tmpdir / "evidence.md"
            artifact_path = tmpdir / "03_introduction.md"
            evidence_path.write_text(SAMPLE_EVIDENCE, encoding="utf-8")
            artifact_path.write_text(
                "Cite using the `[EVID:made_up_0000]` format; the finding holds [EVID:smith_2020].",
                encoding="utf-8",
            )

            result = module.check_citations([artifact_path], evidence_path=evidence_path)

            self.assertTrue(result.passed)
            self.assertEqual(result.checked_tokens, 1)


if __name__ == "__main__":
    unittest.main()

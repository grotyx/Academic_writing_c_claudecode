from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "hooks" / "style_intent.py"


def load_module():
    spec = importlib.util.spec_from_file_location("style_intent", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class DetectTests(unittest.TestCase):
    def setUp(self) -> None:
        self.m = load_module()

    def test_korean_triggers(self) -> None:
        for prompt in (
            "이 초안 학술적으로 바꿔줘",
            "학술 논문에 맞게 다듬어줘",
            "저널 스타일로 변경해줘",
            "논문체로 작성해줘",
        ):
            self.assertTrue(self.m.detect(prompt), prompt)

    def test_english_triggers(self) -> None:
        for prompt in (
            "rewrite this academically",
            "make it academic",
            "polish to journal style",
        ):
            self.assertTrue(self.m.detect(prompt), prompt)

    def test_negatives(self) -> None:
        for prompt in (
            "학술대회 언제야?",
            "학술 논문 검색해줘",
            "what is academic writing?",
            "이 결과 정리해서 커밋해줘",
            "",
        ):
            self.assertFalse(self.m.detect(prompt), prompt)


class EvaluateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.m = load_module()

    def test_injects_on_match(self) -> None:
        out = self.m.evaluate({"prompt": "이 초안 학술적으로 바꿔줘"})
        self.assertIn("style-pass", out)

    def test_empty_on_non_match(self) -> None:
        self.assertEqual(self.m.evaluate({"prompt": "커밋해줘"}), "")

    def test_fails_open_on_garbage(self) -> None:
        self.assertEqual(self.m.evaluate({}), "")


class MainStdinTests(unittest.TestCase):
    """End-to-end: the hook must read UTF-8 JSON from stdin (Korean intact on Windows)."""

    def test_main_reads_utf8_korean_stdin(self) -> None:
        payload = json.dumps({"prompt": "이 초안 학술적으로 바꿔줘"})
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=payload.encode("utf-8"),
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn(b"style-pass", proc.stdout)

    def test_main_quiet_on_non_match(self) -> None:
        payload = json.dumps({"prompt": "그냥 커밋해줘"})
        proc = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input=payload.encode("utf-8"),
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), b"")


if __name__ == "__main__":
    unittest.main()

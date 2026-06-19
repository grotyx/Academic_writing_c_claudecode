from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "critical_review.py"


def load_module():
    spec = importlib.util.spec_from_file_location("critical_review", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class BuildPromptTests(unittest.TestCase):
    def test_manuscript_prompt_embeds_target_and_adversarial_framing(self) -> None:
        m = load_module()
        out = m.build_prompt("manuscript", "The drug cured everyone.")
        self.assertIn("The drug cured everyone.", out)
        self.assertIn("reviewer", out.lower())

    def test_response_prompt_uses_rebuttal_framing(self) -> None:
        m = load_module()
        out = m.build_prompt("response", "We added a sentence.")
        self.assertIn("We added a sentence.", out)
        self.assertIn("reviewer", out.lower())

    def test_braces_in_target_do_not_break_substitution(self) -> None:
        # Target text with literal braces (JSON, LaTeX) must be inserted verbatim.
        m = load_module()
        target = 'Cohort {n=120} with \\cite{smith} and {"k": 1}.'
        out = m.build_prompt("manuscript", target)
        self.assertIn(target, out)


class CallModelTests(unittest.TestCase):
    def test_call_model_posts_and_parses_choice(self) -> None:
        m = load_module()
        fake = mock.Mock()
        fake.json.return_value = {"choices": [{"message": {"content": "weak stats"}}]}
        fake.raise_for_status.return_value = None
        with mock.patch.object(m.requests, "post", return_value=fake) as post:
            out = m.call_model("minimax/minimax-m3", "attack this", "KEY")
        self.assertEqual(out, "weak stats")
        args, kwargs = post.call_args
        self.assertEqual(kwargs["json"]["model"], "minimax/minimax-m3")
        self.assertIn("Bearer KEY", kwargs["headers"]["Authorization"])


class RunCriticalReviewTests(unittest.TestCase):
    def test_failed_model_is_skipped_others_kept(self) -> None:
        m = load_module()

        def side_effect(model_id, prompt, api_key, timeout=120):
            if model_id == "bad/model":
                raise RuntimeError("boom")
            return f"findings from {model_id}"

        with mock.patch.object(m, "call_model", side_effect=side_effect):
            out = m.run_critical_review(
                "text", ["good/a", "bad/model", "good/b"], "manuscript", "KEY"
            )
        self.assertEqual(set(out), {"good/a", "good/b"})
        self.assertNotIn("bad/model", out)


class LoadModelsTests(unittest.TestCase):
    def test_load_models_ignores_comments_and_blanks(self) -> None:
        m = load_module()
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "models.txt"
            p.write_text(
                "# comment\nminimax/minimax-m3\n\n  z-ai/glm-5.2  \n",
                encoding="utf-8",
            )
            self.assertEqual(
                m.load_models(p), ["minimax/minimax-m3", "z-ai/glm-5.2"]
            )


class PromptFileTests(unittest.TestCase):
    def test_prompt_files_are_the_single_source(self) -> None:
        # Prompts must live as files (the single source), not hardcoded.
        m = load_module()
        self.assertTrue((m.PROMPT_DIR / "manuscript.txt").exists())
        self.assertTrue((m.PROMPT_DIR / "response.txt").exists())


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Call OpenRouter models as adversarial peer reviewers.

Deterministic helper for /critical-review. It only calls the OpenRouter
chat-completions API for each model and returns their raw findings; merging
and severity ranking are done by the main Claude agent, not here.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Adversarial prompts live in scripts/critical_prompts/<role>.txt so that this
# script, the protocol doc, and the Claude/Codex reviewers all share one source.
PROMPT_DIR = Path(__file__).resolve().parent / "critical_prompts"
ROLES = ("manuscript", "response")


def build_prompt(role: str, target_text: str) -> str:
    prompt_file = PROMPT_DIR / f"{role}.txt"
    if not prompt_file.exists():
        raise ValueError(f"unknown role: {role}")
    template = prompt_file.read_text(encoding="utf-8")
    # Use replace (not str.format) so literal braces in the prompt or target
    # text -- e.g. JSON or LaTeX examples -- never crash the substitution.
    return template.replace("{target}", target_text)


def call_model(model_id: str, prompt: str, api_key: str, timeout: int = 120) -> str:
    response = requests.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {api_key}"},
        json={"model": model_id, "messages": [{"role": "user", "content": prompt}]},
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def run_critical_review(
    target_text: str, models: list[str], role: str, api_key: str
) -> dict[str, str]:
    prompt = build_prompt(role, target_text)
    results: dict[str, str] = {}
    for model_id in models:
        try:
            results[model_id] = call_model(model_id, prompt, api_key)
        except Exception as exc:  # noqa: BLE001 - one model's failure must not abort
            print(f"warning: model {model_id} failed: {exc}", file=sys.stderr)
    return results


def load_models(path: str | Path) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Adversarial OpenRouter critical review.")
    parser.add_argument("--target", required=True, type=Path, help="Target text file")
    parser.add_argument("--models", help="Comma-separated OpenRouter model IDs")
    parser.add_argument("--models-file", type=Path, help="File with one model ID per line")
    parser.add_argument("--role", choices=ROLES, default="manuscript")
    parser.add_argument("--out", type=Path, help="Directory to write per-model raw responses")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("error: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 2

    if args.models:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    elif args.models_file:
        models = load_models(args.models_file)
    else:
        print("error: provide --models or --models-file", file=sys.stderr)
        return 2

    target_text = args.target.read_text(encoding="utf-8")
    results = run_critical_review(target_text, models, args.role, api_key)

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        for model_id, text in results.items():
            safe = model_id.replace("/", "_")
            (args.out / f"{safe}.md").write_text(text, encoding="utf-8")

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())

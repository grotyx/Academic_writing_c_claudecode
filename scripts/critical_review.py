#!/usr/bin/env python3
"""Call OpenRouter models -- and optionally the local Claude CLI -- as
adversarial peer reviewers.

Deterministic helper for /critical-review. It calls each OpenRouter model (and,
with --include-claude, shells out to `claude -p`) and returns their raw findings;
merging and severity ranking are done by the orchestrating agent, not here. The
Claude-CLI path lets a non-Claude-Code caller (e.g. Codex, or a plain shell) pull
in Claude's review too.
"""

from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Adversarial prompts live in scripts/critical_prompts/<role>.txt so that this
# script, the protocol doc, and the Claude/Codex reviewers all share one source.
PROMPT_DIR = Path(__file__).resolve().parent / "critical_prompts"
# manuscript = senior peer-reviewer pass; response = reviewer-response pass;
# editor = high-impact-tier editor desk-screen (clinical validity / scope fit /
# additional validation), a deliberately higher bar than the target journal.
ROLES = ("manuscript", "response", "editor")

# Pseudo model id routing to the local Claude Code CLI reviewer (claude -p).
CLAUDE_MODEL_ID = "claude-cli"
CODEX_MODEL_ID = "codex-cli"


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


def call_claude_cli(prompt: str, timeout: int = 240) -> str:
    """Run the local Claude Code CLI in headless print mode as a reviewer.

    Lets a non-Claude-Code caller (e.g. Codex or a plain shell) obtain Claude's
    adversarial review by shelling out to `claude -p`. The prompt is piped via
    stdin to avoid command-length limits on large manuscripts.
    """
    proc = subprocess.run(
        ["claude", "-p", "--bare", "--tools", "", "--disallowedTools", "mcp__*"],
        input=prompt,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or f"claude CLI exited {proc.returncode}")
    out = proc.stdout.strip()
    if not out:
        raise RuntimeError("claude CLI returned empty output")
    return out


def call_codex_cli(prompt: str, timeout: int = 240) -> str:
    proc = subprocess.run(["codex", "exec", "--sandbox", "read-only", "-"],
                          input=prompt, text=True, encoding="utf-8", capture_output=True, timeout=timeout)
    if proc.returncode or not proc.stdout.strip():
        raise RuntimeError("codex CLI failed or returned empty output")
    return proc.stdout.strip()


def run_critical_review(
    target_text: str, models: list[str], role: str, api_key: str | None, failures: dict | None = None
) -> dict[str, str]:
    prompt = build_prompt(role, target_text)
    results: dict[str, str] = {}
    for model_id in models:
        try:
            if model_id == CLAUDE_MODEL_ID:
                results[model_id] = call_claude_cli(prompt)
            elif model_id == CODEX_MODEL_ID:
                results[model_id] = call_codex_cli(prompt)
            elif not api_key:
                raise RuntimeError("OPENROUTER_API_KEY not set")
            else:
                results[model_id] = call_model(model_id, prompt, api_key)
            if not isinstance(results[model_id], str) or not results[model_id].strip():
                results.pop(model_id, None)
                raise RuntimeError("empty review response")
        except Exception as exc:  # noqa: BLE001 - one model's failure must not abort
            if failures is not None:
                failures[model_id] = type(exc).__name__
            print(f"warning: model {model_id} unavailable/failed ({type(exc).__name__})", file=sys.stderr)
    return results


def load_models(path: str | Path) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Adversarial critical review (OpenRouter models + optional local Claude CLI)."
    )
    parser.add_argument("--target", required=True, type=Path, help="Target text file")
    parser.add_argument("--models", help="Comma-separated OpenRouter model IDs")
    parser.add_argument("--models-file", type=Path, help="File with one model ID per line")
    parser.add_argument("--role", choices=ROLES, default="manuscript")
    parser.add_argument(
        "--include-claude",
        action="store_true",
        help="Also run the local `claude` CLI (Claude Code, headless) as a reviewer "
        "-- use when invoking from Codex or a plain shell.",
    )
    parser.add_argument("--include-codex", action="store_true", help="Read-only Codex CLI review")
    parser.add_argument("--context", type=Path, action="append", default=[], help="Explicit approved review packet/source files (repeatable)")
    parser.add_argument("--out", type=Path, help="Directory to write per-model raw responses")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()

    if args.models:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    elif args.models_file:
        models = load_models(args.models_file)
    else:
        models = []
    if args.include_claude and CLAUDE_MODEL_ID not in models:
        models.append(CLAUDE_MODEL_ID)
    if args.include_codex and CODEX_MODEL_ID not in models:
        models.append(CODEX_MODEL_ID)
    models = list(dict.fromkeys(models))
    if not models:
        print("error: provide --models, --models-file, or --include-claude", file=sys.stderr)
        return 2

    api_key = os.environ.get("OPENROUTER_API_KEY")

    target_bytes = args.target.read_bytes()
    target_text = target_bytes.decode("utf-8")
    sources = {str(args.target): hashlib.sha256(target_bytes).hexdigest()}
    for path in args.context:
        content_bytes = path.read_bytes()
        content = content_bytes.decode("utf-8")
        sources[str(path)] = hashlib.sha256(content_bytes).hexdigest()
        target_text += f"\n\nSOURCE: {path.name}\n{content}"
    if len(target_text.encode("utf-8")) > 500_000:
        print("error: review packet exceeds 500 KB", file=sys.stderr)
        return 2
    failures = {}
    results = run_critical_review(target_text, models, args.role, api_key, failures)
    manifest = {"status": "complete" if len(results) == len(models) else "partial" if results else "failed",
                "requested": models, "completed": list(results), "failures": failures,
                "sources": sources, "role": args.role,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "scope": "advisory; does not constitute a semantic gate PASS"}

    if args.out:
        from uuid import uuid4
        run_dir = args.out / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "_" + uuid4().hex[:8])
        run_dir.mkdir(parents=True, exist_ok=False)
        manifest["output"] = str(run_dir)
        for model_id, text in results.items():
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", model_id).strip(".") + "_" + hashlib.sha256(model_id.encode()).hexdigest()[:8]
            (run_dir / f"{safe}.md").write_text(text, encoding="utf-8")

        (run_dir / "run.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(manifest, ensure_ascii=False), file=sys.stderr)
    return 0 if results else 1


if __name__ == "__main__":
    raise SystemExit(main())

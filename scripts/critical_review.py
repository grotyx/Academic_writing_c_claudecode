#!/usr/bin/env python3
"""Adversarial peer review by any mix of reviewers the user chooses.

Deterministic helper for /critical-review. Reviewers are `agent[:model]` specs:
openrouter:<model id> (any OpenRouter model), claude, codex, opencode, muse, agy
(local CLIs, each with an optional model). It returns their raw findings; merging
and severity ranking are done by the orchestrating agent, not here.

Defaults come from the user's settings (`manuwright config`), stored in
$MANUWRIGHT_HOME/config.json (default ~/.manuwright/config.json):
  main_model                 model that writes the manuscript (reviewers using it are flagged
                             as not independent)
  review.reviewers           default reviewer specs, e.g. ["codex", "opencode", "openrouter"]
  review.openrouter_models   models used for a bare "openrouter" spec
  review.<agent>_model       default model per local CLI (claude, codex, opencode, muse, agy)
Local CLI reviewers run in an empty temporary folder with read-only or plan modes where the CLI
offers one, so they cannot touch the paper.
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
import tempfile
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
LOCAL_AGENTS = ("claude", "codex", "opencode", "muse", "agy")
LEGACY_IDS = {CLAUDE_MODEL_ID: "claude", CODEX_MODEL_ID: "codex"}


def settings() -> dict:
    try:
        home = Path(os.environ.get("MANUWRIGHT_HOME") or Path.home() / ".manuwright")
        return json.loads((home / "config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, RuntimeError):  # RuntimeError: no home directory (bare CI env)
        return {}


def saved_openrouter_key() -> str | None:
    """The key `manuwright setup` saved (owner-only file); the environment variable wins."""
    try:
        home = Path(os.environ.get("MANUWRIGHT_HOME") or Path.home() / ".manuwright")
        data = json.loads((home / "secrets.json").read_text(encoding="utf-8"))
        return data.get("openrouter_api_key") if isinstance(data, dict) else None
    except (OSError, ValueError, RuntimeError):
        return None


def parse_reviewer(spec: str) -> tuple[str, str | None]:
    """'codex' -> ('codex', None); 'opencode:openai/gpt-x' -> ('opencode', 'openai/gpt-x');
    'openrouter:deepseek/x' or a bare OpenRouter id 'deepseek/x' -> ('openrouter', 'deepseek/x')."""
    spec = spec.strip()
    if spec in LEGACY_IDS:
        return LEGACY_IDS[spec], None
    agent, _, model = spec.partition(":")
    if agent in LOCAL_AGENTS or agent == "openrouter":
        return agent, (model or None)
    return "openrouter", spec


def expand_reviewers(specs: list[str], config: dict) -> list[tuple[str, str | None]]:
    """Apply per-agent default models and expand a bare 'openrouter' to the configured list."""
    review = config.get("review", {})
    out: list[tuple[str, str | None]] = []
    for spec in specs:
        agent, model = parse_reviewer(spec)
        if agent == "openrouter" and not model:
            models = review.get("openrouter_models") or load_models(Path(__file__).with_name("critical_models.txt"))
            out += [("openrouter", m) for m in models]
            continue
        out.append((agent, model or review.get(f"{agent}_model")))
    return list(dict.fromkeys(out))


def reviewer_id(agent: str, model: str | None) -> str:
    if agent == "openrouter":
        return model or "openrouter"
    if model is None and agent in ("claude", "codex"):
        return f"{agent}-cli"  # historical ids kept for existing outputs
    return f"{agent}:{model}" if model else agent


def not_independent(reviewers: list[tuple[str, str | None]], main_model: str | None) -> list[str]:
    """Reviewers whose model is the main writing model: their review is not independent."""
    if not main_model:
        return []
    def key(model: str) -> str:  # "anthropic/claude-opus-5.5" and "claude-opus-5-5" are the same model
        return model.lower().rsplit("/", 1)[-1].split(":")[0].replace(".", "-")
    return [reviewer_id(a, m) for a, m in reviewers if m and key(m) == key(main_model)]


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


def call_claude_cli(prompt: str, timeout: int = 240, model: str | None = None) -> str:
    """Run the local Claude Code CLI in headless print mode as a reviewer.

    Lets a non-Claude-Code caller (e.g. Codex or a plain shell) obtain Claude's
    adversarial review by shelling out to `claude -p`. The prompt is piped via
    stdin to avoid command-length limits on large manuscripts.
    """
    proc = subprocess.run(
        ["claude", "-p", "--bare", "--tools", "", "--disallowedTools", "mcp__*"] + (["--model", model] if model else []),
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


def call_codex_cli(prompt: str, timeout: int = 240, model: str | None = None) -> str:
    with tempfile.TemporaryDirectory(prefix="review-") as tmp:
        proc = subprocess.run(["codex", "exec", "--sandbox", "read-only", "--skip-git-repo-check"]
                              + (["-m", model] if model else []) + ["-"], cwd=tmp,
                              input=prompt, text=True, encoding="utf-8", capture_output=True, timeout=timeout)
    if proc.returncode or not proc.stdout.strip():
        raise RuntimeError("codex CLI failed or returned empty output")
    return proc.stdout.strip()


def local_argv(agent: str, model: str | None, prompt_file: Path, workdir: Path) -> tuple[list[str], str | None]:
    """argv and stdin for a local CLI reviewer (claude and codex have their own functions)."""
    if agent == "opencode":  # read-only "plan" agent; any provider/model the user configured
        return (["opencode", "run", "--agent", "plan", "--dir", str(workdir)] + (["-m", model] if model else [])
                + ["-f", str(prompt_file), "--", "Follow the instructions in the attached file. Reply with the review only."], None)
    if agent == "muse":  # no read-only mode: empty workspace, no web tools, no personal context
        return (["muse", "exec", "--prompt-file", str(prompt_file), "--workspace", str(workdir),
                 "--disable-web-tools", "--no-foreign-personal-context"] + (["--model", model] if model else []), None)
    if agent == "agy":  # plan mode inside the sandbox
        return (["agy", "--mode", "plan", "--sandbox"] + (["--model", model] if model else [])
                + ["-p", prompt_file.read_text(encoding="utf-8")], None)
    raise ValueError(f"unknown local reviewer: {agent}")


def call_local_cli(agent: str, prompt: str, model: str | None = None, timeout: int = 900) -> str:
    if agent == "claude":
        return call_claude_cli(prompt, model=model)
    if agent == "codex":
        return call_codex_cli(prompt, model=model)
    # Everything the reviewer needs is in the prompt. Headless CLIs cannot ask for tool permission
    # (agy then exits with no output), so ask for a text-only answer instead of granting tools.
    prompt = ("Everything you need is included below. Do not run tools, shell commands or file reads; "
              "answer in plain text only.\n\n" + prompt)
    with tempfile.TemporaryDirectory(prefix="review-") as tmp:
        prompt_file = Path(tmp) / "review_prompt.md"
        prompt_file.write_text(prompt, encoding="utf-8")
        workdir = Path(tmp) / "work"
        workdir.mkdir()
        argv, stdin = local_argv(agent, model, prompt_file, workdir)
        proc = subprocess.run(argv, cwd=workdir, input=stdin, text=True, encoding="utf-8",
                              capture_output=True, timeout=timeout)
    if proc.returncode or not proc.stdout.strip():
        raise RuntimeError(f"{agent} CLI failed or returned empty output: {proc.stderr.strip()[-300:]}")
    return proc.stdout.strip()


def run_critical_review(
    target_text: str, models: list[str], role: str, api_key: str | None, failures: dict | None = None
) -> dict[str, str]:
    prompt = build_prompt(role, target_text)
    results: dict[str, str] = {}
    for model_id in models:
        agent, model = parse_reviewer(model_id)
        try:
            if model_id == CLAUDE_MODEL_ID:
                results[model_id] = call_claude_cli(prompt)
            elif model_id == CODEX_MODEL_ID:
                results[model_id] = call_codex_cli(prompt)
            elif agent in LOCAL_AGENTS:
                results[model_id] = call_local_cli(agent, prompt, model)
            elif not api_key:
                raise RuntimeError("OPENROUTER_API_KEY not set")
            else:
                results[model_id] = call_model(model, prompt, api_key)
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
    parser.add_argument(
        "--reviewers",
        help="Comma-separated reviewer specs agent[:model]: openrouter:<id>, claude, codex, opencode, muse, agy "
        "(e.g. codex,opencode:openai/gpt-x,openrouter:deepseek/deepseek-v4-pro). Default: review.reviewers "
        "from `manuwright config`.",
    )
    parser.add_argument("--context", type=Path, action="append", default=[], help="Explicit approved review packet/source files (repeatable)")
    parser.add_argument("--out", type=Path, help="Directory to write per-model raw responses")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()

    config = settings()
    specs = [m.strip() for m in (args.reviewers or "").split(",") if m.strip()]
    if args.models:
        specs += [m.strip() for m in args.models.split(",") if m.strip()]
    elif args.models_file:
        specs += load_models(args.models_file)
    if args.include_claude:
        specs.append("claude")
    if args.include_codex:
        specs.append("codex")
    if not specs:
        specs = config.get("review", {}).get("reviewers", [])
    reviewers = expand_reviewers(specs, config)
    models = [reviewer_id(a, m) if a != "openrouter" else m for a, m in reviewers]
    if not models:
        print("error: choose reviewers with --reviewers (or --models/--include-claude/--include-codex), "
              "or set defaults: manuwright config set review.reviewers codex,opencode,openrouter", file=sys.stderr)
        return 2
    flagged = not_independent(reviewers, config.get("main_model"))
    for rid in flagged:
        print(f"warning: reviewer {rid} uses the main writing model ({config.get('main_model')}); "
              "its review is not independent", file=sys.stderr)

    api_key = os.environ.get("OPENROUTER_API_KEY") or saved_openrouter_key()

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
                "sources": sources, "role": args.role, "main_model": config.get("main_model"),
                "not_independent": flagged,
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

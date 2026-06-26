#!/usr/bin/env python3
"""Run all deterministic verification checks in one command (the `/verify` helper).

Wraps `check_citations.py` + `check_numbers.py` + (optionally) `check_gate.py`
and prints a combined PASS/FAIL. Each underlying checker remains the source of
truth; this only orchestrates them so the gate is one command.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def run(script: str, args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script), *args],
        text=True,
        capture_output=True,
    )
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run citation + number (+ optional gate) checks together."
    )
    parser.add_argument("artifacts", nargs="+", help="Manuscript/table markdown files to check.")
    parser.add_argument("--results", default="results", help="results/ directory for number checks.")
    parser.add_argument(
        "--evidence", default="knowledge/evidence.md", help="evidence.md for citation checks."
    )
    parser.add_argument("--gate", help="Optional gate ledger to verify with check_gate.py.")
    parser.add_argument("--artifact", help="Artifact path passed to check_gate.py --artifact.")
    parser.add_argument(
        "--require-check", action="append", default=[], help="Required gate check (repeatable)."
    )
    parser.add_argument(
        "--verify-hash",
        action="append",
        default=[],
        metavar="LABEL=PATH",
        help="Freshness check passed through to check_gate.py. Repeat per tracked file.",
    )
    parser.add_argument(
        "--cross-check",
        action="append",
        default=[],
        metavar="LABEL=PATH",
        help="Ledger-vs-live cross-check passed through to check_gate.py "
        "(LABEL in citation|numbers|revision_claims). Repeat per dimension.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    results: list[tuple[str, int, str]] = []

    rc, out = run("check_citations.py", [*args.artifacts, "--evidence", args.evidence])
    results.append(("citations", rc, out))

    rc, out = run("check_numbers.py", [*args.artifacts, "--results", args.results])
    results.append(("numbers", rc, out))

    if args.gate:
        gate_args = [args.gate]
        if args.artifact:
            gate_args += ["--artifact", args.artifact]
        for check in args.require_check:
            gate_args += ["--require-check", check]
        for item in args.verify_hash:
            gate_args += ["--verify-hash", item]
        for item in args.cross_check:
            gate_args += ["--cross-check", item]
        if args.cross_check:  # share the same sources the live checks used
            gate_args += ["--evidence", args.evidence, "--results", args.results]
        rc, out = run("check_gate.py", gate_args)
        results.append(("gate", rc, out))

    print("=== verify_all ===")
    for name, rc, out in results:
        print(f"\n--- {name}: {'PASS' if rc == 0 else 'FAIL'} ---")
        if out:
            print(out)

    failed = [name for name, rc, _ in results if rc != 0]
    verdict = "PASS" if not failed else f"FAIL ({', '.join(failed)})"
    print(f"\n=== OVERALL: {verdict} ===")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())

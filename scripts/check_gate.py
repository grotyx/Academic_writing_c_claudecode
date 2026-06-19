#!/usr/bin/env python3
"""Verify a phase gate ledger before workflow progression.

This script checks the small key/value gate files under review/gates/. It is
the deterministic stop sign between phases: a gate must record `status: PASS`
and every required check must be present and PASS.
"""

from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path
from typing import NamedTuple


ROOT = Path(__file__).resolve().parents[1]
FIELD_RE = re.compile(r"^([A-Za-z0-9_-]+):\s*(.*?)\s*$")
CHECK_RE = re.compile(r"^\s{2,}([A-Za-z0-9_-]+):\s*(.*?)\s*$")
# Top-level keys whose indented children form a nested key/value block.
NESTED_BLOCKS = ("checks", "provenance")


class GateEntry(NamedTuple):
    fields: dict[str, str]
    checks: dict[str, str]
    provenance: dict[str, str]


class GateIssue(NamedTuple):
    gate: Path
    field: str
    reason: str
    required_action: str


class GateCheckResult(NamedTuple):
    passed: bool
    failures: list[GateIssue]
    entry: GateEntry | None


def normalize_key(value: str) -> str:
    return value.strip().casefold().replace("-", "_").replace(" ", "_")


def normalize_status(value: str) -> str:
    return value.strip().upper()


def strip_inline_comment(value: str) -> str:
    # Gate fields may carry a trailing "# ..." annotation, e.g.
    # "status: PASS  # PASS | FAIL" or "round: 2  # max 2 attempts".
    # Keep only the value before the comment marker.
    return value.split("#", 1)[0].strip()


def sha256_file(path: Path) -> str:
    """Return the lowercase hex sha256 of a file, read in chunks."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_gate_entry(text: str) -> GateEntry:
    fields: dict[str, str] = {}
    checks: dict[str, str] = {}
    provenance: dict[str, str] = {}
    current_block: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#") or line.lstrip().startswith(">"):
            continue

        top_match = FIELD_RE.match(line)
        if top_match and not raw_line.startswith((" ", "\t")):
            key = normalize_key(top_match.group(1))
            value = strip_inline_comment(top_match.group(2))
            fields[key] = value
            current_block = key if key in NESTED_BLOCKS else None
            continue

        if current_block:
            nested_match = CHECK_RE.match(line)
            if nested_match:
                nested_key = normalize_key(nested_match.group(1))
                nested_value = strip_inline_comment(nested_match.group(2))
                if current_block == "checks":
                    checks[nested_key] = normalize_status(nested_value)
                else:  # provenance: keep the raw value (hex digest)
                    provenance[nested_key] = nested_value
                continue

            if raw_line and not raw_line.startswith((" ", "\t")):
                current_block = None

    return GateEntry(fields=fields, checks=checks, provenance=provenance)


def phase_code_from_path(gate_path: Path) -> str:
    stem = gate_path.name
    if stem.endswith(".GATE.md"):
        stem = stem[: -len(".GATE.md")]
    else:
        stem = gate_path.stem
    return normalize_key(stem).upper()


def check_gate(
    gate_path: Path,
    *,
    required_checks: list[str] | None = None,
    artifact: str | None = None,
    max_round: int = 2,
    verify_hashes: list[tuple[str, Path]] | None = None,
    base_dir: Path | None = None,
) -> GateCheckResult:
    failures: list[GateIssue] = []
    if not gate_path.exists():
        return GateCheckResult(
            False,
            [
                GateIssue(
                    gate_path,
                    "<file>",
                    "gate file not found",
                    "Create the gate ledger file under review/gates/ and rerun phase verification.",
                )
            ],
            None,
        )

    entry = parse_gate_entry(gate_path.read_text(encoding="utf-8"))
    status = normalize_status(entry.fields.get("status", ""))
    if status != "PASS":
        reason = f"status is {status or 'missing'}"
        failures.append(
            GateIssue(
                gate_path,
                "status",
                reason,
                "Record status: PASS only after all verifier outputs pass.",
            )
        )

    if artifact is not None:
        recorded_artifact = entry.fields.get("artifact", "")
        if recorded_artifact != artifact:
            failures.append(
                GateIssue(
                    gate_path,
                    "artifact",
                    f"artifact mismatch: expected {artifact}, found {recorded_artifact or '<missing>'}",
                    "Use the gate file for the requested artifact or correct the artifact field.",
                )
            )

    if max_round:
        raw_round = entry.fields.get("round", "")
        try:
            round_number = int(raw_round)
        except ValueError:
            round_number = 0
        if round_number > max_round:
            failures.append(
                GateIssue(
                    gate_path,
                    "round",
                    f"round {round_number} exceeds max {max_round}",
                    "Escalate to the user after the allowed fix/re-verify attempts.",
                )
            )

    for required_check in required_checks or []:
        check_key = normalize_key(required_check)
        check_status = entry.checks.get(check_key)
        if check_status is None:
            failures.append(
                GateIssue(
                    gate_path,
                    f"checks.{check_key}",
                    f"required check {check_key} is missing",
                    f"Run the {check_key} verifier and record checks: {check_key}: PASS.",
                )
            )
            continue
        if check_status != "PASS":
            failures.append(
                GateIssue(
                    gate_path,
                    f"checks.{check_key}",
                    f"required check {check_key} is {check_status}",
                    f"Fix the {check_key} failure and rerun the verifier before proceeding.",
                )
            )

    # Freshness / provenance: a PASS is only valid for the artifact state it was
    # recorded against. Re-hash each tracked file and compare to the digest the
    # gate stored under `provenance:`. A mismatch means the file changed after the
    # PASS (stale gate) -- the verifiers must run again.
    for label, file_path in verify_hashes or []:
        prov_key = normalize_key(label)
        recorded = entry.provenance.get(prov_key)
        if recorded is None:
            failures.append(
                GateIssue(
                    gate_path,
                    f"provenance.{prov_key}",
                    f"freshness hash for {prov_key} is not recorded",
                    f"Record provenance: {prov_key}: <sha256> when the gate passes, then rerun.",
                )
            )
            continue

        resolved = file_path
        if not resolved.is_absolute():
            resolved = (base_dir or Path.cwd()) / resolved
        if not resolved.exists():
            failures.append(
                GateIssue(
                    gate_path,
                    f"provenance.{prov_key}",
                    f"cannot verify freshness: {resolved} not found",
                    f"Point --verify-hash {prov_key}=<path> at the file that was verified.",
                )
            )
            continue

        recorded_hex = recorded.split(":", 1)[-1].strip().casefold()
        actual_hex = sha256_file(resolved).casefold()
        if actual_hex != recorded_hex:
            failures.append(
                GateIssue(
                    gate_path,
                    f"provenance.{prov_key}",
                    f"stale gate: {prov_key} changed since PASS "
                    f"(recorded {recorded_hex[:12]}, now {actual_hex[:12]})",
                    f"Re-run the verifiers against the current {prov_key} and update the gate.",
                )
            )

    return GateCheckResult(not failures, failures, entry)


def format_result(result: GateCheckResult, gate_path: Path) -> str:
    phase_code = phase_code_from_path(gate_path)
    if result.passed:
        checks = ", ".join(sorted(result.entry.checks)) if result.entry else ""
        return "\n".join(
            [
                "GATE PASS",
                "verifier: Phase-Gate-Ledger",
                f"gate: {gate_path}",
                f"phase_code: {phase_code}",
                f"status: {result.entry.fields.get('status', '') if result.entry else ''}",
                f"checks: {checks}",
            ]
        )

    lines = [
        "GATE FAIL",
        f"failure_code: GATE_FAIL {phase_code}",
        "verifier: Phase-Gate-Ledger",
        f"gate: {gate_path}",
        f"failures: {len(result.failures)}",
    ]
    for failure in result.failures:
        lines.extend(
            [
                "---",
                f"field: {failure.field}",
                f"reason: {failure.reason}",
                f"required_action: {failure.required_action}",
            ]
        )
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify a review/gates phase ledger file.")
    parser.add_argument(
        "gate",
        type=Path,
        nargs="?",
        help="Gate ledger path, e.g. review/gates/phase_04_draft.GATE.md",
    )
    parser.add_argument(
        "--require-check",
        action="append",
        default=[],
        help="Required check name that must be recorded as PASS. Repeat for multiple checks.",
    )
    parser.add_argument("--artifact", help="Artifact path that must match the gate artifact field.")
    parser.add_argument("--max-round", type=int, default=2, help="Maximum allowed fix/re-verify round.")
    parser.add_argument(
        "--verify-hash",
        action="append",
        default=[],
        metavar="LABEL=PATH",
        help="Freshness check: verify sha256(PATH) equals the gate's provenance.<LABEL>. "
        "Repeat per tracked file, e.g. --verify-hash artifact=drafts/05_results.md.",
    )
    parser.add_argument(
        "--compute-hash",
        type=Path,
        metavar="PATH",
        help="Print the sha256 of PATH and exit (use to fill provenance fields).",
    )
    return parser


def parse_verify_hash(items: list[str], parser: argparse.ArgumentParser) -> list[tuple[str, Path]]:
    pairs: list[tuple[str, Path]] = []
    for item in items:
        if "=" not in item:
            parser.error(f"--verify-hash expects LABEL=PATH, got {item!r}")
        label, path_str = item.split("=", 1)
        label = label.strip()
        path_str = path_str.strip()
        if not label or not path_str:
            parser.error(f"--verify-hash expects LABEL=PATH, got {item!r}")
        pairs.append((label, Path(path_str)))
    return pairs


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.compute_hash is not None:
        print(sha256_file(args.compute_hash))
        return 0

    if args.gate is None:
        parser.error("the following arguments are required: gate (unless --compute-hash is used)")

    verify_hashes = parse_verify_hash(args.verify_hash, parser)
    result = check_gate(
        args.gate,
        required_checks=args.require_check,
        artifact=args.artifact,
        max_round=args.max_round,
        verify_hashes=verify_hashes,
    )
    print(format_result(result, args.gate))
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

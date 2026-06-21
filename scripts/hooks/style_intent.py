#!/usr/bin/env python3
"""UserPromptSubmit hook: auto-trigger the style-pass protocol on intent.

When the user's prompt asks to transform text toward academic / journal style
("이 초안 학술적으로 바꿔줘", "make it academic", "저널 스타일로 다듬어줘"), this
injects a short instruction so Claude follows the style-pass protocol (load the
Style Spec + bound exemplar, go section-by-section, run the Style Verifier)
instead of free-handing an abstract "academic style".

It only fires when BOTH a style cue AND a transform/action verb are present, so it
stays quiet on questions *about* academic writing or on reference searches.

Mechanism: prints the instruction to stdout (exit 0) -- for a UserPromptSubmit hook
Claude adds non-empty stdout to the prompt context. It NEVER blocks the prompt and
FAILS OPEN (exit 0) on any error.
"""

from __future__ import annotations

import json
import re
import sys

# Style cue -- Korean + English. `학술` covers 학술적/학술논문/학술적으로.
TRIGGERS = [
    r"학술",
    r"저널\s*스타일",
    r"논문\s*체",
    r"논문\s*스타일",
    r"academic",
    r"journal\s*style",
]

# Transform / action verb -- required so we do not fire on "학술논문 검색" or
# "what is academic writing".
ACTIONS = [
    r"바꿔", r"바꾸", r"변경", r"수정", r"고쳐", r"고치", r"다듬", r"맞게",
    r"적용", r"써", r"쓰", r"작성", r"정리",
    r"rewrite", r"revise", r"transform", r"convert", r"polish",
    r"make\s+it", r"apply",
]

INJECTION = (
    "[style-pass auto-trigger] The user is asking to transform text toward academic/"
    "journal style. Do NOT free-hand 'academic style'. Follow the style-pass protocol "
    "(docs/style_transform_protocol.md): (1) load the project Style Spec "
    "(drafts/**/style_spec.md) + its bound exemplar (Style/own or Style/target_journal) "
    "+ the matching writing_guide section rules; if no Style Spec exists, offer to create "
    "one from a chosen anchor first; (2) confirm the target scope with the user; "
    "(3) transform section-by-section; (4) run the Style Verifier on each section "
    "(auto-fix loop, max 2). Run /style-pass for the full procedure."
)


def detect(prompt: str) -> bool:
    if not prompt:
        return False
    low = prompt.lower()
    has_style = any(re.search(p, low) for p in TRIGGERS)
    if not has_style:
        return False
    return any(re.search(a, low) for a in ACTIONS)


def evaluate(event: dict) -> str:
    """Return the injection text on intent, else empty string. Pure for testing."""
    return INJECTION if detect(event.get("prompt") or "") else ""


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")  # Claude Code emits UTF-8 JSON; Windows default is cp949
    except Exception:
        pass
    try:
        event = json.loads(sys.stdin.read() or "{}")
    except Exception:
        return 0  # fail open
    try:
        out = evaluate(event)
    except Exception:
        return 0  # fail open
    if out:
        sys.stdout.write(out + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

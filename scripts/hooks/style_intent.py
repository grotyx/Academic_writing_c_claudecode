#!/usr/bin/env python3
"""UserPromptSubmit hook: auto-trigger the style-pass protocol on intent.

When the user's prompt asks to transform text toward academic / journal style
("이 초안 학술적으로 바꿔줘", "make it academic", "저널 스타일로 다듬어줘"), this
injects a short instruction so Claude follows the style-pass protocol (load the
Style Spec + bound exemplar, go section-by-section, run the Style Verifier)
instead of free-handing an abstract "academic style".

It only fires when BOTH a style cue AND a transform/action verb are present, so it
stays quiet on questions *about* academic writing or on reference searches.

It also stays quiet when the prompt is about the tool itself (programs, modes, features,
hooks, updates): that is a discussion of the engine, not a request to rewrite text.

Drafting: when the prompt asks to write or rewrite a named section ("서론 써줘", "draft the
Discussion", "04_methods.md 작성") and the academic writing mode is on, the matching section
card (scripts/academic_style.py: moves, phrasebank, model paragraphs, learned style) is
injected, so the section is written in that register from the first draft.

Mode toggle: "학술 모드 꺼줘", "academic mode strict", "학술 모드 켜줘" set the academic writing mode
(saved in ~/.manuwright/config.json) without leaving the conversation.

Reinforcement: inside a paper folder, with the mode on, every prompt gets a one-line reminder of
the register (as caveman does), so long sessions and compaction do not drift back to chat prose.

Mechanism: prints the instruction to stdout (exit 0) -- for a UserPromptSubmit hook
Claude adds non-empty stdout to the prompt context. It NEVER blocks the prompt and
FAILS OPEN (exit 0) on any error.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

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

SEARCH = re.compile(r"검색|찾아|search|look\s*up|\bfind\b|병원|학회|hospital|conference", re.IGNORECASE)
STYLE_ADVERB = re.compile(r"학술\s*적|학술\s*체|academically|academic\s+(?:style|tone|register|english)", re.IGNORECASE)

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


# Talk about the engine itself ("이 프로그램에 학술 모드를 만들 수 있을까") is not a request to rewrite text.
META = re.compile(r"프로그램|모드|기능|스킬|플러그인|훅|업데이트|구현|program|\bmodes?\b|feature|\bskills?\b"
                  r"|plugin|\bhooks?\b|implement", re.IGNORECASE)

SECTION_WORDS = {
    "title": r"(?<!그림 )(?<!그림)(?<!표 )(?<!표)제목|(?<!figure )(?<!table )\btitle\b",  # not a figure or table title
    "abstract": r"초록|\babstract\b",
    "introduction": r"서론|도입부|introduction|\bintro\b",
    # bare 방법/결과 count only right before a drafting verb ("결과 써줘", "방법을 다시 써줘")
    "methods": r"방법\s*(?:섹션|파트|부분|론)|재료\s*(?:및|와)\s*방법|방법\s*(?:을|를)?\s*(?:다시\s*)?(?:써|작성|정리)|\bmethods?\b",
    "results": r"결과\s*(?:섹션|파트|부분)|결과\s*(?:를|을)?\s*(?:다시\s*)?(?:써|작성|정리)|\bresults\b",
    "discussion": r"고찰|\bdiscussion\b",
    "conclusion": r"결론|\bconclusions?\b",
}
SECTION_FILE = re.compile(r"\b0([1-7])_[a-z_]*\.md\b")
FILE_SECTIONS = {"1": "title", "2": "abstract", "3": "introduction", "4": "methods", "5": "results",
                 "6": "discussion", "7": "conclusion"}
DRAFT_VERBS = re.compile(r"써|쓰|작성|초안|다시|고쳐|수정|다듬|정리|만들|보완|바꿔|후보|추천|제안|draft|write|rewrite|revise|suggest", re.IGNORECASE)
MAX_CARDS = 2


def requested_sections(prompt: str) -> list:
    """Sections the prompt asks to draft or rewrite (at most MAX_CARDS), in order of mention."""
    if not prompt or META.search(prompt) or not DRAFT_VERBS.search(prompt):
        return []
    low = prompt.lower()
    hits = [(m.start(), FILE_SECTIONS[m.group(1)]) for m in SECTION_FILE.finditer(low)]
    plain = re.sub(r"\S*[/\\_@]\S*", " ", low)
    for section, pattern in SECTION_WORDS.items():
        match = re.search(pattern, plain, re.IGNORECASE)
        if match:
            hits.append((match.start(), section))
    return list(dict.fromkeys(section for _, section in sorted(hits)))[:MAX_CARDS]


def draft_cards(prompt: str, cwd: str | None = None) -> str:
    sections = requested_sections(prompt)
    if not sections:
        return ""
    academic_style = _academic()
    project = Path(cwd) if cwd else None
    # Only inside a paper folder: in other projects "write the results parser" is not a manuscript.
    if academic_style.mode() == "off" or not academic_style.in_paper(project):
        return ""
    return "\n\n".join(academic_style.card(section, project) for section in sections)


def detect(prompt: str) -> bool:
    if not prompt or META.search(prompt):
        return False
    # Drop paths, URLs and identifiers before matching: pasted logs carry the repository name
    # (Academic_writing_...) and lines like "Restart to apply changes", which are not a request.
    low = re.sub(r"\S*[/\\_@]\S*", " ", prompt.lower())
    has_style = any(re.search(p, low) for p in TRIGGERS)
    if not has_style:
        return False
    # "학술 검색해서 정리해줘" asks for a literature search, not for a rewrite.
    if SEARCH.search(low) and not STYLE_ADVERB.search(low):
        return False
    return any(re.search(a, low) for a in ACTIONS)


# Anchored at the start: "학술 모드 꺼줘", "please turn academic mode off"; a statement such as
# "I turned academic mode off" or "현재 학술 모드는 off" is not a request.
MODE_WORDS = (r"^(?:(?:이제|그럼|다시|please|now|turn|set|switch)\s+)*(?:학술|academic)\s*(?:문체|writing)?\s*(?:모드|mode)"
              r"\s*(?:를|을)?\s*(?:to\s+)?")
END = r"\s*(?:요|please)?[.!\s]*$"
MODE_TOGGLES = (
    ("off", re.compile(MODE_WORDS + r"(?:꺼\s*줘|꺼\s*주세요|꺼|끄기|끄자|해제(?:해\s*줘|해)?|중지(?:해\s*줘|해)?|off)" + END,
                       re.IGNORECASE)),
    ("strict", re.compile(MODE_WORDS + r"(?:strict|엄격(?:하게)?(?:\s*해\s*줘|\s*해|\s*모드로(?:\s*해\s*줘)?)?)" + END,
                          re.IGNORECASE)),
    ("academic", re.compile(MODE_WORDS + r"(?:(?:다시\s*)?켜\s*줘|(?:다시\s*)?켜\s*주세요|켜|켜기|on|academic)" + END,
                            re.IGNORECASE)),
)
# A question, a negation, a condition or a long pasted text is never a switch request
# ("학술 모드 꺼지면 어떻게 돼?", "학술 모드 끄지 마", a log that quotes the phrase).
NOT_A_REQUEST = re.compile(r"\?|뭐|어떻게|왜|무엇|지\s*마|말고|않|면(?:\s|$|,)|\bnot\b|\bdon'?t\b|\bwhat\b|\bhow\b",
                           re.IGNORECASE)


def mode_toggle(prompt: str) -> str | None:
    """'학술 모드 꺼줘' / 'academic mode strict' / '학술 모드 켜줘' -> the mode; anything else -> None."""
    text = (prompt or "").strip()
    if not text or len(text) > 60 or NOT_A_REQUEST.search(text):
        return None
    return next((value for value, pattern in MODE_TOGGLES if pattern.search(text)), None)


def _academic():
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import academic_style

    return academic_style


def evaluate(event: dict) -> str:
    """Return the injection text on intent, else empty string. Pure for testing."""
    prompt = event.get("prompt") or ""
    toggle = mode_toggle(prompt)
    if toggle:
        try:
            academic = _academic()
            academic.set_mode(toggle)
            effective = academic.mode()
            if effective != toggle:  # MANUWRIGHT_WRITING_MODE in the environment wins over the saved setting
                return (f"[manuwright] Saved academic writing mode '{toggle}', but the environment variable "
                        f"MANUWRIGHT_WRITING_MODE={effective} overrides it, so '{effective}' stays in effect. Tell the "
                        "user in one line, and that removing that variable makes the saved setting apply.")
            return (f"[manuwright] Academic writing mode is now '{toggle}' for every paper and session "
                    "(`manuwright mode` shows it). Confirm this to the user in one line.")
        except Exception:
            return ""
    parts = [INJECTION] if detect(prompt) else []
    try:
        cards = draft_cards(prompt, event.get("cwd"))
    except Exception:
        cards = ""  # fail open: a missing card never blocks the prompt
    if cards:
        parts.append(cards)
    try:  # caveman-style per-turn reinforcement, only inside a paper folder and only when no card went in
        academic = _academic()
        if not cards and academic.mode() != "off" and academic.in_paper(Path(event["cwd"]) if event.get("cwd") else None):
            parts.append(academic.reminder())
    except Exception:
        pass
    return "\n\n".join(parts)


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

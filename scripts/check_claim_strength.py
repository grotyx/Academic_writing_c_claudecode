#!/usr/bin/env python3
"""Overclaim check: is each cited sentence worded no more strongly than its evidence allows?

An evidence.md entry may carry
    - **Claim Strength:** speculative | observed | supported | strong
    - **Allowed Wording:** was associated with; suggests        (optional, free text)
(idea from claude-scholar's claim schema). Every manuscript sentence that cites [EVID:id] is graded
by its strongest verb:

    hedged      may, might, could, suggest, hypothesize, possibly ...
    associative was associated with, observed, reported, correlated, found ...
    directional showed, reduced, improved, increased, lowered, was higher/lower ...
    causal      demonstrated, proved, established, confirmed, caused, prevented, is effective ...

and compared with the most permissive strength among the entries it cites:

    speculative -> hedged only
    observed    -> hedged or associative
    supported   -> up to directional
    strong      -> anything

Entries without a recognised Claim Strength are not checked. Advisory by default; exit 1 when any
sentence overclaims (use it as a gate if you want one).

    python scripts/check_claim_strength.py drafts/06_discussion.md --evidence knowledge/evidence.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_citations import EVID_RE, parse_evidence_entries, strip_code_fences  # noqa: E402
from check_style import split_sentences  # noqa: E402

LEVELS = ('hedged', 'associative', 'directional', 'causal')
ALLOWED = {'speculative': 0, 'observed': 1, 'supported': 2, 'strong': 3}
_I = re.IGNORECASE
VERBS = {
    3: re.compile(r"\b(?:demonstrat(?:e|es|ed|ing)|prov(?:e|es|ed|en)|establish(?:es|ed)?|confirm(?:s|ed)?|caus(?:e|es|ed)"
                  r"|prevent(?:s|ed)?|eliminat(?:e|es|ed)|leads? to|led to|results? in|is (?:effective|superior|safe and effective)"
                  r"|definitive(?:ly)?|clearly (?:show|shows|showed))\b", _I),
    2: re.compile(r"\b(?:show(?:s|ed|n)?|reduc(?:e|es|ed)|improv(?:e|es|ed)|increas(?:e|es|ed)|decreas(?:e|es|ed)|lower(?:s|ed)?"
                  r"|rais(?:e|es|ed)|enhanc(?:e|es|ed)|outperform(?:s|ed)?|(?:was|were|is|are) (?:higher|lower|better|worse|"
                  r"greater|shorter|longer))\b", _I),
    1: re.compile(r"\b(?:associated with|association|observ(?:e|es|ed)|report(?:s|ed)?|correlat(?:e|es|ed|ion)|found|noted"
                  r"|linked to|related to)\b", _I),
}
HEDGE = re.compile(r"\b(?:may|might|could|possibl[ey]|potential(?:ly)?|suggest(?:s|ed|ing)?|hypothes\w+|appear(?:s|ed)? to"
                   r"|seem(?:s|ed)? to|perhaps)\b", _I)


ASSOCIATION = re.compile(r"\b(?:associated with|association (?:between|with)|correlated with|linked to)\b", _I)


def sentence_level(sentence: str) -> int:
    """0 hedged .. 3 causal: the strongest verb in the sentence. A hedge, or an explicit association
    ("was associated with lower rates"), caps the claim at associative."""
    level = next((lvl for lvl in (3, 2, 1) if VERBS[lvl].search(sentence)), 0)
    if HEDGE.search(sentence) or (ASSOCIATION.search(sentence) and level < 3):
        return min(level, 1)
    return level


def strength_of(entry) -> int | None:
    value = (entry.fields.get('claim_strength') or '').strip().lower().split()[:1]
    return ALLOWED.get(value[0]) if value else None


def check(paths: list[Path], evidence: Path) -> list[tuple[Path, int, str]]:
    entries = parse_evidence_entries(evidence.read_text(encoding='utf-8'))
    findings = []
    for path in paths:
        text = strip_code_fences(path.read_text(encoding='utf-8', errors='replace'))
        for number, line in enumerate(text.splitlines(), start=1):
            if '[EVID:' not in line:
                continue
            for sentence in split_sentences(line):
                ids = EVID_RE.findall(sentence)
                strengths = [s for s in (strength_of(entries[i]) for i in ids if i in entries) if s is not None]
                if not strengths:
                    continue
                allowed, level = max(strengths), sentence_level(sentence)
                wordings = [w.strip().lower() for i in ids if i in entries
                            for w in re.split(r'[;,]', entries[i].fields.get('allowed_wording', '')) if w.strip()]
                if any(w in sentence.lower() for w in wordings) and level < 3:
                    continue  # written with the entry's own allowed wording
                if level > allowed:
                    names = {v: k for k, v in ALLOWED.items()}
                    wording = '; '.join(entries[i].fields.get('allowed_wording', '') for i in ids if i in entries
                                        and entries[i].fields.get('allowed_wording'))
                    findings.append((path, number, (
                        f'{LEVELS[level]} wording for {names[allowed]} evidence ({", ".join(ids)}): '
                        f'"{sentence.strip()[:90]}"' + (f'; allowed wording: {wording}' if wording else ''))))
    return findings


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    parser = argparse.ArgumentParser(prog='manuwright claim-strength',
                                     description='Flag cited sentences worded more strongly than their evidence.')
    parser.add_argument('files', nargs='+')
    parser.add_argument('--evidence', default='knowledge/evidence.md')
    args = parser.parse_args(argv)
    paths = [p for f in args.files for p in (sorted(Path(f).rglob('*.md')) if Path(f).is_dir() else [Path(f)])]
    findings = check(paths, Path(args.evidence))
    for path, line, message in findings:
        print(f'[OVERCLAIM] {path}:{line} {message}')
    print(f'{len(findings)} overclaim(s).' if findings else 'OK: every cited sentence is within its evidence strength.')
    return 1 if findings else 0


if __name__ == '__main__':
    raise SystemExit(main())

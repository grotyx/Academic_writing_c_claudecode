#!/usr/bin/env python3
"""Letter-blind re-review for a revision: judge the manuscript change before the authors' framing.

A reviewer (human or verifier agent) who reads the response letter together with the diff is pulled
toward the authors' account. This splits the Response-alignment check into three recorded phases
(idea from academic-research-skills' re-review protocol; reimplemented, no text copied):

  Phase 1  expectation   for each reviewer comment, before seeing the revision: what "fully
                         addressed" would look like in the manuscript.
  Phase 2A blind verdict  the original and revised sections and their diff, WITHOUT the response
                         letter: FULLY | PARTIALLY | NOT_ADDRESSED | MADE_WORSE | CANNOT_VERIFY,
                         each with an anchor (file and quoted text) in the revised manuscript.
  Phase 2B final verdict  the letter is revealed. A final verdict that differs from the blind one
                         needs a basis: author_pointer (the letter pointed to evidence the blind
                         read missed), valid_rebuttal, or scope_correction.
  New issues are tagged regression (introduced by the revision) or previously_missed (cannot change
  the decision: no moving goalposts).

  packet  --comments review/reviewer_comments_REV1.md --original drafts --revised drafts/revision/REV1
          --out review/blind_REV1
      writes the blind packet (comments, original and revised sections, diffs, no response letter)
      and a verdict record template with one block per comment.
  check   review/blind_REV1/verdicts.md
      validates the record: every comment has an expectation, a blind verdict with an anchor, a
      final verdict, a basis for every changed verdict, and tagged new issues. Exit 0 = PASS (no
      final NOT_ADDRESSED, MADE_WORSE or CANNOT_VERIFY), else 1. Record response_alignment PASS in the
      phase 8 gate only after this passes.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_response_coverage import parse_original_comments  # noqa: E402

VERDICTS = ('FULLY', 'PARTIALLY', 'NOT_ADDRESSED', 'MADE_WORSE', 'CANNOT_VERIFY')
PASSING = ('FULLY', 'PARTIALLY')
BASES = ('author_pointer', 'valid_rebuttal', 'scope_correction')
LETTER = re.compile(r'response|rebuttal|letter', re.IGNORECASE)
BLOCK = re.compile(r'^##\s+(R\d+-C\d+)\s*$', re.MULTILINE)
FIELD = re.compile(r'^([a-z_]+):[ \t]*(.*)$', re.MULTILINE)


def section_key(path: Path) -> str:
    """05_results_REV1.md and 05_results.md -> 05_results."""
    return re.sub(r'_REV\d+$', '', path.stem, flags=re.IGNORECASE)


def comment_ids(comments: Path) -> list[str]:
    return [f'R{r}-C{c}' for r, c in sorted(parse_original_comments(comments.read_text(encoding='utf-8')))]


def packet(comments: Path, original: Path, revised: Path, out: Path) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(comments, out / 'reviewer_comments.md')
    originals = {section_key(p): p for p in sorted(original.glob('0[1-9]_*.md'))}
    files = []
    for new in sorted(revised.glob('0[1-9]_*.md')):
        if LETTER.search(new.name):
            continue
        key = section_key(new)
        old = originals.get(key)
        (out / 'revised').mkdir(exist_ok=True)
        shutil.copyfile(new, out / 'revised' / new.name)
        if old:
            (out / 'original').mkdir(exist_ok=True)
            shutil.copyfile(old, out / 'original' / old.name)
            diff = difflib.unified_diff(old.read_text(encoding='utf-8').splitlines(),
                                        new.read_text(encoding='utf-8').splitlines(),
                                        fromfile=old.name, tofile=new.name, lineterm='')
            (out / 'diffs').mkdir(exist_ok=True)
            (out / 'diffs' / f'{key}.diff').write_text('\n'.join(diff) + '\n', encoding='utf-8')
        files.append(new.name)
    ids = comment_ids(comments)
    blocks = [f'## {cid}\nexpectation: \nblind_verdict: \nanchor: \nfinal_verdict: \nbasis: \nnew_issue: none\n'
              for cid in ids]
    template = ('# Letter-blind re-review record\n\n'
                'Phase 1: fill every `expectation` before opening revised/ or diffs/.\n'
                'Phase 2A: fill `blind_verdict` (' + ' | '.join(VERDICTS) + ') and `anchor` (file: "quoted text") '
                'from original/, revised/ and diffs/ only.\n'
                'Phase 2B: then read the response letter and fill `final_verdict`; if it differs from the blind '
                'verdict, `basis` must be one of ' + ', '.join(BASES) + '.\n'
                '`new_issue`: none, or "regression: ..." / "previously_missed: ...".\n\n' + '\n'.join(blocks))
    verdicts = out / 'verdicts.md'
    if not verdicts.exists():
        verdicts.write_text(template, encoding='utf-8')
    manifest = {'comments': ids, 'revised_sections': files,
                'sha256': {str(p.relative_to(out)): hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(out.rglob('*')) if p.is_file() and p.name not in ('verdicts.md', 'packet.json')}}
    (out / 'packet.json').write_text(json.dumps(manifest, indent=1), encoding='utf-8')
    return manifest


def parse_record(text: str) -> dict:
    matches = list(BLOCK.finditer(text))
    record = {}
    for i, match in enumerate(matches):
        body = text[match.end():matches[i + 1].start() if i + 1 < len(matches) else len(text)]
        record[match.group(1)] = {k: v.strip() for k, v in FIELD.findall(body)}
    return record


def check(verdicts: Path) -> list[str]:
    folder = verdicts.parent
    problems = []
    manifest_path = folder / 'packet.json'
    if not manifest_path.is_file():
        return [f'{manifest_path} missing: build the packet with `blind_review.py packet` first']
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    leaked = [name for name in manifest.get('sha256', {}) if LETTER.search(Path(name).name)
              and name != 'reviewer_comments.md']
    problems += [f'packet contains {name}: the blind phase must not see the response letter' for name in leaked]
    record = parse_record(verdicts.read_text(encoding='utf-8'))
    for cid in manifest.get('comments', []):
        entry = record.get(cid)
        if entry is None:
            problems.append(f'{cid}: no block in {verdicts.name}')
            continue
        if not entry.get('expectation'):
            problems.append(f'{cid}: Phase 1 expectation is empty')
        blind, final = entry.get('blind_verdict', '').upper(), entry.get('final_verdict', '').upper()
        if blind not in VERDICTS:
            problems.append(f'{cid}: blind_verdict must be one of {", ".join(VERDICTS)}')
        elif blind != 'CANNOT_VERIFY' and not entry.get('anchor'):
            problems.append(f'{cid}: blind verdict {blind} needs an anchor in the revised manuscript')
        if final not in VERDICTS:
            problems.append(f'{cid}: final_verdict must be one of {", ".join(VERDICTS)}')
        elif blind in VERDICTS and final != blind and entry.get('basis', '').split(':')[0].strip() not in BASES:
            problems.append(f'{cid}: verdict changed {blind} -> {final} after reading the letter without a basis '
                            f'({", ".join(BASES)})')
        elif final not in PASSING:
            problems.append(f'{cid}: final verdict {final}')
        issue = entry.get('new_issue', 'none').strip().lower()
        if issue not in ('', 'none') and not issue.startswith(('regression:', 'previously_missed:')):
            problems.append(f'{cid}: new_issue must be none, "regression: ..." or "previously_missed: ..."')
        elif issue.startswith('regression:'):
            problems.append(f'{cid}: regression introduced by the revision: {entry["new_issue"][11:].strip()}')
    return problems


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    parser = argparse.ArgumentParser(description='Letter-blind re-review packet and record check')
    sub = parser.add_subparsers(dest='action', required=True)
    pk = sub.add_parser('packet')
    pk.add_argument('--comments', required=True)
    pk.add_argument('--original', default='drafts')
    pk.add_argument('--revised', required=True)
    pk.add_argument('--out', required=True)
    ck = sub.add_parser('check')
    ck.add_argument('verdicts')
    args = parser.parse_args(argv)
    if args.action == 'packet':
        manifest = packet(Path(args.comments), Path(args.original), Path(args.revised), Path(args.out))
        print(f"Blind packet: {args.out} ({len(manifest['comments'])} comments, "
              f"{len(manifest['revised_sections'])} revised sections; response letter withheld).")
        print(f'Fill {Path(args.out) / "verdicts.md"} phase by phase, then: blind_review.py check '
              f'{Path(args.out) / "verdicts.md"}')
        return 0
    problems = check(Path(args.verdicts))
    for problem in problems:
        print(f'FAIL: {problem}')
    print('PASS: letter-blind re-review complete; record response_alignment in the phase 8 gate.' if not problems
          else f'{len(problems)} problem(s).')
    return 1 if problems else 0


if __name__ == '__main__':
    raise SystemExit(main())

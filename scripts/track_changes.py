#!/usr/bin/env python3
"""Tracked-changes Word file: the previous manuscript against the revised one (Word revisions).

    manuwright track-changes OLD.md NEW.md -o output/manuscript_REV1_tracked.docx

OLD and NEW are Markdown: best, the merged `manuscript_*.md` of two builds (the one you submitted and the
revised one), so the citation numbers and references are compared as the journal saw them. Headings and
paragraphs are compared in order; a changed paragraph shows as the old one deleted and the new one inserted.
"Accept all changes" in Word gives NEW, "Reject all changes" gives OLD. Tables are not tracked (they are
separate files); a file with a table is refused. Inside a paper folder the paper's Word style is used.

For a revision build, set "tracked_baseline" in project.json to the submitted manuscript_*.md; `manuwright
build` then writes manuscript_REVn_..._tracked.docx next to the clean one.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    parser = argparse.ArgumentParser(prog='manuwright track-changes', description=__doc__.split('\n\n')[0])
    parser.add_argument('old')
    parser.add_argument('new')
    parser.add_argument('-o', '--out', required=True, help='the .docx to write')
    parser.add_argument('--project', help='project.json for the Word style (default: the paper folder you are in)')
    args = parser.parse_args(argv)
    from harness import tracked
    from harness.build import DOCX_DEFAULTS, docx_style
    style = DOCX_DEFAULTS
    start = Path(args.project).resolve().parent if args.project else Path.cwd().resolve()
    manifest = next((p / 'project.json' for p in [start, *start.parents] if (p / 'project.json').is_file()), None)
    try:
        if manifest:
            style = docx_style(json.loads(manifest.read_text(encoding='utf-8')), manifest.parent)
        old = Path(args.old).read_text(encoding='utf-8')
        new = Path(args.new).read_text(encoding='utf-8')
        out = Path(args.out)
        if out.suffix.lower() != '.docx':
            raise ValueError('the output must be a .docx file')
        out.parent.mkdir(parents=True, exist_ok=True)
        counts = tracked.tracked_docx(old, new, out, style)
    except (OSError, ValueError) as exc:
        print(f'manuwright track-changes: {exc}', file=sys.stderr)
        return 2
    print(f"wrote {out}: {counts['inserted']} paragraph(s) inserted, {counts['deleted']} deleted, "
          f"{counts['kept']} unchanged. Open it in Word and check it before sending.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

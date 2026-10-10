#!/usr/bin/env python3
"""Keep the personal library (~/.manuwright/library) and paper folders in step, additions only.

What a paper learns (wording rules the author approved, style anchors, notes) should reach every
later paper, and what the library learns should reach papers already started. Nothing is ever
overwritten or deleted: only missing items are added, a changed file keeps a .bak copy, and a
disagreement (the same avoided term with a different preferred term, a style spec or author list
that differs) is reported for the author to decide.

  sync [--pull | --push] [--project DIR]
      no flag: show what differs, change nothing. --pull: add the library's missing wording rules,
      style anchors, style spec and team profile to this paper. --push: add this paper's to the library.
  term --prefer "used" --avoid "utilized" [--context "..."]
      one wording rule, saved in the library and in the current paper.
  note ["text" --topic journal|reviewer|writing|method|other]
      a lesson kept across papers (journal requirements, reviewer preferences, ...); no text lists them.

The session hook pulls additions automatically in a paper folder (`manuwright config set
library-sync auto|ask|off`, default auto); `style edits --apply` pushes the rules it applies.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent
sys.path.insert(0, str(HERE))
import academic_style  # noqa: E402

KINDS = ('own', 'landmark', 'target_journal')
TOPICS = ('journal', 'reviewer', 'writing', 'method', 'other')
SYNC_MODES = ('auto', 'ask', 'off')
TABLE_HEAD = '| Preferred Term | Forbidden Terms | Context |\n|---|---|---|\n'
SECTION = '## Synced Wording Rules'


def library() -> Path:
    return academic_style.home() / 'library'


def writing() -> Path:
    return library() / 'writing'


def sync_mode() -> str:
    try:
        value = json.loads((academic_style.home() / 'config.json').read_text(encoding='utf-8')).get('library_sync')
    except (OSError, ValueError, AttributeError):
        value = None
    return value if value in SYNC_MODES else 'auto'


def paper_root(folder: Path | None) -> Path | None:
    """The paper folder that contains `folder`, or None."""
    if not folder:
        return None
    folder = Path(folder).resolve()
    return next((p for p in [folder, *folder.parents] if academic_style._is_paper_root(p)), None)


def is_template(root: Path) -> bool:
    """The engine's own checkout: its Style/ is the public template, never synced."""
    try:
        return '@WORKFLOW.md' in (root / 'CLAUDE.md').read_text(encoding='utf-8', errors='replace') or \
            (root / 'scripts' / 'hooks').is_dir()
    except OSError:
        return (root / 'scripts' / 'hooks').is_dir()


def paper_terminology(root: Path) -> Path:
    try:
        declared = json.loads((root / 'project.json').read_text(encoding='utf-8')).get('terminology')
    except (OSError, ValueError, AttributeError):
        declared = None
    return root / (declared or 'Style/terminology.md')


# --- wording rules -------------------------------------------------------------------

def rules(path: Path) -> dict[str, tuple[str, str, str]]:
    """{avoided term (lower case): (preferred, avoided as written, context)} from every table that
    has Preferred Term and Forbidden Terms columns (the lint reads the same tables)."""
    found: dict[str, tuple[str, str, str]] = {}
    if not path.is_file():
        return found
    index = None
    for raw in path.read_text(encoding='utf-8', errors='replace').splitlines():
        line = raw.strip()
        if not line.startswith('|'):
            index = None
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        names = [re.sub(r'[^a-z]', '', c.lower()) for c in cells]
        if 'preferredterm' in names and 'forbiddenterms' in names:
            context = names.index('context') if 'context' in names else None
            index = (names.index('preferredterm'), names.index('forbiddenterms'), context)
            continue
        if index is None or set(''.join(cells)) <= {'-', ':', ' '} or len(cells) <= max(index[:2]):
            continue
        preferred, avoided = cells[index[0]], cells[index[1]]
        context = cells[index[2]] if index[2] is not None and index[2] < len(cells) else ''
        for term in re.split(r'[;,]', avoided):
            term = term.strip()
            if preferred and term and term not in ('-', '—'):
                found.setdefault(term.lower(), (preferred, term, context))
    return found


def seed_registry(target: Path) -> None:
    """A new registry starts from the engine's, so the lint keeps its standard vocabulary."""
    if target.is_file():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    engine = ENGINE / 'Style' / 'terminology.md'
    target.write_text(engine.read_text(encoding='utf-8') if engine.is_file() else '# Terminology\n', encoding='utf-8')


def add_rules(target: Path, new: dict[str, tuple[str, str, str]], context: str) -> tuple[list[str], list[str]]:
    """Append the rules `target` lacks; returns (added rows, conflicts). Never edits an existing row."""
    if new:
        seed_registry(target)  # before comparing: a seeded registry may already hold the rule
    have = rules(target)
    added, conflicts, rows = [], [], []
    for key, (preferred, avoided, ctx) in new.items():
        if key in have:
            if have[key][0].lower() != preferred.lower():
                conflicts.append(f'"{avoided}": {target.name} prefers "{have[key][0]}", the other side "{preferred}"')
            continue
        rows.append(f'| {preferred} | {avoided} | {ctx or context} |')
        added.append(f'{avoided} -> {preferred}')
    if rows:
        text = target.read_text(encoding='utf-8')
        backup = target.with_name(target.name + '.bak')
        shutil.copyfile(target, backup)
        if SECTION not in text:
            text = text.rstrip('\n') + f'\n\n{SECTION}\n\nAdded by `manuwright library` (additions only; edit freely).\n\n' + TABLE_HEAD
        elif not text.endswith('\n'):
            text += '\n'
        target.write_text(text + '\n'.join(rows) + '\n', encoding='utf-8')
    return added, conflicts


def library_terminology() -> Path:
    return writing() / 'terminology.md'


def remember_term(prefer: str, avoid: str, context: str, project: Path | None) -> list[str]:
    """One wording rule into the library and, inside a paper, into the paper. Returns report lines."""
    rule = {a.strip().lower(): (prefer.strip(), a.strip(), context) for a in re.split(r'[;,]', avoid) if a.strip()}
    report = []
    targets = [('library', library_terminology())]
    root = paper_root(project)
    if root and not is_template(root):
        targets.append(('paper', paper_terminology(root)))
    for label, path in targets:
        added, conflicts = add_rules(path, rule, context or 'remembered in chat')
        if label == 'paper' and added:
            _declare(root, 'terminology', path)  # the lint and verify read the registry project.json names
        report += [f'{label}: added {a} ({path})' for a in added]
        report += [f'{label}: CONFLICT {c}; left unchanged, ask the author which to keep' for c in conflicts]
        if not added and not conflicts:
            report.append(f'{label}: already has this rule ({path})')
    return report


# --- notes ------------------------------------------------------------------------------

def notes_path() -> Path:
    return library() / 'notes.md'


def add_note(text: str, topic: str) -> str:
    text = ' '.join(text.split())
    path = notes_path()
    current = path.read_text(encoding='utf-8') if path.is_file() else '# Notes kept across papers\n'
    if re.search(r'^- \S+ ' + re.escape(text) + r'$', current, re.M):
        return f'already kept: {text}'
    heading = f'## {topic}'
    line = f'- {date.today().isoformat()} {text}'
    if heading in current.split('\n'):
        lines = current.rstrip('\n').split('\n')
        at = lines.index(heading) + 1
        while at < len(lines) and not lines[at].startswith('## '):
            at += 1
        lines.insert(at, line)
        current = '\n'.join(lines) + '\n'
    else:
        current = current.rstrip('\n') + f'\n\n{heading}\n{line}\n'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(current, encoding='utf-8')
    return f'kept under {topic}: {text} ({path})'


def notes_block(limit: int = 40) -> str:
    """The notes for the session card (newest kept when there are many)."""
    path = notes_path()
    if not path.is_file():
        return ''
    lines = [l for l in path.read_text(encoding='utf-8').splitlines() if l.startswith(('## ', '- '))]
    bullets = [l for l in lines if l.startswith('- ')]
    if not bullets:
        return ''
    if len(bullets) > limit:
        keep = set(bullets[-limit:])
        lines = [l for l in lines if l.startswith('## ') or l in keep]
    return ('YOUR NOTES (personal library, kept across papers; apply them where relevant, and add new ones with '
            '`manuwright library note "..." --topic ...` when the author asks you to remember something):\n'
            + '\n'.join(lines))


# --- files: anchors, style spec, team profile ---------------------------------------------

def file_pairs(root: Path):
    """(label, paper file, library file) for the files that sync as whole files."""
    for kind in KINDS:
        names = {p.name for p in (root / 'Style' / kind).glob('*.md')} | {p.name for p in (writing() / kind).glob('*.md')}
        for name in sorted(names):
            if not name.startswith('example_'):
                yield f'Style/{kind}/{name}', root / 'Style' / kind / name, writing() / kind / name
    yield 'Style/style_spec.md', root / 'Style' / 'style_spec.md', writing() / 'style_spec.md'
    yield 'profile/authors.md', root / 'profile' / 'authors.md', library() / 'profile' / 'authors.md'


def sync(root: Path, direction: str | None) -> dict:
    """direction None: report only; 'pull': library -> paper; 'push': paper -> library."""
    result = {'added_rules': [], 'copied': [], 'conflicts': [], 'differs': [], 'missing_here': [], 'missing_there': []}
    paper_terms, lib_terms = paper_terminology(root), library_terminology()
    lib_rules, paper_rules = rules(lib_terms), rules(paper_terms)
    pull_rules = {k: v for k, v in lib_rules.items() if k not in paper_rules}
    push_rules = {k: v for k, v in paper_rules.items() if k not in lib_rules}
    result['conflicts'] += [f'"{v[1]}": paper prefers "{v[0]}", library "{lib_rules[k][0]}"'
                            for k, v in paper_rules.items() if k in lib_rules and lib_rules[k][0].lower() != v[0].lower()]
    if direction == 'pull' and pull_rules:
        added, _ = add_rules(paper_terms, pull_rules, 'from your library')
        result['added_rules'] = added
        _declare(root, 'terminology', paper_terms)
    elif direction == 'push' and push_rules:
        added, _ = add_rules(lib_terms, push_rules, f'from {root.name}')
        result['added_rules'] = added
    if direction != 'pull':
        result['missing_here'] += [f'rule {v[1]} -> {v[0]}' for v in pull_rules.values()]
    if direction != 'push':
        result['missing_there'] += [f'rule {v[1]} -> {v[0]}' for v in push_rules.values()]
    for label, here, there in file_pairs(root):
        if here.is_file() and there.is_file():
            if here.read_bytes() != there.read_bytes():
                result['differs'].append(label)
            continue
        source, target = (there, here) if direction == 'pull' else (here, there) if direction == 'push' else (None, None)
        if source is not None and source.is_file() and not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            result['copied'].append(label)
            if label == 'Style/style_spec.md' and direction == 'pull':
                _declare(root, 'style_spec', target)
        elif there.is_file() and not here.exists() and direction != 'pull':
            result['missing_here'].append(label)
        elif here.is_file() and not there.exists() and direction != 'push':
            result['missing_there'].append(label)
    return result


def _declare(root: Path, key: str, path: Path) -> None:
    """Point project.json at a registry the sync created, so verify and the lint use it."""
    manifest = root / 'project.json'
    try:
        data = json.loads(manifest.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return
    relative = path.relative_to(root).as_posix()
    if isinstance(data, dict) and not data.get(key):
        data[key] = relative
        manifest.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def session_sync(folder: Path | None) -> str:
    """SessionStart: pull the library's additions into this paper (auto) or say what is waiting (ask)."""
    try:
        root = paper_root(folder)
        mode = sync_mode()
        if not root or mode == 'off' or is_template(root) or not library().is_dir():
            return ''
        result = sync(root, 'pull' if mode == 'auto' else None)
        lines = []
        if result['added_rules'] or result['copied']:
            lines.append('LIBRARY SYNC: added from your personal library to this paper (additions only): '
                         + '; '.join(result['added_rules'] + result['copied']) + '. Tell the author in one line.')
        waiting = [m for m in result['missing_here']]
        if waiting:
            lines.append(f'LIBRARY: {len(waiting)} item(s) in your library are not in this paper; '
                         '"라이브러리 최신으로 받아줘" / `manuwright library sync --pull` adds them.')
        if result['conflicts'] or result['differs']:
            lines.append('LIBRARY: differs from this paper (left unchanged; the author decides): '
                         + '; '.join(result['conflicts'] + result['differs']) + '. `manuwright library sync` shows it.')
        notes = notes_block()
        return '\n'.join(lines + ([notes] if notes else []))
    except Exception:
        return ''  # a sync problem never blocks the session


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    parser = argparse.ArgumentParser(prog='manuwright library', description='Personal library sync, wording rules and notes')
    sub = parser.add_subparsers(dest='action', required=True)
    sy = sub.add_parser('sync', help='compare (default), --pull or --push; additions only')
    sy.add_argument('--pull', action='store_true')
    sy.add_argument('--push', action='store_true')
    sy.add_argument('--project', default='.')
    te = sub.add_parser('term', help='keep one wording rule in the library and the current paper')
    te.add_argument('--prefer', required=True)
    te.add_argument('--avoid', required=True, help='the term(s) to avoid; separate several with ;')
    te.add_argument('--context', default='')
    te.add_argument('--project', default='.')
    no = sub.add_parser('note', help='keep a lesson across papers; no text lists the notes')
    no.add_argument('text', nargs='*')
    no.add_argument('--topic', default='other', choices=TOPICS)
    args = parser.parse_args(argv)
    if args.action == 'term':
        for line in remember_term(args.prefer, args.avoid, args.context, Path(args.project)):
            print(line)
        return 0
    if args.action == 'note':
        if not args.text:
            print(notes_path().read_text(encoding='utf-8') if notes_path().is_file()
                  else f'No notes yet ({notes_path()}). Add one: manuwright library note "..." --topic journal')
            return 0
        print(add_note(' '.join(args.text), args.topic))
        return 0
    root = paper_root(Path(args.project))
    if not root:
        print('error: not inside a paper folder (run it in a folder made by `manuwright init`, or pass --project).',
              file=sys.stderr)
        return 2
    if is_template(root):
        print('This is the engine template checkout; its Style/ is the public template and is not synced.')
        return 0
    if args.pull and args.push:
        print('error: choose --pull or --push', file=sys.stderr)
        return 2
    direction = 'pull' if args.pull else 'push' if args.push else None
    result = sync(root, direction)
    where = {'pull': f'this paper ({root})', 'push': f'your library ({library()})'}.get(direction)
    for item in result['added_rules']:
        print(f'added rule to {where}: {item}')
    for item in result['copied']:
        print(f'copied to {where}: {item}')
    for item in result['missing_here']:
        print(f'in the library, not in this paper: {item}  (--pull adds it)')
    for item in result['missing_there']:
        print(f'in this paper, not in the library: {item}  (--push adds it)')
    for item in result['conflicts']:
        print(f'CONFLICT (left unchanged): {item}')
    for item in result['differs']:
        print(f'differs (left unchanged; merge by hand or ask your agent): {item}')
    if not any(result.values()):
        print('This paper and your library are in step.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

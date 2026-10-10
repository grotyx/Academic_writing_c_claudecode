"""Personal library (~/.manuwright/library): things you reuse across papers.

  docx/<name>.json (+ <name>.docx)   named Word styles; the .docx is a template designed in Word
  profile/authors.md                 team: authors, affiliations, ORCID, funding and boilerplate text
  writing/                           your writing style, same layout as a paper's Style/ folder:
                                     own/ landmark/ target_journal/ extracts, terminology.md, style_spec.md,
                                     PDF/<kind>/ sources and profile/ (the style learned from them by
                                     `manuwright style learn`); neither is copied into papers

  notes.md                           lessons kept across papers (`manuwright library note`), shown at session start

What a paper teaches flows back without overwriting anything (scripts/library_sync.py): `library term` keeps a
wording rule in the library and the paper, `style edits --apply` sends approved rules to the library, `library
sync --pull/--push` adds the missing rules, anchors, style spec and team profile in either direction, and the
session hook pulls the library's additions into a paper folder (`config set library-sync auto|ask|off`).

`manuwright init` copies profile and writing style into each new paper; `manuwright target` offers the
saved Word styles. Extracting a writing style from your papers is LLM work: your agent does it with the
manuwright skill ("register my writing style"), writing into writing/ by Style/style_guide.md.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

KINDS = ('own', 'landmark', 'target_journal')
USAGE = """usage: manuwright library [status]
       manuwright library docx list | remove NAME
       manuwright library docx add <template.docx> --name NAME [--journal KEY | --team | --personal]
       manuwright library docx save NAME [--journal KEY | --team | --personal] [--project PATH]
       manuwright library profile [--edit | --import FILE]
       manuwright library writing add <paper.pdf|.md>... [--kind own|landmark|target_journal]
       manuwright library writing import <folder with own/ landmark/ target_journal/ anchors>
       manuwright library sync [--pull | --push]      this paper <-> your library, additions only
       manuwright library term --prefer WORD --avoid WORD [--context TEXT]   keep one wording rule
       manuwright library note ["TEXT" --topic journal|reviewer|writing|method|other]   keep a lesson
  Existing names are never overwritten; add --replace to do that. In chat: "기억해", "앞으로는 X 대신 Y",
  "공동저자 추가해줘", "라이브러리 최신으로 받아줘" do the same through your agent."""


def root():
    return Path(os.environ.get('MANUWRIGHT_HOME') or Path.home() / '.manuwright') / 'library'


def slug(name):
    value = re.sub(r'[^A-Za-z0-9._-]+', '-', name.strip()).strip('-.')
    if not value:
        raise ValueError('give the style a name (letters, digits, - or _)')
    return value


# --- Word styles ------------------------------------------------------------

SCOPES = {'journal': 'For journal', 'team': 'Team style', 'personal': 'My style'}


def docx_styles():
    """{name: {'settings': {...}, 'template': path|None, 'for': journal|team|personal, 'journal': key|None}}"""
    out = {}
    for meta in sorted((root() / 'docx').glob('*.json')):
        data = json.loads(meta.read_text(encoding='utf-8'))
        template = meta.with_suffix('.docx')
        out[meta.stem] = {'settings': data.get('settings', {}), 'for': data.get('for', 'personal'),
                          'journal': data.get('journal'), 'template': str(template) if template.is_file() else None}
    return out


def save_docx_style(name, settings, template=None, replace=False, scope='personal', journal=None):
    """Save a Word style for a journal, the team or yourself; a .docx template is copied in."""
    folder = root() / 'docx'
    folder.mkdir(parents=True, exist_ok=True)
    name = slug(name)
    if (folder / f'{name}.json').exists() and not replace:
        raise ValueError(f'a style named "{name}" already exists; pick another name or add --replace')
    staged = None
    if template:  # check and stage the new template before touching what is stored
        check_word_file(template)
        staged = folder / f'.{name}.docx.new'
        shutil.copyfile(template, staged)
    clean = {k: v for k, v in settings.items() if k not in ('reference', 'template')}
    data = {'for': 'journal' if journal else scope, 'journal': journal, 'settings': clean}
    (folder / f'{name}.json.new').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')
    if staged:
        os.replace(staged, folder / f'{name}.docx')
    else:
        (folder / f'{name}.docx').unlink(missing_ok=True)  # a replaced style must not keep an old template
    os.replace(folder / f'{name}.json.new', folder / f'{name}.json')
    return name


def check_word_file(path):
    """A real Word document (.docx), not a renamed .dotx template or another file."""
    path = Path(path)
    if path.suffix.lower() != '.docx' or not path.is_file():
        raise ValueError(f'not a .docx file: {path}')
    try:
        from docx import Document
    except ImportError:  # python-docx missing: the build reports it
        return
    try:
        Document(str(path))
    except Exception as exc:  # python-docx raises several types for non-documents
        raise ValueError(f'{path} is not a Word document (.docx) python-docx can open '
                         f'(a .dotx template must be saved as .docx): {exc}') from exc


def describe_style(name, style, journal_label=lambda j: j):
    kind = (f"For {journal_label(style['journal'])}" if style['for'] == 'journal' else SCOPES[style['for']])
    return f"{kind}: {name}{' (Word template)' if style['template'] else ''}"


def apply_docx_style(name, paper_root):
    """project.json "docx" block for a saved style; a Word template is copied into the paper."""
    style = docx_styles()[name]
    block = dict(style['settings'])
    if style['template']:
        target = paper_root / 'templates' / f'{name}.docx'
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(style['template'], target)
        block['reference'] = f'templates/{name}.docx'
    return block


def scope_args(args):
    """--journal KEY | --team | --personal (default) from a command line."""
    if '--journal' in args:
        return 'journal', args[args.index('--journal') + 1]
    return ('team' if '--team' in args else 'personal'), None


def docx_command(args):
    action = args[0] if args else 'list'
    if action == 'list':
        styles = docx_styles()
        for name, style in styles.items():
            settings = ', '.join(f'{k}={v}' for k, v in style['settings'].items())
            print(f"  {describe_style(name, style)}{'  ' + settings if settings else ''}")
        if not styles:
            print('  (none) -- e.g. manuwright library docx add bjj_template.docx --name bjj --journal bjj')
        return 0
    if action == 'add' and len(args) >= 2 and '--name' in args:
        source = Path(args[1]).expanduser()
        scope, journal = scope_args(args)
        name = save_docx_style(args[args.index('--name') + 1], {}, source, '--replace' in args, scope, journal)
        print(f'Saved Word template "{name}" ({describe_style(name, docx_styles()[name])}). '
              'Papers pick it in: manuwright target')
        return 0
    if action == 'save' and len(args) >= 2:
        from manuwright.lifecycle import find_manifest
        manifest = find_manifest(['--project', args[args.index('--project') + 1]] if '--project' in args else [])
        if not manifest:
            print('run inside a paper folder or pass --project PATH', file=sys.stderr)
            return 2
        block = json.loads(manifest.read_text(encoding='utf-8')).get('docx') or {}
        if not block:
            print('this paper uses the default style; set one first with: manuwright target', file=sys.stderr)
            return 2
        template = None
        if block.get('reference'):
            template = (manifest.parent / block['reference']).resolve()
            if not template.is_relative_to(manifest.parent.resolve()):
                raise ValueError('docx.reference must point inside the paper folder')
        config = json.loads(manifest.read_text(encoding='utf-8'))
        scope, journal = scope_args(args)
        if scope == 'personal' and '--personal' not in args and config.get('journal'):
            scope, journal = 'journal', config['journal']  # a paper's style usually belongs to its journal
        name = save_docx_style(args[1], block, template, '--replace' in args, scope, journal)
        print(f'Saved "{name}" from {manifest}.')
        return 0
    if action == 'remove' and len(args) == 2:
        for suffix in ('.json', '.docx'):
            (root() / 'docx' / f'{slug(args[1])}{suffix}').unlink(missing_ok=True)
        print(f'Removed "{args[1]}".')
        return 0
    print(USAGE, file=sys.stderr)
    return 2


# --- team profile -----------------------------------------------------------

def profile_path():
    return root() / 'profile' / 'authors.md'


def profile_command(engine, args):
    path = profile_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if '--import' in args:
        source = Path(args[args.index('--import') + 1]).expanduser()
        if path.exists() and '--replace' not in args:
            print(f'{path} already exists; add --replace to overwrite it with {source}', file=sys.stderr)
            return 1
        shutil.copyfile(source, path)
        print(f'Imported {source} -> {path}')
        return 0
    if not path.exists():
        template = engine / 'profile' / 'example_authors.md'
        shutil.copyfile(template, path) if template.is_file() else path.write_text('# Authors\n', encoding='utf-8')
        print(f'Created {path} from the template.')
    if '--edit' in args:
        editor = os.environ.get('EDITOR')
        parts = [p.strip('"') for p in shlex.split(editor, posix=os.name != 'nt')] if editor else []
        command = [*parts, str(path)] if editor else (['open', '-t', str(path)] if sys.platform == 'darwin' else
                                                      ['notepad', str(path)] if os.name == 'nt' else ['xdg-open', str(path)])
        return subprocess.call(command)
    print(f'Team profile: {path}\n'
          'Fill it once: authors, degrees, affiliations, ORCID, email, funding statements, standard\n'
          'disclosures. Edit it directly (manuwright library profile --edit), or ask your agent:\n'
          '  "Fill my manuwright team profile from this CV / author list" (it edits that file).\n'
          'New papers get a copy in profile/authors.md (manuwright init); the title page is written from it.')
    return 0


# --- writing style ----------------------------------------------------------

def writing():
    return root() / 'writing'


def writing_command(args):
    action = args[0] if args else ''
    kind = args[args.index('--kind') + 1] if '--kind' in args else 'own'
    if kind not in KINDS:
        print(f'--kind must be one of {", ".join(KINDS)}', file=sys.stderr)
        return 2
    files = [a for a in args[1:] if not a.startswith('--') and a not in KINDS]
    if action == 'add' and files:
        for name in files:
            source = Path(name).expanduser()
            target = writing() / ('PDF' if source.suffix.lower() == '.pdf' else '') / kind / source.name
            if target.exists() and '--replace' not in args:
                print(f'kept existing {target} (add --replace to overwrite)')
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            print(f'added {target}')
        print('\nNext (needs an LLM): in Claude Code or Codex, ask "register my writing style in the manuwright '
              'library".\nThe manuwright skill turns these sources into style anchors, terminology.md and '
              f'style_spec.md under {writing()}.')
        return 0
    if action == 'import' and files:
        source = Path(files[0]).expanduser()
        count = kept = 0
        for path in source.rglob('*'):
            # the engine's own guide and example placeholders are not the author's style
            if (path.is_file() and path.suffix.lower() in ('.md', '.pdf') and path.name != 'style_guide.md'
                    and not path.name.startswith('example_')):
                target = writing() / path.relative_to(source)
                if target.exists() and '--replace' not in args:
                    kept += 1
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
                count += 1
        print(f'Imported {count} file(s) from {source} into {writing()}'
              + (f'; kept {kept} existing (add --replace to overwrite).' if kept else '.'))
        return 0
    print(USAGE, file=sys.stderr)
    return 2


def copy_into_paper(paper):
    """Copy profile and writing style into a new paper (never overwrite). Returns project.json updates."""
    updates, copied = {}, []
    if profile_path().is_file() and not (paper / 'profile' / 'authors.md').exists():
        (paper / 'profile').mkdir(exist_ok=True)
        shutil.copyfile(profile_path(), paper / 'profile' / 'authors.md')
        copied.append('profile/authors.md')
    if writing().is_dir():
        for path in writing().rglob('*.md'):
            relative = path.relative_to(writing())
            if relative.parts[0] in ('PDF', 'profile'):
                continue  # sources and the learned profile (it quotes them) stay in the library
            target = paper / 'Style' / relative
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
                copied.append(f'Style/{relative}')
        for key, name in (('terminology', 'terminology.md'), ('style_spec', 'style_spec.md')):
            if (paper / 'Style' / name).is_file():
                updates[key] = f'Style/{name}'
    return updates, copied


def status():
    styles = docx_styles()
    counts = {kind: len(list((writing() / kind).glob('*.md'))) for kind in KINDS}
    sources = len(list((writing() / 'PDF').rglob('*.pdf'))) if (writing() / 'PDF').is_dir() else 0
    print(f'Personal library: {root()}')
    print(f"  Word styles: {', '.join(styles) or 'none'}")
    print(f"  Team profile: {'yes' if profile_path().is_file() else 'none'} ({profile_path()})")
    print(f"  Writing style: {counts['own']} own / {counts['landmark']} landmark / "
          f"{counts['target_journal']} target-journal anchors, {sources} source PDF(s), "
          f"terminology {'yes' if (writing() / 'terminology.md').is_file() else 'no'}, "
          f"style spec {'yes' if (writing() / 'style_spec.md').is_file() else 'no'}")
    print('\n' + USAGE)
    return 0


def main(engine, args):
    if not args or args[0] == 'status':
        return status()
    try:
        if args[0] == 'docx':
            return docx_command(args[1:])
        if args[0] == 'profile':
            return profile_command(engine, args[1:])
        if args[0] in ('writing', 'style'):  # "style" was the first name
            return writing_command(args[1:])
        if args[0] in ('sync', 'term', 'note'):
            sys.path.insert(0, str(engine / 'scripts'))
            import library_sync
            return library_sync.main(args)
    except (OSError, ValueError, KeyError, IndexError) as exc:
        print(f'manuwright library: {exc}', file=sys.stderr)
        return 1
    print(USAGE, file=sys.stderr)
    return 2

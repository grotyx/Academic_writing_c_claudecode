"""Personal library (~/.manuwright/library): things you reuse across papers.

  docx/<name>.json (+ <name>.docx)   named Word styles; the .docx is a template designed in Word
  profile/authors.md                 team: authors, affiliations, ORCID, funding and boilerplate text
  writing/                           your writing style, same layout as a paper's Style/ folder:
                                     own/ landmark/ target_journal/ extracts, terminology.md, style_spec.md,
                                     PDF/<kind>/ sources (never copied into papers)

`manuwright init` copies profile and writing style into each new paper; `manuwright target` offers the
saved Word styles. Extracting a writing style from your papers is LLM work: your agent does it with the
manuwright skill ("register my writing style"), writing into writing/ by Style/style_guide.md.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

KINDS = ('own', 'landmark', 'target_journal')
USAGE = """usage: manuwright library [status]
       manuwright library docx list | add <template.docx> --name NAME | save NAME [--project PATH] | remove NAME
       manuwright library profile [--edit | --import FILE]
       manuwright library style add <paper.pdf|.md>... [--kind own|landmark|target_journal]
       manuwright library style import <Style folder>
  Existing names are never overwritten; add --replace to do that."""


def root():
    return Path(os.environ.get('MANUWRIGHT_HOME') or Path.home() / '.manuwright') / 'library'


def slug(name):
    value = re.sub(r'[^A-Za-z0-9._-]+', '-', name.strip()).strip('-.')
    if not value:
        raise ValueError('give the style a name (letters, digits, - or _)')
    return value


# --- Word styles ------------------------------------------------------------

def docx_styles():
    """{name: {settings..., 'template': path or None}}"""
    out = {}
    for meta in sorted((root() / 'docx').glob('*.json')):
        settings = json.loads(meta.read_text(encoding='utf-8'))
        template = meta.with_suffix('.docx')
        out[meta.stem] = {**settings, 'template': str(template) if template.is_file() else None}
    return out


def save_docx_style(name, settings, template=None, replace=False):
    folder = root() / 'docx'
    folder.mkdir(parents=True, exist_ok=True)
    name = slug(name)
    if (folder / f'{name}.json').exists() and not replace:
        raise ValueError(f'a style named "{name}" already exists; pick another name or add --replace')
    (folder / f'{name}.docx').unlink(missing_ok=True)  # a replaced style must not keep an old template
    clean = {k: v for k, v in settings.items() if k not in ('reference', 'template')}
    (folder / f'{name}.json').write_text(json.dumps(clean, indent=2) + '\n', encoding='utf-8')
    if template:
        shutil.copyfile(template, folder / f'{name}.docx')
    return name


def apply_docx_style(name, paper_root):
    """project.json "docx" block for a saved style; a Word template is copied into the paper."""
    style = docx_styles()[name]
    block = {k: v for k, v in style.items() if k != 'template'}
    if style['template']:
        target = paper_root / 'templates' / f'{name}.docx'
        target.parent.mkdir(exist_ok=True)
        shutil.copyfile(style['template'], target)
        block['reference'] = f'templates/{name}.docx'
    return block


def docx_command(args):
    action = args[0] if args else 'list'
    if action == 'list':
        styles = docx_styles()
        for name, style in styles.items():
            settings = ', '.join(f'{k}={v}' for k, v in style.items() if k != 'template')
            print(f"  {name}: {'Word template' if style['template'] else ''}"
                  f"{' + ' if style['template'] and settings else ''}{settings}")
        if not styles:
            print('  (none) -- add a Word template: manuwright library docx add mystyle.docx --name team')
        return 0
    if action == 'add' and len(args) >= 2 and '--name' in args:
        source = Path(args[1]).expanduser()
        if source.suffix.lower() != '.docx' or not source.is_file():
            print(f'not a .docx file: {source}', file=sys.stderr)
            return 2
        name = save_docx_style(args[args.index('--name') + 1], {}, source, '--replace' in args)
        print(f'Saved Word template "{name}". Choose it per paper with: manuwright target')
        return 0
    if action == 'save' and len(args) >= 2:
        from manuwright.lifecycle import find_manifest
        manifest = find_manifest([a for a in args[2:] if a != '--replace'])
        if not manifest:
            print('run inside a paper folder or pass --project PATH', file=sys.stderr)
            return 2
        block = json.loads(manifest.read_text(encoding='utf-8')).get('docx') or {}
        if not block:
            print('this paper uses the default style; set one first with: manuwright target', file=sys.stderr)
            return 2
        template = manifest.parent / block['reference'] if block.get('reference') else None
        name = save_docx_style(args[1], block, template, '--replace' in args)
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
        command = [editor, str(path)] if editor else (['open', '-t', str(path)] if sys.platform == 'darwin' else
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


def style_command(args):
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
            if path.is_file() and path.suffix.lower() in ('.md', '.pdf'):
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
            if relative.parts[0] == 'PDF':
                continue  # sources stay in the library (copyright, size)
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
        if args[0] == 'style':
            return style_command(args[1:])
    except (OSError, ValueError, KeyError, IndexError) as exc:
        print(f'manuwright library: {exc}', file=sys.stderr)
        return 1
    print(USAGE, file=sys.stderr)
    return 2

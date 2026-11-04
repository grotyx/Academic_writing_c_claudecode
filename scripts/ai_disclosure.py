#!/usr/bin/env python3
"""AI-use disclosure: check the paper's AI-use record and propose disclosure wording for the author to review.

The record is the JSON file named by "ai_usage" in project.json (for example review/ai_usage.json):

    {"used": true, "reviewed_by": "Named human reviewer",
     "disclosure": "Author-reviewed declaration text (built into the manuscript before the references)",
     "tools": [{"tool": "Service or model name", "role": "Language revision",
                "use": "writing", "purpose": "improve the clarity of the Discussion",
                "version": "model/version identifier", "developer": "developer",
                "prompts": "review/ai_prompts/session_1.md"}]}

use is one of writing, references, research, figure, grammar. Entries without "use" are unclassified (still
valid, as before v1.10.4). Grammar-only use needs no declaration under the Elsevier policy; a journal may
differ. Research use (study design, code, analysis, translation of research data) belongs in Methods;
"figure" is AI help with an explanatory image (flow chart, schematic) and is disclosed in its caption too.

    manuwright disclose            print a proposal for the author: declaration, Methods sentences, captions
    manuwright disclose --check    check the record's structure, prompt-log paths and figure paths

Nothing is written. The check proves the record is well formed, not that the disclosure is adequate:
the independent review and the human signoff decide that.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from harness.results import inside  # noqa: E402

USES = ('writing', 'references', 'research', 'figure', 'grammar')
DECLARATION_TITLE = 'Declaration of generative AI and AI-assisted technologies in the manuscript preparation process'


def _text(value) -> bool:
    return isinstance(value, str) and bool(value.strip())


def record_problems(value) -> list[str]:
    """Shape problems of an ai_usage record (no file access). Empty list: well formed."""
    if not isinstance(value, dict) or not _text(value.get('reviewed_by')):
        return ['ai_usage: object with nonempty reviewed_by required']
    if type(value.get('used')) is not bool:
        return ['ai_usage: used must be true or false']
    tools = value.get('tools')
    if value['used'] is False:
        if tools or _text(value.get('disclosure')):
            return ['ai_usage: used=false conflicts with recorded tools or disclosure']
        return []
    if not isinstance(tools, list) or not tools:
        return ['ai_usage: a nonempty tools list is required when used']
    problems = []
    for n, tool in enumerate(tools):
        where = f'ai_usage.tools[{n}]'
        if not isinstance(tool, dict) or not (_text(tool.get('tool')) and _text(tool.get('role'))):
            problems.append('ai_usage: every tools entry needs nonempty tool and role')
            continue
        use = tool.get('use')
        if use is not None and use not in USES:
            problems.append(f'{where}.use: expected writing, references, research, figure or grammar')
        if use is not None and not _text(tool.get('purpose')):
            problems.append(f'{where}.purpose: nonempty string required when use is set')
        for field in ('purpose', 'version', 'developer', 'reviewed_by', 'prompts'):
            if field in tool and not _text(tool[field]):
                problems.append(f'{where}.{field}: nonempty string required')
        figures = tool.get('figures')
        if figures is not None:
            if use not in ('research', 'figure'):
                problems.append(f'{where}.figures: only for use research or figure')
            elif not isinstance(figures, list) or not figures or not all(_text(f) for f in figures) \
                    or len(set(figures)) != len(figures):
                problems.append(f'{where}.figures: a nonempty list of distinct figure paths required')
        elif use == 'figure':
            problems.append(f'{where}.figures: name the figure(s) the tool helped with')
    if not all(isinstance(t, dict) and t.get('use') == 'grammar' for t in tools) and not _text(value.get('disclosure')):
        problems.append('ai_usage: disclosure required for non-grammar or unclassified use')
    return problems


def path_problems(root: Path, config: dict, value: dict) -> tuple[list[str], list[str]]:
    """(failures, blocked) for prompt logs and figure paths named in a well-formed record."""
    failures, blocked = [], []
    declared_figures = set()
    for item in config.get('figures', []):
        try:
            declared_figures.add(inside(root, item))
        except ValueError:
            pass
    dependencies = set()
    for item in config.get('dependencies', []):
        try:
            dependencies.add(inside(root, item))
        except ValueError:
            pass
    for n, tool in enumerate(value.get('tools') or []):
        where = f'ai_usage.tools[{n}]'
        prompts = tool.get('prompts')
        if prompts:
            try:
                if Path(prompts).is_absolute() or prompts.replace('\\', '/').startswith('/'):
                    raise ValueError
                path = inside(root, prompts)
            except ValueError:
                failures.append(f'{where}.prompts: path must be project-relative and stay inside the project')
            else:
                if not path.exists():
                    blocked.append(f'{where}.prompts: file not found: {prompts}')
                elif not path.is_file():
                    failures.append(f'{where}.prompts: {prompts} is not a file')
                elif path not in dependencies:
                    failures.append(f'{where}.prompts: add {prompts} to project.dependencies for freshness checks')
        for figure in tool.get('figures') or []:
            try:
                ok = inside(root, figure) in declared_figures
            except ValueError:
                ok = False
            if not ok:
                failures.append(f'{where}.figures: {figure} is not declared in project.figures')
    return failures, blocked


def check(root: Path, config: dict) -> tuple[list[str], list[str]]:
    """Read the record named by config["ai_usage"]: (failures, blocked)."""
    name = config.get('ai_usage')
    if not name:
        return [], ['ai_usage: project.json names no AI-use record']
    try:
        value = json.loads(inside(root, name).read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        return [], [f'ai_usage: cannot read {name}: {exc}']
    problems = record_problems(value)
    if problems:
        return problems, []
    return path_problems(root, config, value)


def _name(tool: dict) -> str:
    detail = '; '.join(tool[k].strip() for k in ('version', 'developer') if _text(tool.get(k)))
    return tool['tool'].strip() + (f' ({detail})' if detail else '')


def preview(value: dict) -> str:
    """Suggested wording, grouped by where it goes. A proposal for the author, never a record of review."""
    if not value.get('used'):
        return 'No AI use is recorded (used: false). Nothing to declare.'
    tools = value.get('tools') or []
    groups = {use: [t for t in tools if t.get('use') == use] for use in USES}
    unclassified = [t for t in tools if t.get('use') not in USES]
    out = ['PROPOSAL FOR AUTHOR REVIEW. Check every name, version and purpose; edit the wording; then put the '
           'approved text in the record\'s "disclosure". Nothing here has been reviewed yet.', '']
    declared = groups['writing'] + groups['references'] + groups['figure']
    out.append(f'1. Declaration (end of the manuscript, immediately before the references), titled "{DECLARATION_TITLE}":')
    if declared:
        for tool in declared:
            out.append(f'   During the preparation of this work the author(s) used {_name(tool)} in order to '
                       f'{tool["purpose"].strip().rstrip(".")}. After using this tool/service, the author(s) reviewed '
                       'and edited the content as needed and take(s) full responsibility for the content of the publication.')
    else:
        out.append('   (no writing, reference or figure use recorded)')
    out += ['', '2. Methods (AI used in the research itself: design, code, analysis, research-data translation):']
    if groups['research']:
        for tool in groups['research']:
            missing = [k for k in ('version', 'developer') if not _text(tool.get(k))]
            out.append(f'   {_name(tool)} was used to {tool["purpose"].strip().rstrip(".")}.'
                       + (f'  [record the {" and ".join(missing)}]' if missing else ''))
    else:
        out.append('   (no research use recorded)')
    out += ['', '3. Figure captions (explanatory images made with AI help; say so in each caption):']
    if groups['figure']:
        for tool in groups['figure']:
            for figure in tool.get('figures') or []:
                out.append(f'   {figure}: Created with the assistance of {_name(tool)} '
                           f'({tool["purpose"].strip().rstrip(".")}).')
    else:
        out.append('   (no figure use recorded)')
    if groups['grammar']:
        out += ['', '4. Not declared (basic grammar, spelling and punctuation checks; Elsevier policy, check your journal): '
                + ', '.join(_name(t) for t in groups['grammar'])]
    if unclassified:
        out += ['', 'Unclassified (add "use" and "purpose" to get section-specific wording): '
                + ', '.join(_name(t) if _text(t.get('tool')) else '?' for t in unclassified if isinstance(t, dict))]
    out += ['', 'Also state the AI use in the cover letter (ICMJE). AI tools are never authors. Keep prompt logs '
            'local; they are not added to the review packet or the build.']
    return '\n'.join(out)


def find_project(start: Path) -> Path | None:
    return next((p / 'project.json' for p in [start, *start.parents] if (p / 'project.json').is_file()), None)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    parser = argparse.ArgumentParser(prog='manuwright disclose', description=__doc__.split('\n\n')[0])
    parser.add_argument('--check', action='store_true', help='check the record (structure, prompt logs, figure paths)')
    parser.add_argument('--project', help='project.json (default: the paper folder you are in)')
    args = parser.parse_args(argv)
    manifest = Path(args.project) if args.project else find_project(Path.cwd())
    if manifest is None or not manifest.is_file():
        print('manuwright disclose: run it inside a paper folder (project.json) or pass --project', file=sys.stderr)
        return 2
    try:
        root, config = manifest.resolve().parent, json.loads(manifest.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        print(f'manuwright disclose: cannot read {manifest}: {exc}', file=sys.stderr)
        return 2
    failures, blocked = check(root, config)
    if args.check:
        for line in failures + blocked:
            print(line, file=sys.stderr)
        if failures:
            return 1
        if blocked:
            return 2
        print('OK AI-use record checks passed; whether the disclosure is adequate needs the independent review and '
              'human signoff (not a journal-compliance check).')
        return 0
    if blocked or failures:
        for line in failures + blocked:
            print(line, file=sys.stderr)
        return 1 if failures else 2
    print(preview(json.loads(inside(root, config['ai_usage']).read_text(encoding='utf-8'))))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

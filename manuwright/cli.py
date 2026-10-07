"""manuwright: installed entry point for the manuscript engine (Track B).

The same engine runs uninstalled as `python -m harness` / `python scripts/x.py`
(Track A). This wrapper only locates the engine and, for standalone checkers,
fills project-path flags from the current directory when the caller did not
pass them, so an installed engine never reads its own install folder as the
paper (docs/distribution_plan.md, section 2).
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Installed wheel: engine files sit inside the package. Source checkout: one level up.
ENGINE = HERE if (HERE / 'scripts').is_dir() else HERE.parent
HARNESS_COMMANDS = {'doctor', 'status', 'verify', 'packet', 'build', 'record-approval', 'approve'}

# name -> (script, {flag: project-relative default injected when the flag is absent})
TOOLS = {
    'citations': ('check_citations.py', {'--evidence': 'knowledge/evidence.md'}),
    'numbers': ('check_numbers.py', {'--results': 'results'}),
    'gate': ('check_gate.py', {'--base-dir': '.'}),
    'abstract': ('check_abstract.py', {}),
    'coverage': ('check_coverage.py', {'--evidence': 'knowledge/evidence.md'}),
    'crossrefs': ('check_crossrefs.py', {}),
    'abbreviations': ('check_abbreviations.py', {}),
    'style': ('check_style.py', {}),
    'revision-claims': ('check_revision_claims.py', {}),
    'response-coverage': ('check_response_coverage.py', {}),
    'lint': ('lint_manuscript.py', {'--terminology': 'Style/terminology.md'}),
    'verify-all': ('verify_all.py', {'--base-dir': '.'}),
    'format-references': ('format_references.py', {'--evidence': 'knowledge/evidence.md'}),
    'search': ('search_pubmed.py', {}),
    'evidence-table': ('evidence_table.py', {}),
    'extract-claims': ('extract_claims.py', {}),
    'critical-review': ('critical_review.py', {}),
    'compile-response': ('compile_response_docx.py', {}),
}

USAGE = f"""usage: manuwright <command> [args]

Manifest profiles (same as python -m harness):
  {' | '.join(sorted(HARNESS_COMMANDS))}
  status, verify, packet and build use the project.json of the paper folder you are in (or --project PATH)
Standalone tools (same flags as scripts/*.py; project paths default to the current folder):
  {' | '.join(TOOLS)}
  manuwright <tool> --help    shows that tool's own options
Setup and updates:
  init [folder]              starter paper folder (never overwrites, never approves)
  init --refresh-rules [--all]   in an existing paper (or --all registered papers): update only the agent rules (AGENTS/CLAUDE/GEMINI.md)
  check                      one report: version, agent adapters, main model, key, auto-update, writing mode, papers
  mode [academic|strict|off] academic writing mode: style cards + prose findings (strict also blocks)
  style learn [papers...]    measure a corpus of good papers (PDF, DOCX, MD, TXT): your style, landmark, target journal
  style card <section>       the section's style card: moves, phrasebank, model paragraphs, your measured style
  style status               writing mode and learned profile (style extract|check: style metrics vs a Style Spec)
  approve <plan> --kind analysis|draft --approved-by NAME --quote "..."
                             record the author's approval given in chat (ticks the box, hashed receipt)
  rules [keyword|--path]     print the workflow rules (or one section)
  guide [name ...]           list the engine guides the rules cite as docs/<name>.md, or print them
  update [--check|--to X.Y.Z|--auto|--no-agents]   install a release, then refresh the agent adapters; --auto = daily check for hooks/shells
  setup                      one interactive pass: models, reviewers, updates, Obsidian
  target [--project PATH]    this paper's target journal (reference format) and Word style
  env [--project PATH]       this paper's own analysis Python (pandas, scipy, statsmodels) via uv
  run <script.py> [args]     run an analysis script with that environment, from the paper folder
  library [docx|profile|writing ...]   your Word styles/templates, team profile, writing style
  models                     recommended reviewer model sets (OpenRouter, opencode) with live price check
  config [set|unset <key> ...]         settings: auto-update, main-model, review.reviewers,
                                       review.openrouter-models, review.<agent>-model, docx.*
  agents install|update [--only claude,codex,agy,opencode,muse] [--dry-run]
                             install/refresh plugins and skills for each agent
  hook session|gate|lint|style         entry point for agent plugin hooks
Obsidian (Academic Paper Citation Manager plugin):
  obsidian status | obsidian install [--vault PATH] [--enable-mcp] [--yes]
  obsidian connect [--vault PATH] [--only a,b] [--dry-run] [--yes]
  evidence import-obsidian <citekey>... [--vault PATH]   vault note -> knowledge/evidence.md
  --version
"""


def version():
    text = (ENGINE / 'harness' / '__init__.py').read_text(encoding='utf-8')
    return text.split("__version__ = '")[1].split("'")[0]


def project_defaults(args, defaults, cwd):
    """Add a default only when its flag is absent and, for files, the file exists here."""
    extra = []
    for flag, relative in defaults.items():
        if any(a == flag or a.startswith(flag + '=') for a in args):
            continue
        target = cwd / relative
        if flag == '--terminology' and not target.is_file():
            continue  # no project registry: keep the engine's
        extra += [flag, str(target)]
    return extra


HOOKS = {'session': 'session_contract.py', 'gate': 'enforce_gates.py', 'lint': 'lint_on_edit.py',
         'style': 'style_intent.py'}


def hook(args):
    """manuwright hook <session|gate|lint|style>: plugin hook entry (Claude Code, Codex)."""
    if not args or args[0] not in HOOKS:
        print('usage: manuwright hook session|gate|lint|style', file=sys.stderr)
        return 2
    project = Path(os.environ.get('CLAUDE_PROJECT_DIR') or Path.cwd())
    settings = project / '.claude' / 'settings.json'
    try:
        if 'scripts/hooks/' in settings.read_text(encoding='utf-8'):
            return 0  # template checkout: its own hooks already run; never fire twice
    except OSError:
        pass
    script = [sys.executable, str(ENGINE / 'scripts' / 'hooks' / HOOKS[args[0]])]
    if args[0] != 'session':
        return subprocess.call(script)  # hook event JSON passes through on stdin
    subprocess.call(script + [str(project)])
    print('- TOOLS: manuwright verify --project project.json | manuwright citations|numbers|gate ... | '
          'manuwright rules <section>')
    if '--plugin-root' in args and args.index('--plugin-root') + 1 < len(args):
        root = Path(args[args.index('--plugin-root') + 1])
        try:
            plugin = (root / 'harness' / '__init__.py').read_text(encoding='utf-8')
            plugin = plugin.split("__version__ = '")[1].split("'")[0]
        except (OSError, IndexError):
            plugin = None
        if plugin and plugin != version():
            lifecycle = load_lifecycle()
            if lifecycle.load('config.json', {}).get('auto_update'):
                subprocess.Popen([sys.executable, '-m', 'manuwright.cli', 'agents', 'update'], stdin=subprocess.DEVNULL,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True,
                                 cwd=str(HERE.parent))
                print(f'manuwright plugin {plugin} -> CLI {version()}: refreshing agent adapters in the background.')
            else:
                print(f'WARNING: manuwright plugin {plugin} != CLI {version()}. Run `manuwright agents update` '
                      'so hooks, skills and engine match.')
    load_lifecycle().update(ENGINE, ['--auto', '--background'])
    return 0


def load_lifecycle():
    if not __package__:  # run as a file (python manuwright/cli.py) in a source checkout
        sys.path.insert(0, str(HERE.parent))
    from manuwright import lifecycle
    return lifecycle


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    for stream in (sys.stdout, sys.stderr):
        try:  # rules and guides hold Korean and symbols; agents read piped output as UTF-8, not cp949
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')  # the same for the scripts and hooks run below
    if not argv or argv[0] in {'-h', '--help', 'help'}:
        print(USAGE)
        return 0
    command, rest = argv[0], argv[1:]
    if command in {'--version', 'version'}:
        print(f'manuwright {version()} ({ENGINE})')
        return 0
    if command == 'hook':
        return hook(rest)
    if command in {'obsidian', 'evidence'}:
        if not __package__:
            sys.path.insert(0, str(HERE.parent))
        from manuwright import obsidian
        if command == 'obsidian' and rest[:1] in (['status'], ['connect'], ['install']):
            return getattr(obsidian, rest[0])(rest[1:])
        if command == 'evidence' and rest[:1] == ['import-obsidian']:
            return obsidian.import_evidence(rest[1:])
        print('usage: manuwright obsidian status|install|connect [--vault PATH] [--only a,b] [--dry-run] [--yes]\n'
              '       manuwright evidence import-obsidian <citekey>... [--vault PATH]', file=sys.stderr)
        return 2
    if command in {'env', 'run'}:
        if not __package__:
            sys.path.insert(0, str(HERE.parent))
        from manuwright import analysis_env
        return analysis_env.main(rest) if command == 'env' else analysis_env.run_script(rest)
    if command == 'library':
        if not __package__:
            sys.path.insert(0, str(HERE.parent))
        from manuwright import library
        return library.main(ENGINE, rest)
    if command == 'models':
        if not __package__:
            sys.path.insert(0, str(HERE.parent))
        from manuwright import models
        return models.main(rest)
    if command == 'style' and rest[:1] and rest[0] in ('learn', 'card', 'core', 'status'):
        return subprocess.call([sys.executable, str(ENGINE / 'scripts' / 'academic_style.py'), *rest])
    if command in {'init', 'rules', 'guide', 'check', 'mode', 'update', 'config', 'setup', 'agents', 'target', 'project'}:
        lifecycle = load_lifecycle()
        if command in {'config', 'setup', 'mode'}:
            return getattr(lifecycle, command)(rest)
        return getattr(lifecycle, command)(ENGINE, rest)
    if command in HARNESS_COMMANDS:
        if command in {'status', 'verify', 'packet', 'build'} and '--project' not in rest:
            manifest = load_lifecycle().find_manifest([])  # inside a paper folder: its project.json
            if manifest is None:
                print(f'manuwright {command}: no project.json in this folder or above. Run it inside a paper '
                      'folder (manuwright init creates one) or pass --project PATH.', file=sys.stderr)
                return 2
            rest = ['--project', str(manifest), *rest]
        if '--project' in rest and rest.index('--project') + 1 < len(rest):
            lifecycle = load_lifecycle()
            try:
                lifecycle.register(rest[rest.index('--project') + 1])
            except OSError:
                pass  # registry is a convenience for update safety checks
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(filter(None, [str(ENGINE), os.environ.get('PYTHONPATH')])))
        return subprocess.call([sys.executable, '-m', 'harness', command, *rest], env=env)
    if command not in TOOLS:
        print(f'manuwright: unknown command {command!r}\n\n{USAGE}', file=sys.stderr)
        return 2
    script, defaults = TOOLS[command]
    if command == 'search' and (not rest or rest[0] not in {'search', 'fetch', 'doi', 'related', '-h', '--help'}):
        rest = ['search', *rest]  # `manuwright search "<query>"` as documented
    if '-h' not in rest and '--help' not in rest:
        rest += project_defaults(rest, defaults, Path.cwd())
    return subprocess.call([sys.executable, str(ENGINE / 'scripts' / script), *rest])


if __name__ == '__main__':
    raise SystemExit(main())

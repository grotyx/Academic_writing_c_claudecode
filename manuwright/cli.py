"""manuwright: installed entry point for the manuscript engine (Track B).

The same engine runs uninstalled as `python -m harness` / `python scripts/x.py`
(Track A). This wrapper only locates the engine and, for standalone checkers,
fills project-path flags from the current directory when the caller did not
pass them, so an installed engine never reads its own install folder as the
paper (docs/distribution_plan.md, section 2).
"""
from __future__ import annotations
import json
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
    'claim-strength': ('check_claim_strength.py', {'--evidence': 'knowledge/evidence.md'}),
    'coverage': ('check_coverage.py', {'--evidence': 'knowledge/evidence.md'}),
    'crossrefs': ('check_crossrefs.py', {}),
    'abbreviations': ('check_abbreviations.py', {}),
    'style': ('check_style.py', {}),
    'revision-claims': ('check_revision_claims.py', {}),
    'blind-review': ('blind_review.py', {}),
    'response-coverage': ('check_response_coverage.py', {}),
    'lint': ('lint_manuscript.py', {'--terminology': 'Style/terminology.md'}),
    'verify-all': ('verify_all.py', {'--base-dir': '.'}),
    'format-references': ('format_references.py', {'--evidence': 'knowledge/evidence.md'}),
    'search': ('search_pubmed.py', {}),
    'evidence-table': ('evidence_table.py', {}),
    'extract-claims': ('extract_claims.py', {}),
    'critical-review': ('critical_review.py', {}),
    'journal': ('journal_fit.py', {}),
    'compile-response': ('compile_response_docx.py', {}),
    'bind': ('bind_results.py', {}),
    'track-changes': ('track_changes.py', {}),
    'figure': ('make_figure.py', {}),
    'disclose': ('ai_disclosure.py', {}),
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
  init --refresh-rules [--all] [--auto]   in an existing paper (or --all registered papers): update only the agent rules (AGENTS/CLAUDE/GEMINI.md); --auto keeps files you wrote or edited
  check                      one report: version, agent adapters, main model, key, auto-update, writing mode, papers
Writing and review (in chat you can simply ask: "서론 써줘", "과장 표현 검사해줘", "근거 다시 확인해줘"):
  mode [academic|strict|off] academic writing mode (default academic; strict blocks AI-style prose; or say "학술 모드 꺼줘")
  style card <section>       style card for a section (title, abstract, introduction, ... or 서론, 방법, 결과, 고찰 ...)
  style learn <folder>       learn the style of 3+ good papers (yours, landmark, target journal; PDF/DOCX/MD/TXT)
  style edits <ai> <edited>  learn rules from how you edited AI drafts (--git REV; you approve each rule; --apply)
  style preserve <old> <new> check a style rewrite kept every citation, number, p value and table/figure reference
  style flow <file>          the draft's paragraph order (gap, aim; finding, comparison, limitation ...) vs your papers
  style status               writing mode and learned style (style extract|check: metrics against a Style Spec)
  claim-strength drafts      cited sentences worded more strongly than their evidence (Claim Strength in evidence.md)
  bind [--write]             propose result bindings: each number tied to its results CSV cell (review/bindings_overrides.json
                             gives the table context and settles numbers found in several cells)
  figure SPEC.json [--check]  draw a forest/bar/line figure from a results CSV, with provenance verify checks
  disclose [--check]          propose AI-use declaration/Methods/caption wording from the ai_usage record; --check its structure
  track-changes OLD.md NEW.md -o OUT.docx   Word file with the revision as tracked changes (or "tracked_baseline" for build)
  search audit               check every evidence.md entry against PubMed: details match, retracted, corrected
  blind-review packet|check  revision re-review that hides the response letter until the verdicts are written
  journal fit [journal]      does the paper fit this journal: PubMed record, limits, an editor's review
  journal suggest            journals that publish similar work (--mine: only your list; --review ranks the fit)
  journal profile <j> --url  a journal's aims, limits and requirements; journal list [--build|--import FILE]: your journal list
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
  hook session|gate|lint|style|subagent   entry point for agent plugin hooks
Obsidian (Academic Paper Citation Manager plugin):
  obsidian status | obsidian install [--vault PATH] [--enable-mcp] [--yes]
  obsidian connect [--vault PATH] [--only a,b] [--dry-run] [--yes]
  evidence import-obsidian <citekey>... [--vault PATH]   vault note -> knowledge/evidence.md
  --version
"""


HELP_FLAGS = {'-h', '--help'}
VALUE_FLAGS = {'--to', '--only', '--vault', '--evidence', '--journal', '--name', '--project', '--import', '--kind'}
# Commands handled here, not by a script with its own argparse: `<command> --help` must print usage and
# stop, never run (init --help created a "--help" paper folder; update --help ran an update).
OWN_HELP = {'init', 'rules', 'guide', 'check', 'mode', 'update', 'config', 'setup', 'agents', 'target', 'project',
            'env', 'run', 'library', 'models', 'obsidian', 'evidence'}


def command_help(command):
    """The USAGE lines for one command, with their indented continuation lines."""
    out, taking = [], False
    for line in USAGE.splitlines():
        text = line.strip()
        if len(line) - len(line.lstrip()) > 20 and taking:
            out.append(line)
            continue
        taking = text == command or text.startswith(command + ' ')
        if taking:
            out.append(line)
    return 'usage: manuwright\n' + '\n'.join(out) if out else USAGE


# `python -m harness` from a paper folder puts that folder first on sys.path, so a folder named harness/
# there would run instead of the installed verifier. The child drops the current folder and imports the
# engine's package by its absolute path.
HARNESS_RUNNER = ("import runpy, sys; engine = sys.argv[1]; "
                  "sys.path[:] = [engine] + [p for p in sys.path if p not in ('', '.')]; "
                  "sys.argv = ['harness'] + sys.argv[2:]; runpy.run_module('harness', run_name='__main__', alter_sys=True)")


def harness_command(*args):
    return [sys.executable, '-c', HARNESS_RUNNER, str(ENGINE), *args]


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
        if flag == '--terminology':  # the registry the paper's project.json names comes first
            try:
                named = json.loads((cwd / 'project.json').read_text(encoding='utf-8')).get('terminology')
            except (OSError, ValueError, AttributeError):
                named = None
            if isinstance(named, str) and named and (cwd / named).resolve().is_relative_to(cwd.resolve()):
                target = cwd / named
        if flag == '--terminology' and not target.is_file():
            continue  # no project registry: keep the engine's
        extra += [flag, str(target)]
    return extra


HOOKS = {'session': 'session_contract.py', 'gate': 'enforce_gates.py', 'lint': 'lint_on_edit.py',
         'style': 'style_intent.py', 'subagent': 'subagent_style.py'}


def hook(args):
    """manuwright hook <session|gate|lint|style|subagent>: plugin hook entry (Claude Code, Codex)."""
    if not args or args[0] not in HOOKS:
        print('usage: manuwright hook session|gate|lint|style|subagent', file=sys.stderr)
        return 2
    project = Path(os.environ.get('CLAUDE_PROJECT_DIR') or Path.cwd())
    settings = project / '.claude' / 'settings.json'
    try:
        template = 'scripts/hooks/' in settings.read_text(encoding='utf-8')
    except OSError:
        template = False
    script = [sys.executable, str(ENGINE / 'scripts' / 'hooks' / HOOKS[args[0]])]
    if args[0] in ('gate', 'lint'):
        event = sys.stdin.buffer.read()
        try:
            tool = json.loads(event or b'{}').get('tool_name')
        except (ValueError, AttributeError):
            tool = None
        # A template checkout's own Claude hooks cover Write/Edit/MultiEdit only. Every other event (Codex
        # apply_patch) still needs this gate; skipping it on the settings file alone turned the Codex gate off.
        if template and tool in ('Write', 'Edit', 'MultiEdit'):
            return 0
        return subprocess.run(script, input=event).returncode  # hook event JSON passes through on stdin
    if template and os.environ.get('CLAUDE_PROJECT_DIR'):
        return 0  # Claude Code in a template checkout runs its own session, prompt and subagent hooks; Codex does not
    if args[0] != 'session':
        return subprocess.call(script)
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
                print(f'ManuWright plugin {plugin} -> CLI {version()}: refreshing agent adapters in the background.')
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
        print(f'ManuWright {version()} ({ENGINE})')
        return 0
    if command == 'hook':
        return hook(rest)
    if command in OWN_HELP and HELP_FLAGS & set(rest[:1] if command == 'run' else rest):  # run: later args are the script's
        print(command_help(command))
        return 0
    bare = next((flag for i, flag in enumerate(rest) if flag in VALUE_FLAGS
                 and (i + 1 == len(rest) or rest[i + 1].startswith('--'))), None)
    if command in OWN_HELP and command != 'run' and bare:  # "update --to --no-agents" must not install "--no-agents"
        print(f'manuwright {command}: {bare} needs a value\n\n{command_help(command)}', file=sys.stderr)
        return 2
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
    if command == 'style' and rest[:1] and rest[0] in HELP_FLAGS:  # the academic subcommands, then extract|check
        print(command_help('style') + '\n\nstyle extract|check (Style Spec metrics):', flush=True)
    if command == 'style' and rest[:1] and rest[0] in ('learn', 'card', 'core', 'status', 'preserve', 'edits', 'flow'):
        return subprocess.call([sys.executable, str(ENGINE / 'scripts' / 'academic_style.py'), *rest])
    if command in {'init', 'rules', 'guide', 'check', 'mode', 'update', 'config', 'setup', 'agents', 'target', 'project'}:
        lifecycle = load_lifecycle()
        if command in {'config', 'setup', 'mode'}:
            return getattr(lifecycle, command)(rest)
        return getattr(lifecycle, command)(ENGINE, rest)
    if command in HARNESS_COMMANDS and HELP_FLAGS & set(rest):  # argparse help; no paper folder needed
        return subprocess.call(harness_command(command, '--help'))
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
        return subprocess.call(harness_command(command, *rest))
    if command not in TOOLS:
        print(f'manuwright: unknown command {command!r}\n\n{USAGE}', file=sys.stderr)
        return 2
    script, defaults = TOOLS[command]
    if command == 'search' and (not rest or rest[0] not in {'search', 'fetch', 'doi', 'related', 'audit', '-h', '--help'}):
        rest = ['search', *rest]  # `manuwright search "<query>"` as documented
    if '-h' not in rest and '--help' not in rest:
        rest += project_defaults(rest, defaults, Path.cwd())
    return subprocess.call([sys.executable, str(ENGINE / 'scripts' / script), *rest])


if __name__ == '__main__':
    raise SystemExit(main())

"""paperflow: installed entry point for the manuscript engine (Track B).

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
HARNESS_COMMANDS = {'doctor', 'status', 'verify', 'packet', 'build', 'record-approval'}

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

USAGE = f"""usage: paperflow <command> [args]

Manifest profiles (same as python -m harness):
  {' | '.join(sorted(HARNESS_COMMANDS))}
Standalone tools (same flags as scripts/*.py; project paths default to the current folder):
  {' | '.join(TOOLS)}
  paperflow <tool> --help    shows that tool's own options
Setup and updates:
  init [folder]              starter paper folder (never overwrites, never approves)
  rules [keyword|--path]     print the workflow rules (or one section)
  update [--check|--to X.Y.Z|--auto]   install a release; --auto = daily check for hooks/shells
  config [set auto-update on|off]      opt-in patch-only auto-update
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


def load_lifecycle():
    if not __package__:  # run as a file (python paperflow/cli.py) in a source checkout
        sys.path.insert(0, str(HERE.parent))
    from paperflow import lifecycle
    return lifecycle


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in {'-h', '--help', 'help'}:
        print(USAGE)
        return 0
    command, rest = argv[0], argv[1:]
    if command in {'--version', 'version'}:
        print(f'paperflow {version()} ({ENGINE})')
        return 0
    if command in {'init', 'rules', 'update', 'config'}:
        lifecycle = load_lifecycle()
        if command == 'config':
            return lifecycle.config(rest)
        return getattr(lifecycle, command)(ENGINE, rest)
    if command in HARNESS_COMMANDS:
        if '--project' in rest and rest.index('--project') + 1 < len(rest):
            lifecycle = load_lifecycle()
            try:
                lifecycle.register(rest[rest.index('--project') + 1])
            except OSError:
                pass  # registry is a convenience for update safety checks
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(filter(None, [str(ENGINE), os.environ.get('PYTHONPATH')])))
        return subprocess.call([sys.executable, '-m', 'harness', command, *rest], env=env)
    if command not in TOOLS:
        print(f'paperflow: unknown command {command!r}\n\n{USAGE}', file=sys.stderr)
        return 2
    script, defaults = TOOLS[command]
    if '-h' not in rest and '--help' not in rest:
        rest += project_defaults(rest, defaults, Path.cwd())
    return subprocess.call([sys.executable, str(ENGINE / 'scripts' / script), *rest])


if __name__ == '__main__':
    raise SystemExit(main())

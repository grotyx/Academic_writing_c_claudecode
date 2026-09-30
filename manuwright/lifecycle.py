"""manuwright init / rules / update / config (docs/distribution_plan.md, phase 3).

Update policy: check automatically, apply explicitly. Opt-in auto-update applies
only patch releases, and only when no known project pins the engine away from
the new version or holds a fresh semantic review / human signoff that an
engine change would invalidate.
"""
from __future__ import annotations
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_URL = 'https://github.com/grotyx/Academic_writing_c_claudecode'


def home():
    return Path(os.environ.get('MANUWRIGHT_HOME') or Path.home() / '.manuwright')


def load(name, default):
    try:
        return json.loads((home() / name).read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return default


def save(name, data):
    home().mkdir(parents=True, exist_ok=True)
    (home() / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def engine_api(engine):
    """Import the engine's harness package (installed or checkout) without copying code."""
    if str(engine) not in sys.path:
        sys.path.insert(0, str(engine))
    import harness
    from harness import project
    return harness.__version__, project


# --- project registry -------------------------------------------------------

def register(manifest):
    path = str(Path(manifest).resolve())
    known = load('projects.json', [])
    if path not in known:
        save('projects.json', known + [path])


def known_projects():
    return [Path(p) for p in load('projects.json', []) if Path(p).is_file()]


def fresh_reviews(project_api, manifests):
    """Manifests whose semantic review or human signoff is valid right now."""
    fresh = []
    for manifest in manifests:
        try:
            path, config = project_api.load_project(manifest)
            deps = project_api.snapshot(path, config)
        except (OSError, ValueError, KeyError, TypeError):
            continue
        for key in ('semantic_review', 'human_signoff'):
            receipt = path.parent / config.get(key, '') if config.get(key) else None
            try:
                if receipt and json.loads(receipt.read_text(encoding='utf-8')).get('dependencies') == deps:
                    fresh.append(path); break
            except (OSError, ValueError):
                pass
    return fresh


# --- releases ---------------------------------------------------------------

def latest_release():
    """Newest vX.Y.Z tag on the public repository, or None when offline."""
    try:
        out = subprocess.run(['git', 'ls-remote', '--tags', '--refs', REPO_URL], capture_output=True,
                             text=True, timeout=20).stdout
    except (OSError, subprocess.TimeoutExpired):
        return None
    tags = re.findall(r'refs/tags/v(\d+\.\d+\.\d+)$', out, re.M)
    return max(tags, key=lambda t: tuple(map(int, t.split('.'))), default=None)


def auto_blockers(project_api, current, new, manifests):
    """Reasons an automatic update must not run (empty list = safe)."""
    cur, nxt = project_api.version_tuple(current), project_api.version_tuple(new)
    reasons = []
    if nxt[:2] != cur[:2]:
        reasons.append(f'{new} is a minor/major release; auto-update applies patches only')
    for manifest in manifests:
        try:
            pin = json.loads(manifest.read_text(encoding='utf-8')).get('engine')
        except (OSError, ValueError):
            continue
        if pin and project_api.engine_problem(pin, new):
            reasons.append(f'{manifest} pins engine {pin!r}')
    for path in fresh_reviews(project_api, manifests):
        reasons.append(f'{path} has a fresh review that the update would invalidate')
    return reasons


def install_command(tag):
    source = f'git+{REPO_URL}@v{tag}'
    if shutil.which('uv') and 'uv' in Path(sys.prefix).parts:
        return ['uv', 'tool', 'install', '--force', source]
    return [sys.executable, '-m', 'pip', 'install', '--upgrade', source]


def update(engine, args):
    """manuwright update [--check] [--auto] [--to X.Y.Z]"""
    current, api = engine_api(engine)
    auto = '--auto' in args
    if (engine / '.git').exists():
        if not auto:
            print('manuwright: running from a source checkout (Track A); update with git pull.')
        return 0 if auto else 1
    state = load('state.json', {})
    if auto and os.environ.get('MANUWRIGHT_NO_UPDATE_CHECK'):
        return 0
    if auto and state.get('last_check'):
        last = datetime.fromisoformat(state['last_check'])
        if datetime.now(timezone.utc) - last < timedelta(days=1):
            return 0
    target = args[args.index('--to') + 1] if '--to' in args else latest_release()
    save('state.json', {**state, 'last_check': datetime.now(timezone.utc).isoformat(), 'latest': target})
    if not target:
        print('manuwright: no release found (offline or no tags yet).', file=sys.stderr if auto else sys.stdout)
        return 0 if auto else 1
    target = target.lstrip('v')
    newer = api.version_tuple(target) > api.version_tuple(current)
    if '--check' in args or (auto and not newer):
        print(f'manuwright {current}; latest {target}' + ('' if newer else ' (up to date)'))
        return 0
    manifests = known_projects()
    if auto:
        if not load('config.json', {}).get('auto_update'):
            print(f'manuwright {target} available: run `manuwright update`.')
            return 0
        blockers = auto_blockers(api, current, target, manifests)
        if blockers:
            print(f'manuwright {target} available, not auto-applied:\n  - ' + '\n  - '.join(blockers)
                  + '\n  Run `manuwright update` when ready.')
            return 0
    stale = fresh_reviews(api, manifests)
    for path in stale:
        print(f'note: {path} review/signoff will need re-review after this update.')
    command = install_command(target)
    log = home() / 'update.log'
    home().mkdir(parents=True, exist_ok=True)
    if '--background' in args:  # session hooks have short timeouts; never kill an install midway
        handle = log.open('a', encoding='utf-8')
        handle.write(f'{datetime.now(timezone.utc).isoformat()} {current} -> {target} started (auto, background)\n')
        handle.flush()
        subprocess.Popen(command, stdout=handle, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         start_new_session=True)
        print(f'manuwright {current} -> {target}: auto-update running in the background '
              f'(log: {log}). New sessions use it; then run `manuwright agents update`.')
        return 0
    print('running: ' + ' '.join(command))
    code = subprocess.call(command)
    with log.open('a', encoding='utf-8') as handle:
        handle.write(f'{datetime.now(timezone.utc).isoformat()} {current} -> {target} exit={code}'
                     f'{" auto" if auto else ""}\n')
    if code == 0:
        print(f'manuwright {current} -> {target}. Roll back: manuwright update --to {current}')
    return code


REVIEW_AGENTS = ('claude', 'codex', 'opencode', 'muse', 'agy')
CONFIG_KEYS = {  # key -> (path in config.json, kind)
    'auto-update': (('auto_update',), 'onoff'),
    'main-model': (('main_model',), 'text'),
    'review.reviewers': (('review', 'reviewers'), 'list'),
    'review.openrouter-models': (('review', 'openrouter_models'), 'list'),
    **{f'review.{a}-model': (('review', f'{a}_model'), 'text') for a in REVIEW_AGENTS},
    # Saved default DOCX style; a project.json "docx" block overrides it per paper/journal.
    'docx.font': (('docx', 'font'), 'text'),
    **{f'docx.{k.replace("_", "-")}': (('docx', k), 'number')
       for k in ('size', 'heading_size', 'subheading_size', 'line_spacing', 'margin_inches')},
    'docx.line-numbers': (('docx', 'line_numbers'), ('continuous', 'page', 'off')),
    'docx.page-numbers': (('docx', 'page_numbers'), ('center', 'right', 'off')),
}
CONFIG_USAGE = ('usage: manuwright config [set <key> <value> | unset <key>]\n  keys: '
                + ', '.join(CONFIG_KEYS) + '\n  lists are comma-separated; reviewers are agent[:model] '
                '(openrouter:<id>, claude, codex, opencode, muse, agy)\n  docx.* is your default Word style; '
                'a project.json "docx" block overrides it for one paper')


def apply_setting(data, key, value):
    """Set (value) or clear (None) one CONFIG_KEYS entry in data. False if the value is invalid."""
    path, kind = CONFIG_KEYS[key]
    parent = data
    for part in path[:-1]:
        parent = parent.setdefault(part, {})
    if value is None:
        parent.pop(path[-1], None)
        return True
    if ((kind == 'onoff' and value not in {'on', 'off'}) or (isinstance(kind, tuple) and value not in kind)
            or (kind == 'number' and not (re.fullmatch(r'\d+(\.\d+)?', value) and float(value) > 0))):
        return False
    parent[path[-1]] = (value == 'on' if kind == 'onoff' else
                        [v.strip() for v in value.split(',') if v.strip()] if kind == 'list' else
                        float(value) if kind == 'number' else value)
    return True


def show_setting(data, key):
    value = data
    for part in CONFIG_KEYS[key][0]:
        value = value.get(part) if isinstance(value, dict) else None
    if value is None:
        return ''
    if isinstance(value, bool):
        return 'on' if value else 'off'
    if isinstance(value, list):
        return ','.join(value)
    return f'{value:g}' if isinstance(value, float) else str(value)


def config(args):
    """manuwright config [set <key> <value> | unset <key>]"""
    data = load('config.json', {})
    if args[:1] in (['set'], ['unset']) and len(args) >= 2 and args[1] in CONFIG_KEYS:
        if (len(args) != (2 if args[0] == 'unset' else 3)
                or not apply_setting(data, args[1], None if args[0] == 'unset' else args[2])):
            print(CONFIG_USAGE, file=sys.stderr)
            return 2
        save('config.json', data)
    elif args:
        print(CONFIG_USAGE, file=sys.stderr)
        return 2
    print(json.dumps({'home': str(home()), **data, 'projects': [str(p) for p in known_projects()]},
                     indent=2, ensure_ascii=False))
    return 0


SETUP_HELP = {
    'main-model': 'model that writes your manuscripts (reviewers using it are flagged)',
    'review.reviewers': 'default reviewers, comma-separated: claude, codex, opencode, muse, agy, openrouter[:model]',
    'review.openrouter-models': 'OpenRouter models for a bare "openrouter" reviewer, comma-separated',
    'docx.font': 'Word font', 'docx.size': 'body text size (pt)', 'docx.heading-size': 'section heading size (pt)',
    'docx.subheading-size': 'subheading size (pt)', 'docx.line-spacing': 'line spacing (2 = double)',
    'docx.margin-inches': 'page margins (inches)', 'docx.line-numbers': 'line numbers: continuous, page, off',
    'docx.page-numbers': 'page numbers: center, right, off',
    'auto-update': 'install patch updates automatically: on/off',
}


def setup(args, ask=input):
    """manuwright setup: one interactive pass over models, reviewers, Word style, updates and Obsidian."""
    if not sys.stdin.isatty() and ask is input:
        print('manuwright setup is interactive; run it in a terminal, or use: manuwright config set <key> <value>',
              file=sys.stderr)
        return 2
    data = load('config.json', {})
    print('manuwright setup. Enter keeps the value in [brackets]; "-" clears it (engine default).\n')

    def prompt(key):
        while True:
            answer = ask(f'{SETUP_HELP.get(key, key)}\n  {key} [{show_setting(data, key)}]: ').strip()
            if not answer or apply_setting(data, key, None if answer == '-' else answer):
                return
            print('  not valid here; try again.')

    print('1. Models and reviewers')
    for key in ('main-model', 'review.reviewers'):
        prompt(key)
    chosen = [r.split(':')[0].strip() for r in data.get('review', {}).get('reviewers', [])]
    if 'openrouter' in chosen:
        prompt('review.openrouter-models')
    for agent in REVIEW_AGENTS:
        if agent in chosen:
            SETUP_HELP[f'review.{agent}-model'] = f'model for the {agent} reviewer (empty = its own default)'
            prompt(f'review.{agent}-model')
    print('\n2. Word (DOCX) style: your default; a project.json "docx" block overrides it per journal')
    if ask('  Change the Word style? [y/N]: ').strip().lower() in {'y', 'yes'}:
        for key in [k for k in CONFIG_KEYS if k.startswith('docx.')]:
            prompt(key)
    print('\n3. Updates')
    prompt('auto-update')
    save('config.json', data)
    print(f'\nSaved to {home() / "config.json"}.')
    print('\n4. Obsidian reference library (optional, recommended)')
    try:
        from manuwright import obsidian
    except ImportError:  # lifecycle loaded from an engine folder (see agents())
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from manuwright import obsidian
    obsidian.offer_connect()
    return 0

# --- init / rules -----------------------------------------------------------

ANALYSIS_PLAN = """# Analysis Plan

## Research Question

## Study Population

## Variable Definitions

## Statistical Methods

## Significance and Multiple Comparisons

## Missing Data

- [ ] 사용자 승인 완료
"""


def init(engine, args):
    """manuwright init [folder]: starter paper folder; never overwrites, never approves."""
    root = Path(args[0] if args else '.').resolve()
    if (root / 'project.json').exists():
        print(f'manuwright: {root / "project.json"} already exists; nothing changed.', file=sys.stderr)
        return 1
    manifest = json.loads((engine / 'docs' / 'project.example.json').read_text(encoding='utf-8'))
    bootstrap = (engine / 'docs' / 'agent_bootstrap.md').read_text(encoding='utf-8')
    manifest['paper_id'] = re.sub(r'[^a-z0-9]+', '_', root.name.lower()).strip('_') or 'paper'
    files = {
        'project.json': json.dumps(manifest, indent=2, ensure_ascii=False) + '\n',
        'drafts/draft_plan.md': (engine / 'docs' / 'draft_plan_template.md').read_text(encoding='utf-8'),
        'data/analysis_plan.md': ANALYSIS_PLAN,
        'knowledge/evidence.md': '# Evidence\n',
        'AGENTS.md': bootstrap,
        'CLAUDE.md': bootstrap,
        'GEMINI.md': bootstrap,
    }
    for folder in ('data', 'drafts', 'knowledge/pdf', 'results', 'review/gates', 'output'):
        (root / folder).mkdir(parents=True, exist_ok=True)
    for name, text in files.items():
        target = root / name
        if target.exists():
            print(f'kept existing {name}')
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')
        print(f'created {name}')
    register(root / 'project.json')
    print(f'\nNext: fill drafts/draft_plan.md and data/analysis_plan.md, get approval, then edit '
          f'project.json artifacts. `manuwright verify --project {root / "project.json"}` reports what is missing.')
    return 0


def rules(engine, args):
    """manuwright rules [keyword] | --path"""
    workflow = engine / 'WORKFLOW.md'
    if args[:1] == ['--path']:
        print(workflow)
        return 0
    text = workflow.read_text(encoding='utf-8')
    if not args:
        print(text)
        return 0
    keyword = ' '.join(args).lower()
    parts = re.split(r'(?m)^(?=#{2,3} )', text)
    hits = [part for part in parts if keyword in part.splitlines()[0].lower()]
    print('\n'.join(hits) if hits else f'No section heading contains {keyword!r}. Headings:\n'
          + '\n'.join(line for line in text.splitlines() if line.startswith(('## ', '### '))))
    return 0 if hits else 1


# --- agent adapters ---------------------------------------------------------

AGENTS = ('claude', 'codex', 'agy', 'opencode', 'muse')


def agent_steps(engine, agent, mode):
    """Native commands (or a copy step) that install/update this engine's adapters for one agent.

    The installed engine folder is itself the plugin/marketplace root, so adapters always
    match the CLI version that installed them.
    """
    root, skills = str(engine), sorted(p for p in (engine / 'skills').iterdir() if (p / 'SKILL.md').is_file())
    if agent == 'claude':
        if mode == 'install':
            return [['claude', 'plugin', 'marketplace', 'add', root], ['claude', 'plugin', 'install', 'manuwright@manuwright']]
        return [['claude', 'plugin', 'marketplace', 'update', 'manuwright'], ['claude', 'plugin', 'update', 'manuwright@manuwright']]
    if agent == 'codex':
        first = ['codex', 'plugin', 'marketplace', 'add', root] if mode == 'install' else ['codex', 'plugin', 'marketplace', 'upgrade']
        return [first, ['codex', 'plugin', 'add', 'manuwright@manuwright']]
    if agent == 'agy':
        return [['agy', 'plugin', 'install', root]]
    if agent == 'muse':
        return [['muse', 'skills', 'install', str(s), '--scope', 'user', '--force'] for s in skills]
    if agent == 'opencode':
        base = Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / 'opencode' / 'skills'
        return [('copy', s, base / s.name) for s in skills]
    raise ValueError(agent)


def agents(engine, args):
    """manuwright agents install|update [--only a,b] [--dry-run]"""
    if not args or args[0] not in {'install', 'update'}:
        print('usage: manuwright agents install|update [--only claude,codex,agy,opencode,muse] [--dry-run]',
              file=sys.stderr)
        return 2
    mode, dry = args[0], '--dry-run' in args
    chosen = args[args.index('--only') + 1].split(',') if '--only' in args else list(AGENTS)
    unknown = set(chosen) - set(AGENTS)
    if unknown:
        print(f'unknown agent(s): {", ".join(sorted(unknown))}', file=sys.stderr)
        return 2
    failed = 0
    for agent in chosen:
        executable = 'opencode' if agent == 'opencode' else agent
        if not shutil.which(executable):
            print(f'[{agent}] not installed; skipped', flush=True)
            continue
        for step in agent_steps(engine, agent, mode):
            if step[0] == 'copy':
                print(f'[{agent}] copy {step[1]} -> {step[2]}', flush=True)
                if not dry:
                    shutil.rmtree(step[2], ignore_errors=True)
                    shutil.copytree(step[1], step[2])
                continue
            print(f'[{agent}] ' + ' '.join(step), flush=True)
            if not dry:
                code = subprocess.call(step)
                if code:
                    failed += 1
                    print(f'[{agent}] exit {code}; continuing with the next agent')
                    break
    print('Mandatory rules come from each paper folder (CLAUDE.md / AGENTS.md / GEMINI.md, see manuwright init).')
    if mode == 'install' and not dry:
        try:
            from manuwright import obsidian
        except ImportError:
            sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
            from manuwright import obsidian
        obsidian.offer_connect()
    return 1 if failed else 0

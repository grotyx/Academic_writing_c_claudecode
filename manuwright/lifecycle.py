"""manuwright init / rules / update / config (docs/distribution_plan.md, phase 3).

Update policy: check automatically, apply explicitly. Opt-in auto-update applies
only patch releases, and only when no known project pins the engine away from
the new version or holds a fresh semantic review / human signoff that an
engine change would invalidate.
"""
from __future__ import annotations
import importlib.util
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
                             text=True, encoding='utf-8', errors='replace', timeout=20).stdout
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


def native(argv):
    """argv with the program resolved on PATH. On Windows, npm-installed agent CLIs are .cmd
    shims that shutil.which finds but CreateProcess does not, so a bare name fails with
    FileNotFoundError [WinError 2]."""
    return [shutil.which(argv[0]) or argv[0], *argv[1:]]


def on_windows():
    return os.name == 'nt'


def install_command(tag):
    source = f'git+{REPO_URL}@v{tag}'
    if shutil.which('uv') and 'uv' in Path(sys.prefix).parts:
        return ['uv', 'tool', 'install', '--force', source]
    return [sys.executable, '-m', 'pip', 'install', '--upgrade', source]


def update(engine, args):
    """manuwright update [--check] [--auto] [--to X.Y.Z] [--no-agents]"""
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
    if '--check' in args or (not newer and '--to' not in args):
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
    if on_windows() and command[0] == 'uv':
        # uv deletes the tool environment before reinstalling; Windows cannot replace the running
        # manuwright.exe, so an in-process update left a half-removed install (ModuleNotFoundError).
        print(f'manuwright {current} -> {target}: Windows cannot replace manuwright while it is running.\n'
              'Close agent sessions (Claude Code, Codex, ...) and paste this line into a new PowerShell window '
              '(it installs, then refreshes the agent adapters):\n'
              f'  {" ".join(command)}; if ($?) {{ manuwright agents update; manuwright init --refresh-rules --all --auto }}\n'
              '(Paper folders you open later in Claude Code or Codex also update their agent rules themselves.)')
        return 0
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
    if code != 0:
        return code
    print(f'manuwright {current} -> {target}. Roll back: manuwright update --to {current}')
    if '--no-agents' in args:
        print('Agent adapters not refreshed (--no-agents): run `manuwright agents update`.')
    else:
        # Run the newly installed CLI, not this process: its code (and even its Python) is the old one.
        print('Refreshing the agent adapters: manuwright agents update', flush=True)
        if subprocess.call([shutil.which('manuwright') or 'manuwright', 'agents', 'update']):
            print('Agent refresh reported a problem above; fix it and run `manuwright agents update` again.')
    if known_projects():
        # Automatic: only rule files manuwright wrote are replaced (.bak kept); a CLAUDE.md the author
        # wrote is reported, never replaced. Run through the new CLI, which carries the new rules.
        print('Updating the agent rules of your paper folders: manuwright init --refresh-rules --all --auto', flush=True)
        subprocess.call([shutil.which('manuwright') or 'manuwright', 'init', '--refresh-rules', '--all', '--auto'])
    print('Paper folders you open later in Claude Code or Codex also update their agent rules themselves.')
    return 0


def paper_refresh_hint():
    """Which paper folders still carry the old agent rules, and the command that updates them."""
    papers = [m.parent for m in known_projects()]
    if not papers:
        return 'In each existing paper folder: `manuwright init --refresh-rules` (updates only its agent rule files).'
    return ('Update the agent rules of every registered paper at once (only AGENTS/CLAUDE/GEMINI.md change; .bak '
            'copies kept): `manuwright init --refresh-rules --all`. Registered papers:\n'
            + '\n'.join(f'  {p}' for p in dict.fromkeys(papers)))


REVIEW_AGENTS = ('claude', 'codex', 'opencode', 'muse', 'agy')
CONFIG_KEYS = {  # key -> (path in config.json, kind)
    'auto-update': (('auto_update',), 'onoff'),
    'writing-mode': (('writing_mode',), ('academic', 'strict', 'off')),
    'library-sync': (('library_sync',), ('auto', 'ask', 'off')),
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
    'writing-mode': 'academic writing mode: academic (cards + findings after each edit), strict (also blocks), off',
}


KEY_SAVED = []  # set when this run of setup stored a key


def models_masked_input(prompt):
    from manuwright import models
    return models.masked_input(prompt)


def openrouter_key_step(secret, ask=input):
    """Make sure OpenRouter reviewers have a key: environment, saved key, or ask (hidden input)."""
    from manuwright import models
    if os.environ.get('OPENROUTER_API_KEY'):
        print('  OpenRouter key: using the OPENROUTER_API_KEY environment variable.')
        return
    secrets = load('secrets.json', {})
    secrets = secrets if isinstance(secrets, dict) else {}
    saved = secrets.get('openrouter_api_key')
    hint = f' (saved: ...{saved[-4:]}; Enter keeps it)' if saved else ' (Enter to skip)'
    print('  Paste the key, or copy it and just press Enter to read it from the clipboard.')
    key = secret(f'  OpenRouter API key, from https://openrouter.ai/keys{hint}: ').strip()
    clipped = '' if key else models.clipboard_key()
    if clipped and clipped != saved:
        answer = ask(f'  Use the key on the clipboard, {models.mask(clipped)}? [Y/n]: ').strip().lower()
        key = clipped if answer in ('', 'y', 'yes') else ''
    if not key:
        if not saved:
            print('  No key: OpenRouter reviewers will be skipped until you set one (run setup again).')
        return
    print(f'  Received key {models.mask(key)}. Checking it with OpenRouter...')
    works = models.key_works(key)
    if works is False:
        print('  OpenRouter rejected this key; it was not saved.')
        return
    secrets['openrouter_api_key'] = key
    home().mkdir(parents=True, exist_ok=True)
    path, staged = home() / 'secrets.json', home() / '.secrets.json.new'
    staged.unlink(missing_ok=True)
    fd = os.open(staged, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)  # owner-only from the first byte
    with os.fdopen(fd, 'w', encoding='utf-8') as handle:
        json.dump(secrets, handle)
    os.replace(staged, path)  # never a moment where the key sits in a wider-readable file
    KEY_SAVED.append(True)
    print('  Key saved to ' + str(home() / 'secrets.json') + (' (checked with OpenRouter).' if works else
          ' (could not reach OpenRouter to check it).'))


def setup(args, ask=input, secret=None):
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

    KEY_SAVED.clear()
    if secret is None:
        secret = models_masked_input if ask is input else ask
    try:
        return _setup_steps(data, prompt, ask, secret)
    except (EOFError, KeyboardInterrupt):
        print('\nSetup stopped; settings not saved' + (' (the OpenRouter key you entered was saved).' if KEY_SAVED else '.'))
        return 1


def main_model_step(data, ask, models):
    """Numbered main-model choice (terminals without the arrow menu, e.g. Windows): a number picks a
    listed model, any other text is a model id, Enter keeps, "-" clears."""
    options = models.writer_options(data.get('main_model'))
    print(SETUP_HELP['main-model'])
    for i, (value, label) in enumerate(options, 1):
        print(f"   {i}. {label}{'  (current)' if value == data.get('main_model') else ''}")
    while True:
        answer = ask(f"  main-model: number or model id [{show_setting(data, 'main-model')}]: ").strip()
        if not answer:
            return
        if answer.isdigit():
            if 1 <= int(answer) <= len(options):
                data['main_model'] = options[int(answer) - 1][0]
                return
        elif answer in models.AGENTS:
            print(f'  {answer} is an agent, not a model: pick the model you write with by number.')
            continue
        elif apply_setting(data, 'main-model', None if answer == '-' else answer):
            return
        print('  not valid here; try again.')


def _setup_steps(data, prompt, ask, secret):
    try:
        from manuwright import models
    except ImportError:  # lifecycle loaded from an engine folder (see agents())
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from manuwright import models
    print('1. Models and reviewers')
    review = data.setdefault('review', {})
    current = [r.strip() for r in review.get('reviewers', [])]
    local = [r for r in current if r.split(':')[0] in models.AGENTS]
    menu = models.can_menu() and ask is input
    if menu:
        main = data.get('main_model')
        print('Reviewers read the finished draft in the independent review step (critical review). '
              'Pick 3-5 that differ from the model you write with.')
        picked = models.pick('Main model: the model you WRITE with (not a reviewer; a reviewer on it is flagged)',
                             models.writer_options(main) + [('', 'other: type a model id')], {main}, single=True)
        if picked == ['']:
            prompt('main-model')
        elif picked:
            data['main_model'] = picked[0]
        picked = models.pick('Agent reviewers: run on your signed-in plan, no API cost',
                             [(a, models.AGENT_LABELS[a] + ('' if shutil.which(a) else '   - not installed'))
                              for a in models.AGENTS],
                             set(local))
        if picked is not None:
            local = picked
    else:
        main_model_step(data, ask, models)
        SETUP_HELP['review.local'] = ('agent reviewers on your signed-in plan (subscription), comma-separated: '
                                      'claude, codex, muse, agy (empty = none)')
        for agent in models.AGENTS:
            print(f"   {agent:<6} {models.AGENT_LABELS[agent]}{'' if shutil.which(agent) else '   - not installed'}")
        answer = ask(f"{SETUP_HELP['review.local']}\n  agents [{','.join(local) or 'none'}]: ").strip()
        if answer:
            local = [] if answer == '-' else [a.strip() for a in answer.split(',') if a.strip()]
    print('Checking the current OpenRouter and opencode model lists...')
    prices = models.openrouter_prices()
    openrouter = models.choose('OpenRouter', models.OPENROUTER_SETS, review.get('openrouter_models', [])
                               if 'openrouter' in current else [], set(prices), prices, ask)
    if openrouter is None:
        openrouter = review.get('openrouter_models', []) if 'openrouter' in current else []
    if openrouter:
        openrouter_key_step(secret, ask)
    opencode_now = [r.split(':', 1)[1] for r in current if r.startswith('opencode:')]
    opencode = models.choose('opencode', models.OPENCODE_SETS, opencode_now, models.opencode_models(), None, ask)
    if opencode is None:
        opencode = opencode_now
    if openrouter:
        review['openrouter_models'] = openrouter
    review['reviewers'] = local + (['openrouter'] if openrouter else []) + [f'opencode:{m}' for m in opencode]
    print(f"  reviewers: {', '.join(review['reviewers']) or 'none'}")
    print('\n2. Updates')
    if 'auto_update' in data:
        prompt('auto-update')
    else:  # first setup: recommend on; Enter accepts
        while True:
            answer = ask(f"{SETUP_HELP['auto-update']} (recommended: on; on Windows it only announces new "
                         "releases)\n  auto-update [on]: ").strip().lower()
            if answer in ('', 'on', 'off'):
                data['auto_update'] = answer != 'off'
                break
            print('  not valid here; try again.')
    save('config.json', data)
    print(f'\nSaved to {home() / "config.json"}.')
    print('\n3. Obsidian reference library (optional, recommended)')
    print('Word style and reference format belong to each paper: run `manuwright target` inside a paper folder.')
    try:
        from manuwright import obsidian
    except ImportError:  # lifecycle loaded from an engine folder (see agents())
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from manuwright import obsidian
    obsidian.offer_connect()
    return 0

# --- per-paper settings -----------------------------------------------------

DOCX_DEFAULT_TEXT = 'Times New Roman 10 pt, double spacing, 1-inch margins, line numbers, page numbers centred'
FONTS = ['Times New Roman', 'Arial', 'Calibri', 'Cambria', 'Helvetica']


def find_manifest(args):
    if '--project' in args:
        index = args.index('--project') + 1
        return Path(args[index]).resolve() if index < len(args) else None
    for folder in [Path.cwd(), *Path.cwd().parents]:
        if (folder / 'project.json').is_file():
            return folder / 'project.json'
    return None


def target(engine, args, ask=input):
    """manuwright target [--project PATH]: this paper's target journal and Word style, saved in its project.json."""
    from manuwright import models
    path = find_manifest(args)
    if not path or not path.is_file():
        print('manuwright target: no project.json here or above; run it inside a paper folder '
              '(manuwright init <folder> creates one) or pass --project PATH.', file=sys.stderr)
        return 2
    if not sys.stdin.isatty() and ask is input:
        print('manuwright target is interactive; run it in a terminal, or edit "journal" and "docx" in '
              f'{path}', file=sys.stderr)
        return 2
    config = json.loads(path.read_text(encoding='utf-8'))
    before = json.dumps(config, sort_keys=True)
    spec = importlib.util.spec_from_file_location('journal_styles', engine / 'scripts' / 'journal_styles.py')
    styles = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(styles)
    print(f'Settings for this paper only ({path})\n')
    try:
        journal = models.select_one(
            '1. Target journal: reference list format and in-text markers',
            [(name, f"{style['label']}  ({name})") for name, style in styles.STYLES.items()]
            + [('', 'None: keep the registered citation strings, numbered [1]')], config.get('journal', ''), ask)
        if journal is not None:
            if journal:
                config['journal'] = journal
            else:
                config.pop('journal', None)
        docx = dict(config.get('docx', {}))
        now = ', '.join(f'{k}={v}' for k, v in docx.items()) or f'default ({DOCX_DEFAULT_TEXT})'
        from manuwright import library
        saved = library.docx_styles()
        label = lambda key: styles.STYLES[key]['label'] if key in styles.STYLES else key
        target_journal = config.get('journal')
        ranked = sorted(saved.items(), key=lambda item: (
            0 if item[1]['journal'] and item[1]['journal'] == target_journal else
            1 if item[1]['for'] in ('team', 'personal') else 2, item[0]))
        matching = [n for n, s in ranked if s['journal'] and s['journal'] == target_journal]
        if matching:
            print(f"  You have a saved Word style for {label(target_journal)}: {matching[0]} (listed first).")
        action = models.select_one(f'2. Word style for this paper (now: {now})',
                                   [('keep', 'Keep as it is'), ('default', f'Default: {DOCX_DEFAULT_TEXT}')]
                                   + [(f'lib:{n}', library.describe_style(n, s, label)
                                       + ('   <- suggested for this journal' if n in matching else ''))
                                      for n, s in ranked]
                                   + [('custom', "Set this paper's own style")], 'keep', ask)
        if action == 'default':
            docx = {}
        elif action and action.startswith('lib:'):
            docx = library.apply_docx_style(action[4:], path.parent)
        elif action == 'custom':
            docx = {k: v for k, v in docx.items() if k != 'reference'}  # own style replaces a template
            font = models.select_one('Font', [(f, f) for f in FONTS] + [('other', 'other: type a font name')],
                                     docx.get('font', 'Times New Roman'), ask)
            if font == 'other':
                font = ask('  Font name: ').strip() or None
            choices = [
                ('size', 'Body text size (pt)', [(10, '10'), (11, '11'), (12, '12')], 10),
                ('line_spacing', 'Line spacing', [(1.0, 'single'), (1.5, '1.5'), (2.0, 'double')], 2.0),
                ('margin_inches', 'Margins', [(1.0, '1 inch (2.54 cm)'), (0.79, '2 cm'), (1.18, '3 cm')], 1.0),
                ('line_numbers', 'Line numbers', [('continuous', 'continuous'), ('page', 'restart each page'),
                                                  ('off', 'off')], 'continuous'),
                ('page_numbers', 'Page numbers', [('center', 'bottom centre'), ('right', 'bottom right'),
                                                  ('off', 'off')], 'center'),
            ]
            if font:
                docx['font'] = font
            for key, title, options, default in choices:
                value = models.select_one(title, options, docx.get(key, default), ask)
                if value is not None:
                    docx[key] = value
            where = models.select_one('Save this style to your library?',
                                      ([('journal', f'Yes, for {label(target_journal)} papers')] if target_journal else [])
                                      + [('team', 'Yes, as a team style'), ('personal', 'Yes, as my style'),
                                         ('no', 'No')], 'no', ask)
            if where in ('journal', 'team', 'personal'):
                default = target_journal if where == 'journal' else where
                name = ask(f'  Name [{default}]: ').strip() or default
                try:
                    saved_name = library.save_docx_style(name, docx, scope=where,
                                                         journal=target_journal if where == 'journal' else None)
                    print(f'  saved as "{saved_name}"')
                except ValueError as exc:
                    print(f'  not saved: {exc}')
        if docx:
            config['docx'] = docx
        else:
            config.pop('docx', None)
    except (EOFError, KeyboardInterrupt):
        print('\nStopped; project.json unchanged.')
        return 1
    if json.dumps(config, sort_keys=True) == before:
        print('\nNothing changed.')
        return 0
    path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f"\nSaved to {path}: journal={config.get('journal', 'none')}, "
          f"Word style={config.get('docx', 'default')}.\n"
          'project.json is part of the review record: reviews or sign-off made before this change are now stale; '
          'run `manuwright verify` and renew them before the submission build.')
    return 0


project = target  # earlier name, kept working


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


BOOTSTRAP_FILES = ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md')


MANAGED_HEADERS = ('# manuwright agent instructions', '# paperflow agent instructions')


def managed(text):
    """A rule file manuwright wrote (any version), as opposed to one the author wrote."""
    return text.lstrip('\ufeff').startswith(MANAGED_HEADERS)


def refresh_rules(engine, root, auto=False):
    """Bring an existing paper's agent rule files up to this engine version (old copies kept as .bak).
    auto (update, session start): replace only files manuwright wrote; an author's own file is reported."""
    bootstrap = (engine / 'docs' / 'agent_bootstrap.md').read_text(encoding='utf-8')
    changed, kept = [], []
    # A template checkout imports WORKFLOW.md from CLAUDE.md only; its AGENTS.md and GEMINI.md are the
    # template's own, so the whole folder is left alone when any rule file does.
    if any('@WORKFLOW.md' in (root / n).read_text(encoding='utf-8', errors='replace')
           for n in BOOTSTRAP_FILES if (root / n).exists()):
        print('kept the agent rules: this folder is a template checkout; update it with `git pull` instead.')
        return 0
    for name in BOOTSTRAP_FILES:
        target = root / name
        if target.exists() and target.read_text(encoding='utf-8') == bootstrap:
            continue
        if auto and target.exists() and not managed(target.read_text(encoding='utf-8', errors='replace')):
            kept.append(name)
            continue
        if target.exists():
            shutil.copyfile(target, target.with_name(name + '.bak'))
        target.write_text(bootstrap, encoding='utf-8')
        changed.append(name)
    print(f"Agent rules {'updated: ' + ', '.join(changed) + ' (previous copies saved as .bak)' if changed else 'already current'}."
          ' Nothing else in the paper was changed.'
          + (f" Kept {', '.join(kept)}: written by you, not by manuwright; `manuwright init --refresh-rules` in that"
             ' folder replaces it (with a .bak copy).' if kept else ''))
    return 0


def stale_papers(engine):
    """Registered paper folders whose agent rule files differ from this engine's (template checkouts excluded)."""
    bootstrap = (engine / 'docs' / 'agent_bootstrap.md').read_text(encoding='utf-8')
    stale = []
    for root in dict.fromkeys(m.parent for m in known_projects()):
        texts = [(root / n).read_text(encoding='utf-8', errors='replace') for n in BOOTSTRAP_FILES if (root / n).exists()]
        if any('@WORKFLOW.md' in t for t in texts):
            continue
        if len(texts) < len(BOOTSTRAP_FILES) or any(t != bootstrap for t in texts):
            stale.append(root)
    return stale


def refresh_all(engine, auto=False):
    """`manuwright init --refresh-rules --all [--auto]`: refresh every registered paper folder."""
    roots = list(dict.fromkeys(m.parent for m in known_projects()))
    if not roots:
        print('No registered paper folders yet (a paper registers when `manuwright verify` runs in it). '
              'Run `manuwright init --refresh-rules` inside a paper folder instead.')
        return 0
    for root in roots:
        print(f'{root}: ', end='', flush=True)
        refresh_rules(engine, root, auto=auto)
    return 0


EVIDENCE_STARTER = """# Evidence

<!-- One entry per source; cite it in drafts as [EVID:<Evidence ID>]. `manuwright search "<query>"` and
`manuwright search doi <doi>` print ready-made entries. Example (delete it when you add your own):

### [1] Kim et al., 2020
- **Evidence ID:** kim_2020_pmid12345678
- **Citation:** Kim A, Lee B. Title of the paper. Spine J. 2020;20:100-110.
- **DOI:** 10.xxxx/xxxxx
- **PMID:** 12345678
- **Source Status:** verified            (verified | full-text-reviewed | abstract-only | todo)
- **Claim Strength:** observed           (speculative | observed | supported | strong)
- **Allowed Wording:** was associated with
- **Study Design:** retrospective cohort, n = 412
- **Main Findings:** ...
-->
"""


PAPER_GITIGNORE = """# manuwright: copyright-protected or private material stays on this computer
knowledge/pdf/
Style/PDF/
Style/profile/
**/Style/profile/
"""


def init(engine, args):
    """manuwright init [folder] [--refresh-rules [--all]]: starter paper folder; never overwrites, never approves."""
    refresh = '--refresh-rules' in args
    auto = '--auto' in args
    if refresh and '--all' in args:
        return refresh_all(engine, auto=auto)
    args = [a for a in args if a not in ('--refresh-rules', '--all', '--auto')]
    root = Path(args[0] if args else '.').resolve()
    if (root / 'project.json').exists():
        if refresh:
            return refresh_rules(engine, root, auto=auto)
        print(f'manuwright: {root / "project.json"} already exists; nothing changed. After an update, '
              f'`manuwright init --refresh-rules` brings this paper\'s agent rules (AGENTS.md, CLAUDE.md, '
              'GEMINI.md) up to date.', file=sys.stderr)
        return 1
    from manuwright import analysis_env
    manifest = json.loads((engine / 'docs' / 'project.example.json').read_text(encoding='utf-8'))
    bootstrap = (engine / 'docs' / 'agent_bootstrap.md').read_text(encoding='utf-8')
    manifest['paper_id'] = re.sub(r'[^a-z0-9]+', '_', root.name.lower()).strip('_') or 'paper'
    files = {
        'project.json': json.dumps(manifest, indent=2, ensure_ascii=False) + '\n',
        'drafts/draft_plan.md': (engine / 'docs' / 'draft_plan_template.md').read_text(encoding='utf-8'),
        'data/analysis_plan.md': ANALYSIS_PLAN,
        'data/requirements.txt': analysis_env.DEFAULT_REQUIREMENTS,
        'knowledge/evidence.md': EVIDENCE_STARTER,
        '.gitignore': PAPER_GITIGNORE,
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
    from manuwright import library
    updates, copied = library.copy_into_paper(root)
    if updates:
        manifest_path = root / 'project.json'
        manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
        manifest.update(updates)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for name in copied:
        print(f'copied {name} from your library')
    register(root / 'project.json')
    print('\nSet the target journal and this paper\'s Word style any time: cd into the folder and run '
          '`manuwright target`.')
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
        print(text.rstrip() + guide_footer(engine, text))
        return 0
    keyword = ' '.join(args).lower()
    parts = re.split(r'(?m)^(?=#{2,3} )', text)
    hits = [part for part in parts if keyword in part.splitlines()[0].lower()]
    print('\n'.join(hits).rstrip() + guide_footer(engine, '\n'.join(hits)) if hits else
          f'No section heading contains {keyword!r}. Headings:\n'
          + '\n'.join(line for line in text.splitlines() if line.startswith(('## ', '### '))))
    return 0 if hits else 1


# --- engine guides (docs/) --------------------------------------------------
# The rules cite guides as `docs/<name>.md`. Those live in the installed engine, not in the
# paper folder, so agents read them with `manuwright guide <name>` instead of opening a path.

def guide_files(engine):
    """{name: path} for every guide, name relative to docs/ without .md (e.g. 'writing_guide')."""
    root = engine / 'docs'
    return {p.relative_to(root).with_suffix('').as_posix(): p for p in sorted(root.rglob('*.md'))}


def guide_title(path):
    for line in path.read_text(encoding='utf-8', errors='replace').splitlines():
        if line.startswith('#'):
            return line.lstrip('#').strip()
    return ''


# A guide mention ends at ".md" not followed by another identifier character. Not \b: in Python 3
# Hangul is a word character, so "writing_guide.md에" (a Korean particle right after) must still match.
GUIDE_MENTION = re.compile(r'([A-Za-z0-9_./\\-]+?)\.md(?![A-Za-z0-9_])')


def guide_key(raw, files, base=''):
    """The guide a path or name refers to, or None. Accepts docs/x.md, ./docs/x.md, an absolute engine
    path, a bare name, any case, and (with base) a name relative to the citing guide's own folder."""
    key = raw.replace('\\', '/')
    key = re.sub(r'\.md$', '', key)
    if 'docs/' in key.lower():
        key = key[key.lower().rindex('docs/') + 5:]
    key = key.lstrip('./').strip('/')
    lower = {n.lower(): n for n in files}
    for candidate in ([f'{base}/{key}'] if base else []) + [key]:
        if candidate.lower() in lower:
            return lower[candidate.lower()]
    return None


def guide_refs(files, text, base=''):
    """Guides that text cites, in order of first mention, existing ones only."""
    found = (guide_key(m, files, base) for m in GUIDE_MENTION.findall(text))
    return [n for n in dict.fromkeys(found) if n]


def guide_footer(engine, text):
    refs = guide_refs(guide_files(engine), text)
    if not refs:
        return ''
    return ('\n\n--- Guides cited above (they live in the engine, not in this folder). Read the one for this '
            'step with `manuwright guide <name>`, or all at once: `manuwright guide ' + ' '.join(refs) + '`\n'
            + '\n'.join(f'  {n}' for n in refs))


def guide(engine, args):
    """manuwright guide [name ...]: list the engine guides, or print one or more in full."""
    files = guide_files(engine)
    if not args:
        print('Engine guides (the rules cite them as docs/<name>.md). Print one: manuwright guide <name>')
        for name, path in files.items():
            print(f'  {name:<32} {guide_title(path)}')
        return 0
    wanted, missing = [], []
    for arg in args:
        match = guide_key(arg, files)
        (wanted if match else missing).append(match or arg)
    wanted = list(dict.fromkeys(wanted))
    for i, name in enumerate(wanted):  # print every guide that exists, even if another name was wrong
        text = files[name].read_text(encoding='utf-8')
        base = name.rpartition('/')[0]
        cited = [n for n in guide_refs(files, text, base) if n != name and n not in wanted]
        print(('\n\n' if i else '') + f'===== docs/{name}.md =====\n' + text.rstrip()
              + (f'\n\n--- This guide also cites: {", ".join(cited)} (manuwright guide <name>)' if cited else ''))
    if missing:
        import difflib
        for arg in missing:
            key = re.sub(r'\.md$', '', arg.replace('\\', '/')).rpartition('docs/')[2].lstrip('./')
            close = difflib.get_close_matches(key, list(files), n=3, cutoff=0.5)
            print(f'No guide {arg!r}.' + (f' Did you mean: {", ".join(close)}?' if close else '')
                  + ' List them with `manuwright guide`.', file=sys.stderr)
        return 1
    return 0


MODE_HELP = {
    'academic': 'section style cards at session start and on drafting requests; academic-prose findings after '
                'each edit (default)',
    'strict': 'as academic, and a write to a manuscript section whose new text has high-severity findings is '
              'blocked until it is rewritten',
    'off': 'no style cards and no academic-prose findings (terminology lint still runs)',
}


def mode(args):
    """manuwright mode [academic|strict|off]: show or set the academic writing mode."""
    data = load('config.json', {})
    if args:
        if len(args) != 1 or args[0] not in MODE_HELP:
            print('usage: manuwright mode [academic|strict|off]', file=sys.stderr)
            return 2
        data['writing_mode'] = args[0]
        save('config.json', data)
    current = data.get('writing_mode') if data.get('writing_mode') in MODE_HELP else 'academic'
    print(f'Writing mode: {current}: {MODE_HELP[current]}.')
    override = os.environ.get('MANUWRIGHT_WRITING_MODE', '').strip().lower()
    if override in MODE_HELP and override != current:
        print(f'MANUWRIGHT_WRITING_MODE={override} overrides it in this shell.')
    if not args:
        print('Change it: manuwright mode academic|strict|off. Cards: manuwright style card <section>; '
              'learn a corpus: manuwright style learn <papers>.')
    return 0


# --- health check ------------------------------------------------------------

def _run_text(argv):
    """Output of a quick agent CLI query, or None when it cannot run."""
    try:
        done = subprocess.run(native(argv), capture_output=True, text=True, encoding='utf-8', errors='replace',
                              timeout=30, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return done.stdout if done.returncode == 0 else None


def _same_path(a, b):
    try:
        return Path(str(a).removeprefix('\\\\?\\')).resolve() == Path(b).resolve()
    except (OSError, ValueError):
        return False


def adapter_checks(engine, current):
    """[(ok, label, detail)] for each installed agent: marketplace points at this engine, plugin version."""
    rows = []
    if shutil.which('claude'):
        markets = _run_text(['claude', 'plugin', 'marketplace', 'list', '--json'])
        plugins = _run_text(['claude', 'plugin', 'list', '--json'])
        try:
            market = next((m for m in json.loads(markets or '[]') if m.get('name') == 'manuwright'), None)
            plugin = next((p for p in json.loads(plugins or '[]') if p.get('id') == 'manuwright@manuwright'), None)
        except ValueError:
            market = plugin = None
        if markets is None or plugins is None:
            rows.append((None, 'Claude Code', 'could not query `claude plugin`'))
        elif not market or not plugin:
            rows.append((False, 'Claude Code', 'manuwright plugin not installed'))
        elif not _same_path(market.get('path', ''), engine):
            rows.append((False, 'Claude Code', f"marketplace points at {market.get('path')}, not this engine"))
        elif plugin.get('version') != current:
            rows.append((False, 'Claude Code', f"plugin {plugin.get('version')} != CLI {current}"))
        else:
            rows.append((True, 'Claude Code', f'plugin {current}' + (' (restart Claude Code if it was open)'
                                                                      if plugin.get('errors') else '')))
    if shutil.which('codex'):
        markets = _run_text(['codex', 'plugin', 'marketplace', 'list'])
        plugins = _run_text(['codex', 'plugin', 'list'])
        root = next((line.split(None, 1)[1].strip() for line in (markets or '').splitlines()
                     if line.split()[:1] == ['manuwright'] and len(line.split()) > 1), None)
        # STATUS ("installed, enabled") and SOURCE may contain spaces, so match the version token itself.
        version = next((m.group(1) for line in (plugins or '').splitlines() if line.startswith('manuwright@manuwright')
                        for m in [re.search(r'\s(\d+\.\d+\.\d+)\s', line)] if m), None)
        if markets is None or plugins is None:
            rows.append((None, 'Codex', 'could not query `codex plugin`'))
        elif not root or not version:
            rows.append((False, 'Codex', 'manuwright plugin not installed'))
        elif not _same_path(root, engine):
            rows.append((False, 'Codex', f'marketplace points at {root}, not this engine'))
        elif version != current:
            rows.append((False, 'Codex', f'plugin {version} != CLI {current}'))
        else:
            rows.append((True, 'Codex', f'plugin {current}'))
    if shutil.which('opencode'):
        stale = [s.name for _, s, target in agent_steps(engine, 'opencode', 'update')
                 if not (target / 'SKILL.md').is_file()
                 or (target / 'SKILL.md').read_bytes() != (s / 'SKILL.md').read_bytes()]
        rows.append((not stale, 'opencode', 'skills current' if not stale else 'skills out of date: ' + ', '.join(stale)))
    for agent, label in (('agy', 'Antigravity'), ('muse', 'Muse')):
        if shutil.which(agent):
            rows.append((None, label, 'installed (version not queryable; `manuwright agents update` refreshes it)'))
    return rows


def check(engine, args):
    """manuwright check: one readable report of what an update or setup should have left in place."""
    from manuwright import models
    current, _ = engine_api(engine)
    data = load('config.json', {})
    rows = []
    latest = latest_release()
    if latest is None:
        rows.append((None, 'Version', f'{current} (could not reach GitHub to compare)', None))
    else:
        newer = tuple(map(int, latest.lstrip('v').split('.'))) > tuple(map(int, current.split('.')))
        rows.append((not newer, 'Version', f'{current}' + (f', newer release {latest}' if newer else ' (latest)'),
                     'manuwright update' if newer else None))
    agents_fix = 'manuwright agents update'
    rows += [(ok, label, detail, agents_fix if ok is False else None) for ok, label, detail in adapter_checks(engine, current)]
    main = data.get('main_model')
    if not main:
        rows.append((False, 'Main model', 'not set', 'manuwright setup'))
    elif main in models.AGENTS:
        rows.append((False, 'Main model', f'{main!r} is an agent, not a model id', 'manuwright setup'))
    else:
        rows.append((True, 'Main model', main, None))
    reviewers = data.get('review', {}).get('reviewers', [])
    if 'openrouter' in reviewers:
        has_key = bool(os.environ.get('OPENROUTER_API_KEY') or load('secrets.json', {}).get('openrouter_api_key'))
        rows.append((has_key, 'OpenRouter key', 'saved' if has_key else 'missing (OpenRouter reviewers are skipped)',
                     None if has_key else 'manuwright setup'))
    auto = data.get('auto_update')
    rows.append((bool(auto), 'Auto-update', 'on' + (' (announces releases; install with the printed line)'
                                                    if on_windows() else '') if auto else 'off',
                 None if auto else 'manuwright config set auto-update on'))
    writing_mode = data.get('writing_mode') if data.get('writing_mode') in MODE_HELP else 'academic'
    rows.append((True if writing_mode != 'off' else None, 'Writing mode',
                 writing_mode if writing_mode != 'off' else 'off (manuwright mode academic turns it on)', None))
    try:
        profile = json.loads((home() / 'library' / 'writing' / 'profile' / 'style_profile.json').read_text(encoding='utf-8'))
        docs = profile.get('documents', 0)
        rows.append((True if docs >= 3 else None, 'Learned style', f"{docs} document(s), {profile.get('learned', '')}"
                     + ('' if docs >= 3 else ' (too few to change any check: learn from 3 or more papers)'), None))
    except (OSError, ValueError):
        rows.append((None, 'Learned style', 'none yet (optional: manuwright style learn <your or landmark papers>)', None))
    library = home() / 'library'
    sync_mode = data.get('library_sync') if data.get('library_sync') in ('auto', 'ask', 'off') else 'auto'
    try:
        rules_file = (library / 'writing' / 'terminology.md').read_text(encoding='utf-8')
        learned = sum(1 for line in rules_file.splitlines() if line.startswith('| ') and '|---' not in line
                      and 'Preferred Term' not in line and 'Forbidden Terms' not in line)
    except OSError:
        learned = 0
    try:
        notes = sum(1 for line in (library / 'notes.md').read_text(encoding='utf-8').splitlines() if line.startswith('- '))
    except OSError:
        notes = 0
    rows.append((True if sync_mode != 'off' else None, 'Library sync',
                 f'{sync_mode}: {learned} wording-rule row(s), {notes} note(s), team profile '
                 f"{'yes' if (library / 'profile' / 'authors.md').is_file() else 'no'} ({library})", None))
    stale = stale_papers(engine)
    rows.append((not stale, 'Paper agent rules', 'all registered papers current' if not stale else
                 f'{len(stale)} out of date: ' + ', '.join(str(p) for p in stale),
                 None if not stale else 'manuwright init --refresh-rules --all'))
    marks = {True: '✓', False: '✗', None: '·'}
    for ok, label, detail, fix in rows:
        print(f'{marks[ok]} {label:<18} {detail}' + (f'\n    fix: {fix}' if fix else ''))
    problems = sum(ok is False for ok, *_ in rows)
    print(f'\n{problems} item(s) to fix.' if problems else '\nAll good.')
    return 1 if problems else 0


# --- agent adapters ---------------------------------------------------------

AGENTS = ('claude', 'codex', 'agy', 'opencode', 'muse')


def agent_steps(engine, agent, mode):
    """Native commands (or a copy step) that install/update this engine's adapters for one agent.

    The installed engine folder is itself the plugin/marketplace root, so adapters always
    match the CLI version that installed them. That folder moves when a reinstall picks another
    Python (.../python3.11/site-packages -> .../python3.12/...), so update re-adds the marketplace
    from the current folder: both CLIs re-point an existing `manuwright` marketplace on add.
    """
    root, skills = str(engine), sorted(p for p in (engine / 'skills').iterdir() if (p / 'SKILL.md').is_file())
    if agent == 'claude':
        steps = [['claude', 'plugin', 'marketplace', 'add', root], ['claude', 'plugin', 'install', 'manuwright@manuwright']]
        return steps + ([['claude', 'plugin', 'update', 'manuwright@manuwright']] if mode == 'update' else [])
    if agent == 'codex':
        return [['codex', 'plugin', 'marketplace', 'add', root], ['codex', 'plugin', 'add', 'manuwright@manuwright']]
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
                try:
                    code = subprocess.call(native(step))
                    if code and step[:4] == ['codex', 'plugin', 'marketplace', 'add']:
                        # Codex refuses to re-point a marketplace whose old folder still exists
                        # ("already added from a different source"): remove it, then add again.
                        print(f'[{agent}] codex plugin marketplace remove manuwright (then add again)', flush=True)
                        subprocess.call(native(['codex', 'plugin', 'marketplace', 'remove', 'manuwright']))
                        code = subprocess.call(native(step))
                except OSError as exc:
                    code = f'{type(exc).__name__}: {exc}'
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

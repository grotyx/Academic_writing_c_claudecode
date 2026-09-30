"""Optional, recommended: connect the Obsidian "Academic Paper Citation Manager" plugin (MCP `rag-obsidian`).

manuwright never requires it; without the plugin every command here is a no-op or a hint.

manuwright obsidian status                    vaults with the plugin, and which agents are connected
manuwright obsidian install [--vault PATH] [--enable-mcp] [--yes]   plugin from its GitHub release
manuwright obsidian connect [--vault PATH] [--only a,b] [--dry-run] [--yes]
manuwright evidence import-obsidian <citekey>... [--vault PATH] [--evidence knowledge/evidence.md]

The vault is a discovery library. knowledge/evidence.md stays the only citable registry (Rule 1):
imported entries are marked abstract-only until someone reviews the full text.
"""
from __future__ import annotations
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

PLUGIN_ID = 'academic-paper-citation-manager'
SERVER = 'rag-obsidian'
AGENTS = ('claude', 'codex', 'opencode', 'agy', 'muse')


def obsidian_config():
    if sys.platform == 'darwin':
        return Path.home() / 'Library' / 'Application Support' / 'obsidian' / 'obsidian.json'
    if os.name == 'nt':
        return Path(os.environ.get('APPDATA', '')) / 'obsidian' / 'obsidian.json'
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / 'obsidian' / 'obsidian.json'


def bridge(vault):
    return Path(vault) / '.obsidian' / 'plugins' / PLUGIN_ID / 'mcp-bridge.cjs'


def find_vaults():
    """Vaults known to Obsidian that have the plugin's MCP bridge."""
    try:
        data = json.loads(obsidian_config().read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    return [Path(v['path']) for v in data.get('vaults', {}).values() if bridge(v['path']).is_file()]


def opencode_config():
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / 'opencode' / 'opencode.json'


def muse_config():
    return Path(os.environ.get('XDG_CONFIG_HOME') or Path.home() / '.config') / 'muse' / 'settings.json'


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None


def connected(agent):
    """True/False when known, None when the agent is not installed."""
    exe = agent
    if not shutil.which(exe):
        return None
    if agent in ('opencode', 'muse'):
        data = read_json(opencode_config() if agent == 'opencode' else muse_config()) or {}
        return SERVER in ((data.get('mcp') if agent == 'opencode' else data.get('mcpServers')) or {})
    argv = {'claude': ['claude', 'mcp', 'get', SERVER], 'codex': ['codex', 'mcp', 'get', SERVER],
            'agy': ['agy', 'mcp', 'list']}[agent]
    try:
        done = subprocess.run(argv, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return SERVER in done.stdout if agent == 'agy' else done.returncode == 0


def steps(agent, vault):
    command = ['node', str(bridge(vault)), '--vault', str(vault)]
    if agent == 'claude':
        return [['claude', 'mcp', 'add', '-s', 'user', '--transport', 'stdio', SERVER, '--', *command]]
    if agent == 'codex':
        return [['codex', 'mcp', 'add', SERVER, '--', *command]]
    if agent == 'agy':
        return [['agy', 'mcp', 'add', SERVER, *command]]
    if agent == 'opencode':
        return [('json', opencode_config(), ('mcp', SERVER), {'type': 'local', 'command': command, 'enabled': True})]
    if agent == 'muse':
        return [('json', muse_config(), ('mcpServers', SERVER), {'command': command[0], 'args': command[1:]})]
    raise ValueError(agent)


def write_json_entry(path, keys, value):
    data = read_json(path)
    if data is None and path.exists():
        raise ValueError(f'{path} is not valid JSON; not touching it')
    data = data or {}
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + '.manuwright.bak'))
    data.setdefault(keys[0], {})[keys[1]] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def pick_vault(args):
    if '--vault' in args:
        return Path(args[args.index('--vault') + 1]).expanduser().resolve()
    vaults = find_vaults()
    if len(vaults) == 1:
        return vaults[0]
    if not vaults:
        return None
    for i, v in enumerate(vaults, 1):
        print(f'  {i}. {v}')
    if not sys.stdin.isatty():
        print('Several vaults have the plugin; choose one with --vault.', file=sys.stderr)
        return None
    choice = input('Vault number: ').strip()
    return vaults[int(choice) - 1] if choice.isdigit() and 0 < int(choice) <= len(vaults) else None


def status(args):
    vaults = find_vaults()
    print('Vaults with the plugin:' if vaults else f'No vault with the {PLUGIN_ID} plugin found.')
    for v in vaults:
        print(f'  {v}')
    for agent in AGENTS:
        state = connected(agent)
        print(f'  [{agent}] ' + {None: 'not installed', True: 'connected', False: 'not connected'}[state])
    return 0


def connect(args):
    vault = pick_vault(args)
    if vault is None or not bridge(vault).is_file():
        print(f'No vault with the {PLUGIN_ID} plugin selected. Install the plugin in Obsidian first '
              '(Community plugins) and enable Settings > External AI (MCP).', file=sys.stderr)
        return 1
    chosen = args[args.index('--only') + 1].split(',') if '--only' in args else list(AGENTS)
    dry = '--dry-run' in args
    print(f'Vault: {vault}')
    if not dry and '--yes' not in args and sys.stdin.isatty():
        if input(f'Register MCP server "{SERVER}" for {", ".join(chosen)}? [y/N] ').strip().lower() not in {'y', 'yes'}:
            print('Nothing changed.')
            return 0
    failed = 0
    for agent in chosen:
        state = connected(agent)
        if state is None:
            print(f'[{agent}] not installed; skipped', flush=True)
            continue
        if state:
            print(f'[{agent}] already connected; skipped', flush=True)
            continue
        for step in steps(agent, vault):
            if step[0] == 'json':
                print(f'[{agent}] add {SERVER} to {step[1]} (backup: *.manuwright.bak)', flush=True)
                if not dry:
                    try:
                        write_json_entry(step[1], step[2], step[3])
                    except ValueError as exc:
                        print(f'[{agent}] {exc}', flush=True)
                        failed += 1
                continue
            print(f'[{agent}] ' + ' '.join(step), flush=True)
            if not dry and subprocess.call(step):
                failed += 1
    print('Obsidian must be open with Settings > Academic Paper Citation Manager > External AI (MCP) enabled. '
          'Restart the agents to load the server. Cite only [EVID:id] entries from knowledge/evidence.md; '
          'bring vault references in with `manuwright evidence import-obsidian <citekey>`.')
    return 1 if failed else 0


RELEASE_API = 'https://api.github.com/repos/grotyx/rag-obsidian/releases/latest'
ASSETS = ('main.js', 'manifest.json', 'styles.css')


def all_vaults():
    try:
        data = json.loads(obsidian_config().read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    return [Path(v['path']) for v in data.get('vaults', {}).values() if Path(v['path']).is_dir()]


def obsidian_app_installed():
    if sys.platform == 'darwin':
        return Path('/Applications/Obsidian.app').exists() or (Path.home() / 'Applications' / 'Obsidian.app').exists()
    return obsidian_config().exists() or bool(shutil.which('obsidian'))


def download_release(target):
    """Latest plugin release assets -> target folder. Returns the version."""
    import urllib.request
    with urllib.request.urlopen(RELEASE_API, timeout=30) as response:
        release = json.loads(response.read().decode('utf-8'))
    urls = {a['name']: a['browser_download_url'] for a in release.get('assets', [])}
    missing = [name for name in ASSETS if name not in urls]
    if missing:
        raise ValueError(f'release {release.get("tag_name")} lacks {", ".join(missing)}')
    target.mkdir(parents=True, exist_ok=True)
    for name in ASSETS:
        with urllib.request.urlopen(urls[name], timeout=60) as response:
            (target / name).write_bytes(response.read())
    return release.get('tag_name', '?')


def enable_plugin(vault, enable_mcp):
    listing = Path(vault) / '.obsidian' / 'community-plugins.json'
    enabled = read_json(listing)
    if enabled is None and listing.exists():
        raise ValueError(f'{listing} is not valid JSON; not touching it')
    enabled = enabled or []
    if PLUGIN_ID not in enabled:
        if listing.exists():
            shutil.copy2(listing, listing.with_suffix('.json.manuwright.bak'))
        listing.parent.mkdir(parents=True, exist_ok=True)
        listing.write_text(json.dumps(enabled + [PLUGIN_ID], indent=2) + '\n', encoding='utf-8')
    settings_file = Path(vault) / '.obsidian' / 'plugins' / PLUGIN_ID / 'data.json'
    if enable_mcp:
        data = read_json(settings_file) or {}
        data['mcpEnabled'] = True
        settings_file.write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8')


def ask(question, args):
    if '--yes' in args:
        return True
    if not sys.stdin.isatty():
        return False
    return input(question + ' [y/N] ').strip().lower() in {'y', 'yes'}


def install(args):
    """Install the plugin into a vault from its latest GitHub release (asks first)."""
    if not obsidian_app_installed():
        print('Obsidian is not installed. Get it from https://obsidian.md' +
              (' or run: brew install --cask obsidian' if sys.platform == 'darwin' and shutil.which('brew') else '') +
              '. Open it once, create or open a vault, then run: manuwright obsidian install')
        if sys.platform == 'darwin' and shutil.which('brew') and ask('Install Obsidian with Homebrew now?', [a for a in args if a != '--yes']):
            if subprocess.call(['brew', 'install', '--cask', 'obsidian']):
                return 1
            print('Obsidian installed. Open it, create or open a vault, then run: manuwright obsidian install')
        return 1
    vaults = [Path(args[args.index('--vault') + 1]).expanduser().resolve()] if '--vault' in args else all_vaults()
    if not vaults:
        print('No Obsidian vault found. Open Obsidian, create or open a vault, then run: manuwright obsidian install')
        return 1
    if len(vaults) > 1 and '--vault' not in args:
        for i, v in enumerate(vaults, 1):
            print(f'  {i}. {v}' + ('  (plugin installed)' if bridge(v).is_file() or (v / '.obsidian' / 'plugins' / PLUGIN_ID / 'manifest.json').exists() else ''))
        if not sys.stdin.isatty():
            print('Several vaults found; choose one with --vault.', file=sys.stderr)
            return 1
        choice = input('Install into vault number: ').strip()
        if not (choice.isdigit() and 0 < int(choice) <= len(vaults)):
            print('Nothing changed.')
            return 0
        vaults = [vaults[int(choice) - 1]]
    vault = vaults[0]
    target = vault / '.obsidian' / 'plugins' / PLUGIN_ID
    if (target / 'manifest.json').exists():
        print(f'Plugin already installed in {vault}. Update it inside Obsidian (Community plugins).')
        return 0
    enable_mcp = '--enable-mcp' in args
    if not ask(f'Install "Academic Paper Citation Manager" (latest release, github.com/grotyx/rag-obsidian) into {vault}?', args):
        print('Nothing changed.')
        return 0
    if not enable_mcp and sys.stdin.isatty() and '--yes' not in args:
        enable_mcp = ask('Also turn on its MCP access so agents can use the library? '
                         '(local server; Obsidian must be open)', args)
    try:
        version = download_release(target)
        enable_plugin(vault, enable_mcp)
    except (OSError, ValueError) as exc:
        print(f'Install failed: {exc}', file=sys.stderr)
        return 1
    print(f'Installed plugin {version} into {vault}' + (' with MCP access on.' if enable_mcp else '.'))
    print('Next: restart Obsidian (if it asks about community plugins or restricted mode, allow them), '
          + ('' if enable_mcp else 'turn on Settings > Academic Paper Citation Manager > External AI (MCP), ')
          + 'then run: manuwright obsidian connect')
    return 0


def offer_connect():
    """Called after `manuwright agents install`: ask, never install or connect silently."""
    vaults = find_vaults()
    if not vaults:
        print(f'\nOptional (recommended): the Obsidian plugin "Academic Paper Citation Manager" gives every agent a '
              'searchable reference library (PubMed import, AI summaries, citekeys). Not required; '
              'manuwright works without it. https://github.com/grotyx/rag-obsidian')
        if sys.stdin.isatty() and ask('Install it now?', []):
            install([])
        else:
            print('Install later with: manuwright obsidian install')
        return
    missing = [a for a in AGENTS if connected(a) is False]
    if not missing:
        return
    print(f'\nObsidian "{PLUGIN_ID}" found ({vaults[0]}{" and others" if len(vaults) > 1 else ""}). '
          f'Not yet connected: {", ".join(missing)}.')
    if not sys.stdin.isatty():
        print('Connect later with: manuwright obsidian connect')
        return
    if input('Connect the Obsidian reference library to these agents now? [y/N] ').strip().lower() in {'y', 'yes'}:
        connect(['--only', ','.join(missing), '--yes'] + (['--vault', str(vaults[0])] if len(vaults) == 1 else []))


# --- evidence import --------------------------------------------------------

def frontmatter(text):
    match = re.match(r'^---\n(.*?)\n---\n?(.*)$', text, re.S)
    if not match:
        return None, text
    import_yaml = None
    try:
        import yaml  # optional; plain parser below covers the plugin's CSL fields
        import_yaml = yaml.safe_load(match.group(1))
    except Exception:
        import_yaml = None
    return (import_yaml if isinstance(import_yaml, dict) else simple_yaml(match.group(1))), match.group(2)


def simple_yaml(block):
    """Enough YAML for the plugin's CSL notes: scalars, author list of family/given, issued date-parts."""
    data, authors, current, years = {}, [], None, []
    for line in block.splitlines():
        if re.match(r'^[A-Za-z][\w-]*:', line):
            key, _, value = line.partition(':')
            current = key.strip()
            value = value.strip().strip('"').strip("'")
            if value:
                data[current] = value
        elif current == 'author':
            m = re.match(r'\s*-?\s*(family|given|literal):\s*(.+)', line)
            if m:
                if m.group(1) in ('family', 'literal') or not authors:
                    authors.append({})
                authors[-1][m.group(1)] = m.group(2).strip().strip('"').strip("'")
        elif current == 'issued':
            m = re.search(r'-\s*(\d{4})\b', line)
            if m and not years:
                years.append(m.group(1))
    data['author'] = authors
    if years:
        data['issued'] = {'date-parts': [[int(years[0])]]}
    return data


def csl_citation(fm):
    names = [(a.get('family') or a.get('literal', '')) + (' ' + ''.join(p[0] for p in a.get('given', '').replace('-', ' ').split()) if a.get('given') else '')
             for a in fm.get('author') or [] if isinstance(a, dict)]
    authors = ', '.join(names[:6]) + (', et al' if len(names) > 6 else '')
    year = str(((fm.get('issued') or {}).get('date-parts') or [['']])[0][0])
    parts = f"{authors}. {str(fm.get('title', '')).rstrip('.')}. {fm.get('container-title-short') or fm.get('container-title', '')}. {year}"
    if fm.get('volume'):
        parts += f";{fm['volume']}" + (f"({fm['issue']})" if fm.get('issue') else '') + (f":{fm['page']}" if fm.get('page') else '')
    return parts + '.', year


def summary_sections(body):
    match = re.search(r'^## Summary\s*\n(.*?)(?=^## |\Z)', body, re.S | re.M)
    text = match.group(1) if match else ''
    get = lambda name: (re.search(rf'\*\*{name}[^*]*\*\*\s*\n(.+?)(?=\n\*\*|\Z)', text, re.S) or [None, ''])[1].strip()
    return get('Background'), get('Methods'), get('Results'), get('Conclusions')


def references_folder(vault):
    data = read_json(Path(vault) / '.obsidian' / 'plugins' / PLUGIN_ID / 'data.json') or {}
    return Path(vault) / data.get('referencesFolder', 'References')


def find_note(vault, citekey):
    for note in references_folder(vault).rglob('*.md'):
        head = note.read_text(encoding='utf-8', errors='replace')[:400]
        if re.search(rf'^citekey:\s*["\']?{re.escape(citekey)}["\']?\s*$', head, re.M):
            return note
    return None


def evidence_entry(citekey, note):
    fm, body = frontmatter(note.read_text(encoding='utf-8'))
    fm = fm or {}
    citation, year = csl_citation(fm)
    first = (fm.get('author') or [{}])[0]
    background, methods, results, conclusions = summary_sections(body)
    design = fm.get('design') or 'not recorded in the Obsidian note'
    return f"""### {first.get('family', citekey)} et al., {year}
- **Evidence ID:** {citekey}
- **Citation:** {citation}
- **DOI:** {fm.get('DOI', '')}
- **PMID:** {str(fm.get('PMID', '')).strip('"')}
- **Source Status:** abstract-only
- **Imported from:** Obsidian note `{note.name}` (AI summary; verify before relying on it)

- **Study Design:** {design}
- **Objective:** {background or 'See abstract.'}
- **Population:** See methods summary.
- **Intervention/Method:** {methods or 'See abstract.'}

- **Main Findings:**
  - {results or 'See abstract.'}

- **Key Points:**
  - {conclusions or 'See abstract.'}

- **Limitations:** Summary generated in Obsidian; full text not reviewed in manuwright.
- **Relevance:** Imported for this manuscript; state the citation purpose in drafts/draft_plan.md.

---
"""


def import_evidence(args):
    keys = [a for a in args if not a.startswith('--') and a not in {
        args[i + 1] for i, x in enumerate(args[:-1]) if x in ('--vault', '--evidence')}]
    vault = pick_vault(args)
    evidence = Path(args[args.index('--evidence') + 1] if '--evidence' in args else 'knowledge/evidence.md')
    if not keys or vault is None:
        print('usage: manuwright evidence import-obsidian <citekey>... [--vault PATH] [--evidence FILE]', file=sys.stderr)
        return 2
    existing = evidence.read_text(encoding='utf-8') if evidence.exists() else '# Evidence\n'
    added, missing = [], []
    for key in keys:
        if re.search(rf'\*\*Evidence ID:\*\*\s*{re.escape(key)}\s*$', existing, re.M):
            print(f'{key}: already in {evidence}; skipped')
            continue
        note = find_note(vault, key)
        if note is None:
            missing.append(key)
            continue
        existing = existing.rstrip('\n') + '\n\n' + evidence_entry(key, note)
        added.append(key)
    if added:
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text(existing, encoding='utf-8')
    print(f'added {len(added)} to {evidence}: {", ".join(added) or "-"}' + (f'; not found: {", ".join(missing)}' if missing else ''))
    if added:
        print(f'Cite them as [EVID:{added[0]}]. Check each summary against the paper before citing.')
    return 1 if missing else 0

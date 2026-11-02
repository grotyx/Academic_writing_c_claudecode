#!/usr/bin/env python3
"""The author's journal list (library/journals/list.md), built on this computer.

    journal list                                   print the list
    journal list --build                           rebuild with the saved settings, or detect the field
    journal list --build --auto                    detect the field from your papers' references and target journals
    journal list --build --preset ortho-neuro      a ready field (ortho-neuro, ortho, neurosurgery)
    journal list --build --category "SURGERY:neurosurg,spine" --category ORTHOPEDICS
                     [--exclude dental,maxillofacial] [--group "Spine=spine,spinal"] [--top 50]
    journal list --categories [word]               the JCR categories, with how many journals each has
    journal list --add "World Neurosurg" [--group Neurosurgery] | --remove "Cureus"
    journal list --import FILE

A rule is a JCR category, optionally followed by title words (`CATEGORY:word,word`): only journals whose
title contains one of the words are kept, which narrows broad categories such as SURGERY. The build
fetches one public SCIE ranking table (newest year) and NLM abbreviations from the NLM Catalog; the data
stays on this computer and is never shipped with ManuWright. The settings are saved in the list, so the
next `--build` (a new ranking year) repeats them.
"""
from __future__ import annotations

import difflib
import hashlib
import html
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import search_pubmed as pubmed  # noqa: E402

JCR_SITE = 'https://compbio.sookmyung.ac.kr/~journal/'
LIST_HEADER = '| Group | Journal (NLM) | Full title | Category | Category %rank | IF |'
NEURO_WORDS = 'neurosurg,spine,spinal,stereotact,neuro-oncol,neurointerv,neurotrauma,neurospine,neuromodul'
PRESETS = {
    'ortho-neuro': {'rules': ['ORTHOPEDICS', f'CLINICAL NEUROLOGY:{NEURO_WORDS}', f'SURGERY:{NEURO_WORDS}',
                              f'NEUROSCIENCES:{NEURO_WORDS}'],
                    'groups': ['Spine=spine,spinal', f'Neurosurgery={NEURO_WORDS}']},
    'ortho': {'rules': ['ORTHOPEDICS'], 'groups': ['Spine=spine,spinal']},
    'neurosurgery': {'rules': [f'CLINICAL NEUROLOGY:{NEURO_WORDS}', f'SURGERY:{NEURO_WORDS}',
                               f'NEUROSCIENCES:{NEURO_WORDS}'],
                     'groups': ['Spine=spine,spinal', f'Neurosurgery={NEURO_WORDS}']},
}
BROAD = 150  # a category with more journals than this is narrowed by title words when detected
GENERIC = set('''journal journals of the and in for on international american european british annals archives
clinical research reviews review advances current frontiers medicine medical science sciences society official
letters reports open world global asian surgery surgical'''.split())


# --- the list file -------------------------------------------------------------

def norm(text: str) -> str:
    return re.sub(r'[^a-z0-9]', '', text.lower())


def library_journals() -> Path:
    import library_sync
    return library_sync.library() / 'journals'


def list_path() -> Path:
    return library_journals() / 'list.md'


def my_list() -> dict:
    """{normalised NLM abbreviation: row} from the author's journal list."""
    path = list_path()
    if not path.is_file():
        return {}
    rows = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if (line.lstrip().startswith('|') and len(cells) >= 5 and cells[1] and not set(cells[1]) <= set('-: ')
                and cells[1] != 'Journal (NLM)'):
            rows[norm(cells[1])] = {'group': cells[0], 'journal': cells[1], 'title': cells[2],
                                    'category': cells[3], 'rank': cells[4]}
    return rows


def rank_of(row: dict) -> float:
    try:
        return float(row['rank'])
    except (TypeError, ValueError):
        return 100.0


def list_note(entry: dict | None) -> str:
    if not entry:
        return ''
    if rank_of(entry) < 100:
        return f"{entry['group']}: top {entry['rank']}% {entry['category'].title()}"
    return f"{entry['group']} (your list)"


def saved_settings() -> dict:
    path = list_path()
    if path.is_file():
        found = re.search(r'^- settings: (\{.*\})\s*$', path.read_text(encoding='utf-8'), re.M)
        if found:
            try:
                return json.loads(found.group(1))
            except ValueError:
                pass
    return {}


def save_list(text: str) -> Path:
    path = list_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.read_text(encoding='utf-8') != text:
        path.with_name('list.md.bak').write_bytes(path.read_bytes())
    path.write_text(text, encoding='utf-8')
    return path


# --- PubMed / NLM ----------------------------------------------------------------

def patient(call):
    """Retry a PubMed call that NCBI rate-limited (HTTP 429), waiting longer each time."""
    def wrapped(*args, **kwargs):
        for wait in (1, 2, 4, 8, None):
            try:
                return call(*args, **kwargs)
            except urllib.error.HTTPError as exc:
                if exc.code != 429 or wait is None:
                    raise
                time.sleep(wait)
    return wrapped


def summaries(ids: list[str]) -> list[dict]:
    out = []
    for i in range(0, len(ids), 100):
        params = urllib.parse.urlencode({'db': 'pubmed', 'id': ','.join(ids[i:i + 100]), 'retmode': 'json'})
        result = patient(pubmed._fetch_json)(f'{pubmed.BASE_URL}/esummary.fcgi?{params}').get('result', {})
        out += [result[u] for u in result.get('uids', []) if u in result]
        time.sleep(pubmed.RATE_LIMIT_DELAY)
    return out


def journal_issns(ta: str) -> dict:
    """One PubMed record of a journal (by NLM abbreviation): {'source', 'issn', 'essn'} or {}."""
    ids, _ = patient(pubmed.search_pubmed)(f'"{ta}"[ta]', 1)
    time.sleep(pubmed.RATE_LIMIT_DELAY)
    return (summaries(ids) or [{}])[0] if ids else {}


def resolve_ta(row: dict, cache: dict) -> str:
    """NLM title abbreviation from the ISSNs (NLM Catalog), cached; the record whose title matches best."""
    for issn in (row['issn'], row['eissn']):
        if issn and issn in cache:
            return cache[issn]
    best = ('', 0.0)
    for issn in [i for i in (row['issn'], row['eissn']) if i]:
        query = urllib.parse.urlencode({'db': 'nlmcatalog', 'term': f'{issn}[issn]', 'retmode': 'json'})
        ids = patient(pubmed._fetch_json)(f'{pubmed.BASE_URL}/esearch.fcgi?{query}')['esearchresult']['idlist'][:5]
        time.sleep(pubmed.RATE_LIMIT_DELAY)
        if ids:
            query = urllib.parse.urlencode({'db': 'nlmcatalog', 'id': ','.join(ids), 'retmode': 'json'})
            result = patient(pubmed._fetch_json)(f'{pubmed.BASE_URL}/esummary.fcgi?{query}')['result']
            time.sleep(pubmed.RATE_LIMIT_DELAY)
            for uid in ids:
                record = result.get(uid, {})
                full = ' '.join(t.get('title', '') for t in record.get('titlemainlist', []))
                score = difflib.SequenceMatcher(None, row['title'].lower(), full.lower()).ratio()
                if record.get('medlineta') and score > best[1]:
                    best = (record['medlineta'], score)
        if best[0]:
            break
    for issn in (row['issn'], row['eissn']):
        if issn and best[0]:
            cache[issn] = best[0]
    return best[0]


# --- the ranking table -------------------------------------------------------------

def site_rows(page: str) -> list[dict]:
    """Journals from the ranking table: title, ISSNs, IF and {category: %rank} (top category first)."""
    rows = []
    for line in page.splitlines():
        if not re.match(r'\s*(?:<tr>)?\s*<td>\d+</td>', line):
            continue
        cells = [' '.join(html.unescape(re.sub(r'<[^>]+>', ' ', re.sub(r'<br\s*/?>', ' ; ', c))).split())
                 for c in re.findall(r'<td[^>]*>(.*?)</td>', line)]
        if len(cells) < 8:
            continue
        cats = {cells[5]: cells[6]}
        for m in re.finditer(r'([A-Z][A-Z ,&\-()/]+?)\s*:\s*([\d.]+)', cells[7]):
            cats[m.group(1).strip(' ;')] = m.group(2)
        rows.append({'title': cells[1], 'issn': cells[2], 'eissn': cells[3], 'if': cells[4], 'cats': cats})
    return rows


def fetch_site(source: str) -> str:
    """The whole ranking table for the newest year (filtered here, so one download serves every field).
    Kept for a day in the library, so --categories and a rebuild do not download it again."""
    tag = hashlib.sha256(source.encode()).hexdigest()[:8]
    cache = library_journals() / f'ranking_cache_{tag}.html'  # one per ranking page
    if cache.is_file() and time.time() - cache.stat().st_mtime < 86400:
        return cache.read_text(encoding='utf-8')
    agent = {'User-Agent': 'Mozilla/5.0 (ManuWright journal list; one download per build)'}
    with urllib.request.urlopen(urllib.request.Request(source, headers=agent), timeout=60) as response:
        form = response.read().decode('utf-8', errors='replace')
    action = (re.search(r'<form[^>]+action="([^"]+)"', form) or [None, urllib.parse.urljoin(source, 'getJournalResult.php')])[1]
    years = re.findall(r'name="(year(\d{4}))"\s+value="(\d+)"', form)
    fields = {'check_submit': '1', 'title': '', 'i_f': '', 'rank': '100'}
    if years:
        name, _, value = max(years, key=lambda y: y[1])
        fields[name] = value
    request = urllib.request.Request(action, data=urllib.parse.urlencode(fields).encode(), headers=agent)
    with urllib.request.urlopen(request, timeout=180) as response:
        page = response.read().decode('utf-8', errors='replace')
    if site_rows(page[:200000]):
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(page, encoding='utf-8')
    return page


def categories(rows: list[dict]) -> Counter:
    return Counter(c for r in rows for c in r['cats'])


# --- rules ---------------------------------------------------------------------------

def parse_rule(spec: str) -> tuple[str, list[str]]:
    category, _, words = spec.partition(':')
    return category.strip().upper(), [w.strip().lower() for w in words.split(',') if w.strip()]


def parse_group(spec: str) -> tuple[str, list[str]]:
    name, _, words = spec.partition('=')
    return name.strip(), [w.strip().lower() for w in words.split(',') if w.strip()]


def select(rows: list[dict], settings: dict) -> list[dict]:
    rules = [parse_rule(r) for r in settings['rules']]
    groups = [parse_group(g) for g in settings.get('groups', [])]
    exclude = [w.lower() for w in settings.get('exclude', [])]
    top = float(settings.get('top', 50))
    picked = []
    for row in rows:
        title = row['title'].lower()
        if any(w in title for w in exclude):
            continue
        for category, words in rules:
            try:
                rank = float(row['cats'][category])
            except (KeyError, ValueError):
                continue
            if rank > top or (words and not any(w in title for w in words)):
                continue
            group = next((name for name, kws in groups if any(w in title for w in kws)), category.title())
            picked.append({**row, 'group': group, 'category': category, 'rank': rank})
            break
    return picked


def paper_folders(root: Path | None) -> list[Path]:
    import academic_style
    folders = [root] if root else []
    try:
        known = json.loads((academic_style.home() / 'projects.json').read_text(encoding='utf-8'))
        folders += [Path(p).parent for p in known if isinstance(p, str)]
    except (OSError, ValueError):
        pass
    return [f for f in dict.fromkeys(folders) if f and f.is_dir()]


def your_journals(root: Path | None, target_ta: dict) -> Counter:
    """{(issn, essn): weight}: the journals of your references (evidence.md PMIDs) and target journals."""
    weights: Counter = Counter()
    pmids, targets = [], []
    for folder in paper_folders(root):
        try:
            text = (folder / 'knowledge' / 'evidence.md').read_text(encoding='utf-8')
            text = re.sub(r'<!--.*?-->', '', text, flags=re.S)  # the starter's example entry is a comment
            pmids += re.findall(r'\*\*PMID:\*\*\s*(\d+)', text)
        except OSError:
            pass
        try:
            key = json.loads((folder / 'project.json').read_text(encoding='utf-8')).get('journal', '')
            if target_ta.get(key):
                targets.append(target_ta[key])
        except (OSError, ValueError):
            pass
    for record in summaries(list(dict.fromkeys(pmids))[:400]):
        weights[(record.get('issn', ''), record.get('essn', ''))] += 1
    for ta in dict.fromkeys(targets):
        record = journal_issns(ta)
        if record:
            weights[(record.get('issn', ''), record.get('essn', ''))] += 5  # a journal you submit to counts more
    return weights


def detect(rows: list[dict], weights: Counter) -> tuple[list[str], list[str]]:
    """(rules, what was found) from your journals: their main categories; broad ones narrowed to the
    title words your journals share."""
    by_issn = {}
    for row in rows:
        for issn in (row['issn'], row['eissn']):
            if issn:
                by_issn[issn] = row
    matched: list[tuple[dict, int]] = []
    for (issn, essn), weight in weights.items():
        row = by_issn.get(issn) or by_issn.get(essn)
        if row:
            matched.append((row, weight))
    if not matched:
        return [], []
    score: Counter = Counter()
    for row, weight in matched:
        for category in row['cats']:
            score[category] += weight
    total = sum(w for _, w in matched)
    chosen = [c for c, s in score.most_common(4) if s >= 0.2 * total] or [score.most_common(1)[0][0]]
    size = categories(rows)
    rules, notes = [], [f'{len(matched)} of your journals found in the ranking table']
    for category in chosen:
        if size[category] <= BROAD:
            rules.append(category)
            notes.append(f'{category.title()} ({size[category]} journals)')
            continue
        words = Counter(w for row, weight in matched if category in row['cats']
                        for w in set(re.findall(r'[a-z][a-z-]{3,}', row['title'].lower())) - GENERIC
                        for _ in range(weight))
        keep = [w for w, _ in words.most_common(6)]
        if keep:
            rules.append(f"{category}:{','.join(keep)}")
            notes.append(f"{category.title()} narrowed to titles with {', '.join(keep)}")
    return rules, notes


# --- building ------------------------------------------------------------------------

SMALL = {'And', 'Of', 'The', 'In', 'For', 'On'}


def nice(title: str) -> str:
    words = title.title().split(' ')
    return ' '.join(w.lower() if i and w in SMALL else w for i, w in enumerate(words))


def list_text(picked: list[dict], settings: dict, label: str) -> str:
    lines = [f"# My journal list: {label}, top {float(settings.get('top', 50)):g}% of their category", '',
             f"- source: {settings.get('source', JCR_SITE)} (SCIE ranking search, newest year)",
             f'- built: {datetime.now().date().isoformat()}; Category %rank = position in that category '
             '(lower is better; 10 = top 10%)',
             '- kept on this computer only (personal reference); edit freely: add, delete or regroup rows',
             f"- settings: {json.dumps({**settings, 'label': label}, ensure_ascii=False)}", '', LIST_HEADER, '|---|---|---|---|---|---|']
    order = [parse_group(g)[0] for g in settings.get('groups', [])]
    for row in sorted(picked, key=lambda r: (order.index(r['group']) if r['group'] in order else len(order),
                                              r['group'], r['rank'])):
        lines.append(f"| {row['group']} | {row['ta']} | {nice(row['title'])} | {row['category'].title()} | "
                     f"{row['rank']:g} | {row['if']} |")
    return '\n'.join(lines) + '\n'


def build(settings: dict, page: str | None = None, root: Path | None = None, target_ta: dict | None = None,
          weights: Counter | None = None) -> tuple[int, str]:
    """Build and save the list from settings ({'rules', 'groups', 'exclude', 'top', 'source'}, or
    {'auto': True}); (journals saved, message)."""
    settings = dict(settings)
    settings.setdefault('source', JCR_SITE)
    settings.setdefault('top', 50)
    if page is None:
        page = fetch_site(settings['source'])
    rows = site_rows(page)
    if not rows:
        return 0, 'the ranking page had no journal table (the site may have changed); nothing saved'
    label = settings.pop('label', '')
    if settings.pop('auto', False):
        rules, notes = detect(rows, weights if weights is not None else your_journals(root, target_ta or {}))
        if not rules:
            return 0, ('could not tell your field: no references with a PMID or target journal found in your papers. '
                       'Choose one: --preset ortho-neuro|ortho|neurosurgery, or --category "<JCR category>" '
                       '(`manuwright journal list --categories` lists them)')
        settings['rules'] = rules + settings.get('rules', [])
        print('Field detected from your papers: ' + '; '.join(notes), flush=True)
        label = label or 'detected from your papers'
    if not settings.get('rules'):
        return 0, 'no categories chosen; nothing saved'
    known = categories(rows)
    ready = set(PRESETS.get(label, {}).get('rules', []))  # a preset may name a category a table lacks
    unknown = [r for r in settings['rules'] if r not in ready and parse_rule(r)[0] not in known]
    if unknown:
        close = [sorted((k for k in known if re.search(r'\b' + re.escape(parse_rule(r)[0]) + r'\b', k)), key=len)[:1]
                 or difflib.get_close_matches(parse_rule(r)[0], list(known), n=1) for r in unknown]
        hint = '; '.join(f'{u} (did you mean {c[0]}?)' if c else u for u, c in zip(unknown, close))
        return 0, f'not a category in the ranking table: {hint}. `manuwright journal list --categories` lists them'
    picked = select(rows, settings)
    if not picked:
        return 0, 'no journal matched these rules; nothing saved'
    cache_path = library_journals() / 'nlm_cache.json'
    try:
        cache = json.loads(cache_path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        cache = {}
    print(f'{len(picked)} journals selected; looking up their NLM abbreviations (cached after the first run)...',
          flush=True)
    for row in picked:
        try:
            row['ta'] = resolve_ta(row, cache)
        except (OSError, ValueError, KeyError):
            row['ta'] = ''
        row['ta'] = row['ta'] or nice(row['title'])
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text(json.dumps(cache, indent=1, ensure_ascii=False), encoding='utf-8')
    label = label or ', '.join(parse_rule(r)[0].title() for r in settings['rules'])
    path = save_list(list_text(picked, settings, label))
    return len(picked), f'saved {len(picked)} journals to {path} (kept on this computer)'


def settings_from(args) -> dict:
    """Build settings from the command line; none given: the saved ones, else detection."""
    rules = list(args.category)
    groups = list(args.group)
    label = ''
    if args.preset:
        if args.preset not in PRESETS:
            raise ValueError(f'unknown preset {args.preset!r}; use one of {", ".join(PRESETS)}')
        rules = PRESETS[args.preset]['rules'] + rules
        groups = groups or PRESETS[args.preset]['groups']
        label = args.preset
    exclude = [w.strip() for w in args.exclude.split(',') if w.strip()] if args.exclude else []
    settings = {'rules': rules, 'groups': groups, 'exclude': exclude, 'top': args.top, 'source': args.source}
    if args.auto or not (rules or args.preset):
        saved = saved_settings()
        if saved.get('rules') and not args.auto:  # the saved field, with any option given now
            changes = {'groups': groups} if groups else {}
            changes.update({'exclude': exclude} if args.exclude else {})
            changes.update({'top': args.top} if args.top_given else {})
            return {**saved, **changes, 'source': args.source}
        settings['auto'] = True
    if label:
        settings['label'] = label
    return settings


def add_row(journal: str, group: str) -> str:
    record = journal_issns(journal)
    if not record:
        return f'"{journal}" is not a PubMed journal abbreviation (or PubMed is offline); use the NLM abbreviation'
    rows = my_list()
    ta = record.get('source') or journal
    if norm(ta) in rows:
        return f'{ta} is already in your list'
    path = list_path()
    text = path.read_text(encoding='utf-8') if path.is_file() else ('# My journal list\n\n' + LIST_HEADER
                                                                     + '\n|---|---|---|---|---|---|\n')
    line = f"| {group} | {ta} | {record.get('fulljournalname', ta)} | - | - | - |"
    save_list(text.rstrip('\n') + '\n' + line + '\n')
    return f'added {ta} to {path}'


def remove_row(journal: str) -> str:
    path = list_path()
    if not path.is_file():
        return 'no journal list yet'
    key = norm(journal)
    lines = path.read_text(encoding='utf-8').splitlines()
    kept = [l for l in lines if not (l.lstrip().startswith('|') and len(l.split('|')) > 3
                                     and key in (norm(l.split('|')[2]), norm(l.split('|')[3])))]
    if len(kept) == len(lines):
        return f'{journal} is not in your list'
    save_list('\n'.join(kept) + '\n')
    return f'removed {journal} from {path}'


def cmd_list(args, root: Path | None = None, target_ta: dict | None = None) -> int:
    path = list_path()
    try:
        if getattr(args, 'categories', None) is not None:
            page = Path(args.from_html).read_text(encoding='utf-8', errors='replace') if args.from_html else fetch_site(args.source)
            counts = categories(site_rows(page))
            word = args.categories.lower()
            for name, n in sorted(counts.items()):
                if word in name.lower():
                    print(f'{n:5}  {name}')
            print('\nUse a name with --category, optionally narrowed by title words: '
                  '--category "SURGERY:neurosurg,spine"')
            return 0
        if args.build:
            page = Path(args.from_html).read_text(encoding='utf-8', errors='replace') if args.from_html else None
            count, message = build(settings_from(args), page, root, target_ta)
            print(message, file=sys.stdout if count else sys.stderr)
            return 0 if count else 1
        if args.add:
            print(add_row(args.add, args.group[0] if args.group else 'Added'))
            return 0
        if args.remove:
            print(remove_row(args.remove))
            return 0
        if args.import_file:
            text = Path(args.import_file).read_text(encoding='utf-8')
            if LIST_HEADER not in text:
                print(f'journal list: {args.import_file} is not a journal list (needs the table header {LIST_HEADER}).',
                      file=sys.stderr)
                return 2
            save_list(text)
            print(f'saved {len(my_list())} journals to {path} (kept on this computer)')
            return 0
    except ValueError as exc:
        print(f'journal list: {exc}', file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f'journal list: no such file: {exc.filename}', file=sys.stderr)
        return 2
    except OSError as exc:
        print(f'journal list: could not reach the ranking site or PubMed ({exc}). Save the ranking result page from '
              'a browser and pass it with --from-html, or import a list with --import.', file=sys.stderr)
        return 1
    rows = my_list()
    if not rows:
        print(f'No journal list yet ({path}). Build one: manuwright journal list --build (detects your field from '
              'your papers), or --preset ortho-neuro|ortho|neurosurgery, or --category "<JCR category>".')
        return 0
    for row in sorted(rows.values(), key=lambda r: (r['group'], rank_of(r))):
        place = f"top {row['rank']:>5}%" if rank_of(row) < 100 else '      -    '
        print(f"{row['group']:<16} {row['journal']:<34} {place} {row['category'].title()}")
    settings = saved_settings()
    print(f'\n{len(rows)} journals in {path}' + (f"; settings: {', '.join(settings.get('rules', []))}" if settings else ''))
    return 0


def add_arguments(parser) -> None:
    parser.add_argument('--import', dest='import_file', help='save this list file to your library')
    parser.add_argument('--build', action='store_true', help='build the list from the SCIE ranking table')
    parser.add_argument('--auto', action='store_true', help="detect the field from your papers' references")
    parser.add_argument('--preset', help=f"a ready field: {', '.join(PRESETS)}")
    parser.add_argument('--category', action='append', default=[],
                        help='a JCR category, optionally with title words: "SURGERY:neurosurg,spine" (repeatable)')
    parser.add_argument('--exclude', help='title words to leave out, comma-separated (e.g. dental,veterinary)')
    parser.add_argument('--group', action='append', default=[],
                        help='"Name=word,word": group journals whose title has a word (repeatable); with --add, the group')
    parser.add_argument('--top', type=float, default=None, help='category percentile limit (default 50)')
    parser.add_argument('--categories', nargs='?', const='', default=None,
                        help='list the JCR categories (optionally only those containing a word)')
    parser.add_argument('--add', help='add one journal by its NLM abbreviation')
    parser.add_argument('--remove', help='remove one journal')
    parser.add_argument('--source', default=JCR_SITE, help='ranking search page')
    parser.add_argument('--from-html', help='a saved ranking result page instead of downloading it')


def finish_arguments(args) -> None:
    args.top_given = args.top is not None
    if args.top is None:
        args.top = 50.0

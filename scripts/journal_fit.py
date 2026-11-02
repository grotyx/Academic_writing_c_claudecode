#!/usr/bin/env python3
"""Journal fit review and journal suggestions (advisory, docs/critical_review_protocol.md section 6).

    journal_fit.py profile <journal> [--url URL] [--from FILE]   journal profile: aims & scope, limits
    journal_fit.py fit [<journal>] [--query Q] [--years 5] [--reviewers ...] [--no-review]
    journal_fit.py suggest [--query Q] [--years 5] [--top 10] [--mine] [--review] [--reviewers ...]
    journal_fit.py list [--build [--auto|--preset P|--category C[:words]] | --categories | --add J | --import F]

`fit` checks one journal: what it published on this topic in PubMed (counts, recent titles), the
manuscript against the limits in its profile (abstract and main-text words, references, tables and
figures), then the chosen reviewers judge scope fit as that journal's editor (role `journal`).
`suggest` ranks the journals that published the most papers on this topic, marks the ones in the
author's own list (profile/journals.md), and with --review asks the reviewers to rank the fit.

Only the search query goes to PubMed. The manuscript goes only to the reviewers the author chose,
as in critical review. Journal policies come from the profile the author keeps (the official
pages), never from guesses; impact factors are not used.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import search_pubmed as pubmed  # noqa: E402
import journal_list  # noqa: E402
from journal_list import (PRESETS, library_journals, list_note, list_path, my_list, norm,  # noqa: E402,F401
                          patient, summaries)

# Reference-style keys from `manuwright target` -> NLM title abbreviation (PubMed [ta]).
STYLE_TA = {
    'nejm': 'N Engl J Med', 'lancet': 'Lancet', 'spine': 'Spine (Phila Pa 1976)', 'spine-j': 'Spine J',
    'bjj': 'Bone Joint J', 'jbjs': 'J Bone Joint Surg Am', 'neurospine': 'Neurospine',
    'jns-spine': 'J Neurosurg Spine', 'gsj': 'Global Spine J', 'corr': 'Clin Orthop Relat Res',
    'asj': 'Asian Spine J', 'esj': 'Eur Spine J',
}
SECTIONS = ['01_title.md', '02_abstract.md', '03_introduction.md', '04_methods.md', '05_results.md',
            '06_discussion.md', '07_conclusion.md', '09_figure_legends.md']
BODY = ['03_introduction.md', '04_methods.md', '05_results.md', '06_discussion.md', '07_conclusion.md']
LIMITS = ('abstract_words', 'main_text_words', 'references', 'tables_figures')
STOP = set('''a an and are as at be between by for from in into is of on or the to with without versus vs
after before during among patients patient study analysis comparison compared comparing effect effects
outcome outcomes results using use based retrospective prospective cohort clinical new novel role
evaluation assessment association associated single center centre multicenter case series'''.split())
WORD_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9'\-]*")
EVID_RE = re.compile(r"\[EVID:([A-Za-z0-9_.-]+)\]")


# --- paper and profiles ------------------------------------------------------

def paper_root(start: Path) -> Path | None:
    start = start.resolve()
    return next((p for p in [start, *start.parents] if (p / 'project.json').is_file()), None)


def slug(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'journal'


def aliases() -> dict:
    try:
        return json.loads((library_journals() / 'aliases.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def remember_alias(typed: str, ta: str) -> None:
    """"The Spine Journal" -> spine-j: `journal profile` names the file after the NLM abbreviation; fit
    finds it again from the name as typed, offline too."""
    if slug(typed) == slug(ta):
        return
    known = aliases()
    known[slug(typed)] = slug(ta)
    library_journals().mkdir(parents=True, exist_ok=True)
    (library_journals() / 'aliases.json').write_text(json.dumps(known, indent=1, ensure_ascii=False), encoding='utf-8')


def profile_path(journal: str, root: Path | None) -> Path:
    """The paper's own profile (profile/journals/<slug>.md) if present, else the library's."""
    names = list(dict.fromkeys([slug(journal), aliases().get(slug(journal), slug(journal))]))
    for folder in ([root / 'profile' / 'journals'] if root else []) + [library_journals()]:  # the paper's first
        for name in names:
            if (folder / f'{name}.md').is_file():
                return folder / f'{name}.md'
    return library_journals() / f'{aliases().get(slug(journal), slug(journal))}.md'


def read_profile(path: Path) -> dict:
    """{'text', 'limits': {key: int}, 'verified': bool, 'source'} from a profile file ({} if missing)."""
    if not path.is_file():
        return {}
    text = path.read_text(encoding='utf-8')
    limits = {k: int(v) for k, v in re.findall(r'^- (' + '|'.join(LIMITS) + r'):\s*(\d+)\s*$', text, re.M)}
    verified = bool(re.search(r'^- verified_by_author:\s*yes\b', text, re.M | re.I))
    source = (re.search(r'^- source:\s*(\S+)', text, re.M) or [None, ''])[1]
    # The raw page text is for the author to trim; reviewers get the curated part only.
    curated = text.split('\n## Fetched page text', 1)[0].strip()
    return {'text': curated, 'limits': limits, 'verified': verified, 'source': source}


PROFILE_TEMPLATE = """# Journal profile: {name}

- name: {name}
- nlm_abbreviation: {ta}
- source: {source}
- checked: {date}
- verified_by_author: no

Fill the sections below from the journal's official pages (Aims and Scope, Guide for Authors), then set
verified_by_author: yes. Reviewers use only what is written here for the journal's policies.

## Aims and scope


## Article types


## Limits
- abstract_words:
- main_text_words:
- references:
- tables_figures:
- structured_abstract:

## Required
- reporting guideline:
- other:
"""


def page_text(url: str) -> str:
    """Readable text of a web page ('' when it cannot be fetched; many publishers block scripts)."""
    request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (ManuWright journal profile)'})
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            raw = response.read(3_000_000).decode('utf-8', errors='replace')
    except (OSError, ValueError):
        return ''
    raw = re.sub(r'(?is)<(script|style|noscript|svg|nav|footer|header)\b.*?</\1>', ' ', raw)
    raw = re.sub(r'(?i)<br\s*/?>|</(p|div|li|h[1-6]|tr)>', '\n', raw)
    text = html.unescape(re.sub(r'<[^>]+>', ' ', raw))
    lines = [re.sub(r'[ \t\xa0]+', ' ', line).strip() for line in text.splitlines()]
    return '\n'.join(line for line in lines if len(line) > 2)[:15000]


def nlm_abbreviation(journal: str, search=None) -> tuple[str, str]:
    """(NLM title abbreviation, full title) as PubMed knows the journal; ('', '') when not found/offline."""
    search = search or patient(pubmed.search_pubmed)
    try:
        for term in (f'"{journal}"[ta]', f'"{journal}"[jour]'):
            ids, _ = search(term, 1)
            articles = pubmed.fetch_articles(ids) if ids else []
            if articles:
                article = articles[0]
                return article.get('medline_ta') or article.get('journal_abbr') or journal, article.get('journal', '')
    except (OSError, ValueError):
        pass
    return '', ''


def cmd_profile(args) -> int:
    root = paper_root(Path.cwd())
    ta, full = nlm_abbreviation(args.journal)
    name = full or args.journal
    if ta:
        remember_alias(args.journal, ta)
    path = profile_path(ta or args.journal, root)
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(PROFILE_TEMPLATE.format(name=name, ta=ta or args.journal, source=args.url or '',
                                                date=datetime.now().date().isoformat()), encoding='utf-8')
        print(f'created {path}')
    else:
        print(f'kept {path} (already there)')
    fetched = ''
    if args.from_file:
        fetched = Path(args.from_file).read_text(encoding='utf-8', errors='replace')
    elif args.url:
        fetched = page_text(args.url)
        if not fetched:
            print(f'Could not read {args.url} (the publisher may block automated reads). Open the page, copy '
                  'the Aims and Scope and the author limits into the profile, or ask your agent to read it.')
    if fetched:
        text = path.read_text(encoding='utf-8').split('\n## Fetched page text', 1)[0].rstrip()
        stamp = datetime.now().date().isoformat()
        path.write_text(f'{text}\n\n## Fetched page text ({args.url or args.from_file}, {stamp}; unverified, '
                        f'move what matters into the sections above)\n\n{fetched}\n', encoding='utf-8')
        print(f'added the page text ({len(fetched)} characters) under "Fetched page text"')
    if not ta:
        print(f'note: PubMed does not know "{args.journal}" as a journal abbreviation (or is offline); use the NLM '
              'abbreviation, e.g. "Spine J", "Eur Spine J".')
    print('Next: fill Aims and scope, Article types, Limits and Required from the official pages, then set '
          'verified_by_author: yes.')
    return 0


# --- manuscript ----------------------------------------------------------------

def plain(text: str) -> str:
    text = re.sub(r'(?m)^\s*#+.*$', ' ', text)
    text = re.sub(r'(?m)^\s*>.*$', ' ', text)
    return re.sub(r'[*_`|]', ' ', text)


def words(text: str) -> int:
    return len(WORD_RE.findall(plain(EVID_RE.sub(' ', text))))


def declared(root: Path) -> dict:
    """{'02_abstract': path, ..., 'tables': [paths]} from project.json (artifacts, abstract, tables), so a
    paper with sections in drafts/paper1_x/ or a revision folder is measured, not read as empty."""
    try:
        data = json.loads((root / 'project.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        data = {}
    data = data if isinstance(data, dict) else {}
    found: dict = {}
    if isinstance(data.get('abstract'), str) and data['abstract']:
        found['02_abstract'] = root / data['abstract']  # the abstract by its role, whatever the file is called
    for item in list(data.get('artifacts') or []):
        if isinstance(item, str) and item:
            stem = re.sub(r'_REV\d+$', '', Path(item).stem, flags=re.I)
            found.setdefault(stem, root / item)
    found['tables'] = [root / t for t in data.get('tables') or [] if isinstance(t, str)]
    return found


def section_path(root: Path, name: str) -> Path:
    return declared(root).get(Path(name).stem) or root / 'drafts' / name


def read(root: Path, name: str) -> str:
    path = section_path(root, name)
    return path.read_text(encoding='utf-8', errors='replace') if path.is_file() else ''


def title_of(root: Path) -> str:
    for line in read(root, '01_title.md').splitlines():
        line = re.sub(r'^\s*(#+|\*\*?title\*\*?:?|title:)\s*', '', line, flags=re.I).strip(' *_')
        if len(line.split()) >= 4 and ':' not in line[:12]:
            return line
    return ''


def default_query(root: Path) -> str:
    keep = []
    for word in WORD_RE.findall(title_of(root)):
        if word.lower() not in STOP and len(word) > 2 and word.lower() not in (k.lower() for k in keep):
            keep.append(word)
    return ' '.join(keep[:6])


def measure(root: Path) -> dict:
    """Manuscript counts compared with journal limits."""
    references = len(re.findall(r'(?m)^\s*(?:\d+[.)]|\[\d+\])\s+\S', read(root, '08_references.md')))
    if not references:
        references = len(set(EVID_RE.findall(''.join(read(root, n) for n in BODY))))
    figures = len(set(re.findall(r'(?i)\bfig(?:ure)?\.?\s*(\d+)', read(root, '09_figure_legends.md'))))
    declared_tables = declared(root)['tables']
    tables = (len([t for t in declared_tables if t.is_file()]) if declared_tables
              else len([t for t in (root / 'drafts').glob('table_*.md') if re.fullmatch(r'table_\d+', t.stem)]))
    return {'abstract_words': words(read(root, '02_abstract.md')),
            'main_text_words': sum(words(read(root, n)) for n in BODY),
            'references': references, 'tables_figures': tables + figures}


LABELS = {'abstract_words': 'Abstract words', 'main_text_words': 'Main text words (Introduction-Conclusion)',
          'references': 'References', 'tables_figures': 'Tables + figures'}


def limits_table(counts: dict, limits: dict) -> list[str]:
    rows = ['| Item | Manuscript | Journal limit | Status |', '|---|---|---|---|']
    for key in LIMITS:
        limit = limits.get(key)
        status = 'not in profile' if limit is None else ('OVER' if counts[key] > limit else 'ok')
        rows.append(f"| {LABELS[key]} | {counts[key]} | {limit if limit is not None else '-'} | {status} |")
    return rows


def manuscript(root: Path) -> str:
    return '\n\n'.join(f'### {n}\n\n{read(root, n).strip()}' for n in SECTIONS if read(root, n).strip())


# --- PubMed ----------------------------------------------------------------------

def since(years: int) -> str:
    return f'("{datetime.now().year - years + 1}"[dp] : "3000"[dp])'


def journal_evidence(query: str, ta: str, years: int, search=None, fetch=None) -> dict:
    """What the journal published on this topic: counts and recent titles ({'error'} when offline)."""
    search, fetch = search or patient(pubmed.search_pubmed), fetch or patient(pubmed.fetch_articles)
    try:
        ids, on_topic_here = search(f'({query}) AND "{ta}"[ta] AND {since(years)}', 8, 'pub_date')
        time.sleep(pubmed.RATE_LIMIT_DELAY)
        _, on_topic = search(f'({query}) AND {since(years)}', 0)
        time.sleep(pubmed.RATE_LIMIT_DELAY)
        _, journal_total = search(f'"{ta}"[ta] AND {since(years)}', 0)
        recent = fetch(ids) if ids else []
    except (OSError, ValueError) as exc:
        return {'error': str(exc)}
    return {'here': on_topic_here, 'topic': on_topic, 'journal_total': journal_total,
            'recent': [{'pmid': a.get('pmid'), 'title': a.get('title'), 'year': a.get('year'),
                        'design': design(a.get('pub_types', []))} for a in recent]}


def design(pub_types: list[str]) -> str:
    guess = pubmed.guess_study_design(pub_types)
    if not guess.startswith('['):
        return guess
    return next((t for t in pub_types if t not in ('Journal Article', 'English Abstract')), 'article')


def own_list(root: Path | None) -> list[tuple[str, str]]:
    """[(name, abbreviation)] in the order of the author's profile/journals.md (paper, else library)."""
    import library_sync
    for path in ([root / 'profile' / 'journals.md'] if root else []) + [library_sync.library() / 'profile' / 'journals.md']:
        if path.is_file():
            found = re.findall(r'(?m)^##\s+([^(\n]+?)\s*(?:\(([^)\n]+)\))?\s*(?:✓)?\s*$', path.read_text(encoding='utf-8'))
            return [(n.strip(), a.strip()) for n, a in found if not re.search(r'[가-힣]|principle', n, re.I)]
    return []


def cmd_list(args) -> int:
    return journal_list.cmd_list(args, paper_root(Path.cwd()), STYLE_TA)


def rank_journals(records: list[dict], preferred: list[tuple[str, str]], top: int) -> list[dict]:
    by = {}
    for r in records:
        source = r.get('source') or ''
        if not source:
            continue
        row = by.setdefault(source, {'journal': source, 'full': r.get('fulljournalname', ''), 'count': 0,
                                     'latest': '', 'example': ''})
        row['count'] += 1
        year = (r.get('pubdate') or '')[:4]
        if year > row['latest']:
            row['latest'], row['example'] = year, r.get('title', '')
    keys = {norm(a) or norm(n): i + 1 for i, (n, a) in enumerate(preferred)}
    keys.update({norm(n): i + 1 for i, (n, a) in enumerate(preferred)})
    rows = sorted(by.values(), key=lambda r: (-r['count'], r['journal']))[:top]
    total = sum(r['count'] for r in by.values()) or 1
    for row in rows:
        row['share'] = round(100 * row['count'] / total)
        row['yours'] = keys.get(norm(row['journal'])) or keys.get(norm(row['full']))
    return rows


# --- review ----------------------------------------------------------------------

def load_critical():
    spec = importlib.util.spec_from_file_location('critical_review', HERE / 'critical_review.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_reviews(packet: str, reviewers: str | None, run_dir: Path) -> list[str]:
    """Run the chosen reviewers with the journal prompt; returns what was saved, or how to review."""
    cr = load_critical()
    config = cr.settings()
    specs = [s.strip() for s in (reviewers or '').split(',') if s.strip()] or config.get('review', {}).get('reviewers', [])
    pairs = cr.expand_reviewers(specs, config)
    models = [cr.reviewer_id(a, m) if a != 'openrouter' else m for a, m in pairs]
    if not models:
        return ['No reviewers set (`manuwright setup` chooses them). Ask your agent to review packet.md with '
                'scripts/critical_prompts/journal.txt as a fresh subagent (/journal-review).']
    api_key = cr.os.environ.get('OPENROUTER_API_KEY') or cr.saved_openrouter_key()
    failures: dict = {}
    results = cr.run_critical_review(packet, models, 'journal', api_key, failures)
    lines = []
    for model_id, text in results.items():
        name = re.sub(r'[^A-Za-z0-9_.-]', '_', model_id).strip('.') + '_' + hashlib.sha256(model_id.encode()).hexdigest()[:8]
        (run_dir / f'{name}.md').write_text(text, encoding='utf-8')
        lines.append(f'review by {model_id}: {run_dir / (name + ".md")}')
    lines += [f'{m}: failed ({why})' for m, why in failures.items()]
    (run_dir / 'run.json').write_text(json.dumps({'role': 'journal', 'requested': models, 'completed': list(results),
                                                  'failures': failures, 'scope': 'advisory'}, indent=2), encoding='utf-8')
    return lines


def new_run(root: Path, name: str) -> Path:
    run_dir = root / 'review' / 'journal' / f"{slug(name)}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def resolve_journal(arg: str | None, root: Path) -> str:
    if arg:
        return arg
    key = json.loads((root / 'project.json').read_text(encoding='utf-8')).get('journal', '')
    return STYLE_TA.get(key, '')


def cmd_fit(args, search=None, fetch=None) -> int:
    root = paper_root(Path.cwd())
    if not root:
        print('journal fit: run it inside a paper folder (project.json).', file=sys.stderr)
        return 2
    journal = resolve_journal(args.journal, root)
    if not journal:
        print('journal fit: name the journal, e.g. manuwright journal fit "Spine J" (or set it with '
              '`manuwright target`).', file=sys.stderr)
        return 2
    query = args.query or default_query(root)
    if query and not args.query:
        print(f'PubMed search terms (from the title; only these words are sent, --query replaces them): {query}',
              flush=True)
    if not manuscript(root).strip():
        print('journal fit: no manuscript sections found (project.json artifacts, or drafts/0X_*.md); '
              'nothing to measure or review.', file=sys.stderr)
        return 2
    profile = read_profile(profile_path(journal, root))
    report = [f'# Journal fit: {journal}', '',
              f'PubMed query: `{query or "(none: pass --query)"}`, last {args.years} years.']
    if query:
        ev = journal_evidence(query, journal, args.years, search, fetch)
        if 'error' in ev:
            report.append(f'PubMed could not be reached ({ev["error"]}); the review runs without it.')
        else:
            share = f"{100 * ev['here'] / ev['journal_total']:.1f}%" if ev['journal_total'] else '-'
            report.append(f"{journal} published {ev['here']} articles on this topic (of {ev['topic']} on the topic in "
                          f"all journals; {share} of its {ev['journal_total']} articles).")
            report += [f"- {a['year']} {a['title']} (PMID {a['pmid']}; {a['design']})" for a in ev['recent']]
    entry = my_list().get(norm(journal))
    if entry:
        report.append(f'In your journal list: {list_note(entry)}.')
    report += ['', '## Requirements check', *limits_table(measure(root), profile.get('limits', {}))]
    missing = [str(p.relative_to(root)) for k, v in declared(root).items() for p in (v if k == 'tables' else [v])
               if not p.is_file()]
    if missing:
        report.append('Declared in project.json but missing (counted as 0): ' + ', '.join(missing))
    if not profile:
        report += ['', f'No journal profile yet: `manuwright journal profile "{journal}" --url <Aims & Scope page>`, '
                   'then fill it from the official pages. Without it the review cannot check journal policies.']
    elif not profile['verified']:
        report += ['', 'The journal profile is not verified by the author yet (verified_by_author: no).']
    run_dir = new_run(root, journal)
    (run_dir / 'report.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    packet = '\n'.join([f'MODE: fit\nTARGET JOURNAL: {journal}\n', '## Journal profile',
                        profile.get('text') or '(none: judge scope from the PubMed evidence and say what to verify)',
                        '', *report, '', '## Manuscript', manuscript(root)])
    (run_dir / 'packet.md').write_text(packet, encoding='utf-8')
    print('\n'.join(report))
    print(f'\nSaved: {run_dir / "report.md"} and packet.md')
    if not args.no_review:
        print('\n'.join(run_reviews(packet, args.reviewers, run_dir)))
    return 0


def mine_counts(query: str, mine: dict, years: int, search=None) -> list[dict]:
    """Articles on the topic in each journal of the author's list, most first (journals with none left out)."""
    search = search or patient(pubmed.search_pubmed)
    rows = []
    for entry in mine.values():
        _, count = search(f'({query}) AND "{entry["journal"]}"[ta] AND {since(years)}', 0)
        time.sleep(pubmed.RATE_LIMIT_DELAY)
        if count:
            rows.append({'journal': entry['journal'], 'full': entry['title'], 'count': count, 'latest': '-',
                         'yours': None})
    total = sum(r['count'] for r in rows) or 1
    for row in rows:
        row['share'] = round(100 * row['count'] / total)
    return sorted(rows, key=lambda r: (-r['count'], r['journal']))


def cmd_suggest(args) -> int:
    root = paper_root(Path.cwd())
    if not root:
        print('journal suggest: run it inside a paper folder (project.json).', file=sys.stderr)
        return 2
    query = args.query or default_query(root)
    if query and not args.query:
        print(f'PubMed search terms (from the title; only these words are sent, --query replaces them): {query}',
              flush=True)
    if not query:
        print('journal suggest: pass --query "<population intervention outcome terms>" (no title found).',
              file=sys.stderr)
        return 2
    try:
        ids, count = patient(pubmed.search_pubmed)(f'({query}) AND {since(args.years)}', 300)
        records = summaries(ids)
    except (OSError, ValueError) as exc:
        print(f'journal suggest: PubMed could not be reached ({exc}).', file=sys.stderr)
        return 1
    mine = my_list()
    if args.mine and not mine:
        print('journal suggest --mine: no journal list yet; import one with `manuwright journal list --import <file>`.',
              file=sys.stderr)
        return 2
    if args.mine:  # every journal in the list, counted directly (not only those in the 300 most relevant)
        try:
            rows = mine_counts(query, mine, args.years)
        except (OSError, ValueError) as exc:
            print(f'journal suggest: PubMed could not be reached ({exc}).', file=sys.stderr)
            return 1
        rows = rows[:args.top]
    else:
        rows = rank_journals(records, own_list(root), args.top)
    report = [f'# Journal suggestions', '', f'PubMed query: `{query}`, last {args.years} years: {count} articles '
              f'({len(records)} most relevant counted).', '',
              ('Only journals in your list (`journal list`).\n' if args.mine else ''),
              '| # | Journal | Articles | Share | Latest | Your list | Profile |', '|---|---|---|---|---|---|---|']
    for i, row in enumerate(rows, 1):
        has = 'yes' if read_profile(profile_path(row['journal'], root)) else '-'
        yours = list_note(mine.get(norm(row['journal']))) or ('#' + str(row['yours']) if row['yours'] else '-')
        report.append(f"| {i} | {row['journal']} | {row['count']} | {row['share']}% | {row['latest']} | "
                      f"{yours} | {has} |")
    report += ['', 'Counts show where similar work is published, not journal rank; impact factors are not used.',
               'Next: `manuwright journal fit "<journal>"` for the ones you consider.']
    run_dir = new_run(root, 'suggest')
    (run_dir / 'report.md').write_text('\n'.join(report) + '\n', encoding='utf-8')
    print('\n'.join(report))
    print(f'\nSaved: {run_dir / "report.md"}')
    if args.review:
        profiles = [f"### {r['journal']}\n{read_profile(profile_path(r['journal'], root)).get('text', '(no profile)')}"
                    for r in rows]
        packet = '\n'.join(['MODE: suggest\n', *report, '', '## Candidate journal profiles', *profiles, '',
                            '## Manuscript', manuscript(root)])
        (run_dir / 'packet.md').write_text(packet, encoding='utf-8')
        print('\n'.join(run_reviews(packet, args.reviewers, run_dir)))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('profile', help='create a journal profile (aims & scope, limits)')
    p.add_argument('journal')
    p.add_argument('--url', help="the journal's Aims & Scope or Guide for Authors page")
    p.add_argument('--from', dest='from_file', help='a text file with the copied page')
    f = sub.add_parser('fit', help='review the fit with one journal')
    f.add_argument('journal', nargs='?', help='NLM abbreviation, e.g. "Spine J" (default: the target journal)')
    s = sub.add_parser('suggest', help='journals that publish similar work')
    s.add_argument('--top', type=int, default=10)
    s.add_argument('--review', action='store_true', help='also ask the reviewers to rank the fit')
    s.add_argument('--mine', action='store_true', help='only journals in your journal list')
    li = sub.add_parser('list', help='your journal list (group, category percentile), kept on this computer')
    journal_list.add_arguments(li)
    for q in (f, s):
        q.add_argument('--query', help='PubMed terms for the topic (default: words of the title)')
        q.add_argument('--years', type=int, default=5)
        q.add_argument('--reviewers', help='reviewer specs as in critical review (default: your saved reviewers)')
    f.add_argument('--no-review', action='store_true', help='only the PubMed and requirements part')
    args = parser.parse_args(argv)
    if args.command == 'list':
        journal_list.finish_arguments(args)
    return {'profile': cmd_profile, 'fit': cmd_fit, 'suggest': cmd_suggest, 'list': cmd_list}[args.command](args)


if __name__ == '__main__':
    sys.exit(main())

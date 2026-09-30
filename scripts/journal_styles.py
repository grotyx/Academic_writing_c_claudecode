#!/usr/bin/env python3
"""Journal reference styles: render registered evidence as a target journal's reference list.

Each preset states author cutoff, in-text marker, reference order, page-range form, issue/month,
DOI form and journal-name italics. Data comes from full PubMed metadata (all authors, issue,
month, NLM abbreviation) cached in `knowledge/reference_metadata.json` by
`format_references.py --fetch`; without that cache the entry's own Citation string is parsed
(offline fallback; an author list already cut to "et al." cannot be expanded and is reported).

Spine/orthopaedic presets were checked against each journal's author instructions and published
papers; general-medicine presets follow the journals' published reference instructions. Titles are
kept as registered (no automatic sentence-casing). Always confirm against the current author
instructions before submission.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# pattern: vancouver "A. T. J. Y;V(I):P."  nejm "A. T. J Y;V:P."  lancet "A. T. J Y; V: P."
#          springer "A (Y) T. J V:P."
# pages:   asis | full-hyphen | full-endash | abbrev-hyphen | abbrev-endash
# doi:     none | prefix ("doi:10...") | url ("https://doi.org/10...")
# cutoff:  (max listed, kept when over) or None for all authors
STYLES = {
    'vancouver': dict(label='ICMJE / Vancouver (NLM)', cutoff=(6, 6), in_text='bracket', pattern='vancouver',
                      issue=True, pages='asis', doi='none'),
    'ama': dict(label='AMA 11th (JAMA Network)', cutoff=(6, 3), in_text='superscript', pattern='vancouver',
                issue=True, pages='full-hyphen', doi='prefix', italic=True),
    'nejm': dict(label='N Engl J Med', cutoff=(6, 3), in_text='superscript', pattern='nejm',
                 issue=False, pages='abbrev-hyphen', doi='none'),
    'lancet': dict(label='Lancet', cutoff=(6, 3), in_text='superscript', pattern='lancet',
                   issue=False, pages='abbrev-endash', doi='none', italic=True),
    'spine': dict(label='Spine (Phila Pa 1976)', cutoff=(3, 3), in_text='superscript', pattern='nejm',
                  issue=False, pages='abbrev-hyphen', doi='none'),
    'spine-j': dict(label='The Spine Journal', cutoff=(6, 6), in_text='bracket', pattern='vancouver',
                    issue=False, pages='full-endash', doi='none'),
    'bjj': dict(label='Bone Joint J', cutoff=(6, 3), in_text='superscript', pattern='vancouver',
                issue=True, pages='full-endash', doi='prefix', hyphen_initials=True),
    'jbjs': dict(label='J Bone Joint Surg Am', cutoff=None, in_text='superscript', pattern='vancouver',
                 issue=True, month=True, pages='abbrev-hyphen', doi='none'),
    'neurospine': dict(label='Neurospine', cutoff=(3, 3), in_text='superscript', pattern='vancouver',
                       issue=True, pages='full-endash', doi='url'),
    'jns-spine': dict(label='J Neurosurg Spine (AMA)', cutoff=(6, 3), in_text='superscript', pattern='vancouver',
                      issue=True, pages='full-hyphen', doi='prefix', italic=True),
    'gsj': dict(label='Global Spine J (AMA)', cutoff=(6, 3), in_text='superscript', pattern='vancouver',
                issue=True, pages='full-hyphen', doi='prefix', italic=True),
    'corr': dict(label='Clin Orthop Relat Res', cutoff=(6, 3), in_text='bracket', pattern='vancouver',
                 issue=False, pages='full-hyphen', doi='none', italic=True, order='alphabetical'),
    'asj': dict(label='Asian Spine J', cutoff=(6, 3), in_text='superscript', pattern='vancouver',
                issue=True, pages='full-hyphen', doi='url'),
    'esj': dict(label='Eur Spine J (Springer)', cutoff=None, in_text='bracket', pattern='springer',
                issue=False, pages='full-endash', doi='url'),
}
MONTHS = {str(i): m for i, m in enumerate(
    ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], 1)}
VANCOUVER_RE = re.compile(r'^(?P<authors>.+?)\. (?P<title>.+?)\. (?P<journal>[^.]+?)\.? (?P<year>(?:19|20)\d{2})'
                          r'(?: [A-Z][a-z]{2}(?: \d{1,2})?)?(?:;(?P<volume>[^(:]+))?(?:\((?P<issue>[^)]+)\))?'
                          r'(?::(?P<pages>[^.\s]+(?:\.e\d+)?))?\.?\s*$')


def load_cache(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


def from_pubmed(article: dict) -> dict:
    return {'authors': article.get('author_parts') or [[a.rsplit(' ', 1)[0], a.rsplit(' ', 1)[-1], '']
                                                        for a in article.get('authors', [])],
            'complete': True, 'title': article.get('title', ''),
            'journal': article.get('medline_ta') or article.get('journal_abbr') or article.get('journal', ''),
            'year': article.get('year', ''), 'month': article.get('month', ''), 'volume': article.get('volume', ''),
            'issue': article.get('issue', ''), 'pages': article.get('pages', ''), 'doi': article.get('doi', '')}


def from_citation(citation: str, doi: str = '') -> dict | None:
    """Parse a Vancouver Citation string (as written by search_pubmed / import-obsidian)."""
    match = VANCOUVER_RE.match(citation.strip())
    if not match:
        return None
    names = [n.strip() for n in match['authors'].split(',') if n.strip()]
    complete = not (names and names[-1].rstrip('.') == 'et al')
    names = [n for n in names if n.rstrip('.') != 'et al']
    return {'authors': [[n.rsplit(' ', 1)[0], n.rsplit(' ', 1)[-1] if ' ' in n else '', ''] for n in names],
            'complete': complete, 'title': match['title'], 'journal': match['journal'], 'year': match['year'],
            'month': '', 'volume': (match['volume'] or '').strip(), 'issue': match['issue'] or '',
            'pages': match['pages'] or '', 'doi': doi}


def pages(value: str, form: str) -> str:
    match = re.fullmatch(r'(\d+)-(\d+)', value or '')
    if form == 'asis' or not match:
        return (value or '').replace('-', '–') if form.endswith('endash') else (value or '')
    start, end = match.groups()
    if len(end) < len(start):  # expand MEDLINE "1741-9" first
        end = start[:len(start) - len(end)] + end
    if form.startswith('abbrev'):
        i = 0
        while i < len(end) - 1 and start[i] == end[i]:
            i += 1
        end = end[i:]
    return start + ('–' if form.endswith('endash') else '-') + end


def author(parts: list, hyphen: bool) -> str:
    last, initials, fore = (list(parts) + ['', ''])[:3]
    if hyphen and '-' in fore:  # BJJ: "Sang-Min" -> "S-M"
        initials = '-'.join(p[:1].upper() for p in fore.split('-'))
    return f'{last} {initials}'.strip()


def render(meta: dict, style: dict) -> str:
    names = [author(a, style.get('hyphen_initials', False)) for a in meta['authors']]
    cutoff = style['cutoff']
    # A stored list ending in "et al." hides at least one more author than it shows.
    total = len(names) + (0 if meta['complete'] else 1)
    if cutoff and total > cutoff[0]:
        names = names[:cutoff[1]] + ['et al']
    elif not meta['complete']:
        names = names + ['et al']
    authors = ', '.join(names)
    title = meta['title'].rstrip('.')
    journal = f"*{meta['journal']}*" if style.get('italic') else meta['journal']
    date = meta['year'] + (f" {MONTHS.get(meta['month'], meta['month'])}" if style.get('month') and meta['month'] else '')
    issue = f"({meta['issue']})" if style['issue'] and meta['issue'] else ''
    page = pages(meta['pages'], style['pages'])
    pattern = style['pattern']
    if pattern == 'springer':
        text = f"{authors} ({meta['year']}) {title}. {journal} {meta['volume']}{issue}:{page}."
    else:
        sep = '; ' if pattern == 'lancet' else ';'
        colon = ': ' if pattern == 'lancet' else ':'
        journal_part = f'{journal}.' if pattern == 'vancouver' else journal
        vol = f"{sep}{meta['volume']}{issue}" if meta['volume'] else ''
        text = f"{authors}. {title}. {journal_part} {date}{vol}{colon + page if page else ''}."
    doi = meta.get('doi')
    if doi and style['doi'] == 'prefix':
        text += f' doi:{doi}'
    elif doi and style['doi'] == 'url':
        text += f' https://doi.org/{doi}'
    return text.replace('..', '.')


def group_label(numbers: list[int], in_text: str) -> str:
    """[1,2,4-6] style run: ranges of three or more collapse with an en dash."""
    numbers = sorted(set(numbers))
    runs, start = [], 0
    for i in range(1, len(numbers) + 1):
        if i == len(numbers) or numbers[i] != numbers[i - 1] + 1:
            run = numbers[start:i]
            runs.append(f'{run[0]}–{run[-1]}' if len(run) >= 3 else ','.join(map(str, run)))
            start = i
    body = ','.join(runs)
    return f'^{body}^' if in_text == 'superscript' else f'[{body}]'


if __name__ == '__main__':
    demo = {'authors': [['Miller', 'LE', 'Larry E'], ['Bhattacharyya', 'S', ''], ['Pracyk', 'J', ''],
                        ['Kim', 'SM', 'Sang-Min'], ['Lee', 'J', ''], ['Park', 'H', ''], ['Choi', 'Y', '']],
            'complete': True, 'title': 'A trial.', 'journal': 'World Neurosurg', 'year': '2020', 'month': '1',
            'volume': '133', 'issue': '2', 'pages': '358-365', 'doi': '10.1/x'}
    assert render(demo, STYLES['nejm']) == 'Miller LE, Bhattacharyya S, Pracyk J, et al. A trial. World Neurosurg 2020;133:358-65.'
    assert render(demo, STYLES['jbjs']).startswith('Miller LE, Bhattacharyya S, Pracyk J, Kim SM, Lee J, Park H, Choi Y. A trial. World Neurosurg. 2020 Jan;133(2):358-65.')
    assert render(demo, STYLES['lancet']).endswith('*World Neurosurg* 2020; 133: 358–65.')
    assert pages('1741-9', 'full-hyphen') == '1741-1749' and pages('358-365.e4', 'abbrev-hyphen') == '358-365.e4'
    assert group_label([1, 2, 3, 5], 'bracket') == '[1–3,5]' and group_label([2, 1], 'superscript') == '^1,2^'
    print('ok')

#!/usr/bin/env python3
"""Academic writing mode: section style cards, a learned style profile, and prose checks.

A model cannot be fine-tuned from here, so this module does the next best thing at every write:
it puts the right *examples* and *measured targets* in front of the writer and checks the prose
that comes back.

  core                        the always-on card (session start)
  card <section> [--project DIR]
                              the section card: rhetorical moves, rules, phrasebank and model
                              paragraphs (docs/academic_style/), plus the measured style of your
                              corpus when one was learned
  learn [paths...] [--out DIR]
                              measure a corpus of good papers (yours, landmark, target journal;
                              PDF, DOCX, MD or TXT) per section: sentence length, passive voice,
                              hedging, signature phrases, typical openers, and model paragraphs.
                              Default sources: the PDFs in your manuwright writing library.
  check <file>... [--strict]  academic-prose findings (exit 1 on high-severity ones; --strict:
                              on any)
  preserve <before> <after>   a style rewrite must keep every [EVID:id], number, p value and
                              table/figure reference (exit 1 when one was dropped or added)
  edits <ai> <edited> | --git REV | --apply
                              learn from how the author edited AI drafts: word substitutions and
                              deletions, counted (P0 = 2+ times), written to Style/pending_style_rules.md;
                              --apply moves the rules the author ticked into Style/terminology.md
  status                      writing mode and learned profile

Writing mode (`manuwright mode academic|strict|off`, or MANUWRIGHT_WRITING_MODE): academic shows
the cards and reports findings after each edit; strict also blocks a write to a manuscript
section whose new text has high-severity findings; off turns the mode off.

The learned profile and its model paragraphs come from papers you hold; they stay on this
machine (your manuwright library, or --out) and are never copied into a paper folder.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import statistics
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
STYLE_DIR = ROOT / 'docs' / 'academic_style'
sys.path.insert(0, str(HERE))
from check_style import HEDGES, split_sentences  # noqa: E402

SECTIONS = ('title', 'abstract', 'introduction', 'methods', 'results', 'discussion', 'conclusion')
MODES = ('academic', 'strict', 'off')
FILE_SECTIONS = {'01': 'title', '02': 'abstract', '03': 'introduction', '04': 'methods', '05': 'results',
                 '06': 'discussion', '07': 'conclusion'}
SOURCE_SUFFIXES = ('.pdf', '.docx', '.md', '.txt')
DEFAULT_LONG = 45


# --- settings -----------------------------------------------------------------

def home() -> Path:
    return Path(os.environ.get('MANUWRIGHT_HOME') or Path.home() / '.manuwright')


def mode() -> str:
    """academic (default), strict or off: MANUWRIGHT_WRITING_MODE, else `manuwright mode`."""
    value = os.environ.get('MANUWRIGHT_WRITING_MODE', '').strip().lower()
    if not value:
        try:
            value = str(json.loads((home() / 'config.json').read_text(encoding='utf-8')).get('writing_mode') or '')
        except (OSError, ValueError, AttributeError):
            value = ''
    return value if value in MODES else 'academic'


def library_profile_dir() -> Path:
    return home() / 'library' / 'writing' / 'profile'


def profile_dir(project: Path | None = None) -> Path | None:
    """The learned profile in use: the paper's Style/profile/, else the personal library's."""
    for folder in ([project / 'Style' / 'profile'] if project else []) + [library_profile_dir()]:
        if (folder / 'style_profile.json').is_file():
            return folder
    return None


def load_profile(project: Path | None = None) -> tuple[dict, Path | None]:
    folder = profile_dir(project)
    if not folder:
        return {}, None
    try:
        return json.loads((folder / 'style_profile.json').read_text(encoding='utf-8')), folder
    except (OSError, ValueError):
        return {}, None


KOREAN_SECTIONS = {'제목': 'title', '초록': 'abstract', '서론': 'introduction', '방법': 'methods', '재료및방법': 'methods',
                   '결과': 'results', '고찰': 'discussion', '논의': 'discussion', '결론': 'conclusion'}


def section_name(value: str) -> str:
    """'discussion', 'Discussion', '고찰', 'method' -> canonical section name (argparse type)."""
    key = re.sub(r'\s+', '', value).lower()
    name = KOREAN_SECTIONS.get(key) or next((s for s in SECTIONS if key in (s, s.rstrip('s'))), None)
    if not name:
        raise argparse.ArgumentTypeError(f'unknown section {value!r}; use one of: {", ".join(SECTIONS)} '
                                         '(or 제목, 초록, 서론, 방법, 결과, 고찰, 결론)')
    return name


def section_of(path) -> str | None:
    """Section of a manuscript file: 03_introduction.md -> introduction (number prefix or name)."""
    name = Path(str(path)).name.lower()
    prefix = re.match(r'(0[1-7])_', name)
    if prefix:
        return FILE_SECTIONS[prefix.group(1)]
    return next((s for s in SECTIONS if s in name), None)


# --- prose checks ---------------------------------------------------------------

HIGH = 'high'
MEDIUM = 'medium'
_I = re.IGNORECASE
PHRASE_RULES = [  # (severity, code, pattern, message)
    (HIGH, 'AI_PHRASE', re.compile(
        r"\bdelv(?:e|es|ed|ing)\b|\btapestry\b|\btestament to\b|\bit is (?:worth noting|important to note|noteworthy)\b"
        r"|\bsh(?:ed|eds|edding) (?:new )?light on\b|\bin the realm of\b|\bever-(?:evolving|changing)\b|\bin today's\b"
        r"|\ba myriad of\b|\bembark(?:s|ed|ing)? on\b|\bharness(?:es|ed|ing)? the (?:power|potential)\b"
        r"|\bpav(?:e|es|ed|ing) the way\b|\bgame[- ]changer\b|\bunlock(?:s|ed|ing)? the (?:potential|power)\b"
        r"|\b(?:evolving|complex) landscape\b|\bnavigat(?:e|es|ed|ing) the (?:complex|challenges|landscape)",
        _I), 'AI-register phrase; state the specific fact instead'),
    (HIGH, 'AI_PHRASE', re.compile(r"\bplay(?:s|ed|ing)? an? (?:crucial|pivotal|vital) role\b", _I),
     'say what X does to Y, with a citation'),
    # "plays a key/critical role" also occurs in pre-AI papers: a suggestion, never a strict-mode block.
    (MEDIUM, 'AI_PHRASE', re.compile(r"\bplay(?:s|ed|ing)? an? (?:key|critical|central|significant) role\b", _I),
     'say what X does to Y, with a citation'),
    (MEDIUM, 'AI_PHRASE', re.compile(r"\b(?:promising avenues?|valuable insights?|transformative|"
                                     r"foster(?:s|ed|ing)?|(?:highlight|underscore|emphasi[sz]e)s? the (?:critical|crucial|vital) "
                                     r"(?:importance|need|role))\b", _I),
     'AI-register phrase; state the specific finding instead'),
    # A trailing "-ing" clause that announces importance is the AI tell; a plain participle is not
    # (", highlighting ..." occurs 0.4 times per 10,000 words in the reference corpus).
    (HIGH, 'ING_TAIL', re.compile(
        r",\s+(?:thereby\s+|thus\s+)?(?:highlighting|underscoring|emphasi[sz]ing|showcasing|demonstrating|signal(?:l)?ing"
        r"|reinforcing|illustrating)\s+(?:the\s+|its\s+|their\s+|a\s+|an\s+)?(?:\w+\s+)?(?:importance|need|potential|role"
        r"|value|significance|promise|relevance|necessity)\b", _I),
     'trailing ", highlighting the importance ..." clause; end the sentence and state the consequence plainly'),
    (MEDIUM, 'ING_TAIL', re.compile(r",\s+(?:thereby\s+|thus\s+)?(?:highlighting|underscoring|emphasi[sz]ing|showcasing)\b", _I),
     'trailing ", highlighting ..." clause; consider ending the sentence and stating the point'),
    (HIGH, 'CHATBOT', re.compile(r"\bI hope this helps\b|\blet me know\b|\bas an AI\b|^(?:certainly|sure|absolutely)[!,.]"
                                 r"|\bhere is (?:a|an|the) (?:revised|draft|rewritten)", _I | re.M),
     'chat residue; delete it'),
    (HIGH, 'CONTRACTION', re.compile(r"\b(?:do|does|did|is|are|was|were|has|have|had|could|would|should|ca|wo)n['’]t\b"
                                     r"|\b(?:it|that|there|what|let)['’]s\b|\b(?:we|they|you)['’](?:re|ve|ll|d)\b", _I),
     'contraction; write the full form'),
    # 0 occurrences in the 179,000-word reference corpus: the core card says "never", so these are must-fix.
    (HIGH, 'AI_WORD', re.compile(
        r"\b(?:intricate|showcas(?:e|es|ed|ing)|leverag(?:es|ed|ing)|(?<!high[- ])(?<!low[- ])leverage(?!\s+(?:points?|values?|statistics?|plots?|observations?))|seamless(?:ly)?|holistic|paramount"
        r"|underscor(?:e|es|ed|ing)|realm|meticulous(?:ly)?)\b", _I),
     'never used in the reference journals; use a plain, precise word or delete it'),
    # Rare but present in the reference corpus: a suggestion.
    (MEDIUM, 'AI_WORD', re.compile(
        r"\b(?:crucial|pivotal|multifaceted|nuanced|commendable|bolster(?:s|ed|ing)?)\b", _I),
     'AI-register word; use a plain, precise word or delete it'),
    # Guarded patterns adapted from unslop (MIT, Copyright (c) 2026 Mohamed Abdallah; THIRD_PARTY_NOTICES.md).
    (MEDIUM, 'INFLATION', re.compile(
        r"\b(?:marks?|represents?|stands?\s+as)\s+(?:a|an|the)\s+(?:pivotal|defining|critical|key|watershed|seminal)"
        r"\s+(?:moment|turning\s+point|milestone|step|advance)\b|\bserve[sd]?\s+as\s+(?:a|an|the)\s+(?:cornerstone|backbone"
        r"|beacon|catalyst|testament|gateway)\b|\bunprecedented(?=\s+(?:opportunity|opportunities|challenge|challenges"
        r"|growth|impact|change)\b)", _I),
     'significance inflation; state what was found'),
    (MEDIUM, 'VAGUE_ATTRIBUTION', re.compile(r"\b(?:experts|researchers|observers|many|some) (?:argue|believe|maintain|"
                                             r"say|note)\b(?![^.]*\[EVID:)", _I),
     'unattributed claim; name the studies and cite them'),
    (MEDIUM, 'BELIEF', re.compile(r"\bwe (?:believe|feel|think)\b", _I), '"we believe"; let the evidence carry the claim'),
    (MEDIUM, 'SIGNPOST', re.compile(r"(?:^|[.!?]\s+)(?:Importantly|Interestingly|Notably|Remarkably|Crucially|Significantly),"
                                    r"|\bin this section\b", _I),
     'signposting opener; start with the content'),
]
CONNECTIVES = re.compile(r"^(?:Furthermore|Moreover|Additionally|In addition)\b", _I)
SIGNIFICANT = re.compile(r"\bsignificant(?:ly)?\b", _I)
STATS = re.compile(r"\*?\bp\*?\s*[<=>≤]|\bp[ -]values?\b|\bCI\b|confidence interval|\b(?:Supplementary )?(?:Table|Fig(?:ure)?\.?)\s*S?\d"
                   r"|\b(?:OR|HR|RR|aOR|aHR|IRR|odds ratio|hazard ratio|risk ratio|relative risk|mean difference)\b[^.]*\d", _I)
BOLD = re.compile(r"\*\*[^*\n]+\*\*|__[^_\n]+__")
LEADING_BOLD = re.compile(r"^\s*(?:\*\*[^*\n]+\*\*|__[^_\n]+__)\s*[:.]?")
BODY_SECTIONS = ('introduction', 'methods', 'results', 'discussion', 'conclusion')
# Synonym cycling (unslop): 3+ members of one group in a paragraph reads as avoiding repetition.
SYNONYM_GROUPS = (
    frozenset({'utilize', 'utilise', 'leverage', 'employ', 'harness'}),
    frozenset({'showcase', 'highlight', 'emphasize', 'emphasise', 'underscore'}),
    frozenset({'pivotal', 'crucial', 'vital', 'paramount', 'essential'}),
    frozenset({'comprehensive', 'thorough', 'exhaustive', 'holistic'}),
)
FLAT_SECTIONS = ('introduction', 'discussion', 'conclusion')


def _prose_lines(text: str):
    """(line number, line) for running prose: no headings, tables, comments, code or keyword lines."""
    fence = False
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith('```'):
            fence = not fence
            continue
        if (fence or not stripped or stripped[0] in '#|>' or stripped.startswith('<!--')
                or re.match(r'\*{0,2}\s*key\s?words?\s*:', stripped, _I)):
            continue
        yield number, line


def _paragraphs(text: str):
    """(joined prose, [(offset, line number)]) for each paragraph, to place a sentence on its line."""
    block, marks, last = [], [], None
    for number, line in _prose_lines(text):
        if block and number != last + 1:
            yield ' '.join(block), marks
            block, marks = [], []
        marks.append((len(' '.join(block)) + (1 if block else 0), number))
        block.append(line.strip())
        last = number
    if block:
        yield ' '.join(block), marks


def _line_at(paragraph: str, marks: list, sentence: str) -> int:
    offset = paragraph.find(sentence[:40])
    return max((n for o, n in marks if o <= max(offset, 0)), default=marks[0][1])


def _plain(sentence: str) -> str:
    return re.sub(r'[*_`]', '', re.sub(r'\[EVID:[^\]]+\]', '', sentence)).strip()


def prose_issues(text: str, section: str | None = None, long_limit: int | None = None) -> list[tuple]:
    """[(severity, code, line, message)] for academic prose. Pure; never raises on odd input."""
    limit = long_limit or DEFAULT_LONG
    found = []
    for number, line in _prose_lines(text):
        spans = []
        # must-fix rules first, so a "consider" match never hides a must-fix word inside it
        # (", showcasing the ..." is both a tail clause and a never-used word, reported once as must-fix)
        for severity, code, pattern, message in sorted(PHRASE_RULES, key=lambda rule: rule[0] != HIGH):
            for match in pattern.finditer(line):  # every hit: one paragraph is one line in markdown
                if not any((a <= match.start() and match.end() <= b)
                           or (sev != severity and match.start() < b and a < match.end()) for sev, a, b in spans):
                    spans.append((severity, *match.span()))
                    found.append((severity, code, number, f'"{match.group(0).strip(" ,.")}": {message}'))
        if section in BODY_SECTIONS:
            # a run-in heading ("**Study design.** We ...", "**Study design**: We ...") is journal style, not emphasis
            run_in = re.match(r'^\s*(?:\*\*|__)[^*_\n]+(?:[:.](?:\*\*|__)|(?:\*\*|__)\s*[:.])', line)
            body = LEADING_BOLD.sub('', line, count=1) if run_in else line
            if line.strip() and not LEADING_BOLD.fullmatch(line.strip()) and BOLD.search(body):
                found.append((HIGH, 'BOLD', number, 'bold in running text; carry emphasis with sentence structure'))
            if section in ('introduction', 'discussion', 'conclusion') and re.match(r'^\s*(?:[-*+]|\d+[.)])\s+', line):
                found.append((MEDIUM, 'LIST', number, 'list in the body; write it as prose'))
    for paragraph, marks in _paragraphs(text):
        previous_connective = False
        stems = {re.sub(r'(?:s|d|ed|ing)$', '', w) for w in re.findall(r'[a-z]+', paragraph.lower())}
        for group in SYNONYM_GROUPS:
            used = sorted(w for w in group if w in stems or re.sub(r'e$', '', w) in stems)
            if len(used) >= 3:
                found.append((MEDIUM, 'SYNONYM_CYCLING', marks[0][1],
                              f'{", ".join(used)} in one paragraph; pick one plain word and repeat it'))
        lengths = [len(x.split()) for x in split_sentences(paragraph) if x.strip()]
        if section in FLAT_SECTIONS and len(lengths) >= 5 and statistics.pstdev(lengths) < 2.5:
            found.append((MEDIUM, 'FLAT_RHYTHM', marks[0][1],
                          f'{len(lengths)} sentences of nearly equal length; vary them as published prose does'))
        for sentence in split_sentences(paragraph):
            start = _line_at(paragraph, marks, sentence)
            plain = _plain(sentence)
            words = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", plain))
            if words > limit:
                found.append((MEDIUM, 'LONG_SENTENCE', start, f'{words}-word sentence (limit {limit}); split it: '
                                                              f'"{plain[:60]}..."'))
            if re.match(r'^\d', plain) and section != 'title' and not re.match(r'^\d+[.)]\s', plain):  # not a list item
                found.append((MEDIUM, 'NUMERAL_START', start, f'sentence starts with a numeral: "{plain[:40]}"'))
            if plain.endswith('?'):
                found.append((MEDIUM, 'QUESTION', start, f'rhetorical question: "{plain[:60]}"'))
            if '!' in plain:
                found.append((MEDIUM, 'EXCLAMATION', start, 'exclamation mark in scientific prose'))
            connective = bool(CONNECTIVES.match(plain))
            if connective and previous_connective:
                found.append((MEDIUM, 'CONNECTIVE_RUN', start,
                              'consecutive sentences open with Furthermore/Moreover/Additionally; drop one'))
            previous_connective = connective
            if section in ('results', 'abstract') and SIGNIFICANT.search(plain) and not STATS.search(sentence):
                found.append((MEDIUM, 'SIGNIFICANT_NO_STATS', start,
                              f'"significant" without an estimate, CI or *p*: "{plain[:60]}"'))
    return found


MIN_DOCUMENTS, MIN_SENTENCES = 3, 30  # a learned section below this is shown, never enforced


def enough(entry: dict | None) -> bool:
    return bool(entry) and entry.get('documents', 0) >= MIN_DOCUMENTS and entry.get('sentences', 0) >= MIN_SENTENCES


def long_limit_for(section: str | None, project: Path | None = None) -> int:
    """Sentence-length ceiling (30-55 words): the 95th percentile of a large enough learned corpus for this
    section, else of the high-impact reference corpus; never below the reference 90th percentile."""
    profile, _ = load_profile(project)
    entry = (profile.get('sections') or {}).get(section or '')
    reference = (reference_profile().get('overall') or {}).get(section or '') or {}
    length = entry.get('sentence_length', {}) if enough(entry) else {}
    value = length.get('p95') or length.get('p90') or reference.get('p95_len')
    if not value:
        return DEFAULT_LONG
    return int(min(55, max(30, reference.get('p90_len', 0), round(value))))


def reference_profile() -> dict:
    """Measured style of high-impact medical and surgical journals (numbers and generic phrases only)."""
    try:
        return json.loads((STYLE_DIR / 'reference_profile.json').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return {}


PROTECTED = re.compile(r'\[EVID:[^\]]+\]|(?:Table|Fig(?:ure)?\.?|Supplementary (?:Table|Figure))\s*S?\d+[A-Za-z]?'
                       r'|\*?\b[pP]\*?\s*[<=>\u2264\u2265]\s*0?\.\d+'
                       # a number keeps its sign and comparator: "-1.2" -> "1.2" or "\u226565" -> "<65" is a new fact
                       r'|(?:[<>\u2264\u2265]\s*)?(?:(?<![\w.])[-\u2212\u2013])?\d+(?:\.\d+)?\s*%?')


def protected_tokens(text: str) -> Counter:
    """Citations, table/figure references, p values and numbers: what a style rewrite must not change."""
    # italics, P/p and the minus glyph are formatting, not content: "P = 0.04" and "*p* = 0.04" are the same value
    def norm(tok: str) -> str:
        tok = re.sub(r'[\s*_]+', '', tok).replace('\u2212', '-').replace('\u2013', '-')
        return 'p' + tok[1:] if tok[:1] == 'P' else tok
    return Counter(m.group(0) if m.group(0).startswith('[EVID:') else norm(m.group(0)) for m in PROTECTED.finditer(text))


def preserve_problems(before: str, after: str) -> list[str]:
    """Protected tokens a rewrite dropped or added (humanizer/unslop fact-preservation idea, made deterministic)."""
    old, new = protected_tokens(before), protected_tokens(after)
    lost = [f'dropped {tok!r}' + (f' x{n}' if n > 1 else '') for tok, n in (old - new).items()]
    gained = [f'added {tok!r}' + (f' x{n}' if n > 1 else '') for tok, n in (new - old).items()]
    return lost + gained


# --- reading a corpus -----------------------------------------------------------------

def _pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError:
        PdfReader = None
    if PdfReader is not None:
        try:
            return '\n'.join(page.extract_text() or '' for page in PdfReader(str(path)).pages)
        except Exception:
            return ''
    exe = shutil.which('pdftotext')
    if exe:
        done = subprocess.run([exe, '-enc', 'UTF-8', str(path), '-'], capture_output=True, text=True,
                              encoding='utf-8', errors='replace', timeout=120)
        return done.stdout if done.returncode == 0 else ''
    raise RuntimeError('reading PDF needs pypdf (pip install pypdf) or pdftotext')


def _docx_text(path: Path) -> str:
    from docx import Document
    lines = []
    for paragraph in Document(str(path)).paragraphs:
        text = paragraph.text.strip()
        heading = (paragraph.style.name or '').lower().startswith(('heading', 'title'))
        lines.append(('# ' + text) if heading and text else text)
        lines.append('')
    return '\n'.join(lines)


def read_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == '.pdf':
        return _pdf_text(path)
    if suffix == '.docx':
        return _docx_text(path)
    return path.read_text(encoding='utf-8', errors='replace')


NOISE = re.compile(r'downloaded from|©|copyright|https?://|\bdoi\b|all rights reserved|creativecommons', _I)


def clean_text(text: str) -> str:
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text.replace('\r', ''))  # PDF line-break hyphens
    lines = [ln for ln in text.splitlines() if not NOISE.search(ln) and not re.fullmatch(r'\s*\d{1,4}\s*', ln)]
    # Stripped citation numbers glue sentences together ("techniques.Postoperative"); split them again.
    return re.sub(r'([a-z)\]])\.([A-Z][a-z])', r'\1. \2', '\n'.join(lines))


HEADING_NAMES = {
    'abstract': {'abstract', 'summary', 'structured abstract'},
    'introduction': {'introduction', 'background'},
    'methods': {'methods', 'method', 'materials and methods', 'material and methods', 'patients and methods',
                'subjects and methods', 'methodology', 'study design', 'participants and methods'},
    'results': {'results', 'result'},
    'discussion': {'discussion', 'comment'},
    'conclusion': {'conclusion', 'conclusions', 'summary and conclusions'},
}
END_NAMES = {'references', 'reference', 'bibliography', 'acknowledgements', 'acknowledgments', 'acknowledgement',
             'funding', 'conflict of interest', 'conflicts of interest', 'disclosures', 'author contributions',
             'data availability', 'data availability statement', 'supplementary material',
             'declaration of competing interest', 'competing interests', 'abbreviations'}
HEADING_LINE = re.compile(r'^\s*(?:#{1,6}\s*)?(?:\d+(?:\.\d+)*\.?\s+|[IVX]+\.\s+)?([A-Za-z][A-Za-z &/]{2,45}?)\s*:?\s*$')
ABSTRACT_MAX_WORDS = 400


def _heading(line: str) -> tuple[str, str] | None:
    """(section or 'END', heading text) for a heading line, else None."""
    match = HEADING_LINE.match(line.replace('*', ''))
    if not match:
        return None
    name = re.sub(r'\s+', ' ', match.group(1).strip().lower())
    if name in END_NAMES:
        return 'END', name
    section = next((s for s, names in HEADING_NAMES.items() if name in names), None)
    return (section, name) if section else None


def split_sections(text: str) -> dict:
    """{section: text} from a paper's headings; structured-abstract labels stay in the abstract."""
    parts: dict = {}
    current, abstract_words, labels = None, 0, set()
    for line in text.splitlines():
        heading = _heading(line)
        if heading:
            section, name = heading
            if section == 'END':
                if current not in (None, 'abstract'):
                    break
                continue
            # A structured-abstract label (Background:, Methods:) stays in the abstract; the same label a second
            # time is the body's real heading (BMC-style papers open the body with "Background").
            label = (current == 'abstract' and abstract_words < ABSTRACT_MAX_WORDS and name != 'introduction'
                     and section in ('introduction', 'methods', 'results', 'conclusion') and section not in labels)
            if label:
                labels.add(section)
            else:
                current = section
            continue
        if current == 'abstract':
            abstract_words += len(line.split())
            if abstract_words > ABSTRACT_MAX_WORDS + 150:
                current = 'introduction'  # journals that print no Introduction heading
        if current:
            parts.setdefault(current, []).append(line)
    return {section: '\n'.join(lines).strip() for section, lines in parts.items() if '\n'.join(lines).strip()}


def corpus_files(paths: list[Path]) -> list[Path]:
    files = []
    for path in paths:
        if path.is_dir():
            files += sorted(p for p in path.rglob('*') if p.is_file() and p.suffix.lower() in SOURCE_SUFFIXES
                            and 'profile' not in p.relative_to(path).parts[:-1])
        elif path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES:
            files.append(path)
    skip = {'style_guide.md', 'terminology.md', 'style_spec.md', 'readme.md', 'index.md'}
    return [f for f in dict.fromkeys(files) if f.name.lower() not in skip and not f.name.startswith('example_')]


# --- measuring ---------------------------------------------------------------------

IRREGULAR = ('found|made|seen|given|taken|shown|done|kept|held|set|put|led|known|drawn|chosen|written|undergone'
             '|left|lost|met|paid|read|sent|spent|built|brought|felt|cut|begun|grown|thought|told|won|worn')
PASSIVE = re.compile(r'\b(?:is|are|was|were|be|been|being)\s+(?:\w+ly\s+)?(?:\w+ed|' + IRREGULAR + r')\b', _I)
TRANSITIONS = ('However', 'In addition', 'Furthermore', 'Moreover', 'Therefore', 'Thus', 'Nevertheless', 'Conversely',
               'Consequently', 'Notably', 'Overall', 'Specifically', 'Similarly', 'In contrast', 'Accordingly', 'Hence',
               'First', 'Second', 'Finally', 'Additionally', 'Nonetheless', 'Indeed')
STOP = set(('a an the of to in for with on at by from and or but as is are was were be been this that these those '
            'it its their our we which who than then there into not no can may also between after before during '
            'all each both such other more most less').split())
TOKEN = re.compile(r"[a-z0-9][a-z0-9\-']*")


def _sentences(text: str) -> list[str]:
    out = []
    for block in re.split(r'\n\s*\n', text):
        joined = ' '.join(ln.strip() for ln in block.splitlines() if ln.strip() and not ln.strip().startswith(('#', '|')))
        for sentence in split_sentences(joined):
            n = len(sentence.split())
            if 5 <= n <= 80 and sum(c.isalpha() for c in sentence) > len(sentence) * 0.5:
                out.append(_plain(sentence))
    return out


def _blocks(text: str) -> list[str]:
    """Paragraph-like passages: real paragraphs when present, else windows of 4-6 sentences."""
    out = []
    for block in re.split(r'\n\s*\n', text):
        joined = ' '.join(ln.strip() for ln in block.splitlines() if ln.strip() and not ln.strip().startswith(('#', '|')))
        sentences = [s for s in split_sentences(joined) if s.strip()]
        words = len(joined.split())
        if 60 <= words <= 220 and len(sentences) >= 3:
            out.append(joined)
        elif words > 220:
            for i in range(0, len(sentences) - 3, 5):
                window = ' '.join(sentences[i:i + 5])
                if 60 <= len(window.split()) <= 220:
                    out.append(window)
    return out


def _ngrams(sentences: list[str]) -> set:
    """3- and 4-word phrases within one clause (never across punctuation or a number)."""
    grams = set()
    for sentence in sentences:
        for clause in re.split(r"[,;:()\[\]]|\s[-\u2013]\s", sentence.lower()):
            tokens = TOKEN.findall(clause)
            for n in (3, 4):
                for i in range(len(tokens) - n + 1):
                    gram = tokens[i:i + n]
                    if (any(any(c.isdigit() for c in t) for t in gram) or gram[0] in ('and', 'or', 'but')
                            or all(t in STOP for t in gram)):
                        continue
                    grams.add(' '.join(gram))
    return grams


def _top_phrases(counts: Counter, threshold: int, limit: int = 15) -> list:
    """Most shared phrases, dropping windows that overlap a phrase already kept."""
    kept = []
    for gram, count in sorted(counts.items(), key=lambda kv: (-kv[1], -len(kv[0].split()), kv[0])):
        if count < threshold or len(kept) >= limit:
            continue
        words = gram.split()
        heads = {' '.join(words[:2]), ' '.join(words[-2:])}
        if any(gram in k or k in gram or any(h in k for h in heads) and len(set(words) & set(k.split())) >= 2
               for k, _ in kept):
            continue
        kept.append((gram, count))
    return kept


def _measure(sentences: list[str], blocks: list[str]) -> dict:
    lengths = [len(s.split()) for s in sentences]
    words = sum(lengths) or 1
    low = ' '.join(sentences).lower()
    hedges = sum(len(re.findall(r'\b' + re.escape(h) + r'\b', low)) for h in HEDGES)
    openers = Counter(' '.join(s.split()[:2]) for s in sentences if len(s.split()) > 2 and s[0].isalpha())
    transitions = Counter(t for s in sentences for t in TRANSITIONS if re.match(re.escape(t) + r'\b', s))
    ordered = sorted(lengths)
    return {
        'sentences': len(sentences), 'words': words,
        'sentence_length': {'mean': round(statistics.mean(lengths), 1) if lengths else 0,
                            'sd': round(statistics.pstdev(lengths), 1) if lengths else 0,
                            'p90': ordered[int(0.9 * (len(ordered) - 1))] if ordered else 0,
                            'p95': ordered[int(0.95 * (len(ordered) - 1))] if ordered else 0},
        'passive_pct': round(100 * sum(bool(PASSIVE.search(s)) for s in sentences) / (len(sentences) or 1)),
        'we_per_100w': round(100 * len(re.findall(r'\b(?:we|our)\b', low)) / words, 2),
        'hedges_per_100w': round(100 * hedges / words, 2),
        'paragraph_words': round(statistics.median(len(b.split()) for b in blocks)) if blocks else None,
        'openers': [[o, c] for o, c in openers.most_common(8) if c >= 2],
        'transitions': [[t, c] for t, c in transitions.most_common(6)],
    }


def learn(paths: list[Path], out: Path) -> dict:
    """Measure a corpus per section; write style_profile.json and exemplars/<section>.md into out."""
    docs, skipped = [], []
    for path in corpus_files(paths):
        try:
            sections = split_sections(clean_text(read_document(path)))
        except Exception as exc:  # unreadable or unsupported file: report it, keep going
            skipped.append(f'{path.name} ({exc})')
            continue
        short = {s: len(t.split()) for s, t in sections.items() if len(t.split()) < 80}
        skipped += [f'{path.name}: {s} ({n} words, needs 80 or more)' for s, n in short.items()]
        sections = {s: t for s, t in sections.items() if s not in short}
        if sections:
            docs.append((path, sections))
        else:
            skipped.append(f'{path.name} (no Introduction/Methods/Results/Discussion headings found)')
    profile = {'version': 1, 'learned': date.today().isoformat(), 'documents': len(docs),
               'sources': [p.name for p, _ in docs], 'skipped': skipped, 'sections': {}}
    if not docs:
        return profile  # nothing usable: keep the style learned earlier instead of overwriting it with nothing
    out.mkdir(parents=True, exist_ok=True)
    (out / 'exemplars').mkdir(exist_ok=True)
    for section in SECTIONS[1:]:
        per_doc = [(path, _sentences(parts[section]), _blocks(parts[section])) for path, parts in docs if section in parts]
        if not per_doc:
            continue
        sentences = [s for _, ss, _ in per_doc for s in ss]
        blocks = [b for _, _, bs in per_doc for b in bs]
        if len(sentences) < 5:
            continue
        entry = _measure(sentences, blocks)
        entry['documents'] = len(per_doc)
        if len(per_doc) > 1:  # shared across papers = the corpus's voice, not one paper's topic
            phrases = _top_phrases(Counter(g for _, ss, _ in per_doc for g in _ngrams(ss)), 2)
        else:
            phrases = _top_phrases(Counter(g for s in per_doc[0][1] for g in _ngrams([s])), 3)
        entry['phrases'] = [[g, c] for g, c in phrases]
        profile['sections'][section] = entry
        _write_exemplars(out / 'exemplars' / f'{section}.md', section, entry, per_doc)
    (out / 'style_profile.json').write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding='utf-8')
    return profile


def _write_exemplars(target: Path, section: str, entry: dict, per_doc) -> None:
    mean = entry['sentence_length']['mean']
    sd = entry['sentence_length']['sd'] or 1
    scored = []
    for path, _, blocks in per_doc:
        for block in blocks:
            ss = [s for s in split_sentences(block) if s.strip()]
            lengths = [len(s.split()) for s in ss]
            digits = sum(c.isdigit() for c in block) / max(len(block), 1)
            if section in ('introduction', 'discussion', 'conclusion') and digits > 0.06:
                continue
            passive = 100 * sum(bool(PASSIVE.search(s)) for s in ss) / len(ss)
            score = abs(statistics.mean(lengths) - mean) / sd + abs(passive - entry['passive_pct']) / 50
            scored.append((score, path.name, block))
    chosen, used = [], set()
    for score, name, block in sorted(scored):
        if name in used and len({n for _, n, _ in scored}) > len(used):
            continue
        chosen.append((name, block))
        used.add(name)
        if len(chosen) == 3:
            break
    lines = [f'# Model paragraphs from your corpus: {section}', '',
             'Local only (from papers you hold). Imitate rhythm and structure; never copy wording into a manuscript.', '']
    for name, block in chosen:
        lines += [f'Source: {name}', '', block, '']
    target.write_text('\n'.join(lines), encoding='utf-8')


def set_mode(value: str) -> None:
    """Save the writing mode in ~/.manuwright/config.json (what `manuwright mode` does)."""
    path = home() / 'config.json'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        data = {}
    data['writing_mode'] = value
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')


def _is_paper_root(folder: Path) -> bool:
    """A manuwright manifest, or the template layout (drafts/ next to knowledge/evidence.md or WORKFLOW.md).
    A bare drafts/ folder (say ~/drafts) is not enough."""
    manifest = folder / 'project.json'
    if manifest.is_file():
        try:
            data = json.loads(manifest.read_text(encoding='utf-8'))
            if isinstance(data, dict) and ('artifacts' in data or 'evidence' in data):
                return True
        except (OSError, ValueError):
            pass
    return (folder / 'drafts').is_dir() and ((folder / 'knowledge' / 'evidence.md').is_file()
                                             or (folder / 'WORKFLOW.md').is_file())


def in_paper(folder: Path | None) -> bool:
    """Inside a manuwright paper folder (or the template checkout)."""
    if not folder:
        return False
    try:
        folder = Path(folder).resolve()
    except OSError:
        return False
    return any(_is_paper_root(p) for p in [folder, *folder.parents])


def reminder() -> str:
    """One line re-injected on every prompt in a paper folder so the register does not drift."""
    return (f'[academic writing mode: {mode()}] Manuscript prose: plain exact clinical register; plain verbs (used, '
            'showed, found); estimate and 95% CI before p; claims sized to the design; no AI-register words or '
            '", highlighting ..." tails. Before drafting a section: manuwright style card <section>.')


# --- cards ----------------------------------------------------------------------

def core_card(project: Path | None = None) -> str:
    text = (STYLE_DIR / 'core.md').read_text(encoding='utf-8').rstrip()
    current = mode()
    profile, folder = load_profile(project)
    lines = [text, f'- Mode: {current}' + (' (a write to a manuscript section with high-severity findings is BLOCKED)'
                                           if current == 'strict' else ' (findings are reported after each edit)')]
    if profile:
        lines.append(f"- Measured style: learned from {profile.get('documents', 0)} document(s) ({folder}); the "
                     'section card shows its targets and model paragraphs.')
    else:
        lines.append('- No measured style yet: `manuwright style learn <papers>` (yours, landmark or target-journal '
                     'papers) adds your corpus to every card.')
    return '\n'.join(lines)


def _profile_block(section: str, project: Path | None) -> str:
    profile, folder = load_profile(project)
    entry = (profile.get('sections') or {}).get(section)
    if not entry:
        if profile:
            return f'\n## Your corpus\nThe learned profile ({folder}) has no {section} text.'
        return ('\n## Your corpus\nNot learned yet. `manuwright style learn <papers>` (PDF, DOCX, MD or TXT of your own, '
                'landmark or target-journal papers) adds their measured style and model paragraphs here.')
    length = entry['sentence_length']
    note = '' if enough(entry) else (f' -- too small to enforce (needs {MIN_DOCUMENTS}+ papers and {MIN_SENTENCES}+ '
                                     'sentences); the journal targets above still apply')
    out = [f"\n## Your corpus (learned from {entry.get('documents', 0)} document(s), {profile.get('learned', '')}){note}",
           f"- Sentence length: mean {length['mean']} words (SD {length['sd']}); keep under {length['p90']}.",
           f"- Passive voice in {entry['passive_pct']}% of sentences; we/our {entry['we_per_100w']} and hedges "
           f"{entry['hedges_per_100w']} per 100 words." + (f" Paragraphs about {entry['paragraph_words']} words."
                                                            if entry.get('paragraph_words') else '')]
    if entry.get('phrases'):
        out.append('- Signature phrases: ' + '; '.join(f'"{p}"' for p, _ in entry['phrases'][:12]))
    if entry.get('openers'):
        out.append('- Typical sentence openers: ' + '; '.join(f'"{o} ..."' for o, _ in entry['openers'][:6]))
    if entry.get('transitions'):
        out.append('- Transitions used: ' + ', '.join(f'{t} ({c})' for t, c in entry['transitions']))
    exemplars = folder / 'exemplars' / f'{section}.md' if folder else None
    if exemplars and exemplars.is_file():
        body = exemplars.read_text(encoding='utf-8').split('\n', 2)[-1].strip()
        if body:
            out += ['', '## Model paragraphs from your corpus', body]
    return '\n'.join(out)


def card(section: str, project: Path | None = None) -> str:
    if section not in SECTIONS:
        raise ValueError(f'unknown section {section!r}; choose from {", ".join(SECTIONS)}')
    body = (STYLE_DIR / f'{section}.md').read_text(encoding='utf-8').rstrip()
    header = (f'ACADEMIC STYLE CARD: {section} (mode {mode()}). Follow the moves and rules; imitate the model '
              'paragraphs in form only. Model paragraphs are illustrative and fictional: never reuse their facts, '
              'numbers or citations.')
    return header + '\n\n' + body + '\n' + _reference_block(section) + '\n' + _profile_block(section, project)


def _reference_block(section: str) -> str:
    ref = reference_profile()
    entry = (ref.get('overall') or {}).get(section)
    if not entry:
        return ''
    journals = ', '.join(ref.get('corpus', {}))
    out = [f"\n## Measured in high-impact journals ({sum(ref.get('corpus', {}).values())} papers: {journals}; 2019-2022)",
           f"- Sentence length: mean {entry['mean_len']} words (SD {entry['sd_len']}); 90% of sentences under "
           f"{entry['p90_len']} and 95% under {entry['p95_len']} words.",
           f"- Passive voice in {entry['passive_pct']}% of sentences; we/our {entry['we_our_per_100w']} and hedges "
           f"{entry['hedges_per_100w']} per 100 words."]
    # Only phrases with 2+ content words: "the primary outcome", not filler such as "as well as".
    phrases = [p for p in (ref.get('phrasebank') or {}).get(section) or []
               if sum(w not in STOP for w in p.split()) >= 2]
    if phrases:
        out.append('- Phrasing shared across these journals (4+ papers, 3+ journals): '
                   + '; '.join(f'"{p}"' for p in phrases[:18]))
    return '\n'.join(out)


# --- learning from the author's edits --------------------------------------------------
# Idea from writing-style-skill / voice-learn: the author's own corrections of an AI draft are the
# most specific style signal there is. Reimplemented: word-level diff, counted across files, proposed
# as pending rules that the author ticks before they reach Style/terminology.md.

EDIT_TOKEN = re.compile(r"\[EVID:[^\]]+\]|[A-Za-z][A-Za-z'\-]*|\d+(?:\.\d+)?|[^\sA-Za-z\d]")


def _words(text: str) -> list[str]:
    return EDIT_TOKEN.findall(text)


def edit_changes(before: str, after: str) -> tuple[Counter, Counter]:
    """(substitutions 'old -> new', deletions) of up to 3 words, ignoring numbers and citations."""
    import difflib
    a, b = _words(before), _words(after)
    subs, dels = Counter(), Counter()
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes():
        old, new = ' '.join(a[i1:i2]), ' '.join(b[j1:j2])
        if any(t[:1].isdigit() or t.startswith('[EVID') for t in a[i1:i2] + b[j1:j2]):
            continue
        if op == 'replace' and i2 - i1 <= 3 and j2 - j1 <= 3 and old.lower() != new.lower():
            lo, ln = old.lower(), new.lower()
            if lo.endswith(' ' + ln) or lo.startswith(ln + ' '):  # "notably , the" -> "the": a deletion
                dels[(lo[:-len(ln)] if lo.endswith(' ' + ln) else lo[len(ln):]).strip(' ,;:')] += 1
            else:
                subs[f'{lo} -> {ln}'] += 1
        elif op == 'delete' and i2 - i1 <= 2 and re.search('[A-Za-z]', old):
            dels[old.lower()] += 1
    return subs, dels


def _section_pairs(before: Path, after: Path) -> list[tuple[str, str]]:
    if before.is_file():
        return [(before.read_text(encoding='utf-8', errors='replace'), after.read_text(encoding='utf-8', errors='replace'))]
    olds = {p.name: p for p in before.rglob('*.md')}
    return [(olds[p.name].read_text(encoding='utf-8', errors='replace'), p.read_text(encoding='utf-8', errors='replace'))
            for p in sorted(after.rglob('*.md')) if p.name in olds]


def _git_pairs(rev: str, folder: Path) -> list[tuple[str, str]]:
    top = subprocess.run(['git', 'rev-parse', '--show-toplevel'], capture_output=True, text=True, encoding='utf-8',
                         errors='replace', cwd=str(folder if folder.is_dir() else Path.cwd()))
    if top.returncode != 0:
        raise RuntimeError(f'{folder} is not inside a git repository; compare two files or folders instead')
    root = Path(top.stdout.strip()).resolve()
    known = subprocess.run(['git', 'rev-parse', '--verify', '--quiet', f'{rev}^{{commit}}'], capture_output=True,
                           text=True, encoding='utf-8', errors='replace', cwd=str(root))
    if known.returncode != 0:
        raise RuntimeError(f'"{rev}" is not a commit in this repository (try HEAD~1, a commit id from `git log`, '
                           'or compare two files instead)')
    pairs = []
    for path in sorted(folder.rglob('0[1-9]_*.md')):
        try:
            rel = path.resolve().relative_to(root).as_posix()  # git show wants a path from the repository root
        except ValueError:
            continue
        done = subprocess.run(['git', 'show', f'{rev}:{rel}'], capture_output=True, text=True, encoding='utf-8',
                              errors='replace', cwd=str(root))
        if done.returncode == 0:
            pairs.append((done.stdout, path.read_text(encoding='utf-8', errors='replace')))
    return pairs


def edit_proposals(pairs: list[tuple[str, str]]) -> list[tuple[str, str, int, str]]:
    """[(priority, rule, count, kind)]: P0 seen 2+ times, P1 once but an AI-register word, P2 once."""
    subs, dels = Counter(), Counter()
    for before, after in pairs:
        s, d = edit_changes(before, after)
        subs.update(s)
        dels.update(d)
    flagged = re.compile('|'.join(p.pattern for sev, _c, p, _m in PHRASE_RULES if _c in ('AI_PHRASE', 'AI_WORD')), _I)
    out = []
    for kind, counter in (('replace', subs), ('delete', dels)):
        for rule, count in counter.most_common():
            old = rule.split(' -> ')[0]
            ai_ish = flagged.search(old) or old.strip(' ,') in INFLATED
            priority = 'P0' if count >= 2 else 'P1' if ai_ish else 'P2'
            out.append((priority, rule, count, kind))
    return sorted(out, key=lambda r: (r[0], -r[2], r[1]))


# Signposts and inflated verbs that the reference corpus rarely uses (core card, reference_profile.json).
INFLATED = {'notably', 'importantly', 'interestingly', 'remarkably', 'crucially', 'utilize', 'utilized', 'utilizes',
            'utilizing', 'demonstrated', 'exhibited', 'furthermore', 'moreover', 'additionally'}
PENDING = Path('Style') / 'pending_style_rules.md'
LEARNED_HEADER = ('\n## Learned From Author Edits\n\nRules the author approved in Style/pending_style_rules.md '
                  '(`manuwright style edits --apply`).\n\n| Preferred Term | Forbidden Terms | Context |\n|---|---|---|\n')


def _rule_key(line: str) -> str:
    """'replace "a" with "b"' or 'delete "a"' from a pending-rule line, lowercased."""
    m = re.search(r'(replace ".+?" with ".+?"|delete ".+?")', line)
    return m.group(1).lower() if m else line.strip().lower()


def write_pending(proposals: list, target: Path) -> None:
    lines = ['# Pending style rules from your edits', '',
             'Learned from how you edited AI drafts. Tick (`[x]`) only the rules you want enforced, or tell your',
             'agent in chat which ones to keep; then `manuwright style edits --apply`. An agent never decides for you.', '',
             'P0 = you made this change 2+ times; P1 = once, and the old wording is AI register; P2 = once.', '']
    # A rerun merges: rules already listed keep their tick and chat-approval note, so nothing the author
    # approved is lost before `--apply`; only rules not yet listed are added.
    kept = [ln for ln in (target.read_text(encoding='utf-8').splitlines() if target.is_file() else [])
            if re.match(r'\s*-\s*\[[ xX]\]', ln)]
    listed = {_rule_key(ln) for ln in kept}
    lines += kept
    for priority, rule, count, kind in proposals:
        text = f'replace "{rule.split(" -> ")[0]}" with "{rule.split(" -> ")[1]}"' if kind == 'replace' else f'delete "{rule}"'
        if text.lower() not in listed:
            lines.append(f'- [ ] {priority} {text} ({count}x)')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('\n'.join(lines) + '\n', encoding='utf-8')


def approve_pending(pending: Path, rules: list[str], approved_by: str, quote: str) -> list[str]:
    """Tick the rules the author approved in chat (like `manuwright approve` for plans); returns the lines ticked."""
    lines, ticked = pending.read_text(encoding='utf-8').splitlines(), []
    wanted = {re.sub(r'\s+', ' ', r.strip().strip('"').lower()) for r in rules} - {''}
    for i, line in enumerate(lines):
        if not line.lstrip().startswith('- [ ]'):
            continue
        # Exact match only: the old wording ("demonstrated"), "old -> new", or the rule as written.
        # A substring match would let "used" tick 'replace "caused by" ...'.
        terms = re.findall(r'"([^"]+)"', line)
        rule = re.sub(r'^\s*-\s*\[ \]\s*P\d\s*|\s*\(\d+x\)\s*$', '', line).lower()
        names = {t.lower() for t in terms[:1]} | {rule}
        if len(terms) >= 2:
            names.add(f'{terms[0]} -> {terms[1]}'.lower())
        if wanted & names:
            lines[i] = line.replace('- [ ]', '- [x]', 1) + f'  <!-- approved by {approved_by} in chat: "{quote}" -->'
            ticked.append(lines[i])
    pending.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    return ticked


def apply_pending(pending: Path, terminology: Path) -> list[str]:
    """Append the ticked rules to the paper's terminology registry (lint enforces them from then on).
    Rules already in the registry are skipped, and applied lines are marked so a rerun adds nothing."""
    rows = []
    text = terminology.read_text(encoding='utf-8') if terminology.is_file() else '# Terminology\n'
    lines = pending.read_text(encoding='utf-8').splitlines()
    for i, line in enumerate(lines):
        m = re.match(r'-\s*\[[xX]\]\s*P\d\s+(?:replace "(.+?)" with "(.+?)"|delete "(.+?)")', line.strip())
        if m and '(applied)' not in line:
            old, new = (m.group(1), m.group(2)) if m.group(1) else (m.group(3), '(delete)')
            row = f'| {new} | {old} | learned from author edits |'
            if row not in text and row not in rows:
                rows.append(row)
            lines[i] = line + ' (applied)'
    pending.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    if rows:
        if '## Learned From Author Edits' not in text:
            text = text.rstrip('\n') + '\n' + LEARNED_HEADER
        terminology.parent.mkdir(parents=True, exist_ok=True)
        terminology.write_text(text.rstrip('\n') + '\n' + '\n'.join(rows) + '\n', encoding='utf-8')
    return rows


# --- command line -------------------------------------------------------------------

def default_sources() -> list[Path]:
    pdf = home() / 'library' / 'writing' / 'PDF'
    return [pdf] if pdf.is_dir() else []


def _main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    parser = argparse.ArgumentParser(prog='manuwright style', description='Academic writing mode: cards, learned style, checks')
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('core', help='the always-on card')
    c = sub.add_parser('card', help='the card for one section')
    c.add_argument('section', type=section_name, help=', '.join(SECTIONS) + ' (or 제목, 초록, 서론, 방법, 결과, 고찰, 결론)')
    c.add_argument('--project', default='.')
    lr = sub.add_parser('learn', help='measure a corpus of good papers (PDF, DOCX, MD, TXT)')
    lr.add_argument('paths', nargs='*')
    lr.add_argument('--out', help=f'profile folder (default {library_profile_dir()})')
    ck = sub.add_parser('check', help='academic-prose findings for manuscript files')
    ck.add_argument('files', nargs='+')
    ck.add_argument('--strict', action='store_true', help='fail on medium findings too')
    sub.add_parser('status', help='writing mode and learned profile')
    pv = sub.add_parser('preserve', help='did a rewrite keep every citation, number, p value and table/figure reference?')
    pv.add_argument('before')
    pv.add_argument('after')
    ed = sub.add_parser('edits', help="learn rules from how the author edited AI drafts")
    ed.add_argument('before', nargs='?', help='AI draft file or folder')
    ed.add_argument('after', nargs='?', help='author-edited file or folder')
    ed.add_argument('--git', metavar='REV', help='compare drafts/ section files at REV with the working tree')
    ed.add_argument('--folder', default='drafts')
    ed.add_argument('--apply', action='store_true', help='move ticked rules from Style/pending_style_rules.md '
                                                         'into Style/terminology.md')
    ed.add_argument('--approve', action='append', default=[], metavar='RULE',
                    help='tick a rule the author approved in chat (e.g. "demonstrated"); needs --approved-by and --quote')
    ed.add_argument('--approved-by')
    ed.add_argument('--quote', help="the author's exact words")
    args = parser.parse_args(argv)

    if args.action == 'edits':
        if args.approve:
            if not (args.approved_by and args.quote) or not PENDING.is_file():
                print('usage: manuwright style edits --approve RULE --approved-by NAME --quote "their words" '
                      '(after `manuwright style edits` wrote Style/pending_style_rules.md)', file=sys.stderr)
                return 2
            ticked = approve_pending(PENDING, args.approve, args.approved_by, args.quote)
            print(f'Ticked {len(ticked)} rule(s) the author approved; run `manuwright style edits --apply`.')
            if not args.apply:
                return 0
        if args.apply:
            if not PENDING.is_file():
                print(f'No {PENDING}; run `manuwright style edits` first.', file=sys.stderr)
                return 2
            import library_sync  # the paper's registry (project.json "terminology"), seeded from the engine's
            root = library_sync.paper_root(Path.cwd()) or Path.cwd()
            registry = library_sync.paper_terminology(root)
            waiting = [l for l in PENDING.read_text(encoding='utf-8').splitlines()
                       if re.match(r'-\s*\[[xX]\]\s*P\d', l.strip()) and '(applied)' not in l]
            if waiting:  # nothing ticked: create nothing
                library_sync.seed_registry(registry)
            rows = apply_pending(PENDING, registry)
            if rows:
                library_sync._declare(root, 'terminology', registry)
            shown = registry.relative_to(root).as_posix() if registry.is_relative_to(root) else registry
            print(f'Added {len(rows)} approved rule(s) to {shown}.' if rows
                  else f'Nothing new to apply: no ticked rules, or they are already in {shown}.')
            if rows and library_sync.sync_mode() != 'off':
                # what the author taught in this paper reaches every later paper
                learned = {}
                for row in rows:
                    new_word, old_word = [c.strip() for c in row.strip('|').split('|')[:2]]
                    learned[old_word.lower()] = (new_word, old_word, 'learned from author edits')
                added, conflicts = library_sync.add_rules(library_sync.library_terminology(), learned,
                                                          'learned from author edits')
                if added:
                    print(f'Also kept in your personal library ({library_sync.library_terminology()}): {", ".join(added)}')
                for conflict in conflicts:
                    print(f'Library not changed for {conflict}; ask the author which to keep.')
            return 0
        if args.git:
            try:
                pairs = _git_pairs(args.git, Path(args.folder))
            except RuntimeError as exc:
                print(f'error: {exc}', file=sys.stderr)
                return 1
        elif args.before and args.after:
            pairs = _section_pairs(Path(args.before), Path(args.after))
        else:
            print('usage: manuwright style edits <ai_draft> <edited> | --git REV [--folder drafts] | --apply',
                  file=sys.stderr)
            return 2
        proposals = edit_proposals(pairs)
        if not proposals:
            print(f'No word-level edits found in {len(pairs)} section pair(s).')
            return 0
        write_pending(proposals, PENDING)
        for priority, rule, count, kind in proposals[:25]:
            print(f'{priority} {kind:<7} {rule} ({count}x)')
        print(f'{len(proposals)} proposal(s) written to {PENDING}. Show them to the author. They tick what to keep, '
              'or approve in chat and you run `manuwright style edits --approve "<rule>" --approved-by "<name>" '
              '--quote "<their words>" --apply`.')
        return 0

    if args.action == 'preserve':
        read = lambda name: Path(name).read_text(encoding='utf-8', errors='replace')  # noqa: E731
        problems = preserve_problems(read(args.before), read(args.after))
        for problem in problems:
            print(f'CHANGED: {problem}')
        print('FAIL: the rewrite changed protected content; restore it.' if problems
              else 'OK: every [EVID:id], number, p value and table/figure reference is unchanged.')
        return 1 if problems else 0

    if args.action == 'core':
        print(core_card(Path.cwd()))
        return 0
    if args.action == 'card':
        print(card(args.section, Path(args.project).resolve()))
        return 0
    if args.action == 'status':
        profile, folder = load_profile(Path.cwd())
        print(f'Writing mode: {mode()} (change: manuwright mode academic|strict|off)')
        if profile:
            print(f"Learned style: {profile.get('documents')} document(s), {profile.get('learned')}, {folder}")
            print('  sections: ' + ', '.join(f"{s} ({e['sentences']} sentences)" for s, e in profile['sections'].items()))
        else:
            print('Learned style: none (manuwright style learn <papers>)')
        return 0
    if args.action == 'learn':
        paths = [Path(p).expanduser() for p in args.paths] or default_sources()
        if not paths:
            print('No papers given, and your manuwright library has no PDFs yet.\n'
                  'Put 3 or more papers (PDF, DOCX, MD or TXT) in one folder and run:\n'
                  '  manuwright style learn <that folder>\n'
                  'Good choices: your own published papers, landmark papers in your field, recent papers from the '
                  'target journal. Or add them to your library once: manuwright library writing add <files>.',
                  file=sys.stderr)
            return 2
        out = Path(args.out).expanduser() if args.out else library_profile_dir()
        try:
            profile = learn(paths, out)
        except RuntimeError as exc:
            print(f'error: {exc}', file=sys.stderr)
            return 1
        for line in profile['skipped']:
            print(f'skipped {line}')
        if not profile['documents']:
            print('No usable papers found (each needs section headings such as Introduction, Methods, Results, '
                  'Discussion).', file=sys.stderr)
            return 1
        print(f"Learned from {profile['documents']} document(s) -> {out}")
        for section, entry in profile['sections'].items():
            length = entry['sentence_length']
            print(f"  {section:<13} {entry['sentences']:>4} sentences, mean {length['mean']} words, "
                  f"passive {entry['passive_pct']}%, {len(entry.get('phrases', []))} signature phrases"
                  + ('' if enough(entry) else '  (too few to enforce; shown on cards only)'))
        if profile['documents'] < MIN_DOCUMENTS:
            print(f'Note: {MIN_DOCUMENTS} or more papers are needed before your style changes any check; '
                  'until then the journal targets apply.')
        print('Every section card now includes this measured style (manuwright style card <section>).')
        return 0
    failed = 0
    # a folder means its manuscript files (plans are not prose to check)
    paths = [q for f in args.files for q in (sorted(x for x in Path(f).rglob('*.md') if not x.name.endswith('_plan.md'))
                                             if Path(f).is_dir() else [Path(f)])]
    for path in paths:
        section = section_of(path)
        issues = prose_issues(path.read_text(encoding='utf-8', errors='replace'), section,
                              long_limit_for(section, Path.cwd()))
        for severity, code, line, message in issues:
            print(f'[{severity.upper()}/{code}] {path}:{line} {message}')
        failed += sum(1 for s, *_ in issues if s == HIGH or args.strict)
    print('FAIL' if failed else 'OK', f'({failed} blocking finding(s))' if failed else '')
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    try:
        return _main(argv)
    except FileNotFoundError as exc:  # a mistyped path: a one-line message, not a traceback
        print(f'error: file not found: {exc.filename}', file=sys.stderr)
        return 2
    except ValueError as exc:  # e.g. a duplicate Evidence ID in evidence.md
        print(f'error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())

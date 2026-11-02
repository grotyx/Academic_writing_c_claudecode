"""Tracked-changes DOCX for a revision: the previous submission against the revised text, as Word revisions.

Blocks (headings and prose paragraphs, the subset the clean compiler supports) are compared in order. An
unchanged block is plain text; a removed block is a deleted paragraph and an added block an inserted one
(w:del / w:ins, author ManuWright), so "Accept all changes" in Word gives the revised manuscript and
"Reject all changes" the previous one. A changed paragraph shows as the old one deleted and the new one
inserted. Tables are refused: separately built tables are not part of the main manuscript, and tracking a
changed table as text would not be faithful.
"""
from __future__ import annotations

import difflib
import re
from datetime import datetime, timezone

AUTHOR = 'ManuWright'


def blocks(text: str) -> list[str]:
    """Markdown -> ['# Heading', 'paragraph text', ...] (lines of one paragraph joined with a space)."""
    text = re.sub(r'<!--.*?-->', '', text, flags=re.S)
    if '```' in text or '$$' in text or '![' in text:
        raise ValueError('tracked changes support prose and headings only (no code, display math or images)')
    out, prose = [], []
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith('|'):
            raise ValueError('tracked changes do not cover tables: tables are built as separate files; compare '
                             'them separately')
        if not line or line == '---' or re.match(r'^#{1,6}\s+', line):
            if prose:
                out.append(' '.join(prose))
                prose = []
            if line and line != '---':
                out.append(line)
            continue
        if line.startswith('- ') and prose:
            out.append(' '.join(prose))
            prose = []
        prose.append(line)
    if prose:
        out.append(' '.join(prose))
    return out


def _paragraph(doc, block, style):
    """One block as the clean compiler writes it (headings bold, ### italic; prose with inline markup)."""
    from docx.shared import Pt
    from .build import inline
    match = re.match(r'^(#{1,6})\s+(.+)', block)
    if match:
        level = min(len(match.group(1)), 2)
        if style.get('reference') and f'Heading {level}' in [s.name for s in doc.styles]:
            return doc.add_paragraph(match.group(2), style=f'Heading {level}')
        paragraph = doc.add_paragraph()
        run = paragraph.add_run(match.group(2))
        run.bold, run.italic = True, level > 1
        size = style.get('heading_size' if level == 1 else 'subheading_size')
        if size:
            run.font.size = Pt(size)
        return paragraph
    paragraph = doc.add_paragraph()
    inline(paragraph, block)
    return paragraph


def _mark(paragraph, kind, ident, date):
    """Wrap every run in w:ins or w:del and mark the paragraph mark too, so accept/reject joins cleanly."""
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    p = paragraph._p
    for run in list(p.findall(qn('w:r'))):
        wrapper = OxmlElement('w:' + kind)
        wrapper.set(qn('w:id'), str(next(ident)))
        wrapper.set(qn('w:author'), AUTHOR)
        wrapper.set(qn('w:date'), date)
        run.addprevious(wrapper)
        wrapper.append(run)
        if kind == 'del':
            for t in run.findall(qn('w:t')):
                t.tag = qn('w:delText')
    ppr = p.get_or_add_pPr()
    rpr = ppr.find(qn('w:rPr'))
    if rpr is None:
        rpr = OxmlElement('w:rPr')
        ppr.append(rpr)
    mark = OxmlElement('w:' + kind)
    mark.set(qn('w:id'), str(next(ident)))
    mark.set(qn('w:author'), AUTHOR)
    mark.set(qn('w:date'), date)
    rpr.append(mark)


def tracked_docx(old_text: str, new_text: str, out, style=None) -> dict:
    """Write the tracked DOCX; returns {'kept', 'inserted', 'deleted'} block counts."""
    import itertools
    from .build import DOCX_DEFAULTS, document
    style = style or DOCX_DEFAULTS
    old, new = blocks(old_text), blocks(new_text)
    doc = document(style)
    date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    ident = itertools.count(1)
    counts = {'kept': 0, 'inserted': 0, 'deleted': 0}
    for op, a1, a2, b1, b2 in difflib.SequenceMatcher(a=old, b=new, autojunk=False).get_opcodes():
        if op == 'equal':
            for block in new[b1:b2]:
                _paragraph(doc, block, style)
            counts['kept'] += b2 - b1
            continue
        for block in old[a1:a2]:
            _mark(_paragraph(doc, block, style), 'del', ident, date)
        for block in new[b1:b2]:
            _mark(_paragraph(doc, block, style), 'ins', ident, date)
        counts['deleted'] += a2 - a1
        counts['inserted'] += b2 - b1
    doc.save(out)
    return counts


def resolved_text(path, accept: bool) -> list[str]:
    """The paragraphs Word shows after Accept all (accept=True) or Reject all: for checking a tracked file."""
    from docx import Document
    from docx.oxml.ns import qn
    drop, keep = ('w:del', 'w:ins') if accept else ('w:ins', 'w:del')
    paragraphs = []
    for p in Document(path).element.body.iter(qn('w:p')):
        rpr = p.find(qn('w:pPr') + '/' + qn('w:rPr'))
        if rpr is not None and rpr.find(qn(drop)) is not None:
            continue  # the paragraph itself was removed
        parts = []
        for node in p.iter():
            if node.tag in (qn('w:t'), qn('w:delText')):
                inside_drop = any(a.tag == qn(drop) for a in node.iterancestors())
                if not inside_drop:
                    parts.append(node.text or '')
        paragraphs.append(''.join(parts))
    return [p for p in paragraphs if p.strip()]

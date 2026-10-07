"""Plan completeness and content-bound approval receipts (stdlib only).

Receipts record a human decision; they are provenance, not authentication.
"""
from __future__ import annotations
import hashlib
import json
import re
from pathlib import Path

DRAFT_SECTIONS = (
    r'key message|핵심 메시지', r'tone.*voice|논조', r'essential references|필수.*문헌',
    r'evidence gap|근거.*갭', r'claim.*citation|주장.*인용', r'table.*figure|표.*그림',
    r'introduction outline|서론.*개요', r'discussion outline|고찰.*개요',
    r'limitation|한계',
)
ANALYSIS_SECTIONS = (
    r'research question|연구 질문', r'study population|대상.*기준',
    r'variable definitions|변수 정의|endpoints', r'statistical methods|통계.*방법|통계.*검정',
    r'significance.*multiple|유의수준|multiplicity', r'missing data|결측',
)
SECTION_NAMES = {
    r'key message|핵심 메시지': 'Key message (핵심 메시지)', r'tone.*voice|논조': 'Tone & voice (논조)',
    r'essential references|필수.*문헌': 'Essential references (필수 참고문헌)',
    r'evidence gap|근거.*갭': 'Evidence gap (근거 갭; write "None" if there is none)',
    r'claim.*citation|주장.*인용': 'Claim -> citation mapping (주장-인용 매핑)',
    r'table.*figure|표.*그림': 'Table/Figure plan (표·그림 계획)', r'introduction outline|서론.*개요': 'Introduction outline (서론 개요)',
    r'discussion outline|고찰.*개요': 'Discussion outline (고찰 개요)', r'limitation|한계': 'Limitations (한계점)',
    r'research question|연구 질문': 'Research question (연구 질문)', r'study population|대상.*기준': 'Study population (대상 기준)',
    r'variable definitions|변수 정의|endpoints': 'Variable definitions / endpoints (변수 정의)',
    r'statistical methods|통계.*방법|통계.*검정': 'Statistical methods (통계 방법)',
    r'significance.*multiple|유의수준|multiplicity': 'Significance and multiplicity (유의수준·다중비교)',
    r'missing data|결측': 'Missing data (결측 처리)',
}
NONE_ALLOWED = (r'evidence gap|근거.*갭',)
NONE_ANSWER = re.compile(r'^\s*(?:none|n/?a|없음|해당\s*없음)\.?\s*$', re.I)


def describe_missing(patterns: list[str]) -> str:
    """Readable names for the sections validate_plan_content reported as missing or empty."""
    return '; '.join(SECTION_NAMES.get(p, p) for p in patterns)


PLACEHOLDER = re.compile(r'\[(?:TODO|TBD|작성|입력|정의|specify|None /)[^\]]*\]', re.I)


def validate_plan_content(text: str, kind: str) -> list[str]:
    text = re.sub(r'<!--.*?-->|```.*?```', '', text, flags=re.S)
    headings = list(re.finditer(r'^#{2,3}\s+(.+)$', text, re.M))
    sections = []
    for i, match in enumerate(headings):
        # Include subheadings' content up to the next heading of same/higher level.
        level = len(match.group(0)) - len(match.group(0).lstrip('#'))
        end = len(text)
        for later in headings[i+1:]:
            later_level = len(later.group(0)) - len(later.group(0).lstrip('#'))
            if later_level <= level:
                end = later.start(); break
        lines = [line for line in text[match.end():end].splitlines()
                 # an unticked template option ("- [ ] ...") is not content; a ticked one or "- [EVID:..]" is
                 if line.strip() and not line.lstrip().startswith(('>', '#', '<!--'))
                 and not re.match(r'\s*[-*]\s*\[\s\]', line)]
        body = '\n'.join(lines)
        sections.append((match.group(1), body))
    required = ANALYSIS_SECTIONS if kind == 'analysis' else DRAFT_SECTIONS
    missing = []
    for pattern in required:
        matches = [body for heading, body in sections if re.search(pattern, heading, re.I)]
        if not any((len(re.sub(r'[\W_]+', '', body)) >= 8 or (pattern in NONE_ALLOWED and NONE_ANSWER.match(body)))
                   and not PLACEHOLDER.search(body) for body in matches):
            missing.append(pattern)
    return missing


def plan_hash(plan: Path) -> str:
    return hashlib.sha256(plan.read_bytes()).hexdigest()


def approval_problem(plan: Path, *, required: bool = False) -> str | None:
    receipt = plan.with_suffix('.approval.json')
    if not receipt.exists():
        return 'missing approval receipt' if required else None
    try:
        data = json.loads(receipt.read_text(encoding='utf-8'))
        if data.get('status') != 'approved' or not data.get('approved_by') or not data.get('decision_reference'):
            return 'incomplete approval receipt'
        if data.get('sha256') != plan_hash(plan):
            return 'stale approval: plan changed after approval'
    except (OSError, ValueError, AttributeError):
        return 'invalid approval receipt'
    return None

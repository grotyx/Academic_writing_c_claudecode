"""Journal reference presets: author cutoffs, page/issue/DOI forms, grouped markers, DOCX superscript."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


js = load('journal_styles')
fr = load('format_references')

META = {'authors': [['Nakarai', 'H', 'Hiroyuki'], ['Kato', 'S', 'So'], ['Kawamura', 'N', 'Naohiro'],
                    ['Higashikawa', 'A', 'Akiro'], ['Takeshita', 'Y', 'Yujiro'], ['Fukushima', 'M', 'Masayoshi'],
                    ['Ono', 'T', 'Takashi'], ['Park', 'SM', 'Sang-Min']],
        'complete': True, 'title': 'Minimal clinically important difference.', 'journal': 'Spine J', 'year': '2022',
        'month': 'Apr', 'volume': '22', 'issue': '4', 'pages': '549-560', 'doi': '10.1016/j.spinee.2021.10.010'}


@pytest.mark.parametrize('journal,expected', [
    ('nejm', 'Nakarai H, Kato S, Kawamura N, et al. Minimal clinically important difference. Spine J 2022;22:549-60.'),
    ('spine', 'Nakarai H, Kato S, Kawamura N, et al. Minimal clinically important difference. Spine J 2022;22:549-60.'),
    ('lancet', 'Nakarai H, Kato S, Kawamura N, et al. Minimal clinically important difference. *Spine J* 2022; 22: 549–60.'),
    ('ama', 'Nakarai H, Kato S, Kawamura N, et al. Minimal clinically important difference. *Spine J*. 2022;22(4):549-560. doi:10.1016/j.spinee.2021.10.010'),
    ('spine-j', 'Nakarai H, Kato S, Kawamura N, Higashikawa A, Takeshita Y, Fukushima M, et al. Minimal clinically important difference. Spine J. 2022;22:549–560.'),
    ('neurospine', 'Nakarai H, Kato S, Kawamura N, et al. Minimal clinically important difference. Spine J. 2022;22(4):549–560. https://doi.org/10.1016/j.spinee.2021.10.010'),
    ('esj', 'Nakarai H, Kato S, Kawamura N, Higashikawa A, Takeshita Y, Fukushima M, Ono T, Park SM (2022) Minimal clinically important difference. Spine J 22:549–560. https://doi.org/10.1016/j.spinee.2021.10.010'),
])
def test_presets(journal, expected):
    assert js.render(META, js.STYLES[journal]) == expected


def test_jbjs_lists_every_author_with_month_and_bjj_hyphenates_initials():
    assert js.render(META, js.STYLES['jbjs']).endswith('Ono T, Park SM. Minimal clinically important difference. Spine J. 2022 Apr;22(4):549-60.')
    few = dict(META, authors=META['authors'][-2:])
    assert js.render(few, js.STYLES['bjj']).startswith('Ono T, Park S-M. ')


def test_citation_fallback_and_incomplete_author_list():
    meta = js.from_citation('Nakarai H, Kato S, Kawamura N, Higashikawa A, Takeshita Y, Fukushima M, et al. '
                            'Minimal clinically important difference. Spine J. 2022;22(4):549-560.')
    assert meta['complete'] is False and len(meta['authors']) == 6 and meta['issue'] == '4'
    assert js.render(meta, js.STYLES['nejm']).startswith('Nakarai H, Kato S, Kawamura N, et al.')
    assert js.from_citation('not a vancouver string') is None


EVIDENCE = """# Evidence

### [1] Zed 2020
- **Evidence ID:** zed_2020
- **Citation:** Zed A, Young B. Later trial. Spine. 2020;45(1):1-9.
- **Source Status:** verified

### [2] Adams 2019
- **Evidence ID:** adams_2019
- **Citation:** Adams C, Brown D, Clark E, Dunn F, Evans G, Ford H, et al. Earlier cohort. Spine J. 2019;19(2):100-110.
- **Source Status:** verified
"""


def test_build_groups_markers_orders_and_flags(tmp_path):
    evidence = tmp_path / 'evidence.md'
    evidence.write_text(EVIDENCE, encoding='utf-8')
    draft = tmp_path / 'intro.md'
    draft.write_text('Claim [EVID:zed_2020] [EVID:adams_2019].\n', encoding='utf-8')
    nejm = fr.build([draft], evidence_path=evidence, style='numbered', journal='nejm')
    assert fr.convert_text(draft.read_text(), nejm.labels, nejm.in_text) == 'Claim ^1,2^.\n'
    assert nejm.incomplete_authors == []  # NEJM cuts at 3 anyway
    corr = fr.build([draft], evidence_path=evidence, style='numbered', journal='corr')
    assert corr.order == ['adams_2019', 'zed_2020'] and fr.convert_text('[EVID:adams_2019]', corr.labels, 'bracket') == '[1]'
    jbjs = fr.build([draft], evidence_path=evidence, style='numbered', journal='jbjs')
    assert jbjs.incomplete_authors == ['adams_2019']  # JBJS wants every author; the stored string stops at 6
    cache = {'1': js.from_citation('Adams C, Brown D, Clark E, Dunn F, Evans G, Ford H, Gray I. Earlier cohort. '
                                   'Spine J. 2019;19(2):100-110.')}
    evidence.write_text(EVIDENCE.replace('- **Evidence ID:** adams_2019', '- **Evidence ID:** adams_2019\n- **PMID:** 1'))
    (tmp_path / 'reference_metadata.json').write_text(json.dumps(cache))
    jbjs = fr.build([draft], evidence_path=evidence, style='numbered', journal='jbjs')
    assert jbjs.incomplete_authors == [] and 'Ford H, Gray I.' in jbjs.references[1]


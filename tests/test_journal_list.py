"""Your journal list: rules, detection from your papers, add/remove, setup step (no network)."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import journal_fit as jf  # noqa: E402
import journal_list as jl  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_home(tmp_path_factory, monkeypatch):
    monkeypatch.setenv('MANUWRIGHT_HOME', str(tmp_path_factory.mktemp('lhome')))
    monkeypatch.setattr(jl.time, 'sleep', lambda s: None)
    monkeypatch.setattr(jl, 'resolve_ta', lambda row, cache: ABBR.get(row['issn'], ''))


def row(n, title, issn, top, rank, other=''):
    return (f'<td>{n}</td> <td>{title}</td> <td>{issn}</td> <td>{issn}X</td><td><p>5.0</p></td>'
            f'<td><button>{top}</button></td><td>{rank}</td><td>{other}<br></td> <td>PUB</td><td>Monthly</td> </tr>')


PAGE = '\n'.join([
    row(1, 'SPINE JOURNAL', '1529-9430', 'ORTHOPEDICS', 9.88, 'CLINICAL NEUROLOGY : 20.1'),
    row(2, 'JOURNAL OF NEUROSURGERY', '0022-3085', 'CLINICAL NEUROLOGY', 33.57),
    row(3, 'LANCET NEUROLOGY', '1474-4422', 'CLINICAL NEUROLOGY', 0.23),
    row(4, 'JOURNAL OF PHYSIOTHERAPY', '1836-9553', 'REHABILITATION', 1.2, 'ORTHOPEDICS : 1.74'),
    row(5, 'JOURNAL OF UROLOGY', '0022-5347', 'UROLOGY & NEPHROLOGY', 12),
    row(6, 'JOURNAL OF CRANIO-MAXILLOFACIAL SURGERY', '1010-5182', 'SURGERY', 49.7, 'DENTISTRY, ORAL SURGERY & MEDICINE : 30'),
    row(7, 'WORLD NEUROSURGERY', '1878-8750', 'SURGERY', 70.0, 'CLINICAL NEUROLOGY : 72'),
])
ABBR = {'1529-9430': 'Spine J', '0022-3085': 'J Neurosurg', '1836-9553': 'J Physiother', '0022-5347': 'J Urol',
        '1474-4422': 'Lancet Neurol', '1010-5182': 'J Craniomaxillofac Surg', '1878-8750': 'World Neurosurg'}


def args(**kw):
    base = dict(import_file=None, build=True, auto=False, preset=None, category=[], exclude=None, group=[], top=None,
                categories=None, add=None, remove=None, source='https://site', from_html=None, replace=True,
                send_pmids=True)
    base.update(kw)
    parsed = argparse.Namespace(**base)
    jl.finish_arguments(parsed)
    return parsed


def test_presets_categories_title_words_exclusions_and_groups():
    rows = jl.site_rows(PAGE)
    assert len(rows) == 7 and rows[0]['cats'] == {'ORTHOPEDICS': '9.88', 'CLINICAL NEUROLOGY': '20.1'}
    count, message = jl.build({**jl.PRESETS['ortho-neuro'], 'label': 'ortho-neuro'}, PAGE)
    listed = jl.my_list()
    assert count == 3 and set(listed) == {'spinej', 'jneurosurg', 'jphysiother'}  # neurology and >50% left out
    assert listed['spinej']['group'] == 'Spine' and listed['jneurosurg']['group'] == 'Neurosurgery'
    assert listed['jphysiother']['group'] == 'Orthopedics'
    assert jl.saved_settings()['rules'][0] == 'ORTHOPEDICS'
    jl.build({'rules': ['SURGERY', 'UROLOGY & NEPHROLOGY'], 'exclude': ['maxillofacial'], 'top': 80,
              'groups': ['Neurosurgery=neurosurg']}, PAGE, replace=True)
    listed = jl.my_list()
    assert set(listed) == {'worldneurosurg', 'jurol'} and listed['worldneurosurg']['group'] == 'Neurosurgery'
    assert jl.list_path().with_name('list.md.bak').is_file()  # the earlier list is kept
    count, message = jl.build({'rules': ['UROLOGY']}, PAGE, replace=True)
    assert count == 0 and 'did you mean UROLOGY & NEPHROLOGY?' in message


def test_field_is_detected_from_the_journals_you_cite_and_target():
    weights = Counter({('1529-9430', ''): 6, ('0022-3085', ''): 3, ('9999-0000', ''): 1})  # last: not in the table
    rows = jl.site_rows(PAGE)
    monkey_broad = jl.BROAD
    try:
        jl.BROAD = 2  # make CLINICAL NEUROLOGY "broad" in this small table
        rules, notes = jl.detect(rows, weights)
    finally:
        jl.BROAD = monkey_broad
    assert rules[0] == 'CLINICAL NEUROLOGY:spine,neurosurgery' or rules[0].startswith('CLINICAL NEUROLOGY:')
    assert 'ORTHOPEDICS' in rules and '2 of your journals found' in notes[0]
    count, message = jl.build({'auto': True}, PAGE, weights=weights, replace=True)
    assert count >= 2 and 'detected' in open(jl.list_path(), encoding='utf-8').read()
    assert jl.build({'auto': True}, PAGE, weights=Counter(), replace=True)[1].startswith('could not tell your field')


def test_your_journals_reads_pmids_and_target_journals(tmp_path, monkeypatch):
    paper = tmp_path / 'paper'
    (paper / 'knowledge').mkdir(parents=True)
    (paper / 'knowledge' / 'evidence.md').write_text('- **PMID:** 111\n- **PMID:** 222\n- **PMID:** 111\n', encoding='utf-8')
    (paper / 'project.json').write_text(json.dumps({'journal': 'spine-j'}), encoding='utf-8')
    seen = []
    monkeypatch.setattr(jl, 'summaries', lambda ids: seen.append(ids) or [{'issn': '1529-9430', 'essn': ''} for _ in ids])
    monkeypatch.setattr(jl, 'journal_issns', lambda ta: {'issn': '1529-9430', 'essn': '', 'source': ta})
    weights = jl.your_journals(paper, jf.STYLE_TA, confirm=lambda *a: True)
    assert seen[0] == ['111', '222'] and weights[('1529-9430', '')] == 2 + 5


def test_saved_settings_are_reused_add_remove_and_command_line(tmp_path, monkeypatch, capsys):
    (tmp_path / 'page.html').write_text(PAGE, encoding='utf-8')
    page = str(tmp_path / 'page.html')
    assert jl.cmd_list(args(preset='ortho', from_html=page)) == 0
    assert set(jl.my_list()) == {'spinej', 'jphysiother'}
    assert jl.cmd_list(args(from_html=page)) == 0  # no rules: the saved settings, not detection
    assert set(jl.my_list()) == {'spinej', 'jphysiother'}
    assert jl.cmd_list(args(preset='dentistry', from_html=page)) == 2
    assert jl.cmd_list(args(build=False, categories='uro', from_html=page)) == 0
    assert 'UROLOGY & NEPHROLOGY' in capsys.readouterr().out
    monkeypatch.setattr(jl, 'journal_issns', lambda ta: {'source': 'World Neurosurg', 'fulljournalname': 'World neurosurgery'}
                        if ta == 'World Neurosurg' else {})
    assert jl.cmd_list(args(build=False, add='World Neurosurg', group=['Neurosurgery'])) == 0
    entry = jl.my_list()['worldneurosurg']
    assert entry['group'] == 'Neurosurgery' and jl.list_note(entry) == 'Neurosurgery (your list)'
    assert jl.cmd_list(args(build=False, remove='J Physiother')) == 0
    assert 'jphysiother' not in jl.my_list()
    assert jl.cmd_list(args(build=False)) == 0
    out = capsys.readouterr().out
    assert 'added World Neurosurg' in out and 'removed J Physiother' in out and 'settings: ORTHOPEDICS' in out


def test_import_suggest_mine_and_fit_use_the_list(tmp_path, monkeypatch, capsys):
    from tests.test_journal_fit import paper, fake_search, fake_fetch, fit_args
    root = paper(tmp_path)
    monkeypatch.chdir(root)
    listing = ('# My journal list\n\n' + jl.LIST_HEADER + '\n|---|---|---|---|---|---|\n'
               '| Spine | Spine J | Spine Journal | Orthopedics | 9.88 | 5.1 |\n'
               '| Spine | Eur Spine J | European Spine Journal | Orthopedics | 28.49 | 3.2 |\n')
    (tmp_path / 'list.md').write_text(listing, encoding='utf-8')
    (tmp_path / 'bad.md').write_text('| a | b |\n', encoding='utf-8')
    assert jl.cmd_list(args(build=False, import_file=str(tmp_path / 'bad.md'))) == 2
    assert jl.cmd_list(args(build=False, import_file=str(tmp_path / 'list.md'))) == 0

    def counts(term, retmax=20, sort='relevance'):
        return [], (4 if '"Eur Spine J"[ta]' in term else 0)
    real = jf.mine_counts
    monkeypatch.setattr(jf.pubmed, 'search_pubmed', lambda term, retmax=20, sort='relevance': (['1'], 30))
    monkeypatch.setattr(jf, 'summaries', lambda ids: [])
    monkeypatch.setattr(jf, 'mine_counts', lambda q, mine, years: real(q, mine, years, counts))
    assert jf.cmd_suggest(argparse.Namespace(query='olif', years=5, top=5, review=False, reviewers=None, mine=True)) == 0
    out = capsys.readouterr().out
    assert '| 1 | Eur Spine J | 4 | 100% | - | Spine: top 28.49% Orthopedics |' in out and '| Spine J |' not in out
    assert jf.cmd_fit(fit_args(journal='Spine J'), search=fake_search, fetch=fake_fetch) == 0
    assert 'In your journal list: Spine: top 9.88% Orthopedics.' in capsys.readouterr().out


def test_setup_offers_the_list_once(monkeypatch, capsys):
    sys.path.insert(0, str(ROOT))
    from manuwright import lifecycle
    tool = lifecycle.journal_tool()
    built = []
    monkeypatch.setattr(lifecycle, 'journal_tool', lambda: tool)
    monkeypatch.setattr(tool.journal_list, 'build', lambda settings, **kw: built.append(settings) or (3, 'saved 3'))
    lifecycle.journal_list_step(lambda _: '-')
    lifecycle.journal_list_step(lambda _: '')
    lifecycle.journal_list_step(lambda _: 'ortho')
    lifecycle.journal_list_step(lambda _: 'UROLOGY & NEPHROLOGY; SURGERY:neurosurg')
    assert built[0] == {'auto': True} and built[1]['rules'] == ['ORTHOPEDICS'] and built[1]['label'] == 'ortho'
    assert built[2] == {'rules': ['UROLOGY & NEPHROLOGY', 'SURGERY:neurosurg']}
    assert 'skipped; later: manuwright journal list --build' in capsys.readouterr().out
    jl.save_list('# x\n\n' + jl.LIST_HEADER + '\n| Spine | Spine J | S | Orthopedics | 9 | 5 |\n')
    lifecycle.journal_list_step(lambda _: pytest.fail('a list exists: no question'))


def test_review_fixes_options_on_saved_settings_label_offline_and_odd_cells(tmp_path, monkeypatch, capsys):
    (tmp_path / 'page.html').write_text(PAGE + '\n' + row(8, 'SPINE DEFORMITY', '2212-134X', 'ORTHOPEDICS', 'N/A'),
                                        encoding='utf-8')
    page = str(tmp_path / 'page.html')
    assert jl.cmd_list(args(preset='ortho-neuro', from_html=page)) == 0  # a non-numeric rank is skipped
    assert jl.saved_settings()['label'] == 'ortho-neuro' and 'ortho-neuro' in jl.list_path().read_text()
    assert jl.cmd_list(args(top=5, from_html=page)) == 0  # --top on the saved field, not detection
    assert set(jl.my_list()) == {'jphysiother'} and jl.saved_settings()['rules'][0] == 'ORTHOPEDICS'
    assert jl.cmd_list(args(top=50, exclude='urology, physiother', from_html=page)) == 0
    assert 'jphysiother' not in jl.my_list() and jl.saved_settings()['exclude'] == ['urology', 'physiother']

    def offline(ta):
        raise OSError('no network')
    monkeypatch.setattr(jl, 'journal_issns', offline)
    assert jl.cmd_list(args(build=False, add='World Neurosurg')) == 1
    assert jl.cmd_list(args(build=False, import_file=str(tmp_path / 'missing.md'))) == 2
    assert 'could not reach' in capsys.readouterr().err


def test_the_starter_example_pmid_is_not_a_reference(tmp_path, monkeypatch):
    sys.path.insert(0, str(ROOT))
    from manuwright import lifecycle
    (tmp_path / 'knowledge').mkdir()
    (tmp_path / 'knowledge' / 'evidence.md').write_text(lifecycle.EVIDENCE_STARTER, encoding='utf-8')
    seen = []
    monkeypatch.setattr(jl, 'summaries', lambda ids: seen.append(ids) or [])
    assert jl.your_journals(tmp_path, {}) == Counter() and seen == [[]]


def test_build_keeps_an_existing_list_and_reference_pmids_need_consent(tmp_path, monkeypatch):
    jl.save_list('# mine\n\n' + jl.LIST_HEADER + '\n|---|---|---|---|---|---|\n| Spine | Spine J | x | y | 1 | 1 |\n')
    count, message = jl.build({**jl.PRESETS['ortho-neuro'], 'label': 'ortho-neuro'}, PAGE)
    assert count == 0 and '--replace' in message and 'Spine J' in jl.list_path().read_text(encoding='utf-8')
    jl.build({**jl.PRESETS['ortho-neuro'], 'label': 'ortho-neuro'}, PAGE, replace=True)
    jl.build({'rules': ['UROLOGY & NEPHROLOGY']}, PAGE, replace=True)
    assert len(list(jl.list_path().parent.glob('list.md*.bak'))) == 2  # the hand-made list survives as a dated copy
    paper = tmp_path / 'paper'
    (paper / 'knowledge').mkdir(parents=True)
    (paper / 'knowledge' / 'evidence.md').write_text('- **PMID:** 111\n', encoding='utf-8')
    sent = []
    monkeypatch.setattr(jl, 'summaries', lambda ids: sent.append(ids) or [])
    jl.your_journals(paper, {})  # no consent: nothing sent
    jl.your_journals(paper, {}, confirm=lambda n, papers: False)
    assert sent == [[], []]


def test_ranking_rows_do_not_depend_on_line_breaks():
    one_line = PAGE.replace('\n', '')
    assert len(jl.site_rows(one_line)) == len(jl.site_rows(PAGE)) == len(jl.site_rows(PAGE.replace('<td', '\n<td')))

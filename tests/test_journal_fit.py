"""Journal fit review and suggestions: PubMed record, limits, packet, reviewers (network faked)."""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import journal_fit as jf  # noqa: E402


@pytest.fixture(autouse=True)
def isolated_home(tmp_path_factory, monkeypatch):
    monkeypatch.setenv('MANUWRIGHT_HOME', str(tmp_path_factory.mktemp('jhome')))
    monkeypatch.setattr(jf.time, 'sleep', lambda s: None)


def paper(tmp_path):
    root = tmp_path / 'paper'
    (root / 'drafts').mkdir(parents=True)
    (root / 'project.json').write_text(json.dumps({'artifacts': [], 'journal': 'spine-j'}), encoding='utf-8')
    (root / 'drafts' / '01_title.md').write_text('# Title\n\nOblique lumbar interbody fusion for adult degenerative '
                                                 'spondylolisthesis: a retrospective cohort study\n', encoding='utf-8')
    (root / 'drafts' / '02_abstract.md').write_text('**Background:** ' + 'word ' * 260, encoding='utf-8')
    (root / 'drafts' / '03_introduction.md').write_text('Fusion rates vary [EVID:a_2020] [EVID:b_2021].\n', encoding='utf-8')
    (root / 'drafts' / '08_references.md').write_text('1. A. One.\n2. B. Two.\n3. C. Three.\n', encoding='utf-8')
    (root / 'drafts' / '09_figure_legends.md').write_text('Figure 1. Flow.\nFigure 2. Curves.\n', encoding='utf-8')
    (root / 'drafts' / 'table_1.md').write_text('| a |\n', encoding='utf-8')
    return root


def fake_search(term, retmax=20, sort='relevance'):
    if '"Spine J"[ta]' in term and 'Oblique' in term:
        return ['111', '222'], 2
    if '"Spine J"[ta]' in term:
        return [], 1300
    return [], 120


def fake_fetch(ids):
    return [{'pmid': i, 'title': f'Paper {i}', 'year': '2025', 'pub_types': ['Journal Article', 'Comparative Study']}
            for i in ids]


def fit_args(**kw):
    base = dict(journal=None, query=None, years=5, reviewers=None, no_review=True)
    base.update(kw)
    return argparse.Namespace(**base)


def test_query_counts_and_limits(tmp_path):
    root = paper(tmp_path)
    assert jf.default_query(root) == 'Oblique lumbar interbody fusion adult degenerative'
    counts = jf.measure(root)
    assert counts == {'abstract_words': 261, 'main_text_words': 3, 'references': 3, 'tables_figures': 3}
    table = '\n'.join(jf.limits_table(counts, {'abstract_words': 250, 'references': 40}))
    assert '| Abstract words | 261 | 250 | OVER |' in table and '| References | 3 | 40 | ok |' in table
    assert 'Tables + figures | 3 | - | not in profile' in table


def test_profile_is_read_and_only_its_curated_part_goes_to_reviewers(tmp_path):
    path = tmp_path / 'p.md'
    path.write_text(jf.PROFILE_TEMPLATE.format(name='The Spine Journal', ta='Spine J', source='https://x', date='2026')
                    .replace('- abstract_words:', '- abstract_words: 250').replace('verified_by_author: no', 'verified_by_author: yes')
                    + '\n## Fetched page text (x)\n\nRAW PAGE\n', encoding='utf-8')
    profile = jf.read_profile(path)
    assert profile['limits'] == {'abstract_words': 250} and profile['verified'] and profile['source'] == 'https://x'
    assert 'RAW PAGE' not in profile['text'] and 'Aims and scope' in profile['text']


def test_fit_writes_the_record_and_packet_without_sending_anything_by_default(tmp_path, monkeypatch, capsys):
    root = paper(tmp_path)
    monkeypatch.chdir(root / 'drafts')
    assert jf.cmd_fit(fit_args(), search=fake_search, fetch=fake_fetch) == 0  # journal from project.json
    out = capsys.readouterr().out
    assert 'Spine J published 2 articles on this topic (of 120' in out and 'PMID 111; Comparative Study' in out
    assert 'No journal profile yet' in out
    run = next((root / 'review' / 'journal').glob('spine-j_*'))
    packet = (run / 'packet.md').read_text(encoding='utf-8')
    assert packet.startswith('MODE: fit\nTARGET JOURNAL: Spine J') and 'Oblique lumbar interbody' in packet
    assert not (run / 'run.json').exists()  # --no-review: no reviewer called


def test_fit_runs_the_saved_reviewers_with_the_journal_prompt(tmp_path, monkeypatch, capsys):
    root = paper(tmp_path)
    monkeypatch.chdir(root)
    cr = jf.load_critical()
    seen = {}

    def fake_run(packet, models, role, key, failures):
        seen.update(models=models, role=role, prompt=cr.build_prompt(role, packet))
        return {models[0]: 'VERDICT: FIT'}
    monkeypatch.setattr(jf, 'load_critical', lambda: cr)
    monkeypatch.setattr(cr, 'run_critical_review', fake_run)
    monkeypatch.setattr(cr, 'settings', lambda: {'review': {'reviewers': ['codex']}})
    assert jf.cmd_fit(fit_args(journal='Spine J', no_review=False), search=fake_search, fetch=fake_fetch) == 0
    assert seen['role'] == 'journal' and seen['models'] == ['codex-cli']
    assert 'handling editor of the journal' in seen['prompt'] and 'TARGET JOURNAL: Spine J' in seen['prompt']
    run = next((root / 'review' / 'journal').glob('spine-j_*'))
    assert json.loads((run / 'run.json').read_text())['completed'] == ['codex-cli']
    assert 'review by codex-cli' in capsys.readouterr().out


def test_fit_without_reviewers_says_how_to_review(tmp_path, monkeypatch, capsys):
    root = paper(tmp_path)
    monkeypatch.chdir(root)
    cr = jf.load_critical()
    monkeypatch.setattr(jf, 'load_critical', lambda: cr)
    monkeypatch.setattr(cr, 'settings', lambda: {})
    assert jf.cmd_fit(fit_args(journal='Spine J', no_review=False), search=fake_search, fetch=fake_fetch) == 0
    assert 'No reviewers set' in capsys.readouterr().out


def test_fit_still_works_offline(tmp_path, monkeypatch, capsys):
    root = paper(tmp_path)
    monkeypatch.chdir(root)

    def offline(*a, **k):
        raise OSError('no network')
    assert jf.cmd_fit(fit_args(journal='Spine J'), search=offline, fetch=offline) == 0
    assert 'PubMed could not be reached' in capsys.readouterr().out


def test_suggest_ranks_journals_and_marks_the_authors_list(tmp_path, monkeypatch, capsys):
    root = paper(tmp_path)
    (root / 'profile').mkdir()
    (root / 'profile' / 'journals.md').write_text('# Formats\n\n## 공통 원칙\n\n## The Spine Journal (Spine J) ✓\n\n'
                                                  '## European Spine Journal (Eur Spine J)\n', encoding='utf-8')
    monkeypatch.chdir(root)
    monkeypatch.setattr(jf.pubmed, 'search_pubmed', lambda term, retmax=20, sort='relevance': (['1', '2', '3', '4'], 40))
    records = [{'source': 'Eur Spine J', 'pubdate': '2025 Jan', 'title': 'E1'},
               {'source': 'Eur Spine J', 'pubdate': '2026 Mar', 'title': 'E2'},
               {'source': 'Cureus', 'pubdate': '2024', 'title': 'C1'},
               {'source': 'Spine J', 'pubdate': '2023', 'title': 'S1'}]
    monkeypatch.setattr(jf, 'summaries', lambda ids: records)
    args = argparse.Namespace(query=None, years=5, top=5, review=False, reviewers=None)
    assert jf.cmd_suggest(args) == 0
    out = capsys.readouterr().out
    assert '| 1 | Eur Spine J | 2 | 50% | 2026 | #2 |' in out and '| Spine J | 1 | 25% | 2023 | #1 |' in out
    assert '| Cureus | 1 | 25% | 2024 | - |' in out and 'not journal rank' in out


def test_chat_requests_reach_the_agent_only_in_a_paper(tmp_path):
    spec = importlib.util.spec_from_file_location('style_intent', ROOT / 'scripts' / 'hooks' / 'style_intent.py')
    intent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(intent)
    root = paper(tmp_path)
    (root / 'knowledge').mkdir()
    (root / 'knowledge' / 'evidence.md').write_text('# Evidence\n', encoding='utf-8')
    for prompt in ('이 논문 Spine J 에 맞는지 봐줘', '어느 저널에 투고할까?', '저널 추천해줘', 'Is it a fit for Spine J?'):
        assert 'manuwright journal' in intent.journal_request(prompt, str(root)), prompt
    for prompt in ('서론 써줘', '결과를 표에 맞게 정리해줘', '이 기능 저널 추천 구현해줘'):
        assert intent.journal_request(prompt, str(root)) == '', prompt
    assert intent.journal_request('어느 저널에 투고할까?', str(tmp_path)) == ''  # not a paper folder

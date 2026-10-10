"""Personal library sync: wording rules, notes and files flow between papers and the library, additions only."""
from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import academic_style as acad  # noqa: E402
import library_sync as sync  # noqa: E402
from lint_manuscript import load_forbidden_terms  # noqa: E402


def paper(tmp_path, name='paper1'):
    root = tmp_path / name
    (root / 'drafts').mkdir(parents=True)
    (root / 'knowledge').mkdir()
    (root / 'knowledge' / 'evidence.md').write_text('# Evidence\n', encoding='utf-8')
    (root / 'project.json').write_text(json.dumps({'artifacts': []}), encoding='utf-8')
    return root


def test_term_goes_to_library_and_paper_without_overwriting(tmp_path):
    root = paper(tmp_path)
    report = sync.remember_term('used', 'utilized', '', root / 'drafts')
    assert any(line.startswith('library: added utilized -> used') for line in report)
    assert any(line.startswith('paper: added utilized -> used') for line in report)
    library = sync.library_terminology()
    # a new registry starts from the engine's, so the lint keeps its standard vocabulary
    assert load_forbidden_terms(library)['utilized'] == 'used' and len(load_forbidden_terms(library)) > 20
    registry = root / 'Style' / 'terminology.md'
    assert load_forbidden_terms(registry)['utilized'] == 'used'
    # the lint reads the registry project.json names, so the paper's is declared
    assert json.loads((root / 'project.json').read_text(encoding='utf-8'))['terminology'] == 'Style/terminology.md'
    again = sync.remember_term('used', 'utilized', '', root)
    assert all('already has' in line for line in again)
    conflict = sync.remember_term('employed', 'utilized', '', root)
    assert all('CONFLICT' in line for line in conflict)
    assert load_forbidden_terms(library)['utilized'] == 'used'  # the author decides; nothing replaced


def test_sync_pull_push_and_report(tmp_path):
    first, second = paper(tmp_path, 'first'), paper(tmp_path, 'second')
    sync.remember_term('used', 'utilized', '', first)
    (first / 'Style' / 'own').mkdir(parents=True)
    (first / 'Style' / 'own' / 'park_2021.md').write_text('# anchor\n', encoding='utf-8')
    (first / 'profile').mkdir()
    (first / 'profile' / 'authors.md').write_text('# Authors\n- Park\n', encoding='utf-8')
    pushed = sync.sync(first, 'push')
    assert {'Style/own/park_2021.md', 'profile/authors.md'} <= set(pushed['copied'])
    report = sync.sync(second, None)
    assert 'rule utilized -> used' in report['missing_here'] and 'Style/own/park_2021.md' in report['missing_here']
    assert not (second / 'Style').exists()  # a report changes nothing
    pulled = sync.sync(second, 'pull')
    assert 'utilized -> used' in pulled['added_rules'] and 'profile/authors.md' in pulled['copied']
    assert json.loads((second / 'project.json').read_text(encoding='utf-8'))['terminology'] == 'Style/terminology.md'
    assert sync.sync(second, 'pull')['added_rules'] == []  # idempotent
    (second / 'profile' / 'authors.md').write_text('# Authors\n- Park\n- Kim\n', encoding='utf-8')
    assert 'profile/authors.md' in sync.sync(second, 'push')['differs']  # never overwritten
    assert '- Kim' not in (sync.library() / 'profile' / 'authors.md').read_text(encoding='utf-8')
    assert sync.is_template(ROOT)  # the engine checkout is never synced


def test_notes_are_kept_once_and_shown_at_session_start(tmp_path, monkeypatch):
    assert 'kept under journal' in sync.add_note('Spine uses a capital P for p values.', 'journal')
    assert sync.add_note('Spine uses  a capital P for p values.', 'journal').startswith('already kept')
    sync.add_note('Reviewer 2 at JNS asks for MCID.', 'reviewer')
    root = paper(tmp_path)
    card = sync.session_sync(root)
    assert 'YOUR NOTES' in card and 'capital P' in card and '## reviewer' in card
    sync.remember_term('used', 'utilized', '', None)  # library only
    other = paper(tmp_path, 'other')
    assert 'LIBRARY SYNC: added' in sync.session_sync(other)  # auto pull (default)
    assert load_forbidden_terms(other / 'Style' / 'terminology.md')['utilized'] == 'used'
    third = paper(tmp_path, 'third')
    (sync.academic_style.home() / 'config.json').write_text(json.dumps({'library_sync': 'ask'}), encoding='utf-8')
    card = sync.session_sync(third)
    assert 'not in this paper' in card and not (third / 'Style').exists()
    (sync.academic_style.home() / 'config.json').write_text(json.dumps({'library_sync': 'off'}), encoding='utf-8')
    assert sync.session_sync(third) == ''


def test_applied_edit_rules_reach_the_library(tmp_path, monkeypatch):
    root = paper(tmp_path)
    (root / 'Style').mkdir()
    (root / 'Style' / 'pending_style_rules.md').write_text(
        '# Pending\n\n- [x] P0 replace "demonstrated" with "showed" (2x)\n', encoding='utf-8')
    monkeypatch.chdir(root)
    assert acad.main(['edits', '--apply']) == 0
    assert load_forbidden_terms(root / 'Style' / 'terminology.md')['demonstrated'] == 'showed'
    assert load_forbidden_terms(sync.library_terminology())['demonstrated'] == 'showed'


def test_chat_memory_requests_reach_the_agent_only_in_a_paper(tmp_path):
    spec = importlib.util.spec_from_file_location('style_intent', ROOT / 'scripts' / 'hooks' / 'style_intent.py')
    intent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(intent)
    root = paper(tmp_path)
    for prompt in ('앞으로는 utilized 대신 used로 써', '이거 기억해줘', '공동저자 홍길동 추가해줘',
                   '김철수 소속이 바뀌었어', '라이브러리 최신으로 받아줘', 'Add Dr Lee as a co-author'):
        assert 'manuwright library' in intent.evaluate({'prompt': prompt, 'cwd': str(root)}), prompt
    assert intent.memory_request('이거 기억해줘', str(tmp_path)) == ''  # not a paper folder
    for prompt in ('서론 써줘', '이 기능을 라이브러리에 반영되게 만들어줘', '결과 정리해줘'):
        assert intent.memory_request(prompt, str(root)) == '', prompt


def test_cli_routes_library_commands(tmp_path, monkeypatch, capsys):
    from manuwright import library
    root = paper(tmp_path)
    monkeypatch.chdir(root)
    assert library.main(ROOT, ['term', '--prefer', 'used', '--avoid', 'utilized']) == 0
    assert library.main(ROOT, ['note', 'JAMA wants key points', '--topic', 'journal']) == 0
    assert library.main(ROOT, ['sync']) == 0
    out = capsys.readouterr().out
    assert 'library: added utilized -> used' in out and 'kept under journal' in out
    assert os.path.isfile(sync.notes_path())

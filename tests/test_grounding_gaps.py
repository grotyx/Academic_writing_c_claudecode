"""v1.10.9: cases where a wrong manuscript used to get a green check (independent reviews, 261126). Synthetic data."""
import pytest

from harness.project import checker
from manuwright import cli

NUM = checker('check_numbers')
CIT = checker('check_citations')
GATE = checker('check_gate')


def numbers(tmp_path, text, csv='estimate\n2.5\n'):
    (tmp_path / 'results').mkdir(exist_ok=True)
    (tmp_path / 'results/r.csv').write_text(csv, encoding='utf-8')
    (tmp_path / 'a.md').write_text(text + '\n', encoding='utf-8')
    return NUM.check_numbers([tmp_path / 'a.md'], results_dir=tmp_path / 'results')


@pytest.mark.parametrize('text', [
    'The change was −2.5 points.',              # typographic minus: the sign was dropped
    'The p value was p ≤ 2.5.',                  # typographic comparator: p-value lost
    'Table 1 summarizes 876 patients.',              # caption prefix exempted the whole line
    'We enrolled 2024 patients.',                    # year-sized count
    'A total of 2,048 patients were included.',      # thousands separator is never a year
    'The groups had 15/28/12 events.',               # three-group count read as a date
    'In total, n = 2019 were analysed.',
    'Of 2024 patients, half had pain.',
])
def test_unsupported_numbers_now_fail(tmp_path, text):
    result = numbers(tmp_path, text)
    assert not result.passed and result.checked_numbers >= 1, text


@pytest.mark.parametrize('text', [
    'The change was 2.5 points.',
    'The cohort was enrolled in 2019 at a single center.',
    'Patients treated between 2015 and 2020 were eligible.',
    'We followed the 2019 guideline (Smith et al., 2020).',
    'Follow-up ended on 12/03/2021 for the last patient.',
    'Table 1 shows baseline characteristics.',
    '## 2.1 Statistical analysis',
    'As reported by Weber 2007 in a trial, surgery helped.',
])
def test_supported_and_structural_numbers_still_pass(tmp_path, text):
    assert numbers(tmp_path, text).passed, text


@pytest.mark.parametrize('text', ['The difference was significant (P value < 0.05).',
                                  'The difference was significant (*p*-value < 0.05).',
                                  'The difference was significant (*p* ≤ 0.05).'])
def test_nonsignificant_p_cannot_support_a_threshold_claim(tmp_path, text):
    assert not numbers(tmp_path, text, csv='outcome,p\npain,0.054\n').passed, text
    assert numbers(tmp_path, text, csv='outcome,p\npain,0.012\n').passed, text


def test_p_value_table_header_with_emphasis(tmp_path):
    table = '| Outcome | *P*-value |\n|---|---|\n| Pain | 0.05 |'
    assert not numbers(tmp_path, table, csv='outcome,estimate\npain,0.054\n').passed


def test_negative_csv_value_supports_typographic_minus(tmp_path):
    assert numbers(tmp_path, 'The change was −2.5 points.', csv='estimate\n−2.5\n').passed


@pytest.mark.parametrize('text', ['Prior work [EVID:missing.', 'Prior work [evid:ghost_2020].',
                                  'Prior work [EVID :ghost_2020].', 'Prior work [EVID:\nghost_2020].'])
def test_malformed_citation_openers_fail(tmp_path, text):
    (tmp_path / 'ev.md').write_text('# Evidence\n', encoding='utf-8')
    (tmp_path / 'a.md').write_text(text + '\n', encoding='utf-8')
    result = CIT.check_citations([tmp_path / 'a.md'], evidence_path=tmp_path / 'ev.md')
    assert not result.passed and result.checked_tokens >= 1, text


def test_gate_pass_beside_a_failed_check_fails(tmp_path):
    gate = tmp_path / 'g.GATE.md'
    gate.write_text('artifact: paper.md\nstatus: PASS\nchecks:\n  citation: FAIL\n  numbers: PASS\n', encoding='utf-8')
    result = GATE.check_gate(gate, max_round=2)
    assert not result.passed and any('citation is FAIL' in f.reason for f in result.failures)
    gate.write_text('artifact: paper.md\nstatus: PASS\nchecks:\n  citation: PASS\n  numbers: N/A\n', encoding='utf-8')
    assert GATE.check_gate(gate, max_round=2).passed


@pytest.mark.parametrize('command', ['init', 'update', 'env', 'run', 'obsidian', 'setup', 'agents', 'config'])
def test_help_prints_usage_and_changes_nothing(tmp_path, monkeypatch, capsys, command):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv('MANUWRIGHT_HOME', str(tmp_path / 'home'))
    assert cli.main([command, '--help']) == 0
    assert command in capsys.readouterr().out
    assert list(tmp_path.iterdir()) == []


def test_profile_help_needs_no_paper_folder(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert cli.main(['verify', '--help']) == 0

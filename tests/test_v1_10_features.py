"""v1.10.0: result-binding proposals, number-level exemptions, tracked revisions, journal statistics notation.
All data are synthetic."""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'scripts' / f'{name}.py')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def paper(tmp_path, results_md, allow=None, journal=None):
    (tmp_path / 'results').mkdir()
    (tmp_path / 'drafts').mkdir()
    (tmp_path / 'review').mkdir()
    (tmp_path / 'results' / 'outcomes.csv').write_text(
        'outcome,MIS_n,MIS_mean,OPEN_n,OPEN_mean,p\nebl_ml,60,178.4,60,440.0,<0.001\nlos_days,60,4.0,60,6.0,<0.001\n',
        encoding='utf-8')
    (tmp_path / 'drafts' / '05_results.md').write_text(results_md, encoding='utf-8')
    config = {'paper_id': 'demo', 'results': 'results', 'numeric_artifacts': ['drafts/05_results.md'],
              'artifacts': ['drafts/05_results.md']}
    if allow is not None:
        config['numeric_allow'] = allow
    if journal:
        config['journal'] = journal
    (tmp_path / 'project.json').write_text(json.dumps(config), encoding='utf-8')
    return config


# --- bind --------------------------------------------------------------------------------

def test_bind_never_invents_context_and_binds_once_given(tmp_path):
    bind = module('bind_results')
    config = paper(tmp_path, '# Results\n\nMean EBL was 178.4 mL after MIS-TLIF and 440.0 mL after open TLIF.\n')
    report = bind.propose(tmp_path, config)['report']
    assert not report['bound'] and len(report['unresolved']) == 2  # no time point, population, comparison or unit
    (tmp_path / 'review' / 'bindings_overrides.json').write_text(json.dumps({'tables': {'results/outcomes.csv': {
        'timepoint': 'during surgery', 'population': 'all patients', 'comparison': 'MIS vs open', 'unit': 'mL'}}}),
        encoding='utf-8')
    proposal = bind.propose(tmp_path, config)
    assert len(proposal['bindings']) == 2 and proposal['bindings'][0]['context']['outcome'] == 'ebl_ml'


def test_bind_leaves_ambiguous_numbers_to_an_override_with_line_text(tmp_path):
    bind = module('bind_results')
    config = paper(tmp_path, '# Results\n\nEach group had 60 patients.\n')
    (tmp_path / 'review' / 'bindings_overrides.json').write_text(json.dumps({
        'tables': {'results/outcomes.csv': {'timepoint': 'baseline', 'population': 'all', 'comparison': 'MIS vs open',
                                            'unit': 'patients'}}}), encoding='utf-8')
    report = bind.propose(tmp_path, config)['report']
    assert report['suggested'] and not report['bound']
    overrides = json.loads((tmp_path / 'review' / 'bindings_overrides.json').read_text(encoding='utf-8'))
    overrides['numbers'] = [{'artifact': 'drafts/05_results.md', 'line': 3, 'number': '60',
                             'line_text': 'Each group had', 'cell': 'results/outcomes.csv:2:MIS_n'}]
    (tmp_path / 'review' / 'bindings_overrides.json').write_text(json.dumps(overrides), encoding='utf-8')
    assert len(bind.propose(tmp_path, config)['bindings']) == 1
    (tmp_path / 'drafts' / '05_results.md').write_text('# Results\n\nThe cohort had 60 patients.\n', encoding='utf-8')
    report = bind.propose(tmp_path, config)['report']  # the sentence changed: the override must not follow it
    assert any('line_text' in p for p in report['problems']) and not report['bound']


def test_bind_write_passes_the_validator(tmp_path, monkeypatch):
    from harness.results import validate_bindings
    bind = module('bind_results')
    config = paper(tmp_path, '# Results\n\nMean EBL was 178.4 mL after MIS-TLIF.\n')
    (tmp_path / 'review' / 'bindings_overrides.json').write_text(json.dumps({'tables': {'results/outcomes.csv': {
        'timepoint': 'during surgery', 'population': 'all patients', 'comparison': 'MIS vs open', 'unit': 'mL'}}}),
        encoding='utf-8')
    monkeypatch.chdir(tmp_path)
    assert bind.main(['--write']) == 0
    assert json.loads((tmp_path / 'project.json').read_text(encoding='utf-8'))['result_bindings'] == 'review/result_bindings.json'
    assert validate_bindings(tmp_path, tmp_path / 'review' / 'result_bindings.json', 'demo',
                             ['drafts/05_results.md'], module('check_numbers')) == 1


# --- numeric_allow -------------------------------------------------------------------------

def test_numeric_allow_exempts_only_numbers_inside_the_phrase(tmp_path):
    cn = module('check_numbers')
    paper(tmp_path, '# Results\n\nAt 12 months, 12 patients improved; 112 months later none.\n',
          allow=[{'text': '12 months', 'reason': 'time point'}])
    numbers = [t.number for t in cn.iter_artifact_numbers(tmp_path / 'drafts' / '05_results.md')]
    assert numbers == ['12', '112']  # "12 months" exempt; "12 patients" and "112 months" are still checked


def test_numeric_allow_is_validated_and_stale_rules_fail_verify(tmp_path):
    from harness import project
    cn = module('check_numbers')
    paper(tmp_path, '# Results\n\nAt 12 months.\n', allow=[{'text': '24 months', 'reason': 'time point'}])
    count, unmatched = cn.allow_report(tmp_path, [{'text': '24 months', 'reason': 'x'}],
                                       [tmp_path / 'drafts' / '05_results.md'])
    assert count == 0 and unmatched == ['24 months']
    config = json.loads((tmp_path / 'project.json').read_text(encoding='utf-8'))
    config.update({'schema_version': 1, 'study_type': 'original_research', 'evidence': 'k.md', 'draft_plan': 'd.md',
                   'analysis_plan': 'a.md', 'numeric_allow': [{'text': 'no number', 'reason': 'x'}]})
    for name in ('k.md', 'd.md', 'a.md'):
        (tmp_path / name).write_text('x', encoding='utf-8')
    (tmp_path / 'project.json').write_text(json.dumps(config), encoding='utf-8')
    with pytest.raises(ValueError, match='numeric_allow'):
        project.load_project(tmp_path / 'project.json')


# --- tracked changes --------------------------------------------------------------------------

def test_tracked_docx_accepts_to_new_and_rejects_to_old(tmp_path):
    pytest.importorskip('docx')
    from harness import tracked
    old = '# Results\n\nMean EBL was 178.4 mL (*p* < 0.001).^1^\n\nUnchanged paragraph.\n'
    new = '# Results\n\nMean EBL was 178.4 mL and 440.0 mL (*p* < 0.001).^1^\n\nUnchanged paragraph.\n\nAdded.\n'
    out = tmp_path / 'tracked.docx'
    counts = tracked.tracked_docx(old, new, out)
    assert counts == {'kept': 2, 'inserted': 2, 'deleted': 1}
    assert tracked.resolved_text(out, True) == ['Results', 'Mean EBL was 178.4 mL and 440.0 mL (p < 0.001).1',
                                                'Unchanged paragraph.', 'Added.']
    assert tracked.resolved_text(out, False) == ['Results', 'Mean EBL was 178.4 mL (p < 0.001).1', 'Unchanged paragraph.']


def test_tracked_docx_refuses_tables():
    from harness import tracked
    with pytest.raises(ValueError, match='tables'):
        tracked.blocks('| a | b |\n|---|---|\n| 1 | 2 |\n')


# --- statistics notation ------------------------------------------------------------------------

@pytest.mark.parametrize('journal,line,flagged', [
    ('gsj', 'Lower (*P* = 0.02).', 'AMA style'),
    ('gsj', 'Lower (*P* ≤ 0.05).', 'AMA style'),
    ('gsj', 'Lower (*P* = .02).', None),
    ('spine', 'Lower (*p* = .02).', 'leading zero'),
    ('spine', 'Lower (*P* = 0.02).', None),
])
def test_p_value_notation_follows_the_target_journal(tmp_path, journal, line, flagged):
    lint = module('lint_manuscript')
    paper(tmp_path, f'# Results\n\n{line}\n', journal=journal)
    stat = [m for code, _p, _l, m in lint.lint_file(tmp_path / 'drafts' / '05_results.md', {}) if code == 'STAT_FORMAT']
    if flagged:
        assert any(flagged in m for m in stat), stat
    else:
        assert not stat, stat


# --- Codex final review blockers ---------------------------------------------------------------

def test_a_stray_manifest_in_a_subfolder_cannot_add_exemptions(tmp_path):
    cn = module('check_numbers')
    paper(tmp_path, '# Results\n\nMean age was 54 years.\n')
    (tmp_path / 'drafts' / 'project.json').write_text(json.dumps(
        {'artifacts': ['05_results.md'], 'numeric_allow': [{'text': '54 years', 'reason': 'local'}]}), encoding='utf-8')
    cn.select_manifest(tmp_path, [])  # what verify and bind do with the paper's own manifest
    try:
        assert [t.number for t in cn.iter_artifact_numbers(tmp_path / 'drafts' / '05_results.md')] == ['54']
    finally:
        cn.select_manifest(tmp_path, [])
        cn.SELECTED = None


def test_a_changed_override_wins_over_a_kept_binding(tmp_path, monkeypatch):
    bind = module('bind_results')
    paper(tmp_path, '# Results\n\nEach group had 60 patients.\n')
    overrides = {'tables': {'results/outcomes.csv': {'timepoint': 'baseline', 'population': 'all',
                                                     'comparison': 'MIS vs open', 'unit': 'patients'}},
                 'numbers': [{'artifact': 'drafts/05_results.md', 'line': 3, 'number': '60',
                              'line_text': 'Each group had', 'cell': 'results/outcomes.csv:2:MIS_n'}]}
    (tmp_path / 'review' / 'bindings_overrides.json').write_text(json.dumps(overrides), encoding='utf-8')
    monkeypatch.chdir(tmp_path)
    assert bind.main(['--write']) == 0
    overrides['numbers'][0]['cell'] = 'results/outcomes.csv:2:OPEN_n'
    (tmp_path / 'review' / 'bindings_overrides.json').write_text(json.dumps(overrides), encoding='utf-8')
    assert bind.main(['--write']) == 0
    written = json.loads((tmp_path / 'review' / 'result_bindings.json').read_text(encoding='utf-8'))
    assert [r['source']['column'] for r in written['results']] == ['OPEN_n']
    overrides['numbers'].append(dict(overrides['numbers'][0]))  # a duplicate entry is an error, not a success
    (tmp_path / 'review' / 'bindings_overrides.json').write_text(json.dumps(overrides), encoding='utf-8')
    assert bind.main(['--write']) == 1


def test_two_csv_files_with_the_same_name_stay_apart(tmp_path):
    bind = module('bind_results')
    config = paper(tmp_path, '# Results\n\nGroup A had 60 and group B had 60.\n')
    for sub in ('a', 'b'):
        (tmp_path / 'results' / sub).mkdir()
        (tmp_path / 'results' / sub / 'outcomes.csv').write_text('outcome,n\npatients,60\n', encoding='utf-8')
    context = {'timepoint': 'baseline', 'population': 'all', 'comparison': 'none', 'unit': 'patients'}
    (tmp_path / 'review' / 'bindings_overrides.json').write_text(json.dumps({
        'tables': {'results/a/outcomes.csv': context, 'results/b/outcomes.csv': context},
        'numbers': [{'artifact': 'drafts/05_results.md', 'line': 3, 'number': '60', 'occurrence': 1,
                     'line_text': 'Group A', 'cell': 'results/a/outcomes.csv:2:n'},
                    {'artifact': 'drafts/05_results.md', 'line': 3, 'number': '60', 'occurrence': 2,
                     'line_text': 'group B', 'cell': 'results/b/outcomes.csv:2:n'}]}), encoding='utf-8')
    proposal = bind.propose(tmp_path, config)
    assert sorted(r['source']['file'] for r in proposal['results']) == ['results/a/outcomes.csv', 'results/b/outcomes.csv']


def test_two_character_comparators_are_checked(tmp_path):
    lint = module('lint_manuscript')
    paper(tmp_path, '# Results\n\nLower (*P* <= 0.02).\n', journal='gsj')
    stat = [m for code, _p, _l, m in lint.lint_file(tmp_path / 'drafts' / '05_results.md', {}) if code == 'STAT_FORMAT']
    assert any('AMA style' in m for m in stat)

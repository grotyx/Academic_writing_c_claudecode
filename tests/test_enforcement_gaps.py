"""v1.10.10: plan-first hooks, approval records, paths and the engine's own code (independent reviews, 261126)."""
import io
import json
import subprocess
import sys

import pytest

from harness.project import load_project, receipt_problem
from harness.results import validate_bindings
from manuwright import analysis_env, cli
from tests.test_enforce_gates import load_module
from tests.test_harness import project, put  # noqa: F401  (fixture)

GATES = load_module()


def write_event(cwd, path, tool='Write'):
    if tool == 'apply_patch':
        return {'tool_name': tool, 'cwd': str(cwd), 'tool_input': {'command': f'*** Begin Patch\n*** Add File: {path}\n+x\n*** End Patch\n'}}
    return {'tool_name': tool, 'cwd': str(cwd), 'tool_input': {'file_path': path, 'content': 'x'}}


@pytest.mark.parametrize('path', ['drafts/05_results.md', 'drafts/results.md', 'drafts/revision/../05_results.md',
                                  'drafts/paper1/discussion.md'])
def test_section_writes_without_a_plan_are_blocked(tmp_path, path):
    assert 'Rule 8' in (GATES.decide(write_event(tmp_path, path)) or '')


def test_a_parent_folder_named_revision_does_not_exempt_a_paper(tmp_path):
    paper = tmp_path / 'revision' / 'paper'
    paper.mkdir(parents=True)
    assert 'Rule 8' in GATES.decide(write_event(paper, 'drafts/05_results.md'))
    assert GATES.decide(write_event(paper, 'drafts/revision/REV1/05_results_REV1.md')) is None
    assert GATES.decide(write_event(paper, 'drafts/table_1.md')) is None  # tables come from Phase 2


@pytest.mark.parametrize('path', ['data/py/01_descriptive.py', 'data/01_descriptive.py', 'data/R/01_models.R',
                                  'data/paper1/02_compare.py', 'data/py/explore.ipynb'])
def test_analysis_scripts_without_a_plan_are_blocked(tmp_path, path):
    assert 'Rule 7' in (GATES.decide(write_event(tmp_path, path)) or '')


def test_plan_approval_inside_a_comment_is_not_an_approval(tmp_path):
    plan = tmp_path / 'drafts' / 'draft_plan.md'
    plan.parent.mkdir()
    plan.write_text('# Plan\n<!-- - [x] 사용자 승인 완료 -->\n', encoding='utf-8')
    assert 'not approved' in GATES.plan_problem(plan)


def test_blank_reviewer_or_decision_reference_is_refused(tmp_path):
    for fields in ({'reviewer': '   ', 'decision_reference': 'email 2026-11-20'},
                   {'reviewer': 'Dr Kim', 'decision_reference': ' '},
                   {'reviewer': {'name': 'x'}, 'decision_reference': 'email'}):
        receipt = tmp_path / 'signoff.json'
        receipt.write_text(json.dumps({'status': 'approved', 'dependencies': {}, **fields}), encoding='utf-8')
        assert receipt_problem(receipt, {}, human=True), fields


def test_codex_patch_in_a_template_checkout_still_runs_the_gate(tmp_path, monkeypatch, capsys):
    (tmp_path / '.claude').mkdir()
    (tmp_path / '.claude/settings.json').write_text('{"x": "scripts/hooks/enforce_gates.py"}', encoding='utf-8')
    monkeypatch.setenv('CLAUDE_PROJECT_DIR', str(tmp_path))
    calls = []
    monkeypatch.setattr(cli.subprocess, 'run', lambda cmd, input: calls.append(input) or subprocess.CompletedProcess(cmd, 2))
    for tool, expected in (('apply_patch', 2), ('Write', 0)):
        event = json.dumps(write_event(tmp_path, 'drafts/05_results.md', tool)).encode()
        monkeypatch.setattr(sys, 'stdin', io.TextIOWrapper(io.BytesIO(event)))
        assert cli.hook(['gate']) == expected, tool
    assert len(calls) == 1  # only the Codex event reached the gate script; Claude's own hook covers Write


def test_verifier_never_imports_a_harness_folder_from_the_paper(tmp_path):
    (tmp_path / 'harness').mkdir()
    (tmp_path / 'harness/__init__.py').write_text('', encoding='utf-8')
    (tmp_path / 'harness/__main__.py').write_text('print("SHADOW")', encoding='utf-8')
    out = subprocess.run(cli.harness_command('doctor'), cwd=tmp_path, capture_output=True, text=True)
    assert 'SHADOW' not in out.stdout and '"version"' in out.stdout


@pytest.mark.parametrize('paper_id', ['/tmp/evil', '../evil', 'a/b', 'C:evil', '..'])
def test_paper_id_must_be_a_plain_name(paper_id):
    with pytest.raises(ValueError):
        analysis_env.env_dir(paper_id)
    figure = __import__('harness.project', fromlist=['checker']).checker('make_figure')
    assert figure.paper_python({'paper_id': paper_id}) is None


def test_run_needs_an_approved_analysis_plan(project, monkeypatch, capsys):  # noqa: F811
    monkeypatch.chdir(project.parent)
    monkeypatch.setattr(analysis_env.subprocess, 'call', lambda *a, **k: pytest.fail('script ran without a plan'))
    put(project.parent / 'data/analysis_plan.md', '# Analysis plan\n\n- [ ] 사용자 승인 완료\n')
    assert analysis_env.run_script(['data/py/01.py']) == 2 and 'Rule 7' in capsys.readouterr().err


def test_bound_csv_must_live_in_the_results_folder(project):  # noqa: F811
    root = project.parent
    put(root / 'drafts/notes.csv', 'age\n54\n')
    bindings = {'results': [{'result_id': 'r1', 'paper_id': 'demo', 'raw': '54', 'outcome': 'age', 'timepoint': 'baseline',
                             'population': 'all', 'comparison': 'none', 'statistic': 'mean', 'unit': 'years',
                             'source': {'file': 'drafts/notes.csv', 'row': 2, 'column': 'age',
                                        'sha256': __import__('hashlib').sha256(b'age\n54\n').hexdigest()}}],
                'bindings': []}
    manifest = put(root / 'review/result_bindings.json', bindings)
    with pytest.raises(ValueError, match='results directory'):
        validate_bindings(root, manifest, 'demo', [], None, results_dir=root / 'results')


def test_state_file_cannot_be_a_manuscript_input(project):  # noqa: F811
    config = json.loads(project.read_text(encoding='utf-8'))
    put(project, dict(config, state='drafts/05_results.md'))
    with pytest.raises(ValueError, match='state must be'):
        load_project(project)
    put(project, dict(config, state='review/state.json'))
    load_project(project)


def test_journal_fit_never_reads_outside_the_paper(tmp_path):
    fit = __import__('harness.project', fromlist=['checker']).checker('journal_fit')
    (tmp_path / 'secret.md').write_text('private', encoding='utf-8')
    paper = tmp_path / 'paper'
    paper.mkdir()
    (paper / 'project.json').write_text(json.dumps({'artifacts': ['../secret.md'], 'abstract': '../secret.md'}),
                                        encoding='utf-8')
    assert fit.read(paper, '02_abstract.md') == ''

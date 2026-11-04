"""manuwright disclose: AI-use record checks, disclosure proposal, declaration placement in the build. Synthetic data."""
import json
import os

import pytest

from harness.build import build
from harness.project import checker, verify
from tests.test_harness import project, put, sign, isolated_home  # noqa: F401  (fixtures)

AI = checker('ai_disclosure')
WRITING = {'tool': 'Synthetic model', 'role': 'Language revision', 'use': 'writing',
           'purpose': 'improve the clarity of the Discussion', 'version': 'v1', 'developer': 'Synthetic Inc'}


def ai_check(project):  # noqa: F811
    sign(project)
    return next(c for c in verify(project, 'submission')['checks'] if c['check'] == 'ai_disclosure')


@pytest.mark.parametrize('record, message', [
    ({'used': False, 'reviewed_by': 'R'}, None),
    ({'used': True, 'reviewed_by': 'R', 'disclosure': 'Used a model.', 'tools': [{'tool': 'M', 'role': 'editing'}]}, None),
    ({'used': True, 'reviewed_by': 'R', 'tools': [dict(WRITING, use='grammar')]}, None),
    ({'used': True, 'reviewed_by': 'R', 'tools': [dict(WRITING, use='grammar'), WRITING]}, 'disclosure required'),
    ({'used': True, 'reviewed_by': 'R', 'tools': [{'tool': 'M', 'role': 'editing'}]}, 'disclosure required'),
    ({'used': False, 'reviewed_by': 'R', 'tools': [WRITING]}, 'conflicts'),
    ({'used': False, 'reviewed_by': 'R', 'disclosure': 'x'}, 'conflicts'),
    ({'used': True, 'reviewed_by': ['R'], 'disclosure': 'x', 'tools': [WRITING]}, 'reviewed_by'),
    ({'used': True, 'reviewed_by': 'R', 'disclosure': 'x', 'tools': [dict(WRITING, tool=3)]}, 'tool and role'),
    ({'used': True, 'reviewed_by': 'R', 'disclosure': 'x', 'tools': [dict(WRITING, use='drafting')]}, '.use: expected'),
    ({'used': True, 'reviewed_by': 'R', 'disclosure': 'x', 'tools': [dict(WRITING, purpose='')]}, '.purpose'),
    ({'used': True, 'reviewed_by': 'R', 'disclosure': 'x', 'tools': [dict(WRITING, version=2)]}, '.version'),
    ({'used': True, 'reviewed_by': 'R', 'disclosure': 'x', 'tools': [dict(WRITING, use='figure')]}, '.figures: name'),
    ({'used': True, 'reviewed_by': 'R', 'disclosure': 'x', 'tools': [dict(WRITING, figures=['f.png'])]}, 'only for use'),
    ({'used': True, 'reviewed_by': 'R', 'disclosure': 'x',
      'tools': [dict(WRITING, use='figure', figures=['f.png', 'f.png'])]}, 'distinct'),
    ({'used': True, 'reviewed_by': 'R', 'tools': [dict(WRITING, use='grammar')], 'disclosure': ['x']}, 'must be text'),
    ({'used': True, 'reviewed_by': 'R', 'tools': [dict(WRITING, use='grammar')], 'disclosure': 'Voluntary.'}, None),
    ({'used': False, 'reviewed_by': 'R', 'disclosure': ['lost']}, 'must be text'),
    ({'used': False, 'reviewed_by': 'R', 'tools': {}}, 'must be a list'),
    ({'used': True, 'reviewed_by': 'R', 'disclosure': 'x', 'tools': [dict(WRITING, use=None)]}, '.use: expected'),
    ({'used': True, 'reviewed_by': 'R', 'disclosure': 'x', 'tools': [dict(WRITING, use='research', figures=None)]},
     'distinct figure paths'),
])
def test_record_shape(record, message):
    problems = AI.record_problems(record)
    assert (not problems) if message is None else any(message in p for p in problems), problems


def test_prompt_logs_and_figures_must_resolve_inside_the_project(project, tmp_path):  # noqa: F811
    root = project.parent
    config = json.loads(project.read_text(encoding='utf-8'))
    put(root / 'review/ai_prompts/s1.md', 'prompt text')
    (root / 'review/ai_prompts/dir.md').mkdir()
    outside = tmp_path.parent / 'outside_prompt.md'
    outside.write_text('x', encoding='utf-8')
    os.symlink(outside, root / 'review/ai_prompts/link.md')
    cases = [('review/ai_prompts/s1.md', 'add review/ai_prompts/s1.md to project.dependencies'),
             ('review/ai_prompts/none.md', 'file not found'),
             ('review/ai_prompts/dir.md', 'is not a file'),
             (str(root / 'review/ai_prompts/s1.md'), 'project-relative'),
             ('../outside_prompt.md', 'project-relative'),
             ('review/ai_prompts/link.md', 'project-relative')]
    for prompts, message in cases:
        failures, blocked = AI.path_problems(root, config, {'tools': [dict(WRITING, prompts=prompts)]})
        assert any(message in p for p in failures + blocked), (prompts, failures, blocked)
    config['dependencies'] = ['review/ai_prompts/s1.md']
    assert AI.path_problems(root, config, {'tools': [dict(WRITING, prompts='review/ai_prompts/s1.md')]}) == ([], [])
    research = dict(WRITING, use='research', figures=['drafts/figures/figure_2.png'])
    assert 'not declared in project.figures' in AI.path_problems(root, config, {'tools': [research]})[0][0]


def test_submission_check_fails_bad_records_and_blocks_missing_prompt_logs(project):  # noqa: F811
    root = project.parent
    put(root / 'review/ai.json', {'used': True, 'reviewed_by': 'R', 'disclosure': 'Used a model.',
                                  'tools': [dict(WRITING, use='drafting')]})
    assert ai_check(project)['status'] == 'FAIL'
    put(root / 'review/ai.json', {'used': True, 'reviewed_by': 'R', 'disclosure': 'Used a model.',
                                  'tools': [dict(WRITING, prompts='review/ai_prompts/gone.md')]})
    check = ai_check(project)
    assert check['status'] == 'BLOCKED' and 'file not found' in check['detail']
    put(root / 'review/ai.json', {'used': True, 'reviewed_by': 'R', 'disclosure': 'Used a model.', 'tools': [WRITING]})
    assert ai_check(project)['status'] == 'PASS'


def test_preview_groups_by_destination_and_writes_nothing(project, capsys):  # noqa: F811
    root = project.parent
    record = {'used': True, 'reviewed_by': 'R', 'disclosure': 'x', 'tools': [
        WRITING, dict(WRITING, use='research', purpose='write the analysis code', developer=None),
        dict(WRITING, use='grammar', tool='Spell checker', purpose='spelling'), {'tool': 'Old model', 'role': 'editing'}]}
    record['tools'][1].pop('developer')
    put(root / 'review/ai.json', record)
    before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
    assert AI.main(['--project', str(project)]) == 0
    out = capsys.readouterr().out
    assert 'PROPOSAL FOR AUTHOR REVIEW' in out
    assert 'used Synthetic model (v1; Synthetic Inc) in order to improve the clarity of the Discussion.' in out
    assert 'Synthetic model (v1) was used to write the analysis code.  [record the developer]' in out
    assert 'Not declared' in out and 'Spell checker' in out and 'Unclassified' in out and 'Old model' in out
    assert before == {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
    assert AI.main(['--project', str(project), '--check']) == 0


def test_cli_needs_a_paper_folder(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert AI.main([]) == 2 and 'paper folder' in capsys.readouterr().err


def cite(project):  # noqa: F811
    put(project.parent / 'knowledge/evidence.md', '# Evidence\n\n### [1] Zed 2020\n- **Evidence ID:** zed_2020\n'
        '- **Citation:** Zed A, Young B. Later trial. Spine. 2020;45(1):1-9.\n- **Source Status:** verified\n')
    put(project.parent / 'drafts/03_introduction.md',
        '# Introduction\n\nAn important clinical question remains unresolved [EVID:zed_2020].\n')


def test_build_puts_the_declaration_between_the_body_and_the_references(project):  # noqa: F811
    root = project.parent
    cite(project)
    put(root / 'review/ai.json', {'used': True, 'reviewed_by': 'R', 'disclosure': 'Approved declaration text.',
                                  'tools': [WRITING]})
    sign(project)
    out = build(project)
    text = next(out.glob('manuscript_*.md')).read_text(encoding='utf-8')
    assert text.count(AI.DECLARATION_TITLE) == 1
    assert text.index('Mean age') < text.index(AI.DECLARATION_TITLE) < text.index('Approved declaration text.') \
        < text.index('# References') < text.index('Zed A, Young B')
    from docx import Document
    paragraphs = [p.text for p in Document(next(out.glob('manuscript_*.docx'))).paragraphs]
    title = paragraphs.index(AI.DECLARATION_TITLE)
    assert paragraphs[title + 1] == 'Approved declaration text.'
    assert max(i for i, p in enumerate(paragraphs) if 'Mean age' in p) < title < paragraphs.index('References')


def test_tracked_baseline_shows_the_declaration_move_and_stays_unchanged(project):  # noqa: F811
    root = project.parent
    cite(project)
    put(root / 'review/ai.json', {'used': True, 'reviewed_by': 'R', 'disclosure': 'Approved declaration text.',
                                  'tools': [WRITING]})
    baseline = put(root / 'output/submitted/manuscript.md', '# Introduction\n\nAn important clinical question remains '
                   'unresolved.\n\n# Results\n\nMean age was 54 years.\n\n# References\n\nZed A.\n\n'
                   '# AI assistance disclosure\n\nApproved declaration text.\n')
    before = baseline.read_bytes()
    config = json.loads(project.read_text(encoding='utf-8'))
    config['tracked_baseline'] = 'output/submitted/manuscript.md'
    put(project, config)
    sign(project)
    out = build(project)
    assert list(out.glob('manuscript_*_tracked.docx')) and baseline.read_bytes() == before


def test_cli_reports_a_malformed_manifest_as_input_error(project, capsys):  # noqa: F811
    root = project.parent
    put(root / 'review/ai.json', {'used': True, 'reviewed_by': 'R', 'disclosure': 'x', 'tools': [WRITING]})
    config = json.loads(project.read_text(encoding='utf-8'))
    put(project, dict(config, figures=None))
    assert AI.main(['--project', str(project), '--check']) == 2 and '"figures" must be a list' in capsys.readouterr().err
    put(project, '[]')
    assert AI.main(['--project', str(project), '--check']) == 2 and 'JSON object' in capsys.readouterr().err


def test_figure_captions_remind_missing_version_and_developer():
    tool = {'tool': 'Diagram model', 'role': 'flow chart', 'use': 'figure', 'purpose': 'draw the flow chart',
            'figures': ['drafts/figures/figure_1.png']}
    text = AI.preview({'used': True, 'reviewed_by': 'R', 'disclosure': 'x', 'tools': [tool]})
    assert 'figure_1.png: Created with the assistance of Diagram model (draw the flow chart).  [record the version and developer]' in text


def test_grammar_only_without_disclosure_builds_no_section(project):  # noqa: F811
    root = project.parent
    put(root / 'review/ai.json', {'used': True, 'reviewed_by': 'R', 'tools': [dict(WRITING, use='grammar')]})
    sign(project)
    out = build(project)
    assert AI.DECLARATION_TITLE not in next(out.glob('manuscript_*.md')).read_text(encoding='utf-8')

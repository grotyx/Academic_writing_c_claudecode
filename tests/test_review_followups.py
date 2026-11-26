"""v1.10.11: the remaining findings of the independent reviews (261126). Synthetic data."""
import json
from pathlib import Path

import pytest

from harness.build import build
from harness.project import checker
from manuwright import lifecycle, obsidian
from tests.test_harness import project, put, sign  # noqa: F401  (fixture)

GATE = checker('check_gate')


def test_revision_claims_never_fall_back_to_the_engine_drafts(tmp_path, monkeypatch):
    rc = checker('check_revision_claims')
    monkeypatch.chdir(tmp_path)
    assert rc.infer_draft_root(tmp_path / 'letter.md') == tmp_path / 'drafts'
    paper = tmp_path / 'revision' / 'paper'
    letter = paper / 'drafts' / 'revision' / 'REV1' / 'response_letter_REV1.md'
    assert rc.infer_draft_root(letter) == (paper / 'drafts').resolve()


def test_live_number_check_needs_its_results_folder(tmp_path):
    (tmp_path / 'a.md').write_text('Prose only.\n', encoding='utf-8')
    with pytest.raises(FileNotFoundError):
        GATE.run_live_check('numbers', Path('a.md'), base_dir=tmp_path, results_dir=Path('missing'))


def test_gate_round_must_be_a_number_and_artifact_hash_is_always_checked(tmp_path):
    (tmp_path / 'paper.md').write_text('x\n', encoding='utf-8')
    gate = tmp_path / 'g.GATE.md'
    gate.write_text('artifact: paper.md\nstatus: PASS\nround: two\n', encoding='utf-8')
    assert any(f.field == 'round' for f in GATE.check_gate(gate, base_dir=tmp_path).failures)
    gate.write_text(f'artifact: paper.md\nstatus: PASS\nprovenance:\n  artifact: {"0" * 64}\n', encoding='utf-8')
    assert any('stale gate' in f.reason for f in GATE.check_gate(gate, base_dir=tmp_path).failures)
    digest = GATE.sha256_file(tmp_path / 'paper.md')
    gate.write_text(f'artifact: paper.md\nstatus: PASS\nprovenance:\n  artifact: {digest}\n', encoding='utf-8')
    assert GATE.check_gate(gate, base_dir=tmp_path).passed


def test_two_supplements_with_the_same_output_name_stop_the_build(project):  # noqa: F811
    root = project.parent
    put(root / 'drafts/supp_table_1.md', '# Supplementary Table 1\n\nA.\n')
    put(root / 'drafts/supplementary_table_1.md', '# Supplementary Table 1\n\nB.\n')
    config = json.loads(project.read_text(encoding='utf-8'))
    put(project, dict(config, supplements=['drafts/supp_table_1.md', 'drafts/supplementary_table_1.md']))
    from harness.project import load_project
    with pytest.raises(ValueError, match='would both be built'):  # since v1.10.14 already at load, before any review
        load_project(project)


def test_supplementary_mentions_are_not_main_tables(tmp_path):
    cr = checker('check_crossrefs')
    (tmp_path / 'a.md').write_text('See Supplementary Table 2 and Table 1-3, and Figure 2-1.\n', encoding='utf-8')
    found = [(m.kind, m.number) for m in cr.find_mentions(tmp_path / 'a.md')]
    assert ('table', 2) not in found[:1] and found.count(('table', 2)) == 1  # only from "Table 1-3"
    assert ('figure', 1) in found and ('figure', 2) in found
    (tmp_path / 'b.md').write_text('Figure 1-999999.\n', encoding='utf-8')
    assert len(cr.find_mentions(tmp_path / 'b.md')) == 2


def test_style_rewrite_that_swaps_group_values_needs_review():
    acad = checker('academic_style')
    before, after = 'Group A had 10 deaths. Group B had 20 deaths.', 'Group A had 20 deaths. Group B had 10 deaths.'
    assert acad.preserve_problems(before, after) == [] and acad.order_problem(before, after)
    assert acad.order_problem(before, 'In group A, 10 died. In group B, 20 died.') is None


def test_registry_keeps_every_paper(tmp_path):
    for name in ('a', 'b', 'c'):
        put(tmp_path / name / 'project.json', '{}')
        lifecycle.register(tmp_path / name / 'project.json')
    known = json.loads((lifecycle.home() / 'projects.json').read_text(encoding='utf-8'))
    assert len(known) == 3 and not (lifecycle.home() / 'projects.lock').exists()


def test_update_installs_from_pypi_when_it_has_the_release(monkeypatch):
    monkeypatch.setattr(lifecycle, 'on_pypi', lambda tag: True)
    assert lifecycle.install_command('9.9.9')[-1] == 'manuwright==9.9.9'
    monkeypatch.setattr(lifecycle, 'on_pypi', lambda tag: False)
    assert lifecycle.install_command('9.9.9')[-1].endswith('@v9.9.9')


def test_response_coverage_reads_markdown_headings():
    cov = checker('check_response_coverage')
    assert cov.REVIEWER_RE.match('# Reviewer 1') and cov.COMMENT_RE.match('### Comment 2')


def test_lint_skips_multiline_comments(tmp_path):
    lint = checker('lint_manuscript')
    (tmp_path / 'drafts').mkdir()
    path = tmp_path / 'drafts' / '05_results.md'
    path.write_text('# Results\n\n<!--\nnote: utilize [TODO]\n-->\nPain decreased.\n', encoding='utf-8')
    assert not [i for i in lint.lint_file(path, {'utilize': 'use'}) if i[0] in ('PLACEHOLDER', 'TERMINOLOGY')]


def test_obsidian_citekeys_become_valid_evidence_ids():
    assert obsidian.evidence_id('smith:2020') == 'smith_2020' and obsidian.evidence_id('kim_2021') == 'kim_2021'


def test_obsidian_references_folder_stays_in_the_vault(tmp_path):
    settings = tmp_path / '.obsidian' / 'plugins' / obsidian.PLUGIN_ID / 'data.json'
    put(settings, {'referencesFolder': '../..'})
    assert obsidian.references_folder(tmp_path) == tmp_path / 'References'


def test_library_sync_leaves_a_signed_paper_alone(project):  # noqa: F811
    sync = checker('library_sync')
    assert not sync.signed_off(project.parent)
    sign(project)
    assert sync.signed_off(project.parent)


def test_lint_hook_reads_every_file_of_a_patch(tmp_path, monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location('lint_on_edit', Path(__file__).resolve().parents[1] / 'scripts/hooks/lint_on_edit.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    seen = []
    monkeypatch.setattr(module, 'evaluate_path', lambda event, path: seen.append(path) or (0, ''))
    patch = '*** Begin Patch\n*** Update File: drafts/03_introduction.md\n+a\n*** Add File: drafts/05_results.md\n+b\n*** End Patch\n'
    module.evaluate({'tool_name': 'apply_patch', 'tool_input': {'patch': patch}})
    assert seen == ['drafts/03_introduction.md', 'drafts/05_results.md']


DISCUSSION = ('In this trial, endoscopic decompression was associated with less leg pain at 12 months. The difference was small.\n\n'
              'These results are consistent with previous studies that reported similar outcomes. Other trials agreed.\n\n'
              'This may be explained by less muscle injury, because the approach spares the multifidus. It is plausible.\n\n'
              'This study has limitations. Selection bias cannot be excluded in a two-centre cohort of this size.\n\n'
              'In conclusion, endoscopic decompression was associated with less pain. Further trials are needed.\n')


def test_paragraph_flow_is_measured_and_compared():
    acad = checker('academic_style')
    assert acad.flow_of('discussion', DISCUSSION) == ['principal', 'comparison', 'mechanism', 'limitation', 'conclusion']
    assert any('Flow matches' in line for line in acad.flow_report('discussion', DISCUSSION, None))
    parts = DISCUSSION.strip().split('\n\n')
    moved = '\n\n'.join([parts[0], parts[3], parts[1], parts[2], parts[4]])
    assert any('limitation comes before comparison' in line for line in acad.flow_report('discussion', moved, None))
    learned = acad.learn_flow('discussion', [DISCUSSION, DISCUSSION, moved])
    assert learned['papers'] == 3 and learned['kept'] == 2 and learned['typical'][0] == 'principal'


def test_learned_flow_reaches_the_card(tmp_path, monkeypatch):
    acad = checker('academic_style')
    corpus = tmp_path / 'corpus'
    corpus.mkdir()
    for i in range(3):
        (corpus / f'paper{i}.md').write_text(
            '# Introduction\n\n' + 'Back pain is common and costly for many patients in clinics. ' * 12 + '\n\n'
            '# Discussion\n\n' + DISCUSSION + '\n' + 'Patients improved in both groups over the follow-up period. ' * 8,
            encoding='utf-8')
    profile = acad.learn([corpus], tmp_path / 'profile')
    assert profile['sections']['discussion']['flow']['typical'][:2] == ['principal', 'comparison']


def test_max_round_must_be_a_real_limit(tmp_path):
    import subprocess
    import sys
    gate = tmp_path / 'g.GATE.md'
    gate.write_text('artifact: paper.md\nstatus: PASS\nround: 5\n', encoding='utf-8')
    for bad in (0, -1):
        with pytest.raises(ValueError, match='1 or more'):
            GATE.check_gate(gate, max_round=bad)
    assert any('exceeds max 2' in f.reason for f in GATE.check_gate(gate, max_round=2).failures)
    script = Path(__file__).resolve().parents[1] / 'scripts' / 'check_gate.py'
    done = subprocess.run([sys.executable, str(script), str(gate), '--max-round', '0'], capture_output=True, text=True)
    assert done.returncode == 2 and '1 or more' in done.stderr and 'Traceback' not in done.stderr


# --- code review of v1.10.9-v1.10.13 (261126) ---

def test_state_cannot_replace_a_review_or_approval_receipt(project):  # noqa: F811
    from harness.project import load_project
    config = json.loads(project.read_text(encoding='utf-8'))
    for state in ('review/semantic.json', 'review/human.json', 'review/x.approval.json'):
        put(project, dict(config, state=state))
        with pytest.raises(ValueError, match='state must be'):
            load_project(project)


def test_revision_claims_resolve_project_paths_in_a_multi_paper_layout(tmp_path):
    rc = checker('check_revision_claims')
    draft_root = tmp_path / 'drafts' / 'paper1_x'
    revised = draft_root / 'revision' / 'REV1' / '05_results_REV1.md'
    put(revised, '# Results\n')
    letter = draft_root / 'revision' / 'REV1' / 'response_letter_REV1.md'
    put(letter, 'x')
    claim = rc.ChangeClaim('R1-C1', 'x', 'drafts/paper1_x/revision/REV1/05_results_REV1.md', [], '', {})
    assert rc.paper_root(draft_root) == tmp_path.resolve()
    assert rc.resolve_revised_section_path(claim, letter, rc.infer_draft_root(letter)) is not None
    assert rc.infer_draft_root(tmp_path / 'review' / 'letter.md', default=tmp_path / 'drafts') == tmp_path / 'drafts'


@pytest.mark.parametrize('path, blocked', [('drafts/table_2_results.md', False), ('drafts/discussion_notes.md', False),
                                           ('drafts/supp_methods.md', False), ('drafts/results.md', True),
                                           ('drafts/discussion_REV1.md', True)])
def test_only_section_names_need_the_draft_plan(tmp_path, path, blocked):
    from tests.test_enforce_gates import load_module
    event = {'tool_name': 'Write', 'cwd': str(tmp_path), 'tool_input': {'file_path': path, 'content': 'x'}}
    assert bool(load_module().decide(event)) is blocked, path


def test_run_checks_a_renamed_analysis_plan_as_an_analysis_plan(tmp_path):
    from tests.test_enforce_gates import ANALYSIS_CONTENT, load_module
    plan = put(tmp_path / 'data' / 'analysis_plan_v2.md', ANALYSIS_CONTENT + '\n- [ x ] 사용자 승인 완료\n')
    gates = load_module()
    assert gates.plan_problem(plan, 'analysis') is None
    assert checker('plan_validation').has_checked_approval(plan.read_text(encoding='utf-8'))


@pytest.mark.parametrize('text', ['We enrolled 2024 (52%) women.', 'The cohort comprised 2024.', '| Total | 2024 |',
                                  'Of 2024 patients, half improved.'])
def test_year_sized_counts_followed_by_punctuation_are_checked(tmp_path, text):
    from tests.test_grounding_gaps import numbers
    result = numbers(tmp_path, text, csv='estimate\n52\n')
    assert not result.passed, text


@pytest.mark.parametrize('text', ['Smith (2020) reported this.', 'Data from 2015 to 2020 were used.',
                                  'It was described earlier (Kim and Lee, 2019).', 'The 2016 WHO classification was used.',
                                  'Records 2015–2020 were reviewed.'])
def test_year_contexts_stay_exempt(tmp_path, text):
    from tests.test_grounding_gaps import numbers
    assert numbers(tmp_path, text).passed, text


def test_flow_positions_ignore_repeats():
    acad = checker('academic_style')
    gap = 'However, little is known about this question in older adults. Few studies exist.'
    aim = 'We aimed to compare the two treatments in a cohort of older adults. We report it here.'
    other = 'Pain was measured with a visual scale in every clinic visit. Scores ranged widely.'
    text = '\n\n'.join([gap, other, gap, aim])
    assert acad.flow_of('introduction', text) == ['gap', 'aim']


def test_paper_id_rule_is_shared():
    from harness.results import plain_name
    from manuwright import analysis_env
    for bad in (' ..', 'a/b', '', '..', ' x'):
        assert not plain_name(bad)
        with pytest.raises(ValueError):
            analysis_env.env_dir(bad)
    assert plain_name('paper1_spine')


# --- AGY Carbon re-review of v1.10.13 (261126) ---

@pytest.mark.parametrize('text', ['| Group | N |\n|---|---|\n| Total | 2024 |', 'Total enrollment was 2024.',
                                  'We enrolled 2024 MRI-confirmed patients.', 'Enrollment reached up to 2024 patients.',
                                  'The change was –2.5 points.', 'The difference was significant (*p value* < 0.05).',
                                  '| Outcome | Adjusted *P* value |\n|---|---|\n| Pain | <0.05 |',
                                  'In Korea, 2024 patients were treated.', 'In 2019 patients with stenosis, pain fell.'])
def test_rereview_numbers_that_must_be_checked(tmp_path, text):
    from tests.test_grounding_gaps import numbers
    assert not numbers(tmp_path, text, csv='estimate,p\n2.5,0.054\n').passed, text


@pytest.mark.parametrize('text', ['Patients treated in 2018–2022 were included.', 'A 2020 meta-analysis reported it.',
                                  'In a 2019 randomized trial, surgery helped.', 'Smith et al., 2020 reported fewer events.',
                                  'Follow-up ended on 2021/03/12 for the last patient.', 'Baseline data are in Tables 1 and 2.',
                                  'Figures 1–3 show the data.'])
def test_rereview_dates_and_lists_that_are_not_results(tmp_path, text):
    from tests.test_grounding_gaps import numbers
    assert numbers(tmp_path, text, csv='estimate\n25.0\n').passed, text


def test_markdown_heading_letters_are_parsed_entry_by_entry(tmp_path):
    cov = checker('check_response_coverage')
    comments = put(tmp_path / 'comments.md', '# Reviewer 1\n### Comment 1\nClarify N.\n### Comment 2\nAdd limitation.\n')
    unanswered = put(tmp_path / 'u.md', '# Reviewer 1\n### Comment 1\nResponse: Clarified.\n### Comment 2\n')
    assert not cov.check_response_coverage(unanswered).passed
    full = put(tmp_path / 'f.md', '# Reviewer 1\n### Comment 1\nResponse: Clarified.\n### Comment 2\nResponse: Added.\n')
    assert cov.check_response_coverage(full, comments_path=comments, strict=True).passed


@pytest.mark.parametrize('text', ['# Plan\n~~~\n- [x] 사용자 승인 완료\n~~~\n', '# Plan\nTick `- [x] 사용자 승인 완료` after review.\n',
                                  '# Plan\n<!--\n- [x] 사용자 승인 완료\n', '- [x] 사용자 승인 완료\n- [ ] 사용자 승인 완료\n'])
def test_hidden_or_contradicted_ticks_are_not_approvals(text):
    assert not checker('plan_validation').has_checked_approval(text)


def test_approve_never_ticks_an_example_inside_a_comment(tmp_path):
    from harness.__main__ import approve_in_chat
    from tests.test_enforce_gates import ANALYSIS_CONTENT
    plan = put(tmp_path / 'data' / 'analysis_plan.md',
               '<!-- Example: - [ ] 사용자 승인 완료 -->\n' + ANALYSIS_CONTENT + '\n- [ ] 사용자 승인 완료\n')
    approve_in_chat(plan, 'analysis', 'Dr Kim', 'approved')
    text = plan.read_text(encoding='utf-8')
    assert text.startswith('<!-- Example: - [ ] 사용자 승인 완료 -->') and checker('plan_validation').has_checked_approval(text)


def test_revision_sections_never_leave_a_paper_without_drafts(tmp_path):
    rc = checker('check_revision_claims')
    put(tmp_path / 'outside_secret.md', 'Secret text with pain.')
    letter = put(tmp_path / 'rev_paper' / 'revision' / 'REV1' / 'response_letter_REV1.md', 'x')
    claim = rc.ChangeClaim('R1-C1', 'x', '../../../outside_secret.md', ['pain'], '', {})
    assert rc.resolve_revised_section_path(claim, letter, rc.infer_draft_root(letter)) is None


@pytest.mark.parametrize('path, blocked', [('data/py/models/01_cox.py', True), ('data/py/report.Rmd', True),
                                           ('data/py/report.qmd', True)])
def test_nested_and_notebook_analysis_scripts_need_a_plan(tmp_path, path, blocked):
    from tests.test_enforce_gates import load_module
    assert bool(load_module().decide_path(str(tmp_path), path)) is blocked


def test_hook_finds_the_paper_plan_and_ignores_folders_named_drafts_above_it(tmp_path):
    from tests.test_enforce_gates import ANALYSIS_CONTENT, load_module
    gates = load_module()
    paper = tmp_path / 'drafts' / 'my-paper'
    put(paper / 'data' / 'analysis_plan.md', ANALYSIS_CONTENT + '\n- [x] 사용자 승인 완료\n')
    assert gates.decide_path(str(paper), 'data/models/01_cox.py') is None
    assert gates.decide_path(str(paper), 'knowledge/methods.md') is None
    assert 'Rule 8' in gates.decide_path(str(paper), 'drafts/methods.md')


def test_update_refuses_a_flag_where_a_version_belongs(capsys):
    from manuwright import cli
    assert cli.main(['update', '--to', '--no-agents']) == 2 and '--to needs a value' in capsys.readouterr().err


def test_blind_anchor_quotes_stay_in_revised_and_upgrades_need_one(tmp_path):
    br = checker('blind_review')
    put(tmp_path / 'revised' / '05_results_REV1.md', 'Pain decreased (*p* < 0.05).')
    put(tmp_path / 'reviewer_comments.md', 'Comment 1) Please show pain decreased.')
    assert 'not in revised/' in br.quote_problem(tmp_path, '../reviewer_comments.md: "Please show pain decreased."')
    assert br.quote_problem(tmp_path, '05_results_REV1.md: "Pain decreased (p < 0.05)."') is None
    assert 'quotes text' in br.quote_problem(tmp_path, "05_results_REV1.md: 'fabricated quote'")
    assert 'must name a revised file' in br.quote_problem(tmp_path, 'see letter', required=True)


def test_gate_round_below_one_and_orphan_artifact_hash_fail(tmp_path):
    gate = tmp_path / 'g.GATE.md'
    gate.write_text('artifact: paper.md\nstatus: PASS\nround: -3\n', encoding='utf-8')
    assert any(f.field == 'round' for f in GATE.check_gate(gate, base_dir=tmp_path).failures)
    gate.write_text(f'status: PASS\nprovenance:\n  artifact: {"0" * 64}\n', encoding='utf-8')
    assert any(f.field == 'artifact' for f in GATE.check_gate(gate, base_dir=tmp_path).failures)


def test_preserve_reads_thousands_and_two_character_comparators():
    acad = checker('academic_style')
    assert acad.preserve_problems('We enrolled 1,250 patients.', 'We enrolled 1250 patients.') == []
    assert acad.preserve_problems('Patients aged >= 65 had p <= 0.05.', 'Patients aged <= 65 had p >= 0.05.')
    assert acad.prose_issues("# Results\n\n<!--\nNote: don't delve into **this** yet.\n-->\nPain decreased.\n",
                             'results') == []


def test_flow_keeps_one_sentence_paragraphs_and_reads_gap_questions():
    acad = checker('academic_style')
    intro = ('Lumbar stenosis is common in older adults and a leading cause of leg pain. Surgery is widely used.\n\n'
             'However, little is known about endoscopic surgery in this group. Few trials exist.\n\n'
             'Therefore, we aimed to compare endoscopic and open decompression in older adults.\n')
    assert acad.flow_of('introduction', intro) == ['background', 'gap', 'aim']
    assert acad.paragraph_move('introduction', 'Whether early decompression is a better option is an open '
                               'clinical question. Consensus is lacking in elderly patients.') == 'gap'


def test_crossrefs_do_not_invent_tables_from_data():
    cr = checker('check_crossrefs')
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / 'a.md'
        path.write_text('As shown in Table 1, 12 patients had complications. In Figure 2, 30-day mortality fell. '
                        'Extended Data Table 3 shows sensitivity.\n', encoding='utf-8')
        assert [(m.kind, m.number) for m in cr.find_mentions(path)] == [('table', 1), ('figure', 2)]


def test_commented_out_citations_are_not_numbered_and_bare_evid_fails(tmp_path):
    cc = checker('check_citations')
    put(tmp_path / 'ev.md', '# Evidence\n')
    a = put(tmp_path / 'a.md', '<!-- Removed [EVID:smith_2019] -->\nPain is common.\n')
    assert cc.iter_evid_tokens(a) == []
    b = put(tmp_path / 'b.md', 'Prior work (EVID:lee_2021) showed pain.\n')
    assert not cc.check_citations([b], evidence_path=tmp_path / 'ev.md').passed


def test_bind_reads_typographic_bounds(tmp_path):
    bind = checker('bind_results')
    put(tmp_path / 'results' / 'p.csv', 'outcome,p\npain,≤0.001\n')
    cell = bind.cells(tmp_path, tmp_path / 'results')[0]
    assert cell['number'].raw == '<=0.001'

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
    sign(project)
    with pytest.raises(ValueError, match='would both be built'):
        build(project)


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

"""Adversarial cases from the 2026-09-06 review; all data are synthetic."""
import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name.replace('/', '_'), ROOT / 'scripts' / (name + '.py'))
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


@pytest.mark.parametrize('status', ['unverified', 'retracted', 'typo'])
def test_invalid_source_status_fails(tmp_path, status):
    m = module('check_citations')
    art, ev = tmp_path/'draft.md', tmp_path/'evidence.md'
    art.write_text('Claim [EVID:kim_2020]')
    ev.write_text(f'### [EVID:kim_2020]\n- **Source Status:** {status}\n')
    assert not m.check_citations([art], evidence_path=ev).passed


def test_duplicate_source_fails_without_overwriting(tmp_path):
    m = module('check_citations')
    art, ev = tmp_path/'draft.md', tmp_path/'evidence.md'
    art.write_text('Claim [EVID:kim_2020]')
    ev.write_text('### [EVID:kim_2020]\n- **Source Status:** todo\n'
                  '### [EVID:kim_2020]\n- **Source Status:** verified\n')
    assert not m.check_citations([art], evidence_path=ev).passed


def test_importer_disambiguates_same_author_year():
    m = module('search_pubmed')
    def eid(pmid):
        import re
        article = dict(first_author='Kim', year='2020', title='Study', authors=['Kim A'], pmid=pmid)
        return re.search(r'Evidence ID:\*\* (.+)', m.format_evidence_entry(article, 1)).group(1)
    assert eid('100') != eid('200')


@pytest.mark.parametrize('source,claim,expected', [
    ('<0.001', '= 0.001', False), ('<=0.001', '< 0.001', False),
    ('>=0.05', '> 0.05', False), ('0.0004', '= 0.000', False),
    ('<0.001', '<=0.001', True), ('<=0.001', '<0.01', True),
    ('0.0004', '<0.001', True), ('0.05', '=0.05', True),
])
def test_p_value_entailment(tmp_path, source, claim, expected):
    m = module('check_numbers')
    rd=tmp_path/'results'; rd.mkdir()
    (rd/'table.csv').write_text(f'p_value\n{source}\n')
    art=tmp_path/'draft.md'; art.write_text(f'The effect had p {claim}.')
    assert m.check_numbers([art], results_dir=rd).passed is expected


def test_placeholder_does_not_hide_other_numbers(tmp_path):
    m=module('check_numbers')
    rd=tmp_path/'results';rd.mkdir();(rd/'table.csv').write_text('age\n54\n')
    art=tmp_path/'draft.md';art.write_text('XX patients had a mean age of 999.')
    result=m.check_numbers([art],results_dir=rd)
    assert not result.passed
    assert result.checked_numbers == 1
    assert any(f.number=='999' for f in result.failures)


def test_gate_is_bound_to_declared_artifact(tmp_path):
    m=module('check_gate')
    bad,good=tmp_path/'bad.md',tmp_path/'good.md'
    bad.write_text('999 patients.');good.write_text('54 patients.')
    rd=tmp_path/'results';rd.mkdir();(rd/'table.csv').write_text('n\n54\n')
    gate=tmp_path/'phase_04.GATE.md'
    gate.write_text(f'artifact: {bad}\nstatus: PASS\nchecks:\n  numbers: PASS\n'
                    f'provenance:\n  artifact: {m.sha256_file(good)}\n')
    result=m.check_gate(gate, artifact=str(bad), required_checks=['numbers'],
                         verify_hashes=[('artifact',good)], cross_checks=[('numbers',good)],results_dir=rd)
    assert not result.passed
    assert any('artifact mismatch' in f.reason for f in result.failures)


def test_checkbox_only_plan_rejected(tmp_path):
    m=module('hooks/enforce_gates')
    plan=tmp_path/'draft_plan.md';plan.write_text('- [x] 사용자 승인 완료\n',encoding='utf-8')
    assert m.plan_problem(plan) is not None


def test_rev2_compares_to_latest_prior_section(tmp_path):
    m=module('check_revision_claims')
    draft=tmp_path/'drafts';rev1=draft/'revision'/'REV1';rev1.mkdir(parents=True)
    rev2=draft/'revision'/'REV2';rev2.mkdir()
    (draft/'04_methods.md').write_text('Original text.')
    prior='Original text. Sensitivity analysis was added.'
    (rev1/'04_methods_REV1.md').write_text(prior)
    (rev2/'04_methods_REV2.md').write_text(prior)
    response=rev2/'response_letter_REV2.md'
    response.write_text('[CHANGE]\ncomment_id: 1.1\nclaim: Added sensitivity analysis\n'
                        'section: 04_methods\nexpected_terms: sensitivity analysis\n[/CHANGE]\n')
    assert not m.check_revision_claims(response,strict=True).passed


def test_missing_openrouter_key_keeps_claude(tmp_path):
    m=module('critical_review')
    art=tmp_path/'draft.md';art.write_text('Synthetic draft')
    with patch.dict(os.environ,{},clear=True), patch.object(sys,'argv',[
        'critical_review.py','--target',str(art),'--models','example/model','--include-claude']), \
        patch.object(m,'call_claude_cli',return_value='Review') as call:
        assert m.main()==0
        call.assert_called_once()


@pytest.mark.parametrize('claim,expected', [('= 0.001', False), ('< 0.001', True)])
def test_pipe_table_p_bounds(tmp_path, claim, expected):
    m = module('check_numbers')
    rd = tmp_path/'results'; rd.mkdir()
    (rd/'table.csv').write_text('p_value\n<0.001\n')
    art = tmp_path/'draft.md'
    art.write_text('| Outcome | p-value |\n| --- | --- |\n| Fusion | '+claim+' |\n')
    assert m.check_numbers([art],results_dir=rd).passed is expected


def test_scientific_p_value(tmp_path):
    m = module('check_numbers')
    rd = tmp_path/'results'; rd.mkdir()
    (rd/'table.csv').write_text('p_value\n0.0004\n')
    art = tmp_path/'draft.md'; art.write_text('The effect had p = 4e-4.')
    result = m.check_numbers([art],results_dir=rd)
    assert result.passed
    assert result.checked_numbers == 1


def test_standard_agent_bootstraps_exist():
    for name in ('AGENTS.md', 'CLAUDE.md', 'GEMINI.md'):
        assert (ROOT/name).is_file()
        assert 'WORKFLOW.md' in (ROOT/name).read_text(encoding='utf-8')
    assert 'AGENTS.MD' not in [p.name for p in ROOT.iterdir()]


@pytest.mark.parametrize('header', ['12-month outcome', 'Group 1 (n=40)', 'Outcome'])
@pytest.mark.parametrize('claim,expected', [('=0.001',False), ('<0.001',True)])
def test_numeric_table_headers_preserve_p_bounds(tmp_path, header, claim, expected):
    m=module('check_numbers')
    rd=tmp_path/'results';rd.mkdir()
    (rd/'p.csv').write_text('p_value,n,group\n<0.001,40,1\n',encoding='utf-8')
    artifact=tmp_path/'table.md'
    artifact.write_text(f'| {header} | p-value |\n| --- | --- |\n| Fusion | {claim} |\n',encoding='utf-8')
    assert m.check_numbers([artifact],results_dir=rd).passed is expected


# --- 2026-10-07 review and synthetic end-to-end run (v1.9.2) ---------------------------------

@pytest.mark.parametrize('before,after', [
    ('(P < .001)', '(P > .001)'),               # capital P
    ('mean difference -1.2', 'mean difference 1.2'),  # sign
    ('aged ≥65', 'aged <65'),              # comparator
])
def test_style_preserve_catches_sign_comparator_and_capital_p(before, after):
    assert module('academic_style').preserve_problems(before, after)


@pytest.mark.parametrize('before,after', [
    ('*p* = 0.04', 'P = 0.04'),        # italics and case are formatting
    ('1.5-2.3', '1.5 to 2.3'),         # a range hyphen is not a minus sign
    ('value −1.2', 'value -1.2'),  # minus glyph
])
def test_style_preserve_ignores_formatting(before, after):
    assert module('academic_style').preserve_problems(before, after) == []


def test_claim_strength_grades_a_hard_wrapped_sentence_whole(tmp_path):
    m = module('check_claim_strength')
    ev, draft = tmp_path / 'evidence.md', tmp_path / '06_discussion.md'
    ev.write_text('### [1] Smith\n- **Evidence ID:** smith_2020\n- **Claim Strength:** observed\n', encoding='utf-8')
    draft.write_text('# Discussion\n\nDrug X reduced mortality and prevented\nfractures in older adults [EVID:smith_2020].\n',
                     encoding='utf-8')
    findings = m.check([draft], ev)
    assert len(findings) == 1 and findings[0][1] == 4 and 'causal' in findings[0][2]


def test_claim_strength_hedge_in_one_clause_does_not_soften_another():
    m = module('check_claim_strength')
    assert m.sentence_level('Drug X could not be shown to cause harm, but it prevented fractures.') == 3
    assert m.sentence_level('MIS-TLIF may reduce blood loss.') <= 1


def test_claim_strength_folder_skips_plans(tmp_path):
    m = module('check_claim_strength')
    (tmp_path / 'knowledge').mkdir(); (tmp_path / 'drafts').mkdir()
    (tmp_path / 'knowledge' / 'evidence.md').write_text(
        '### [1] A\n- **Evidence ID:** a_2020\n- **Claim Strength:** observed\n', encoding='utf-8')
    (tmp_path / 'drafts' / 'draft_plan.md').write_text('- X reduces Y -> A 2020 [EVID:a_2020]\n', encoding='utf-8')
    cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        assert m.main(['drafts']) == 0
    finally:
        os.chdir(cwd)


def test_audit_fails_a_doi_pubmed_does_not_know():
    m = module('search_pubmed')
    text = ('# Evidence\n\n### [1] Fake\n- **Evidence ID:** fake_2021\n- **DOI:** 10.9999/fake.1\n\n'
            '### [2] Bare\n- **Evidence ID:** bare_2020\n')
    rows = {r[0]: r for r in m.audit_evidence(text, fetch=lambda ids: [], resolve=lambda doi: None)}
    assert rows['fake_2021'][1] == 'failed' and rows['bare_2020'][1] == 'unchecked'


def test_style_edits_rerun_keeps_approved_rules(tmp_path):
    m = module('academic_style')
    pending = tmp_path / 'pending_style_rules.md'
    m.write_pending([('P0', 'utilized -> used', 2, 'replace')], pending)
    m.approve_pending(pending, ['utilized'], 'Author', 'keep it')
    m.write_pending([('P0', 'utilized -> used', 3, 'replace'), ('P2', 'very', 1, 'delete')], pending)
    text = pending.read_text(encoding='utf-8')
    assert '- [x] P0 replace "utilized" with "used"' in text and 'approved by Author' in text
    assert text.count('utilized') == 1 and '- [ ] P2 delete "very"' in text


def test_academic_check_accepts_a_folder(tmp_path):
    (tmp_path / 'drafts').mkdir()
    (tmp_path / 'drafts' / '06_discussion.md').write_text('# Discussion\n\nThis study delves into it.\n', encoding='utf-8')
    import subprocess
    done = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'academic_style.py'), 'check', 'drafts'],
                          cwd=tmp_path, capture_output=True, text=True, encoding='utf-8')
    assert 'Traceback' not in done.stderr and 'delves' in done.stdout


def test_forbidden_term_does_not_match_inside_a_hyphenated_compound(tmp_path):
    m = module('lint_manuscript')
    draft = tmp_path / '05_results.md'
    draft.write_text('# Results\n\nMIS-TLIF had lower blood loss. The MIS group was younger.\n', encoding='utf-8')
    found = [i for i in m.lint_file(draft, {'MIS': 'minimally invasive spine surgery (MISS)'}) if i[0] == 'TERMINOLOGY']
    assert len(found) == 1  # "MIS group" only


def test_superscript_citation_follows_punctuation_without_space():
    m = module('format_references')
    out = m.convert_text('pooled analyses [EVID:a][EVID:b]. Similar [EVID:c], and x', {'a': '1', 'b': '2', 'c': '3'},
                         'superscript')
    assert out == 'pooled analyses.^1,2^ Similar,^3^ and x'


def _blind_packet(tmp_path):
    m = module('blind_review')
    orig, rev = tmp_path / 'orig', tmp_path / 'rev'
    orig.mkdir(); rev.mkdir()
    (tmp_path / 'comments.md').write_text('Reviewer #1:\n\nComment 1) Report the CI.\n', encoding='utf-8')
    (orig / '05_results.md').write_text('# Results\n\nMean 4.0.\n', encoding='utf-8')
    (rev / '05_results.md').write_text('# Results\n\nMean 4.0 (95% CI 3.5 to 4.5).\n', encoding='utf-8')
    (rev / '08_reply_to_reviewers.md').write_text('Reviewer 1\n\nResponse: added.\n', encoding='utf-8')
    (rev / '09_notes.md').write_text('Reviewer #1 asked for a CI.\n\n**Response:** added.\n\nResponse: see Results.\n',
                                     encoding='utf-8')
    out = tmp_path / 'out'
    manifest = m.packet(tmp_path / 'comments.md', orig, rev, out)
    verdicts = out / 'verdicts.md'
    verdicts.write_text(verdicts.read_text(encoding='utf-8').replace('expectation: ', 'expectation: CI reported')
                        .replace('blind_verdict: ', 'blind_verdict: FULLY')
                        .replace('anchor: \n', 'anchor: 05_results.md: "95% CI"\n')
                        .replace('final_verdict: ', 'final_verdict: FULLY'), encoding='utf-8')
    return m, manifest, out, verdicts


def test_blind_packet_withholds_a_letter_by_name_or_by_content(tmp_path):
    m, manifest, out, verdicts = _blind_packet(tmp_path)
    assert manifest['revised_sections'] == ['05_results.md']
    assert m.check(verdicts) == []


def test_blind_check_fails_when_the_packet_changed_after_it_was_built(tmp_path):
    m, _manifest, out, verdicts = _blind_packet(tmp_path)
    (out / 'revised' / '05_results.md').write_text('tampered', encoding='utf-8')
    (out / 'revised' / '08_reply_to_reviewers.md').write_text('Reviewer 1\nResponse: a.\nResponse: b.\n', encoding='utf-8')
    problems = ' | '.join(m.check(verdicts))
    assert 'changed after the packet was built' in problems and 'added to the packet' in problems


def test_capital_p_is_accepted(tmp_path):
    m = module('lint_manuscript')
    draft = tmp_path / '05_results.md'
    draft.write_text('# Results\n\nThe difference was significant (*P* < 0.001).\n', encoding='utf-8')
    assert not [i for i in m.lint_file(draft, {}) if i[0] == 'STAT_FORMAT']


# --- 2026-11-02 review of v1.9.4..v1.9.11 (Claude and Codex) ---------------------------------

def test_journal_fit_reads_the_sections_project_json_declares(tmp_path):
    import json
    m = module('journal_fit')
    (tmp_path / 'drafts' / 'paper1').mkdir(parents=True)
    (tmp_path / 'drafts' / 'paper1' / '02_abstract.md').write_text('# Abstract\n\n' + 'word ' * 300, encoding='utf-8')
    (tmp_path / 'drafts' / 'paper1' / 'table_1.md').write_text('| a |\n', encoding='utf-8')
    (tmp_path / 'project.json').write_text(json.dumps({
        'abstract': 'drafts/paper1/02_abstract.md', 'artifacts': ['drafts/paper1/02_abstract.md'],
        'tables': ['drafts/paper1/table_1.md']}), encoding='utf-8')
    counts = m.measure(tmp_path)
    assert counts['abstract_words'] == 300 and counts['tables_figures'] == 1
    assert 'word word' in m.manuscript(tmp_path)


def test_journal_profile_alias_is_found_by_the_typed_name(tmp_path, monkeypatch):
    m = module('journal_fit')
    monkeypatch.setattr(m, 'library_journals', lambda: tmp_path)
    (tmp_path / 'spine-j.md').write_text('# Spine J\n', encoding='utf-8')
    m.remember_alias('The Spine Journal', 'Spine J')
    assert m.profile_path('The Spine Journal', None) == tmp_path / 'spine-j.md'


def test_nlm_lookup_survives_an_empty_article_list(monkeypatch):
    m = module('journal_fit')
    monkeypatch.setattr(m.pubmed, 'fetch_articles', lambda ids: [])
    assert m.nlm_abbreviation('Spine J', search=lambda term, n: (['123'], 1)) == ('', '')


def test_library_rule_lands_in_the_synced_table_once_and_backups_are_kept(tmp_path, monkeypatch):
    monkeypatch.setenv('MANUWRIGHT_HOME', str(tmp_path / 'home'))
    m = module('library_sync')
    terms = tmp_path / 'terminology.md'
    terms.write_text(f'# T\n\n{m.SECTION}\n\n{m.TABLE_HEAD}| used | utilized | x |\n\n## Local exceptions\n\nprose\n',
                     encoding='utf-8')
    for _ in range(3):
        m.add_rules(terms, {'demonstrated': ('showed', 'demonstrated', '')}, 'c')
    assert terms.read_text(encoding='utf-8').count('| showed | demonstrated |') == 1
    assert 'demonstrated' in m.rules(terms) and terms.read_text(encoding='utf-8').rstrip().endswith('prose')
    terms.write_text(terms.read_text(encoding='utf-8') + 'edited\n', encoding='utf-8')
    m.add_rules(terms, {'leverage': ('use', 'leverage', '')}, 'c')
    assert len(list(tmp_path.glob('terminology.md*.bak'))) == 2  # the earlier copy is not overwritten


def test_library_does_not_write_a_terminology_file_outside_the_paper(tmp_path, monkeypatch):
    import json
    monkeypatch.setenv('MANUWRIGHT_HOME', str(tmp_path / 'home'))
    m = module('library_sync')
    outside = tmp_path / 'shared_terms.md'
    paper = tmp_path / 'paper'
    paper.mkdir()
    (paper / 'project.json').write_text(json.dumps({'artifacts': [], 'terminology': str(outside)}), encoding='utf-8')
    assert m.paper_terminology(paper) is None
    report = m.remember_term('used', 'utilized', '', paper)
    assert any('outside the paper' in line for line in report) and not outside.exists()


def test_pubmed_requests_have_a_timeout():
    m = module('search_pubmed')
    assert m.TIMEOUT and 'timeout=TIMEOUT' in (ROOT / 'scripts' / 'search_pubmed.py').read_text(encoding='utf-8')


def test_backups_in_the_same_second_all_survive(tmp_path, monkeypatch):
    monkeypatch.setenv('MANUWRIGHT_HOME', str(tmp_path / 'home'))
    m = module('library_sync')
    target = tmp_path / 'terms.md'
    for content in 'ABCD':
        target.write_text(content, encoding='utf-8')
        m.keep_backup(target)
    assert sorted(p.read_text(encoding='utf-8') for p in tmp_path.glob('terms.md*.bak')) == list('ABCD')


def test_journal_fit_finds_the_abstract_by_its_role_and_names_missing_files(tmp_path):
    import json
    m = module('journal_fit')
    (tmp_path / 'drafts').mkdir()
    (tmp_path / 'drafts' / 'abstract.md').write_text('word ' * 300, encoding='utf-8')
    (tmp_path / 'project.json').write_text(json.dumps({'abstract': 'drafts/abstract.md',
                                                       'artifacts': ['drafts/abstract.md', 'drafts/05_results.md']}),
                                           encoding='utf-8')
    assert m.measure(tmp_path)['abstract_words'] == 300 and 'word word' in m.manuscript(tmp_path)


def test_paper_profile_wins_over_library_profile_under_either_name(tmp_path, monkeypatch):
    m = module('journal_fit')
    lib = tmp_path / 'lib'
    lib.mkdir()
    monkeypatch.setattr(m, 'library_journals', lambda: lib)
    m.remember_alias('The Spine Journal', 'Spine J')
    (lib / 'the-spine-journal.md').write_text('library', encoding='utf-8')
    paper = tmp_path / 'paper'
    (paper / 'profile' / 'journals').mkdir(parents=True)
    (paper / 'profile' / 'journals' / 'spine-j.md').write_text('paper', encoding='utf-8')
    assert m.profile_path('The Spine Journal', paper).read_text(encoding='utf-8') == 'paper'


def test_style_edits_apply_refuses_an_outside_registry(tmp_path):
    import json
    import subprocess
    paper = tmp_path / 'paper'
    (paper / 'Style').mkdir(parents=True)
    (paper / 'project.json').write_text(json.dumps({'artifacts': [], 'terminology': str(tmp_path / 'shared.md')}),
                                        encoding='utf-8')
    (paper / 'Style' / 'pending_style_rules.md').write_text('- [x] P0 replace "utilized" with "used" (2x)\n',
                                                           encoding='utf-8')
    done = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'academic_style.py'), 'edits', '--apply'], cwd=paper,
                          capture_output=True, text=True, encoding='utf-8',
                          env={**os.environ, 'MANUWRIGHT_HOME': str(tmp_path / 'home')})
    assert done.returncode == 2 and 'outside the paper' in done.stderr and 'Traceback' not in done.stderr
    assert not (tmp_path / 'shared.md').exists()

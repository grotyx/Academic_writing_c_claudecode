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

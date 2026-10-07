"""v1.9.0 tools: claim strength, letter-blind re-review, learning from author edits, evidence audit."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import academic_style as acad  # noqa: E402
import blind_review  # noqa: E402
import check_claim_strength as strength  # noqa: E402
import search_pubmed  # noqa: E402

EVIDENCE = """### [1] Lee 2020
- **Evidence ID:** lee_2020
- **Source Status:** verified
- **Claim Strength:** observed
- **Allowed Wording:** was associated with
### [2] Kim 2021
- **Evidence ID:** kim_2021
- **Source Status:** verified
- **Claim Strength:** strong
### [3] Park 2019
- **Evidence ID:** park_2019
- **Source Status:** verified
- **Claim Strength:** [TODO: speculative | observed | supported | strong]
"""


def test_claim_strength_flags_wording_stronger_than_the_evidence(tmp_path):
    (tmp_path / 'ev.md').write_text(EVIDENCE, encoding='utf-8')
    draft = tmp_path / '06_discussion.md'
    draft.write_text('Early mobilization reduced complications [EVID:lee_2020]. '
                     'Fusion was associated with fewer reoperations [EVID:lee_2020].\n'
                     'Bracing may lower pain [EVID:lee_2020]. Endoscopy demonstrated superiority [EVID:kim_2021].\n'
                     'X proved Y [EVID:park_2019]. Z prevented W [EVID:lee_2020] [EVID:kim_2021].\n', encoding='utf-8')
    findings = strength.check([draft], tmp_path / 'ev.md')
    assert [(line, msg.split(' wording')[0]) for _, line, msg in findings] == [(1, 'directional')]
    assert 'allowed wording: was associated with' in findings[0][2]
    assert strength.main([str(draft), '--evidence', str(tmp_path / 'ev.md')]) == 1


def test_lint_after_edit_reports_overclaims_from_the_paper_evidence(tmp_path):
    (tmp_path / 'knowledge').mkdir()
    (tmp_path / 'knowledge' / 'evidence.md').write_text(EVIDENCE, encoding='utf-8')
    target = tmp_path / 'drafts' / '06_discussion.md'
    target.parent.mkdir()
    target.write_text('Early mobilization reduced complications [EVID:lee_2020].\n', encoding='utf-8')
    spec = importlib.util.spec_from_file_location('lint_on_edit', ROOT / 'scripts' / 'hooks' / 'lint_on_edit.py')
    lint = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lint)
    code, message = lint.evaluate({'tool_name': 'Write', 'cwd': str(tmp_path), 'tool_input': {'file_path': str(target)}})
    assert code == 2 and '[OVERCLAIM] line 1' in message


def make_revision(tmp_path):
    (tmp_path / 'drafts' / 'revision' / 'REV1').mkdir(parents=True)
    (tmp_path / 'review').mkdir()
    comments = tmp_path / 'review' / 'reviewer_comments_REV1.md'
    comments.write_text('Reviewer #1:\n\nComment 1) Report the CI.\n\nComment 2) Add a limitation.\n', encoding='utf-8')
    (tmp_path / 'drafts' / '05_results.md').write_text('Pain fell.\n', encoding='utf-8')
    (tmp_path / 'drafts' / 'revision' / 'REV1' / '05_results_REV1.md').write_text('Pain fell (95% CI 1-2).\n',
                                                                                 encoding='utf-8')
    (tmp_path / 'drafts' / 'revision' / 'REV1' / 'response_letter_REV1.md').write_text('Dear Editor', encoding='utf-8')
    return comments


def test_blind_packet_withholds_the_letter_and_the_record_needs_every_phase(tmp_path):
    comments = make_revision(tmp_path)
    out = tmp_path / 'review' / 'blind_REV1'
    manifest = blind_review.packet(comments, tmp_path / 'drafts', tmp_path / 'drafts' / 'revision' / 'REV1', out)
    assert manifest['comments'] == ['R1-C1', 'R1-C2'] and manifest['revised_sections'] == ['05_results_REV1.md']
    assert not any('response' in name for name in manifest['sha256']) and (out / 'diffs' / '05_results.diff').is_file()
    assert any('Phase 1 expectation is empty' in p for p in blind_review.check(out / 'verdicts.md'))

    def record(c1, c2):
        (out / 'verdicts.md').write_text(f'## R1-C1\n{c1}\n## R1-C2\n{c2}\n', encoding='utf-8')
        return blind_review.check(out / 'verdicts.md')
    good = ('expectation: CI reported for the primary outcome\nblind_verdict: FULLY\n'
            'anchor: 05_results_REV1.md: "95% CI 1-2"\nfinal_verdict: FULLY\nbasis:\nnew_issue: none')
    swayed = ('expectation: a limitation paragraph names selection bias\nblind_verdict: NOT_ADDRESSED\nanchor: none found\n'
              'final_verdict: FULLY\nbasis:\nnew_issue: none')
    assert record(good, good) == []
    assert any('without a basis' in p for p in record(good, swayed))
    assert record(good, swayed.replace('basis:', 'basis: author_pointer: Discussion para 5')) == []
    assert any('regression' in p for p in record(good, good.replace('new_issue: none', 'new_issue: regression: CI wrong')))
    assert any('must be none' in p for p in record(good, good.replace('new_issue: none', 'new_issue: typo')))


def test_edits_propose_rules_and_only_ticked_rules_reach_the_registry(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    ai = ('Notably, the cohort demonstrated lower pain. We utilized drains. '
          'Results demonstrated benefit in 10 patients [EVID:a_1].\n')
    mine = 'The cohort showed lower pain. We used drains. Results showed benefit in 12 patients [EVID:a_1].\n'
    proposals = acad.edit_proposals([(ai, mine)])
    assert ('P0', 'demonstrated -> showed', 2, 'replace') in proposals
    assert ('P1', 'notably', 1, 'delete') in proposals and ('P1', 'utilized -> used', 1, 'replace') in proposals
    assert not any('10' in rule or '12' in rule for _, rule, _, _ in proposals)  # numbers are never rules
    (tmp_path / 'ai.md').write_text(ai, encoding='utf-8')
    (tmp_path / 'me.md').write_text(mine, encoding='utf-8')
    assert acad.main(['edits', 'ai.md', 'me.md']) == 0
    assert acad.main(['edits', '--apply']) == 0
    assert not (tmp_path / 'Style' / 'terminology.md').exists()  # nothing ticked, nothing applied
    pending = tmp_path / 'Style' / 'pending_style_rules.md'
    pending.write_text(pending.read_text(encoding='utf-8').replace('- [ ] P0', '- [x] P0'), encoding='utf-8')
    assert acad.main(['edits', '--apply']) == 0
    import lint_manuscript
    terms = lint_manuscript.load_forbidden_terms(tmp_path / 'Style' / 'terminology.md')
    assert terms == {'demonstrated': 'showed'}


def test_evidence_audit_scores_metadata_and_flags_retractions():
    evidence = """### [1] Hamilton et al., 2022
- **Evidence ID:** hamilton_2022
- **Citation:** Hamilton TW, et al. Efficacy of liposomal bupivacaine and bupivacaine hydrochloride vs bupivacaine hydrochloride alone as a periarticular anesthetic for patients undergoing knee replacement. JAMA Surg. 2022;157:481-489.
- **DOI:** 10.1001/jamasurg.2022.0713
- **PMID:** 35385072
### [2] Smith 2021
- **Evidence ID:** smith_2021
- **Citation:** Smith J. Knee replacement outcomes. Spine. 2021.
- **DOI:** 10.1000/wrong
### [3] No identifiers
- **Evidence ID:** none_2020
"""
    records = [
        {'pmid': '35385072', 'title': 'Efficacy of Liposomal Bupivacaine and Bupivacaine Hydrochloride vs Bupivacaine '
         'Hydrochloride Alone as a Periarticular Anesthetic for Patients Undergoing Knee Replacement',
         'first_author': 'Hamilton', 'year': '2022', 'journal_abbr': 'JAMA Surg', 'doi': '10.1001/jamasurg.2022.0713'},
        {'pmid': '222', 'title': 'Knee replacement outcomes in older adults', 'first_author': 'Smith', 'year': '2021',
         'journal_abbr': 'Spine (Phila Pa 1976)', 'doi': '10.1000/right', 'retracted': True},
    ]
    rows = search_pubmed.audit_evidence(evidence, fetch=lambda ids: [r for r in records if r['pmid'] in ids],
                                        resolve=lambda doi: '222' if doi == '10.1000/wrong' else None)
    by_id = {eid: (status, score, notes) for eid, status, score, notes in rows}
    assert by_id['hamilton_2022'][:2] == ('verified', 1.0)
    assert by_id['smith_2021'][0] == 'retracted' and 'DOI 10.1000/wrong != PubMed 10.1000/right' in by_id['smith_2021'][2]
    assert 'none_2020' not in by_id
    assert search_pubmed.audit_status(0.75) == 'partial' and search_pubmed.audit_status(0.4) == 'failed'


def test_pubmed_parser_reads_retraction_links():
    import xml.etree.ElementTree as ET
    xml = ('<PubmedArticle><MedlineCitation><PMID>1</PMID><Article><ArticleTitle>T</ArticleTitle>'
           '<PublicationTypeList><PublicationType>Journal Article</PublicationType></PublicationTypeList></Article>'
           '<CommentsCorrectionsList><CommentsCorrections RefType="RetractionIn"/>'
           '<CommentsCorrections RefType="ErratumIn"/></CommentsCorrectionsList></MedlineCitation></PubmedArticle>')
    article = search_pubmed._parse_article(ET.fromstring(xml))
    assert article['retracted'] and article['erratum'] and not article['concern']


def test_cli_routes_the_new_tools():
    import subprocess
    run = lambda *args: subprocess.run([sys.executable, '-m', 'manuwright.cli', *args], capture_output=True,  # noqa: E731
                                       text=True, encoding='utf-8', cwd=str(ROOT)).stdout
    assert 'manuwright search audit' in run('search', 'audit', '--help')
    assert 'packet' in run('blind-review', '--help') and '--evidence' in run('claim-strength', '--help')
    assert '--apply' in run('style', 'edits', '--help')

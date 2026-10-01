"""Personal library: saved Word styles and templates, team profile, writing style copied into new papers."""
import json
from pathlib import Path

import pytest

from manuwright import library, lifecycle

ENGINE = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def home(tmp_path, monkeypatch):
    monkeypatch.setenv('MANUWRIGHT_HOME', str(tmp_path / 'home'))
    return tmp_path / 'home'


def make_template(path):
    from docx import Document
    from docx.shared import Pt
    doc = Document()
    doc.styles['Heading 1'].font.size = Pt(17)
    doc.add_paragraph('template text that must not leak into manuscripts')
    doc.save(path)
    return path


def test_word_template_saved_once_used_in_any_paper(tmp_path, capsys):
    template = make_template(tmp_path / 'team.docx')
    assert library.main(ENGINE, ['docx', 'add', str(template), '--name', 'Team style']) == 0
    assert library.docx_styles()['Team-style']['template']
    paper = tmp_path / 'paper'
    lifecycle.init(ENGINE, [str(paper)])
    answers = iter(['15', '3'])  # journal: none; Word style 3 = my saved style (keep, default, saved, custom)
    assert lifecycle.target(ENGINE, ['--project', str(paper / 'project.json')], ask=lambda _: next(answers)) == 0
    block = json.loads((paper / 'project.json').read_text())['docx']
    assert block == {'reference': 'templates/Team-style.docx'} and (paper / 'templates' / 'Team-style.docx').is_file()
    from harness.build import docx_style, document, append_markdown
    style = docx_style({'docx': block}, paper)
    doc = document(style)
    append_markdown(doc, '# Introduction\n\nBody text.', style)
    texts = [p.text for p in doc.paragraphs]
    assert texts == ['Introduction', 'Body text.']  # template content dropped, its heading style used
    assert doc.paragraphs[0].style.name == 'Heading 1' and doc.paragraphs[0].style.font.size.pt == 17


def test_reference_counts_in_review_snapshot(tmp_path):
    from tests.test_harness import put
    from harness.project import snapshot
    root = tmp_path
    put(root / 'templates/t.docx', 'x')
    put(root / 'project.json', '{}')
    files = snapshot(root / 'project.json', {'docx': {'reference': 'templates/t.docx'}, 'artifacts': []})
    assert any(k.endswith('t.docx') for k in files)


def test_init_copies_profile_and_writing_style(tmp_path):
    source = tmp_path / 'Style'
    (source / 'own').mkdir(parents=True)
    (source / 'own' / 'park_2024.md').write_text('# anchor', encoding='utf-8')
    (source / 'PDF' / 'own').mkdir(parents=True)
    (source / 'PDF' / 'own' / 'park_2024.pdf').write_bytes(b'%PDF')
    (source / 'terminology.md').write_text('# Terms', encoding='utf-8')
    (source / 'style_guide.md').write_text('engine guide', encoding='utf-8')
    (source / 'own' / 'example_YYYY_Journal_keyword.md').write_text('placeholder', encoding='utf-8')
    assert library.main(ENGINE, ['writing', 'import', str(source)]) == 0
    assert library.main(ENGINE, ['profile']) == 0
    assert library.profile_path().read_text(encoding='utf-8').startswith('# Author')
    paper = tmp_path / 'paper'
    lifecycle.init(ENGINE, [str(paper)])
    assert (paper / 'profile' / 'authors.md').is_file() and (paper / 'Style' / 'own' / 'park_2024.md').is_file()
    assert not (paper / 'Style' / 'PDF').exists()  # sources stay in the library
    assert not (paper / 'Style' / 'style_guide.md').exists()
    assert not (paper / 'Style' / 'own' / 'example_YYYY_Journal_keyword.md').exists()
    assert json.loads((paper / 'project.json').read_text())['terminology'] == 'Style/terminology.md'


def test_style_add_files_sources_by_kind(tmp_path, capsys):
    pdf = tmp_path / 'smith_2024.pdf'
    pdf.write_bytes(b'%PDF')
    assert library.main(ENGINE, ['style', 'add', str(pdf), '--kind', 'landmark']) == 0
    assert (library.writing() / 'PDF' / 'landmark' / 'smith_2024.pdf').is_file()
    assert 'register my writing style' in capsys.readouterr().out
    assert library.main(ENGINE, ['style', 'add', str(pdf), '--kind', 'nope']) == 2


def test_library_never_overwrites_without_replace(tmp_path, capsys):
    one, two = make_template(tmp_path / 'one.docx'), make_template(tmp_path / 'two.docx')
    assert library.main(ENGINE, ['docx', 'add', str(one), '--name', 'team']) == 0
    assert library.main(ENGINE, ['docx', 'add', str(two), '--name', 'team']) == 1
    assert 'already exists' in capsys.readouterr().err
    assert library.main(ENGINE, ['docx', 'add', str(two), '--name', 'team', '--replace']) == 0
    md = tmp_path / 'a.md'
    md.write_text('first', encoding='utf-8')
    library.main(ENGINE, ['style', 'add', str(md)])
    md.write_text('second', encoding='utf-8')
    library.main(ENGINE, ['style', 'add', str(md)])
    assert (library.writing() / 'own' / 'a.md').read_text() == 'first'
    library.main(ENGINE, ['style', 'add', str(md), '--replace'])
    assert (library.writing() / 'own' / 'a.md').read_text() == 'second'
    library.main(ENGINE, ['profile'])
    assert library.main(ENGINE, ['profile', '--import', str(md)]) == 1


def test_journal_style_is_suggested_for_that_journal(tmp_path, capsys):
    template = make_template(tmp_path / 'bjj.docx')
    assert library.main(ENGINE, ['docx', 'add', str(template), '--name', 'bjj-house', '--journal', 'bjj']) == 0
    library.save_docx_style('mine', {'font': 'Arial'})  # a personal style is listed, not suggested
    paper = tmp_path / 'paper'
    lifecycle.init(ENGINE, [str(paper)])
    import importlib.util
    spec = importlib.util.spec_from_file_location('js', ENGINE / 'scripts' / 'journal_styles.py')
    js = importlib.util.module_from_spec(spec); spec.loader.exec_module(js)
    bjj = str(list(js.STYLES).index('bjj') + 1)
    answers = iter([bjj, '3'])  # pick BJJ; its saved style is listed first after keep/default
    assert lifecycle.target(ENGINE, ['--project', str(paper / 'project.json')], ask=lambda _: next(answers)) == 0
    config = json.loads((paper / 'project.json').read_text())
    assert config['journal'] == 'bjj' and config['docx'] == {'reference': 'templates/bjj-house.docx'}
    out = capsys.readouterr().out
    assert 'saved Word style for Bone Joint J: bjj-house' in out and 'My style: mine' in out
    assert 'suggested for this journal' in out
    assert library.docx_styles()['bjj-house']['for'] == 'journal'


def test_writing_is_the_command_and_style_still_works(tmp_path):
    md = tmp_path / 'b.md'
    md.write_text('x', encoding='utf-8')
    assert library.main(ENGINE, ['writing', 'add', str(md)]) == 0
    assert library.main(ENGINE, ['style', 'add', str(md), '--replace']) == 0


def test_enter_never_switches_style_on_its_own(tmp_path):
    library.save_docx_style('bjj-house', {'font': 'Arial'}, journal='bjj')
    paper = tmp_path / 'paper'
    lifecycle.init(ENGINE, [str(paper)])
    config = json.loads((paper / 'project.json').read_text()); config['journal'] = 'bjj'
    (paper / 'project.json').write_text(json.dumps(config))
    answers = iter(['', ''])  # Enter, Enter: keep journal, keep the default style
    assert lifecycle.target(ENGINE, ['--project', str(paper / 'project.json')], ask=lambda _: next(answers)) == 0
    assert 'docx' not in json.loads((paper / 'project.json').read_text())


def test_replace_failure_keeps_the_stored_template(tmp_path):
    good = make_template(tmp_path / 'good.docx')
    library.main(ENGINE, ['docx', 'add', str(good), '--name', 'house'])
    stored = library.root() / 'docx' / 'house.docx'
    before = stored.read_bytes()
    assert library.main(ENGINE, ['docx', 'add', str(tmp_path / 'missing.docx'), '--name', 'house', '--replace']) == 1
    assert stored.read_bytes() == before and library.docx_styles()['house']['template']
    assert library.main(ENGINE, ['docx', 'add', str(stored), '--name', 'house', '--replace']) == 0  # itself
    assert stored.read_bytes() == before
    fake = tmp_path / 'fake.docx'
    fake.write_text('not a word file')
    assert library.main(ENGINE, ['docx', 'add', str(fake), '--name', 'fake']) == 1
    assert 'fake' not in library.docx_styles()


def test_template_numbering_is_not_duplicated(tmp_path):
    from docx import Document
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from harness.build import docx_style, document
    doc = Document()
    sect = doc.sections[0]._sectPr
    own = OxmlElement('w:lnNumType'); own.set(qn('w:countBy'), '5'); sect.append(own)
    field = OxmlElement('w:fldSimple'); field.set(qn('w:instr'), 'PAGE'); doc.sections[0].footer.paragraphs[0]._p.append(field)
    (tmp_path / 'templates').mkdir()
    doc.save(tmp_path / 'templates' / 't.docx')
    style = docx_style({'docx': {'reference': 'templates/t.docx', 'line_numbers': 'page', 'page_numbers': 'center'}}, tmp_path)
    built = document(style)
    sect = built.sections[0]._sectPr
    assert len(sect.findall(qn('w:lnNumType'))) == 1 and sect.find(qn('w:lnNumType')).get(qn('w:restart')) == 'newPage'
    assert len(list(built.sections[0].footer.paragraphs[0]._p.iter(qn('w:fldSimple')))) == 1
    with pytest.raises(ValueError):
        docx_style({'docx': {'reference': '../outside.docx'}}, tmp_path)


def test_target_without_project_value(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert lifecycle.target(ENGINE, ['--project'], ask=lambda _: '') == 2


def test_word_page_number_in_content_control_is_detected(tmp_path):
    from docx import Document
    from docx.oxml import parse_xml
    from docx.oxml.ns import nsdecls, qn
    from harness.build import docx_style, document
    doc = Document()
    footer = doc.sections[0].footer._element
    footer.append(parse_xml(f'<w:sdt {nsdecls("w")}><w:sdtContent><w:p><w:r><w:instrText>PAGE</w:instrText></w:r>'
                            '</w:p></w:sdtContent></w:sdt>'))
    (tmp_path / 't.docx').parent.mkdir(exist_ok=True)
    doc.save(tmp_path / 't.docx')
    built = document(docx_style({'docx': {'reference': 't.docx', 'page_numbers': 'center'}}, tmp_path))
    root = built.sections[0].footer._element
    assert len(list(root.iter(qn('w:fldSimple')))) == 0 and len(list(root.iter(qn('w:instrText')))) == 1

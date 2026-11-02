"""manuwright figure: figures drawn from results CSV, with provenance checked by verify. Synthetic data."""
import importlib.util
import json
from pathlib import Path

import pytest

from harness.project import load_project, snapshot, verify
from tests.test_harness import project, put, isolated_home  # noqa: F401  (fixtures)

ROOT = Path(__file__).resolve().parents[1]


def module():
    spec = importlib.util.spec_from_file_location('make_figure', ROOT / 'scripts' / 'make_figure.py')
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


FOREST = {'kind': 'forest', 'csv': 'results/or.csv', 'label': 'variable', 'estimate': 'or', 'low': 'lo', 'high': 'hi',
          'log': True, 'annotate': 'text', 'out': 'drafts/figures/figure_1.png'}


def fake_render(spec, records, style, target, fmt):
    target.write_bytes(json.dumps(records).encode())  # stands in for matplotlib: same inputs, same bytes
    return {'font': 'test', 'width_mm': 85.0, 'height_mm': 40.0, 'matplotlib': 'none'}


@pytest.fixture
def drawn(project, monkeypatch):  # noqa: F811
    root = project.parent
    put(root / 'results/or.csv', 'variable,or,lo,hi,text\nAge,1.21,1.05,1.40,1.21 (1.05–1.40)\nSmoking,2.10,1.30,3.39,x\n')
    put(root / 'drafts/figures/figure_1.json', FOREST)
    fig = module()
    monkeypatch.setattr(fig, 'render', fake_render)
    fig.draw(root, json.loads(project.read_text(encoding='utf-8')), root / 'drafts/figures/figure_1.json')
    put(root / 'drafts/05_results.md', '# Results\n\nMean age was 54 years (Figure 1).\n')
    config = json.loads(project.read_text(encoding='utf-8'))
    config['figures'] = ['drafts/figures/figure_1.png']
    put(project, config)
    return project, fig


def figure_check(report):
    return next(c for c in report['checks'] if c['check'] == 'figures')


def test_select_keeps_order_raw_cells_and_repeated_x_across_series():
    fig = module()
    data = 'time,group,mean,lo,hi\n3 mo,A,22.1,19.5,24.7\n3 mo,B,25.3,22.4,28.2\n12 mo,A,18.4,15.9,20.9\n12 mo,B,19.9,17.1,22.7\n'
    spec = {'kind': 'line', 'x': 'time', 'y': 'mean', 'series': 'group', 'low': 'lo', 'high': 'hi'}
    records = fig.select(spec, data.encode(), 'odi.csv')
    assert [r['row'] for r in records] == [1, 2, 3, 4] and records[0]['cells']['mean'] == '22.1'
    spec['rows'] = {'column': 'group', 'values': ['B', 'A']}
    assert [r['cells']['group'] for r in fig.select(spec, data.encode(), 'odi.csv')] == ['B', 'B', 'A', 'A']


@pytest.mark.parametrize('csv_text, spec_change, message', [
    ('variable,or,lo,hi\nAge,1.2,1.3,1.4\n', {}, 'interval'),
    ('variable,or,lo,hi\nAge,1.2 (1.0-1.4),1.0,1.4\n', {}, 'single number'),
    ('variable,or,lo,hi\nAge,nan,1.0,1.4\n', {}, 'not finite'),
    ('variable,or,lo,hi\nAge,0.5,-1,1.4\n', {'log': True}, 'positive'),
    ('variable,or,lo,hi\nAge,1.2,1.0,1.4\nAge,1.3,1.0,1.4\n', {}, 'twice'),
    ('variable,or,or,hi\nAge,1.2,1.0,1.4\n', {}, 'duplicate column'),
    ('variable,or,lo,hi\nAge,1.2,1.0,1.4\n', {'rows': {'column': 'variable', 'values': ['Sex']}}, 'no row'),
])
def test_select_refuses_bad_input(csv_text, spec_change, message):
    spec = dict(kind='forest', label='variable', estimate='or', low='lo', high='hi', **spec_change)
    with pytest.raises(ValueError, match=message):
        module().select(spec, csv_text.encode(), 'or.csv')


def test_spec_rejects_unknown_keys_and_missing_series_cells(tmp_path):
    fig = module()
    put(tmp_path / 's.json', dict(FOREST, colour='red'))
    with pytest.raises(ValueError, match='unknown keys colour'):
        fig.load_spec(tmp_path / 's.json')
    data = 'time,group,mean\n3 mo,A,1\n3 mo,B,2\n12 mo,A,3\n'
    with pytest.raises(ValueError, match="series 'B' has no row for 12 mo"):
        fig.select({'kind': 'bar', 'x': 'time', 'y': 'mean', 'series': 'group'}, data.encode(), 'c.csv')


def test_out_cannot_overwrite_inputs_or_leave_the_results_folder(project):  # noqa: F811
    root, fig = project.parent, module()
    config = json.loads(project.read_text(encoding='utf-8'))
    put(root / 'results/or.csv', 'variable,or,lo,hi\nAge,1.2,1.0,1.4\n')
    put(root / 'or.csv', 'variable,or,lo,hi\nAge,1.2,1.0,1.4\n')
    put(root / 't.json', dict(FOREST, annotate='variable', csv='or.csv'))
    with pytest.raises(ValueError, match='results folder'):
        fig.gather(root, config, root / 't.json')
    put(root / 'w.png.provenance.json', dict(FOREST, annotate='variable', out='w.png'))  # its sidecar is the spec
    with pytest.raises(ValueError, match='overwrite an input'):
        fig.gather(root, config, root / 'w.png.provenance.json')
    put(root / 'v.json', dict(FOREST, annotate='variable', out='../escape.png'))
    with pytest.raises(ValueError, match='escapes'):
        fig.gather(root, config, root / 'v.json')


def test_verify_passes_a_current_figure_and_fails_each_kind_of_staleness(drawn):
    project, fig = drawn
    root = project.parent
    assert figure_check(verify(project))['status'] == 'PASS'
    original = (root / 'results/or.csv').read_text(encoding='utf-8')
    put(root / 'results/or.csv', original.replace('2.10', '2.11'))
    assert 'or.csv changed' in figure_check(verify(project))['detail']
    put(root / 'results/or.csv', original)
    spec = json.loads((root / 'drafts/figures/figure_1.json').read_text(encoding='utf-8'))
    put(root / 'drafts/figures/figure_1.json', dict(spec, xlabel='Odds ratio'))
    assert 'figure_1.json changed' in figure_check(verify(project))['detail']
    put(root / 'drafts/figures/figure_1.json', spec)
    config = json.loads(project.read_text(encoding='utf-8'))
    put(project, dict(config, figure_style={'dpi': 300}))
    assert 'figure_style changed' in figure_check(verify(project))['detail']
    put(project, config)
    (root / 'drafts/figures/figure_1.png').write_bytes(b'edited')
    assert figure_check(verify(project))['status'] == 'FAIL'


def test_a_broken_sidecar_fails_even_with_an_unbound_reason(drawn):
    project, _ = drawn
    root = project.parent
    (root / 'drafts/figures/figure_1.png.provenance.json').write_text('{not json', encoding='utf-8')
    config = json.loads(project.read_text(encoding='utf-8'))
    put(project, dict(config, figures_unbound={'drafts/figures/figure_1.png': 'flow diagram'}))
    snapshot(*load_project(project))  # never raises on a broken sidecar
    assert figure_check(verify(project))['status'] == 'FAIL'


def test_unbound_figures_need_a_reason_outside_draft(project):  # noqa: F811
    root = project.parent
    (root / 'drafts/figures').mkdir(parents=True)
    (root / 'drafts/figures/figure_1.tiff').write_bytes(b'flow diagram')
    put(root / 'drafts/05_results.md', '# Results\n\nMean age was 54 years (Figure 1).\n')
    config = json.loads(project.read_text(encoding='utf-8'))
    put(project, dict(config, figures=['drafts/figures/figure_1.tiff']))
    assert figure_check(verify(project))['status'] == 'PASS'
    assert figure_check(verify(project, 'submission'))['status'] == 'BLOCKED'
    put(project, dict(config, figures=['drafts/figures/figure_1.tiff'],
                      figures_unbound={'drafts/figures/figure_1.tiff': 'CONSORT diagram checked against counts'}))
    assert figure_check(verify(project, 'submission'))['status'] == 'PASS'
    put(project, dict(config, figures=['drafts/figures/figure_1.tiff'], figures_unbound={'drafts/figures/x.tiff': 'r'}))
    with pytest.raises(ValueError, match='figures_unbound'):
        load_project(project)


def test_provenance_inputs_are_in_the_review_snapshot(drawn):
    project, _ = drawn
    deps = snapshot(*load_project(project))
    keys = {Path(key).as_posix() for key in deps}  # snapshot keys use the platform separator
    assert 'drafts/figures/figure_1.png.provenance.json' in keys and 'drafts/figures/figure_1.json' in keys


def test_specs_and_sidecars_are_not_figures_in_the_folder_inventory(tmp_path):
    cross = importlib.util.spec_from_file_location('check_crossrefs', ROOT / 'scripts' / 'check_crossrefs.py')
    obj = importlib.util.module_from_spec(cross)
    cross.loader.exec_module(obj)
    (tmp_path / 'figure_2.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'figure_2.tiff.provenance.json').write_text('{}', encoding='utf-8')
    (tmp_path / 'figure_1.tiff').write_bytes(b'x')
    assert obj.collect_figure_inventory(None, tmp_path) == {1}


def test_check_needs_no_matplotlib_and_draw_explains_how_to_get_it(drawn, monkeypatch, capsys):
    project, fig = drawn
    spec = str(project.parent / 'drafts/figures/figure_1.json')
    assert fig.main(['--check', spec]) == 0
    monkeypatch.setitem(__import__('sys').modules, 'matplotlib', None)  # import fails
    monkeypatch.setattr(fig, 'paper_python', lambda config: None)
    assert fig.main([spec]) == 2 and 'manuwright env' in capsys.readouterr().err


@pytest.mark.parametrize('suffix', ['.tiff', '.png', '.pdf', '.eps'])
def test_real_render_writes_each_format(tmp_path, suffix):
    pytest.importorskip('matplotlib')
    fig = module()
    put(tmp_path / 'project.json', {'paper_id': 'f', 'results': 'results'})
    put(tmp_path / 'results/or.csv', 'variable,or,lo,hi,text\nAge,1.21,1.05,1.40,1.21 (1.05–1.40)\n')
    put(tmp_path / 's.json', dict(FOREST, out='fig/figure_1' + suffix))
    fig.draw(tmp_path, {'paper_id': 'f', 'results': 'results'}, tmp_path / 's.json')
    out = tmp_path / ('fig/figure_1' + suffix)
    assert out.stat().st_size > 1000 and fig.check(tmp_path, {'results': 'results'}, out)[0] == 'ok'
    if suffix == '.tiff':
        from PIL import Image
        with Image.open(out) as image:
            assert image.info.get('compression') == 'tiff_lzw' and round(image.size[0] / 600 * 25.4) == 85


def test_check_of_another_spec_with_the_same_output_fails(drawn):
    project, fig = drawn
    root = project.parent
    put(root / 'drafts/figures/other.json', dict(FOREST, estimate='lo'))
    assert fig.main(['--check', str(root / 'drafts/figures/other.json')]) == 1
    assert fig.check(root, {}, root / 'drafts/figures/figure_1.png', root / 'drafts/figures/other.json')[0] == 'fail'


def test_a_planted_temp_link_cannot_overwrite_the_csv(drawn):
    project, fig = drawn
    root = project.parent
    before = (root / 'results/or.csv').read_bytes()
    for name in ('.figure_1.png.tmp', '.figure_1.png.provenance.json.tmp'):
        (root / 'drafts/figures' / name).symlink_to(root / 'results/or.csv')
    fig.draw(root, json.loads(project.read_text(encoding='utf-8')), root / 'drafts/figures/figure_1.json')
    assert (root / 'results/or.csv').read_bytes() == before


def test_a_sidecar_that_is_a_directory_fails_the_figure_without_crashing(drawn):
    project, _ = drawn
    side = project.parent / 'drafts/figures/figure_1.png.provenance.json'
    side.unlink()
    side.mkdir()
    snapshot(*load_project(project))
    assert figure_check(verify(project))['status'] == 'FAIL'

#!/usr/bin/env python3
"""Draw a figure from a results CSV and record where every plotted value came from.

    manuwright figure drafts/figures/figure_2.json          # draw it (needs matplotlib)
    manuwright figure --check drafts/figures/figure_2.json  # is the image still current? (no matplotlib)

The spec is a small JSON file next to the figure. Kinds: "forest" (estimate with its interval per row),
"bar" and "line" (a value per x, optionally per series, optional interval). The figure only plots values
already in the CSV: no statistics, no rounding, no estimation. Annotations print a CSV column verbatim.

    {"kind": "forest", "csv": "results/table3_regression.csv",
     "rows": {"column": "variable", "values": ["Age", "Smoking"]},
     "label": "variable", "estimate": "or", "low": "ci_low", "high": "ci_high",
     "reference": 1, "log": true, "annotate": "or_ci",
     "xlabel": "Odds ratio (95% CI)", "width": "single", "out": "drafts/figures/figure_2.tiff"}

Bar and line: "x", "y", optional "series", "low"/"high" (together). x is categorical, in CSV or "rows" order;
every series needs every x. Size and type come from "figure_style" in project.json (defaults: 85 mm single,
174 mm double column, 600 dpi, Arial 8 pt); these are defaults, not any journal's rule: check the journal's
instructions. The format follows the output suffix: .tiff, .png, .pdf or .eps.

Next to the image it writes <image>.provenance.json (spec, CSV and image SHA-256, the selected rows, the
effective style). `manuwright verify` fails a listed figure whose CSV, spec, style or image changed since it
was drawn; a figure without provenance (flow diagram, KM curve from the analysis script, photograph) needs a
reason in "figures_unbound" for revision and submission profiles.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import math
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from harness.results import inside  # noqa: E402

SCHEMA = 1
FORMATS = {'.tif': 'tiff', '.tiff': 'tiff', '.png': 'png', '.pdf': 'pdf', '.eps': 'eps'}
COMMON = {'kind', 'csv', 'out', 'rows', 'annotate', 'xlabel', 'ylabel', 'width', 'height'}
KINDS = {'forest': ({'label', 'estimate', 'low', 'high'}, {'reference', 'log'}),
         'bar': ({'x', 'y'}, {'series', 'low', 'high'}),
         'line': ({'x', 'y'}, {'series', 'low', 'high'})}
STYLE_DEFAULTS = {'single_mm': 85.0, 'double_mm': 174.0, 'dpi': 600, 'font': ['Arial', 'Helvetica', 'DejaVu Sans'],
                  'font_pt': 8.0, 'preset': 'prism'}
# Looks only: colours, line weights, ticks, grid. The plotted numbers never depend on the preset.
PRESETS = {
    'nejm': {'colors': ['#0072B5', '#BC3C29', '#E18727', '#20854E', '#7876B1', '#6F99AD'], 'ink': '#0072B5',
             'axis': 0.6, 'tick': 2.5, 'grid': True, 'edge': None, 'offset': 0, 'labelweight': 'normal'},
    'prism': {'colors': ['#4A7DB5', '#D9644A', '#5FA35B', '#8E6BB5', '#E0A43A', '#808080'], 'ink': 'black',
              'axis': 1.0, 'tick': 4.0, 'grid': False, 'edge': 'black', 'offset': 4, 'labelweight': 'bold'},
    'grey': {'colors': ['0.1', '0.55', '0.8', '0.35'], 'ink': 'black',
             'axis': 0.6, 'tick': 3.5, 'grid': False, 'edge': 'black', 'offset': 0, 'labelweight': 'normal'},
}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sidecar_of(image: Path) -> Path:
    return image.with_name(image.name + '.provenance.json')


def find_project(start: Path, explicit: str | None):
    if explicit:
        manifest = Path(explicit).resolve()
    else:
        manifest = next((p / 'project.json' for p in [start, *start.parents] if (p / 'project.json').is_file()), None)
        if manifest is None:
            raise ValueError('no project.json above the spec; pass --project')
    return manifest.parent, json.loads(manifest.read_text(encoding='utf-8'))


def resolve_style(config: dict) -> dict:
    given = config.get('figure_style') or {}
    if not isinstance(given, dict) or set(given) - set(STYLE_DEFAULTS):
        raise ValueError('figure_style keys: ' + ', '.join(STYLE_DEFAULTS))
    style = dict(STYLE_DEFAULTS, **given)
    for key in ('single_mm', 'double_mm', 'font_pt'):
        if not isinstance(style[key], (int, float)) or isinstance(style[key], bool) or not 0 < style[key] <= 500:
            raise ValueError(f'figure_style.{key} must be a positive number')
        style[key] = float(style[key])
    if not isinstance(style['dpi'], int) or isinstance(style['dpi'], bool) or not 72 <= style['dpi'] <= 2400:
        raise ValueError('figure_style.dpi must be an integer from 72 to 2400')
    if isinstance(style['font'], str):
        style['font'] = [style['font']]
    if not isinstance(style['font'], list) or not style['font'] or not all(isinstance(f, str) and f for f in style['font']):
        raise ValueError('figure_style.font must be a font name or a list of them')
    if not isinstance(style['preset'], str) or style['preset'] not in PRESETS:
        raise ValueError('figure_style.preset must be one of: ' + ', '.join(PRESETS))
    return style


def load_spec(spec_path: Path) -> tuple[bytes, dict]:
    raw = spec_path.read_bytes()
    spec = json.loads(raw.decode('utf-8-sig'))
    if not isinstance(spec, dict) or spec.get('kind') not in KINDS:
        raise ValueError('spec "kind" must be one of: ' + ', '.join(KINDS))
    required, optional = KINDS[spec['kind']]
    missing = sorted(({'csv', 'out'} | required) - set(spec))
    unknown = sorted(set(spec) - COMMON - required - optional)
    if missing or unknown:
        raise ValueError('spec ' + '; '.join(filter(None, [missing and 'missing ' + ', '.join(missing),
                                                             unknown and 'unknown keys ' + ', '.join(unknown)])))
    for key in (required | optional | {'csv', 'out', 'annotate', 'xlabel', 'ylabel'}) - {'reference', 'log'}:
        if key in spec and (not isinstance(spec[key], str) or (key not in ('xlabel', 'ylabel') and not spec[key].strip())):
            raise ValueError(f'spec "{key}" must be text')
    if ('low' in spec) != ('high' in spec):
        raise ValueError('spec needs "low" and "high" together')
    if 'log' in spec and not isinstance(spec['log'], bool):
        raise ValueError('spec "log" must be true or false')
    if 'reference' in spec and (not isinstance(spec['reference'], (int, float)) or isinstance(spec['reference'], bool)):
        raise ValueError('spec "reference" must be a number')
    width = spec.get('width', 'single')
    if width not in ('single', 'double') and (not isinstance(width, (int, float)) or isinstance(width, bool) or not 10 <= width <= 500):
        raise ValueError('spec "width" is single, double or a width in mm (10-500)')
    if 'height' in spec and (not isinstance(spec['height'], (int, float)) or isinstance(spec['height'], bool) or not 10 <= spec['height'] <= 500):
        raise ValueError('spec "height" is a height in mm (10-500)')
    rows = spec.get('rows')
    if rows is not None and (not isinstance(rows, dict) or set(rows) != {'column', 'values'} or not isinstance(rows['column'], str)
                             or not isinstance(rows['values'], list) or not rows['values']
                             or not all(isinstance(v, str) for v in rows['values']) or len(set(rows['values'])) != len(rows['values'])):
        raise ValueError('spec "rows" is {"column": name, "values": [distinct cell texts]}')
    if Path(spec['out']).suffix.lower() not in FORMATS:
        raise ValueError('spec "out" must end in ' + ', '.join(FORMATS))
    return raw, spec


def number(text: str, where: str) -> float:
    try:
        value = float(text.strip())
    except ValueError:
        raise ValueError(f'{where}: {text!r} is not a single number (split composite cells into columns)') from None
    if not math.isfinite(value):
        raise ValueError(f'{where}: {text!r} is not finite')
    return value


def select(spec: dict, csv_bytes: bytes, csv_name: str) -> list[dict]:
    """The rows the figure plots, in plot order, with the raw cells and parsed numbers."""
    reader = csv.reader(io.StringIO(csv_bytes.decode('utf-8-sig'), newline=''))
    try:
        header = next(reader)
    except StopIteration:
        raise ValueError(f'{csv_name} is empty') from None
    if len(set(header)) != len(header):
        raise ValueError(f'{csv_name} has duplicate column names')
    rows = []
    for index, cells in enumerate(reader, 1):
        if not any(c.strip() for c in cells):
            continue
        if len(cells) != len(header):
            raise ValueError(f'{csv_name} row {index} has {len(cells)} cells for {len(header)} columns')
        rows.append((index, dict(zip(header, cells))))
    kind = spec['kind']
    text_cols = [spec[k] for k in ('label', 'x', 'series', 'annotate') if k in spec]
    numeric_cols = [spec[k] for k in ('estimate', 'y', 'low', 'high') if k in spec]
    filter_col = [spec['rows']['column']] if spec.get('rows') else []
    absent = sorted({c for c in text_cols + numeric_cols + filter_col if c not in header})
    if absent:
        raise ValueError(f'{csv_name} has no column ' + ', '.join(absent))
    if spec.get('rows'):
        chosen = []
        for wanted in spec['rows']['values']:
            hits = [r for r in rows if r[1][spec['rows']['column']].strip() == wanted]
            if not hits:
                raise ValueError(f'{csv_name}: no row with {spec["rows"]["column"]} = {wanted!r}')
            chosen += hits
    else:
        chosen = rows
    if not chosen:
        raise ValueError(f'{csv_name}: no rows selected')
    records, keys = [], set()
    for index, cells in chosen:
        where = f'{csv_name} row {index}'
        values = {c: number(cells[c], f'{where} column {c}') for c in numeric_cols}
        key = (cells[spec['label']].strip(),) if kind == 'forest' else \
            (cells[spec['x']].strip(), cells[spec['series']].strip() if 'series' in spec else '')
        if key in keys:
            raise ValueError(f'{where}: {" / ".join(k for k in key if k)} appears twice')
        keys.add(key)
        point = values[spec['estimate' if kind == 'forest' else 'y']]
        if 'low' in spec and not values[spec['low']] <= point <= values[spec['high']]:
            raise ValueError(f'{where}: the interval does not contain the value')
        if spec.get('log') and min(values.values()) <= 0:
            raise ValueError(f'{where}: a log axis needs positive values')
        records.append({'row': index, 'cells': {c: cells[c] for c in dict.fromkeys(text_cols + numeric_cols)},
                        'values': values})
    if kind != 'forest' and 'series' in spec:
        xs = {r['cells'][spec['x']].strip() for r in records}
        for series in {r['cells'][spec['series']].strip() for r in records}:
            have = {r['cells'][spec['x']].strip() for r in records if r['cells'][spec['series']].strip() == series}
            if have != xs:
                raise ValueError(f'{csv_name}: series {series!r} has no row for ' + ', '.join(sorted(xs - have)))
    if spec.get('log') and spec.get('reference', 1) <= 0:
        raise ValueError('a log axis needs a positive reference')
    return records


def gather(root: Path, config: dict, spec_path: Path):
    """Everything the figure depends on, read once: (spec bytes, spec, csv path, csv bytes, records, style, out)."""
    spec_raw, spec = load_spec(spec_path)
    csv_path = inside(root, spec['csv'])
    results = inside(root, config.get('results') or 'results')
    if not csv_path.is_relative_to(results):
        raise ValueError(f'{spec["csv"]} is not under the results folder')
    csv_bytes = csv_path.read_bytes()
    records = select(spec, csv_bytes, spec['csv'])
    out = inside(root, spec['out'])
    inputs = {spec_path.resolve(), csv_path, (root / 'project.json').resolve()}
    if out in inputs or sidecar_of(out) in inputs:
        raise ValueError('"out" would overwrite an input file')
    return spec_raw, spec, csv_path, csv_bytes, records, resolve_style(config), out


def rel(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def check(root: Path, config: dict, image: Path, spec: Path | None = None) -> tuple[str, str]:
    """('ok', detail) | ('unbound', '') | ('fail', why). Read-only, no matplotlib. With `spec`, the image must
    have been drawn from that spec (another spec writing the same file is not current)."""
    side = sidecar_of(image)
    if not side.exists():
        return 'unbound', ''
    name = rel(root, image)
    try:
        record = json.loads(side.read_text(encoding='utf-8'))
        if record.get('schema_version') != SCHEMA or record.get('output') != name:
            return 'fail', f'{name}: provenance is for another file or schema'
        if sha(image.read_bytes()) != record.get('image_sha256'):
            return 'fail', f'{name}: the image changed after it was drawn (redraw with manuwright figure)'
        spec_path = inside(root, record['spec'])
        if spec is not None and spec_path != spec.resolve():
            return 'fail', f'{name} was drawn from {record["spec"]}, not {rel(root, spec)}'
        spec_raw, spec, csv_path, csv_bytes, records, style, out = gather(root, config, spec_path)
        if out != image.resolve():
            return 'fail', f'{name}: its spec now writes {spec["out"]}'
        if sha(spec_raw) != record.get('spec_sha256'):
            return 'fail', f'{name}: {record["spec"]} changed; redraw with manuwright figure {record["spec"]}'
        if rel(root, csv_path) != record.get('csv') or sha(csv_bytes) != record.get('csv_sha256'):
            return 'fail', f'{name}: {spec["csv"]} changed; redraw with manuwright figure {record["spec"]}'
        if records != record.get('records'):
            return 'fail', f'{name}: the plotted rows do not match the CSV'
        if style != record.get('style'):
            return 'fail', f'{name}: figure_style changed; redraw with manuwright figure {record["spec"]}'
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return 'fail', f'{name}: provenance cannot be checked ({exc})'
    return 'ok', f'{name} from {record["csv"]}'


def dependencies(root: Path, figures: list[str]) -> set[Path]:
    """Sidecars and the specs/CSVs they name, for the review snapshot. Never raises."""
    found = set()
    for value in figures:
        try:
            side = sidecar_of(inside(root, value))
            if side.exists():
                raw = side.read_bytes()  # a directory or unreadable file stays out; check() fails the figure
                found.add(side)
                record = json.loads(raw.decode('utf-8'))
                for key in ('spec', 'csv'):
                    path = inside(root, record[key])
                    if path.is_file():
                        found.add(path)
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            continue
    return found


def render(spec: dict, records: list[dict], style: dict, target: Path, fmt: str) -> dict:
    import matplotlib
    matplotlib.use('Agg')
    from matplotlib import font_manager, pyplot as plt
    font = next((f for f in style['font'] if _has_font(font_manager, f)), 'DejaVu Sans')
    look = PRESETS[style['preset']]
    plt.rcParams.update({'font.family': font, 'font.size': style['font_pt'], 'text.parse_math': False,
                         'axes.linewidth': look['axis'], 'xtick.major.width': look['axis'],
                         'ytick.major.width': look['axis'], 'xtick.major.size': look['tick'],
                         'ytick.major.size': look['tick'], 'xtick.direction': 'out', 'ytick.direction': 'out',
                         'axes.labelweight': look['labelweight'], 'legend.handlelength': 1.2,
                         'svg.hashsalt': 'manuwright', 'pdf.fonttype': 42, 'ps.fonttype': 42})
    width = {'single': style['single_mm'], 'double': style['double_mm']}.get(spec.get('width', 'single'), spec.get('width'))
    kind = spec['kind']
    count = len(records)
    height = spec.get('height') or (max(35.0, 12 + 6.5 * count) if kind == 'forest' else width * 0.72)
    fig, ax = plt.subplots(figsize=(width / 25.4, height / 25.4), layout='constrained')
    colors, markers = look['colors'], ['o', 's', '^', 'D']
    if kind == 'forest':
        ys = list(range(count, 0, -1))
        est = [r['values'][spec['estimate']] for r in records]
        lo = [r['values'][spec['low']] for r in records]
        hi = [r['values'][spec['high']] for r in records]
        ax.errorbar(est, ys, xerr=[[e - l for e, l in zip(est, lo)], [h - e for e, h in zip(est, hi)]],
                    fmt='s', color=look['ink'], markersize=4, elinewidth=look['axis'] + 0.3, capsize=0)
        ax.axvline(spec.get('reference', 1), color='0.35', linewidth=look['axis'], linestyle='--', zorder=1)  # above the grid, below the estimates
        if spec.get('log'):
            _log_axis(ax.xaxis, ax.set_xscale)
        ax.set_yticks(ys, [r['cells'][spec['label']] for r in records])
        ax.set_ylim(0.4, count + 0.6)
        if spec.get('annotate'):
            for y, r in zip(ys, records):
                ax.annotate(r['cells'][spec['annotate']], (1.02, y), xycoords=('axes fraction', 'data'),
                            va='center', ha='left', annotation_clip=False)
    else:
        xs = list(dict.fromkeys(r['cells'][spec['x']].strip() for r in records))
        series = list(dict.fromkeys(r['cells'][spec['series']].strip() for r in records)) if 'series' in spec else ['']
        step = 0.8 / len(series)
        for n, name in enumerate(series):
            rows = {r['cells'][spec['x']].strip(): r for r in records
                    if 'series' not in spec or r['cells'][spec['series']].strip() == name}
            ordered = [rows[x] for x in xs]
            ys = [r['values'][spec['y']] for r in ordered]
            err = None
            if 'low' in spec:
                err = [[y - r['values'][spec['low']] for y, r in zip(ys, ordered)],
                       [r['values'][spec['high']] - y for y, r in zip(ys, ordered)]]
            if kind == 'bar':
                pos = [i - 0.4 + step * (n + 0.5) for i in range(len(xs))]
                ax.bar(pos, ys, step * 0.85, color=colors[n % len(colors)], edgecolor=look['edge'] or 'none',
                       linewidth=look['axis'], yerr=err, capsize=2.5,
                       error_kw={'elinewidth': look['axis'], 'capthick': look['axis']}, label=name or None)
            else:
                pos = [i + (n - (len(series) - 1) / 2) * 0.06 for i in range(len(xs))]  # small dodge: bars stay readable
                ax.errorbar(pos, ys, yerr=err, color=colors[n % len(colors)], marker=markers[n % 4],
                            markersize=4, linewidth=1.2, capsize=2.5, elinewidth=look['axis'],
                            capthick=look['axis'], markeredgecolor=look['edge'] or colors[n % len(colors)],
                            markeredgewidth=look['axis'] * 0.8, label=name or None)
            if spec.get('annotate'):
                for p, y, r in zip(pos, ys, ordered):
                    ax.annotate(r['cells'][spec['annotate']], (p, y), textcoords='offset points', xytext=(0, 4),
                                ha='center', va='bottom')
        ax.set_xticks(range(len(xs)), xs)
        if spec.get('log'):
            _log_axis(ax.yaxis, ax.set_yscale)
        if 'series' in spec:
            ax.legend(frameon=False)
    ax.set_xlabel(spec.get('xlabel', ''))
    ax.set_ylabel(spec.get('ylabel', ''))
    ax.spines[['top', 'right']].set_visible(False)
    if look['offset']:
        ax.spines[['left', 'bottom']].set_position(('outward', look['offset']))
    if look['grid'] and kind != 'forest':  # a forest keeps only its dashed null line
        ax.grid(axis='y', color='0.88', linewidth=0.5)
        ax.set_axisbelow(True)
    options = {'format': fmt, 'dpi': style['dpi']}
    if fmt == 'tiff':
        options['pil_kwargs'] = {'compression': 'tiff_lzw'}
    elif fmt == 'png':
        options['metadata'] = {'Software': None}
    elif fmt == 'pdf':
        options['metadata'] = {'Creator': None, 'Producer': None, 'CreationDate': None}
    elif fmt == 'eps':
        options['metadata'] = {'Creator': None}
    fig.savefig(target, **options)
    plt.close(fig)
    return {'font': font, 'width_mm': round(width, 2), 'height_mm': round(height, 2),
            'matplotlib': matplotlib.__version__}


def _log_axis(axis, set_scale) -> None:
    """Log scale with plain tick labels (0.5, 0.75, 1, 1.5), not 10^0 mathtext, which parse_math=False would
    print raw. Every view gets 2 to 7 ticks inside it, 1 kept when visible, and labels precise enough that
    different ticks never read the same."""
    from matplotlib import ticker
    set_scale('log')
    low, high = sorted(axis.get_view_interval())
    ticks = _log_ticks(low, high)
    labels = _tick_labels(ticks)
    axis.set_major_locator(ticker.FixedLocator(ticks))
    axis.set_major_formatter(ticker.FuncFormatter(lambda value, _: labels.get(value, '')))
    axis.set_minor_locator(ticker.NullLocator())


def _log_ticks(low: float, high: float, most: int = 7) -> list[float]:
    from matplotlib import ticker
    first, last = math.floor(math.log10(low)), math.ceil(math.log10(high))
    steps = (1, 1.5, 2, 3, 5, 7.5) if last - first <= 3 else (1,)  # wide views: decades only
    ticks = [m * 10.0 ** e for e in range(first, last + 1) for m in steps]
    ticks = [t for t in ticks if low <= t <= high]
    if len(ticks) < 3:  # under a decade wide: evenly spaced round numbers, as on a linear axis
        ticks = [t for t in ticker.MaxNLocator(nbins=4, steps=[1, 2, 2.5, 5, 10]).tick_values(low, high)
                 if t > 0 and low <= t <= high]
        if low <= 1 <= high and 1 not in ticks:
            ticks = sorted(ticks + [1.0])
    while len(ticks) > most:
        step = math.ceil(len(ticks) / most)
        start = ticks.index(1.0) % step if 1.0 in ticks else 0  # keep the null line labelled
        ticks = ticks[start::step]
    return ticks


def _tick_labels(ticks: list[float]) -> dict:
    for digits in range(2, 16):
        labels = [f'{t:.{digits}g}' for t in ticks]
        if len(set(labels)) == len(labels):
            return dict(zip(ticks, labels))
    return {t: repr(t) for t in ticks}


def _has_font(font_manager, name: str) -> bool:
    try:
        font_manager.findfont(name, fallback_to_default=False)
        return True
    except ValueError:
        return False


def draw(root: Path, config: dict, spec_path: Path) -> str:
    spec_raw, spec, csv_path, csv_bytes, records, style, out = gather(root, config, spec_path)
    fmt = FORMATS[out.suffix.lower()]
    out.parent.mkdir(parents=True, exist_ok=True)
    temps = []
    for _ in range(2):  # created exclusively, so an existing file or link is never written through
        handle, name = tempfile.mkstemp(dir=out.parent, prefix='.' + out.name + '.', suffix='.tmp')
        os.close(handle)
        temps.append(Path(name))
    temp_image, temp_side = temps
    try:
        rendered = render(spec, records, style, temp_image, fmt)
        if spec_path.read_bytes() != spec_raw or csv_path.read_bytes() != csv_bytes:
            raise ValueError('the spec or CSV changed while drawing; run it again')
        record = {'schema_version': SCHEMA, 'output': rel(root, out), 'image_sha256': sha(temp_image.read_bytes()),
                  'spec': rel(root, spec_path), 'spec_sha256': sha(spec_raw),
                  'csv': rel(root, csv_path), 'csv_sha256': sha(csv_bytes),
                  'style': style, 'rendered': rendered, 'records': records}
        temp_side.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
        os.replace(temp_image, out)  # an interrupt between the two replaces leaves a hash mismatch, never a false pass
        os.replace(temp_side, sidecar_of(out))
    finally:
        for temp in temps:
            temp.unlink(missing_ok=True)
    return (f'wrote {rel(root, out)} ({rendered["width_mm"]} x {rendered["height_mm"]} mm, {style["dpi"]} dpi, '
            f'{rendered["font"]}) from {len(records)} row(s) of {rel(root, csv_path)}, and its provenance. '
            'Look at it before you list it under "figures".')


def paper_python(config: dict) -> Path | None:
    """The paper's analysis environment (manuwright env), which installs matplotlib by default."""
    home = Path(os.environ.get('MANUWRIGHT_HOME') or Path.home() / '.manuwright')
    python = home / 'envs' / str(config.get('paper_id', '')) / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    return python if config.get('paper_id') and python.exists() else None


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    parser = argparse.ArgumentParser(prog='manuwright figure', description=__doc__.split('\n\n')[0])
    parser.add_argument('spec', help='the figure spec (JSON)')
    parser.add_argument('--check', action='store_true', help='only check the drawn image is still current')
    parser.add_argument('--project', help='project.json (default: the nearest one above the spec)')
    args = parser.parse_args(argv)
    spec_path = Path(args.spec).resolve()
    try:
        root, config = find_project(spec_path.parent, args.project)
        if args.check:
            out = inside(root, load_spec(spec_path)[1]['out'])
            state, detail = check(root, config, out, spec_path)
            if state == 'ok':
                print(f'OK {detail}')
                return 0
            print(f'{rel(root, out)}: not drawn yet' if state == 'unbound' else detail, file=sys.stderr)
            return 1
        try:
            import matplotlib  # noqa: F401
        except ImportError:
            python = paper_python(config)
            if python and Path(sys.executable).resolve() != python.resolve():
                return subprocess.call([str(python), str(Path(__file__).resolve()), *(argv if argv is not None else sys.argv[1:])])
            print('manuwright figure: matplotlib is not installed. Run `manuwright env` in the paper folder '
                  '(the paper environment includes it), or install it next to manuwright: '
                  '`uv tool install manuwright --with matplotlib` / `pip install "manuwright[figures]"`.', file=sys.stderr)
            return 2
        print(draw(root, config, spec_path))
    except (OSError, ValueError, KeyError) as exc:
        print(f'manuwright figure: {exc}', file=sys.stderr)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

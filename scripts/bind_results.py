#!/usr/bin/env python3
"""Propose result bindings: each number in the numeric artifacts tied to the results CSV cell it reports.

`manuwright verify` (submission) needs review/result_bindings.json: every number in numeric_artifacts bound
to one CSV cell together with its outcome, time point, population, comparison, statistic and unit. This
writes the mechanical part and leaves every judgement visible:

- a number found in exactly one cell is bound;
- a number found in several cells is only suggested (the cell whose row label and column name share most
  words with the sentence) and stays unresolved until an override confirms it;
- a number in no single-number cell stays unbound (split composite cells such as "54.3 (12.1)" into columns);
- the context the CSV cannot give (time point, population, comparison, unit) comes from
  review/bindings_overrides.json "tables" defaults, once per results file. Without them the numbers of that
  file stay unresolved: an unknown context is never filled in.

Overrides (review/bindings_overrides.json):

    {"tables": {"results/table2_outcomes.csv": {"timepoint": "12 months", "population": "all patients",
                                                "comparison": "MIS-TLIF vs open TLIF",
                                                "unit": {"ebl_ml": "mL", "*": "as in column"}}},
     "numbers": [{"artifact": "drafts/05_results.md", "line": 5, "number": "60", "occurrence": 1,
                  "line_text": "Length of stay was", "cell": "results/table1_baseline.csv:3:MIS_n",
                  "context": {"population": "MIS-TLIF group"}}]}

A "numbers" entry picks the cell for one number (the occurrence-th "60" on that line); `line_text` must still
be on that line, so an override never silently moves to another sentence after an edit. Bindings already in
review/result_bindings.json for an artifact that has not changed since are kept as they are.

    manuwright bind                 report what would be bound (nothing written)
    manuwright bind --write         write review/result_bindings.json (.bak kept) and declare it in project.json

Binding is bookkeeping, not proof: the semantic data review still checks that each number means what the
sentence says.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
import tempfile
from collections import Counter
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import check_numbers as cn  # noqa: E402
from harness.results import CONTEXT, digest, inside  # noqa: E402

OVERRIDES = 'review/bindings_overrides.json'
DEFAULT_BINDINGS = 'review/result_bindings.json'
WORD = re.compile(r'[a-z][a-z0-9]+')
ASKED = ('timepoint', 'population', 'comparison', 'unit')  # what a CSV cannot say


def words(text: str) -> set[str]:
    return set(WORD.findall(re.sub(r'[_\-]', ' ', text.lower())))


def cells(root: Path, results: Path) -> list[dict]:
    """Every CSV cell holding exactly one number (the validator's rule), with its row label."""
    found = []
    for path in sorted(results.rglob('*.csv')):
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream)
            first = reader.fieldnames[0] if reader.fieldnames else None
            for row_number, row in enumerate(reader, start=2):
                label = (row.get(first) or '') if first else ''
                for column, raw in row.items():
                    if column is None or raw is None:
                        continue
                    values = cn.extract_numbers_from_text(raw)
                    if len(values) != 1:
                        continue
                    found.append({'file': path.relative_to(root).as_posix(), 'path': path, 'row': row_number,
                                  'column': column, 'raw': raw, 'label': label,
                                  'number': cn.ResultNumber(values[0], raw, path, row_number, column)})
    return found


def cell_key(cell: dict) -> str:
    return f"{cell['file']}:{cell['row']}:{cell['column']}"


def table_context(defaults: dict, cell: dict) -> dict | None:
    """The four context fields for this cell from the file's defaults, or None when any is missing."""
    entry = defaults.get(cell['file'])
    if not isinstance(entry, dict):
        return None
    out = {}
    for field in ASKED:
        value = entry.get(field)
        if isinstance(value, dict):  # per column, "*" for the rest
            value = value.get(cell['column'], value.get('*'))
        if not isinstance(value, str) or not value.strip():
            return None
        out[field] = value.strip()
    return out


def context_for(cell: dict, defaults: dict, extra: dict | None = None) -> dict | None:
    base = table_context(defaults, cell)
    extra = {k: v for k, v in (extra or {}).items() if k in CONTEXT and isinstance(v, str) and v.strip()}
    if base is None and not all(field in extra for field in ASKED):
        return None
    label = cell['label'].strip()
    outcome = label if label and not cn.extract_numbers_from_text(label) else Path(cell['file']).stem
    return {'outcome': outcome, 'statistic': cell['column'], **(base or {}), **extra}


def load_overrides(root: Path) -> tuple[dict, list[dict], list[str]]:
    path = root / OVERRIDES
    if not path.is_file():
        return {}, [], []
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except ValueError as exc:
        return {}, [], [f'{OVERRIDES}: not valid JSON ({exc})']
    if not isinstance(data, dict):
        return {}, [], [f'{OVERRIDES}: expected an object with "tables" and "numbers"']
    tables = data.get('tables') if isinstance(data.get('tables'), dict) else {}
    numbers = data.get('numbers') if isinstance(data.get('numbers'), list) else []
    return tables, numbers, []


def propose(root: Path, config: dict) -> dict:
    """{'bindings', 'results', 'report': {bound, suggested, unresolved, unbound, kept, problems}}."""
    cn.select_manifest(root, config.get('numeric_allow', []))  # the same exemptions verify uses
    results_dir = inside(root, config.get('results', 'results'))
    all_cells = cells(root, results_dir)
    by_key = {cell_key(c): c for c in all_cells}
    defaults, overrides, problems = load_overrides(root)
    report = {'bound': [], 'suggested': [], 'unresolved': [], 'unbound': [], 'kept': [], 'problems': problems}
    existing = {}
    manifest = config.get('result_bindings') or DEFAULT_BINDINGS
    try:
        old = json.loads(inside(root, manifest).read_text(encoding='utf-8'))
        records = {r['result_id']: r for r in old.get('results', [])}
        for binding in old.get('bindings', []):
            existing.setdefault(binding['artifact'], []).append((binding, records.get(binding['result_id'])))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        existing = {}
    used_overrides = set()
    keys = Counter((o.get('artifact'), o.get('line'), str(o.get('number')), int(o.get('occurrence', 1)))
                   for o in overrides if isinstance(o, dict))
    report['problems'] += [f'{OVERRIDES}: two "numbers" entries for {a}:{l} "{n}" occurrence {k}; keep one'
                           for (a, l, n, k), c in keys.items() if c > 1]
    overridden = {o.get('artifact') for o in overrides if isinstance(o, dict)}
    results, bindings = {}, []

    def same(record, cell, context):
        return (record['source']['file'] == cell['file'] and record['source']['row'] == cell['row']
                and record['source']['column'] == cell['column'] and all(record[k] == context[k] for k in CONTEXT))

    def record_for(cell, context):
        base = f"{cell['file']}:r{cell['row']}:{cell['column']}"  # the full path: two outcomes.csv stay apart
        result_id, n = base, 1
        while result_id in results and not same(results[result_id], cell, context):
            n += 1
            result_id = f'{base}#{n}'
        if result_id not in results:
            results[result_id] = {'result_id': result_id, 'paper_id': config['paper_id'], 'raw': cell['raw'], **context,
                                  'source': {'file': cell['file'], 'row': cell['row'], 'column': cell['column'],
                                             'sha256': digest(cell['path'])}}
        return result_id

    for artifact in config.get('numeric_artifacts', []):
        path = inside(root, artifact)
        sha = digest(path)
        tokens = cn.iter_artifact_numbers(path)
        kept = existing.get(artifact, [])
        if (artifact not in overridden and kept and len(kept) == len(tokens)
                and all(b.get('artifact_sha256') == sha and r for b, r in kept)
                and all(r['result_id'] not in results or results[r['result_id']] == r for _, r in kept)):
            # unchanged since it was bound (by hand or by this tool) and no override names it: keep it
            for binding, record in kept:
                results.setdefault(record['result_id'], record)
                bindings.append(binding)
            report['kept'].append(f'{artifact}: {len(kept)} binding(s) unchanged')
            continue
        seen = Counter()
        lines = path.read_text(encoding='utf-8').splitlines()
        for index, token in enumerate(tokens):
            seen[(token.line, token.number)] += 1
            where = f'{artifact}:{token.line} "{token.number}"'
            override = next((o for i, o in enumerate(overrides) if isinstance(o, dict)
                             and o.get('artifact') == artifact and o.get('line') == token.line
                             and str(o.get('number')) == token.number
                             and int(o.get('occurrence', 1)) == seen[(token.line, token.number)]
                             and not used_overrides.add(i)), None)
            if override is not None:
                text = override.get('line_text', '')
                if not text or text not in lines[token.line - 1]:
                    report['problems'].append(f'{where}: override line_text "{text}" is not on that line any more; '
                                              'check the override')
                    report['unresolved'].append(f'{where}: stale override')
                    continue
                cell = by_key.get(str(override.get('cell', '')))
                if cell is None or not cn.matches_number(token, cell['number']):
                    report['problems'].append(f'{where}: override cell {override.get("cell")} does not hold this number')
                    report['unresolved'].append(f'{where}: override does not match')
                    continue
                context = context_for(cell, defaults, override.get('context'))
                if context is None:
                    report['unresolved'].append(f'{where}: {cell_key(cell)} needs timepoint/population/comparison/unit '
                                                f'(add "tables" defaults for {cell["file"]} in {OVERRIDES})')
                    continue
                bindings.append({'artifact': artifact, 'artifact_sha256': sha, 'token_index': index,
                                 'result_id': record_for(cell, context), 'context': context})
                report['bound'].append(f'{where} -> {cell_key(cell)} (override)')
                continue
            candidates = [c for c in all_cells if cn.matches_number(token, c['number'])]
            if not candidates:
                report['unbound'].append(f'{where}: no single-number CSV cell holds it')
                continue
            if len(candidates) > 1:
                sentence = words(token.context)
                scored = sorted(((len(sentence & (words(c['label']) | words(c['column']) | words(Path(c['file']).stem))), c)
                                 for c in candidates), key=lambda s: -s[0])
                best = scored[0]
                hint = (f'best guess {cell_key(best[1])}' if best[0] and (len(scored) == 1 or scored[1][0] < best[0])
                        else 'no cell fits the sentence better than another')
                report['suggested'].append(f'{where}: {len(candidates)} cells ({", ".join(cell_key(c) for _, c in scored[:4])}'
                                           f'{", ..." if len(scored) > 4 else ""}); {hint}. Confirm with a "numbers" '
                                           f'override (line_text: a few words of that line)')
                continue
            cell = candidates[0]
            context = context_for(cell, defaults)
            if context is None:
                report['unresolved'].append(f'{where}: {cell_key(cell)} needs timepoint/population/comparison/unit '
                                            f'(add "tables" defaults for {cell["file"]} in {OVERRIDES})')
                continue
            bindings.append({'artifact': artifact, 'artifact_sha256': sha, 'token_index': index,
                             'result_id': record_for(cell, context), 'context': context})
            report['bound'].append(f'{where} -> {cell_key(cell)}')
    for i, override in enumerate(overrides):
        if i not in used_overrides:
            report['problems'].append(f'{OVERRIDES}: numbers entry {i + 1} matched no number '
                                      f'({override.get("artifact")}:{override.get("line")} "{override.get("number")}")')
    return {'bindings': bindings, 'results': list(results.values()), 'report': report}


def write_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_file() and path.read_text(encoding='utf-8') != text:
        backup = path.with_name(path.name + '.bak')
        if backup.exists() and backup.read_bytes() != path.read_bytes():
            stamp, n = datetime.now().strftime('%Y%m%d-%H%M%S'), 0
            while True:
                backup = path.with_name(f"{path.name}.{stamp}{'-' + str(n) if n else ''}.bak")
                try:
                    with open(backup, 'xb') as out:
                        out.write(path.read_bytes())
                    break
                except FileExistsError:
                    n += 1
        else:
            backup.write_bytes(path.read_bytes())
    handle, temporary = tempfile.mkstemp(dir=path.parent, prefix='.' + path.name)
    with os.fdopen(handle, 'w', encoding='utf-8') as out:
        out.write(text)
    os.replace(temporary, path)


def find_project(start: Path) -> Path | None:
    start = start.resolve()
    return next((p / 'project.json' for p in [start, *start.parents] if (p / 'project.json').is_file()), None)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    parser = argparse.ArgumentParser(prog='manuwright bind', description='Propose result bindings from results/*.csv.')
    parser.add_argument('--project', help='project.json (default: the paper folder you are in)')
    parser.add_argument('--write', action='store_true', help='write review/result_bindings.json')
    args = parser.parse_args(argv)
    manifest = Path(args.project) if args.project else find_project(Path.cwd())
    if not manifest or not manifest.is_file():
        print('manuwright bind: run it inside a paper folder (project.json) or pass --project', file=sys.stderr)
        return 2
    root = manifest.parent.resolve()
    try:
        config = json.loads(manifest.read_text(encoding='utf-8'))
        proposal = propose(root, config)
    except (OSError, ValueError, KeyError) as exc:
        print(f'manuwright bind: {exc}', file=sys.stderr)
        return 2
    report = proposal['report']
    for title, key in (('Bound', 'bound'), ('Kept (unchanged since bound)', 'kept'),
                       ('Several cells: confirm with an override', 'suggested'),
                       ('Unresolved', 'unresolved'), ('In no single-number cell', 'unbound'), ('Problems', 'problems')):
        if report[key]:
            print(f'\n{title} ({len(report[key])}):')
            for line in report[key]:
                print('  ' + line)
    open_items = sum(len(report[k]) for k in ('suggested', 'unresolved', 'unbound'))
    print(f'\n{len(proposal["bindings"])} number(s) bound; {open_items} still open.')
    if report['problems']:
        print(f'Fix the {len(report["problems"])} problem(s) in {OVERRIDES} first; nothing written.', file=sys.stderr)
        return 1
    if not args.write:
        print('Nothing written. `manuwright bind --write` saves the bound ones'
              + ('; the open ones keep verify failing until they are resolved.' if open_items else '.'))
        return 0 if not open_items else 1
    target_name = config.get('result_bindings') or DEFAULT_BINDINGS
    target = inside(root, target_name)
    write_atomic(target, json.dumps({'results': proposal['results'], 'bindings': proposal['bindings']},
                                    indent=1, ensure_ascii=False) + '\n')
    if not config.get('result_bindings'):
        config['result_bindings'] = target_name
        write_atomic(manifest, json.dumps(config, indent=2, ensure_ascii=False) + '\n')
    print(f'wrote {target.relative_to(root)}' + ('' if open_items else '; run `manuwright verify`.'))
    return 0 if not open_items else 1


if __name__ == '__main__':
    raise SystemExit(main())

"""Bind numerical claims to a specific CSV cell and result context.

This verifies the declared bindings, not whether prose means what the author
says it means. Semantic data review remains mandatory for submission.
"""
from __future__ import annotations
import csv
import hashlib
import json
from pathlib import Path

CONTEXT = ('outcome', 'timepoint', 'population', 'comparison', 'statistic', 'unit')


def inside(root: Path, value: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ValueError('expected a nonempty project-relative path')
    path = (root / value.replace('\\', '/')).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f'path escapes project: {value}')
    return path


def plain_name(value) -> bool:
    """A paper_id that is one plain folder name (it names ~/.manuwright/envs/<paper_id>): no separator, drive or
    dot segment, no surrounding spaces. The single rule for project.json, `manuwright env/run` and figures."""
    return (isinstance(value, str) and value == value.strip() and value not in ('', '.', '..')
            and not any(c in value for c in '/\\:'))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_bindings(root, manifest, paper_id, artifacts, checker, results_dir=None):
    """results_dir: when given, every bound CSV must be a regular file inside it (not a copy elsewhere)."""
    data = json.loads(manifest.read_text(encoding='utf-8'))
    records = {}
    digests, tables = {}, {}  # one read per file, however many results or bindings point at it

    def cached_digest(path):
        if path not in digests:
            digests[path] = digest(path)
        return digests[path]

    def csv_rows(path):
        if path not in tables:
            with path.open(encoding='utf-8-sig', newline='') as stream:
                reader = csv.DictReader(stream)
                names = reader.fieldnames or []
                if len(names) != len(set(names)):
                    raise ValueError(f'duplicate column names in {path.name}: a binding could read the wrong one')
                tables[path] = list(reader)
        return tables[path]
    for record in data['results']:
        key = record['result_id']
        if key in records:
            raise ValueError(f'duplicate result_id: {key}')
        if record['paper_id'] != paper_id:
            raise ValueError(f'wrong paper for {key}')
        if any(not isinstance(record.get(k), str) or not record[k].strip() for k in CONTEXT):
            raise ValueError(f'incomplete result context: {key}')
        source = record['source']
        path = inside(root, source['file'])
        if results_dir is not None and (not path.is_relative_to(Path(results_dir).resolve()) or not path.is_file()
                                        or (Path(root) / source['file']).is_symlink()):
            raise ValueError(f'bound CSV is not a regular file in the results directory: {source["file"]}')
        if cached_digest(path) != source['sha256']:
            raise ValueError(f'stale CSV source: {key}')
        rows = csv_rows(path)
        row = source['row']
        if type(row) is not int or row < 2 or row - 2 >= len(rows):
            raise ValueError(f'invalid CSV row: {key}')
        raw = rows[row - 2][source['column']]
        # Cells must encode one numeric value/bound, not a mean+SD composite.
        values = checker.extract_numbers_from_text(raw)
        if len(values) != 1 or str(record['raw']).strip() != raw.strip():
            raise ValueError(f'result does not match exact CSV cell: {key}')
        records[key] = (record, checker.ResultNumber(values[0], checker.UNARY_DASH_RE.sub('-', raw.translate(checker.TYPOGRAPHIC)), path, row,
                                                  source['column']))
    by_artifact = {inside(root, a): [] for a in artifacts}
    for binding in data['bindings']:
        path = inside(root, binding['artifact'])
        if path not in by_artifact:
            raise ValueError(f'binding is outside numeric_artifacts: {binding["artifact"]}')
        by_artifact[path].append(binding)
    count = 0
    for path, bindings in by_artifact.items():
        tokens = checker.iter_artifact_numbers(path)
        seen = set()
        for binding in bindings:
            index = binding['token_index']
            if type(index) is not int or index < 0 or index >= len(tokens) or index in seen:
                raise ValueError(f'duplicate/invalid token index in {path.name}')
            seen.add(index)
            if cached_digest(path) != binding['artifact_sha256']:
                raise ValueError(f'stale numeric binding: {path.name}')
            record, cell = records[binding['result_id']]
            if any(binding['context'].get(k) != record[k] for k in CONTEXT):
                raise ValueError(f'outcome/group/timepoint/unit mismatch: {path.name}, token {index}')
            if not checker.matches_number(tokens[index], cell):
                raise ValueError(f'number does not match its bound result: {path.name}, token {index}')
            count += 1
        if seen != set(range(len(tokens))):
            raise ValueError(f'unbound numeric claims in {path.name}')
    return count

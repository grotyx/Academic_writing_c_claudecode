"""Project manifests, immutable dependency snapshots, and verification profiles."""
from __future__ import annotations
import importlib.util
import json
import re
from pathlib import Path
from .results import inside, digest, validate_bindings

REPO = Path(__file__).resolve().parents[1]
STUDY_TYPES = {'original_research', 'systematic_review', 'narrative_review', 'case_report'}
SEMANTIC_CHECKS = {'constraint', 'citation_semantics', 'data_semantics', 'logic', 'style', 'reporting'}


def checker(name):
    spec = importlib.util.spec_from_file_location(name, REPO / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_project(path):
    path = Path(path).resolve()
    config = json.loads(path.read_text(encoding='utf-8'))
    if config.get('schema_version') != 1 or not config.get('paper_id'):
        raise ValueError('project requires schema_version: 1 and paper_id')
    if config.get('study_type') not in STUDY_TYPES:
        raise ValueError('unsupported study_type')
    artifacts = config.get('artifacts')
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError('artifacts must list manuscript sections in publication order')
    # supplements: supplementary tables/figures (e.g. drafts/supp_table_1.md) -- checked like tables,
    # built as separate supplementary files, never numbered as main Table N.
    paths = artifacts + config.get('tables', []) + config.get('supplements', []) + config.get('figures', [])
    resolved = [inside(path.parent, item) for item in paths]
    if len(resolved) != len(set(resolved)):
        raise ValueError('duplicate artifact paths')
    missing = [str(item.relative_to(path.parent)) for item in resolved if not item.is_file()]
    if missing:
        raise ValueError('one or more declared artifacts are missing: ' + ', '.join(missing))
    for key in ('evidence', 'draft_plan'):
        if not inside(path.parent, config[key]).is_file():
            raise ValueError(f'missing {key}')
    if not config.get('analysis_plan') and not config.get('analysis_not_applicable'):
        raise ValueError('provide analysis_plan or an explicit analysis_not_applicable reason')
    if config['study_type'] == 'original_research' and not config.get('analysis_plan'):
        raise ValueError('original research requires an analysis plan')
    for item in config.get('numeric_artifacts', []):
        if inside(path.parent, item) not in resolved:
            raise ValueError('numeric_artifacts must be in artifacts, tables or supplements')
    number_of = re.compile(r'table[_\- ]?(\d+)', re.I)
    seen = {}
    for item in config.get('tables', []):
        if re.search(r'supp', Path(item).stem, re.I):
            raise ValueError(f'{item} looks supplementary: list it under "supplements", not "tables" '
                             '(a main table number must not be reused)')
        match = number_of.search(Path(item).stem)
        if match and match.group(1) in seen:
            raise ValueError(f'{item} and {seen[match.group(1)]} would both be Table {match.group(1)}')
        if match:
            seen[match.group(1)] = item
    listed = set(resolved[:len(artifacts)])
    if config.get('abstract') and inside(path.parent, config['abstract']) not in listed:
        raise ValueError('abstract must be one of the published artifacts')
    if not config.get('abstract') and any(re.search(r'abstract', Path(a).stem, re.I) for a in artifacts):
        raise ValueError('an abstract artifact is published; declare it in the abstract field')
    for key in ('terminology', 'style_spec'):
        if config.get(key) and not inside(path.parent, config[key]).is_file():
            raise ValueError(f'missing {key}')
    if config.get('journal') and config['journal'] not in checker('journal_styles').STYLES:
        raise ValueError('unknown journal preset: ' + str(config['journal']) + ' (see scripts/journal_styles.py)')
    return path, config


def snapshot(path, config):
    root = path.parent
    files = {path}
    for key in ('artifacts', 'tables', 'supplements', 'figures', 'dependencies'):
        files.update(inside(root, item) for item in config.get(key, []))
    for key in ('evidence', 'draft_plan', 'analysis_plan', 'result_bindings', 'abstract',
                'response', 'comments', 'ai_usage', 'checklist', 'terminology', 'style_spec'):
        if config.get(key):
            record = inside(root, config[key])
            # Submission records are written late; before they exist a draft profile must still
            # run. The submission profile blocks on their absence separately.
            if key in ('ai_usage', 'checklist') and not record.exists():
                continue
            files.add(record)
    reference = (config.get('docx') or {}).get('reference') if isinstance(config.get('docx'), dict) else None
    if reference:  # the Word template shapes the built manuscript
        files.add(inside(root, reference))
    metadata = inside(root, config['evidence']).with_name('reference_metadata.json') if config.get('evidence') else None
    if metadata and metadata.exists():  # cached PubMed metadata shapes the journal-formatted bibliography
        files.add(metadata)
    for key in ('draft_plan', 'analysis_plan'):
        if config.get(key):
            receipt = inside(root, config[key]).with_suffix('.approval.json')
            if receipt.exists():
                files.add(receipt)
    if config.get('results'):
        directory = inside(root, config['results'])
        if not directory.is_dir():
            raise ValueError('results directory not found')
        files.update(directory.rglob('*.csv'))
    if config.get('result_bindings'):
        bindings = json.loads(inside(root, config['result_bindings']).read_text(encoding='utf-8'))
        files.update(inside(root, item['source']['file']) for item in bindings['results'])
    if config.get('response'):
        response = inside(root, config['response'])
        revision = re.fullmatch(r'REV(\d+)', response.parent.name)
        if revision and response.parent.parent.name == 'revision':
            draft_root = response.parent.parent.parent
            files.update(draft_root.glob('*.md'))
            for prior in range(1, int(revision.group(1))):
                files.update((draft_root / 'revision' / f'REV{prior}').glob('*.md'))
    # Content and membership both matter; adding/deleting a dependency invalidates review.
    result = {str(file.relative_to(root)): digest(file) for file in sorted(files)}
    # A review is also bound to the checker implementation and terminology rules.
    for folder in ('harness', 'scripts'):
        for file in sorted((REPO / folder).rglob('*.py')):
            result['@engine/' + file.relative_to(REPO).as_posix()] = digest(file)
    result['@engine/Style/terminology.md'] = digest(REPO / 'Style/terminology.md')
    return result


def version_tuple(text):
    return tuple(int(part) for part in re.findall(r'\d+', str(text))[:3])


def engine_problem(spec, version):
    """Check an optional manifest pin such as '>=1.8,<1.9' against an engine version."""
    ops = {'>=': lambda a, b: a >= b, '<=': lambda a, b: a <= b, '==': lambda a, b: a == b,
           '>': lambda a, b: a > b, '<': lambda a, b: a < b}
    for clause in filter(None, (c.strip() for c in str(spec).split(','))):
        match = re.fullmatch(r'(>=|<=|==|>|<)\s*v?([\d.]+)', clause)
        if not match:
            return f'invalid engine pin clause: {clause!r}'
        if not ops[match.group(1)](version_tuple(version), version_tuple(match.group(2))):
            return f'engine {version} does not satisfy project pin {spec!r}'
    return None


def explain(result, limit=5):
    """Checker result -> True, or the first few issues with artifact/line detail."""
    if result.passed:
        return True
    issues = getattr(result, 'failures', None) or getattr(result, 'issues', None) or []
    lines = ['; '.join(f'{k}={v}' for k, v in issue._asdict().items()) if hasattr(issue, '_asdict') else str(issue)
             for issue in issues[:limit]]
    more = f' (+{len(issues) - limit} more)' if len(issues) > limit else ''
    return (' | '.join(lines) or 'check failed') + more


def completion_problem(key, value):
    """Validate submission completion records (docs/harness_guide.md, Submission output)."""
    if not isinstance(value, dict) or not str(value.get('reviewed_by') or '').strip():
        return f'{key}: object with nonempty reviewed_by required'
    if key == 'ai_usage':
        if type(value.get('used')) is not bool:
            return 'ai_usage: used must be true or false'
        if value['used'] is False:
            return None
        tools = value.get('tools')
        if not str(value.get('disclosure') or '').strip() or not isinstance(tools, list) or not tools:
            return 'ai_usage: disclosure and a nonempty tools list are required when used'
        for tool in tools:
            if not isinstance(tool, dict) or not all(str(tool.get(f) or '').strip() for f in ('tool', 'role')):
                return 'ai_usage: every tools entry needs nonempty tool and role'
        return None
    for field in ('guideline', 'version', 'source_url'):
        if not str(value.get(field) or '').strip():
            return f'checklist: missing {field}'
    items = value.get('items')
    if not isinstance(items, list) or not items:
        return 'checklist: items must be a nonempty list'
    seen = set()
    for item in items:
        ident = str(item.get('id') or '').strip() if isinstance(item, dict) else ''
        if not ident or ident in seen:
            return f'checklist: every item needs a unique nonempty id ({ident or "missing"})'
        seen.add(ident)
        if item.get('status') == 'PASS':
            if not str(item.get('location') or '').strip():
                return f'checklist item {ident}: PASS requires a manuscript location'
        elif item.get('status') == 'NOT_APPLICABLE':
            if not str(item.get('reason') or '').strip():
                return f'checklist item {ident}: NOT_APPLICABLE requires a reason'
        else:
            return f'checklist item {ident}: status must be PASS or NOT_APPLICABLE'
    return None


def receipt_problem(path, dependencies, *, human=False):
    data = json.loads(path.read_text(encoding='utf-8'))
    expected = 'approved' if human else 'PASS'
    if data.get('status') != expected or not data.get('reviewer'):
        return 'missing reviewer or successful status'
    if data.get('dependencies') != dependencies:
        return 'stale/incomplete review dependencies'
    if human:
        if not data.get('decision_reference'):
            return 'missing human decision reference'
    else:
        if data.get('method') not in {'independent', 'human'}:
            return 'independent or human semantic review is required'
        if any(data.get('checks', {}).get(key) != 'PASS' for key in SEMANTIC_CHECKS):
            return 'required semantic checks are missing or failed'
        if data.get('findings') != []:
            return 'unresolved semantic findings'
    return None


def revision_scope(root, config, artifacts):
    module = checker('check_revision_claims')
    response = inside(root, config['response'])
    draft_root = module.infer_draft_root(response)
    included = set(artifacts)
    for claim in module.parse_change_blocks(response.read_text(encoding='utf-8')):
        revised = module.resolve_revised_section_path(claim, response, draft_root)
        if revised is None or revised.resolve() not in included:
            return 'revision claim target is absent from submission artifacts'
    revision = module.infer_revision_id(response)
    if revision:
        number = int(revision[3:])
        for artifact in artifacts:
            stem = re.sub(r'_REV\d+$', '', artifact.stem, flags=re.I)
            versions = [draft_root / 'revision' / f'REV{n}' / name
                        for n in range(number, 0, -1)
                        for name in (f'{stem}_REV{n}.md', f'{stem}.md')]
            latest = next((p.resolve() for p in versions if p.is_file()), None)
            if latest is not None and artifact != latest:
                return f'stale revision artifact: {artifact.name}; use {latest.name}'
    return True


def numeric_scope(root, config, artifacts, number_checker):
    included = {inside(root, name) for name in config.get('numeric_artifacts', [])}
    exemptions = config.get('numeric_exemptions', {})
    if not isinstance(exemptions, dict):
        return 'numeric_exemptions must map artifact paths to reasons'
    excluded = {inside(root, name): reason for name, reason in exemptions.items()}
    if any(p not in artifacts or p in included or not isinstance(reason, str) or not reason.strip()
           for p, reason in excluded.items()):
        return 'invalid numeric exemption: use an omitted artifact and a nonempty reason'
    tables = {inside(root, name) for name in config.get('tables', []) + config.get('supplements', [])}
    for artifact in artifacts:
        if artifact in included or artifact.name.startswith(('01_title', '08_references')):
            continue
        if not number_checker.iter_artifact_numbers(artifact):
            continue
        core = artifact in tables or bool(re.search(r'(?:abstract|results)', artifact.stem, re.I))
        if artifact not in excluded or core:
            return f'unchecked numeric artifact: {artifact.relative_to(root)}'
    return True


def verify(path, profile='draft'):
    path, config = load_project(path)
    root = path.parent
    checks = []
    def record(name, state, detail=''):
        checks.append({'check': name, 'status': state, 'detail': detail})
    def run(name, action):
        try:
            value = action()
            record(name, 'PASS' if value is None or value is True else 'FAIL', '' if value in (None, True) else str(value))
        except (OSError, ValueError, KeyError, TypeError, AttributeError, IndexError) as exc:
            record(name, 'BLOCKED', str(exc))
    if config.get('engine'):
        from . import __version__
        problem = engine_problem(config['engine'], __version__)
        record('engine_pin', 'BLOCKED' if problem else 'PASS', problem or '')
    artifacts = [inside(root, item) for item in config['artifacts'] + config.get('tables', []) + config.get('supplements', [])]
    initial = snapshot(path, config)
    cc = checker('check_citations')
    run('citations', lambda: explain(cc.check_citations(artifacts, evidence_path=inside(root, config['evidence']))))
    lint = checker('lint_manuscript')
    def lint_check():
        registry = inside(root, config['terminology']) if config.get('terminology') else lint.TERMINOLOGY_FILE
        terms = lint.load_forbidden_terms(registry)
        issues = [issue for artifact in artifacts for issue in lint.lint_file(artifact, terms)]
        if not issues:
            return True
        shown = ' | '.join(f'{code} {Path(path).name}:{line} {message}' for code, path, line, message in issues[:5])
        return f'{len(issues)} lint findings: {shown}'
    run('manuscript_lint', lint_check)
    if config.get('style_spec'):
        style = checker('check_style')
        def style_check():
            targets = style.parse_spec_targets(inside(root, config['style_spec']))
            if not targets:
                raise ValueError('style_spec has no parsable Target Metrics')
            issues = [f'{a.name}: {msg}' for a in artifacts for msg in style.check_file(a, targets)[1]]
            return True if not issues else ' | '.join(issues)
        run('style_metrics', style_check)
    plan_module = checker('plan_validation')
    for key, kind in [('draft_plan', 'draft'), ('analysis_plan', 'analysis')]:
        if not config.get(key):
            record(key, 'NOT_APPLICABLE', config['analysis_not_applicable']); continue
        def validate_plan(key=key, kind=kind):
            plan = inside(root, config[key]); text = plan.read_text(encoding='utf-8')
            missing = plan_module.validate_plan_content(text, kind)
            if missing:
                return 'missing/empty sections: ' + plan_module.describe_missing(missing)
            if not __import__('re').search(r'-\s*\[[xX]\]\s*(?:\*\*)?사용자 승인 완료', text):
                return 'missing checked approval line'
            return plan_module.approval_problem(plan, required=profile != 'draft')
        run(key, validate_plan)
    numeric = config.get('numeric_artifacts', [])
    cn = checker('check_numbers')
    run('numeric_scope', lambda: numeric_scope(root, config, artifacts, cn))
    if numeric:
        run('number_tokens', lambda: explain(cn.check_numbers([inside(root, item) for item in numeric],
            results_dir=inside(root, config['results']))))
        if config.get('result_bindings'):
            def bound():
                validate_bindings(root, inside(root, config['result_bindings']), config['paper_id'], numeric, cn)
            run('result_bindings', bound)
        else:
            record('result_bindings', 'BLOCKED' if profile != 'draft' else 'NOT_APPLICABLE',
                   'Legacy token checking does not validate outcome/group/timepoint/unit; add result_bindings.')
    elif config.get('numbers_not_applicable') and config['study_type'] != 'original_research':
        record('numbers', 'NOT_APPLICABLE', config['numbers_not_applicable'])
    else:
        record('numbers', 'BLOCKED', 'Declare numeric_artifacts or a justified non-research exemption.')
    if config.get('abstract'):
        body = [item for item in artifacts if item != inside(root, config['abstract'])]
        run('abstract', lambda: explain(checker('check_abstract').check_abstract(inside(root, config['abstract']), body)))
    else:
        record('abstract', 'NOT_APPLICABLE', 'No separate abstract declared.')
    cross = checker('check_crossrefs')
    def crossrefs():
        inventory = {'table': set(), 'figure': set()}
        for kind, field, pattern in [('table','tables',cross.TABLE_FILE_RE), ('figure','figures',cross.FIGURE_FILE_RE)]:
            for value in config.get(field, []):
                match = pattern.search(Path(value).stem)
                if not match:
                    return f'{field} filenames must contain a stable number: {value}'
                number = int(match.group(1))
                if number in inventory[kind]:
                    return f'duplicate {kind} number {number}'
                inventory[kind].add(number)
        body = [inside(root, value) for value in config['artifacts']
                if not Path(value).name.startswith(('01_title','08_references','09_figure_legends'))]
        mentions = [mention for art in body for mention in cross.find_mentions(art)]
        for kind in ('table','figure'):
            order = cross.first_mention_order(mentions, kind)
            if set(order) != inventory[kind]:
                return f'{kind} references differ from declared inventory (including empty inventory)'
            if order != sorted(order):
                return f'{kind} first appearances are out of order'
        return True
    run('crossrefs', crossrefs)
    refs = checker('format_references')
    def bibliography():
        result = refs.build(artifacts, evidence_path=inside(root, config['evidence']), style='numbered',
                            journal=config.get('journal'))
        problems = result.unknown + result.missing_citation + result.incomplete_authors + result.unparsed
        return True if not problems else 'bibliography incomplete for ' + ', '.join(problems)
    run('bibliography', bibliography)
    if profile == 'revision' or config.get('response'):
        run('revision_scope', lambda: revision_scope(root, config, artifacts))
        run('response_citations', lambda: explain(cc.check_citations([inside(root, config['response'])],
            evidence_path=inside(root, config['evidence']))))
        run('revision_claims', lambda: explain(checker('check_revision_claims').check_revision_claims(
            inside(root, config['response']), strict=True)))
        run('response_coverage', lambda: explain(checker('check_response_coverage').check_response_coverage(
            inside(root, config['response']), comments_path=inside(root, config['comments']), strict=True)))
    if profile != 'draft':
        def semantic():
            return receipt_problem(inside(root, config['semantic_review']), initial)
        run('semantic_review', semantic)
    if profile == 'submission':
        run('human_signoff', lambda: receipt_problem(inside(root, config['human_signoff']), initial, human=True))
        def required_json(key):
            return completion_problem(key, json.loads(inside(root, config[key]).read_text(encoding='utf-8')))
        run('ai_disclosure', lambda: required_json('ai_usage'))
        run('reporting_checklist', lambda: required_json('checklist'))
    if snapshot(path, config) != initial:
        record('snapshot', 'FAIL', 'inputs changed during verification')
    status = 'FAIL' if any(x['status']=='FAIL' for x in checks) else 'BLOCKED' if any(x['status']=='BLOCKED' for x in checks) else 'PASS'
    return {'schema_version': 1, 'paper_id': config['paper_id'], 'profile': profile,
            'status': status, 'checks': checks, 'dependencies': initial}

"""Project manifests, immutable dependency snapshots, and verification profiles."""
from __future__ import annotations
import importlib.util
import json
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
    paths = artifacts + config.get('tables', []) + config.get('figures', [])
    resolved = [inside(path.parent, item) for item in paths]
    if len(resolved) != len(set(resolved)):
        raise ValueError('duplicate artifact paths')
    if any(not item.is_file() for item in resolved):
        raise ValueError('one or more declared artifacts are missing')
    for key in ('evidence', 'draft_plan'):
        if not inside(path.parent, config[key]).is_file():
            raise ValueError(f'missing {key}')
    if not config.get('analysis_plan') and not config.get('analysis_not_applicable'):
        raise ValueError('provide analysis_plan or an explicit analysis_not_applicable reason')
    if config['study_type'] == 'original_research' and not config.get('analysis_plan'):
        raise ValueError('original research requires an analysis plan')
    for item in config.get('numeric_artifacts', []):
        if inside(path.parent, item) not in resolved:
            raise ValueError('numeric_artifacts must be in artifacts or tables')
    return path, config


def snapshot(path, config):
    root = path.parent
    files = {path}
    for key in ('artifacts', 'tables', 'figures', 'dependencies'):
        files.update(inside(root, item) for item in config.get(key, []))
    for key in ('evidence', 'draft_plan', 'analysis_plan', 'result_bindings', 'abstract',
                'response', 'comments', 'ai_usage', 'checklist'):
        if config.get(key):
            files.add(inside(root, config[key]))
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
        import re
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
    artifacts = [inside(root, item) for item in config['artifacts'] + config.get('tables', [])]
    initial = snapshot(path, config)
    cc = checker('check_citations')
    run('citations', lambda: cc.check_citations(artifacts, evidence_path=inside(root, config['evidence'])).passed)
    lint = checker('lint_manuscript')
    def lint_check():
        terms = lint.load_forbidden_terms(lint.TERMINOLOGY_FILE)
        issues = [issue for artifact in artifacts for issue in lint.lint_file(artifact, terms)]
        return True if not issues else f'{len(issues)} lint findings; run scripts/lint_manuscript.py for details'
    run('manuscript_lint', lint_check)
    plan_module = checker('plan_validation')
    for key, kind in [('draft_plan', 'draft'), ('analysis_plan', 'analysis')]:
        if not config.get(key):
            record(key, 'NOT_APPLICABLE', config['analysis_not_applicable']); continue
        def validate_plan(key=key, kind=kind):
            plan = inside(root, config[key]); text = plan.read_text(encoding='utf-8')
            missing = plan_module.validate_plan_content(text, kind)
            if missing:
                return 'missing/empty sections: ' + ', '.join(missing)
            if not __import__('re').search(r'-\s*\[[xX]\]\s*(?:\*\*)?사용자 승인 완료', text):
                return 'missing checked approval line'
            return plan_module.approval_problem(plan, required=profile != 'draft')
        run(key, validate_plan)
    numeric = config.get('numeric_artifacts', [])
    cn = checker('check_numbers')
    if numeric:
        run('number_tokens', lambda: cn.check_numbers([inside(root, item) for item in numeric],
            results_dir=inside(root, config['results'])).passed)
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
        run('abstract', lambda: checker('check_abstract').check_abstract(inside(root, config['abstract']), body).passed)
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
        result = refs.build(artifacts, evidence_path=inside(root, config['evidence']), style='numbered')
        return not result.unknown and not result.missing_citation
    run('bibliography', bibliography)
    if profile == 'revision' or config.get('response'):
        run('response_citations', lambda: cc.check_citations([inside(root, config['response'])],
            evidence_path=inside(root, config['evidence'])).passed)
        run('revision_claims', lambda: checker('check_revision_claims').check_revision_claims(
            inside(root, config['response']), strict=True).passed)
        run('response_coverage', lambda: checker('check_response_coverage').check_response_coverage(
            inside(root, config['response']), comments_path=inside(root, config['comments']), strict=True).passed)
    if profile != 'draft':
        def semantic():
            return receipt_problem(inside(root, config['semantic_review']), initial)
        run('semantic_review', semantic)
    if profile == 'submission':
        run('human_signoff', lambda: receipt_problem(inside(root, config['human_signoff']), initial, human=True))
        def required_json(key):
            value = json.loads(inside(root, config[key]).read_text(encoding='utf-8'))
            if key == 'ai_usage':
                return (type(value.get('used')) is bool and bool(value.get('reviewed_by')) and
                        (value['used'] is False or (bool(value.get('disclosure')) and bool(value.get('tools')))))
            return (bool(value.get('guideline')) and bool(value.get('version')) and
                    bool(value.get('source_url')) and bool(value.get('reviewed_by')) and
                    bool(value.get('items')) and all(item.get('status') == 'PASS' or
                    (item.get('status') == 'NOT_APPLICABLE' and item.get('reason')) for item in value['items']))
        run('ai_disclosure', lambda: required_json('ai_usage'))
        run('reporting_checklist', lambda: required_json('checklist'))
    if snapshot(path, config) != initial:
        record('snapshot', 'FAIL', 'inputs changed during verification')
    status = 'FAIL' if any(x['status']=='FAIL' for x in checks) else 'BLOCKED' if any(x['status']=='BLOCKED' for x in checks) else 'PASS'
    return {'schema_version': 1, 'paper_id': config['paper_id'], 'profile': profile,
            'status': status, 'checks': checks, 'dependencies': initial}

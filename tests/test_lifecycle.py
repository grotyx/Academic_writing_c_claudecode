"""manuwright init / update / auto-update safety rules (distribution phase 3)."""
import json
import os
from pathlib import Path

import pytest

from harness import __version__
from harness import project as api
from harness.project import engine_problem, verify
from manuwright import lifecycle
from tests.test_harness import project, put, sign  # noqa: F401  (fixture reuse)

ENGINE = Path(__file__).resolve().parents[1]


@pytest.fixture(autouse=True)
def isolated_home(tmp_path_factory, monkeypatch):
    monkeypatch.setenv('MANUWRIGHT_HOME', str(tmp_path_factory.mktemp('pfhome')))
    monkeypatch.delenv('MANUWRIGHT_NO_UPDATE_CHECK', raising=False)


def test_init_creates_unapproved_starter_and_never_overwrites(tmp_path):
    root = tmp_path / 'My Paper'
    put(root / 'AGENTS.md', 'local author instructions\n')
    assert lifecycle.init(ENGINE, [str(root)]) == 0
    manifest = json.loads((root / 'project.json').read_text(encoding='utf-8'))
    assert manifest['paper_id'] == 'my_paper'
    assert (root / 'AGENTS.md').read_text(encoding='utf-8') == 'local author instructions\n'
    for plan in ('drafts/draft_plan.md', 'data/analysis_plan.md'):
        assert '- [x]' not in (root / plan).read_text(encoding='utf-8')
    assert not list(root.rglob('*.approval.json'))
    assert lifecycle.known_projects() == [root / 'project.json']
    assert lifecycle.init(ENGINE, [str(root)]) == 1


@pytest.mark.parametrize('spec,version,ok', [('>=1.8,<1.9', '1.8.3', True), ('>=1.8,<1.9', '1.9.0', False),
                                             ('==1.7.9', '1.7.9', True), ('~1.8', '1.8.0', False)])
def test_engine_pin(spec, version, ok):
    assert (engine_problem(spec, version) is None) is ok


def test_verify_blocks_mismatched_engine_pin(project):
    data = json.loads(project.read_text(encoding='utf-8'))
    data['engine'] = '<1.0'
    put(project, data)
    report = verify(project)
    assert report['status'] == 'BLOCKED'
    assert any(c['check'] == 'engine_pin' and c['status'] == 'BLOCKED' for c in report['checks'])


def test_auto_update_blockers(project):
    major, minor, patch = api.version_tuple(__version__)
    next_patch, next_minor = f'{major}.{minor}.{patch + 1}', f'{major}.{minor + 1}.0'
    assert lifecycle.auto_blockers(api, __version__, next_patch, [project]) == []
    assert 'patches only' in lifecycle.auto_blockers(api, __version__, next_minor, [])[0]
    data = json.loads(project.read_text(encoding='utf-8'))
    data['engine'] = f'=={__version__}'
    put(project, data)
    assert 'pins engine' in lifecycle.auto_blockers(api, __version__, next_patch, [project])[0]
    del data['engine']
    put(project, data)
    sign(project)
    assert 'fresh review' in lifecycle.auto_blockers(api, __version__, next_patch, [project])[0]


@pytest.fixture
def fake_release(monkeypatch, tmp_path):
    """Installed-looking engine (no .git) with a pretend newer patch release."""
    major, minor, patch = api.version_tuple(__version__)
    monkeypatch.setattr(lifecycle, 'latest_release', lambda: f'{major}.{minor}.{patch + 1}')
    calls = []
    monkeypatch.setattr(lifecycle.subprocess, 'call', lambda cmd: calls.append(cmd) or 0)
    return tmp_path / 'site-packages' / 'manuwright', calls


def test_auto_update_is_opt_in_and_daily(fake_release, capsys):
    engine, calls = fake_release
    assert lifecycle.update(engine, ['--auto']) == 0
    assert 'available' in capsys.readouterr().out and not calls
    lifecycle.config(['set', 'auto-update', 'on'])
    assert lifecycle.update(engine, ['--auto']) == 0
    assert not calls  # already checked today
    lifecycle.save('state.json', {})
    assert lifecycle.update(engine, ['--auto']) == 0
    assert len(calls) == 1 and calls[0][-1].endswith('@v' + lifecycle.latest_release())
    assert '->' in (lifecycle.home() / 'update.log').read_text(encoding='utf-8')


def test_auto_update_waits_for_fresh_reviews(fake_release, project, capsys):
    engine, calls = fake_release
    lifecycle.config(['set', 'auto-update', 'on'])
    lifecycle.register(project)
    sign(project)
    assert lifecycle.update(engine, ['--auto']) == 0
    assert not calls and 'not auto-applied' in capsys.readouterr().out


def test_manual_update_skips_reinstall_when_up_to_date(fake_release, monkeypatch, capsys):
    engine, calls = fake_release
    monkeypatch.setattr(lifecycle, 'latest_release', lambda: __version__)
    assert lifecycle.update(engine, []) == 0
    assert not calls and 'up to date' in capsys.readouterr().out


def test_windows_uv_update_prints_command_instead_of_replacing_running_exe(fake_release, monkeypatch, capsys):
    engine, calls = fake_release
    monkeypatch.setattr(lifecycle, 'install_command', lambda tag: ['uv', 'tool', 'install', '--force', f'x@v{tag}'])
    monkeypatch.setattr(lifecycle, 'on_windows', lambda: True)
    assert lifecycle.update(engine, []) == 0
    out = capsys.readouterr().out
    assert not calls and 'uv tool install --force' in out and 'new terminal' in out


def test_update_refuses_source_checkout():
    assert lifecycle.update(ENGINE, ['--check']) == 1


# --- phase 4: agent adapters -------------------------------------------------

MANIFESTS = ['.claude-plugin/plugin.json', '.codex-plugin/plugin.json', 'plugin.json', 'gemini-extension.json']


@pytest.mark.parametrize('manifest', MANIFESTS)
def test_adapter_versions_match_engine(manifest):
    assert json.loads((ENGINE / manifest).read_text(encoding='utf-8'))['version'] == __version__


def test_adapter_references_exist():
    hooks = json.loads((ENGINE / 'hooks/hooks.json').read_text(encoding='utf-8'))['hooks']
    names = {h['command'].split('manuwright hook ')[1].split()[0].rstrip(';') for event in hooks.values()
             for group in event for h in group['hooks']}
    from manuwright.cli import HOOKS
    assert names == set(HOOKS)
    assert all((ENGINE / 'scripts/hooks' / script).is_file() for script in HOOKS.values())
    assert (ENGINE / json.loads((ENGINE / 'gemini-extension.json').read_text(encoding='utf-8'))['contextFileName']).is_file()
    for skill in (ENGINE / 'skills').iterdir():
        head = (skill / 'SKILL.md').read_text(encoding='utf-8').split('---')[1]
        assert f'name: {skill.name}' in head and 'description:' in head


def test_agents_dry_run_lists_native_commands(monkeypatch, capsys):
    monkeypatch.setattr(lifecycle.shutil, 'which', lambda name: '/bin/' + name)
    monkeypatch.setattr(lifecycle.subprocess, 'call', lambda cmd: pytest.fail('dry run executed ' + str(cmd)))
    assert lifecycle.agents(ENGINE, ['install', '--dry-run']) == 0
    out = capsys.readouterr().out
    for line in ('claude plugin marketplace add', 'codex plugin add manuwright@manuwright',
                 'agy plugin install', 'muse skills install', '[opencode] copy'):
        assert line in out
    assert lifecycle.agents(ENGINE, ['install', '--only', 'cursor']) == 2


def test_agents_run_resolved_paths_and_survive_a_missing_program(monkeypatch, capsys):
    # Windows: npm agent CLIs are .cmd shims; CreateProcess only finds them by full path, and a
    # missing program must not abort the remaining agents with a traceback.
    monkeypatch.setattr(lifecycle.shutil, 'which', lambda name: f'C:/npm/{name}.cmd')
    calls = []
    def fake_call(cmd):
        calls.append(cmd)
        if cmd[0].endswith('muse.cmd'):
            raise FileNotFoundError(2, 'The system cannot find the file specified')
        return 0
    monkeypatch.setattr(lifecycle.subprocess, 'call', fake_call)
    assert lifecycle.agents(ENGINE, ['update', '--only', 'claude,muse,agy']) == 1
    assert calls and all(cmd[0].endswith('.cmd') for cmd in calls)
    assert any(cmd[0].endswith('agy.cmd') for cmd in calls)  # agents after the failure still run
    assert '[muse] exit FileNotFoundError' in capsys.readouterr().out


def test_agents_update_repoints_marketplaces_to_the_current_engine(monkeypatch, capsys):
    # A reinstall can move the engine (python3.11 -> python3.12 site-packages); `marketplace update`
    # / `upgrade` then fail on the old, deleted path, so update re-adds from the current folder.
    monkeypatch.setattr(lifecycle.shutil, 'which', lambda name: '/bin/' + name)
    assert lifecycle.agents(ENGINE, ['update', '--only', 'claude,codex', '--dry-run']) == 0
    out = capsys.readouterr().out
    for agent in ('claude', 'codex'):
        assert f'[{agent}] {agent} plugin marketplace add {ENGINE}' in out
    assert 'marketplace update' not in out and 'marketplace upgrade' not in out


def hook_run(args, cwd, stdin='{}'):
    import subprocess, sys
    return subprocess.run([sys.executable, str(ENGINE / 'manuwright/cli.py'), 'hook', *args], cwd=cwd, input=stdin,
                          capture_output=True, text=True, encoding='utf-8', timeout=60,
                          env={k: v for k, v in __import__('os').environ.items() if k != 'CLAUDE_PROJECT_DIR'})


def test_plugin_hook_gates_paper_folder_and_skips_template_checkout(tmp_path):
    event = json.dumps({'tool_name': 'Write', 'cwd': str(tmp_path), 'tool_input': {'file_path': 'drafts/04_methods.md'}})
    blocked = hook_run(['gate'], tmp_path, event)
    assert blocked.returncode == 2 and 'BLOCKED' in blocked.stderr
    put(tmp_path / '.claude/settings.json', '{"hooks": {"x": "sh scripts/hooks/run.sh scripts/hooks/enforce_gates.py"}}')
    assert hook_run(['gate'], tmp_path, event).returncode == 0  # local template hooks already enforce


def test_plugin_session_hook_prints_contract(tmp_path):
    out = hook_run(['session'], tmp_path).stdout
    assert 'WORKFLOW CONTRACT' in out and 'manuwright verify' in out


# --- reviewer settings -------------------------------------------------------

def test_config_sets_models_and_reviewers(capsys):
    assert lifecycle.config(['set', 'main-model', 'claude-opus-5-5']) == 0
    assert lifecycle.config(['set', 'review.reviewers', 'codex, opencode,openrouter']) == 0
    assert lifecycle.config(['set', 'review.opencode-model', 'openai/gpt-x']) == 0
    assert lifecycle.config(['set', 'review.openrouter-models', 'deepseek/a,qwen/b']) == 0
    data = lifecycle.load('config.json', {})
    assert data['main_model'] == 'claude-opus-5-5'
    assert data['review'] == {'reviewers': ['codex', 'opencode', 'openrouter'], 'opencode_model': 'openai/gpt-x',
                              'openrouter_models': ['deepseek/a', 'qwen/b']}
    assert lifecycle.config(['unset', 'review.opencode-model']) == 0
    assert 'opencode_model' not in lifecycle.load('config.json', {})['review']
    assert lifecycle.config(['set', 'colour', 'blue']) == 2


def test_reviewers_come_from_settings_with_models(monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location('cr', ENGINE / 'scripts' / 'critical_review.py')
    cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
    lifecycle.config(['set', 'main-model', 'deepseek/a'])
    lifecycle.config(['set', 'review.opencode-model', 'openai/gpt-x'])
    lifecycle.config(['set', 'review.openrouter-models', 'deepseek/a,qwen/b'])
    cfg = cr.settings()
    got = cr.expand_reviewers(['codex', 'opencode', 'muse:m1', 'openrouter', 'openrouter:z/c', 'claude-cli'], cfg)
    assert got == [('codex', None), ('opencode', 'openai/gpt-x'), ('muse', 'm1'), ('openrouter', 'deepseek/a'),
                   ('openrouter', 'qwen/b'), ('openrouter', 'z/c'), ('claude', None)]
    assert cr.not_independent(got, cfg['main_model']) == ['deepseek/a']
    workdir, prompt = Path('/tmp/w'), Path('/tmp/p.md')
    assert cr.local_argv('opencode', 'openai/gpt-x', prompt, workdir)[0][:6] == ['opencode', 'run', '--agent', 'plan', '--dir', str(workdir)]
    assert '--disable-web-tools' in cr.local_argv('muse', None, prompt, workdir)[0]


def test_local_reviewer_runs_outside_the_paper(monkeypatch, tmp_path):
    import importlib.util
    spec = importlib.util.spec_from_file_location('cr', ENGINE / 'scripts' / 'critical_review.py')
    cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
    seen = {}
    def fake_run(argv, cwd=None, **kw):
        seen['argv'], seen['cwd'] = argv, cwd
        return type('P', (), {'returncode': 0, 'stdout': 'review text', 'stderr': ''})()
    monkeypatch.setattr(cr.subprocess, 'run', fake_run)
    monkeypatch.setattr(cr.Path, 'read_text', lambda self, **kw: 'PROMPT')
    out = cr.run_critical_review('manuscript', ['agy:gemini-x', 'opencode:openai/gpt-x'], 'manuscript', None)
    assert out == {'agy:gemini-x': 'review text', 'opencode:openai/gpt-x': 'review text'}
    assert 'review-' in str(seen['cwd'])


def test_config_saves_default_docx_style(capsys):
    assert lifecycle.config(['set', 'docx.font', 'Arial']) == 0
    assert lifecycle.config(['set', 'docx.line-spacing', '1.5']) == 0
    assert lifecycle.config(['set', 'docx.line-numbers', 'page']) == 0
    assert lifecycle.config(['set', 'docx.size', 'big']) == 2
    assert lifecycle.config(['set', 'docx.page-numbers', 'left']) == 2
    assert lifecycle.load('config.json', {})['docx'] == {'font': 'Arial', 'line_spacing': 1.5, 'line_numbers': 'page'}


def test_setup_walks_every_setting_then_offers_obsidian(monkeypatch, capsys):
    from manuwright import obsidian, models
    offered = []
    monkeypatch.setattr(obsidian, 'offer_connect', lambda: offered.append(1))
    monkeypatch.setattr(models, 'openrouter_prices', lambda: {'z-ai/glm-5.3': (3e-7, 6e-6), 'deepseek/a': (1e-7, 1e-7)})
    monkeypatch.setattr(models, 'opencode_models', lambda: {'opencode-go/kimi-k3', 'opencode-go/glm-5.3'})
    monkeypatch.delenv('OPENROUTER_API_KEY', raising=False)
    monkeypatch.setattr(models, 'key_works', lambda key: key == 'sk-or-good')
    answers = iter(['claude-opus-5-5', 'codex',
                    'deepseek/b', 'n', 'deepseek/a',  # OpenRouter: unknown id refused, then a known one
                    'sk-or-good',                     # OpenRouter key, hidden input
                    '9', 'opencode-go/kimi-k3,opencode-go/glm-5.3',  # opencode: out-of-range number, then own ids
                    'maybe', 'on'])          # auto-update, with 1 retry
    assert lifecycle.setup([], ask=lambda _: next(answers)) == 0
    data = lifecycle.load('config.json', {})
    assert data['main_model'] == 'claude-opus-5-5'
    assert data['review']['reviewers'] == ['codex', 'openrouter', 'opencode:opencode-go/kimi-k3', 'opencode:opencode-go/glm-5.3']
    assert data['review']['openrouter_models'] == ['deepseek/a']
    assert 'docx' not in data  # Word style is per paper (manuwright project)
    assert data['auto_update'] is True and offered == [1]
    secrets = lifecycle.home() / 'secrets.json'
    assert json.loads(secrets.read_text())['openrouter_api_key'] == 'sk-or-good'
    assert 'sk-or-good' not in (lifecycle.home() / 'config.json').read_text()
    if os.name == 'posix':
        assert secrets.stat().st_mode & 0o777 == 0o600
    out = capsys.readouterr().out
    assert 'not valid' in out and 'did you mean "deepseek/a"' in out and '~$0.032/review' in out


def test_setup_main_model_is_a_numbered_choice_with_installed_agents(monkeypatch, capsys):
    from manuwright import obsidian, models
    monkeypatch.setattr(obsidian, 'offer_connect', lambda: None)
    monkeypatch.setattr(models, 'openrouter_prices', lambda: {})
    monkeypatch.setattr(models, 'opencode_models', set)
    monkeypatch.setattr(models.shutil, 'which', lambda name: '/bin/codex' if name == 'codex' else None)
    monkeypatch.setattr(lifecycle.shutil, 'which', lambda name: '/bin/codex' if name == 'codex' else None)
    answers = iter(['claude', '99', '1', '', '0', '0', ''])  # agent name and bad number refused, then 1
    assert lifecycle.setup([], ask=lambda _: next(answers)) == 0
    out = capsys.readouterr().out
    first = next(line for line in out.splitlines() if line.startswith('   1. '))
    assert 'openai/' in first and 'Codex installed' in first  # installed agent's models listed first
    assert 'Claude Code not installed' in out and 'is an agent, not a model' in out
    assert 'claude' in out and 'not installed' in out  # reviewer list shows install status
    assert lifecycle.load('config.json', {})['main_model'] == models.writer_options()[0][0]


def test_setup_picks_a_recommended_set(monkeypatch):
    from manuwright import obsidian, models
    monkeypatch.setattr(obsidian, 'offer_connect', lambda: None)
    monkeypatch.setattr(models, 'openrouter_prices', lambda: {})
    monkeypatch.setattr(models, 'opencode_models', set)
    monkeypatch.delenv('OPENROUTER_API_KEY', raising=False)
    monkeypatch.setattr(models, 'key_works', lambda key: False)
    answers = iter(['', '-', '1', 'sk-bad', '0', ''])  # a rejected key is not saved
    assert lifecycle.setup([], ask=lambda _: next(answers)) == 0
    review = lifecycle.load('config.json', {})['review']
    assert review['reviewers'] == ['openrouter']
    assert review['openrouter_models'] == models.OPENROUTER_SETS['balanced'][1]
    assert not (lifecycle.home() / 'secrets.json').exists()


def test_setup_interrupt_saves_nothing(capsys):
    def stop(_):
        raise KeyboardInterrupt
    assert lifecycle.setup([], ask=stop) == 1
    assert lifecycle.load('config.json', {}) == {} and 'settings not saved' in capsys.readouterr().out


def test_checklist_menu_keys(capsys):
    from manuwright import models
    options = [('a/x', 'a/x'), ('b/y', 'b/y'), ('c/z', 'c/z')]
    keys = iter([models.DOWN, models.SPACE, models.DOWN, models.SPACE, models.ENTER])
    assert models.pick('t', options, {'a/x'}, keys=keys) == ['a/x', 'b/y', 'c/z']
    assert models.pick('t', options, set(), {'1': ('set', ['c/z'])}, keys=iter(['1', models.ENTER])) == ['c/z']
    assert models.pick('t', options, {'a/x'}, keys=iter(['n', models.ENTER])) == []
    assert models.pick('t', options, {'a/x'}, keys=iter([models.ESC])) is None
    assert models.pick('t', options, {'a/x'}, single=True, keys=iter([models.UP, models.ENTER])) == ['c/z']
    assert '[x] a/x' in capsys.readouterr().out


def test_writer_and_reviewer_names_match_across_spellings():
    import importlib.util
    spec = importlib.util.spec_from_file_location('cr', ENGINE / 'scripts' / 'critical_review.py')
    cr = importlib.util.module_from_spec(spec); spec.loader.exec_module(cr)
    flagged = cr.not_independent([('openrouter', 'anthropic/claude-opus-5.5'), ('openrouter', 'z-ai/glm-5.3')], 'claude-opus-5-5')
    assert flagged == ['anthropic/claude-opus-5.5']


def test_target_sets_journal_and_word_style_for_one_paper(tmp_path, monkeypatch, capsys):
    folder = tmp_path / 'paper1'
    assert lifecycle.init(ENGINE, [str(folder)]) == 0
    monkeypatch.chdir(folder / 'drafts')  # found from a subfolder too
    # numbered fallback: journal 3 (nejm), custom style: font 2 (Arial), size 3 (12), spacing 2 (1.5),
    # margins Enter (keep default), line numbers 2 (page), page numbers 3 (off)
    answers = iter(['3', '3', '2', '3', '2', '', '2', '3', ''])  # last: don't save to the library
    assert lifecycle.target(ENGINE, [], ask=lambda _: next(answers)) == 0
    config = json.loads((folder / 'project.json').read_text())
    assert config['journal'] == 'nejm'
    assert config['docx'] == {'font': 'Arial', 'size': 12, 'line_spacing': 1.5, 'line_numbers': 'page',
                              'page_numbers': 'off'}
    assert 'stale' in capsys.readouterr().out
    assert lifecycle.load('config.json', {}).get('docx') is None  # global settings untouched
    answers = iter(['15', '2'])  # journal: None (last of 14 presets + 1); Word style: back to default
    assert lifecycle.target(ENGINE, [], ask=lambda _: next(answers)) == 0
    config = json.loads((folder / 'project.json').read_text())
    assert 'journal' not in config and 'docx' not in config


def test_target_needs_a_paper_folder(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert lifecycle.target(ENGINE, [], ask=lambda _: '') == 2
    assert 'no project.json' in capsys.readouterr().err


def test_project_is_an_alias_of_target():
    assert lifecycle.project is lifecycle.target


def test_masked_key_input_shows_stars_and_handles_backspace():
    import io
    from manuwright import models
    out = io.StringIO()
    typed = iter(list('sk-or-v1-abc') + ['\x7f'] + list('d') + ['\r'])
    assert models.masked_input('key: ', typed, out) == 'sk-or-v1-abd'
    shown = out.getvalue()
    assert 'sk-or' not in shown and shown.count('*') == 13 and '\b \b' in shown
    assert models.mask('sk-or-v1-0123456789abcdef') == 'sk-or-v1...cdef (25 characters)'


def test_refresh_rules_updates_only_agent_files(tmp_path, capsys):
    paper = tmp_path / 'paper'
    lifecycle.init(ENGINE, [str(paper)])
    (paper / 'CLAUDE.md').write_text('old rules', encoding='utf-8')
    (paper / 'drafts' / 'draft_plan.md').write_text('my plan', encoding='utf-8')
    assert lifecycle.init(ENGINE, [str(paper)]) == 1 and '--refresh-rules' in capsys.readouterr().err
    assert lifecycle.init(ENGINE, [str(paper), '--refresh-rules']) == 0
    assert (paper / 'CLAUDE.md').read_text(encoding='utf-8') == (ENGINE / 'docs' / 'agent_bootstrap.md').read_text(encoding='utf-8')
    assert (paper / 'CLAUDE.md.bak').read_text(encoding='utf-8') == 'old rules'
    assert (paper / 'drafts' / 'draft_plan.md').read_text(encoding='utf-8') == 'my plan'
    assert 'manuwright approve' in (paper / 'AGENTS.md').read_text(encoding='utf-8')

    (paper / 'GEMINI.md').write_text('# x\n@WORKFLOW.md\n', encoding='utf-8')
    lifecycle.init(ENGINE, [str(paper), '--refresh-rules'])
    assert '@WORKFLOW.md' in (paper / 'GEMINI.md').read_text(encoding='utf-8')

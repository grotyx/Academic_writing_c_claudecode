"""manuwright init / update / auto-update safety rules (distribution phase 3)."""
import json
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

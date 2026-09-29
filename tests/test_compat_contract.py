"""Track A compatibility contract (docs/distribution_plan.md, phase 1).

Freezes today's no-install behavior before packaging work starts:
- every script runs from a raw checkout, from an unrelated cwd, without PYTHONPATH;
- legacy checker defaults resolve against the engine checkout, not the cwd;
- hooks resolve the edited file from the event cwd (spaces/Unicode paths);
- manifests outside the repo and several manifests in one process stay independent.
If a later phase changes one of these on purpose, change the test in the same PR.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from harness.project import verify
from tests.test_enforce_gates import DRAFT_CONTENT
from tests.test_harness import project, put  # noqa: F401  (fixture reuse)

ENGINE = Path(__file__).resolve().parents[1]
CLIS = sorted(p.name for p in (ENGINE / 'scripts').glob('*.py')
              if p.name not in {'plan_validation.py'} and 'argparse' in p.read_text(encoding='utf-8'))


@pytest.fixture
def elsewhere(tmp_path):
    """An unrelated working directory with a space and non-ASCII characters."""
    folder = tmp_path / 'paper folder' / '논문'
    folder.mkdir(parents=True)
    return folder


def run(args, cwd, stdin=None):
    env = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PAPERFLOW_PROJECT'}}
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd, input=stdin,
                          capture_output=True, text=True, encoding='utf-8', env=env, timeout=60)


@pytest.mark.parametrize('script', CLIS)
def test_scripts_run_without_install_from_any_cwd(script, elsewhere):
    result = run([ENGINE / 'scripts' / script, '--help'], elsewhere)
    assert result.returncode == 0, result.stderr


def test_citation_default_registry_is_engine_relative(elsewhere):
    put(elsewhere / 'knowledge/evidence.md', '# Local registry that legacy defaults must ignore\n')
    put(elsewhere / 'a.md', '# X\n\nA claim [EVID:nope_2020].\n')
    out = run([ENGINE / 'scripts/check_citations.py', 'a.md'], elsewhere).stdout
    assert f'evidence: {ENGINE / "knowledge" / "evidence.md"}' in out


def test_number_default_results_are_engine_relative(elsewhere):
    put(elsewhere / 'results/local.csv', 'x\n54\n')
    put(elsewhere / 'r.md', '# Results\n\nMean was 54.\n')
    out = run([ENGINE / 'scripts/check_numbers.py', 'r.md'], elsewhere).stdout
    assert f'results: {ENGINE / "results"}' in out


def hook(event_cwd, file_path, process_cwd):
    event = {'tool_name': 'Write', 'cwd': str(event_cwd), 'tool_input': {'file_path': file_path}}
    return subprocess.run(['sh', str(ENGINE / 'scripts/hooks/run.sh'), str(ENGINE / 'scripts/hooks/enforce_gates.py')],
                          cwd=process_cwd, input=json.dumps(event), capture_output=True, text=True,
                          encoding='utf-8', timeout=60)


@pytest.mark.skipif(shutil.which('sh') is None, reason='hook launcher needs POSIX sh')
def test_hook_resolves_target_from_event_cwd(elsewhere, tmp_path):
    blocked = hook(elsewhere, 'drafts/04_methods.md', tmp_path)
    assert blocked.returncode == 2 and 'BLOCKED' in blocked.stderr
    put(elsewhere / 'drafts/draft_plan.md', DRAFT_CONTENT + '\n- [x] 사용자 승인 완료\n')
    allowed = hook(elsewhere, 'drafts/04_methods.md', tmp_path)
    assert allowed.returncode == 0 and not allowed.stderr, allowed.stderr


def test_manifests_in_one_process_stay_independent(project, tmp_path_factory):
    other = tmp_path_factory.mktemp('second') / 'second paper'
    shutil.copytree(project.parent, other)
    put(other / 'drafts/03_introduction.md', '# Introduction\n\nA claim [EVID:ghost_2020].\n')
    assert verify(project)['status'] == 'PASS'
    assert verify(other / 'project.json')['status'] == 'FAIL'
    assert verify(project)['status'] == 'PASS'

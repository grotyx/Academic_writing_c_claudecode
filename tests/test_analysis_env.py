"""Per-paper analysis environment: uv-managed Python only, lock file written, scripts run from the paper."""
import json
import subprocess
from pathlib import Path

import pytest

from manuwright import analysis_env, lifecycle

ENGINE = Path(__file__).resolve().parents[1]


def test_build_uses_managed_python_and_writes_lock(tmp_path, monkeypatch):
    monkeypatch.setenv('MANUWRIGHT_HOME', str(tmp_path / 'home'))
    monkeypatch.setattr(analysis_env.shutil, 'which', lambda exe: '/usr/bin/uv')
    paper = tmp_path / 'paper'
    lifecycle.init(ENGINE, [str(paper)])
    assert 'scipy' in (paper / 'data' / 'requirements.txt').read_text()
    calls = []

    def fake_run(argv, **kw):
        calls.append((argv, kw.get('env', {}).get('UV_PYTHON_PREFERENCE')))
        if argv[0] == 'uv' and argv[1] == 'venv':
            python = analysis_env.python_of(Path(argv[-1]))
            python.parent.mkdir(parents=True)
            python.write_text('')
        out = '3.12.13 3.0 1.18 0.15' if argv[1] == '-c' else 'scipy==1.18.1\n'
        return subprocess.CompletedProcess(argv, 0, out, '')
    analysis_env.build(paper, 'paper', run=fake_run)
    assert calls[0][0][:4] == ['uv', 'venv', '--python', '3.12'] and calls[0][1] == 'only-managed'
    assert 'Python 3.12.13' in (paper / 'data' / 'environment.lock.txt').read_text()
    assert str(analysis_env.env_dir('paper')).startswith(str(tmp_path / 'home'))  # outside the paper folder


def test_env_needs_uv_and_a_paper(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert analysis_env.main([]) == 1 and 'paper folder' in capsys.readouterr().err
    monkeypatch.setattr(analysis_env.shutil, 'which', lambda exe: None)
    with pytest.raises(ValueError, match='uv is needed'):
        analysis_env.build(tmp_path, 'x')

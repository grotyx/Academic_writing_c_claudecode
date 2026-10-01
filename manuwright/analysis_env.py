"""Per-paper analysis environment: the paper's own Python and statistics packages, built with uv.

The system, Homebrew or pyenv Python can have broken or missing scipy/statsmodels; analysis then
depends on whichever machine runs it. `manuwright env` builds a uv-managed Python (never the
system one) with the packages in the paper's data/requirements.txt, outside the paper folder
(~/.manuwright/envs/<paper_id>, so cloud-synced folders stay small), and writes
data/environment.lock.txt with exact versions for the Methods section and reproducibility.
`manuwright run <script>` runs an analysis script with it from the paper folder.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PYTHON = '3.12'
DEFAULT_REQUIREMENTS = """# Analysis packages for this paper (manuwright env installs these; edit and rerun to change)
pandas
numpy
scipy
statsmodels
matplotlib
openpyxl
"""


def env_dir(paper_id):
    return Path(os.environ.get('MANUWRIGHT_HOME') or Path.home() / '.manuwright') / 'envs' / paper_id


def python_of(env):
    return env / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')


def paper(args):
    from manuwright.lifecycle import find_manifest
    manifest = find_manifest(args)
    if not manifest or not manifest.is_file():
        raise ValueError('run inside a paper folder (manuwright init creates one) or pass --project PATH')
    config = json.loads(manifest.read_text(encoding='utf-8'))
    return manifest.parent, config.get('paper_id') or manifest.parent.name


def build(root, paper_id, run=subprocess.run):
    if not shutil.which('uv'):
        raise ValueError('uv is needed for the analysis environment: https://docs.astral.sh/uv/ '
                         '(macOS: brew install uv, or curl -LsSf https://astral.sh/uv/install.sh | sh)')
    requirements = root / 'data' / 'requirements.txt'
    if not requirements.exists():
        requirements.parent.mkdir(parents=True, exist_ok=True)
        requirements.write_text(DEFAULT_REQUIREMENTS, encoding='utf-8')
        print(f'created {requirements} (edit it to add packages)')
    env = env_dir(paper_id)
    managed = {**os.environ, 'UV_PYTHON_PREFERENCE': 'only-managed'}  # never a broken system/pyenv Python
    if not python_of(env).exists():
        print(f'Creating the analysis environment for {paper_id} (Python {PYTHON}, uv-managed) ...')
        run(['uv', 'venv', '--python', PYTHON, str(env)], check=True, env=managed)
    print('Installing packages from data/requirements.txt ...')
    run(['uv', 'pip', 'install', '--python', str(python_of(env)), '-r', str(requirements)], check=True, env=managed)
    check = run([str(python_of(env)), '-c',
                 'import sys, pandas, scipy, statsmodels; print(sys.version.split()[0], pandas.__version__, '
                 'scipy.__version__, statsmodels.__version__)'], check=True, capture_output=True, text=True)
    frozen = run(['uv', 'pip', 'freeze', '--python', str(python_of(env))], check=True, capture_output=True, text=True)
    python_version, pandas_v, scipy_v, statsmodels_v = check.stdout.split()
    (root / 'data' / 'environment.lock.txt').write_text(
        f'# Analysis environment for {paper_id}: Python {python_version}\n' + frozen.stdout, encoding='utf-8')
    print(f'Ready: Python {python_version}, pandas {pandas_v}, scipy {scipy_v}, statsmodels {statsmodels_v}.\n'
          f'Exact versions: data/environment.lock.txt. Run scripts with: manuwright run data/py/<script>.py')
    return env


def main(args):
    """manuwright env [--project PATH]: build or update this paper's analysis environment."""
    try:
        root, paper_id = paper(args)
        build(root, paper_id)
    except (ValueError, subprocess.CalledProcessError, OSError) as exc:
        print(f'manuwright env: {exc}', file=sys.stderr)
        return 1
    return 0


def run_script(args):
    """manuwright run <script.py> [args...]: run an analysis script with this paper's environment."""
    if not args:
        print('usage: manuwright run data/py/<script>.py [args...]', file=sys.stderr)
        return 2
    script = Path(args[0])
    if script.exists():
        args = [str(script.resolve()), *args[1:]]  # the script runs from the paper folder
    try:
        root, paper_id = paper([])
        python = python_of(env_dir(paper_id))
        if not python.exists():
            build(root, paper_id)
    except (ValueError, subprocess.CalledProcessError, OSError) as exc:
        print(f'manuwright run: {exc}', file=sys.stderr)
        return 1
    return subprocess.call([str(python), *args], cwd=root)

"""The help must list every command the CLI routes (a stale help line once shipped in a release)."""
import re
from pathlib import Path

from manuwright import cli, library

SOURCE = (Path(cli.__file__)).read_text(encoding='utf-8')
ALIASES = {'project', 'version', '--version'}  # kept working, not advertised


def routed_commands():
    names = set(re.findall(r"command == '([\w-]+)'", SOURCE))
    for group in re.findall(r"command in \{([^}]*)\}", SOURCE):
        names |= set(re.findall(r"'([\w-]+)'", group))
    return names - ALIASES


def test_every_routed_command_is_in_the_help():
    missing = sorted(name for name in routed_commands() if not re.search(rf'(^|\s){re.escape(name)}(\s|$|\[)', cli.USAGE, re.M))
    assert not missing, f'add to cli.USAGE: {missing}'
    assert all(tool in cli.USAGE for tool in cli.TOOLS)


def test_library_help_names_its_subcommands():
    for sub in ('docx', 'profile', 'writing', '--journal', '--team', '--personal', '--replace'):
        assert sub in library.USAGE
    assert 'library [docx|profile|writing' in cli.USAGE


def test_verify_finds_project_json_from_the_paper_folder(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert cli.main(['verify']) == 2 and 'no project.json' in capsys.readouterr().err
    (tmp_path / 'project.json').write_text('{}')
    (tmp_path / 'drafts').mkdir()
    monkeypatch.chdir(tmp_path / 'drafts')
    seen = []
    monkeypatch.setattr(cli.subprocess, 'call', lambda argv, **kw: seen.append(argv) or 0)
    assert cli.main(['verify', '--profile', 'draft']) == 0
    assert seen[0][-4:] == ['--project', str(tmp_path / 'project.json'), '--profile', 'draft']

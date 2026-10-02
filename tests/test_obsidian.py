"""Obsidian plugin link: vault discovery, MCP registration steps, evidence import."""
import json
from pathlib import Path

import pytest

from manuwright import obsidian

NOTE = """---
citekey: miller2020minimally
type: article-journal
title: 'Minimally invasive versus open TLIF: a meta-analysis'
author:
  - family: Miller
    given: L E
  - family: Pracyk
    given: J
issued:
  date-parts:
    - - 2020
container-title: World Neurosurg
volume: "133"
page: 358-365
DOI: 10.1016/j.wneu.2019.08.162
PMID: "31476471"
design: meta-analysis
---

# Minimally invasive versus open TLIF

## Summary

**Background / Objective**
Compare MI-TLIF with open TLIF.

**Methods**
Seven randomized trials, 496 patients.

**Results**
Less blood loss and shorter stay with MI-TLIF.

**Conclusions**
Perioperative benefit, small ODI difference.
"""


@pytest.fixture
def vault(tmp_path, monkeypatch):
    root = tmp_path / 'My Vault'
    plugin = root / '.obsidian' / 'plugins' / obsidian.PLUGIN_ID
    plugin.mkdir(parents=True)
    (plugin / 'mcp-bridge.cjs').write_text('// bridge', encoding='utf-8')
    (plugin / 'data.json').write_text('{"referencesFolder": "Refs"}', encoding='utf-8')
    (root / 'Refs').mkdir()
    (root / 'Refs' / '2020-Miller.md').write_text(NOTE, encoding='utf-8')
    config = tmp_path / 'obsidian.json'
    config.write_text(json.dumps({'vaults': {'a': {'path': str(root)}, 'b': {'path': str(tmp_path / 'plain')}}}))
    monkeypatch.setattr(obsidian, 'obsidian_config', lambda: config)
    monkeypatch.setenv('XDG_CONFIG_HOME', str(tmp_path / 'xdg'))
    return root


def test_finds_only_vaults_with_the_plugin(vault):
    assert obsidian.find_vaults() == [vault]


def test_native_commands_and_json_entries(vault, tmp_path):
    cmd = obsidian.steps('codex', vault)[0]
    assert cmd[:4] == ['codex', 'mcp', 'add', 'rag-obsidian'] and cmd[-2:] == ['--vault', str(vault)]
    kind, path, keys, value = obsidian.steps('opencode', vault)[0]
    path.parent.mkdir(parents=True)
    path.write_text('{"plugin": ["x"]}', encoding='utf-8')
    obsidian.write_json_entry(path, keys, value)
    data = json.loads(path.read_text())
    assert data['plugin'] == ['x'] and data['mcp']['rag-obsidian']['command'][0] == 'node'
    assert path.with_suffix('.json.manuwright.bak').read_text() == '{"plugin": ["x"]}'
    bad = tmp_path / 'bad.json'
    bad.write_text('{not json')
    with pytest.raises(ValueError):
        obsidian.write_json_entry(bad, ('mcp', 'x'), {})
    assert bad.read_text() == '{not json'


def test_import_evidence_from_note(vault, tmp_path, capsys):
    evidence = tmp_path / 'knowledge' / 'evidence.md'
    code = obsidian.import_evidence(['miller2020minimally', 'nosuchkey', '--vault', str(vault), '--evidence', str(evidence)])
    text = evidence.read_text(encoding='utf-8')
    assert code == 1 and 'not found: nosuchkey' in capsys.readouterr().out
    assert '**Evidence ID:** miller2020minimally' in text and '**Source Status:** abstract-only' in text
    assert 'Miller LE, Pracyk J. Minimally invasive versus open TLIF: a meta-analysis. World Neurosurg. 2020;133:358-365.' in text
    assert 'Less blood loss and shorter stay' in text and '**PMID:** 31476471' in text
    obsidian.import_evidence(['miller2020minimally', '--vault', str(vault), '--evidence', str(evidence)])
    assert evidence.read_text(encoding='utf-8').count('Evidence ID:** miller2020minimally') == 1


def test_imported_entry_passes_citation_check(vault, tmp_path):
    import importlib.util
    engine = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('cc', engine / 'scripts' / 'check_citations.py')
    cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
    evidence = tmp_path / 'evidence.md'
    obsidian.import_evidence(['miller2020minimally', '--vault', str(vault), '--evidence', str(evidence)])
    draft = tmp_path / 'intro.md'
    draft.write_text('# Introduction\n\nPooled trials favoured MI-TLIF [EVID:miller2020minimally].\n', encoding='utf-8')
    assert cc.check_citations([draft], evidence_path=evidence).passed


def test_no_plugin_only_suggests(tmp_path, monkeypatch, capsys):
    config = tmp_path / 'obsidian.json'
    config.write_text('{"vaults": {}}')
    monkeypatch.setattr(obsidian, 'obsidian_config', lambda: config)
    obsidian.offer_connect()
    out = capsys.readouterr().out
    assert 'Optional (recommended)' in out and 'Not required' in out


def test_install_into_vault_asks_and_never_overwrites(tmp_path, monkeypatch, capsys):
    vault = tmp_path / 'New Vault'
    (vault / '.obsidian').mkdir(parents=True)
    (vault / '.obsidian' / 'community-plugins.json').write_text('["dataview"]')
    monkeypatch.setattr(obsidian, 'obsidian_app_installed', lambda: True)
    def fake_download(target):
        target.mkdir(parents=True, exist_ok=True)
        for name in obsidian.ASSETS:
            (target / name).write_text('{"version": "0.7.9"}' if name == 'manifest.json' else 'x')
        return '0.7.9'
    monkeypatch.setattr(obsidian, 'download_release', fake_download)
    assert obsidian.install(['--vault', str(vault)]) == 0  # no tty, no --yes: nothing changes
    assert not (vault / '.obsidian' / 'plugins').exists()
    assert obsidian.install(['--vault', str(vault), '--yes', '--enable-mcp']) == 0
    plugin = vault / '.obsidian' / 'plugins' / obsidian.PLUGIN_ID
    assert json.loads((vault / '.obsidian' / 'community-plugins.json').read_text()) == ['dataview', obsidian.PLUGIN_ID]
    assert json.loads((plugin / 'data.json').read_text()) == {'mcpEnabled': True}
    (plugin / 'main.js').write_text('user copy')
    assert obsidian.install(['--vault', str(vault), '--yes']) == 0
    assert (plugin / 'main.js').read_text() == 'user copy'
    assert 'already installed' in capsys.readouterr().out


def test_agent_probes_never_touch_the_terminal(monkeypatch):
    seen = {}
    monkeypatch.setattr(obsidian.shutil, 'which', lambda exe: '/bin/' + exe)
    def fake_run(argv, **kw):
        seen.update(kw)
        class Done:
            returncode, stdout = 0, ''
        return Done()
    monkeypatch.setattr(obsidian.subprocess, 'run', fake_run)
    assert obsidian.connected('codex') is True
    assert seen['stdin'] is obsidian.subprocess.DEVNULL and seen['start_new_session'] is True
    # agent CLIs print UTF-8; the Windows code page (cp949 on Korean Windows) crashed the reader thread
    assert seen['encoding'] == 'utf-8' and seen['errors'] == 'replace'


def test_ask_survives_closed_input(monkeypatch):
    monkeypatch.setattr(obsidian.sys.stdin, 'isatty', lambda: True, raising=False)
    monkeypatch.setattr(obsidian, 'restore_terminal', lambda: None)
    def eof(_):
        raise EOFError
    monkeypatch.setattr('builtins.input', eof)
    assert obsidian.ask('Connect?', []) is False

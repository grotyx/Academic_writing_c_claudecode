"""Shared test setup."""
import pytest


@pytest.fixture(autouse=True)
def _private_manuwright_home(tmp_path_factory, monkeypatch):
    # Never let a test register papers or write settings in the real ~/.manuwright.
    monkeypatch.setenv('MANUWRIGHT_HOME', str(tmp_path_factory.mktemp('manuwright_home')))

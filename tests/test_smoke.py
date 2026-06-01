from skillkit.config import registry_root
from pathlib import Path


def test_registry_root_default(monkeypatch):
    monkeypatch.delenv("SKILLKIT_REGISTRY", raising=False)
    assert registry_root() == Path("~/ai/skillkit").expanduser()


def test_registry_root_env(monkeypatch, tmp_path):
    monkeypatch.setenv("SKILLKIT_REGISTRY", str(tmp_path))
    assert registry_root() == tmp_path

"""Tests for the skillkit CLI entry point."""
from pathlib import Path
from skillkit.cli import main


def _registry(tmp_path):
    g = tmp_path / "g"; (g / "qa").mkdir(parents=True)
    (g / "qa" / "SKILL.md").write_text("---\nname: qa\ndescription: QA\n---\n")
    (tmp_path / "sources.toml").write_text(f'[sources]\ngstack = "{g}"\n')
    (tmp_path / "packs").mkdir()
    return tmp_path


def test_add_then_sync(tmp_path, monkeypatch, capsys):
    reg = _registry(tmp_path); proj = tmp_path / "proj"; proj.mkdir()
    monkeypatch.setenv("SKILLKIT_REGISTRY", str(reg))
    monkeypatch.chdir(proj)
    assert main(["add", "gstack:qa"]) == 0
    assert (proj / ".claude/skills/qa/SKILL.md").exists()


def test_list_runs(tmp_path, monkeypatch):
    reg = _registry(tmp_path)
    monkeypatch.setenv("SKILLKIT_REGISTRY", str(reg))
    monkeypatch.chdir(tmp_path)
    assert main(["list"]) == 0


def test_add_and_rm_pack_routes_to_packs(tmp_path, monkeypatch):
    reg = _registry(tmp_path); proj = tmp_path / "proj"; proj.mkdir()
    monkeypatch.setenv("SKILLKIT_REGISTRY", str(reg))
    monkeypatch.chdir(proj)
    from skillkit.manifest import read_manifest
    assert main(["add", "pack:code-repo"]) == 0
    assert read_manifest(proj).packs == ["code-repo"]
    assert read_manifest(proj).skills == []
    assert main(["rm", "pack:code-repo"]) == 0
    assert read_manifest(proj).packs == []

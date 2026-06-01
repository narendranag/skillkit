from pathlib import Path
from skillkit.manifest import Manifest, read_manifest, write_manifest, resolve
from skillkit.catalog import Pack


def test_read_missing_manifest_is_empty(tmp_path):
    m = read_manifest(tmp_path)
    assert m.skills == [] and m.packs == [] and m.vendor is False


def test_write_then_read_roundtrip(tmp_path):
    write_manifest(tmp_path, Manifest(skills=["gstack:qa"], packs=["code-repo"], vendor=True))
    m = read_manifest(tmp_path)
    assert m.skills == ["gstack:qa"]
    assert m.packs == ["code-repo"]
    assert m.vendor is True


def test_resolve_flattens_packs_and_dedups():
    packs = {"code-repo": Pack("code-repo", "", ("gstack:qa", "mine:spine"))}
    m = Manifest(skills=["gstack:qa", "gstack:diagnose"], packs=["code-repo"], vendor=False)
    assert resolve(m, packs) == ["gstack:qa", "gstack:diagnose", "mine:spine"]

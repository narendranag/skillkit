from pathlib import Path
from skillkit.catalog import parse_frontmatter

def _write_skill(d: Path, name: str, desc: str):
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {desc}\n---\nbody\n")

def test_parse_frontmatter(tmp_path):
    _write_skill(tmp_path / "qa", "qa", "QA a web app")
    fm = parse_frontmatter(tmp_path / "qa" / "SKILL.md")
    assert fm["name"] == "qa"
    assert fm["description"] == "QA a web app"

def test_parse_frontmatter_missing(tmp_path):
    (tmp_path / "SKILL.md").write_text("no frontmatter here\n")
    assert parse_frontmatter(tmp_path / "SKILL.md") == {}

from skillkit.catalog import load_sources, scan_source, build_catalog

def test_load_sources(tmp_path):
    (tmp_path / "sources.toml").write_text(
        '[sources]\nmine = "~/ai/skillkit/skills"\ngstack = "%s"\n' % (tmp_path / "g")
    )
    srcs = load_sources(tmp_path)
    assert srcs["mine"] == Path("~/ai/skillkit/skills").expanduser()
    assert srcs["gstack"] == tmp_path / "g"

def test_scan_source(tmp_path):
    root = tmp_path / "g"
    _write_skill(root / "qa", "qa", "QA things")
    _write_skill(root / "ship", "ship", "Ship things")
    (root / "not-a-skill").mkdir()  # no SKILL.md -> ignored
    entries = scan_source("gstack", root)
    names = sorted(e.name for e in entries)
    assert names == ["qa", "ship"]
    assert all(e.source == "gstack" for e in entries)

def test_build_catalog_unions_sources(tmp_path):
    g = tmp_path / "g"; m = tmp_path / "m"
    _write_skill(g / "qa", "qa", "QA")
    _write_skill(m / "spine", "spine", "mine")
    (tmp_path / "sources.toml").write_text(
        f'[sources]\nmine = "{m}"\ngstack = "{g}"\n'
    )
    cat = build_catalog(tmp_path)
    refs = sorted(e.ref for e in cat)
    assert refs == ["gstack:qa", "mine:spine"]

from skillkit.catalog import load_packs

def test_load_packs(tmp_path):
    packs_dir = tmp_path / "packs"; packs_dir.mkdir()
    (packs_dir / "code-repo.toml").write_text(
        '[pack]\nname = "code-repo"\ndescription = "coding set"\n'
        'skills = ["gstack:qa", "mine:spine"]\n'
    )
    packs = load_packs(tmp_path)
    assert packs["code-repo"].description == "coding set"
    assert packs["code-repo"].skills == ("gstack:qa", "mine:spine")

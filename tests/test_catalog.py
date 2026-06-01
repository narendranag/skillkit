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

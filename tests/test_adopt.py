from pathlib import Path
from skillkit.adopt import find_scatter, to_trash

def test_find_scatter_only_twinned(tmp_path):
    skills = tmp_path / "skills"
    gstack = skills / "gstack"
    (gstack / "qa").mkdir(parents=True)
    (gstack / "ship").mkdir()
    (skills / "qa").mkdir()        # twin -> scatter
    (skills / "ship").mkdir()      # twin -> scatter
    (skills / "standalone").mkdir()  # no twin -> keep
    (skills / "link").symlink_to(tmp_path)  # symlink -> keep
    found = sorted(p.name for p in find_scatter(skills))
    assert found == ["qa", "ship"]

def test_to_trash_moves_dir(tmp_path):
    src = tmp_path / "victim"; src.mkdir(); (src / "f").write_text("x")
    trash = tmp_path / "trash"; trash.mkdir()
    to_trash(src, trash)
    assert not src.exists()
    assert (trash / "victim" / "f").exists()

def test_to_trash_timestamp_on_collision(tmp_path):
    src = tmp_path / "victim"; src.mkdir()
    trash = tmp_path / "trash"; (trash / "victim").mkdir(parents=True)
    to_trash(src, trash)
    assert not src.exists()
    moved = [p for p in trash.iterdir() if p.name.startswith("victim")]
    assert len(moved) == 2  # original + timestamped

from skillkit.adopt import adopt_gstack, register_source

def test_register_source_writes_sources_toml(tmp_path):
    reg = tmp_path / "reg"; reg.mkdir()
    register_source(reg, "gstack", Path("~/.claude/skills/gstack"))
    import tomllib
    data = tomllib.loads((reg / "sources.toml").read_text())
    assert data["sources"]["gstack"] == "~/.claude/skills/gstack"

def test_adopt_gstack_dry_run_lists_without_moving(tmp_path):
    skills = tmp_path / "skills"; (skills / "gstack" / "qa").mkdir(parents=True)
    (skills / "qa").mkdir()
    reg = tmp_path / "reg"; reg.mkdir(); trash = tmp_path / "trash"; trash.mkdir()
    moved = adopt_gstack(reg, claude_skills=skills, trash_dir=trash, yes=False)
    assert moved == []                      # nothing moved without yes
    assert (skills / "qa").exists()         # still there

def test_adopt_gstack_yes_moves_and_registers(tmp_path):
    skills = tmp_path / "skills"; (skills / "gstack" / "qa").mkdir(parents=True)
    (skills / "qa").mkdir()
    reg = tmp_path / "reg"; reg.mkdir(); trash = tmp_path / "trash"; trash.mkdir()
    moved = adopt_gstack(reg, claude_skills=skills, trash_dir=trash, yes=True)
    assert [p.name for p in moved] == ["qa"]
    assert not (skills / "qa").exists()
    assert (trash / "qa").exists()
    assert (reg / "sources.toml").exists()

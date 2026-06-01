from pathlib import Path
from skillkit.adopt import find_scatter, to_trash, register_source

def test_find_scatter_only_twinned(tmp_path):
    skills = tmp_path / "skills"
    gstack = skills / "gstack"
    (gstack / "qa").mkdir(parents=True)
    (gstack / "qa" / "SKILL.md").write_text("---\nname: qa\n---\n")
    (gstack / "ship").mkdir()
    (gstack / "ship" / "SKILL.md").write_text("---\nname: ship\n---\n")
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

from skillkit.adopt import adopt_gstack

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
    (skills / "gstack" / "qa" / "SKILL.md").write_text("---\nname: qa\n---\n")
    (skills / "qa").mkdir()
    reg = tmp_path / "reg"; reg.mkdir(); trash = tmp_path / "trash"; trash.mkdir()
    moved = adopt_gstack(reg, claude_skills=skills, trash_dir=trash, yes=True)
    assert [p.name for p in moved] == ["qa"]
    assert not (skills / "qa").exists()
    assert (trash / "qa").exists()
    assert (reg / "sources.toml").exists()


# --- C1: guard against gstack being a file/non-dir ---

def test_find_scatter_gstack_is_file_returns_empty(tmp_path):
    skills = tmp_path / "skills"; skills.mkdir()
    (skills / "gstack").write_text("not a dir")  # gstack is a FILE
    (skills / "qa").mkdir()
    assert find_scatter(skills) == []   # must not raise


# --- I2: symlinked twin inside gstack is not treated as a twin ---

def test_find_scatter_ignores_symlinked_gstack_twin(tmp_path):
    skills = tmp_path / "skills"; gstack = skills / "gstack"; gstack.mkdir(parents=True)
    real = tmp_path / "real_qa"; real.mkdir()
    (gstack / "qa").symlink_to(real)   # twin under gstack is a SYMLINK
    (skills / "qa").mkdir()            # top-level qa
    assert find_scatter(skills) == []  # symlinked twin shouldn't flag it


# --- I1: name-collision IS trashed (known design limitation) ---

def test_find_scatter_name_collision_is_flagged_known_limitation(tmp_path):
    # Documents that find_scatter matches by NAME only: a hand-authored dir whose
    # name collides with a gstack skill WILL be flagged. The CLI must preview the
    # list before --yes so the user can abort.
    skills = tmp_path / "skills"; gstack = skills / "gstack"; gstack.mkdir(parents=True)
    (gstack / "qa").mkdir()
    (gstack / "qa" / "SKILL.md").write_text("---\nname: qa\n---\n")
    (skills / "qa").mkdir()
    (skills / "qa" / "MY_WORK.txt").write_text("hand authored")
    flagged = [p.name for p in find_scatter(skills)]
    assert "qa" in flagged   # name-match only; this is the documented behavior


# --- M2: register_source preserves existing entries ---

def test_register_source_preserves_existing(tmp_path):
    reg = tmp_path / "reg"; reg.mkdir()
    (reg / "sources.toml").write_text('[sources]\nmine = "~/ai/skillkit/skills"\n', encoding="utf-8")
    register_source(reg, "gstack", Path("~/.claude/skills/gstack"))
    import tomllib
    data = tomllib.loads((reg / "sources.toml").read_text(encoding="utf-8"))
    assert data["sources"]["mine"] == "~/ai/skillkit/skills"   # preserved
    assert data["sources"]["gstack"] == "~/.claude/skills/gstack"


# --- M3: to_trash second collision yields .2 ---

def test_to_trash_second_collision(tmp_path):
    src = tmp_path / "victim"; src.mkdir()
    trash = tmp_path / "trash"; (trash / "victim").mkdir(parents=True); (trash / "victim.1").mkdir()
    dest = to_trash(src, trash)
    assert dest.name == "victim.2"
    assert not src.exists()


def test_find_scatter_ignores_gstack_support_dirs(tmp_path):
    # A gstack subdir WITHOUT a SKILL.md (e.g. "bin", "docs") is support tooling,
    # not a skill, so a same-named top-level dir must NOT be flagged for trashing.
    skills = tmp_path / "skills"; gstack = skills / "gstack"; gstack.mkdir(parents=True)
    (gstack / "qa").mkdir(); (gstack / "qa" / "SKILL.md").write_text("---\nname: qa\n---\n")
    (gstack / "bin").mkdir()  # support dir, no SKILL.md
    (skills / "qa").mkdir()   # real skill scatter -> should be flagged
    (skills / "bin").mkdir()  # user's own 'bin' -> must NOT be flagged
    flagged = sorted(p.name for p in find_scatter(skills))
    assert flagged == ["qa"]

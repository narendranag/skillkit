from pathlib import Path
from skillkit.sync import sync, vendor, MANAGED_MARKER


def _write_skill(d: Path, name: str, desc: str = "d"):
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(f"---\nname: {name}\ndescription: {desc}\n---\n")


def _registry(tmp_path: Path):
    g = tmp_path / "g"
    _write_skill(g / "qa", "qa"); _write_skill(g / "ship", "ship")
    (tmp_path / "sources.toml").write_text(f'[sources]\ngstack = "{g}"\n')
    (tmp_path / "packs").mkdir()
    return tmp_path


def test_sync_copies_selected_skill(tmp_path):
    reg = _registry(tmp_path); proj = tmp_path / "proj"
    (proj / ".claude").mkdir(parents=True)
    (proj / ".claude/skills.toml").write_text('skills = ["gstack:qa"]\npacks = []\nvendor = false\n')
    sync(proj, reg)
    assert (proj / ".claude/skills/qa/SKILL.md").exists()
    assert (proj / ".claude/skills/qa" / MANAGED_MARKER).exists()
    assert not (proj / ".claude/skills/ship").exists()


def test_sync_removes_delisted_managed_skill(tmp_path):
    reg = _registry(tmp_path); proj = tmp_path / "proj"
    (proj / ".claude").mkdir(parents=True)
    (proj / ".claude/skills.toml").write_text('skills = ["gstack:qa"]\npacks = []\nvendor = false\n')
    sync(proj, reg)
    (proj / ".claude/skills.toml").write_text('skills = []\npacks = []\nvendor = false\n')
    sync(proj, reg)
    assert not (proj / ".claude/skills/qa").exists()


def test_sync_never_deletes_hand_placed_skill(tmp_path):
    reg = _registry(tmp_path); proj = tmp_path / "proj"
    hand = proj / ".claude/skills/custom"; hand.mkdir(parents=True)
    (hand / "SKILL.md").write_text("---\nname: custom\n---\n")  # no marker
    (proj / ".claude/skills.toml").write_text('skills = []\npacks = []\nvendor = false\n')
    sync(proj, reg)
    assert (hand / "SKILL.md").exists()


def test_vendor_writes_gitignore_negation(tmp_path):
    reg = _registry(tmp_path); proj = tmp_path / "proj"
    (proj / ".claude").mkdir(parents=True)
    (proj / ".claude/skills.toml").write_text('skills = ["gstack:qa"]\npacks = []\nvendor = true\n')
    vendor(proj, reg)
    assert (proj / ".claude/skills/qa/SKILL.md").exists()
    gi = (proj / ".gitignore").read_text()
    assert "!.claude/skills/" in gi

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

"""One-time: de-scatter gstack's globally-installed skills."""
from __future__ import annotations
import shutil
import tomllib
from pathlib import Path

import tomli_w

def find_scatter(claude_skills: Path) -> list[Path]:
    """Top-level dirs in ~/.claude/skills that have a twin under gstack/.
    Excludes symlinks and the gstack dir itself."""
    gstack = claude_skills / "gstack"
    if not gstack.is_dir():
        return []
    twins = {d.name for d in gstack.iterdir() if d.is_dir() and not d.is_symlink()}
    out: list[Path] = []
    for child in claude_skills.iterdir():
        if child.name == "gstack" or child.is_symlink() or not child.is_dir():
            continue
        if child.name in twins:
            out.append(child)
    return out

def to_trash(path: Path, trash_dir: Path) -> Path:
    """Move path into trash_dir, counter-suffixing on name collision (.1, .2, ...).

    Deterministic: uses a sequential counter, not wall-clock time."""
    dest = trash_dir / path.name
    n = 1
    while dest.exists():
        dest = trash_dir / f"{path.name}.{n}"
        n += 1
    shutil.move(str(path), str(dest))
    return dest

def register_source(registry_root: Path, name: str, path: Path) -> None:
    f = registry_root / "sources.toml"
    data = tomllib.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    sources = data.setdefault("sources", {})
    sources[name] = str(path)  # store unexpanded (~) form
    f.write_text(tomli_w.dumps(data), encoding="utf-8")

def adopt_gstack(registry_root: Path, *, claude_skills: Path,
                 trash_dir: Path, yes: bool) -> list[Path]:
    scatter = find_scatter(claude_skills)
    register_source(registry_root, "gstack", Path("~/.claude/skills/gstack"))
    if not yes:
        return []
    return [to_trash(p, trash_dir) for p in scatter]

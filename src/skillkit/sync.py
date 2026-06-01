"""Materialize a project's resolved skills into .claude/skills/."""
from __future__ import annotations
import shutil
from pathlib import Path
from skillkit.catalog import build_catalog, load_packs
from skillkit.manifest import read_manifest, resolve

MANAGED_MARKER = ".skillkit-managed"

def _skills_dir(project: Path) -> Path:
    return project / ".claude" / "skills"

def _materialize(src: Path, dest: Path) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)
    (dest / MANAGED_MARKER).write_text("managed by skillkit\n")

def _managed_dirs(skills_dir: Path) -> set[str]:
    if not skills_dir.exists():
        return set()
    return {d.name for d in skills_dir.iterdir()
            if d.is_dir() and (d / MANAGED_MARKER).exists()}

def sync(project: Path, registry_root: Path) -> list[str]:
    catalog = {e.ref: e for e in build_catalog(registry_root)}
    packs = load_packs(registry_root)
    refs = resolve(read_manifest(project), packs)
    skills_dir = _skills_dir(project)
    skills_dir.mkdir(parents=True, exist_ok=True)

    wanted_names: set[str] = set()
    installed: list[str] = []
    for ref in refs:
        entry = catalog.get(ref)
        if entry is None:
            continue
        _materialize(entry.path, skills_dir / entry.name)
        wanted_names.add(entry.name)
        installed.append(entry.name)

    for name in _managed_dirs(skills_dir) - wanted_names:
        shutil.rmtree(skills_dir / name)
    return installed

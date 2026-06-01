"""Materialize a project's resolved skills into .claude/skills/."""
from __future__ import annotations
import shutil
import subprocess
from pathlib import Path
from skillkit.catalog import build_catalog, load_packs
from skillkit.manifest import read_manifest, resolve

MANAGED_MARKER = ".skillkit-managed"

def _skills_dir(project: Path) -> Path:
    return project / ".claude" / "skills"

def _materialize(src: Path, dest: Path) -> None:
    if dest.exists() and not (dest / MANAGED_MARKER).exists():
        raise RuntimeError(
            f"{dest} exists and is not skillkit-managed; "
            "remove or rename it before syncing."
        )
    tmp = dest.parent / (dest.name + ".__sk_tmp__")
    if tmp.exists():
        shutil.rmtree(tmp)
    shutil.copytree(src, tmp)
    (tmp / MANAGED_MARKER).write_text("managed by skillkit\n", encoding="utf-8")
    if dest.exists():
        shutil.rmtree(dest)
    tmp.rename(dest)

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


def vendor(project: Path, registry_root: Path) -> list[str]:
    installed = sync(project, registry_root)
    gi = project / ".gitignore"
    line = "!.claude/skills/"
    existing = gi.read_text(encoding="utf-8") if gi.exists() else ""
    if line not in existing:
        gi.write_text(
            existing + ("" if existing.endswith("\n") or not existing else "\n") + line + "\n",
            encoding="utf-8",
        )
    return installed


def update(project: Path, registry_root: Path) -> list[str]:
    if (registry_root / ".git").exists():
        subprocess.run(["git", "-C", str(registry_root), "pull", "--ff-only"], check=False)
    return sync(project, registry_root)

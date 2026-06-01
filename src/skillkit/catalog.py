"""Build the union skill catalog from declared source roots."""
from __future__ import annotations
import tomllib
from dataclasses import dataclass
from pathlib import Path
import yaml

@dataclass(frozen=True)
class SkillEntry:
    source: str
    name: str
    path: Path
    description: str

    @property
    def ref(self) -> str:
        return f"{self.source}:{self.name}"

@dataclass(frozen=True)
class Pack:
    name: str
    description: str
    skills: tuple[str, ...]

def parse_frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text()
    if not text.startswith("---"):
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}
    data = yaml.safe_load(parts[1]) or {}
    return data if isinstance(data, dict) else {}

def load_sources(registry_root: Path) -> dict[str, Path]:
    f = registry_root / "sources.toml"
    if not f.exists():
        return {}
    data = tomllib.loads(f.read_text())
    return {
        k: Path(v).expanduser()
        for k, v in data.get("sources", {}).items()
    }

def scan_source(source: str, root: Path) -> list[SkillEntry]:
    if not root.exists():
        return []
    out: list[SkillEntry] = []
    for child in sorted(root.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            fm = parse_frontmatter(skill_md)
            out.append(SkillEntry(
                source=source,
                name=fm.get("name", child.name),
                path=child,
                description=fm.get("description", ""),
            ))
    return out

def build_catalog(registry_root: Path) -> list[SkillEntry]:
    catalog: list[SkillEntry] = []
    for source, root in load_sources(registry_root).items():
        catalog.extend(scan_source(source, root))
    return catalog

def load_packs(registry_root: Path) -> dict[str, Pack]:
    packs_dir = registry_root / "packs"
    out: dict[str, Pack] = {}
    if not packs_dir.exists():
        return out
    for f in sorted(packs_dir.glob("*.toml")):
        data = tomllib.loads(f.read_text()).get("pack", {})
        name = data.get("name", f.stem)
        out[name] = Pack(
            name=name,
            description=data.get("description", ""),
            skills=tuple(data.get("skills", [])),
        )
    return out

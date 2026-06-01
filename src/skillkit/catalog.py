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

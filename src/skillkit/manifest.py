"""Read/write a project's .claude/skills.toml and resolve it to skill refs."""
from __future__ import annotations
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
import tomli_w
from skillkit.catalog import Pack

MANIFEST_REL = Path(".claude/skills.toml")


@dataclass
class Manifest:
    skills: list[str] = field(default_factory=list)
    packs: list[str] = field(default_factory=list)
    vendor: bool = False


def read_manifest(project: Path) -> Manifest:
    f = project / MANIFEST_REL
    if not f.exists():
        return Manifest()
    data = tomllib.loads(f.read_text(encoding="utf-8"))
    return Manifest(
        skills=list(data.get("skills", [])),
        packs=list(data.get("packs", [])),
        vendor=bool(data.get("vendor", False)),
    )


def write_manifest(project: Path, m: Manifest) -> None:
    f = project / MANIFEST_REL
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(
        tomli_w.dumps({"skills": m.skills, "packs": m.packs, "vendor": m.vendor}),
        encoding="utf-8",
    )


def resolve(m: Manifest, packs: dict[str, Pack]) -> list[str]:
    refs: list[str] = []
    seen: set[str] = set()

    def add(ref: str) -> None:
        if ref not in seen:
            seen.add(ref)
            refs.append(ref)

    for ref in m.skills:
        add(ref)
    for pack_name in m.packs:
        for ref in packs.get(pack_name, Pack(pack_name, "", ())).skills:
            add(ref)
    return refs

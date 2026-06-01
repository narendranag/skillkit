"""skillkit command-line entry point."""
from __future__ import annotations
import argparse
from pathlib import Path
from rich import print as rprint
from skillkit.config import registry_root
from skillkit.catalog import build_catalog, load_packs
from skillkit.manifest import read_manifest, write_manifest
from skillkit import sync as sync_mod
from skillkit import adopt as adopt_mod


def _add(ref: str, project: Path, reg: Path) -> int:
    m = read_manifest(project)
    if ref.startswith("pack:"):
        name = ref.split(":", 1)[1]
        if name not in m.packs:
            m.packs.append(name)
    elif ref not in m.skills:
        m.skills.append(ref)
    write_manifest(project, m)
    sync_mod.sync(project, reg)
    return 0


def _rm(ref: str, project: Path, reg: Path) -> int:
    m = read_manifest(project)
    if ref.startswith("pack:"):
        name = ref.split(":", 1)[1]
        m.packs = [p for p in m.packs if p != name]
    else:
        m.skills = [s for s in m.skills if s != ref]
    write_manifest(project, m)
    sync_mod.sync(project, reg)
    return 0


def _list(project: Path, reg: Path) -> int:
    installed = set(read_manifest(project).skills)
    for e in build_catalog(reg):
        mark = "*" if e.ref in installed else " "
        rprint(f"[{mark}] {e.ref}  [dim]{e.description}[/dim]")
    for name, pack in load_packs(reg).items():
        rprint(f"    pack:{name}  [dim]{', '.join(pack.skills)}[/dim]")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="skillkit")
    sub = p.add_subparsers(dest="cmd", required=True)
    for verb in ("add", "rm"):
        sp = sub.add_parser(verb); sp.add_argument("ref")
    sub.add_parser("sync"); sub.add_parser("update")
    sub.add_parser("vendor"); sub.add_parser("list")
    ad = sub.add_parser("adopt"); ad.add_argument("target", choices=["gstack"])
    ad.add_argument("--yes", action="store_true")

    sub.add_parser("pick")
    pk = sub.add_parser("pack")
    pk_sub = pk.add_subparsers(dest="pack_cmd", required=True)
    pc = pk_sub.add_parser("create"); pc.add_argument("name")
    pk_sub.add_parser("list")
    psh = pk_sub.add_parser("show"); psh.add_argument("name")

    args = p.parse_args(argv)
    reg = registry_root()
    project = Path.cwd()

    if args.cmd == "add":
        return _add(args.ref, project, reg)
    if args.cmd == "rm":
        return _rm(args.ref, project, reg)
    if args.cmd == "sync":
        sync_mod.sync(project, reg); return 0
    if args.cmd == "update":
        sync_mod.update(project, reg); return 0
    if args.cmd == "vendor":
        sync_mod.vendor(project, reg); return 0
    if args.cmd == "list":
        return _list(project, reg)
    if args.cmd == "pick":
        from skillkit.tui import PickApp
        chosen = PickApp(reg).run() or []
        m = read_manifest(project)
        for ref in chosen:
            if ref not in m.skills:
                m.skills.append(ref)
        write_manifest(project, m)
        sync_mod.sync(project, reg)
        rprint(f"Installed {len(chosen)} skills")
        return 0
    if args.cmd == "pack":
        if args.pack_cmd == "create":
            from skillkit.tui import PickApp
            import tomli_w
            chosen = PickApp(reg).run() or []
            (reg / "packs").mkdir(exist_ok=True)
            (reg / "packs" / f"{args.name}.toml").write_text(
                tomli_w.dumps({"pack": {"name": args.name, "description": "", "skills": chosen}}),
                encoding="utf-8",
            )
            rprint(f"Wrote pack {args.name} with {len(chosen)} skills")
            return 0
        if args.pack_cmd == "list":
            for name, pk in load_packs(reg).items():
                rprint(f"pack:{name}  [dim]{', '.join(pk.skills)}[/dim]")
            return 0
        if args.pack_cmd == "show":
            pk = load_packs(reg).get(args.name)
            rprint(pk if pk else f"no pack {args.name}")
            return 0
    if args.cmd == "adopt":
        claude_skills = Path("~/.claude/skills").expanduser()
        if not args.yes:
            scatter = adopt_mod.find_scatter(claude_skills)
            rprint(f"[bold]Would move {len(scatter)} scattered gstack dirs to Trash:[/bold]")
            for d in sorted(scatter, key=lambda p: p.name):
                rprint(f"  - {d.name}")
            rprint("[yellow]Review the list above. Re-run with --yes to proceed.[/yellow]")
            # still register the gstack source (safe, non-destructive)
            adopt_mod.adopt_gstack(reg, claude_skills=claude_skills,
                                   trash_dir=Path("~/.Trash").expanduser(), yes=False)
        else:
            moved = adopt_mod.adopt_gstack(reg, claude_skills=claude_skills,
                                           trash_dir=Path("~/.Trash").expanduser(), yes=True)
            rprint(f"[green]Moved {len(moved)} gstack dirs to Trash[/green] and registered the gstack source.")
        return 0
    return 1

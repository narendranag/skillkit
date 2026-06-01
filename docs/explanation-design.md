# Why skillkit works the way it does

This explains the design decisions behind skillkit: why it copies instead of
symlinks, why packs are live references, how it avoids destroying your work, and
what the gstack adoption actually does. For the factual surface, see the
[reference](reference.md). The full design record is in the
[spec](superpowers/specs/2026-06-02-skillkit-design.md).

## The problem

Claude Code loads skills from `~/.claude/skills/` (global, every session) and from
enabled plugins (also global). A framework like gstack installs ~80 skills into
the global path. The result: every session in every repo carries skills that only
matter in a few. There's no built-in way to say "this repo gets these three, and
nothing else."

Claude Code *does* load per-project skills from a repo's `.claude/skills/`. That's
the lever skillkit pulls.

## The hybrid registry

skillkit doesn't require you to copy every skill into one place. `sources.toml`
declares source *roots* — your own authored skills, gstack's canonical directory,
the older `~/.agents/skills` set, anything. The catalog is the union of skills
found under those roots, each tagged by source (`gstack:qa`, `mine:spine-helper`).

This is "hybrid": you author some skills (they live in the registry's `skills/`),
and you reference others in place (no copy, no fork). Adding gstack as a source
costs nothing — its skills become installable without duplicating them.

## Manifest + sync, not symlinks

When you install skills into a project, skillkit commits *intent* to
`.claude/skills.toml` and materializes the actual skills into a gitignored
`.claude/skills/` via `sync`. Three approaches were considered:

- **Symlink** into a central registry — auto-updates, tiny. But symlinks break the
  moment a repo is cloned elsewhere or runs in CI, and committing a symlink is
  fragile. Worse, a registry edit would change agent behavior in every repo
  retroactively, with no signal.
- **Copy/vendor and commit** — portable, but goes stale and bloats repos.
- **Manifest + sync** (chosen) — commit the lockfile (intent), gitignore the
  payload, rehydrate on demand.

### Trade-offs

Sync requires an explicit command — that's the point. Updates are *deliberate*:
you run `skillkit sync` / `skillkit update` and know which repo is on which
version, rather than a registry edit silently rewriting behavior under you. The
cost is that a fresh clone needs one `skillkit sync` to populate skills. For repos
that can't run skillkit (shared, CI), `skillkit vendor` flips to the
copy-and-commit model — the escape hatch, not the default.

There is no version pinning. The manifest records which skills/packs, and `sync`
always materializes the registry's current state. Pins would fight the live-pack
model below and add machinery a personal tool doesn't need.

## Live packs

A pack is a named bundle of skill refs stored in the registry. The project
manifest stores the pack *name*, not its expanded contents. Each `sync` re-reads
the pack definition, so editing a pack (adding a fifth skill) propagates to every
project that lists it, on their next sync.

This is the whole point of a pack: central control. The alternative — freezing the
member list into each manifest at add-time — would mean re-adding the pack
everywhere to pick up a change. The deliberate-update guarantee still holds because
`sync`/`update` are explicit; a pack edit doesn't touch a project until you sync it.

## The marker-protection safety model

`sync` is the only writer of `.claude/skills/`, and it must never destroy work it
didn't create. The mechanism: every skill skillkit materializes gets a
`.skillkit-managed` marker file written inside it.

```
.claude/skills/
  qa/              <- has .skillkit-managed  (skillkit owns it)
    SKILL.md
    .skillkit-managed
  my-hand-skill/   <- no marker               (hand-placed, off-limits)
    SKILL.md
```

Two invariants follow:

- **Removal pass**: when a skill is delisted from the manifest, `sync` removes its
  directory — but only if the marker is present. Unmarked dirs are never removed.
- **Materialize pass**: before writing a skill, if a directory with that name
  already exists *without* a marker, `sync` raises rather than overwrite it. A
  hand-placed `qa/` is never clobbered by a wanted `gstack:qa`.

Materialization is also atomic: skillkit copies into a temp directory, writes the
marker, then renames into place. A failed copy (disk full, source vanished) leaves
the previously-installed skill intact instead of half-deleted.

## gstack adoption

`adopt gstack` makes per-project selection subtractive. gstack keeps a canonical
copy of every skill under `~/.claude/skills/gstack/`, separate from the scattered
top-level copies that load globally. So adoption:

1. Registers `~/.claude/skills/gstack` as the `gstack` source (so you can pull
   skills from it per-project afterward).
2. Moves the scattered top-level copies to the macOS Trash.

### Why "Trash", not delete

The operation is reversible from Finder. A bad call (or a name-collision
false-positive) is recoverable. skillkit never hard-deletes here.

### The name-match limitation, and its mitigation

Detection is by directory name: a top-level dir is "scatter" if it has a same-named
twin under `gstack/` that contains a `SKILL.md`. This can't distinguish a gstack
copy from a hand-authored skill that happens to share a name. The `SKILL.md` twin
check excludes gstack's support dirs (`bin`, `docs`, …), and symlinks are always
skipped — but a genuine name collision would still be flagged.

The mitigation is procedural, not magical: the dry-run (no `--yes`) prints the
exact list of directories it would move, every time, and you approve it. That's
why the command refuses to do anything destructive without `--yes`.

## Related

- [Reference](reference.md)
- [How-to guide](howto.md)
- [Tutorial](tutorial-getting-started.md)
- [Design spec](superpowers/specs/2026-06-02-skillkit-design.md)

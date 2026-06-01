# skillkit Reference

Complete technical reference for the `skillkit` CLI and its file formats. For a
guided introduction, see the [tutorial](tutorial-getting-started.md); for task
recipes, see the [how-to guide](howto.md); for the *why*, see the
[design explanation](explanation-design.md).

## Registry location

skillkit reads its registry (sources, packs, authored skills) from a single
directory, resolved in this order:

1. `$SKILLKIT_REGISTRY` if set
2. `~/ai/skillkit` (default)

The registry is a normal git repo you own. A project's installed skills live in
that project's `.claude/skills/`, not in the registry.

## Skill references

A skill is addressed as `source:name` (e.g. `gstack:qa`, `mine:spine-helper`).
A pack is addressed as `pack:name` (e.g. `pack:code-repo`). `source` is a key
from `sources.toml`; `name` is the skill's `name:` from its `SKILL.md` (falling
back to its directory name).

## Commands

| Command | Effect |
|---------|--------|
| `skillkit add <source:name \| pack:name>` | Add a skill or pack to this project's manifest, then `sync`. |
| `skillkit rm <source:name \| pack:name>` | Remove a skill or pack from the manifest, then `sync`. |
| `skillkit pick` | Open the Textual multiselect over the catalog; install the chosen skills. |
| `skillkit pack create <name>` | Open the picker, save the selection as `packs/<name>.toml` in the registry. |
| `skillkit pack list` | List all packs and their members. |
| `skillkit pack show <name>` | Show one pack. |
| `skillkit sync` | Materialize `.claude/skills/` from the manifest (current registry state). |
| `skillkit update` | `git pull --ff-only` the registry, then `sync`. |
| `skillkit vendor` | `sync`, then commit-enable `.claude/skills/` for this repo (see below). |
| `skillkit list` | Print the catalog (installed skills marked `*`) and packs. |
| `skillkit adopt gstack [--yes]` | De-scatter a global gstack install (see below). |

All commands return exit code `0` on success. `add`/`rm`/`pick`/`sync`/`vendor`
operate on the current working directory as the project.

### `add`

Routes by prefix: `pack:foo` is appended to the manifest's `packs`, anything else
to `skills`. Idempotent (no duplicates). After syncing, if you added a *skill* ref
that is not in the catalog, skillkit prints a warning — nothing was materialized.

### `sync`

The core operation. For each resolved ref present in the catalog, it copies the
skill's folder into `.claude/skills/<name>/` and writes a `.skillkit-managed`
marker file inside it. Skills are copied fresh each run, so registry edits are
picked up. Managed dirs (those with the marker) that are no longer wanted are
removed. Dirs **without** the marker (hand-placed skills) are never removed, and
`sync` refuses to overwrite an unmarked dir whose name collides with a wanted
skill (it raises rather than destroy your work).

### `vendor`

Runs `sync`, then appends `!.claude/skills/` to the project's `.gitignore` so the
materialized skills can be committed. Use for repos that must be self-contained
(shared with others, or CI) where `skillkit sync` won't be run.

### `update`

Fast-forwards the registry repo (`git pull --ff-only`, best-effort) then syncs.
Because packs are live references, this is how you pull both new registry content
and edited pack definitions into a project.

### `adopt gstack`

Makes per-project selection actually subtractive when gstack has installed ~80
skills globally into `~/.claude/skills/`.

- **Dry run** (`skillkit adopt gstack`): prints the exact list of directories it
  *would* move to Trash, and non-destructively registers `~/.claude/skills/gstack`
  as the `gstack` source. Moves nothing.
- **Apply** (`skillkit adopt gstack --yes`): moves each scattered dir to the macOS
  Trash (reversible from Finder) and registers the source.

A directory under `~/.claude/skills/` is treated as gstack scatter only if it
(a) is a real directory (not a symlink), and (b) has a same-named twin under
`~/.claude/skills/gstack/` that itself contains a `SKILL.md`. Support dirs
(`bin`, `docs`, etc.) and symlinks (e.g. to `~/.agents/skills`) are left alone.
Matching is by **name** — always review the dry-run list before `--yes`.

## File formats

### `sources.toml` (registry)

Declares the source roots scanned to build the catalog. Paths may use `~`.

```toml
[sources]
mine   = "~/ai/skillkit/skills"
gstack = "~/.claude/skills/gstack"
agents = "~/.agents/skills"
```

### `packs/<name>.toml` (registry)

A named bundle of skill refs. Packs are live references — editing this file
changes what every project that lists the pack gets on its next `sync`.

```toml
[pack]
name = "code-repo"
description = "Everyday coding repo set"
skills = ["gstack:browse", "gstack:qa", "gstack:ship", "mine:spine-helper"]
```

### `.claude/skills.toml` (project manifest)

Intent for one project. Committed. `.claude/skills/` itself is gitignored (unless
vendored).

```toml
skills = ["gstack:diagnose"]
packs  = ["code-repo"]
vendor = false
```

| Key | Type | Meaning |
|-----|------|---------|
| `skills` | list of `source:name` | Individually-added skills. |
| `packs` | list of pack names (no `pack:` prefix) | Packs whose members are resolved at sync time. |
| `vendor` | bool | Informational flag; `skillkit vendor` is what actually commit-enables skills. |

### `SKILL.md` frontmatter (any skill)

skillkit reads YAML frontmatter for the catalog. `name` and `description` are used.

```markdown
---
name: my-skill
description: One line shown in `skillkit list` and the picker.
---
Skill body...
```

## Related

- [Tutorial: Getting started](tutorial-getting-started.md)
- [How-to guide](howto.md)
- [Design explanation](explanation-design.md)
- [Design spec](superpowers/specs/2026-06-02-skillkit-design.md)

# skillkit — design spec

**Date:** 2026-06-02
**Author:** Narendra Nag
**Status:** Draft for review

## Problem

Claude Code loads skills from `~/.claude/skills/` (global, every session) and from
enabled plugins (also global). Frameworks like gstack scatter ~80 skills into the
global dir, so every session carries skills that only matter in a few repos. There is
no easy way to say "this repo gets these three gstack skills plus one of mine, and
nothing else."

Claude Code *does* load per-project skills from a repo's `.claude/skills/<name>/`.
That is the lever. `skillkit` is a small tool to curate a registry of skills and
install chosen subsets — individually or as named packs — into a project's
`.claude/skills/`.

## Goals

- A **hybrid registry**: one catalog spanning skills I author/fork *and* references to
  skills that already live elsewhere (gstack, the `~/.agents/skills` set, plugins).
- **Skill packs**: named bundles (e.g. `code-repo` = three gstack skills + one custom)
  installed in one command, instead of scrolling 80 skills.
- **Per-project install** via a committed manifest, with `.claude/skills/` rehydrated
  on demand — clean repos, reproducible across my fleet.
- **Deliberate, propagating updates**: `sync` materializes current registry state;
  editing a pack propagates to every project on its next `sync` (live references).
- Make per-project picking genuinely **subtractive** for gstack (stop the global 80
  from loading), not just additive.

## Non-goals (YAGNI)

- **No version pinning / semver / lockfile hashes.** The manifest records *intent*
  (which skills/packs); `sync` always pulls the registry's current state. "Deliberate"
  comes from `sync` being an explicit command, not from pins.
- No remote skill marketplace / publishing flow beyond it being a normal public git repo.
- No GUI beyond the terminal TUI.
- No management of MCP servers (separate concern).

## Decisions (locked during brainstorming)

| Decision | Choice |
|---|---|
| Registry model | **Hybrid** — authored skills + in-place references to existing installs |
| Install mode | **Manifest + sync**; `.claude/skills/` gitignored, rehydrated by `sync`. `vendor` flag copies-in + commits for self-contained repos |
| Pack semantics | **Live reference** — manifest stores `pack:<name>`; `sync`/`update` re-resolve |
| Versioning | **None** (YAGNI) |
| Implementation | **Python + Textual TUI**, managed with `uv` (pyproject) |
| Registry home | **`~/ai/skillkit/`**, a new **public** git repo (CLI + registry content together) |
| gstack | **De-scatter in v1** — register gstack's canonical dir as a source, remove the global scatter |

## Architecture

### Repo layout (`~/ai/skillkit/`, public)
```
skillkit/
  pyproject.toml            # uv-managed; entry point `skillkit`
  src/skillkit/
    __init__.py
    cli.py                  # arg parsing, dispatch
    catalog.py              # scan sources -> union catalog
    manifest.py             # read/write .claude/skills.toml
    sync.py                 # materialize / vendor / update
    adopt.py                # gstack de-scatter
    tui.py                  # Textual screens: pick, pack create
  sources.toml              # declared source roots
  packs/
    code-repo.toml
    ...
  skills/                   # skills I author/fork (canonical "mine:" copies)
    <skill-name>/SKILL.md
  docs/superpowers/specs/   # this spec
  .pre-commit-config.yaml   # gitleaks (matches existing setup)
  .gitignore
  README.md                 # incl. public-repo caveat + gstack-upgrade note
```

### Components (each independently testable)

1. **catalog.py** — given `sources.toml`, scan each source root one level deep for
   skill dirs (those containing `SKILL.md`), parse YAML frontmatter (`name`,
   `description`), and return a catalog: list of `{source, name, path, description}`.
   Plugins are auto-detected read-only from `~/.claude/plugins`. Pack definitions are
   loaded from `packs/*.toml`. Pure function of disk state; no side effects.

2. **manifest.py** — read/write a project's `.claude/skills.toml`. Entries are intent:
   `skills = ["gstack:qa", "mine:spine-helper"]`, `packs = ["code-repo"]`. Resolves
   packs against the catalog into a flat set of skill refs (dedup).

3. **sync.py** —
   - `sync`: resolve manifest -> flat skill set -> for each, **copy** the skill folder
     from its source into `.claude/skills/<name>/` (fresh copy each run = picks up
     registry edits). Remove `.claude/skills/<name>` dirs that skillkit manages but are
     no longer in the manifest (tracked via a `.skillkit-managed` marker file per dir so
     we never delete hand-placed skills).
   - `update`: `git -C ~/ai/skillkit pull` (if a remote exists) then `sync`.
   - `vendor`: same copy, but write/commit into `.claude/skills/` as tracked files and
     add a local `.gitignore` negation so the repo is self-contained.

4. **adopt.py** (`skillkit adopt gstack`) — register `~/.claude/skills/gstack` as the
   `gstack` source in `sources.toml`, then remove the ~55 top-level scattered gstack
   skill dirs from `~/.claude/skills/` (only those that also exist under
   `gstack/`, to be safe). Print a summary; never touch non-gstack dirs or symlinks.
   README documents that `gstack-upgrade` may re-scatter and how to re-run adopt.

5. **tui.py** (Textual) — `pick` opens a multiselect catalog grouped by source
   (spacebar select, enter installs into the current project). `pack create <name>`
   uses the same selector and writes `packs/<name>.toml`. Non-interactive verbs
   (`add`, `sync`, `update`, `vendor`, `list`) print with `rich`.

### Data formats

```toml
# ~/ai/skillkit/sources.toml
[sources]
mine   = "~/ai/skillkit/skills"
gstack = "~/.claude/skills/gstack"
agents = "~/.agents/skills"
# plugins auto-detected from ~/.claude/plugins
```

```toml
# ~/ai/skillkit/packs/code-repo.toml
[pack]
name = "code-repo"
description = "Everyday coding repo set"
skills = ["gstack:browse", "gstack:qa", "gstack:ship", "mine:spine-helper"]
```

```toml
# <project>/.claude/skills.toml
skills = ["gstack:diagnose"]
packs  = ["code-repo"]
vendor = false
```

### Command surface
```
skillkit add <source:name | pack:name>   # add to this project's manifest, then sync
skillkit rm  <source:name | pack:name>   # remove from manifest, then sync
skillkit pick                            # Textual multiselect over the catalog
skillkit pack create <name>              # build a pack from a selection
skillkit pack list|show <name>           # inspect packs
skillkit sync                            # materialize .claude/skills/ from manifest
skillkit update                          # pull registry, re-resolve, sync
skillkit vendor                          # copy-in + commit (self-contained repo)
skillkit list                            # installed-here vs available
skillkit adopt gstack                    # de-scatter gstack (one-time)
```

### gitignore strategy
- Global gitignore (`~/.config/git/ignore`) gains `**/.claude/skills/` so materialized
  skills never get committed by default across all repos.
- `vendor` writes a repo-local `.gitignore` with `!.claude/skills/` to opt that repo in
  to committing them.

## Error handling

- Missing source root or unreadable `SKILL.md` -> warn and skip that entry, continue.
- `add` of an unknown ref -> error listing near-matches from the catalog.
- `sync` outside a project (no writable cwd / refusal) -> clear message.
- `adopt gstack` is idempotent and only removes dirs that have a canonical twin under
  `gstack/`; prints exactly what it will remove and requires `--yes` for the deletion.

## Testing

- `catalog.py`: fixture source tree -> assert union, frontmatter parse, dedup.
- `manifest.py`: round-trip read/write; pack resolution incl. nested dedup.
- `sync.py`: temp project; assert copy, removal of de-listed managed skills, marker-file
  protection of hand-placed skills, vendor toggling gitignore.
- `adopt.py`: fake `~/.claude/skills` with scattered + canonical dirs -> assert only
  twinned scatter removed, symlinks and standalone dirs untouched.
- TUI: smoke test that screens build and selection maps to manifest writes.

## Build sequence

1. Scaffold repo: pyproject (uv), package skeleton, pre-commit/gitleaks, README, gitignore.
2. `catalog.py` + tests.
3. `manifest.py` + tests.
4. `sync.py` (sync/update/vendor) + tests.
5. `cli.py` wiring non-interactive verbs.
6. `adopt.py` + tests; run `adopt gstack` for real once green.
7. `tui.py` (pick, pack create).
8. Author first pack (`code-repo`) and dogfood in a coding repo.

## Open risks

- gstack-upgrade re-scattering: documented; `adopt` is re-runnable. Could later add a
  post-upgrade hook, out of scope for v1.
- Public repo hygiene: gitleaks pre-commit + README caveat to keep secrets/client names
  out of authored skills.

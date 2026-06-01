# skillkit

A per-project Claude Code skill manager. Curate a hybrid registry of skills — yours, gstack's, team collections — and install chosen subsets (individually or as packs) into a project's `.claude/skills/`. Skills become active only in the projects you select them for, not in every Claude Code session system-wide.

**Why it exists.** Frameworks like [gstack](https://github.com/gstacks/gstack) scatter ~80 skills into `~/.claude/skills/` so they load in _every_ session, regardless of project. skillkit makes skill selection per-project and declarative: commit a `skills.toml`, `sync` anywhere.

---

## Install

```sh
git clone <this-repo> ~/ai/skillkit
cd ~/ai/skillkit
uv tool install --editable .
```

This puts `skillkit` on your PATH via uv's tool shim directory. If `uv` prints a PATH hint after install, add the suggested directory to your shell's `$PATH`.

**Registry location** — resolved in this order:

1. `$SKILLKIT_REGISTRY` environment variable
2. Default: `~/ai/skillkit` (the cloned repo itself)

---

## Concepts

| Concept | Where it lives | What it is |
|---|---|---|
| **Source** | `sources.toml` in the registry | A named root directory whose sub-dirs are skills. Declare your `mine` skills, gstack's dir, a shared team collection, etc. |
| **Catalog** | computed | Union of all source roots — every skill across all declared sources. |
| **Pack** | `packs/*.toml` in the registry | A named bundle of skill refs (`source:name`). LIVE references: re-resolved on every `sync`, so updating a skill in a source is automatically picked up. |
| **Project manifest** | `.claude/skills.toml` (committed) | Records which skills and packs a project wants. This is the _intent_; commit it so teammates can rehydrate. |
| **Materialized skills** | `.claude/skills/` (gitignored by default) | The actual skill directories, copied in by `sync`. Rehydrate with `skillkit sync`. |

### `sources.toml` example

```toml
[sources]
mine   = "~/ai/skillkit/skills"
gstack = "~/.claude/skills/gstack"
```

### Pack file example (`packs/webapp.toml`)

```toml
[pack]
name        = "webapp"
description = "Skills for a typical web app project"
skills      = ["mine:qa", "gstack:next-best-practices", "gstack:review"]
```

---

## Commands

| Command | What it does |
|---|---|
| `skillkit add <ref>` | Add a skill or pack to the project manifest and sync |
| `skillkit rm <ref>` | Remove a skill or pack from the manifest and sync |
| `skillkit pick` | Textual multiselect TUI — browse the catalog and toggle skills/packs |
| `skillkit sync` | Materialize the current manifest into `.claude/skills/` |
| `skillkit update` | `git pull` the registry, then sync |
| `skillkit vendor` | Copy skills in and mark them committed (see Install Modes) |
| `skillkit list` | Show catalog with `[*]` next to installed skills/packs |
| `skillkit pack create <name>` | Interactively build a new pack (Textual picker → `packs/<name>.toml`) |
| `skillkit pack list` | List all packs in the registry |
| `skillkit pack show <name>` | Show a pack's details |
| `skillkit adopt gstack` | Register gstack's dir as a source and preview scattered dirs (dry run) |
| `skillkit adopt gstack --yes` | Same, plus move scattered gstack dirs to macOS Trash |

**Ref syntax:**
- `source:name` — a specific skill, e.g. `mine:qa`, `gstack:review`
- `pack:name` — an entire pack, e.g. `pack:webapp`

---

## Install Modes

### Default (gitignored, rehydrated on sync)

`.claude/skills/` is listed in `.gitignore`. Each teammate or CI environment runs `skillkit sync` after checkout to materialize skills locally. Only `skills.toml` is committed.

```sh
skillkit add gstack:review   # adds to .claude/skills.toml, materializes immediately
skillkit sync                # re-materialize anywhere after a fresh checkout
```

### Vendor mode (skills committed to the repo)

Useful for self-contained repos or when you want skills version-locked to the repo snapshot:

```sh
skillkit vendor
```

This runs `sync` then writes a `!.claude/skills/` negation line to `.gitignore`, so the materialized skills directory is tracked by git. Commit both the manifest and the `skills/` directory.

---

## Authoring Skills

A skill is a directory containing a `SKILL.md` file. Front-matter declares metadata:

```markdown
---
name: my-skill
description: Short description shown in catalog and picker
---

# My Skill

Instructions for Claude...
```

Place skill directories under a root declared in `sources.toml`. They appear in `skillkit list` and the `pick` TUI immediately.

---

## `skillkit adopt gstack`

gstack installs its skills scattered into `~/.claude/skills/` alongside skills from other sources. `adopt gstack` consolidates this:

1. Registers `~/.claude/skills/gstack` as a `gstack` source in `sources.toml`.
2. Detects "scattered" gstack skill dirs — top-level dirs in `~/.claude/skills/` whose names match a dir inside `~/.claude/skills/gstack/`.
3. Without `--yes`: shows the dry-run list of dirs that _would_ be moved to Trash. No filesystem changes beyond writing `sources.toml`.
4. With `--yes`: moves those scattered dirs to macOS Trash (reversible).

> **Always review the dry-run first.** Scatter detection matches by directory name only — a non-gstack skill sharing a name with a gstack skill will be flagged.

```sh
skillkit adopt gstack        # dry run — review the list
skillkit adopt gstack --yes  # approved — move scattered dirs to Trash
```

After running `gstack-upgrade`, gstack may re-scatter skills. Just re-run `skillkit adopt gstack --yes`.

---

## Public-Repo Caveat

> **This registry repo is PUBLIC.**

Keep secrets, internal URLs, and client names out of skill files under `skills/`. A [gitleaks](https://github.com/gitleaks/gitleaks) pre-commit hook is configured in `.pre-commit-config.yaml`. Enable it once after cloning:

```sh
pre-commit install
```

The hook scans each commit for leaked credentials before they are pushed.

---

## Running Tests

```sh
uv run pytest        # 33 tests
```

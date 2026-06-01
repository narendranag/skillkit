# CLAUDE.md — skillkit

Per-project Claude Code skill manager: curate a hybrid registry of skills and
install chosen subsets (individually or as packs) into a project's
`.claude/skills/`. Full design in `docs/explanation-design.md` and
`docs/superpowers/specs/2026-06-02-skillkit-design.md`.

## Environment

- Python 3.11+ managed with **`uv`** (not pip/brew). Run things with `uv run ...`.
- Tests: `uv run pytest` (34 tests). Always TDD — write the failing test first.
- Install the CLI for manual testing: `uv tool install --editable .`.

## Module map (`src/skillkit/`)

| File | Responsibility | Notes |
|------|----------------|-------|
| `config.py` | `registry_root()` | `$SKILLKIT_REGISTRY` or `~/ai/skillkit`. |
| `catalog.py` | scan sources → union catalog | `SkillEntry` (frozen, has `.ref`), `Pack` (frozen, `skills: tuple`), `parse_frontmatter`, `load_sources`, `scan_source`, `build_catalog`, `load_packs`. Pure function of disk state. |
| `manifest.py` | read/write/resolve `.claude/skills.toml` | `Manifest`, `resolve()` flattens skills + pack members, dedup first-seen. |
| `sync.py` | the ONLY writer of `.claude/skills/` | `sync`, `vendor`, `update`, `MANAGED_MARKER`. |
| `adopt.py` | the ONLY thing that touches `~/.claude/skills/` | `find_scatter`, `to_trash`, `register_source`, `adopt_gstack`. Destructive (Trash moves). |
| `cli.py` | argparse dispatch | `main(argv) -> int`. Thin layer over the above. |
| `tui.py` | Textual multiselect | `PickApp(registry_root=...)`; `pick` / `pack create` use it. |

Keep these boundaries. `catalog` is read-only; `sync` owns project skills; `adopt`
owns the global dir. Don't cross them.

## Non-negotiable invariants (have unit tests — keep them green)

- **sync never destroys unmarked dirs.** Materialized skills get a
  `.skillkit-managed` marker. Removal only touches marked dirs; `_materialize`
  *raises* rather than overwrite an unmarked dir whose name collides. Materialize
  is atomic (copy to temp → write marker → rename). Don't "simplify" this back to
  rmtree-then-copytree.
- **adopt matches by name + `SKILL.md` twin, skips symlinks.** `find_scatter` only
  flags a `~/.claude/skills/X` dir if `gstack/X` exists, is a real dir, and
  contains `SKILL.md`. Symlinks (e.g. to `~/.agents/skills`) are skipped. It's
  name-based, so the CLI dry-run MUST print the candidate list and `--yes` is
  required before any Trash move.
- **No version pinning (YAGNI).** Manifest carries refs only; `sync` always
  materializes the registry's current state. Packs are LIVE references.

## Conventions

- All file I/O passes `encoding="utf-8"` (read and write). Match it.
- Refs are `source:name`; packs are `pack:name` on the CLI, bare names in the
  manifest's `packs` list.
- Prefer the dedicated tools / small focused files. New behavior → new test.
- Frontmatter parsing is line-based (`---` on its own line) and guards
  `yaml.YAMLError` → `{}`. Don't revert to substring splitting.

## Public-repo caveat

This repo is **public**. Never commit secrets, internal URLs, client names, or
real tokens — including in authored skills under `skills/`. A gitleaks pre-commit
hook is configured; run `pre-commit install` once. (Note: the zernio MCP that
also lives in this user's world uses a Bearer token — it must never land here.)

## Gotchas

- `vendor` writes a `!.claude/skills/` negation to the repo `.gitignore`. Git
  can't always re-include files under a globally-ignored directory via a child
  negation — verify with `git check-ignore` before relying on vendor mode; may
  need `!.claude/skills/**`.
- `adopt gstack` is idempotent; gstack-upgrade re-scatters, just re-run it.

# Getting started with skillkit

By the end of this tutorial you'll have skillkit installed, your global gstack
skills de-scattered, a reusable "code-repo" pack, and that pack installed into a
real project — so a fresh Claude Code session in that project loads only the
skills you chose.

You'll build this in about ten minutes.

## What you'll need

- macOS with Claude Code installed (skills load from `.claude/skills/`).
- [`uv`](https://docs.astral.sh/uv/) on your PATH.
- The skillkit repo cloned at `~/ai/skillkit` (the default registry location).
- A gstack install that scattered skills into `~/.claude/skills/` (optional — skip
  Step 2 if you don't have one).

## Step 1: Install skillkit

From the repo:

```bash
cd ~/ai/skillkit
uv tool install --editable .
```

Confirm it landed on your PATH:

```bash
skillkit --help
```

You should see the subcommand list (`add`, `rm`, `sync`, `adopt`, `pick`, `pack`, …).
That's the whole CLI — you now have skillkit working.

## Step 2: De-scatter gstack (preview first)

gstack installs ~80 skills into `~/.claude/skills/`, and they load in *every*
session. To make per-project selection meaningful, move them out of the global
path. First, see exactly what would move — this changes nothing:

```bash
skillkit adopt gstack
```

You'll see something like:

```
Would move 55 scattered gstack dirs to Trash:
  - browse
  - qa
  - ship
  ...
Review the list above. Re-run with --yes to proceed.
```

Read the list. Everything there should be a gstack skill. When you're satisfied:

```bash
skillkit adopt gstack --yes
```

The scattered dirs move to your macOS Trash (recoverable from Finder), and
gstack's canonical directory is registered as a source you can pull from. Open a
fresh Claude Code session and you'll see the global gstack skills are gone — but
still available to install per-project.

## Step 3: See what's available

```bash
skillkit list
```

This prints the catalog — every skill across your registered sources, tagged by
source (`gstack:qa`, `mine:spine-helper`, …), with installed skills marked `*`.

## Step 4: Build a pack

Instead of picking the same handful of skills every time, bundle them once:

```bash
skillkit pack create code-repo
```

A multiselect opens. Space to select the three or four skills you actually use in
coding repos (say `gstack:browse`, `gstack:qa`, `gstack:ship`), Enter to save.
This writes `~/ai/skillkit/packs/code-repo.toml`.

Verify it:

```bash
skillkit pack show code-repo
```

## Step 5: Install the pack into a project

Switch to a real coding repo and add the pack:

```bash
cd ~/code/my-project
skillkit add pack:code-repo
```

skillkit writes `.claude/skills.toml` (committed intent) and materializes the
pack's skills into `.claude/skills/` (gitignored). Check:

```bash
skillkit list          # the pack's skills now show *
ls .claude/skills/      # exactly your chosen skills, each with a .skillkit-managed marker
```

Open a fresh Claude Code session in this repo: it loads your three skills and
nothing else.

## What you built

You now have:

- skillkit installed as a CLI.
- gstack moved out of the global skill path (so nothing loads everywhere by default).
- A `code-repo` pack you can drop into any project with one command.
- One project running exactly the skills you chose.

Next: add the pack to your other repos (`skillkit add pack:code-repo`), edit the
pack once to change them everywhere (`skillkit pack create code-repo` again, then
`skillkit update` in each project), or author your own skill — see the
[how-to guide](howto.md). For the full command set, see the
[reference](reference.md).

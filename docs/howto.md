# skillkit How-To Guides

Task-oriented recipes. These assume you've installed skillkit and know the basics
(see the [tutorial](tutorial-getting-started.md)). For full command and format
details, see the [reference](reference.md).

---

## How to add skills to a project

Goal: pull one or more registry skills into the current repo.

### Steps

1. From the project root, add a skill by ref:

   ```bash
   skillkit add gstack:diagnose
   ```

   This appends to `.claude/skills.toml` and syncs immediately.

2. Add several at once by repeating, or browse interactively:

   ```bash
   skillkit pick
   ```

   Space to select, Enter to install.

### Verification

```bash
skillkit list      # added skills are marked *
ls .claude/skills/  # the skill folders are present
```

### Troubleshooting

- **"`x:y` is not in the catalog" warning** — the ref doesn't match any source.
  Run `skillkit list` to see valid refs, or check the source is declared in
  `sources.toml`.

---

## How to create and reuse a skill pack

Goal: bundle a set of skills under one name and install them together.

### Steps

1. Create the pack from a selection:

   ```bash
   skillkit pack create code-repo
   ```

   Or hand-write `~/ai/skillkit/packs/code-repo.toml` (see the
   [reference](reference.md#packsnametoml-registry)).

2. Install it in any project:

   ```bash
   skillkit add pack:code-repo
   ```

3. Change the pack later — edit `packs/code-repo.toml` (add/remove a skill), then
   in each project run:

   ```bash
   skillkit update
   ```

   Packs are live references, so the change propagates on sync.

### Verification

```bash
skillkit pack show code-repo
```

---

## How to de-scatter a global gstack install

Goal: stop ~80 gstack skills from loading in every session, and pull only the ones
you want per-project.

### Prerequisites

- A gstack install that populated `~/.claude/skills/`.

### Steps

1. Preview — this moves nothing:

   ```bash
   skillkit adopt gstack
   ```

2. Read the printed list. Confirm every entry is a gstack skill you're happy to
   move out of the global path.

3. Apply:

   ```bash
   skillkit adopt gstack --yes
   ```

   Scattered dirs move to the macOS Trash; gstack's canonical dir is registered as
   the `gstack` source.

### Verification

Open a fresh Claude Code session — the global gstack skills are gone. Then in a
project, `skillkit add gstack:qa` pulls one back in just for that repo.

### Troubleshooting

- **A non-gstack dir appears in the preview** — do not run `--yes`. Matching is by
  name; a hand-authored skill that shares a name with a gstack skill will be
  listed. Rename or move it first.
- **gstack-upgrade re-scattered the skills** — just re-run
  `skillkit adopt gstack --yes`. It's idempotent.

---

## How to make a repo self-contained (vendor)

Goal: commit the skills into a repo so collaborators or CI get them without
running skillkit.

### Steps

1. Add the skills/packs you want as usual (`skillkit add ...`).

2. Vendor them:

   ```bash
   skillkit vendor
   ```

   This syncs, then appends `!.claude/skills/` to the repo's `.gitignore` so the
   materialized skills become committable.

3. Commit the skills:

   ```bash
   git add .claude/skills .gitignore .claude/skills.toml
   git commit -m "vendor skillkit skills"
   ```

### Verification

```bash
git check-ignore .claude/skills/<some-skill>/SKILL.md   # should print nothing (not ignored)
```

If it's still ignored, your global gitignore excludes the whole `.claude/skills/`
directory; ensure the repo-level `!.claude/skills/` negation is present and, if
needed, broaden it (`!.claude/skills/**`).

---

## How to author your own skill

Goal: add a skill you wrote to the registry so you can install it anywhere.

### Steps

1. Create a directory under the registry's `mine` source with a `SKILL.md`:

   ```bash
   mkdir -p ~/ai/skillkit/skills/spine-helper
   $EDITOR ~/ai/skillkit/skills/spine-helper/SKILL.md
   ```

2. Give it frontmatter:

   ```markdown
   ---
   name: spine-helper
   description: One-line summary shown in list and picker.
   ---
   Skill instructions...
   ```

3. It now appears in the catalog as `mine:spine-helper`:

   ```bash
   skillkit list | grep spine-helper
   ```

### Verification

```bash
cd ~/some-project && skillkit add mine:spine-helper
ls .claude/skills/spine-helper/
```

### Troubleshooting

- **Doesn't appear in `list`** — confirm the `mine` source path in `sources.toml`
  points at `~/ai/skillkit/skills` and the dir contains a `SKILL.md`.
- **Public repo** — the registry is public. Keep secrets, internal URLs, and
  client names out of authored skills. The gitleaks pre-commit hook will catch
  obvious secrets if you run `pre-commit install`.

## Related

- [Tutorial](tutorial-getting-started.md)
- [Reference](reference.md)
- [Design explanation](explanation-design.md)

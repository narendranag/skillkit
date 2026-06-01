"""Smoke tests for the Textual TUI (PickApp)."""
import pytest
from pathlib import Path
from skillkit.tui import PickApp


def _registry(tmp_path):
    g = tmp_path / "g"
    (g / "qa").mkdir(parents=True)
    (g / "qa" / "SKILL.md").write_text("---\nname: qa\ndescription: QA\n---\n")
    (tmp_path / "sources.toml").write_text(f'[sources]\ngstack = "{g}"\n')
    (tmp_path / "packs").mkdir()
    return tmp_path


@pytest.mark.asyncio
async def test_pickapp_builds_and_lists(tmp_path):
    app = PickApp(registry_root=_registry(tmp_path))
    async with app.run_test() as pilot:
        await pilot.pause()
        # The catalog should contain gstack:qa as a selectable option.
        # Use get_option_at_index (returns Selection with .value) to check.
        count = app.selection.option_count
        assert count > 0, "Expected at least one option in SelectionList"
        values = [
            app.selection.get_option_at_index(i).value
            for i in range(count)
        ]
        assert "gstack:qa" in values, f"Expected 'gstack:qa' in {values}"

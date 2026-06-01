"""Textual TUI for browsing the catalog and building packs."""
from __future__ import annotations
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header
from textual.widgets import SelectionList
from textual.widgets.selection_list import Selection
from skillkit.catalog import build_catalog


class PickApp(App):
    """Multiselect over the catalog; returns chosen refs on exit."""

    BINDINGS = [("enter", "confirm", "Install"), ("q", "quit", "Quit")]

    def __init__(self, registry_root: Path):
        super().__init__()
        self._reg = registry_root
        # Build Selection objects upfront so compose can pass them to constructor.
        # Passing selections to the constructor works in all Textual versions,
        # and avoids add_option-before-mount issues in some builds.
        entries = build_catalog(self._reg)
        self._selections = [
            Selection(f"{e.ref}  —  {e.description}", e.ref)
            for e in entries
        ]
        self.selection: SelectionList[str] = SelectionList(*self._selections)
        self.chosen: list[str] = []

    def compose(self) -> ComposeResult:
        yield Header()
        yield self.selection
        yield Footer()

    def action_confirm(self) -> None:
        self.chosen = list(self.selection.selected)
        self.exit(self.chosen)

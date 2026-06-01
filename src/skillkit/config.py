"""Resolve where the skillkit registry lives."""
import os
from pathlib import Path


def registry_root() -> Path:
    """Registry repo root: $SKILLKIT_REGISTRY or ~/ai/skillkit."""
    return Path(os.environ.get("SKILLKIT_REGISTRY", "~/ai/skillkit")).expanduser()

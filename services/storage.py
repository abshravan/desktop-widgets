# storage.py — Read/write JSON state in ~/.config/desktop-widget/.
# All persistent UI state (todos, window position, etc.) goes through this.

import json
import os
from pathlib import Path

CONFIG_DIR = Path(os.path.expanduser("~/.config/desktop-widget"))


def _file(name: str) -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR / name


def load(name: str, default):
    path = _file(name)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        return default


def save(name: str, data):
    try:
        _file(name).write_text(json.dumps(data, indent=2))
    except OSError:
        pass

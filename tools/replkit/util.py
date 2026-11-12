"""Small shared helpers for Replkit."""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ReplkitError(Exception):
    """Base class for errors that should be shown without a traceback."""


def now_iso() -> str:
    """Return a stable UTC timestamp with second precision."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path | str) -> Any:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path | str, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def read_text(path: Path | str) -> str:
    return Path(path).read_text(encoding="utf-8")


def atomic_write(path: Path | str, text: str) -> None:
    """Write a file through a temporary sibling, then replace it.

    This avoids a half-written state file if the process is interrupted.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "replica"


def is_hex_colour(value: str) -> bool:
    return bool(
        re.fullmatch(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", value.strip())
    )

"""Environment and installation checks for OpenReplica."""

from __future__ import annotations

import importlib.util
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List

from . import state


def _check(
    name: str,
    ok: bool,
    detail: str,
    fix: str = "",
    required: bool = True,
) -> Dict[str, Any]:
    return {"name": name, "ok": bool(ok), "detail": detail, "fix": fix, "required": required}


def run(root: Path | str = ".") -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    checks.append(
        _check(
            "python",
            sys.version_info >= (3, 8),
            sys.version.split()[0],
            "Instala Python 3.8 o superior.",
        )
    )
    checks.append(
        _check(
            "git",
            shutil.which("git") is not None,
            shutil.which("git") or "no encontrado",
            "Instala git.",
        )
    )

    node = shutil.which("node")
    npm = shutil.which("npm")
    checks.append(
        _check(
            "node",
            node is not None,
            node or "no encontrado (opcional)",
            "Instala Node.js si tu clon lo necesita.",
            required=False,
        )
    )
    checks.append(
        _check(
            "npm",
            npm is not None,
            npm or "no encontrado (opcional)",
            "Instala npm si tu clon lo necesita.",
            required=False,
        )
    )

    playwright = importlib.util.find_spec("playwright") is not None
    checks.append(
        _check(
            "playwright",
            playwright,
            "disponible" if playwright else "no instalado (captura manual o stub)",
            "pip install playwright && playwright install chromium",
            required=False,
        )
    )

    state_file = state.state_path(root)
    checks.append(
        _check(
            "replica/state.json",
            state_file.exists(),
            str(state_file) if state_file.exists() else "no existe",
            "Ejecuta: replica init",
            required=False,
        )
    )

    replica_dir = state.replica_dir(root)
    writable = True
    if replica_dir.exists():
        writable = os.access(replica_dir, os.W_OK)
    checks.append(
        _check(
            "escritura en replica/",
            writable,
            "ok" if writable else "sin permiso de escritura",
            "Revisa los permisos de la carpeta replica/.",
        )
    )

    cli = shutil.which("replica")
    local_cli = Path(root).resolve() / ".opencode" / "bin" / "replica"
    cli_path = cli or (str(local_cli) if local_cli.exists() else None)
    checks.append(
        _check(
            "CLI en PATH",
            cli_path is not None,
            cli_path or "no encontrado",
            "Instala con: ./scripts/install.sh --global o usa .opencode/bin/replica",
            required=False,
        )
    )

    local_bin = Path.home() / ".local" / "bin"
    in_path = str(local_bin) in os.environ.get("PATH", "").split(os.pathsep)
    checks.append(
        _check(
            "~/.local/bin en PATH",
            in_path,
            "ok" if in_path else "no esta en PATH",
            'Anade: export PATH="$HOME/.local/bin:$PATH"',
            required=False,
        )
    )

    ok = all(check["ok"] for check in checks if check["required"])
    return {"ok": ok, "checks": checks}


def render(result: Dict[str, Any]) -> str:
    lines = ["Doctor de OpenReplica", ""]
    for check in result["checks"]:
        if check["ok"]:
            mark = "[x]"
        elif check["required"]:
            mark = "[!]"
        else:
            mark = "[-]"
        suffix = "" if check["required"] else " (opcional)"
        lines.append(mark + " " + check["name"] + ": " + check["detail"] + suffix)
        if not check["ok"] and check["fix"]:
            lines.append("    " + check["fix"])
    lines.append("")
    lines.append("Todo listo." if result["ok"] else "Hay requisitos pendientes.")
    return "\n".join(lines)

"""Project state and phase transitions for OpenReplica."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

from .util import atomic_write, now_iso, read_json, write_json

PHASES = [
    "recon",
    "architect",
    "design",
    "build",
    "backend",
    "test",
    "diff",
    "entrepreneur",
    "brand",
    "launch",
    "deploy",
]

STATUSES = ("pending", "in_progress", "blocked", "passed", "skipped")

ARTIFACTS = {
    "recon": ["replica/recon.md", "replica/features.csv"],
    "architect": ["replica/architecture.md"],
    "design": ["replica/design/tokens.json"],
    "build": ["replica/features.csv", "replica/build-log.md"],
    "backend": ["replica/backend.md", ".env.example"],
    "test": ["replica/test-plan.md", "replica/bugs.md"],
    "diff": ["replica/parity.json"],
    "entrepreneur": ["replica/reviews.csv", "replica/feedback.md"],
    "brand": ["replica/brand.json"],
    "launch": ["replica/listing.json"],
    "deploy": ["replica/preflight.md"],
}


class StateError(Exception):
    """Raised when the state file is missing or invalid."""


def project_root(root: Path | str = ".") -> Path:
    return Path(root).resolve()


def replica_dir(root: Path | str = ".") -> Path:
    return project_root(root) / "replica"


def state_path(root: Path | str = ".") -> Path:
    return replica_dir(root) / "state.json"


def default_state(name: Optional[str] = None) -> Dict[str, Any]:
    now = now_iso()
    return {
        "version": 1,
        "name": name or "replica",
        "created_at": now,
        "updated_at": now,
        "phases": {
            phase: {
                "status": "pending",
                "artifacts": [],
                "notes": "",
                "model": None,
                "updated_at": None,
            }
            for phase in PHASES
        },
        "meta": {},
    }


def validate(state: Dict[str, Any]) -> bool:
    if not isinstance(state, dict):
        raise StateError("state must be a JSON object")
    if state.get("version") != 1:
        raise StateError("unsupported state version")
    phases = state.get("phases")
    if not isinstance(phases, dict):
        raise StateError("state.phases must be an object")
    for phase in PHASES:
        row = phases.get(phase)
        if not isinstance(row, dict):
            raise StateError("missing phase: " + phase)
        if row.get("status") not in STATUSES:
            raise StateError("invalid status for " + phase)
    return True


def load(root: Path | str = ".") -> Dict[str, Any]:
    path = state_path(root)
    if not path.exists():
        raise StateError(
            "no replica/state.json found in "
            + str(project_root(root))
            + "; run: replica init"
        )
    state = read_json(path)
    validate(state)
    return state


def save(root: Path | str, state: Dict[str, Any]) -> None:
    validate(state)
    state["updated_at"] = now_iso()
    write_json(state_path(root), state)


def init(root: Path | str = ".", name: Optional[str] = None, force: bool = False) -> Dict[str, Any]:
    rdir = replica_dir(root)
    path = state_path(root)
    if path.exists() and not force:
        raise StateError("replica/state.json already exists; use --force to replace it")

    for sub in ("screens", "clone-screens", "design"):
        (rdir / sub).mkdir(parents=True, exist_ok=True)

    state = default_state(name or project_root(root).name)
    write_json(path, state)

    readme = rdir / "README.md"
    if not readme.exists():
        atomic_write(
            readme,
            "# Replica workspace\n\n"
            "This folder holds the evidence and decisions for each phase.\n\n"
            "- `state.json`: phase status. Do not edit by hand unless you must.\n"
            "- `screens/`: original captures.\n"
            "- `clone-screens/`: captures of your clone.\n"
            "- `design/`: design tokens and visual notes.\n\n"
            "Run `replica status` to see the next phase, and "
            "`replica gate <phase>` before moving on.\n",
        )
    return state


def set_phase(
    state: Dict[str, Any],
    phase: str,
    status: str,
    artifacts: Optional[list[str]] = None,
    notes: Optional[str] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    if phase not in PHASES:
        raise StateError("unknown phase: " + phase)
    if status not in STATUSES:
        raise StateError("unknown status: " + status)
    row = state["phases"][phase]
    row["status"] = status
    if artifacts is not None:
        row["artifacts"] = list(artifacts)
    if notes is not None:
        row["notes"] = notes
    if model is not None:
        row["model"] = model
    row["updated_at"] = now_iso()
    return row


def get_phase(state: Dict[str, Any], phase: str) -> Dict[str, Any]:
    if phase not in PHASES:
        raise StateError("unknown phase: " + phase)
    return state["phases"][phase]


def next_phase(state: Dict[str, Any]) -> Optional[str]:
    for phase in PHASES:
        if state["phases"][phase]["status"] not in ("passed", "skipped"):
            return phase
    return None


def summary(state: Dict[str, Any]) -> Dict[str, Any]:
    counts: Dict[str, int] = {}
    for phase in PHASES:
        status = state["phases"][phase]["status"]
        counts[status] = counts.get(status, 0) + 1
    return {
        "name": state.get("name"),
        "current": next_phase(state),
        "phases": {phase: state["phases"][phase]["status"] for phase in PHASES},
        "counts": counts,
        "updated_at": state.get("updated_at"),
    }


def render(data: Dict[str, Any]) -> str:
    marks = {
        "passed": "[x]",
        "skipped": "[-]",
        "in_progress": "[~]",
        "blocked": "[!]",
        "pending": "[ ]",
    }
    lines = [
        "Proyecto: " + str(data.get("name") or "replica"),
        "Fase actual: " + str(data.get("current") or "completo"),
        "",
    ]
    for phase in PHASES:
        status = data["phases"][phase]
        lines.append(marks.get(status, "[?]") + " " + phase.ljust(13) + status)
    lines.append("")
    lines.append(
        "Resumen: " + ", ".join(key + "=" + str(value) for key, value in sorted(data["counts"].items()))
    )
    return "\n".join(lines)

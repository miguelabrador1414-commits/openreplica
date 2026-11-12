"""Command line entry point for OpenReplica."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, List, Optional

from . import __version__, browser, doctor, extract, gate, state
from . import contrast, imgdiff, listing, parity, reviews, sweep
from .util import ReplkitError

FORWARD = {
    "imgdiff": imgdiff,
    "parity": parity,
    "sweep": sweep,
    "contrast": contrast,
    "reviews": reviews,
    "listing": listing,
}


def _print_json(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="replica",
        description="OpenReplica: clona un producto con evidencia y puertas de calidad.",
        epilog=(
            "Herramientas deterministicas: "
            + ", ".join(sorted(FORWARD))
            + ". Usa 'replica <herramienta> --help' para sus opciones."
        ),
    )
    parser.add_argument("--version", action="version", version="replkit " + __version__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="crea replica/ y el estado del proyecto")
    init.add_argument("path", nargs="?", default=".")
    init.add_argument("--name", help="nombre del proyecto")
    init.add_argument("--force", action="store_true", help="reemplaza el estado existente")

    status = sub.add_parser("status", help="muestra la fase actual y el estado")
    status.add_argument("--root", default=".")
    status.add_argument("--json", action="store_true")

    gate_parser = sub.add_parser("gate", help="comprueba la evidencia de una fase")
    gate_parser.add_argument("phase", choices=state.PHASES)
    gate_parser.add_argument("--root", default=".")
    gate_parser.add_argument("--json", action="store_true")

    mark = sub.add_parser("mark", help="actualiza el estado de una fase")
    mark.add_argument("phase", choices=state.PHASES)
    mark.add_argument("status", choices=state.STATUSES)
    mark.add_argument("--root", default=".")
    mark.add_argument("--notes", default=None)
    mark.add_argument("--artifact", action="append", default=None)
    mark.add_argument("--model", default=None)

    doc = sub.add_parser("doctor", help="revisa el entorno y la instalacion")
    doc.add_argument("--root", default=".")
    doc.add_argument("--json", action="store_true")

    cap = sub.add_parser("capture", help="captura una URL o un fixture local")
    cap.add_argument("url")
    cap.add_argument("--root", default=".")
    cap.add_argument("--out", help="carpeta de salida (por defecto replica/screens)")
    cap.add_argument(
        "--backend",
        choices=("auto", "stub", "playwright", "manual"),
        default="auto",
        help="auto usa playwright si esta instalado y hay --allow-network; si no, stub o manual",
    )
    cap.add_argument("--fixture", help="HTML o carpeta con index.html/styles.json/screens")
    cap.add_argument("--allow-network", action="store_true")
    cap.add_argument(
        "--viewport",
        action="append",
        default=[],
        help="nombre=1440x900 o 390x844; se puede repetir",
    )

    ext = sub.add_parser("extract", help="extrae rutas, controles, colores y fuentes de HTML")
    ext.add_argument("path")
    ext.add_argument("--json", action="store_true")

    return parser


def _cmd_init(args: argparse.Namespace) -> int:
    data = state.init(args.path, name=args.name, force=args.force)
    print("Inicializado: " + str(state.state_path(args.path)))
    print(state.render(state.summary(data)))
    return 0


def _cmd_status(args: argparse.Namespace) -> int:
    data = state.load(args.root)
    summary = state.summary(data)
    if args.json:
        _print_json(summary)
    else:
        print(state.render(summary))
    return 0


def _cmd_gate(args: argparse.Namespace) -> int:
    result = gate.run(args.phase, args.root)
    if args.json:
        _print_json(result)
    else:
        print(gate.render(result))
    return 0 if result["passed"] else 2


def _cmd_mark(args: argparse.Namespace) -> int:
    data = state.load(args.root)
    state.set_phase(
        data,
        args.phase,
        args.status,
        artifacts=args.artifact,
        notes=args.notes,
        model=args.model,
    )
    state.save(args.root, data)
    print("Fase " + args.phase + " -> " + args.status)
    print(state.render(state.summary(data)))
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    result = doctor.run(args.root)
    if args.json:
        _print_json(result)
    else:
        print(doctor.render(result))
    return 0 if result["ok"] else 1


def _cmd_capture(args: argparse.Namespace) -> int:
    views = browser.parse_viewports(args.viewport)
    out = args.out or str(Path(args.root).resolve() / "replica" / "screens")
    data = browser.capture(
        args.url,
        out,
        backend=args.backend,
        fixture=args.fixture,
        allow_network=args.allow_network,
        viewports=views,
    )
    _print_json(data)
    if data.get("backend") == "manual":
        print("Captura manual preparada en " + str(data.get("file")), file=sys.stderr)
    return 0


def _cmd_extract(args: argparse.Namespace) -> int:
    data = extract.extract(args.path)
    if args.json:
        _print_json(data)
    else:
        print(extract.render(data))
    return 0


HANDLERS = {
    "init": _cmd_init,
    "status": _cmd_status,
    "gate": _cmd_gate,
    "mark": _cmd_mark,
    "doctor": _cmd_doctor,
    "capture": _cmd_capture,
    "extract": _cmd_extract,
}


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] in FORWARD:
        return FORWARD[argv[0]].main(argv[1:])

    parser = build_parser()
    args = parser.parse_args(argv)
    handler = HANDLERS[args.command]
    try:
        return handler(args)
    except (ReplkitError, state.StateError, browser.BrowserError, extract.ExtractError) as exc:
        print("replica: " + str(exc), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("replica: cancelado", file=sys.stderr)
        return 130

"""Phase gates for OpenReplica.

A gate answers one question: does the evidence for this phase exist, is it
well formed, and does it meet the minimum quality bar? It is deliberately
deterministic. It does not judge taste or design quality.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from . import contrast, listing, parity, reviews as reviews_mod, sweep

DIFF_MIN = 70.0
DEPLOY_MIN = 80.0


def _check(name: str, passed: bool, detail: str, fix: str = "") -> Dict[str, Any]:
    return {"name": name, "passed": bool(passed), "detail": detail, "fix": fix}


def _read(root: Path, rel: str) -> str | None:
    path = root / rel
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def _file_check(root: Path, rel: str, min_chars: int = 1, label: str | None = None) -> Dict[str, Any]:
    name = label or rel
    path = root / rel
    if not path.is_file():
        return _check(name, False, "falta " + rel, "Crea " + rel + ".")
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return _check(name, False, "no se pudo leer: " + str(exc), "Revisa los permisos.")
    if "{{" in text:
        return _check(name, False, "tiene placeholders sin rellenar ({{...}})", "Rellena la plantilla.")
    if len(text.strip()) < min_chars:
        return _check(
            name,
            False,
            "contenido insuficiente (" + str(len(text.strip())) + " caracteres)",
            "Escribe al menos " + str(min_chars) + " caracteres.",
        )
    return _check(name, True, "ok")


def _load_json(root: Path, rel: str) -> tuple[Any, str | None]:
    path = root / rel
    if not path.is_file():
        return None, "falta " + rel
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except (OSError, ValueError) as exc:
        return None, "JSON invalido en " + rel + ": " + str(exc)


def _open_high_bugs(text: str) -> List[str]:
    found: List[str] = []
    blocks = re.split(r"(?m)^###\s+BUG-", text)
    for block in blocks[1:]:
        severity = re.search(r"(?im)^\s*[-*]?\s*Severity:\s*(S[1-4])", block)
        status = re.search(r"(?im)^\s*[-*]?\s*Status:\s*(.+)", block)
        if not severity or not status:
            continue
        if severity.group(1).upper() not in ("S1", "S2"):
            continue
        if not status.group(1).strip().lower().startswith("open"):
            continue
        first = block.splitlines()[0].strip() if block.splitlines() else "BUG"
        found.append(severity.group(1).upper() + " " + first[:80])
    return found


def _brand_config(brand: Dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    cfg = brand.get("sweep") if isinstance(brand.get("sweep"), dict) else brand
    avoid = [str(x) for x in (cfg.get("avoid") or []) if str(x).strip()]
    domains = [str(x) for x in (cfg.get("domains") or []) if str(x).strip()]
    colors = [str(x) for x in (cfg.get("colors") or []) if str(x).strip()]
    return avoid, domains, colors


def check_recon(root: Path) -> List[Dict[str, Any]]:
    checks = [_file_check(root, "replica/recon.md", 200, "recon.md")]
    features = root / "replica/features.csv"
    if not features.is_file():
        checks.append(
            _check("features.csv", False, "falta replica/features.csv", "Crea la matriz de caracteristicas.")
        )
        return checks
    try:
        rows = parity.load(features)
        result = parity.score(rows)
    except (parity.MatrixError, OSError, ValueError) as exc:
        checks.append(_check("features.csv", False, "no se pudo leer: " + str(exc), "Revisa el CSV."))
        return checks
    checks.append(
        _check(
            "features.csv",
            result["counted"] > 0,
            str(result["counted"]) + " features contadas",
            "Anade filas con feature, priority y clone.",
        )
    )
    checks.append(
        _check(
            "valores de la matriz",
            not result["problems"],
            str(len(result["problems"])) + " problemas",
            "Usa priority must/should/could y clone yes/partial/no/skip.",
        )
    )
    checks.append(
        _check(
            "must-haves",
            result["must_have_total"] > 0,
            str(result["must_have_total"]) + " must-haves",
            "Marca al menos una feature como must.",
        )
    )
    return checks


def check_architect(root: Path) -> List[Dict[str, Any]]:
    return [_file_check(root, "replica/architecture.md", 200, "architecture.md")]


def check_design(root: Path) -> List[Dict[str, Any]]:
    checks = [_file_check(root, "replica/design/tokens.json", 20, "tokens.json")]
    tokens, error = _load_json(root, "replica/design/tokens.json")
    if error:
        checks.append(_check("tokens.json", False, error, "Crea replica/design/tokens.json."))
        return checks
    if not isinstance(tokens, dict):
        checks.append(_check("tokens.json", False, "debe ser un objeto JSON", "Revisa el archivo."))
        return checks

    colours = contrast.colours(tokens)
    checks.append(
        _check(
            "tokens de color",
            bool(colours),
            str(len(colours)) + " colores",
            "Anade color.* con valores hex.",
        )
    )
    pairs = tokens.get("pairs") or contrast.default_pairs(colours)
    if not pairs:
        checks.append(
            _check(
                "pares de contraste",
                False,
                "sin pares que comprobar",
                "Anade pairs o tokens text/bg.",
            )
        )
        return checks
    rows = contrast.check(colours, pairs)
    failures = [row for row in rows if "error" in row or not row["aa"]]
    checks.append(
        _check(
            "WCAG AA",
            not failures,
            str(len(failures)) + " de " + str(len(rows)) + " pares fallan",
            "Ajusta los colores y ejecuta: replica contrast replica/design/tokens.json",
        )
    )
    return checks


def check_build(root: Path) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    features = root / "replica/features.csv"
    if not features.is_file():
        checks.append(_check("features.csv", False, "falta replica/features.csv", "Crea la matriz."))
    else:
        try:
            rows = parity.load(features)
        except (parity.MatrixError, OSError, ValueError) as exc:
            checks.append(_check("features.csv", False, "no se pudo leer: " + str(exc), "Revisa el CSV."))
        else:
            done = sum(1 for row in rows if row.get("clone", "").lower() in ("yes", "partial"))
            checks.append(
                _check(
                    "features implementadas",
                    done > 0,
                    str(done) + " con clone yes/partial",
                    "Marca clone=yes o partial en las features que ya funcionan.",
                )
            )

    checks.append(_file_check(root, "replica/build-log.md", 100, "build-log.md"))
    shots = root / "replica/clone-screens"
    count = len([p for p in shots.rglob("*") if p.is_file()]) if shots.is_dir() else 0
    checks.append(
        _check(
            "capturas del clon",
            count > 0,
            str(count) + " archivos",
            "Captura el clon en replica/clone-screens.",
        )
    )
    return checks


def check_backend(root: Path) -> List[Dict[str, Any]]:
    checks = [
        _file_check(root, "replica/backend.md", 100, "backend.md"),
        _file_check(root, ".env.example", 10, ".env.example"),
    ]
    text = (_read(root, "replica/backend.md") or "") + "\n" + (_read(root, ".env.example") or "")
    leaks = [token for token in ("sk_live_", "AKIA", "BEGIN PRIVATE KEY", "ghp_") if token in text]
    checks.append(
        _check(
            "sin secretos",
            not leaks,
            "limpio" if not leaks else "posibles secretos: " + ", ".join(leaks),
            "No pegues claves reales en documentacion ni en .env.example.",
        )
    )
    return checks


def check_test(root: Path) -> List[Dict[str, Any]]:
    checks = [
        _file_check(root, "replica/test-plan.md", 100, "test-plan.md"),
        _file_check(root, "replica/bugs.md", 20, "bugs.md"),
    ]
    bugs = _read(root, "replica/bugs.md") or ""
    open_high = _open_high_bugs(bugs)
    checks.append(
        _check(
            "bugs S1/S2 abiertos",
            not open_high,
            "ninguno" if not open_high else "; ".join(open_high),
            "Cierra o arregla los S1/S2 antes de avanzar.",
        )
    )
    return checks


def check_diff(root: Path) -> List[Dict[str, Any]]:
    data, error = _load_json(root, "replica/parity.json")
    if error:
        return [_check("parity.json", False, error, "Ejecuta replica parity y guarda el JSON.")]
    if not isinstance(data, dict):
        return [_check("parity.json", False, "debe ser un objeto JSON", "Revisa el archivo.")]
    overall = data.get("overall")
    if not isinstance(overall, (int, float)):
        return [_check("parity.json", False, "no tiene overall numerico", "Usa la salida de replica parity.")]
    return [
        _check(
            "parity",
            overall >= DIFF_MIN,
            "overall=" + str(overall) + " (minimo " + str(DIFF_MIN) + ")",
            "Sube la paridad antes de pasar a la siguiente fase.",
        )
    ]


def check_entrepreneur(root: Path) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    path = root / "replica/reviews.csv"
    if not path.is_file():
        checks.append(_check("reviews.csv", False, "falta replica/reviews.csv", "Recoge resenas reales."))
    else:
        try:
            rows, dropped, duplicates = reviews_mod.load_reviews(path)
        except (reviews_mod.FeedbackError, OSError, ValueError, KeyError, re.error) as exc:
            checks.append(_check("reviews.csv", False, "no se pudo leer: " + str(exc), "Revisa el CSV."))
        else:
            checks.append(
                _check(
                    "reviews.csv",
                    len(rows) > 0,
                    str(len(rows)) + " usables, " + str(dropped) + " descartadas, "
                    + str(duplicates) + " duplicadas",
                    "Cada fila necesita url y text.",
                )
            )
    checks.append(_file_check(root, "replica/feedback.md", 100, "feedback.md"))
    return checks


def check_brand(root: Path) -> List[Dict[str, Any]]:
    checks = [_file_check(root, "replica/brand.json", 20, "brand.json")]
    brand, error = _load_json(root, "replica/brand.json")
    if error:
        checks.append(_check("brand.json", False, error, "Crea replica/brand.json."))
        return checks
    if not isinstance(brand, dict):
        checks.append(_check("brand.json", False, "debe ser un objeto JSON", "Revisa el archivo."))
        return checks

    name = brand.get("name") or brand.get("brand")
    checks.append(
        _check("nombre de marca", bool(name), str(name or "sin nombre"), "Define el nombre de tu marca.")
    )
    avoid, domains, colors = _brand_config(brand)
    checks.append(
        _check(
            "reglas del sweep",
            bool(avoid or domains or colors),
            str(len(avoid)) + " nombres, " + str(len(domains)) + " dominios, "
            + str(len(colors)) + " colores",
            "Anade avoid, domains o colors a brand.json.",
        )
    )
    if avoid or domains or colors:
        hits = sweep.sweep(str(root), avoid, domains, colors)
        detail = "limpio" if not hits else str(len(hits)) + " coincidencias: " + "; ".join(
            hit["file"] + ":" + str(hit["line"]) for hit in hits[:3]
        )
        checks.append(
            _check(
                "sweep de marca",
                not hits,
                detail,
                "Elimina el nombre, dominio o colores del original; ejecuta replica sweep.",
            )
        )
    return checks


def check_launch(root: Path) -> List[Dict[str, Any]]:
    checks = [_file_check(root, "replica/listing.json", 20, "listing.json")]
    data, error = _load_json(root, "replica/listing.json")
    if error:
        checks.append(_check("listing.json", False, error, "Crea replica/listing.json."))
        return checks
    if not isinstance(data, dict):
        checks.append(_check("listing.json", False, "debe ser un objeto JSON", "Revisa el archivo."))
        return checks
    issues = listing.lint(data)
    errors = [issue for issue in issues if issue["level"] == "error"]
    warnings = [issue for issue in issues if issue["level"] == "warn"]
    checks.append(
        _check(
            "lint de ficha",
            not errors,
            str(len(errors)) + " errores, " + str(len(warnings)) + " avisos",
            "Corrige los errores; ejecuta: replica listing replica/listing.json",
        )
    )
    return checks


def check_deploy(root: Path) -> List[Dict[str, Any]]:
    checks = [_file_check(root, "replica/preflight.md", 200, "preflight.md")]
    preflight = _read(root, "replica/preflight.md") or ""
    unchecked = re.findall(r"(?m)^\s*[-*]\s*\[ \]", preflight)
    checked = re.findall(r"(?m)^\s*[-*]\s*\[[xX]\]", preflight)
    checks.append(
        _check(
            "preflight completo",
            not unchecked and bool(checked),
            str(len(checked)) + " hechos, " + str(len(unchecked)) + " pendientes",
            "Marca todas las casillas de preflight.md.",
        )
    )

    data, error = _load_json(root, "replica/parity.json")
    if error:
        checks.append(_check("parity", False, error, "Genera replica/parity.json."))
    elif not isinstance(data, dict) or not isinstance(data.get("overall"), (int, float)):
        checks.append(_check("parity", False, "sin overall numerico", "Usa la salida de replica parity."))
    else:
        overall = data["overall"]
        checks.append(
            _check(
                "parity",
                overall >= DEPLOY_MIN,
                "overall=" + str(overall) + " (minimo " + str(DEPLOY_MIN) + ")",
                "Sube la paridad antes de desplegar.",
            )
        )

    checks.extend(check_test(root))
    checks.extend(check_brand(root))
    return checks


CHECKS = {
    "recon": check_recon,
    "architect": check_architect,
    "design": check_design,
    "build": check_build,
    "backend": check_backend,
    "test": check_test,
    "diff": check_diff,
    "entrepreneur": check_entrepreneur,
    "brand": check_brand,
    "launch": check_launch,
    "deploy": check_deploy,
}


def run(phase: str, root: Path | str = ".") -> Dict[str, Any]:
    if phase not in CHECKS:
        raise ValueError("unknown phase: " + phase)
    base = Path(root).resolve()
    checks = CHECKS[phase](base)
    passed = all(check["passed"] for check in checks)
    errors = [
        {"check": check["name"], "detail": check["detail"], "fix": check["fix"]}
        for check in checks
        if not check["passed"]
    ]
    return {
        "phase": phase,
        "root": str(base),
        "passed": passed,
        "checks": checks,
        "errors": errors,
    }


def render(result: Dict[str, Any]) -> str:
    lines = [
        "Gate " + result["phase"] + ": " + ("PASA" if result["passed"] else "BLOQUEADO"),
        "",
    ]
    for check in result["checks"]:
        lines.append(("[x] " if check["passed"] else "[ ] ") + check["name"] + " - " + check["detail"])
        if not check["passed"] and check["fix"]:
            lines.append("    " + check["fix"])
    if not result["passed"]:
        lines.append("")
        lines.append("Corrige lo anterior y repite: replica gate " + result["phase"])
    return "\n".join(lines)

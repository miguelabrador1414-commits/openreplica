"""Capture backends for OpenReplica.

The default path is deterministic and offline: a stub reads a local fixture.
Real browser capture is optional and only runs when Playwright is installed
and the caller explicitly allows network access.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_VIEWPORTS = [
    {"name": "desktop", "width": 1440, "height": 900},
    {"name": "mobile", "width": 390, "height": 844},
]


class BrowserError(Exception):
    """User-facing capture error."""


class MissingDependency(BrowserError):
    """Raised when Playwright is requested but not installed."""


def _stamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def parse_viewports(values: List[str]) -> List[Dict[str, Any]]:
    if not values:
        return list(DEFAULT_VIEWPORTS)
    result: List[Dict[str, Any]] = []
    for index, raw in enumerate(values, start=1):
        name = "viewport" + str(index)
        spec = raw.strip()
        if "=" in spec:
            prefix, spec = spec.split("=", 1)
            name = prefix.strip() or name
        if "x" not in spec.lower():
            raise BrowserError("viewport invalido: " + raw + " (usa nombre=1440x900 o 390x844)")
        width_text, height_text = spec.lower().split("x", 1)
        try:
            width = int(width_text)
            height = int(height_text)
        except ValueError as exc:
            raise BrowserError("viewport invalido: " + raw) from exc
        if width <= 0 or height <= 0:
            raise BrowserError("viewport debe ser positivo: " + raw)
        result.append({"name": name, "width": width, "height": height})
    return result


class StubBackend:
    """Offline capture from a local fixture directory."""

    name = "stub"

    def __init__(self, fixture: str | Path | None):
        if not fixture:
            raise BrowserError("el backend stub necesita --fixture con un HTML o una carpeta")
        self.fixture = Path(fixture).expanduser().resolve()
        if not self.fixture.exists():
            raise BrowserError("no existe el fixture: " + str(self.fixture))

    def capture(
        self,
        url: str,
        out_dir: str | Path,
        viewports: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        out = Path(out_dir).expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)

        styles: Any = None
        screens: List[Dict[str, str]] = []
        if self.fixture.is_dir():
            html_path = self.fixture / "index.html"
            if not html_path.is_file():
                candidates = sorted(self.fixture.glob("*.html"))
                if not candidates:
                    raise BrowserError("el fixture no contiene index.html ni otro .html")
                html_path = candidates[0]
            html = html_path.read_text(encoding="utf-8", errors="replace")
            styles_path = self.fixture / "styles.json"
            if styles_path.is_file():
                try:
                    styles = json.loads(styles_path.read_text(encoding="utf-8"))
                except ValueError as exc:
                    raise BrowserError("styles.json invalido: " + str(exc)) from exc
            screens_dir = self.fixture / "screens"
            if screens_dir.is_dir():
                for source in sorted(screens_dir.glob("*.png")):
                    target = out / source.name
                    shutil.copy2(source, target)
                    screens.append({"name": source.stem, "file": str(target)})
        else:
            html = self.fixture.read_text(encoding="utf-8", errors="replace")

        payload = {
            "url": url,
            "backend": "stub",
            "captured_at": _stamp(),
            "viewports": viewports or list(DEFAULT_VIEWPORTS),
            "network": False,
            "html": html,
            "styles": styles,
            "screens": screens,
        }
        (out / "capture.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return payload


class PlaywrightBackend:
    """Optional real capture. Requires playwright and explicit network access."""

    name = "playwright"

    @staticmethod
    def available() -> bool:
        return importlib.util.find_spec("playwright") is not None

    def capture(
        self,
        url: str,
        out_dir: str | Path,
        viewports: List[Dict[str, Any]] | None = None,
        allow_network: bool = False,
    ) -> Dict[str, Any]:
        if not allow_network:
            raise BrowserError("la captura real necesita --allow-network")
        if not self.available():
            raise MissingDependency(
                "Playwright no esta instalado. Usa --backend stub o instala con: "
                "pip install playwright && playwright install chromium"
            )

        from playwright.sync_api import sync_playwright

        out = Path(out_dir).expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)
        views = viewports or list(DEFAULT_VIEWPORTS)
        screens: List[Dict[str, Any]] = []
        html = ""
        styles: Any = {}

        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                for viewport in views:
                    page = browser.new_page(
                        viewport={"width": viewport["width"], "height": viewport["height"]}
                    )
                    page.goto(url, wait_until="networkidle", timeout=45000)
                    html = page.content()
                    styles = page.evaluate(
                        """
                        () => {
                          const pick = (el) => {
                            const s = getComputedStyle(el);
                            return {
                              color: s.color,
                              backgroundColor: s.backgroundColor,
                              fontFamily: s.fontFamily,
                              fontSize: s.fontSize,
                              fontWeight: s.fontWeight,
                              lineHeight: s.lineHeight,
                              borderRadius: s.borderRadius
                            };
                          };
                          const nodes = [...document.querySelectorAll('*')].slice(0, 500);
                          return {
                            title: document.title,
                            url: location.href,
                            body: pick(document.body),
                            headings: [...document.querySelectorAll('h1,h2,h3')].slice(0, 80)
                              .map(el => ({tag: el.tagName, text: el.textContent.trim().slice(0, 160), ...pick(el)})),
                            buttons: [...document.querySelectorAll('button,a')].slice(0, 120)
                              .map(el => ({tag: el.tagName, text: el.textContent.trim().slice(0, 100), ...pick(el)})),
                            inputs: [...document.querySelectorAll('input,select,textarea')].slice(0, 120)
                              .map(el => ({tag: el.tagName, type: el.getAttribute('type'), name: el.getAttribute('name'), ...pick(el)})),
                            colors: [...new Set(nodes.map(el => getComputedStyle(el).color)
                              .concat(nodes.map(el => getComputedStyle(el).backgroundColor)))].slice(0, 160),
                            fonts: [...new Set(nodes.map(el => getComputedStyle(el).fontFamily))].slice(0, 80)
                          };
                        }
                        """
                    )
                    target = out / (str(viewport["name"]) + ".png")
                    page.screenshot(path=str(target), full_page=True)
                    screens.append(
                        {
                            "name": viewport["name"],
                            "file": str(target),
                            "width": viewport["width"],
                            "height": viewport["height"],
                        }
                    )
                    page.close()
            finally:
                browser.close()

        payload = {
            "url": url,
            "backend": "playwright",
            "captured_at": _stamp(),
            "viewports": views,
            "network": True,
            "html": html,
            "styles": styles,
            "screens": screens,
        }
        (out / "capture.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        return payload


class ManualBackend:
    """Writes a checklist when no automated backend is available."""

    name = "manual"

    def capture(
        self,
        url: str,
        out_dir: str | Path,
        viewports: List[Dict[str, Any]] | None = None,
    ) -> Dict[str, Any]:
        out = Path(out_dir).expanduser().resolve()
        out.mkdir(parents=True, exist_ok=True)
        views = viewports or list(DEFAULT_VIEWPORTS)
        lines = [
            "# Captura manual",
            "",
            "URL: " + url,
            "",
            "Playwright no esta disponible. Captura estas pantallas a mano y guarda",
            "los PNG en esta carpeta.",
            "",
        ]
        for viewport in views:
            lines.append(
                "- " + str(viewport["name"]) + ": " + str(viewport["width"]) + "x"
                + str(viewport["height"])
            )
        lines.extend(
            [
                "",
                "Para automatizar:",
                "",
                "    pip install playwright",
                "    playwright install chromium",
                "    replica capture " + url + " --backend playwright --allow-network",
                "",
            ]
        )
        manual = out / "MANUAL.md"
        manual.write_text("\n".join(lines), encoding="utf-8")
        return {
            "url": url,
            "backend": "manual",
            "manual": True,
            "file": str(manual),
            "viewports": views,
            "network": False,
        }


def capture(
    url: str,
    out_dir: str | Path,
    backend: str = "auto",
    fixture: str | Path | None = None,
    allow_network: bool = False,
    viewports: List[Dict[str, Any]] | None = None,
) -> Dict[str, Any]:
    views = viewports or list(DEFAULT_VIEWPORTS)
    if backend == "stub":
        return StubBackend(fixture).capture(url, out_dir, views)
    if backend == "manual":
        return ManualBackend().capture(url, out_dir, views)
    if backend == "playwright":
        return PlaywrightBackend().capture(url, out_dir, views, allow_network)
    if backend != "auto":
        raise BrowserError("backend desconocido: " + backend)

    if fixture:
        return StubBackend(fixture).capture(url, out_dir, views)
    if PlaywrightBackend.available() and allow_network:
        return PlaywrightBackend().capture(url, out_dir, views, allow_network)
    return ManualBackend().capture(url, out_dir, views)

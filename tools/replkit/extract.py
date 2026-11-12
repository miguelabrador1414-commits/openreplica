"""Deterministic HTML extraction for recon and design.

This is not a browser. It reads HTML and CSS text and reports what is in the
markup: routes, headings, controls, colours and fonts. It intentionally does
not execute JavaScript.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List

MAX_BYTES = 2_000_000
TAG_RE = re.compile(r"<[^>]+>")
HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3,8})\b")
RGB_RE = re.compile(r"rgba?\([^)]*\)")
FONT_RE = re.compile(r"font-family\s*:\s*([^;\"'}]+)", re.I)


class ExtractError(Exception):
    """Raised when a path cannot be extracted."""


class _Collector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: List[Dict[str, str]] = []
        self.inputs: List[Dict[str, str]] = []
        self.forms: List[Dict[str, str]] = []
        self.images: List[Dict[str, str]] = []
        self.meta: List[Dict[str, str]] = []
        self.classes: List[str] = []
        self.styles: List[str] = []
        self._in_style = False

    def handle_starttag(self, tag: str, attrs: List[tuple[str, str | None]]) -> None:
        data = {key: (value or "") for key, value in attrs}
        if tag == "a" and data.get("href"):
            self.links.append({"href": data["href"], "class": data.get("class", "")})
        elif tag == "input":
            self.inputs.append(
                {
                    "type": data.get("type", ""),
                    "name": data.get("name", ""),
                    "placeholder": data.get("placeholder", ""),
                    "class": data.get("class", ""),
                }
            )
        elif tag in ("select", "textarea"):
            self.inputs.append(
                {
                    "type": tag,
                    "name": data.get("name", ""),
                    "placeholder": data.get("placeholder", ""),
                    "class": data.get("class", ""),
                }
            )
        elif tag == "form":
            self.forms.append({"action": data.get("action", ""), "method": data.get("method", "")})
        elif tag == "img":
            self.images.append(
                {"src": data.get("src", ""), "alt": data.get("alt", ""), "class": data.get("class", "")}
            )
        elif tag == "meta":
            self.meta.append({"name": data.get("name", ""), "content": data.get("content", "")})
        if data.get("class"):
            self.classes.extend(data["class"].split())
        if data.get("style"):
            self.styles.append(data["style"])
        if tag == "style":
            self._in_style = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "style":
            self._in_style = False

    def handle_data(self, data: str) -> None:
        if self._in_style:
            self.styles.append(data)


def _uniq(values: List[str]) -> List[str]:
    seen = set()
    result = []
    for value in values:
        key = value.strip().lower()
        if key and key not in seen:
            seen.add(key)
            result.append(value.strip())
    return result


def _text(fragment: str) -> str:
    return re.sub(r"\s+", " ", TAG_RE.sub(" ", fragment)).strip()


def _items(html: str, tag: str, limit: int = 200) -> List[Dict[str, str]]:
    pattern = re.compile(r"<" + tag + r"\b([^>]*)>(.*?)</" + tag + r">", re.I | re.S)
    result = []
    for match in pattern.finditer(html):
        result.append({"tag": tag, "text": _text(match.group(2))[:200], "attrs": match.group(1).strip()[:200]})
        if len(result) >= limit:
            break
    return result


def extract_html(html: str, source: str = "") -> Dict[str, Any]:
    collector = _Collector()
    collector.feed(html)

    title_match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = _text(title_match.group(1)) if title_match else ""
    headings = []
    for level in range(1, 7):
        headings.extend(_items(html, "h" + str(level), limit=100))
    headings.sort(key=lambda item: int(item["tag"][1]))

    buttons = _items(html, "button", limit=100)
    styles = "\n".join(collector.styles)
    colours = _uniq(HEX_RE.findall(styles) + RGB_RE.findall(styles))
    fonts = _uniq(match.group(1).strip() for match in FONT_RE.finditer(styles))
    links = collector.links
    routes = _uniq(
        [
            link["href"]
            for link in links
            if link["href"].startswith("/") and not link["href"].startswith("//")
        ]
    )
    return {
        "source": source,
        "title": title,
        "headings": headings,
        "links": links[:300],
        "routes": routes,
        "buttons": buttons,
        "inputs": collector.inputs[:200],
        "forms": collector.forms,
        "images": collector.images[:200],
        "meta": collector.meta,
        "classes": _uniq(collector.classes),
        "colors": colours,
        "fonts": fonts,
        "text_sample": _text(html)[:500],
    }


def _merge(results: List[Dict[str, Any]], source: str) -> Dict[str, Any]:
    merged: Dict[str, Any] = {
        "source": source,
        "title": "",
        "headings": [],
        "links": [],
        "routes": [],
        "buttons": [],
        "inputs": [],
        "forms": [],
        "images": [],
        "meta": [],
        "classes": [],
        "colors": [],
        "fonts": [],
        "text_sample": "",
        "files": [],
    }
    for item in results:
        if not merged["title"] and item.get("title"):
            merged["title"] = item["title"]
        if not merged["text_sample"] and item.get("text_sample"):
            merged["text_sample"] = item["text_sample"]
        for key in ("headings", "links", "buttons", "inputs", "forms", "images", "meta"):
            merged[key].extend(item.get(key, []))
        for key in ("classes", "colors", "fonts", "routes"):
            merged[key].extend(item.get(key, []))
    for key in ("classes", "colors", "fonts", "routes"):
        merged[key] = _uniq(merged[key])
    merged["files"] = [item["source"] for item in results]
    return merged


def extract(path: str | Path) -> Dict[str, Any]:
    target = Path(path).expanduser().resolve()
    if not target.exists():
        raise ExtractError("no existe: " + str(target))
    if target.is_dir():
        files = sorted(
            item
            for item in target.rglob("*")
            if item.is_file() and item.suffix.lower() in (".html", ".htm")
        )
        if not files:
            raise ExtractError("no hay archivos .html en " + str(target))
        results = []
        for item in files:
            if item.stat().st_size > MAX_BYTES:
                raise ExtractError("archivo demasiado grande: " + str(item))
            results.append(
                extract_html(item.read_text(encoding="utf-8", errors="replace"), str(item.relative_to(target)))
            )
        return _merge(results, str(target))

    if target.stat().st_size > MAX_BYTES:
        raise ExtractError("archivo demasiado grande: " + str(target))
    return extract_html(target.read_text(encoding="utf-8", errors="replace"), str(target))


def render(data: Dict[str, Any]) -> str:
    lines = ["Extraccion: " + str(data.get("source")), ""]
    lines.append("Titulo: " + (data.get("title") or "(sin titulo)"))
    lines.append(
        "Elementos: "
        + str(len(data.get("headings", [])))
        + " titulos, "
        + str(len(data.get("buttons", [])))
        + " botones, "
        + str(len(data.get("inputs", [])))
        + " campos, "
        + str(len(data.get("routes", [])))
        + " rutas"
    )
    if data.get("colors"):
        lines.append("Colores: " + ", ".join(data["colors"][:20]))
    if data.get("fonts"):
        lines.append("Fuentes: " + "; ".join(data["fonts"][:10]))
    if data.get("routes"):
        lines.append("Rutas: " + ", ".join(data["routes"][:20]))
    if data.get("headings"):
        lines.append("")
        lines.append("Titulos:")
        for item in data["headings"][:20]:
            lines.append("  " + item["tag"] + " " + item["text"])
    if data.get("buttons"):
        lines.append("")
        lines.append("Botones:")
        for item in data["buttons"][:20]:
            lines.append("  " + (item["text"] or "(sin texto)"))
    return "\n".join(lines)

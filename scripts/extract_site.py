"""Extract embedded HTML apps from the SEES:4800 Google Sites course website.

Each Google Sites lecture page stores its content as a complete HTML document
inside a ``data-code`` attribute (Google Sites "Embed code" widget). This
script fetches every known page, pulls those documents out, and writes:

- ``archive/raw/<page>__<n>.html``  verbatim extracted apps (fidelity reference)
- ``docs/lecture/<module>/apps/<page>.html``  working copies served by MkDocs,
  with a small course-navigation bar injected at the top of <body>
- ``archive/inventory.json``  machine-readable report
- stdout: human-readable summary (embed titles, sizes, empty pages)

Stdlib only (urllib + html.parser); run with any Python >= 3.9:

    python scripts/extract_site.py
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

BASE = "https://sites.google.com"
SITE = "/view/enviromentalgeophysics"

# page path (after SITE) -> (module dir, app filename stem); None = wrapper-only page
PAGES: dict[str, tuple[str, str] | None] = {
    "/home": None,
    "/lecture": None,
    "/lecture/introduction-to-environmental-geophysics": ("intro", "introduction"),
    "/lecture/gravity-methods": ("gravity", "gravity-methods"),
    "/lecture/gravity-methods/activity-1": ("gravity", "activity-1"),
    "/lecture/gravity-methods/activity-2": ("gravity", "activity-2"),
    "/lecture/gravity-methods/activity-3": ("gravity", "activity-3"),
    "/lecture/magnetic-methods": ("magnetic", "magnetic-methods"),
    "/lecture/magnetic-methods/magnetic-signal": ("magnetic", "magnetic-signal"),
    "/lecture/magnetic-methods/continuation": ("magnetic", "continuation"),
    "/lecture/magnetic-methods/depth-estimation": ("magnetic", "depth-estimation"),
    "/lecture/seismic-methods": ("seismic", "seismic-methods"),
    "/lecture/seismic-methods/stress-and-strain": ("seismic", "stress-and-strain"),
    "/lecture/seismic-methods/seismic-refraction-method": ("seismic", "seismic-refraction"),
    "/lecture/electrical-methods": ("electrical", "electrical-methods"),
    "/lecture/electrical-methods/ert": ("electrical", "ert"),
    "/lecture/electrical-methods/sp": ("electrical", "sp"),
    "/lecture/electrical-methods/ip": ("electrical", "ip"),
    "/lecture/electromagnetic-methods": ("em", "electromagnetic-methods"),
    "/lecture/electromagnetic-methods/fdem-tem": ("em", "fdem-tem"),
    "/lecture/gpr": ("gpr", "gpr"),
    "/lecture/mt": ("mt", "mt"),
    "/lecture/borehole-geophysics": ("borehole", "borehole-geophysics"),
}

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")

# Injected right after <body> of each working copy. Relative paths assume the
# app lives at /lecture/<module>/apps/<name>.html: ../ is the module page,
# ../../../ is the course home (works locally and under the Pages subpath).
NAV_BAR = """
<div id="course-nav-bar" style="position:sticky;top:0;z-index:2000;display:flex;gap:1.5rem;align-items:center;padding:.45rem 1rem;background:#0b1220;border-bottom:1px solid #334155;font-family:'Segoe UI',Tahoma,sans-serif;font-size:.85rem;">
  <a href="../../../" style="color:#94a3b8;text-decoration:none;">&#8592; Course Home</a>
  <a href="../" style="color:#94a3b8;text-decoration:none;">Module Page</a>
  <span style="margin-left:auto;color:#475569;">SEES:4800 Environmental Geophysics</span>
</div>
"""


class EmbedCollector(HTMLParser):
    """Collect data-code / data-url embeds, the page <h1>, and main text."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.embeds: list[dict] = []
        self.h1_parts: list[str] = []
        self._in_h1 = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        code = a.get("data-code")
        if code:
            self.embeds.append({"kind": "code", "code": code})
        else:
            url = a.get("data-url")
            if url and "atari-embeds" not in url and url.startswith("http"):
                self.embeds.append({"kind": "url", "url": url})
        if tag == "h1":
            self._in_h1 += 1

    def handle_endtag(self, tag: str) -> None:
        if tag == "h1" and self._in_h1:
            self._in_h1 -= 1

    def handle_data(self, data: str) -> None:
        if self._in_h1:
            self.h1_parts.append(data.strip())


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def embed_title(code: str) -> str | None:
    m = re.search(r"<title>([^<]*)</title>", code, re.IGNORECASE)
    return m.group(1).strip() if m else None


def inject_nav(code: str) -> str:
    m = re.search(r"<body[^>]*>", code, re.IGNORECASE)
    if not m:
        return NAV_BAR + code
    return code[: m.end()] + NAV_BAR + code[m.end():]


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    raw_dir = root / "archive" / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    inventory: list[dict] = []
    for path, target in PAGES.items():
        url = f"{BASE}{SITE}{path}"
        page_slug = path.strip("/").replace("/", "__") or "home"
        try:
            html = fetch(url)
        except Exception as exc:  # noqa: BLE001 - report and continue
            print(f"[FAIL] {path}: {exc}")
            inventory.append({"page": path, "error": str(exc)})
            continue

        parser = EmbedCollector()
        parser.feed(html)
        entry: dict = {
            "page": path,
            "url": url,
            "h1": " ".join(p for p in parser.h1_parts if p),
            "embeds": [],
        }

        for i, emb in enumerate(parser.embeds):
            if emb["kind"] == "url":
                entry["embeds"].append({"kind": "url", "url": emb["url"]})
                print(f"[URL ] {path}: embed-by-URL -> {emb['url']}")
                continue
            code = emb["code"]
            title = embed_title(code)
            raw_path = raw_dir / f"{page_slug}__{i}.html"
            raw_path.write_text(code, encoding="utf-8")
            rec = {
                "kind": "code",
                "title": title,
                "chars": len(code),
                "raw": str(raw_path.relative_to(root)),
            }
            if target is not None:
                module, stem = target
                app_dir = root / "docs" / "lecture" / module / "apps"
                app_dir.mkdir(parents=True, exist_ok=True)
                name = stem if i == 0 else f"{stem}-{i + 1}"
                app_path = app_dir / f"{name}.html"
                app_path.write_text(inject_nav(code), encoding="utf-8")
                rec["app"] = str(app_path.relative_to(root))
            entry["embeds"].append(rec)

        inventory.append(entry)
        n = len(entry["embeds"])
        titles = "; ".join(e.get("title") or e.get("url", "?") for e in entry["embeds"])
        status = f"{n} embed(s): {titles}" if n else "EMPTY (no embeds)"
        print(f"[ OK ] {path:60s} h1={entry['h1']!r:35s} {status}")
        time.sleep(0.5)

    inv_path = root / "archive" / "inventory.json"
    inv_path.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    print(f"\nInventory written to {inv_path}")

    empty = [e["page"] for e in inventory if not e.get("embeds") and "error" not in e]
    if empty:
        print(f"Pages with no embeds ({len(empty)}): {', '.join(empty)}")
    errors = [e["page"] for e in inventory if "error" in e]
    if errors:
        print(f"Pages that FAILED ({len(errors)}): {', '.join(errors)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path
from typing import Any


API_ROOT = "https://api.github.com/repos/game-icons/icons"
RAW_ROOT = "https://raw.githubusercontent.com/game-icons/icons/master"
LICENSE_URL = "https://creativecommons.org/licenses/by/3.0/"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "dcc-mcp-free-media/0.1"}


def api(path: str) -> Any:
    headers = dict(HEADERS)
    if token := os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(API_ROOT + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def icons() -> list[dict[str, str]]:
    tree = api("/git/trees/master?recursive=1")
    if tree.get("truncated"):
        raise RuntimeError("Game Icons repository tree response was truncated")
    return [item for item in tree.get("tree") or [] if item.get("type") == "blob" and str(item.get("path", "")).endswith(".svg")]


def summary(icon_path: str) -> dict[str, str]:
    parts = icon_path.split("/")
    if len(parts) != 2 or not icon_path.endswith(".svg"):
        raise ValueError("icon_path must be an author/name.svg path returned by search_game_icons")
    author, filename = parts
    slug = filename.removesuffix(".svg")
    return {
        "icon_path": icon_path,
        "name": slug,
        "author": author,
        "format": "svg",
        "source_url": f"https://game-icons.net/1x1/{author}/{slug}.html",
        "download_url": f"{RAW_ROOT}/{icon_path}",
        "license_spdx": "CC-BY-3.0",
        "license_url": LICENSE_URL,
        "attribution_text": f"{slug} icon by {author}, available on game-icons.net under CC BY 3.0",
    }


def find(icon_path: str) -> dict[str, str]:
    normalized = icon_path.replace("\\", "/").strip("/")
    if normalized not in {item["path"] for item in icons()}:
        raise ValueError("icon_path was not found in the official Game Icons repository")
    return summary(normalized)


def download(url: str, output_dir: str, filename: str) -> str:
    target = Path(output_dir).expanduser().resolve() / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response, target.open("wb") as stream:
        stream.write(response.read())
    return str(target)

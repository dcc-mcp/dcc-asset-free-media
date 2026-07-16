from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_URL = "https://www.googleapis.com/webfonts/v1/webfonts"
GITHUB_API = "https://api.github.com/repos/google/fonts/contents"
HEADERS = {"User-Agent": "dcc-mcp-free-media/0.1"}
LICENSES = {
    "ofl": ("OFL-1.1", "OFL.txt"),
    "apache": ("Apache-2.0", "LICENSE.txt"),
    "ufl": ("UFL-1.0", "LICENCE.txt"),
}


def read_json(url: str) -> Any:
    headers = dict(HEADERS)
    if token := os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def catalog() -> list[dict[str, Any]]:
    api_key = os.environ.get("GOOGLE_FONTS_API_KEY")
    if not api_key:
        raise RuntimeError("GOOGLE_FONTS_API_KEY is required")
    data = read_json(API_URL + "?" + urllib.parse.urlencode({"key": api_key, "sort": "popularity"}))
    return data.get("items") or []


def summary(font: dict[str, Any]) -> dict[str, Any]:
    family = font["family"]
    return {
        "family": family,
        "category": font.get("category"),
        "variants": font.get("variants") or [],
        "subsets": font.get("subsets") or [],
        "version": font.get("version"),
        "last_modified": font.get("lastModified"),
        "source_url": "https://fonts.google.com/specimen/" + urllib.parse.quote_plus(family),
    }


def family_license(family: str) -> dict[str, str]:
    slug = re.sub(r"[^a-z0-9]", "", family.lower())
    for folder, (spdx, filename) in LICENSES.items():
        try:
            files = read_json(f"{GITHUB_API}/{folder}/{slug}")
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                continue
            raise
        match = next((item for item in files if item.get("name", "").lower() == filename.lower()), None)
        if match:
            return {"license_spdx": spdx, "license_url": match["download_url"], "family_path": f"{folder}/{slug}"}
    raise ValueError(f"Could not resolve the license file for Google Font family: {family}")


def download(url: str, output_dir: str, filename: str) -> str:
    target = Path(output_dir).expanduser().resolve() / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=60) as response, target.open("wb") as stream:
        stream.write(response.read())
    return str(target)

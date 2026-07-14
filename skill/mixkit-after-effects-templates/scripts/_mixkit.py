from __future__ import annotations

import html
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


LICENSE_URL = "https://mixkit.co/license/#videoTemplateFree"
LICENSE_TEXT = "Mixkit Free License for Video Templates; review the item license before use."
HEADERS = {"User-Agent": "dcc-mcp-free-media/0.1"}
ITEM_PATH = re.compile(r"^/free-after-effects-templates/[a-z0-9-]+-(\d+)/$")


def read_text(url: str) -> str:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def validated_source_url(source_url: str) -> tuple[str, str]:
    parsed = urllib.parse.urlparse(source_url)
    match = ITEM_PATH.fullmatch(parsed.path)
    if parsed.scheme != "https" or parsed.netloc.lower() != "mixkit.co" or not match:
        raise ValueError("Expected an https://mixkit.co/free-after-effects-templates/<slug>-<id>/ item URL")
    return urllib.parse.urlunparse(("https", "mixkit.co", parsed.path, "", "", "")), match.group(1)


def inspect(source_url: str) -> dict[str, Any]:
    source_url, item_id = validated_source_url(source_url)
    page = read_text(source_url)
    title_match = re.search(r'<h1[^>]*data-test-id="item-page-title"[^>]*>(.*?)</h1>', page, re.S)
    description_match = re.search(r'<p[^>]*data-test-id="item-page-description"[^>]*>(.*?)</p>', page, re.S)
    modal_match = re.search(r'data-download--button-modal-url-value="([^"]+)"', page)
    if not modal_match:
        raise RuntimeError("Mixkit free template download endpoint was not found")
    modal_url = urllib.parse.urljoin(source_url, html.unescape(modal_match.group(1)))
    modal = read_text(modal_url)
    download_match = re.search(r'data-download--modal-url-value="([^"]+)"', modal)
    if not download_match:
        raise RuntimeError("Mixkit template ZIP URL was not found")
    download_url = html.unescape(download_match.group(1))
    parsed_download = urllib.parse.urlparse(download_url)
    if parsed_download.scheme != "https" or parsed_download.netloc.lower() != "assets.mixkit.co" or not parsed_download.path.endswith(".zip"):
        raise RuntimeError("Mixkit returned an unexpected download URL")
    clean = lambda value: re.sub(r"<[^>]+>", "", html.unescape(value or "")).strip()
    return {
        "id": item_id,
        "title": clean(title_match.group(1) if title_match else f"Mixkit template {item_id}"),
        "description": clean(description_match.group(1) if description_match else ""),
        "source_url": source_url,
        "download_url": download_url,
        "license_url": LICENSE_URL,
        "license_text": LICENSE_TEXT,
    }


def download(url: str, output_dir: str, item_id: str) -> str:
    target = Path(output_dir).expanduser().resolve() / f"mixkit-after-effects-{item_id}.zip"
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as stream:
        while chunk := response.read(1024 * 1024):
            stream.write(chunk)
    return str(target)


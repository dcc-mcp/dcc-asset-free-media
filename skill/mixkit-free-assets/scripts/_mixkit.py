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


def audio_license(item_type: str) -> tuple[str, str]:
    if item_type == "music":
        return "https://mixkit.co/license/#license-music", "Mixkit Free License for Stock Music; review the current license before use."
    if item_type == "sfx":
        return "https://mixkit.co/license/#license-sfx", "Mixkit Free License for Sound Effects; review the current license before use."
    raise ValueError("item_type must be music or sfx")


def list_audio(category_url: str, limit: int = 20) -> list[dict[str, Any]]:
    parsed = urllib.parse.urlparse(category_url)
    allowed = parsed.path.startswith("/free-stock-music/") or parsed.path.startswith("/free-sound-effects/")
    if parsed.scheme != "https" or parsed.netloc.lower() != "mixkit.co" or not allowed:
        raise ValueError("Expected a Mixkit free-stock-music or free-sound-effects category URL")
    page = read_text(category_url)
    cards = page.split('<div class="item-grid__item">')[1:]
    results = []
    for card in cards:
        item_id = re.search(r'data-audio-player-item-id-value="(\d+)"', card)
        item_type = re.search(r'data-audio-player-item-type-value="(music|sfx)"', card)
        title = re.search(r'<h2 class="item-grid-card__title">\s*(.*?)\s*</h2>', card, re.S)
        modal = re.search(r'data-download--button-modal-url-value="([^"]+)"', card)
        if not (item_id and item_type and title and modal):
            continue
        author = re.search(r'<p class="item-grid-music-preview__author">\s*by\s+(.*?)\s*</p>', card, re.S)
        duration = re.search(r'data-test-id="duration">\s*(.*?)\s*</div>', card, re.S)
        license_url, license_text = audio_license(item_type.group(1))
        results.append({
            "id": int(item_id.group(1)),
            "type": item_type.group(1),
            "title": re.sub(r"<[^>]+>", "", html.unescape(title.group(1))).strip(),
            "author": re.sub(r"<[^>]+>", "", html.unescape(author.group(1))).strip() if author else None,
            "duration": duration.group(1).strip() if duration else None,
            "source_url": category_url,
            "license_url": license_url,
            "license_text": license_text,
        })
        if len(results) >= limit:
            break
    return results


def resolve_audio(item_type: str, item_id: int) -> dict[str, str]:
    license_url, license_text = audio_license(item_type)
    prefix = "free-stock-music" if item_type == "music" else "free-sound-effects"
    modal_url = f"https://mixkit.co/{prefix}/download/{int(item_id)}/?context=item+grid"
    modal = read_text(modal_url)
    match = re.search(r'data-download--modal-url-value="([^"]+)"', modal)
    if not match:
        raise RuntimeError("Mixkit audio download URL was not found")
    download_url = html.unescape(match.group(1))
    parsed = urllib.parse.urlparse(download_url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "assets.mixkit.co" or Path(parsed.path).suffix.lower() not in {".mp3", ".wav"}:
        raise RuntimeError("Mixkit returned an unexpected audio download URL")
    return {"download_url": download_url, "source_url": f"https://mixkit.co/{prefix}/", "license_url": license_url, "license_text": license_text}


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


def download(url: str, output_dir: str, filename: str) -> str:
    target = Path(output_dir).expanduser().resolve() / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as stream:
        while chunk := response.read(1024 * 1024):
            stream.write(chunk)
    return str(target)

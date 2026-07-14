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
VIDEO_ITEM_PATH = re.compile(r"^/free-stock-video/[a-z0-9-]+-(\d+)/$")


def read_text(url: str) -> str:
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def clean_html(value: str) -> str:
    return re.sub(r"<[^>]+>", "", html.unescape(value or "")).strip()


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
    return {
        "id": item_id,
        "title": clean_html(title_match.group(1) if title_match else f"Mixkit template {item_id}"),
        "description": clean_html(description_match.group(1) if description_match else ""),
        "source_url": source_url,
        "download_url": download_url,
        "license_url": LICENSE_URL,
        "license_text": LICENSE_TEXT,
    }


def inspect_video(source_url: str) -> dict[str, Any]:
    parsed = urllib.parse.urlparse(source_url)
    match = VIDEO_ITEM_PATH.fullmatch(parsed.path)
    if parsed.scheme != "https" or parsed.netloc.lower() != "mixkit.co" or not match:
        raise ValueError("Expected an https://mixkit.co/free-stock-video/<slug>-<id>/ item URL")
    source_url = urllib.parse.urlunparse(("https", "mixkit.co", parsed.path, "", "", ""))
    page = read_text(source_url)
    if 'data-license="videoFree"' not in page or "Mixkit Stock Video Free License" not in page:
        raise ValueError("The selected video is not offered under the Mixkit Stock Video Free License")
    title_match = re.search(r'<h1[^>]*data-test-id="item-page-title"[^>]*>(.*?)</h1>', page, re.S)
    options = []
    for input_tag in re.findall(r'<input[^>]+data-download--video-options-target="downloadOption"[^>]*>', page, re.S):
        endpoint = re.search(r'value="([^"]+)"', input_tag)
        label = re.search(r'data-label="([^"]+)"', input_tag)
        size = re.search(r'data-size="([^"]+)"', input_tag)
        if not endpoint:
            continue
        endpoint_url = urllib.parse.urljoin(source_url, html.unescape(endpoint.group(1)))
        endpoint_parsed = urllib.parse.urlparse(endpoint_url)
        query = urllib.parse.parse_qs(endpoint_parsed.query)
        resolution = query.get("type", [""])[0]
        if endpoint_parsed.netloc.lower() != "mixkit.co" or endpoint_parsed.path != f"/free-stock-video/download/{match.group(1)}/" or not resolution:
            raise RuntimeError("Mixkit returned an unexpected stock video endpoint")
        options.append({
            "resolution": resolution,
            "label": html.unescape(label.group(1)) if label else resolution,
            "size_mb": float(size.group(1)) if size else None,
            "endpoint_url": endpoint_url,
        })
    if not options:
        raise RuntimeError("Mixkit stock video download options were not found")
    return {
        "id": match.group(1),
        "title": clean_html(title_match.group(1) if title_match else f"Mixkit stock video {match.group(1)}"),
        "source_url": source_url,
        "license_url": "https://mixkit.co/license/#videoFree",
        "license_text": "Mixkit Stock Video Free License; commercial and personal use allowed under the current license.",
        "options": options,
    }


def resolve_video(video: dict[str, Any], resolution: str) -> str:
    option = next((item for item in video["options"] if item["resolution"] == resolution), None)
    if option is None:
        available = ", ".join(item["resolution"] for item in video["options"])
        raise ValueError(f"Resolution {resolution!r} is unavailable; choose one of: {available}")
    modal = read_text(option["endpoint_url"])
    match = re.search(r'data-download--modal-url-value="([^"]+)"', modal)
    if not match:
        raise RuntimeError("Mixkit stock video download URL was not found")
    download_url = html.unescape(match.group(1))
    parsed = urllib.parse.urlparse(download_url)
    if parsed.scheme != "https" or parsed.netloc.lower() != "assets.mixkit.co" or Path(parsed.path).suffix.lower() != ".mp4":
        raise RuntimeError("Mixkit returned an unexpected stock video download URL")
    return download_url


def download(url: str, output_dir: str, filename: str) -> str:
    target = Path(output_dir).expanduser().resolve() / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as stream:
        while chunk := response.read(1024 * 1024):
            stream.write(chunk)
    return str(target)

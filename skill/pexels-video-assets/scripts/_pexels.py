from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_URL = "https://api.pexels.com/v1"
LICENSE_URL = "https://www.pexels.com/license/"
LICENSE_TEXT = "Pexels License; review the source license for current permitted and prohibited uses."
HEADERS = {"User-Agent": "dcc-mcp-free-media/0.1"}


def api(path: str, params: dict[str, Any] | None = None) -> Any:
    api_key = os.environ.get("PEXELS_API_KEY")
    if not api_key:
        raise RuntimeError("PEXELS_API_KEY is required")
    url = API_URL + path
    if params:
        url += "?" + urllib.parse.urlencode({key: value for key, value in params.items() if value is not None})
    request = urllib.request.Request(url, headers={**HEADERS, "Authorization": api_key})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def download(url: str, output_dir: str, filename: str) -> str:
    target = Path(output_dir).expanduser().resolve() / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(request, timeout=180) as response, target.open("wb") as stream:
        while chunk := response.read(1024 * 1024):
            stream.write(chunk)
    return str(target)


def video_summary(video: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": video.get("id"),
        "width": video.get("width"),
        "height": video.get("height"),
        "duration": video.get("duration"),
        "image": video.get("image"),
        "source_url": video.get("url"),
        "author": (video.get("user") or {}).get("name"),
        "license_url": LICENSE_URL,
        "license_text": LICENSE_TEXT,
        "files": [
            {
                "id": item.get("id"),
                "quality": item.get("quality"),
                "file_type": item.get("file_type"),
                "width": item.get("width"),
                "height": item.get("height"),
                "fps": item.get("fps"),
            }
            for item in video.get("video_files") or []
        ],
    }


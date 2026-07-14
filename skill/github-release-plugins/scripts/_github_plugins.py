from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any


API_URL = "https://api.github.com"
REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def api(path: str) -> Any:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "dcc-mcp-free-media/0.1", "X-GitHub-Api-Version": "2022-11-28"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    with urllib.request.urlopen(urllib.request.Request(API_URL + path, headers=headers), timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def inspect(repository: str) -> dict[str, Any]:
    if not REPOSITORY.fullmatch(repository):
        raise ValueError("repository must be GitHub owner/name")
    repo = api(f"/repos/{repository}")
    license_spdx = (repo.get("license") or {}).get("spdx_id")
    if not license_spdx or license_spdx in {"NOASSERTION", "OTHER"}:
        raise RuntimeError("Repository must declare a recognized SPDX open-source license")
    release = api(f"/repos/{repository}/releases/latest")
    return {
        "repository": repository,
        "description": repo.get("description"),
        "topics": repo.get("topics") or [],
        "license_spdx": license_spdx,
        "source_url": release["html_url"],
        "version": release["tag_name"],
        "published_at": release.get("published_at"),
        "assets": [{"id": item["id"], "name": item["name"], "size": item["size"], "download_count": item.get("download_count"), "source_url": item["browser_download_url"]} for item in release.get("assets") or []],
    }


def download_asset(url: str, output_dir: str, name: str) -> tuple[str, str, int]:
    target = Path(output_dir).expanduser().resolve() / Path(name).name
    target.parent.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    size = 0
    request = urllib.request.Request(url, headers={"User-Agent": "dcc-mcp-free-media/0.1"})
    with urllib.request.urlopen(request, timeout=300) as response, target.open("wb") as stream:
        while chunk := response.read(1024 * 1024):
            stream.write(chunk)
            digest.update(chunk)
            size += len(chunk)
    return str(target), digest.hexdigest(), size

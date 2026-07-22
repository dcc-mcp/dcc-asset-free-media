from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


API_URL = "https://www.googleapis.com/webfonts/v1/webfonts"
GITHUB_API = "https://api.github.com/repos/google/fonts/contents"
HEADERS = {"User-Agent": "dcc-mcp-free-media/0.1"}
NOTO_CJK_REVISION = "523d033d6cb47f4a80c58a35753646f5c3608a78"
NOTO_CJK_RAW = f"https://raw.githubusercontent.com/notofonts/noto-cjk/{NOTO_CJK_REVISION}"
CURATED_FONTS = {
    ("Noto Sans SC", "regular"): {
        "family": "Noto Sans SC",
        "category": "sans-serif",
        "variants": ["regular"],
        "subsets": ["chinese-simplified", "latin"],
        "version": NOTO_CJK_REVISION,
        "file_url": f"{NOTO_CJK_RAW}/Sans/SubsetOTF/SC/NotoSansSC-Regular.otf",
        "sha256": "faa6c9df652116dde789d351359f3d7e5d2285a2b2a1f04a2d7244df706d5ea9",
        "size_bytes": 8_331_336,
        "license_spdx": "OFL-1.1",
        "license_url": f"{NOTO_CJK_RAW}/LICENSE",
        "license_sha256": "6a73f9541c2de74158c0e7cf6b0a58ef774f5a780bf191f2d7ec9cc53efe2bf2",
        "license_size_bytes": 4_301,
    },
}
LICENSES = {
    "ofl": ("OFL-1.1", "OFL.txt"),
    "apache": ("Apache-2.0", "LICENSE.txt"),
    "ufl": ("UFL-1.0", "LICENCE.txt"),
}


def curated_font(family: str, variant: str) -> dict[str, Any]:
    try:
        return dict(CURATED_FONTS[(family, variant)])
    except KeyError as exc:
        raise ValueError(
            "Without GOOGLE_FONTS_API_KEY, family and variant must exactly match "
            "a curated entry: Noto Sans SC / regular"
        ) from exc


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


def download(
    url: str,
    output_dir: str,
    filename: str,
    *,
    expected_sha256: str | None = None,
    expected_size: int | None = None,
) -> tuple[str, str, int]:
    if urllib.parse.urlparse(url).scheme != "https":
        raise ValueError("Google Font downloads require HTTPS")
    target = Path(output_dir).expanduser().resolve() / filename
    target.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(url, headers=HEADERS)
    temporary: Path | None = None
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            if urllib.parse.urlparse(response.geturl()).scheme != "https":
                raise RuntimeError("Google Font download redirected away from HTTPS")
            digest = hashlib.sha256()
            size = 0
            with tempfile.NamedTemporaryFile(
                "wb", dir=target.parent, prefix=f".{target.name}.", delete=False
            ) as stream:
                temporary = Path(stream.name)
                while chunk := response.read(1024 * 1024):
                    stream.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
        sha256 = digest.hexdigest()
        if expected_size is not None and size != expected_size:
            raise RuntimeError(f"Downloaded size mismatch: expected {expected_size}, got {size}")
        if expected_sha256 is not None and sha256 != expected_sha256:
            raise RuntimeError(f"Downloaded SHA-256 mismatch: expected {expected_sha256}, got {sha256}")
        os.replace(temporary, target)
        temporary = None
        return str(target), sha256, size
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

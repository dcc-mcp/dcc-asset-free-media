from __future__ import annotations

import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dcc_mcp_core.asset_import import AssetAttribution, AssetDescriptor, AssetFileVariant
from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _google_fonts import catalog, download, family_license, summary


def descriptor(font: dict[str, Any], variant: str, local_path: str, license_path: str, license_spdx: str) -> dict[str, Any]:
    info = summary(font)
    value = AssetDescriptor(
        asset_id=f"google-fonts:{re.sub(r'[^a-z0-9]+', '-', font['family'].lower()).strip('-')}:{variant}",
        variants=[AssetFileVariant(local_path=local_path, format=Path(local_path).suffix.lstrip("."), preferred=True)],
        attribution=AssetAttribution(source_url=info["source_url"], license_spdx=license_spdx),
        extra={"family": font["family"], "variant": variant, "license_path": license_path},
    )
    value.validate()
    return value.to_dict()


@skill_entry
def main(family: str, output_dir: str, variant: str = "regular", **_: Any) -> dict[str, Any]:
    try:
        font = next((item for item in catalog() if item["family"].casefold() == family.casefold()), None)
        if not font:
            raise ValueError(f"Google Font family not found: {family}")
        file_url = (font.get("files") or {}).get(variant)
        if not file_url:
            raise ValueError(f"Variant {variant!r} is unavailable; choose one of: {', '.join(font.get('variants') or [])}")
        license_info = family_license(font["family"])
        suffix = Path(urlparse(file_url).path).suffix or ".ttf"
        stem = re.sub(r"[^A-Za-z0-9._-]+", "-", font["family"]).strip("-")
        local_path = download(file_url, output_dir, f"{stem}-{variant}{suffix}")
        license_path = download(license_info["license_url"], output_dir, f"{stem}-LICENSE.txt")
        return skill_success(
            "Google Font downloaded",
            files=[local_path, license_path],
            source_url=summary(font)["source_url"],
            asset_descriptor=descriptor(font, variant, local_path, license_path, license_info["license_spdx"]),
        )
    except Exception as exc:
        return skill_exception(exc, message="Failed to download Google Font")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)

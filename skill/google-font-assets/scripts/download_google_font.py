from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dcc_mcp_core.asset_import import AssetAttribution, AssetDescriptor, AssetFileVariant
from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _google_fonts import catalog, curated_font, download, family_license, summary


def descriptor(
    font: dict[str, Any],
    variant: str,
    local_path: str,
    license_path: str,
    provenance: dict[str, Any],
) -> dict[str, Any]:
    value = AssetDescriptor(
        asset_id=f"google-fonts:{re.sub(r'[^a-z0-9]+', '-', font['family'].lower()).strip('-')}:{variant}",
        variants=[
            AssetFileVariant(local_path=local_path, format=Path(local_path).suffix.lstrip("."), preferred=True)
        ],
        attribution=AssetAttribution(source_url=provenance["source_url"], license_spdx=provenance["license_spdx"]),
        extra={
            "family": font["family"],
            "variant": variant,
            "license_path": license_path,
            **{key: value for key, value in provenance.items() if key not in {"source_url", "license_spdx"}},
        },
    )
    value.validate()
    return value.to_dict()


@skill_entry
def main(family: str, output_dir: str, variant: str = "regular", **_: Any) -> dict[str, Any]:
    try:
        curated = None
        if os.environ.get("GOOGLE_FONTS_API_KEY"):
            font = next((item for item in catalog() if item["family"].casefold() == family.casefold()), None)
            if not font:
                raise ValueError(f"Google Font family not found: {family}")
            file_url = (font.get("files") or {}).get(variant)
            if not file_url:
                raise ValueError(f"Variant {variant!r} is unavailable; choose one of: {', '.join(font.get('variants') or [])}")
            license_info = family_license(font["family"])
        else:
            curated = curated_font(family, variant)
            font = curated
            file_url = curated["file_url"]
            license_info = curated
        suffix = Path(urlparse(file_url).path).suffix or ".ttf"
        stem = re.sub(r"[^A-Za-z0-9._-]+", "-", font["family"]).strip("-")
        local_path, sha256, size_bytes = download(
            file_url,
            output_dir,
            f"{stem}-{variant}{suffix}",
            expected_sha256=None if curated is None else curated["sha256"],
            expected_size=None if curated is None else curated["size_bytes"],
        )
        license_path, license_sha256, license_size_bytes = download(
            license_info["license_url"],
            output_dir,
            f"{stem}-LICENSE.txt",
            expected_sha256=None if curated is None else curated["license_sha256"],
            expected_size=None if curated is None else curated["license_size_bytes"],
        )
        source_url = file_url if curated else summary(font)["source_url"]
        provenance = {
            "source_url": source_url,
            "sha256": sha256,
            "size_bytes": size_bytes,
            "license_spdx": license_info["license_spdx"],
            "license_url": license_info["license_url"],
            "license_sha256": license_sha256,
            "license_size_bytes": license_size_bytes,
        }
        if curated:
            provenance["source_revision"] = curated["version"]
        return skill_success(
            "Google Font downloaded",
            files=[local_path, license_path],
            source_url=source_url,
            asset_descriptor=descriptor(
                font,
                variant,
                local_path,
                license_path,
                provenance,
            ),
        )
    except Exception as exc:
        return skill_exception(exc, message="Failed to download Google Font")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)

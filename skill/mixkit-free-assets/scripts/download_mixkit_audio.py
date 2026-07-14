from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dcc_mcp_core.asset_import import AssetAttribution, AssetDescriptor, AssetFileVariant
from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _mixkit import download, resolve_audio


def descriptor(item_type: str, item_id: int, title: str | None, author: str | None, metadata: dict[str, str], local_path: str) -> dict[str, Any]:
    value = AssetDescriptor(
        asset_id=f"mixkit:{item_type}-{item_id}",
        variants=[AssetFileVariant(local_path=local_path, format=Path(local_path).suffix.lstrip("."), preferred=True)],
        attribution=AssetAttribution(
            source_url=metadata["source_url"],
            license_text=metadata["license_text"],
            author=author,
            attribution_text=f"{title or f'Mixkit {item_type} {item_id}'} from Mixkit",
        ),
        extra={"license_url": metadata["license_url"], "title": title, "item_type": item_type},
    )
    value.validate()
    return value.to_dict()


@skill_entry
def main(item_type: str, item_id: int, output_dir: str, title: str | None = None, author: str | None = None, **_: Any) -> dict[str, Any]:
    try:
        metadata = resolve_audio(item_type, item_id)
        suffix = Path(urlparse(metadata["download_url"]).path).suffix
        local_path = download(metadata["download_url"], output_dir, f"mixkit-{item_type}-{item_id}{suffix}")
        return skill_success(
            "Mixkit audio downloaded",
            files=[local_path],
            source_url=metadata["source_url"],
            license_url=metadata["license_url"],
            asset_descriptor=descriptor(item_type, item_id, title, author, metadata, local_path),
        )
    except Exception as exc:
        return skill_exception(exc, message="Failed to download Mixkit audio")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)

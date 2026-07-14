from __future__ import annotations

from pathlib import Path
from typing import Any

from dcc_mcp_core.asset_import import AssetAttribution, AssetDescriptor, AssetFileVariant
from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _mixkit import download, inspect_video, resolve_video


def descriptor(video: dict[str, Any], local_path: str, resolution: str) -> dict[str, Any]:
    value = AssetDescriptor(
        asset_id=f"mixkit:stock-video-{video['id']}",
        variants=[AssetFileVariant(local_path=local_path, format="mp4", preferred=True)],
        attribution=AssetAttribution(
            source_url=video["source_url"],
            license_text=video["license_text"],
            attribution_text=f"{video['title']} from Mixkit",
        ),
        extra={"license_url": video["license_url"], "title": video["title"], "resolution": resolution},
    )
    value.validate()
    return value.to_dict()


@skill_entry
def main(source_url: str, resolution: str, output_dir: str, **_: Any) -> dict[str, Any]:
    try:
        video = inspect_video(source_url)
        download_url = resolve_video(video, resolution)
        filename = f"mixkit-stock-video-{video['id']}-{resolution}.mp4"
        local_path = download(download_url, output_dir, filename)
        return skill_success(
            "Mixkit stock video downloaded",
            files=[local_path],
            local_path=local_path,
            size_bytes=Path(local_path).stat().st_size,
            source_url=video["source_url"],
            license_url=video["license_url"],
            asset_descriptor=descriptor(video, local_path, resolution),
        )
    except Exception as exc:
        return skill_exception(exc, message="Failed to download Mixkit stock video")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)

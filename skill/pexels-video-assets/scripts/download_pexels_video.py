from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from dcc_mcp_core.asset_import import AssetAttribution, AssetDescriptor, AssetFileVariant
from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success

from _pexels import LICENSE_TEXT, LICENSE_URL, api, download


def select_file(files: list[dict[str, Any]], max_width: int) -> dict[str, Any] | None:
    usable = [item for item in files if item.get("link") and item.get("width")]
    within_limit = [item for item in usable if int(item["width"]) <= max_width]
    candidates = within_limit or usable
    return max(candidates, key=lambda item: int(item.get("width") or 0), default=None)


def descriptor(video: dict[str, Any], local_path: str) -> dict[str, Any]:
    author = (video.get("user") or {}).get("name")
    value = AssetDescriptor(
        asset_id=f"pexels:video-{video['id']}",
        variants=[AssetFileVariant(local_path=local_path, format=Path(local_path).suffix.lstrip(".") or "mp4", preferred=True)],
        attribution=AssetAttribution(
            source_url=video["url"],
            license_text=LICENSE_TEXT,
            author=author,
            attribution_text=f"Video by {author} on Pexels" if author else "Video from Pexels",
        ),
        extra={"license_url": LICENSE_URL},
    )
    value.validate()
    return value.to_dict()


@skill_entry
def main(video_id: int, output_dir: str, max_width: int = 1920, **_: Any) -> dict[str, Any]:
    try:
        video = api(f"/videos/videos/{int(video_id)}")
        selected = select_file(video.get("video_files") or [], max_width)
        if not selected:
            return skill_error("Pexels video has no downloadable files", str(video_id), raw=video)
        suffix = Path(urlparse(selected["link"]).path).suffix or ".mp4"
        local_path = download(selected["link"], output_dir, f"pexels-{video_id}-{selected.get('id', 'video')}{suffix}")
        return skill_success(
            "Pexels video downloaded",
            files=[local_path],
            source_url=video["url"],
            license_url=LICENSE_URL,
            asset_descriptor=descriptor(video, local_path),
        )
    except Exception as exc:
        return skill_exception(exc, message="Failed to download Pexels video")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)


from __future__ import annotations

from pathlib import Path
from typing import Any

from dcc_mcp_core.asset_import import AssetAttribution, AssetDescriptor, AssetFileVariant
from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _game_icons import download, find


def descriptor(icon: dict[str, str], local_path: str) -> dict[str, Any]:
    value = AssetDescriptor(
        asset_id=f"game-icons:{icon['icon_path'].removesuffix('.svg')}",
        variants=[AssetFileVariant(local_path=local_path, format="svg", preferred=True)],
        attribution=AssetAttribution(
            source_url=icon["source_url"],
            license_spdx=icon["license_spdx"],
            author=icon["author"],
            attribution_text=icon["attribution_text"],
        ),
        extra={"license_url": icon["license_url"]},
    )
    value.validate()
    return value.to_dict()


@skill_entry
def main(icon_path: str, output_dir: str, **_: Any) -> dict[str, Any]:
    try:
        icon = find(icon_path)
        local_path = download(icon["download_url"], output_dir, Path(icon_path).name)
        return skill_success(
            "Game icon downloaded",
            files=[local_path],
            source_url=icon["source_url"],
            asset_descriptor=descriptor(icon, local_path),
        )
    except Exception as exc:
        return skill_exception(exc, message="Failed to download Game Icon")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)

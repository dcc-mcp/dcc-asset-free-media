from __future__ import annotations

from typing import Any

from dcc_mcp_core.skill import skill_entry, skill_error, skill_exception, skill_success

from _github_plugins import download_asset, inspect


@skill_entry
def main(repository: str, asset_id: int, output_dir: str, **_: Any) -> dict[str, Any]:
    try:
        release = inspect(repository)
        asset = next((item for item in release["assets"] if item["id"] == int(asset_id)), None)
        if not asset:
            return skill_error("Release asset not found", str(asset_id), raw=release)
        local_path, sha256, size = download_asset(asset["source_url"], output_dir, asset["name"])
        package = {
            "repository": repository,
            "version": release["version"],
            "local_path": local_path,
            "source_url": asset["source_url"],
            "release_url": release["source_url"],
            "license_spdx": release["license_spdx"],
            "sha256": sha256,
            "size": size,
        }
        return skill_success("GitHub plugin release asset downloaded", files=[local_path], plugin_package=package)
    except Exception as exc:
        return skill_exception(exc, message="Failed to download GitHub plugin release asset")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)

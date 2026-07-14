from __future__ import annotations

from typing import Any

from dcc_mcp_core.asset_import import AssetAttribution, AssetDescriptor, AssetFileVariant
from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _mixkit import download, inspect


def descriptor(template: dict[str, Any], local_path: str) -> dict[str, Any]:
    value = AssetDescriptor(
        asset_id=f"mixkit:after-effects-{template['id']}",
        variants=[AssetFileVariant(local_path=local_path, format="zip", preferred=True)],
        attribution=AssetAttribution(
            source_url=template["source_url"],
            license_text=template["license_text"],
            attribution_text=f"{template['title']} from Mixkit",
        ),
        extra={"license_url": template["license_url"], "title": template["title"]},
    )
    value.validate()
    return value.to_dict()


@skill_entry
def main(source_url: str, output_dir: str, **_: Any) -> dict[str, Any]:
    try:
        template = inspect(source_url)
        local_path = download(template["download_url"], output_dir, template["id"])
        return skill_success(
            "Mixkit After Effects template downloaded",
            files=[local_path],
            source_url=template["source_url"],
            license_url=template["license_url"],
            asset_descriptor=descriptor(template, local_path),
        )
    except Exception as exc:
        return skill_exception(exc, message="Failed to download Mixkit After Effects template")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)


from __future__ import annotations

from typing import Any

from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _pexels import api, video_summary


@skill_entry
def main(
    query: str,
    orientation: str | None = None,
    size: str | None = None,
    limit: int = 10,
    **_: Any,
) -> dict[str, Any]:
    try:
        data = api(
            "/videos/search",
            {"query": query, "orientation": orientation, "size": size, "per_page": limit},
        )
        return skill_success(
            "Pexels videos found",
            videos=[video_summary(video) for video in data.get("videos") or []],
            source_url=data.get("url") or "https://www.pexels.com/videos/",
        )
    except Exception as exc:
        return skill_exception(exc, message="Failed to search Pexels videos")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)


from __future__ import annotations

from typing import Any

from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _mixkit import list_audio


@skill_entry
def main(category_url: str, limit: int = 20, **_: Any) -> dict[str, Any]:
    try:
        return skill_success("Mixkit audio listed", items=list_audio(category_url, limit))
    except Exception as exc:
        return skill_exception(exc, message="Failed to list Mixkit audio")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)

from __future__ import annotations

from typing import Any

from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _game_icons import icons, summary


@skill_entry
def main(query: str, limit: int = 20, **_: Any) -> dict[str, Any]:
    try:
        terms = query.lower().replace("_", "-").split()
        matches = [item["path"] for item in icons() if all(term in item["path"].lower() for term in terms)]
        return skill_success("Game icons found", icons=[summary(path) for path in matches[:limit]])
    except Exception as exc:
        return skill_exception(exc, message="Failed to search Game Icons")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)

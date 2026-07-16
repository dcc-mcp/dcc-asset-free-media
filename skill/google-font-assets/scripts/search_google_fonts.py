from __future__ import annotations

from typing import Any

from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _google_fonts import catalog, summary


@skill_entry
def main(query: str = "", category: str | None = None, subset: str | None = None, limit: int = 20, **_: Any) -> dict[str, Any]:
    try:
        query = query.casefold().strip()
        matches = [
            font for font in catalog()
            if (not query or query in font["family"].casefold())
            and (not category or font.get("category") == category)
            and (not subset or subset in (font.get("subsets") or []))
        ]
        return skill_success("Google Fonts found", fonts=[summary(font) for font in matches[:limit]])
    except Exception as exc:
        return skill_exception(exc, message="Failed to search Google Fonts")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)

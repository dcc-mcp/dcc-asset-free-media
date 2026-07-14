from __future__ import annotations

from typing import Any

from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _mixkit import inspect


@skill_entry
def main(source_url: str, **_: Any) -> dict[str, Any]:
    try:
        return skill_success("Mixkit After Effects template inspected", template=inspect(source_url))
    except Exception as exc:
        return skill_exception(exc, message="Failed to inspect Mixkit After Effects template")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)


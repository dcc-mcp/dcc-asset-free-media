from __future__ import annotations

from typing import Any

from dcc_mcp_core.skill import skill_entry, skill_exception, skill_success

from _github_plugins import inspect


@skill_entry
def main(repository: str, **_: Any) -> dict[str, Any]:
    try:
        return skill_success("GitHub plugin release inspected", release=inspect(repository))
    except Exception as exc:
        return skill_exception(exc, message="Failed to inspect GitHub plugin release")


if __name__ == "__main__":
    from dcc_mcp_core.skill import run_main

    run_main(main)

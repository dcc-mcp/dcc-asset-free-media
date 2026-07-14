from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(skill: str, name: str):
    scripts = ROOT / "skill" / skill / "scripts"
    sys.path.insert(0, str(scripts))
    spec = importlib.util.spec_from_file_location(f"{skill}_{name}", scripts / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def validate_skills() -> None:
    from dcc_mcp_core import validate_skill

    for name in ("pexels-video-assets", "mixkit-after-effects-templates"):
        report = validate_skill(str(ROOT / "skill" / name))
        assert not report.has_errors, report


def pexels_smoke() -> None:
    module = load("pexels-video-assets", "download_pexels_video")
    files = [
        {"id": 1, "width": 1280, "link": "https://videos.pexels.com/a.mp4"},
        {"id": 2, "width": 1920, "link": "https://videos.pexels.com/b.mp4"},
        {"id": 3, "width": 3840, "link": "https://videos.pexels.com/c.mp4"},
    ]
    assert module.select_file(files, 1920)["id"] == 2
    video = {"id": 42, "url": "https://www.pexels.com/video/42/", "user": {"name": "Creator"}}
    value = module.descriptor(video, "/tmp/pexels-42.mp4")
    assert value["asset_id"] == "pexels:video-42"
    assert value["attribution"]["author"] == "Creator"


def mixkit_smoke() -> None:
    helper = load("mixkit-after-effects-templates", "_mixkit")
    page = '''<h1 data-test-id="item-page-title">Pixel Frame Intro</h1>
    <p data-test-id="item-page-description">A pixelated intro.</p>
    <button data-download--button-modal-url-value="/free-after-effects-templates/download/615/"></button>'''
    modal = '<div data-download--modal-url-value="https://assets.mixkit.co/video-templates/615/mixkit-615.zip"></div>'
    with patch.object(helper, "read_text", side_effect=[page, modal]):
        template = helper.inspect("https://mixkit.co/free-after-effects-templates/pixel-frame-intro-615/")
    assert template["id"] == "615"
    assert template["title"] == "Pixel Frame Intro"
    downloader = load("mixkit-after-effects-templates", "download_mixkit_after_effects_template")
    value = downloader.descriptor(template, "/tmp/mixkit-615.zip")
    assert value["asset_id"] == "mixkit:after-effects-615"
    assert value["attribution"]["license_text"]


def main() -> None:
    validate_skills()
    pexels_smoke()
    mixkit_smoke()


if __name__ == "__main__":
    main()


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

    for name in (
        "pexels-video-assets",
        "mixkit-free-assets",
        "github-release-plugins",
        "game-icons-assets",
        "google-font-assets",
    ):
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
    helper = load("mixkit-free-assets", "_mixkit")
    page = '''<h1 data-test-id="item-page-title">Pixel Frame Intro</h1>
    <p data-test-id="item-page-description">A pixelated intro.</p>
    <button data-download--button-modal-url-value="/free-after-effects-templates/download/615/"></button>'''
    modal = '<div data-download--modal-url-value="https://assets.mixkit.co/video-templates/615/mixkit-615.zip"></div>'
    with patch.object(helper, "read_text", side_effect=[page, modal]):
        template = helper.inspect("https://mixkit.co/free-after-effects-templates/pixel-frame-intro-615/")
    assert template["id"] == "615"
    assert template["title"] == "Pixel Frame Intro"
    downloader = load("mixkit-free-assets", "download_mixkit_after_effects_template")
    value = downloader.descriptor(template, "/tmp/mixkit-615.zip")
    assert value["asset_id"] == "mixkit:after-effects-615"
    assert value["attribution"]["license_text"]

    audio_page = '''<div class="item-grid__item"><div data-audio-player-item-id-value="738" data-audio-player-item-type-value="music"></div><h2 class="item-grid-card__title">Hip Hop 02</h2><p class="item-grid-music-preview__author">by Lily J</p><div data-test-id="duration">1:55</div><button data-download--button-modal-url-value="/free-stock-music/download/738/"></button></div>'''
    with patch.object(helper, "read_text", return_value=audio_page):
        items = helper.list_audio("https://mixkit.co/free-stock-music/", 1)
    assert items[0]["id"] == 738
    assert items[0]["author"] == "Lily J"

    video_page = '''<h1 data-test-id="item-page-title">Programmer working with codes</h1>
    <a data-license="videoFree">Mixkit Stock Video Free License</a>
    <input data-download--video-options-target="downloadOption" data-label="Full HD" data-size="33.32" value="/free-stock-video/download/41637/?context=sidebar&amp;type=1080p">'''
    video_modal = '<div data-download--modal-url-value="https://assets.mixkit.co/videos/41637/41637-1080.mp4"></div>'
    with patch.object(helper, "read_text", return_value=video_page):
        video = helper.inspect_video("https://mixkit.co/free-stock-video/programmer-working-with-codes-on-a-computer-41637/")
    assert video["options"][0]["resolution"] == "1080p"
    with patch.object(helper, "read_text", return_value=video_modal):
        assert helper.resolve_video(video, "1080p").endswith("41637-1080.mp4")
    restricted_page = video_page.replace('data-license="videoFree"', 'data-license="videoRestricted"')
    with patch.object(helper, "read_text", return_value=restricted_page):
        try:
            helper.inspect_video("https://mixkit.co/free-stock-video/programmer-working-with-codes-on-a-computer-41637/")
        except ValueError as exc:
            assert "not offered" in str(exc)
        else:
            raise AssertionError("Restricted-license stock video must be rejected")


def github_plugin_smoke() -> None:
    helper = load("github-release-plugins", "_github_plugins")
    repo = {"description": "plugin", "topics": ["after-effects"], "license": {"spdx_id": "MIT"}}
    release = {"html_url": "https://github.com/example/plugin/releases/tag/v1", "tag_name": "v1", "published_at": "2026-01-01", "assets": [{"id": 7, "name": "plugin.zip", "size": 12, "download_count": 3, "browser_download_url": "https://github.com/example/plugin/releases/download/v1/plugin.zip"}]}
    with patch.object(helper, "api", side_effect=[repo, release]):
        value = helper.inspect("example/plugin")
    assert value["license_spdx"] == "MIT"
    assert value["assets"][0]["id"] == 7


def game_icons_smoke() -> None:
    helper = load("game-icons-assets", "_game_icons")
    value = helper.summary("lorc/acid-blob.svg")
    assert value["author"] == "lorc"
    assert value["license_spdx"] == "CC-BY-3.0"
    downloader = load("game-icons-assets", "download_game_icon")
    descriptor = downloader.descriptor(value, "/tmp/acid-blob.svg")
    assert descriptor["asset_id"] == "game-icons:lorc/acid-blob"


def google_fonts_smoke() -> None:
    search = load("google-font-assets", "search_google_fonts")
    fonts = [
        {"family": "Pixelify Sans", "category": "display", "subsets": ["latin"], "variants": ["regular"]},
        {"family": "Roboto", "category": "sans-serif", "subsets": ["latin"], "variants": ["regular"]},
    ]
    with patch.object(search, "catalog", return_value=fonts):
        result = search.main(query="pixel", category="display")
    assert result["context"]["fonts"][0]["family"] == "Pixelify Sans"


def main() -> None:
    validate_skills()
    pexels_smoke()
    mixkit_smoke()
    github_plugin_smoke()
    game_icons_smoke()
    google_fonts_smoke()


if __name__ == "__main__":
    main()

from __future__ import annotations

import hashlib
import importlib.util
import io
import os
import sys
import tempfile
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

    helper = load("google-font-assets", "_google_fonts")
    curated = helper.curated_font("Noto Sans SC", "regular")
    assert curated["size_bytes"] == 8_331_336
    assert curated["sha256"] == "faa6c9df652116dde789d351359f3d7e5d2285a2b2a1f04a2d7244df706d5ea9"
    try:
        helper.curated_font("noto sans sc", "regular")
    except ValueError:
        pass
    else:
        raise AssertionError("Keyless curated family matching must be exact")

    class Response(io.BytesIO):
        def __init__(self, payload: bytes, url: str = "https://example.invalid/font.otf") -> None:
            super().__init__(payload)
            self.url = url

        def geturl(self) -> str:
            return self.url

    payload = b"verified font"
    with tempfile.TemporaryDirectory() as output_dir:
        target = Path(output_dir) / "font.otf"
        target.write_bytes(b"existing")
        try:
            helper.download("http://example.invalid/font.otf", output_dir, target.name)
        except ValueError:
            pass
        else:
            raise AssertionError("Non-HTTPS downloads must fail closed")
        for unsafe_url in (
            "http://fonts.gstatic.com.evil.invalid/font.otf",
            "http://user@fonts.gstatic.com/font.otf",
            "http://fonts.gstatic.com:80/font.otf",
        ):
            try:
                helper.download(unsafe_url, output_dir, target.name)
            except ValueError:
                pass
            else:
                raise AssertionError(f"Non-canonical Google Fonts URL must fail closed: {unsafe_url}")
        with patch.object(helper.urllib.request, "urlopen", return_value=Response(payload)):
            try:
                helper.download("https://example.invalid/font.otf", output_dir, target.name, expected_sha256="0" * 64)
            except RuntimeError:
                pass
            else:
                raise AssertionError("Hash mismatch must fail closed")
        assert target.read_bytes() == b"existing"
        assert not list(Path(output_dir).glob(".font.otf.*"))
        with patch.object(helper.urllib.request, "urlopen", return_value=Response(payload)):
            local_path, sha256, size = helper.download(
                "https://example.invalid/font.otf",
                output_dir,
                target.name,
                expected_sha256=hashlib.sha256(payload).hexdigest(),
                expected_size=len(payload),
            )
        assert Path(local_path).read_bytes() == payload
        assert sha256 == hashlib.sha256(payload).hexdigest() and size == len(payload)

    downloader = load("google-font-assets", "download_google_font")
    api_http_url = "http://fonts.gstatic.com/s/pixelifysans/v1/pixelify.ttf"
    api_https_url = "https://fonts.gstatic.com/s/pixelifysans/v1/pixelify.ttf"
    api_license_url = "https://example.invalid/OFL.txt"
    api_font = {**fonts[0], "files": {"regular": api_http_url}}
    api_license = {"license_spdx": "OFL-1.1", "license_url": api_license_url}
    api_payload = b"api font payload"
    license_payload = b"OFL license payload"
    requested_urls: list[str] = []

    def api_urlopen(request, timeout: int):
        requested_urls.append(request.full_url)
        payloads = {api_https_url: api_payload, api_license_url: license_payload}
        return Response(payloads[request.full_url], request.full_url)

    with tempfile.TemporaryDirectory() as output_dir:
        with (
            patch.dict(os.environ, {"GOOGLE_FONTS_API_KEY": "test"}),
            patch.object(downloader, "catalog", return_value=[api_font]),
            patch.object(downloader, "family_license", return_value=api_license),
            patch.object(helper.urllib.request, "urlopen", side_effect=api_urlopen),
        ):
            api_result = downloader.main(family="Pixelify Sans", output_dir=output_dir)
        api_descriptor = api_result["context"]["asset_descriptor"]
        assert api_result["success"]
        assert requested_urls == [api_https_url, api_license_url]
        assert Path(api_descriptor["variants"][0]["local_path"]).read_bytes() == api_payload
        assert Path(api_descriptor["extra"]["license_path"]).read_bytes() == license_payload
        assert api_descriptor["asset_id"] == "google-fonts:pixelify-sans:regular"

    with (
        patch.dict(os.environ, {"GOOGLE_FONTS_API_KEY": ""}),
        patch.object(
            downloader,
            "download",
            side_effect=[
                ("/tmp/Noto-Sans-SC-regular.otf", curated["sha256"], curated["size_bytes"]),
                ("/tmp/Noto-Sans-SC-LICENSE.txt", curated["license_sha256"], curated["license_size_bytes"]),
            ],
        ),
    ):
        curated_result = downloader.main(family="Noto Sans SC", variant="regular", output_dir="/tmp")
    descriptor = curated_result["context"]["asset_descriptor"]
    assert descriptor["attribution"]["source_url"] == curated["file_url"]
    assert descriptor["extra"]["license_url"] == curated["license_url"]


def main() -> None:
    validate_skills()
    pexels_smoke()
    mixkit_smoke()
    github_plugin_smoke()
    game_icons_smoke()
    google_fonts_smoke()


if __name__ == "__main__":
    main()

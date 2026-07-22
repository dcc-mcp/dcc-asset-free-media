---
name: google-font-assets
description: Search Google Fonts and download a verified font variant with its family license as an AssetDescriptor.
license: MIT
compatibility: "dcc-mcp-core 0.19+, Python 3.10+"
metadata:
  dcc-mcp:
    version: v0.2.0
    dcc: python
    layer: domain
    tags: [asset, font, typography, ui, google-fonts]
    search-hint: "free game font, UI font, Google Fonts, TTF, typography"
    produces: [asset_descriptor]
    tools: tools.yaml
---

# Google Font Assets

Use this skill for game and application UI fonts. With `GOOGLE_FONTS_API_KEY`, search for a family,
then download one returned variant. Without a key, the download tool accepts only the exact curated
pair `Noto Sans SC` / `regular`. That fallback is pinned to an immutable official noto-cjk commit;
the font and license are streamed to temporary files, verified by size and SHA-256, then atomically installed.

Keep that license with redistributed font files. Modified fonts may have reserved-name requirements.

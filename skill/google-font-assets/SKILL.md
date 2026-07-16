---
name: google-font-assets
description: Search Google Fonts and download a font variant with its family license as an AssetDescriptor.
license: MIT
compatibility: "dcc-mcp-core 0.19+, Python 3.10+"
metadata:
  dcc-mcp:
    version: v0.1.0
    dcc: python
    layer: domain
    tags: [asset, font, typography, ui, google-fonts]
    search-hint: "free game font, UI font, Google Fonts, TTF, typography"
    produces: [asset_descriptor]
    tools: tools.yaml
---

# Google Font Assets

Use this skill for game and application UI fonts. Set `GOOGLE_FONTS_API_KEY`, search for a family,
then download one returned variant. The download includes the font family's actual license file.

Keep that license with redistributed font files. Modified fonts may have reserved-name requirements.

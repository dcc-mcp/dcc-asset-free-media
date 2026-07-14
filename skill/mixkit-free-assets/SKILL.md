---
name: mixkit-free-assets
description: Download free-license Mixkit stock video, music, sound effects, and explicit After Effects templates as validated AssetDescriptors.
license: MIT
compatibility: "dcc-mcp-core 0.19+, Python 3.10+"
metadata:
  dcc-mcp:
    version: v0.2.0
    dcc: after-effects
    layer: domain
    tags: [asset, mixkit, stock-video, music, sound-effects, after-effects, template, motion-graphics, download]
    search-hint: "free stock video, free music, sound effect, whoosh, free AE template, Mixkit, opener, logo reveal"
    produces: [asset_descriptor]
    tools: tools.yaml
---

# Mixkit Free Assets

Inspect and download explicit Mixkit stock video pages only when the item declares the Stock Video
Free License; Restricted License items are rejected. Use the audio listing tools to discover and
download free Mixkit music or sound effects. For After
Effects templates, require an explicit Mixkit item page, inspect it first, then download the ZIP.
Every result carries the item-specific Mixkit license link.

Downloads return a validated `asset_descriptor`. This skill does not redistribute files, bypass
sign-in, or automate premium Envato Elements content.

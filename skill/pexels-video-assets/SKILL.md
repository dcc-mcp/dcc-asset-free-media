---
name: pexels-video-assets
description: Search and download free Pexels stock video as validated AssetDescriptors.
license: MIT
compatibility: "dcc-mcp-core 0.19+, Python 3.8+"
metadata:
  dcc-mcp:
    version: v0.1.0
    dcc: python
    layer: domain
    tags: [asset, pexels, video, stock, download]
    search-hint: "free stock video, pexels video, footage, background video, b-roll"
    produces: [asset_descriptor]
    tools: tools.yaml
---

# Pexels Video Assets

Use this skill to find free stock video through the official Pexels API. Set `PEXELS_API_KEY`.

Search first, retain the returned creator and source URL, then download the selected video ID.
The download result contains a validated `asset_descriptor` for handoff to Premiere Pro, After
Effects, or another DCC adapter. Follow the Pexels license and API attribution guidelines.


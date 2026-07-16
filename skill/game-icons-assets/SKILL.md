---
name: game-icons-assets
description: Search and download CC BY 3.0 game UI icons from the official Game-Icons.net repository.
license: MIT
compatibility: "dcc-mcp-core 0.19+, Python 3.10+"
metadata:
  dcc-mcp:
    version: v0.1.0
    dcc: python
    layer: domain
    tags: [asset, game, icon, svg, ui, cc-by]
    search-hint: "free game icon, HUD icon, inventory icon, ability icon, SVG game UI"
    produces: [asset_descriptor]
    tools: tools.yaml
---

# Game Icons Assets

Use this skill for HUD, inventory, ability, and other game UI icons. Search first, then download
the selected repository path. Every result retains its author and required CC BY 3.0 attribution.

The skill returns the original SVG only. Rasterization and DCC import stay with the consuming tool.

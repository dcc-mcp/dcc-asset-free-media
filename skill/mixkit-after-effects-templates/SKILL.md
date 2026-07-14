---
name: mixkit-after-effects-templates
description: Inspect and download explicit free Mixkit After Effects template pages as validated AssetDescriptors.
license: MIT
compatibility: "dcc-mcp-core 0.19+, Python 3.10+"
metadata:
  dcc-mcp:
    version: v0.1.0
    dcc: after-effects
    layer: domain
    tags: [asset, mixkit, after-effects, template, motion-graphics, download]
    search-hint: "free AE template, Mixkit After Effects template, opener, logo reveal, intro"
    produces: [asset_descriptor]
    tools: tools.yaml
---

# Mixkit After Effects Templates

Use this skill when the user has selected an explicit free After Effects template page on Mixkit.
Inspect the page first, confirm its license link, and then download the ZIP. The resolver accepts
only `mixkit.co` After Effects item pages and `assets.mixkit.co` ZIP downloads.

The result is a validated `asset_descriptor`; pass it to an After Effects workflow. This skill does
not redistribute templates, bypass sign-in, or automate premium Envato Elements content.

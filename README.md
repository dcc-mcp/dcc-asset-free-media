# DCC-MCP Free Media Assets

<p align="center">
  <img src="docs/assets/dcc-asset-free-media.svg" alt="DCC-MCP · FREE-MEDIA-ASSETS" width="600">
</p>

## Agent workflow

AI agents should use installed package skills through the shared gateway. IDE
users may continue to use the MCP endpoint.

### Install or update the CLI

`dcc-mcp-cli` is the preferred control path for every shell-capable agent. If
it is missing, ask the user before installing the latest official release:

```bash
# Linux/macOS
curl -fsSL https://raw.githubusercontent.com/dcc-mcp/dcc-mcp-core/main/scripts/install-cli.sh | sh

# Windows PowerShell
powershell -ExecutionPolicy Bypass -c "irm https://raw.githubusercontent.com/dcc-mcp/dcc-mcp-core/main/scripts/install-cli.ps1 | iex"
```

Keep an official build current through the release manifest:

```bash
dcc-mcp-cli update check
dcc-mcp-cli update apply
```

`update apply` downloads and stages the latest CLI for the next launch. It
does not update a running `dcc-mcp-server`; update that server in its own
environment.

```bash
dcc-mcp-cli dcc-types
dcc-mcp-cli list
dcc-mcp-cli search --query "<task>" --dcc-type <host>
dcc-mcp-cli describe <tool-slug>
dcc-mcp-cli call <tool-slug> --json '{"key":"value"}'
```

If the package skill is not active, call
`dcc-mcp-cli load-skill <skill-name> --dcc-type <host>`. After the task,
query `dcc-mcp-cli stats --range 24h --session-id <task-id>` and pass only
bounded evidence to the `review_skill_improvement` prompt from
`dcc-mcp-skills-creator`.


DCC-neutral skills for finding and downloading license-safe media used by content and game demos.

- `pexels-video-assets` searches the official Pexels API and downloads selected video files.
- `mixkit-free-assets` downloads selected Mixkit music, sound effects, and explicit AE template ZIPs.
- `github-release-plugins` inspects licensed open-source GitHub projects and downloads release assets with SHA-256 verification metadata.
- `game-icons-assets` searches and downloads CC BY 3.0 SVG icons from Game-Icons.net.
- `google-font-assets` searches Google Fonts and downloads one verified font variant with its family license; keyless mode provides the pinned Noto Sans SC Regular fallback.

Every download returns a validated `AssetDescriptor` with a local file, original source URL,
creator when available, and license information. The skills never import files into Adobe apps;
pass the descriptor to an adapter skill for that step.

Pexels requires `PEXELS_API_KEY`. Google Fonts search and general downloads require `GOOGLE_FONTS_API_KEY`;
without one, `google-font-assets` v0.2.0 accepts only exact `Noto Sans SC` / `regular` and verifies the font and OFL license against an immutable official noto-cjk revision.
Mixkit downloads are resolved from current listing/item pages.
GitHub plugin downloads require a public repository with a declared open-source SPDX license.
This repository does not redistribute third-party media, templates, or plugin binaries.

## Showcases

### Pexels video assets

![Stock video discovery, licensed download, and verified editing handoff](docs/images/pexels-video-assets-showcase.webp)

### Mixkit free assets

![Free video, audio, and template discovery with license-gated downloads](docs/images/mixkit-free-assets-showcase.webp)

### Game icons assets

![Game icon search, attribution capture, and HUD asset handoff](docs/images/game-icons-assets-showcase.webp)

### Google font assets

![Font family selection, license download, and game UI typography result](docs/images/google-font-assets-showcase.webp)

### GitHub release plugins

![Licensed release inspection, checksum verification, and manual plugin review](docs/images/github-release-plugins-showcase.webp)

These are original workflow illustrations; no third-party thumbnails, logos, or interface captures
are reproduced.

## Validate

```bash
python tests/smoke_test.py
```

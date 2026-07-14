---
name: github-release-plugins
description: Inspect licensed open-source GitHub projects and download release plugin packages with SHA-256 metadata.
license: MIT
compatibility: "dcc-mcp-core 0.19+, Python 3.10+"
metadata:
  dcc-mcp:
    version: v0.1.0
    dcc: python
    layer: domain
    tags: [plugin, github, open-source, release, download, security]
    search-hint: "free Adobe plugin, open source After Effects plugin, Premiere plugin, GitHub release"
    tools: tools.yaml
---

# GitHub Release Plugins

Use this skill only for an explicit public GitHub repository. Inspect the latest release first.
The repository must declare an SPDX open-source license. Download a selected release asset by ID;
the result records its source URL, version, license, local path, size, and SHA-256 digest.

This skill downloads but never installs or executes plugin binaries. Host compatibility and trust
remain separate user decisions.

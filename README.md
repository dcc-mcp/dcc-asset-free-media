# DCC-MCP Free Media Assets

DCC-neutral skills for finding and downloading free stock video and After Effects templates.

- `pexels-video-assets` searches the official Pexels API and downloads selected video files.
- `mixkit-after-effects-templates` inspects an explicit Mixkit template page and downloads its ZIP.

Every download returns a validated `AssetDescriptor` with a local file, original source URL,
creator when available, and license information. The skills never import files into Adobe apps;
pass the descriptor to an adapter skill for that step.

Pexels requires `PEXELS_API_KEY`. Mixkit downloads are resolved from the selected item page at
runtime; this repository does not redistribute third-party media or templates.

## Validate

```bash
python tests/smoke_test.py
```


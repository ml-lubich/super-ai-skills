---
name: own-chrome
description: >
  Drive the Google Chrome already open on this machine with the own-chrome
  CLI. Use when the user wants their real browser, existing sign-ons, any
  site they can click, filtered tab lists, or JSON an agent can parse. Do not
  hardcode a profile. Do not launch a second browser. Do not use CUA here.
---

# Own Chrome

`own-chrome` talks to the Google Chrome already listening on `127.0.0.1:9222`. The profile is whatever that process was started with. The package is stdlib-only and installs with `uv tool install`.

Public repo: https://github.com/ml-lubich/own-chrome. Local checkout: `~/dev/own-chrome`. Entry points: `own-chrome` and `li`.

## Install

```bash
uv tool install git+https://github.com/ml-lubich/own-chrome
```

That puts both commands on `PATH`. Re-run it after the source changes.

## Commands

Agents should pass `--json`. `--filter` is a case-insensitive substring of the title or URL. `--limit` caps rows (default 20). A filter that matches nothing exits 2.

```bash
own-chrome status --json --filter linkedin --limit 5
own-chrome tabs --filter linkedin --json
own-chrome open https://example.com
own-chrome goto https://example.com --tab example.com
own-chrome eval 'document.title' --tab example.com --json
```

`status` fails if nothing is listening, or if the process is Chrome for Testing, Playwright, or the devtools-mcp profile (`--enable-automation`, `ms-playwright`, `chrome-devtools-mcp`).

## Repeatability

Facts live in brain (`ml-lubich/brain-knowledge`) and move between machines with `brain sync`. This skill file is the local kit (`ml-lubich/claude-kit` restored into `~/.claude`). It can be behind a pull. Before driving Chrome, run `brain recall "own-chrome"` and follow a newer note over this file.

## Agent prompt

```text
brain recall "own-chrome" first. The local skill can lag a git pull.
Use own-chrome against the Chrome already on 127.0.0.1:9222.
Prefer --json --filter --limit. Run own-chrome status --json first.
If it errors, stop. Do not kill Chrome. Do not launch Chrome for Testing.
Do not copy the default profile folder. LinkedIn goes through li (li commands --json).
```

## Chrome 136+

`--remote-debugging-port` on the default Chrome data directory is ignored, so 9222 never opens. Debugging works when that Chrome was started with some other `--user-data-dir`. Confirm with `own-chrome status` before acting.

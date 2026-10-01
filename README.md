# super-ai-skills

The unified agent engineering hub and meta-repository integrating Misha's personal agent skills, MCP servers, and automation tools as submodules and modular skills.

## Architecture

- `skills/`: Comprehensive agent skills compatible with Claude Code, Cursor, Codex, and Gemini/Antigravity.
- `packages/`: Git submodules of core MCP tools and standalone repositories:
  - `packages/linkedin-mcp`: LinkedIn MCP server & CLI (Voyager API + CDP Chrome automation)
  - `packages/imail-mcp`: macOS Mail.app CLI + MCP server
  - `packages/whatsapp-mcp`: WhatsApp Web MCP server
  - `packages/imsg-mcp`: macOS iMessage MCP server
  - `packages/jenkins-mcp`: Jenkins CLI + MCP server
  - `packages/inotes-mcp`: macOS Apple Notes CLI + MCP server
  - `packages/vercel-mcp`: Multi-account Vercel CLI + MCP server
  - `packages/railway-mcp`: Railway Cloud CLI + MCP server
  - `packages/own-chrome`: Headless/headful Chrome CDP controller for agents
  - `packages/humanizer`: Prose humanization and AI-writing filter
  - `packages/claude-tiers`: Model-tiered Claude Code delegation ruleset
  - `packages/callgen`: Audio/call transcript analyzer & visualization generator
  - `packages/bitbucket-cli`: Minimal Bitbucket Data Center/Cloud CLI (`bb`)
  - `packages/like-fable`: Agent behavior & collaboration prompt library

## Quickstart & Dev Setup (macOS / Linux)

Pure Python OOP setup without shell scripts:

```bash
git clone --recurse-submodules https://github.com/ml-lubich/super-ai-skills.git
cd super-ai-skills

# Install via pip or uv
pip install -e .

# Run the Python-native environment bootstrap
super-skills setup-dev
```

## CLI Usage

- `super-skills doctor`: Environment diagnostic and health check
- `super-skills list-skills`: List all 35+ available agent skills
- `super-skills list-mcp`: List all 14 MCP server submodules
- `super-skills install-skills --target all`: Link skills into Claude, Cursor, Codex, and Gemini
- `super-skills setup-dev`: Re-run full system dev bootstrap

## Collaborators

- **Misha Lubich** (`@ml-lubich`) - Owner
- **Joe** (`@java-heapler`) - Read / Write Collaborator

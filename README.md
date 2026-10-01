# superai-skills

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
- `prompts/`: Agent-friendly setup prompts and instructions for headless or autonomous setup.

## Quickstart & Dev Setup (macOS / Linux)

Pure Python OOP setup without shell scripts:

```bash
git clone --recurse-submodules https://github.com/ml-lubich/superai-skills.git
cd superai-skills

# Install via pip or uv
pip install -e .

# Run the Python-native environment bootstrap
superai-skills setup-dev
```

## Agent Onboarding Prompt

For autonomous coding agents (Claude Code, Cursor Agent, Codex, Gemini/Antigravity), paste the onboarding prompt from:
👉 [`prompts/AGENT_SETUP_PROMPT.md`](file:///Users/mlubich/dev/superai-skills/prompts/AGENT_SETUP_PROMPT.md)

## CLI Usage

- `superai-skills doctor`: Environment diagnostic and health check
- `superai-skills list-skills`: List all 35+ available agent skills
- `superai-skills list-mcp`: List all 14 MCP server submodules
- `superai-skills install-skills --target all`: Link skills into Claude, Cursor, Codex, and Gemini
- `superai-skills setup-dev`: Re-run full system dev bootstrap

> **Note:** Voice learning / stylistic RAG belongs in individual skill repos (e.g. `humanizer`, `linkedin-outreach`), not in this meta-repo. `superai-skills` is just a collection — it does not learn on its own.

## Collaborators

- **Misha Lubich** (`@ml-lubich`) - Owner
- **Joe** (`@java-heapler`) - Read / Write Collaborator

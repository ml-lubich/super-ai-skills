---
name: linkedin-post
description: Draft and safely publish grounded engineering posts, tech memes, and diagrams to LinkedIn without AI buzzwords or cringe. Supports image/meme attachment and automated posting.
---

# LinkedIn Post & Meme Automation Skill (`linkedin-post`)

Safely draft and publish grounded technical engineering posts, architecture diagrams, and relatable tech memes to LinkedIn. Designed to sound authentically human—never generic, hyped, or embarrassing.

## 1. Anti-Cringe & Humanizer Guardrails

- ❌ **STRICT BANNED WORDS & PATTERNS**:
  - "Excited to announce", "Thrilled to share", "In today's fast-paced world", "Game-changer", "Leveraging", "Testament to", "Delve", "Embark".
  - Multi-line hashtag dumps (`#AI #Tech #Innovation #Leadership #Engineering`). Maximum 1-2 relevant hashtags at most.
  - Inflated symbolism or dramatic life lessons.

- ✅ **GROUNDED HUMAN VOICE**:
  - Short, uneven paragraphs (1-3 sentences each).
  - Relatable engineering humor & memes (e.g., legacy Java vs modern frameworks, production bug triage at 4:59 PM, open-weight LLMs hallucinating SQL, Docker containers working on 'my machine').
  - Stances on real trade-offs (e.g., on-prem vLLM open weights vs expensive APIs, deterministic allowlists vs open prompt execution, TDD vs manual QA).

## 2. Tech Meme & Image Automation

- **Meme Generation**:
  - Generate custom tech memes or diagrams using Python (`PIL`/`matplotlib`) or image tools.
  - Keep memes relevant to senior software engineering, AI infrastructure, distributed systems, and DevOps realities.

- **Image Attachment in LinkedIn Post**:
  - When posting with an image/meme, upload the file directly to LinkedIn's post attachment input:
    ```bash
    agent-browser upload "input[type='file']" /path/to/meme.png
    ```

## 3. Safety Control & Approval

- **Default Mode**: ALWAYS output the drafted post text and preview the meme in chat for user review first.
- **Publishing Mode**: Only navigate to LinkedIn and submit after user approves or explicitly requests auto-posting.

## 4. Automated Browser Publishing Workflow

1. Open LinkedIn Feed:
   ```bash
   agent-browser open --headed "https://www.linkedin.com/feed/"
   ```
2. Click "Start a post" button:
   ```bash
   agent-browser click @e_start_post
   ```
3. Attach Meme / Diagram Image (if applicable):
   ```bash
   agent-browser upload "input[type='file']" /path/to/meme.png
   ```
4. Type humanized post text using real keystroke emulation:
   ```bash
   agent-browser keyboard type "<humanized_post_text>"
   ```
5. Verify preview and click "Post".

---
name: hermes-tweet
description: Hermes Tweet guidance for Xquik-powered X/Twitter research, monitoring, and approval-gated social actions.
---

# Hermes Tweet

Use this skill when a Claude Code project uses Hermes Tweet or needs to hand off X/Twitter research and social monitoring work to a Hermes Agent runtime with Xquik configured.

## Setup

Install and enable the Hermes Tweet plugin on the Hermes runtime host:

```sh
hermes plugins install Xquik-dev/hermes-tweet
hermes plugins enable hermes-tweet
```

Set `XQUIK_API_KEY` in that runtime environment. Leave `HERMES_TWEET_ENABLE_ACTIONS` disabled unless the workflow intentionally allows account-changing actions.

## Use Cases

- Research public X/Twitter conversations for a launch, brand, creator, or repo.
- Monitor keywords or accounts and summarize relevant changes.
- Prepare action previews for posts, replies, follows, DMs, webhooks, draws, or extraction jobs.
- Keep write workflows explicit and user-approved.

## Guardrails

- Keep credentials out of prompts, examples, code, and issue text.
- Start with read-only research before any action workflow.
- State the exact action and expected side effect before invoking a write-capable tool.
- Stop on policy, auth, or account-state failures instead of retrying through alternate routes.

# nitro-dev

A Claude Code skill for developing applications with [Nitro v3](https://v3.nitro.build) — the framework-agnostic server framework powered by H3, UnJS, and Vite.

## What it does

Provides Claude with comprehensive Nitro knowledge including:

- **Route handlers** — file-based routing, HTTP methods, dynamic params, streaming
- **Caching** — `defineCachedHandler`, `defineCachedFunction`, SWR, route rule caching
- **Storage** — KV storage via unstorage with 20+ drivers (Redis, S3, fs, etc.)
- **Database** — SQL via db0 (SQLite, PostgreSQL, MySQL, D1, etc.)
- **Middleware & Plugins** — request lifecycle, runtime hooks
- **Tasks** — background tasks with cron scheduling
- **WebSocket** — real-time handlers with pub/sub
- **Deployment** — 30+ presets (Cloudflare, Vercel, Netlify, AWS, Node.js, Bun, Deno...)
- **Configuration** — runtime config, route rules, env vars

## Installation

Copy the `nitro-dev` folder into your Claude Code skills directory:

```
~/.claude/skills/nitro-dev/
```

Or clone this repo directly:

```bash
git clone https://github.com/kbzowski/nitro-skill.git ~/.claude/skills/nitro-dev
```

## Structure

```
nitro-dev/
├── SKILL.md                    # Core skill (triggers, quick start, concepts)
└── references/
    ├── routing.md              # Full routing patterns
    ├── caching-storage.md      # Cache, storage, database
    ├── advanced.md             # Middleware, plugins, tasks, WebSocket, errors
    └── deployment.md           # Deployment presets & config reference
```

## Triggers

The skill activates when Claude encounters Nitro-related context: `nitro.config.ts`, `defineHandler`, `nitro/h3`, `nitro/cache`, `useStorage`, `defineNitroConfig`, and similar patterns.

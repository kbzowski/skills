---
name: tanstack-docs
description: >
  Searches and fetches TanStack documentation, and scaffolds TanStack projects using @tanstack/cli.
  Use this skill whenever the user asks about TanStack APIs, needs to look up how TanStack Router,
  Query, Form, Table, Start, Store, Virtual, or any other TanStack library works, wants to search
  TanStack docs for a specific topic, or needs to find ecosystem integrations. Also use it when
  the user wants to create a new TanStack Start/Router app, add integrations to an existing project,
  or asks about TanStack CLI commands and add-ons. Trigger even if the user just says "how does
  TanStack Router handle data loading" or "show me TanStack Query mutation docs" — any question
  about TanStack library usage should go through this skill's doc commands first.
---

# TanStack CLI

`@tanstack/cli` provides two key capabilities: **documentation lookup** (search and fetch
TanStack docs directly from the terminal) and **project scaffolding** (create/manage TanStack
apps). Pass `--json` on every command for machine-readable output.

## When to use

- User asks how a TanStack API works (Router loaders, Query mutations, Form validation, etc.)
- User needs to look up TanStack documentation for a specific topic
- User wants to discover TanStack ecosystem integrations or libraries
- User wants to scaffold a new TanStack Start or Router project
- User wants to add integrations (Clerk, Drizzle, Sentry, etc.) to an existing TanStack project

## When NOT to use

- The question is about a non-TanStack library (React Router, SWR, Formik, etc.)
- The user already has the documentation content and just needs help interpreting it
- The user is working with a Next.js, Remix, or other non-TanStack project

## Package manager runner

Before running any command, detect the runner from the lockfile in the project root.
Default to `npx` when no lockfile is present.

| Lockfile | Runner |
|----------|--------|
| `package-lock.json` | `npx` |
| `pnpm-lock.yaml` | `pnpx` |
| `yarn.lock` | `yarn dlx` |
| `bun.lockb` | `bunx` |

All commands below use `<runner>` as a placeholder for the detected command.

---

## 1. Search documentation

This is the primary use case. Search the docs first rather than answering from general
knowledge — TanStack APIs evolve rapidly and cached knowledge goes stale.

### Search docs by topic

```bash
<runner> @tanstack/cli search-docs "<query>" --library <lib> --json
```

The `--library` flag scopes the search to a specific TanStack library. Known libraries:
`start`, `router`, `query`, `form`, `table`, `store`, `virtual`, `config`, `pacer`, `db`, `devtools`.

**Examples:**
```bash
# How does data loading work in TanStack Router?
<runner> @tanstack/cli search-docs "data loading" --library router --json

# How to set up mutations in TanStack Query?
<runner> @tanstack/cli search-docs "mutations" --library query --json

# Server functions in TanStack Start
<runner> @tanstack/cli search-docs "server functions" --library start --json

# Virtualizing lists
<runner> @tanstack/cli search-docs "virtualizer" --library virtual --json
```

Filter by framework when the library supports multiple (e.g. React, Solid):
```bash
<runner> @tanstack/cli search-docs "useQuery" --library query --framework react --json
```

### Fetch a specific doc page

When search results return paths, fetch the full content:

```bash
<runner> @tanstack/cli doc <library> <path> --json
```

**Examples:**
```bash
# Fetch the data loading guide for React Router
<runner> @tanstack/cli doc router framework/react/guide/data-loading --json

# Fetch the query options reference
<runner> @tanstack/cli doc query framework/react/reference/useQuery --json

# Fetch TanStack Start SSR guide
<runner> @tanstack/cli doc start framework/react/guide/ssr --json
```

The `<path>` comes from search results. Run `search-docs` first to discover the right path,
then `doc` to read the full page.

### Workflow for answering TanStack questions

1. Run `search-docs` with relevant keywords and the `--library` flag
2. Review search results — identify the most relevant doc page path
3. Fetch full content with `doc <library> <path> --json`
4. Synthesize the docs into a clear answer for the user

---

## 2. Discover libraries and ecosystem

### List all TanStack libraries

```bash
<runner> @tanstack/cli libraries --json
```

Returns metadata about every TanStack library. Use to confirm library names or help the user
pick the right one.

### Query ecosystem by category

```bash
<runner> @tanstack/cli ecosystem --category <category> --json
```

Categories include: `database`, `hosting`, `auth`, `monitoring`, etc.
Use for discovery questions like "what databases work with TanStack?"

---

## 3. Scaffold a new project

```bash
<runner> @tanstack/cli create <project-name> [flags]
```

**Always pass `-y`** to avoid interactive prompts. Key flags:

| Flag | Purpose |
|------|---------|
| `-y` | Accept all defaults (TanStack Start + file-router) |
| `--add-ons <list>` | Comma-separated integrations (e.g. `clerk,drizzle,tailwind-css`) |
| `--router-only` | SPA without SSR |
| `--framework <name>` | `react` or `solid` |
| `--toolchain <name>` | `eslint` or `biome` |
| `--template <ref>` | Template URL or built-in ID |
| `--no-examples` | Skip example code |
| `--package-manager <pm>` | `npm`, `yarn`, `pnpm`, `bun`, `deno` |
| `--deployment <host>` | `vercel`, `netlify`, `cloudflare`, `aws` |

**Examples:**
```bash
<runner> @tanstack/cli create my-app -y --add-ons clerk,drizzle,tailwind-css --deployment vercel
<runner> @tanstack/cli create my-spa -y --router-only --add-ons tanstack-query
```

### Discover available add-ons

```bash
<runner> @tanstack/cli create --list-add-ons --json
<runner> @tanstack/cli create --addon-details <name> --json
```

---

## 4. Add integrations to existing project

Run from the project root (where `.tanstack.json` lives):

```bash
<runner> @tanstack/cli add <add-on> [<add-on>...]
```

```bash
<runner> @tanstack/cli add clerk drizzle sentry
```

---

## 5. Other commands

```bash
# Pin TanStack package versions (remove ^ from ranges)
<runner> @tanstack/cli pin-versions

# Custom add-on authoring
<runner> @tanstack/cli add-on init | compile | dev

# Custom template creation
<runner> @tanstack/cli template init | compile
```

See [references/addon-authoring.md](references/addon-authoring.md) for add-on development details.

---

## Important notes

- The MCP server mode (`tanstack mcp`) has been **removed** — do not use it.
- Node.js 18+ is required.
- Always use `--json` for programmatic output parsing.
- `--list-add-ons` is a flag of the `create` command, not standalone.

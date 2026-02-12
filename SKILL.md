---
name: nitro-dev
description: >
  Comprehensive Nitro v3 framework development skill for building server APIs, full-stack apps,
  and backend services. Use when working on projects that use Nitro (nitro, nitropack) including:
  (1) Creating API routes and handlers, (2) Configuring caching, storage, or database,
  (3) Setting up middleware, plugins, or WebSocket handlers, (4) Deploying to any platform
  (Cloudflare, Vercel, Netlify, AWS, Node.js, Bun, Deno, etc.), (5) Working with runtime config,
  route rules, tasks, prerendering, (6) Integrating Nitro with Vite, React, Vue, Hono, or other frameworks,
  (7) Any project with nitro.config.ts, nitro/vite plugin, or routes/ directory using defineHandler.
  Triggers on: nitro, nitropack, defineHandler, defineNitroConfig, nitro/h3, nitro/cache,
  nitro/storage, nitro/task, nitro/database, defineCachedHandler, useStorage, useRuntimeConfig.
---

# Nitro v3 Development

Nitro is a framework-agnostic server framework powered by H3, UnJS, and Vite/Rolldown/Rollup.
It provides file-based routing, deployment to 30+ platforms with zero config, and runtime-agnostic APIs.

**Docs**: https://v3.nitro.build
**LLM context**: https://v3.nitro.build/llms.txt | https://v3.nitro.build/llms-full.txt

## Quick Start

### New Project

```bash
npx create-nitro-app my-app
cd my-app && npm install && npm run dev
```

### Add to Existing Vite App

```bash
npm install nitro
```

```ts
// vite.config.ts
import { defineConfig } from "vite";
import { nitro } from "nitro/vite";

export default defineConfig({
  plugins: [nitro()],
});
```

Routes go in `server/routes/` (with Vite) or `routes/` (standalone).

## Core Concepts

### Route Handlers

```ts
// routes/api/hello.ts → GET|POST /api/hello
import { defineHandler } from "nitro/h3";

export default defineHandler((event) => {
  return { message: "Hello Nitro!" };
});
```

HTTP method suffix restricts methods: `hello.get.ts`, `hello.post.ts`, `hello.delete.ts`.

Dynamic params: `routes/users/[id].ts` → access via `event.context.params!.id`.

Catch-all: `routes/[...slug].ts` → `event.context.params!.slug`.

### Request/Response

```ts
import { defineHandler, getQuery, readBody, createError, setHeader } from "nitro/h3";

export default defineHandler(async (event) => {
  const query = getQuery(event);           // ?key=value
  const body = await readBody(event);      // POST body
  setHeader(event, "X-Custom", "value");

  if (!query.id) {
    throw createError({ statusCode: 400, message: "Missing id" });
  }

  return { data: query.id };
});
```

### Middleware

Files in `middleware/` run before every request. Control order with numeric prefixes (`1.auth.ts`, `2.log.ts`). Return nothing to continue, return a value to respond immediately.

```ts
// middleware/auth.ts
export default defineHandler((event) => {
  event.context.user = { name: "Nitro" };
});
```

### Caching

```ts
import { defineCachedHandler } from "nitro/cache";

export default defineCachedHandler(
  (event) => ({ timestamp: Date.now() }),
  { maxAge: 3600, swr: true }
);
```

### Storage (KV)

```ts
import { useStorage } from "nitro/storage";

export default defineHandler(async () => {
  await useStorage().setItem("key", { value: 1 });
  return await useStorage().getItem("key");
});
```

### Runtime Config

```ts
// nitro.config.ts
export default defineNitroConfig({
  runtimeConfig: { apiSecret: "dev", public: { apiBase: "/api" } },
});
```

```ts
// In handler — override with NITRO_API_SECRET env var
import { useRuntimeConfig } from "nitro/runtime-config";
const config = useRuntimeConfig();
```

### Config File

```ts
// nitro.config.ts
import { defineNitroConfig } from "nitro/config";

export default defineNitroConfig({
  routeRules: {
    "/api/**": { cors: true },
    "/blog/**": { swr: 600 },
    "/old": { redirect: "/new" },
  },
  storage: { redis: { driver: "redis", url: "redis://localhost:6379" } },
  experimental: { database: true, tasks: true, websocket: true },
});
```

## Import Paths

| Import | Purpose |
|--------|---------|
| `nitro/h3` | `defineHandler`, `getQuery`, `readBody`, `createError`, `setHeader`, `getCookie`, `setCookie`, `defineWebSocketHandler` |
| `nitro/cache` | `defineCachedHandler`, `defineCachedFunction` |
| `nitro/storage` | `useStorage` |
| `nitro/database` | `useDatabase` |
| `nitro/task` | `defineTask`, `runTask` |
| `nitro/config` | `defineNitroConfig` |
| `nitro/runtime-config` | `useRuntimeConfig` |
| `nitro/context` | `useRequest` (experimental async context) |
| `nitro` | `definePlugin`, `defineErrorHandler`, `defineRouteMeta`, `fetch` (server fetch) |
| `nitro/vite` | `nitro` (Vite plugin) |

## Detailed References

- **Routing**: See [references/routing.md](references/routing.md) for full routing patterns, params, methods, streaming, route rules, and route metadata.
- **Caching, Storage & Database**: See [references/caching-storage.md](references/caching-storage.md) for cache options, storage drivers, database connectors, and server assets.
- **Advanced Features**: See [references/advanced.md](references/advanced.md) for middleware, plugins, tasks, WebSocket, error handling, server entry, async context, and prerendering.
- **Deployment & Config**: See [references/deployment.md](references/deployment.md) for all deployment presets, platform-specific setup, and full configuration reference.

## Request Lifecycle (Priority Order)

1. Route rules (headers, redirects, caching)
2. Global middleware (`middleware/`)
3. Server entry (`server.ts`)
4. Route handlers (`routes/`)
5. Renderer (`index.html` or custom)

## Common Patterns

### CRUD API

```
routes/api/
  users/
    index.get.ts      → GET /api/users (list)
    index.post.ts     → POST /api/users (create)
    [id].get.ts       → GET /api/users/:id (read)
    [id].put.ts       → PUT /api/users/:id (update)
    [id].delete.ts    → DELETE /api/users/:id (delete)
```

### Proxy & Redirect via Config

```ts
routeRules: {
  "/api/v1/**": { proxy: "https://api-v1.example.com/**" },
  "/legacy/**": { redirect: "/modern/**" },
}
```

### SPA with API Routes

Vite handles the frontend; Nitro handles `server/routes/`:

```ts
// vite.config.ts
import { defineConfig } from "vite";
import { nitro } from "nitro/vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react(), nitro()],
});
```

### SSR with Framework

```ts
// server.ts — integrate with any framework
import { Hono } from "hono";
const app = new Hono();
app.get("/ssr/*", (c) => c.html(renderApp(c.req.url)));
export default app;
```

## Key Constraints

- Runtime code must be **runtime-agnostic** (no Node.js-only APIs without checks)
- Prefer **Web APIs** (fetch, Request, Response, URL)
- Use `pathe` instead of `node:path` for cross-platform support
- `routeRules` are applied at build time — dynamic runtime rules need handler logic
- Database and tasks require `experimental` flags
- WebSocket requires `experimental.websocket` or `features.websocket`

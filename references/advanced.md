# Advanced Features Reference

## Middleware

Full docs: https://v3.nitro.build/guide/middleware

Middleware runs before route matching on every request. Place files in `middleware/` (or `server/middleware/` with serverDir).

### Global Middleware

```ts
// middleware/auth.ts
import { defineHandler, getHeader, createError } from "nitro/h3";

export default defineHandler((event) => {
  const token = getHeader(event, "authorization");
  if (!token) {
    throw createError({ statusCode: 401, message: "Unauthorized" });
  }
  event.context.user = verifyToken(token);
  // Return nothing to continue to next middleware/route
});
```

### Execution Order

Control order with numeric prefixes:

```
middleware/
  1.cors.ts       ← runs first
  2.auth.ts       ← runs second
  3.logging.ts    ← runs third
```

### Key Rules

- Returning a value from middleware **closes the request** (sends response)
- Return nothing / `undefined` to continue to routes
- Files prefixed with `_` are ignored (`middleware/_helper.ts`)

---

## Plugins

Full docs: https://v3.nitro.build/guide/plugins

Plugins run once at server startup. Place files in `plugins/` (or `server/plugins/` with serverDir).

```ts
// plugins/init.ts
import { definePlugin } from "nitro";

export default definePlugin((nitroApp) => {
  // Run on startup
  console.log("Server starting...");

  // Hook into request lifecycle
  nitroApp.hooks.hook("request", (event) => {
    console.log(`[${event.method}] ${event.path}`);
  });

  nitroApp.hooks.hook("response", (response, event) => {
    response.headers.set("X-Server", "Nitro");
  });

  nitroApp.hooks.hook("error", (error, context) => {
    console.error("Server error:", error.message);
  });

  nitroApp.hooks.hook("close", () => {
    console.log("Server shutting down...");
  });
});
```

### Available Runtime Hooks

| Hook | Arguments | Description |
|------|-----------|-------------|
| `request` | `(event)` | Before request processing |
| `response` | `(response, event)` | After response generated |
| `error` | `(error, context)` | On error |
| `close` | `()` | Server shutdown |

---

## Tasks (Experimental)

Full docs: https://v3.nitro.build/guide/tasks

Background tasks with optional cron scheduling.

### Enable

```ts
// nitro.config.ts
export default defineNitroConfig({
  experimental: { tasks: true },
});
```

### Define Tasks

Place in `tasks/` directory. File path becomes task name (`tasks/db/migrate.ts` → `db:migrate`):

```ts
// tasks/db/migrate.ts
import { defineTask } from "nitro/task";

export default defineTask({
  meta: {
    name: "db:migrate",
    description: "Run database migrations",
  },
  async run({ payload, context }) {
    // Task logic here
    await performMigration(payload.version);
    return { result: "Migrations complete" };
  },
});
```

### Run Tasks Programmatically

```ts
import { runTask } from "nitro/task";

export default defineHandler(async () => {
  const { result } = await runTask("db:migrate", {
    payload: { version: "1.2.0" },
  });
  return result;
});
```

### Scheduled Tasks (Cron)

```ts
// nitro.config.ts
export default defineNitroConfig({
  experimental: { tasks: true },
  scheduledTasks: {
    "*/5 * * * *": ["cache:cleanup"],    // every 5 minutes
    "0 * * * *": ["reports:generate"],   // every hour
    "0 0 * * *": ["db:backup"],          // daily at midnight
  },
});
```

### Dev Task API

In development, tasks are exposed at:

- `GET /_nitro/tasks` — list all tasks
- `GET /_nitro/tasks/db:migrate` — run specific task

---

## WebSocket

Full docs: https://v3.nitro.build/guide/websocket

### Enable

```ts
// nitro.config.ts
export default defineNitroConfig({
  experimental: { websocket: true },
  // or: features: { websocket: true },
});
```

### Define WebSocket Handler

```ts
// routes/_ws.ts
import { defineWebSocketHandler } from "nitro/h3";

export default defineWebSocketHandler({
  open(peer) {
    peer.send({ message: `Welcome ${peer}!` });
    peer.subscribe("chat");
    peer.publish("chat", { message: `${peer} joined!` });
  },

  message(peer, message) {
    const text = message.text();
    if (text === "ping") {
      peer.send({ message: "pong" });
    } else {
      peer.publish("chat", { message: text, from: peer.toString() });
    }
  },

  close(peer) {
    peer.publish("chat", { message: `${peer} left!` });
  },

  error(peer, error) {
    console.error("WebSocket error:", error);
  },
});
```

### Peer API

- `peer.send(data)` — send to this peer
- `peer.publish(topic, data)` — broadcast to topic subscribers
- `peer.subscribe(topic)` — subscribe to topic
- `peer.unsubscribe(topic)` — unsubscribe from topic

---

## Error Handling

Full docs: https://v3.nitro.build/guide/errors

### Throwing Errors in Handlers

```ts
import { defineHandler, createError } from "nitro/h3";

export default defineHandler((event) => {
  const id = event.context.params?.id;
  if (!id) {
    throw createError({
      statusCode: 400,
      statusMessage: "Missing ID",
      message: "The 'id' parameter is required",
    });
  }
  return { id };
});
```

### Custom Error Handler

```ts
// error.ts (root level)
import { defineErrorHandler } from "nitro";

export default defineErrorHandler(async (error, event, { defaultHandler }) => {
  // Custom JSON error response
  if (event.path.startsWith("/api/")) {
    return Response.json(
      { error: error.message, status: error.statusCode },
      { status: error.statusCode || 500 }
    );
  }
  // Fall back to default for non-API routes
  return defaultHandler(error, event);
});
```

Register in config:

```ts
// nitro.config.ts
export default defineNitroConfig({
  errorHandler: "~/error",
});
```

---

## Server Entry

Full docs: https://v3.nitro.build/guide/server-entry

`server.ts` acts as a global entry point running before route matching:

```ts
// server.ts
export default {
  async fetch(request: Request): Promise<Response | void> {
    const url = new URL(request.url);

    // Handle specific routes directly
    if (url.pathname === "/health") {
      return new Response("OK");
    }

    // Return nothing to continue to Nitro routes
  },
};
```

### Framework Integration in Server Entry

```ts
// server.ts — using Hono
import { Hono } from "hono";

const app = new Hono();
app.get("/hono", (c) => c.text("Hello from Hono!"));

export default app;
```

---

## Runtime Config

Full docs: https://v3.nitro.build/guide/configuration

### Define Defaults

```ts
// nitro.config.ts
export default defineNitroConfig({
  runtimeConfig: {
    apiSecret: "default-secret",
    public: {
      apiBase: "/api",
    },
  },
});
```

### Access in Handlers

```ts
import { useRuntimeConfig } from "nitro/runtime-config";

export default defineHandler(() => {
  const config = useRuntimeConfig();
  return { apiBase: config.public.apiBase };
});
```

### Override with Environment Variables

All runtime config can be overridden with `NITRO_` prefix:

```bash
NITRO_API_SECRET=production-secret
NITRO_PUBLIC_API_BASE=https://api.example.com
```

Nested keys use `_` separator, matching camelCase config keys via scule conversion.

---

## Async Context (Experimental)

Access current request without passing `event`:

```ts
// nitro.config.ts
export default defineNitroConfig({
  experimental: { asyncContext: true },
});
```

```ts
import { useRequest } from "nitro/context";

// In any function called during request handling
async function getCurrentUser() {
  const request = useRequest();
  const auth = request.headers.get("authorization");
  return verifyAuth(auth);
}

export default defineHandler(async () => {
  const user = await getCurrentUser(); // no need to pass event
  return { user };
});
```

---

## Prerendering

Full docs: https://v3.nitro.build/guide/prerender

Generate static HTML at build time:

```ts
// nitro.config.ts
export default defineNitroConfig({
  prerender: {
    routes: ["/", "/about", "/blog"],
    crawlLinks: true,     // auto-discover links
    concurrency: 4,       // parallel renders
    retry: 3,
    retryDelay: 500,
  },
  routeRules: {
    "/static-page": { prerender: true },
  },
});
```

Use `prerender:routes` hook to add routes dynamically:

```ts
// nitro.config.ts
export default defineNitroConfig({
  hooks: {
    "prerender:routes": async (routes) => {
      const posts = await fetchBlogPosts();
      posts.forEach((p) => routes.add(`/blog/${p.slug}`));
    },
  },
});
```

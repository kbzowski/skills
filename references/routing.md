# Routing Reference

Full docs: https://v3.nitro.build/guide/routing

## File-Based Route Mapping

Files in `routes/` (or `server/routes/` with serverDir) map directly to URL paths:

```
routes/index.ts          → /
routes/hello.ts          → /hello
routes/api/test.ts       → /api/test
routes/api/hello.get.ts  → /hello (GET only)
routes/api/hello.post.ts → /hello (POST only)
```

## HTTP Method Suffixes

Append method before `.ts` to restrict:

```
routes/users.get.ts     → GET /users
routes/users.post.ts    → POST /users
routes/users.put.ts     → PUT /users
routes/users.delete.ts  → DELETE /users
routes/users.patch.ts   → PATCH /users
```

## Dynamic Parameters

```
routes/users/[id].ts         → /users/:id
routes/users/[id]/posts.ts   → /users/:id/posts
routes/[...slug].ts          → catch-all (matches any depth)
```

Access params:

```ts
import { defineHandler } from "nitro/h3";

export default defineHandler((event) => {
  const id = event.context.params!.id;
  // For catch-all: event.context.params!.slug (string of remaining path)
  return { id };
});
```

## Route Groups

Directories wrapped in `()` are ignored in URL path:

```
routes/(admin)/dashboard.ts → /dashboard
routes/(api)/v1/users.ts    → /v1/users
```

## Handler Definition

```ts
// Simple - return value becomes JSON response
export default defineHandler(() => {
  return { message: "Hello" };
});

// With event access
export default defineHandler((event) => {
  const query = getQuery(event);
  const body = await readBody(event);
  return { query, body };
});

// Async handler
export default defineHandler(async (event) => {
  const data = await fetchData();
  return data;
});
```

## Reading Request Data

```ts
import { defineHandler, getQuery, readBody, getHeader, getCookie } from "nitro/h3";

export default defineHandler(async (event) => {
  // Query params: /api/search?q=hello
  const { q } = getQuery(event);

  // Request body (POST/PUT/PATCH)
  const body = await readBody(event);

  // Headers
  const auth = getHeader(event, "authorization");

  // Cookies
  const session = getCookie(event, "session");

  return { q, body };
});
```

## Setting Response

```ts
import { defineHandler, setResponseStatus, setHeader, setCookie } from "nitro/h3";

export default defineHandler((event) => {
  setResponseStatus(event, 201);
  setHeader(event, "X-Custom", "value");
  setCookie(event, "token", "abc123", { httpOnly: true });
  return { created: true };
});
```

## Streaming Responses

```ts
export default defineHandler(() => {
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(new TextEncoder().encode("chunk1"));
      controller.enqueue(new TextEncoder().encode("chunk2"));
      controller.close();
    },
  });
  return stream;
});
```

## Environment-Specific Routes

```
routes/debug.get.dev.ts       → only in development
routes/optimized.get.prod.ts  → only in production
routes/seo.get.prerender.ts   → only during prerender
```

## Server Fetch (Internal Calls)

Call routes internally without HTTP:

```ts
import { fetch } from "nitro";

export default defineHandler(async () => {
  const data = await fetch("/api/users").then(r => r.json());
  return { users: data };
});
```

## Route Rules (Config-Based)

Define behavior for route patterns in config without writing handlers:

```ts
// nitro.config.ts
export default defineNitroConfig({
  routeRules: {
    // Caching
    "/api/cached/**": { cache: { maxAge: 600 } },
    "/blog/**": { swr: 600 },
    "/static/**": { isr: { expiration: 3600 } },

    // Redirects
    "/old": { redirect: "/new" },
    "/old/**": { redirect: "/new/**" },
    "/moved": { redirect: { to: "https://other.com", statusCode: 308 } },

    // Proxy
    "/proxy/**": { proxy: "https://api.example.com/**" },

    // Headers
    "/api/**": { cors: true, headers: { "cache-control": "no-cache" } },

    // Prerender
    "/about": { prerender: true },
  },
});
```

## Route Metadata (Experimental)

Define OpenAPI metadata for routes:

```ts
import { defineRouteMeta } from "nitro";

defineRouteMeta({
  openAPI: {
    tags: ["users"],
    summary: "Get user by ID",
    parameters: [{ in: "path", name: "id", required: true }],
  },
});

export default defineHandler((event) => {
  return { id: event.context.params!.id };
});
```

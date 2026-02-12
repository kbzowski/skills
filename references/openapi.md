# OpenAPI Reference

Nitro can auto-generate OpenAPI 3.1.0 specifications from route handlers and serve interactive API documentation via Scalar or Swagger UI.

Full docs: https://v3.nitro.build/guide/openapi

## Enable

```ts
// nitro.config.ts
export default defineNitroConfig({
  experimental: { openAPI: true },
});
```

## Configuration

```ts
// nitro.config.ts
export default defineNitroConfig({
  experimental: { openAPI: true },
  openAPI: {
    // API metadata
    meta: {
      title: "My API",
      description: "API documentation",
      version: "1.0.0",
    },

    // OpenAPI JSON endpoint (default: "/_openapi.json")
    route: "/_openapi.json",

    // Production behavior:
    //   false (default) — disabled in production
    //   "runtime" — generated at runtime
    //   "prerender" — generated at build time (static JSON)
    production: "prerender",

    // Interactive UI configuration
    ui: {
      scalar: {
        route: "/_scalar",  // Scalar UI endpoint
      },
      swagger: {
        route: "/_swagger", // Swagger UI endpoint
      },
    },
  },
});
```

## Route Metadata

Define OpenAPI metadata per route using `defineRouteMeta()`:

```ts
// routes/api/users/[id].get.ts
import { defineRouteMeta } from "nitro";
import { defineHandler } from "nitro/h3";

defineRouteMeta({
  openAPI: {
    tags: ["Users"],
    summary: "Get user by ID",
    description: "Returns a single user by their unique identifier",
    parameters: [
      {
        in: "path",
        name: "id",
        required: true,
        schema: { type: "string" },
        description: "User ID",
      },
    ],
    responses: {
      200: {
        description: "User found",
        content: {
          "application/json": {
            schema: {
              type: "object",
              properties: {
                id: { type: "string" },
                name: { type: "string" },
                email: { type: "string", format: "email" },
              },
            },
          },
        },
      },
      404: { description: "User not found" },
    },
  },
});

export default defineHandler((event) => {
  const id = event.context.params!.id;
  return { id, name: "John", email: "john@example.com" };
});
```

## Auto-Generated Features

Without any `defineRouteMeta`, Nitro still generates:

- **Paths** from file-based routes (`routes/api/users.ts` → `GET /api/users`)
- **Path parameters** from dynamic segments (`[id]` → `{id}` parameter)
- **HTTP methods** from file suffixes (`.get.ts`, `.post.ts`)
- **Tags** based on route path structure (`/api/**` → "API Routes")

## Dev Endpoints

In development mode, the following endpoints are available:

| Endpoint | Description |
|----------|-------------|
| `/_openapi.json` | OpenAPI 3.1.0 JSON spec |
| `/_scalar` | Scalar interactive UI |
| `/_swagger` | Swagger interactive UI |

## Example: Full API with OpenAPI

```ts
// routes/api/posts/index.get.ts
import { defineRouteMeta } from "nitro";

defineRouteMeta({
  openAPI: {
    tags: ["Posts"],
    summary: "List all posts",
    parameters: [
      { in: "query", name: "page", schema: { type: "integer", default: 1 } },
      { in: "query", name: "limit", schema: { type: "integer", default: 10 } },
    ],
  },
});

export default defineHandler(async (event) => {
  const { page, limit } = getQuery(event);
  return { posts: [], page, limit };
});
```

```ts
// routes/api/posts/index.post.ts
import { defineRouteMeta } from "nitro";

defineRouteMeta({
  openAPI: {
    tags: ["Posts"],
    summary: "Create a new post",
    requestBody: {
      required: true,
      content: {
        "application/json": {
          schema: {
            type: "object",
            required: ["title", "content"],
            properties: {
              title: { type: "string" },
              content: { type: "string" },
              published: { type: "boolean", default: false },
            },
          },
        },
      },
    },
  },
});

export default defineHandler(async (event) => {
  const body = await readBody(event);
  return { id: "new-id", ...body };
});
```

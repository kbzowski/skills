# H3 Utilities Reference

All utilities available via `import { ... } from "nitro/h3"`. Nitro re-exports the full H3 API.

Full H3 docs: https://h3.unjs.io

## Handler Definition

```ts
import { defineHandler, defineWebSocketHandler } from "nitro/h3";

// Basic handler
export default defineHandler((event) => {
  return { ok: true };
});

// Async handler
export default defineHandler(async (event) => {
  const data = await fetchData();
  return data;
});

// WebSocket handler
export default defineWebSocketHandler({
  open(peer) {},
  message(peer, msg) {},
  close(peer) {},
});
```

| Function | Description |
|----------|-------------|
| `defineHandler(fn)` | Define route handler |
| `defineEventHandler(fn)` | Alias for defineHandler |
| `defineLazyEventHandler(fn)` | Lazy-loaded handler (resolved on first request) |
| `defineMiddleware(fn)` | Define middleware handler |
| `defineWebSocketHandler(hooks)` | Define WebSocket handler |

## Request — Reading Query & Params

```ts
import { defineHandler, getQuery, getRouterParams, getRouterParam } from "nitro/h3";

export default defineHandler((event) => {
  // GET /api/users/42?sort=name&limit=10
  const query = getQuery(event);              // { sort: "name", limit: "10" }
  const params = getRouterParams(event);      // { id: "42" }
  const id = getRouterParam(event, "id");     // "42"
  // Or via context:
  const id2 = event.context.params!.id;       // "42"
  return { query, id };
});
```

| Function | Description |
|----------|-------------|
| `getQuery(event)` | Parse URL query parameters |
| `getRouterParams(event)` | Get all route params |
| `getRouterParam(event, name)` | Get single route param |

## Request — Reading Body

```ts
import { defineHandler, readBody, readRawBody, readFormData, readMultipartFormData } from "nitro/h3";

export default defineHandler(async (event) => {
  // JSON body
  const json = await readBody(event);

  // Raw body as string/Buffer
  const raw = await readRawBody(event);

  // FormData (multipart/form-data or application/x-www-form-urlencoded)
  const form = await readFormData(event);

  // Multipart form data with file uploads
  const parts = await readMultipartFormData(event);
  // parts = [{ name, filename, type, data (Buffer) }, ...]
});
```

| Function | Description |
|----------|-------------|
| `readBody(event)` | Parse request body (JSON, form, text) |
| `readRawBody(event, encoding?)` | Raw body as string or Buffer |
| `readFormData(event)` | Parse as Web FormData |
| `readMultipartFormData(event)` | Parse multipart uploads |

## Request — Headers & Method

```ts
import { defineHandler, getRequestHeader, getRequestHeaders, getRequestMethod, getRequestURL, getRequestIP } from "nitro/h3";

export default defineHandler((event) => {
  const auth = getRequestHeader(event, "authorization");
  const allHeaders = getRequestHeaders(event);
  const method = getRequestMethod(event);        // "GET", "POST", etc.
  const url = getRequestURL(event);              // URL object
  const ip = getRequestIP(event, { xForwardedFor: true });
  return { method, ip };
});
```

| Function | Description |
|----------|-------------|
| `getRequestHeader(event, name)` | Get single request header |
| `getRequestHeaders(event)` | Get all request headers |
| `getRequestMethod(event)` | Get HTTP method |
| `getRequestURL(event)` | Get full request URL |
| `getRequestIP(event, opts?)` | Get client IP address |

## Request — Cookies

```ts
import { defineHandler, getCookie, parseCookies } from "nitro/h3";

export default defineHandler((event) => {
  const session = getCookie(event, "session_id");
  const all = parseCookies(event);               // { session_id: "abc", theme: "dark" }
  return { session };
});
```

| Function | Description |
|----------|-------------|
| `getCookie(event, name)` | Get single cookie value |
| `parseCookies(event)` | Parse all cookies |

## Response — Status & Headers

```ts
import { defineHandler, setResponseStatus, setHeader, appendHeader, removeResponseHeader } from "nitro/h3";

export default defineHandler((event) => {
  setResponseStatus(event, 201, "Created");
  setHeader(event, "X-Custom", "value");
  setHeader(event, "Cache-Control", "max-age=3600");
  appendHeader(event, "Set-Cookie", "a=1");
  appendHeader(event, "Set-Cookie", "b=2");
  return { created: true };
});
```

| Function | Description |
|----------|-------------|
| `setResponseStatus(event, code, text?)` | Set HTTP status code |
| `setHeader(event, name, value)` | Set response header |
| `appendHeader(event, name, value)` | Append header value (e.g. multiple Set-Cookie) |
| `removeResponseHeader(event, name)` | Remove response header |

## Response — Cookies

```ts
import { defineHandler, setCookie, deleteCookie } from "nitro/h3";

export default defineHandler((event) => {
  setCookie(event, "token", "abc123", {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    maxAge: 60 * 60 * 24, // 1 day
    path: "/",
  });
  deleteCookie(event, "old_token");
  return { ok: true };
});
```

| Function | Description |
|----------|-------------|
| `setCookie(event, name, value, opts?)` | Set cookie with options |
| `deleteCookie(event, name, opts?)` | Delete cookie |

## Response — Special Responses

```ts
import { defineHandler, sendRedirect, sendNoContent, html } from "nitro/h3";

// Redirect
export default defineHandler((event) => {
  return sendRedirect(event, "/new-location", 301);
});

// No Content (204)
export default defineHandler((event) => {
  return sendNoContent(event);
});

// HTML response
export default defineHandler((event) => {
  return html(event, "<h1>Hello</h1>");
});
```

| Function | Description |
|----------|-------------|
| `sendRedirect(event, location, code?)` | Send redirect response |
| `sendNoContent(event, code?)` | Send empty 204 response |
| `html(event, html)` | Send HTML with correct content-type |
| `sendStream(event, stream)` | Send ReadableStream |
| `sendFile(event, filepath)` | Send file from disk |

## Error Handling

```ts
import { defineHandler, createError } from "nitro/h3";

export default defineHandler((event) => {
  const id = event.context.params?.id;

  if (!id) {
    throw createError({
      statusCode: 400,
      statusMessage: "Bad Request",
      message: "The 'id' parameter is required",
      data: { field: "id" }, // optional extra data
    });
  }

  const user = findUser(id);
  if (!user) {
    throw createError({ statusCode: 404, message: "User not found" });
  }

  return user;
});
```

| Function | Description |
|----------|-------------|
| `createError(opts)` | Create HTTP error to throw |
| `HTTPError` | Error class for HTTP errors |
| `sendError(event, error)` | Send error response manually |
| `isError(value)` | Check if value is an H3 error |

## Proxy

```ts
import { defineHandler, proxyRequest, sendProxy } from "nitro/h3";

export default defineHandler((event) => {
  return proxyRequest(event, "https://api.example.com" + event.path, {
    headers: { "X-Forwarded-For": getRequestIP(event) },
  });
});
```

| Function | Description |
|----------|-------------|
| `proxyRequest(event, target, opts?)` | Proxy entire request to target |
| `sendProxy(event, target, opts?)` | Lower-level proxy |

## Validation

```ts
import { defineHandler, getValidatedQuery, readValidatedBody } from "nitro/h3";

export default defineHandler(async (event) => {
  // Validate with any schema library (zod, valibot, etc.)
  const query = await getValidatedQuery(event, (data) => {
    if (!data.page) throw createError({ statusCode: 400, message: "page required" });
    return { page: Number(data.page) };
  });

  const body = await readValidatedBody(event, myZodSchema.parse);
  return { query, body };
});
```

| Function | Description |
|----------|-------------|
| `getValidatedQuery(event, validate)` | Get and validate query params |
| `readValidatedBody(event, validate)` | Read and validate body |

## Conversion Utilities

| Function | Description |
|----------|-------------|
| `toRequest(event)` | Convert H3Event to Web Request |
| `toResponse(event)` | Convert to Web Response |
| `fromNodeHandler(handler)` | Convert Node.js handler to H3 |
| `toNodeHandler(app)` | Convert H3 app to Node.js handler |
| `isHTTPEvent(event)` | Check if event is HTTP event |

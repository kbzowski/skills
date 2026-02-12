# SSR Patterns Reference

Nitro integrates with Vite to enable server-side rendering with any framework.

## Vite Config for SSR

All SSR setups share a common Vite configuration pattern with separate client and SSR environments:

```ts
// vite.config.ts
import { defineConfig } from "vite";
import { nitro } from "nitro/vite";

export default defineConfig({
  plugins: [nitro()],
  environments: {
    client: {
      build: {
        rollupOptions: { input: "./src/entry-client.tsx" },
      },
    },
    ssr: {
      build: {
        rollupOptions: { input: "./src/entry-server.tsx" },
      },
    },
  },
});
```

## Server Entry Pattern

The `server.ts` file handles SSR by importing the server entry and rendering HTML:

```ts
// server.ts
export default {
  async fetch(request: Request): Promise<Response | void> {
    const url = new URL(request.url);

    // Only SSR for non-API, non-asset routes
    if (url.pathname.startsWith("/api/") || url.pathname.includes(".")) {
      return; // let Nitro handle API routes and static files
    }

    // Import server entry (built by Vite SSR environment)
    const { render } = await import("./src/entry-server");
    return render(request);
  },
};
```

## Asset Imports

Nitro provides special query parameters for importing asset metadata from Vite builds:

```ts
// In server entry
import clientAssets from "./src/entry-client?assets=client";
import ssrAssets from "./src/entry-server?assets=ssr";

// Assets contain CSS/JS links for the HTML shell
// clientAssets.styles = ['<link rel="stylesheet" href="/assets/style.css">']
// clientAssets.scripts = ['<script type="module" src="/assets/entry-client.js"></script>']
```

---

## React SSR

### Server Entry

```tsx
// src/entry-server.tsx
import { renderToReadableStream } from "react-dom/server.edge";
import { App } from "./App";
import clientAssets from "./entry-client?assets=client";
import ssrAssets from "./entry-server?assets=ssr";

export async function render(request: Request): Promise<Response> {
  const assets = { ...clientAssets, ...ssrAssets };

  const stream = await renderToReadableStream(
    <html>
      <head>
        <meta charSet="utf-8" />
        {assets.styles?.map((s, i) => (
          <link key={i} rel="stylesheet" href={s} />
        ))}
      </head>
      <body>
        <div id="root">
          <App url={request.url} />
        </div>
        {assets.scripts?.map((s, i) => (
          <script key={i} type="module" src={s} />
        ))}
      </body>
    </html>
  );

  return new Response(stream, {
    headers: { "Content-Type": "text/html" },
  });
}
```

### Client Entry

```tsx
// src/entry-client.tsx
import { hydrateRoot } from "react-dom/client";
import { App } from "./App";

hydrateRoot(
  document.getElementById("root")!,
  <App url={window.location.href} />
);
```

### Vite Config

```ts
// vite.config.ts
import { defineConfig } from "vite";
import { nitro } from "nitro/vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react(), nitro()],
  environments: {
    client: { build: { rollupOptions: { input: "./src/entry-client.tsx" } } },
    ssr: { build: { rollupOptions: { input: "./src/entry-server.tsx" } } },
  },
});
```

---

## Vue SSR

### Server Entry

```ts
// src/entry-server.ts
import { createSSRApp } from "vue";
import { renderToString } from "vue/server-renderer";
import { App } from "./App.vue";
import clientAssets from "./entry-client?assets=client";
import ssrAssets from "./entry-server?assets=ssr";

export async function render(request: Request): Promise<Response> {
  const app = createSSRApp(App);
  const assets = { ...clientAssets, ...ssrAssets };

  const html = await renderToString(app);

  const page = `<!DOCTYPE html>
<html>
  <head>${(assets.styles || []).join("")}</head>
  <body>
    <div id="app">${html}</div>
    ${(assets.scripts || []).join("")}
  </body>
</html>`;

  return new Response(page, {
    headers: { "Content-Type": "text/html" },
  });
}
```

### Client Entry

```ts
// src/entry-client.ts
import { createSSRApp } from "vue";
import { App } from "./App.vue";

const app = createSSRApp(App);
app.mount("#app");
```

### Vue Router SSR

For apps with Vue Router, use `createMemoryHistory` on server and `createWebHistory` on client:

```ts
// Server
import { createRouter, createMemoryHistory } from "vue-router";
const router = createRouter({
  history: createMemoryHistory(),
  routes: [/* ... */],
});
app.use(router);
await router.push(url.pathname);
await router.isReady();

// Client
import { createRouter, createWebHistory } from "vue-router";
const router = createRouter({
  history: createWebHistory(),
  routes: [/* ... */],
});
app.use(router);
router.isReady().then(() => app.mount("#app"));
```

---

## Solid SSR

### Server Entry

```tsx
// src/entry-server.tsx
import { renderToStringAsync } from "solid-js/web";
import { HydrationScript } from "solid-js/web";
import { App } from "./App";
import clientAssets from "./entry-client?assets=client";
import ssrAssets from "./entry-server?assets=ssr";

export async function render(request: Request): Promise<Response> {
  const assets = { ...clientAssets, ...ssrAssets };

  const appHtml = await renderToStringAsync(() => <App url={request.url} />);

  const shellHtml = await renderToStringAsync(() => (
    <html>
      <head>
        <HydrationScript />
        {assets.styles?.map((s) => <link rel="stylesheet" href={s} />)}
      </head>
      <body>
        <div id="app" innerHTML={appHtml} />
        {assets.scripts?.map((s) => <script type="module" src={s} />)}
      </body>
    </html>
  ));

  return new Response(shellHtml, {
    headers: { "Content-Type": "text/html" },
  });
}
```

### Client Entry

```tsx
// src/entry-client.tsx
import { hydrate } from "solid-js/web";
import { App } from "./App";

hydrate(() => <App url={window.location.href} />, document.getElementById("app")!);
```

---

## Key Points

- Server entry uses `renderToReadableStream` (React) or `renderToString` (Vue/Solid) for SSR
- Client entry hydrates the server-rendered HTML
- Asset metadata (`?assets=client` / `?assets=ssr`) provides CSS/JS links for the HTML shell
- `server.ts` acts as the glue connecting Nitro routing with framework SSR
- API routes in `routes/` work alongside SSR without conflicts
- Both streaming and string-based rendering are supported

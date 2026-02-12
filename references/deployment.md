# Deployment & Configuration Reference

Full docs: https://v3.nitro.build/deploy

## Overview

Nitro auto-detects the deployment target and builds accordingly. Override with `NITRO_PRESET` env var or config.

## Setting Preset

```bash
# Via environment variable
NITRO_PRESET=cloudflare_pages npm run build

# Via config
export default defineNitroConfig({
  preset: "cloudflare_pages",
});
```

## Available Presets

### Runtimes

| Preset | Description |
|--------|-------------|
| `node_server` | Node.js standalone server (default) |
| `node_cluster` | Node.js cluster mode |
| `node` | Node.js middleware |
| `bun` | Bun runtime |
| `deno_server` | Deno server |
| `deno_deploy` | Deno Deploy |

### Serverless / Edge

| Preset | Description |
|--------|-------------|
| `aws_lambda` | AWS Lambda |
| `aws_amplify` | AWS Amplify Hosting |
| `cloudflare_module` | Cloudflare Workers |
| `cloudflare_pages` | Cloudflare Pages |
| `netlify` | Netlify Functions |
| `netlify_edge` | Netlify Edge Functions |
| `vercel` | Vercel Serverless |
| `vercel_edge` | Vercel Edge Functions |
| `firebase_app_hosting` | Firebase App Hosting |

### PaaS / Hosting

| Preset | Description |
|--------|-------------|
| `azure_swa` | Azure Static Web Apps |
| `azure` | Azure Functions |
| `digital_ocean` | DigitalOcean App Platform |
| `heroku` | Heroku |
| `flightcontrol` | Flightcontrol |
| `genezio` | Genezio |
| `iis` | IIS (Windows) |
| `koyeb` | Koyeb |
| `render_com` | Render |
| `stormkit` | Stormkit |
| `zeabur` | Zeabur |
| `zerops` | Zerops |
| `platform_sh` | Platform.sh |
| `alwaysdata` | Alwaysdata |
| `cleavr` | Cleavr |

### Static

| Preset | Description |
|--------|-------------|
| `github_pages` | GitHub Pages |
| `static` | Static site generation |

---

## Node.js Deployment (Default)

Build output: `.output/` directory with standalone server.

```bash
# Build
npm run build

# Run
node .output/server/index.mjs
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NITRO_PORT` / `PORT` | Server port | `3000` |
| `NITRO_HOST` / `HOST` | Server host | `0.0.0.0` |
| `NITRO_UNIX_SOCKET` | Unix socket path | — |
| `NITRO_SSL_CERT` | SSL certificate path | — |
| `NITRO_SSL_KEY` | SSL key path | — |
| `NITRO_SHUTDOWN_TIMEOUT` | Graceful shutdown timeout (ms) | `30000` |
| `NITRO_SHUTDOWN_FORCE_TIMEOUT` | Force shutdown timeout (ms) | `3000` |
| `NITRO_SHUTDOWN_SIGNALS` | Comma-separated signals | `SIGTERM,SIGINT` |

---

## Cloudflare Deployment

```ts
// nitro.config.ts
export default defineNitroConfig({
  preset: "cloudflare_pages",
});
```

### Cloudflare Bindings

Access KV, R2, D1, etc. via `event.context.cloudflare`:

```ts
export default defineHandler((event) => {
  const { env, context } = event.context.cloudflare;
  const kv = env.MY_KV_NAMESPACE;
  // Use KV, R2, D1, etc.
});
```

### Wrangler Config

```toml
# wrangler.toml
name = "my-app"
compatibility_date = "2024-01-01"

[[kv_namespaces]]
binding = "MY_KV"
id = "xxx"
```

---

## Vercel Deployment

```ts
export default defineNitroConfig({
  preset: "vercel",
});
```

Nitro auto-generates `vercel.json` configuration.

---

## Netlify Deployment

```ts
export default defineNitroConfig({
  preset: "netlify",
});
```

---

## AWS Lambda

```ts
export default defineNitroConfig({
  preset: "aws_lambda",
  // Enable streaming (optional)
  awsLambda: { streaming: true },
});
```

---

## Configuration Reference

Full config in `nitro.config.ts` or `vite.config.ts` (under `nitro` key):

```ts
import { defineNitroConfig } from "nitro/config";

export default defineNitroConfig({
  // === Directories ===
  serverDir: false,               // set to "./" or "server" for dir-based layout
  scanDirs: [],                   // additional dirs to scan for routes/middleware/plugins
  buildDir: "node_modules/.nitro",
  output: {
    dir: ".output",
    serverDir: ".output/server",
    publicDir: ".output/public",
  },

  // === Runtime ===
  runtimeConfig: {},
  routeRules: {},
  handlers: [],
  plugins: [],
  errorHandler: undefined,        // path to custom error handler

  // === Features ===
  features: {
    runtimeHooks: true,
    websocket: false,
  },
  experimental: {
    asyncContext: false,
    database: false,
    tasks: false,
    openAPI: false,
    envExpansion: false,
    websocket: false,
  },

  // === Storage & Data ===
  storage: {},
  devStorage: {},
  database: {},
  devDatabase: {},

  // === Tasks ===
  tasks: {},
  scheduledTasks: {},

  // === Build ===
  preset: undefined,              // auto-detected or manual
  minify: true,
  sourcemap: false,
  entry: undefined,               // custom entry file
  baseURL: "/",

  // === Prerender ===
  prerender: {
    routes: [],
    crawlLinks: false,
    concurrency: 1,
    retry: 3,
    retryDelay: 500,
  },

  // === Assets ===
  publicAssets: [],
  serverAssets: [],

  // === Advanced ===
  hooks: {},
  virtual: {},
  imports: false,                 // auto-imports config (unimport)
});
```

## Vite Integration

```ts
// vite.config.ts
import { defineConfig } from "vite";
import { nitro } from "nitro/vite";

export default defineConfig({
  plugins: [nitro()],
  nitro: {
    // All nitro config options available here
    routeRules: { "/api/**": { cors: true } },
  },
});
```

## Standalone Config

```ts
// nitro.config.ts
import { defineNitroConfig } from "nitro/config";

export default defineNitroConfig({
  // config here
});
```

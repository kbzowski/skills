# Caching, Storage & Database Reference

## Caching

Full docs: https://v3.nitro.build/guide/cache

### Cached Handlers

Wrap route handlers with automatic response caching:

```ts
import { defineCachedHandler } from "nitro/cache";

export default defineCachedHandler(
  (event) => {
    return { timestamp: Date.now(), data: "expensive computation" };
  },
  {
    maxAge: 60 * 60, // 1 hour in seconds
    swr: true, // stale-while-revalidate
    staleMaxAge: 60 * 60 * 24, // serve stale for up to 24h while revalidating
  }
);
```

### Cached Functions

Cache any async function result:

```ts
import { defineCachedFunction } from "nitro/cache";

const getRepoStars = defineCachedFunction(
  async (repo: string) => {
    const data = await fetch(`https://api.github.com/repos/${repo}`).then((r) =>
      r.json()
    );
    return { stars: data.stargazers_count };
  },
  {
    maxAge: 3600,
    name: "ghStars",
    getKey: (repo) => repo, // cache key based on argument
  }
);

// Usage in handler:
export default defineHandler(async () => {
  return await getRepoStars("unjs/nitro");
});
```

### Cache Options

```ts
{
  name?: string;              // Cache name (for grouping)
  group?: string;             // Cache group prefix
  getKey?: (...args) => string; // Custom cache key generator
  maxAge?: number;            // TTL in seconds
  swr?: boolean | number;     // Stale-while-revalidate (true or seconds)
  staleMaxAge?: number;       // Max stale age in seconds
  base?: string;              // Storage base for cache data
  shouldBypassCache?: (...args) => boolean;     // Skip cache lookup
  shouldInvalidateCache?: (...args) => boolean; // Force refresh
  varies?: string[];          // Vary by request headers (handler only)
}
```

### Route Rule Caching

Configure caching via config without code changes:

```ts
// nitro.config.ts
export default defineNitroConfig({
  routeRules: {
    "/api/data/**": { cache: { maxAge: 600 } },
    "/blog/**": { swr: 600 },       // shorthand for stale-while-revalidate
    "/pages/**": { isr: { expiration: 3600 } }, // ISR mode
  },
});
```

---

## Storage

Full docs: https://v3.nitro.build/guide/storage

Nitro uses [unstorage](https://unstorage.unjs.io) for runtime-agnostic key-value storage.

### Basic Usage

```ts
import { useStorage } from "nitro/storage";

export default defineHandler(async () => {
  const storage = useStorage();

  // Set value
  await storage.setItem("users:1", { name: "John", age: 30 });

  // Get value
  const user = await storage.getItem("users:1");

  // Check existence
  const exists = await storage.hasItem("users:1");

  // List keys
  const keys = await storage.getKeys("users");

  // Remove
  await storage.removeItem("users:1");

  // Clear namespace
  await storage.clear("users");

  return { user, keys };
});
```

### Namespaced Storage

```ts
// Access specific mount point
const redis = useStorage("redis");
await redis.setItem("session:abc", { userId: 1 });

// Access server assets (read-only, bundled at build)
const assets = useStorage("assets:server");
const template = await assets.getItem("templates/email.html");
```

### Storage Configuration

```ts
// nitro.config.ts
export default defineNitroConfig({
  storage: {
    redis: {
      driver: "redis",
      url: "redis://localhost:6379",
    },
    s3: {
      driver: "s3",
      bucket: "my-bucket",
      region: "us-east-1",
    },
    fs: {
      driver: "fs",
      base: "./data",
    },
  },
  // Dev-only storage (won't affect production)
  devStorage: {
    redis: {
      driver: "fs",
      base: "./.data/redis",
    },
  },
});
```

### Available Storage Drivers

Common unstorage drivers: `memory`, `fs`, `redis`, `s3`, `cloudflare-kv-binding`, `cloudflare-r2-binding`, `azure-storage-table`, `azure-storage-blob`, `mongodb`, `http`, `lru-cache`, `vercel-kv`.

Full list: https://unstorage.unjs.io/drivers

### Server Assets

Bundle static files accessible at runtime:

```ts
// nitro.config.ts
export default defineNitroConfig({
  serverAssets: [
    { baseName: "templates", dir: "./server/templates" },
    { baseName: "data", dir: "./server/data" },
  ],
});
```

```ts
// In handler
const assets = useStorage("assets:server");
const html = await assets.getItem("templates:welcome.html");
const config = await assets.getItem("data:defaults.json");
```

---

## Database (Experimental)

Full docs: https://v3.nitro.build/guide/database

Nitro integrates [db0](https://db0.unjs.io) for SQL database access.

### Enable

```ts
// nitro.config.ts
export default defineNitroConfig({
  experimental: { database: true },
});
```

### Usage

```ts
import { useDatabase } from "nitro/database";

export default defineHandler(async () => {
  const db = useDatabase(); // "default" connection

  // SQL template literals (safe from injection)
  const userId = 1;
  const { rows } = await db.sql`SELECT * FROM users WHERE id = ${userId}`;

  // Insert
  await db.sql`INSERT INTO users (name, email) VALUES (${"John"}, ${"john@example.com"})`;

  return { rows };
});
```

### Multiple Connections

```ts
// nitro.config.ts
export default defineNitroConfig({
  experimental: { database: true },
  database: {
    default: {
      connector: "sqlite",
      options: { name: "db" }, // .data/db.sqlite
    },
    analytics: {
      connector: "postgresql",
      options: { url: process.env.PG_URL },
    },
  },
});
```

```ts
// In handler
const mainDb = useDatabase();          // default
const analyticsDb = useDatabase("analytics");
```

### Dev Database Override

```ts
// nitro.config.ts
export default defineNitroConfig({
  devDatabase: {
    default: {
      connector: "sqlite",
      options: { name: "dev-db" },
    },
  },
});
```

### Supported Connectors

db0 connectors: `sqlite`, `libsql`, `postgresql`, `mysql`, `d1` (Cloudflare), `pglite`, `bun:sqlite`.

Full list: https://db0.unjs.io/connectors

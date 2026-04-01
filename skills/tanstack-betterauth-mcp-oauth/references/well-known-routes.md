# Well-Known Discovery Routes

These are Nitro (h3) routes served at the domain root. They MUST live in `server/routes/`,
not as TanStack Start file routes.

## File 1: `server/routes/.well-known/oauth-authorization-server.get.ts`

MCP clients discover the OAuth server by looking here first.

```typescript
import { oauthProviderAuthServerMetadata } from '@better-auth/oauth-provider'
import { defineEventHandler, setResponseHeader, toRequest } from 'h3'
import { auth } from '@/server/auth'

// biome-ignore lint/suspicious/noExplicitAny: Better Auth plugin generic constraint mismatch — safe because oauthProvider is installed
const handler = oauthProviderAuthServerMetadata(auth as any)

// MCP spec: clients construct this URL by stripping the path from the MCP
// server URL, so it MUST be served at the domain root regardless of where
// Better Auth's basePath is.
export default defineEventHandler(async (event) => {
  setResponseHeader(event, 'Access-Control-Allow-Origin', '*')
  setResponseHeader(event, 'Access-Control-Allow-Methods', 'GET, OPTIONS')
  setResponseHeader(event, 'Access-Control-Allow-Headers', 'Content-Type, MCP-Protocol-Version')
  const request = toRequest(event)
  return handler(request)
})
```

## File 2: `server/routes/.well-known/oauth-authorization-server/api/auth.get.ts`

RFC 8414 requires the metadata also at `/.well-known/oauth-authorization-server/{issuer-path}`.
Since Better Auth's default basePath is `/api/auth`, this goes at `.../api/auth.get.ts`.

The handler is identical to File 1 — same imports, same code. Only the file path differs.

If the project uses a different auth basePath (e.g., `/auth`), adjust the directory structure
accordingly: `server/routes/.well-known/oauth-authorization-server/auth.get.ts`.

```typescript
// Same as File 1 — identical implementation at a different path
import { oauthProviderAuthServerMetadata } from '@better-auth/oauth-provider'
import { defineEventHandler, setResponseHeader, toRequest } from 'h3'
import { auth } from '@/server/auth'

const handler = oauthProviderAuthServerMetadata(auth as any)

export default defineEventHandler(async (event) => {
  setResponseHeader(event, 'Access-Control-Allow-Origin', '*')
  setResponseHeader(event, 'Access-Control-Allow-Methods', 'GET, OPTIONS')
  setResponseHeader(event, 'Access-Control-Allow-Headers', 'Content-Type, MCP-Protocol-Version')
  const request = toRequest(event)
  return handler(request)
})
```

## File 3: `server/routes/.well-known/oauth-protected-resource.get.ts`

Tells MCP clients what scopes the resource server supports and where to authenticate.

```typescript
import { oauthProviderResourceClient } from '@better-auth/oauth-provider/resource-client'
import { defineEventHandler, setResponseHeader } from 'h3'
import { auth } from '@/server/auth'
import { env } from '@/server/env'

// biome-ignore lint/suspicious/noExplicitAny: Better Auth plugin generic constraint mismatch — safe because oauthProvider is installed
const resourceClient = oauthProviderResourceClient(auth as any)
const { getProtectedResourceMetadata } = resourceClient.getActions()

export default defineEventHandler(async (event) => {
  const metadata = await getProtectedResourceMetadata(
    {
      resource: `${env.APP_URL}/api/mcp`,
      authorization_servers: [`${env.APP_URL}/api/auth`],
      scopes_supported: ['mcp:read', 'mcp:write', 'mcp:manage'],
    },
    { silenceWarnings: { oidcScopes: true } },
  )
  setResponseHeader(event, 'Access-Control-Allow-Origin', '*')
  setResponseHeader(event, 'Access-Control-Allow-Methods', 'GET, OPTIONS')
  setResponseHeader(event, 'Access-Control-Allow-Headers', 'Content-Type')
  setResponseHeader(event, 'Cache-Control', 'public, max-age=300, stale-while-revalidate=60')
  return metadata
})
```

## Adapting to Different Configurations

- **Different auth basePath**: Change the directory for File 2 to match. E.g., if basePath
  is `/auth`, the file goes at `server/routes/.well-known/oauth-authorization-server/auth.get.ts`.
- **Different MCP endpoint**: Change `resource` in File 3 to match.
- **Different scopes**: Change `scopes_supported` in File 3 to match your scope names.
- **Custom APP_URL source**: Adapt the env import to wherever your base URL is defined.

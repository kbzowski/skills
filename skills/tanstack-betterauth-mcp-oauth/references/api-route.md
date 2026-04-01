# MCP API Route

Create `src/routes/api/mcp.ts` — the HTTP handler for MCP JSON-RPC requests.

```typescript
import { oauthProviderResourceClient } from '@better-auth/oauth-provider/resource-client'
import { WebStandardStreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/webStandardStreamableHttp.js'
import { createFileRoute } from '@tanstack/react-router'
import type { JWTPayload } from 'jose'
import { auth } from '@/server/auth'
import { env } from '@/server/env'
import { jwtToMcpContext, type McpAuthContext } from '@/server/mcp/auth'
import { createMcpServer } from '@/server/mcp/server'

// biome-ignore lint/suspicious/noExplicitAny: Better Auth plugin generic constraint mismatch — safe because oauthProvider is installed
const resourceClient = oauthProviderResourceClient(auth as any)
const { verifyAccessToken } = resourceClient.getActions()

// MCP clients connect from various origins. Per MCP spec, the resource server
// must allow cross-origin requests. Auth is token-based, not cookies.
const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, DELETE, OPTIONS',
  'Access-Control-Allow-Headers':
    'Content-Type, Authorization, MCP-Protocol-Version',
  'Cache-Control': 'no-store',
} as const

function jsonRpcError(
  message: string,
  status: number,
  extraHeaders?: Record<string, string>,
) {
  return Response.json(
    { jsonrpc: '2.0', error: { code: -32000, message }, id: null },
    { status, headers: { ...CORS_HEADERS, ...extraHeaders } },
  )
}

/**
 * Extract client IP from request headers.
 * IMPORTANT: Only trust these headers when the server runs behind a reverse proxy
 * that overwrites them (nginx, Cloudflare, etc.). Direct clients can spoof them.
 * Used for display in session management, not for security decisions.
 */
function getClientIp(request: Request): string | undefined {
  return (
    request.headers.get('x-real-ip') ||
    request.headers.get('x-forwarded-for')?.split(',')[0]?.trim() ||
    undefined
  )
}

async function handleMcpRequest({ request }: { request: Request }) {
  const authHeader = request.headers.get('authorization')
  const token = authHeader?.startsWith('Bearer ')
    ? authHeader.slice(7)
    : undefined

  if (!token) {
    const resourceMetadataUrl = `${env.APP_URL}/.well-known/oauth-protected-resource`
    return jsonRpcError('Unauthorized: Authentication required', 401, {
      'WWW-Authenticate': `Bearer resource_metadata="${resourceMetadataUrl}"`,
      'Access-Control-Expose-Headers': 'WWW-Authenticate',
    })
  }

  let jwt: JWTPayload
  try {
    jwt = await verifyAccessToken(token, {
      verifyOptions: {
        audience: [env.APP_URL, `${env.APP_URL}/`, `${env.APP_URL}/api/mcp`],
        issuer: `${env.APP_URL}/api/auth`,
      },
      jwksUrl: `${env.APP_URL}/api/auth/jwks`,
    })
  } catch (err) {
    return jsonRpcError('Invalid or expired token', 401)
  }

  let authCtx: McpAuthContext
  try {
    authCtx = jwtToMcpContext(jwt, getClientIp(request))
  } catch (e) {
    return jsonRpcError((e as Error).message, 403)
  }

  // Rate limiting per user — use the project's existing rate limiter (e.g., limiter,
  // rate-limiter-flexible, upstash/ratelimit, or the framework's built-in middleware).
  // Key by userId so one user can't exhaust limits for others.
  const allowed = await checkRateLimit(`mcp:${authCtx.userId}`)
  if (!allowed) {
    return Response.json(
      { jsonrpc: '2.0', error: { code: -32000, message: 'Too many requests' }, id: null },
      { status: 429, headers: { ...CORS_HEADERS, 'Retry-After': '60' } },
    )
  }

  const mcpServer = createMcpServer(authCtx)
  const transport = new WebStandardStreamableHTTPServerTransport({
    sessionIdGenerator: undefined, // stateless — no server-side sessions
    enableJsonResponse: true,      // JSON mode, not SSE
  })

  await mcpServer.connect(transport)

  try {
    const response = await transport.handleRequest(request)
    for (const [key, value] of Object.entries(CORS_HEADERS)) {
      response.headers.set(key, value)
    }
    return response
  } finally {
    await mcpServer.close()
  }
}

export const Route = createFileRoute('/api/mcp')({
  server: {
    handlers: {
      GET: () =>
        Response.json(
          {
            error:
              'SSE transport is not supported. Use POST with JSON response.',
          },
          {
            status: 405,
            headers: { ...CORS_HEADERS, Allow: 'POST, DELETE, OPTIONS' },
          },
        ),
      POST: handleMcpRequest,
      // Sessions are disabled (stateless JSON mode) — DELETE is a no-op per MCP spec
      DELETE: () =>
        new Response(null, { status: 204, headers: { ...CORS_HEADERS } }),
      OPTIONS: () =>
        new Response(null, {
          status: 204,
          headers: { ...CORS_HEADERS, 'Access-Control-Max-Age': '86400' },
        }),
    },
  },
})
```

## Adaptation Notes

- **MCP endpoint path**: If using a path other than `/api/mcp`, change the `createFileRoute`
  path and all audience URL references
- **Auth base path**: If not `/api/auth`, adjust the `issuer` and `jwksUrl` values
- **Rate limiting**: Implement `checkRateLimit(key: string): Promise<boolean>` using the
  project's existing rate limiter. Common options:
  - **Better Auth's built-in** `rateLimit` plugin (already configured in Phase 3)
  - **rate-limiter-flexible** — `new RateLimiterMemory({ points: 60, duration: 60 })`
  - **@upstash/ratelimit** — for serverless/edge deployments
  - **Custom middleware** — adapt whatever the project already uses for API rate limiting
  If the project has no rate limiter, add one — this endpoint is the primary attack surface.
- **Logging**: Add your project's logger for token verification failures and unexpected errors
- **Environment**: Adapt `env.APP_URL` to wherever your base URL is configured

## Why These Design Decisions

**Stateless (new server per request):** MCP over HTTP doesn't require persistent sessions.
Creating a fresh McpServer per request simplifies the architecture — no session storage,
no cleanup, no stale state. The cost is minimal since McpServer is lightweight.

**`enableJsonResponse: true`:** The MCP SDK supports both SSE and JSON response modes.
SSE is for long-running streaming responses. For typical tool calls that return quickly,
JSON mode is simpler and more reliable across proxies and CDNs.

**`sessionIdGenerator: undefined`:** Disables the SDK's built-in session tracking. Combined
with stateless server creation, this means no session IDs in headers, no Mcp-Session-Id
negotiation. Each request is fully independent.

**CORS `*`:** MCP clients run from many origins — Claude Desktop, VS Code extensions,
browser-based editors. Token-based auth (not cookies) means `Access-Control-Allow-Origin: *`
is safe and required by the MCP specification.

**`WWW-Authenticate` on 401:** The MCP client discovery flow starts with a request to the
MCP endpoint. If it gets 401 with `resource_metadata="..."`, it knows where to find the
OAuth metadata. Without this header, clients have no way to discover the auth server.

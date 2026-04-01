---
name: tanstack-betterauth-mcp-oauth
description: >
  Adds a production-ready MCP (Model Context Protocol) server with OAuth 2.1 authorization
  to a TanStack Start + Better Auth project. Database-agnostic — works with any Better Auth
  adapter (Prisma, Drizzle, Kysely, Knex, MikroORM, MongoDB, etc.). Generates all layers:
  database schema, Better Auth OAuth provider config, well-known discovery endpoints,
  MCP API route with JWT verification, scope-based permissions, consent UI, session
  management, and E2E tests.
  Use when the user wants to add MCP, add an MCP server, add MCP OAuth, integrate AI tools
  with OAuth, expose tools via MCP, or connect Claude/Cursor/VS Code to their TanStack
  Start app. Also triggers on "MCP endpoint", "tool server", or "OAuth for AI clients"
  in a TanStack Start + Better Auth context.
---

# Add MCP Server with OAuth 2.1 to TanStack Start + Better Auth

Add a complete MCP server with OAuth 2.1 authorization to a TanStack Start + Better Auth
project. The end result is a stateless JSON-RPC endpoint that AI clients (Claude Code,
Claude Desktop, Cursor, VS Code, Windsurf, claude.ai) connect to via standard OAuth
flows with PKCE. Database-agnostic — works with any Better Auth adapter (Prisma, Drizzle,
Kysely, Knex, MikroORM, MongoDB, etc.).

## When to Use

- The project uses **TanStack Start** and **Better Auth**
- The user wants to add an MCP server, MCP endpoint, or MCP OAuth integration
- The user wants AI tools (Claude, Cursor, VS Code) to connect to their app
- The user mentions "tool server", "OAuth for AI clients", or "expose tools via MCP"

## When NOT to Use

- The project does **not** use TanStack Start — this skill relies on TanStack file routes
  and Nitro server routes
- The project does **not** use Better Auth — the OAuth provider plugin is Better Auth-specific
- The user wants SSE-based streaming MCP (this skill implements stateless JSON-RPC only)
- The user wants a standalone MCP server (not integrated into an existing web app)

## Architecture Overview

```
Client (Claude/Cursor/etc.)
  │
  ├─ GET  /.well-known/oauth-protected-resource     → discovers auth server
  ├─ GET  /.well-known/oauth-authorization-server    → gets OAuth metadata
  ├─ POST /api/auth/oauth2/register                  → dynamic client registration
  ├─ GET  /api/auth/oauth2/authorize                 → redirects to login → consent
  ├─ POST /api/auth/oauth2/token                     → exchanges code for JWT
  │
  └─ POST /api/mcp  (Bearer JWT)                     → MCP JSON-RPC endpoint
       ├─ verifyAccessToken (JWKS)
       ├─ jwtToMcpContext (userId, scopes, ip)
       ├─ createMcpServer with registered tools
       └─ WebStandardStreamableHTTPServerTransport (stateless JSON, no SSE)
```

**Files created (8-12 depending on options):**

| Layer | Path | Purpose |
|-------|------|---------|
| Database | Adapter-specific | McpScope type + 5 OAuth tables |
| Auth | Auth config file | `jwt()` + `oauthProvider()` plugins |
| Discovery | `server/routes/.well-known/` | 3 Nitro routes for OAuth metadata |
| MCP core | `src/server/mcp/` | auth, permissions, utils, server factory |
| API route | `src/routes/api/mcp.ts` | HTTP handler with JWT verification |
| Tools | `src/server/mcp/tools/` | Domain-specific MCP tools |
| Consent | `src/routes/oauth/consent.tsx` | OAuth consent page |
| Sessions | Admin route + server functions | Session management UI |
| Tests | `e2e/mcp-oauth.spec.ts` | Playwright E2E tests |

## Phase 0: Prerequisites

Verify the project has these foundations. Install anything missing.

**Required packages:**
```
@modelcontextprotocol/sdk    # MCP server SDK
@better-auth/oauth-provider  # OAuth 2.1 provider + resource client
jose                         # JWT verification
```

**Required project setup:**
- TanStack Start (with `createFileRoute`, server handlers)
- Better Auth (with any database adapter — Prisma, Drizzle, Kysely, Knex, MikroORM, MongoDB, etc.)
- Sessions stored in database (required for OAuth token lifecycle)
- A `server/routes/` directory for Nitro routes (create if missing)

**Detect existing patterns:**
- Find the Better Auth config file (usually `src/server/auth.ts`)
- **Identify the database adapter** (Prisma, Drizzle, Kysely, etc.) — this determines how
  to add OAuth tables in Phase 2
- Find the env/config file with `APP_URL` (needed for audience/issuer URLs)
- Check for existing rate limiting middleware
- Check the UI component library (shadcn/ui, etc.) for the consent page

## Phase 1: Gather Information

Ask the user:

1. **Project name** — used as MCP server name (e.g., "MyApp")
2. **Locale** — for consent page and error messages (default: English)
3. **MCP scopes** — default `read`, `write`, `manage` with hierarchy `manage > write > read`
4. **MCP endpoint path** — default `/api/mcp`
5. **Domain entities** — what tools to expose (e.g., "projects", "documents", "orders")
6. **Auth base path** — default `/api/auth`
7. **Whether to include session management** — recommended yes
8. **Whether to include E2E tests** — recommended yes

## Phase 2: Database Schema

Better Auth has its own migration CLI that can generate the OAuth tables automatically:

```bash
npx @better-auth/cli migrate   # applies migrations directly
npx @better-auth/cli generate  # generates migration files for manual review
```

**Recommended approach:**
1. First add the `oauthProvider` plugin to your Better Auth config (Phase 3)
2. Run `npx @better-auth/cli generate` to see what tables it wants to create
3. **Review the generated migration carefully** — Better Auth's CLI may rename or alter
   existing tables if it detects naming mismatches. Verify it doesn't break your schema.
4. Apply the migration
5. Then manually add performance indexes and fix cascade behavior (see below)

**After the auto-migration, verify and fix:**
- **Session FK must cascade on delete** on `oauthRefreshToken.sessionId` and
  `oauthAccessToken.sessionId`. Better Auth may generate these as SET NULL — change to
  CASCADE. Without this, logging out orphans tokens instead of cleaning them up.
- **Add indexes** on `clientId`, `userId`, `sessionId`, `expiresAt` columns for performance
  (see `references/database-schema.md` for the complete index list)
- Add `McpScope` type: enum in Prisma/Postgres, string literal union for other adapters

Read `references/database-schema.md` for the complete manual schema if you prefer full
control, or as a reference for what the auto-migration should produce. It includes
Prisma, Drizzle, and raw SQL variants.

## Phase 3: Better Auth Config

Add two plugins to the existing Better Auth config:

```typescript
import { oauthProvider } from '@better-auth/oauth-provider'
import { jwt } from 'better-auth/plugins/jwt'
```

Add to the `plugins` array:
```typescript
jwt(),
oauthProvider({
  loginPage: '/login',           // your login route
  consentPage: '/oauth/consent', // consent page we'll create in Phase 8
  scopes: [
    'openid', 'profile', 'email', 'offline_access',
    'mcp:read', 'mcp:write', 'mcp:manage',
  ],
  allowDynamicClientRegistration: true,
  allowUnauthenticatedClientRegistration: true,
  accessTokenExpiresIn: 300,      // 5 minutes
  refreshTokenExpiresIn: 604800,  // 7 days
  validAudiences: [
    env.APP_URL,
    `${env.APP_URL}/`,
    `${env.APP_URL}/api/mcp`,
  ],
  silenceWarnings: { oauthAuthServerConfig: true },
}),
```

Add a rate limit rule for client registration:
```typescript
'/oauth2/register': { window: 3600, max: 10 },
```

**Why these settings matter:**
- `allowUnauthenticatedClientRegistration` — MCP clients register themselves dynamically
  before the user has logged in. Without this, Claude/Cursor/etc. can't connect.
- `accessTokenExpiresIn: 300` — JWTs are self-contained and can't be individually revoked.
  Short TTL (5 min) limits the window after revocation where a token still works.
- `validAudiences` with multiple variants — different MCP clients may set the audience
  claim to the base URL, with trailing slash, or with the MCP path.

## Phase 4: Well-Known Discovery Routes

Read `references/well-known-routes.md` for the complete code.

These are the most pitfall-prone part of the integration. Three critical rules:

1. **Must be Nitro routes in `server/routes/`**, not TanStack Start file routes.
   MCP clients discover the auth server by stripping the path from the MCP URL and
   looking for `/.well-known/oauth-protected-resource` at the domain root. TanStack Start
   routes live under the app's routing — Nitro routes are served directly by the underlying
   server, which is what we need.

2. **Need both the MCP-spec path AND the RFC 8414 path.** Some clients look at
   `/.well-known/oauth-authorization-server` (MCP spec), others at
   `/.well-known/oauth-authorization-server/{auth-base-path}` (RFC 8414). Serve both.

3. **CORS on all endpoints.** `Access-Control-Allow-Origin: *` is required because MCP
   clients run from various origins. Auth is token-based, not cookie-based.

The `auth as any` cast on `oauthProviderAuthServerMetadata(auth)` and
`oauthProviderResourceClient(auth)` is required due to a generic constraint mismatch
in Better Auth's types. It's safe when the oauthProvider plugin is installed.

## Phase 5: MCP Core

Read `references/mcp-core.md` for the complete code for all 4 files.

Create `src/server/mcp/` with:

- **`auth.ts`** — `McpAuthContext` type and `jwtToMcpContext()` that maps JWT scope claims
  (e.g., `"mcp:read mcp:write"`) to `McpScope` string literal types
- **`permissions.ts`** — Scope hierarchy where `manage` includes `write` and `read`,
  `write` includes `read`. `assertMcpScope()` throws `McpPermissionError` if missing.
  Optionally add resource-level access checks for per-entity permissions.
- **`utils.ts`** — `textResult()` helper for MCP tool responses, `wrapToolHandler()`
  that maps ORM-specific "not found" errors to user-friendly messages and logs unexpected errors
- **`server.ts`** — Factory that creates an McpServer with automatic error handling on all
  tools and registers the domain-specific tool groups

## Phase 6: MCP API Route

Read `references/api-route.md` for the complete code.

Create `src/routes/api/mcp.ts` — the HTTP handler. Key design decisions:

- **Stateless**: new McpServer per request, no server-side sessions.
  `sessionIdGenerator: undefined` and `enableJsonResponse: true` (no SSE).
- **JWT verification** via `oauthProviderResourceClient(auth).getActions().verifyAccessToken()`
  against the JWKS endpoint. Validates audience and issuer.
- **CORS `*`** on all responses — MCP spec requirement, auth is token-based.
- **401 with `WWW-Authenticate`** header pointing to protected resource metadata URL.
  Without this, MCP clients can't discover where to authenticate.
- **Rate limiting** per user: `mcp:{userId}` key. Required — use the project's existing
  rate limiter (Better Auth plugin, rate-limiter-flexible, upstash, etc.).
- **GET → 405**, **DELETE → 204** (no-op, stateless), **OPTIONS → CORS preflight**.

## Phase 7: Tool Registration

Generate domain-specific tools based on the user's entities. Each tool file follows this
pattern (adapt the data access calls to the project's ORM):

```typescript
import type { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import { z } from 'zod'
import type { McpAuthContext } from '../auth'
import { assertMcpScope } from '../permissions'
import { textResult } from '../utils'
// Import the project's data access layer (Prisma, Drizzle, Kysely, etc.)

export function registerEntityTools(server: McpServer, ctx: McpAuthContext) {
  server.registerTool(
    'list_items',
    { description: 'List all items accessible to the user' },
    async () => {
      assertMcpScope(ctx, 'read')
      // Adapt to your ORM — example uses Prisma:
      const items = await prisma.item.findMany({ where: { userId: ctx.userId } })
      return textResult(items)
    },
  )

  server.registerTool(
    'create_item',
    {
      description: 'Create a new item',
      inputSchema: { name: z.string().describe('Item name') },
    },
    async ({ name }) => {
      assertMcpScope(ctx, 'write')
      // Adapt to your ORM — example uses Prisma:
      const item = await prisma.item.create({
        data: { name, userId: ctx.userId },
      })
      return textResult(item)
    },
  )
}
```

After creating tool files, import and call them in `server.ts`'s `createMcpServer()`.

Sanitize responses with a whitelist — only expose known-safe fields, never leak internal
IDs, tokens, or sensitive metadata.

## Phase 8: Consent Page

Read `references/consent-page.md` for the structure and security requirements.

Create `src/routes/oauth/consent.tsx` — a standalone page (no auth layout wrapper).

Security-critical: the client name displayed to the user must be fetched from the server
via `/api/auth/oauth2/public-client?client_id=...`, never from URL query parameters.
An attacker could craft a URL with a spoofed `client_name` to trick users into authorizing
a malicious app that appears legitimate.

The page shows: app name, requested scopes with labels, unverified app warning,
accept/reject buttons. On accept, POSTs to `/api/auth/oauth2/consent` with
`{ accept: true, oauth_query: "<original-query-string>" }` and redirects to the
returned URL.

## Phase 9: Session Management (Optional)

Read `references/session-management.md` for the structure and revocation requirements.

Two server functions + an admin page:
- **`getMcpSessions()`** — lists OAuth consents with client metadata and latest IP
- **`revokeMcpSession()`** — atomic revocation in a single transaction

The revocation must delete ALL of these atomically (single transaction):
1. The `OauthConsent` record
2. All `OauthAccessToken` records for that client+user
3. All `OauthRefreshToken` records for that client+user
4. All pending authorization codes (`Verification` records with `identifier` starting
   with `oauth2:{clientId}:`) to close the replay window

Partial cleanup creates security gaps — orphaned tokens or replayable codes.

## Phase 10: E2E Tests (Optional)

Read `references/e2e-tests.md` for the test specification and key testing patterns.

Cover these areas:
- Well-known endpoint discovery (3 tests)
- Security: 401 without/with-bad token, 405 GET, CORS OPTIONS (4 tests)
- Dynamic client registration (2 tests)
- Full OAuth flow with PKCE (2 tests)
- Session revocation (1 test, if session management included)

Key testing patterns:
- Intercept the OAuth callback redirect to avoid ERR_CONNECTION_REFUSED (no real callback server)
- Handle consent page auto-skip when consent was previously granted
- Include `resource` parameter in authorize and token exchange (audience validation)
- Token endpoint uses form encoding, not JSON

## Phase 11: Verification Checklist

After implementing all phases:

- [ ] `GET /.well-known/oauth-authorization-server` returns issuer, token_endpoint, etc.
- [ ] `GET /.well-known/oauth-protected-resource` returns MCP scopes and auth server URL
- [ ] `POST /api/mcp` without token returns 401 with `WWW-Authenticate` header
- [ ] `POST /api/mcp` with invalid token returns 401
- [ ] `OPTIONS /api/mcp` returns CORS headers
- [ ] Full OAuth flow works end-to-end in a real MCP client (Claude Code, Cursor, etc.)
- [ ] Scope restrictions work (read-only token can't call write tools)
- [ ] Token refresh works after access token expires (5 min)
- [ ] Session revocation removes the app from admin page
- [ ] Rate limiting triggers on excessive requests

### MCP Client Configuration

After setup, users connect their MCP client with config like (replace `APP_NAME`
and `APP_URL` with the actual project values):

**Claude Code** (`.mcp.json` or `~/.claude/mcp.json`):
```json
{ "mcpServers": { "APP_NAME": { "type": "http", "url": "APP_URL/api/mcp" } } }
```

**Cursor** (`.cursor/mcp.json`):
```json
{ "mcpServers": { "APP_NAME": { "url": "APP_URL/api/mcp" } } }
```

**VS Code** (`.vscode/mcp.json`):
```json
{ "servers": { "APP_NAME": { "type": "http", "url": "APP_URL/api/mcp" } } }
```

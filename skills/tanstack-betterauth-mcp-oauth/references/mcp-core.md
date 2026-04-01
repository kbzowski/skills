# MCP Core Files

Create these 4 files in `src/server/mcp/`.

## `auth.ts` — JWT to Auth Context

Maps OAuth JWT scope claims to the application's McpScope type.
For Prisma projects, import the generated enum. For other adapters, define `McpScope` as
a string literal union type directly in this file.

```typescript
import type { JWTPayload } from 'jose'
// For Prisma: import type { McpScope } from '@/generated/prisma/client'
// For other adapters, define locally:
export type McpScope = 'read' | 'write' | 'manage'

export type McpAuthContext = {
  userId: string
  scopes: Array<McpScope>
  ip: string | undefined
}

const OAUTH_SCOPE_MAP: Record<string, McpScope> = {
  'mcp:read': 'read',
  'mcp:write': 'write',
  'mcp:manage': 'manage',
}

export function jwtToMcpContext(
  jwt: JWTPayload,
  ip: string | undefined,
): McpAuthContext {
  const scopeStr =
    typeof jwt.scope === 'string'
      ? jwt.scope
      : Array.isArray(jwt.scope)
        ? jwt.scope.join(' ')
        : ''
  if (!jwt.sub) {
    throw new Error('Token missing subject claim')
  }

  const mcpScopes = scopeStr
    .split(' ')
    .map((s: string) => OAUTH_SCOPE_MAP[s])
    .filter(Boolean) as Array<McpScope>
  if (mcpScopes.length === 0) {
    throw new Error('Token has no MCP scopes')
  }

  return {
    userId: jwt.sub,
    scopes: mcpScopes,
    ip,
  }
}
```

**Adaptation notes:**
- If using different scope names, update `OAUTH_SCOPE_MAP` keys and values
- For Prisma, import `McpScope` from the generated client instead of defining it locally
- For Drizzle/Kysely/others, define `McpScope` as a string literal union in this file
- The `scope` claim in JWTs can be a string or array — handle both

---

## `permissions.ts` — Scope Hierarchy and Assertions

```typescript
// For Prisma: import type { McpScope } from '@/generated/prisma/client'
// For other adapters: McpScope is already exported from ./auth
import type { McpScope, McpAuthContext } from './auth'

const SCOPE_HIERARCHY: Record<McpScope, Array<McpScope>> = {
  manage: ['manage', 'write', 'read'],
  write: ['write', 'read'],
  read: ['read'],
}

function hasScope(
  grantedScopes: Array<McpScope>,
  requiredScope: McpScope,
): boolean {
  return grantedScopes.some((granted) =>
    SCOPE_HIERARCHY[granted].includes(requiredScope),
  )
}

export function assertMcpScope(
  ctx: McpAuthContext,
  requiredScope: McpScope,
): void {
  if (!hasScope(ctx.scopes, requiredScope)) {
    throw new McpPermissionError(
      `Missing required scope: ${requiredScope}`,
    )
  }
}

export class McpPermissionError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'McpPermissionError'
  }
}
```

**Optional: resource-level access checks**

If your domain has per-entity permissions (e.g., shared resources), add functions like:

```typescript
export async function assertMcpEntityAccess(
  ctx: McpAuthContext,
  entityId: string,
  requiredScope: McpScope,
): Promise<{ entity: Entity; permission: Permission }> {
  assertMcpScope(ctx, requiredScope)
  const { entity, permission } = await checkEntityAccess(entityId, ctx.userId)

  if (requiredScope === 'write' && !canEdit(permission)) {
    throw new McpPermissionError('No permission to edit this resource')
  }
  if (requiredScope === 'manage' && !isOwner(permission)) {
    throw new McpPermissionError('No permission to manage this resource')
  }

  return { entity, permission }
}
```

---

## `utils.ts` — Response Helpers and Error Wrapping

```typescript
import { McpPermissionError } from './permissions'

export function serialize(data: unknown) {
  return JSON.stringify(data, (_key, value) =>
    value instanceof Date ? value.toISOString() : value,
  )
}

/** Shorthand for returning a text result from an MCP tool handler. */
export function textResult(data: unknown) {
  return { content: [{ type: 'text' as const, text: serialize(data) }] }
}

/**
 * Detect ORM-specific "not found" errors. Adapt to the project's adapter:
 * - Prisma:  (error as any)?.code === 'P2025'
 * - Kysely:  error instanceof NoResultError
 * - General: error.message?.includes('not found')
 */
function isNotFoundError(error: unknown): boolean {
  return (error as any)?.code === 'P2025'
}

/**
 * Wraps an MCP tool handler to map known errors to user-friendly messages
 * and log unexpected errors. The MCP SDK catches thrown errors and returns
 * `{ isError: true }` — this wrapper improves the error message quality.
 */
export function wrapToolHandler<T extends (...args: any[]) => any>(fn: T): T {
  return (async (...args: unknown[]) => {
    try {
      return await fn(...args)
    } catch (error) {
      if (error instanceof McpPermissionError) {
        throw error
      }

      if (isNotFoundError(error)) {
        throw new Error('Resource not found')
      }

      console.error('Unexpected MCP tool error', error)
      throw new Error('Internal server error')
    }
  }) as T
}
```

**Adaptation notes:**
- Replace `console.error` with your project's logger if available
- Localize error messages to the project's language if needed
- Adapt `isNotFoundError()` to the project's ORM:
  - **Prisma**: `error.code === 'P2025'`
  - **Drizzle**: check for empty results in the tool handler itself
  - **Kysely**: `error instanceof NoResultError`
  - **General**: `error.message?.includes('not found')`

---

## `server.ts` — MCP Server Factory

```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js'
import type { McpAuthContext } from './auth'
import { wrapToolHandler } from './utils'
// Import your tool registration functions:
// import { registerEntityTools } from './tools/entities'

/**
 * Wraps McpServer.registerTool so every tool handler automatically gets
 * error mapping (Prisma P2025 → friendly message, unexpected → logged).
 */
function withErrorHandling(server: McpServer): McpServer {
  const original = server.registerTool.bind(server)
  ;(server as any).registerTool = (name: string, ...rest: any[]) => {
    const handler = rest.pop()
    rest.push(wrapToolHandler(handler))
    return (original as any)(name, ...rest)
  }
  return server
}

export function createMcpServer(ctx: McpAuthContext): McpServer {
  const server = withErrorHandling(
    new McpServer(
      { name: 'PROJECT_NAME' /* replace */, version: '1.0.0' },
      { capabilities: { tools: {} } },
    ),
  )

  // Register your tool groups:
  // registerEntityTools(server, ctx)

  return server
}
```

**Adaptation notes:**
- Replace `'PROJECT_NAME'` with the actual project name
- Import and call each tool registration function
- The `withErrorHandling` wrapper intercepts the SDK's `registerTool` method to
  automatically wrap every handler — you don't need to call `wrapToolHandler` manually
  in individual tools

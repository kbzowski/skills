# Session Management

Server functions + admin page for listing and revoking connected MCP apps.
Adapt all data access calls to the project's ORM (examples below use Prisma syntax).

## Server Functions

Create `src/functions/mcp-sessions.functions.ts` with two server functions:

### `getMcpSessions` — List Connected Apps

```
GET server function, requires auth middleware

1. Query oauthConsent where userId = current user
   - Include oauthClient fields: name, clientId, icon, uri, createdAt
   - Order by createdAt desc

2. For each unique clientId, find the most recent oauthRefreshToken
   - Include session.ipAddress for "last seen IP" display

3. Return array of:
   { id, clientId, clientName, clientIcon, clientUri, scopes,
     ipAddress, createdAt, updatedAt }
```

### `revokeMcpSession` — Revoke a Connected App

```
POST server function, requires auth middleware
Input: { consentId: uuid }

1. Verify ownership: find oauthConsent where id = consentId AND userId = current user
   - Throw if not found

2. ATOMIC TRANSACTION — delete ALL of these in a single transaction:
   a. The OauthConsent record
   b. All OauthAccessToken records for that clientId + userId
   c. All OauthRefreshToken records for that clientId + userId
   d. All pending Verification records where identifier starts with
      "oauth2:{clientId}:" (closes the authorization code replay window)

3. Return { success: true }
```

**Why atomic?** Partial cleanup creates security gaps — orphaned tokens remain valid
until expiry, and replayable authorization codes allow re-establishing access.

## Query Keys and Options

Add to the project's query infrastructure:

```typescript
// Query key
mcpSessions: () => ['mcpSessions'] as const

// Query options
export const mcpSessionsQueryOptions = queryOptions({
  queryKey: queryKeys.mcpSessions(),
  queryFn: () => getMcpSessions(),
})
```

## Admin Page

Create an admin route (e.g., `src/routes/_authenticated/admin/mcp.tsx`):

```
Route loader: ensureQueryData(mcpSessionsQueryOptions)

Page structure:
- Title: "MCP Integrations"
- Subtitle: "Applications connected to your account via OAuth"
- Empty state with icon when no sessions
- For each session: card showing:
  - Client name (fallback to clientId)
  - Authorization date
  - IP address (if available)
  - Client URI (if available)
  - "Revoke access" button
- Confirmation dialog before revocation

Revoke mutation:
- mutationFn: revokeMcpSession({ data: { consentId } })
- onSuccess: invalidate mcpSessions query, close dialog
```

Add `data-testid` attributes for E2E testing:
- `mcp-title` on the page heading
- `mcp-session-{id}` on each session card
- `revoke-session-btn-{id}` on each revoke button
- `confirm-revoke` on the confirmation button

## Adaptation Notes

- Adapt all data access to the project's ORM (Prisma, Drizzle, Kysely, etc.)
- Use the project's UI components (shadcn/ui Card, AlertDialog, Button, etc.)
- Localize all strings to the project's language
- The admin route path depends on the project's route structure
- Add the route to the project's admin navigation

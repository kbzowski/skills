# OAuth Consent Page

Create `src/routes/oauth/consent.tsx` — a standalone page where users approve or deny
OAuth authorization requests from MCP clients. Adapt to the project's UI library and locale.

## Route and Structure

```
createFileRoute('/oauth/consent') → ConsentPage component
```

Standalone page (no auth layout wrapper). Centered card with:
1. "Authorization Request" heading + app name
2. Client name (loaded from server — see Security below)
3. Unverified app warning (if not `skipConsent`)
4. Scope list with human-readable labels
5. Accept / Deny buttons
6. Error display area

## Scope Labels Map

Define a `SCOPE_LABELS` record mapping OAuth scope strings to user-friendly labels:

```typescript
const SCOPE_LABELS: Record<string, string> = {
  openid: 'Identity (OpenID)',
  profile: 'Profile data',
  email: 'Email address',
  offline_access: 'Offline access (token refresh)',
  'mcp:read': 'Read data',
  'mcp:write': 'Write data (create, edit)',
  'mcp:manage': 'Full management (archive, delete, share)',
}
```

Adapt scope names and labels to the project's scopes and locale. Display unknown scopes
with a warning indicator (e.g., red dot) to alert the user about unexpected permissions.

## State and URL Parameters

Extract from `window.location.search`:
- `client_id` — identifies the requesting application
- `scope` — space-separated scope string, split into array

Preserve the **full original query string** as `oauthQuery` — Better Auth signs these
parameters, so any modification invalidates the authorization request.

## Consent Flow

**On Accept:**
```
POST /api/auth/oauth2/consent
Body: { accept: true, oauth_query: "<original-query-string>" }
→ Response contains { url } → redirect to that URL
```

**On Deny:**
```
POST /api/auth/oauth2/consent
Body: { accept: false, oauth_query: "<original-query-string>" }
```

Include `credentials: 'include'` on fetch calls (session cookie needed).

## Security Requirements (Critical)

1. **Client name MUST come from the server, never from URL params.**
   Fetch via `GET /api/auth/oauth2/public-client?client_id={clientId}`.
   An attacker could craft a URL with `client_name=<trusted app name>` to trick users
   into authorizing a malicious app.

2. **Unverified client warning:** Dynamically registered clients (all MCP clients by default)
   must show a warning banner. Only clients with `skipConsent: true` in the database are
   considered verified.

3. **Preserved query string:** The `oauth_query` sent to the consent endpoint must be the
   exact original query string. Better Auth signs it — modification invalidates the request.

4. **Unknown scope highlighting:** Scopes not in `SCOPE_LABELS` should be visually
   distinguished (e.g., red indicator) to alert users about unexpected permission requests.

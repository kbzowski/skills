# E2E Test Specification for MCP OAuth

What to test and key patterns for testing the MCP OAuth integration.
Use the project's existing test framework (Playwright, Cypress, etc.).

## Test Helpers Needed

### PKCE Helpers

Generate `code_verifier` (random 32 bytes, base64url) and `code_challenge`
(SHA-256 of verifier, base64url). Standard OAuth 2.1 PKCE — use `node:crypto`.

### Dynamic Client Registration Helper

```
POST /api/auth/oauth2/register
Body: {
  client_name: "E2E Test MCP Client",
  redirect_uris: ["http://127.0.0.1:9999/callback"],
  grant_types: ["authorization_code", "refresh_token"],
  response_types: ["code"],
  scope: "openid profile email offline_access mcp:read mcp:write mcp:manage",
  token_endpoint_auth_method: "none"
}
→ Returns { client_id, client_secret? }
```

### Full OAuth Flow Helper

Performs the complete flow: login → authorize → consent → code exchange → returns access token.

Key steps:
1. Register a client (dynamic registration)
2. Generate PKCE pair
3. Log in as a test user (project-specific)
4. Navigate to `/api/auth/oauth2/authorize` with params:
   `response_type=code`, `client_id`, `redirect_uri`, `scope`, `code_challenge`,
   `code_challenge_method=S256`, `state`, `resource={APP_URL}/api/mcp`
5. Handle consent page (click Accept if visible, may auto-skip if previously consented)
6. Capture the authorization code from the callback redirect
7. Exchange code for token via `POST /api/auth/oauth2/token` with
   `grant_type=authorization_code`, `code`, `redirect_uri`, `client_id`,
   `code_verifier`, `resource`

### MCP JSON-RPC Helper

```
POST /api/mcp
Headers: Content-Type: application/json, Accept: application/json,
         Authorization: Bearer {token} (optional)
Body: { jsonrpc: "2.0", method: "...", params: {...}, id: 1 }
```

## Test Categories

### 1. Well-Known Endpoints (3 tests)

**Authorization server metadata at MCP spec path:**
- `GET /.well-known/oauth-authorization-server` → 200
- Response contains: `issuer`, `authorization_endpoint`, `token_endpoint`,
  `registration_endpoint`, `response_types_supported` includes `"code"`,
  `code_challenge_methods_supported` includes `"S256"`

**Authorization server metadata at RFC 8414 path:**
- `GET /.well-known/oauth-authorization-server/api/auth` → 200
- Response contains `issuer`

**Protected resource metadata:**
- `GET /.well-known/oauth-protected-resource` → 200
- `scopes_supported` contains `mcp:read`, `mcp:write`, `mcp:manage`
- `authorization_servers` contains `{APP_URL}/api/auth`
- `resource` equals `{APP_URL}/api/mcp`

### 2. Security (4 tests)

**Unauthenticated request:**
- `POST /api/mcp` without Authorization header → 401
- Response has `WWW-Authenticate` header containing `Bearer` and `resource_metadata`

**Invalid token:**
- `POST /api/mcp` with `Authorization: Bearer invalid-jwt-token` → 401

**GET method rejected:**
- `GET /api/mcp` → 405

**CORS preflight:**
- `OPTIONS /api/mcp` → 204
- `Access-Control-Allow-Origin: *`
- `Access-Control-Allow-Methods` includes `POST`

### 3. Dynamic Client Registration (2 tests)

**Public client registration:**
- Register a client → response has `client_id`

**Confidential client forced to public when unauthenticated:**
- Register with `token_endpoint_auth_method: "client_secret_post"`
- Response `token_endpoint_auth_method` should be `"none"` (downgraded to public)

### 4. OAuth Flow (2 tests)

**Full flow end-to-end:**
- Run the full OAuth flow helper → get access token
- Call `tools/list` with the token → 200, `result.tools` is non-empty

**Read-only token cannot call write tools:**
- Run OAuth flow with scopes `"openid mcp:read"` only
- Call a write-requiring tool → response has `result.isError: true`

### 5. Session Management (1 test, if session management is included)

**Session appears and can be revoked:**
- Run OAuth flow → get access token
- Verify token works (`tools/list` → 200)
- Navigate to the MCP admin page
- Verify at least one session card is visible
- Click "Revoke access" → confirm
- Verify session card count decreased
- Token may still work briefly (JWT TTL) — accept both 200 and 401

## Key Testing Patterns

**Intercept the OAuth callback redirect.** The redirect URI (e.g., `http://127.0.0.1:9999/callback`)
has no real server. Intercept the redirect in the test framework to capture the authorization
code without hitting `ERR_CONNECTION_REFUSED`.

**Handle consent auto-skip.** If the user previously consented for this client, the consent
page may be skipped. Check if the Accept button is visible before clicking it.

**The `resource` parameter matters.** Include `resource={APP_URL}/api/mcp` in both the
authorize request and the token exchange. Without it, the JWT `aud` claim won't match
and token verification will fail.

**Token exchange uses form encoding.** The token endpoint expects
`Content-Type: application/x-www-form-urlencoded`, not JSON.

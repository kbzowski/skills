# Database Schema for MCP OAuth

Better Auth's `oauthProvider` plugin requires 5 tables with exact names. This file provides
schemas for multiple adapters. Use the section matching your project's database adapter.

## Table of Contents
- [Required Tables Overview](#required-tables-overview)
- [Prisma](#prisma)
- [Drizzle](#drizzle)
- [Raw SQL (PostgreSQL)](#raw-sql-postgresql)
- [Other Adapters](#other-adapters)
- [Critical Notes](#critical-notes)

---

## Required Tables Overview

Better Auth expects these exact table names (camelCase):

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `jwks` | JWT signing key rotation | publicKey, privateKey, createdAt, expiresAt |
| `oauthClient` | Registered OAuth applications | clientId (unique), name, scopes[], redirectUris[] |
| `oauthRefreshToken` | Long-lived refresh tokens (7d) | token (unique), clientId, sessionId, userId, expiresAt |
| `oauthAccessToken` | Short-lived access tokens (5m) | token (unique), clientId, sessionId, userId, refreshId, expiresAt |
| `oauthConsent` | User consent records | clientId, userId, scopes[] |

Also define an `McpScope` type for your application code:
- **Prisma**: `enum McpScope { read write manage }`
- **Drizzle/others**: `type McpScope = 'read' | 'write' | 'manage'` (TypeScript string literal union)

---

## Prisma

Add to `prisma/schema.prisma`:

```prisma
enum McpScope {
  read
  write
  manage
}

model Jwks {
  id         String    @id @default(uuid(7)) @db.Uuid
  publicKey  String
  privateKey String
  createdAt  DateTime
  expiresAt  DateTime?
  @@index([createdAt])
  @@map("jwks")
}

model OauthClient {
  id                      String              @id @default(uuid(7)) @db.Uuid
  clientId                String
  clientSecret            String?
  disabled                Boolean?            @default(false)
  skipConsent             Boolean?
  enableEndSession        Boolean?
  subjectType             String?
  scopes                  String[]
  userId                  String?             @db.Uuid
  user                    User?               @relation(fields: [userId], references: [id], onDelete: Cascade)
  createdAt               DateTime?
  updatedAt               DateTime?
  name                    String?
  uri                     String?
  icon                    String?
  contacts                String[]
  tos                     String?
  policy                  String?
  softwareId              String?
  softwareVersion         String?
  softwareStatement       String?
  redirectUris            String[]
  postLogoutRedirectUris  String[]
  tokenEndpointAuthMethod String?
  grantTypes              String[]
  responseTypes           String[]
  public                  Boolean?
  type                    String?
  requirePKCE             Boolean?
  referenceId             String?
  metadata                Json?
  oauthRefreshTokens      OauthRefreshToken[]
  oauthAccessTokens       OauthAccessToken[]
  oauthConsents           OauthConsent[]
  @@unique([clientId])
  @@index([userId])
  @@map("oauthClient")
}

model OauthRefreshToken {
  id                String             @id @default(uuid(7)) @db.Uuid
  token             String             @unique
  clientId          String
  oauthclient       OauthClient        @relation(fields: [clientId], references: [clientId], onDelete: Cascade)
  sessionId         String?            @db.Uuid
  session           Session?           @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  userId            String             @db.Uuid
  user              User               @relation(fields: [userId], references: [id], onDelete: Cascade)
  referenceId       String?
  expiresAt         DateTime?
  createdAt         DateTime?
  revoked           DateTime?
  authTime          DateTime?
  scopes            String[]
  oauthAccessTokens OauthAccessToken[]
  @@index([clientId])
  @@index([userId])
  @@index([sessionId])
  @@index([expiresAt])
  @@map("oauthRefreshToken")
}

model OauthAccessToken {
  id                String             @id @default(uuid(7)) @db.Uuid
  token             String?
  clientId          String
  oauthclient       OauthClient        @relation(fields: [clientId], references: [clientId], onDelete: Cascade)
  sessionId         String?            @db.Uuid
  session           Session?           @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  userId            String?            @db.Uuid
  user              User?              @relation(fields: [userId], references: [id], onDelete: Cascade)
  referenceId       String?
  refreshId         String?            @db.Uuid
  oauthrefreshtoken OauthRefreshToken? @relation(fields: [refreshId], references: [id], onDelete: Cascade)
  expiresAt         DateTime?
  createdAt         DateTime?
  scopes            String[]
  @@unique([token])
  @@index([clientId])
  @@index([userId])
  @@index([sessionId])
  @@index([refreshId])
  @@index([expiresAt])
  @@map("oauthAccessToken")
}

model OauthConsent {
  id          String      @id @default(uuid(7)) @db.Uuid
  clientId    String
  oauthclient OauthClient @relation(fields: [clientId], references: [clientId], onDelete: Cascade)
  userId      String?     @db.Uuid
  user        User?       @relation(fields: [userId], references: [id], onDelete: Cascade)
  referenceId String?
  scopes      String[]
  createdAt   DateTime?
  updatedAt   DateTime?
  @@index([clientId, userId])
  @@map("oauthConsent")
}
```

Add to existing models:
```prisma
// User model — add:
oauthClients       OauthClient[]
oauthRefreshTokens OauthRefreshToken[]
oauthAccessTokens  OauthAccessToken[]
oauthConsents      OauthConsent[]

// Session model — add:
oauthRefreshTokens OauthRefreshToken[]
oauthAccessTokens  OauthAccessToken[]
```

**PostgreSQL-specific**: `@db.Uuid` — remove for MySQL/SQLite. Use `uuid()` instead of `uuid(7)` if your DB doesn't support UUIDv7.

---

## Drizzle

For Drizzle ORM, define the tables in your schema file. Adapt the column types to your
database dialect (pg, mysql, sqlite).

```typescript
import { pgTable, uuid, text, boolean, timestamp, jsonb, index, uniqueIndex } from 'drizzle-orm/pg-core'

// Reference your existing user and session tables
import { user, session } from './auth-schema'

export const jwks = pgTable('jwks', {
  id: uuid('id').primaryKey().defaultRandom(),
  publicKey: text('publicKey').notNull(),
  privateKey: text('privateKey').notNull(),
  createdAt: timestamp('createdAt').notNull(),
  expiresAt: timestamp('expiresAt'),
}, (t) => [index('jwks_createdAt_idx').on(t.createdAt)])

export const oauthClient = pgTable('oauthClient', {
  id: uuid('id').primaryKey().defaultRandom(),
  clientId: text('clientId').notNull(),
  clientSecret: text('clientSecret'),
  disabled: boolean('disabled').default(false),
  skipConsent: boolean('skipConsent'),
  enableEndSession: boolean('enableEndSession'),
  subjectType: text('subjectType'),
  scopes: text('scopes').array(),
  userId: uuid('userId').references(() => user.id, { onDelete: 'cascade' }),
  createdAt: timestamp('createdAt'),
  updatedAt: timestamp('updatedAt'),
  name: text('name'),
  uri: text('uri'),
  icon: text('icon'),
  contacts: text('contacts').array(),
  tos: text('tos'),
  policy: text('policy'),
  softwareId: text('softwareId'),
  softwareVersion: text('softwareVersion'),
  softwareStatement: text('softwareStatement'),
  redirectUris: text('redirectUris').array(),
  postLogoutRedirectUris: text('postLogoutRedirectUris').array(),
  tokenEndpointAuthMethod: text('tokenEndpointAuthMethod'),
  grantTypes: text('grantTypes').array(),
  responseTypes: text('responseTypes').array(),
  public: boolean('public'),
  type: text('type'),
  requirePKCE: boolean('requirePKCE'),
  referenceId: text('referenceId'),
  metadata: jsonb('metadata'),
}, (t) => [
  uniqueIndex('oauthClient_clientId_key').on(t.clientId),
  index('oauthClient_userId_idx').on(t.userId),
])

export const oauthRefreshToken = pgTable('oauthRefreshToken', {
  id: uuid('id').primaryKey().defaultRandom(),
  token: text('token').notNull().unique(),
  clientId: text('clientId').notNull().references(() => oauthClient.clientId, { onDelete: 'cascade' }),
  sessionId: uuid('sessionId').references(() => session.id, { onDelete: 'cascade' }),
  userId: uuid('userId').notNull().references(() => user.id, { onDelete: 'cascade' }),
  referenceId: text('referenceId'),
  expiresAt: timestamp('expiresAt'),
  createdAt: timestamp('createdAt'),
  revoked: timestamp('revoked'),
  authTime: timestamp('authTime'),
  scopes: text('scopes').array(),
}, (t) => [
  index('oauthRefreshToken_clientId_idx').on(t.clientId),
  index('oauthRefreshToken_userId_idx').on(t.userId),
  index('oauthRefreshToken_sessionId_idx').on(t.sessionId),
  index('oauthRefreshToken_expiresAt_idx').on(t.expiresAt),
])

export const oauthAccessToken = pgTable('oauthAccessToken', {
  id: uuid('id').primaryKey().defaultRandom(),
  token: text('token'),
  clientId: text('clientId').notNull().references(() => oauthClient.clientId, { onDelete: 'cascade' }),
  sessionId: uuid('sessionId').references(() => session.id, { onDelete: 'cascade' }),
  userId: uuid('userId').references(() => user.id, { onDelete: 'cascade' }),
  referenceId: text('referenceId'),
  refreshId: uuid('refreshId').references(() => oauthRefreshToken.id, { onDelete: 'cascade' }),
  expiresAt: timestamp('expiresAt'),
  createdAt: timestamp('createdAt'),
  scopes: text('scopes').array(),
}, (t) => [
  uniqueIndex('oauthAccessToken_token_key').on(t.token),
  index('oauthAccessToken_clientId_idx').on(t.clientId),
  index('oauthAccessToken_userId_idx').on(t.userId),
  index('oauthAccessToken_sessionId_idx').on(t.sessionId),
  index('oauthAccessToken_refreshId_idx').on(t.refreshId),
  index('oauthAccessToken_expiresAt_idx').on(t.expiresAt),
])

export const oauthConsent = pgTable('oauthConsent', {
  id: uuid('id').primaryKey().defaultRandom(),
  clientId: text('clientId').notNull().references(() => oauthClient.clientId, { onDelete: 'cascade' }),
  userId: uuid('userId').references(() => user.id, { onDelete: 'cascade' }),
  referenceId: text('referenceId'),
  scopes: text('scopes').array(),
  createdAt: timestamp('createdAt'),
  updatedAt: timestamp('updatedAt'),
}, (t) => [
  index('oauthConsent_clientId_userId_idx').on(t.clientId, t.userId),
])
```

For MySQL: replace `uuid` with appropriate type, `text().array()` with JSON columns.
For SQLite: use `text` for all columns, store arrays as JSON strings.

---

## Raw SQL (PostgreSQL)

For adapters without schema DSL (Kysely, Knex, raw SQL), use these migrations:

```sql
-- Table: jwks
CREATE TABLE "jwks" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "publicKey" TEXT NOT NULL,
    "privateKey" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL,
    "expiresAt" TIMESTAMP(3),
    CONSTRAINT "jwks_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "jwks_createdAt_idx" ON "jwks"("createdAt");

-- Table: oauthClient
CREATE TABLE "oauthClient" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "clientId" TEXT NOT NULL,
    "clientSecret" TEXT,
    "disabled" BOOLEAN DEFAULT false,
    "skipConsent" BOOLEAN,
    "enableEndSession" BOOLEAN,
    "subjectType" TEXT,
    "scopes" TEXT[],
    "userId" UUID REFERENCES "User"("id") ON DELETE CASCADE,
    "createdAt" TIMESTAMP(3),
    "updatedAt" TIMESTAMP(3),
    "name" TEXT,
    "uri" TEXT,
    "icon" TEXT,
    "contacts" TEXT[],
    "tos" TEXT,
    "policy" TEXT,
    "softwareId" TEXT,
    "softwareVersion" TEXT,
    "softwareStatement" TEXT,
    "redirectUris" TEXT[],
    "postLogoutRedirectUris" TEXT[],
    "tokenEndpointAuthMethod" TEXT,
    "grantTypes" TEXT[],
    "responseTypes" TEXT[],
    "public" BOOLEAN,
    "type" TEXT,
    "requirePKCE" BOOLEAN,
    "referenceId" TEXT,
    "metadata" JSONB,
    CONSTRAINT "oauthClient_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "oauthClient_clientId_key" ON "oauthClient"("clientId");
CREATE INDEX "oauthClient_userId_idx" ON "oauthClient"("userId");

-- Table: oauthRefreshToken
CREATE TABLE "oauthRefreshToken" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "token" TEXT NOT NULL,
    "clientId" TEXT NOT NULL REFERENCES "oauthClient"("clientId") ON DELETE CASCADE,
    "sessionId" UUID REFERENCES "Session"("id") ON DELETE CASCADE,
    "userId" UUID NOT NULL REFERENCES "User"("id") ON DELETE CASCADE,
    "referenceId" TEXT,
    "expiresAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3),
    "revoked" TIMESTAMP(3),
    "authTime" TIMESTAMP(3),
    "scopes" TEXT[],
    CONSTRAINT "oauthRefreshToken_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "oauthRefreshToken_token_key" ON "oauthRefreshToken"("token");
CREATE INDEX "oauthRefreshToken_clientId_idx" ON "oauthRefreshToken"("clientId");
CREATE INDEX "oauthRefreshToken_userId_idx" ON "oauthRefreshToken"("userId");
CREATE INDEX "oauthRefreshToken_sessionId_idx" ON "oauthRefreshToken"("sessionId");
CREATE INDEX "oauthRefreshToken_expiresAt_idx" ON "oauthRefreshToken"("expiresAt");

-- Table: oauthAccessToken
CREATE TABLE "oauthAccessToken" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "token" TEXT,
    "clientId" TEXT NOT NULL REFERENCES "oauthClient"("clientId") ON DELETE CASCADE,
    "sessionId" UUID REFERENCES "Session"("id") ON DELETE CASCADE,
    "userId" UUID REFERENCES "User"("id") ON DELETE CASCADE,
    "referenceId" TEXT,
    "refreshId" UUID REFERENCES "oauthRefreshToken"("id") ON DELETE CASCADE,
    "expiresAt" TIMESTAMP(3),
    "createdAt" TIMESTAMP(3),
    "scopes" TEXT[],
    CONSTRAINT "oauthAccessToken_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "oauthAccessToken_token_key" ON "oauthAccessToken"("token");
CREATE INDEX "oauthAccessToken_clientId_idx" ON "oauthAccessToken"("clientId");
CREATE INDEX "oauthAccessToken_userId_idx" ON "oauthAccessToken"("userId");
CREATE INDEX "oauthAccessToken_sessionId_idx" ON "oauthAccessToken"("sessionId");
CREATE INDEX "oauthAccessToken_refreshId_idx" ON "oauthAccessToken"("refreshId");
CREATE INDEX "oauthAccessToken_expiresAt_idx" ON "oauthAccessToken"("expiresAt");

-- Table: oauthConsent
CREATE TABLE "oauthConsent" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "clientId" TEXT NOT NULL REFERENCES "oauthClient"("clientId") ON DELETE CASCADE,
    "userId" UUID REFERENCES "User"("id") ON DELETE CASCADE,
    "referenceId" TEXT,
    "scopes" TEXT[],
    "createdAt" TIMESTAMP(3),
    "updatedAt" TIMESTAMP(3),
    CONSTRAINT "oauthConsent_pkey" PRIMARY KEY ("id")
);
CREATE INDEX "oauthConsent_clientId_userId_idx" ON "oauthConsent"("clientId", "userId");
```

For MySQL: replace `UUID` with `CHAR(36)`, `TEXT[]` with `JSON`, `gen_random_uuid()` with UUID function.
For SQLite: remove array types, use `TEXT` with JSON serialization.

---

## Other Adapters

For **MikroORM**, **Knex**, **Kysely**, **MongoDB**, or any other Better Auth adapter:

1. Better Auth's oauthProvider creates these tables automatically if you use `better-auth`'s
   built-in migration tooling (`npx @better-auth/cli migrate` or `npx @better-auth/cli generate`).
2. If you prefer manual schema management, use the Raw SQL above as the reference for
   exact column names, types, and constraints.
3. For MongoDB: use collections with the same names. Arrays are native. UUIDs can be strings.

The key requirement is that **table and column names match exactly** — Better Auth queries
them by these names internally.

---

## Critical Notes

### Session FK Must CASCADE

The `sessionId` foreign key on `oauthRefreshToken` and `oauthAccessToken` must use
`ON DELETE CASCADE`. When a session is deleted (user logs out), all associated OAuth tokens
must be cleaned up automatically. Using SET NULL would orphan tokens — they'd remain valid
until expiry even though the session is gone.

### Performance Indexes

Don't skip the indexes — they're needed for:
- `clientId` — Better Auth looks up tokens by client during verification
- `userId` — listing a user's tokens/consents on the admin page
- `sessionId` — cascade deletion performance
- `expiresAt` — token cleanup/expiry queries
- `OauthConsent(clientId, userId)` composite — consent lookup during authorization

### McpScope Type

For Prisma, use the native `enum`. For other adapters, define a TypeScript type:

```typescript
export type McpScope = 'read' | 'write' | 'manage'
```

This is used in `src/server/mcp/auth.ts` and `src/server/mcp/permissions.ts`. The values
stored in the database (in `scopes` arrays) are OAuth scope strings like `mcp:read` —
the mapping happens in `jwtToMcpContext()`.

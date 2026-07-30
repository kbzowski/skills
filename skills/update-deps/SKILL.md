---
name: update-deps
description: >
  Disciplined dependency-update pipeline: detect outdated packages,
  read every changelog via dedicated agents, categorize patch/minor/major,
  verify breaking-change claims against the actual code, apply updates grouped
  by type, then verify with lint + build + typecheck + unit + targeted E2E and
  commit per group. Use whenever the user wants to update, bump, or upgrade
  dependencies / packages, asks "aktualizuj zaleznosci", "zaktualizuj paczki",
  "update dependencies", "bump deps", "update to latest", "--latest", or asks to
  check what is outdated. Handles security-first prioritization, transitive-dep
  build breaks (pnpm overrides), and an opt-in "new features worth adopting" report.
---

# Dependency Update Pipeline

You run dependency updates: methodically, with real changelog research, code-level verification, and grouped commits. Speed is not the goal — a correct, verified, reviewable upgrade is.

## Core rules (from the user)

- **Patch** → update immediately, no questions.
- **Minor** → check if anything interests us (new features), but **update anyway**. Report noteworthy features without implementing them.
- **Major** → you **MUST** check for breaking changes AND for anything new worth adopting, before updating.
- **Always research changelogs with dedicated agents** (subagents), not inline guessing. Their knowledge may be stale — trust release notes + code, not memory.
- Communicate in Polish; English only in code/commits/docs. Be terse.
- Stack/library first, DIY last. Verify "only/just/breaking" claims at the source (CLAUDE.md verification discipline). Treat subagent findings as hypotheses until confirmed against raw code.

## Environment notes

- Windows + **PowerShell** is the default shell, but **use the Bash tool for git commits** — commitlint enforces conventional commits and **body lines must be ≤100 chars**. Use multiple `-m` flags with short lines; do NOT use PowerShell here-strings (`@'...'@`) inside the Bash tool — they leak literal `@` into the message.
- `pnpm` only. Lefthook pre-commit runs `biome` + `tsc --noEmit`; commit-msg runs commitlint. A green `pnpm build` typechecks **stricter** than `tsc` (rolldown catches missing exports in transitive deps).
- E2E is heavy: each spec triggers global-setup (build + per-worker DBs + servers). Run **targeted specs**, not the full suite, unless asked.

## Phase 1 — Detect what's outdated

```
pnpm outdated
```

**`pnpm outdated` is not enough.** It misses packages whose installed version resolved *below* the latest but still *within* the caret range (e.g. radix-ui pinned at 1.4.3 in the lockfile while 1.5.0 is published the same day). After the main pass, if the user wants `--latest` or "truly latest", re-check with a fresh `pnpm outdated` and, for anything still behind, compare `npm view <pkg> version` against the resolved version in `pnpm-lock.yaml`. Bump those caret ranges explicitly in `package.json`.

Also note deprecated stubs (e.g. `@types/recharts` when recharts ≥3 ships its own types) → flag for **removal**.

Categorize every package: **security** (regardless of bump size), **patch**, **minor**, **major**, **remove**. Security fixes are surfaced from changelogs — keep them in their own first commit.

In the case of pinned dependencies, you should first determine **WHY** they have been pinned (a bug in newer versions, incompatibility, or accidental pinning). For each one, consider whether it can be updated. If in doubt, the user makes the decision.

## Phase 2 — Research changelogs (dedicated agents, parallel)

Dispatch `general-purpose` agents IN PARALLEL (one message, multiple Agent calls), grouped so each has a focused, sized scope. A good split:
1. **All major bumps** — breaking changes are mandatory; also new features. Have the agent grep our actual usage in the repo to assess impact.
2. **Key minors** (the libraries we lean on: TanStack Form/Query/Router/Start, Zod, XState, Prisma, Tailwind) — new features worth adopting + silent breaking/deprecations.
3. **Other minors/patches + 0.x** — features + quiet breaking; explicit verdict on any deprecated package removal.

Each agent returns, per package: version from→to, breaking changes (or "none"), impact on us (from grep), new/noteworthy features, recommendation. Tell them not to modify files and to cite official release notes.

## Phase 3 — Verify breaking-change claims in code

Do NOT take agent conclusions as fact. Confirm the dangerous ones yourself:
- **Node/engine bumps** (e.g. commitlint 21 needs Node ≥22): check `node -v` and `package.json` `engines`.
- **Silent breaking patterns** (e.g. Zod 4.4 `.merge()` / `.base64()` / `.cuid()` / `z.undefined()`): grep `src` for every pattern. Confirm `.url()` etc. only sit on real URLs.
- **Removed/renamed APIs** (e.g. archiver v8 dropped the `archiver()` factory for `new ZipArchive()`; mailpit-api v2 changed the constructor signature): read the actual import/usage sites.
- **Removed translation/locale keys, etc.**: grep the consuming component.

Anything genuinely affected becomes a planned code edit, not a surprise during build.

## Phase 4 — Apply, grouped by type

Edit `package.json` group-by-group, running `pnpm install` after each group so failures are isolated:
1. **Security** (e.g. better-auth, nodemailer)
2. **Patch**
3. **Minor** (+ add `engines` / config changes that minors require)
4. **Major** (+ required code migrations + package removals)

### Transitive-dep build breaks

A bump can pull a transitive dep that breaks the bundler even though the code path is dead for us (seen with `better-auth` → `@better-auth/kysely-adapter` importing migration consts dropped from `kysely` 0.29's main barrel; we use the Prisma adapter, so it's dead code, but rolldown still chokes). Fix with a `pnpm.overrides` pin to the last working transitive version, confirm the path is truly unused, and **save a memory** (per `feedback_flag_temporary_workarounds`) so the pin is removed after the upstream is fixed. See `reference_kysely_override_better_auth`.

## Phase 5 — Verify

After all groups (or per group when risky):
1. `pnpm lint` — biome (pre-existing warnings are fine; zero errors).
2. `pnpm build` — production build + strict typecheck (catches transitive missing-export breaks).
3. `npx tsc --noEmit` — covers files outside the build graph (e.g. `e2e/`). Note: the root `tsconfig.json` `exclude` must keep out standalone sub-projects like `docs/` (Astro) and `node_modules`, or tsc/build will fail on them.
4. `pnpm test` — vitest unit.
5. **Targeted E2E** for changed deps, e.g.:
   - mail libs (mailpit-api) → `e2e/auth/register.spec.ts`, `e2e/workflows/email-notifications.spec.ts`, `e2e/reminders/*`
   - zip/export (archiver) → `e2e/api/export-submissions.spec.ts`
   - auth (better-auth) → `e2e/auth/login.spec.ts`, `register.spec.ts`
   - HTML render (html-react-parser) → relevant UI spec
   Run: `pnpm test:e2e <spec> <spec> ...`

Fix root causes, never raise timeouts (per `feedback_no_timeout_fixes`).

## Phase 6 — Commit, grouped by type

One commit per group, conventional commits, body lines ≤100 chars (use Bash + multiple `-m`):
1. `fix(deps): security updates ...`
2. `chore(deps): patch updates`
3. `chore(deps): minor updates` (mention `engines` / overrides added)
4. `chore(deps): major updates` (mention code migrations + removals)

Keep unrelated staged changes out — `git add` only the dep files (`package.json`, `pnpm-lock.yaml`) plus any migration source files you actually edited. Watch the index: a failed commit-msg leaves files staged, and a retry can sweep in unrelated staged work.

## Phase 7 — Report & follow-ups

- Update the graphify graph only if you edited source (`/graphify src --update`); pure dep bumps don't need it.
- Present a concise **"nowości warte rozważenia"** report for minors/majors: features we could adopt later (e.g. TanStack Form FormGroup, Tailwind scrollbar utilities, Prisma `queryPlanCacheMaxSize`) — list them, do **not** implement unless asked.
- End with the verification summary (lint/build/tsc/unit/E2E results) and any open decisions.

## Anti-patterns

- Bumping everything with one `pnpm update` and skipping changelogs.
- Trusting an agent's "API is stable" without reading our call-sites (archiver v8 proved it wrong).
- One giant `chore(deps)` commit — makes rollback and review impossible.
- Increasing timeouts to make E2E pass.
- Leaving a transitive-dep override undocumented.

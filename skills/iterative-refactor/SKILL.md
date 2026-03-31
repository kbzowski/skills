---
name: iterative-refactor
description: >
  Structured, multi-iteration codebase refactoring with analysis, proposals, and verification.
  Use when the user asks for deep refactoring across multiple files, architectural improvements,
  structural simplification, or iterative code quality passes. Covers: module reorganization,
  internal API redesign, type consolidation, service layer deduplication, directory restructuring,
  and framework-specific best practices.
---

# Iterative Refactoring

## When to Use

- Deep structural refactoring across multiple files or modules
- Iterative quality improvement passes over a codebase area
- Architectural reorganization (directory restructuring, layer extraction)
- Eliminating duplication across services, types, or data access patterns

## When NOT to Use

- Simple single-file renames or variable extractions — just do them directly
- Splitting a single React component — use `split-component` instead
- Greenfield development — no existing code to refactor
- Performance-only optimization without structural changes
- Code review without making changes

## Philosophy

Treat refactoring as structural improvement, not cosmetic cleanup. Make the codebase simpler to reason about, easier to extend, harder to misuse. Touch core modules, change internal APIs, move files between directories, remove unnecessary abstractions.

Small renames and extract-variable changes are fine as part of a larger effort, but they should never be the entire deliverable. If a module has deep structural problems, address them — do not paper over them with surface-level tidying.

Prefer bold changes that simplify architecture over safe changes that preserve the status quo. The build/lint/test verification step exists precisely to catch regressions from ambitious changes.

## Context gathering

Before starting any analysis, establish the project context:

1. **Read CLAUDE.md** (or equivalent project config) — extract tech stack, conventions,
   path aliases, formatting tools, test commands, locale, and any documented architectural
   decisions. This is the source of truth for project-specific rules.
2. **Identify the stack** — frameworks, ORM, bundler, test runner, linter. Use what you find
   in CLAUDE.md, `package.json`, config files, and import statements.
3. **Look up current best practices** — if web search is available, look up current documentation
   for each major framework/library in the stack. Focus on migration guides, recommended patterns,
   and deprecation notices.
4. **Note project-specific docs links** — if CLAUDE.md or README references documentation URLs,
   fetch those when relevant rather than generic search results.

Do this once per refactoring session, not before every iteration.

## Workflow

### 1. Analyze

Scan the codebase (or the area indicated by the user) and identify refactoring targets.
Look beyond surface issues — seek structural problems. Apply each analysis lens (see below)
to the target area and collect findings.

Produce a ranked list of targets with severity (high/medium/low) and estimated blast radius
(how many files/modules are affected).

### 2. Propose scope

Present the analysis to the user as a concrete proposal:

```
## Refactoring proposal — iteration N

### High priority
1. **[target]** — [what's wrong] → [what you'd change] (touches N files)
2. ...

### Medium priority
3. ...

### Suggested scope for this iteration
Targets 1–2 (they're related — fixing X enables simplifying Y).
Estimated: ~N files modified, ~N created, ~N deleted.
```

Wait for user approval or scope adjustment before proceeding. If the user rejects the proposal, ask what area or constraint to focus on and re-analyze.

### 3. Implement

Execute changes in dependency order:
1. Types, constants, schemas first
2. Service/hook layer (shared logic)
3. Consumer components / route handlers
4. Route definitions, barrel exports, index files last

After each logical group of changes, verify the build still passes. Do not batch all
changes and check at the very end — catch issues incrementally.

### 4. Verify

After all changes are complete, run the project's build, lint, and test commands
(as documented in CLAUDE.md or equivalent). If no project config exists, check `package.json`
scripts or `Makefile` for available commands. Typical sequence:
- Build
- Lint / format check
- Relevant E2E or integration tests for the changed area

If something fails, do not bypass the problem. Trace it to its root cause and fix it there.
Suppressing errors (type casts, lint-disable, `any`) is not acceptable unless the
alternative is a disproportionate yak-shave — and even then, leave a `// TODO:` with context.

### 5. Report

Generate a report following [references/report-template.md](references/report-template.md).
Present the report to the user. If the user wants it saved, ask where to save it.

The report serves as history for future iterations — be specific about what changed and why.

## Goals (priority order)

1. **Simplification** — reduce moving parts, remove indirection, make data flow obvious
2. **Readability** — code should communicate intent; a new developer should follow it without
   inline comments explaining "what this does"
3. **Strong static typing** — prefer type deduction and inference over explicit generics,
   class inheritance, or escape hatches like `any`. Reach for generics and inheritance only
   when deduction yields something worse
4. **Framework best practices** — current idioms for the project's stack (look them up, do not
   guess)
5. **Query/data optimization** — reduce round-trips, deduplicate data access into a service layer

## Analysis lenses

Apply these perspectives during the Analyze phase. Not every lens applies to every task —
use the ones relevant to the target area and the project's stack. Each lens describes what
to look for and what good looks like after refactoring.

### Components / UI

**Look for:**
- God components mixing data fetching, business logic, and presentation
- Prop drilling through 3+ levels where context or composition would be cleaner
- Inline logic in templates/JSX that obscures the render tree
- Components with 200+ lines that do multiple unrelated things
- UI state management interleaved with server state

**Target state:**
- Each component has one clear responsibility
- Data fetching lives in hooks or a service layer, not in component bodies
- Presentation components are pure — given props, they render. No side effects
- Shared UI patterns extracted into components (even if used once, when it isolates a concern)

### Database / queries / data access

**Look for:**
- Raw queries or ORM calls scattered across components or route handlers
- N+1 query patterns (fetching related data in loops)
- Duplicated query logic — same query written in multiple places with slight variations
- Missing or inconsistent data validation at the boundary (input from DB treated as trusted)
- Schema/migration drift — the code assumes a structure the schema doesn't enforce

**Target state:**
- All data access goes through a service or repository layer
- Queries are defined once, parameterized for variations
- Data shapes validated at the boundary (with schemas), typed from there on
- Related data fetched together (joins, includes) rather than in separate round-trips

### Server functions / API layer

**Look for:**
- Fat handlers doing validation + business logic + data access + response formatting
- Inconsistent error handling (some throw, some return error objects, some swallow)
- Auth/permission checks duplicated across handlers instead of middleware/wrapper
- Request/response shapes defined inline rather than as shared schemas
- Server functions that are thin wrappers around a single DB call with no added value

**Target state:**
- Handlers are thin: validate input → call service → format response
- Cross-cutting concerns (auth, logging, error handling) in middleware or wrappers
- Input/output schemas shared between client and server where applicable
- Error handling follows one consistent pattern throughout the API layer

### Types / schemas / validation

**Look for:**
- Duplicated types that describe the same entity with slight variations
- `any`, `unknown` casts, or `as` assertions used to silence the compiler
- Types defined far from where they're used, forcing readers to jump around
- Manual type definitions that could be inferred from schemas or DB models
- Validation logic (if/else checks) that duplicates what a schema already defines

**Target state:**
- Single source of truth per entity — one schema, types derived from it
- Type deduction preferred (inference, schema derivation)
- No `any` except in genuinely dynamic boundaries (third-party untyped libs)
- Validation at boundaries only — once data passes validation, trust the types
- Related types co-located with the module that owns them

### Architecture / directory structure

**Look for:**
- Files grouped by technical role (/components, /hooks, /utils) when feature-based
  grouping would better reflect actual dependencies
- Circular dependencies between modules
- Barrel files (index re-exports) that obscure the real dependency graph
- "Utils" or "helpers" folders that became dumping grounds for unrelated functions
- Modules with unclear ownership — used by everything, maintained by no one

**Target state:**
- Directory structure reflects domain/feature boundaries
- Each module has a clear public API; internals are not imported directly
- No circular dependencies — the dependency graph is a DAG
- Shared utilities are small, focused, and genuinely shared (used by 3+ consumers)
- A new developer can find code by thinking about the feature, not the file type

## What bold refactoring looks like

These are not just allowed — they are expected when the analysis justifies them:

- **Break apart god components/modules** — extract sub-units even if each piece is used only
  once. Single-use extraction is valuable when it isolates a concern.
- **Redesign internal APIs** — change function signatures, return types, prop
  interfaces when the current shape is awkward or leaky. Update all consumers.
- **Move logic to the right layer** — data fetching out of components, transformations into
  pure functions, validation into schemas.
- **Restructure directories** — move from type-based grouping to feature-based (or vice versa)
  if it better reflects actual module boundaries. Rename files to match what they actually do.
- **Delete unnecessary abstractions** — remove wrapper components, forwarding hooks, or utility
  layers that exist "for flexibility" but serve exactly one use case. Inline them.
- **Consolidate duplicated types** — find structurally identical or near-identical types across
  the codebase and unify them.
- **Rewrite, don't patch** — if a module's structure is fundamentally wrong, rewrite it from
  scratch rather than applying incremental fixes that preserve the flawed skeleton.

When a change cascades to many consumers, that is usually a sign the change is correct —
the old API was coupling things that should not have been coupled.

## Implementation rules

- Preserve all test selectors (e.g. `data-testid`) — automated tests depend on them
- Follow project conventions from CLAUDE.md / project config
- Changes in dependency order: types/constants → services/hooks → consumers → routes/exports
- Run build and lint after each logical group of changes
- Run relevant tests after completing all changes
- Do not bypass problems — find root causes and fix them at the source

## Anti-patterns to watch for

These are common mistakes during refactoring — avoid them:

- **Renaming without restructuring** — changing names achieves nothing if the underlying
  structure stays wrong
- **Extracting then re-coupling** — creating a new file but importing everything from the
  old one, producing two tightly coupled modules instead of one honest monolith
- **Over-abstracting** — introducing a generic/reusable layer for something used once.
  Extraction for readability (isolating a concern) is good; extraction for hypothetical
  reuse is premature
- **Preserving dead code** — if code is unused after refactoring, delete it. Do not comment
  it out or move it to a `_deprecated` folder
- **Type gymnastics** — complex mapped/conditional types that are harder to understand than
  the duplication they replace. Simple duplication can be better than clever types
- **Shallow iteration** — making safe, small changes to avoid risk. The verification step
  (build + lint + tests) exists so you can make ambitious changes confidently

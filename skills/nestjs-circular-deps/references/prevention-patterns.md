# Prevention Patterns

## Core Principle

Modules encapsulate functionality, not database tables. Module dependencies
form a DAG — one-way flow, no cycles. When two modules seem to need each
other, ask: who orchestrates the work?

---

## Layered Module Hierarchy

```
Layer 4: API          (controllers, resolvers)     → imports 3,2,1,0
Layer 3: Application  (use cases, CQRS handlers)   → imports 2,1,0
Layer 2: Domain       (entities, domain services)   → imports 1,0
Layer 1: Infra        (database, cache, messaging)  → imports 0
Layer 0: Core         (config, logging, health)     → imports nothing
```

```
src/
├── core/           # Layer 0
├── infrastructure/ # Layer 1
├── domain/         # Layer 2  (users/, orders/ subfolders)
├── application/    # Layer 3  (use-cases/, dto/)
└── api/            # Layer 4  (controllers/, resolvers/)
```

## Barrel File Rules

1. One barrel per module root — re-export only public API
2. **Never import from own barrel** — use direct relative paths within module
3. Barrels never import from other barrels
4. Never barrel-export module classes or providers (NestJS docs warn explicitly)
5. Keep exports minimal — unexported = no coupling

## DDD Boundaries

**Shared Kernel:** Small module with shared value objects/DTOs. Cap at ~5 exports.

**Anti-Corruption Layer:** Consumer defines abstract class, provider implements it.
Consumer never sees provider's internal types.

**Domain Events:** Cross-context side effects via EventEmitter2 or @nestjs/cqrs.
No direct module imports between bounded contexts.

## CI Gates

```bash
# madge — file-level cycle detection
npx madge --circular --extensions ts src/

# spelunker — runtime DI graph cycle detection
npx ts-node scripts/spelunker-analyze.ts --json | \
  node -e "const r=JSON.parse(require('fs').readFileSync(0,'utf8')); \
  process.exit(r.summary.totalCycles > 0 ? 1 : 0)"
```

```json
// ESLint — import/no-cycle
{ "rules": { "import/no-cycle": ["error", { "maxDepth": 3 }] } }
```

## Code Review Checklist

- [ ] New import creates a cycle? (`madge --circular`)
- [ ] Import direction correct? (lower → higher = violation)
- [ ] Can the data be passed as parameter instead of importing?
- [ ] Cross-context import going through ACL/abstract class?
- [ ] Barrel file updated correctly? No module/provider re-exports?

## NestJS Gotchas

- **`@Global()` modules** hide the dependency graph — avoid except config/logging
- **Dynamic modules** (`forRoot`/`forRootAsync`) — deps are on factory injects, not the module class
- **`LazyModuleLoader`** — masks CD errors until lazy module first loads
- **Module re-exports** — `exports: [UsersModule]` creates transitive implicit deps
- **WET > DRY** — some duplication is better than a cycle

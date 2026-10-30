---
name: update-deps
description: >
  Runs a disciplined dependency update for any language and package manager
  (npm/pnpm/yarn/bun, uv/poetry/pip, cargo, go, maven/gradle, dotnet, composer,
  bundler, pub, ...). Detects languages, package managers and monorepo projects
  first and asks when anything is unclear, checks why versions are pinned,
  researches every changelog with dedicated agents, puts security fixes first,
  categorizes patch/minor/major, verifies breaking-change claims against the
  code, applies updates grouped by type, verifies with lint, build, typecheck,
  unit and targeted E2E, and commits per group. Use when the user wants to
  update, bump or upgrade dependencies or packages, says "aktualizuj
  zaleznosci", "zaktualizuj paczki", "update dependencies", "bump deps",
  "update to latest", "--latest", or asks what is outdated.
---

# Dependency Update Pipeline

Run dependency updates methodically: real changelog research, code-level verification, grouped commits. Speed is not the goal — a correct, verified, reviewable upgrade is.

## Core rules

- **Patch** → update immediately, no questions.
- **Minor** → check if anything interests us (new features), but **update anyway**. Report noteworthy features without implementing them.
- **Major** → you **MUST** check for breaking changes AND for anything new worth adopting, before updating.
- **Always research changelogs with dedicated agents** (subagents), not inline guessing. Their knowledge may be stale — trust release notes + code, not memory.
- Reply in the user's language; English in code/commits/docs. Be terse.
- Stack/library first, DIY last. Verify "only/just/breaking" claims at the source. Treat subagent findings as hypotheses until confirmed against raw code.
- **Never guess the ecosystem.** Anything uncertain in Phase 0 is a question to the user, not an assumption.

## Environment notes

- Follow the project's commit rules. If commitlint is configured, respect its limits (e.g. body line length); pass multi-line messages as multiple `-m` flags so the shell doesn't mangle them.
- Use only the package manager the project already uses (Phase 0). Never mix (e.g. `npm install` in a pnpm repo, `pip install` in a uv/poetry project) — it rewrites or desyncs the lockfile.
- Read the project's own verification setup before running anything: `CLAUDE.md`/`AGENTS.md`, scripts in the manifest (`package.json` scripts, `pyproject` tasks, `Makefile`, `justfile`, `Taskfile`), pre-commit hooks (lefthook, husky, pre-commit) and the CI workflow. CI is the most reliable list of what "green" means.
- E2E is usually heavy. Run **targeted specs/tests**, not the full suite, unless asked.

## Workflow

Copy this checklist and tick it off as you go:

```
Update progress:
- [ ] Phase 0: units detected (path · language · manager · lockfile), scope confirmed
- [ ] Phase 1: outdated + audit run, packages categorized, every pin's reason found
- [ ] Phase 2: changelog agents dispatched and returned
- [ ] Phase 3: breaking-change claims verified in code
- [ ] Phase 4: security → patch → minor → major applied, install after each group
- [ ] Phase 5: lint, build, typecheck, unit, targeted E2E green
- [ ] Phase 6: commit plan approved by the user, then one commit per group (per unit)
- [ ] Phase 6b: headless UI components (only if used, after user consent)
- [ ] Phase 7: features report + verification summary + open decisions
```

## Phase 0 — Detect languages, package managers, and scope

Do this before anything else. Output: a list of **units** = (project path, language, package manager, lockfile).

1. **Find manifests and lockfiles** across the repo (skip `node_modules`, `.venv`, `vendor`, `target`, `dist`, `build`, `.git`). Use Glob for the signals below.
2. **Map each to a package manager:**

   | Ecosystem | Manifest | Lockfile → manager | Outdated check |
   |---|---|---|---|
   | JS/TS | `package.json` (`packageManager` field wins) | `pnpm-lock.yaml` pnpm · `yarn.lock` yarn (v1 vs berry: `.yarnrc.yml`) · `package-lock.json` npm · `bun.lock`/`bun.lockb` bun | `pnpm outdated -r` / `yarn outdated` (v1), `yarn upgrade-interactive` (berry) / `npm outdated` / `bun outdated` |
   | Python | `pyproject.toml`, `requirements*.txt`, `setup.py`, `Pipfile` | `uv.lock` uv · `poetry.lock` poetry · `pdm.lock` pdm · `Pipfile.lock` pipenv · none → pip (+ pip-tools if `*.in` files) | `uv tree --outdated --depth 1` / `poetry show --outdated --top-level` / `pdm outdated` / `pip list --outdated` |
   | Rust | `Cargo.toml` | `Cargo.lock` | `cargo outdated --root-deps-only` (if installed), else `cargo update --dry-run` + `cargo search` |
   | Go | `go.mod` (`go.work` = workspace) | `go.sum` | `go list -m -u all` |
   | JVM | `pom.xml` · `build.gradle(.kts)`, `gradle/libs.versions.toml` | — | `mvn versions:display-dependency-updates` / `./gradlew dependencyUpdates` (only if the versions plugin is configured; otherwise ask) |
   | .NET | `*.csproj`/`*.fsproj`, `Directory.Packages.props` | `packages.lock.json` | `dotnet list package --outdated` |
   | PHP | `composer.json` | `composer.lock` | `composer outdated --direct` |
   | Ruby | `Gemfile` | `Gemfile.lock` | `bundle outdated --only-explicit` |
   | Dart/Flutter | `pubspec.yaml` | `pubspec.lock` | `dart pub outdated` / `flutter pub outdated` |
   | Elixir | `mix.exs` | `mix.lock` | `mix hex.outdated` |

   Anything not in the table: identify the manager from the manifest and its docs, then confirm with the user.
3. **Detect monorepo / workspaces:** `pnpm-workspace.yaml`, `workspaces` in `package.json`, `nx.json`, `turbo.json`, `lerna.json`, `[workspace]` in `Cargo.toml`, `go.work`, `[tool.uv.workspace]`, Gradle `settings.gradle(.kts)` includes, Maven `<modules>`, `.sln` with several projects — or simply several independent manifests in subdirectories. Note whether units **share one lockfile** (one workspace) or are independent.
4. **Also note toolchain/infra pins** you see (`.nvmrc`, `.python-version`, `.tool-versions`, `.prototools`, `rust-toolchain.toml`, `engines`, Dockerfile `FROM`, CI action versions). List them; update only if the user includes them in scope — but they matter in Phase 3 (engine requirements of new versions).
5. **Ask the user (AskUserQuestion) when any of these hold:**
   - a manager is ambiguous: no lockfile, several lockfiles in one project (e.g. `package-lock.json` + `pnpm-lock.yaml`), `packageManager` contradicts the lockfile, `requirements.txt` next to `pyproject.toml` with no clear owner, Gradle/Maven without a versions plugin;
   - the language of a unit is unclear (generated code, vendored deps, example/fixture projects that may not be "real");
   - **more than one unit exists and the user did not name a project/path in the request** → ask whether the update covers the **whole repo** or **selected projects** (multiSelect list of detected units, plus "Całość").
   If the user's request already names the project or path, use it and don't ask about scope.
6. Present the detected units in one short list (path · language · manager · scope yes/no) before Phase 1.

Run Phases 1–7 **per unit in scope**. Units sharing one lockfile (a JS workspace, a Cargo/uv/Go workspace) are one unit — update them together with the workspace-level command.

## Phase 1 — Detect what's outdated

Run the unit's outdated check from the Phase 0 table.

**The outdated command is not always enough.** E.g. `pnpm outdated` misses packages whose installed version resolved *below* the latest but still *within* the caret range (radix-ui pinned at 1.4.3 in the lockfile while 1.5.0 is published the same day). If the user wants `--latest` or "truly latest", compare the registry's latest version (`npm view <pkg> version`, `pip index versions <pkg>`, `cargo search <crate>`, `go list -m -versions <mod>`, …) against the version resolved in the lockfile, and bump the ranges explicitly in the manifest.

Also note deprecated stubs (e.g. `@types/recharts` when recharts ≥3 ships its own types; `types-*` stubs once a Python lib ships `py.typed`) → flag for **removal**.

Categorize every package: **security** (regardless of bump size), **patch**, **minor**, **major**, **remove**. Security fixes are surfaced from changelogs and audit tools (`pnpm audit`, `npm audit`, `pip-audit`, `cargo audit`, `govulncheck`, `composer audit`, `bundle audit`, `dotnet list package --vulnerable`) — keep them in their own first commit.

Not every ecosystem is strict semver: treat `0.x` minor bumps as major, Go major versions change the import path (`/v2`), CalVer packages need the changelog to decide. When the category is unclear, read the changelog and categorize by actual impact.

### Pinned versions — find the reason before touching them

A pin can be accidental or deliberate, and a deliberate one may guard against a CVE or an incompatibility. **Never bump, loosen, or remove a pin before you know why it exists.**

1. **List every pin** in the unit: exact versions without a range (`"1.2.3"`, `==1.2.3`, `=1.2.3` in Cargo, `[1.2.3]` in NuGet, Gradle `strictly`), upper bounds (`<2`, `~=`), and transitive pins (`pnpm.overrides`, npm `overrides`, yarn `resolutions`, uv `override-dependencies`/`constraint-dependencies`, pip constraints files, Cargo `[patch]`, Go `replace`/`exclude`, Maven `dependencyManagement`, Gradle constraints, Dart `dependency_overrides`), plus Renovate/Dependabot ignore rules.
2. **Find the reason**, in this order: comment next to the pin → `git log -S '<pkg>' -- <manifest>` and `git blame` on the line (commit message, linked PR/issue) → saved memories / notes → `CLAUDE.md`/docs/ADRs → the upstream issue tracker for the pinned version.
3. **Classify and act:**
   - **Security (CVE / advisory / compromised release)** — the pin forces a fixed version or blocks a malicious one. Check the advisory (`npm audit`, `pip-audit`, `cargo audit`, GHSA/OSV for the package). Moving to a newer version that still contains the fix is fine; loosening or removing the pin is allowed only if every version the new range can resolve is unaffected. Never resolve to a version inside the advisory's affected range.
   - **Compatibility** (with another package, the runtime, a peer dependency, a platform) — check whether the constraint still holds: is the other package now updated, is the upstream bug fixed (issue closed, fix in the changelog)? Lift the pin only when the cause is gone, and verify that pair specifically in Phase 5.
   - **Bug in newer versions** — check whether the upstream fix has shipped. If yes, update; if not, keep the pin.
   - **Accidental** (e.g. `npm install --save-exact`, a copied snippet, no trace in history) — treat as a normal update, keep the project's usual range style.
   - **Unknown reason** — do not change it; ask the user.
4. Report every pin in the Phase 0/1 summary as: package · pinned version · latest · reason (with source: commit/issue/advisory) · decision (keep / bump pin / remove pin / ask). Every "remove pin" goes to the user for confirmation.

## Phase 2 — Research changelogs (dedicated agents, parallel)

Dispatch `general-purpose` agents IN PARALLEL (one message, multiple Agent calls), grouped so each has a focused, sized scope. A good split:
1. **All major bumps** — breaking changes are mandatory; also new features. Have the agent grep our actual usage in the repo to assess impact.
2. **Key minors** (the libraries the project leans on most: framework, router, data/ORM, validation, auth, state, styling — e.g. TanStack, Zod, Prisma, Tailwind; Django, FastAPI, SQLAlchemy, Pydantic; Spring; tokio, serde) — new features worth adopting + silent breaking/deprecations.
3. **Other minors/patches + 0.x** — features + quiet breaking; explicit verdict on any deprecated package removal.

With several units in scope, split agents per unit/ecosystem as well, so no agent mixes ecosystems.

Each agent returns, per package: version from→to, breaking changes (or "none"), impact on us (from grep), new/noteworthy features, recommendation. Tell them not to modify files and to cite official release notes.

## Phase 3 — Verify breaking-change claims in code

Do NOT take agent conclusions as fact. Confirm the dangerous ones yourself:
- **Runtime/engine bumps** (e.g. commitlint 21 needs Node ≥22; a lib dropping Python 3.9; a crate raising MSRV; `go` directive bump): check the installed runtime and the project's declared minimum (`engines`, `requires-python`, `rust-version`, `go.mod`, toolchain files from Phase 0).
- **Silent breaking patterns** (e.g. Zod 4.4 `.merge()` / `.base64()` / `.cuid()` / `z.undefined()`): grep the source for every pattern. Confirm `.url()` etc. only sit on real URLs.
- **Removed/renamed APIs** (e.g. archiver v8 dropped the `archiver()` factory for `new ZipArchive()`; mailpit-api v2 changed the constructor signature): read the actual import/usage sites.
- **Removed translation/locale keys, config options, etc.**: grep the consumers.

Anything genuinely affected becomes a planned code edit, not a surprise during build.

## Phase 4 — Apply, grouped by type

Edit the manifest group-by-group, running the manager's install/lock command after each group (`pnpm install`, `uv lock && uv sync`, `poetry lock`, `cargo update -p …`, `go get … && go mod tidy`, `dotnet restore`, `composer update <pkgs>`, `bundle update <gems>`, …) so failures are isolated:
1. **Security** (e.g. better-auth, nodemailer)
2. **Patch**
3. **Minor** (+ add `engines` / config changes that minors require)
4. **Major** (+ required code migrations + package removals)

### Transitive-dep build breaks

A bump can pull a transitive dep that breaks the build even though the code path is unused (e.g. `better-auth` → `@better-auth/kysely-adapter` importing migration consts dropped from `kysely` 0.29's main barrel; a project on the Prisma adapter never runs that code, but rolldown still fails the build). Fix with the ecosystem's pin for transitive versions (`pnpm.overrides` / npm `overrides` / yarn `resolutions`, uv `override-dependencies` or constraints, Cargo `[patch]` or `cargo update --precise`, Go `replace`, Gradle constraints / Maven `dependencyManagement`, Dart `dependency_overrides`), confirm the path is truly unused, and **leave a trace** — a comment next to the pin (where the format allows) and a note in the commit body with the upstream issue — so the pin is removed once upstream is fixed.

## Phase 5 — Verify

After all groups (or per group when risky), run the project's own checks found in the environment notes step — in this order, skipping what the project doesn't have:
1. **Lint** — zero errors (pre-existing warnings are fine).
2. **Build** — production build. In JS bundlers (rolldown/vite) the build typechecks **stricter** than `tsc` (catches missing exports in transitive deps).
3. **Typecheck** — `tsc --noEmit`, `mypy`/`pyright`, `cargo check`, `go vet` … — covers files outside the build graph (e.g. `e2e/`). The root `tsconfig.json` `exclude` must keep out standalone sub-projects like `docs/` (Astro) and `node_modules`, or tsc/build will fail on them.
4. **Unit tests** — vitest/jest, pytest, `cargo test`, `go test ./...`, `dotnet test`, …
5. **Targeted E2E / integration** for changed deps, e.g.:
   - mail libs (mailpit-api) → register / email-notification / reminder specs
   - zip/export (archiver) → export specs
   - auth (better-auth) → login / register specs
   - HTML render (html-react-parser) → relevant UI spec

In a monorepo, verify every unit that depends on what changed — not only the one whose manifest you edited.

Fix root causes, never raise timeouts.

## Phase 6 — Commit, grouped by type

**Ask for consent before the first commit.** Show the commit plan — one line per commit: message + files to stage — and ask once (AskUserQuestion) whether to commit it as planned. Consent covers that plan only; any commit outside it needs a new question. If the user declines, leave the changes uncommitted and hand over the plan with ready commit messages.

One commit per group, conventional commits (follow the project's commitlint rules if present). With several independent units, commit per group per unit and put the unit in the scope (`chore(deps/api): patch updates`):
1. `fix(deps): security updates ...`
2. `chore(deps): patch updates`
3. `chore(deps): minor updates` (mention `engines` / overrides added)
4. `chore(deps): major updates` (mention code migrations + removals)

Keep unrelated staged changes out — `git add` only the dep files (manifest + lockfile of the unit) plus any migration source files you actually edited. Watch the index: a failed commit-msg leaves files staged, and a retry can sweep in unrelated staged work.

## Phase 6b — Headless UI components (only if the project uses them)

Skip this phase unless the unit depends on a headless UI library: `radix-ui` / `@radix-ui/*` or Base UI (`@base-ui-components/react`, `@base-ui/react`), often with copied component sources (shadcn: `components.json`, `components/ui/`).

Once all updates have been completed, ask the user whether to update the headless UI components (Radix UI or Base UI, depending on the project). If consent is given, follow the current update methodology recommended by the authors (look it up — don't rely on memory). If none is available, check the current upstream version of each component manually and compare it with the code in the repo. Local changes to the copied components must survive: adapt the code instead of overwriting it.

After the component update, run the Phase 5 checks (lint, build, typecheck, unit, and E2E/UI specs that cover the touched components). This commit is outside the Phase 6 plan, so ask for consent to commit it together with the consent question above. Commit it separately from the dependency groups, staging only the component files and any manifest/lockfile changes it needed: `chore(ui): update <radix|base-ui> components` (list updated components in the body). Include it in the Phase 7 verification summary.

## Phase 7 — Report & follow-ups

- Present a concise **"new features worth considering"** report for minors/majors: features we could adopt later (e.g. TanStack Form FormGroup, Tailwind scrollbar utilities, Prisma `queryPlanCacheMaxSize`) — list them, do **not** implement unless asked.
- End with the verification summary (lint/build/typecheck/unit/E2E results per unit) and any open decisions.

## Anti-patterns

- Assuming the package manager from the language alone (Python ≠ pip, JS ≠ npm) instead of reading lockfiles.
- Updating the whole monorepo when the user meant one project — or one project when they meant all. Ask.
- Bumping or removing a pin/override without knowing why it was added — it may be the only thing blocking a CVE.
- Bumping everything with one blanket update command and skipping changelogs.
- Trusting an agent's "API is stable" without reading our call-sites (archiver v8 proved it wrong).
- One giant `chore(deps)` commit — makes rollback and review impossible.
- Increasing timeouts to make E2E pass.
- Leaving a transitive-dep override undocumented.

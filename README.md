# Skills

Personal collection of Claude Code agent skills.

## Install

The repo is a plugin marketplace, so Claude Code handles installation and updates:

```
/plugin marketplace add kbzowski/skills
/plugin install kbzowski-skills@kbzowski
```

To pull in later changes:

```
/plugin marketplace update kbzowski
/plugin update kbzowski-skills
```

## Available Skills

### Documents & research

| Skill | Description |
|-------|-------------|
| [read-pdf](skills/read-pdf/) | Convert a PDF to agent-readable Markdown with docling + GPU EasyOCR, including scans |
| [fact-check-local](skills/fact-check-local/) | Verify a document claim-by-claim against a local source corpus |
| [leapspace](skills/leapspace/) | Literature research via Elsevier LeapSpace with verifiable Scopus citations |
| [scientific-paper-review](skills/scientific-paper-review/) | Peer review of empirical papers with web verification and statistical integrity checks |
| [thesis-review](skills/thesis-review/) | Reviewer/supervisor opinions for engineering and master's theses (WIMIIP AGH) |
| [thesis-title-polish](skills/thesis-title-polish/) | Reformulate a Polish thesis title to the `[WHAT] + [DOMAIN] + [HOW] + [WHY]` schema |

### Refactoring & code quality

| Skill | Description |
|-------|-------------|
| [refactor](skills/refactor/) | Refactor for readability, strong typing, decomposition, and framework best practices |
| [iterative-refactor](skills/iterative-refactor/) | Structured codebase refactoring with analysis, proposals, and verification |
| [split-component](skills/split-component/) | Split large React components into focused files, hooks, and sub-components |
| [nestjs-circular-deps](skills/nestjs-circular-deps/) | Diagnose, fix, and prevent circular dependencies in NestJS projects |
| [gritql](skills/gritql/) | Structural AST-aware code search via the Grit CLI, for when regex isn't enough |

### Testing & maintenance

| Skill | Description |
|-------|-------------|
| [fix-playwright](skills/fix-playwright/) | Fix Playwright E2E failures and flakiness, verified by 3 consecutive green runs |
| [update-deps](skills/update-deps/) | Dependency updates with real changelog research, code-level verification, grouped commits |

### Image generation

| Skill | Description |
|-------|-------------|
| [gpt-image-2-openrouter](skills/gpt-image-2-openrouter/) | Text-to-image via OpenRouter using `openai/gpt-5.4-image-2` |
| [nano-banana-2-openrouter](skills/nano-banana-2-openrouter/) | Text-to-image via OpenRouter using `google/gemini-3.1-flash-image-preview` |
| [adobe-firefly](skills/adobe-firefly/) | Generate images in Adobe Firefly through Chrome, no API needed |

### References & integrations

| Skill | Description |
|-------|-------------|
| [pyrefly](skills/pyrefly/) | Reference for pyrefly, Meta's Rust-based Python type checker |
| [radashi](skills/radashi/) | Reference for the ~154 functions of the radashi TypeScript toolkit |
| [tanstack-docs](skills/tanstack-docs/) | Search TanStack documentation and scaffold projects with `@tanstack/cli` |
| [here-routing](skills/here-routing/) | Driving routes, distances, and travel times via HERE Maps Routing API v8 |

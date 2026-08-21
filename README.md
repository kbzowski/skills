# Skills

Personal collection of Claude Code agent skills.

## Install as a Claude Code plugin (recommended)

The repo is also a plugin marketplace, so Claude Code handles installation and updates:

```
/plugin marketplace add kbzowski/skills
/plugin install kbzowski-skills@kbzowski
```

To pull in later changes:

```
/plugin marketplace update kbzowski
/plugin update kbzowski-skills
```

The plugin declares no `version`, so its version is the git commit SHA — every pushed commit
is a new version and updates flow without a manual bump.

## Install individual skills

```bash
# Install all skills
npx skills add kbzowski/skills

# Install a specific skill
npx skills add kbzowski/skills -s iterative-refactor

# List available skills
npx skills add kbzowski/skills -l
```

## Available Skills

| Skill | Description |
|-------|-------------|
| [split-component](skills/split-component/) | Split large React components into smaller, focused files with extracted hooks, sub-components, and Context |
| [iterative-refactor](skills/iterative-refactor/) | Structured codebase refactoring with analysis, proposals, and verification |
| [fix-playwright](skills/fix-playwright/) | Fix all Playwright E2E test failures and flaky tests, verify with 3 consecutive green runs |
| [here-routing](skills/here-routing/) | Fetch real driving routes, distances, and travel times using HERE Maps Routing API v8 |
| [nestjs-circular-deps](skills/nestjs-circular-deps/) | Diagnose, fix, and prevent circular dependencies in NestJS projects |
| [tanstack-docs](skills/tanstack-docs/) | Search and fetch TanStack documentation, scaffold TanStack projects using @tanstack/cli |
| [gpt-image-2-openrouter](skills/gpt-image-2-openrouter/) | Generate images via OpenRouter using the openai/gpt-5.4-image-2 model (text-to-image) |
| [radashi](skills/radashi/) | Reference for ~154 functions in the radashi TypeScript utility toolkit (array, async, curry, object, string, typed, etc.) |
| [gritql](skills/gritql/) | Structural (AST-aware) code search via the Grit CLI — find code by *shape* (calls with string-literal args, `console.log` inside `try/catch`, etc.) when regex isn't enough |
| [nano-banana-2-openrouter](skills/nano-banana-2-openrouter/) | Generate images via OpenRouter using the google/gemini-3.1-flash-image-preview model (text-to-image, "nano-banana-2") |
| [refactor](skills/refactor/) | Codebase refactoring focused on readability, simplification, strong typing, decomposition, deduplication, and framework best practices |
| [scientific-paper-review](skills/scientific-paper-review/) | Rigorous peer review of empirical research papers with automated web verification, statistical integrity checks, and AI-slop / paper-mill detection |
| [thesis-review](skills/thesis-review/) | Reviewer/supervisor opinions for engineering & master's theses (WIMIIP AGH Informatyka Techniczna); calibrates rigor to degree level |
| [thesis-title-polish](skills/thesis-title-polish/) | Reformulate a Polish thesis title to the `[WHAT] + [DOMAIN] + [HOW] + [WHY]` schema and propose an English version |
| [pyrefly](skills/pyrefly/) | Knowledge reference for pyrefly (Meta's Rust-based Python type checker): CLI, full `pyrefly.toml` schema, 102 error kinds, mypy/pyright migration, Django/Pydantic support, baseline workflow, IDE setup, tensor shapes |
| [leapspace](skills/leapspace/) | Literature research via Elsevier LeapSpace (ScienceDirect AI assistant) driven through Chrome: grounded answers with verifiable Scopus citations, Deep Research reports, expert/funding discovery, BibTeX/RIS export |
| [update-deps](skills/update-deps/) | Disciplined dependency-update pipeline: detect outdated packages, research changelogs with parallel agents, verify breaking changes against real code, apply grouped by patch/minor/major, verify with lint/build/typecheck/unit/targeted E2E, commit per group |
| [adobe-firefly](skills/adobe-firefly/) | Generate images in Adobe Firefly (no API) driven through Chrome: pick a model (Adobe/partner), set aspect ratio / resolution or quality / reference images, generate, and download — handles reference-image upload into Firefly's shadow-DOM dropzones |
| [fact-check-local](skills/fact-check-local/) | Verify a document claim-by-claim against a local source corpus: claim registry, typed tests, evidence-mandatory verdicts, mechanical checks, independent double verification, and capture–recapture residual estimate — converges instead of finding "new" errors every pass |
| [read-pdf](skills/read-pdf/) | Convert a PDF into agent-readable Markdown with docling + GPU EasyOCR: tables reconstructed, optional figure extraction, `--full-ocr` for scans |

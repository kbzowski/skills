# Skills

Personal collection of Claude Code agent skills.

## Install

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

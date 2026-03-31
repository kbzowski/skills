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

# Iteration Report Template

Use this template for the report at the end of each refactoring iteration.

```markdown
# Iteration N: [Title]

## Date
[YYYY-MM-DD]

## Context
[1-2 sentences: what was the goal of this iteration]

## Changes

### Change 1: [name]
- **Problem:** [what was wrong]
- **Solution:** [what was done]
- **Files:** [new], [modified]

### Change 2: [name]
...

## Summary

| Metric | Before | After |
|--------|--------|-------|
| [e.g. component.tsx] | [lines] | [lines] |
| New files | 0 | N |
| [duplication, other metrics] | ... | ... |

## Verification
- [ ] Build — OK/FAIL
- [ ] Lint / format check — OK/FAIL
- [ ] Tests — [list of runs, results]

## Deferred to next iterations
- [what was skipped and why]

## Notes
- [observations, patterns to follow, risks]
```

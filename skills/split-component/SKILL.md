---
name: split-component
description: >-
  Split large React components into smaller, focused files by extracting
  sub-components, custom hooks, and utility logic. Analyze props drilling and
  suggest React Context aggregation. Use when the user asks to: extract
  components/hooks/logic, split a file, decompose a component, reduce file
  size, eliminate props drilling, introduce Context, extract hook, or
  extract component.
---

# Split Component

Split large React component files into smaller, focused modules. Extract sub-components, custom hooks, and utility logic into separate files. Analyze props flow and suggest React Context where it reduces drilling.

## When to Use

- A React component file exceeds ~200 lines and mixes multiple concerns
- Props are drilled through 2+ levels and Context would simplify the flow
- A file contains inline sub-components, hook clusters, or utility functions that deserve their own modules
- The user asks to extract, split, or decompose a component

## When NOT to Use

- The file is already small and focused (under ~100 lines)
- The target is not a React component (use `iterative-refactor` for general refactoring)
- The user wants a full multi-file architectural refactor (use `iterative-refactor` instead)
- The component is well-structured but just needs minor cleanup

## Workflow

1. **Select target** — user points to a file or component
2. **Analyze** — read the file, map its structure
3. **Propose extraction plan** — present what to extract and where, get user approval
4. **Execute** — create new files, update imports, wire Context if needed
5. **Verify** — build + lint + test pass

## Step 1: Select target

Prompt for the target file or component if not already specified.

## Step 2: Analyze

Read the target file. Produce a structured analysis. See [references/analysis-checklist.md](references/analysis-checklist.md) for the full checklist.

Key things to identify:
- Inline sub-components (JSX blocks that could be standalone)
- Hook logic (useState/useEffect clusters, data fetching, form handling)
- Utility/helper functions not tied to React lifecycle
- Props passed 2+ levels deep (drilling candidates)
- Shared state consumed by multiple extracted pieces (Context candidates)

## Step 3: Propose extraction plan

Present a concise plan to the user:

```
Extraction plan for ComponentName (src/routes/path.tsx, ~450 lines)

Extract:
1. [component] UserTable -> ./components/user-table.tsx (~80 lines)
   - receives: users, onDelete, onEdit
2. [hook] useUserFilters -> ./hooks/use-user-filters.ts (~40 lines)
   - manages: filter state, debounced search, sort
3. [util] formatUserName -> @/lib/utils/format-user-name.ts (~15 lines)

Context opportunity:
- EventFormContext wrapping EventForm
  - eliminates drilling of: formData, setFormData, errors
  - consumers: FieldList, FieldEditor, FormPreview

After extraction: ComponentName reduces to ~120 lines (orchestration + layout)
```

Wait for user approval before proceeding. If the user rejects the plan, ask what to adjust and revise.

## Step 4: Execute

Follow the extraction in dependency order (utils first, then hooks, then components, then Context).

### File placement conventions

Determine placement based on scope:

| Scope | Placement |
|-------|-----------|
| Used only by parent component | Sibling directory: `./components/`, `./hooks/` |
| Used across a route subtree | Shared directory within that subtree |
| Used app-wide | Project-wide shared directory |

### Extraction rules

- Preserve all `data-testid` attributes
- Preserve all existing exports (re-export from original file if needed for backward compat during transition)
- Use `import type` for type-only imports
- Use the project's path alias for cross-directory imports if configured, otherwise use relative paths
- Follow the project's existing file naming convention (detect from sibling files)
- Each extracted file exports one primary symbol (component, hook, or utility)

### Context extraction

When introducing React Context to eliminate props drilling:

See [references/context-patterns.md](references/context-patterns.md) for patterns.

Key rules:
- Only introduce Context when 3+ props drill through 2+ levels, or when multiple sibling components need the same parent state
- Co-locate Context with the component tree that uses it (not global unless truly global)
- Export a typed `useXxxContext` hook — never export the Context object directly
- Provider wraps the highest common ancestor, not the root

## Step 5: Verify

Run the project's build, lint, and test commands. Detect available scripts from `package.json`:
1. Build — confirm no import/type errors
2. Lint / format check
3. Relevant tests — if tests exist for the affected route or component

If the build fails after extraction, trace the error (usually a missing import or broken path) and fix it before proceeding. Do not roll back the entire extraction for a fixable error.

Report the result: verification status and final line count reduction.

# Analysis Checklist

When analyzing a component file for decomposition, check each category below.

## 1. Sub-component candidates

Identify JSX blocks that:
- Are wrapped in a conditional or map
- Have their own local event handlers
- Could render independently (have clear input/output boundary)
- Are 20+ lines of JSX

For each candidate, note:
- Proposed name
- Props it would receive
- Whether it has local state

## 2. Hook candidates

Look for clusters of:
- `useState` + `useEffect` that work together (e.g. fetch + loading + error state)
- Form state management (field values, validation, submission)
- Timer/interval/debounce logic
- Window/document event listeners
- Any 3+ hooks that serve a single concern

For each candidate, note:
- Proposed hook name (`useXxx`)
- What state it encapsulates
- What it returns (values, setters, handlers)

## 3. Utility candidates

Look for:
- Pure functions (no hooks, no JSX)
- Formatting/transformation logic
- Validation helpers
- Constants and config objects used only in this file

For each candidate, note:
- Proposed function name
- Whether it's component-specific or reusable

## 4. Props drilling analysis

Trace each prop from where it originates to where it's consumed:
- Mark props that pass through 2+ intermediate components without being used
- Group drilled props by their origin (same parent state = same Context candidate)

Score drilling severity:
- **Low**: 1-2 props, 2 levels - tolerable, skip Context
- **Medium**: 3-4 props, 2 levels - Context recommended
- **High**: 5+ props or 3+ levels - Context strongly recommended

## 5. Context candidates

For each group of drilled props, evaluate:
- How many components consume them?
- Are they read-only or read-write?
- Do they change frequently (perf concern)?
- Is there an existing Context nearby that could be extended?

Propose Context only when:
- Drilling severity is Medium or High
- 3+ components would benefit
- The data logically belongs together (single responsibility)

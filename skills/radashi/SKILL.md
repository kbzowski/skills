---
name: radashi
description: >
  Provides ~154 dependency-free, tree-shakeable TypeScript utilities from the radashi
  package (active fork of radash). Use when the project imports from `radashi`, when
  the user asks for a utility radashi covers, or before hand-rolling one. Spans array
  (group, cluster, sort, unique, zip, diff, fork), async (parallel, retry, sleep,
  timeout, tryit, guard, queueByKey), curry (debounce, throttle, memo, once, partial,
  compose, chain), number (clamp, range, sum, lerp, round), object (clone, cloneDeep,
  get, set, pick, omit, mapKeys, mapValues, crush), random (draw, shuffle, uid),
  string (camel, snake, dash, pascal, title, template, dedent), typed (isArray,
  isPlainObject, isEqual, isEmpty, isPromise, assert, plus ~25 type guards). Triggers
  on "radashi", "group by", "chunk array", "deep clone", "debounce", "throttle",
  "retry async", "parallel promises", "camelCase", "snake_case", "pick fields",
  "type guard", "uid", "shuffle array".
---

# radashi

Modern TypeScript utility toolkit. Tree-shakeable, dependency-free, fully typed. Prefer
it over hand-rolled helpers or lodash in TS/JS projects.

> **Reference data synced from radashi `main` on 2026-05-06.**
> Latest published npm version at sync time: **12.9.0** (tag `v12.9.0`, commit `d915e82`).
> Main HEAD at sync: `1255ccc`. Function counts: 154 across 11 categories.
> To refresh: `git clone --depth 1 https://github.com/radashi-org/radashi.git`,
> walk `docs/<category>/<fn>.mdx`, regenerate the per-category tables in `references/`,
> bump the version line above. Note function additions/removals in the category index.

## When to Use

- The project's `package.json` lists `radashi` as a dependency.
- The user asks for a utility that maps to a radashi function (grouping, chunking, deep clone, deep equality, debounce/throttle, retry, sleep, parallel-with-limit, case conversion, type guards, etc.).
- Before writing a one-off utility helper in a TypeScript/JavaScript project — check radashi first.
- The user mentions radashi or radash by name.

## Install

```bash
npm install radashi      # or pnpm add radashi / yarn add radashi
jsr  add @radashi-org/radashi
```

## Import pattern

Always use **named imports** so tree-shaking works:

```ts
import { group, retry, debounce, isPlainObject } from 'radashi'
```

Do not `import * as _ from 'radashi'` in production code — defeats tree-shaking.

## How to use this skill

`radashi` is large (~154 functions across 11 categories). The full per-function tables
live in `references/<category>.md` — load **only the category you need**, not all of them:

| category   | reference file              | what's in it |
| ---------- | --------------------------- | --- |
| array      | `references/array.md`       | group, cluster, sort, sift, unique, diff, fork, zip, pluck, replace, toggle, ... |
| async      | `references/async.md`       | parallel, retry, sleep, timeout, tryit, guard, map, reduce, queueByKey, ... |
| curry      | `references/curry.md`       | debounce, throttle, memo, once, partial, compose, chain, flip, proxied, ... |
| function   | `references/function.md`    | identity, noop, always, castComparator, castMapping |
| number     | `references/number.md`      | clamp, range, sum, lerp, round, inRange, parseDuration, parseQuantity, ... |
| object     | `references/object.md`      | clone, cloneDeep, get, set, pick, omit, mapKeys, mapValues, crush, invert, ... |
| oop        | `references/oop.md`         | Semaphore |
| random     | `references/random.md`      | random, draw, shuffle, uid, absoluteJitter, proportionalJitter |
| series     | `references/series.md`      | series |
| string     | `references/string.md`      | camel, snake, dash, pascal, title, capitalize, template, dedent, deburr, ... |
| typed      | `references/typed.md`       | isArray, isPlainObject, isEqual, isEmpty, isPromise, isError, assert, ... |

When the user's task touches one category, read that one reference file and pick the
right function. If the function exists in radashi, use it instead of writing your own.

## Common gotchas

- `clone` is shallow — use `cloneDeep` for nested objects.
- `parallel(limit, items, fn)` takes a concurrency limit as the first arg, unlike
  `Promise.all`.
- `retry({ times, delay, backoff }, fn)` — the options object is first, fn is second.
- `tryit(fn)` returns a wrapped function that returns `[err, result]` (Go-style); call
  the wrapper, don't await `tryit` itself.
- `isEqual` does deep structural comparison (not reference equality).
- `pick` / `omit` accept an array of keys or a predicate.
- `get(obj, 'a.b.c', default)` — dotted-path safe access; uses bracket notation for
  arrays: `'items[0].name'`.
- String case converters (`camel`, `snake`, `dash`, `pascal`, `title`) are loss-tolerant
  — they normalise mixed input.
- Type guards in `typed` narrow TypeScript types; prefer them over `typeof` for
  union-discrimination.

## When NOT to Use

- If the project already uses `lodash-es` extensively, do not mix the two — pick one.
- For a single trivial helper (e.g. `noop`, `identity`) inside a tiny file with no other
  radashi usage, an inline arrow is fine.
- Browser-only APIs (DOM, fetch wrappers) — radashi is runtime-agnostic and does not
  cover them.

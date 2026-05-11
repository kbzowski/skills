---
name: gritql
description: >
  Searches source code structurally (AST-aware) via the Grit CLI (`@getgrit/cli`).
  Use when ripgrep/Grep is the wrong tool because the question is about code
  *shape*, not text:
  "all calls of foo where the first argument is a string literal", "all console.log
  inside try/catch", "all imports of X used only as a type", "all async functions
  that don't await anything", "all React components missing a key prop", "all SQL
  queries with a hardcoded LIMIT". Works across JavaScript, TypeScript, TSX, Python,
  Go, Rust, Java, CSS, HTML, JSON, YAML, SQL, HCL/Terraform, Solidity, Markdown.
  Triggers on "GritQL", "grit apply", "structural search", "AST search", "AST grep",
  "tree-sitter search", "codemod", "find pattern", "semgrep-style", "search by
  syntax", or any search request whose constraint is structural ("inside", "calls
  with N args", "where the body contains", "only when wrapped in").
---

# GritQL — structural code search

GritQL is Grit's query language for searching source code by **syntax structure**,
not text. A pattern in backticks like `` `console.log($msg)` `` matches every
`console.log(...)` call regardless of quote style, whitespace, line breaks, or
semicolons — because matching happens against the parsed AST, not the source string.

This skill is **search-only**. GritQL can also rewrite code with `=>`, but that's
out of scope here — use it for finding things Grep can't find.

## When to Use

Reach for GritQL when the search constraint is **structural**:

- "All `foo()` calls whose first argument is a string literal."
- "All `console.log` calls inside a `try` block."
- "All `import`s of `X` used only as a type."
- "All functions that return a `Promise` but aren't declared `async`."
- "All React components missing a `key` prop inside `.map()`."
- Anything whose phrasing includes *inside*, *containing*, *wrapped in*, *with N arguments*, *not used as*.

## When NOT to Use

Stay with **Grep** (ripgrep) when:

- Searching for a symbol name, string literal, filename, or any pure-text token.
- A single regex expresses the query with no false positives.
- You need fuzzy/partial matches across non-code files.
- You're scanning very large repos for speed and don't need AST awareness — ripgrep is faster on cold text scans.
- The language isn't supported by Grit (anything outside `js`/`ts`/`tsx`/`python`/`go`/`rust`/`java`/`css`/`html`/`json`/`yaml`/`sql`/`hcl`/`solidity`/`markdown`).

## Install

```bash
npm install -g @getgrit/cli
grit --version
```

That's it. No login, no daemon. Run `grit init` once in a repo if you want a
`.grit/` config directory for saved patterns; for ad-hoc search you don't need it.

To silence telemetry: `export GRIT_TELEMETRY_DISABLED=true` (or set the env var
on Windows).

## Two ways to run a pattern

**Inline** — fastest for one-off questions, no file needed:

```bash
grit apply '`console.log($msg)`' --lang js
```

**`.grit` file** — for anything non-trivial or that you'll reuse. Save as
`find-logs.grit`:

```grit
engine marzano(0.1)
language js

`console.log($msg)` where {
  $msg <: within `try { $_ } catch($_) { $_ }`
}
```

Then: `grit apply ./find-logs.grit`.

The `engine marzano(0.1)` + `language <lang>` header is **required** in `.grit`
files. Languages: `js`, `ts`, `tsx`, `python`, `go`, `rust`, `java`, `css`,
`html`, `json`, `yaml`, `sql`, `hcl`, `solidity`, `markdown`.

## Minimum-viable syntax (the ~10 things you'll actually use)

```
`code with $metavar`        # backtick-wrapped code snippet, structural match
$x                          # named metavariable, captures anything
$_                          # anonymous metavar (don't care)
$...                        # spread, matches 0+ nodes (e.g. argument lists)

pattern where { ... }       # add conditions
$x <: pattern               # "$x matches pattern" — the workhorse predicate
$x <: string()              # built-in: $x is a string literal
$x <: within `outer($_)`    # $x is somewhere inside this outer shape
$x <: contains `inner($_)`  # $x contains this inner shape

or { p1, p2 }               # match any
and { p1, p2 }              # match all (rarely needed at top level)
not pattern                 # negate
maybe pattern               # optional — don't fail if absent

r"regex"($capture)          # regex with capture; useful inside where {}
```

That's enough for ~90% of real searches. The rest (`bubble`, `limit N`,
`range(start_line=...)`, list/dict indexing, custom `function` blocks) lives in
`references/syntax-cheatsheet.md`.

## Worked examples

### 1. Every `console.log` call, anywhere

```bash
grit apply '`console.log($msg)`' --lang js
```

### 2. Every `console.log` whose argument is a string literal

```bash
grit apply '`console.log($msg)` where { $msg <: string() }' --lang js
```

### 3. Every `console.log` **inside** a try/catch

```grit
engine marzano(0.1)
language js

`console.log($msg)` where {
  $msg <: within `try { $_ } catch($_) { $_ }`
}
```

### 4. Every `useState` call where the initial value is `null`

```grit
engine marzano(0.1)
language tsx

`useState($init)` where {
  $init <: `null`
}
```

### 5. Every Python function decorated with `@pytest.fixture`

```grit
engine marzano(0.1)
language python

`@pytest.fixture
def $name($...): $_`
```

More recipes per language live in `references/examples-search.md`.

## Where to find more

- `references/syntax-cheatsheet.md` — full operator/predicate table.
- `references/cli-usage.md` — `grit apply` flags, `grit list`, `grit check`, `.grit` file layout, stdlib patterns.
- `references/examples-search.md` — copy-pasteable patterns per language (JS/TS, Python, Go, CSS).

## Gotchas worth knowing up front

- **Backticks are mandatory** around code snippets. `console.log($m)` without
  backticks is a syntax error.
- **Inline patterns on the shell need careful quoting.** On bash/zsh, wrap the
  whole argument in single quotes so the backticks aren't interpreted:
  `grit apply '`foo($x)`' --lang js`. On PowerShell, prefer a `.grit` file —
  PowerShell mangles backticks (it uses them as the line-continuation character).
- **Whitespace/quote style don't matter** in the pattern — structural match. But
  the **shape** does: `` `foo($x)` `` won't match `foo(a, b)` because the arg
  count differs. Use `` `foo($...)` `` for variadic.
- **`<:` is left-to-right** ("$x matches this pattern"), not assignment. Easy to
  swap mentally if you've used `=~` languages.
- **Default scan is the current directory.** Pass paths after the pattern:
  `grit apply '`foo($x)`' src/ --lang js`.
- **Language inference** works from file extensions, but for inline patterns
  always pass `--lang` to avoid surprises.

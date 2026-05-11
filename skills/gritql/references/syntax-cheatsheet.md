# GritQL syntax cheatsheet

Full operator/predicate reference. SKILL.md covers the ~10 most common; this is
everything else, grouped by what you're trying to do.

## File header (`.grit` files only)

```grit
engine marzano(0.1)
language js
```

Languages: `js`, `ts`, `tsx`, `python`, `go`, `rust`, `java`, `css`, `html`,
`json`, `yaml`, `sql`, `hcl`, `solidity`, `markdown`. Inline patterns infer
language from `--lang` or file extension.

## Metavariables

| Form    | Meaning                                                |
| ------- | ------------------------------------------------------ |
| `$x`    | Named binding. Same name in two places → must match same node. |
| `$_`    | Anonymous wildcard. Don't capture, don't constrain.    |
| `$...`  | Spread. Matches zero or more siblings (args, statements, etc.). |
| `$...rest` | Named spread. Captures the rest.                    |

## Code snippets

Wrap any code in **backticks**; that's a pattern.

```
`console.log($msg)`
`function $name($...args) { $...body }`
`for ($i = 0; $i < $n; $i++) { $...body }`
```

Structural match: quote style, whitespace, semicolons, trailing commas all
ignored. Argument **count** does matter — use `$...` for variadic.

## The `<:` match operator

Read it as **"matches"**. The metavariable on the left is tested against the
pattern on the right.

```grit
$x <: string()                  // $x is a string literal
$x <: number()                  // $x is a numeric literal
$x <: identifier()              // $x is a bare identifier
$x <: `foo($_)`                 // $x is shaped like foo(anything)
$x <: or { `null`, `undefined` }
$x <: not `bar`
```

## Tree navigation

Used inside `where { ... }`:

| Operator   | Direction | Meaning                                          |
| ---------- | --------- | ------------------------------------------------ |
| `contains` | downward  | The node has a descendant matching pattern.      |
| `within`   | upward    | The node has an ancestor matching pattern.       |
| `before`   | sibling   | There's a matching node before this one.         |
| `after`    | sibling   | There's a matching node after this one.          |
| `includes` | inline    | Like `contains` but only direct text inclusion.  |

```grit
`console.log($_)` where {
  $_ <: within `function $_($...) { $...body }`
}
```

## Logical composition

```grit
or  { p1, p2, p3 }   // any
and { p1, p2 }       // all (often implicit inside where {})
not pattern          // negate
maybe pattern        // optional — succeed even if absent
```

## Conditions and assignment

```grit
pattern where {
  $x <: string(),
  $y <: not `null`,
  $count > 3,           // numeric comparisons
  $name == "foo",       // equality
  $list <: some { ... } // at least one element matches
}
```

Inside `where`, you can also bind variables:

```grit
$x = "literal"
$x += "appended"
$list = [1, 2, 3]
```

## Predicates / built-in patterns

| Predicate                       | Matches                              |
| ------------------------------- | ------------------------------------ |
| `string()`                      | String literal                       |
| `number()`                      | Numeric literal                      |
| `boolean()`                     | `true` or `false`                    |
| `identifier()`                  | Bare identifier                      |
| `literal(value="42")`           | Literal with a specific value        |
| `call_expression()`             | Any function call (lang-specific)    |
| `call_expression(callee=$x)`    | Field-based AST match                |
| `r"regex"`                      | Regex string match                   |
| `r"regex"($cap)`                | Regex with capture group → metavar   |

Each language has its own AST node types (`call_expression`, `function_declaration`,
`jsx_element`, etc.); browse them by running `grit list` or peeking at
tree-sitter grammars.

## Lists, dicts, indexing

```grit
$list[0]                  // first element
$list[-1]                 // last element
$list <: some pattern     // some element matches
$list <: every pattern    // every element matches
$map.key                  // dict access
```

## Scope & flow control

| Construct           | What it does                                                  |
| ------------------- | ------------------------------------------------------------- |
| `pattern as $var`   | Bind the whole matched node to `$var`.                        |
| `bubble`            | Isolate metavariables to this scope (don't leak outward).     |
| `bubble($x)`        | Like `bubble`, but `$x` pierces the bubble.                   |
| `sequential { ... }`| Apply patterns in order (mostly for rewrites).                |
| `multifile { ... }` | Match across multiple files with shared metavars.             |
| `limit N`           | Stop after N matches.                                         |
| `range(start_line=1, end_line=50)` | Restrict to a line range.                  |

## Comments

```grit
// single-line only
```

## Custom functions (advanced)

```grit
function uppercase($s) js {
  return $s.toUpperCase()
}
```

The `js` block embeds JavaScript executed by the engine. Useful for computed
values inside `where`; rarely needed for pure search.

## Rewrite operator (out of scope, mentioned for completeness)

`pattern => replacement` rewrites code; `pattern => .` deletes. This skill is
search-only — see https://docs.grit.io/language/overview for rewrite docs.

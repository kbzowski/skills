# GritQL search recipes

Copy-pasteable patterns grouped by language. Each is a complete `.grit` file
unless marked **inline**.

## JavaScript / TypeScript

### Every `console.log` call (inline)

```bash
grit apply '`console.log($msg)`' --lang js
```

### `console.log` with a string-literal first argument

```grit
engine marzano(0.1)
language js

`console.log($msg)` where {
  $msg <: string()
}
```

### `console.log` inside a `try` block

```grit
engine marzano(0.1)
language js

`console.log($msg)` where {
  $msg <: within `try { $_ } catch($_) { $_ }`
}
```

### Functions returning a Promise but not declared `async`

```grit
engine marzano(0.1)
language ts

`function $name($...args): Promise<$T> { $...body }` where {
  $name <: not within `async function $_($...) { $... }`
}
```

### `useState(null)` calls (likely missing types in TS)

```grit
engine marzano(0.1)
language tsx

`useState($init)` where {
  $init <: `null`
}
```

### Test files using `.only` (left over from debugging)

```grit
engine marzano(0.1)
language js

or {
  `it.only($...)`,
  `test.only($...)`,
  `describe.only($...)`
}
```

### `fetch()` calls with a hardcoded URL string

```grit
engine marzano(0.1)
language ts

`fetch($url, $...rest)` where {
  $url <: string()
}
```

### `import` of a specific module

```grit
engine marzano(0.1)
language ts

`import $what from "react"`
```

### React components missing a `key` prop in a `.map()`

```grit
engine marzano(0.1)
language tsx

`$arr.map(($item) => $jsx)` where {
  $jsx <: not contains `key=$_`
}
```

## Python

### Every `print()` call

```grit
engine marzano(0.1)
language python

`print($...)`
```

### `pytest` fixtures

```grit
engine marzano(0.1)
language python

`@pytest.fixture
def $name($...): $_`
```

### Bare `except:` clauses (anti-pattern)

```grit
engine marzano(0.1)
language python

`try:
    $_
except:
    $_`
```

### Functions decorated with `@staticmethod` but using `self`

```grit
engine marzano(0.1)
language python

`@staticmethod
def $name(self, $...): $...body`
```

## Go

### Every `fmt.Println` call

```grit
engine marzano(0.1)
language go

`fmt.Println($...)`
```

### Error-ignoring assignments (`_, err := ...; _ = err`)

```grit
engine marzano(0.1)
language go

`_ = $err` where {
  $err <: identifier()
}
```

## CSS

### `!important` declarations

```grit
engine marzano(0.1)
language css

r".+!important.*"
```

### Fixed pixel font-sizes (use rem instead)

```grit
engine marzano(0.1)
language css

`font-size: $sizepx`
```

## Recipe template

When in doubt, start with the literal code you'd be looking for, then replace
the parts that vary with `$metavars`:

1. Write the code: `myFn("hello", 42)`
2. Replace variables: `` `myFn($a, $b)` ``
3. Add constraints inside `where { ... }` only if needed.
4. Run inline first (`grit apply '...' --lang xxx`), promote to a `.grit` file
   once it's worth keeping.

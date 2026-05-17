# Migrating from mypy

## Step 1 — auto-migrate

```bash
pyrefly init path/to/project
```

Reads `mypy.ini` / `setup.cfg [mypy]` / `[tool.mypy]` and produces a `pyrefly.toml`.
Then **review the generated config** — not all options translate cleanly.

## Step 2 — match mypy defaults (if desired)

Mypy by default doesn't type-check unannotated function bodies; pyrefly does. To
mimic mypy's default:

```toml
check-unannotated-defs = false
infer-return-types     = "never"
```

For mypy `--check-untyped-defs` / `--strict`:
```toml
check-unannotated-defs = true
infer-return-types     = "never"
```

Honor existing `# type: ignore` comments:
```toml
permissive-ignores = true
```

## Step 3 — handle the noise

Either fix errors immediately, or snapshot them:
```bash
pyrefly check --baseline=pyrefly_baseline.json --update-baseline
```

See `suppressions-and-baseline.md`.

## Option mapping

| Mypy | Pyrefly |
| --- | --- |
| `files` / `modules` / `packages` | `project-includes` (note: mypy doesn't recurse into `modules`, pyrefly does) |
| `python_version` | `python-version` |
| `platform` | `python-platform` |
| `mypy_path` | `search-path` |
| `[mypy-foo.*] ignore_missing_imports = True` | `replace-imports-with-any = ["foo.*"]` |
| `disable_error_code` / `enable_error_code` (per-module) | `sub-config` with `[errors]` table |
| `strict = True` | `preset = "strict"` (approximate) |
| `check_untyped_defs` | `check-unannotated-defs` |
| `warn_unused_ignores` | `unused-ignore` error kind (on by default) |

## Per-module configs

Pyrefly's `sub-config` only supports diagnostic settings. Mypy per-module options
beyond `disable_error_code` / `enable_error_code` **don't migrate**.

## Error code mapping (full table from docs)

| Mypy code | Pyrefly kind |
| --- | --- |
| `abstract` | `bad-instantiation` |
| `arg-type` | `bad-argument-type` |
| `assert-type` | `assert-type` |
| `assignment` | `bad-assignment` |
| `attr-defined` | `missing-attribute` |
| `await-not-async` | `not-async` |
| `call-arg` | `bad-argument-count` |
| `call-overload` | `no-matching-overload` |
| `deprecated` | `deprecated` |
| `dict-item` | `bad-typed-dict` |
| `import` | `missing-import` |
| `import-not-found` | `missing-import` |
| `import-untyped` | `untyped-import` |
| `index` | `bad-index`, `unsupported-operation` |
| `metaclass` | `invalid-inheritance` |
| `name-defined` | `unknown-name` |
| `name-match` | `name-mismatch` |
| `no-overload-impl` | `invalid-overload` |
| `no-untyped-def` | `implicit-any` |
| `operator` | `unsupported-operation` |
| `override` | `bad-override` |
| `possibly-undefined` | `unbound-name` |
| `redundant-cast` | `redundant-cast` |
| `redundant-expr` | `redundant-condition` |
| `return` | `bad-return` |
| `return-value` | `bad-return` |
| `syntax` | `parse-error` |
| `top-level-await` | `not-async` |
| `truthy-bool` | `redundant-condition` |
| `truthy-function` | `redundant-condition` |
| `truthy-iterable` | `redundant-condition` |
| `type-arg` | `implicit-any` |
| `type-var` | `bad-specialization` |
| `typeddict-readonly-mutated` | `read-only` |
| `typeddict-unknown-key` | `bad-typed-dict-key` |
| `union-attr` | `missing-attribute` |
| `unused-awaitable` | `unused-coroutine` |
| `unused-coroutine` | `unused-coroutine` |
| `used-before-def` | `unbound-name` |
| `valid-type` | `invalid-annotation` |

## Suppression comment translation

```python
# Before (mypy):
x = something()  # type: ignore[assignment]

# Pyrefly also honors `# type: ignore` natively, or you can switch to:
x = something()  # pyrefly: ignore[bad-assignment]
```

With `permissive-ignores = true`, the mypy form works unchanged.

## Caveat from docs

> "While there is an overlap between mypy's config options and pyrefly's config
> options, it's not always possible to cleanly translate one config option to
> another." — always review `pyrefly init` output.

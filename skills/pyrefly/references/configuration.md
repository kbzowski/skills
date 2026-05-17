# Pyrefly Configuration Reference

Configuration lives in **`pyrefly.toml`** OR **`[tool.pyrefly]`** in `pyproject.toml`.
**All keys are `kebab-case`.**

Run `pyrefly init` first — never hand-write a config from scratch.

## File selection

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `project-includes` | list of globs | `["**/*.py*"]` | Files to type-check |
| `project-excludes` | list of globs | `["**/node_modules", "**/__pycache__", "**/venv/**", "**/.[!/.]*/**"]` + site-packages | Filter from `project-includes` |
| `disable-project-excludes-heuristics` | bool | `false` | Set true to fully reset excludes to `[]` |

## Import resolution

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `search-path` | list of dirs | auto-detected import root | **Highest precedence** in import resolution |
| `disable-search-path-heuristics` | bool | `false` | Disable auto search-path detection |
| `site-package-path` | list of dirs | `./typings` + interpreter packages | **Lowest priority** in import resolution |

Resolution order: `search-path` → typeshed → fallback search-path → `site-package-path` → error.

## Python environment

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `python-version` | `"3.X[.Y]"` string | from interpreter or `3.13.0` | Controls `sys.version` checks |
| `python-platform` | string | from interpreter or `"linux"` | Controls `sys.platform` checks |
| `python-interpreter-path` | path | `$(which python3)` then `python` | Interpreter to query |
| `fallback-python-interpreter-name` | string | `python3` then `python` | If `python-interpreter-path` unset |
| `conda-environment` | string | none | Name of conda env to query |
| `skip-interpreter-query` | bool | `false` | Use hard-coded defaults instead |
| `typeshed-path` | path | bundled typeshed | Override bundled typeshed |

## Type-checking behavior

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `check-unannotated-defs` | bool | `true` | Check bodies of fully-unannotated functions |
| `infer-return-types` | `"never"` / `"annotated"` / `"checked"` | `"checked"` | When to infer return types |
| `infer-with-first-use` | bool | `true` | Infer TypeVars on first usage (else `Any`) |
| `strict-callable-subtyping` | bool | `false` | Enforce strict parameter compatibility |

For **mypy-default semantics**:
```toml
check-unannotated-defs = false
infer-return-types     = "never"
```

For **mypy `--strict` / `--check-untyped-defs` semantics**:
```toml
check-unannotated-defs = true
infer-return-types     = "never"
```

## Error configuration

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `preset` | `"off"` / `"basic"` / `"legacy"` / `"default"` / `"strict"` | none | Base error-rule preset |
| `errors` | table `{ kind = bool }` | `{}` | Per-kind toggle (true=on, false=off) |
| `min-severity` | `"ignore"` / `"info"` / `"warn"` / `"error"` | `"error"` | Minimum severity to display |
| `output-format` | `"min-text"` / `"full-text"` / `"json"` / `"github"` / `"omit-errors"` | `"full-text"` | Default for `pyrefly check` |
| `baseline` | path to JSON | none | Errors in this file are suppressed |
| `disable-type-errors-in-ide` | bool | `false` | Suppress type errors in IDE mode only |

Example:
```toml
[tool.pyrefly]
preset = "strict"

[tool.pyrefly.errors]
missing-import      = false
implicit-any        = false
unused-coroutine    = true
```

## Imports — special handling

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `replace-imports-with-any` | list of regex | `[]` | Unconditionally replace these modules with `Any` |
| `ignore-missing-imports` | list of regex | `[]` | Only replace with `Any` if module not found |

Used during mypy migration: `[mypy-some.module] ignore_missing_imports = True` becomes
`replace-imports-with-any = ["some.module"]`.

## Miscellaneous

| Option | Type | Default | Notes |
| --- | --- | --- | --- |
| `use-ignore-files` | bool | `true` | Honor `.gitignore` etc. |
| `ignore-errors-in-generated-code` | bool | `false` | Skip files containing `@generated` |
| `permissive-ignores` | bool | `false` | Honor mypy/pyright ignore comments |
| `enabled-ignores` | list | `["type", "pyrefly"]` | Which tools' ignores to respect |
| `skip-lsp-config-indexing` | bool | `false` | Disable project indexing in LSP mode |
| `sub-config` | TOML array of tables | `[]` | Per-path overrides (only diagnostic settings) |
| `tensor-shapes` | bool | `false` | **Experimental.** Enable tensor shape inference |
| `extra-file-extensions` | list | `[]` | Additional extensions to treat as Python |
| `recursion-depth-limit` | int | `0` | Debug: max inference recursion |
| `recursion-overflow-handler` | `"break-with-placeholder"` / `"panic-with-debug-info"` | `"break-with-placeholder"` | Debug |

## `sub-config` (per-path overrides)

Only **diagnostic settings** (`errors`, `min-severity`, etc.) can be overridden —
*not* `python-version`, `python-platform`, or `search-path`. This is a notable
limitation vs. pyright's execution environments.

```toml
[[tool.pyrefly.sub-config]]
matches = ["tests/**/*.py"]

[tool.pyrefly.sub-config.errors]
implicit-any = false
```

## Minimal sane config

```toml
[tool.pyrefly]
project-includes = ["src/**/*.py", "tests/**/*.py"]
python-version   = "3.12"
preset           = "default"
```

## Debugging

`pyrefly dump-config` prints the resolved config (post-heuristics, with detected
interpreter values) for any file in the project.

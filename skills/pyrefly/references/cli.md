# Pyrefly CLI Reference

All commands run from project root unless paths given. Pyrefly looks for
`pyrefly.toml` or `[tool.pyrefly]` in `pyproject.toml`.

## `pyrefly init [path]`

Generates a config. Auto-migrates from existing config:

- Reads `mypy.ini`, `setup.cfg [mypy]`, or `[tool.mypy]` in `pyproject.toml`.
- Reads `pyrightconfig.json` or `[tool.pyright]` in `pyproject.toml`.
- Writes `pyrefly.toml` (or appends `[tool.pyrefly]` to `pyproject.toml`).

Run this **before** writing config by hand. Review the output — some options
(per-module overrides, execution environments) don't translate cleanly.

## `pyrefly check [paths...]`

Run the type checker. With no args, checks the whole project.

Headline flags:

| Flag | Description |
| --- | --- |
| `--summarize-errors` | Short summary instead of full per-error output |
| `--output-format=FORMAT` | One of `min-text`, `full-text` (default), `json`, `github`, `omit-errors` |
| `--baseline=PATH` | Compare against baseline JSON; only report new errors |
| `--update-baseline` | Combined with `--baseline`: overwrite the baseline with current errors |
| `-c`, `--config=PATH` | Use a specific config file |
| `-p`, `--preset=NAME` | `off`/`basic`/`legacy`/`default`/`strict` |
| `--min-severity=LEVEL` | `ignore`/`info`/`warn`/`error` |
| `--error=KIND` / `--warn=KIND` / `--ignore=KIND` | Per-kind severity override (repeatable) |

Most config options are **also CLI flags** (the kebab-case key prefixed with `--`).
Useful ones for ad-hoc overrides:

```
--project-excludes          --search-path           --site-package-path
--python-version            --python-platform       --python-interpreter-path
--fallback-python-interpreter-name                  --skip-interpreter-query
--typeshed-path             --conda-environment
--check-unannotated-defs    --infer-return-types    --infer-with-first-use
--strict-callable-subtyping --permissive-ignores    --enabled-ignores
--use-ignore-files          --ignore-errors-in-generated-code
--replace-imports-with-any  --ignore-missing-imports
--disable-project-excludes-heuristics               --disable-search-path-heuristics
--tensor-shapes
--recursion-depth-limit     --recursion-overflow-handler
```

Examples:
```bash
pyrefly check                                # all project files
pyrefly check src/module.py                  # one file
pyrefly check --output-format=github         # GitHub Actions annotations
pyrefly check --baseline=pyrefly_baseline.json --update-baseline   # snapshot
```

## `pyrefly suppress`

Bulk-add `# pyrefly: ignore` comments for all currently-detected errors.

| Flag | Description |
| --- | --- |
| `--comment-location=same-line` | Place ignore on the error line, not the line above |
| `--remove-unused` | Remove ignore comments that no longer suppress any error |

Workflow for adoption on a dirty codebase:
```bash
pyrefly suppress                              # silence everything
# ... fix errors gradually ...
pyrefly suppress --remove-unused              # clean up after a pass
```

## `pyrefly infer <path>`

Auto-add type annotations to source files in place. Status: under active
development. Flags toggle parameters / return types / containers (specific names
not enumerated in docs).

Caveats from docs:
- "Currently under active development"
- "Manually review the changes created by `pyrefly infer`"
- "It is common that new annotations will expose new type errors"
- Run in small batches.

## `pyrefly stubgen <path>`

Generate `.pyi` stubs.

| Flag | Default | Description |
| --- | --- | --- |
| `-o`, `--output-dir` | `out` | Output directory (mirrors source structure) |
| `--include-private` | off | Include `_single_leading_underscore` names |
| `--include-docstrings` | off | Preserve docstrings in stubs |

Extracts functions/methods, classes, module/class variables, imports, type aliases.
Dunder names always included. Unresolvable types annotated as `Incomplete` from
`_typeshed`. **Experimental.**

## `pyrefly coverage report <path>`

JSON report with `files` (per-file) and `summary` (aggregate) keys.

Per-file fields: line count, functions (with `is_type_known`, `is_return_type_known`,
parameter-level `is_type_known`), classes, suppressions, annotation completeness %,
type completeness %.

Summary fields: `total_files`, `total_functions`, `fully_annotated_functions`,
`type_complete_functions`, `aggregate_annotation_completeness`,
`aggregate_type_completeness`.

Definitions:
- **Fully annotated** = return type + all params annotated (excluding `self`/`cls`).
- **Type-complete** = fully annotated AND no `Any` in resolved types.

Pipe into `jq` or dashboards. **Experimental.**

## `pyrefly dump-config`

Debug command. Prints the resolved configuration (including auto-detected
search-path, site-package-path, interpreter info) for a given file. Use to diagnose
"missing-import" errors and import precedence surprises.

## `pyrefly lsp`

Run as a Language Server (LSP). Used by editor integrations — usually invoked by
the editor, not the user directly. See `references/ide-setup.md`.

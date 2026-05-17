# Error Suppressions and Baseline

Two independent mechanisms:

- **Suppression comments** = ignore specific errors at specific source locations.
- **Baseline file** = snapshot all current errors so CI fails only on *new* ones.

Use baseline for adopting pyrefly on a dirty codebase; use suppressions for genuinely
unsolvable cases that should stay silent forever.

## Comment syntax

```python
# pyrefly: ignore
x: str = 1                       # error suppressed (line below)

x: str = 1  # pyrefly: ignore    # error suppressed (trailing)

# pyrefly: ignore[bad-assignment]
x: str = 1                       # only this specific kind suppressed

# pyrefly: ignore-errors          # at top of file: suppresses all errors in file
```

Pyrefly also honors **`# type: ignore`** (standard Python typing spec) — useful when
sharing code with mypy/pyright.

To honor other tools' ignore comments:
```toml
permissive-ignores = true
```

The `enabled-ignores` option (default `["type", "pyrefly"]`) controls which ignore
directive prefixes pyrefly respects. Valid values beyond the default are **not
enumerated in docs** — leave as default unless `permissive-ignores = true` alone
isn't enough, then experiment.

## Bulk add / remove

```bash
pyrefly suppress                                # add ignore comments for every current error
pyrefly suppress --comment-location=same-line   # trailing instead of line-above
pyrefly suppress --remove-unused                # remove ignores that no longer match an error
```

Run `--remove-unused` after every cleanup pass — pyrefly will flag stale ignores as
`unused-ignore`.

## Baseline files

Stores current errors in a JSON file. Errors that match an entry are suppressed.

```bash
# Create / refresh baseline
pyrefly check --baseline=pyrefly_baseline.json --update-baseline

# Subsequent runs only show errors not in the baseline
pyrefly check --baseline=pyrefly_baseline.json
```

Or set in config:
```toml
[tool.pyrefly]
baseline = "pyrefly_baseline.json"
```

**Matching key**: file location + error code + column number. If code shifts lines,
location is normalized.

**Limitations**:
- Baseline is project-level — cannot be overridden in `sub-config` sections.
- Baseline-suppressed errors **still appear in the IDE** (so devs see them during
  editing). This is intentional — CI is the gate, the IDE is informational.

## Which to use when

| Scenario | Use |
| --- | --- |
| Adopting pyrefly on existing codebase | Baseline (CI), maybe `pyrefly suppress` once for IDE silence |
| One-off legitimate exception (e.g. dynamic library, plugin system) | Inline `# pyrefly: ignore[<kind>]` with a comment explaining why |
| Whole vendored / generated file | `# pyrefly: ignore-errors` at top OR `ignore-errors-in-generated-code = true` if file has `@generated` |
| Whole subdirectory (e.g. tests) | `sub-config` with relaxed `[errors]`, OR add to `project-excludes` |
| Third-party module untyped | `replace-imports-with-any` or `ignore-missing-imports` in config |

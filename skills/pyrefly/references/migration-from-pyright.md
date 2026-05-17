# Migrating from pyright

## Step 1 — auto-migrate

```bash
pyrefly init path/to/project
```

Reads `pyrightconfig.json` or `[tool.pyright]` and produces a `pyrefly.toml`. Review
the generated config — see notable differences below.

## Step 2 — honor existing ignore comments

To keep `# pyright: ignore[...]` working:
```toml
permissive-ignores = true
enabled-ignores    = ["type", "pyrefly", "pyright"]
```

## Notable behavioral differences

### File listing
Pyright uses **paths**; pyrefly uses **globs**. Plain paths still work but you can
upgrade to `**/*.py` patterns.

### Platforms
Pyright supports `"Windows"`, `"Linux"`, `"Darwin"`, `"All"`. Pyrefly's
`python-platform` is a string corresponding to a Python `sys.platform` value;
docs explicitly confirm `"linux"` as the default. Pyright's `"All"` maps to
`"linux"`. Run `pyrefly init` and inspect the migrated value.

### Execution environments → sub-config
Pyright's `executionEnvironments` can override Python version, platform, and module
paths per directory. **Pyrefly's `sub-config` only overrides diagnostic settings** —
not version/platform/paths. This is a hard limitation; if you rely on per-directory
Python versions, you'll need separate pyrefly invocations.

### Stubs
- Pyright auto-imports from `__builtins__.pyi`.
- Pyrefly requires adding the stubs directory to `site-package-path` explicitly.

## Option mapping

| Pyright | Pyrefly |
| --- | --- |
| `include` | `project-includes` |
| `exclude` | `project-excludes` |
| `pythonVersion` | `python-version` |
| `pythonPlatform` | `python-platform` |
| `extraPaths` | `search-path` |
| `stubPath` | `site-package-path` (one entry) |
| `typeCheckingMode` | `preset` — not formally mapped in docs; pyrefly's presets are `off` / `basic` / `legacy` / `default` / `strict`. Pick the closest after `pyrefly init` |
| `useLibraryCodeForTypes` | (always on in pyrefly) |
| `executionEnvironments` | partially — only diagnostic overrides via `sub-config` |

## Error code mapping (full table from docs)

| Pyright diagnostic | Pyrefly kind |
| --- | --- |
| `reportAbstractUsage` | `bad-instantiation` |
| `reportArgumentType` | `bad-argument-type` |
| `reportAssertTypeFailure` | `assert-type` |
| `reportAssignmentType` | `bad-assignment` |
| `reportAttributeAccessIssue` | `missing-attribute` |
| `reportDeprecated` | `deprecated` |
| `reportIncompatibleMethodOverride` | `bad-override` |
| `reportIncompatibleVariableOverride` | `bad-override` |
| `reportInconsistentOverload` | `inconsistent-overload` |
| `reportIndexIssue` | `bad-index` |
| `reportInvalidTypeArguments` | `bad-specialization` |
| `reportInvalidTypeForm` | `invalid-annotation` |
| `reportInvalidTypeVarUse` | `invalid-type-var` |
| `reportMissingImports` | `missing-import` |
| `reportMissingModuleSource` | `missing-source` |
| `reportMissingParameterType` | `unannotated-parameter` |
| `reportMissingTypeStubs` | `untyped-import` |
| `reportNoOverloadImplementation` | `invalid-overload` |
| `reportOperatorIssue` | `unsupported-operation` |
| `reportPossiblyUnboundVariable` | `unbound-name` |
| `reportPrivateUsage` | `no-access` |
| `reportReturnType` | `bad-return` |
| `reportUnboundVariable` | `unbound-name` |
| `reportUndefinedVariable` | `unknown-name` |
| `reportUninitializedInstanceVariable` | `implicitly-defined-attribute` |
| `reportUnknownArgumentType` | `implicit-any` |
| `reportUnknownMemberType` | `implicit-any` |
| `reportUnknownParameterType` | `unannotated-parameter` |
| `reportUnknownVariableType` | `implicit-any` |
| `reportUnnecessaryCast` | `redundant-cast` |
| `reportUnusedCoroutine` | `unused-coroutine` |

## Suppression comment translation

```python
# Before (pyright):
x = something()  # pyright: ignore[reportAssignmentType]

# With permissive-ignores=true: works as-is.
# Or convert:
x = something()  # pyrefly: ignore[bad-assignment]
```

# Import Resolution

## Resolution order

For absolute imports:
1. **`search-path`** — project files (highest precedence)
2. **Typeshed** — bundled stdlib stubs
3. **Fallback search-path** — auto-detected
4. **`site-package-path`** — third-party packages (lowest precedence)
5. → `missing-import` error

For relative imports: resolved relative to the importing file's path.

## `search-path` vs `site-package-path`

| | `search-path` | `site-package-path` |
| --- | --- | --- |
| Represents | Project source | Third-party packages |
| Precedence | Highest | Lowest |
| Auto-populated from | CLI args, config, detected import root (`src/`, parent with `__init__.py`, or config directory) | Config + queried Python interpreter |
| Default | (auto-detected) | `./typings/` + interpreter site-packages |

## Stub file priority

For each package, pyrefly does **two passes**: stub packages first, then source.

1. `<pkg>-stubs` packages (e.g. `pandas-stubs`)
2. `.pyi` files inside the regular package
3. `.py` source files

## Bundled stubs decision tree

**Without a pyrefly config**:
- Package installed → use bundled (typeshed) stubs.
- Package not installed → `missing-source-for-stubs` error.

**With a pyrefly config**:
- User-installed stubs take precedence.
- Otherwise → `untyped-import` error if recommended stubs exist.

## Common pitfalls

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `missing-import` for an installed package | Wrong interpreter queried | Set `python-interpreter-path` or `conda-environment` |
| `missing-import` for in-project module | Project root not auto-detected | Add to `search-path` |
| Wrong package version's types | Stubs vs source mismatch | Add stub dir to `site-package-path`, or uninstall stale stubs |
| `untyped-import` | Recommended stubs not installed | `pip install <pkg>-stubs` or `replace-imports-with-any = ["<pkg>"]` |

## Debug command

```bash
pyrefly dump-config
```

Shows the resolved config (after heuristics) including which interpreter was
queried, the effective `search-path`, and the effective `site-package-path`. Use
this whenever an import isn't resolving as expected.

## Replace / ignore missing imports

```toml
# Always treat these modules as Any (even if installed)
replace-imports-with-any = ["legacy_internal.*", "vendor\\.untyped_lib"]

# Treat as Any only if not found
ignore-missing-imports = ["optional_dep\\..*"]
```

Both take **regex** patterns, not globs.

## Notes

- Namespace package handling is **not documented**; behavior is via typeshed/interpreter rules.
- Virtualenv detection happens via the queried Python interpreter — pyrefly does
  not have its own venv autodetection beyond `$VIRTUAL_ENV` / `which python3`.

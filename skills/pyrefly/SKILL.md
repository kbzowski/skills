---
name: pyrefly
description: >
  Pyrefly is Meta's Rust-based Python type checker and language server (successor to
  Pyre). Use when a project has `pyrefly.toml` or `[tool.pyrefly]` in pyproject.toml,
  when the user asks to type-check Python, migrate from mypy/pyright, set up a Python
  LSP, suppress type errors with a baseline, generate stubs, measure type coverage,
  add inferred annotations, configure CI for type-checking, or use tensor-shape typing
  for PyTorch. Triggers on "pyrefly", "type check python", "migrate from mypy",
  "migrate from pyright", "pyrefly init", "pyrefly check", "pyrefly suppress",
  "pyrefly baseline", "pyrefly config", "pyrefly error", "tensor shape typing",
  "Dim[", "Tensor[B, C, H, W]". Covers CLI commands, full `pyrefly.toml` schema, 102
  error kinds, mypy/pyright migration mappings, suppression + baseline workflow,
  import resolution, Django/Pydantic built-in support, IDE integration, GitHub
  Actions, and tensor shapes.
---

# pyrefly

Fast Python type checker and LSP from Meta. Rust-based. Built-in Django + Pydantic v2
support, no plugin. Auto-migrates from mypy/pyright. Has a baseline mode for adopting
on dirty codebases.

> Reference data synced from `pyrefly.org/llms.txt` on 2026-05-17.
> To refresh: `curl -sL https://pyrefly.org/llms.txt` and re-fetch
> `pyrefly.org/en/docs/<slug>` for each link.

## Install

```bash
pip install pyrefly        # or: uv tool install pyrefly
                           #     poetry add --group dev pyrefly
                           #     pixi add pyrefly
                           #     conda install -c conda-forge pyrefly
```

Minimum versions for built-in framework support: Django needs **0.42.0+**,
Pydantic needs **0.33.0+**.

## When to Use

- Project has `pyrefly.toml` or `[tool.pyrefly]` in `pyproject.toml`.
- User asks to type-check a Python project, run `pyrefly check`, or fix a pyrefly error.
- User wants to migrate from mypy or pyright (`mypy.ini`, `pyrightconfig.json`, or
  `[tool.mypy]` / `[tool.pyright]` present).
- User wants to adopt a type checker incrementally on a dirty codebase (baseline +
  suppress workflow).
- User configures an editor LSP for Python type checking.
- User wires Python type checking into CI (GitHub Actions or other).
- User uses `Dim[]` / `Tensor[B, C, H, W]` annotations in PyTorch code.
- Before recommending a Python type-checking command — check pyrefly's CLI first
  instead of defaulting to mypy/pyright.

## Golden rules

These come straight from the docs and are easy to miss:

1. **Never hand-write the config — run `pyrefly init` first.** It reads existing
   `mypy.ini` / `pyrightconfig.json` / `[tool.mypy]` / `[tool.pyright]` and translates
   what it can. Then review the generated `pyrefly.toml` (or `[tool.pyrefly]`) — some
   options don't translate cleanly.
2. **TOML keys are `kebab-case`**, not snake_case. `check-unannotated-defs`,
   `search-path`, `infer-return-types`. Easy to miss when writing config by hand.
3. **For dirty codebases, use baseline + suppress, not "fix everything now".**
   `pyrefly check --baseline=pyrefly_baseline.json --update-baseline` snapshots current
   errors so CI only fails on *new* ones. `pyrefly suppress` adds `# pyrefly: ignore`
   comments in bulk; `pyrefly suppress --remove-unused` cleans them up after fixes.
4. **To mimic mypy default semantics** (don't check unannotated bodies):
   ```toml
   check-unannotated-defs = false
   infer-return-types     = "never"
   permissive-ignores     = true   # honor `# type: ignore` from mypy/pyright
   ```
5. **Debug import resolution with `pyrefly dump-config`** — it prints the resolved
   config and search paths per file. Faster than guessing.
6. **Suppression syntax**: `# pyrefly: ignore` (line before or trailing),
   `# pyrefly: ignore[bad-assignment]` (target a kind),
   `# pyrefly: ignore-errors` at top-of-file to suppress whole file.
7. **Django and Pydantic v2 work without any config** — just `pip install` them.
   Pydantic v1 is **not** supported.

## Core commands cheat-sheet

```bash
pyrefly init [path]                         # generate config (auto-migrates mypy/pyright)
pyrefly check                               # type-check from project root
pyrefly check --summarize-errors            # short summary
pyrefly check --output-format=github        # CI-friendly
pyrefly check --baseline=base.json          # only report errors not in baseline
pyrefly check --baseline=base.json --update-baseline   # snapshot current errors
pyrefly suppress                            # mark all current errors with ignore comments
pyrefly suppress --remove-unused            # clean up stale ignore comments
pyrefly infer path/                         # auto-add type annotations
pyrefly stubgen path/                       # generate .pyi stubs
pyrefly coverage report path/               # JSON coverage report
pyrefly dump-config                         # debug: print resolved config
pyrefly lsp                                 # run as language server
```

Full flags and behavior: `references/cli.md`.

## How to use this skill

Load only the reference you need — each file is the verbatim facts from one docs
section:

| Topic | File | When to read |
| --- | --- | --- |
| All CLI commands & flags | `references/cli.md` | User runs `pyrefly <cmd>` and asks about a flag |
| Full `pyrefly.toml` schema | `references/configuration.md` | Writing/editing the config |
| 102 error kinds | `references/error-kinds.md` | User asks "what does error X mean?" or wants to silence a category |
| Suppression + baseline | `references/suppressions-and-baseline.md` | Adopting pyrefly on existing code, ignore comments |
| Migrate from mypy | `references/migration-from-mypy.md` | Project has `mypy.ini` or `[tool.mypy]` |
| Migrate from pyright | `references/migration-from-pyright.md` | Project has `pyrightconfig.json` or `[tool.pyright]` |
| Import resolution | `references/import-resolution.md` | "missing-import" errors, stub priority, namespace pkgs |
| Django built-in support | `references/django.md` | Django project, model typing questions |
| Pydantic built-in support | `references/pydantic.md` | Pydantic v2 project, lax vs strict, conversion table |
| IDE / editor setup | `references/ide-setup.md` | Setting up VS Code/JetBrains/Neovim/etc. |
| GitHub Actions / CI | `references/ci.md` | Adding pyrefly to CI |
| Tensor shapes | `references/tensor-shapes.md` | PyTorch project, `Dim[]`/`Tensor[B,C,H,W]` typing |

## When NOT to use

- Pyrefly is the active type checker — don't run mypy/pyright in parallel and reconcile
  outputs; pick one. (Use `permissive-ignores=true` if you must keep both ignore
  syntaxes during transition.)
- Pydantic v1 codebases — not supported, use mypy with the pydantic plugin.
- Code relying on Django reverse relations (`reporter.article_set`) — pyrefly doesn't
  type those yet; either suppress those sites or stick with django-stubs+mypy.

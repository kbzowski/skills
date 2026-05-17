# CI / GitHub Actions

## Official GitHub Action

```yaml
- uses: facebook/pyrefly@main
```

With options:
```yaml
- uses: facebook/pyrefly@main
  with:
    version:           "0.60.0"        # pin a version
    python-version:    "3.12"
    args:              "--summarize-errors"
    working-directory: "packages/api"  # run pyrefly from a subdirectory
```

## Manual setup (any CI)

```yaml
- run: pip install pyrefly
- run: pyrefly check --output-format=github
```

`--output-format=github` emits GitHub Actions annotations (`::error file=...` style)
so failures appear inline on the PR diff.

Other CIs: use `--output-format=json` and post-process, or default `full-text`.

## Pattern: baseline-gated CI

For codebases adopting pyrefly incrementally:

```yaml
- run: pip install pyrefly
- run: pyrefly check --baseline=pyrefly_baseline.json --output-format=github
```

Commit `pyrefly_baseline.json` to the repo. CI fails only on **new** errors.
Refresh the baseline locally with `--update-baseline` after fixing batches.

## Pre-commit hook example

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pyrefly
        name: pyrefly
        entry: pyrefly check
        language: system
        types:   [python]
        pass_filenames: false
```

Run on changed files only: omit `pass_filenames: false` (pyrefly accepts paths).

## Caching

Pyrefly is fast (Rust); explicit caching usually isn't needed in CI. If you must,
cache the Python venv / `~/.cache/uv` between runs.

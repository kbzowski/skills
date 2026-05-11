# Grit CLI usage

Installed via `npm install -g @getgrit/cli`. Verify with `grit --version`
(should print `grit 0.1.x` or later).

## The commands you'll actually use

| Command                       | Purpose                                                  |
| ----------------------------- | -------------------------------------------------------- |
| `grit apply <pattern>`        | Run a pattern. Pattern can be an inline string, a `.grit` file path, or the name of an installed pattern (`grit list`). |
| `grit apply <pattern> <path>` | Restrict scan to a path (file or directory).             |
| `grit list`                   | List stdlib + project patterns available by name.        |
| `grit init`                   | Create a `.grit/` config directory in the current repo (for saved patterns + config). Not required for ad-hoc search. |
| `grit check`                  | Run every enforced pattern in `.grit/grit.yaml` against the repo (CI-friendly). |
| `grit --help`                 | The flag/subcommand list is the authoritative source.    |

## `grit apply` — the only command this skill needs

```bash
grit apply <pattern> [paths...] [flags]
```

Useful flags:

| Flag              | Effect                                                          |
| ----------------- | --------------------------------------------------------------- |
| `--lang <name>`   | Force a target language. **Always pass this for inline patterns**, since there's no file extension to infer from. |
| `--dry-run`       | Show matches without modifying files (default for search; relevant when rewriting). |
| `--json`          | Machine-readable output. Useful when piping into Claude or other tooling. |
| `--limit <N>`     | Cap the number of results.                                      |
| `--output <fmt>`  | Output format (`standard`, `compact`, `json`).                  |

### Inline patterns

```bash
# bash / zsh — single-quote the whole arg so backticks survive
grit apply '`console.log($msg)`' --lang js

# Restrict to a directory
grit apply '`useState($init)`' src/ --lang tsx

# JSON output for programmatic consumption
grit apply '`fetch($url)`' --lang ts --json
```

**Windows / PowerShell note:** PowerShell uses backticks as the line-continuation
character, which mangles inline patterns. Either:

1. Use a `.grit` file (recommended), or
2. Switch to `cmd.exe` or Git Bash for inline patterns, or
3. Escape carefully — usually not worth it.

### `.grit` file patterns

Always start with the engine + language header:

```grit
engine marzano(0.1)
language js

`console.log($msg)` where {
  $msg <: within `try { $_ } catch($_) { $_ }`
}
```

Run with `grit apply ./find-logs.grit`. Language is taken from the file's
`language` directive, so `--lang` isn't needed.

## `.grit/` repo config (optional)

`grit init` creates:

```
.grit/
  grit.yaml          # pattern enforcement config
  patterns/          # your project's saved patterns
```

`grit.yaml` lets you mark patterns as enforced (run by `grit check` in CI) or
suggested. For ad-hoc search from Claude Code, you don't need this — just use
`grit apply` directly.

## Telemetry

Grit phones home by default. To disable:

```bash
# Bash / zsh
export GRIT_TELEMETRY_DISABLED=true

# PowerShell
$env:GRIT_TELEMETRY_DISABLED = "true"
```

## Exit codes

`grit apply` exits non-zero when matches are found, which makes it shell-friendly
for "fail CI if pattern X exists" checks. For Claude Code search, ignore the exit
code and read stdout.

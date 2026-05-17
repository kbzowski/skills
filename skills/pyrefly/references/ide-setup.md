# IDE / Editor Setup

Pyrefly runs as an LSP via `pyrefly lsp`. Most editors below auto-invoke this.

## VS Code

Extension: **`meta.pyrefly`** ([marketplace](https://marketplace.visualstudio.com/items?itemName=meta.pyrefly), also on Open VSX).

Activates automatically on Python files.

Key settings:
| Setting | Type | Default |
| --- | --- | --- |
| `python.pyrefly.typeCheckingMode` | `"auto"` / `"off"` / `"basic"` / `"legacy"` / `"default"` / `"strict"` | `"auto"` |
| `python.pyrefly.disableTypeErrors` | bool | `false` |
| `python.pyrefly.diagnosticMode` | `"openFilesOnly"` / `"workspace"` | `"openFilesOnly"` |
| `editor.inlayHints.enabled` | bool | (enable for inlay hints) |

Code-actions-on-save: `source.fixAll.pyrefly`.

## JetBrains / PyCharm

**Settings → Python → Tools → Pyrefly** → **Enable**. Choose execution mode:
- **Interpreter** — searches interpreter installations.
- **Path** — searches `$PATH`.

## Neovim 0.11+

With Mason:
```lua
require("mason").setup()
require("mason-lspconfig").setup({ ensure_installed = { "pyrefly" } })
vim.lsp.enable({ "pyrefly" })
```

Or `:MasonInstall pyrefly`, then `vim.lsp.enable({"pyrefly"})`.

System-installed alternative: ensure `pyrefly` on `$PATH`, configure via `lspconfig`.

## Vim/Neovim + coc.nvim

`coc-settings.json`:
```json
"languageserver": {
  "pyrefly": {
    "command": "pyrefly",
    "args": ["lsp"],
    "filetypes": ["python"],
    "rootPatterns": ["pyrefly.toml", "pyproject.toml", ".git"]
  }
}
```

## Vim + ALE

```vim
let g:ale_linters = { 'python': ['pyrefly'] }
```

## Emacs (eglot)

```elisp
(add-to-list 'eglot-server-programs
  `((python-ts-mode python-mode) . ("pyrefly" "lsp")))
```

With `use-package`:
```elisp
(use-package eglot
  :ensure t
  :hook ((python-mode python-ts-mode) . eglot-ensure)
  :config
  (add-to-list 'eglot-server-programs
    `((python-ts-mode python-mode) . ("pyrefly" "lsp"))))
```

## Helix

`languages.toml`:
```toml
[language-server.pyrefly]
command = "pyrefly"
args    = ["lsp"]

[[language]]
name             = "python"
language-servers = ["pyrefly"]
```

## Other editors

| Editor | How |
| --- | --- |
| Cursor, Windsurf, Antigravity, Kiro | Search "Pyrefly" on OpenVSX |
| Sublime Text | LSP package — see [LSP docs](https://lsp.sublimetext.io/language_servers/#pyrefly) |
| Zed | Install from [extensions marketplace](https://zed.dev/extensions/pyrefly) |
| Positron | Built-in |
| Jupyter Lab | Via [jupyterlab-lsp](https://jupyterlab-lsp.readthedocs.io/) |
| Marimo | See Marimo LSP docs |

## Supported LSP features

All standard LSP 3.17 navigation/edit features:

**Navigation**: go-to-definition, go-to-type-definition, go-to-declaration,
go-to-implementation, find-references, call hierarchy, type hierarchy.

**Code understanding**: hover (type + docstring), document symbols, workspace
symbols, semantic tokens, inlay hints (types, params, returns).

**Editing**: completion (project-aware imports), signature help, document
highlights, rename, move/rename file with auto-update.

**Code actions**: add missing import, remove redundant cast.

**Refactoring**: pull/push members between classes, convert package ↔ module,
extract variable/field, inline variable, invert boolean, introduce parameter,
move nested function to top level.

**Other**: diagnostics, code actions on save (`source.fixAll.pyrefly`),
Jupyter/Marimo notebook support (experimental).

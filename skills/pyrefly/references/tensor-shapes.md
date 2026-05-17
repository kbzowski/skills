# Tensor Shapes (Experimental)

Static shape-checking for PyTorch tensors. Enable with `tensor-shapes = true` in
config. Niche — most users don't need this.

## Enabling

```toml
[tool.pyrefly]
tensor-shapes = true
search-path   = ["path/to/fixtures"]   # copy from pyrefly source: test/tensor_shapes/fixtures/
```

Recommended imports:
```python
from __future__ import annotations
import torch
import torch.nn as nn
from torch import Tensor
from torch_shapes import Dim
```

## Core types

| Type | Meaning |
| --- | --- |
| `Dim[X]` | Integer whose type-level identity is `X` (literal `5` or TypeVar `N`). Subtype of `int`. |
| `Tensor[D1, D2, ...]` | Tensor with shape `(D1, D2, ...)`. Each `Di` is a `Dim` literal, TypeVar, or arithmetic expression. |
| `Tensor[*Bs, D]` | Variadic leading dims (`TypeVarTuple`). |
| `Tensor` | Shape unknown. |

## Arithmetic on `Dim`

Both operands must be `Dim` (not `int * Dim`):

| Op | Result |
| --- | --- |
| `a + b` | `Dim[A + B]` |
| `a - b` | `Dim[A - B]` |
| `a * b` | `Dim[A * B]` |
| `a // b` | `Dim[A // B]` |
| `a ** b` | `Dim[A ** B]` |

Auto-simplification: `2 * C // 2` → `C`. **Not** simplified: `N * (X // N)` ≠ `X`
— common in multi-head reshape; use `# type: ignore` or `# pyrefly: ignore`.

## Minimal example

```python
from __future__ import annotations
import torch.nn as nn
from torch import Tensor
from torch_shapes import Dim

class TwoLayerNet[InDim, HidDim, OutDim](nn.Module):
    def __init__(self, in_dim: Dim[InDim], hid_dim: Dim[HidDim], out_dim: Dim[OutDim]):
        super().__init__()
        self.fc1 = nn.Linear(in_dim, hid_dim)
        self.fc2 = nn.Linear(hid_dim, out_dim)

    def forward[B](self, x: Tensor[B, InDim]) -> Tensor[B, OutDim]:
        return self.fc2(torch.relu(self.fc1(x)))
```

## Debugging idioms

- `reveal_type(x)` — pyrefly prints inferred type in diagnostics.
- `assert_type(x, Tensor[B, 512])` — type-checked assertion; **crashes at runtime
  if executed**, remove after porting.

## Shape access

- `x.shape` → `tuple[Dim[B], Dim[C], Dim[H], Dim[W]]`
- `x.size(0)` → `Dim[B]`
- `x.size()` → full shape tuple

## Common patterns and gotchas

| Pattern | Approach |
| --- | --- |
| Shape-preserving loop (`for layer in ModuleList`) | `n_layers: int` (count, not Dim); `assert_type` inside loop body |
| First iteration changes shape | Run it outside the loop, then loop from index 1 |
| Multi-head reshape `NHead * (D // NHead)` | `# pyrefly: ignore` — simplification gap |
| `nn.Sequential(*list_var)` erases shapes | Extract shape-changing layers as attributes, chain in `forward` |
| Hyperparameters used as Dim arithmetic | `nc: Final = 3` on the class → resolves to `Literal[3]` |
| Encoder-decoder / U-Net | Express via generic class methods returning `Tensor[B, 2*C, (H-2)//2 + 1, ...]` |
| Recursive depth with exponential shapes | `@overload` pair: base case `Dim[1]`, recursive case `Dim[I]` |
| List indexing erases concrete `Dim` | Narrow with explicit annotation: `down: Down[C, 2*C] = self.downs[idx]` |

## Agent skill: `/port-model`

When porting an existing PyTorch model to tensor-shape types, pyrefly ships a
companion agent skill. Invocation in Claude Code:

```
/port-model path/to/model.py
```

or "Port this model to use tensor shape types: path/to/model.py".

Prerequisite: project has the fixture stubs.

Workflow: audits ops against fixtures and DSL registry → inventories
classes/methods → ports each module in dependency order (types constructor, probes
forward with `reveal_type`, writes forward with `assert_type`) → runs
`verify_port.sh` for a completion report (`ig` = ignore count, `sh` = shaped
asserts, `ba` = bare asserts).

## More docs

Tutorials (Read on-demand only if user is actively porting a model):
- https://pyrefly.org/en/docs/tensor-shapes — overview
- https://pyrefly.org/en/docs/tensor-shapes-setup — setup
- https://pyrefly.org/en/docs/tensor-shapes-reference — Dim/Tensor API
- https://pyrefly.org/en/docs/tensor-shapes-tutorial-basics — MLP
- https://pyrefly.org/en/docs/tensor-shapes-tutorial-loops — Transformer, ModuleList
- https://pyrefly.org/en/docs/tensor-shapes-tutorial-architectures — U-Net, generators
- https://pyrefly.org/en/docs/tensor-shapes-tutorial-advanced — configs, dynamic patterns
- https://pyrefly.org/en/docs/tensor-shapes-contributing — fixtures + DSL contributions

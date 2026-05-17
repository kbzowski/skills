# Pydantic Support

**Built-in. No plugin or config flag needed.** Requires pyrefly **0.33.0+** and
**Pydantic v2 or later**. Pydantic v1 is **not** supported.

## What's recognized

- `BaseModel`, `Field`, `ConfigDict`, model-level config options
- `pydantic_settings.BaseSettings`
- `@pydantic.dataclasses.dataclass`
- Frozen models (`model_config = ConfigDict(frozen=True)`)
- Strict fields (`Field(strict=True)`)
- `extra="forbid"` / `extra="allow"`
- Field constraints (`gt`, `lt`, `ge`, `le`, `min_length`, …)
- `RootModel[T]`
- Aliases: `Field(alias=...)`, `validate_by_name`, `validate_by_alias`

## Lax vs Strict mode

**Lax mode is the default** and mirrors Pydantic's runtime coercion. An `int` field
accepts a wider union (named `LaxInt = int | bool | float | str | bytes | Decimal`).

```python
class Model(BaseModel):
    x: int = 0

Model(x=1)              # OK
Model(x=True)           # OK (lax)
Model(x=1.0)            # OK (lax)
Model(x='123')          # OK (lax)
Model(x=b'123')         # OK (lax)
Model(x=Decimal('123')) # OK (lax)
```

**Strict mode** — set per-field via `Field(strict=True)` or per-model via
`model_config = ConfigDict(strict=True)`:

```python
class User(BaseModel):
    name: str
    age:  int = Field(strict=True)

User(name="Alice", age="30")   # ERROR: age expects int, not str
```

## Lax conversion table (atomic)

| Field type | Accepted union (`Lax<T>`) |
| --- | --- |
| `int` | `int \| bool \| float \| str \| bytes \| Decimal` |
| `float` | `int \| bool \| float \| str \| bytes \| Decimal` |
| `bool` | `bool \| int \| float \| str \| Decimal` |
| `Decimal` | `Decimal \| int \| float \| str` |
| `str` | `str \| bytes \| bytearray` |
| `bytes` | `str \| bytes \| bytearray` |
| `date` | `date \| datetime \| int \| float \| str \| bytes \| Decimal` |
| `datetime` | `date \| datetime \| int \| float \| str \| bytes \| Decimal` |
| `time` | `time \| int \| float \| str \| bytes \| Decimal` |
| `timedelta` | `timedelta \| int \| float \| str \| bytes \| Decimal` |
| `Path` | `Path \| str` |
| `UUID` | `UUID \| str` |
| `None` | `None` (no conversion) |

## Lax conversion (compositional)

| Field type | Accepted |
| --- | --- |
| `type[T]` | `type[T_converted]` |
| `T1 \| T2 \| ...` | union of converted parts |
| `list[T]`, `set[T]`, `frozenset[T]`, `Sequence[T]`, `Iterable[T]`, `deque[T]`, `tuple[T, ...]` | `Iterable[T_converted]` |
| `tuple[T1, T2, ...]` | `Iterable[T1_flat \| T2_flat \| ...]` |
| `dict[K, V]` | `Mapping[K, V_converted]` |

## Patterns

### Frozen model
```python
class Model(BaseModel):
    model_config = ConfigDict(frozen=True)
    x: int = 42

m = Model()
m.x = 10                        # ERROR: Cannot set field; model is frozen
```

### Forbid extras
```python
class ModelForbid(BaseModel, extra="forbid"):
    x: int

ModelForbid(x=1, y=2)           # ERROR: unexpected field `y`
```

### Field constraints
```python
class M(BaseModel):
    x: int = Field(gt=0, lt=10)

M(x=0)                          # ERROR: violates gt
M(x=15)                         # ERROR: violates lt
```

### Root models
```python
class IntRootModel(RootModel[int]):       pass
class StrictIntRootModel(RootModel[StrictInt]): pass

IntRootModel(123)               # OK
IntRootModel("123")             # OK (lax)
StrictIntRootModel("123")       # ERROR
```

### Aliases
```python
class M(BaseModel, validate_by_name=True, validate_by_alias=True):
    x: int = Field(alias='y')

M(x=0)    # OK
M(y=0)    # OK
```

## Limitations

- **`alias_generator` (e.g. `alias_generator=to_camel`) is NOT recognized.**
  Constructing with the generated alias (`firstName` instead of `first_name`) raises
  `missing-argument`. Workaround: explicit `Field(alias=...)` per field, or
  `# pyrefly: ignore[missing-argument]` at construction sites.

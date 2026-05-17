# Pyrefly Error Kinds (102)

Used in suppressions (`# pyrefly: ignore[<kind>]`) and in `[errors]` config table.
All names are kebab-case.

## Calls and arguments

| Kind | Meaning |
| --- | --- |
| `bad-argument-count` | Wrong number of arguments |
| `bad-argument-type` | Argument of wrong type |
| `bad-keyword-argument` | Keyword arg given multiple values |
| `missing-argument` | Required argument not provided |
| `unexpected-keyword` | Extra keyword argument |
| `unexpected-positional-argument` | Positional passed for keyword-only |
| `not-callable` | Non-callable used as function |
| `no-matching-overload` | Overload set has no match |
| `unused-coroutine` | Async result not awaited |

## Assignment, attributes, names

| Kind | Meaning |
| --- | --- |
| `bad-assignment` | Value conflicts with annotation / `Final` constraint |
| `annotation-mismatch` | Multiple conflicting annotations for one variable |
| `redefinition` | Re-annotation with different type |
| `missing-attribute` | Attribute does not exist |
| `no-access` | Attribute exists but cannot be used this way |
| `read-only` | Trying to modify read-only attribute |
| `implicitly-defined-attribute` | Attribute assigned outside `__init__` |
| `unknown-name` | Name not in scope |
| `unbound-name` | Conditionally defined name, possibly undefined |

## Imports

| Kind | Meaning |
| --- | --- |
| `missing-import` | Module not found |
| `missing-module-attribute` | Name doesn't exist in module |
| `missing-source` | Stubs found but no source |
| `missing-source-for-stubs` | Bundled stubs without source |
| `implicit-import` | Submodule accessed through parent without import |
| `untyped-import` | Library used without recommended stubs |

## Returns, raises, yields, control flow

| Kind | Meaning |
| --- | --- |
| `bad-return` | Return value doesn't match annotation |
| `bad-raise` | Invalid exception/cause in `raise` |
| `invalid-yield` | `yield` in disallowed context |
| `unreachable` | Code after exit point |
| `not-iterable` | Non-iterable used in `for` etc. |
| `not-async` | `await` on non-awaitable |
| `bad-context-manager` | Non-context-manager in `with` |
| `bad-unpacking` | Wrong number of unpack targets |
| `open-unpacking` | TypedDict unpacked with incompatible items |
| `bad-index` | Container indexed with wrong type |
| `division-by-zero` | Literal zero in `/`, `//`, `%` |

## Classes and inheritance

| Kind | Meaning |
| --- | --- |
| `bad-class-definition` | Class definition problem |
| `bad-instantiation` | Instantiating non-instantiable (e.g. Protocol) |
| `inconsistent-inheritance` | Conflicting inherited fields |
| `invalid-inheritance` | Bad inheritance structure |
| `implicit-abstract-class` | Subclass has unimplemented abstract methods |
| `abstract-method-call` | Calling `@abstractmethod` |
| `invalid-super-call` | Bad `super()` call |
| `bad-override` | LSP violation |
| `bad-override-mutable-attribute` | Mutable override with incompatible type |
| `bad-override-param-name` | Override renames parameters |
| `missing-override-decorator` | Should have `@override` |

## Generics, TypeVars, variance

| Kind | Meaning |
| --- | --- |
| `bad-specialization` | Generic specialized incorrectly |
| `invalid-type-var` | Bad TypeVar definition or use |
| `invalid-type-var-tuple` | Bad TypeVarTuple |
| `invalid-param-spec` | Bad ParamSpec |
| `invalid-variance` | TypeVar used against declared variance |
| `variance-mismatch` | Inferred variance differs from declaration |
| `incompatible-overload-residual` | Overload type incompatible with TypeVar |

## Overloads

| Kind | Meaning |
| --- | --- |
| `invalid-overload` | `@overload` missing impl or signatures |
| `inconsistent-overload` | Overload signature inconsistent with impl |
| `inconsistent-overload-default` | Default value type inconsistent in overload |
| `incompatible-overload-residual` | (see Generics) |

## TypedDict

| Kind | Meaning |
| --- | --- |
| `bad-typed-dict` | Unsupported keyword in TypedDict |
| `bad-typed-dict-key` | Wrong key used |
| `not-required-key-access` | NotRequired key accessed without check |

## Match statements

| Kind | Meaning |
| --- | --- |
| `bad-match` | Issue with `match` or `__match_args__` |
| `non-exhaustive-match` | Enum match missing case |
| `unreachable-match-case` | Case pattern can never match |
| `invalid-pattern` | Runtime-invalid pattern |

## Typing-system misuse

| Kind | Meaning |
| --- | --- |
| `invalid-annotation` | Misuse of typing special form |
| `invalid-argument` | Bad arg to typing function |
| `invalid-decorator` | Decorator misused |
| `invalid-literal` | `Literal` with bad parameter |
| `invalid-type-alias` | Illegal alias value |
| `invalid-self-type` | `Self` in unsupported context |
| `invalid-syntax` | Syntactic edge case |
| `not-a-type` | Non-type where type expected |
| `name-mismatch` | Variable name ≠ functional-form first arg |
| `bad-function-definition` | Function definition issue |
| `bad-dunder-all` | `__all__` entry missing |
| `unresolvable-dunder-all` | `__all__` not statically analyzable |
| `unimported-directive` | Typing directive used without import |

## Protocols

| Kind | Meaning |
| --- | --- |
| `protocol-implicitly-defined-attribute` | Protocol attr assigned in method, not class |
| `unsafe-overlap` | Runtime-checkable Protocol with incompatible attrs |
| `unannotated-protocol-member` | Protocol member without annotation |

## Implicit `Any` and missing annotations

| Kind | Meaning |
| --- | --- |
| `implicit-any` | Umbrella for inferred `Any` |
| `implicit-any-attribute` | Attribute inferred as `Any \| None` |
| `implicit-any-empty-container` | `[]`/`{}`/`set()` pinned to `Any` container |
| `implicit-any-parameter` | Parameter unannotated → `Any` |
| `implicit-any-type-argument` | Generic used without args → `Any` |
| `unannotated-attribute` | (deprecated → `implicit-any-attribute`) |
| `unannotated-parameter` | (deprecated → `implicit-any-parameter`) |
| `unannotated-return` | Missing return annotation |

## Redundancy / style

| Kind | Meaning |
| --- | --- |
| `redundant-cast` | `cast()` to already-compatible type |
| `redundant-condition` | Condition is statically True/False |
| `unnecessary-comparison` | Identity compare with known result |
| `unnecessary-type-conversion` | `int(x)` when `x` already int, etc. |
| `unused-ignore` | Ignore comment doesn't suppress anything |

## Deprecation / runtime

| Kind | Meaning |
| --- | --- |
| `deprecated` | Use of deprecated class/function |
| `unsupported` | Typing feature not supported |
| `unsupported-delete` | `del` on undeletable |
| `unsupported-operation` | Op between incompatible types |
| `bad-param-name-override` | (deprecated → `bad-override-param-name`) |

## Tooling output

| Kind | Meaning |
| --- | --- |
| `assert-type` | `typing.assert_type()` call failed |
| `reveal-type` | Output of `reveal_type()` |

## Internals

| Kind | Meaning |
| --- | --- |
| `parse-error` | Parsing failed |
| `internal-error` | Internal pyrefly error |
| `non-convergent-recursion` | Inference didn't converge |

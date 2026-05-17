# Django Support

**Built-in. No plugin or config flag needed.** Requires pyrefly **0.42.0+** and
`django-stubs` installed:

```bash
pip install django-stubs pyrefly
```

## What's typed

- Model classes (`models.Model` subclasses)
- Field types (`CharField`, `IntegerField`, `ForeignKey`, `UUIDField`, …)
- Auto fields `id`, `pk` (correctly typed even when custom PK is used)
- `ForeignKey` forward access AND the `<name>_id` shadow field
- Nullable FKs → `T | None`
- `ManyToManyField` → `ManyRelatedManager[T, Model]`
- Choice enums (`Choices` / `IntegerChoices` / `TextChoices`)
- Auto-generated `get_<field>_display()` for choice fields
- Class-based generic views and their mixins
- `factory_boy` (`DjangoModelFactory.create()`, `.create_batch()`)

## Examples

```python
class Reporter(models.Model):
    full_name = models.CharField(max_length=70)

reporter = Reporter()
assert_type(reporter.id, int)                 # auto PK typed
```

```python
class Reporter(models.Model):
    uuid = models.UUIDField(primary_key=True)

r = Reporter()
assert_type(r.uuid, UUID)
assert_type(r.pk, UUID)                       # pk matches custom PK
```

```python
class Article(models.Model):
    reporter = models.ForeignKey(Reporter, on_delete=models.CASCADE)

a = Article()
assert_type(a.reporter, Reporter)
assert_type(a.reporter_id, int)               # shadow FK field
assert_type(a.reporter.full_name, str)        # chained access
```

```python
class Article(models.Model):
    reporter = models.ForeignKey(Reporter, null=True, on_delete=models.CASCADE)

a = Article()
assert_type(a.reporter, Reporter | None)      # null=True → optional
```

```python
class Book(models.Model):
    authors = models.ManyToManyField(Author)

b = Book()
assert_type(b.authors, ManyRelatedManager[Author, models.Model])
assert_type(b.authors.all(), QuerySet[Author, Author])
```

```python
class Vehicle(models.IntegerChoices):
    CAR   = 1, "Car"
    TRUCK = 2, "Truck"

assert_type(Vehicle.CAR.value, int)
assert_type(Vehicle.CAR.label, str)
```

```python
# factory_boy
class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

user  = UserFactory.create()                  # → User
users = UserFactory.create_batch(3)           # → list[User]
```

## Known limitations

- **Reverse relations are not typed**: `reporter.article_set` won't be inferred.
- **Advanced QuerySet operations beyond `.all()`** are limited.
- **M2M type representation differs from mypy**: pyrefly uses
  `ManyRelatedManager[Author, Model]` for *all* M2M fields targeting the same model,
  whereas django-stubs+mypy creates a distinct synthetic type per field. Some
  assignments mypy rejects, pyrefly will accept.
- Full ORM coverage is a work-in-progress.

## Workarounds for unsupported patterns

```python
# Reverse relation:
reporter.article_set  # pyrefly: ignore[missing-attribute]

# Or per-test sub-config:
# [[tool.pyrefly.sub-config]]
# matches = ["**/tests/**/*.py"]
# [tool.pyrefly.sub-config.errors]
# missing-attribute = false
```

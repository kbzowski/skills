# Iteration Report Template

Use this template for the report at the end of each refactoring iteration.

```markdown
# Iteracja N: [Tytul]

## Data
[YYYY-MM-DD]

## Kontekst
[1-2 zdania: co bylo celem tej iteracji]

## Wykonane zmiany

### Zmiana 1: [nazwa]
- **Problem:** [co bylo zle]
- **Rozwiazanie:** [co zrobiono]
- **Pliki:** [nowe], [zmodyfikowane]

### Zmiana 2: [nazwa]
...

## Podsumowanie

| Metryka | Przed | Po |
|---------|-------|----|
| [np. configure.tsx] | [linie] | [linie] |
| Nowe pliki | 0 | N |
| [duplikacje, inne metryki] | ... | ... |

## Weryfikacja
- [ ] `pnpm build` - OK/FAIL
- [ ] `pnpm check` - OK/FAIL
- [ ] E2E testy - [lista uruchomionych, wyniki]

## Odlozone na nastepne iteracje
- [co nie weszlo i dlaczego]

## Uwagi
- [wnioski, wzorce do nasledowania, ryzyka]
```

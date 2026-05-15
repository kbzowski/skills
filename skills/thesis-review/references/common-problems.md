# Problemy recenzji WIMIIP (z department meeting)

Prezentacja wydziałowa 2025 zidentyfikowała powtarzające się problemy. Czwarty problem z prezentacji — *niewłaściwe sformułowanie tytułu* — jest adresowany na etapie zatwierdzania tematu, a nie oceny pracy, i **nie wchodzi do skilla recenzyjnego**. Pozostałe trzy problemy skill adresuje explicite.

## 1. Niedostosowanie celu i zakresu pracy do poziomu studiów

**Diagnoza:** Prace mgr często nie spełniają wymogów mgr (brak elementu twórczego, płytka analiza, brak samodzielnego wnioskowania) — i dostają 5,0 "za poprawne wykonanie".

**Jak skill to wykrywa:**
- Sprawdza obecność co najmniej jednej z trzech cech poszerzających (patrz `inz-vs-mgr.md`).
- Liczy sygnały "mgr w przebraniu inż" (jedno rozwiązanie, jedna metoda, jeden zbiór, brak state of the art).

**Jak skill to egzekwuje:**
- Twarda reguła w rubryce: mgr bez cechy poszerzającej = max 4,0.
- Odrębna sekcja 1.5 recenzji wymaga wskazania elementu poszerzającego *ze stroną*. Brak wskazania = brak uzasadnienia 5,0.

## 2. Halucynacje AI

**Diagnoza:** Studenci używają LLM i nie weryfikują wygenerowanych cytowań — w pracach pojawiają się zmyślone DOI, tytuły, autorzy. Także generowane wykresy bez interpretacji.

**Jak skill to wykrywa:**
- Subagent `literature-verifier` sprawdza każde DOI, tytuł/autor, datę publikacji, strony.
- Subagent `ai-pattern-detector` szuka wzorców stylu AI w tekście oraz wizualnie weryfikuje każdy rysunek/wykres (brak interpretacji, rozjazd liczb, brak etykiet osi, stockowe diagramy).

**Jak skill to egzekwuje:**
- Wykryte halucynacje bibliograficzne → cap 3,0 (pojedyncze) / 2,0 (masowe).
- W recenzji sekcja 1.4 wymienia konkretne problemowe pozycje.
- W sekcji 3.3 opisany jest wynik detektora AI skonfrontowany z deklaracją w rozdziale GenAI.

## 3. Pobieżne recenzje

**Diagnoza:** Recenzenci piszą 3-5 zdań ogólników i stawiają 5,0. Dane WIMIIP 24/25: 1574 recenzji, średnia 4,3-4,5 — stanowczo za wysoka.

**Jak skill to adresuje:**
- Szablon `template-recenzja.md` wymaga 12+ sekcji merytorycznych, każda z konkretnym fragmentem i wskazaniem strony.
- Rubryka `grading-rubric.md` wymaga uzasadnienia każdej oceny, wymienia defekty.
- Krok 7 workflow — konfrontacja: jeśli recenzent proponuje 5,0, a skill widzi defekty, skill proponuje niższą ocenę z konkretnym uzasadnieniem.
- Ocena wyjściowa 4,5 (nie 5,0) — 5,0 wymaga *pozytywnego uzasadnienia wybitności*, nie tylko braku defektów.

---

## Jak raport z tych trzech problemów wchodzi do recenzji

Skill **nie tworzy osobnej sekcji "problemy"** — rozkłada wnioski na właściwe sekcje szablonu. Ale w uzasadnieniu oceny końcowej (sekcja 5) wymienia, które z problemów zidentyfikował i jak wpłynęły na ocenę.

Przykład fragmentu uzasadnienia:

> Ocena 4,0 wynika z dwóch czynników: (1) praca mgr bez wyraźnego elementu poszerzającego zakres — analizowano jeden algorytm na jednym zbiorze danych (s. 28-45), brak porównań; (2) w bibliografii stwierdzono dwie pozycje z DOI niemożliwymi do zweryfikowania ([14] i [22]).

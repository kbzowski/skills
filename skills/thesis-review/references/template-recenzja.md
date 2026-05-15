# Szablon recenzji (recenzent, APD)

Struktura odpowiada polom APD. Wszystkie sekcje są wymagane. Każda ocena cząstkowa musi mieć uzasadnienie ze wskazaniem strony.

```markdown
# Recenzja pracy dyplomowej

**Autor:** [imię nazwisko]
**Tytuł:** [tytuł pracy]
**Opiekun:** [tytuł imię nazwisko]
**Recenzent:** [tytuł imię nazwisko]
**Stopień studiów:** [inżynierska / magisterska]
**Kierunek:** Informatyka Techniczna, WIMIIP AGH

## 1. Ocena merytoryczna

### 1.1 Zgodność treści pracy z tematem
[2-4 zdania. Czy treść pracy realizuje zatwierdzony temat? Jeśli są rozbieżności — wskaż, które rozdziały wykraczają poza temat lub których brakuje względem tytułu. Nie oceniaj jakości samego sformułowania tytułu — został on zatwierdzony na etapie zgłoszenia tematu; oceniaj tylko to, czy praca go wypełnia.]

### 1.2 Stopień realizacji celu pracy i przyjętych założeń
[Przytocz cel ze wstępu. Odnieś się do niego: czy został zrealizowany w całości, częściowo, pozornie? Wskaż konkretne wyniki lub ich brak. 3-5 zdań.]

### 1.3 Trafność doboru metod badawczych i zastosowanych technologii
[Oceń wybór: czy uzasadniony? Czy są alternatywy, których nie rozważono? Czy metoda była adekwatna do problemu? 2-4 zdania.]

### 1.4 Zakres, aktualność i adekwatność wykorzystanej literatury
[Liczba pozycji, proporcja artykułów naukowych vs dokumentacji, aktualność. Jeśli agent literaturowy wykrył halucynacje — zaznacz konkretnie: "Pozycja [X] z bibliografii nie istnieje (zweryfikowano DOI)." 2-4 zdania.]

### 1.5 Nowatorstwo rozwiązania problemu inżynierskiego oraz praktyczna wartość wyników
[**Dla inż:** oceń praktyczną wartość wyniku inżynierskiego. Nie wymaga się innowacji.
**Dla mgr:** wskaż element poszerzający zakres (innowacja / pogłębiona analiza / szerszy kontekst) z konkretną stroną. Jeśli go nie ma — napisz to wprost. 3-5 zdań.]

### 1.6 Spójność i poprawność wnioskowania
[Czy wnioski wynikają z przedstawionych danych? Czy autor wyciąga je samodzielnie, czy powtarza za literaturą? Czy nie ma przeskoków logicznych? 2-3 zdania.]

### 1.7 Krytyczna analiza wyników i kierunki dalszych badań
[**Dla mgr — obowiązkowe.** Czy autor krytycznie analizuje własne wyniki (ograniczenia, warunki brzegowe, błędy metodyczne) i wskazuje uzasadnione kierunki dalszych prac? Przepisanie „w przyszłości można rozszerzyć o…" bez uzasadnienia = brak analizy.
**Dla inż — opcjonalnie**, ale obecność to atut. 2-3 zdania.]

## 2. Struktura i układ pracy

### 2.1 Kompletność i ciągłość logiczna struktury
[Dwa aspekty łącznie:
**Kompletność** — wymień brakujące sekcje spośród: wstęp, część analityczna, syntetyczna, weryfikacyjna, zakończenie, **rozdział "Wykorzystanie narzędzi GenAI"**, bibliografia. Brak rozdziału GenAI zaznacz wyraźnie.
**Ciągłość logiczna** — czy proporcje między częścią analityczną, syntetyczną a weryfikacyjną są właściwe? Czy tytuły rozdziałów odpowiadają treści? 2-4 zdania łącznie.]

### 2.2 Przejrzystość i poprawność redakcyjna przypisów i odsyłaczy
[Czy cytowania są poprawne i konsekwentne? Czy wszystkie rysunki/tabele mają odnośniki w tekście? 1-2 zdania.]

## 3. Język i styl

### 3.1 Poprawność językowa, stylistyczna i gramatyczna
[Konkretnie: czy są błędy, kolokwializmy, styl potoczny, niezrozumiałe konstrukcje? Podaj 1-2 przykłady ze stroną. 2-3 zdania.]

### 3.2 Właściwa terminologia i jasność wywodu
[Czy terminy branżowe są używane poprawnie i konsekwentnie? Czy są niejasne fragmenty? 1-2 zdania.]

### 3.3 Sygnały użycia narzędzi AI w tekście
[Jeśli subagent wykrył wzorce charakterystyczne dla pisania AI — opisz krótko. Odwołaj się do strony. Jeśli student zadeklarował użycie w rozdziale GenAI — odnieś się do spójności deklaracji z tym, co widać w tekście.]

## 4. Mocne i słabe strony

### 4.1 Kluczowe atuty
- [Konkretny atut 1 ze wskazaniem strony]
- [Konkretny atut 2 ze wskazaniem strony]
- [Konkretny atut 3 — opcjonalnie]

### 4.2 Najważniejsze niedociągnięcia
- [Konkretny defekt 1 ze wskazaniem strony]
- [Konkretny defekt 2 ze wskazaniem strony]
- [Konkretny defekt 3]

## 5. Ocena końcowa

**Ocena proponowana: [X,X]**

Uzasadnienie oceny: [2-4 zdania wiążące ocenę z konkretnymi wymienionymi wyżej defektami / atutami. NIE piszemy ogólników typu "praca stanowi wartościowy wkład" — tylko konkretne uzasadnienie, dlaczego ta wartość, a nie wyższa / niższa.]
```

## Zasady wypełniania

- **Każda sekcja ma wskazane strony / fragmenty pracy.** Bez wskazań recenzja jest pobieżna (jeden z problemów WIMIIP).
- **Zwięzłość > rozwlekłość.** Lepiej 2 zdania konkretne niż 5 zdań ogólników.
- **Nie rozpoczynaj zdań od** "Dodatkowo,", "Co więcej,", "Istotnie,", "Warto podkreślić,", "Należy zauważyć,". To znaczniki stylu AI.
- **Nie używaj** frazesów typu "praca stanowi cenny wkład", "imponująca analiza", "dogłębne ujęcie tematu".
- **Używaj** konkretnych czasowników: *wykazał, pominął, uzasadnił, nie rozważył, zastosował, zweryfikował, zignorował, przyjął bez uzasadnienia*.

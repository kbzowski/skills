# Szablon opinii opiekuna (APD)

Opinia opiekuna w APD jest krótsza niż recenzja recenzenta i ma inną strukturę. Dzieli się na: **charakterystykę merytoryczną pracy** oraz **ocenę dyplomanta** (proces realizacji).

```markdown
# Opinia opiekuna pracy dyplomowej

**Autor:** [imię nazwisko]
**Tytuł:** [tytuł pracy]
**Opiekun:** [tytuł imię nazwisko]
**Stopień studiów:** [inżynierska / magisterska]
**Kierunek:** Informatyka Techniczna, WIMIIP AGH

## 1. Charakterystyka merytoryczna pracy

### 1.1 Zgodność treści z kierunkiem studiów
[Czy treść pracy mieści się w obszarze Informatyki Technicznej? Które efekty uczenia się są realizowane? 2-3 zdania.]

### 1.2 Stopień realizacji celu pracy
[Przytocz cel ze wstępu i oceń realizację. **Dla mgr** — wskaż, czy praca spełnia wymóg "samodzielnego opracowania" i "samodzielnego analizowania i wnioskowania". **Dla inż** — czy stanowi udokumentowaną realizację problemu inżynierskiego. 3-4 zdania.]

### 1.3 Samodzielność wykonania pracy
[Odnieś się do:
- treści raportu JSA (jeśli dostępny — poziom podobieństwa),
- wykorzystania GenAI zgodnie z deklaracją studenta w obowiązkowym rozdziale,
- oświadczenia studenta o samodzielności.
2-4 zdania. Jeśli są zastrzeżenia — wskaż konkretnie.]

### 1.4 Zgodność pracy z wytycznymi redakcyjnymi WIMIIP
[Struktura, objętość (inż 20-35, mgr 40-60 stron), obecność wszystkich wymaganych sekcji, w tym rozdziału GenAI. 1-2 zdania.]

### 1.5 Stopień trudności podjętego problemu oraz dobór metod/narzędzi
[Opiekun, w odróżnieniu od recenzenta, zna kontekst sformułowania tematu i może go ocenić. Dwa aspekty łącznie:
**Stopień trudności** — czy temat był wymagający dla poziomu studiów (nie „zawyżony" jako mgr, nie „zaniżony" jako inż), jakie wymagał kompetencji, czy zakres był ambitny.
**Dobór metod i narzędzi** — czy dyplomant uzasadnił wybór technologii/metod, czy rozważył alternatywy, czy wybór był adekwatny do problemu. Niepowtarzaj 1.2 — tam jest o realizacji celu, tu o trafności drogi. 2-4 zdania.]

## 2. Ocena dyplomanta

### 2.1 Umiejętność praktycznego wykorzystania wiedzy
[Jak dyplomant wykorzystał wiedzę ze studiów? Które przedmioty / obszary widać w pracy? 2-3 zdania.]

### 2.2 Kompetencje i umiejętności w zakresie kierunku
[Co dyplomant opanował, co wykazał w pracy. **Dla mgr** — umiejętności samodzielnej analizy, formułowania hipotez, wnioskowania. **Dla inż** — umiejętności projektowe, implementacyjne, weryfikacyjne. 2-3 zdania.]

### 2.3 Wartość praktyczna i potencjał wdrożeniowy
[**Szczególnie istotne dla inż.** Czy wynik pracy jest gotowy do wykorzystania (system, narzędzie, raport audytowy, metodyka), czy pozostaje prototypem akademickim? Kto mógłby z tego skorzystać (konkretny zakład, zespół, społeczność open source)? Dla mgr — waga mniejsza, ale warto wskazać, czy rezultat ma potencjał wdrożeniowy poza pracą. 1-3 zdania.]

### 2.4 Terminowość realizacji zadań
[Czy dyplomant pracował w terminach? Regularność konsultacji. Jeśli były problemy — jak zostały rozwiązane. 1-2 zdania.]

## 3. Ocena końcowa

**Ocena proponowana: [X,X]**

Uzasadnienie oceny: [2-3 zdania konkretnie wiążące ocenę z charakterystyką pracy i dyplomanta.]
```

## Opinia opiekuna a recenzja — różnice

| | Opinia opiekuna | Recenzja recenzenta |
| --- | --- | --- |
| perspektywa | proces realizacji + praca | głównie praca |
| obejmuje ocenę dyplomanta | tak | nie |
| długość | zwięźlejsza | bardziej szczegółowa |
| terminowość | obowiązkowy element | nie |
| stopień trudności problemu | opiekun widzi genezę tematu — może ocenić | tylko z tekstu, ograniczenie |
| wartość praktyczna/wdrożeniowa | tak (sekcja 2.3) | przez pryzmat rezultatów pracy |
| samodzielność — źródło | obserwacja procesu + tekst | tylko tekst |

## Zasady wypełniania

Wszystkie zasady z `template-recenzja.md` dotyczące stylu (unikanie wzorców AI, konkretne czasowniki, brak frazesów) obowiązują tak samo. Opinia opiekuna ma być krótsza, ale **nie pobieżna** — każda sekcja wymaga konkretnej treści, nie ogólnika.

Opiekun ma dodatkowe informacje z procesu realizacji (których recenzent nie ma). Skill zachęca opiekuna, by te informacje wykorzystał w sekcji 2 — ale **nie zastępuje nimi analizy tekstu pracy**. Jeśli proces był wzorowy, a tekst słaby — opinia musi to odzwierciedlić.

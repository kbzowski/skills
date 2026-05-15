# Inżynierska vs magisterska — rozróżnienie wymagań

Ten dokument jest **sercem skilla**. Kluczowy problem recenzji na WIMIIP to nierozróżnianie wymagań inż i mgr — prace inżynierskie "w przebraniu magisterskim" dostają 5,0, bo nikt nie egzekwuje kryterium poszerzenia zakresu. Skill ma to egzekwować.

## Definicje formalne (Ustawa + Regulamin AGH)

**Projekt dyplomowy (inż, I stopień):**
> Udokumentowana realizacja praktycznego przedsięwzięcia projektowego, stanowiąca potwierdzenie umiejętności wykorzystania wiedzy wymaganej od absolwenta studiów I stopnia danego kierunku. Rozwiązanie **problemu inżynierskiego** dla wiodącej dyscypliny kierunku studiów.

**Praca dyplomowa (mgr, II stopień):**
> **Samodzielne opracowanie** określonego zagadnienia naukowego, artystycznego lub praktycznego albo **dokonanie techniczne** lub artystyczne, prezentujące ogólną wiedzę i umiejętności studenta związane ze studiami na danym kierunku, poziomie i profilu, oraz **umiejętności samodzielnego analizowania i wnioskowania**.

Różnica jest w dwóch słowach: **samodzielne opracowanie** (mgr) vs **udokumentowana realizacja** (inż). Mgr musi zawierać element intelektualnej autorskiej syntezy — nie tylko wykonanie zadania wg specyfikacji.

## Cechy charakterystyczne poszerzające zakres (mgr → inż)

Praca mgr, poza wszystkim, co zawiera praca inż, musi mieć **co najmniej jedną z trzech cech** (z prezentacji department meeting):

1. **Element innowacyjny, twórczy lub naukowy** — autorskie rozwiązanie nieobecne w literaturze, propozycja metody, analiza nowatorska.
2. **Pogłębiona analiza** — zbadanie różnych problemów tą samą metodą / algorytmem. *(Np. "zastosowanie XGBoost do trzech różnych zbiorów danych z porównaniem").*
3. **Szerszy kontekst** — wykorzystanie różnych algorytmów / metod do rozwiązania tego samego problemu. *(Np. "porównanie pięciu algorytmów klasyfikacji dla problemu X").*

Jeśli **żadnej** z tych cech nie ma — praca mgr jest za słaba dla swojego stopnia, **niezależnie od jakości wykonania**. To jest sztywne kryterium.

## Objętość

| | inż | mgr |
| --- | --- | --- |
| zalecana objętość | 20-35 stron | 40-60 stron |
| samodzielne prace studenta | min. 50% | min. 50% |

## Bibliografia — oczekiwania wg stopnia

| | inż typowa (praktyczna / wdrożeniowa) | inż z nachyleniem badawczym | mgr |
| --- | --- | --- | --- |
| minimalna liczba prawidłowych pozycji bibliograficznych | brak sztywnego minimum; całkowity brak (0-2) to defekt | oczekuj proporcjonalnie do zakresu analitycznego | **co najmniej 10-15** |
| Co się liczy | książki, artykuły, raporty, standardy, prace naukowe (doktoraty / mgr / inż — recenzowane), dane publiczne (np. GUS) | j.w. | j.w. |
| Co NIE liczy się do bibliografii | dokumentacja frameworków, blogi, wpisy na forach, strony firm — powinny być w przypisach dolnych | j.w. | j.w. |

Szczegóły w `agents/literature-verifier.md` (sekcja "Ocena jakości doboru").

Objętość poza zakresem jest sygnałem — nie defektem automatycznym, ale wymaga komentarza w recenzji. Praca inż na 60 stron z reguły jest "nadmuchana" (literatura skopiowana, puste opisy). Praca mgr na 30 stron z reguły jest zbyt płytka jak na swój poziom.

## Struktura pracy — obowiązkowe sekcje

Obie prace muszą zawierać:

1. **Strona tytułowa, spis treści**
2. **Wstęp** (2-3 strony) — wprowadzenie, uzasadnienie tematu, **cel pracy**, założenia techniczne, streszczenie
3. **Część analityczna** — wprowadzenie do tematu, analiza literatury, przegląd istniejących rozwiązań, **uzasadnienie wyboru podejścia**
4. **Część syntetyczna** — opis przyjętych rozwiązań + uzasadnienie ich wyboru
5. **Część weryfikacyjna** — warunki testów, metody (mgr), wyniki + analiza, wnioski
6. **Zakończenie** — podsumowanie + kierunki dalszych prac
7. **Rozdział "Wykorzystanie narzędzi GenAI"** — **obowiązkowy w inż i mgr**
8. **Bibliografia**
9. **Załączniki** (opcjonalnie — obliczenia, kod, instrukcje)

**Brak któregokolwiek z 1-8 = defekt do odnotowania w sekcji "struktura i układ" recenzji.**

Brak rozdziału GenAI to defekt poważny, bo wymóg jest eksplicytny — obniża ocenę strukturalną minimum o 0,5.

## Kontrolne pytania do pracy — inż

Gdy czytasz projekt dyplomowy, zadaj sobie:

1. **Czy jest zdefiniowany problem inżynierski?** Nie "temat zainteresowania", tylko **problem do rozwiązania** z mierzalnymi kryteriami sukcesu.
2. **Czy jest udokumentowany proces realizacji?** Praca pokazuje ścieżkę: problem → analiza opcji → wybór → implementacja → weryfikacja. Brak którejś fazy = defekt.
3. **Czy jest weryfikacja?** Studenci często pomijają — "działa u mnie" to nie weryfikacja. Wymagane: warunki testów, kryteria, wyniki, analiza.
4. **Czy wnioski odpowiadają na cel?** Jeśli cel brzmiał "zaprojektować i przetestować", a wnioski mówią "opisałem framework X", to defekt.
5. **Czy wybrane narzędzia/metody są uzasadnione?** "Użyłem Reacta bo znam" to nie uzasadnienie. Powinno być porównanie z alternatywami.

Projekt inż **nie musi** mieć elementu innowacyjnego — wystarczy rzetelna realizacja problemu inżynierskiego.

## Kontrolne pytania do pracy — mgr

Wszystkie powyższe plus:

1. **Gdzie konkretnie jest element poszerzający zakres?** (1 z 3 cech). Wskaż stronę. Jeśli nie potrafisz wskazać — to nie praca mgr.
2. **Czy autor samodzielnie analizuje i wnioskuje?** Odróżnij: samodzielne wnioskowanie (autor łączy obserwacje, formułuje hipotezy, weryfikuje je) vs przepisywanie wniosków z literatury / wniosków oczywistych ("algorytm działał").
3. **Czy część analityczna to krytyczny przegląd, czy wypisanie?** Przegląd krytyczny: autor ocenia, porównuje, wskazuje luki. Wypisanie: "Autor X w pracy Y napisał Z, autor A w pracy B napisał C".
4. **Czy metody badawcze są opisane?** Dla mgr to wymóg eksplicytny ("metody badawcze" w części weryfikacyjnej). Dla inż wystarczy "warunki testowania".
5. **Czy praca ma oś/tezę, czy jest zbiorem luźnych rozdziałów?** Mgr musi mieć spójną linię rozumowania od wstępu do wniosków.

## Mapowanie defektów na stopień oceny

Patrz osobny plik: `grading-rubric.md`. Krótko:

- **Mgr bez żadnej z trzech cech poszerzających** — maksymalnie 4,0 (dostateczny plus / dobry). Nigdy 4,5 ani 5,0.
- **Mgr bez rozdziału GenAI** — -0,5 od oceny wyjściowej.
- **Inż bez sekcji weryfikacyjnej** — maksymalnie 3,5.
- **Inż z celem nierealizującym się w pracy** (rozjazd cel-wnioski) — maksymalnie 3,5.

## Sygnały, że praca jest "inż w przebraniu mgr"

To jest najczęstszy patologiczny przypadek na WIMIIP. Sygnały:

- Tylko jedno rozwiązanie badane, jedna metoda, jeden zbiór danych — brak porównania.
- Brak rozdziału "state of the art" / krytycznego przeglądu literatury.
- Bibliografia 10-15 pozycji, głównie dokumentacja frameworków, brak artykułów naukowych.
- Wnioski ograniczone do "działa" / "nie działa" bez szerszej refleksji.
- Tytuł zaczyna się od "Projekt i implementacja..." (bez aspektu analitycznego).
- Brak hipotezy badawczej lub pytania badawczego.

Jeśli **3 lub więcej** z tych sygnałów występuje w pracy mgr — to jest mgr przebrana. Ocena max 4,0 z wyraźnym uzasadnieniem w recenzji.

## Sygnały, że praca jest nadmiernie rozbudowana (inż "na mgr-a")

Odwrotny patologiczny przypadek — mniej szkodliwy, ale też defekt:

- Praca inż ma 50+ stron.
- Część analityczna zajmuje 40% pracy zamiast 20-25%.
- Rozdziały literaturowe nie wiążą się z częścią implementacyjną.
- Cel sformułowany jak dla mgr (np. "analiza porównawcza algorytmów..."), ale realizacja ograniczona do jednego.

To rzadziej obniża ocenę, ale trzeba to skomentować — recenzent powinien zasugerować, że praca mogłaby być podstawą pracy mgr po rozszerzeniu.

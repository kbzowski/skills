---
name: thesis-review-wimiip
description: Pisanie recenzji i opinii prac dyplomowych (inżynierskich i magisterskich) z kierunku Informatyka Techniczna na WIMIIP AGH. Używaj ZAWSZE gdy użytkownik prosi o recenzję, opinię, ocenę pracy dyplomowej, projektu dyplomowego, pracy magisterskiej lub inżynierskiej — nawet jeśli nie wspomina o AGH czy WIMIIP. Także gdy użytkownik przesyła PDF/DOCX i mówi "przeczytaj pracę", "co myślisz o tej pracy", "oceń tę pracę dyplomową", "przygotuj recenzję", "napisz opinię promotora". Skill rozróżnia wymagania dla projektu inżynierskiego (problem inżynierski) i pracy magisterskiej (element innowacyjny, pogłębiona analiza, szerszy kontekst) i dobiera ostrość oceny do stopnia studiów.
---

# Recenzja pracy dyplomowej — Informatyka Techniczna WIMIIP AGH

Ten skill wspiera nauczyciela akademickiego w napisaniu **opinii opiekuna** lub **recenzji recenzenta** pracy dyplomowej studenta kierunku Informatyka Techniczna na WIMIIP AGH. Obsługuje **projekty dyplomowe (inż)** i **prace dyplomowe (mgr)**. Wynik to gotowy tekst w Markdown do wklejenia do APD.

## Dlaczego ten skill istnieje

Na WIMIIP zidentyfikowano trzy powtarzające się problemy w recenzjach (dane z 24/25: średnia ocen 4,5-4,8 — zawyżona):

1. **Niedostosowanie poziomu pracy do stopnia studiów** — prace "inżynierskie w przebraniu magisterskim" dostają 5,0, bo nikt nie egzekwuje kryterium "poszerzenia zakresu".
2. **Halucynacje AI** — zmyślone przypisy, nieistniejące DOI, wygenerowane wykresy bez interpretacji.
3. **Pobieżne recenzje** — recenzent pisze 3 zdania i stawia 5,0.

Skill wymusza strukturalną, krytyczną analizę adresującą te problemy. (Czwarty problem z prezentacji WIMIIP — niewłaściwe tytuły — jest adresowany na etapie zatwierdzania tematu, nie na etapie recenzji.)

## Workflow — co robisz po kolei

### Krok 1 — Ustal kontekst (tylko gdy nie wynika z wejścia)

Pytaj o to, czego nie da się ustalić z wejścia. Jeśli użytkownik podał ścieżkę do pliku, nazwa pliku / metadane mogą już mówić, czy to inż czy mgr. Jeśli jednoznacznie wynika — pomiń pytanie.

Potencjalne pytania (zadajesz tylko te, których odpowiedź nie jest znana):

1. **Czy piszesz opinię opiekuna, czy recenzję recenzenta?** *(opiekun / recenzent)*
2. **Stopień studiów?** *(inż / mgr)* — z reguły wynika z tytułu pliku ("Praca_Magisterska_...", "Projekt_Dyplomowy_...") lub strony tytułowej pracy.
3. **Ścieżka pliku pracy** — tylko jeśli nie została załączona.

Odpowiedzi krótkie, jednosłowne.

### Krok 2 — Zasada nadrzędna: pytania tylko wtedy, gdy tekst pracy nie odpowiada

**Skill jest czytelnikiem pracy, nie ankieterem.** Nie zadawaj pytań, na które odpowiedź znajduje się lub powinna się znajdować w samej pracy.

Dobrze napisana praca **musi** zawierać:

| Element | Gdzie w pracy | Brak = |
| --- | --- | --- |
| cel pracy, problem, zakres, założenia | wstęp (2-3 strony) | poważny defekt — odnotuj w recenzji |
| stan wiedzy, uzasadnienie podejścia | część analityczna | defekt |
| opis przyjętych rozwiązań | część syntetyczna | defekt |
| warunki testów, wyniki, analiza | część weryfikacyjna | defekt |
| podsumowanie, kierunki dalszych prac | zakończenie | defekt |
| deklaracja użycia GenAI (inż i mgr) | osobny rozdział | **obowiązkowy brak — obniża ocenę** |

**Jeśli któregoś elementu brakuje w pracy — to nie jest luka do zapełnienia wywiadem, to defekt do odnotowania w sekcji "słabe strony" recenzji i uwzględnienia w ocenie.** Nie rekompensuj słabości pracy wywiadem z autorem ani opiekunem.

#### Jedyne pytania, które wolno zadać

**Obie ścieżki** — startowo (jeśli nie wynika z pliku/metadanych):
- Rola: opiekun czy recenzent?
- Stopień: inż czy mgr?
- Ścieżka pliku pracy.

**Warunkowo (opiekun i recenzent)** — tylko jeśli z pracy wynika, że coś zostało dostarczone z zewnątrz, a jego status ma wpływ na ocenę samodzielności (np. praca mówi "wykorzystano dane zakładu X" bez wyjaśnienia, czy student je pozyskał sam) — wolno zadać **jedno konkretne pytanie** wskazujące stronę i fragment. Wzór: *"Na s. 17 autor pisze o wykorzystaniu zbioru danych X. Czy student pozyskał go sam, czy został mu dostarczony?"* To nie jest wywiad — to uzupełnienie luki w pracy.

**Na końcu (po analizie, przed finalizacją)** — dla obu ścieżek jedno pytanie: *"Zanim zaproponuję ocenę — jak Ty byś ocenił tę pracę (2-5)?"* Skill potem pokazuje swoją niezależną propozycję. Nie dopasowuje się.

#### Czego NIE wolno pytać — zamiast tego sprawdź w pracy

Dla każdego z poniższych elementów najpierw sprawdź, czy i gdzie znajduje się w pracy. Jeśli go nie ma — nie zadawaj pytania, zanotuj brak jako defekt.

| Nie pytaj o to | Sprawdź w pracy | Jeśli brak |
| --- | --- | --- |
| cel / problem do rozwiązania | wstęp (z reguły 1-2 pierwsze strony) | defekt — obniża ocenę merytoryczną |
| oczekiwane rezultaty, założenia techniczne | wstęp, akapity o celach szczegółowych | defekt |
| uzasadnienie poziomu (problem inżynierski / poszerzenie zakresu) | część analityczna, uzasadnienie wyboru problemu | defekt — zwłaszcza dla mgr (wymóg "samodzielnego opracowania naukowego lub dokonania technicznego") |
| wkład własny studenta | oświadczenie o samodzielności, rozdział GenAI, ślady stylu AI, spójność narracji, jakość wniosków | ocena na podstawie całości — nie pytaj opiekuna |
| ewentualna zmiana zakresu | niespójności między wstępem a częścią weryfikacyjną, rozjeżdżające się sekcje | jeśli są niespójności — defekt; jeśli nie ma — nieistotne |
| wykorzystane dane / kod / infrastruktura | wstęp lub część syntetyczna powinna deklarować źródło danych, wybór stacku | brak deklaracji źródeł zewnętrznych — defekt samodzielności |

### Krok 3 — Przeczytaj pracę bezpośrednio (PDF/DOCX)

Nie używaj żadnego pośredniego skryptu ekstrakcji. Podaj plik PDF/DOCX do narzędzia `Read` w całości — model czyta pracę natywnie wraz ze wszystkimi grafikami, diagramami, tabelami i wykresami. Jeśli praca jest długa, czytaj ją partiami (np. po 15-20 stron na raz), ale **nigdy nie pomijaj stron z grafikami** — wizualna analiza rysunków i wykresów jest wymagana.

Notuj sobie w trakcie czytania:
- strukturę (numery stron, na których zaczynają się kolejne rozdziały),
- wykryty stopień studiów, tytuł, autora, opiekuna (ze strony tytułowej),
- obecność rozdziału „Wykorzystanie narzędzi GenAI" (obowiązkowy dla inż i mgr),
- listę pozycji bibliografii z numerami oraz wszystkie cytowania inline (`[1]`, `[2]`, ...),
- listę rysunków, tabel i fragmentów kodu wraz z ich numerami i numerami stron.

Opinia opiekuna i recenzja są wpisywane w systemie APD, a nie w pliku pracy — skill nie musi ich filtrować z tekstu.

### Krok 3a — Weryfikacja grafik i materiałów wizualnych

Grafiki (rysunki, wykresy, diagramy, schematy, screeny interfejsu) są częstym miejscem halucynacji i powierzchowności — student może wygenerować wykres z wartościami bez pokrycia w danych, skopiować diagram z dokumentacji bez źródła, lub wstawić rysunek bez interpretacji w tekście.

Dla każdego rysunku / wykresu / diagramu sprawdź:

1. **Podpis i numer.** Czy rysunek ma numer (np. „Rys. 7") i sensowny podpis? Rysunki bez podpisu lub z podpisem generycznym („Wynik") to defekt redakcyjny.
2. **Odwołanie w tekście.** Czy rysunek jest cytowany w głównym tekście? Rysunek bez odwołania — defekt.
3. **Interpretacja.** Czy po odwołaniu do rysunku autor pisze, co z niego wynika? „Jak widać na rys. 7, wyniki są zadowalające" — to nie interpretacja. Oczekiwane: konkretne odczyty (wartości, trendy, outliery, wnioski).
4. **Źródło.** Jeśli rysunek jest wykresem z danymi — czy dane, na podstawie których powstał, są dostępne lub opisane w pracy? Jeśli to diagram koncepcyjny skopiowany z literatury — czy ma podpis „na podstawie [X]" i cytat?
5. **Spójność z tekstem.** Czy wartości / etykiety na wykresie zgadzają się z liczbami podanymi w tekście? Rozjazd jest sygnałem automatycznej generacji bez weryfikacji.
6. **Jakość wizualna a wymowa.** Wykres bez osi, bez jednostek, z nieczytelnymi etykietami → defekt redakcyjny. Wykres „ładny" ale bezwartościowy (np. pie-chart z 95% / 5% — nic nie komunikuje) → skomentuj.

Zanotuj listę grafik problematycznych ze stronami i wstaw je do sekcji recenzji 2.2 (jeśli problem redakcyjny) albo 1.5 / 1.6 (jeśli problem merytoryczny — brak interpretacji, rozjazd z tekstem).

### Krok 4 — Orkiestracja niezależnych agentów (równolegle)

**Filozofia.** Recenzja to nie monolog — to wynik weryfikacji w wielu wymiarach. Główny przebieg czyta pracę i syntetyzuje wnioski; **niezależni agenci sprawdzają fakty, których model główny może nie pamiętać lub mylnie ocenić**. Każdy agent dostaje zwięzły, zamknięty prompt z konkretnym zakresem i zwraca raport, który wchodzi jako dane wejściowe do recenzji. Agentów uruchamiaj **równolegle** (jeden message, wiele Agent tool calls) — to skraca czas i pozwala porównać niezależne werdykty.

#### Agenci uruchamiani po przeczytaniu pracy

1. **literature-verifier** (`agents/literature-verifier.md`) — weryfikuje bibliografię agresywnie: każde DOI, autor/tytuł/rok, czy źródła to artykuły naukowe / dokumentacje / blogi (proporcja ma znaczenie dla oceny — patrz `inz-vs-mgr.md`). Halucynacje bibliograficzne są kluczowym problemem WIMIIP.

2. **ai-pattern-detector** (`agents/ai-pattern-detector.md`) — skanuje tekst pod kątem wzorców pisania AI (patrz `references/ai-writing-patterns.md`).

3. **fact-checker (online)** — uruchom z dostępem do WebSearch/WebFetch. Zadanie: zweryfikować **konkretne tezy merytoryczne** z pracy (daty, wartości techniczne, parametry standardów, status technologii, nazwy publikacji, liczby cytowane z innych prac). Format promptu: lista 10-20 ponumerowanych tez z numerami stron. Format odpowiedzi: ✓ POTWIERDZONE / ⚠ NIEŚCISŁE / ✗ BŁĘDNE z linkami źródłowymi do każdej tezy. **Agent musi mieć regułę "zanim oznaczysz coś jako błędne, zweryfikuj w sieci — twoja data odcięcia wiedzy może nie pokrywać się z datą pracy"**.

#### Agent uruchamiany na końcu — przed finalizacją

4. **review-auditor** — niezależny audytor Twojej własnej recenzji. Po napisaniu wstępnej wersji recenzji uruchom agenta z dwoma wejściami: (a) plik PDF pracy, (b) plik z recenzją. Zadanie: dla **każdego konkretnego twierdzenia** w recenzji opatrzonego numerem strony/cytatem/liczbą sprawdzić, czy znajduje pokrycie w pracy. Format wyjścia: tabela `Twierdzenie | Lokalizacja | ✓/⚠/✗ | Komentarz`. Po raporcie audytora — popraw recenzję w punktach oznaczonych ⚠ i ✗.

**Reguła: ufaj raportowi audytora bardziej niż własnej pamięci.** W toku pisania recenzji łatwo o false-positive (zarzut czegoś, czego nie ma) lub błędną lokalizację (cytat z innej strony niż się wydaje). Audytor czyta pracę z czystej perspektywy.

#### Wskazówki orkiestracyjne

- **Równoległość.** Agenci 1-3 startują w jednej wiadomości po przeczytaniu pracy. Agent 4 startuje po napisaniu recenzji.
- **Zamknięte prompty.** Każdy agent dostaje samodzielny prompt — żadnych odwołań do "wcześniejszej rozmowy". Agent musi mieć wszystko, czego potrzebuje, w jednym tekście.
- **Format wyjścia narzucany.** Każdy prompt musi narzucać konkretny format (tabela, lista z werdyktami) — bez tego raporty są rozwlekłe i trudne do scalenia.
- **Brief w tonie kolegi-eksperta**, nie ankiety. Wyjaśnij agentowi, **po co** to robi (kontekst recenzji), a nie tylko **co**.
- **Limit objętości.** Każdy agent powinien mieć cap (np. "raport pod 1500 słów", "max 50 wierszy tabeli"), inaczej wraca rozlewny tekst, który zalewa kontekst.

### Krok 5 — Analiza pracy według kryteriów

Przeczytaj strukturę pracy i oceń ją wg kryteriów z:
- `references/inz-vs-mgr.md` — **kluczowy plik** — precyzyjne rozróżnienie wymagań inż vs mgr.
- `references/grading-rubric.md` — jak braki mapują się na ocenę.
- `references/common-problems.md` — najczęstsze defekty recenzji WIMIIP.

Dla **inż** pytaj: *Czy to jest udokumentowana realizacja problemu inżynierskiego, czy tylko rozbudowane zaliczenie przedmiotu?*
Dla **mgr** pytaj dodatkowo: *Gdzie jest element innowacyjny / twórczy / naukowy? Gdzie pogłębiona analiza lub szerszy kontekst? Czy student wnioskuje samodzielnie?*

#### Krok 5a — Analiza języka i terminologii

Po analizie merytorycznej zrób **osobny przebieg** koncentrujący się wyłącznie na warstwie językowej. To nie jest powielenie pracy ai-pattern-detectora — tamten szuka *wzorców AI*, ten szuka *błędów językowych*:

- **Błędy ortograficzne** — szczególnie te powtarzające się (np. ten sam błąd na wielu wykresach jest poważniejszy niż jednorazowa literówka).
- **Błędy gramatyczne i składniowe** — niepotrzebne przecinki, brakujące słowa w zdaniach, powtórzone wyrazy.
- **Niespójności** — kapitalizacja terminów (Fence vs fence, Staging vs staging), kolejność nazwisk autorów, mieszane cudzysłowy (proste angielskie vs polskie typograficzne), pisownia tych samych terminów polską vs angielską formą.
- **Anglicyzmy bez tłumaczenia** w polskim tekście (np. *current GPU*, *input lag*, *memcpy* jako rzeczownik).
- **Defekty redakcyjne tabel/wykresów/podpisów** — zdublowana numeracja, urwane podpisy, błędne odnośniki konfiguracji, nakładające się etykiety.
- **Jakość kodu** — fragmenty kodu w pracy o programowaniu **muszą się kompilować**. Sprawdź proste przypadki (deklaracje zmiennych, struktury kontrolne) — błąd składniowy w przykładzie kodu jest defektem merytoryczno-redakcyjnym.

Notuj wszystko z numerami stron / numerami obiektów. To zasili sekcję 3 recenzji oraz "niedociągnięcia" (4.2).

#### Krok 5b — Analiza części weryfikacyjnej / eksperymentalnej

Dla prac z częścią weryfikacyjną (eksperyment, pomiar, badanie ankietowe, analiza zbioru danych, walidacja użytkowa, porównanie metod) przejdź rozdział pod kątem **rzetelności metodycznej i odtwarzalności**. Pytania domyślne:

- **Rama interpretacyjna.** Czy autor stawia jakąś ramę przed prezentacją wyników — pytanie badawcze, hipotezę, oczekiwany wynik, kryterium sukcesu? Hipoteza w sensie ścisłym jest wymagana tylko dla prac o charakterze badawczym (głównie mgr lub inż z naciskiem badawczym); w pracach typowo wdrożeniowych / projektowych wystarczy jasno postawione kryterium akceptacji wyniku ("system uznajemy za działający, jeśli...") albo cel pomiaru sformułowany w wstępie. Defektem jest natomiast prezentowanie wyników bez **żadnej** ramy interpretacyjnej — autor wówczas może wyciągać wnioski post hoc na podstawie samych liczb, ale traci możliwość weryfikacji założeń.
- **Procedura badawcza.** Czy procedura jest opisana w stopniu pozwalającym ją powtórzyć przez osobę trzecią? (Liczba prób / iteracji / respondentów / próbek; warunki początkowe; dobór próby; zabezpieczenia przed obciążeniem wyniku.)
- **Środowisko / narzędzia.** Czy zadeklarowane jest środowisko (sprzęt, oprogramowanie z wersjami, platforma, narzędzie pomiarowe lub sposób zbierania danych)? Brak konkretów uniemożliwia weryfikację.
- **Parametry obiektów badanych.** Czy parametry tego, co testowane (zbiór danych, model, scenariusz, prototyp, ankieta), są podane w pełni — z konkretami a nie ogólnikami?
- **Testy kontrolne / grupy odniesienia.** Czy autor uwzględnia scenariusze, w których wynik mógłby być artefaktem doboru próby/warunków? Ważne dla każdej pracy porównawczej — zawsze pytaj, czy istnieje punkt odniesienia (baseline).
- **Statystyka / istotność.** Czy podane są miary rozrzutu (odchylenie, percentyle, przedział ufności), liczba powtórzeń, ewentualnie test istotności? Dla pracy mgr — wymóg silniejszy niż dla inż.
- **Spójność wewnętrzna.** Czy wartości w tabelach, wykresach i tekście się zgadzają? Czy te same parametry w różnych miejscach pracy mają te same wartości? Niespójności bez wyjaśnienia są sygnałem ostrzegawczym.
- **Interpretacja vs prezentacja.** Czy autor po pokazaniu wyniku **wyciąga wniosek** (co z tej liczby wynika), czy tylko opisuje liczbę? "Wynik wyniósł X" to nie analiza.
- **Dyskusja ograniczeń.** Czy autor sam wskazuje granice swojego badania (czego wynik nie obejmuje, gdzie są źródła błędu)? Dla mgr — element wymagany.

Te uwagi wchodzą do sekcji 1.3 recenzji (trafność doboru metod), 1.6 (poprawność wnioskowania), 1.7 (krytyczna analiza) i do "niedociągnięć".

**Reguła:** to kontrolne pytania, nie checklist do wypełnienia. Dobierz te, które pasują do typu pracy. Praca teoretyczna lub czysto implementacyjna może nie mieć rozdziału weryfikacyjnego w klasycznym sensie — wtedy ten krok pomijaj lub okrojona wersja (czy implementacja została w ogóle przetestowana, na czym, w jakich warunkach).

### Krok 6 — Wybór formatu recenzji + napisanie

**Format APD (WIMIIP).** APD nie wymusza struktury — pole opinii/recenzji to **otwarty tekst**. Użytkownik wkleja, co chce. Skill oferuje dwa style organizacji tego tekstu:

**Zanim napiszesz recenzję, zapytaj użytkownika o format:**

> *"Czy chcesz recenzję w wersji **szczegółowej** (z wewnętrznym podziałem na rozdziały i podpunkty — łatwa do skanowania, każdy aspekt wyraźnie oznaczony) czy **skompresowanej** (jednolity tekst prozą, w stylu wypowiedzi człowieka — krótszy, brzmi naturalniej)?"*

#### Wersja szczegółowa

Użyj szablonu z:
- `references/template-recenzja.md` — dla recenzenta,
- `references/template-opinia.md` — dla opiekuna.

Szablony zawierają **wewnętrzny** podział na rozdziały (1. Ocena merytoryczna, 2. Struktura, 3. Język, 4. Mocne/słabe strony, 5. Ocena końcowa) z podpunktami. Ten podział nie jest narzucony przez APD — jest narzędziem organizacyjnym dla recenzenta, który chce mieć każdy aspekt wyraźnie wydzielony. Każda sekcja 2-4 zdania, każda ze wskazaniem stron/cytatów.

#### Wersja skompresowana

Jednolity tekst prozą, **bez nagłówków sekcji**, **bez numeracji**. Cała ocena merytoryczno-strukturalno-językowa płynie w jednym ciągu, kończąc oceną i jednozdaniowym uzasadnieniem.

Zasady stylu skompresowanego:

- **Akapity tematyczne, nie sekcyjne.** Akapit może mówić o metodyce; następny o bibliografii; następny o defektach językowych. Brak nagłówków "1.4 Bibliografia".
- **Płynne przejścia.** Myśl o jednym defekcie wprowadza kolejny: *"...autor nie przeprowadza testu kontrolnego, który rozstrzygnąłby tę kwestię. Bibliografia zawiera 25 pozycji, ale to jej forma stanowi główny defekt..."* — brak szwów.
- **Krótkie cytaty inline z numerami stron** zamiast wydzielonych przykładów: *literówki: "trójkąt pokrywająvy" (s. 64), "Pokazuje on sposób łatwy sposób na stworzenie" (s. 12)*.
- **Końcowe zdanie autorskie.** Zamiast standardowej formuły "ocena uzasadniona X, Y, Z" — jedno osobiste zdanie z subiektywną oceną kalibrującą surowość/łagodność. Wzór z realnej recenzji: *"Ciężko oprzeć się wrażeniu, że w redakcji pracy wykorzystano o wiele więcej AI niż autor zadeklarował, dane liczbowe są jednak spójne i wysoce prawdopodobne, co w mojej ocenie jest wystarczające do akceptacji ich jako samodzielnego wkładu dyplomanta."* Tak pisze recenzent-człowiek: stawia tezę i jednocześnie ją kalibruje.
- **Bez wstępu typu "W niniejszej recenzji ocenię..."** — od razu do treści.
- **Długość docelowa:** 4-7 akapitów po 4-8 zdań. Krótsze niż wersja szczegółowa.
- **Ocena na końcu** wraz z 1-2 zdaniami uzasadnienia.

Reguły stylu z `references/ai-writing-patterns.md` obowiązują **w obu formatach**.

### Krok 7 — Propozycja oceny + konfrontacja

1. Zapytaj użytkownika: *"Zanim zaproponuję ocenę — jak Ty byś ocenił tę pracę (2-5)?"*
2. Niezależnie oblicz propozycję oceny wg `references/grading-rubric.md` na podstawie zebranych defektów i pozytywnych sygnałów.
3. Pokaż obie oceny. **Nie dopasowuj swojej oceny do oceny użytkownika — w żadną stronę.** Jeśli użytkownik zaproponował ocenę niższą niż wynika z analizy skilla (np. 3,5, a praca obiektywnie zasługuje na 4,5), skill **podnosi ocenę** z uzasadnieniem — wskazuje mocne strony, których użytkownik mógł niedocenić. Jeśli użytkownik zaproponował wyższą ocenę niż wynika z analizy — skill obniża, wskazując defekty. Kierunek konfrontacji jest symetryczny. Użytkownik ostatecznie decyduje, co wpisać.

### Krok 8 — Niezależny audyt recenzji (review-auditor)

**Po napisaniu wstępnej recenzji, przed jej finalizacją** — zapisz recenzję do pliku `.md` i uruchom niezależnego agenta (general-purpose) z dwoma wejściami: PDF pracy + plik recenzji. Zadanie agenta: zweryfikować każde konkretne twierdzenie z recenzji (cytat, numer strony, liczba, lokalizacja) względem faktycznej treści pracy.

Format wyjścia agenta:

| Twierdzenie z recenzji | Strona/lokalizacja | Werdykt (✓/⚠/✗) | Komentarz |

Agent nie ma kontekstu wcześniejszej rozmowy — czyta pracę "na świeżo". To eliminuje:
- false-positive (zarzut cech, których nie ma — np. zarzut niespójnej kapitalizacji terminu, który w pracy jest spójnie pisany),
- błędne lokalizacje (cytat przypisany do złej strony),
- przesadzone uogólnienia ("większość wykresów ma X" gdy faktycznie tylko niektóre).

Po raporcie audytora:
- ✗ → usuń zarzut z recenzji (lub popraw, jeśli da się ratować z innym numerem strony),
- ⚠ → przeformułuj/ogranicz (np. zawęź lokalizację z "s. 8 i 18" do "s. 8" jeśli na s. 18 nie znaleziono),
- ✓ → zostaw bez zmian.

**Reguła:** ufaj audytorowi bardziej niż własnej pamięci pracy. Po lekturze 81 stron model główny ma niedokładne wspomnienia o szczegółach — audytor czyta z czystej perspektywy.

### Krok 9 — Finalizacja

Po audycie i poprawkach zwróć użytkownikowi finalny plik `.md`. Użytkownik kopiuje do APD.

## Styl pisanego tekstu — unikaj wzorców AI

Tekst recenzji **nie może wyglądać jak wygenerowany przez AI**. To kwestia wiarygodności — recenzje w stylu AI są natychmiast rozpoznawane przez komisję i rzucają cień na recenzenta.

Konkretne zakazy (pełna lista w `references/ai-writing-patterns.md`):

- **Nie używaj** słów-sygnałów: *warto podkreślić, należy zauważyć, w dzisiejszych czasach, w dynamicznie zmieniającym się świecie, stanowi świadectwo, wpisuje się w szerszy kontekst, gra kluczową rolę, holistyczne podejście, zagłębić się, tkanka, fascynujący.*
- **Nie używaj konstrukcji interpretacyjno-pustych**: *"co świadczy o"*, *"co wskazuje na"*, *"co potwierdza"*, *"co dowodzi"*, *"co stanowi o"*, *"co przekłada się na"*, *"co znajduje odzwierciedlenie w"*, *"co przejawia się w"*. Zamiast doklejać interpretację konstrukcją „co świadczy o X", napisz prosto: *„Autor zastosował metodę X. Metoda X jest adekwatna / nieadekwatna ponieważ Y."*
- **Nie otwieraj zdań od** *"Dodatkowo,"*, *"Co więcej,"*, *"Istotnie,"* w sposób seryjny.
- **Nie stosuj pustych pochwał** ("imponująca praca", "dogłębna analiza") bez konkretnego wskazania strony/fragmentu.
- **Nie używaj** szablonowych zakończeń typu *"Pomimo pewnych niedociągnięć, praca stanowi cenny wkład..."*.
- **Nie nadużywaj myślników długich (—)** ani pogrubień.
- **Nie stosuj** konstrukcji *"nie tylko X, ale także Y"* seryjnie.
- **Nie pisz** "w sposób kompleksowy", "w sposób znaczący" — pisz konkretnie.

Zamiast tego: **konkrety z numerami stron**. *"Na s. 23 autor pomija omówienie złożoności algorytmu, choć porównuje go z O(n log n) na s. 25."* — tak piszą ludzie.

## Pliki pomocnicze

Czytaj je **dopiero gdy są potrzebne** (progressive disclosure):

- `references/inz-vs-mgr.md` — wymagania inż vs mgr, najważniejszy plik skilla.
- `references/template-recenzja.md` — szablon recenzji (recenzent, APD).
- `references/template-opinia.md` — szablon opinii (opiekun, APD).
- `references/grading-rubric.md` — rubryka oceny 2-5 z mapowaniem defektów.
- `references/common-problems.md` — problemy z department meeting WIMIIP.
- `references/ai-writing-patterns.md` — wzorce AI — do unikania w recenzji ORAZ wykrywania w pracy.

- `agents/literature-verifier.md` — instrukcje dla subagenta weryfikującego bibliografię.
- `agents/ai-pattern-detector.md` — instrukcje dla subagenta wykrywającego wzorce AI w pracy.

## Zasada: świadomość własnych ograniczeń wiedzy

Model LLM wykonujący recenzję ma datę odcięcia wiedzy (cutoff) — niekoniecznie pokrywającą się z datą powstania pracy. Zanim stwierdzisz, że coś w pracy jest zmyślone / nieistniejące / niepoprawne (nazwa narzędzia, wersja, standard, publikacja) — **zweryfikuj w sieci**. Dopiero po tym wpisz to do recenzji.

Ta zasada dotyczy całego skilla, nie tylko subagentów: zarówno weryfikator literatury, jak i detektor wzorców AI, jak i sam główny przebieg recenzji muszą się nią kierować. Błędna diagnoza halucynacji (pomyłka recenzenta, że coś nie istnieje, bo model nie wie) kompromituje recenzję bardziej niż przeoczona słabość pracy.

## Zasada oceny

Jeśli praca się nie nadaje — nie nadaje się. Ocena **2,0**, praca nie jest dopuszczana do obrony. Oceny pozytywne **3,0 — 5,0** muszą wiernie i rzetelnie oddawać stan pracy. Żadnego kompromisu w dół ("nie chcę być zbyt surowy") ani w górę ("szkoda studenta") względem rzeczywistej jakości.

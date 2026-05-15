# Rubryka oceny — jak defekty mapują się na ocenę

Skala AGH: 2,0 / 3,0 / 3,5 / 4,0 / 4,5 / 5,0.

## Filozofia

Statystyki WIMIIP 24/25: średnia opiekun 4,6 / recenzent 4,3-4,5. **Rozkład jest zbyt przesunięty w górę.** Skill ma oceniać uczciwie, nie "grzecznie". Ocena 5,0 jest zarezerwowana dla prac wybitnych, nie "dobrze wykonanych".

## Referencyjne kotwice

**5,0 (bardzo dobry)** — praca wybitna. Dla **mgr**: istotny element twórczy, samodzielne wnioskowanie, bibliografia z bieżącej literatury, wszystkie rozdziały domknięte, potencjał publikacyjny. Dla **inż**: realizacja problemu inżynierskiego na poziomie produkcyjnym, pełna weryfikacja, dokumentacja umożliwiająca reprodukcję, własne przemyślenia ponad wymagane minimum.

**4,5 (plus dobry)** — praca bardzo dobra, z drobnymi mankamentami. Cel zrealizowany w pełni. Struktura kompletna. Maksymalnie 2-3 drobne defekty niewpływające na wartość merytoryczną.

**4,0 (dobry)** — praca dobra. Cel zrealizowany. Widoczne mankamenty: płytsze wnioski, pominięte aspekty, luki w analizie — ale całość trzyma się merytorycznie.

**3,5 (plus dostateczny)** — praca z istotnymi brakami, która mimo to realizuje minimum wymagane dla stopnia. Np. słaba część weryfikacyjna, braki w literaturze, ale temat domknięty.

**3,0 (dostateczny)** — praca z poważnymi brakami. Cel zrealizowany tylko częściowo, duże luki strukturalne lub merytoryczne. Nadaje się na obronę, ale "na styk".

**2,0 (niedostateczny)** — praca nie spełnia wymagań stopnia studiów. Brak realizacji celu, plagiat / halucynacje AI jako dominujący element, brak wymaganych sekcji.

## Twarde reguły (sztywne progi)

Te reguły **nadpisują** ogólną ocenę — nie można ich obejść "bo poza tym praca jest niezła".

| Defekt | Maksymalna ocena |
| --- | --- |
| Mgr bez żadnej z 3 cech poszerzających (innowacja / pogłębiona analiza / szerszy kontekst) | **4,0** |
| Mgr bez samodzielnych wniosków autora (wnioski = przepisanie z literatury lub oczywistości) | **4,0** |
| Brak rozdziału "Wykorzystanie narzędzi GenAI" (inż i mgr) | odjęcie **0,5** |
| Wykryte halucynowane pozycje bibliograficzne (fałszywe DOI, nieistniejące tytuły) | **3,0** |
| Masowe halucynacje (≥5 fałszywych pozycji) | **2,0** |
| Brak części weryfikacyjnej (inż lub mgr) | **3,5** |
| Cel pracy nie jest zrealizowany (rozjazd cel–wnioski) | **3,5** |
| Brak uzasadnienia wyboru metody / technologii | odjęcie **0,5** |
| Mgr z mniej niż 10 prawidłowymi pozycjami bibliograficznymi (książki, artykuły, raporty, standardy, prace naukowe / doktoraty / mgr / inż, dane publiczne — po odrzuceniu dokumentacji / blogów / stron WWW) | odjęcie **0,5** |
| Inż z całkowitym brakiem bibliografii (0-2 pozycje) | odjęcie **0,5** |
| Pozycje w bibliografii, które powinny być w przypisach dolnych (dokumentacja, blogi, zwykłe strony WWW) | odjęcie **0,3** (defekt redakcyjny) |
| Praca mgr < 35 stron lub inż < 15 stron | odjęcie **0,5** |
| Oczywisty plagiat lub kopiowanie bez cytowania | **2,0** |

## Algorytm propozycji oceny

1. Zacznij od oceny wyjściowej **4,5** (nie 5,0 — 5,0 wymaga pozytywnego uzasadnienia).
2. Dla każdego defektu z listy twardych reguł zastosuj regułę (cap lub odjęcie).
3. Za każdy z trzech problemów WIMIIP zidentyfikowany w pracy odejmij **0,3**:
   - niedostosowanie poziomu do stopnia (jeśli nie trafiło już w twarde reguły),
   - ślady halucynacji AI niewynikające z bibliografii (wygenerowane wykresy, zmyślone dane),
   - pobieżne traktowanie części analitycznej lub weryfikacyjnej.
4. Zaokrąglij do najbliższej wartości ze skali AGH (3,0 / 3,5 / 4,0 / 4,5 / 5,0).
5. Żeby uzyskać 5,0 — oprócz braku defektów potrzebny jest **pozytywny sygnał wybitności**: coś, co w recenzji trzeba nazwać po imieniu ("element twórczy: autorski algorytm X", "samodzielne wnioskowanie: hipoteza Y zweryfikowana eksperymentalnie"). Bez takiego sygnału maksymalna ocena to 4,5.

## Zasada uzasadnienia

Każda wartość inna niż 5,0 wymaga w recenzji **konkretnego wskazania** defektów ze stronami. "Praca dobra, ocena 4,0" bez uzasadnienia jest sama w sobie pobieżną recenzją — jednym z problemów WIMIIP. Recenzja wygenerowana przez skill zawsze wymienia, co obniżyło ocenę i gdzie to widać.

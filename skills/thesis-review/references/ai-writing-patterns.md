# Wzorce pisania przez AI — do unikania w recenzji i wykrywania w pracy

Ten plik pełni **dwie funkcje**:

1. **Filtr stylu** — recenzja napisana przez skill nie może zawierać tych wzorców. Tekst w stylu AI natychmiast rzuca cień na recenzenta.
2. **Detektor** — subagent `ai-pattern-detector` szuka tych wzorców w pracy dyplomowej. Ich obecność (zwłaszcza niezadeklarowana w rozdziale GenAI) jest sygnałem do obniżenia oceny za samodzielność.

Oparte na Wikipedia:Signs_of_AI_writing, dostosowane do języka polskiego i do polskiego stylu akademickiego.

## 1. Frazy-sygnały (czerwone flagi)

Nadreprezentowane w tekstach generowanych przez LLM po polsku:

| Fraza | Dlaczego podejrzana |
| --- | --- |
| "warto podkreślić", "warto zauważyć" | sztuczne kierowanie uwagi bez treści |
| "należy zauważyć", "należy zaznaczyć" | filler bez informacji |
| "w dzisiejszych czasach", "w obecnej erze" | pusty otwieracz |
| "w dynamicznie zmieniającym się świecie" | klasyczny filler LLM |
| "stanowi świadectwo", "jest świadectwem" | patetyczne |
| "gra kluczową rolę", "odgrywa kluczową rolę" | klisza |
| "holistyczne podejście" | LLM uwielbia |
| "zagłębić się" (w temat / analizę) | bezpośrednie tłumaczenie z "delve into" |
| "fascynujący", "ekscytujący" (o zagadnieniu technicznym) | nieformalny zachwyt |
| "wpisuje się w szerszy kontekst" | filler |
| "stanowi kamień milowy" | patos |
| "krajobraz [czegoś]" (IT / technologii) | tłumaczenie z "landscape" |
| "kluczowy / krytyczny / fundamentalny" (piętrzone) | inflacja emfazy |

## 2. Konstrukcje interpretacyjno-puste

LLM doklejają interpretację do obserwacji strukturą „obserwacja + co świadczy o Y". Ludzki ekspert pisze prosto: „obserwacja. Powód." albo „obserwacja. Wniosek."

Do unikania:
- "co świadczy o..."
- "co wskazuje na..."
- "co dowodzi..."
- "co potwierdza..."
- "co stanowi o..."
- "co przekłada się na..."
- "co znajduje odzwierciedlenie w..."
- "co przejawia się w..."
- "co podkreśla..."

Przykład **źle (AI-style)**: *"Autor zastosował algorytm k-means, co świadczy o znajomości podstawowych metod klasteryzacji."*

Przykład **dobrze**: *"Autor zastosował algorytm k-means. Dla tego zbioru danych DBSCAN byłby adekwatniejszy — zob. s. 34, gdzie widać wyraźne klastry o różnej gęstości."* — konkret z uzasadnieniem.

## 3. Otwieracze akapitów

LLM otwiera akapity wedle stałego zestawu. Seryjne powtarzanie tych słów na początku zdań to sygnał.

- "Dodatkowo," / "Ponadto," / "Co więcej,"
- "Istotnie,"
- "W związku z powyższym,"
- "Podsumowując,"
- "Z drugiej strony," (gdy nie było pierwszej)

Jedno wystąpienie jest OK. Trzy w rzędu na początku akapitów — sygnał.

## 4. Konstrukcje stylistyczne

- **"nie tylko X, ale także Y"** — używane seryjnie, LLM jest od tego uzależnione.
- **Potrójność rytmiczna** — "szybki, niezawodny i skalowalny" wszędzie, gdzie tylko można to zmieścić.
- **Wariacja synonimiczna** — w kolejnych zdaniach ten sam obiekt raz jest "systemem", raz "rozwiązaniem", raz "aplikacją", raz "narzędziem", żeby uniknąć powtórzeń. Ludzie powtarzają słowa.
- **Formy bezosobowe piętrzone** — "zostało zrealizowane", "zostało zastosowane", "zostało zaimplementowane" w każdym akapicie. Naturalny polski miesza strony.
- **Puste pochwały** — "imponujący", "kompleksowy", "dogłębny" bez konkretu.

## 5. Typografia i formatowanie

- **Myślnik długi (—)** w środku zdania zamiast przecinka lub nawiasów. LLM lubi. W polskim akademickim — zwykle przecinek.
- **Pogrubianie** każdego wystąpienia terminu kluczowego.
- **Tytuły sekcji w stylu** "Wprowadzenie do Zagadnienia: Kluczowe Aspekty" (Title Case po polsku — nienaturalne).
- **Emoji i emotikony** w tekście technicznym.
- **Listy z pogrubionymi nagłówkami w każdym punkcie** — gdy treść każdego punktu to pół zdania.

## 6. Bibliografia — sygnały halucynacji

Agent literaturowy szuka:
- DOI, który nie resolvuje (404).
- Tytuł + autor niezgodne z rzeczywistym tytułem pod tym DOI.
- Data publikacji nierealna (np. artykuł 2025 cytowany w pracy oddanej w 2024).
- "Nazwiska-worki" — autorzy z imieniem i inicjałem, który brzmi uniwersalnie (J. Smith, A. Kowalski) w wielu cytowaniach.
- Czasopisma nieistniejące lub fałszywe.
- Brak stron w cytowaniach ("s. ??") lub podejrzanie okrągłe numery (s. 100, 200, 300).
- Cytowania odnoszące się do stron nieistniejących w źródle.
- Cytowania prywatnych repozytoriów GitHub bez podania commitu lub daty.
- **Odwołanie do literatury, która istnieje, ale treściowo nie pasuje do kontekstu, w którym została użyta** — student (lub LLM) podpiera twierdzenie cytatem, który w źródle mówi o czymś zupełnie innym. To klasyczna halucynacja "miękka": formalnie pozycja istnieje, DOI się zgadza, ale autor źródła nigdy nie pisał tego, co mu się przypisuje. Wykrycie wymaga przeczytania (choćby streszczenia) cytowanego źródła i porównania z miejscem, w którym zostało przywołane.

## 7. Wykrywanie w pracy — co raportuje subagent

Subagent `ai-pattern-detector` zwraca raport w formacie:

```json
{
  "summary": "High / Medium / Low suspicion of AI-generated text",
  "lexical_signals": [
    {"phrase": "warto zauważyć", "count": 7, "pages": [12, 15, 18, 23, 27, 31, 42]}
  ],
  "structural_signals": [
    {"pattern": "parallel tricolons in conclusions", "pages": [45, 46]}
  ],
  "bibliographic_signals": [
    {"entry": "[17]", "issue": "DOI 10.xxxx/... not found"}
  ],
  "declared_vs_observed": "Student zadeklarował użycie ChatGPT do tłumaczeń; styl rozdziału 3 sugeruje pełne generowanie.",
  "confidence": "medium"
}
```

Raport wchodzi do sekcji "samodzielność" w recenzji / opinii.

## 8. Co NIE jest sygnałem AI

Aby nie generować fałszywych alarmów:

- Pojedyncze wystąpienie dowolnej z powyższych fraz — szum, nie sygnał.
- Formalny styl akademicki to nie AI — akademicy też piszą bezosobowo, tylko bardziej różnorodnie.
- Używanie LaTeXa, dobrej typografii, konsekwentnych przypisów — to sygnał staranności, nie AI.
- Wystąpienie terminów technicznych w liczbach mnogich — normalne w informatyce.

**Siłę sygnału ocenia się klastrem** — kilka wzorców razem, w wysokim zagęszczeniu, zwłaszcza w rozdziałach, które student deklaruje jako własne, plus halucynacje w bibliografii = silny sygnał. Pojedyncza fraza = zero wniosków.

# Raport: diagnostyka predykcyjna maszyn wirujących

## 1. Wykrywanie zużycia łożysk

Analiza obwiedni sygnału drgań pozwala wykryć defekt bieżni zewnętrznej średnio
**31 dni** przed pierwszym alarmem temperaturowym (Nowak 2023).

Nowak (2023) monitorował 14 przekładni przemysłowych przez 18 miesięcy.
Sygnał próbkowano z częstotliwością 25,6 kHz, a przed transformatą Hilberta
stosowano filtr pasmowoprzepustowy 2-8 kHz.

Dla defektów bieżni wewnętrznej czas wyprzedzenia był krótszy i wyniósł 12 dni
(Nowak 2023). W 2 z 14 badanych jednostek defekt nie rozwinął się w oknie obserwacji.

Żadne ze źródeł nie ocenia przemysłowych protokołów fieldbus jako medium transportu
danych diagnostycznych.

## 2. Analiza oleju

Próbkę reprezentatywną należy pobierać **za filtrem z linii tłocznej** (Schmidt 2024).

Pobór w niewłaściwym punkcie zaniża kod czystości ISO 4406 nawet o dwie klasy
(Schmidt 2024). Średnia rozbieżność między dwoma lokalizacjami wyniosła 1,8 klasy ISO
przy 60 parach próbek.

Pobór ze zbiornika jest odradzany — osiadłe cząstki zaniżają wynik zliczania.

Stanowisko testowe Schmidta pracowało pod ciśnieniem 210 bar.

## 3. Bibliografia

1. **Nowak, A.; Lewandowski, P.** (2023). Early detection of rolling-element bearing
   wear via vibration envelope analysis. *Journal of Machine Diagnostics* 41.
   DOI: 10.1016/j.jmd.2023.04.011
2. **Schmidt, K.** (2024). Sampling-point selection for particle counting in hydraulic
   systems. *Tribology International* 189. DOI: 10.1016/j.triboint.2024.109421

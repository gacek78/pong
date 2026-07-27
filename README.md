# Pong

Klasyczny Pong w [pygame](https://www.pygame.org/) — z komputerem na trzech poziomach
trudności albo we dwoje przy jednej klawiaturze. Gracz 1 może grać klawiaturą lub myszą.

Pole gry dopasowuje się do proporcji monitora (na 16:9 to 1280×720, na 4:3 — 960×720),
więc obraz wypełnia ekran bez czarnych pasów. Wszystkie rozmiary są ułamkami wysokości,
dzięki czemu gra wygląda tak samo w każdej rozdzielczości.

## Wymagania

- Python 3.11 lub nowszy
- `pygame` 2.6.1 (zob. `requirements.txt`)

## Instalacja

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Na Linuksie/macOS zamiast `.venv\Scripts\python.exe` użyj `.venv/bin/python`.

## Uruchamianie

Na Windowsie najprościej dwuklikiem w **`graj.bat`** — startuje od razu na pełnym ekranie,
korzystając z Pythona z lokalnego `.venv`.

Z konsoli:

```bash
.venv\Scripts\python.exe pong.py                 # okno, z menu wyboru przeciwnika
.venv\Scripts\python.exe pong.py --pelny-ekran   # od razu na pełnym ekranie
.venv\Scripts\python.exe pong.py --poziom 2      # od razu z komputerem, z pominięciem menu
.venv\Scripts\python.exe pong.py --mysz          # gracz 1 od startu steruje myszą
```

`--poziom` przyjmuje `1` (łatwy), `2` (średni) lub `3` (trudny). `--mysz` przydaje się
głównie razem z `--poziom`, bo wtedy menu (a w nim przełącznik sterowania) jest pomijane.

## Sterowanie

Gracz 1 gra klawiaturą albo myszą — wybór klawiszem `K` w menu, zapamiętywany do końca sesji.
W trybie myszy paletka podąża za kursorem 1:1, bez ograniczenia prędkości. Działa to także
w trybie dla dwojga (gracz 1 myszą, gracz 2 strzałkami).

Na czas rozgrywki kursor znika i zostaje przechwycony przez okno — inaczej wyjechałby bokiem
poza nie, a paletka zamarłaby w miejscu. Kursor wraca do systemu w pauzie (`Spacja`),
po zakończonym meczu i w menu.

| Klawisz | Działanie |
|---|---|
| `W` / `S` lub mysz | gracz 1 — lewa paletka |
| `↑` / `↓` | gracz 2 — prawa paletka (w trybie dla dwojga) |
| `1`–`4` | wybór w menu: komputer łatwy/średni/trudny albo dwoje graczy |
| `K` | w menu: przełącza sterowanie gracza 1 (klawiatura ↔ mysz) |
| `Spacja` | pauza |
| `R` | nowa gra po zakończonym meczu |
| `M` | powrót do menu po zakończonym meczu |
| `F11` lub `Alt`+`Enter` | pełny ekran |
| `Esc` | wyjście z pełnego ekranu, a w oknie — zamknięcie gry |

Mecz trwa do 5 punktów. Piłka przyspiesza z każdym odbiciem od paletki (do ustalonego
limitu), a kąt odbicia zależy od tego, w które miejsce paletki trafi.

## Poziomy komputera

Komputer nie „teleportuje się" na wysokość piłki — taki przeciwnik byłby nie do pokonania.
Zamiast tego ma ograniczoną prędkość paletki i martwą strefę, czyli tolerancję, poniżej
której nie reaguje. Parametry siedzą w słowniku `POZIOMY` w `pong.py`:

| Poziom | Prędkość paletki | Martwa strefa |
|---|---|---|
| łatwy | 0,55× gracza | 0,45 wysokości paletki |
| średni | 0,85× | 0,25 |
| trudny | 1,05× | 0,10 |

## Autotest

Gra ma wbudowany tryb testowy — przelatuje 1800 klatek bez otwierania okna, sterując
prawą paletką komputerem, a lewą zostawiając nieruchomo na środku.

```bash
SDL_VIDEODRIVER=dummy .venv\Scripts\python.exe pong.py --autotest
```

W PowerShellu: `$env:SDL_VIDEODRIVER = 'dummy'` w osobnej linii przed poleceniem.
Domyślnie testuje poziom średni; `--poziom 1|3` sprawdza pozostałe.

Wynik przy powodzeniu:

```
autotest OK: 1800 klatek, komputer zdobyl 5 pkt, ostatni wynik 0:0
```

Sprawdzane są cztery warunki — trzy niezmienniki po każdej klatce i jeden na końcu:

| Warunek | Co wyłapuje |
|---|---|
| piłka nie zachodzi na żadną paletkę | zakleszczenie piłki wewnątrz paletki |
| piłka mieści się w polu w pionie | ucieczka poza górną lub dolną krawędź |
| paletka komputera mieści się w polu | brak ograniczenia ruchu AI |
| komputer zdobył co najmniej jeden punkt | AI, które przestało trafiać w piłkę |

Ostatni warunek liczy **dorobek całego przebiegu**, a nie wynik bieżącego meczu. Ma to
znaczenie, bo test restartuje mecz po każdej wygranej, żeby przez całe 1800 klatek ćwiczyć
rozgrywkę — a restart zeruje tablicę wyników. Dlatego w komunikacie widać dwie liczby:
łączny dorobek komputera i wynik meczu trwającego w chwili zakończenia testu. Przykład
wyżej (`5 pkt` przy stanie `0:0`) to normalny przebieg, w którym komputer wygrał mecz
do pięciu tuż przed ostatnią klatką.

To najszybszy sposób sprawdzenia regresji po zmianie logiki gry.

## Uwaga o `graj.bat`

Plik musi mieć zakończenia linii **CRLF** — `cmd.exe` źle parsuje pliki wsadowe
zapisane z samymi LF. Pilnuje tego `.gitattributes` (`*.bat text eol=crlf`).

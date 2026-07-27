# Pong

Klasyczny Pong w [pygame](https://www.pygame.org/) — z komputerem na trzech poziomach
trudności albo we dwoje przy jednej klawiaturze.

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
```

`--poziom` przyjmuje `1` (łatwy), `2` (średni) lub `3` (trudny).

## Sterowanie

| Klawisz | Działanie |
|---|---|
| `W` / `S` | gracz 1 — lewa paletka |
| `↑` / `↓` | gracz 2 — prawa paletka (w trybie dla dwojga) |
| `1`–`4` | wybór w menu: komputer łatwy/średni/trudny albo dwoje graczy |
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
| łatwy | 0,60× gracza | 0,45 wysokości paletki |
| średni | 0,85× | 0,25 |
| trudny | 1,05× | 0,10 |

## Autotest

Gra ma wbudowany tryb testowy — przelatuje 1800 klatek bez otwierania okna i asercjami
pilnuje niezmienników: piłka nie utyka w paletce, nie ucieka poza pole w pionie, paletka
komputera nie wyjeżdża poza ekran, a komputer zdobywa punkty przeciw nieruchomemu graczowi.

```bash
SDL_VIDEODRIVER=dummy .venv\Scripts\python.exe pong.py --autotest
```

W PowerShellu: `$env:SDL_VIDEODRIVER = 'dummy'` w osobnej linii przed poleceniem.

To najszybszy sposób sprawdzenia regresji po zmianie logiki gry.

## Uwaga o `graj.bat`

Plik musi mieć zakończenia linii **CRLF** — `cmd.exe` źle parsuje pliki wsadowe
zapisane z samymi LF. Pilnuje tego `.gitattributes` (`*.bat text eol=crlf`).

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Uruchamianie

`pygame` **nie jest** w globalnym Pythonie — wszystko idzie przez `.venv`. Dwuklik w `pong.py`
nie zadziała.

```bash
.venv\Scripts\python.exe pong.py                 # okno, menu wyboru przeciwnika
.venv\Scripts\python.exe pong.py --pelny-ekran   # od razu pelny ekran (tak startuje graj.bat)
.venv\Scripts\python.exe pong.py --poziom 2      # pomija menu, od razu z komputerem
.venv\Scripts\python.exe pong.py --mysz          # gracz 1 od startu steruje mysza
```

## Test

Jedyny test to wbudowany autotest — brak pytest, brak katalogu `tests/`.

```bash
SDL_VIDEODRIVER=dummy .venv\Scripts\python.exe pong.py --autotest            # poziom sredni
SDL_VIDEODRIVER=dummy .venv\Scripts\python.exe pong.py --autotest --poziom 1 # wybrany poziom
```

Przelatuje 1800 klatek bez okna, sterując prawą paletką komputerem i zostawiając lewą
nieruchomo. Trzy asercje niezmienników po każdej klatce (piłka nie zachodzi na paletkę,
mieści się w polu w pionie, paletka AI nie wyjeżdża) plus warunek końcowy. Uruchamiać po
każdej zmianie logiki gry.

Do weryfikacji wizualnej: renderuj headless i zapisz `pygame.image.save(pygame.display.get_surface(), ...)`
z osobnego wątku po ~2 s, potem obejrzyj PNG — szybsze niż proszenie użytkownika o zrzut.
Na `dummy` proporcja ekranu wychodzi 4:3 (pole 960×720), na prawdziwym monitorze 16:9 (1280×720).

## Architektura

Cały projekt to jeden plik `pong.py` (~320 linii) bez klas: kilka czystych funkcji plus
monolityczna pętla gry w `main()`. Nie rozbijać tego na moduły bez wyraźnej prośby.

**Wymiary są globalne i ustawiane raz** przez `ustaw_wymiary(proporcja)` z proporcji monitora.
`WYSOKOSC` to zawsze 720, `SZEROKOSC` liczona z proporcji, więc obraz wypełnia ekran bez
czarnych pasów. Wszystkie rozmiary i prędkości są ułamkami `WYSOKOSC` — **nigdy nie wpisywać
stałych pikselowych**, rozjadą się na innym ekranie. Okno działa w trybie `SCALED | RESIZABLE`,
więc logika żyje w stałej rozdzielczości, a pygame skaluje obraz.

**Stany gry** to nie maszyna stanów, tylko flagi lokalne w `main()`: `w_menu`, `pauza`,
`zwyciezca`, `rozpocznij_mecz`, `poziom_ai` (`None` = drugą paletką steruje człowiek),
`mysz` (sterowanie gracza 1; przełączane klawiszem `K` w menu, domyślnie klawiatura).
Gałąź menu kończy się `continue`, więc logika rozgrywki jej nie dotyczy.

**Sterowanie myszą** to jedna linia: `paletka1.centery = pygame.mouse.get_pos()[1]` — w trybie
`SCALED` pygame podaje pozycję kursora już w logicznej rozdzielczości, więc nic nie przeliczamy,
a `clamp_ip(obszar)` pilnuje krawędzi. Konieczne jest przy tym `pygame.event.set_grab(True)`
na czas rozgrywki: bez przechwycenia kursor wyjeżdża bokiem poza okno, gra przestaje dostawać
jego pozycję i paletka zamiera (potwierdzone w grze). Grab i ukrycie kursora liczy jedna flaga
`chwyc_mysz` przed rysowaniem — w pauzie i po meczu kursor musi wrócić do systemu, inaczej nie
da się przełączyć na inne okno. Ruch jest 1:1, bez limitu prędkości — świadomie, bo o to
chodzi w Pongu na myszy. Domyślne `mysz = False` jest **konieczne dla autotestu**: na sterowniku
`dummy` nie ma kursora, `get_pos()` zwraca (0, 0) i lewa paletka wjechałaby na górę zamiast stać
nieruchomo. Z tego samego powodu `pygame.mouse.set_pos()` nie działa na `dummy` — chcąc
przetestować mysz headless, trzeba podmienić `pygame.mouse.get_pos`.

### Model prędkości piłki

Nieoczywisty i łatwo go zepsuć przy „drobnej" korekcie:

- Pozioma prędkość rośnie o `PRZYSPIESZENIE` (5%) **tylko przy odbiciu od paletki**, z sufitem
  `MAX_PREDKOSC_PILKI`. Od startowych 6 px/klatkę do sufitu 14,4 trzeba ~18 odbić.
- Odbicia od góry i dołu **nie zmieniają wartości** prędkości, tylko znak składowej pionowej.
- Pionowa prędkość **nie jest zachowywana** — `odbij_od_paletki()` nadpisuje ją przy każdym
  odbiciu wzorem `|vx| × odchylenie`, gdzie `odchylenie` (−1…1) mówi, jak daleko od środka
  paletki trafiła piłka. Trafienie środkiem → lot poziomy, krawędzią → 45°. To stąd bierze się
  wrażenie, że piłka „zwolniła", choć vx właśnie urosło.
- Punkt resetuje prędkość do startowej (`reset_pilki()`); nie ma żadnego wytracania.

### Trudność komputera

Słownik `POZIOMY`: nazwa, mnożnik prędkości paletki, martwa strefa (ułamek wysokości paletki).
Martwa strefa to tolerancja, poniżej której AI nie reaguje. **Próg 0,50 jest jakościowy** — poniżej
AI zdąży dotknąć piłki krawędzią paletki, powyżej zaczyna realnie przepuszczać. Chcąc zmienić
trudność, ruszać tych dwóch liczb, nie logiki `ruch_komputera()`.

Uwaga na ziarnistość: prędkość przechodzi przez `round()`, więc mnożniki 0,45 i 0,50 dają ten sam
wynik (6 px/klatkę). Sprawdzać efekt liczbowo, nie zakładać.

## Pułapki potwierdzone w praktyce

- **`graj.bat` musi mieć CRLF.** `cmd.exe` źle parsuje pliki wsadowe z samymi LF — objawia się
  echem treści skryptu i odpaleniem gałęzi błędu mimo kodu wyjścia 0. Pilnuje tego `.gitattributes`
  (`*.bat text eol=crlf`). Nie wprowadzać w tym pliku wieloliniowych bloków `if ( … )`.
- **`toggle_fullscreen()` rzuca `pygame.error` na sterowniku `dummy`.** Dlatego
  `przelacz_pelny_ekran()` zwraca `bool`, a gałąź ESC zamyka grę, gdy przełączenie zawiodło —
  bez tego ESC staje się martwym klawiszem i gry nie da się zamknąć. Nie upraszczać tego z powrotem.
- **Pętla gry używa `tick_busy_loop()`, nie `tick()`.** Zwykły `tick()` opiera się na `SDL_Delay`
  i przy granulacji timera Windows gubi klatki: zmierzone 8,8% klatek dłuższych niż 20 ms (ogon
  do 26 ms) przy oczekiwanych 16,7 ms. `tick_busy_loop()` zbija to do 0,6%. Widać to dopiero przy
  sterowaniu myszą, bo pozycja jest bezwzględna — zgubiona klatka to zatrzymanie paletki i skok,
  podczas gdy przyrostowy ruch klawiaturą ją maskuje. Kosztem jest zajęty rdzeń (busy-wait);
  w menu został zwykły `tick()`, bo statyczny ekran nie potrzebuje równego rytmu.
  Vsync tu nie pomoże — pomiar pokazał, że jest wyłączony (bez limitu gra kręci ~265 FPS).
- **Autotest asertuje `punkty2_lacznie`, nie `punkty2`.** Test restartuje mecz po każdej wygranej,
  co zeruje `punkty2`; asercja na nim była niestabilna w ~15% przebiegów. Licznik łączny nie może
  być zerowany przy restarcie.

## Konwencje

- Komentarze, docstringi i komunikaty commitów po polsku.
- **Teksty renderowane na ekranie i zawartość `graj.bat` — bez polskich znaków diakrytycznych**
  („latwy", „wygral", „wyjscie"). Docstringi i komentarze w kodzie mogą mieć diakrytyki.
- README opisuje sterowanie, poziomy trudności i autotest — przy zmianie tych rzeczy
  aktualizować go razem z kodem, bo tabele zawierają konkretne liczby ze słownika `POZIOMY`.

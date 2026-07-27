"""Pong — z komputerem albo we dwoje.

Po starcie menu pozwala wybrać przeciwnika: komputer (trzy poziomy) lub drugi gracz.

Sterowanie: W/S — gracz 1 (lewa paletka), strzałki góra/dół — gracz 2 (prawa paletka).
Spacja — pauza, R — nowa gra po zakończonym meczu, M — powrót do menu,
F11 (lub Alt+Enter) — pełny ekran, ESC — wyjście z pełnego ekranu, a w oknie zamknięcie gry.

Uruchomienie z opcją --pelny-ekran startuje od razu na pełnym ekranie.
"""

import random
import sys

import pygame

# --- stałe niezależne od rozdzielczości ---
BAZOWA_WYSOKOSC = 720        # logiczna wysokość pola gry; szerokość liczona z proporcji ekranu
PRZYSPIESZENIE = 1.05        # piłka przyspiesza z każdym odbiciem od paletki
FPS = 60
PUNKTY_DO_WYGRANEJ = 5
KLATEK_AUTOTESTU = 1800

BIALY = (255, 255, 255)
CZARNY = (0, 0, 0)
SZARY = (80, 80, 80)

# Poziomy komputera: nazwa, mnoznik predkosci paletki, martwa strefa (ulamek wysokosci paletki).
# Martwa strefa to tolerancja, ponizej ktorej komputer nie reaguje — im wieksza, tym bardziej
# niemrawy przeciwnik. Na latwym komputer jest wolniejszy od gracza, na trudnym minimalnie szybszy.
POZIOMY = {
    1: ("latwy", 0.55, 0.45),
    2: ("sredni", 0.85, 0.25),
    3: ("trudny", 1.05, 0.10),
}

# --- wymiary pola gry, ustawiane raz przez ustaw_wymiary() ---
SZEROKOSC = WYSOKOSC = 0
SZER_PALETKI = WYS_PALETKI = ROZMIAR_PILKI = 0
PREDKOSC_PALETKI = 0
PREDKOSC_PILKI = MAX_PREDKOSC_PILKI = 0.0


def ustaw_wymiary(proporcja):
    """Dopasowuje pole gry i rozmiary elementów do proporcji ekranu (szerokość/wysokość).

    Dzięki temu obraz wypełnia cały monitor, bez czarnych pasów po bokach — na 16:9
    pole gry to 1280x720, na 4:3 960x720. Wszystkie rozmiary są ułamkami wysokości,
    więc gra wygląda tak samo niezależnie od rozdzielczości.
    """
    global SZEROKOSC, WYSOKOSC, SZER_PALETKI, WYS_PALETKI, ROZMIAR_PILKI
    global PREDKOSC_PALETKI, PREDKOSC_PILKI, MAX_PREDKOSC_PILKI

    WYSOKOSC = BAZOWA_WYSOKOSC
    SZEROKOSC = round(WYSOKOSC * proporcja)
    SZER_PALETKI = WYSOKOSC // 36
    WYS_PALETKI = WYSOKOSC // 6
    ROZMIAR_PILKI = WYSOKOSC // 36
    # paletka musi nadazac za pionowym ruchem piłki (do ok. 1.2 * MAX_PREDKOSC_PILKI)
    PREDKOSC_PALETKI = max(1, round(WYSOKOSC / 55))
    PREDKOSC_PILKI = WYSOKOSC / 120
    MAX_PREDKOSC_PILKI = WYSOKOSC / 50


def reset_pilki(kierunek):
    """Zwraca pozycję środkową i prędkość piłki (kierunek: -1 w lewo, 1 w prawo)."""
    pilka_x = (SZEROKOSC - ROZMIAR_PILKI) / 2
    pilka_y = (WYSOKOSC - ROZMIAR_PILKI) / 2
    predkosc_y = PREDKOSC_PILKI * random.choice((-1, 1)) * random.uniform(0.4, 0.9)
    return pilka_x, pilka_y, PREDKOSC_PILKI * kierunek, predkosc_y


def odbij_od_paletki(pilka_x, pilka_y, paletka, predkosc_x):
    """Odbicie od paletki: piłka jest wypychana poza nią, a kąt zależy od miejsca trafienia."""
    if predkosc_x < 0:
        pilka_x = float(paletka.right)
    else:
        pilka_x = float(paletka.left - ROZMIAR_PILKI)
    predkosc_x = -predkosc_x * PRZYSPIESZENIE
    predkosc_x = max(-MAX_PREDKOSC_PILKI, min(MAX_PREDKOSC_PILKI, predkosc_x))
    odchylenie = (pilka_y + ROZMIAR_PILKI / 2 - paletka.centery) / (WYS_PALETKI / 2)
    return pilka_x, predkosc_x, abs(predkosc_x) * odchylenie


def ruch_komputera(paletka, pilka, predkosc_x, poziom):
    """Prowadzi prawą paletkę: goni piłkę, gdy ta leci w jej stronę, inaczej wraca na środek.

    Ograniczona prędkość i martwa strefa sprawiają, że komputer da się pokonać —
    idealny "teleport" na wysokość piłki byłby nie do przejścia.
    """
    _, mnoznik, martwa_strefa = POZIOMY[poziom]
    predkosc = max(1, round(PREDKOSC_PALETKI * mnoznik))
    cel = pilka.centery if predkosc_x > 0 else WYSOKOSC // 2
    roznica = cel - paletka.centery
    if abs(roznica) > WYS_PALETKI * martwa_strefa:
        paletka.y += predkosc if roznica > 0 else -predkosc


def przelacz_pelny_ekran():
    """Przelacza okno/pelny ekran. Zwraca False, gdy sterownik tego nie potrafi."""
    try:
        pygame.display.toggle_fullscreen()
        return True
    except pygame.error:
        return False


def rysuj_napis(ekran, czcionka, tekst, srodek):
    obraz = czcionka.render(tekst, True, BIALY)
    ekran.blit(obraz, obraz.get_rect(center=srodek))


def main(autotest=False, pelny_ekran=False, poziom=None):
    pygame.init()
    # pole gry dostaje proporcje monitora, wiec obraz wypelnia go w calosci
    ekran_info = pygame.display.Info()
    proporcja = ekran_info.current_w / ekran_info.current_h if ekran_info.current_h else 16 / 9
    ustaw_wymiary(proporcja)

    # SCALED: logika gry zostaje w stalej rozdzielczosci, a pygame skaluje obraz do rozmiaru
    # okna/ekranu. RESIZABLE pozwala dodatkowo rozciagnac okno myszka.
    tryb = pygame.SCALED | pygame.RESIZABLE
    if pelny_ekran:
        tryb |= pygame.FULLSCREEN
    ekran = pygame.display.set_mode((SZEROKOSC, WYSOKOSC), tryb)
    pygame.display.set_caption("Pong")
    obszar = pygame.Rect(0, 0, SZEROKOSC, WYSOKOSC)

    zegar = pygame.time.Clock()          # jeden zegar na całą grę, nie nowy co klatkę
    czcionka = pygame.font.Font(None, WYSOKOSC // 9)
    czcionka_mala = pygame.font.Font(None, WYSOKOSC // 26)

    # paletki przy samych krawedziach pola gry
    paletka1 = pygame.Rect(0, 0, SZER_PALETKI, WYS_PALETKI)
    paletka2 = pygame.Rect(SZEROKOSC - SZER_PALETKI, 0, SZER_PALETKI, WYS_PALETKI)
    paletka1.centery = paletka2.centery = WYSOKOSC // 2
    pilka_x, pilka_y, predkosc_x, predkosc_y = reset_pilki(random.choice((-1, 1)))
    pilka = pygame.Rect(pilka_x, pilka_y, ROZMIAR_PILKI, ROZMIAR_PILKI)

    punkty1 = punkty2 = 0
    punkty2_lacznie = 0    # dorobek prawej paletki z calego autotestu; punkty2 zeruje sie co mecz
    pauza = False
    zwyciezca = None
    klatka = 0
    poziom_ai = poziom or (2 if autotest else None)   # None = drugą paletką steruje człowiek
    w_menu = not autotest and poziom is None          # podany poziom pomija menu
    rozpocznij_mecz = False

    while True:
        for zdarzenie in pygame.event.get():
            if zdarzenie.type == pygame.QUIT:
                pygame.quit()
                return
            if zdarzenie.type == pygame.KEYDOWN:
                alt_enter = zdarzenie.key == pygame.K_RETURN and zdarzenie.mod & pygame.KMOD_ALT
                if zdarzenie.key == pygame.K_F11 or alt_enter:
                    przelacz_pelny_ekran()
                if zdarzenie.key == pygame.K_ESCAPE:
                    # w pelnym ekranie ESC najpierw z niego wychodzi, zeby nie zamknac gry przez
                    # pomylke; gdy sterownik nie umie przelaczyc trybu, ESC zamyka gre — inaczej
                    # nie dalo by sie wyjsc
                    if not (pygame.display.is_fullscreen() and przelacz_pelny_ekran()):
                        pygame.quit()
                        return

                if w_menu:
                    wybor = {pygame.K_1: 1, pygame.K_KP_1: 1,
                             pygame.K_2: 2, pygame.K_KP_2: 2,
                             pygame.K_3: 3, pygame.K_KP_3: 3}.get(zdarzenie.key)
                    if wybor:
                        poziom_ai = wybor
                        w_menu, rozpocznij_mecz = False, True
                    elif zdarzenie.key in (pygame.K_4, pygame.K_KP_4):
                        poziom_ai = None
                        w_menu, rozpocznij_mecz = False, True
                    continue

                if zdarzenie.key == pygame.K_SPACE and zwyciezca is None:
                    pauza = not pauza
                if zdarzenie.key == pygame.K_r and zwyciezca is not None:
                    rozpocznij_mecz = True
                if zdarzenie.key == pygame.K_m and zwyciezca is not None:
                    w_menu = True

        if rozpocznij_mecz:
            punkty1 = punkty2 = 0
            zwyciezca = None
            pauza = False
            rozpocznij_mecz = False
            paletka1.centery = paletka2.centery = WYSOKOSC // 2
            pilka_x, pilka_y, predkosc_x, predkosc_y = reset_pilki(random.choice((-1, 1)))
            pilka.topleft = (round(pilka_x), round(pilka_y))

        if w_menu:
            ekran.fill(CZARNY)
            rysuj_napis(ekran, czcionka, "PONG", (SZEROKOSC // 2, WYSOKOSC // 4))
            # legenda klawiszy jest tylko tutaj — ekran gry ma zostac czysty
            pozycje = ["1 - z komputerem (latwy)",
                       "2 - z komputerem (sredni)",
                       "3 - z komputerem (trudny)",
                       "4 - dwoje graczy",
                       "",
                       "gracz 1: W / S          gracz 2: strzalki gora / dol",
                       "spacja - pauza          F11 - pelny ekran",
                       "ESC - wyjscie"]
            for i, tekst in enumerate(pozycje):
                rysuj_napis(ekran, czcionka_mala, tekst,
                            (SZEROKOSC // 2, WYSOKOSC // 2 + i * WYSOKOSC // 16))
            pygame.display.flip()
            zegar.tick(FPS)
            continue

        if zwyciezca is None and not pauza:
            # --- ruch paletek (z ograniczeniem do ekranu) ---
            klawisze = pygame.key.get_pressed()
            if klawisze[pygame.K_w]:
                paletka1.y -= PREDKOSC_PALETKI
            if klawisze[pygame.K_s]:
                paletka1.y += PREDKOSC_PALETKI
            if poziom_ai is None:
                if klawisze[pygame.K_UP]:
                    paletka2.y -= PREDKOSC_PALETKI
                if klawisze[pygame.K_DOWN]:
                    paletka2.y += PREDKOSC_PALETKI
            else:
                ruch_komputera(paletka2, pilka, predkosc_x, poziom_ai)
            paletka1.clamp_ip(obszar)
            paletka2.clamp_ip(obszar)

            # --- ruch piłki ---
            pilka_x += predkosc_x
            pilka_y += predkosc_y

            # odbicie od góry i dołu: korekta pozycji + wymuszony znak prędkości,
            # dzięki czemu piłka nie może się "przykleić" do krawędzi
            if pilka_y <= 0:
                pilka_y = 0.0
                predkosc_y = abs(predkosc_y)
            elif pilka_y + ROZMIAR_PILKI >= WYSOKOSC:
                pilka_y = float(WYSOKOSC - ROZMIAR_PILKI)
                predkosc_y = -abs(predkosc_y)

            # odbicie od paletek — tylko gdy piłka faktycznie leci w ich stronę
            pilka.topleft = (round(pilka_x), round(pilka_y))
            if predkosc_x < 0 and pilka.colliderect(paletka1):
                pilka_x, predkosc_x, predkosc_y = odbij_od_paletki(pilka_x, pilka_y, paletka1, predkosc_x)
            elif predkosc_x > 0 and pilka.colliderect(paletka2):
                pilka_x, predkosc_x, predkosc_y = odbij_od_paletki(pilka_x, pilka_y, paletka2, predkosc_x)
            pilka.topleft = (round(pilka_x), round(pilka_y))

            # --- punktacja ---
            if pilka.right < 0:
                punkty2 += 1
                punkty2_lacznie += 1
                pilka_x, pilka_y, predkosc_x, predkosc_y = reset_pilki(1)
                pilka.topleft = (round(pilka_x), round(pilka_y))
            elif pilka.left > SZEROKOSC:
                punkty1 += 1
                pilka_x, pilka_y, predkosc_x, predkosc_y = reset_pilki(-1)
                pilka.topleft = (round(pilka_x), round(pilka_y))

            if punkty1 >= PUNKTY_DO_WYGRANEJ:
                zwyciezca = 1
            elif punkty2 >= PUNKTY_DO_WYGRANEJ:
                zwyciezca = 2

        # --- rysowanie ---
        ekran.fill(CZARNY)
        kreska = WYSOKOSC // 40
        for y in range(0, WYSOKOSC, kreska * 2):
            pygame.draw.rect(ekran, SZARY, (SZEROKOSC // 2 - 2, y, 4, kreska))
        pygame.draw.rect(ekran, BIALY, paletka1)
        pygame.draw.rect(ekran, BIALY, paletka2)
        if zwyciezca is None:
            pygame.draw.rect(ekran, BIALY, pilka)
        rysuj_napis(ekran, czcionka, f"{punkty1}   {punkty2}", (SZEROKOSC // 2, WYSOKOSC // 12))

        if zwyciezca is not None:
            zwyciezca_opis = "Komputer" if zwyciezca == 2 and poziom_ai else f"Gracz {zwyciezca}"
            rysuj_napis(ekran, czcionka, f"{zwyciezca_opis} wygral!", (SZEROKOSC // 2, WYSOKOSC // 2))
            rysuj_napis(ekran, czcionka_mala, "R - nowa gra, M - menu, ESC - wyjscie",
                        (SZEROKOSC // 2, WYSOKOSC // 2 + WYSOKOSC // 10))
        elif pauza:
            rysuj_napis(ekran, czcionka, "PAUZA", (SZEROKOSC // 2, WYSOKOSC // 2))

        pygame.display.flip()
        zegar.tick(0 if autotest else FPS)   # w autoteście bez limitu klatek

        if autotest:
            assert not (pilka.colliderect(paletka1) or pilka.colliderect(paletka2)), \
                f"pilka utknela w paletce w klatce {klatka}: {pilka}"
            assert 0 <= pilka.top and pilka.bottom <= WYSOKOSC, \
                f"pilka wyszla poza ekran w pionie w klatce {klatka}: {pilka}"
            assert obszar.contains(paletka2), \
                f"paletka komputera wyjechala poza ekran w klatce {klatka}: {paletka2}"
            if zwyciezca is not None:
                rozpocznij_mecz = True    # kolejny mecz, zeby test caly czas cwiczyl rozgrywke
            klatka += 1
            if klatka >= KLATEK_AUTOTESTU:
                assert punkty2_lacznie > 0, \
                    f"komputer nie zdobyl ani punktu przeciw nieruchomej paletce w {klatka} klatkach"
                print(f"autotest OK: {klatka} klatek, komputer zdobyl {punkty2_lacznie} pkt, "
                      f"ostatni wynik {punkty1}:{punkty2}")
                pygame.quit()
                return


if __name__ == "__main__":
    # --poziom 1|2|3 startuje od razu z komputerem, z pominieciem menu
    wybrany = None
    if "--poziom" in sys.argv:
        wybrany = int(sys.argv[sys.argv.index("--poziom") + 1])
        if wybrany not in POZIOMY:
            sys.exit(f"--poziom musi byc jednym z: {', '.join(map(str, POZIOMY))}")
    main(autotest="--autotest" in sys.argv,
         pelny_ekran="--pelny-ekran" in sys.argv,
         poziom=wybrany)

@echo off
rem Uruchamia Ponga Pythonem z lokalnego venv (tam jest zainstalowany pygame).
cd /d "%~dp0"
rem Start od razu na pelnym ekranie; ESC lub F11 wraca do okna.
".venv\Scripts\python.exe" pong.py --pelny-ekran
rem Okno zostaje otwarte tylko przy bledzie, zebys mogl przeczytac komunikat.
if errorlevel 1 pause

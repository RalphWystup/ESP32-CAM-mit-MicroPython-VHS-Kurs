@echo off
rem ===========================================================================================================
rem  VHS-Kurs "ESP32-CAM und ESP32 mit MicroPython"  --  die EINE Batch-Datei: installieren, Thonny starten, Programm testen  (ESP32_Start.bat, Fassung 1.7)
rem  Autor: Prof. Dr.-Ing. Ralph Wystup M.Sc.  -  erstellt mit KI und Agent (Claude Code, Anthropic)  -  Fassung 1.7 vom 24.11.2026
rem  1.7: Auswahl kommt sofort (sein Wort: "die auswahl soll gleich kommen"); Schutzmantel: das Fenster bleibt bei jedem Fehler offen (sein Wort: "so was bitte
rem       sicher abfangen"); Fehler der 1.6 behoben: eine Klammer im Meldungstext innerhalb eines Klammerblocks liess cmd die ganze Datei abbrechen
rem       ("cmd flasch nur kurz auf") -- darum hier keine Klammerbloecke mehr, nur goto und call.
rem  1.6: eine Batch-Datei oben; 1.5: Handauswahl des Anschlusses; 1.4: Bewegungsmelder; 1.3: gemeinsame Seite esp_kurs_installation_1.2.py;
rem  1.2: laeuft von allein durch, PC-Einrichtung 1.7 ohne Internet; 1.1: Name statt Nummer
rem -----------------------------------------------------------------------------------------------------------
rem  Sein Wort: Ordner kopieren, fabrikfrisches Brett an USB, Batch starten -- sonst nichts.
rem  Auswahl 1: Fehlen Thonny-Python, pyserial oder esptool, laeuft zuerst Werkzeuge\PC_einrichten\1_PC_einrichten_1.7.bat (installiert nur, was fehlt;
rem             Windows fragt fuer den USB-Treiber einmal nach Administratorrechten). Dann startet Werkzeuge\esp_kurs_installation_1.2.py
rem             (Webserver nur auf diesem PC, http://127.0.0.1:8765/) und oeffnet die Seite im Browser. Fenster offen lassen, solange installiert wird.
rem  Auswahl 2: Werkzeuge\Thonny_starten.bat   Auswahl 3: Werkzeuge\Programm_testen.bat
rem ===========================================================================================================
if "%~1"=="innen" goto innen
rem --- Schutzmantel: der eigentliche Ablauf laeuft in einem eigenen cmd; was auch passiert, dieses Fenster bleibt offen ---
cmd /c ""%~f0" innen"
echo.
echo ---------------------------------------------------------------------------
echo  Fenster schliessen mit einer beliebigen Taste.
pause >nul
exit /b

:innen
setlocal
title ESP32 Start
set "VONSTART=1"
set "BRETT="
if exist "%~dp0Werkzeuge\brett.txt" set /p BRETT=<"%~dp0Werkzeuge\brett.txt"
set "VORGABE=1"
if defined BRETT set "VORGABE=2"
echo.
echo  VHS-Kurs ESP32 und ESP32-CAM mit MicroPython -- was soll geschehen?
echo.
echo    1 = Brett installieren    -- beim ersten Mal, und fuer jedes weitere Brett
echo    2 = Thonny starten        -- mit dem installierten Brett arbeiten
echo    3 = Programm testen       -- ein Programm ohne Thonny 15 Sekunden laufen lassen
echo.
if defined BRETT echo  Zuletzt installiert: %BRETT%   -- Eingabetaste allein waehlt 2.
if not defined BRETT echo  Noch kein Brett installiert   -- Eingabetaste allein waehlt 1.
echo.
set "WAHL=%VORGABE%"
set /p WAHL=  Auswahl [%VORGABE%]:
if "%WAHL%"=="1" goto installieren
if "%WAHL%"=="2" goto thonny
if "%WAHL%"=="3" goto testen
echo.
echo  "%WAHL%" ist keine Auswahl -- bitte die Batch noch einmal starten und 1, 2 oder 3 eingeben.
goto ende

:installieren
call :pc_pruefen
if not defined PYD goto fehlt
echo.
echo === Brett installieren -- im Browser das Brett waehlen, ESP32-Brett oder ESP32-CAM; danach startet es von selbst ===
tasklist /fi "imagename eq thonny.exe" | find /i "thonny.exe" >nul
if not errorlevel 1 echo HINWEIS: Thonny laeuft -- vor dem Installieren schliessen, sonst ist der Anschluss des Bretts belegt.
"%PYD%\python.exe" "%~dp0Werkzeuge\esp_kurs_installation_1.2.py"
goto ende

:thonny
call :pc_pruefen
if not defined PYD goto fehlt
call "%~dp0Werkzeuge\Thonny_starten.bat"
goto ende

:testen
call :pc_pruefen
if not defined PYD goto fehlt
call "%~dp0Werkzeuge\Programm_testen.bat"
goto ende

:fehlt
echo.
echo  Thonny-Python nicht gefunden -- die PC-Einrichtung in Werkzeuge\PC_einrichten ist nicht durchgelaufen. Bitte die Batch noch einmal starten.
goto ende

:pc_pruefen
rem --- Thonnys Python suchen; fehlen Python, pyserial oder esptool: PC einrichten (nur was fehlt), dann noch einmal suchen ---
call :python_suchen
set "FEHLT=1"
if defined PYD "%PYD%\python.exe" -c "import serial, esptool" >nul 2>&1 && set "FEHLT="
if not defined FEHLT goto :eof
echo.
echo === PC einrichten -- Thonny, Pakete, USB-Treiber; nur beim ersten Mal, nur was fehlt ===
set "OHNEPAUSE=1"
call "%~dp0Werkzeuge\PC_einrichten\1_PC_einrichten_1.7.bat"
set "OHNEPAUSE="
call :python_suchen
goto :eof

:python_suchen
set "PYD="
for %%d in ("%LOCALAPPDATA%\Programs\Thonny" "%ProgramFiles%\Thonny" "%ProgramFiles(x86)%\Thonny") do if not defined PYD if exist "%%~d\python.exe" set "PYD=%%~d"
goto :eof

:ende
endlocal
exit /b

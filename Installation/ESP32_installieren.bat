@echo off
rem ===========================================================================================================
rem  VHS-Kurs "ESP32-CAM und ESP32 mit MicroPython"  --  Mein ESP32 installieren (gemeinsam fuer beide Bretter)  (ESP32_installieren.bat, Fassung 1.5 -- gemeinsam fuer ESP32-CAM und ESP32-Brett)
rem  Autor: Prof. Dr.-Ing. Ralph Wystup M.Sc.  -  erstellt mit KI und Agent (Claude Code, Anthropic)  -  Fassung 1.5 vom 24.11.2026 (Seite 1.2 mit Handauswahl des Anschlusses bei mehreren Brettern; 1.4: Seite 1.1 mit Bewegungsmelder fuer die Kamera; 1.3: gemeinsame Seite esp_kurs_installation_1.2.py: Brett waehlen, ESP32-CAM oder ESP32-Brett; 1.2: laeuft von allein durch, PC-Einrichtung 1.7 ohne Internet; 1.1: Name statt Nummer)
rem -----------------------------------------------------------------------------------------------------------
rem  Sein Wort: Ordner kopieren, fabrikfrisches Brett an USB, Batch starten -- sonst nichts.
rem  Fehlen Thonny-Python, pyserial oder esptool, laeuft zuerst Werkzeuge\PC_einrichten\1_PC_einrichten_1.7.bat (installiert nur, was fehlt; Windows fragt fuer den
rem  USB-Treiber einmal nach Administratorrechten). Dann startet Werkzeuge\esp_kurs_esp32_installieren_1.1.py (Webserver nur auf diesem PC, http://127.0.0.1:8765/) und oeffnet die Seite im Browser.
rem  Dieses Fenster offen lassen, solange installiert wird; schliessen beendet die Installationsseite.
rem ===========================================================================================================
setlocal
title ESP32 Installationsseite
set "PYD="
for %%d in ("%LOCALAPPDATA%\Programs\Thonny" "%ProgramFiles%\Thonny" "%ProgramFiles(x86)%\Thonny") do if not defined PYD if exist "%%~d\python.exe" set "PYD=%%~d"
set "FEHLT=1"
if defined PYD "%PYD%\python.exe" -c "import serial, esptool" >nul 2>&1 && set "FEHLT="
if defined FEHLT (
  echo === Schritt 1 von 2: PC einrichten -- Thonny, Pakete, USB-Treiber; nur beim ersten Mal, nur was fehlt ===
  set "OHNEPAUSE=1"
  call "%~dp0Werkzeuge\PC_einrichten\1_PC_einrichten_1.7.bat"
  set "OHNEPAUSE="
  set "PYD="
  for %%d in ("%LOCALAPPDATA%\Programs\Thonny" "%ProgramFiles%\Thonny" "%ProgramFiles(x86)%\Thonny") do if not defined PYD if exist "%%~d\python.exe" set "PYD=%%~d"
)
if not defined PYD (
  echo Thonny-Python nicht gefunden -- die PC-Einrichtung (Werkzeuge\PC_einrichten) ist nicht durchgelaufen. Bitte noch einmal starten.
  pause
  exit /b 1
)
echo === Schritt 2 von 2: Brett installieren -- im Browser das Brett waehlen (ESP32-Brett oder ESP32-CAM); es startet von selbst ===
tasklist /fi "imagename eq thonny.exe" | find /i "thonny.exe" >nul
if not errorlevel 1 echo HINWEIS: Thonny laeuft -- vor dem Installieren schliessen, sonst ist der Anschluss des Bretts belegt.
"%PYD%\python.exe" "%~dp0Werkzeuge\esp_kurs_installation_1.2.py"
pause
endlocal

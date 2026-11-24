@echo off
rem ===========================================================================================================
rem  VHS-Kurs "ESP32 mit MicroPython"  --  Installationsseite fuer ESP32-WROOM-32-Bretter starten (Dozent)  (Dozent_ESP32_installieren_1.0.bat)
rem  Autor: Prof. Dr.-Ing. Ralph Wystup M.Sc.  -  Mitarbeit: Claude (Anthropic, Claude Code)  -  Fassung 1.0 vom 24.11.2026 (aus Dozent_Kameras_installieren_1.4.bat fuer das ESP32-WROOM-32-Brett)
rem -----------------------------------------------------------------------------------------------------------
rem  Startet Werkzeuge\esp_kurs_esp32_installieren_1.0.py (Webserver nur auf diesem PC, http://127.0.0.1:8765/) und oeffnet die Seite im Browser.
rem  Dieses Fenster offen lassen, solange installiert wird; schliessen beendet die Installationsseite.
rem ===========================================================================================================
setlocal
title ESP32 Installationsseite
set "PYD="
for %%d in ("%LOCALAPPDATA%\Programs\Thonny" "%ProgramFiles%\Thonny" "%ProgramFiles(x86)%\Thonny") do if not defined PYD if exist "%%~d\python.exe" set "PYD=%%~d"
if not defined PYD (
  echo Thonny-Python nicht gefunden -- bitte zuerst ..\Teilnehmer\Teilnehmer_1_PC_einrichten_1.6.bat ausfuehren.
  pause
  exit /b 1
)
tasklist /fi "imagename eq thonny.exe" | find /i "thonny.exe" >nul
if not errorlevel 1 echo HINWEIS: Thonny laeuft -- vor dem Installieren schliessen, sonst ist der Anschluss des Bretts belegt.
"%PYD%\python.exe" "%~dp0Werkzeuge\esp_kurs_esp32_installieren_1.0.py"
pause
endlocal

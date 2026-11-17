@echo off
rem ===========================================================================================================
rem  (Dateiname eindeutig nach seinem Wort 17.11.2026; vorher esp_kurs_installieren_1.0.bat)
rem  VHS-Kurs "ESP32-CAM mit MicroPython"  --  Installationsseite starten (Dozent)  (Dozent_Kameras_installieren_1.4.bat)
rem  Autor: Prof. Dr.-Ing. Ralph Wystup M.Sc.  -  Mitarbeit: Claude (Anthropic, Claude Code)  -  Fassung 1.4 vom 17.11.2026 (Anschlussfehler nie flashen; ohne main.py, Probelauf; Fortschrittsbalken; Programme im Unterordner Werkzeuge)
rem -----------------------------------------------------------------------------------------------------------
rem  Startet Werkzeuge\esp_kurs_installieren_1.4.py (Webserver nur auf diesem PC, http://127.0.0.1:8765/) und oeffnet die Seite im Browser.
rem  Dieses Fenster offen lassen, solange installiert wird; schliessen beendet die Installationsseite.
rem ===========================================================================================================
setlocal
title ESP32-CAM Installationsseite
set "PYD="
for %%d in ("%LOCALAPPDATA%\Programs\Thonny" "%ProgramFiles%\Thonny" "%ProgramFiles(x86)%\Thonny") do if not defined PYD if exist "%%~d\python.exe" set "PYD=%%~d"
if not defined PYD (
  echo Thonny-Python nicht gefunden -- bitte zuerst ..\Teilnehmer\Teilnehmer_1_PC_einrichten_1.5.bat ausfuehren.
  pause
  exit /b 1
)
tasklist /fi "imagename eq thonny.exe" | find /i "thonny.exe" >nul
if not errorlevel 1 echo HINWEIS: Thonny laeuft -- vor dem Installieren schliessen, sonst ist der Anschluss der Kamera belegt.
"%PYD%\python.exe" "%~dp0Werkzeuge\esp_kurs_installieren_1.4.py"
pause
endlocal

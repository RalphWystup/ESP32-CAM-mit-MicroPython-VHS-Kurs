@echo off
rem ===========================================================================================================
rem  (Dateiname eindeutig nach seinem Wort 17.11.2026; vorher esp_kurs_thonny_starten_1.2.bat)
rem  VHS-Kurs "ESP32-CAM mit MicroPython"  --  Thonny mit Kamera starten  (Teilnehmer_2_Thonny_mit_Kamera_starten_1.4.bat)
rem  Autor: Prof. Dr.-Ing. Ralph Wystup M.Sc.  -  Mitarbeit: Claude (Anthropic, Claude Code)  -  Fassung 1.4 vom 17.11.2026
rem -----------------------------------------------------------------------------------------------------------
rem  Jedes Mal per Doppelklick, wenn mit der Kamera gearbeitet wird:
rem    1. Kamera suchen und ihren Anschluss vorbereiten (esp_com_vorlauf_1.2.py: erst 9600, dann 115200 Baud, DTR/RTS aus, Neustart),
rem    2. Thonny mit dem Kameraprogramm starten -- dann nur noch den gruenen Start-Knopf (F5) druecken:
rem       das Programm laeuft auf der Kamera, unten stehen die Verbindungsdaten.
rem  1.4: Vorlauf 1.2 startet die Kamera per Software neu (sonst steht sie nach dem Einstecken im Bootlader); kamera.py 1.6.
rem  1.3: Programme in den Unterordnern Werkzeuge und Kameraprogramme.
rem  1.2: Kameraprogramm 1.4.
rem  1.1: Thonny oeffnet gleich esp_cam_kamera_1.4.py (sein Wort: "sollen sie nur den start knopf druecken muessen").
rem  Voraussetzung: einmal Teilnehmer_1_PC_einrichten_1.6.bat ausgefuehrt (Thonny, Pakete, Treiber, Thonny-Einstellung).
rem ===========================================================================================================
setlocal
set "PY="
set "THONNY="
for %%d in ("%LOCALAPPDATA%\Programs\Thonny" "%ProgramFiles%\Thonny" "%ProgramFiles(x86)%\Thonny") do if not defined THONNY if exist "%%~d\thonny.exe" set "THONNY=%%~d"
if not defined THONNY for /f "usebackq delims=" %%p in (`powershell -NoProfile -Command "$k='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Thonny_is1','HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Thonny_is1','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Thonny_is1'; foreach($x in $k){ $v=(Get-ItemProperty $x -ErrorAction SilentlyContinue).InstallLocation; if($v){ $v.TrimEnd('\'); break } }"`) do set "THONNY=%%p"
if not defined THONNY (
  echo Thonny ist nicht installiert -- bitte zuerst Teilnehmer_1_PC_einrichten_1.6.bat ausfuehren.
  pause
  exit /b 1
)
if exist "%THONNY%\python.exe" set "PY=%THONNY%\python.exe"
tasklist /fi "imagename eq thonny.exe" | find /i "thonny.exe" >nul
if not errorlevel 1 (
  echo Thonny laeuft schon -- bitte Thonny schliessen und diese Datei noch einmal starten.
  pause
  exit /b 1
)
echo.
echo === Kamera vorbereiten ===
if defined PY "%PY%" "%~dp0Werkzeuge\esp_com_vorlauf_1.2.py"
if errorlevel 1 (
  pause
  exit /b 1
)
echo.
echo === Thonny wird gestartet ===
start "" "%THONNY%\thonny.exe" "%~dp0Kameraprogramme\esp_cam_kamera_1.6.py"
echo Thonny oeffnet das Kameraprogramm -- jetzt nur den gruenen Start-Knopf druecken.
timeout /t 8 >nul
endlocal
exit /b 0

@echo off
rem ===========================================================================================================
rem  VHS-Kurs "ESP32-CAM und ESP32 mit MicroPython"  --  Thonny mit dem Brett starten  (Werkzeuge\Thonny_starten.bat, Fassung 1.3 vom 24.11.2026 -- liegt in Werkzeuge, aufgerufen von ESP32_Start.bat; 1.3: aus ESP32_Start kein eigenes Warten)
rem  Autor: Prof. Dr.-Ing. Ralph Wystup M.Sc.  -  erstellt mit KI und Agent (Claude Code, Anthropic)
rem -----------------------------------------------------------------------------------------------------------
rem  Jedes Mal per Doppelklick. Liest aus Werkzeuge\brett.txt, welches Brett zuletzt installiert wurde:
rem    cam -> Kamera vorbereiten (esp_com_vorlauf_1.2.py: 9600/115200 Baud, Neustart aus dem Download-Modus), Thonny mit kamera.py
rem    esp -> Thonny mit blink.py (das WROOM-Brett braucht keinen Vorlauf)
rem  Dann nur den gruenen Start-Knopf (F5) druecken. Voraussetzung: einmal ESP32_Start.bat (Installation).
rem ===========================================================================================================
setlocal
set "THONNY="
set "PY="
for %%d in ("%LOCALAPPDATA%\Programs\Thonny" "%ProgramFiles%\Thonny" "%ProgramFiles(x86)%\Thonny") do if not defined THONNY if exist "%%~d\thonny.exe" set "THONNY=%%~d"
if not defined THONNY (
  echo Thonny ist nicht installiert -- bitte zuerst ESP32_Start.bat ausfuehren.
  pause
  exit /b 1
)
if exist "%THONNY%\python.exe" set "PY=%THONNY%\python.exe"
tasklist /fi "imagename eq thonny.exe" | find /i "thonny.exe" >nul
if not errorlevel 1 (
  echo Thonny laeuft schon -- bitte dort weiterarbeiten oder Thonny schliessen und diese Datei noch einmal starten.
  pause
  exit /b 1
)
set "BRETT=esp"
if exist "%~dp0brett.txt" set /p BRETT=<"%~dp0brett.txt"
echo.
if /i "%BRETT%"=="cam" (
  echo === ESP32-CAM: Kamera vorbereiten ===
  if defined PY "%PY%" "%~dp0esp_com_vorlauf_1.2.py"
  echo === Thonny wird gestartet ===
  start "" "%THONNY%\thonny.exe" "%~dp0..\Programme\ESP32-CAM\esp_cam_kamera_1.6.py"
  echo Thonny oeffnet das Kameraprogramm -- jetzt nur den gruenen Start-Knopf druecken.
) else (
  echo === ESP32-Brett: Thonny wird gestartet ===
  start "" "%THONNY%\thonny.exe" "%~dp0..\Programme\ESP32\esp32_blink_1.0.py"
  echo Thonny oeffnet blink.py -- jetzt nur den gruenen Start-Knopf druecken ^(die blaue LED am Brett blinkt^).
)
if not defined VONSTART timeout /t 8 >nul
endlocal
exit /b 0

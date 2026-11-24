@echo off
rem ===========================================================================================================
rem  VHS-Kurs "ESP32-CAM und ESP32 mit MicroPython"  --  Programm auf dem Brett testen, ohne Thonny  (Werkzeuge\Programm_testen.bat, Fassung 1.4 vom 24.11.2026 -- liegt in Werkzeuge, aufgerufen von ESP32_Start.bat; 1.4: pause nur beim Doppelklick, nicht aus ESP32_Start; 1.2: Soft-Reboot nach Stop, Handauswahl)
rem  Autor: Prof. Dr.-Ing. Ralph Wystup M.Sc.  -  erstellt mit KI und Agent (Claude Code, Anthropic)
rem -----------------------------------------------------------------------------------------------------------
rem  Zeigt, was auf dem Brett liegt, fragt nach dem Programm und startet es fuer 15 Sekunden (Ausgabe hier im Fenster),
rem  dann Stop wie in Thonny. Thonny muss geschlossen sein (es haelt sonst den Anschluss).
rem ===========================================================================================================
setlocal
set "PYD="
for %%d in ("%LOCALAPPDATA%\Programs\Thonny" "%ProgramFiles%\Thonny" "%ProgramFiles(x86)%\Thonny") do if not defined PYD if exist "%%~d\python.exe" set "PYD=%%~d"
if not defined PYD (
  echo Thonny-Python nicht gefunden -- bitte zuerst ESP32_Start.bat ausfuehren.
  pause
  exit /b 1
)
"%PYD%\python.exe" "%~dp0programm_starten_1.2.py"
set /p PROG=Welches Programm starten (z. B. blink.py, pwm.py, led_handy.py, kamera.py, bewegung.py)? 
if "%PROG%"=="" goto ende
"%PYD%\python.exe" "%~dp0programm_starten_1.2.py" %PROG% 15
:ende
if not defined VONSTART pause
endlocal

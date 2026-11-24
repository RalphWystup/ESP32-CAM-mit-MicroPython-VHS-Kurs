@echo off
rem ===========================================================================================================
rem  VHS-Kurs "ESP32-CAM und ESP32 mit MicroPython"  --  Programm auf dem Brett testen, ohne Thonny  (Programm_testen.bat, Fassung 1.2 vom 24.11.2026; Soft-Reboot nach Stop; bei mehreren Brettern Handauswahl)
rem  Autor: Prof. Dr.-Ing. Ralph Wystup M.Sc.  -  erstellt mit KI und Agent (Claude Code, Anthropic)
rem -----------------------------------------------------------------------------------------------------------
rem  Zeigt, was auf dem Brett liegt, fragt nach dem Programm und startet es fuer 15 Sekunden (Ausgabe hier im Fenster),
rem  dann Stop wie in Thonny. Thonny muss geschlossen sein (es haelt sonst den Anschluss).
rem ===========================================================================================================
setlocal
set "PYD="
for %%d in ("%LOCALAPPDATA%\Programs\Thonny" "%ProgramFiles%\Thonny" "%ProgramFiles(x86)%\Thonny") do if not defined PYD if exist "%%~d\python.exe" set "PYD=%%~d"
if not defined PYD (
  echo Thonny-Python nicht gefunden -- bitte zuerst ESP32_installieren.bat ausfuehren.
  pause
  exit /b 1
)
"%PYD%\python.exe" "%~dp0Werkzeuge\programm_starten_1.2.py"
set /p PROG=Welches Programm starten (z. B. blink.py, pwm.py, led_handy.py, kamera.py, bewegung.py)? 
if "%PROG%"=="" goto ende
"%PYD%\python.exe" "%~dp0Werkzeuge\programm_starten_1.2.py" %PROG% 15
:ende
pause
endlocal

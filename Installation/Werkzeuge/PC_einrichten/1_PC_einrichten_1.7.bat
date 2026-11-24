@echo off
rem ===========================================================================================================
rem  (Dateiname eindeutig nach seinem Wort 17.11.2026; vorher esp_kurs_einrichten_1.4.bat)
rem  Teilnehmer_1_PC_einrichten_1.6.bat -- richtet einen Windows-PC fuer den Kurs "ESP32-CAM mit MicroPython" ein.
rem  Grundsatz (sein Wort 17.11.2026): erst nachsehen, nur Fehlendes installieren, nichts Vorhandenes ueberschreiben.
rem   1. Thonny: ist schon IRGENDEIN Thonny da (Standardordner oder laut Windows-Registry, auch Thonny 4), wird
rem      nichts installiert. Sonst Thonny 5.0.1 (64 Bit, Python 3.14) von GitHub, SHA-256 geprueft, still, nur fuer
rem      den angemeldeten Benutzer (keine Administratorrechte).
rem   2. In Thonnys Python: pyserial 3.5 und esptool 5.2.0.
rem   3. USB-Treiber (wie beim Kurs-Agenten): mit pnputil im Treiberspeicher nachsehen; fehlt er, beim Hersteller
rem      laden und mit pnputil installieren -- nur dafuer eine Windows-Abfrage nach Administratorrechten (Ja).
rem      CH340/CH341 (WCH, auf den ESP32-CAM-MB-Brettern) und CP210x (Silicon Labs, auf manchen Brettern;
rem      der Hersteller sperrt den Download zeitweise -- dann nur ein Hinweis).
rem      Windows nimmt nur signierte Kerneltreiber an (pnputil prueft die Signatur); feste Pruefsumme nicht,
rem      weil WCH die Datei bei neuen Fassungen austauscht.
rem   4. Thonny einstellen: [ESP32] dtr = False, rts = False (sonst haelt Thonny die Kamera auf dem MB-Brett im Reset:
rem      "Device is busy or does not respond"); alte Einstellungsdatei wird gesichert; nur wenn Thonny geschlossen ist.
rem   5. Anzeige: Thonny-Fassung, Pakete, serielle Anschluesse.
rem  Liegen Thonny-Installer und Treiber im Unterordner pakete (esp_pakete_holen_1.0.py), werden DIESE genommen (ohne Internet);
rem  der Thonny-Installer wird auch dort ueber die Pruefsumme geprueft.
rem  Aufruf: Doppelklick.  Schalter: nurladen  = Thonny-Installer und Treiber nur laden und pruefen, nichts installieren
rem                                  ohnepause = am Ende nicht auf eine Taste warten
rem  1.6 (17.11.2026): Verweis auf Teilnehmer_2 1.4.
rem  1.7 (24.11.2026, ESP32-Brett): Python-Pakete aus pakete\wheels, wenn vorhanden (ohne Internet); mit OHNEPAUSE=1 ohne Halt am Ende (Aufruf aus ESP32_installieren.bat); Schlusszeile ohne Kamera.
rem  1.5 (17.11.2026): Hilfsprogramme im Unterordner Werkzeuge.
rem  1.4 (17.11.2026): Thonny wird auf MicroPython (ESP32) voreingestellt; danach Teilnehmer_2_Thonny_mit_Kamera_starten_1.4.bat benutzen.
rem  1.3 (17.11.2026): esp_thonny_einstellen 1.1 -- schon eingestellt = kein Fehler, auch bei laufendem Thonny.
rem  1.2 (17.11.2026): pakete-Ordner zuerst; Schritt 4 Thonny einstellen (DTR/RTS aus), gemessen an seinem Thonny 5.0.0.
rem  1.1 (17.11.2026): Thonny-Suche auch ueber die Registry; Treiberschritt; Anzeige ohne Zugangsblatt.
rem  Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) -- gemeinsam erstellt.
rem ===========================================================================================================
setlocal
set "VER=5.0.1"
set "URL=https://github.com/thonny/thonny/releases/download/v5.0.1/thonny-5.0.1-x64.exe"
set "SOLL=a2b04784cd2ee7d4c22ed46865de5e8ba6eaf55950543ef9546374f53cf778a5"
set "DATEI=%TEMP%\thonny-5.0.1-x64.exe"
set "TD=%TEMP%\esp_kurs_treiber"
set "PAK=%~dp0pakete"
set "PY="
set "THONNY="
set "NURLADEN="
set "OHNEPAUSE="
set "FEHLER="
if /i "%~1"=="nurladen" set "NURLADEN=1"
if /i "%~1"=="ohnepause" set "OHNEPAUSE=1"
if /i "%~2"=="ohnepause" set "OHNEPAUSE=1"

echo.
echo === ESP32-CAM-Kurs: PC einrichten (erst nachsehen, nur Fehlendes installieren) ===
echo.
echo --- 1. Thonny ---
if defined NURLADEN goto thonny_laden
call :suche_thonny
if defined THONNY goto thonny_da

:thonny_laden
if exist "%PAK%\thonny-5.0.1-x64.exe" (
  echo Thonny %VER% aus dem Ordner pakete.
  set "DATEI=%PAK%\thonny-5.0.1-x64.exe"
  goto thonny_pruefen
)
echo Kein Thonny gefunden. Thonny %VER% wird aus dem Internet geladen (etwa 31 MB) ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol='Tls12'; Invoke-WebRequest -Uri '%URL%' -OutFile '%DATEI%'"
if not exist "%DATEI%" goto fehler_laden
:thonny_pruefen
set "IST="
for /f "usebackq delims=" %%h in (`powershell -NoProfile -Command "(Get-FileHash -Algorithm SHA256 '%DATEI%').Hash.ToLower()"`) do set "IST=%%h"
if /i not "%IST%"=="%SOLL%" goto fehler_pruefsumme
echo Pruefsumme stimmt.
if defined NURLADEN goto treiber
echo Thonny wird installiert (still, nur fuer diesen Benutzer) ...
start "" /wait "%DATEI%" /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CURRENTUSER
call :suche_thonny
if not defined PY goto fehler_installation
echo Thonny installiert: "%THONNY%"
goto pakete

:thonny_da
echo Thonny ist schon da: "%THONNY%" -- es wird nichts installiert oder ueberschrieben.
if not defined PY echo HINWEIS: in diesem Thonny-Ordner liegt kein python.exe -- Pakete bitte in Thonny unter Werkzeuge - Pakete verwalten installieren.
if not defined PY goto treiber

:pakete
echo.
echo --- 2. Pakete in Thonnys Python ---
echo "%PY%"
if exist "%PAK%\wheels\" (
  echo Pakete aus dem Ordner pakete\wheels ^(ohne Internet^).
  "%PY%" -m pip install --user --upgrade --disable-pip-version-check -q --no-index --find-links "%PAK%\wheels" pyserial==3.5 esptool==5.2.0
) else (
  "%PY%" -m pip install --user --upgrade --disable-pip-version-check -q pyserial==3.5 esptool==5.2.0
)
if errorlevel 1 (echo FEHLER: Pakete nicht installiert - Internetverbindung pruefen.& set "FEHLER=1") else (echo pyserial 3.5 und esptool 5.2.0 installiert.)

:treiber
echo.
echo --- 3. USB-Treiber ---
call :treiber_eins CH340 "ch341ser.inf" "https://www.wch-ic.com/download/file?id=5" "CH341SER.ZIP"
call :treiber_eins CP210x "silabser.inf" "https://www.silabs.com/documents/public/software/CP210x_Universal_Windows_Driver.zip" "CP210x_Universal_Windows_Driver.zip"
if defined NURLADEN goto ende

echo.
echo --- 4. Thonny einstellen (DTR/RTS aus) ---
if defined PY if exist "%~dp0Werkzeuge\esp_thonny_einstellen_1.2.py" "%PY%" "%~dp0Werkzeuge\esp_thonny_einstellen_1.2.py"
if errorlevel 1 set "FEHLER=1"
echo.
echo --- 5. Anzeige ---
if defined PY if exist "%~dp0Werkzeuge\esp_kurs_pruefen_1.0.py" "%PY%" "%~dp0Werkzeuge\esp_kurs_pruefen_1.0.py"
echo.
if defined FEHLER (echo Fertig, aber mit FEHLER - siehe oben.) else (echo Fertig.)
if not defined OHNEPAUSE echo Zum Arbeiten: Brett per USB anstecken, Thonny_starten.bat doppelklicken, in Thonny den gruenen Start-Knopf druecken.
goto ende

rem ---------------------------------------------------------------------------------------------------------
:treiber_eins
rem  %1 Name  %2 INF-Name im Treiberspeicher  %3 Herstelleradresse  %4 Dateiname
pnputil /enum-drivers > "%TEMP%\esp_kurs_treiberliste.txt" 2>&1
findstr /i /c:"%~2" "%TEMP%\esp_kurs_treiberliste.txt" >nul
if not errorlevel 1 (
  echo %~1-Treiber ist schon da -- nichts zu tun.
  if not defined NURLADEN exit /b 0
)
if not exist "%TD%" mkdir "%TD%"
if exist "%PAK%\%~4" (
  echo %~1-Treiber aus dem Ordner pakete.
  powershell -NoProfile -Command "try { Expand-Archive -Force '%PAK%\%~4' '%TD%\%~1' } catch { exit 2 }"
  goto treiber_gefunden
)
echo %~1-Treiber wird beim Hersteller geladen ...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; [Net.ServicePointManager]::SecurityProtocol='Tls12'; try { Invoke-WebRequest -Uri '%~3' -OutFile '%TD%\%~4' -UserAgent 'Mozilla/5.0' } catch { exit 1 }; try { Expand-Archive -Force '%TD%\%~4' '%TD%\%~1' } catch { exit 2 }"
:treiber_gefunden
set "INF="
for /f "delims=" %%i in ('dir /s /b "%TD%\%~1\%~2" 2^>nul') do if not defined INF set "INF=%%i"
if not defined INF (
  echo HINWEIS: %~1-Treiber war nicht zu bekommen ^(Hersteller sperrt den Download zeitweise^). Nur noetig, wenn das Brett einen %~1 hat.
  exit /b 0
)
echo geladen: "%INF%"
if defined NURLADEN exit /b 0
echo %~1-Treiber wird installiert -- Windows fragt nach Administratorrechten, bitte mit Ja beantworten.
powershell -NoProfile -Command "Start-Process -FilePath pnputil -ArgumentList '/add-driver','\"%INF%\"','/install' -Verb RunAs -Wait"
pnputil /enum-drivers > "%TEMP%\esp_kurs_treiberliste.txt" 2>&1
findstr /i /c:"%~2" "%TEMP%\esp_kurs_treiberliste.txt" >nul
if errorlevel 1 (echo FEHLER: %~1-Treiber ist danach nicht im Treiberspeicher.& set "FEHLER=1") else (echo %~1-Treiber installiert.)
exit /b 0

:suche_thonny
set "PY="
set "THONNY="
for %%d in ("%LOCALAPPDATA%\Programs\Thonny" "%ProgramFiles%\Thonny" "%ProgramFiles(x86)%\Thonny") do if not defined THONNY if exist "%%~d\thonny.exe" set "THONNY=%%~d"
if not defined THONNY for /f "usebackq delims=" %%p in (`powershell -NoProfile -Command "$k='HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Thonny_is1','HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\Thonny_is1','HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Thonny_is1'; foreach($x in $k){ $v=(Get-ItemProperty $x -ErrorAction SilentlyContinue).InstallLocation; if($v){ $v.TrimEnd('\'); break } }"`) do set "THONNY=%%p"
if defined THONNY if exist "%THONNY%\python.exe" set "PY=%THONNY%\python.exe"
exit /b 0

:fehler_laden
echo FEHLER: Thonny konnte nicht geladen werden. Internetverbindung pruefen.
goto ende_fehler
:fehler_pruefsumme
echo FEHLER: Die geladene Datei hat nicht die erwartete Pruefsumme -- sie wird NICHT installiert.
echo   erwartet %SOLL%
echo   erhalten %IST%
if /i not "%DATEI%"=="%PAK%\thonny-5.0.1-x64.exe" del "%DATEI%" 2>nul
goto ende_fehler
:fehler_installation
echo FEHLER: Thonny wurde nach der Installation nicht gefunden.
goto ende_fehler

:ende_fehler
if not defined OHNEPAUSE pause
endlocal
exit /b 1
:ende
if not defined OHNEPAUSE pause
endlocal
if defined FEHLER exit /b 1
exit /b 0

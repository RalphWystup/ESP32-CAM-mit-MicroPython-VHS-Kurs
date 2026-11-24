# VHS-Kurs „ESP32-CAM und ESP32 mit MicroPython“ – mein Brett installieren

**Volkshochschule · Kurs „ESP32-CAM und ESP32 mit MicroPython“**
Prof. Dr.-Ing. Ralph Wystup M.Sc. · erstellt mit KI und Agent (Claude Code, Anthropic) · Fassung 1.1 vom 24.11.2026 (1.1: Bewegungsmelder auf der Kamera)

Ein Ordner für beide Bretter: das gewöhnliche **ESP32-Brett** (ESP32-WROOM-32, 30 Stifte, blaue LED) und die **ESP32-CAM**
(Kamera auf dem USB-Brett). Es braucht kein Internet: Thonny, beide USB-Treiber (CH340 und CP210x), die Python-Pakete und
beide MicroPython-Firmwares liegen im Ordner.

## Einmal: das Brett installieren

1. Diesen Ordner auf den eigenen Rechner kopieren (nicht vom Stick aus starten).
2. Nur **ein** Brett mit einem USB-**Daten**kabel anstecken. Thonny muss geschlossen sein.
3. **`ESP32_installieren.bat`** doppelklicken.
   - Beim ersten Mal richtet sie den PC ein: Thonny 5.0.1, die Python-Pakete pyserial und esptool, die USB-Treiber
     (Windows fragt dafür einmal nach Administratorrechten – mit Ja beantworten) und stellt Thonny ein.
   - Dann öffnet sich im Browser die Seite „Mein ESP32 installieren“.
4. Auf der Seite **das Brett wählen** (ESP32-Brett oder ESP32-CAM). Der Name ist mit dem Windows-Benutzernamen vorbelegt
   (Umlaute werden ersetzt). Sobald genau ein Brett angeschlossen ist, startet die Installation nach 10 Sekunden **von selbst**;
   wer das Brett oder den Namen ändern will, drückt „Abbrechen“, stellt um und drückt „Brett installieren“.
   Ein fabrikfrisches Brett bekommt zuerst MicroPython (etwa 2 Minuten – Kabel nicht berühren), dann die Programme,
   zum Schluss läuft ein Probelauf. Am Ende steht grün **FERTIG** mit dem Namen des WLANs (`VHS-ESP-<Name>` oder `VHS-CAM-<Name>`).
5. Das schwarze Fenster schließen. Die Brettwahl merkt sich der Ordner (`Werkzeuge\brett.txt`).

## Jedes Mal: mit dem Brett arbeiten

**`Thonny_starten.bat`** doppelklicken. Beim ESP32-Brett öffnet Thonny `blink.py`, bei der Kamera bereitet die Datei die Kamera vor
(sie steht nach dem Einstecken im Download-Modus) und öffnet `kamera.py`. Dann den **grünen Start-Knopf** drücken; **Stop** beendet.
Andere Programme: in Thonny links im Dateibereich „MicroPython-Gerät“ öffnen.

| Auf dem Brett | ESP32-Brett | ESP32-CAM |
|---|---|---|
| `blink.py` | blaue LED (GPIO 2) blinkt | weiße Blitz-LED blinkt (sehr hell) |
| `pwm.py` | LED per PWM heller und dunkler | Blitz-LED per PWM |
| `led_handy.py` | LED vom Handy aus: WLAN `VHS-ESP-<Name>`, `http://192.168.4.1/` | wie links, WLAN `VHS-CAM-<Name>` |
| `kamera.py` | – | Livebild im Browser unter `http://192.168.4.1/` |
| `bewegung.py` | – | Bewegungsmelder mit Bildübertragung: Kamera liefert ihre Bedienseite selbst, LED blitzt, wenn das Foto angekommen ist (Anleitung: `Beispiele\\Bewegungsmelder` im Repositorium) |

Die Programme liegen zum Lesen in `Programme\ESP32\` und `Programme\ESP32-CAM\`.

## Ohne Thonny ausprobieren

**`Programm_testen.bat`** zeigt, was auf dem Brett liegt, fragt nach dem Programm und lässt es 15 Sekunden laufen (Ausgabe im Fenster),
dann stoppt es wie in Thonny. Gut für einen schnellen Funktionstest; Thonny muss dabei geschlossen sein.

## Wenn etwas nicht geht

- Mehrere Bretter am PC: die Seite zeigt dann eine Auswahl des Anschlusses (sonst wählt sie ihn selbst); `Programm_testen.bat` fragt ebenfalls.
- „Kein ESP32-Brett gefunden“: ein USB-**Daten**kabel nehmen (manche Kabel laden nur); Kabel ab- und wieder anstecken.
- „Anschluss ist belegt“: Thonny oder eine andere Seite mit dem Brett schließen, Kabel 5 Sekunden abziehen, noch einmal.
- Das Flashen klappt nicht automatisch: die Seite sagt dann, wann die Taste BOOT (Brett) bzw. IO0 (Kamera) zu halten ist.
- Kamera: Thonny meldet „Device is busy“ oder „waiting for download“ – `Thonny_starten.bat` noch einmal (oder RST an der Kamera).
- Falsches Brett gewählt? Einfach noch einmal `ESP32_installieren.bat` mit der richtigen Wahl – die Firmware wird dann ersetzt.

## Was in diesem Ordner liegt

Oben nur, was gedrückt wird: `ESP32_installieren.bat` (einmal), `Thonny_starten.bat` (jedes Mal) und `Programm_testen.bat` (Funktionstest ohne Thonny), dazu dieses Liesmich.
`Werkzeuge\` Installationsseite, die beiden Konfigurationen, Kamera-Vorlauf, `PC_einrichten\` mit `pakete\` (Thonny 5.0.1, Treiber CH340 und CP210x,
Python-Pakete in `wheels\`); `Programme\ESP32\` und `Programme\ESP32-CAM\` mit den Programmen und der jeweiligen Firmware. Es stehen keine Kennwörter darin.

# VHS-Kurs „ESP32-CAM mit MicroPython“ – für Teilnehmer

Prof. Dr.-Ing. Ralph Wystup M.Sc. · Fassung 1.3 vom 17.11.2026

## Einmal: PC einrichten

**`Teilnehmer_1_PC_einrichten_1.6.bat`** doppelklicken. Sie installiert nur, was fehlt:
Thonny (ein vorhandenes Thonny bleibt unangetastet), die Python-Pakete pyserial und esptool, den USB-Treiber der Kamera
(Windows fragt dafür einmal nach Administratorrechten – mit Ja beantworten) und stellt Thonny auf die Kamera ein.
Thonny und der Treiber liegen im Ordner `pakete` – es geht auch ohne Internet (nur die Python-Pakete brauchen Internet).

## Jedes Mal: mit der Kamera arbeiten

1. Kamera per USB-Kabel anstecken.
   **Wichtig:** Nach dem Einstecken steht die Kamera im „Download-Modus“ (eine Eigenheit des USB-Bretts). Die Datei aus Schritt 2
   startet sie deshalb automatisch neu. Wer Thonny direkt öffnet, drückt stattdessen einmal **RST** an der Kamera.
2. **`Teilnehmer_2_Thonny_mit_Kamera_starten_1.4.bat`** doppelklicken – Thonny öffnet sich mit dem Kameraprogramm.
3. Den **grünen Start-Knopf** drücken. Unten steht „AM HANDY EINGEBEN“: WLAN-Name (z. B. `VHS-CAM-2`), Kennwort, Adresse.
   Danach meldet das Programm kurz jeden Zugriff und alle 30 s den Zustand. **Stop** beendet es.
4. Handy oder Laptop mit diesem WLAN verbinden, im Browser `http://192.168.4.1/` öffnen – das Livebild erscheint.

## Beispiele auf der Kamera

In Thonny links im Dateibereich „MicroPython-Gerät“ öffnen und Start drücken; „Stop“ beendet:

| Datei | Was passiert |
|---|---|
| `blink.py` | die weiße Blitz-LED vorne blinkt (sehr hell – nicht hineinsehen) |
| `pwm.py` | die Blitz-LED wird per PWM langsam heller und dunkler |
| `led_handy.py` | weiße LED vom Handy aus schalten (WLAN der Kamera, `http://192.168.4.1/`) |
| `kamera.py` | das Kameraprogramm |

Die gleichen Programme liegen zum Lesen im Unterordner `Kameraprogramme`.

## Wenn etwas nicht geht

- Thonny meldet „Device is busy or does not respond“ oder „waiting for download“: an der Kamera **RST** drücken
  (oder Thonny schließen und Datei 2 noch einmal starten).
- „Die Kamera hängt“: USB-Kabel 5 Sekunden abziehen, wieder anstecken, dann Start.
- „Kamera lässt sich nicht öffnen“: Thonny schließen, Kabel ab- und wieder anstecken, Datei 2 noch einmal starten.
- Keine Kamera gefunden: ein USB-**Daten**kabel nehmen (manche Kabel laden nur).

# ESP32-CAM und ESP32 mit MicroPython – VHS-Kurs

**Prof. Dr.-Ing. Ralph Wystup M.Sc. — erstellt mit KI und Agent (Claude Code, Anthropic)**

Kursmaterial für einen Einsteigerkurs: Eine ESP32-CAM (AI Thinker, auf dem USB-Brett ESP32-CAM-MB) oder ein gewöhnliches
ESP32-Brett (ESP32-WROOM-32, 30 Stifte) wird mit MicroPython betrieben und in **Python** programmiert. Die Kamera spannt ein eigenes WLAN auf (`VHS-CAM-<Nr>`) und zeigt
ihr Livebild im Browser unter `http://192.168.4.1/`. Dazu drei kleine Beispiele (LED blinkt, PWM, LED vom Handy schalten).
Gearbeitet wird mit **Thonny**.

Stand 24.11.2026 · Anleitung Fassung 1.10 · Kameraprogramm 1.6 · Installationsseite 1.4 (Kamera) / 1.0 (ESP32-Brett) · gemeinsames Installationsprogramm für beide Bretter: eine Batch-Datei `ESP32_Start.bat` 1.7 (fragt 1/2/3, bleibt bei Fehlern offen; am 24.11. an beiden Brettern durchgetestet) · Beispiel Bewegungsmelder 1.4

Anleitung als Seite: <https://ralphwystup.github.io/ESP32-CAM-mit-MicroPython-VHS-Kurs/> · als PDF: `LIESMICH_1.10.pdf`,
für Teilnehmer: `Installation/LIESMICH_Installation_1.3.pdf` (beide Bretter) sowie `Teilnehmer/LIESMICH_Teilnehmer_1.3.pdf` (Kamera, bisheriger Weg).

## Aufbau

| Ordner | Inhalt |
|---|---|
| `Teilnehmer/` | `Teilnehmer_1_PC_einrichten_1.6.bat` (einmal: Thonny, Python-Pakete, USB-Treiber, Thonny-Einstellung – nur was fehlt), `Teilnehmer_2_Thonny_mit_Kamera_starten_1.4.bat` (jedes Mal: Kamera vorbereiten, Thonny öffnen), Anleitung, `Kameraprogramme/` zum Lesen, `Werkzeuge/` |
| `Dozent/` | `Dozent_Kameras_installieren_1.4.bat` – Installationsseite im Browser (`http://127.0.0.1:8765/`): Kamera anstecken, Nummer eintragen, Knopf drücken; flasht werksfrische Kameras, spielt die Programme auf und macht einen Probelauf wie in Thonny. `Kameraprogramme/`, `Werkzeuge/` |

Auf jede Kamera kommen `kamera.py` (Kameraprogramm), `blink.py`, `pwm.py`, `led_handy.py`, `ssd1306.py` (OLED-Treiber)
und `kamera.json` (Name). Gestartet wird in Thonny mit dem grünen Start-Knopf; es gibt bewusst kein `main.py`.

| `Installation/` | **das gemeinsame Installationsprogramm für ESP32-CAM und ESP32-Brett, zum Weitergeben:** `ESP32_Start.bat` 1.7 (die eine Batch-Datei: fragt sofort 1 = Brett installieren, 2 = Thonny starten, 3 = Programm testen, bleibt bei jedem Fehler offen; Auswahl 1 richtet beim ersten Mal den PC ein – Thonny, Pakete, beide USB-Treiber, ohne Internet –, dann die Seite „Mein ESP32 installieren“: Brett wählen, Name mit dem Windows-Benutzer vorbelegt, Start von selbst; ein fabrikfrisches Brett bekommt die passende MicroPython-Firmware, die Programme und einen Probelauf; WLAN `VHS-ESP-<Name>` bzw. `VHS-CAM-<Name>`), Anleitung 1.3; `Werkzeuge/` (`Thonny_starten.bat` und `Programm_testen.bat`, von der Batch-Datei aufgerufen – Programm ohne Thonny starten, Ausgabe im Fenster, Stop mit Soft-Reboot; Seite 1.2: Brettwahl, Selbststart, Handauswahl des Anschlusses bei mehreren Brettern; Konfigurationen 1.1/1.5, Kamera-Vorlauf, `PC_einrichten/` 1.7, Pakete aus `pakete/wheels`), `Programme/ESP32/`, `Programme/ESP32-CAM/` (mit `bewegung.py`, dem Bewegungsmelder). Am 24.11. am ESP32-Brett und an der ESP32-CAM durchgetestet |
| `Dozent_ESP32/` | Dozentenfassung für das ESP32-Brett mit Brett-Nummer und Protokoll (`Dozent_ESP32_installieren_1.0.bat`, `Werkzeuge/`, `Programme/`); `esp32_brett_abfragen_1.0.py` fragt ein Brett ab, ohne etwas zu ändern (Chip, Flash, MicroPython?) |
| `Beispiele/Bewegungsmelder/` | ESP32-CAM als Bewegungsmelder mit Bildübertragung: `esp_cam_bewegung_1.4.py` (kommt als `main.py` auf die Kamera, liefert die Bedienseite selbst aus), `anzeige_bewegung_1.2.html`, Anleitung 1.4, Manuskript (Erkennung mit Formeln, Bilder, Nachrechnung) |

## Nicht im Repositorium (Fremddateien) – so kommen sie dazu

| Datei | Woher | Wohin |
|---|---|---|
| `firmware.bin` – MicroPython 1.27 mit Kameratreiber | <https://github.com/cnadler86/micropython-camera-API/releases/tag/v0.6.2>, Datei `mpy_cam-v1.27.0-AI_THINKER.zip` entpacken; SHA-256 von `firmware.bin`: `b26ba45de13549272d888c229c5c3864b75250471ac290478d752b8098ee70ea` | `Dozent/Kameraprogramme/` |
| pyserial 3.5, esptool 5.2.0 samt Abhängigkeiten als Wheel-Dateien (Python 3.14, Windows 64 Bit) | `pip download`/`pip wheel` (PyPI) | `Installation/Werkzeuge/PC_einrichten/pakete/wheels/` – dann braucht die Einrichtung kein Internet |
| Thonny 5.0.1, CH340-Treiber | lädt `Teilnehmer_1_PC_einrichten_1.6.bat` selbst von GitHub bzw. WCH; für Rechner ohne Internet vorher `Dozent/Werkzeuge/esp_pakete_holen_1.2.py` | `Teilnehmer/pakete/` bzw. `Installation/Werkzeuge/PC_einrichten/pakete/` |
| CP210x-Treiber (Silicon Labs, für Bretter mit CP2102-Wandler) | silabs.com sperrt Skript-Downloads; derselbe WHQL-Treiber 11.5.0.417 (9.12.2025) liegt im Microsoft-Update-Katalog („Silicon Laboratories Inc. Driver Update (11.5.0.417)“), Katalog-Signatur von Microsoft geprüft; als ZIP mit `silabser.inf` gepackt, SHA-256 `f2654c3f14d9b85f0ca45d4aefc0483436aa5aed87e7722b8fadf44e08d76208` (`Dozent_ESP32/Werkzeuge/cp210x_holen_1.1.py` holt ihn) | `Installation/Werkzeuge/PC_einrichten/pakete/CP210x_Universal_Windows_Driver.zip` |

## Was man über die Hardware wissen sollte

- **CH340-Falle:** Manche USB-Wandler auf dem ESP32-CAM-MB lassen sich nach dem Einstecken nicht direkt mit 115200 Baud
  öffnen (Windows: „Ein an das System angeschlossenes Gerät funktioniert nicht“). Erst mit 9600 Baud öffnen hilft – die
  Werkzeuge hier tun das selbst.
- **Nach dem Einstecken** steht die Kamera im Download-Modus; einmal RST drücken oder die Startdatei benutzen (sie startet
  die Kamera per Software neu).
- **Thonny** muss `dtr = False, rts = False` haben, sonst hält es die Kamera im Reset – `Teilnehmer_1_…` stellt das ein.
- Bei **Stop** schaltet `kamera.py` die Kamera ab; ohne das startet der Kameratreiber nach Thonnys Soft-Reboot nicht wieder.

## Lizenz

MIT (siehe `LICENSE`). `ssd1306.py` stammt aus micropython-lib (MIT). MicroPython und der Kameratreiber gehören ihren
Urhebern (Lizenzen auf deren Projektseiten).

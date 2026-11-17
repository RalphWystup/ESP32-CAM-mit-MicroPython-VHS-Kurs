# ESP32-CAM mit MicroPython – VHS-Kurs

**Prof. Dr.-Ing. Ralph Wystup M.Sc. — erstellt mit KI und Agent (Claude Code, Anthropic)**

Kursmaterial für einen Einsteigerkurs: Eine ESP32-CAM (AI Thinker, auf dem USB-Brett ESP32-CAM-MB) wird mit
MicroPython betrieben und in **Python** programmiert. Die Kamera spannt ein eigenes WLAN auf (`VHS-CAM-<Nr>`) und zeigt
ihr Livebild im Browser unter `http://192.168.4.1/`. Dazu drei kleine Beispiele (LED blinkt, PWM, LED vom Handy schalten).
Gearbeitet wird mit **Thonny**.

Stand 17.11.2026 · Anleitung Fassung 1.8 · Kameraprogramm 1.6 · Installationsseite 1.4

Anleitung als Seite: <https://ralphwystup.github.io/ESP32-CAM-mit-MicroPython-VHS-Kurs/> · als PDF: `LIESMICH_1.8.pdf`,
für Teilnehmer: `Teilnehmer/LIESMICH_Teilnehmer_1.3.pdf`.

## Aufbau

| Ordner | Inhalt |
|---|---|
| `Teilnehmer/` | `Teilnehmer_1_PC_einrichten_1.6.bat` (einmal: Thonny, Python-Pakete, USB-Treiber, Thonny-Einstellung – nur was fehlt), `Teilnehmer_2_Thonny_mit_Kamera_starten_1.4.bat` (jedes Mal: Kamera vorbereiten, Thonny öffnen), Anleitung, `Kameraprogramme/` zum Lesen, `Werkzeuge/` |
| `Dozent/` | `Dozent_Kameras_installieren_1.4.bat` – Installationsseite im Browser (`http://127.0.0.1:8765/`): Kamera anstecken, Nummer eintragen, Knopf drücken; flasht werksfrische Kameras, spielt die Programme auf und macht einen Probelauf wie in Thonny. `Kameraprogramme/`, `Werkzeuge/` |

Auf jede Kamera kommen `kamera.py` (Kameraprogramm), `blink.py`, `pwm.py`, `led_handy.py`, `ssd1306.py` (OLED-Treiber)
und `kamera.json` (Name). Gestartet wird in Thonny mit dem grünen Start-Knopf; es gibt bewusst kein `main.py`.

## Nicht im Repositorium (Fremddateien) – so kommen sie dazu

| Datei | Woher | Wohin |
|---|---|---|
| `firmware.bin` – MicroPython 1.27 mit Kameratreiber | <https://github.com/cnadler86/micropython-camera-API/releases/tag/v0.6.2>, Datei `mpy_cam-v1.27.0-AI_THINKER.zip` entpacken; SHA-256 von `firmware.bin`: `b26ba45de13549272d888c229c5c3864b75250471ac290478d752b8098ee70ea` | `Dozent/Kameraprogramme/` |
| Thonny 5.0.1, CH340-Treiber | lädt `Teilnehmer_1_PC_einrichten_1.6.bat` selbst von GitHub bzw. WCH; für Rechner ohne Internet vorher `Dozent/Werkzeuge/esp_pakete_holen_1.2.py` | `Teilnehmer/pakete/` |

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

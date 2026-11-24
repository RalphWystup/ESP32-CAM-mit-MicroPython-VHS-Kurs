---
title: "ESP32-CAM Bewegungsmelder mit Bildübertragung"
subtitle: "VHS-Kurs „ESP32-CAM mit MicroPython“ · Fassung 1.4 vom 20.11.2026"
author: "Prof. Dr.-Ing. Ralph Wystup M.Sc. · Mitarbeit: Claude (Anthropic, Claude Code)"
lang: de
---

# Was es tut

Die Kamera spannt ihr eigenes WLAN auf und beobachtet ihr Bildfeld. Erkennt sie eine Bewegung, legt sie genau das Foto
(640 × 480), in dem sie die Bewegung erkannt hat, zum Abholen bereit. Die Seite im Browser holt jedes neue Foto über WLAN,
zeigt es groß und sammelt es in einer Galerie. **Erst wenn das Foto auf der Seite angekommen ist**, meldet die Seite das der
Kamera, und die weiße LED blitzt einmal kurz. Ein Blitz heißt also: Das Bild ist wirklich da.

**Die Kamera liefert die Seite selbst aus.** Man braucht am PC oder Handy keine Datei: Man wählt das WLAN der Kamera und
öffnet im Browser `http://192.168.4.1/`. Über diese Seite wird alles bedient: Wächter an/aus, Foto jetzt, LED-Test und
die Einstellungen.

Das Programm liegt auf der Kamera als `main.py` und startet nach jedem Einschalten von selbst.

# Dateien im Ordner `C:\VHS_Kurs\ESP32CAM Bewegungsmelder`

| Datei | Wofür |
|:--|:--|
| `esp_cam_bewegung_1.4.py` | Kameraprogramm (MicroPython); kommt als **`main.py`** auf die Kamera |
| `anzeige_bewegung_1.2.html` | Anzeige- und Steuerseite; kommt als **`anzeige.html`** auf die Kamera |
| `kameraprobe_1.0.py` | Probe für Thonny: kann die Kamera alles, was das Programm braucht? |
| `LIESMICH_Bewegungsmelder_1.4.md` / `.pdf` | diese Anleitung |
| `pruefung\` | Prüfläufe (PC-Nachbau, Browserprüfung, echte Kamera) für den Dozenten |
| `alt\` | frühere Fassungen 1.0–1.3 und Seiten 1.0–1.1 |

# Einmal einrichten (mit Thonny)

**Voraussetzung:** Kamera mit MicroPython 1.27 und Kameratreiber von cnadler86 (wie im Kurs eingerichtet; die
`kameraprobe_1.0.py` prüft das).

1. Kamera mit USB anstecken, Thonny öffnen.
2. Unten rechts **„MicroPython (ESP32) · COM…“** wählen (nicht „Lokales Python“). Auf **Stop** klicken, bis `>>>` erscheint.
3. **Datei → Öffnen → Dieser Computer** → `esp_cam_bewegung_1.4.py`.\
   **Datei → Speichern unter → MicroPython-Gerät**, Name **`main.py`**.
4. **Datei → Öffnen → Dieser Computer** → `anzeige_bewegung_1.2.html`.\
   **Datei → Speichern unter → MicroPython-Gerät**, Name **`anzeige.html`**.
5. In Thonny **Strg+D** drücken. Die Kamera startet neu, `main.py` läuft an, unten steht der Kasten mit der Adresse.

# Benutzen

1. Kamera einschalten (USB-Netzteil oder PC). Das Programm startet von selbst.
2. Am Handy oder PC das WLAN der Kamera wählen, z. B. **`VHS-CAM-3`** (offen, ohne Kennwort). Fragt das Handy
   „Kein Internet – trotzdem verbinden?“: **Ja**.
3. Im Browser **`http://192.168.4.1/`** öffnen. Der Empfang startet von selbst.
4. Vor der Kamera bewegen: Das Foto erscheint, danach blitzt die LED.

**Verbindung reißt ab** (Handy verlässt das WLAN, Kamera kurz ohne Strom): Die Seite meldet nach drei Fehlversuchen
„Verbindung unterbrochen – verbinde automatisch neu (Versuch N)“ und fragt jede Sekunde weiter. Ist die Kamera wieder
erreichbar, steht im Protokoll „Verbindung wieder da – automatisch neu verbunden“, und Bilder, die inzwischen entstanden
sind, werden nachgeholt. Man muss nichts drücken.

**Achtung bei einem Laptop mit Brücke oder Internetverbindung:** Wechselt er ins WLAN der Kamera, verliert er sein
normales Netz. Für die Seite lieber das Handy oder einen zweiten Rechner nehmen.

## Die Adresse ablesen

Die Kamera schreibt ihre Adresse über USB:

- beim Start in einem Kasten: `#  2. Im Browser öffnen: http://192.168.4.1/`,
- danach alle 5 s die Zeile `KAMERA-URL http://192.168.4.1/ WLAN VHS-CAM-3`.

In Thonny sieht man das unten im Fenster. Beim Verbinden hält Thonny ein laufendes `main.py` an; dann **Strg+D** drücken,
die Kamera startet neu und schreibt die Adresse. Jedes andere serielle Terminal mit 115200 Baud geht auch.

## Die Seite

| Bereich | Knöpfe und Anzeigen |
|:--|:--|
| links: 1 · Adresse über USB | nur wenn die Seite als Datei vom PC kommt (Chrome/Edge); von der Kamera: „nicht nötig“ |
| links: 2 · Bilder über WLAN | Adresse, Empfang starten / Anhalten |
| links: 3 · Bilder speichern | Speicherordner (nur als Datei vom PC); **angezeigtes Bild herunterladen** (immer) |
| Mitte | großes Bild, darunter die Galerie; Klick auf ein Galeriebild zeigt es groß |
| rechts: Kamera steuern | **Wächter an / aus**, **Foto jetzt**, **LED-Test**, Einstellungen, **Einstellungen übertragen** |
| rechts: Zähler | empfangene Bilder, Zeit, Größe, Anteil, **Übertragungsdauer**; Prüfbilder, Bildfehler, freier Speicher, Laufzeit der Kamera |

Gesperrte Knöpfe sagen beim Darüberfahren, warum sie gesperrt sind. Die Einstellungen speichert die Kamera in
`einstellungen.json`; sie gelten auch nach dem nächsten Einschalten. Ein Wert außerhalb der Grenzen wird nicht übertragen.

# Einstellungen

| Name | Vorgabe | Grenzen | Bedeutung |
|:--|:--|:--|:--|
| Schwelle | 25 | 5 … 100 | Graustufen (0…255), ab der ein Messpunkt als verändert zählt |
| Anteil | 2 % | 0,5 … 50 % | Anteil veränderter Messpunkte für „Bewegung“ (2 % = 24 von 1200) |
| Ruhe | 3 s | 1 … 60 s | Mindestabstand zweier Bewegungsbilder |
| Blitz | 120 ms | 20 … 1000 ms | Dauer des LED-Blitzes |

**So wird gerechnet:** Die Kamera nimmt immer Fotos 640 × 480 (JPEG) auf und wird nie umgeschaltet. Jedes Foto wird auf
dem Chip auf 160 × 120 verkleinert entpackt (Modul `jpeg`, nur die Helligkeit), davon jeder 4. Punkt in beide Richtungen,
also 40 × 30 = 1200 Messpunkte; etwa 3 Prüfbilder je Sekunde. Vom Unterschied zum Hintergrund wird zuerst die mittlere
Helligkeitsänderung abgezogen (die Kamera regelt die Belichtung nach – das ist keine Bewegung). Ein Gegenstand von
40 × 40 Punkten des verkleinerten Bilds trifft 10 × 10 = 100 Messpunkte = 8,3 % und löst aus; einer von 8 × 8 trifft
4 Messpunkte = 0,3 % und löst nicht aus. Der Hintergrund läuft langsam mit (¾ alt + ¼ neu). Nach jedem Bewegungsbild und
nach jedem Blitz lernt die Kamera den Hintergrund neu, damit der eigene Blitz nicht als Bewegung zählt.

# Adressen der Kamera

| Adresse | Inhalt |
|:--|:--|
| `http://192.168.4.1/` | Anzeige- und Steuerseite (`anzeige.html` aus dem Flash; fehlt sie: kurze Notseite) |
| `/ereignis` | Nummer, Alter, Größe des letzten Bilds (JSON) |
| `/letztes.jpg` | letztes Bild (in Stücken zu 4 KB; während der Übertragung pausiert die Erkennung) |
| `/gesehen?nr=N` | Seite meldet: Bild N ist angekommen → LED blitzt (nur einmal je Bild) |
| `/status` | Wächter, Zähler, Einstellungen, freier Speicher, Laufzeit (JSON) |
| `/steuern?…` | Wächter und Einstellungen setzen, z. B. `?wache=0` oder `?schwelle=30&ruhe_ms=2000`; Namen: `wache`, `schwelle`, `anteil`, `ruhe_ms`, `blitz_ms` |
| `/foto` | jetzt ein Foto machen (zählt wie eine Bewegung, Anteil 0) |
| `/blitz` | LED-Test |

# Wenn etwas nicht geht

| Meldung | Was die Kamera tut | Was man tut |
|:--|:--|:--|
| „Kamera startet nicht … Sensor aus/an“ | schaltet den Bildsensor über GPIO 32 kurz ab und versucht es bis zu dreimal | nichts |
| „Gerät startet in 3 s neu“ | Neustart wie die RST-Taste; `main.py` läuft danach von allein | nichts; hilft es mehrmals nicht: USB 5 s abziehen |
| „Kamera liefert keine Bilder – wird neu gestartet“ | nach 5 Fehlbildern hintereinander | nichts |
| Seite: „Verbindung unterbrochen – verbinde automatisch neu“ | – | warten; dauert es länger: WLAN der Kamera gewählt? Adresse `http://192.168.4.1/`? |
| Seite: „Bild Nr. N kam nicht an … neuer Versuch“ | – | nichts; die Seite holt das Bild noch einmal (Frist 20 s je Bild) |
| LED blitzt, aber kein Bild | kommt mit Fassung 1.4 nicht mehr vor: Blitz erst nach Ankunft | melden |

# Geprüft (20.11.2026)

**An der echten Kamera** (AI Thinker, MicroPython 1.27 mit SPIRAM, über USB am Laptop):

- **Fassung 1.4 aufgespielt:** `main.py` und `anzeige.html` auf der Kamera gleich den Dateien (Prüfsumme); die bisherige
  Fassung liegt auf der Kamera als `main_1.3.py` und `anzeige_1.1.html`. Nach Neustart wie RST: Programm lief an, Adresse
  ausgegeben, echte Bewegung erkannt.
- **Test durch den Dozenten am 20.11.2026:** Bilder kommen auf der Seite an, die LED blitzt danach.
- **Neustarts (Fassung 1.3, gleicher Startteil):** 7 von 7 RICHTIG\
  (`pruefung/echte_kamera_neustarttest_1.3.out`).
- **Webserver (Fassung 1.3):** Seite vollständig aus dem Flash, Steuern, falscher Wert abgewiesen, Foto, LED-Test, echte
  Bewegung
  (`pruefung/echte_kamera_webtest_1.3.out`).
- **Dauerlauf** (Fassung 1.2, gleiche Erkennung): 4 Minuten, 789 Prüfbilder, 0 Fehler, Speicher gleichbleibend.
- **Hängender Sensor:** Abschalten über GPIO 32 für 300 ms holt ihn zurück; daher `powerdown_pin=32` und bis zu drei
  Versuche beim Start. Was den Sensor hängen ließ, ist nicht gemessen.

**Der Fehler aus Fassung 1.3** („LED blitzt, aber keine Bilder“) wurde am PC nachgestellt: Bei langsamem WLAN (4 kB/s)
gab die Seite nach 3 s auf, die Kamera blitzte trotzdem\
(`pruefung/nachstellung_alt_1.3_langsam.out`). Seit 1.4 / Seite
1.2: Blitz erst nach der Rückmeldung der Seite, Fristen 4 s je Abfrage und 20 s je Bild, erst nach drei Fehlversuchen eine
Meldung, danach selbsttätig neu verbinden.

**Am PC** (nachgebildete Kamera `pruefung/sim_kamera_1.5.py` mit Programm 1.4, Chromium ohne Grafikbeschleunigung,
Skalierung 1 und 1,5):

- Seite **von der Kamera ausgeliefert**, Netz ungedrosselt und gedrosselt auf 4 kB/s, je 26 Prüfpunkte RICHTIG
  (`pruefung/knopfprobe_kameraseite_1.2_0kBs_endstand.out`, `…_4kBs_lauf2.out`). Darunter: Empfang startet von selbst,
  LED blitzt nur für angekommene Bilder, **Netz 12 s weg**: „unterbrochen – verbinde automatisch neu“, danach von selbst
  wieder verbunden, nächstes Bild kommt an; kein Rollbalken bei 1280 × 720.
- Seite **als Datei vom PC**: 58 Prüfpunkte RICHTIG (`pruefung/knopfprobe_anzeige_1.2_pcdatei.out`).
- Steuerbefehle einzeln (`pruefung/sim_1.4_steuern.out`); Sicherungswege Kamera-Neustart und Geräte-Neustart
  (`sim_1.3_luecke.out`, `sim_1.3_kaputt.out`).

# Fassungen

| Fassung | Was neu ist |
|:--|:--|
| 1.4 / Seite 1.2 (20.11.2026) | LED blitzt erst, wenn die Seite das Bild bestätigt; längere Fristen für langsames WLAN; automatisch neu verbinden nach Abbruch; Übertragungsdauer im Zähler |
| 1.3 / Seite 1.1 (20.11.2026) | `main.py` startet von selbst; Seite kommt von der Kamera; alles über die Seite steuerbar; Sensor-Abschaltung GPIO 32 |
| 1.2 (20.11.2026) | Kamera fest JPEG statt Umschalten Graubild ↔ JPEG (Umschalten scheiterte im Dauerlauf an der echten Kamera) |
| 1.1 (20.11.2026) | LED blitzt nach der Übertragung statt vor dem Foto |
| 1.0 (18.11.2026) | erste Fassung |

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""esp_thonny_einstellen_1.2.py -- auf dem PC: stellt in Thonnys configuration.ini (Abschnitt [ESP32]) dtr = False und rts = False ein.
Warum: Thonny 5.0.1 öffnet den Anschluss mit den Vorgaben ESP32.dtr/ESP32.rts = None, dann schaltet pyserial beide Leitungen EIN; auf dem
ESP32-CAM-MB-Brett hängen sie an EN/IO0 und halten die Kamera im Reset -> „Device is busy or does not respond“ (gemessen 17.11.2026).
Quelle: thonny/plugins/micropython/serial_connection.py und mp_front.py (Optionen <backend>.dtr / <backend>.rts).
Nur wenn Thonny NICHT läuft (es schreibt die Datei beim Beenden neu); alte Datei vorher als configuration_vor_esp_<Zeit>.ini gesichert;
fehlt die Datei (Thonny nie gestartet), wird sie mit nur diesem Abschnitt angelegt. 17.11.2026.
1.2 (17.11.2026, sein Wort „wenn dann die cam über usb verbunden wird sollen sie nur den start knopf drücken müssen“): zusätzlich
[run] backend_name = ESP32 (Thonny startet gleich mit MicroPython auf der Kamera) und [ESP32] port = auto, falls dort noch nichts steht
(Thonny erkennt CH340/CP210x selbst; ein eingetragener Anschluss bleibt).
1.1: ist beides schon False, nichts tun -- auch wenn Thonny läuft (1.0 meldete dann einen Fehler).
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import configparser, datetime, os, shutil, subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ordner = os.path.join(os.environ["APPDATA"], "Thonny"); datei = os.path.join(ordner, "configuration.ini"); os.makedirs(ordner, exist_ok=True)
c = configparser.ConfigParser(interpolation=None); c.optionxform = str
if os.path.isfile(datei): c.read(datei, encoding="utf-8")
if (c.get("ESP32", "dtr", fallback="") == "False" and c.get("ESP32", "rts", fallback="") == "False" and c.get("run", "backend_name", fallback="") == "ESP32"
        and c.get("ESP32", "port", fallback="")):
    print("Thonny ist schon eingestellt (MicroPython ESP32, DTR/RTS aus) -- nichts zu tun."); sys.exit(0)
laeuft = "thonny.exe" in subprocess.run(["tasklist", "/fi", "imagename eq thonny.exe"], capture_output=True, text=True, errors="replace").stdout.lower()
if laeuft: print("Thonny läuft -- bitte Thonny schließen und erneut starten (sonst überschreibt Thonny die Einstellung beim Beenden)."); sys.exit(1)
c = configparser.ConfigParser(interpolation=None); c.optionxform = str
if os.path.isfile(datei):
    sich = os.path.join(ordner, f"configuration_vor_esp_{datetime.datetime.now():%Y-%m-%d_%H%M%S}.ini"); shutil.copy2(datei, sich); print("gesichert:", sich)
    c.read(datei, encoding="utf-8")
if not c.has_section("ESP32"): c.add_section("ESP32")
vorher = {k: c.get("ESP32", k, fallback="(nicht gesetzt)") for k in ("dtr", "rts")}
c.set("ESP32", "dtr", "False"); c.set("ESP32", "rts", "False")
if not c.get("ESP32", "port", fallback=""): c.set("ESP32", "port", "auto")
if not c.has_section("run"): c.add_section("run")
b_vorher = c.get("run", "backend_name", fallback="(nicht gesetzt)"); c.set("run", "backend_name", "ESP32")
with open(datei, "w", encoding="utf-8") as f: c.write(f)
print(f"Thonny eingestellt: Interpreter {b_vorher} -> MicroPython (ESP32), Anschluss {c.get('ESP32', 'port')}, dtr {vorher['dtr']} -> False, rts {vorher['rts']} -> False\n  ({datei})")

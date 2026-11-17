#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""esp_pakete_holen_1.2.py -- auf dem PC: legt die Installationsdateien für die Kursteilnehmer in C:\\VHS_Kurs\\pakete ab, damit
esp_kurs_einrichten auch ohne Internet läuft: Thonny 5.0.1 (GitHub) und CH340-Treiber CH341SER.ZIP 4.0.2026.02 (WCH), beide mit SHA-256
geprüft; CP210x (Silicon Labs) wird versucht, der Hersteller sperrt Skript-Downloads (Access Denied) -- dann von Hand im Browser laden.
Überschreibt nichts. 1.1: Ziel Teilnehmer\\pakete (Ordnergliederung 17.11.2026), das Skript liegt in Dozent\\. 17.11.2026, sein Wort: „am besten die Treibern gleich mit runterladen in den pordner für die Teinnehmer und Thonny auch“.
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import hashlib, os, sys, urllib.request
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ZIEL = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Teilnehmer", "pakete")   # 1.2: aus Dozent\Werkzeuge -> ..\..\Teilnehmer\pakete
DATEIEN = [("thonny-5.0.1-x64.exe", "https://github.com/thonny/thonny/releases/download/v5.0.1/thonny-5.0.1-x64.exe",
            "a2b04784cd2ee7d4c22ed46865de5e8ba6eaf55950543ef9546374f53cf778a5"),
           ("CH341SER.ZIP", "https://www.wch-ic.com/download/file?id=5", "59967d9ce371d0bf3df02dec0b66c8dfbf9ca576da0572ff4404148a7c381807"),
           ("CP210x_Universal_Windows_Driver.zip", "https://www.silabs.com/documents/public/software/CP210x_Universal_Windows_Driver.zip", None)]
os.makedirs(ZIEL, exist_ok=True)
for name, url, soll in DATEIEN:
    z = os.path.join(ZIEL, name)
    if os.path.exists(z): print("schon da, nicht überschrieben:", name); continue
    try:
        d = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
    except Exception as e:
        print(f"{name}: nicht zu bekommen ({str(e)[:80]})" + (" -- von Hand im Browser laden: https://www.silabs.com/developer-tools/usb-to-uart-bridge-vcp-drivers" if "silabs" in url else "")); continue
    h = hashlib.sha256(d).hexdigest()
    if soll and h != soll: print(f"{name}: FALSCHE Prüfsumme {h} -- nicht abgelegt"); continue
    if d[:2] != b"PK" and name.lower().endswith(".zip"): print(f"{name}: kein ZIP (Sperrseite des Herstellers?) -- nicht abgelegt"); continue
    open(z, "wb").write(d); print(f"abgelegt: {name} ({len(d)} Byte, SHA-256 {h[:16]}…{' geprüft' if soll else ''})")
print("Inhalt", ZIEL, ":", sorted(os.listdir(ZIEL)))

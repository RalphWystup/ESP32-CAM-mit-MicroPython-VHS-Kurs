#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""esp_kurs_pruefen_1.0.py -- für Kursteilnehmer: Thonny-Fassung, Python, Pakete pyserial/esptool und serielle Anschlüsse anzeigen. Ändert
nichts. (Kursfassung von esp_pc_pruefen_1.0.py, ohne Zugangsblatt.) 17.11.2026.
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import importlib.metadata as md
def fassung(p):
    try: return md.version(p)
    except Exception: return "FEHLT"
print("Thonny", fassung("thonny"), "| Python", sys.version.split()[0], "|", sys.executable)
print("pyserial", fassung("pyserial"), "| esptool", fassung("esptool"))
try:
    from serial.tools import list_ports
    ps = list(list_ports.comports())
    for p in ps:
        art = "CH340 (ESP32-CAM-Brett)" if "1A86" in (p.hwid or "").upper() else ("CP210x" if "10C4" in (p.hwid or "").upper() else "")
        print("Anschluss", p.device, "|", p.description, "|", art)
    if not ps: print("Kein serieller Anschluss gefunden -- Kamera eingesteckt? USB-Kabel mit Datenleitungen?")
except Exception as e: print("Anschlüsse nicht lesbar:", e)

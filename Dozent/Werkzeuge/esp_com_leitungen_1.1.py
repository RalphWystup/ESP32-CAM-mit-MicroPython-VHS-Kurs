#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""esp_com_leitungen_1.1.py -- auf dem PC: was nimmt der CH340 an COM5 an? Von harmlos nach riskant, Abbruch beim ERSTEN Fehler (ein
abgelehnter Einstellversuch legt diesen Wandler bis zum Neustecken lahm, gemessen 17.11.2026). Schreibt nichts aufs Gerät; DTR/RTS-Schalten
kann die ESP32-CAM zurücksetzen. 1.1: Abbruch beim ersten Fehler (1.0 öffnete nach einem Fehler gar nicht mehr).
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import serial
s = serial.Serial(); s.port = "COM5"; s.baudrate = 115200; s.timeout = 0.2; s.dtr = False; s.rts = False
schritte = [("öffnen 115200, DTR/RTS aus", s.open), ("DTR an", lambda: setattr(s, "dtr", True)), ("DTR aus", lambda: setattr(s, "dtr", False)),
            ("RTS an", lambda: setattr(s, "rts", True)), ("RTS aus", lambda: setattr(s, "rts", False))]
schritte += [(f"Baud {b}", (lambda b=b: setattr(s, "baudrate", b))) for b in (57600, 230400, 250000, 460800, 921600)]
for name, f in schritte:
    try: f(); print("OK     ", name, flush=True)
    except Exception as e: print("FEHLER ", name, "--", str(e)[:110], "\n(Abbruch: Wandler jetzt vermutlich bis zum Neustecken gesperrt)"); break
try: s.close()
except Exception: pass

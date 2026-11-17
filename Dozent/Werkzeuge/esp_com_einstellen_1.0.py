#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""esp_com_einstellen_1.0.py -- auf dem PC: COM5 mit verschiedenen Einstellungen öffnen (Baudraten, mit/ohne DTR/RTS-Steuerung), und über
.NET System.IO.Ports als zweiten, unabhängigen Weg. Liest nur, schreibt nichts aufs Gerät. 17.11.2026 (PermissionError 31 „Cannot configure port“).
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import serial
for baud in (9600, 115200, 460800):
    for dsr in (False,):
        try:
            s = serial.Serial(); s.port = "COM5"; s.baudrate = baud; s.timeout = 0.3; s.dtr = False; s.rts = False; s.open()
            d = s.read(200); s.close(); print(f"pyserial {baud}: OFFEN, {len(d)} Byte gelesen")
        except Exception as e: print(f"pyserial {baud}: {type(e).__name__}: {e}")
c = ("$p = New-Object System.IO.Ports.SerialPort 'COM5',115200; $p.ReadTimeout = 300; "
     "try { $p.Open(); 'NET: OFFEN'; $p.Close() } catch { 'NET: ' + $_.Exception.Message }")
r = subprocess.run(["powershell", "-NoProfile", "-Command", c], capture_output=True, text=True, encoding="utf-8", errors="replace"); print((r.stdout + r.stderr).strip())
r = subprocess.run("mode COM5", shell=True, capture_output=True, text=True, encoding="cp850", errors="replace"); print("mode COM5:", (r.stdout + r.stderr).strip()[-600:])

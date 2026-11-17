#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""esp_autoreset_pruefen_1.0.py -- auf dem PC: kommt die ESP32-CAM auf dem MB-Brett über DTR/RTS (esptool default-reset) von selbst in den
Flash-Modus? Vorlauf 9600/115200, dann esptool flash-id mit automatischem Reset und hard-reset danach. Liest nur, schreibt nichts. 17.11.2026.
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import serial
from serial.tools import list_ports
port = next((p.device for p in list_ports.comports() if "1A86" in (p.hwid or "").upper()), "COM5")
for b in (9600, 115200):
    s = serial.Serial(); s.port = port; s.baudrate = b; s.timeout = 0.2; s.dtr = False; s.rts = False; s.open(); s.close()
r = subprocess.run([sys.executable, "-m", "esptool", "--chip", "esp32", "--port", port, "--baud", "115200", "flash-id"], capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
print(port, "Rückgabe", r.returncode); print((r.stdout + r.stderr)[-1500:])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""esp32_brett_abfragen_1.0.py (24.11.2026) -- auf dem PC: ein ESP32-Brett am angegebenen Anschluss abfragen, ohne etwas zu ändern:
(1) esptool flash-id (Chip, Flash-Größe, MAC), (2) nach dem Reset: steht MicroPython drauf? (Raw-REPL, Fassung, Dateien).
Aufruf: python esp32_brett_abfragen_1.0.py COM5
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import subprocess, sys, time, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
PORT = sys.argv[1] if len(sys.argv) > 1 else "COM5"
PY = None
for d in (os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Thonny"), r"C:\Program Files\Thonny", r"C:\Program Files (x86)\Thonny"):
    if os.path.isfile(os.path.join(d, "python.exe")): PY = os.path.join(d, "python.exe"); break
print("Thonny-Python:", PY)
print("== esptool flash-id an", PORT, flush=True)
r = subprocess.run([PY or sys.executable, "-m", "esptool", "--chip", "auto", "--port", PORT, "--baud", "115200", "flash-id"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90)
txt = (r.stdout + r.stderr)
for z in txt.splitlines():
    if any(k in z for k in ("Chip", "chip", "Detecting", "MAC", "Flash", "flash", "Crystal", "Features", "Manufacturer", "Device", "error", "Error", "fatal")): print("  ", z.strip()[:140])
print("   rc =", r.returncode, flush=True)
print("== MicroPython?", flush=True)
try:
    import serial
    s = serial.Serial(); s.port = PORT; s.baudrate = 115200; s.timeout = 0.3; s.dtr = False; s.rts = False; s.open()
    s.dtr = False; s.rts = True; time.sleep(0.15); s.rts = False; time.sleep(2.5); boot = s.read(6000).decode("utf-8", "replace")
    print("   Bootmeldung (Auszug):"); [print("     ", z[:120]) for z in boot.splitlines() if z.strip()][:12]
    s.write(b"\r\x03\x03"); time.sleep(0.3); s.reset_input_buffer(); s.write(b"\r\x01"); time.sleep(0.5); p = s.read(300)
    if b"raw REPL" in p:
        s.write(b"import sys, os\nprint(sys.implementation, sys.platform)\nprint(sorted(os.listdir()))\ntry:\n import camera; print('Kameratreiber da')\nexcept ImportError:\n print('kein Kameratreiber')\n\x04"); time.sleep(1.5)
        print("   Raw-REPL ok:"); [print("     ", z[:140]) for z in s.read(4000).decode("utf-8", "replace").replace("\x04", "\n").splitlines() if z.strip()]
        s.write(b"\x02")
    else: print("   kein Raw-REPL (keine MicroPython-Antwort):", p[:120])
    s.close()
except Exception as e: print("   Fehler:", str(e)[:200])

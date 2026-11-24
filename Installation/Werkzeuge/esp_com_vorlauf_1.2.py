#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==========================================================================================================
#  VHS-Kurs  „ESP32-CAM mit MicroPython“  –  Anschluss der Kamera vorbereiten  (esp_com_vorlauf_1.2.py)
#  Autor: Prof. Dr.-Ing. Ralph Wystup M.Sc.  ·  Mitarbeit: Claude (Anthropic, Claude Code)  ·  Fassung 1.2 vom 17.11.2026
# ----------------------------------------------------------------------------------------------------------
#  Sucht die Kamera (USB-Wandler CH340 = 1A86 oder CP210x = 10C4) und öffnet ihren Anschluss erst mit 9600, dann mit 115200 Baud,
#  DTR/RTS aus. Danach verbindet Thonny ohne „Ein an das System angeschlossenes Gerät funktioniert nicht“ (CH340-Falle). Ändert nichts.
#  1.2: danach RST per Software (RTS-Puls bei DTR aus): nach dem Einstecken steht die Kamera auf dem MB-Brett im Bootlader
#       (Thonny: „Device is busy“) -- gemessen 17.11.2026. 1.1: Anschluss automatisch (1.0: fest COM5). Aufruf: python esp_com_vorlauf_1.2.py [COMx]
# ==========================================================================================================
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import serial
from serial.tools import list_ports
if len(sys.argv) > 1: port, art = sys.argv[1], "vorgegeben"
else:
    k = [(p.device, p.description) for p in list_ports.comports() if any(v in (p.hwid or "").upper() for v in ("1A86", "10C4"))]
    if not k: print("Keine Kamera gefunden -- bitte die ESP32-CAM per USB-Kabel anstecken (Datenkabel, nicht nur Ladekabel)."); sys.exit(1)
    port, art = k[0]
for b in (9600, 115200):
    try:
        s = serial.Serial(); s.port = port; s.baudrate = b; s.timeout = 0.2; s.dtr = False; s.rts = False; s.open(); s.close()
    except Exception as e:
        print(f"{port}: lässt sich nicht öffnen ({str(e)[:90]}).\nThonny schließen, Kabel ab- und wieder anstecken, dann noch einmal."); sys.exit(1)
import time
try:
    s = serial.Serial(); s.port = port; s.baudrate = 115200; s.timeout = 0.3; s.dtr = False; s.rts = False; s.open()
    s.rts = True; time.sleep(0.15); s.rts = False; time.sleep(2.5); boot = s.read(4000); s.close()
    ok = b"MicroPython" in boot
except Exception as e:
    ok = False; print("Neustart der Kamera nicht möglich:", str(e)[:80])
print(f"Kamera an {port} ({art}) -- Anschluss vorbereitet" + (", Kamera neu gestartet (MicroPython meldet sich)." if ok else
      ". Die Kamera hat sich nicht gemeldet -- in Thonny Stop drücken; hilft das nicht, RST an der Kamera drücken."))
print(f"In Thonny: unten rechts „MicroPython (ESP32)“ und {port} wählen, dann Stop klicken.")

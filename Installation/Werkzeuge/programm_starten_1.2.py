#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==========================================================================================================
#  VHS-Kurs  „ESP32-CAM und ESP32 mit MicroPython“
#  Programm auf dem Brett starten – ohne Thonny  (programm_starten_1.2.py)
# ----------------------------------------------------------------------------------------------------------
#  Autor:      Prof. Dr.-Ing. Ralph Wystup M.Sc.
#  Mitarbeit:  Claude (Anthropic, Claude Code)
#  Fassung:    1.2 vom 24.11.2026 -- nach dem Stop ein Soft-Reboot (Strg+D) wie Thonnys „Stop“: sonst hält ein weiterlaufender Faden (Webserver von
#              led_handy.py) den Port 80, und das nächste Programm meldet EADDRINUSE (am 24.11. an der Kamera gesehen).  1.1: bei mehreren Brettern Handauswahl des Anschlusses (sein Wort: „sonst eine Handauswahl einführen?“).  1.0: sein Wort: „Programme auf dem esp32 testen, geht das auch ohne Thonny? also testprogramm
#              auswählen und starten von hand und von dir zum test“
# ----------------------------------------------------------------------------------------------------------
#  Startet eine Datei, die auf dem Brett liegt, so wie der grüne Start-Knopf in Thonny (Raw-REPL: exec(open(name).read())),
#  liest die Ausgabe einige Sekunden mit und beendet das Programm mit Strg+C (wie „Stop“). Ohne Dateiname: zeigt, was auf dem
#  Brett liegt. Der Anschluss wird gesucht (CH340 = USB 1A86, CP210x = 10C4), wenn keiner angegeben ist.
#  Aufruf: python programm_starten_1.2.py [blink.py] [Sekunden] [COMx]      (Programm_testen.bat fragt danach)
# ==========================================================================================================
import sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
try:
    import serial
    from serial.tools import list_ports
except ImportError:
    print("FEHLER: Paket pyserial fehlt -- zuerst ESP32_installieren.bat ausführen."); sys.exit(1)
arg = [a for a in sys.argv[1:] if a]; name = next((a for a in arg if a.endswith(".py")), None); sek = next((int(a) for a in arg if a.isdigit()), 12); port = next((a for a in arg if a.upper().startswith("COM")), None)
if not port:
    k = [p.device for p in list_ports.comports() if any(v in (p.hwid or "").upper() for v in ("1A86", "10C4"))]
    if not k: print("Kein Brett gefunden (CH340/CP210x). Kabel? Datenkabel?"); sys.exit(1)
    port = k[0]
    if len(k) > 1:
        print("Mehrere Bretter angeschlossen:", ", ".join(k))
        w = input("Welcher Anschluss (Eingabetaste = " + port + ")? ").strip().upper()
        if w in k: port = w
s = serial.Serial(); s.port = port; s.baudrate = 115200; s.timeout = 0.3; s.dtr = False; s.rts = False; s.open()
def bis(ende, frist):
    p = b""; t0 = time.time()
    while time.time() - t0 < frist:
        p += s.read(512)
        if ende in p[-len(ende) - 2:]: break
    return p
def rein():
    s.write(b"\r\x03\x03"); time.sleep(0.3); s.reset_input_buffer()
    for _ in range(3):
        s.write(b"\r\x01")
        if bis(b"raw REPL; CTRL-B to exit\r\n>", 3).endswith(b">"): return True
        s.write(b"\x03\x03"); time.sleep(0.3); s.reset_input_buffer()
    return False
if not rein():
    print("Brett antwortet nicht -- Neustart per Software ...", flush=True); s.dtr = False; s.rts = True; time.sleep(0.15); s.rts = False; time.sleep(2.5); s.read(4000)
    if not rein(): print("Keine MicroPython-Antwort an", port, "-- erst ESP32_installieren.bat ausführen."); sys.exit(1)
if not name:
    s.write(b"import os; print(sorted(os.listdir()))\x04"); time.sleep(1.0); out = s.read(4000).decode("utf-8", "replace")
    print("Auf dem Brett an", port + ":", out.replace("\x04", " ").replace("OK", "").strip()); s.write(b"\x02"); s.close(); sys.exit(0)
print(f"Starte {name} auf {port} für {sek} s (dann Stop wie in Thonny) ...", flush=True)
s.write(f"exec(open({name!r}).read(), {{'__name__': '__main__'}})\x04".encode())
if s.read(2) != b"OK": print("nicht angenommen -- liegt die Datei auf dem Brett?"); s.close(); sys.exit(1)
t0 = time.time(); p = b""; fertig = False
while time.time() - t0 < sek:
    c = s.read(512)
    if c:
        p += c; sys.stdout.write(c.decode("utf-8", "replace").replace("\x04", "\n")); sys.stdout.flush()
        if b"\x04>" in p[-4:]: fertig = True; break   # Programm endete von selbst
if not fertig:
    s.write(b"\x03"); time.sleep(1.5); q = s.read(4000).decode("utf-8", "replace"); print("\n--- Stop (Strg+C) gesendet ---"); print(q.replace("\x04", "\n").strip()[-600:])
    s.write(b"\x03\x03"); time.sleep(0.3); s.write(b"\x02"); time.sleep(0.3); s.reset_input_buffer(); s.write(b"\x04"); time.sleep(2.5); s.read(8000); print("--- Soft-Reboot (wie Thonny nach Stop) ---")
else:
    print("\n--- Programm endete von selbst ---"); s.write(b"\x03\x03"); time.sleep(0.3); s.write(b"\x02"); time.sleep(0.3); s.reset_input_buffer(); s.write(b"\x04"); time.sleep(2.5); s.read(8000)
s.write(b"\x02"); s.close(); print("Ende.")

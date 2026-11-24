#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cam_bild_seriell_1.0.py (24.11.2026) -- auf dem PC, aus C:\\Bruecke: ein Foto von der ESP32-CAM über USB holen, ohne WLAN und ohne Thonny.
Sein Wort: „wenn die cam reagiert kannst du ja zur Probe ein bild holen, sollt meine zimmerdecke mit lampe drauf sein“. Geht wie Programm_testen
in den Raw-REPL von MicroPython, schaltet die Kamera ein (VGA, JPEG wie in esp_cam_kamera_1.6.py), nimmt drei Bilder (das erste ist oft dunkel),
schickt das letzte als Base64 über die Leitung und legt es als JPEG ab. Aufruf: python cam_bild_seriell_1.0.py [COMx] [Zieldatei]
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import sys, time, base64, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import serial
from serial.tools import list_ports
arg = [a for a in sys.argv[1:] if a]; port = next((a for a in arg if a.upper().startswith("COM")), None)
ziel = next((a for a in arg if a.lower().endswith(".jpg")), os.path.join(r"C:\VHS_Kurs", "Misc", "Proben", time.strftime("cam_bild_%Y-%m-%d_%H%M%S.jpg")))
if not port:
    k = [p.device for p in list_ports.comports() if any(v in (p.hwid or "").upper() for v in ("1A86", "10C4"))]
    if not k: print("Kein Brett gefunden (CH340/CP210x)."); sys.exit(1)
    port = k[0]; print("Anschlüsse:", k, "-> genommen:", port)
s = serial.Serial(); s.port = port; s.baudrate = 115200; s.timeout = 0.3; s.dtr = False; s.rts = False; s.open()
def bis(ende, frist):
    p = b""; t0 = time.time()
    while time.time() - t0 < frist:
        p += s.read(4096)
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
    if not rein(): print("Keine MicroPython-Antwort an", port); sys.exit(1)
CODE = r"""
import ubinascii, time
from camera import Camera, PixelFormat, FrameSize
c = None
for versuch in range(2):
    try:
        c = Camera(pixel_format=PixelFormat.JPEG, frame_size=FrameSize.VGA, jpeg_quality=85, fb_count=2); break
    except OSError as e:
        print('Kamera startet nicht:', e, '-- zweiter Versuch')
        try: Camera(init=False).deinit()
        except Exception as e2: print('deinit:', e2)
        time.sleep(1)
if c is None:
    print('KEINE KAMERA')
else:
    b = None
    for _ in range(3):
        b = c.capture(); time.sleep_ms(200)
    print('LEN', len(b))
    print('B64', ubinascii.b2a_base64(b).decode().strip(), 'ENDE')
    c.deinit()
"""
s.reset_input_buffer(); s.write(CODE.encode() + b"\x04")
if bis(b"OK", 3)[-2:] != b"OK": print("Raw-REPL hat den Code nicht angenommen."); sys.exit(1)
aus = bis(b"\x04>", 40).decode("utf-8", "replace")
text = aus.replace("\x04", "\n")
print("Antwort des Bretts (ohne Bilddaten):", " | ".join(z[:120] for z in text.splitlines() if not z.startswith("B64"))[:600])
s.write(b"\x02"); s.close()
if "B64 " in text and " ENDE" in text:
    b64 = text.split("B64 ", 1)[1].split(" ENDE", 1)[0].strip()
    daten = base64.b64decode(b64); os.makedirs(os.path.dirname(ziel), exist_ok=True); open(ziel, "wb").write(daten)
    print("BILD:", ziel, len(daten), "Byte; JPEG-Kopf", daten[:2] == b"\xff\xd8", "Ende", daten[-2:] == b"\xff\xd9")
else:
    print("KEIN BILD erhalten."); sys.exit(2)

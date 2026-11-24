#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vhs_zuschauen_1.0.py (24.11.2026) -- auf dem PC, aus C:\\Bruecke: beim Test von ESP32_Start.bat zuschauen (sein Wort: „ich teste jetzt, schau zu“).
Liest nur: Fenster mit „ESP32 Start“ im Titel, die Installationsseite auf 127.0.0.1:8765 (/zustand, wenn sie läuft), Werkzeuge\\brett.txt und die
Protokolle im Installationsordner. Läuft <Sekunden> (Vorgabe 45) und meldet jede neue Zeile. Greift nichts an.
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import os, sys, time, json, ctypes, urllib.request
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
dauer = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else 45
Z = r"C:\VHS_Kurs\VHS_ESP32_Installation"
def fenster():
    u = ctypes.windll.user32; titel = []
    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def cb(h, _):
        if u.IsWindowVisible(h):
            n = u.GetWindowTextLengthW(h)
            if n:
                b = ctypes.create_unicode_buffer(n + 1); u.GetWindowTextW(h, b, n + 1)
                if any(k in b.value for k in ("ESP32", "Thonny", "installieren", "cmd", "Eingabeaufforderung")): titel.append(b.value[:60])
        return True
    u.EnumWindows(cb, 0); return titel
def zustand():
    try: return json.loads(urllib.request.urlopen("http://127.0.0.1:8765/zustand", timeout=2).read().decode("utf-8", "replace"))
    except Exception: return None
def protokolle():
    aus = {}
    for rel in ("esp32_protokoll.csv", "kameras_protokoll.csv", os.path.join("Werkzeuge", "brett.txt")):
        p = os.path.join(Z, rel)
        if os.path.isfile(p):
            try: aus[rel] = open(p, encoding="utf-8", errors="replace").read().strip().splitlines()[-1][:120]
            except OSError: pass
    pd = os.path.join(Z, "protokoll")
    if os.path.isdir(pd): aus["protokoll/"] = ", ".join(sorted(os.listdir(pd))[-3:])
    return aus
t0 = time.time(); alt_f = None; alt_n = 0; alt_p = None; alt_l = None
print(time.strftime("%H:%M:%S"), "zuschauen", dauer, "s")
while time.time() - t0 < dauer:
    f = fenster()
    if f != alt_f: print(time.strftime("%H:%M:%S"), "Fenster:", f); alt_f = f
    z = zustand()
    if z is None:
        if alt_l is not None: print(time.strftime("%H:%M:%S"), "Seite nicht (mehr) erreichbar"); alt_l = None
    else:
        if alt_l is None: print(time.strftime("%H:%M:%S"), "Seite läuft: laeuft=%s brett=%s nummer=%s" % (z.get("laeuft"), z.get("brett"), z.get("nummer"))); alt_l = True
        zeilen = z.get("zeilen", [])
        for zeile in zeilen[alt_n:]: print("   ", zeile[:150])
        alt_n = len(zeilen)
        if z.get("frage"): print("    FRAGE der Seite:", z["frage"][:150])
        if not z.get("laeuft") and z.get("ergebnis"): print(time.strftime("%H:%M:%S"), "ERGEBNIS:", z["ergebnis"])
    p = protokolle()
    if p != alt_p: print(time.strftime("%H:%M:%S"), "Dateien:", p); alt_p = p
    time.sleep(2)
print(time.strftime("%H:%M:%S"), "Ende des Zuschauens")

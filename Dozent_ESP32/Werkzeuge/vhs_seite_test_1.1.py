#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vhs_seite_test_1.1.py (24.11.2026; 1.1: Seite 1.2) -- auf dem PC, aus C:\\Bruecke: Ende-zu-Ende-Test der gemeinsamen Installationsseite am echten Brett.
Startet C:\\VHS_Kurs\\VHS_ESP32_Installation\\Werkzeuge\\esp_kurs_installation_1.2.py mit Thonnys Python als Unterprozess, fragt /naechste,
/ports, /dateien ab, stößt POST /start {nummer, brett} an (wie der Knopf bzw. der Selbststart der Seite), wartet auf das Ergebnis und
beendet den Server. Aufruf: python vhs_seite_test_1.0.py <Name> <esp|cam> [COMx]   -- mit COMx wird die Konfiguration auf diesen Anschluss gezwungen
(sonst nimmt sie den ersten gefundenen; sein Wort: „an com 5 liegt nun ein board zum testen“).
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import os, subprocess, sys, time, json, urllib.request
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
name, brett = sys.argv[1], sys.argv[2]; port = sys.argv[3] if len(sys.argv) > 3 else None
PY = None
for d in (os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs", "Thonny"), r"C:\Program Files\Thonny"):
    if os.path.isfile(os.path.join(d, "python.exe")): PY = os.path.join(d, "python.exe"); break
SEITE = r"C:\VHS_Kurs\VHS_ESP32_Installation\Werkzeuge\esp_kurs_installation_1.2.py"
args = [PY, "-u", SEITE] + (["--port", port] if port else [])   # --port wird von den Konfigurationen aus sys.argv gelesen (PORT_VORGABE)
srv = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace", cwd=os.path.dirname(SEITE))
def hole(pfad, daten=None):
    req = urllib.request.Request("http://127.0.0.1:8765" + pfad, data=json.dumps(daten).encode() if daten is not None else None, method="POST" if daten is not None else "GET")
    return urllib.request.urlopen(req, timeout=10).read().decode("utf-8", "replace")
try:
    for _ in range(40):
        try: hole("/zustand"); break
        except Exception: time.sleep(0.5)
    print("naechste:", hole("/naechste")); print("ports:", hole("/ports")[:300])
    print("dateien", brett, ":", [d["ziel"] for d in json.loads(hole("/dateien?brett=" + brett))])
    print("start:", hole("/start", {"nummer": name, "brett": brett})); t0 = time.time(); letzte = 0
    while time.time() - t0 < 900:
        z = json.loads(hole("/zustand"))
        for zeile in z["zeilen"][letzte:]: print("   ", zeile[:160])
        letzte = len(z["zeilen"])
        if z.get("frage"): print("   FRAGE der Seite:", z["frage"][:200]); hole("/antwort", {"text": ""}); time.sleep(1)
        if not z["laeuft"] and z["ergebnis"]: print("ERGEBNIS:", z["ergebnis"], "brett", z.get("brett"), "nummer", z.get("nummer")); break
        time.sleep(1.0)
    try: print("brett.txt:", open(os.path.join(os.path.dirname(SEITE), "brett.txt"), encoding="utf-8").read())
    except OSError as e: print("brett.txt fehlt", e)
finally:
    srv.terminate()
    try: srv.wait(10)
    except Exception: srv.kill()
    aus = srv.stdout.read() if srv.stdout else ""; print("Server-Ausgabe (Ende):", aus[-400:].replace("\n", " | "))

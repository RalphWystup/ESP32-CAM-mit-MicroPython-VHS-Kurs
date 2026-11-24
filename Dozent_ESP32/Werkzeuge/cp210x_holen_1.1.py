#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cp210x_holen_1.1.py (24.11.2026) -- auf dem PC: CP210x-Treiber (Silicon Labs) aus dem Microsoft-Update-Katalog holen (silabs.com sperrt
Skript-Downloads mit 403; der Katalog führt denselben WHQL-Treiber „Silicon Laboratories Inc. Driver Update (11.5.0.417)“, 9.12.2025, 205 kB).
Ablauf: CAB vom Microsoft-Server laden -> mit expand.exe (Windows) auspacken -> prüfen (silabser.inf mit DriverVer, .cat, .sys) ->
als ZIP nach C:\\VHS_Kurs\\Teilnehmer_ESP32\\Werkzeuge\\PC_einrichten\\pakete\\CP210x_Universal_Windows_Driver.zip (so sucht 1_PC_einrichten_1.6.bat
den Treiber: Dateiname, darin silabser.inf). Überschreibt nichts.
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import os, subprocess, sys, zipfile, hashlib, urllib.request, tempfile, re
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
URL = "https://catalog.s.download.windowsupdate.com/c/msdownload/update/driver/drvs/2026/02/3bc68c22-eb83-4383-b451-4c581d06d3fb_6092f1062939e09f524b5d8e9108530f7f516f13.cab"
Z = r"C:\VHS_Kurs\Teilnehmer_ESP32\Werkzeuge\PC_einrichten\pakete\CP210x_Universal_Windows_Driver.zip"
if os.path.exists(Z): print("schon da:", Z); sys.exit(0)
d = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=120).read()
print("CAB:", len(d), "Byte, SHA-256", hashlib.sha256(d).hexdigest(), "Kopf", d[:4])
if d[:4] != b"MSCF": print("kein CAB"); sys.exit(1)
tmp = tempfile.mkdtemp(prefix="cp210x_"); cab = os.path.join(tmp, "treiber.cab"); open(cab, "wb").write(d); aus = os.path.join(tmp, "aus"); os.makedirs(aus)
r = subprocess.run(["expand.exe", "-F:*", cab, aus], capture_output=True, text=True, errors="replace"); print("expand:", r.returncode, (r.stdout + r.stderr).strip()[-300:])
dateien = [os.path.join(w, f) for w, _, fs in os.walk(aus) for f in fs]; print("Dateien:", [os.path.basename(f) for f in dateien])
inf = [f for f in dateien if f.lower().endswith("silabser.inf")]
if not inf: print("silabser.inf fehlt"); sys.exit(1)
t = open(inf[0], encoding="utf-16", errors="replace").read() if open(inf[0], "rb").read(2) in (b"\xff\xfe", b"\xfe\xff") else open(inf[0], encoding="latin-1").read()
m = re.search(r"DriverVer\s*=\s*([^\r\n]+)", t); print("DriverVer:", m.group(1) if m else "?"); print("Hersteller-Zeile:", (re.search(r"Provider\s*=\s*([^\r\n]+)", t) or [None, "?"])[1])
if not any(f.lower().endswith(".cat") for f in dateien) or not any(f.lower().endswith(".sys") for f in dateien): print("cat/sys fehlt"); sys.exit(1)
os.makedirs(os.path.dirname(Z), exist_ok=True)
with zipfile.ZipFile(Z, "w", zipfile.ZIP_DEFLATED) as z:
    for f in dateien: z.write(f, os.path.join("CP210x_11.5.0.417", os.path.relpath(f, aus)))
print("ZIP:", Z, os.path.getsize(Z), "Byte, SHA-256", hashlib.sha256(open(Z, "rb").read()).hexdigest())
r = subprocess.run(["powershell", "-NoProfile", "-Command", f"Get-AuthenticodeSignature '{[f for f in dateien if f.lower().endswith('.cat')][0]}' | Format-List Status,SignerCertificate"], capture_output=True, text=True, errors="replace"); print("Signatur des Katalogs:", r.stdout.strip()[:400])

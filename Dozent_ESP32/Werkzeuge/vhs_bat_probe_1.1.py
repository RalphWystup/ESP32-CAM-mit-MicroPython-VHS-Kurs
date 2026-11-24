#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vhs_bat_probe_1.1.py (24.11.2026; 1.1: interne „call :marke“ bleiben, Option echt = Originaldatei laufen lassen, Option brett=cam|esp legt Werkzeuge\\brett.txt vorübergehend an, Antwortzeilen mit | oder / getrennt (die Brücke lässt nur / durch)) -- auf dem PC, aus C:\\Bruecke: Probelauf einer Batch-Datei ohne Fenster und ohne Nebenwirkung.
Sein Wort: „cmd flasch nur kurz auf, und sonst passiert nichts“. Legt neben die Batch eine Probe-Kopie, in der jede Zeile, die python.exe,
Thonny oder einen Browser startet, durch „echo WUERDE: …“ ersetzt ist, und führt sie mit cmd /c ohne Tastatur (stdin leer) aus. Ausgabe und
Fehlercode kommen zurück. Aufruf: python vhs_bat_probe_1.1.py <Batch-Datei> [Antwort|Antwort2] [echt] [brett=cam]
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import os, re, subprocess, sys, pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
arg = sys.argv[1:]; echt = "echt" in arg; brett = next((a[6:] for a in arg if a.startswith("brett=")), None); arg = [a for a in arg if a != "echt" and not a.startswith("brett=")]
bat = pathlib.Path(arg[0]); antwort = "".join(z + "\r\n" for z in arg[1].replace("+", "|").replace("/", "|").split("|")) if len(arg) > 1 else ""
bt = bat.parent / "Werkzeuge" / "brett.txt"; bt_war = bt.exists()
if brett and not bt_war: bt.write_text(brett + "\n"); print("brett.txt vorübergehend:", brett)
text = bat.read_bytes().decode("cp1252", "replace")
print("Datei:", bat, len(text), "Zeichen; CR:", text.count("\r"), "LF:", text.count("\n"), "BOM:", bat.read_bytes()[:3] == b"\xef\xbb\xbf")
zeilen = []
for z in text.split("\n"):
    r = z.rstrip("\r"); s = r.strip().lower()
    if not echt and (("python.exe" in s and not s.startswith(("if ", "for ", "rem", "set "))) or (s.startswith(("call ", "start ")) and not s.startswith("call :")) or (" call " in s and "goto" in s)):
        r = "echo WUERDE: " + r.replace("%", "%%").replace("&", "^&").replace("|", "^|").replace("<", "^<").replace(">", "^>")
    zeilen.append(r)
probe = bat.with_name(bat.stem + "_PROBE.bat")
if echt: probe = bat; print("ECHTER LAUF der Originaldatei")
else: probe.write_bytes("\r\n".join(zeilen).encode("cp1252", "replace"))
try:
    p = subprocess.run(["cmd.exe", "/c", str(probe)], input=antwort.encode("cp850"), capture_output=True, cwd=str(bat.parent), timeout=240)
    print("Fehlercode:", p.returncode)
    print("--- Ausgabe ---"); print(p.stdout.decode("cp850", "replace")); print("--- Fehler ---"); print(p.stderr.decode("cp850", "replace"))
finally:
    if not echt: probe.unlink(missing_ok=True); print("Probe-Kopie entfernt:", not probe.exists())
    if brett and not bt_war: bt.unlink(missing_ok=True); print("brett.txt wieder weg:", not bt.exists())

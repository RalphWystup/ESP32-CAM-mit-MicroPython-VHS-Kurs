#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""esp_com_diagnose_1.0.py -- auf dem PC: Zustand des CH340 (COM5) aus Windows lesen (Status, Problemcode, Treiber, laufende Programme,
die serielle Anschlüsse öffnen könnten). Ändert nichts. 17.11.2026 (COM5: PermissionError 31 beim Öffnen).
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import subprocess, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
def ps(c):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", c], capture_output=True, text=True, encoding="utf-8", errors="replace")
    print((r.stdout + r.stderr).strip()[-2500:], flush=True)
ps("Get-PnpDevice | Where-Object { $_.FriendlyName -like '*CH340*' -or $_.FriendlyName -like '*(COM5)*' } | Format-List FriendlyName,Status,Problem,InstanceId,Present")
ps("Get-CimInstance Win32_PnPSignedDriver | Where-Object { $_.DeviceName -like '*CH340*' } | Format-List DeviceName,DriverVersion,DriverDate,DriverProviderName")
ps("Get-Process | Where-Object { $_.ProcessName -match 'thonny|arduino|putty|serial|esptool|python|mpremote|cura|platformio|code' } | Format-Table Id,ProcessName,StartTime -AutoSize")

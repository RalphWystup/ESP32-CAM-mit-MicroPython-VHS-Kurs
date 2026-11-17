#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""esp_thonny_fassung_1.0.py -- auf dem PC: welche Thonny-Fassung ist installiert? Nur lesen. 17.11.2026.
Autoren: Prof. Dr.-Ing. Ralph Wystup M.Sc. und Claude (Anthropic, Claude Code) — gemeinsam erstellt."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
try:
    import importlib.metadata as md; print("Thonny", md.version("thonny"))
except Exception as e:
    try:
        import thonny; print("Thonny", thonny.get_version())
    except Exception as e2: print("nicht lesbar:", e, e2)

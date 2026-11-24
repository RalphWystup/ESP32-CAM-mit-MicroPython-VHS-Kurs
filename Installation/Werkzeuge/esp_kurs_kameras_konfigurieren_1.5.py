#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==========================================================================================================
#  VHS-Kurs  „ESP32-CAM mit MicroPython“
#  Kameras konfigurieren – für den Dozenten  (esp_kurs_kameras_konfigurieren_1.5.py)
# ----------------------------------------------------------------------------------------------------------
#  Autor:      Prof. Dr.-Ing. Ralph Wystup M.Sc.
#  Mitarbeit:  Claude (Anthropic, Claude Code)
#  Fassung:    1.5 vom 17.11.2026 (1.5: ein Anschlussfehler beim Prüfen der Firmware führt NIE zum Flashen (Befund 12:30: „Cannot
#              configure port“ wurde als „keine Firmware“ gedeutet) -- erst ein zweiter Versuch, dann Abbruch mit Anweisung;
#              Flash-Fehlermeldung nennt die eigentliche Ursache.  1.4: ohne main.py -- ein vorhandenes wird entfernt (sein Wort „bitte ohne main py“);
#              kamera.py 1.6, blink 1.2/led_handy 1.1 mit der weißen LED; RST per Software (RTS-Puls), wenn die Kamera im
#              Bootlader steht; Schritt 4 = Probelauf wie in Thonny: Start, Stop, Soft-Reboot, Start.  1.3: Fortschritt beim Flashen (Prozent aus esptool) und beim Aufspielen je Datei über
#              fortschritt(); naechste_nummer() aus dem Protokoll -- sein Wort „den downlod verlauf bitte auch anzeigen“.  1.2: liegt in Dozent\Werkzeuge, Kameradateien und firmware.bin in Dozent\Kameraprogramme,
#              Protokoll kameras_protokoll.csv in Dozent\.  1.1: als Modul nutzbar für die Installationsseite esp_kurs_installieren_1.0.py --
#              Ablauf nur unter __main__; print/input lassen sich von außen ersetzen; halt() wirft Abbruch statt sys.exit)
# ----------------------------------------------------------------------------------------------------------
#  Sein Wort: „ich habe ja 3 cams, ich brauche also eine konfigrationssoftware … zudem soll ein einfaches Blink und pwm
#  programm auch enthalten sein“, „ich gehe von einer werksfrischen esp32cam aus! … auch die com müsste man zuerst automatisch suchen“.
#  Je Kamera (eine nach der anderen, Nummer 1, 2, 3 …):
#    1. Anschluss automatisch suchen (CH340 = USB 1A86, CP210x = 10C4) und vorbereiten (erst 9600, dann 115200 Baud).
#    2. Firmware: ist MicroPython mit Kameratreiber schon drauf, wird nicht geflasht; eine werksfrische Kamera bekommt
#       firmware.bin (MicroPython 1.27 + Kameratreiber) -- erst mit automatischem Reset, sonst mit Ansage (IO0 halten).
#    3. Aufspielen (alles in Thonny im Dateibereich sichtbar):
#         kamera.py            Kameraprogramm (Start in Thonny, eigenes WLAN „VHS-CAM-<Nummer>“, Adresse 192.168.4.1)
#         blink.py             Beispiel: rote LED blinkt          pwm.py      Beispiel: Blitz-LED per PWM
#         led_handy.py         Beispiel: LED vom Handy aus (mit OLED, falls angeschlossen)   ssd1306.py  OLED-Treiber
#         kamera.json          {"name": "VHS-CAM-<Nummer>"}
#    4. Neustart, Verbindungsdaten anzeigen, Zeile ins Protokoll kameras_protokoll.csv (Datum, Nummer, WLAN, MAC, Anschluss,
#       Firmware) -- zum Beschriften der Kameras. Kennwörter werden nie geschrieben oder angezeigt.
#  Aufruf: Doppelklick auf esp_kurs_kameras_konfigurieren_1.5.bat, oder
#          python esp_kurs_kameras_konfigurieren_1.5.py [--nummer N] [--ohne-fragen] [--port COMx]
# ==========================================================================================================
import binascii, hashlib, os, subprocess, sys, time
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
try:
    import serial
    from serial.tools import list_ports
except ImportError:
    print("FEHLER: Paket pyserial fehlt -- zuerst esp_kurs_einrichten.bat ausführen."); sys.exit(1)

HIER = os.path.dirname(os.path.abspath(__file__))
DOZENT = os.path.dirname(HIER); PROGRAMME = os.path.join(DOZENT, "Kameraprogramme")   # 1.2: Ordnergliederung
FW = os.path.join(PROGRAMME, "firmware.bin"); FW_SHA = "b26ba45de13549272d888c229c5c3864b75250471ac290478d752b8098ee70ea"
FRAGEN = "--ohne-fragen" not in sys.argv
PORT_VORGABE = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else None
MODULE = "import asyncio, gc, json, network, time, ubinascii\nfrom machine import Pin\nfrom camera import Camera, PixelFormat, FrameSize\nprint('MODULE OK')"


def schritt(n, text): print(f"\n[{n}/4] {text}", flush=True)
def ok(text): print(f"      OK  {text}", flush=True)
class Abbruch(Exception):
    pass


def halt(text): print(f"\n  >>> {text}", flush=True); raise Abbruch(text)


def warte(text):
    if FRAGEN: input(f"\n  >>> {text}\n      danach Eingabetaste drücken ... ")
    else: print(f"  >>> {text} (ohne Fragen: weiter in 5 s)"); time.sleep(5)


# ---------------------------------------------------------------------------------------------------------- Anschluss
def finde_port():
    if PORT_VORGABE: return PORT_VORGABE, "vorgegeben"
    for versuch in range(3):
        k = [(p.device, p.description) for p in list_ports.comports() if any(v in (p.hwid or "").upper() for v in ("1A86", "10C4"))]
        if k: return k[0]
        warte("Keine Kamera gefunden. Bitte die ESP32-CAM mit dem USB-Brett per Kabel an den PC stecken.")
    halt("Keine Kamera gefunden. Steckt das Kabel? Ist es ein Datenkabel (nicht nur Ladekabel)? Ist der USB-Treiber installiert?")


def vorlauf(port):
    for b in (9600, 115200):
        try:
            s = serial.Serial(); s.port = port; s.baudrate = b; s.timeout = 0.2; s.dtr = False; s.rts = False; s.open(); s.close()
        except Exception as e:
            if "PermissionError" in str(e) or "Zugriff" in str(e) or "Access" in str(e):
                return f"{port} ist belegt oder gestört ({str(e)[:70]}). Thonny schließen, Kabel ab- und wieder anstecken."
            return f"{port} lässt sich nicht öffnen ({str(e)[:90]}). Kabel ab- und wieder anstecken."
    return None


# ---------------------------------------------------------------------------------------------------------- MicroPython (Raw-REPL)
class Kamera:
    def __init__(self, port):
        self.s = serial.Serial(); self.s.port = port; self.s.baudrate = 115200; self.s.timeout = 0.3; self.s.dtr = False; self.s.rts = False; self.s.open()

    def _bis(self, ende, frist):
        p = b""; t0 = time.time()
        while time.time() - t0 < frist:
            p += self.s.read(512)
            if ende in p[-len(ende) - 2:]: break
        return p

    def rst(self):
        """RST per Software: RTS-Puls bei DTR aus (EN kurz auf 0, IO0 bleibt oben) -- wie die RST-Taste."""
        s = self.s; s.dtr = False; s.rts = True; time.sleep(0.15); s.rts = False; time.sleep(2.5); return s.read(4000)

    def rein(self):
        if self._rein(): return True
        print("      Kamera antwortet nicht (steht nach dem Einstecken oft im Bootlader) -- Neustart per Software ...", flush=True)
        self.rst(); return self._rein()

    def _rein(self):
        s = self.s; s.write(b"\r\x03\x03"); time.sleep(0.3); s.reset_input_buffer()
        for _ in range(3):
            s.write(b"\r\x01")
            if self._bis(b"raw REPL; CTRL-B to exit\r\n>", 3).endswith(b">"): return True
            s.write(b"\x03\x03"); time.sleep(0.3); s.reset_input_buffer()
        return False

    def aus(self, code, frist=20):
        self.s.write(code.encode() if isinstance(code, str) else code); self.s.write(b"\x04")
        if self.s.read(2) != b"OK": return "", "nicht angenommen"
        t = self._bis(b"\x04>", frist).split(b"\x04")
        return t[0].decode("utf-8", "replace"), (t[1].decode("utf-8", "replace") if len(t) > 1 else "")

    def lies_datei(self, name):
        out, err = self.aus(f"try:\n import binascii\n f=open({name!r},'rb'); print(binascii.hexlify(f.read()).decode()); f.close()\nexcept OSError:\n print('FEHLT')", 30)
        o = out.strip()
        return None if (err or o == "FEHLT") else binascii.unhexlify(o)

    def schreibe(self, inhalt, ziel):
        out, err = self.aus(f"f = open({ziel!r}, 'wb')")
        if err: return False
        for i in range(0, len(inhalt), 256):
            out, err = self.aus(f"f.write(__import__('binascii').unhexlify({binascii.hexlify(inhalt[i:i + 256]).decode()!r}))")
            if err: return False
            fortschritt("Aufspielen " + ziel, 100.0 * min(i + 256, len(inhalt)) / len(inhalt), f"{min(i + 256, len(inhalt))} von {len(inhalt)} Byte")
        out, err = self.aus(f"f.close(); import os; print(os.stat({ziel!r})[6])")
        return not err and out.strip() == str(len(inhalt))

    def neustart_mitlesen(self, sekunden=30):
        self.s.write(b"import machine; machine.reset()\x04"); t0 = time.time(); p = b""
        while time.time() - t0 < sekunden:
            p += self.s.read(512)
            if b"Webserver l" in p: time.sleep(0.5); p += self.s.read(512); break
        zeilen = p.decode("utf-8", "replace").splitlines()
        i0 = next((i for i, z in enumerate(zeilen) if "=====" in z), 0)
        return [z.rstrip() for z in zeilen[i0:] if z.strip()]

    def probelauf(self, sekunden=40):
        """kamera.py so ausführen wie der Start-Knopf in Thonny, Ausgabe bis „Webserver läuft“ lesen, dann Strg+C wie „Stop“.
        Rückgabe: (Zeilen, Webserver lief, Kamera wurde beim Stop abgeschaltet)."""
        if not self.rein(): return [], False, False
        self.s.write(b"exec(open('kamera.py').read(), {'__name__': '__main__'})\x04")
        if self.s.read(2) != b"OK": return ["(nicht angenommen)"], False, False
        p = b""; t0 = time.time()
        while time.time() - t0 < sekunden:
            p += self.s.read(512)
            if b"Webserver l" in p or b"Traceback" in p or b"\x04" in p: break
        time.sleep(0.5); p += self.s.read(2000)
        self.s.write(b"\x03"); time.sleep(2.0); q = self.s.read(4000)
        zeilen = [z.rstrip() for z in (p + q).decode("utf-8", "replace").replace("\x04", "\n").splitlines() if z.strip() and z.strip() != ">"]
        return zeilen, b"Webserver l" in p, b"ausgeschaltet" in q

    def weich(self):
        """Soft-Reboot wie Thonny vor dem Ausführen."""
        s = self.s; s.write(b"\r\x03\x03"); time.sleep(0.3); s.write(b"\x02"); time.sleep(0.3); s.reset_input_buffer(); s.write(b"\x04"); time.sleep(2.5)
        return s.read(8000)

    def zu(self):
        try: self.s.close()
        except Exception: pass


def firmware_da(port):
    """True: MicroPython mit Kameratreiber da; False: keine passende Firmware (dann flashen); None: Anschlussfehler (NIE flashen)."""
    try: k = Kamera(port)
    except Exception as e: return None, f"Anschluss: {str(e)[:80]}"
    try:
        if not k.rein(): return False, "keine MicroPython-Antwort"
        out, err = k.aus(MODULE)
        return ("MODULE OK" in out), (out.strip() or err.strip()[-120:])
    finally: k.zu()


# ---------------------------------------------------------------------------------------------------------- Flashen
_letzt = {}


def fortschritt(art, prozent, text=""):
    """Fortschritt melden; die Installationsseite ersetzt diese Funktion (Balken). Auf der Kommandozeile: alle 10 %."""
    stufe = int(prozent // 10)
    if _letzt.get(art) != stufe or prozent >= 100:
        _letzt[art] = stufe; print(f"      {art}: {prozent:5.1f} %  {text}", flush=True)


def esptool(port, *a, auto=True):
    """esptool laufen lassen und die Prozentzeilen („Writing at … 66.7% …“) als Fortschritt melden."""
    import re
    vor = [] if auto else ["--before", "no-reset", "--after", "no-reset"]
    p = subprocess.Popen([sys.executable, "-u", "-m", "esptool", "--chip", "esp32", "--port", port, "--baud", "115200", *vor, *a],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace",
                         env=dict(os.environ, PYTHONUNBUFFERED="1"))
    alles = []
    for zeile in p.stdout:
        alles.append(zeile)
        m = re.search(r"(\d+(?:\.\d+)?)%\s+(\d+)/(\d+) bytes", zeile)
        if m: fortschritt("Firmware schreiben", float(m.group(1)), f"{int(m.group(2)) // 1024} von {int(m.group(3)) // 1024} kB (gepackt)")
        elif "Erasing flash" in zeile or "Chip erase" in zeile: fortschritt("Firmware schreiben", 0.0, "Flash wird gelöscht ...")
        elif "Verifying" in zeile or "Hash of data verified" in zeile: fortschritt("Firmware schreiben", 100.0, "geprüft")
    p.wait()
    return p.returncode, "".join(alles)


def flashen(port):
    if not os.path.isfile(FW): halt("firmware.bin fehlt im Kursordner.")
    if hashlib.sha256(open(FW, "rb").read()).hexdigest() != FW_SHA: halt("firmware.bin ist beschädigt (Prüfsumme falsch) -- Kursordner neu kopieren.")
    print("      Firmware wird geschrieben (etwa 2 Minuten, bitte das Kabel nicht berühren) ...", flush=True)
    rc, txt = esptool(port, "write-flash", "--erase-all", "-z", "0x1000", FW, auto=True)
    if rc == 0 and "Hash of data verified" in txt: ok("Firmware geschrieben und geprüft (automatischer Reset)"); return
    print("      Der automatische Wechsel in den Flash-Modus hat nicht geklappt -- dann von Hand:", flush=True)
    warte("Kabel abziehen. Die Taste IO0 auf dem USB-Brett GEDRÜCKT HALTEN, Kabel wieder einstecken, IO0 nach 2 Sekunden loslassen.")
    f = vorlauf(port)
    if f: halt(f)
    print("      Firmware wird geschrieben (etwa 2 Minuten) ...", flush=True)
    rc, txt = esptool(port, "write-flash", "--erase-all", "-z", "0x1000", FW, auto=False)
    if rc != 0 or "Hash of data verified" not in txt:
        z = [l.strip() for l in txt.splitlines() if l.strip() and "troubleshooting" not in l]
        grund = next((l for l in reversed(z) if "rror" in l or "fatal" in l.lower() or "Failed" in l), z[-1] if z else "keine Meldung")
        halt("Flashen nicht gelungen: " + grund[:200] + " -- USB-Kabel 5 s abziehen, wieder anstecken, noch einmal installieren.")
    ok("Firmware geschrieben und geprüft")
    warte("Jetzt die Taste RST an der Kamera kurz drücken (ohne IO0).")


# ---------------------------------------------------------------------------------------------------------- Ablauf
import datetime, json
DATEIEN = [("esp_cam_kamera_1.6.py", "kamera.py"), ("esp_cam_blink_1.2.py", "blink.py"), ("esp_cam_pwm_1.0.py", "pwm.py"),
           ("esp_cam_led_handy_1.1.py", "led_handy.py"), ("ssd1306.py", "ssd1306.py")]           # 1.4: kein main.py
PROTOKOLL = os.path.join(DOZENT, "kameras_protokoll.csv")


def naechste_nummer():
    """nächste freie Kameranummer aus kameras_protokoll.csv (höchste + 1; 1, wenn es noch keins gibt)."""
    try:
        n = [int(z.split(";")[1]) for z in open(PROTOKOLL, encoding="utf-8").read().splitlines()[1:] if z.count(";") >= 5]
        return max(n) + 1 if n else 1
    except (OSError, ValueError):
        return 1


def eine_kamera(nummer):
    name = f"VHS-CAM-{nummer}"
    print("\n" + "=" * 64 + f"\n Kamera Nr. {nummer}  ->  WLAN „{name}“\n" + "=" * 64, flush=True)
    schritt(1, "Kamera suchen und Anschluss vorbereiten")
    port, beschr = finde_port(); ok(f"Kamera an {port} ({beschr})")
    f = vorlauf(port)
    if f: halt(f)
    ok("Anschluss lässt sich öffnen")
    schritt(2, "Firmware")
    da, info = firmware_da(port); geflasht = False
    if da is None:                                   # Anschlussfehler: einmal Luft lassen, Vorlauf, noch einmal -- nie flashen
        time.sleep(3); f = vorlauf(port)
        da, info = firmware_da(port) if not f else (None, f)
    if da is None:
        halt(f"Der Anschluss der Kamera ist gestört ({info}). Thonny schließen, USB-Kabel 5 s abziehen, wieder anstecken, dann noch einmal installieren.")
    if da: ok("MicroPython mit Kameratreiber ist schon drauf -- es wird nicht geflasht")
    else:
        print(f"      keine passende Firmware ({info}) -- eine werksfrische Kamera bekommt jetzt MicroPython", flush=True)
        flashen(port); geflasht = True; time.sleep(4)
        for _ in range(4):
            if not vorlauf(port):
                da, info = firmware_da(port)
                if da: break
            time.sleep(3)
        if not da: halt(f"Nach dem Flashen antwortet die Kamera nicht ({info}). RST drücken und dieses Programm noch einmal starten.")
        ok("MicroPython mit Kameratreiber antwortet")
    schritt(3, "Programme aufspielen")
    k = Kamera(port)
    if not k.rein(): k.zu(); halt("Die Kamera antwortet nicht. RST drücken und dieses Programm noch einmal starten.")
    ziele = [(open(os.path.join(PROGRAMME, q), "rb").read(), z) for q, z in DATEIEN]
    ziele.append((json.dumps({"name": name}).encode("utf-8"), "kamera.json"))
    for inhalt, ziel in ziele:
        alt = k.lies_datei(ziel)
        if alt == inhalt: ok(f"{ziel:13s} schon aktuell"); continue
        if alt is not None and FRAGEN and ziel != "kamera.json":
            if input(f"      Auf der Kamera liegt ein anderes {ziel}. Überschreiben? (j/n) ").strip().lower() != "j":
                print(f"      {ziel} bleibt unverändert."); continue
        if not k.schreibe(inhalt, ziel): k.zu(); halt(f"{ziel} konnte nicht geschrieben werden. Programm noch einmal starten.")
        ok(f"{ziel:13s} aufgespielt ({len(inhalt)} Byte, Größe geprüft)")
    out, err = k.aus("import os\ntry:\n os.remove('main.py'); print('ENTFERNT')\nexcept OSError:\n pass")
    if "ENTFERNT" in out: ok("main.py entfernt (Start nur über Thonny)")
    out, err = k.aus("import os; print(sorted(os.listdir()))"); ok("auf der Kamera: " + out.strip())
    schritt(4, "Probelauf wie in Thonny: Start, Stop, noch einmal Start")
    k.rst()
    zeilen, lief, aus = k.probelauf()
    for z in zeilen:
        if "kennwort" in z.lower() and "Sicherheit" not in z and "Kennwort       :" not in z: continue
        print("      " + z)
    if not lief: k.zu(); halt("Das Kameraprogramm ist beim Probelauf nicht angelaufen (Ausgabe oben). USB-Kabel 5 s abziehen, wieder anstecken, noch einmal installieren.")
    ok("1. Start: Webserver lief" + ("; bei Stop wurde die Kamera abgeschaltet" if aus else " (Abschalten bei Stop NICHT gemeldet)"))
    k.weich()
    zeilen2, lief2, aus2 = k.probelauf()
    if not lief2: k.zu(); halt("Der zweite Start (nach Stop, wie in Thonny) ist gescheitert: " + " | ".join(zeilen2[-4:])[:200])
    ok("2. Start nach Stop und Soft-Reboot: Webserver lief" + ("; Kamera wieder abgeschaltet" if aus2 else ""))
    k.rst(); k.zu()
    mac = next((z.split(":", 1)[1].strip() for z in zeilen if "MAC-Adresse" in z), "")
    neu = not os.path.isfile(PROTOKOLL)
    with open(PROTOKOLL, "a", encoding="utf-8") as p:
        if neu: p.write("Datum;Nummer;WLAN;MAC;Anschluss;Firmware\n")
        p.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M};{nummer};{name};{mac};{port};{'neu geflasht' if geflasht else 'war schon drauf'}\n")
    print("\n" + "-" * 64 + f"\n Kamera Nr. {nummer} FERTIG -- WLAN „{name}“, http://192.168.4.1/  (Start in Thonny: kamera.py öffnen, Start-Knopf)\n Bitte die Kamera mit „{name}“ beschriften.  (Protokoll: kameras_protokoll.csv)\n" + "-" * 64, flush=True)


if __name__ == "__main__":
  print("=" * 64 + "\n VHS-Kurs ESP32-CAM  ·  Kameras konfigurieren  ·  Fassung 1.5\n Prof. Dr.-Ing. Ralph Wystup M.Sc.\n" + "=" * 64, flush=True)
  nummer = int(sys.argv[sys.argv.index("--nummer") + 1]) if "--nummer" in sys.argv else None
  if nummer is not None or not FRAGEN:
      eine_kamera(nummer or 1)
  else:
      nummer = 1
      while True:
          e = input(f"\nKamera Nr. {nummer} per USB anstecken (nur diese eine), dann Eingabetaste.  Andere Nummer eintippen oder q = Ende: ").strip().lower()
          if e == "q": break
          if e.isdigit(): nummer = int(e)
          try:
              eine_kamera(nummer); nummer += 1
              print("Kamera abziehen.")
          except Abbruch:
              print("Diese Kamera ist NICHT fertig -- Hinweis oben beachten, dann dieselbe Nummer noch einmal.")
      print("Ende. Protokoll:", PROTOKOLL)

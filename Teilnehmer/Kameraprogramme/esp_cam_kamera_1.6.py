# ==========================================================================================================
#  VHS-Kurs  „ESP32-CAM mit MicroPython“
#  Kamerabild über WLAN – Kameraprogramm  (kamera.py)
# ----------------------------------------------------------------------------------------------------------
#  Autor:      Prof. Dr.-Ing. Ralph Wystup M.Sc.
#  Mitarbeit:  Claude (Anthropic, Claude Code)
#  Fassung:    1.6 vom 17.11.2026
#  Gerät:      ESP32-CAM (AI Thinker, Kamera OV2640) auf dem USB-Brett ESP32-CAM-MB
#  Firmware:   MicroPython 1.27 mit Kameratreiber (github.com/cnadler86/micropython-camera-API, v0.6.2)
# ----------------------------------------------------------------------------------------------------------
#  Starten: in Thonny diese Datei öffnen und den grünen Start-Knopf drücken (F5). „Stop“ beendet das Programm.
#  (Die Kamera startet nach dem Einschalten nichts von selbst -- es gibt kein main.py.)
#
#  Was das Programm tut
#    1. Es spannt ein eigenes WLAN auf, Adresse 192.168.4.1. Name aus kamera.json ({"name": "VHS-CAM-1"}),
#       sonst „ESP32CAM-xxxx“ (Ende der MAC-Adresse). Mit ap.json ({"kennwort": "xxxxxxxx"}, mind. 8 Zeichen) geschützt,
#       sonst offen. Liegt wlan.json ({"ssid": "MeinNetz", "kennwort": "xxxxxxxx"}) auf der Kamera, geht sie zusätzlich ins Heimnetz.
#    2. Ein kleiner Webserver (Port 80) liefert das Kamerabild:
#         http://<adresse>/            Seite mit Livebild und Knöpfen für den Blitz
#         http://<adresse>/bild.jpg    ein Einzelbild (VGA 640 × 480, JPEG)
#         http://<adresse>/stream      Livebild als MJPEG-Strom
#         http://<adresse>/blitz?an=1  Blitz-LED an  (an=0: aus)
#         http://<adresse>/status      Zähler, freier Speicher, WLAN-Signal (JSON)
#    3. Ausgabe in Thonny: zuerst „AM HANDY EINGEBEN“ (WLAN-Name, Kennwort, Adresse), dann die Verbindungsdaten;
#       danach kurz jeder Zugriff und alle 30 s der Zustand. Kennwörter werden nie ausgegeben.
#
#  Dateien auf der Kamera (in Thonny im Dateibereich „MicroPython-Gerät“):
#    kamera.py   dieses Programm                     kamera.json  Name der Kamera = Name ihres WLANs
#    blink.py    Beispiel: Blitz-LED blinkt          pwm.py       Beispiel: Blitz-LED per PWM heller/dunkler
#    led_handy.py Beispiel: LED vom Handy aus        ssd1306.py   OLED-Treiber
#    ap.json / wlan.json  Kennwort des eigenen WLANs / Heimnetz (freiwillig, vom Dozenten)
#
#  Änderungen: 1.6 bei „Stop“ wird die Kamera abgeschaltet (sonst startet sie nach dem Soft-Reboot von Thonny nicht
#  wieder: „Failed to capture initial frame“/ESP_ERR_NOT_SUPPORTED; gemessen 17.11.2026) · 1.5 ohne main.py (Start nur in Thonny), „Am Handy eingeben“, Zustand per print, Kamera-Neustart nach
#  Stop/Start (Treiber lief nach Soft-Reboot weiter: „Failed to capture initial frame“) · 1.4 WLAN-Name aus kamera.json ·
#  1.3 Start-Knopf · 1.2 Kopf, Verbindungsdaten · 1.1 eigenes WLAN immer · 1.0 erste Fassung
# ==========================================================================================================
import asyncio, gc, json, network, time, ubinascii
from machine import Pin
from camera import Camera, PixelFormat, FrameSize

FASSUNG = "1.6"
blitz = Pin(4, Pin.OUT, value=0)                 # Blitz-LED an GPIO4
zaehler = {"bilder": 0, "fehler": 0}
cam = None
AP = HEIM = STA = APIF = None
INFO = {}


# ---------------------------------------------------------------------------------------------------------- Netz
def _lies(name):
    """JSON-Datei auf der Kamera lesen; None, wenn sie fehlt oder kaputt ist."""
    try:
        return json.load(open(name))
    except (OSError, ValueError):
        return None


def netze():
    """Eigenes WLAN immer; Heimnetz zusätzlich, wenn wlan.json da ist."""
    ap = network.WLAN(network.AP_IF); ap.active(True)
    k = _lies("kamera.json") or {}
    name = k.get("name") or "ESP32CAM-" + ubinascii.hexlify(ap.config("mac")[-2:]).decode()
    a = _lies("ap.json")
    if a and len(a.get("kennwort", "")) >= 8:
        ap.config(essid=name, authmode=network.AUTH_WPA2_PSK, password=a["kennwort"]); sicherheit = "WPA2, mit Kennwort (ap.json)"
    else:
        ap.config(essid=name, authmode=network.AUTH_OPEN); sicherheit = "offen, ohne Kennwort"
    del a
    INFO.update(ap_name=name, ap_sicherheit=sicherheit, ap_ip=ap.ifconfig()[0], ap_maske=ap.ifconfig()[1],
                mac=":".join("%02X" % b for b in ap.config("mac")))
    try:
        INFO["ap_kanal"] = ap.config("channel")
    except Exception:
        INFO["ap_kanal"] = None
    sta = network.WLAN(network.STA_IF); z = _lies("wlan.json"); heim = None
    if z:
        INFO["heim_ssid"] = z.get("ssid")
        sta.active(True); sta.connect(z["ssid"], z["kennwort"]); del z
        print("Verbinde mit dem Heimnetz", INFO["heim_ssid"], "...")
        t0 = time.ticks_ms()
        while not sta.isconnected() and time.ticks_diff(time.ticks_ms(), t0) < 20000:
            time.sleep_ms(200)
        if sta.isconnected():
            heim = sta.ifconfig()[0]
            INFO.update(heim_ip=heim, heim_maske=sta.ifconfig()[1], heim_router=sta.ifconfig()[2], heim_rssi=sta.status("rssi"))
        else:
            sta.active(False); INFO["heim_fehler"] = "nicht erreicht (20 s)"
    else:
        sta.active(False)
    return ap.ifconfig()[0], heim, sta


def jetzt():
    t = time.localtime(); return "%02d:%02d:%02d" % (t[3], t[4], t[5])


def verbindungsdaten():
    """Verbindungsdaten übersichtlich ausgeben (ohne Kennwörter)."""
    s = "=" * 64
    print()
    print("#" * 64)
    print("#  AM HANDY / LAPTOP EINGEBEN")
    print("#    1. WLAN verbinden :", INFO["ap_name"])
    print("#    2. Kennwort       :", "keins (offenes WLAN)" if INFO["ap_sicherheit"].startswith("offen") else "steht auf dem Aushang des Dozenten")
    print("#    3. Im Browser     : http://%s/" % INFO["ap_ip"])
    print("#" * 64)
    print()
    print(s)
    print(" VHS-Kurs ESP32-CAM  ·  Kameraprogramm Fassung", FASSUNG)
    print(" Prof. Dr.-Ing. Ralph Wystup M.Sc.")
    print(s)
    print(" Eigenes WLAN")
    print("   Netzname (SSID) :", INFO["ap_name"])
    print("   Sicherheit      :", INFO["ap_sicherheit"])
    print("   IP-Adresse      :", INFO["ap_ip"], " Maske", INFO["ap_maske"])
    if INFO.get("ap_kanal"):
        print("   Funkkanal       :", INFO["ap_kanal"])
    print("   MAC-Adresse     :", INFO["mac"])
    print(" Heimnetz")
    if HEIM:
        print("   Netzname (SSID) :", INFO["heim_ssid"])
        print("   IP-Adresse      :", INFO["heim_ip"], " Maske", INFO["heim_maske"], " Router", INFO["heim_router"])
        print("   Signal          :", INFO["heim_rssi"], "dBm")
    elif INFO.get("heim_ssid"):
        print("   Netzname (SSID) :", INFO["heim_ssid"], "--", INFO.get("heim_fehler"))
    else:
        print("   nicht eingerichtet (keine wlan.json)")
    print(" Im Browser")
    for ip in [INFO["ap_ip"]] + ([HEIM] if HEIM else []):
        print("   http://%s/           Seite mit Livebild" % ip)
        print("   http://%s/bild.jpg   Einzelbild" % ip)
        print("   http://%s/stream     Livebild-Strom" % ip)
    print(" Kamera: VGA 640 x 480, JPEG  ·  „Stop“ in Thonny beendet das Programm")
    print(s)


# ---------------------------------------------------------------------------------------------------------- Kamera
def bild():
    """Ein JPEG-Bild aufnehmen; None bei Fehler."""
    b = cam.capture()
    if not b:
        zaehler["fehler"] += 1; return None
    b = bytes(b); cam.free_buffer()
    if b[:2] != b"\xff\xd8":                     # kein JPEG-Anfang
        zaehler["fehler"] += 1; return None
    zaehler["bilder"] += 1
    return b


def kamera_starten():
    """Kamera einschalten. Nach Stop und neuem Start (Soft-Reboot in Thonny) läuft der Treiber oft noch -- dann erst
    abschalten und neu einschalten."""
    for versuch in range(2):
        try:
            return Camera(pixel_format=PixelFormat.JPEG, frame_size=FrameSize.VGA, jpeg_quality=85, fb_count=2)
        except OSError as e:
            print(jetzt(), " Kamera startet nicht (", e, ") -- zweiter Versuch ...")
            try:
                Camera(init=False).deinit()
            except Exception:
                pass
            gc.collect(); time.sleep_ms(500)
    print()
    print("!" * 64)
    print("!  Die Kamera hängt. Bitte das USB-Kabel 5 Sekunden abziehen, wieder anstecken")
    print("!  und dann in Thonny noch einmal den grünen Start-Knopf drücken.")
    print("!" * 64)
    raise OSError("Kamera lässt sich nicht starten -- USB-Kabel kurz abziehen, dann noch einmal Start")


# ---------------------------------------------------------------------------------------------------------- Webserver
SEITE = """<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>ESP32-CAM</title><style>body{font-family:sans-serif;background:#fff;color:#000;margin:1em}img{max-width:100%;border:1px solid #888}
a,button{margin-right:1em}</style></head><body><h1>ESP32-CAM</h1><p>VHS-Kurs &middot; Prof. Dr.-Ing. Ralph Wystup M.Sc.</p>
<p><a href="/bild.jpg">Einzelbild</a><a href="/stream">nur Strom</a><a href="/status">Status</a>
<button onclick="fetch('/blitz?an=1')">Blitz an</button><button onclick="fetch('/blitz?an=0')">Blitz aus</button></p>
<img src="/stream" alt="Livebild"></body></html>"""


async def antwort(w, kopf, rumpf=b""):
    w.write(kopf.encode())
    if rumpf:
        w.write(rumpf)
    await w.drain()


async def anfrage(r, w):
    try:
        try:
            wer = w.get_extra_info("peername")[0]
        except Exception:
            wer = "?"
        zeile = (await r.readline()).decode()
        while (await r.readline()) not in (b"\r\n", b""):
            pass
        pfad = zeile.split(" ")[1] if " " in zeile else "/"
        if pfad == "/":
            print(jetzt(), "", wer, " Seite geöffnet")
            s = SEITE.encode()
            await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: %d\r\n\r\n" % len(s), s)
        elif pfad.startswith("/bild.jpg"):
            bild(); b = bild()                    # erstes Bild verwerfen (alter Pufferinhalt)
            if b:
                await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\nCache-Control: no-store\r\n\r\n" % len(b), b)
                print(jetzt(), "", wer, " Einzelbild", len(b) // 1024, "kB")
            else:
                await antwort(w, "HTTP/1.0 503 Service Unavailable\r\n\r\nkein Bild")
        elif pfad.startswith("/stream"):
            await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: multipart/x-mixed-replace; boundary=bild\r\nCache-Control: no-store\r\n\r\n")
            print(jetzt(), "", wer, " Livebild gestartet")
            n = 0
            try:
                while True:
                    b = bild()
                    if b:
                        await antwort(w, "--bild\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n" % len(b), b); w.write(b"\r\n"); n += 1
                    await asyncio.sleep_ms(1)
            finally:
                print(jetzt(), "", wer, " Livebild beendet,", n, "Bilder")
        elif pfad.startswith("/blitz"):
            blitz.value(1 if "an=1" in pfad else 0)
            print(jetzt(), "", wer, " Blitz", "an" if blitz.value() else "aus")
            await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: text/plain\r\n\r\n" + ("an" if blitz.value() else "aus"))
        elif pfad.startswith("/status"):
            s = json.dumps({"fassung": FASSUNG, "zugangspunkt": AP, "heimnetz": HEIM, "bilder": zaehler["bilder"], "fehler": zaehler["fehler"],
                            "frei_byte": gc.mem_free(), "rssi_dBm": STA.status("rssi") if HEIM and STA.isconnected() else None})
            await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n\r\n" + s)
        else:
            await antwort(w, "HTTP/1.0 404 Not Found\r\n\r\nunbekannt")
    except Exception as e:                        # Client weg (Strom abgebrochen) oder Fehler: Verbindung schließen
        if not isinstance(e, OSError):
            print("Fehler:", e)
    finally:
        try:
            w.close(); await w.wait_closed()
        except Exception:
            pass
        gc.collect()


async def haupt():
    await asyncio.start_server(anfrage, "0.0.0.0", 80)
    while True:
        await asyncio.sleep(30)
        try:
            geraete = len(APIF.status("stations"))
        except Exception:
            geraete = "?"
        print(jetzt(), " Zustand:", zaehler["bilder"], "Bilder,", zaehler["fehler"], "Fehler,", geraete, "Gerät(e) im WLAN,",
              gc.mem_free() // 1024, "kB frei")


# ---------------------------------------------------------------------------------------------------------- Start
def start():
    """Netze, Kamera, Verbindungsdaten, Webserver -- mit kurzer Meldung je Schritt."""
    global cam, AP, HEIM, STA, APIF
    print(jetzt(), " [1/3] WLAN wird eingerichtet ...")
    AP, HEIM, STA = netze(); APIF = network.WLAN(network.AP_IF)
    print(jetzt(), " [1/3] WLAN OK:", INFO["ap_name"], AP, "" if not HEIM else "+ Heimnetz " + HEIM)
    print(jetzt(), " [2/3] Kamera wird eingeschaltet ...")
    cam = kamera_starten()
    print(jetzt(), " [2/3] Kamera OK: VGA 640 x 480, JPEG")
    verbindungsdaten()
    print(jetzt(), " [3/3] Webserver OK -- Kamera bereit -- Webserver läuft.")
    try:
        asyncio.run(haupt())
    finally:                                     # „Stop“ in Thonny: Kamera sauber abschalten, damit der nächste Start geht
        try:
            cam.deinit(); print(jetzt(), " Kamera ausgeschaltet -- Programm beendet.")
        except Exception as e:
            print(jetzt(), " Kamera ließ sich nicht abschalten:", e)
        blitz.value(0)
        asyncio.new_event_loop()


# Start-Knopf in Thonny: die Datei wird ausgeführt und startet sofort.
if __name__ == "__main__":
    start()

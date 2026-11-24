# ==========================================================================================================
#  VHS-Kurs  „ESP32-CAM mit MicroPython“
#  Bewegungsmelder mit Bildübertragung – Kameraprogramm  (auf der Kamera als main.py)
# ----------------------------------------------------------------------------------------------------------
#  Autor:      Prof. Dr.-Ing. Ralph Wystup M.Sc.
#  Mitarbeit:  Claude (Anthropic, Claude Code)
#  Fassung:    1.4 vom 20.11.2026 (1.3: Seite von der Kamera, main.py; 1.2: fest JPEG; 1.1: Blitz nach der Übertragung; 1.0 vom 18.11.2026)
#  Gerät:      ESP32-CAM (AI Thinker, Kamera OV2640) auf dem USB-Brett ESP32-CAM-MB
#  Firmware:   MicroPython 1.27 mit Kameratreiber (github.com/cnadler86/micropython-camera-API, v0.6.2)
# ----------------------------------------------------------------------------------------------------------
#  1.4 (sein Befund 20.11.2026 „led blitzt aber ich sehe keine bilder!“): Die LED blitzte schon, wenn die Kamera das Bild an
#  das Netz übergeben hatte -- angekommen war es damit nicht. Jetzt blitzt sie erst, wenn die Seite den Empfang mit
#  /gesehen?nr=N meldet. Während ein Bild gesendet wird, pausiert der Wächter; gesendet wird in Stücken zu 4 kB.
#  Alle 5 s wird geprüft, ob das eigene WLAN noch an ist; sonst wird es neu eingerichtet (automatischer Neuaufbau).
#  Starten (1.3, sein Wort 20.11.2026 „das soll alles über die html gesteuert werden, das python programm auf der cam
#  dazu als main ablegen“): diese Datei liegt auf der Kamera als main.py und startet beim Einschalten von selbst.
#  Bedient wird alles über die Seite, die die Kamera selbst ausliefert: im WLAN der Kamera http://192.168.4.1/ öffnen
#  (Datei anzeige.html im Flash der Kamera = anzeige_bewegung_1.2.html; Wächter an/aus, Foto jetzt, LED-Test,
#  Einstellungen). Die URL steht beim Start und alle 5 s in der Ausgabe (print). Thonny ist nur zum Aufspielen nötig; zum Testen geht auch dort F5.
#
#  Was das Programm tut
#    1. Eigenes WLAN (Zugangspunkt), Adresse 192.168.4.1. Name aus kamera.json, sonst „ESP32CAM-xxxx“;
#       mit ap.json ({"kennwort": "..."}, mind. 8 Zeichen) geschützt, sonst offen.
#    2. Bewegung erkennen (1.2): die Kamera bleibt FEST auf Foto VGA 640 × 480 (JPEG) und wird nie umgeschaltet. Jedes
#       Foto wird auf dem Chip verkleinert entpackt (Modul jpeg, 160 × 120, Helligkeit Y), davon jeder 4. Bildpunkt
#       (40 × 30 = 1200 Punkte), verglichen
#       mit einem langsam mitlaufenden Hintergrund. Eine gleichmäßige Helligkeitsänderung (Belichtung) wird vorher
#       abgezogen. Bewegung = mehr als ANTEIL der Punkte weichen um mehr als SCHWELLE Graustufen ab.
#    3. Bei Bewegung: genau das Foto, in dem sie erkannt wurde, liegt zum Abholen bereit, die Anzeige-Seite holt es über
#       WLAN. Sobald ein Bewegungsbild ganz übertragen ist, blitzt die weiße LED einmal kurz (1.1, sein Wort 20.11.2026:
#       „immer wenn eine Bewegung erkannt wurde und ein Bild gemacht und übertragen wurde soll die weiße LED kurz
#       aufblitzen“). Danach lernt der Wächter den Hintergrund neu, damit der eigene Blitz nicht als Bewegung zählt.
#       Warum fest (gemessen an der echten Kamera 20.11.2026): das Umschalten Graubild <-> JPEG (1.0/1.1) scheiterte nach
#       einigen Minuten mit ESP_ERR_NOT_SUPPORTED, danach startete die Kamera erst nach Abziehen des Kabels wieder.
#    Sicherheit (1.2): liefert die Kamera 5-mal hintereinander kein Bild, wird sie neu gestartet; geht auch das nicht,
#       startet sich das ganze Gerät nach 3 s selbst neu (wie die RST-Taste) -- als main.py läuft es dann von allein weiter.
#    Sensor (1.3, gemessen an der echten Kamera 20.11.2026): blieb der Sensor hängen, meldete Camera() ESP_ERR_NOT_SUPPORTED,
#       auch nach Neustart des Chips; den Sensor über GPIO 32 (PWDN) kurz abzuschalten holte ihn sofort zurück. Darum
#       Camera(..., powerdown_pin=32) und vor jedem neuen Versuch GPIO 32 für 300 ms hoch.
#    4. Über USB (seriell) wird alle 5 s die Zeile „KAMERA-URL http://192.168.4.1/“ ausgegeben – daraus liest die
#       Anzeige-Seite die Adresse. Ist kein USB angeschlossen, läuft alles ohne diese Ausgabe weiter.
#    5. Webserver (Port 80), alle Antworten für die Anzeige-Seite freigegeben (CORS):
#         http://<adresse>/              (1.3) Anzeige- und Steuerseite anzeige.html aus dem Flash (fehlt sie: kurze Notseite)
#         http://<adresse>/ereignis      Nummer, Zeit und Größe des letzten Bewegungsbilds (JSON)
#         http://<adresse>/letztes.jpg   das letzte Bewegungsbild
#         http://<adresse>/status        Zähler, Einstellungen, freier Speicher (JSON)
#         http://<adresse>/steuern?wache=1&schwelle=25&anteil=0.02&ruhe_ms=3000&blitz_ms=120
#                                        (1.3) Wächter an/aus und Einstellungen; gespeichert in einstellungen.json
#         http://<adresse>/foto          (1.3) jetzt ein Foto machen (zählt wie eine Bewegung, Anteil 0)
#         http://<adresse>/blitz         (1.3) LED-Test: einmal kurz blitzen
#         http://<adresse>/gesehen?nr=N  (1.4) die Seite meldet: Bild N ist angekommen -> LED blitzt einmal
# ==========================================================================================================
import asyncio, gc, json, network, time, ubinascii
import jpeg
from machine import Pin, reset
from camera import Camera, PixelFormat, FrameSize

FASSUNG = "1.4"
SCHWELLE = 25          # Graustufen (0…255), ab der ein Bildpunkt als „verändert“ zählt
ANTEIL = 0.02          # Anteil veränderter Punkte, ab dem Bewegung gemeldet wird (2 % = 24 von 1200 Punkten)
RUHE_MS = 3000         # Mindestabstand zwischen zwei Bewegungsbildern
EINLERNEN = 8          # so viele Prüfbilder nach dem Start und nach jedem Foto nur zum Lernen des Hintergrunds
BLITZ_MS = 120         # so lange blitzt die LED, wenn ein Bewegungsbild übertragen ist
WACHE = True           # 1.3: Wächter an (über die Seite schaltbar)
GRENZEN = {"schwelle": (5, 100), "anteil": (0.005, 0.5), "ruhe_ms": (1000, 60000), "blitz_ms": (20, 1000)}
SENSOR_AUS = 32       # PWDN des Bildsensors (AI Thinker)
B, H, SCHRITT = 160, 120, 4                      # Foto verkleinert entpackt auf 160 × 120, jeder 4. Punkt in beide Richtungen
DEC = jpeg.Decoder(pixel_format="CbYCrY", scale_width=B, scale_height=H, return_bytes=True)   # Y = Helligkeit an jeder 2. Stelle

blitz = Pin(4, Pin.OUT, value=0)                 # Blitz-LED an GPIO4
INDEX = [y * B + x for y in range(SCHRITT // 2, H, SCHRITT) for x in range(SCHRITT // 2, B, SCHRITT)]
LETZTES = {"nr": 0, "ms": 0, "byte": 0, "anteil": 0.0}
BILD = [None]                                    # das letzte Bewegungsbild (JPEG)
GEMELDET = [0]                                   # Nummer des letzten Bilds, für das schon geblitzt wurde
NEU_LERNEN = [False]                             # nach dem Blitz: Hintergrund neu lernen
SENDET = [0]                                     # 1.4: so viele Bilder werden gerade gesendet (Wächter pausiert)
zaehler = {"graubilder": 0, "fotos": 0, "fehler": 0}
cam = None
INFO = {}
URL = "http://192.168.4.1/"
START_MS = time.ticks_ms()


# ---------------------------------------------------------------------------------------------------------- Netz
def _lies(name):
    try:
        return json.load(open(name))
    except (OSError, ValueError):
        return None


def netz():
    """Eigenes WLAN (Zugangspunkt)."""
    ap = network.WLAN(network.AP_IF); ap.active(True)
    k = _lies("kamera.json") or {}
    name = k.get("name") or "ESP32CAM-" + ubinascii.hexlify(ap.config("mac")[-2:]).decode()
    a = _lies("ap.json")
    if a and len(a.get("kennwort", "")) >= 8:
        ap.config(essid=name, authmode=network.AUTH_WPA2_PSK, password=a["kennwort"]); offen = False
    else:
        ap.config(essid=name, authmode=network.AUTH_OPEN); offen = True
    del a
    INFO.update(name=name, offen=offen, ip=ap.ifconfig()[0])
    return ap


def einstellungen_laden():
    """1.3: gespeicherte Einstellungen (einstellungen.json) übernehmen, nur gültige Werte."""
    e = _lies("einstellungen.json") or {}
    setzen(e, speichern=False)


def setzen(e, speichern=True):
    """1.3: Einstellungen prüfen und übernehmen; gibt eine Liste der Fehler zurück (leer = alles übernommen)."""
    global SCHWELLE, ANTEIL, RUHE_MS, BLITZ_MS, WACHE
    fehler = []; neu = {}
    for k, (lo, hi) in GRENZEN.items():
        if k in e:
            try:
                v = float(e[k])
            except (TypeError, ValueError):
                fehler.append(k + ": keine Zahl"); continue
            if not lo <= v <= hi:
                fehler.append("%s: %s liegt nicht in %s … %s" % (k, e[k], lo, hi)); continue
            neu[k] = v
    if "wache" in e:
        neu["wache"] = str(e["wache"]) in ("1", "true", "True", "an")
    if fehler:
        return fehler                              # nichts übernehmen, wenn ein Wert falsch ist
    if "schwelle" in neu: SCHWELLE = int(neu["schwelle"])
    if "anteil" in neu: ANTEIL = neu["anteil"]
    if "ruhe_ms" in neu: RUHE_MS = int(neu["ruhe_ms"])
    if "blitz_ms" in neu: BLITZ_MS = int(neu["blitz_ms"])
    if "wache" in neu:
        if neu["wache"] and not WACHE: NEU_LERNEN[0] = True
        WACHE = neu["wache"]
    if speichern and neu:
        try:
            with open("einstellungen.json", "w") as f:
                json.dump({"schwelle": SCHWELLE, "anteil": ANTEIL, "ruhe_ms": RUHE_MS, "blitz_ms": BLITZ_MS, "wache": WACHE}, f)
        except OSError as x:
            print(jetzt(), " Einstellungen nicht gespeichert:", x)
        print(jetzt(), " Einstellungen: Wächter", "an" if WACHE else "aus", "· Schwelle", SCHWELLE, "· Anteil", ANTEIL,
              "· Ruhe", RUHE_MS, "ms · Blitz", BLITZ_MS, "ms")
    return []


def abfrage_lesen(pfad):
    """'/steuern?a=1&b=2' -> {'a': '1', 'b': '2'}"""
    e = {}
    if "?" in pfad:
        for teil in pfad.split("?", 1)[1].split("&"):
            if "=" in teil:
                k, v = teil.split("=", 1); e[k] = v
    return e


def zustand_json():
    return json.dumps({"fassung": FASSUNG, "wlan": INFO.get("name"), "url": URL, "wache": WACHE, "graubilder": zaehler["graubilder"],
                       "fotos": zaehler["fotos"], "fehler": zaehler["fehler"], "schwelle": SCHWELLE, "anteil": ANTEIL,
                       "ruhe_ms": RUHE_MS, "blitz_ms": BLITZ_MS, "frei_byte": gc.mem_free(),
                       "laufzeit_s": time.ticks_diff(time.ticks_ms(), START_MS) // 1000})


def neues_bild(b, a):
    """Ein Bild als neues Ereignis bereitlegen (Bewegung oder von Hand)."""
    BILD[0] = None; gc.collect(); BILD[0] = b
    zaehler["fotos"] += 1
    LETZTES.update(nr=LETZTES["nr"] + 1, ms=time.ticks_ms(), byte=len(b), anteil=round(a, 3))


def wlan_pruefen():
    """1.4: Ist der Zugangspunkt aus (sollte nie sein), wird er neu eingerichtet -- die Seite verbindet dann von selbst neu."""
    try:
        if network.WLAN(network.AP_IF).active():
            return
    except Exception:
        pass
    print(jetzt(), " WLAN war aus -- wird neu eingerichtet")
    try:
        netz()
    except Exception as e:
        print(jetzt(), " WLAN neu einrichten ging nicht:", e)


def jetzt():
    t = time.localtime(); return "%02d:%02d:%02d" % (t[3], t[4], t[5])


def url_zeile():
    """Maschinenlesbare Zeile für die Anzeige-Seite (seriell). Ohne USB geht print ins Leere – kein Fehler."""
    try:
        print("KAMERA-URL", URL, "WLAN", INFO["name"])
    except Exception:
        pass


# ---------------------------------------------------------------------------------------------------------- Kamera
def sensor_aus_an():
    """1.3: Bildsensor über PWDN (GPIO 32) 300 ms abschalten -- holt einen hängenden Sensor zurück (gemessen 20.11.2026)."""
    p = Pin(SENSOR_AUS, Pin.OUT); p.value(1); time.sleep_ms(300); p.value(0); time.sleep_ms(300)


def kamera_an():
    """Kamera einschalten: fest Foto VGA 640 × 480 (JPEG), Sensor mit PWDN an GPIO 32. Drei Versuche, dazwischen den Sensor
    abschalten; geht es nicht: Gerät neu starten."""
    global cam
    for versuch in range(3):
        try:
            cam = Camera(pixel_format=PixelFormat.JPEG, frame_size=FrameSize.VGA, jpeg_quality=85, fb_count=2,
                         powerdown_pin=SENSOR_AUS)
            return
        except OSError as e:
            print(jetzt(), " Kamera startet nicht (", e, ") -- Sensor aus/an, neuer Versuch ...")
            try:
                Camera(init=False).deinit()
            except Exception:
                pass
            cam = None; gc.collect(); sensor_aus_an()
    neustart("Kamera lässt sich nicht starten")


def neustart(grund):
    """Letzte Sicherung: das ganze Gerät neu starten (wie die RST-Taste)."""
    print("!" * 64)
    print("!  " + grund + " -- Gerät startet in 3 s neu (wie die RST-Taste).")
    print("!  Läuft das Programm als main.py, geht es danach von allein weiter.")
    print("!" * 64)
    blitz.value(0); time.sleep_ms(3000); reset()


def kamera_neu():
    """Kamera aus und wieder an (nach 5 Fehlbildern hintereinander)."""
    global cam
    print(jetzt(), " Kamera liefert keine Bilder -- wird neu gestartet")
    try:
        cam.deinit()
    except Exception:
        pass
    cam = None; gc.collect(); time.sleep_ms(500)
    kamera_an()


def aufnahme():
    """Ein Foto aufnehmen; gibt (1200 Messpunkte als bytearray, JPEG) zurück oder (None, None) bei Fehler."""
    try:
        f = cam.capture()
        b = bytes(f) if f else None
        cam.free_buffer()
        if not b or b[:2] != b"\xff\xd8":
            zaehler["fehler"] += 1; return None, None
        px = DEC.decode(b)
        p = bytearray(px[2 * k + 1] for k in INDEX)
    except Exception as e:
        zaehler["fehler"] += 1; print(jetzt(), " Bildfehler:", e); return None, None
    zaehler["graubilder"] += 1
    return p, b


def vergleich(neu, hinter):
    """Anteil der Messpunkte, die nach Abzug der mittleren Helligkeitsänderung um mehr als SCHWELLE abweichen."""
    n = len(neu)
    versatz = (sum(neu) - sum(hinter)) // n       # gleichmäßige Änderung (Belichtung) herausnehmen
    z = 0
    for i in range(n):
        d = neu[i] - hinter[i] - versatz
        if d > SCHWELLE or d < -SCHWELLE:
            z += 1
    return z / n


def nachfuehren(neu, hinter):
    """Hintergrund langsam mitführen: 3/4 alt + 1/4 neu."""
    for i in range(len(neu)):
        hinter[i] = (3 * hinter[i] + neu[i]) >> 2


async def blitzen(nr):
    """Bewegungsbild nr ist bei der Seite angekommen (1.4: /gesehen): LED einmal kurz, dann Hintergrund neu lernen lassen."""
    blitz.value(1)
    await asyncio.sleep_ms(BLITZ_MS)
    blitz.value(0)
    NEU_LERNEN[0] = True
    print(jetzt(), " Bild Nr. %d bei der Seite angekommen -- LED geblitzt" % nr)


# ---------------------------------------------------------------------------------------------------------- Wächter
async def waechter():
    hinter = None; lernen = EINLERNEN; letzt = time.ticks_ms() - RUHE_MS; fehl = 0
    while True:
        if NEU_LERNEN[0]:                         # 1.1: eigener Blitz war im Bild
            NEU_LERNEN[0] = False; hinter = None; lernen = EINLERNEN
        if SENDET[0]:                             # 1.4: Bild wird gesendet -> Rechenzeit dem Senden lassen
            await asyncio.sleep_ms(50); continue
        if not WACHE:                             # 1.3: Wächter über die Seite ausgeschaltet
            hinter = None; lernen = EINLERNEN
            await asyncio.sleep_ms(200); continue
        p, b = aufnahme()
        if p is None:
            fehl += 1
            if fehl >= 5:                         # 1.2: 5 Fehlbilder hintereinander -> Kamera neu starten
                fehl = 0; kamera_neu(); hinter = None; lernen = EINLERNEN
            await asyncio.sleep_ms(100); continue
        fehl = 0
        if hinter is None:
            hinter = p
        elif lernen > 0:
            nachfuehren(p, hinter); lernen -= 1
        else:
            a = vergleich(p, hinter)
            if a > ANTEIL and time.ticks_diff(time.ticks_ms(), letzt) >= RUHE_MS:
                letzt = time.ticks_ms()            # 1.2: das Foto ist genau dieses Bild
                if b:
                    neues_bild(b, a)
                    print(jetzt(), " BEWEGUNG Nr. %d  (%d %% der Punkte verändert)  Foto %d kB" % (LETZTES["nr"], round(a * 100), len(b) // 1024))
                hinter = None; lernen = EINLERNEN   # neuer Zustand wird Hintergrund (kein Dauerauslösen)
            else:
                nachfuehren(p, hinter)
        p = b = None
        await asyncio.sleep_ms(30)


# ---------------------------------------------------------------------------------------------------------- Webserver
FREI = "Access-Control-Allow-Origin: *\r\nAccess-Control-Allow-Private-Network: true\r\nCache-Control: no-store\r\n"
SEITE = """<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>ESP32-CAM Bewegung</title><style>body{font-family:sans-serif;background:#fff;color:#000;margin:1em}img{max-width:100%;border:1px solid #888}</style>
</head><body><h1>ESP32-CAM Bewegungsmelder</h1><p id="t">noch keine Bewegung</p><img id="b" alt="letztes Bewegungsbild">
<p>Die volle Anzeige mit Steuerung und Bildergalerie ist die Datei <b>anzeige.html</b> auf der Kamera (fehlt hier) bzw. <b>anzeige_bewegung_1.2.html</b>.</p>
<script>let n=0;setInterval(async()=>{try{const e=await(await fetch('/ereignis')).json();if(e.nr!==n){n=e.nr;
document.getElementById('b').src='/letztes.jpg?nr='+n;document.getElementById('t').textContent='Bewegung Nr. '+n;}}catch(x){}},1000)</script>
</body></html>"""


async def antwort(w, kopf, rumpf=b""):
    w.write(kopf.encode())
    if rumpf:
        w.write(rumpf)
    await w.drain()


async def seite_senden(w):
    """1.3: die Anzeige- und Steuerseite anzeige.html aus dem Flash in Stücken senden; fehlt sie, die kurze Notseite."""
    try:
        n = __import__("os").stat("anzeige.html")[6]
        f = open("anzeige.html", "rb")
    except OSError:
        s = SEITE.encode()
        await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n" + FREI + "Content-Length: %d\r\n\r\n" % len(s), s)
        return
    try:
        w.write(("HTTP/1.0 200 OK\r\nContent-Type: text/html; charset=utf-8\r\n" + FREI + "Content-Length: %d\r\n\r\n" % n).encode())
        puffer = bytearray(2048)
        while True:
            k = f.readinto(puffer)
            if not k:
                break
            w.write(puffer[:k] if k < len(puffer) else puffer)
            await w.drain()
    finally:
        f.close()


async def anfrage(r, w):
    try:
        zeile = (await r.readline()).decode()
        while (await r.readline()) not in (b"\r\n", b""):
            pass
        teile = zeile.split(" ")
        art = teile[0] if teile else "GET"
        pfad = teile[1] if len(teile) > 1 else "/"
        if art == "OPTIONS":                       # Vorabfrage des Browsers (Seite vom PC, Kamera im eigenen Netz)
            await antwort(w, "HTTP/1.0 204 No Content\r\n" + FREI + "Access-Control-Allow-Methods: GET\r\nAccess-Control-Allow-Headers: *\r\n\r\n")
        elif pfad == "/" or pfad.startswith("/?") or pfad.startswith("/index"):
            await seite_senden(w)
        elif pfad.startswith("/ereignis"):
            s = json.dumps({"nr": LETZTES["nr"], "alter_ms": time.ticks_diff(time.ticks_ms(), LETZTES["ms"]) if LETZTES["nr"] else None,
                            "byte": LETZTES["byte"], "anteil": LETZTES["anteil"], "fassung": FASSUNG})
            await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n" + FREI + "\r\n" + s)
        elif pfad.startswith("/letztes.jpg"):
            b = BILD[0]; nr = LETZTES["nr"]
            if b:
                SENDET[0] += 1
                try:                              # 1.4: in Stücken senden, Wächter pausiert solange
                    w.write(("HTTP/1.0 200 OK\r\nContent-Type: image/jpeg\r\n" + FREI + "X-Nr: %d\r\nContent-Length: %d\r\n\r\n" % (nr, len(b))).encode())
                    mv = memoryview(b)
                    for i in range(0, len(b), 4096):
                        w.write(mv[i:i + 4096]); await w.drain()
                finally:
                    SENDET[0] -= 1
            else:
                await antwort(w, "HTTP/1.0 404 Not Found\r\n" + FREI + "\r\nnoch kein Bild")
        elif pfad.startswith("/gesehen"):          # 1.4: die Seite hat das Bild angezeigt -> erst jetzt blitzen
            try:
                nr = int(abfrage_lesen(pfad).get("nr", "0"))
            except ValueError:
                nr = 0
            neu = GEMELDET[0] < nr <= LETZTES["nr"]
            if neu:
                GEMELDET[0] = nr; asyncio.create_task(blitzen(nr))
            await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n" + FREI + "\r\n" + json.dumps({"nr": nr, "blitz": neu}))
        elif pfad.startswith("/status"):
            await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n" + FREI + "\r\n" + zustand_json())
        elif pfad.startswith("/steuern"):          # 1.3: Wächter und Einstellungen von der Seite
            f = setzen(abfrage_lesen(pfad))
            if f:
                await antwort(w, "HTTP/1.0 400 Bad Request\r\nContent-Type: application/json\r\n" + FREI + "\r\n" + json.dumps({"fehler": f}))
            else:
                await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n" + FREI + "\r\n" + zustand_json())
        elif pfad.startswith("/foto"):             # 1.3: Foto von Hand
            p, b = aufnahme()
            if b:
                neues_bild(b, 0.0); NEU_LERNEN[0] = True
                print(jetzt(), " FOTO von Hand Nr. %d  %d kB" % (LETZTES["nr"], len(b) // 1024))
                await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n" + FREI + "\r\n" + json.dumps({"nr": LETZTES["nr"], "byte": len(b)}))
            else:
                await antwort(w, "HTTP/1.0 503 Service Unavailable\r\nContent-Type: application/json\r\n" + FREI + "\r\n" + json.dumps({"fehler": "Kamera lieferte kein Bild"}))
        elif pfad.startswith("/blitz"):            # 1.3: LED-Test
            blitz.value(1); await asyncio.sleep_ms(BLITZ_MS); blitz.value(0); NEU_LERNEN[0] = True
            await antwort(w, "HTTP/1.0 200 OK\r\nContent-Type: application/json\r\n" + FREI + "\r\n" + json.dumps({"blitz_ms": BLITZ_MS}))
        else:
            await antwort(w, "HTTP/1.0 404 Not Found\r\n" + FREI + "\r\nunbekannt")
    except Exception as e:
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
    asyncio.create_task(waechter())
    n = 0
    while True:
        url_zeile()                               # alle 5 s, damit die Anzeige-Seite sie auch später noch findet
        wlan_pruefen()                            # 1.4: WLAN weg -> neu einrichten
        await asyncio.sleep(5)
        n += 1
        if n % 6 == 0:
            print(jetzt(), " Zustand:", zaehler["graubilder"], "Prüfbilder,", zaehler["fotos"], "Bewegungsbilder,",
                  zaehler["fehler"], "Fehler,", gc.mem_free() // 1024, "kB frei")


# ---------------------------------------------------------------------------------------------------------- Start
def start():
    global URL
    print(jetzt(), " [1/3] WLAN wird eingerichtet ...")
    einstellungen_laden()
    netz()
    URL = "http://%s/" % INFO["ip"]
    print(jetzt(), " [1/3] WLAN OK:", INFO["name"], INFO["ip"], "(offen)" if INFO["offen"] else "(mit Kennwort aus ap.json)")
    print(jetzt(), " [2/3] Kamera wird eingeschaltet ...")
    kamera_an()
    print(jetzt(), " [2/3] Kamera OK: fest Foto VGA 640 x 480, Erkennung im verkleinerten Foto, LED blitzt nach der Übertragung")
    print()
    print("#" * 64)
    print("#  1. WLAN verbinden :", INFO["name"], " (Kennwort: keins)" if INFO["offen"] else " (Kennwort: Aushang)")
    print("#  2. Im Browser öffnen:", URL, " (die Kamera liefert die Seite selbst)")
    print("#     (wahlweise auf dem PC: anzeige_bewegung_1.2.html mit USB und Speicherordner)")
    print("#  Bewegung: Schwelle", SCHWELLE, "Graustufen, ab", int(ANTEIL * 100), "% der Punkte, Ruhe", RUHE_MS // 1000, "s")
    print("#" * 64)
    print(jetzt(), " [3/3] Wächter und Webserver laufen. „Stop“ beendet.")
    try:
        asyncio.run(haupt())
    finally:
        blitz.value(0)
        try:
            cam.deinit(); print(jetzt(), " Kamera ausgeschaltet -- Programm beendet.")
        except Exception as e:
            print(jetzt(), " Kamera ließ sich nicht abschalten:", e)
        asyncio.new_event_loop()


if __name__ == "__main__":
    start()

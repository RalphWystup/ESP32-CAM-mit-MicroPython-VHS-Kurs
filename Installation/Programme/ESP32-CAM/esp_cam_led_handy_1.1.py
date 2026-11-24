# ==========================================================================================================
#  VHS-Kurs  „ESP32-CAM mit MicroPython“
#  Beispiel 3: LED vom Handy aus schalten  (led_handy.py)
# ----------------------------------------------------------------------------------------------------------
#  Autor:      Prof. Dr.-Ing. Ralph Wystup M.Sc.
#  Mitarbeit:  Claude (Anthropic, Claude Code)
#  Fassung:    1.1 vom 17.11.2026 – nach seinem led_blink_Handy.py, angepasst an die ESP32-CAM
# ----------------------------------------------------------------------------------------------------------
#  Eine Webseite (Handy oder Laptop) schaltet die LED an, aus oder lässt sie blinken; das Blink-Intervall
#  ist einstellbar. Ist ein OLED-Display (SSD1306, 128 × 64, I2C) angeschlossen, zeigt es IP-Adresse und
#  LED-Zustand; ohne Display läuft das Programm genauso (Ausgabe dann nur in Thonny).
#
#  Anpassungen an die ESP32-CAM gegenüber dem ESP32-DevKit:
#    * LED: weiße Blitz-LED vorne, GPIO 4, 1 = an (sehr hell); an GPIO 2 hat die ESP32-CAM keine LED, die rote LED
#      hängt bei diesen Brettern fest an VCC (1.1).
#    * OLED: SCL an IO14, SDA an IO15 (GPIO 21/22 gehören hier zur Kamera), VCC 3,3 V, GND.
#    * WLAN: KEIN Kennwort im Programm. Die Kamera spannt ihr eigenes WLAN auf (Name aus kamera.json,
#      z. B. „VHS-CAM-1“, Adresse 192.168.4.1); liegt wlan.json auf der Kamera, geht sie zusätzlich ins
#      Heimnetz – wie das Kameraprogramm.
#  In Thonny: Datei öffnen, grüner Start-Knopf; im Handy ins WLAN der Kamera, Browser: http://192.168.4.1/
#  „Stop“ in Thonny beendet das Programm. Braucht ssd1306.py auf der Kamera (liegt dort schon).
# ==========================================================================================================
import network, json, time, ubinascii, _thread
import usocket as socket
from machine import Pin, SoftI2C

LED_PIN = 4                       # weiße Blitz-LED vorne, 1 = an
LOW_AKTIV = False
OLED_SCL, OLED_SDA = 14, 15       # freie Pins der ESP32-CAM

led = Pin(LED_PIN, Pin.OUT)
led_an_zustand = False
blink_state = False
blink_interval = 0.5              # Sekunden


def led_setzen(an):
    global led_an_zustand
    led_an_zustand = an
    led.value((0 if an else 1) if LOW_AKTIV else (1 if an else 0))


def _lies(name):
    try:
        return json.load(open(name))
    except (OSError, ValueError):
        return None


# ---------------------------------------------------------------------------------------------------------- WLAN
ap = network.WLAN(network.AP_IF); ap.active(True)
name = (_lies("kamera.json") or {}).get("name") or "ESP32CAM-" + ubinascii.hexlify(ap.config("mac")[-2:]).decode()
a = _lies("ap.json")
if a and len(a.get("kennwort", "")) >= 8:
    ap.config(essid=name, authmode=network.AUTH_WPA2_PSK, password=a["kennwort"]); sicherheit = "mit Kennwort"
else:
    ap.config(essid=name, authmode=network.AUTH_OPEN); sicherheit = "offen"
del a
ip_address = ap.ifconfig()[0]
heim_ip = None
z = _lies("wlan.json")
if z:
    sta = network.WLAN(network.STA_IF); sta.active(True); sta.connect(z["ssid"], z["kennwort"]); del z
    t0 = time.time()
    while not sta.isconnected() and time.time() - t0 < 15:
        time.sleep(0.5)
    if sta.isconnected():
        heim_ip = sta.ifconfig()[0]

print("=" * 50)
print(" VHS-Kurs ESP32-CAM -- LED vom Handy aus")
print(" WLAN der Kamera :", name, "(" + sicherheit + ")")
print(" Im Browser      : http://%s/" % ip_address)
if heim_ip:
    print(" im Heimnetz     : http://%s/" % heim_ip)
print("=" * 50)

# ---------------------------------------------------------------------------------------------------------- OLED (freiwillig)
oled = None
try:
    import ssd1306
    i2c = SoftI2C(scl=Pin(OLED_SCL), sda=Pin(OLED_SDA))
    if 0x3C in i2c.scan():
        oled = ssd1306.SSD1306_I2C(128, 64, i2c)
        print("OLED-Display gefunden (SCL IO%d, SDA IO%d)" % (OLED_SCL, OLED_SDA))
    else:
        print("kein OLED-Display angeschlossen -- es geht auch ohne")
except Exception as e:
    print("OLED nicht nutzbar:", e)


# ---------------------------------------------------------------------------------------------------------- Webserver
def seite():
    zustand = "BLINKT" if blink_state else ("AN" if led_an_zustand else "AUS")
    return """HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Connection: close

<html><head><meta name="viewport" content="width=device-width"><style>
body {{ font-family: Arial, sans-serif; background-color: #f0f8ff; text-align: center; padding: 20px; }}
h1 {{ color: #4CAF50; }}
.button {{ display: inline-block; padding: 15px 30px; font-size: 18px; margin: 10px; border: none; border-radius: 5px;
          text-decoration: none; color: white; }}
.on {{ background-color: #4CAF50; }} .off {{ background-color: #f44336; }} .blink {{ background-color: #2196F3; }}
.status {{ font-size: 20px; margin-top: 20px; color: #333; }}
input[type="number"] {{ padding: 8px; font-size: 16px; width: 80px; margin: 10px; }}
</style></head><body>
<h1>ESP32-CAM - LED Steuerung</h1><p>VHS-Kurs &middot; {name}</p>
<a href="/led/on" class="button on">LED Einschalten</a>
<a href="/led/off" class="button off">LED Ausschalten</a>
<a href="/led/blink" class="button blink">LED Blink-Modus</a>
<div><label>Blink-Intervall (0.1-5 Sek.):</label><br>
<input type="number" step="0.1" min="0.1" max="5" value="{iv}" id="interval">
<button onclick="window.location.href='/interval?value='+document.getElementById('interval').value">Setzen</button></div>
<div class="status">LED Zustand: {z}</div>
</body></html>
""".format(name=name, iv=blink_interval, z=zustand)


def web_server():
    global blink_state, blink_interval
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(socket.getaddrinfo("0.0.0.0", 80)[0][-1])
    s.listen(2)
    while True:
        cl, addr = s.accept()
        try:
            anfrage = str(cl.recv(1024))
            if "GET /led/on" in anfrage:
                blink_state = False; led_setzen(True); print("LED eingeschaltet")
            elif "GET /led/off" in anfrage:
                blink_state = False; led_setzen(False); print("LED ausgeschaltet")
            elif "GET /led/blink" in anfrage:
                blink_state = True; print("LED Blink-Modus")
            elif "GET /interval?value=" in anfrage:
                try:
                    iv = float(anfrage.split("value=")[1].split(" ")[0])
                    if 0.1 <= iv <= 5.0:
                        blink_interval = iv; print("Blink-Intervall", iv, "s")
                except ValueError:
                    print("Ungültiges Intervall")
            cl.send(seite())
        except OSError:
            pass
        finally:
            cl.close()


# ---------------------------------------------------------------------------------------------------------- Blinken und Anzeige
def anzeigen_und_blinken():
    while True:
        if blink_state:
            led_setzen(not led_an_zustand); time.sleep(blink_interval); zustand = "BLINKT"
        else:
            time.sleep(0.5); zustand = "AN" if led_an_zustand else "AUS"
        if oled:
            oled.fill(0)
            oled.text("LED Steuerung", 0, 0)
            oled.text("IP: " + ip_address, 0, 20)
            oled.text("LED: " + zustand, 0, 40)
            if blink_state:
                oled.text("Int: %.1fs" % blink_interval, 0, 52)
            oled.show()


led_setzen(False)
_thread.start_new_thread(web_server, ())
try:
    anzeigen_und_blinken()
finally:
    led_setzen(False)

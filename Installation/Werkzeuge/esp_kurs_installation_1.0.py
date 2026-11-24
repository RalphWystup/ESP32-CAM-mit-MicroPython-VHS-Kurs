#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ==========================================================================================================
#  VHS-Kurs  „ESP32 mit MicroPython“
#  Gemeinsame Installationsseite für ESP32-CAM und ESP32-WROOM-32  (esp_kurs_installation_1.0.py)
# ----------------------------------------------------------------------------------------------------------
#  Autor:      Prof. Dr.-Ing. Ralph Wystup M.Sc.
#  Mitarbeit:  Claude (Anthropic, Claude Code)
#  Fassung:    1.0 vom 24.11.2026 -- gemeinsames Installationsprogramm (sein Wort: „nur das gemeinsame instalationsprogramm rein“): auf der Seite
#              wird das Brett gewählt (ESP32-Brett oder ESP32-CAM), darunter arbeiten die beiden geprüften Konfigurationen unverändert
#              (esp_kurs_esp32_konfigurieren_1.1.py, esp_kurs_kameras_konfigurieren_1.5.py); die Wahl steht in Werkzeuge\brett.txt für Thonny_starten.bat.
#              Aus esp_kurs_esp32_installieren_1.2.py; dort sein Wort: „alles so einrichten dass alles nach drücken der start batt von alleine läuft“: Name mit dem
#              Windows-Benutzernamen vorbelegt, die Installation startet von selbst (10 s Vorlauf, abbrechbar), sobald genau ein Brett angeschlossen ist.
#              1.1: Teilnehmerfassung: Name statt Nummer (WLAN „VHS-ESP-<Name>“), ohne Dozententext; Arbeit macht
#              esp_kurs_esp32_konfigurieren_1.1.py.  1.0: aus esp_kurs_installieren_1.4.py (ESP32-CAM) für das ESP32-WROOM-32-Brett abgeleitet.  (Herkunft 1.4: Konfiguration 1.5 -- Anschlussfehler führt nie zum Flashen.  1.3: Konfiguration 1.4 -- ohne main.py, Probelauf wie in Thonny.  1.2: Fortschrittsbalken Flashen/Aufspielen, Kameranummer = nächste freie aus dem Protokoll;
#              sein Wort „den downlod verlauf bitte auch anzeigen“.  1.1: liegt in Dozent\Werkzeuge; Kameradateien aus Dozent\Kameraprogramme, Protokoll Dozent\protokoll)
# ----------------------------------------------------------------------------------------------------------
#  Sein Wort: „ich würde dann die cam an einen usb port anschliesen und am besten in einer html einen knopf drücken zum fertigen
#  installieren der boards auch mit anzeige der programme die darauf geladen werden sollen. Und es muss dann unter thonny laufen.
#  und du sollst den Prozess überwachen können und wenn nötig eingreifen“.
#  Ein kleiner Webserver NUR auf diesem PC (http://127.0.0.1:8765/):
#    *  Seite: Programme, die auf das Brett kommen (Fassung, Zweck, Größe, Inhalt ansehen), erkannte Anschlüsse, Brettnummer,
#       Knopf „Brett installieren“, laufende Schritte; verlangt ein Schritt etwas (z. B. IO0 halten), erscheint die Anweisung mit Knopf.
#    *  Die Arbeit macht esp_kurs_esp32_konfigurieren_1.0.py (derselbe Code wie auf der Kommandozeile).
#    *  Jede Zeile geht zusätzlich nach protokoll\installation_<Datum>.log; GET /zustand liefert den Stand als JSON, POST /antwort und
#       POST /start greifen ein (so kann Claude über die Brücke überwachen und eingreifen: esp_kurs_ueberwachen_1.0.py).
#  Aufruf: ESP32_installieren.bat (Doppelklick) oder python esp_kurs_esp32_installieren_1.1.py
# ==========================================================================================================
import datetime, html, importlib.util, json, os, re, sys, threading, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HIER = os.path.dirname(os.path.abspath(__file__)); PORT = 8765
def lade_modul(name, datei):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HIER, datei)); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
OBEN = os.path.dirname(HIER)
KK_ESP = lade_modul("kk_esp", "esp_kurs_esp32_konfigurieren_1.1.py"); KK_CAM = lade_modul("kk_cam", "esp_kurs_kameras_konfigurieren_1.5.py")
KK_ESP.PROGRAMME = os.path.join(OBEN, "Programme", "ESP32"); KK_ESP.FW = os.path.join(KK_ESP.PROGRAMME, "ESP32_GENERIC-20251209-v1.27.0.bin"); KK_ESP.PROTOKOLL = os.path.join(OBEN, "esp32_protokoll.csv")
KK_CAM.PROGRAMME = os.path.join(OBEN, "Programme", "ESP32-CAM"); KK_CAM.FW = os.path.join(KK_CAM.PROGRAMME, "firmware.bin"); KK_CAM.PROTOKOLL = os.path.join(OBEN, "kameras_protokoll.csv")
BRETTER = {"esp": KK_ESP, "cam": KK_CAM}; BRETT_DATEI = os.path.join(HIER, "brett.txt")
def brett_lesen():
    try: b = open(BRETT_DATEI, encoding="utf-8").read().strip()
    except OSError: b = ""
    return b if b in BRETTER else "esp"
os.makedirs(os.path.join(OBEN, "protokoll"), exist_ok=True)
LOG = os.path.join(OBEN, "protokoll", f"installation_{datetime.date.today():%Y-%m-%d}.log")

ZWECK = {"esp": {"blink.py": "Beispiel 1: blaue LED (GPIO 2) blinkt", "pwm.py": "Beispiel 2: LED per PWM heller/dunkler",
                 "led_handy.py": "Beispiel 3: LED vom Handy aus schalten (eigenes WLAN, mit OLED an GPIO 22/21)", "ssd1306.py": "Treiber für das OLED-Display (micropython-lib)",
                 "esp.json": "Name des Bretts = Name seines WLANs"},
         "cam": {"kamera.py": "Kameraprogramm: in Thonny Start drücken; eigenes WLAN, Livebild im Browser", "blink.py": "Beispiel 1: weiße Blitz-LED blinkt",
                 "pwm.py": "Beispiel 2: Blitz-LED per PWM heller/dunkler", "led_handy.py": "Beispiel 3: LED vom Handy aus schalten (mit OLED an IO14/15)",
                 "ssd1306.py": "Treiber für das OLED-Display (micropython-lib)", "kamera.json": "Name der Kamera = Name ihres WLANs"}}
Z = {"laeuft": False, "nummer": None, "brett": "esp", "zeilen": [], "frage": None, "ergebnis": None, "beginn": None, "fortschritt": None}
SPERRE = threading.Lock(); ANTWORT = threading.Event(); ANTWORT_TEXT = [""]


def melde(*a, sep=" ", end="\n", flush=False, **_):
    text = sep.join(str(x) for x in a) + ("" if end == "\n" else end)
    with SPERRE:
        for z in text.split("\n"):
            Z["zeilen"].append(z)
        del Z["zeilen"][:-600]
    with open(LOG, "a", encoding="utf-8") as f:
        for z in text.split("\n"):
            f.write(f"{datetime.datetime.now():%H:%M:%S} {z}\n")


def frage(text=""):
    """ersetzt input() im Konfigurationsprogramm: Frage auf der Seite, warten auf den Knopf (oder POST /antwort)."""
    text = text.replace("danach Eingabetaste drücken ...", "Danach „Erledigt, weiter“ klicken.").replace(">>> ", "").strip()
    melde(f"  ? {text}")
    with SPERRE: Z["frage"] = text
    ANTWORT.clear(); ANTWORT.wait()
    with SPERRE: Z["frage"] = None
    melde(f"  -> Antwort: {ANTWORT_TEXT[0] or '(weiter)'}")
    return ANTWORT_TEXT[0]


def fortschritt(art, prozent, text=""):
    """ersetzt KK.fortschritt: Balken auf der Seite; ins Protokoll nur je 25 %."""
    with SPERRE:
        alt = Z["fortschritt"]; Z["fortschritt"] = {"art": art, "prozent": round(prozent, 1), "text": text}
    if not alt or alt["art"] != art or int(alt["prozent"] // 25) != int(prozent // 25):
        with open(LOG, "a", encoding="utf-8") as f: f.write(f"{datetime.datetime.now():%H:%M:%S}       {art}: {prozent:.0f} %  {text}\n")


for _m in BRETTER.values(): _m.print = melde; _m.input = frage; _m.FRAGEN = True; _m.fortschritt = fortschritt


def installieren(nummer, brett):
    KK = BRETTER[brett]
    with SPERRE: Z.update(laeuft=True, nummer=nummer, brett=brett, ergebnis=None, beginn=time.time(), fortschritt=None); Z["zeilen"].clear()
    try: open(BRETT_DATEI, "w", encoding="utf-8").write(brett)   # Thonny_starten.bat liest die Wahl
    except OSError: pass
    melde(f"===== Installation {'ESP32-CAM' if brett == 'cam' else 'ESP32-Brett'} „{nummer}“ beginnt {datetime.datetime.now():%d.%m.%Y %H:%M:%S} =====")
    try:
        (KK.eine_kamera if brett == "cam" else KK.ein_brett)(nummer); erg = "FERTIG"
    except KK.Abbruch as e:
        erg = "ABGEBROCHEN: " + str(e)
    except Exception as e:
        erg = f"FEHLER: {type(e).__name__}: {e}"; melde("  >>> " + erg)
    melde(f"===== Ergebnis ESP32-Brett Nr. {nummer}: {erg} =====")
    with SPERRE: Z.update(laeuft=False, ergebnis=erg)


def dateiliste(brett):
    KK = BRETTER[brett]; aus = []
    for q, ziel in KK.DATEIEN:
        p = os.path.join(KK.PROGRAMME, q); t = open(p, encoding="utf-8").read()
        m = re.search(r"Fassung:?\s+(\d+\.\d+)", t[:3000])
        aus.append({"ziel": ziel, "quelle": q, "fassung": m.group(1) if m else "–", "byte": os.path.getsize(p), "zweck": ZWECK[brett].get(ziel, "")})
    j = "kamera.json" if brett == "cam" else "esp.json"; aus.append({"ziel": j, "quelle": "(wird erzeugt)", "fassung": "–", "byte": 0, "zweck": ZWECK[brett][j]})
    return aus


SEITE = """<!doctype html><html lang="de"><head><meta charset="utf-8"><title>ESP32 installieren</title>
<style>
body{font-family:Segoe UI,Arial,sans-serif;background:#fff;color:#000;margin:0;padding:16px 24px;max-width:1200px}
h1{font-size:22px;margin:0 0 2px}.unter{color:#444;margin-bottom:14px}
.reihe{display:flex;gap:24px;flex-wrap:wrap}.spalte{flex:1 1 480px;min-width:320px}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid #ccc;padding:5px 6px;text-align:left;vertical-align:top}
th{background:#f2f2f2}a{color:#00e}button{font-size:16px;padding:8px 18px;border:1px solid #000;background:#fff;cursor:pointer;border-radius:4px}
button.haupt{background:#000;color:#fff}button:disabled{opacity:.4;cursor:default}
input{font-size:16px;width:70px;padding:6px}#log{background:#fafafa;border:1px solid #bbb;height:430px;overflow:auto;font:13px Consolas,monospace;white-space:pre;padding:8px}
#frage{border:2px solid #000;padding:10px;margin:10px 0;display:none;background:#fffbe6}#ergebnis{font-weight:bold;margin:8px 0;min-height:1.3em}
#fbox{margin:6px 0 10px}#ftext{font-size:14px;margin-bottom:3px;min-height:1.2em}#fbalken{border:1px solid #000;height:18px;background:#fff}#fwert{height:100%;width:0;background:#000;transition:width .3s}
.ok{color:#060}.schlecht{color:#a00}#ansicht{white-space:pre;font:12px Consolas,monospace;border:1px solid #bbb;max-height:300px;overflow:auto;padding:6px;display:none}
</style></head><body>
<h1>Mein ESP32 installieren</h1><div class="unter">VHS-Kurs „ESP32-CAM und ESP32 mit MicroPython“ &middot; Prof. Dr.-Ing. Ralph Wystup M.Sc. &middot; erstellt mit KI und Agent (Claude Code, Anthropic) &middot; Installationsseite 1.0</div>
<p style="font-size:16px"><b>Welches Brett?</b> <label><input type="radio" name="brett" value="esp" id="b_esp"> ESP32-Brett (WROOM-32, 30 Stifte, blaue LED)</label> &nbsp; <label><input type="radio" name="brett" value="cam" id="b_cam"> ESP32-CAM (Kamera auf dem USB-Brett)</label></p>
<div class="reihe"><div class="spalte">
<h3>Das kommt auf das Brett</h3><table id="dateien"><tr><th>Datei auf dem Brett</th><th>Fassung</th><th>Zweck</th><th>Byte</th></tr></table>
<p id="fwtext">Dazu, falls das Brett werksfrisch ist: die passende MicroPython-Firmware 1.27 (ESP32-Brett: ESP32_GENERIC von micropython.org; ESP32-CAM: mit Kameratreiber). Ein vorhandenes <b>main.py</b> wird entfernt – gestartet wird in Thonny.</p>
<div id="ansicht"></div>
<h3>Angeschlossen</h3><div id="ports">…</div>
</div><div class="spalte">
<h3>Installieren</h3>
<p>Nur <b>ein</b> ESP32-Brett per USB anstecken. Thonny muss geschlossen sein.</p>
<p>Mein Name (für das WLAN, Buchstaben und Ziffern): <input id="nummer" type="text" maxlength="16" value="" placeholder="z. B. Anna" style="width:130px"> &rarr; WLAN <b id="wlan">VHS-ESP-…</b>
&nbsp; <button class="haupt" id="los">Brett installieren</button></p>
<div id="auto" style="border:2px solid #000;padding:8px 10px;margin:6px 0;background:#eef7ee;min-height:1.4em"></div>
<div id="frage"><div id="fragetext"></div><p><button onclick="antworte('')">Erledigt, weiter</button>
<span id="janein"><button onclick="antworte('j')">Ja</button> <button onclick="antworte('n')">Nein</button></span></p></div>
<div id="ergebnis"></div>
<div id="fbox"><div id="ftext">&nbsp;</div><div id="fbalken"><div id="fwert"></div></div></div>
<div id="log"></div>
</div></div>
<script>
const $=id=>document.getElementById(id);
const saeubern=v=>v.replace(/ä/g,'ae').replace(/ö/g,'oe').replace(/ü/g,'ue').replace(/Ä/g,'Ae').replace(/Ö/g,'Oe').replace(/Ü/g,'Ue').replace(/ß/g,'ss').replace(/ /g,'-').replace(/[^A-Za-z0-9-]/g,'').slice(0,16);
const praefix=()=>brett()==='cam'?'VHS-CAM-':'VHS-ESP-';
$('nummer').oninput=()=>$('wlan').textContent=praefix()+(saeubern($('nummer').value)||'…');
for(const id of ['b_esp','b_cam'])$(id).onchange=()=>{$('wlan').textContent=praefix()+(saeubern($('nummer').value)||'…');liste();autoRest=0;};
function brett(){return $('b_cam').checked?'cam':'esp';}
async function liste(){const d=await (await fetch('/dateien?brett='+brett())).json();while($('dateien').rows.length>1)$('dateien').deleteRow(1);for(const f of d){const r=$('dateien').insertRow();
 r.innerHTML=`<td>${f.quelle.startsWith('(')?f.ziel:`<a href="#" onclick="zeige('${f.quelle}');return false">${f.ziel}</a>`}</td><td>${f.fassung}</td><td>${f.zweck}</td><td>${f.byte||''}</td>`;}}
async function zeige(q){const t=await (await fetch('/datei?name='+encodeURIComponent(q))).text();$('ansicht').style.display='block';$('ansicht').textContent=t;}
async function ports(){const d=await (await fetch('/ports')).json();$('ports').innerHTML=d.length?d.map(p=>`${p.port} – ${p.text}${p.kamera?' <b>(ESP32)</b>':''}`).join('<br>'):'kein ESP32-Brett gefunden';}
$('los').onclick=async()=>{gestartet=true;$('auto').textContent='';const n=saeubern($('nummer').value);if(!n){$('ergebnis').textContent='Bitte zuerst den Namen eintragen.';$('ergebnis').className='schlecht';return;}await fetch('/start',{method:'POST',body:JSON.stringify({nummer:n,brett:brett()})});};
async function antworte(t){await fetch('/antwort',{method:'POST',body:JSON.stringify({text:t})});}
async function zustand(){try{const z=await (await fetch('/zustand')).json();
 const log=$('log'),unten=log.scrollTop+log.clientHeight>=log.scrollHeight-5;log.textContent=z.zeilen.join('\\n');if(unten)log.scrollTop=log.scrollHeight;
 $('los').disabled=z.laeuft;$('frage').style.display=z.frage?'block':'none';$('fragetext').textContent=z.frage||'';$('janein').style.display=(z.frage||'').includes('(j/n)')?'inline':'none';
 $('ergebnis').textContent=z.laeuft?('läuft … Brett '+z.nummer):(z.ergebnis?(z.ergebnis.startsWith('FERTIG')?z.ergebnis+' – Brett abziehen, dieses Fenster und das schwarze Fenster schließen. Danach: Thonny_starten.bat.':z.ergebnis):'');$('ergebnis').className=z.ergebnis&&z.ergebnis.startsWith('FERTIG')?'ok':(z.ergebnis?'schlecht':'');

 const f=z.fortschritt;$('ftext').textContent=f?`${f.art}: ${f.prozent.toFixed(0)} %  ${f.text}`:'\u00a0';$('fwert').style.width=(f?f.prozent:0)+'%';
}catch(e){$('ergebnis').textContent='Installationsprogramm antwortet nicht (Fenster geschlossen?)';}}
async function naechste(){const d=await (await fetch('/naechste')).json();}
let auto=null,autoRest=0,gestartet=false;
async function vorbelegen(){const d=await (await fetch('/naechste')).json();$(d.brett==='cam'?'b_cam':'b_esp').checked=true;if(d.name&&!$('nummer').value){$('nummer').value=d.name;}$('wlan').textContent=praefix()+(saeubern($('nummer').value)||'…');liste();}
async function selbststart(){if(gestartet)return;const d=await (await fetch('/ports')).json();const b=d.filter(p=>p.kamera);const n=saeubern($('nummer').value);if(b.length!==1||!n){$('auto').textContent=b.length===0?'Warte auf ein Brett am USB … (die Installation startet dann von selbst)':b.length>1?'Mehrere Bretter angeschlossen – bitte nur eines anstecken.':'Bitte den Namen eintragen.';autoRest=0;return;}
 if(autoRest===0)autoRest=10;autoRest--; $('auto').innerHTML=`Brett an ${b[0].port} gefunden – Installation startet in <b>${autoRest+1} s</b> von selbst (${brett()==='cam'?'ESP32-CAM':'ESP32-Brett'}, WLAN ${praefix()}${n}) – falsches Brett? Oben umschalten. <button onclick="abbrechen()">Abbrechen</button>`; if(autoRest<=0){gestartet=true;$('auto').textContent='';$('los').click();}}
function abbrechen(){gestartet=true;$('auto').textContent='Selbststart abgebrochen – „Brett installieren“ drücken, wenn es losgehen soll.';}
$('nummer').addEventListener('input',()=>{autoRest=0;});
ports();vorbelegen().then(()=>{auto=setInterval(selbststart,1000);});setInterval(zustand,700);setInterval(ports,3000);
</script></body></html>"""


class Seite(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _aus(self, code, inhalt, art="application/json; charset=utf-8"):
        b = inhalt.encode("utf-8") if isinstance(inhalt, str) else inhalt
        self.send_response(code); self.send_header("Content-Type", art); self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        pfad = self.path.split("?")[0]
        if pfad == "/": return self._aus(200, SEITE, "text/html; charset=utf-8")
        if pfad == "/zustand":
            with SPERRE: return self._aus(200, json.dumps(dict(Z, zeilen=list(Z["zeilen"])), ensure_ascii=False))
        if pfad == "/dateien": return self._aus(200, json.dumps(dateiliste("cam" if "brett=cam" in self.path else "esp"), ensure_ascii=False))
        if pfad == "/naechste": return self._aus(200, json.dumps({"name": KK_ESP.kennung_saeubern(os.environ.get("USERNAME") or os.environ.get("USER") or ""), "brett": brett_lesen()}))   # 1.2: Vorbelegung = Windows-Benutzer
        if pfad == "/ports":
            return self._aus(200, json.dumps([{"port": p.device, "text": p.description, "kamera": any(v in (p.hwid or "").upper() for v in ("1A86", "10C4"))}
                                              for p in KK_ESP.list_ports.comports()], ensure_ascii=False))
        if pfad == "/datei":
            name = os.path.basename(self.path.split("name=", 1)[-1].split("&")[0].replace("%20", " "))
            for m in BRETTER.values():
                if name in [q for q, _ in m.DATEIEN]: return self._aus(200, open(os.path.join(m.PROGRAMME, name), encoding="utf-8").read(), "text/plain; charset=utf-8")
            return self._aus(404, "unbekannt", "text/plain; charset=utf-8")
        if pfad == "/log": return self._aus(200, open(LOG, encoding="utf-8").read() if os.path.isfile(LOG) else "", "text/plain; charset=utf-8")
        self._aus(404, "{}")

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0); d = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/start":
            with SPERRE: belegt = Z["laeuft"]
            if belegt: return self._aus(409, json.dumps({"fehler": "läuft schon"}))
            threading.Thread(target=installieren, args=(KK_ESP.kennung_saeubern(d.get("nummer") or "1"), "cam" if d.get("brett") == "cam" else "esp"), daemon=True).start(); return self._aus(200, "{}")
        if self.path == "/antwort":
            ANTWORT_TEXT[0] = str(d.get("text", "")); ANTWORT.set(); return self._aus(200, "{}")
        self._aus(404, "{}")


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Seite)
    print("=" * 64 + f"\n VHS-Kurs ESP32-CAM und ESP32  ·  Installationsseite 1.0\n Prof. Dr.-Ing. Ralph Wystup M.Sc.\n" + "=" * 64)
    print(f" Seite: http://127.0.0.1:{PORT}/      Protokoll: {LOG}\n Dieses Fenster offen lassen; schließen beendet die Installationsseite.", flush=True)
    threading.Timer(1.0, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}/")).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass

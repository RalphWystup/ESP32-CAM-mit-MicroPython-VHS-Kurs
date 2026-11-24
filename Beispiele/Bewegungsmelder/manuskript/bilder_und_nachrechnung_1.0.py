"""bilder_und_nachrechnung_1.0.py -- Bilder und Zahlen für Manuskript_Bewegungsmelder_1.0 (20.11.2026).
Die Rechenregeln sind WÖRTLICH aus esp_cam_bewegung_1.4.py übernommen (vergleich, nachfuehren, INDEX), damit jede Zahl im
Manuskript mit dem Programm nachgerechnet ist."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
B, H, SCHRITT = 160, 120, 4
INDEX = [y * B + x for y in range(SCHRITT // 2, H, SCHRITT) for x in range(SCHRITT // 2, B, SCHRITT)]
def vergleich(neu, hinter, S):
    n = len(neu); versatz = (sum(neu) - sum(hinter)) // n; z = 0
    for i in range(n):
        d = neu[i] - hinter[i] - versatz
        if d > S or d < -S: z += 1
    return z / n
def nachfuehren(neu, hinter):
    for i in range(len(neu)): hinter[i] = (3 * hinter[i] + neu[i]) >> 2
print("Messpunkte:", len(INDEX), "| Spalten x:", list(range(2, B, 4))[:3], "... | Zeilen y:", list(range(2, H, 4))[:3], "...")
print("Anteil 2 %: Auslösung erst bei z/1200 > 0.02 -> z >=", min(z for z in range(1201) if z / 1200 > 0.02))
# --- Bild 1: Messraster über dem Foto 640 x 480
fig, ax = plt.subplots(figsize=(6.4, 4.8 * 0.92))
px = [((k % B) * 4 + 2, (k // B) * 4 + 2) for k in INDEX]
ax.scatter([p[0] for p in px], [p[1] for p in px], s=4, c="#1f4e9c")
ox, oy, ow, oh = 300, 180, 80, 80
inn = sum(1 for (x, y) in px if ox <= x < ox + ow and oy <= y < oy + oh)
ax.add_patch(Rectangle((ox, oy), ow, oh, fill=False, ec="#c0392b", lw=1.6))
ax.text(ox + ow + 6, oy + oh / 2, "Gegenstand 80 × 80 Bildpunkte\ntrifft %d Messpunkte = %.1f %%" % (inn, inn / 12), color="#c0392b", va="center", bbox=dict(fc="white", ec="none", pad=2))
ax.set_xlim(0, 640); ax.set_ylim(480, 0); ax.set_aspect("equal")
ax.set_xlabel("x im Foto [Bildpunkte]"); ax.set_ylabel("y im Foto [Bildpunkte]")
ax.set_title("1200 Messpunkte (40 × 30), Abstand 16 Bildpunkte des Fotos 640 × 480")
fig.tight_layout(); fig.savefig("bild1_messraster.png", dpi=200); plt.close(fig)
print("Gegenstand 80x80 an (300,180): Messpunkte", inn)
# --- Bild 2: Hintergrund folgt -- Sprung und Rampe, mit dem echten Rechenweg
def lauf(signal, S=25, n_hint=1200):
    """ein Messpunkt ändert sich nach 'signal', die übrigen bleiben 100; gibt Abweichung d des Punkts je Bild"""
    hinter = None; lernen = 8; ds = []
    for v in signal:
        p = bytearray([100] * n_hint); p[0] = v
        if hinter is None: hinter = bytearray(p); ds.append(0); continue
        if lernen > 0: nachfuehren(p, hinter); lernen -= 1; ds.append(0); continue
        versatz = (sum(p) - sum(hinter)) // len(p); ds.append(p[0] - hinter[0] - versatz); nachfuehren(p, hinter)
    return ds
N = 32; T = 0.32
rampe = [min(255, 100 + int(5 * max(0, k - 12))) for k in range(N)]          # 5 Graustufen je Prüfbild
rampe7 = [min(255, 100 + int(7 * max(0, k - 12))) for k in range(N)]
d5, d7 = lauf(rampe), lauf(rampe7)
print("Rampe 5/Bild: größte Abweichung", max(d5), "| Rampe 7/Bild:", max(d7), "(Theorie Dauerabweichung 4*delta = 20 bzw. 28)")
fig, ax = plt.subplots(figsize=(6.4, 2.8))
t = [k * T for k in range(N)]
ax.plot(t, d5, "-o", ms=3, c="#1f4e9c", lw=2, label="langsam: +5 Graustufen je Prüfbild")
ax.plot(t, d7, "-s", ms=3, c="#b9770e", lw=2, label="schneller: +7 Graustufen je Prüfbild")
ax.axhline(25, c="#c0392b", lw=1.2, ls="--"); ax.text(0.1, 26.5, "Schwelle 25", color="#c0392b")
ax.axvspan(0, 9 * T, color="#dddddd", lw=0); ax.text(0.1, 2, "Einlernen\n(1 + 8 Bilder)", fontsize=8)
ax.set_xlabel("Zeit [s] (ein Prüfbild ≈ 0,32 s)"); ax.set_ylabel("Abweichung d [Graustufen]")
ax.set_title("Ein Messpunkt wird gleichmäßig heller")
ax.legend(loc="upper left", bbox_to_anchor=(0.36, 1.0), frameon=False); ax.set_ylim(0, 45)
fig.tight_layout(); fig.savefig("bild2_hintergrund.png", dpi=200); plt.close(fig)
# --- Versatz-Beispiel: Gegenstand mit Kontrast c deckt Anteil f
for f, c in ((0.1, 100), (0.5, 60)):
    n = 1200; k = int(f * n); hinter = bytearray([100] * n); neu = bytearray([100 + c] * k + [100] * (n - k))
    print("Versatzbeispiel f=%.1f c=%d: Versatz %d, Anteil %.3f" % (f, c, (sum(neu) - sum(hinter)) // n, vergleich(neu, hinter, 25)))
# --- Bild 3: Ablauf
fig, ax = plt.subplots(figsize=(6.6, 7.4)); ax.set_xlim(0, 10); ax.set_ylim(0, 13.4); ax.axis("off")
def kasten(x, y, w, h, text, farbe="#eef3fb"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05,rounding_size=0.15", fc=farbe, ec="#333333", lw=1))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.3)
def pfeil(x1, y1, x2, y2, text=""):
    ax.annotate("", (x2, y2), (x1, y1), arrowprops=dict(arrowstyle="->", lw=1.2, color="#333333"))
    if text: ax.text((x1 + x2) / 2 + 0.12, (y1 + y2) / 2, text, fontsize=7.5, va="center", color="#333333")
ax.text(2.6, 13.1, "KAMERA (ESP32-CAM, main.py)", ha="center", weight="bold"); ax.text(8.1, 13.1, "BROWSER (anzeige.html)", ha="center", weight="bold")
kasten(0.3, 11.7, 4.6, 1.0, "Bildsensor OV2640: Foto JPEG 640 × 480\n(fest, nie umgeschaltet), ≈ 14,5 kB, ≈ 130 ms")
kasten(0.3, 10.1, 4.6, 1.0, "Modul jpeg: verkleinert entpacken 160 × 120,\nnur Helligkeit Y, ≈ 180 ms")
kasten(0.3, 8.5, 4.6, 1.0, "1200 Messpunkte (jeder 4. Punkt, 40 × 30)")
kasten(0.3, 6.5, 4.6, 1.4, "Vergleich mit Hintergrund h:\nd = p − h − Versatz,  zählen |d| > S\nAnteil a = Zahl / 1200")
kasten(0.2, 4.6, 4.8, 1.35, "a > A  und  ≥ Ruhe seit letztem Bild?\nnein: Hintergrund nachführen h ← (3h + p)/4,\ndann nächstes Prüfbild (≈ 0,32 s je Runde)", "#fff7e6")
kasten(0.3, 2.9, 4.6, 1.2, "ja: dieses Foto = Bewegungsbild Nr. N\n(nur im Arbeitsspeicher, ersetzt das vorige)\nHintergrund neu lernen", "#e8f6ec")
kasten(0.3, 0.6, 4.6, 1.4, "LED GPIO 4 blitzt (Blitz-Dauer),\ndanach Hintergrund neu lernen\n(eigener Blitz ≠ Bewegung)", "#fdecea")
for y1, y2 in ((11.7, 11.1), (10.1, 9.5), (8.5, 7.9), (6.5, 5.9), (4.7, 4.1)): pfeil(2.6, y1, 2.6, y2)
kasten(5.6, 9.8, 4.2, 1.6, "alle 0,7 s:  GET /ereignis\n→ {nr, alter_ms, byte, anteil}\nFrist 4 s")
kasten(5.6, 6.9, 4.2, 2.0, "neue Nummer N?\nGET /letztes.jpg (Frist 20 s)\nKamera sendet in 4-kB-Stücken,\nWächter pausiert solange")
kasten(5.6, 4.3, 4.2, 1.8, "Bild groß zeigen, in die Galerie\n(höchstens 40 im Browser),\nwahlweise in Ordner speichern")
kasten(5.6, 2.2, 4.2, 1.3, "GET /gesehen?nr=N\n„Bild N ist angekommen“")
pfeil(5.6, 10.0, 4.95, 3.5); ax.text(5.0, 6.3, "fragt nach\nNummer und\nholt das Bild", fontsize=7.5, color="#333333", bbox=dict(fc="white", ec="none", pad=1)); pfeil(7.7, 9.8, 7.7, 8.9); pfeil(7.7, 6.9, 7.7, 6.1); pfeil(7.7, 4.3, 7.7, 3.5)
pfeil(5.6, 2.6, 4.95, 1.4); ax.text(5.05, 2.05, "Kamera blitzt\nnur einmal je Nummer", fontsize=7.5, color="#333333", bbox=dict(fc="white", ec="none", pad=1))
ax.text(7.7, 0.55, "3 Fehlversuche hintereinander:\n„Verbindung unterbrochen –\nverbinde automatisch neu“;\nfragt weiter, holt Verpasstes nach", ha="center", fontsize=7.5, color="#555555")
fig.tight_layout(); fig.savefig("bild3_ablauf.png", dpi=200); plt.close(fig)
print("Bilder geschrieben")
# --- Nachtrag: Quadrate an allen Lagen zum Raster (Beispiel A)
P = [((k % B) * 4 + 2, (k // B) * 4 + 2) for k in INDEX]
for L in (64, 72, 80, 96):
    zs = {sum(1 for (x, y) in P if ox <= x < ox + L and oy <= y < oy + L) for ox in range(100, 132) for oy in range(100, 132)}
    print("Quadrat %d x %d Bildpunkte, alle Lagen: getroffene Messpunkte %s" % (L, L, sorted(zs)))

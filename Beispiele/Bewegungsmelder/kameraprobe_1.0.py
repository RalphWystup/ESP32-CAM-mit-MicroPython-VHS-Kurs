# ==========================================================================================================
#  VHS-Kurs  „ESP32-CAM mit MicroPython“ -- Kameraprobe (kameraprobe_1.0.py)
#  Autor: Prof. Dr.-Ing. Ralph Wystup M.Sc. · Mitarbeit: Claude (Anthropic, Claude Code) · Fassung 1.0 vom 20.11.2026
#  In Thonny öffnen, F5. Prüft, ob die Kamera alles kann, was der Bewegungsmelder 1.2 braucht:
#    Modul jpeg vorhanden, Kamera fest auf Foto 640 × 480 (JPEG), jedes Foto klein entpacken (160 × 120) für die Erkennung.
#  10 Zeilen „BILD“: Fotogröße, Dauer Aufnahme / Entpacken, mittlere Helligkeit, freier Speicher. Am Ende blitzt die LED.
#  Erwartet (echte Kamera 20.11.2026): Foto 12–15 kB, Aufnahme etwa 130 ms, Entpacken etwa 180 ms, frei etwa 3900 kB,
#  Helligkeit ändert sich, wenn man die Hand vor die Kamera hält. Speichert nichts.
# ==========================================================================================================
import gc, time
from machine import Pin
try:
    import jpeg
except ImportError:
    print("Das Modul jpeg fehlt -- bitte die Kamera-Firmware von cnadler86 (micropython-camera-API) aufspielen.")
    raise SystemExit
from camera import Camera, PixelFormat, FrameSize

INDEX = [y * 160 + x for y in range(2, 120, 4) for x in range(2, 160, 4)]   # 1200 Messpunkte wie im Bewegungsmelder
cam = None
try:
    cam = Camera(pixel_format=PixelFormat.JPEG, frame_size=FrameSize.VGA, jpeg_quality=85, fb_count=2)
    dec = jpeg.Decoder(pixel_format="CbYCrY", scale_width=160, scale_height=120, return_bytes=True)
    print("Kamera an: Foto 640 x 480 (JPEG), frei", gc.mem_free() // 1024, "kB")
    for i in range(10):
        t0 = time.ticks_ms(); f = cam.capture(); b = bytes(f); cam.free_buffer(); t1 = time.ticks_ms()
        px = dec.decode(b); p = bytearray(px[2 * k + 1] for k in INDEX); t2 = time.ticks_ms()
        print("BILD %d  Foto %d kB  Aufnahme %d ms  Entpacken %d ms  Helligkeit %d  frei %d kB"
              % (i, len(b) // 1024, t1 - t0, t2 - t1, sum(p) // len(p), gc.mem_free() // 1024))
        b = px = p = None; gc.collect(); time.sleep_ms(300)
except Exception as e:
    print("FEHLER:", e, "-- USB-Kabel 5 s abziehen, wieder anstecken, noch einmal F5")
finally:
    try:
        cam.deinit()
    except Exception:
        pass
led = Pin(4, Pin.OUT); led.value(1); time.sleep_ms(120); led.value(0)
print("Kameraprobe fertig.")

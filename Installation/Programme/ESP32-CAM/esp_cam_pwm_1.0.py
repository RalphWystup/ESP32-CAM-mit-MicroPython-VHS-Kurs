# ==========================================================================================================
#  VHS-Kurs  „ESP32-CAM mit MicroPython“
#  Beispiel 2: Pulsweitenmodulation (PWM)  (pwm.py)
# ----------------------------------------------------------------------------------------------------------
#  Autor:      Prof. Dr.-Ing. Ralph Wystup M.Sc.
#  Mitarbeit:  Claude (Anthropic, Claude Code)
#  Fassung:    1.0 vom 17.11.2026
# ----------------------------------------------------------------------------------------------------------
#  Die Blitz-LED vorne (GPIO 4) wird per PWM langsam heller und wieder dunkler („atmen“).
#  PWM schaltet die LED sehr schnell (hier 1000-mal pro Sekunde) ein und aus; das Verhältnis von Ein- zu
#  Ausschaltzeit (Tastgrad, duty) bestimmt die mittlere Helligkeit. duty_u16: 0 = aus … 65535 = ganz an.
#  Damit es nicht blendet, geht die Helligkeit nur bis HOECHST (etwa 3 %).
#  In Thonny: Datei öffnen, grüner Start-Knopf; „Stop“ beendet das Programm (die LED geht dann aus).
#  Zum Ausprobieren: FREQUENZ auf 2 Hz stellen – dann sieht man das Ein- und Ausschalten.
# ==========================================================================================================
from machine import Pin, PWM
import time

FREQUENZ = 1000                      # Hz
HOECHST = 2000                       # von 65535 -- etwa 3 %, die Blitz-LED ist sehr hell
SCHRITTE = 50
PAUSE = 0.02                         # Sekunden je Schritt

led = PWM(Pin(4), freq=FREQUENZ, duty_u16=0)
print("PWM an GPIO 4 mit", FREQUENZ, "Hz -- Stop in Thonny beendet.")
try:
    while True:
        for i in list(range(SCHRITTE + 1)) + list(range(SCHRITTE, -1, -1)):
            d = HOECHST * i * i // (SCHRITTE * SCHRITTE)      # quadratisch: wirkt für das Auge gleichmäßiger
            led.duty_u16(d)
            time.sleep(PAUSE)
        print("Tastgrad zuletzt", d, "von 65535")
finally:
    led.duty_u16(0)
    led.deinit()

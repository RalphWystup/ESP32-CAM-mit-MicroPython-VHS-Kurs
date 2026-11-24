# ==========================================================================================================
#  VHS-Kurs  „ESP32-CAM mit MicroPython“
#  Beispiel 1: LED blinkt  (blink.py)
# ----------------------------------------------------------------------------------------------------------
#  Autor:      Prof. Dr.-Ing. Ralph Wystup M.Sc.
#  Mitarbeit:  Claude (Anthropic, Claude Code)
#  Fassung:    1.2 vom 17.11.2026 – nach seinem led_blickt.py, angepasst an die ESP32-CAM
# ----------------------------------------------------------------------------------------------------------
#  Die ESP32-CAM hat an GPIO 2 keine LED (das war beim ESP32-DevKit so). Hier blinkt die weiße Blitz-LED vorne
#  (GPIO 4): 1 = an, 0 = aus. ACHTUNG: sehr hell -- nicht direkt hineinsehen.
#  (1.2: die rote LED auf der Rückseite hängt bei diesen Brettern fest an VCC und lässt sich nicht schalten.)
#  Wer eine eigene LED anschließen will: IO2 am Stiftleistenrand, LED mit 220-Ω-Vorwiderstand nach GND,
#  dann LED_PIN = 2 und LOW_AKTIV = False.
#  In Thonny: Datei öffnen, grüner Start-Knopf; „Stop“ beendet das Programm.
# ==========================================================================================================
from machine import Pin
import time

LED_PIN = 4            # weiße Blitz-LED vorne
LOW_AKTIV = False      # Blitz-LED: leuchtet bei 1
PAUSE = 1.5            # Sekunden an und aus

led = Pin(LED_PIN, Pin.OUT)


def led_setzen(an):
    led.value((0 if an else 1) if LOW_AKTIV else (1 if an else 0))


print("LED an GPIO", LED_PIN, "blinkt alle", PAUSE, "s -- Stop in Thonny beendet.")
try:
    while True:
        led_setzen(True)       # LED an
        time.sleep(PAUSE)      # 1,5 s warten
        led_setzen(False)      # LED aus
        time.sleep(PAUSE)      # 1,5 s warten
finally:
    led_setzen(False)

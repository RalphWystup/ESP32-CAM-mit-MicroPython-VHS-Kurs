# ==========================================================================================================
#  VHS-Kurs  „ESP32 mit MicroPython“
#  Beispiel 1: LED blinkt  (blink.py)
# ----------------------------------------------------------------------------------------------------------
#  Autor:      Prof. Dr.-Ing. Ralph Wystup M.Sc.
#  Mitarbeit:  Claude (Anthropic, Claude Code)
#  Fassung:    1.0 vom 24.11.2026 – nach seinem led_blickt.py, für das ESP32-WROOM-32-Brett (30 Stifte)
# ----------------------------------------------------------------------------------------------------------
#  Auf dem ESP32-Brett sitzt eine blaue LED an GPIO 2 (Beschriftung D2): 1 = an, 0 = aus.
#  Wer eine eigene LED anschließen will: GPIO 2 (oder einen anderen freien Stift), LED mit 220-Ω-Vorwiderstand
#  nach GND, dann LED_PIN anpassen.
#  In Thonny: Datei öffnen, grüner Start-Knopf; „Stop“ beendet das Programm.
# ==========================================================================================================
from machine import Pin
import time

LED_PIN = 2            # blaue LED auf dem Brett (D2)
LOW_AKTIV = False      # diese LED leuchtet bei 1
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

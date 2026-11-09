# Hardware test for the Simon game wiring (MicroPython).
# 1. Each LED turns on once, in order, with its tone.
# 2. All LEDs turn on. Each button press turns off the LED of that button.

from machine import Pin, PWM
from time import sleep_ms

NAMES = ("green", "red", "yellow", "blue")
LED_GPIOS = (18, 17, 9, 8)  # A0, A1, A2, A3
BUTTON_GPIOS = (35, 37, 36, 16)  # MOSI, MISO, SCK, RX
TONES = (415, 310, 252, 209)  # Hz
BUZZER_GPIO = 7  # SDA

leds = [Pin(gpio, Pin.OUT, value=0) for gpio in LED_GPIOS]
buttons = [Pin(gpio, Pin.IN, Pin.PULL_UP) for gpio in BUTTON_GPIOS]
buzzer = PWM(Pin(BUZZER_GPIO), freq=440, duty_u16=0)

try:
    print("Step 1: each LED in order")
    for i in range(4):
        print("  LED", NAMES[i], "on GPIO", LED_GPIOS[i])
        leds[i].value(1)
        buzzer.freq(TONES[i])
        buzzer.duty_u16(32768)
        sleep_ms(700)
        buzzer.duty_u16(0)
        leds[i].value(0)
        sleep_ms(300)

    print("Step 2: press each button to turn off its LED")
    for i in range(4):
        if buttons[i].value() == 0:
            print("  WARNING: button", NAMES[i], "reads pressed before any press")
    for led in leds:
        led.value(1)

    while any(led.value() for led in leds):
        for i in range(4):
            if buttons[i].value() == 0 and leds[i].value() == 1:
                leds[i].value(0)
                print("  button", NAMES[i], "on GPIO", BUTTON_GPIOS[i], "pressed")
        sleep_ms(20)

    print("Test complete: all 4 buttons work")
finally:
    buzzer.duty_u16(0)
    for led in leds:
        led.value(0)

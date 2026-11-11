# Hardware for the games: 4 LEDs, 4 buttons, 1 piezo buzzer.
# Board: Adafruit QT Py ESP32-S3 (MicroPython).

from machine import Pin, PWM
from time import sleep_ms, ticks_ms, ticks_diff

# Colour index. Each tuple below uses this order.
GREEN, RED, YELLOW, BLUE = 0, 1, 2, 3
NAMES = ("green", "red", "yellow", "blue")

LED_GPIOS = (17, 8, 18, 9)  # header pins A1, A3, A0, A2
BUTTON_GPIOS = (35, 16, 37, 36)  # header pins MOSI, RX, MISO, SCK
BUZZER_GPIO = 7  # header pin SDA
TONES = (415, 310, 252, 209)  # Hz

BEEP_TONE = 880  # Hz
DEBOUNCE_MS = 30
# LED for each bit of a binary number, from the lowest bit.
BINARY_BIT_LEDS = (RED, BLUE, GREEN, YELLOW)
BINARY_SHOW_MS = 5000

leds = [Pin(gpio, Pin.OUT, value=0) for gpio in LED_GPIOS]
# Each button connects its pin to GND. The internal pull-up holds the pin high.
buttons = [Pin(gpio, Pin.IN, Pin.PULL_UP) for gpio in BUTTON_GPIOS]
buzzer = PWM(Pin(BUZZER_GPIO), freq=440, duty_u16=0)

sound_on = True


def toggle_sound():
    """Change the sound setting. Return the new setting."""
    global sound_on
    sound_on = not sound_on
    return sound_on


def tone_on(frequency):
    if sound_on:
        buzzer.freq(frequency)
        buzzer.duty_u16(32768)  # 50% square wave


def tone_off():
    buzzer.duty_u16(0)


def beep(ms=200):
    tone_on(BEEP_TONE)
    sleep_ms(ms)
    tone_off()


def set_leds(on):
    """Turn on the LEDs whose index is in `on`. Turn off the others."""
    for index, led in enumerate(leds):
        led.value(1 if index in on else 0)


def set_all_leds(value):
    for led in leds:
        led.value(value)


def all_off():
    tone_off()
    set_all_leds(0)


def play(index, on_ms):
    """Turn on one LED and its tone for on_ms milliseconds."""
    leds[index].value(1)
    tone_on(TONES[index])
    sleep_ms(on_ms)
    tone_off()
    leds[index].value(0)


def pressed_button():
    """Return the index of a button that is pressed now, or None."""
    for index, button in enumerate(buttons):
        if button.value() == 1:
            continue  # high = not pressed
        sleep_ms(DEBOUNCE_MS)
        if button.value() == 0:
            return index
        # The pin went high again: contact bounce, not a press.
    return None


def wait_for_release(index):
    while buttons[index].value() == 0:
        pass
    sleep_ms(DEBOUNCE_MS)


def read_press(timeout_ms=None):
    """Wait for one button press and release. Return the button index.

    The LED and tone of the button stay on while the player holds it.
    With a timeout, return None if no press starts in that time.
    """
    start = ticks_ms()
    while timeout_ms is None or ticks_diff(ticks_ms(), start) < timeout_ms:
        index = pressed_button()
        if index is None:
            continue
        leds[index].value(1)
        tone_on(TONES[index])
        wait_for_release(index)
        tone_off()
        leds[index].value(0)
        return index
    return None


def start_signal():
    """Flash all LEDs once before a game starts."""
    set_all_leds(1)
    sleep_ms(400)
    set_all_leds(0)
    sleep_ms(800)


def show_binary(number):
    """Show a number in binary on the LEDs. A number above 15 shows as 15."""
    number = min(number, 15)
    for bit, index in enumerate(BINARY_BIT_LEDS):
        leds[index].value((number >> bit) & 1)
    sleep_ms(BINARY_SHOW_MS)
    set_all_leds(0)

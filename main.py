# Simon game for the Adafruit QT Py ESP32-S3 (MicroPython).
# The board shows a sequence on 4 LEDs. The player repeats it on 4 buttons.
# Each correct round adds one step to the sequence.
# Press any button to start a game.

import random
from machine import Pin, PWM
from time import sleep_ms, ticks_ms, ticks_us, ticks_diff, ticks_add

# Index 0-3 is green, red, yellow, blue. Each tuple uses this order.
LED_GPIOS = (18, 17, 9, 8)  # A0, A1, A2, A3
BUTTON_GPIOS = (35, 37, 36, 16)  # MOSI, MISO, SCK, RX
TONES = (415, 310, 252, 209)  # Hz
BUZZER_GPIO = 7  # SDA

LOSE_TONE = 120  # Hz
INPUT_TIMEOUT_MS = 3000  # time the player has for each press
DEBOUNCE_MS = 30

leds = [Pin(gpio, Pin.OUT, value=0) for gpio in LED_GPIOS]
# Each button connects its pin to GND. The internal pull-up holds the pin high.
buttons = [Pin(gpio, Pin.IN, Pin.PULL_UP) for gpio in BUTTON_GPIOS]
buzzer = PWM(Pin(BUZZER_GPIO), freq=440, duty_u16=0)


def tone_on(frequency):
    buzzer.freq(frequency)
    buzzer.duty_u16(32768)  # 50% square wave


def tone_off():
    buzzer.duty_u16(0)


def set_all_leds(value):
    for led in leds:
        led.value(value)


def any_pressed():
    for button in buttons:
        if button.value() == 0:
            return True
    return False


def wait_for_release():
    while any_pressed():
        pass
    sleep_ms(DEBOUNCE_MS)


def play(index, on_ms):
    """Turn on one LED and its tone for on_ms milliseconds."""
    leds[index].value(1)
    tone_on(TONES[index])
    sleep_ms(on_ms)
    tone_off()
    leds[index].value(0)


def step_times(length):
    """Return (on, off) times in ms. The sequence speeds up as it grows."""
    if length <= 5:
        return 420, 80
    if length <= 13:
        return 320, 60
    return 220, 50


def show_sequence(sequence):
    on_ms, off_ms = step_times(len(sequence))
    for index in sequence:
        play(index, on_ms)
        sleep_ms(off_ms)


def read_press():
    """Return the index of the pressed button, or None after the timeout.

    The LED and tone stay on while the player holds the button.
    """
    deadline = ticks_add(ticks_ms(), INPUT_TIMEOUT_MS)
    while ticks_diff(deadline, ticks_ms()) > 0:
        for index, button in enumerate(buttons):
            if button.value() == 1:
                continue  # high = not pressed
            sleep_ms(DEBOUNCE_MS)
            if button.value() == 1:
                continue  # contact bounce, not a press
            leds[index].value(1)
            tone_on(TONES[index])
            while button.value() == 0:
                pass
            tone_off()
            leds[index].value(0)
            sleep_ms(DEBOUNCE_MS)
            return index
    return None


def wait_for_start():
    """Turn the LEDs on in turn until the player presses a button."""
    index = 0
    while True:
        leds[index].value(1)
        end = ticks_add(ticks_ms(), 150)
        while ticks_diff(end, ticks_ms()) > 0:
            if any_pressed():
                leds[index].value(0)
                wait_for_release()
                random.seed(ticks_us())
                return
        leds[index].value(0)
        index = (index + 1) % len(leds)


def lose(expected):
    """Play the lose tone, then flash the LED that the player had to press."""
    leds[expected].value(1)
    tone_on(LOSE_TONE)
    sleep_ms(1000)
    tone_off()
    leds[expected].value(0)
    for _ in range(3):
        sleep_ms(150)
        leds[expected].value(1)
        sleep_ms(150)
        leds[expected].value(0)
    sleep_ms(1000)


def start_signal():
    set_all_leds(1)
    sleep_ms(400)
    set_all_leds(0)
    sleep_ms(800)


def play_game():
    """Play one game. Return the score (the number of completed rounds)."""
    sequence = []
    while True:
        sequence.append(random.randrange(len(leds)))
        show_sequence(sequence)
        for expected in sequence:
            if read_press() != expected:
                lose(expected)
                return len(sequence) - 1
        sleep_ms(800)


try:
    while True:
        wait_for_start()
        start_signal()
        score = play_game()
        print("Game over. Score:", score)
finally:
    # Stop the tone and LEDs when you interrupt the program (Ctrl-C or Stop).
    tone_off()
    set_all_leds(0)

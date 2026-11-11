# Simon and reverse Simon.
# The board shows a sequence. Each correct round adds one step.
#   simon:         the player repeats the sequence in the same order.
#   reverse_simon: the player enters the sequence from the last step to the first.

import random
from time import sleep_ms

import hw

LOSE_TONE = 120  # Hz
INPUT_TIMEOUT_MS = 3000  # time the player has for each press


def step_times(length):
    """Return (on, off) times in ms. The sequence speeds up as it grows."""
    if length <= 5:
        return 420, 192
    if length <= 13:
        return 320, 144
    return 220, 120


def show_sequence(sequence):
    on_ms, off_ms = step_times(len(sequence))
    for index in sequence:
        hw.play(index, on_ms)
        sleep_ms(off_ms)


def lose(expected):
    """Play the lose tone, then flash the LED that the player had to press."""
    hw.leds[expected].value(1)
    hw.tone_on(LOSE_TONE)
    sleep_ms(1000)
    hw.tone_off()
    hw.leds[expected].value(0)
    for _ in range(3):
        sleep_ms(150)
        hw.leds[expected].value(1)
        sleep_ms(150)
        hw.leds[expected].value(0)
    sleep_ms(1000)


def run(reverse=False):
    """Play one game. At the end, show the score in binary.

    The score is the number of completed rounds.
    """
    hw.start_signal()
    sequence = []
    while True:
        sequence.append(random.randrange(len(hw.leds)))
        show_sequence(sequence)
        answer = reversed(sequence) if reverse else sequence
        for expected in answer:
            if hw.read_press(INPUT_TIMEOUT_MS) != expected:
                lose(expected)
                score = len(sequence) - 1
                print("Game over. Score:", score)
                hw.show_binary(score)
                return
        sleep_ms(800)

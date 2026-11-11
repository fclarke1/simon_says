# Wordle: find a hidden code of 5 colours.
# The player enters 5 presses. The board plays the guess back with feedback
# for each element:
#   on for 1 s        correct colour in this position
#   4 flashes in 1 s  the colour is in the code, but not in this position
#   1 short flash     the colour is not in the code
# There is no limit on the number of guesses. The score is the number of guesses.

import random
from time import sleep_ms

import hw

CODE_LENGTH = 5

ABSENT, PRESENT, CORRECT = 0, 1, 2

CORRECT_MS = 1000
FLASH_COUNT = 4
FLASH_MS = 125  # on time and off time of each flash: 4 flashes take 1 s
ABSENT_MS = 150
ELEMENT_GAP_MS = 300

VICTORY_ORDER = (hw.RED, hw.GREEN, hw.BLUE, hw.YELLOW)


def score_guess(code, guess):
    """Return the feedback for each element of the guess.

    CORRECT: the colour is in the code in this position.
    PRESENT: the colour is in a different position of the code. The number of
             times that the colour occurs in the code makes no difference.
    ABSENT:  the colour is not in the code.
    """
    result = []
    for position, colour in enumerate(guess):
        if code[position] == colour:
            result.append(CORRECT)
        elif colour in code:
            result.append(PRESENT)
        else:
            result.append(ABSENT)
    return result


def show_feedback(guess, result):
    for colour, feedback in zip(guess, result):
        if feedback == CORRECT:
            hw.play(colour, CORRECT_MS)
        elif feedback == PRESENT:
            for _ in range(FLASH_COUNT):
                hw.play(colour, FLASH_MS)
                sleep_ms(FLASH_MS)
        else:
            # One short flash. The element takes the same time as a correct one.
            hw.play(colour, ABSENT_MS)
            sleep_ms(CORRECT_MS - ABSENT_MS)
        sleep_ms(ELEMENT_GAP_MS)


def victory():
    """All LEDs flash once. Then red, green, blue, yellow turn on in turn, 4 times."""
    hw.set_all_leds(1)
    sleep_ms(400)
    hw.set_all_leds(0)
    sleep_ms(400)
    for _ in range(4):
        for index in VICTORY_ORDER:
            hw.play(index, 100)
    sleep_ms(500)


def run():
    """Play one game. At the end, show the number of guesses in binary."""
    hw.start_signal()
    code = [random.randrange(len(hw.leds)) for _ in range(CODE_LENGTH)]
    guesses = 0
    while True:
        guess = [hw.read_press() for _ in range(CODE_LENGTH)]
        guesses += 1
        result = score_guess(code, guess)
        print("Guess", guesses, [hw.NAMES[colour] for colour in guess], result)
        sleep_ms(600)
        # For a correct guess, each element stays on for 1 s. This plays the
        # code back to the player.
        show_feedback(guess, result)
        if result == [CORRECT] * CODE_LENGTH:
            victory()
            print("Code found. Guesses:", guesses)
            hw.show_binary(guesses)
            return

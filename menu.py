# Start menu. The LEDs repeat the pattern of the current game.
#   Blue:   go to the next game
#   Green:  start the current game
#   Yellow: turn the sound on or off (one beep = on, no beep = off)
#   Red:    no action

import random
from time import ticks_ms, ticks_us, ticks_diff

import hw

STEP_MS = 150
PAUSE_MS = 500
ORDER = (hw.RED, hw.BLUE, hw.GREEN, hw.YELLOW)

# A pattern is a list of frames. A frame is (LEDs that are on, time in ms).
_FORWARD = [((index,), STEP_MS) for index in ORDER]
_BACKWARD = [((index,), STEP_MS) for index in reversed(ORDER)]
_PAUSE = [((), PAUSE_MS)]

CHASE = _FORWARD + _PAUSE
CHASE_BOTH_WAYS = _FORWARD + _PAUSE + _BACKWARD + _PAUSE
BLINK_ALL = [((0, 1, 2, 3), 300), ((), 300)]
FIVE_SECONDS = [
    ((hw.BLUE,), 100),
    ((), 300),
    ((hw.GREEN,), 100),
    ((), 50),
    ((hw.RED,), 100),
    ((), 100),
    ((0, 1, 2, 3), 100),
    ((), 400),
    ((hw.YELLOW,), 100),
    ((), 2000),
]


def _show_pattern(frames):
    """Repeat the pattern until a button press. Return the button index."""
    while True:
        for on, ms in frames:
            hw.set_leds(on)
            start = ticks_ms()
            while ticks_diff(ticks_ms(), start) < ms:
                index = hw.pressed_button()
                if index is not None:
                    hw.set_all_leds(0)
                    hw.wait_for_release(index)
                    return index


def choose(games, current):
    """Show the menu. Return the index of the game that the player starts.

    `games` is a sequence of (name, pattern, function).
    `current` is the index of the game that the menu shows first.
    """
    while True:
        button = _show_pattern(games[current][1])
        if button == hw.BLUE:
            current = (current + 1) % len(games)
            print("Menu:", games[current][0])
        elif button == hw.GREEN:
            # The time of the press is different each time: use it as the seed.
            random.seed(ticks_us())
            return current
        elif button == hw.YELLOW:
            if hw.toggle_sound():
                hw.beep()
            print("Sound:", "on" if hw.sound_on else "off")

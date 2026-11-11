# Games for the Adafruit QT Py ESP32-S3 (MicroPython).
# The board shows a menu at power-on. The player selects a game.
# To return to the menu during a game, reset the board.

import five_seconds
import hw
import menu
import simon
import wordle

# Each game: (name, menu pattern, function that plays one game).
GAMES = (
    ("simon", menu.CHASE, lambda: simon.run(reverse=False)),
    ("reverse_simon", menu.CHASE_BOTH_WAYS, lambda: simon.run(reverse=True)),
    ("wordle", menu.BLINK_ALL, wordle.run),
    ("five_seconds", menu.FIVE_SECONDS, five_seconds.run),
)

current = 0
try:
    while True:
        current = menu.choose(GAMES, current)
        print("Start:", GAMES[current][0])
        GAMES[current][2]()
finally:
    # Stop the tone and LEDs when you interrupt the program (Ctrl-C or Stop).
    hw.all_off()

# Five seconds: a game for 1 to 4 players. Each player has one button.
# All LEDs turn on for a random time of 1 to 3 s. The time starts when they
# turn off. Each player presses once, as near to 5.0 s as possible.
# The round always runs for 10 s. A button with no press has no player.
# There is no light and no tone during the round.
#
# Results:
#   1. Ranking: the LED of the player furthest from 5.0 s turns on first.
#      The LED of the nearest player (the winner) turns on last.
#   2. The LED of the winner flashes 3 times.
#   3. Replay: all LEDs turn on and off again to show the start. The board
#      then replays the full 10 s. The LED of each player turns on for 0.1 s
#      at the time of the press. All LEDs flash for 0.1 s at exactly 5.0 s.

import random
from time import sleep_ms, ticks_ms, ticks_diff

import hw

TARGET_MS = 5000
ROUND_MS = 10000
START_ON_MIN_MS = 1000
START_ON_MAX_MS = 3000
RANK_STEP_MS = 1000
REPLAY_FLASH_MS = 100
REPLAY_START_ON_MS = 1000


def start_signal(on_ms):
    """Turn on all LEDs for on_ms. The time starts when they turn off."""
    hw.set_all_leds(1)
    hw.beep()
    sleep_ms(on_ms - 200)  # the beep takes 200 ms
    hw.set_all_leds(0)


def read_round():
    """Run the 10 s round. Return the press time in ms for each button, or None.

    Only the first press of each button counts.
    """
    times = [None] * len(hw.buttons)
    start = ticks_ms()
    while True:
        elapsed = ticks_diff(ticks_ms(), start)
        if elapsed >= ROUND_MS:
            return times
        for index, button in enumerate(hw.buttons):
            if times[index] is None and button.value() == 0:
                times[index] = elapsed


def ranking(times):
    """Return the players, from the furthest from 5.0 s to the nearest."""
    players = [index for index, time in enumerate(times) if time is not None]
    players.sort(key=lambda index: -abs(times[index] - TARGET_MS))
    return players


def show_ranking(order):
    for index in order:
        hw.leds[index].value(1)
        hw.tone_on(hw.TONES[index])
        sleep_ms(150)
        hw.tone_off()
        sleep_ms(RANK_STEP_MS - 150)
    # All player LEDs are on now. They stayed on for 1 s after the last one.
    hw.set_all_leds(0)
    sleep_ms(400)
    winner = order[-1]
    for _ in range(3):
        hw.play(winner, 200)
        sleep_ms(200)


def replay(times):
    """Replay the 10 s round on the LEDs."""
    lit = [None] * len(hw.leds)
    tone = 0
    start = ticks_ms()
    while True:
        now = ticks_diff(ticks_ms(), start)
        if now >= ROUND_MS:
            break
        target_flash = TARGET_MS <= now < TARGET_MS + REPLAY_FLASH_MS
        new_tone = hw.BEEP_TONE if target_flash else 0
        for index, time in enumerate(times):
            pressed = time is not None and time <= now < time + REPLAY_FLASH_MS
            on = 1 if (pressed or target_flash) else 0
            if on != lit[index]:
                hw.leds[index].value(on)
                lit[index] = on
            if pressed and not target_flash:
                new_tone = hw.TONES[index]
        if new_tone != tone:
            if new_tone:
                hw.tone_on(new_tone)
            else:
                hw.tone_off()
            tone = new_tone
    hw.all_off()


def run():
    """Play one round, then show the ranking and the replay."""
    on_ms = START_ON_MIN_MS + random.randrange(START_ON_MAX_MS - START_ON_MIN_MS + 1)
    start_signal(on_ms)
    times = read_round()

    order = ranking(times)
    for index in order:
        print(hw.NAMES[index], times[index] / 1000, "s")
    if not order:
        print("No player pressed a button.")
        return

    sleep_ms(1000)
    show_ranking(order)
    print("Winner:", hw.NAMES[order[-1]])

    sleep_ms(1000)
    hw.set_all_leds(1)
    sleep_ms(REPLAY_START_ON_MS)
    hw.set_all_leds(0)
    replay(times)
    sleep_ms(1000)

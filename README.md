# Simon Says

Four games for the Adafruit QT Py ESP32-S3. The board has 4 coloured LEDs, 4 buttons, and a piezo buzzer. A menu at power-on lets the player select a game:

| Game | Description |
|---|---|
| `simon` | The board shows a sequence. The player repeats it. Each correct round adds one step. |
| `reverse_simon` | As `simon`, but the player enters the sequence from the last step to the first. |
| `wordle` | The player finds a hidden code of 5 colours. The board gives feedback on each guess. |
| `five_seconds` | For 1 to 4 players. Each player presses a button as near to 5.0 seconds as possible. |

The program uses **MicroPython**, not CircuitPython. The board does not show up as a USB drive. VS Code and the MicroPico extension communicate with the board over a serial port.

## Files

| File | Purpose |
|---|---|
| `main.py` | The list of games and the main loop. The board runs this file each time it starts. |
| `hw.py` | Pins, LEDs, buttons, buzzer, and the sound setting. |
| `menu.py` | The start menu and the LED pattern of each game. |
| `simon.py` | `simon` and `reverse_simon`. |
| `wordle.py` | `wordle`. |
| `five_seconds.py` | `five_seconds`. |
| `test.py` | A hardware test for the LEDs, the buttons, and the buzzer. It does not use the other files. |
| `.micropico` | Marks this folder as a MicroPico project. |

To add a game, write a file with a function that plays one game, and add one entry to `GAMES` in `main.py`.

## Hardware

- Adafruit QT Py ESP32-S3
- 4 LEDs: green, red, yellow, blue
- 4 resistors, 1 for each LED
- 4 push buttons
- 1 passive piezo buzzer, 12 mm ("without circuit")
- 3×AA battery pack with a switch

### Wiring

| Part | Header pin | GPIO | Connection |
|---|---|---|---|
| Green LED | A1 | 17 | GPIO → resistor → LED anode (long leg) → LED cathode → GND |
| Red LED | A3 | 8 | as above |
| Yellow LED | A0 | 18 | as above |
| Blue LED | A2 | 9 | as above |
| Green button | MOSI | 35 | GPIO → button → GND |
| Red button | RX | 16 | as above |
| Yellow button | MISO | 37 | as above |
| Blue button | SCK | 36 | as above |
| Buzzer | SDA | 7 | GPIO → buzzer + → buzzer − → GND |

The GPIO numbers are in `hw.py` (`LED_GPIOS`, `BUTTON_GPIOS`, `BUZZER_GPIO`) and in `test.py`.

The buttons need no resistors. The program turns on the internal pull-up on each button pin, so a pressed button reads low.

### LED resistors

The pins output 3.3 V. Each LED colour has a different forward voltage, so each colour needs a different resistor to give a similar brightness.

| Colour | Start value |
|---|---|
| Red, yellow | 330 Ω |
| Yellow-green | 220 Ω |
| Bright green, blue | 47 Ω |

Do not use less than 33 Ω.

### Power

Connect the 3×AA battery pack to the `BAT` and `GND` pads on the back of the board. These pads have diode protection and accept 3–6 V. Check the [Adafruit pinout page](https://learn.adafruit.com/adafruit-qt-py-esp32-s3/pinouts) before you solder.

If you connect the battery to the `5V` pin instead, put a Schottky diode (for example 1N5817) between battery + and `5V`. The diode stops USB current from flowing into the batteries.

## Software setup

The development environment is VS Code in WSL (Ubuntu) on Windows, with the MicroPico extension.

### 1. Install MicroPython on the board (once)

The board runs MicroPython 1.28.0 (`ESP32_GENERIC_S3`). The firmware file and `esptool` are in `../microcontroller`:

```
../microcontroller/setup/ESP32_GENERIC_S3-20260406-v1.28.0.bin
../microcontroller/.venv/bin/esptool
```

### 2. Forward the USB port to WSL (each session)

VS Code runs MicroPico inside WSL. WSL cannot see a Windows COM port, so you must forward the board's USB port to WSL with [usbipd-win](https://github.com/dorssel/usbipd-win). Run these commands in **Windows PowerShell**, not in WSL.

1. Find the bus ID of the board. The board shows as `USB Serial Device (COMx)` with `VID:PID` `303a:4001`.
   ```
   usbipd list
   ```
2. Share the device. Do this once per USB port, in PowerShell as Administrator. Replace `2-2` with the bus ID from step 1.
   ```
   usbipd bind --busid 2-2
   ```
3. Attach the device to WSL. Keep this window open.
   ```
   usbipd attach --wsl --hardware-id 303a:4001 --auto-attach
   ```

`--hardware-id` selects the board by its `VID:PID`, so the command works on any USB port. `--auto-attach` re-attaches the board after each reset or reconnection. Without it, the board goes back to Windows each time it resets.

If your version of `usbipd` rejects `--hardware-id`, use `--busid` with the bus ID from step 1. The bus ID changes when you use a different USB port.

To check the connection, run this command in WSL. It must show `/dev/ttyACM0`.

```
ls /dev/ttyACM*
```

If you get a permission error, add your user to the `dialout` group and log in again:

```
sudo usermod -aG dialout $USER
```

While the board is attached to WSL, Windows cannot use its COM port.

### 3. Connect MicroPico

1. In VS Code, open this folder in WSL.
2. Look at the status bar. It shows "Connected" when MicroPico finds the board.
3. If it does not connect, run **MicroPico: Connect** from the command palette.

## Run the program

The program uses 6 files: `main.py`, `hw.py`, `menu.py`, `simon.py`, `wordle.py`, and `five_seconds.py`. All 6 files must be on the board.

| Task | MicroPico command |
|---|---|
| Save all files to the board | **MicroPico: Upload project to Pico** |
| Save one changed file to the board | **MicroPico: Upload current file to Pico** |
| Run `test.py` once, without saving it to the board | **MicroPico: Run current file on Pico** |
| Stop the program | **Stop** button in the status bar |

After an upload, reset the board or run `main.py` to start the menu. The MicroPico terminal shows the selected game, each `wordle` guess, and the score.

## Menu

The menu shows at power-on and after each game. The LEDs repeat the pattern of the current game.

| Game | LED pattern |
|---|---|
| `simon` | red, blue, green, yellow, 0.5 s pause |
| `reverse_simon` | red, blue, green, yellow, 0.5 s pause, yellow, green, blue, red, 0.5 s pause |
| `wordle` | all 4 LEDs flash on and off together |
| `five_seconds` | blue, 0.3 s gap, green, red, all 4 LEDs, 0.4 s gap, yellow, 2 s pause. Each flash is 0.1 s. |

| Button | Action |
|---|---|
| Blue | Go to the next game |
| Green | Start the current game |
| Yellow | Turn the sound on or off. One beep confirms on. No beep confirms off. |
| Red | No action |

The sound is on at each power-on. To return to the menu during a game, reset the board.

## How to play

### `simon`

1. All 4 LEDs flash once. Then round 1 starts.
2. The board plays the sequence. Each colour has its own tone: green 415 Hz, red 310 Hz, yellow 252 Hz, blue 209 Hz.
3. Repeat the sequence on the buttons. The LED and its tone stay on while you hold a button.
4. A wrong button, or no press for 3 seconds, ends the game. The board plays a low tone and flashes the LED that you had to press.
5. The LEDs show the score in binary for 5 seconds. The score is the number of completed rounds.

The sequence plays faster after round 5 and again after round 13.

### `reverse_simon`

The game is the same as `simon`, but you enter the sequence from the last step to the first step.

### `wordle`

1. All 4 LEDs flash once. The board picks a hidden code of 5 colours. A colour can occur more than once.
2. Press 5 buttons to enter a guess. There is no time limit.
3. The board plays your guess back. Each element gives feedback:

   | Feedback | Meaning |
   |---|---|
   | On for 1 s | Correct colour in this position |
   | 4 flashes in 1 s | The colour is in the code, but not in this position |
   | 1 short flash | The colour is not in the code |

4. Guess again until all 5 elements are correct. There is no limit on the number of guesses.
5. When you find the code, all 4 LEDs flash once. Then red, green, blue, and yellow turn on in turn, 4 times.
6. The LEDs show the number of guesses in binary for 5 seconds.

A colour flashes 4 times whenever the code contains that colour in a different position. The number of times that the colour occurs in the code makes no difference. For example, the code has one green, in position 1. A guess with green in positions 1 and 2 shows "on for 1 s" for position 1 and "4 flashes" for position 2.

### `five_seconds`

Each player uses one button. 1 to 4 players can play.

1. All 4 LEDs turn on for a random time of 1 to 3 seconds. The time starts when they turn off.
2. Each player presses their button once, as near to 5.0 seconds as possible. There is no light and no tone during the round. Only the first press of each button counts.
3. The round always runs for 10 seconds. A button with no press has no player.
4. **Ranking:** the LED of the player furthest from 5.0 seconds turns on first. Each second, the LED of the next player turns on. The LED of the nearest player, the winner, turns on last.
5. All LEDs turn off. The LED of the winner flashes 3 times.
6. **Replay:** all 4 LEDs turn on for 1 second. The replay starts when they turn off, and it runs for the full 10 seconds. The LED of each player turns on for 0.1 seconds at the time of the press. All 4 LEDs flash for 0.1 seconds at exactly 5.0 seconds.

The MicroPico terminal shows the press time of each player.

### Binary score

Red is the lowest bit (1), then blue (2), green (4), and yellow (8). For example, a score of 5 turns on red and green. A score above 15 shows as 15 (all LEDs on).

## Settings

| Setting | File | Use |
|---|---|---|
| `TONES` | `hw.py` | The tone for each colour, in Hz. If the buzzer is too quiet, try values from 1000 to 2000 Hz. |
| `LED_GPIOS`, `BUTTON_GPIOS` | `hw.py` | The GPIO numbers, if your wiring is different from the table above. |
| `BINARY_SHOW_MS` | `hw.py` | The time that the score stays on. |
| `INPUT_TIMEOUT_MS` | `simon.py` | The time that the player has for each press. |
| `CODE_LENGTH` | `wordle.py` | The number of colours in the hidden code. |
| `TARGET_MS`, `ROUND_MS` | `five_seconds.py` | The target time and the length of the round. |

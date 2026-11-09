# Simon Says

A memory game for the Adafruit QT Py ESP32-S3. The board shows a sequence on 4 coloured LEDs and plays a tone for each LED. The player repeats the sequence on 4 buttons. Each correct round adds one step to the sequence.

The program uses **MicroPython**, not CircuitPython. The board does not show up as a USB drive. VS Code and the MicroPico extension communicate with the board over a serial port.

## Files

| File | Purpose |
|---|---|
| `main.py` | The game. The board runs this file each time it starts. |
| `test.py` | A hardware test for the LEDs, the buttons, and the buzzer. |
| `.micropico` | Marks this folder as a MicroPico project. |

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
| Green LED | A0 | 18 | GPIO → resistor → LED anode (long leg) → LED cathode → GND |
| Red LED | A1 | 17 | as above |
| Yellow LED | A2 | 9 | as above |
| Blue LED | A3 | 8 | as above |
| Green button | MOSI | 35 | GPIO → button → GND |
| Red button | MISO | 37 | as above |
| Yellow button | SCK | 36 | as above |
| Blue button | RX | 16 | as above |
| Buzzer | SDA | 7 | GPIO → buzzer + → buzzer − → GND |

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
2. Share the device. Do this once per USB port, in PowerShell as Administrator.
   ```
   usbipd bind --busid 3-2
   ```
3. Attach the device to WSL. Keep this window open.
   ```
   usbipd attach --wsl --busid 3-2 --auto-attach
   ```

`--auto-attach` re-attaches the board after each reset or reconnection. Without it, the board goes back to Windows each time it resets.

The bus ID `3-2` belongs to one USB port. If you use a different port, run `usbipd list` again.

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

| Task | MicroPico command |
|---|---|
| Run a file once, without saving it to the board | **MicroPico: Run current file on Pico** |
| Save `main.py` to the board so that it runs at each start | **MicroPico: Upload current file to Pico** |
| Stop the program | **Stop** button in the status bar |

Run `test.py` with **Run current file on Pico**. Do not upload it, so that `main.py` stays on the board.

The score shows in the MicroPico terminal after each game.

## How to play

1. The LEDs turn on one after the other. Press any button to start.
2. All 4 LEDs flash once. Then round 1 starts.
3. The board plays the sequence. Each colour has its own tone: green 415 Hz, red 310 Hz, yellow 252 Hz, blue 209 Hz.
4. Repeat the sequence on the buttons. The LED and its tone stay on while you hold a button.
5. A wrong button, or no press for 3 seconds, ends the game. The board plays a low tone and flashes the LED that you had to press.
6. The LEDs show the score in binary for 5 seconds. Red is the lowest bit (1), then blue (2), green (4), and yellow (8). For example, a score of 5 turns on red and green. A score above 15 shows as 15 (all LEDs on).

The sequence plays faster after round 5 and again after round 13.

## Settings

Change these values at the top of `main.py`:

| Setting | Use |
|---|---|
| `TONES` | The tone for each colour, in Hz. If the buzzer is too quiet, try values from 1000 to 2000 Hz. |
| `INPUT_TIMEOUT_MS` | The time that the player has for each press. |
| `LED_GPIOS`, `BUTTON_GPIOS` | The GPIO numbers, if your wiring is different from the table above. |

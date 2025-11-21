# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MicroPython project for controlling WS2812B NeoPixel 8x8 LED matrices with Raspberry Pi Pico 2W (RP2350 chip). Uses VS Code with the MicroPico extension for development and deployment.

## Development Environment

- **IDE**: VS Code with MicroPico extension (`paulober.pico-w-go`)
- **Language**: MicroPython (not standard Python)
- **Target Hardware**: Raspberry Pi Pico 2W (RP2350)
- **Firmware**: MicroPython for RP2350 from micropython.org/download/RPI_PICO2_W/

## Deploying to Pico

Files are uploaded to the Pico using the MicroPico extension:
- `Ctrl+Shift+P` → "MicroPico: Upload file to Pico"
- Or use the MicroPico status bar buttons

To run code on the Pico:
- `Ctrl+Shift+P` → "MicroPico: Run current file on Pico"

## Code Architecture

### Core Modules

- **`neopixel_basics.py`** - Standalone examples using the built-in `neopixel` module directly. Good for learning raw NeoPixel API.

- **`neopixel_matrix.py`** - `NeoPixelMatrix` class that wraps raw NeoPixel access with x,y coordinate system. Handles serpentine layout conversion automatically. Import this when building new features.

- **`neopixel_animations.py`** - Animation library with effects (rainbow, fire, matrix rain, etc.). Uses raw index access with helper functions, not the Matrix class.

### Key Patterns

**Serpentine Layout**: Most 8x8 matrices wire odd rows in reverse. The `xy_to_index()` function handles this:
```python
def xy_to_index(x, y, serpentine=True):
    if serpentine and y % 2 == 1:
        return y * 8 + (7 - x)
    return y * 8 + x
```

**Brightness Control**: Always apply brightness scaling (default 0.3) to prevent overcurrent:
```python
color = tuple(int(c * BRIGHTNESS) for c in color)
```

**Display Update**: Changes don't appear until `np.write()` is called.

## Hardware Configuration

- **Data Pin**: GP0 (configurable via `DATA_PIN` constant)
- **LED Count**: 64 (8x8 matrix)
- **Power**: External 5V supply required (not from Pico)

## MicroPython Specifics

- Use `from machine import Pin` (not RPi.GPIO)
- Use `from utime import sleep` (or `time.sleep`)
- Built-in `neopixel` module - no pip install needed
- Limited RAM - avoid large data structures

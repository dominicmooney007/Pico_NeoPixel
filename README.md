# NeoPixel 8x8 Matrix - Beginner Guide for Raspberry Pi Pico 2W

A complete beginner's guide to using WS2812B NeoPixel 8x8 LED matrices with the Raspberry Pi Pico 2W.

---

## Quick Start

1. Wire up your hardware (see below)
2. Install MicroPython on your Pico 2W
3. Upload the example files to your Pico
4. Run `neopixel_basics.py` to test your setup!

---

## Hardware Setup

### What You Need

- Raspberry Pi Pico 2W
- WS2812B 8x8 NeoPixel Matrix (64 LEDs)
- 5V 4A Power Supply (minimum 2A)
- Jumper wires
- (Optional) 74AHCT125 level shifter

### Wiring Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   EXTERNAL 5V POWER SUPPLY (4A recommended)                 │
│   ┌─────────────┐                                           │
│   │  (+) ────────────────────────> NeoPixel VCC (Red)       │
│   │  (-) ───┬────────────────────> NeoPixel GND (Black)     │
│   └─────────┼───┘                                           │
│             │                                               │
│   PICO 2W   │    *** IMPORTANT: Common Ground! ***          │
│   ┌─────────┼─────────┐                                     │
│   │  GND ───┘         │                                     │
│   │  GP0 ────────────────────────> NeoPixel DIN (Green)     │
│   └───────────────────┘                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Pin Connections

| NeoPixel Pin | Connect To           | Wire Color (typical) |
|--------------|----------------------|----------------------|
| VCC / 5V     | External 5V PSU (+)  | Red                  |
| GND          | Pico GND + PSU (-)   | Black                |
| DIN          | Pico GP0             | Green/Yellow         |

### Power Warning

**Never power 64 LEDs directly from the Pico!**

- 64 LEDs at full brightness = 3.8A (Pico can only supply ~500mA)
- Use an external 5V power supply rated for 2-4A
- Always connect grounds together (Pico GND to power supply GND)

---

## Software Setup

### 1. Install MicroPython

1. Download the **Pico 2W** firmware from: https://micropython.org/download/RPI_PICO2_W/
   - Make sure to get the **RP2350** version (not RP2040!)
2. Hold the **BOOTSEL** button on your Pico 2W
3. While holding, connect USB to your computer
4. Release BOOTSEL - a drive called "RPI-RP2" appears
5. Drag and drop the `.uf2` file onto the drive
6. Pico reboots automatically with MicroPython installed

### 2. Install Thonny IDE (Recommended)

1. Download from: https://thonny.org/
2. Open Thonny
3. Go to **Tools > Options > Interpreter**
4. Select "MicroPython (Raspberry Pi Pico)"
5. Select the correct COM port

### 3. Upload the Example Files

1. Open each `.py` file in Thonny
2. Go to **File > Save As**
3. Choose "MicroPython device"
4. Keep the same filename

---

## Example Files

### `neopixel_basics.py`
Start here! Simple examples demonstrating:
- Setting individual pixels
- Filling with solid colors
- Basic animations (chase, fade)
- Color definitions

### `neopixel_matrix.py`
Helper class for working with x,y coordinates:
- `set_pixel(x, y, color)` - Easy coordinate addressing
- `draw_row()`, `draw_column()` - Line drawing
- `draw_rectangle()`, `draw_border()` - Shape drawing
- Layout test to determine if your matrix is serpentine

### `neopixel_animations.py`
Fun animations to try:
- Rainbow wave
- Fire effect
- Matrix rain (The Matrix style)
- Sparkle / twinkle
- Breathing effect
- Snake
- Spiral
- And more!

---

## Understanding Pixel Layout

NeoPixel matrices are wired as a single strip. Most use a **serpentine** (zigzag) pattern:

```
Row 0: →  0   1   2   3   4   5   6   7
Row 1: ← 15  14  13  12  11  10   9   8   (reversed!)
Row 2: → 16  17  18  19  20  21  22  23
Row 3: ← 31  30  29  28  27  26  25  24   (reversed!)
...
```

To test your matrix layout, run in Thonny:
```python
from neopixel_matrix import test_layout
test_layout()
```

---

## Quick Code Reference

### Basic Usage
```python
from machine import Pin
from neopixel import NeoPixel

# Setup
np = NeoPixel(Pin(0, Pin.OUT), 64)

# Set a pixel (index 0-63)
np[0] = (255, 0, 0)  # Red (R, G, B)
np.write()           # Update display

# Fill all pixels
np.fill((0, 255, 0))  # Green
np.write()

# Turn off
np.fill((0, 0, 0))
np.write()
```

### Using X,Y Coordinates
```python
from neopixel_matrix import NeoPixelMatrix

matrix = NeoPixelMatrix(pin=0)
matrix.set_pixel(3, 4, (255, 0, 0))  # Red at x=3, y=4
matrix.show()
```

### Common Colors
```python
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
BLUE    = (0, 0, 255)
WHITE   = (255, 255, 255)
YELLOW  = (255, 255, 0)
CYAN    = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE  = (255, 165, 0)
OFF     = (0, 0, 0)
```

---

## Troubleshooting

### LEDs not lighting up
- Check DIN vs DOUT - data goes INTO DIN
- Verify common ground connection
- Check power supply is on and connected

### Flickering or wrong colors
- Add a level shifter (74AHCT125)
- Check for loose connections
- Try a different GPIO pin

### Only some LEDs work
- Power supply may be insufficient
- Check for damaged LEDs in the chain

### Colors look wrong (e.g., red shows as green)
- Your matrix might use GRB instead of RGB
- Try swapping R and G values in your code

### First LED is always on/wrong color
- Normal for some matrices - first LED may need a "dummy" signal
- Add `np[0] = (0,0,0)` before your main code

---

## Tips for Beginners

1. **Start with low brightness** (20-30%) to save power and your eyes
2. **Always call `np.write()`** after making changes - nothing updates until you do
3. **Use the helper class** from `neopixel_matrix.py` for easier coordinate-based drawing
4. **Power off when rewiring** to avoid shorts
5. **Add a capacitor** (1000µF) across power lines for stability

---

## Resources

- [MicroPython NeoPixel Docs](https://docs.micropython.org/en/latest/esp8266/tutorial/neopixel.html)
- [Raspberry Pi Pico Documentation](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html)
- [WS2812B Datasheet](https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf)
- [Adafruit NeoPixel Guide](https://learn.adafruit.com/adafruit-neopixel-uberguide)

---

Happy coding! 🎨

# NeoPixel 8x8 Matrix - Beginner Guide for Raspberry Pi Pico 2W
# ============================================================
#
# HARDWARE SETUP:
# ---------------
# NeoPixel Matrix    Pico 2W           Notes
# ------------------------------------------------------
# DIN (Data In)  --> GP0 (Pin 1)       Any GPIO works
# VCC (+5V)      --> External 5V PSU   DO NOT use Pico's 5V!
# GND            --> GND               Connect to BOTH Pico AND PSU ground
#
# IMPORTANT: 64 LEDs can draw up to 3.8A at full white brightness!
# Use a 5V 4A power supply for reliable operation.
#
# WIRING DIAGRAM:
#
#   External 5V Power Supply
#   ┌─────────────────────┐
#   │  (+) ─────────────────────────> NeoPixel VCC
#   │  (-) ───┬─────────────────────> NeoPixel GND
#   └─────────┼───────────┘
#             │
#   Pico 2W   │
#   ┌─────────┼───────────┐
#   │  GND ───┘           │         (Common ground!)
#   │  GP0 ─────────────────────────> NeoPixel DIN
#   └─────────────────────┘
#

from machine import Pin
from neopixel import NeoPixel
from utime import sleep

# =============================================================================
# CONFIGURATION - Change these to match your setup
# =============================================================================

DATA_PIN = 0          # GPIO pin connected to DIN (data in)
NUM_LEDS = 64         # 8x8 matrix = 64 LEDs
BRIGHTNESS = 0.3      # Start low! (0.0 to 1.0)

# =============================================================================
# INITIALIZE THE NEOPIXEL STRIP
# =============================================================================

# Create the NeoPixel object
np = NeoPixel(Pin(DATA_PIN, Pin.OUT), NUM_LEDS)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def dim(color, brightness=BRIGHTNESS):
    """Reduce color brightness to save power and protect your eyes!"""
    return tuple(int(c * brightness) for c in color)

def clear():
    """Turn off all LEDs"""
    np.fill((0, 0, 0))
    np.write()

def fill(color):
    """Fill all LEDs with one color"""
    np.fill(dim(color))
    np.write()

# =============================================================================
# COMMON COLORS (RGB format: Red, Green, Blue - each 0-255)
# =============================================================================

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
OFF = (0, 0, 0)

# =============================================================================
# EXAMPLE 1: Turn on a single LED
# =============================================================================

def example_single_led():
    """Light up the first LED red"""
    print("Example 1: Single LED")
    clear()
    np[0] = dim(RED)  # First LED (index 0)
    np.write()        # Always call write() to update the display!
    sleep(2)

# =============================================================================
# EXAMPLE 2: Fill with solid color
# =============================================================================

def example_fill_colors():
    """Cycle through different colors"""
    print("Example 2: Solid colors")
    colors = [RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA]

    for color in colors:
        fill(color)
        sleep(1)

    clear()

# =============================================================================
# EXAMPLE 3: Light up LEDs one by one
# =============================================================================

def example_sequential():
    """Light each LED in sequence"""
    print("Example 3: Sequential LEDs")

    for i in range(NUM_LEDS):
        clear()
        np[i] = dim(BLUE)
        np.write()
        sleep(0.05)

    clear()

# =============================================================================
# EXAMPLE 4: Simple chase effect
# =============================================================================

def example_chase():
    """A dot chasing around the matrix"""
    print("Example 4: Chase effect")

    for _ in range(3):  # Run 3 times
        for i in range(NUM_LEDS):
            np.fill((0, 0, 0))        # Clear all
            np[i] = dim(GREEN)         # Light current LED
            np.write()
            sleep(0.03)

# =============================================================================
# EXAMPLE 5: Fade in and out
# =============================================================================

def example_fade():
    """Fade all LEDs in and out"""
    print("Example 5: Fade effect")

    # Fade in
    for brightness in range(0, 100, 5):
        color = (brightness, 0, brightness)  # Purple fade
        np.fill(color)
        np.write()
        sleep(0.03)

    # Fade out
    for brightness in range(100, 0, -5):
        color = (brightness, 0, brightness)
        np.fill(color)
        np.write()
        sleep(0.03)

    clear()

# =============================================================================
# RUN ALL EXAMPLES
# =============================================================================

if __name__ == "__main__":
    print("NeoPixel 8x8 Matrix - Basic Examples")
    print("=" * 40)
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            example_single_led()
            example_fill_colors()
            example_sequential()
            example_chase()
            example_fade()
            print("\nRestarting examples...\n")
            sleep(1)

    except KeyboardInterrupt:
        clear()
        print("\nStopped. All LEDs off.")

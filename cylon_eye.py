# Cylon Eye / KITT Scanner - NeoPixel 8x8 Matrix
# ===============================================
#
# The classic scanning red eye effect from Battlestar Galactica
# and Knight Rider's KITT!
#
# Features:
# - Smooth sweeping animation
# - Fading trail effect
# - Multiple modes (single, double, random)
# - Customizable colors
#

from machine import Pin
from neopixel import NeoPixel
from utime import sleep
import math

# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_PIN = 0
WIDTH = 8
HEIGHT = 8
NUM_LEDS = WIDTH * HEIGHT
BRIGHTNESS = 0.5

# Animation settings
SCAN_SPEED = 0.03    # Seconds per frame
TRAIL_LENGTH = 4     # Number of fading pixels behind eye
EYE_WIDTH = 2        # Width of the bright center

# Initialize NeoPixel
np = NeoPixel(Pin(DATA_PIN, Pin.OUT), NUM_LEDS)

# =============================================================================
# COLORS
# =============================================================================

# Classic Cylon red
CYLON_RED = (255, 0, 0)

# KITT red (slightly different)
KITT_RED = (255, 20, 0)

# Alternative colors
BLUE_SCANNER = (0, 100, 255)
GREEN_SCANNER = (0, 255, 50)
PURPLE_SCANNER = (150, 0, 255)
ORANGE_SCANNER = (255, 100, 0)
WHITE_SCANNER = (255, 255, 255)

# =============================================================================
# HELPERS
# =============================================================================

def xy(x, y):
    """Convert x,y to pixel index (serpentine layout)."""
    if y % 2 == 1:
        return y * WIDTH + (WIDTH - 1 - x)
    return y * WIDTH + x

def dim(color, factor=1.0):
    """Apply brightness and additional dimming factor."""
    return tuple(int(c * BRIGHTNESS * factor) for c in color)

def set_pixel(x, y, color):
    """Set pixel at x,y."""
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        np[xy(x, y)] = color

def clear():
    """Clear display."""
    np.fill((0, 0, 0))
    np.write()

def show():
    """Update display."""
    np.write()

def lerp(a, b, t):
    """Linear interpolation."""
    return a + (b - a) * t

# =============================================================================
# CYLON EYE ANIMATIONS
# =============================================================================

def draw_eye(pos, color, row=3):
    """
    Draw the scanning eye at position with trail.
    pos can be fractional for smooth movement.
    """
    np.fill((0, 0, 0))

    # Draw on two rows for better visibility
    rows = [row, row + 1] if row < HEIGHT - 1 else [row]

    for y in rows:
        # Draw trailing fade (behind the eye)
        for i in range(TRAIL_LENGTH + EYE_WIDTH + TRAIL_LENGTH):
            x = int(pos) - TRAIL_LENGTH + i
            if 0 <= x < WIDTH:
                # Calculate distance from center of eye
                dist = abs(x - pos)

                if dist < EYE_WIDTH / 2:
                    # Bright center
                    intensity = 1.0
                elif dist < EYE_WIDTH / 2 + TRAIL_LENGTH:
                    # Fading trail
                    trail_dist = dist - EYE_WIDTH / 2
                    intensity = 1.0 - (trail_dist / TRAIL_LENGTH)
                    intensity = max(0, intensity ** 1.5)  # Exponential fade
                else:
                    intensity = 0

                if intensity > 0:
                    pixel_color = dim(color, intensity)
                    set_pixel(x, y, pixel_color)

    show()


def single_sweep(color=CYLON_RED, speed=SCAN_SPEED):
    """Single eye sweeping back and forth."""
    # Sweep right
    for i in range(WIDTH * 4):
        pos = i / 4
        draw_eye(pos, color)
        sleep(speed)

    # Sweep left
    for i in range(WIDTH * 4, 0, -1):
        pos = i / 4
        draw_eye(pos, color)
        sleep(speed)


def double_sweep(color1=CYLON_RED, color2=BLUE_SCANNER, speed=SCAN_SPEED):
    """Two eyes sweeping in opposite directions."""
    for frame in range(WIDTH * 8):
        np.fill((0, 0, 0))

        # Eye 1 position (sweeps back and forth)
        cycle = frame % (WIDTH * 8)
        if cycle < WIDTH * 4:
            pos1 = cycle / 4
        else:
            pos1 = (WIDTH * 8 - cycle) / 4

        # Eye 2 position (opposite)
        pos2 = WIDTH - 1 - pos1

        # Draw both eyes on different rows
        # Eye 1 on rows 1-2
        for y in [1, 2]:
            for i in range(-TRAIL_LENGTH, EYE_WIDTH + TRAIL_LENGTH):
                x = int(pos1) + i
                if 0 <= x < WIDTH:
                    dist = abs(x - pos1)
                    if dist < EYE_WIDTH / 2:
                        intensity = 1.0
                    else:
                        intensity = max(0, 1.0 - (dist - EYE_WIDTH/2) / TRAIL_LENGTH) ** 1.5
                    if intensity > 0:
                        set_pixel(x, y, dim(color1, intensity))

        # Eye 2 on rows 5-6
        for y in [5, 6]:
            for i in range(-TRAIL_LENGTH, EYE_WIDTH + TRAIL_LENGTH):
                x = int(pos2) + i
                if 0 <= x < WIDTH:
                    dist = abs(x - pos2)
                    if dist < EYE_WIDTH / 2:
                        intensity = 1.0
                    else:
                        intensity = max(0, 1.0 - (dist - EYE_WIDTH/2) / TRAIL_LENGTH) ** 1.5
                    if intensity > 0:
                        set_pixel(x, y, dim(color2, intensity))

        show()
        sleep(speed)


def vertical_sweep(color=GREEN_SCANNER, speed=SCAN_SPEED):
    """Eye sweeping vertically."""
    # Sweep down
    for i in range(HEIGHT * 4):
        pos = i / 4
        np.fill((0, 0, 0))

        for x in range(WIDTH):
            for j in range(-TRAIL_LENGTH, EYE_WIDTH + TRAIL_LENGTH):
                y = int(pos) + j
                if 0 <= y < HEIGHT:
                    dist = abs(y - pos)
                    if dist < EYE_WIDTH / 2:
                        intensity = 1.0
                    else:
                        intensity = max(0, 1.0 - (dist - EYE_WIDTH/2) / TRAIL_LENGTH) ** 1.5
                    if intensity > 0:
                        set_pixel(x, y, dim(color, intensity))
        show()
        sleep(speed)

    # Sweep up
    for i in range(HEIGHT * 4, 0, -1):
        pos = i / 4
        np.fill((0, 0, 0))

        for x in range(WIDTH):
            for j in range(-TRAIL_LENGTH, EYE_WIDTH + TRAIL_LENGTH):
                y = int(pos) + j
                if 0 <= y < HEIGHT:
                    dist = abs(y - pos)
                    if dist < EYE_WIDTH / 2:
                        intensity = 1.0
                    else:
                        intensity = max(0, 1.0 - (dist - EYE_WIDTH/2) / TRAIL_LENGTH) ** 1.5
                    if intensity > 0:
                        set_pixel(x, y, dim(color, intensity))
        show()
        sleep(speed)


def radar_sweep(color=GREEN_SCANNER, speed=SCAN_SPEED * 2):
    """Rotating radar-style sweep."""
    cx, cy = 3.5, 3.5

    for angle in range(0, 360, 3):
        np.fill((0, 0, 0))

        # Draw fading trail
        for trail in range(30):
            a = math.radians(angle - trail * 2)

            for r in range(1, 5):
                x = int(cx + r * math.cos(a))
                y = int(cy + r * math.sin(a))

                if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                    intensity = (1 - trail / 30) ** 2
                    set_pixel(x, y, dim(color, intensity))

        show()
        sleep(speed)


def pulsing_eye(color=CYLON_RED, cycles=3):
    """Eye that pulses while scanning."""
    for cycle in range(cycles):
        # Sweep with pulsing
        for direction in [1, -1]:
            positions = range(0, WIDTH * 4) if direction == 1 else range(WIDTH * 4, 0, -1)

            for i in positions:
                pos = i / 4

                # Pulse intensity
                pulse = 0.5 + 0.5 * math.sin(i / 3)

                np.fill((0, 0, 0))

                for y in [3, 4]:
                    for j in range(-TRAIL_LENGTH, EYE_WIDTH + TRAIL_LENGTH):
                        x = int(pos) + j
                        if 0 <= x < WIDTH:
                            dist = abs(x - pos)
                            if dist < EYE_WIDTH / 2:
                                intensity = pulse
                            else:
                                intensity = max(0, pulse * (1.0 - (dist - EYE_WIDTH/2) / TRAIL_LENGTH) ** 1.5)
                            if intensity > 0:
                                set_pixel(x, y, dim(color, intensity))

                show()
                sleep(SCAN_SPEED)


def multi_color_sweep():
    """Sweep that changes colors."""
    colors = [CYLON_RED, ORANGE_SCANNER, GREEN_SCANNER, BLUE_SCANNER, PURPLE_SCANNER]

    for color in colors:
        single_sweep(color, SCAN_SPEED)


def knight_rider():
    """Classic KITT effect with smooth acceleration."""
    color = KITT_RED

    while True:
        # Accelerate right
        for i in range(WIDTH * 4):
            pos = i / 4
            # Ease in/out speed
            progress = i / (WIDTH * 4)
            speed = SCAN_SPEED * (0.5 + abs(progress - 0.5))
            draw_eye(pos, color)
            sleep(speed)

        # Accelerate left
        for i in range(WIDTH * 4, 0, -1):
            pos = i / 4
            progress = i / (WIDTH * 4)
            speed = SCAN_SPEED * (0.5 + abs(progress - 0.5))
            draw_eye(pos, color)
            sleep(speed)


# =============================================================================
# MAIN
# =============================================================================

def run_cylon_eye():
    """Main function - cycles through all effects."""
    print("=" * 50)
    print("  Cylon Eye / KITT Scanner")
    print("=" * 50)
    print("\nModes: Single, Double, Vertical, Radar, Pulse, Multi-color")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            print("Mode: Classic Cylon")
            for _ in range(3):
                single_sweep(CYLON_RED)

            print("Mode: Double Scanner")
            for _ in range(2):
                double_sweep()

            print("Mode: Vertical Sweep")
            for _ in range(2):
                vertical_sweep()

            print("Mode: Radar Sweep")
            radar_sweep()

            print("Mode: Pulsing Eye")
            pulsing_eye()

            print("Mode: Multi-Color")
            multi_color_sweep()

            print("\nRestarting sequence...\n")

    except KeyboardInterrupt:
        clear()
        print("\nCylon eye deactivated.")


if __name__ == "__main__":
    run_cylon_eye()

    # Or run specific effects:
    # knight_rider()  # Runs forever
    # radar_sweep()
    # double_sweep()

# NeoPixel 8x8 Matrix - Fun Animations
# =====================================
#
# A collection of fun animation effects for your 8x8 NeoPixel matrix.
# Run this file to see all animations in sequence!
#

from machine import Pin
from neopixel import NeoPixel
from utime import sleep
import math

# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_PIN = 0
NUM_LEDS = 64
WIDTH = 8
HEIGHT = 8
BRIGHTNESS = 0.3  # Keep low to save power!

# Initialize NeoPixel
np = NeoPixel(Pin(DATA_PIN, Pin.OUT), NUM_LEDS)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def xy_to_index(x, y, serpentine=True):
    """Convert x,y to pixel index (serpentine layout)."""
    if serpentine and y % 2 == 1:
        return y * WIDTH + (WIDTH - 1 - x)
    return y * WIDTH + x


def set_pixel(x, y, color):
    """Set pixel at x,y with brightness applied."""
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        r, g, b = color
        np[xy_to_index(x, y)] = (
            int(r * BRIGHTNESS),
            int(g * BRIGHTNESS),
            int(b * BRIGHTNESS)
        )


def clear():
    """Turn off all LEDs."""
    np.fill((0, 0, 0))
    np.write()


def show():
    """Update the display."""
    np.write()


def wheel(pos):
    """
    Generate rainbow colors across 0-255 positions.
    This creates a smooth color transition through the spectrum.
    """
    pos = pos % 256
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    else:
        pos -= 170
        return (pos * 3, 0, 255 - pos * 3)


# =============================================================================
# ANIMATION 1: Rainbow Wave
# =============================================================================

def rainbow_wave(duration=5):
    """
    Rainbow colors flowing across the matrix.
    """
    print("Animation: Rainbow Wave")
    iterations = int(duration / 0.02)

    for j in range(iterations):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                # Color based on position + time offset
                color_index = (x * 32 + y * 32 + j * 4) % 256
                set_pixel(x, y, wheel(color_index))
        show()
        sleep(0.02)


# =============================================================================
# ANIMATION 2: Color Wipe
# =============================================================================

def color_wipe(color, wait=0.03):
    """
    Fill the matrix one pixel at a time.
    """
    print(f"Animation: Color Wipe")
    r, g, b = color

    for i in range(NUM_LEDS):
        np[i] = (int(r * BRIGHTNESS), int(g * BRIGHTNESS), int(b * BRIGHTNESS))
        show()
        sleep(wait)


# =============================================================================
# ANIMATION 3: Sparkle
# =============================================================================

def sparkle(color, duration=3):
    """
    Random pixels twinkle on and off.
    """
    print("Animation: Sparkle")
    import random

    iterations = int(duration / 0.05)
    r, g, b = color

    for _ in range(iterations):
        # Clear previous
        np.fill((0, 0, 0))

        # Light random pixels
        for _ in range(10):  # 10 sparkles at a time
            idx = random.randint(0, NUM_LEDS - 1)
            brightness = random.uniform(0.1, BRIGHTNESS)
            np[idx] = (int(r * brightness), int(g * brightness), int(b * brightness))

        show()
        sleep(0.05)


# =============================================================================
# ANIMATION 4: Breathing Effect
# =============================================================================

def breathing(color, cycles=3):
    """
    All LEDs fade in and out together, like breathing.
    """
    print("Animation: Breathing")
    r, g, b = color

    for _ in range(cycles):
        # Fade in
        for i in range(0, 100, 2):
            brightness = (i / 100) * BRIGHTNESS
            np.fill((int(r * brightness), int(g * brightness), int(b * brightness)))
            show()
            sleep(0.02)

        # Fade out
        for i in range(100, 0, -2):
            brightness = (i / 100) * BRIGHTNESS
            np.fill((int(r * brightness), int(g * brightness), int(b * brightness)))
            show()
            sleep(0.02)


# =============================================================================
# ANIMATION 5: Matrix Rain (like The Matrix movie)
# =============================================================================

def matrix_rain(duration=5):
    """
    Green 'rain' falling down the matrix, like The Matrix.
    """
    print("Animation: Matrix Rain")
    import random

    # Track drops: each column has a drop position
    drops = [random.randint(-HEIGHT, 0) for _ in range(WIDTH)]
    iterations = int(duration / 0.1)

    for _ in range(iterations):
        np.fill((0, 0, 0))

        for x in range(WIDTH):
            # Draw the drop and its trail
            for trail in range(4):
                y = drops[x] - trail
                if 0 <= y < HEIGHT:
                    # Brightest at head, fading trail
                    intensity = 255 - (trail * 60)
                    intensity = max(0, intensity)
                    set_pixel(x, y, (0, intensity, 0))

            # Move drop down
            drops[x] += 1

            # Reset drop when it goes off screen
            if drops[x] > HEIGHT + 4:
                drops[x] = random.randint(-4, 0)

        show()
        sleep(0.1)


# =============================================================================
# ANIMATION 6: Expanding Square
# =============================================================================

def expanding_square(color, cycles=3):
    """
    A square expands from the center outward.
    """
    print("Animation: Expanding Square")

    for _ in range(cycles):
        # Expand from center
        for size in range(5):
            np.fill((0, 0, 0))

            # Calculate rectangle bounds
            x1 = 3 - size
            y1 = 3 - size
            x2 = 4 + size
            y2 = 4 + size

            # Draw rectangle outline
            for x in range(max(0, x1), min(WIDTH, x2 + 1)):
                for y in range(max(0, y1), min(HEIGHT, y2 + 1)):
                    if x == x1 or x == x2 or y == y1 or y == y2:
                        set_pixel(x, y, color)

            show()
            sleep(0.15)

        sleep(0.3)


# =============================================================================
# ANIMATION 7: Snake
# =============================================================================

def snake(duration=5):
    """
    A colorful snake slithers across the matrix.
    """
    print("Animation: Snake")

    snake_length = 8
    snake_body = [(0, 0)]  # List of (x, y) positions

    # Direction: 0=right, 1=down, 2=left, 3=up
    direction = 0
    dx = [1, 0, -1, 0]
    dy = [0, 1, 0, -1]

    iterations = int(duration / 0.1)

    for i in range(iterations):
        # Get head position
        head_x, head_y = snake_body[-1]

        # Try to move in current direction
        new_x = head_x + dx[direction]
        new_y = head_y + dy[direction]

        # If hit wall, turn
        if new_x < 0 or new_x >= WIDTH or new_y < 0 or new_y >= HEIGHT:
            direction = (direction + 1) % 4
            new_x = head_x + dx[direction]
            new_y = head_y + dy[direction]

        # Add new head
        snake_body.append((new_x, new_y))

        # Remove tail if too long
        if len(snake_body) > snake_length:
            snake_body.pop(0)

        # Draw snake
        np.fill((0, 0, 0))
        for j, (x, y) in enumerate(snake_body):
            # Color gradient along body
            color = wheel((i * 5 + j * 30) % 256)
            set_pixel(x, y, color)

        show()
        sleep(0.1)


# =============================================================================
# ANIMATION 8: Fire Effect
# =============================================================================

def fire_effect(duration=5):
    """
    Simulated fire effect rising from the bottom.
    """
    print("Animation: Fire Effect")
    import random

    # Heat array
    heat = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

    iterations = int(duration / 0.05)

    for _ in range(iterations):
        # Cool down every cell
        for y in range(HEIGHT):
            for x in range(WIDTH):
                cooldown = random.randint(0, 20)
                heat[y][x] = max(0, heat[y][x] - cooldown)

        # Heat rises
        for y in range(HEIGHT - 1, 0, -1):
            for x in range(WIDTH):
                # Average of cells below
                left = max(0, x - 1)
                right = min(WIDTH - 1, x + 1)
                heat[y][x] = (heat[y-1][left] + heat[y-1][x] + heat[y-1][right]) // 3

        # Random sparks at bottom
        for x in range(WIDTH):
            if random.random() < 0.5:
                heat[0][x] = min(255, heat[0][x] + random.randint(160, 255))

        # Convert heat to colors and display
        for y in range(HEIGHT):
            for x in range(WIDTH):
                h = heat[y][x]
                # Fire color palette: black -> red -> yellow -> white
                if h < 85:
                    r, g, b = h * 3, 0, 0
                elif h < 170:
                    r, g, b = 255, (h - 85) * 3, 0
                else:
                    r, g, b = 255, 255, (h - 170) * 3

                set_pixel(x, HEIGHT - 1 - y, (r, g, b))  # Flip Y so fire rises

        show()
        sleep(0.05)


# =============================================================================
# ANIMATION 9: Checkerboard Flash
# =============================================================================

def checkerboard(color1, color2, flashes=6):
    """
    Alternating checkerboard pattern.
    """
    print("Animation: Checkerboard")

    for i in range(flashes):
        np.fill((0, 0, 0))

        for y in range(HEIGHT):
            for x in range(WIDTH):
                if (x + y + i) % 2 == 0:
                    set_pixel(x, y, color1)
                else:
                    set_pixel(x, y, color2)

        show()
        sleep(0.3)


# =============================================================================
# ANIMATION 10: Spiral
# =============================================================================

def spiral(color, inward=True):
    """
    Light up pixels in a spiral pattern.
    """
    print("Animation: Spiral")

    # Generate spiral coordinates
    coords = []
    x, y = 0, 0
    dx, dy = 1, 0
    visited = set()

    for _ in range(NUM_LEDS):
        coords.append((x, y))
        visited.add((x, y))

        # Check if we need to turn
        next_x, next_y = x + dx, y + dy
        if (next_x < 0 or next_x >= WIDTH or
            next_y < 0 or next_y >= HEIGHT or
            (next_x, next_y) in visited):
            # Turn right: (1,0) -> (0,1) -> (-1,0) -> (0,-1)
            dx, dy = -dy, dx
            next_x, next_y = x + dx, y + dy

        x, y = next_x, next_y

    # Reverse for inward spiral
    if not inward:
        coords = coords[::-1]

    # Animate
    for x, y in coords:
        set_pixel(x, y, color)
        show()
        sleep(0.03)

    sleep(0.5)
    clear()


# =============================================================================
# RUN ALL ANIMATIONS
# =============================================================================

if __name__ == "__main__":
    print("NeoPixel 8x8 Matrix - Animation Showcase")
    print("=" * 45)
    print("Press Ctrl+C to stop\n")

    # Define some colors
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)
    CYAN = (0, 255, 255)
    PURPLE = (128, 0, 128)

    try:
        while True:
            rainbow_wave(duration=5)
            clear()
            sleep(0.5)

            color_wipe(RED)
            color_wipe((0, 0, 0))  # Wipe off
            sleep(0.5)

            sparkle(WHITE, duration=3)
            clear()
            sleep(0.5)

            breathing(BLUE, cycles=2)
            clear()
            sleep(0.5)

            matrix_rain(duration=5)
            clear()
            sleep(0.5)

            expanding_square(CYAN, cycles=3)
            clear()
            sleep(0.5)

            snake(duration=5)
            clear()
            sleep(0.5)

            fire_effect(duration=5)
            clear()
            sleep(0.5)

            checkerboard(RED, BLUE, flashes=6)
            clear()
            sleep(0.5)

            spiral(GREEN, inward=True)
            spiral(PURPLE, inward=False)

            print("\n--- Restarting animations ---\n")

    except KeyboardInterrupt:
        clear()
        print("\nStopped. All LEDs off.")

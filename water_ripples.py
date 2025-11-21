# Water Ripples Simulation - NeoPixel 8x8 Matrix
# ==============================================
#
# Peaceful water surface with droplets creating
# expanding ripple waves that interfere with each other.
#
# Features:
# - Realistic wave physics
# - Wave interference patterns
# - Random droplets
# - Beautiful color effects
#

from machine import Pin
from neopixel import NeoPixel
from utime import sleep
import math
import random

# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_PIN = 0
WIDTH = 8
HEIGHT = 8
NUM_LEDS = WIDTH * HEIGHT
BRIGHTNESS = 0.4

# Simulation settings
WAVE_SPEED = 0.5       # How fast waves propagate
DAMPING = 0.96         # Wave energy decay (0.9-0.99)
DROP_CHANCE = 0.03     # Chance of new droplet per frame
FRAME_DELAY = 0.03     # Seconds between frames

# Initialize NeoPixel
np = NeoPixel(Pin(DATA_PIN, Pin.OUT), NUM_LEDS)

# =============================================================================
# COLORS
# =============================================================================

# Water color palette (height mapped to color)
def water_color(height):
    """
    Map water height to color.
    Negative = dark blue (trough)
    Zero = medium blue (calm)
    Positive = light blue/white (crest)
    """
    # Normalize height to -1 to 1 range
    h = max(-1, min(1, height / 50))

    if h < 0:
        # Trough - darker blue
        factor = 1 + h  # 0 to 1
        r = int(0 * factor)
        g = int(50 * factor)
        b = int(150 + 50 * factor)
    else:
        # Crest - lighter, more cyan/white
        r = int(100 * h)
        g = int(150 + 100 * h)
        b = int(200 + 55 * h)

    return (r, g, b)


def sunset_water_color(height):
    """Alternative color scheme - sunset reflection."""
    h = max(-1, min(1, height / 50))

    if h < 0:
        # Deep - purple/dark blue
        factor = 1 + h
        r = int(50 * factor)
        g = int(0)
        b = int(100 + 50 * factor)
    else:
        # High - orange/gold
        r = int(150 + 105 * h)
        g = int(80 + 80 * h)
        b = int(50 * (1 - h))

    return (r, g, b)


def neon_water_color(height):
    """Neon/cyberpunk color scheme."""
    h = max(-1, min(1, height / 50))

    # Cycle through neon colors based on height
    if h < -0.3:
        return (int(50 * (1 + h)), 0, int(200 * (1 + h)))  # Purple
    elif h < 0.3:
        return (0, int(200 * (h + 1)), int(150 * (1 - abs(h))))  # Cyan
    else:
        return (int(255 * h), int(100 * h), int(200 * (1 - h)))  # Pink

# =============================================================================
# HELPERS
# =============================================================================

def xy(x, y):
    """Convert x,y to pixel index (serpentine layout)."""
    if y % 2 == 1:
        return y * WIDTH + (WIDTH - 1 - x)
    return y * WIDTH + x

def dim(color):
    """Apply brightness."""
    return tuple(int(c * BRIGHTNESS) for c in color)

def set_pixel(x, y, color):
    """Set pixel at x,y."""
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        np[xy(x, y)] = dim(color)

def clear():
    """Clear display."""
    np.fill((0, 0, 0))
    np.write()

def show():
    """Update display."""
    np.write()

# =============================================================================
# WATER SIMULATION
# =============================================================================

class WaterSimulation:
    """
    Simple wave simulation using height field.
    Each cell has a height and velocity.
    """

    def __init__(self):
        # Current height at each cell
        self.height = [[0.0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        # Velocity (rate of height change) at each cell
        self.velocity = [[0.0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        # Color function
        self.color_func = water_color

    def drop(self, x, y, strength=50):
        """Create a droplet at position."""
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            self.height[y][x] = strength

    def random_drop(self):
        """Create a random droplet."""
        x = random.randint(0, WIDTH - 1)
        y = random.randint(0, HEIGHT - 1)
        strength = random.uniform(30, 60)
        self.drop(x, y, strength)

    def update(self):
        """Update simulation one step."""
        # Calculate new velocities based on height differences
        new_velocity = [[0.0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

        for y in range(HEIGHT):
            for x in range(WIDTH):
                # Get neighboring heights
                neighbors = []

                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                        neighbors.append(self.height[ny][nx])
                    else:
                        # Edge - reflect
                        neighbors.append(self.height[y][x])

                # Average neighbor height
                avg_height = sum(neighbors) / len(neighbors)

                # Accelerate toward average (wave equation)
                acceleration = (avg_height - self.height[y][x]) * WAVE_SPEED

                # Update velocity with damping
                new_velocity[y][x] = (self.velocity[y][x] + acceleration) * DAMPING

        self.velocity = new_velocity

        # Update heights based on velocities
        for y in range(HEIGHT):
            for x in range(WIDTH):
                self.height[y][x] += self.velocity[y][x]

    def draw(self):
        """Draw current water state."""
        for y in range(HEIGHT):
            for x in range(WIDTH):
                color = self.color_func(self.height[y][x])
                set_pixel(x, y, color)
        show()

    def get_max_height(self):
        """Get maximum absolute height (for activity detection)."""
        max_h = 0
        for y in range(HEIGHT):
            for x in range(WIDTH):
                max_h = max(max_h, abs(self.height[y][x]))
        return max_h

# =============================================================================
# ANIMATION MODES
# =============================================================================

def run_random_drops():
    """Random droplets falling continuously."""
    print("Mode: Random Drops")

    sim = WaterSimulation()
    frame = 0

    while True:
        # Random drops
        if random.random() < DROP_CHANCE:
            sim.random_drop()

        sim.update()
        sim.draw()

        frame += 1
        yield  # Allow mode switching

        sleep(FRAME_DELAY)


def run_rain():
    """Heavy rain effect."""
    print("Mode: Rain")

    sim = WaterSimulation()

    while True:
        # Multiple drops per frame
        for _ in range(random.randint(0, 2)):
            if random.random() < 0.3:
                sim.random_drop()

        sim.update()
        sim.draw()

        yield
        sleep(FRAME_DELAY)


def run_center_pulse():
    """Rhythmic pulses from center."""
    print("Mode: Center Pulse")

    sim = WaterSimulation()
    frame = 0

    while True:
        # Pulse every 30 frames
        if frame % 30 == 0:
            sim.drop(WIDTH // 2, HEIGHT // 2, 60)

        sim.update()
        sim.draw()

        frame += 1
        yield
        sleep(FRAME_DELAY)


def run_corner_drops():
    """Drops from alternating corners."""
    print("Mode: Corner Drops")

    sim = WaterSimulation()
    frame = 0
    corners = [(0, 0), (WIDTH-1, 0), (0, HEIGHT-1), (WIDTH-1, HEIGHT-1)]

    while True:
        # Drop from corner every 20 frames
        if frame % 20 == 0:
            corner = corners[(frame // 20) % 4]
            sim.drop(corner[0], corner[1], 50)

        sim.update()
        sim.draw()

        frame += 1
        yield
        sleep(FRAME_DELAY)


def run_wave_machine():
    """Waves generated from one side."""
    print("Mode: Wave Machine")

    sim = WaterSimulation()
    frame = 0

    while True:
        # Generate wave from left side
        if frame % 15 == 0:
            y = random.randint(0, HEIGHT - 1)
            sim.drop(0, y, 40)

        sim.update()
        sim.draw()

        frame += 1
        yield
        sleep(FRAME_DELAY)


def run_interference():
    """Two sources creating interference pattern."""
    print("Mode: Interference Pattern")

    sim = WaterSimulation()
    frame = 0

    while True:
        # Two synchronized sources
        if frame % 20 == 0:
            sim.drop(1, HEIGHT // 2, 40)
            sim.drop(WIDTH - 2, HEIGHT // 2, 40)

        sim.update()
        sim.draw()

        frame += 1
        yield
        sleep(FRAME_DELAY)


def run_sunset():
    """Sunset color scheme."""
    print("Mode: Sunset Waters")

    sim = WaterSimulation()
    sim.color_func = sunset_water_color
    frame = 0

    while True:
        if random.random() < DROP_CHANCE:
            sim.random_drop()

        sim.update()
        sim.draw()

        frame += 1
        yield
        sleep(FRAME_DELAY)


def run_neon():
    """Neon/cyberpunk color scheme."""
    print("Mode: Neon Pool")

    sim = WaterSimulation()
    sim.color_func = neon_water_color
    frame = 0

    while True:
        if random.random() < DROP_CHANCE * 1.5:
            sim.random_drop()

        sim.update()
        sim.draw()

        frame += 1
        yield
        sleep(FRAME_DELAY)

# =============================================================================
# MAIN
# =============================================================================

def run_water_ripples():
    """Main function - cycles through all modes."""
    print("=" * 50)
    print("  Water Ripples Simulation")
    print("=" * 50)
    print("\nModes: Random, Rain, Pulse, Corners, Waves, Interference")
    print("Press Ctrl+C to stop\n")

    modes = [
        run_random_drops,
        run_rain,
        run_center_pulse,
        run_corner_drops,
        run_wave_machine,
        run_interference,
        run_sunset,
        run_neon,
    ]

    try:
        while True:
            for mode_func in modes:
                mode = mode_func()

                # Run each mode for ~200 frames
                for _ in range(200):
                    next(mode)

                print("\nSwitching mode...\n")
                sleep(0.5)

    except KeyboardInterrupt:
        clear()
        print("\nWater simulation ended.")


def run_endless(mode='random'):
    """Run a single mode endlessly."""
    modes = {
        'random': run_random_drops,
        'rain': run_rain,
        'pulse': run_center_pulse,
        'corners': run_corner_drops,
        'waves': run_wave_machine,
        'interference': run_interference,
        'sunset': run_sunset,
        'neon': run_neon,
    }

    if mode not in modes:
        print(f"Unknown mode: {mode}")
        print(f"Available: {list(modes.keys())}")
        return

    print(f"Running '{mode}' mode endlessly...")
    mode_gen = modes[mode]()

    try:
        while True:
            next(mode_gen)
    except KeyboardInterrupt:
        clear()
        print("\nStopped.")


if __name__ == "__main__":
    run_water_ripples()

    # Or run a specific mode:
    # run_endless('neon')
    # run_endless('interference')

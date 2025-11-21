# Sand/Particle Simulation - NeoPixel 8x8 Matrix
# ===============================================
#
# Watch sand grains fall and pile up realistically!
# Particles obey gravity and slide off each other.
#
# Features:
# - Realistic particle physics
# - Multiple sand colors
# - Particles pile up naturally
# - Random spawning at top
#

from machine import Pin
from neopixel import NeoPixel
from utime import sleep
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
SPAWN_RATE = 0.3         # Chance to spawn new grain each frame
SIMULATION_SPEED = 0.08  # Seconds between frames
MAX_GRAINS = 50          # Maximum grains before reset

# Initialize NeoPixel
np = NeoPixel(Pin(DATA_PIN, Pin.OUT), NUM_LEDS)

# =============================================================================
# COLORS - Different sand types
# =============================================================================

SAND_COLORS = [
    (194, 178, 128),  # Classic sand
    (210, 180, 140),  # Tan
    (139, 119, 101),  # Dark sand
    (255, 200, 100),  # Golden sand
    (180, 140, 100),  # Brown sand
]

BACKGROUND = (0, 0, 0)

# Special colored sand modes
RAINBOW_MODE = False
LAYERED_MODE = True  # Different colors create layers

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

def wheel(pos):
    """Rainbow color wheel."""
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
# SAND PARTICLE
# =============================================================================

class SandGrain:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.settled = False

# =============================================================================
# SAND SIMULATION
# =============================================================================

class SandSimulation:
    def __init__(self):
        self.grains = []
        self.grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.grain_count = 0
        self.color_index = 0

    def reset(self):
        """Reset simulation."""
        self.grains = []
        self.grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.grain_count = 0
        print("\nSimulation reset!")

    def spawn_grain(self):
        """Spawn a new grain at random position at top."""
        # Find empty spot at top
        empty_spots = [x for x in range(WIDTH) if self.grid[0][x] is None]

        if not empty_spots:
            return  # Top row full

        x = random.choice(empty_spots)

        # Choose color
        if RAINBOW_MODE:
            color = wheel(self.grain_count * 10)
        elif LAYERED_MODE:
            # Change color periodically for layered effect
            color = SAND_COLORS[self.color_index % len(SAND_COLORS)]
            if self.grain_count % 8 == 0:
                self.color_index += 1
        else:
            color = random.choice(SAND_COLORS)

        grain = SandGrain(x, 0, color)
        self.grains.append(grain)
        self.grid[0][x] = grain
        self.grain_count += 1

    def update(self):
        """Update all grain positions."""
        # Process grains from bottom to top so lower grains move first
        grains_by_y = sorted(self.grains, key=lambda g: -g.y)

        for grain in grains_by_y:
            if grain.settled:
                continue

            x, y = grain.x, grain.y

            # Try to fall straight down
            if y + 1 < HEIGHT and self.grid[y + 1][x] is None:
                self.move_grain(grain, x, y + 1)

            # Try to slide diagonally
            elif y + 1 < HEIGHT:
                # Randomly choose left or right first for natural look
                if random.randint(0, 1):
                    directions = [-1, 1]
                else:
                    directions = [1, -1]

                moved = False
                for dx in directions:
                    new_x = x + dx
                    if (0 <= new_x < WIDTH and
                        self.grid[y + 1][new_x] is None):
                        self.move_grain(grain, new_x, y + 1)
                        moved = True
                        break

                if not moved:
                    # Can't move - settle
                    grain.settled = True

            else:
                # At bottom - settle
                grain.settled = True

    def move_grain(self, grain, new_x, new_y):
        """Move grain to new position."""
        # Clear old position
        self.grid[grain.y][grain.x] = None

        # Set new position
        grain.x = new_x
        grain.y = new_y
        self.grid[new_y][new_x] = grain

    def is_full(self):
        """Check if simulation area is full."""
        # Full if top row has settled grains
        return all(self.grid[0][x] is not None and
                   self.grid[0][x].settled for x in range(WIDTH))

    def count_active(self):
        """Count non-settled grains."""
        return sum(1 for g in self.grains if not g.settled)

    def draw(self):
        """Draw current state."""
        np.fill((0, 0, 0))

        for grain in self.grains:
            set_pixel(grain.x, grain.y, grain.color)

        show()

# =============================================================================
# ANIMATION MODES
# =============================================================================

def run_continuous():
    """Run continuous sand simulation with auto-reset."""
    print("=" * 50)
    print("  Sand Simulation - Continuous Mode")
    print("=" * 50)
    print("\nWatch sand fall and pile up!")
    print("Press Ctrl+C to stop\n")

    sim = SandSimulation()
    frame = 0

    try:
        while True:
            # Spawn new grains
            if (random.random() < SPAWN_RATE and
                sim.grain_count < MAX_GRAINS and
                not sim.is_full()):
                sim.spawn_grain()

            # Update physics
            sim.update()

            # Draw
            sim.draw()

            # Status
            active = sim.count_active()
            print(f"\rGrains: {sim.grain_count:3d} | Active: {active:2d} | Frame: {frame:5d}", end="")

            # Check for reset
            if sim.is_full() or sim.grain_count >= MAX_GRAINS:
                print("\n\nPile complete! Resetting...")
                sleep(2)

                # Collapse animation
                for _ in range(HEIGHT):
                    for y in range(HEIGHT - 1, 0, -1):
                        for x in range(WIDTH):
                            if sim.grid[y-1][x]:
                                set_pixel(x, y-1, (0, 0, 0))
                    show()
                    sleep(0.1)

                sim.reset()
                sleep(0.5)

            frame += 1
            sleep(SIMULATION_SPEED)

    except KeyboardInterrupt:
        clear()
        print(f"\n\nStopped after {frame} frames, {sim.grain_count} grains.")

def run_hourglass():
    """Hourglass effect - sand falls, then flips."""
    print("=" * 50)
    print("  Sand Simulation - Hourglass Mode")
    print("=" * 50)

    sim = SandSimulation()

    try:
        while True:
            # Fill from top
            print("\nFilling...")
            while not sim.is_full() and sim.grain_count < MAX_GRAINS:
                if random.random() < 0.5:
                    sim.spawn_grain()
                sim.update()
                sim.draw()
                sleep(SIMULATION_SPEED)

            print("Full! Waiting...")
            sleep(2)

            # "Flip" - invert colors briefly then reset
            print("Flipping hourglass...")
            for _ in range(5):
                np.fill(dim((50, 40, 30)))
                show()
                sleep(0.1)
                clear()
                sleep(0.1)

            sim.reset()
            sleep(0.5)

    except KeyboardInterrupt:
        clear()
        print("\nHourglass stopped.")

def run_waterfall():
    """Continuous waterfall from one side."""
    print("=" * 50)
    print("  Sand Simulation - Waterfall Mode")
    print("=" * 50)

    sim = SandSimulation()
    frame = 0

    try:
        while True:
            # Always spawn at left side
            if sim.grid[0][0] is None:
                color = wheel(frame * 2)
                grain = SandGrain(0, 0, color)
                sim.grains.append(grain)
                sim.grid[0][0] = grain
                sim.grain_count += 1

            # Remove grains that reach right side at bottom
            for grain in sim.grains[:]:
                if grain.x == WIDTH - 1 and grain.y == HEIGHT - 1:
                    sim.grid[grain.y][grain.x] = None
                    sim.grains.remove(grain)

            sim.update()
            sim.draw()

            frame += 1
            sleep(SIMULATION_SPEED * 0.7)

    except KeyboardInterrupt:
        clear()
        print("\nWaterfall stopped.")

# =============================================================================
# MAIN
# =============================================================================

def run_sand_simulation():
    """Main entry point - cycles through modes."""
    modes = [
        ("Continuous", run_continuous),
    ]

    print("Sand Simulation Starting...")
    print("Press Ctrl+C to stop\n")

    try:
        run_continuous()
    except KeyboardInterrupt:
        clear()
        print("\nSimulation ended.")

if __name__ == "__main__":
    run_sand_simulation()

    # Alternative modes:
    # run_hourglass()
    # run_waterfall()

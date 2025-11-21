# Conway's Game of Life - NeoPixel 8x8 Matrix
# ============================================
#
# The classic cellular automaton simulation on your LED matrix!
#
# RULES:
# 1. Any live cell with 2 or 3 neighbors survives
# 2. Any dead cell with exactly 3 neighbors becomes alive
# 3. All other cells die or stay dead
#
# The grid wraps around (toroidal topology) so patterns can travel
# across edges and reappear on the opposite side.
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
BRIGHTNESS = 0.3

# Animation settings
GENERATION_DELAY = 0.15  # Seconds between generations
MAX_GENERATIONS = 200    # Auto-reset after this many generations
STAGNATION_CHECK = 10    # Reset if pattern unchanged for this many generations

# Initialize NeoPixel
np = NeoPixel(Pin(DATA_PIN, Pin.OUT), NUM_LEDS)

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
    """Rainbow color wheel (0-255)."""
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
# GAME OF LIFE ENGINE
# =============================================================================

class GameOfLife:
    def __init__(self):
        self.grid = [[0] * WIDTH for _ in range(HEIGHT)]
        self.generation = 0
        self.population = 0
        self.history = []  # Track recent states for stagnation detection

    def randomize(self, density=0.4):
        """Fill grid with random cells."""
        self.grid = [[1 if random.random() < density else 0
                      for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.generation = 0
        self.history = []
        print(f"New random pattern (density: {int(density*100)}%)")

    def load_pattern(self, pattern, offset_x=0, offset_y=0):
        """Load a predefined pattern onto the grid."""
        self.grid = [[0] * WIDTH for _ in range(HEIGHT)]
        for y, row in enumerate(pattern):
            for x, cell in enumerate(row):
                px = (x + offset_x) % WIDTH
                py = (y + offset_y) % HEIGHT
                self.grid[py][px] = cell
        self.generation = 0
        self.history = []

    def count_neighbors(self, x, y):
        """Count live neighbors (toroidal wrap)."""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % WIDTH
                ny = (y + dy) % HEIGHT
                count += self.grid[ny][nx]
        return count

    def step(self):
        """Advance one generation."""
        new_grid = [[0] * WIDTH for _ in range(HEIGHT)]
        self.population = 0

        for y in range(HEIGHT):
            for x in range(WIDTH):
                neighbors = self.count_neighbors(x, y)
                alive = self.grid[y][x]

                # Apply rules
                if alive:
                    # Live cell survives with 2 or 3 neighbors
                    new_grid[y][x] = 1 if neighbors in [2, 3] else 0
                else:
                    # Dead cell becomes alive with exactly 3 neighbors
                    new_grid[y][x] = 1 if neighbors == 3 else 0

                self.population += new_grid[y][x]

        self.grid = new_grid
        self.generation += 1

        # Track history for stagnation detection
        state = tuple(tuple(row) for row in self.grid)
        self.history.append(state)
        if len(self.history) > STAGNATION_CHECK:
            self.history.pop(0)

    def is_stagnant(self):
        """Check if pattern has stopped changing."""
        if len(self.history) < STAGNATION_CHECK:
            return False
        # Check if current state matches any recent state
        current = self.history[-1]
        return self.history.count(current) >= 3

    def is_dead(self):
        """Check if all cells are dead."""
        return self.population == 0

# =============================================================================
# CLASSIC PATTERNS
# =============================================================================

# Glider - moves diagonally
GLIDER = [
    [0, 1, 0],
    [0, 0, 1],
    [1, 1, 1],
]

# Blinker - oscillates (period 2)
BLINKER = [
    [1, 1, 1],
]

# Toad - oscillates (period 2)
TOAD = [
    [0, 1, 1, 1],
    [1, 1, 1, 0],
]

# Beacon - oscillates (period 2)
BEACON = [
    [1, 1, 0, 0],
    [1, 1, 0, 0],
    [0, 0, 1, 1],
    [0, 0, 1, 1],
]

# Pulsar fragment (simplified for 8x8)
PULSAR_MINI = [
    [0, 1, 1, 1],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
    [1, 0, 0, 0],
]

# R-pentomino - chaotic, long-lived
R_PENTOMINO = [
    [0, 1, 1],
    [1, 1, 0],
    [0, 1, 0],
]

# Diehard - dies after 130 generations
DIEHARD = [
    [0, 0, 0, 0, 0, 0, 1, 0],
    [1, 1, 0, 0, 0, 0, 0, 0],
    [0, 1, 0, 0, 0, 1, 1, 1],
]

# Acorn - takes 5206 generations to stabilize (will wrap on 8x8)
ACORN = [
    [0, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [1, 1, 0, 0, 1, 1, 1],
]

# Block - stable (still life)
BLOCK = [
    [1, 1],
    [1, 1],
]

# Beehive - stable (still life)
BEEHIVE = [
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [0, 1, 1, 0],
]

# Glider gun fragment (simplified)
GLIDER_GUN_MINI = [
    [0, 0, 0, 1, 1, 0],
    [0, 0, 1, 0, 0, 1],
    [1, 1, 0, 0, 0, 1],
    [1, 1, 0, 0, 1, 0],
    [0, 0, 1, 1, 0, 0],
]

# Two gliders collision
TWO_GLIDERS = [
    [0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0],
]

PATTERNS = {
    'glider': (GLIDER, 0, 0),
    'blinker': (BLINKER, 2, 3),
    'toad': (TOAD, 2, 3),
    'beacon': (BEACON, 2, 2),
    'r_pentomino': (R_PENTOMINO, 2, 2),
    'diehard': (DIEHARD, 0, 2),
    'acorn': (ACORN, 0, 2),
    'block': (BLOCK, 3, 3),
    'beehive': (BEEHIVE, 2, 3),
    'two_gliders': (TWO_GLIDERS, 0, 0),
}

# =============================================================================
# DISPLAY MODES
# =============================================================================

def display_classic(game):
    """Classic green on black display."""
    np.fill((0, 0, 0))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if game.grid[y][x]:
                set_pixel(x, y, (0, 255, 0))
    show()

def display_rainbow(game):
    """Color based on generation."""
    np.fill((0, 0, 0))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if game.grid[y][x]:
                color = wheel((game.generation * 3 + x * 10 + y * 10) % 256)
                set_pixel(x, y, color)
    show()

def display_heat(game):
    """Warmer colors for cells with more neighbors."""
    np.fill((0, 0, 0))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if game.grid[y][x]:
                neighbors = game.count_neighbors(x, y)
                # More neighbors = warmer color
                if neighbors <= 1:
                    color = (0, 0, 255)      # Blue - lonely
                elif neighbors == 2:
                    color = (0, 255, 0)      # Green - stable
                elif neighbors == 3:
                    color = (255, 255, 0)    # Yellow - thriving
                else:
                    color = (255, 0, 0)      # Red - overcrowded (will die)
                set_pixel(x, y, color)
    show()

def display_age(game, ages):
    """Color based on how long cell has been alive."""
    np.fill((0, 0, 0))
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if game.grid[y][x]:
                age = ages[y][x]
                # Young cells are bright, old cells fade to different colors
                if age < 3:
                    color = (255, 255, 255)  # White - newborn
                elif age < 6:
                    color = (0, 255, 255)    # Cyan - young
                elif age < 10:
                    color = (0, 255, 0)      # Green - mature
                elif age < 20:
                    color = (255, 255, 0)    # Yellow - old
                else:
                    color = (255, 100, 0)    # Orange - ancient
                set_pixel(x, y, color)
    show()

DISPLAY_MODES = [
    ('Classic Green', display_classic),
    ('Rainbow', display_rainbow),
    ('Heat Map', display_heat),
]

# =============================================================================
# MAIN ANIMATION
# =============================================================================

def run_game_of_life():
    """Main game loop."""
    print("=" * 50)
    print("  Conway's Game of Life - NeoPixel Edition")
    print("=" * 50)
    print("\nRules:")
    print("  - Live cell with 2-3 neighbors survives")
    print("  - Dead cell with 3 neighbors becomes alive")
    print("  - All others die")
    print("\nPress Ctrl+C to stop\n")

    game = GameOfLife()
    pattern_names = list(PATTERNS.keys())
    pattern_index = 0
    display_mode = 0

    # Track cell ages for age display mode
    ages = [[0] * WIDTH for _ in range(HEIGHT)]

    # Start with a classic pattern
    pattern, ox, oy = PATTERNS[pattern_names[pattern_index]]
    game.load_pattern(pattern, ox, oy)
    print(f"Pattern: {pattern_names[pattern_index]}")

    try:
        while True:
            # Display current state
            if display_mode < len(DISPLAY_MODES):
                _, display_func = DISPLAY_MODES[display_mode]
                if display_func == display_heat:
                    display_heat(game)
                else:
                    display_func(game)
            else:
                display_age(game, ages)

            # Update ages
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    if game.grid[y][x]:
                        ages[y][x] += 1
                    else:
                        ages[y][x] = 0

            # Print status
            print(f"\rGen: {game.generation:4d} | Pop: {game.population:2d} | Mode: {display_mode+1}/4", end="")

            # Check for reset conditions
            should_reset = (
                game.is_dead() or
                game.is_stagnant() or
                game.generation >= MAX_GENERATIONS
            )

            if should_reset:
                reason = "extinct" if game.is_dead() else "stagnant" if game.is_stagnant() else "max gen"
                print(f"\n\nPattern {reason}! Loading next pattern...")
                sleep(1)

                # Cycle to next pattern or random
                pattern_index = (pattern_index + 1) % (len(pattern_names) + 1)

                if pattern_index < len(pattern_names):
                    pattern, ox, oy = PATTERNS[pattern_names[pattern_index]]
                    game.load_pattern(pattern, ox, oy)
                    print(f"Pattern: {pattern_names[pattern_index]}")
                else:
                    game.randomize(random.uniform(0.25, 0.5))

                # Cycle display mode
                display_mode = (display_mode + 1) % 4

                # Reset ages
                ages = [[0] * WIDTH for _ in range(HEIGHT)]

                sleep(0.5)
                continue

            # Advance simulation
            game.step()
            sleep(GENERATION_DELAY)

    except KeyboardInterrupt:
        clear()
        print("\n\nGame stopped. Final stats:")
        print(f"  Generations: {game.generation}")
        print(f"  Final population: {game.population}")

# =============================================================================
# QUICK DEMO - Run specific pattern
# =============================================================================

def demo_pattern(name, generations=50, display='rainbow'):
    """Run a specific pattern for demo purposes."""
    if name not in PATTERNS:
        print(f"Unknown pattern: {name}")
        print(f"Available: {list(PATTERNS.keys())}")
        return

    game = GameOfLife()
    pattern, ox, oy = PATTERNS[name]
    game.load_pattern(pattern, ox, oy)
    print(f"Running '{name}' for {generations} generations...")

    display_funcs = {
        'classic': display_classic,
        'rainbow': display_rainbow,
        'heat': display_heat,
    }
    display_func = display_funcs.get(display, display_rainbow)

    for _ in range(generations):
        display_func(game)
        game.step()
        sleep(GENERATION_DELAY)

    clear()
    print("Demo complete!")

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    run_game_of_life()

    # Or run a specific pattern:
    demo_pattern('glider', generations=100)
    #demo_pattern('r_pentomino', generations=150, display='heat')

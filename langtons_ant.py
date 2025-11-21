# Langton's Ant - Cellular Automaton on NeoPixel 8x8 Matrix
# =========================================================
#
# A simple ant follows two rules, yet creates surprisingly
# complex and beautiful patterns!
#
# RULES:
# 1. On a WHITE cell: turn 90° RIGHT, flip color, move forward
# 2. On a BLACK cell: turn 90° LEFT, flip color, move forward
#
# Despite these simple rules, the ant creates chaotic patterns
# before eventually building a "highway" - a repeating pattern
# that moves diagonally forever.
#
# On an 8x8 grid with wrapping, the ant creates mesmerizing
# cycling patterns!
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
STEP_DELAY = 0.08     # Seconds between steps
TRAIL_FADE = True     # Cells fade over time
WRAP_EDGES = True     # Ant wraps around edges (toroidal)
MULTI_ANT = False     # Multiple ants mode

# Initialize NeoPixel
np = NeoPixel(Pin(DATA_PIN, Pin.OUT), NUM_LEDS)

# =============================================================================
# COLORS
# =============================================================================

# Classic mode
WHITE_CELL = (200, 200, 200)
BLACK_CELL = (0, 0, 0)
ANT_COLOR = (255, 0, 0)

# Rainbow mode colors (for extended ruleset)
COLORS = [
    (0, 0, 0),        # Black (0)
    (255, 0, 0),      # Red (1)
    (255, 165, 0),    # Orange (2)
    (255, 255, 0),    # Yellow (3)
    (0, 255, 0),      # Green (4)
    (0, 255, 255),    # Cyan (5)
    (0, 0, 255),      # Blue (6)
    (255, 0, 255),    # Magenta (7)
]

# =============================================================================
# HELPERS
# =============================================================================

def xy(x, y):
    """Convert x,y to pixel index (serpentine layout)."""
    if y % 2 == 1:
        return y * WIDTH + (WIDTH - 1 - x)
    return y * WIDTH + x

def dim(color, factor=1.0):
    """Apply brightness."""
    return tuple(int(c * BRIGHTNESS * factor) for c in color)

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
# DIRECTIONS
# =============================================================================

# Direction vectors: UP, RIGHT, DOWN, LEFT
DIRECTIONS = [(0, -1), (1, 0), (0, 1), (-1, 0)]
DIR_NAMES = ['UP', 'RIGHT', 'DOWN', 'LEFT']

def turn_right(direction):
    """Turn 90 degrees clockwise."""
    return (direction + 1) % 4

def turn_left(direction):
    """Turn 90 degrees counter-clockwise."""
    return (direction - 1) % 4

# =============================================================================
# LANGTON'S ANT
# =============================================================================

class Ant:
    """A single Langton's Ant."""

    def __init__(self, x, y, direction=0, color=ANT_COLOR):
        self.x = x
        self.y = y
        self.direction = direction  # 0=UP, 1=RIGHT, 2=DOWN, 3=LEFT
        self.color = color
        self.steps = 0

    def move(self):
        """Move forward one cell."""
        dx, dy = DIRECTIONS[self.direction]
        self.x += dx
        self.y += dy

        # Wrap around edges
        if WRAP_EDGES:
            self.x = self.x % WIDTH
            self.y = self.y % HEIGHT
        else:
            # Bounce off walls
            if self.x < 0:
                self.x = 0
                self.direction = turn_right(turn_right(self.direction))
            elif self.x >= WIDTH:
                self.x = WIDTH - 1
                self.direction = turn_right(turn_right(self.direction))
            if self.y < 0:
                self.y = 0
                self.direction = turn_right(turn_right(self.direction))
            elif self.y >= HEIGHT:
                self.y = HEIGHT - 1
                self.direction = turn_right(turn_right(self.direction))

        self.steps += 1


class LangtonAnt:
    """Classic Langton's Ant simulation."""

    def __init__(self):
        self.grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.ant = Ant(WIDTH // 2, HEIGHT // 2)
        self.history = []  # For pattern detection

    def reset(self, random_start=False):
        """Reset simulation."""
        self.grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

        if random_start:
            # Random starting position and direction
            self.ant = Ant(
                random.randint(0, WIDTH - 1),
                random.randint(0, HEIGHT - 1),
                random.randint(0, 3)
            )
            # Optionally randomize some cells
            for _ in range(random.randint(0, 10)):
                x = random.randint(0, WIDTH - 1)
                y = random.randint(0, HEIGHT - 1)
                self.grid[y][x] = 1
        else:
            self.ant = Ant(WIDTH // 2, HEIGHT // 2)

        self.history = []

    def step(self):
        """Execute one step of the simulation."""
        x, y = self.ant.x, self.ant.y

        # Get current cell state
        cell = self.grid[y][x]

        # Apply rules
        if cell == 0:  # White/off cell
            self.ant.direction = turn_right(self.ant.direction)
            self.grid[y][x] = 1  # Flip to black/on
        else:  # Black/on cell
            self.ant.direction = turn_left(self.ant.direction)
            self.grid[y][x] = 0  # Flip to white/off

        # Move forward
        self.ant.move()

        # Track state for pattern detection
        state = (self.ant.x, self.ant.y, self.ant.direction, tuple(tuple(row) for row in self.grid))
        self.history.append(hash(state))
        if len(self.history) > 500:
            self.history.pop(0)

    def is_cycling(self):
        """Check if pattern is repeating."""
        if len(self.history) < 100:
            return False
        # Check if recent state matches earlier state
        recent = self.history[-50:]
        for i in range(len(self.history) - 100):
            if self.history[i:i+50] == recent:
                return True
        return False

    def draw(self, color_mode='classic'):
        """Draw current state."""
        np.fill((0, 0, 0))

        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.grid[y][x] == 1:
                    if color_mode == 'classic':
                        color = WHITE_CELL
                    elif color_mode == 'rainbow':
                        color = wheel((x * 30 + y * 30 + self.ant.steps) % 256)
                    elif color_mode == 'heat':
                        # Older cells are cooler colors
                        color = wheel((self.ant.steps - x * 10 - y * 10) % 256)
                    else:
                        color = WHITE_CELL
                    set_pixel(x, y, color)

        # Draw ant
        set_pixel(self.ant.x, self.ant.y, self.ant.color)

        show()


# =============================================================================
# EXTENDED LANGTON'S ANT (Multiple Colors)
# =============================================================================

class ExtendedAnt:
    """
    Extended Langton's Ant with multiple colors and custom rules.

    Rules are specified as a string like "RL" (classic) or "LLRR" (4 colors).
    R = turn right, L = turn left
    """

    def __init__(self, rules="RL"):
        self.rules = rules  # e.g., "RL", "LLRR", "LRRRRRLLR"
        self.num_states = len(rules)
        self.grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.ant = Ant(WIDTH // 2, HEIGHT // 2)

    def reset(self):
        """Reset simulation."""
        self.grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.ant = Ant(WIDTH // 2, HEIGHT // 2)

    def step(self):
        """Execute one step."""
        x, y = self.ant.x, self.ant.y
        state = self.grid[y][x]

        # Apply rule for current state
        rule = self.rules[state]
        if rule == 'R':
            self.ant.direction = turn_right(self.ant.direction)
        else:  # 'L'
            self.ant.direction = turn_left(self.ant.direction)

        # Cycle to next state
        self.grid[y][x] = (state + 1) % self.num_states

        # Move
        self.ant.move()

    def draw(self):
        """Draw with multiple colors."""
        np.fill((0, 0, 0))

        for y in range(HEIGHT):
            for x in range(WIDTH):
                state = self.grid[y][x]
                if state > 0:
                    color = COLORS[state % len(COLORS)]
                    set_pixel(x, y, color)

        # Draw ant
        set_pixel(self.ant.x, self.ant.y, ANT_COLOR)

        show()


# =============================================================================
# MULTIPLE ANTS
# =============================================================================

class MultiAnt:
    """Multiple ants interacting on the same grid."""

    def __init__(self, num_ants=2):
        self.grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.ants = []

        # Create ants with different colors
        ant_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
        ]

        for i in range(num_ants):
            x = random.randint(0, WIDTH - 1)
            y = random.randint(0, HEIGHT - 1)
            direction = random.randint(0, 3)
            color = ant_colors[i % len(ant_colors)]
            self.ants.append(Ant(x, y, direction, color))

    def step(self):
        """All ants take one step."""
        for ant in self.ants:
            x, y = ant.x, ant.y
            cell = self.grid[y][x]

            if cell == 0:
                ant.direction = turn_right(ant.direction)
                self.grid[y][x] = 1
            else:
                ant.direction = turn_left(ant.direction)
                self.grid[y][x] = 0

            ant.move()

    def draw(self):
        """Draw grid and all ants."""
        np.fill((0, 0, 0))

        # Draw grid
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.grid[y][x] == 1:
                    set_pixel(x, y, (100, 100, 100))

        # Draw ants (on top)
        for ant in self.ants:
            set_pixel(ant.x, ant.y, ant.color)

        show()


# =============================================================================
# ANIMATION MODES
# =============================================================================

def run_classic():
    """Classic Langton's Ant."""
    print("Mode: Classic Langton's Ant")

    sim = LangtonAnt()

    while True:
        sim.step()
        sim.draw('classic')
        print(f"\rSteps: {sim.ant.steps:6d}", end="")

        if sim.ant.steps > 2000:
            print("\nRestarting with random configuration...")
            sim.reset(random_start=True)
            sleep(0.5)

        yield
        sleep(STEP_DELAY)


def run_rainbow():
    """Rainbow colored trail."""
    print("Mode: Rainbow Ant")

    sim = LangtonAnt()

    while True:
        sim.step()
        sim.draw('rainbow')

        if sim.ant.steps > 2000:
            sim.reset(random_start=True)

        yield
        sleep(STEP_DELAY)


def run_extended(rules="LLRR"):
    """Extended ruleset with multiple colors."""
    print(f"Mode: Extended Ant (rules: {rules})")

    sim = ExtendedAnt(rules)

    while True:
        sim.step()
        sim.draw()

        if sim.ant.steps > 2000:
            sim.reset()

        yield
        sleep(STEP_DELAY)


def run_multi_ant(num_ants=2):
    """Multiple ants."""
    print(f"Mode: {num_ants} Ants")

    sim = MultiAnt(num_ants)
    steps = 0

    while True:
        sim.step()
        sim.draw()
        steps += 1

        if steps > 2000:
            sim = MultiAnt(num_ants)
            steps = 0

        yield
        sleep(STEP_DELAY)


def run_chaos():
    """Chaotic mode - random rule changes."""
    print("Mode: Chaos (random rules)")

    rules_list = ["RL", "RLR", "LLRR", "LRRL", "RRLLLRLLLRRR", "LLRRRLRLRLLR"]
    rule_index = 0

    sim = ExtendedAnt(rules_list[rule_index])

    while True:
        sim.step()
        sim.draw()

        # Change rules periodically
        if sim.ant.steps > 500:
            rule_index = (rule_index + 1) % len(rules_list)
            print(f"\nNew rules: {rules_list[rule_index]}")
            sim = ExtendedAnt(rules_list[rule_index])

        yield
        sleep(STEP_DELAY)


# =============================================================================
# MAIN
# =============================================================================

def run_langtons_ant():
    """Main function - cycles through modes."""
    print("=" * 50)
    print("  Langton's Ant - Cellular Automaton")
    print("=" * 50)
    print("\nRules:")
    print("  On WHITE: turn RIGHT, flip color, move")
    print("  On BLACK: turn LEFT, flip color, move")
    print("\nPress Ctrl+C to stop\n")

    modes = [
        ('Classic', run_classic),
        ('Rainbow', run_rainbow),
        ('Extended LLRR', lambda: run_extended("LLRR")),
        ('Extended LRRL', lambda: run_extended("LRRL")),
        ('Two Ants', lambda: run_multi_ant(2)),
        ('Three Ants', lambda: run_multi_ant(3)),
        ('Chaos', run_chaos),
    ]

    try:
        while True:
            for name, mode_func in modes:
                print(f"\n--- {name} ---")
                mode = mode_func()

                # Run each mode for ~1000 steps
                for _ in range(1000):
                    next(mode)

                print("\nSwitching mode...")
                sleep(0.5)

    except KeyboardInterrupt:
        clear()
        print("\n\nAnt simulation ended.")


if __name__ == "__main__":
    run_langtons_ant()

    # Or run specific modes:
    # Run classic forever:
    # sim = LangtonAnt()
    # while True:
    #     sim.step()
    #     sim.draw()
    #     sleep(STEP_DELAY)

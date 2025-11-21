# Hourglass Simulation - NeoPixel 8x8 Matrix at 45 Degrees
# ========================================================
#
# Mount your 8x8 matrix rotated 45 degrees (diamond shape)
# and watch sand flow through an hourglass!
#
#        *           <- Top chamber
#       ***
#      *****
#       * *         <- Neck (narrow passage)
#      *****
#       ***
#        *          <- Bottom chamber
#
# The simulation assumes gravity pulls toward the bottom corner.
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
FRAME_DELAY = 0.06      # Seconds between frames
GRAIN_DROP_DELAY = 8    # Frames between grains passing through neck
SAND_COUNT = 20         # Number of sand grains

# Initialize NeoPixel
np = NeoPixel(Pin(DATA_PIN, Pin.OUT), NUM_LEDS)

# =============================================================================
# COLORS
# =============================================================================

SAND_COLOR = (255, 200, 100)     # Golden sand
SAND_DARK = (180, 140, 70)       # Darker sand variation
GLASS_COLOR = (40, 60, 80)       # Subtle blue glass outline
BACKGROUND = (0, 0, 0)           # Black

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

# =============================================================================
# HOURGLASS SHAPE DEFINITION
# =============================================================================

# Define the hourglass shape as a diamond with a neck in the middle
# When rotated 45°, this creates the classic hourglass look

def in_hourglass(x, y):
    """
    Check if position is inside the hourglass shape.
    The hourglass is diamond-shaped with a narrow neck at center.
    """
    cx, cy = 3.5, 3.5  # Center

    # Distance from center (Manhattan distance for diamond shape)
    dx = abs(x - cx)
    dy = abs(y - cy)

    # Top half (y < 4): diamond expands as you go up from center
    if y < 4:
        # Narrow at center (y=3), wide at top (y=0)
        # At y=3: allow x from 3-4 (width 2) - the neck
        # At y=0: allow x from 0-7 (width 8)
        max_dx = (4 - y) + 0.5  # Expands toward top
        if y >= 3:  # Neck area
            max_dx = 1.0  # Very narrow
        return dx <= max_dx

    # Bottom half (y >= 4): diamond expands as you go down from center
    else:
        # Narrow at center (y=4), wide at bottom (y=7)
        max_dx = (y - 3) + 0.5  # Expands toward bottom
        if y <= 4:  # Neck area
            max_dx = 1.0  # Very narrow
        return dx <= max_dx


def is_neck(x, y):
    """Check if position is in the narrow neck."""
    return y in [3, 4] and x in [3, 4]


def get_hourglass_cells():
    """Get all cells that are inside the hourglass."""
    cells = []
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if in_hourglass(x, y):
                cells.append((x, y))
    return cells


def get_top_chamber():
    """Get cells in top chamber (above neck)."""
    return [(x, y) for x, y in get_hourglass_cells() if y < 3]


def get_bottom_chamber():
    """Get cells in bottom chamber (below neck)."""
    return [(x, y) for x, y in get_hourglass_cells() if y > 4]


def get_neck_cells():
    """Get the neck cells."""
    return [(x, y) for x, y in get_hourglass_cells() if y in [3, 4]]

# =============================================================================
# SAND GRAIN
# =============================================================================

class SandGrain:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.settled = False
        # Slight color variation
        variation = random.randint(-20, 20)
        self.color = (
            max(0, min(255, SAND_COLOR[0] + variation)),
            max(0, min(255, SAND_COLOR[1] + variation)),
            max(0, min(255, SAND_COLOR[2] + variation))
        )

# =============================================================================
# HOURGLASS SIMULATION
# =============================================================================

class Hourglass:
    def __init__(self):
        self.grains = []
        self.grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.frame = 0
        self.flipped = False  # Which way gravity goes
        self.fill_top()

    def fill_top(self):
        """Fill top chamber with sand."""
        self.grains = []
        self.grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]

        top_cells = get_top_chamber()
        random.shuffle(top_cells) if hasattr(random, 'shuffle') else None

        # Fill top chamber
        for i, (x, y) in enumerate(top_cells):
            if i >= SAND_COUNT:
                break
            grain = SandGrain(x, y)
            grain.settled = True  # Start settled
            self.grains.append(grain)
            self.grid[y][x] = grain

    def fill_bottom(self):
        """Fill bottom chamber with sand (for flip)."""
        self.grains = []
        self.grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]

        bottom_cells = get_bottom_chamber()

        for i, (x, y) in enumerate(bottom_cells):
            if i >= SAND_COUNT:
                break
            grain = SandGrain(x, y)
            grain.settled = True
            self.grains.append(grain)
            self.grid[y][x] = grain

    def get_gravity_targets(self, x, y):
        """
        Get target positions for a grain based on gravity.
        When not flipped: gravity toward bottom (increasing y)
        When flipped: gravity toward top (decreasing y)
        """
        targets = []

        if not self.flipped:
            # Gravity down - try to move toward bottom corner
            # Priority: straight down, then diagonal down-left/right
            dy = 1
            targets = [
                (x, y + dy),           # Straight down
                (x - 1, y + dy),       # Down-left
                (x + 1, y + dy),       # Down-right
            ]
        else:
            # Gravity up - try to move toward top corner
            dy = -1
            targets = [
                (x, y + dy),           # Straight up
                (x - 1, y + dy),       # Up-left
                (x + 1, y + dy),       # Up-right
            ]

        # Randomize left/right preference
        if random.randint(0, 1):
            targets[1], targets[2] = targets[2], targets[1]

        return targets

    def can_move_to(self, x, y):
        """Check if a grain can move to this position."""
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            return False
        if not in_hourglass(x, y):
            return False
        if self.grid[y][x] is not None:
            return False
        return True

    def move_grain(self, grain, new_x, new_y):
        """Move grain to new position."""
        self.grid[grain.y][grain.x] = None
        grain.x = new_x
        grain.y = new_y
        self.grid[new_y][new_x] = grain

    def update(self):
        """Update simulation one step."""
        self.frame += 1

        # Sort grains by position (process in gravity direction first)
        if not self.flipped:
            # Process bottom grains first when gravity is down
            sorted_grains = sorted(self.grains, key=lambda g: -g.y)
        else:
            # Process top grains first when gravity is up
            sorted_grains = sorted(self.grains, key=lambda g: g.y)

        any_moved = False

        for grain in sorted_grains:
            if grain.settled:
                # Check if grain should become unsettled
                targets = self.get_gravity_targets(grain.x, grain.y)
                can_fall = any(self.can_move_to(tx, ty) for tx, ty in targets)
                if can_fall:
                    grain.settled = False

            if not grain.settled:
                targets = self.get_gravity_targets(grain.x, grain.y)

                moved = False
                for tx, ty in targets:
                    if self.can_move_to(tx, ty):
                        self.move_grain(grain, tx, ty)
                        moved = True
                        any_moved = True
                        break

                if not moved:
                    grain.settled = True

        return any_moved

    def is_complete(self):
        """Check if all sand has moved to destination chamber."""
        if not self.flipped:
            # Check if no sand in top chamber
            for grain in self.grains:
                if grain.y < 3:  # Still in top
                    return False
        else:
            # Check if no sand in bottom chamber
            for grain in self.grains:
                if grain.y > 4:  # Still in bottom
                    return False
        return True

    def flip(self):
        """Flip the hourglass."""
        self.flipped = not self.flipped

        # Unsettle all grains
        for grain in self.grains:
            grain.settled = False

    def draw(self):
        """Draw the hourglass."""
        np.fill((0, 0, 0))

        # Draw hourglass outline (subtle)
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if in_hourglass(x, y):
                    # Check if this is an edge cell
                    is_edge = False
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if not in_hourglass(nx, ny):
                            is_edge = True
                            break

                    if is_edge:
                        set_pixel(x, y, GLASS_COLOR)

        # Draw sand grains
        for grain in self.grains:
            set_pixel(grain.x, grain.y, grain.color)

        show()

    def draw_flip_animation(self):
        """Animate the flip."""
        # Flash effect
        for _ in range(3):
            np.fill(dim((50, 50, 80)))
            show()
            sleep(0.1)
            np.fill((0, 0, 0))
            show()
            sleep(0.1)

# =============================================================================
# MAIN
# =============================================================================

def run_hourglass():
    """Main hourglass simulation loop."""
    print("=" * 50)
    print("  Hourglass Simulation (45° mounted)")
    print("=" * 50)
    print("\nMount your matrix rotated 45 degrees!")
    print("Press Ctrl+C to stop\n")

    hourglass = Hourglass()
    cycle = 0

    try:
        while True:
            cycle += 1
            print(f"\n--- Cycle {cycle} ---")

            # Wait a moment before sand starts falling
            for _ in range(30):
                hourglass.draw()
                sleep(FRAME_DELAY)

            # Let sand fall
            stable_frames = 0
            while stable_frames < 20:
                moved = hourglass.update()
                hourglass.draw()

                if moved:
                    stable_frames = 0
                else:
                    stable_frames += 1

                print(f"\rFrame: {hourglass.frame}", end="")
                sleep(FRAME_DELAY)

            # Wait at bottom
            print("\nSand settled. Waiting...")
            for _ in range(50):
                hourglass.draw()
                sleep(FRAME_DELAY)

            # Flip animation
            print("Flipping hourglass...")
            hourglass.draw_flip_animation()
            hourglass.flip()

    except KeyboardInterrupt:
        clear()
        print("\n\nHourglass stopped.")


def run_simple_hourglass():
    """Simplified version - just sand falling through center."""
    print("=" * 50)
    print("  Simple Hourglass")
    print("=" * 50)

    grains = []
    grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]

    # Initial sand in top half
    for y in range(3):
        for x in range(2, 6):
            if len(grains) < SAND_COUNT:
                grain = SandGrain(x, y)
                grains.append(grain)
                grid[y][x] = grain

    frame = 0

    try:
        while True:
            np.fill((0, 0, 0))

            # Draw neck constriction
            for y in range(HEIGHT):
                for x in range(WIDTH):
                    # Hourglass shape
                    if y < 4:
                        allowed_x = range(y, 8 - y)
                    else:
                        allowed_x = range(7 - y, y + 1)

                    if x not in allowed_x:
                        set_pixel(x, y, (20, 20, 30))

            # Update grains (bottom to top)
            for grain in sorted(grains, key=lambda g: -g.y):
                x, y = grain.x, grain.y

                # Try to fall
                moved = False
                for dx in ([0, -1, 1] if random.randint(0, 1) else [0, 1, -1]):
                    new_x = x + dx
                    new_y = y + 1

                    if new_y >= HEIGHT:
                        continue

                    # Check hourglass bounds
                    if new_y < 4:
                        allowed = range(new_y, 8 - new_y)
                    else:
                        allowed = range(7 - new_y, new_y + 1)

                    if new_x in allowed and grid[new_y][new_x] is None:
                        grid[y][x] = None
                        grain.x = new_x
                        grain.y = new_y
                        grid[new_y][new_x] = grain
                        moved = True
                        break

            # Draw grains
            for grain in grains:
                set_pixel(grain.x, grain.y, grain.color)

            show()
            frame += 1
            print(f"\rFrame: {frame}", end="")

            # Check if all sand at bottom - reset
            all_bottom = all(g.y >= 5 for g in grains)
            if all_bottom:
                sleep(2)
                print("\nResetting...")

                # Move all sand back to top
                grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]
                i = 0
                for y in range(3):
                    for x in range(2, 6):
                        if i < len(grains):
                            grains[i].x = x
                            grains[i].y = y
                            grid[y][x] = grains[i]
                            i += 1

            sleep(FRAME_DELAY)

    except KeyboardInterrupt:
        clear()
        print("\n\nStopped.")


if __name__ == "__main__":
    # Choose which version to run:
    run_hourglass()         # Full simulation with flip
    # run_simple_hourglass()  # Simpler version

# Tetris AI - Self-Playing Tetris on NeoPixel 8x8 Matrix
# ======================================================
#
# Watch an AI play Tetris! The AI evaluates all possible
# placements and chooses the best move.
#
# Features:
# - All 7 classic Tetris pieces
# - AI with smart placement strategy
# - Line clear animations
# - Score and level tracking
# - Auto-restart on game over
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

# Game settings
DROP_SPEED = 0.15     # Initial drop speed (seconds)
AI_THINK_TIME = 0.3   # Pause to show AI "thinking"
LINE_CLEAR_TIME = 0.3 # Animation time for line clear
SPEED_INCREASE = 0.95 # Speed multiplier per level

# Initialize NeoPixel
np = NeoPixel(Pin(DATA_PIN, Pin.OUT), NUM_LEDS)

# =============================================================================
# TETROMINO DEFINITIONS
# =============================================================================

# Each piece defined as list of rotations, each rotation is list of (x,y) offsets
PIECES = {
    'I': [
        [(0,0), (1,0), (2,0), (3,0)],
        [(0,0), (0,1), (0,2), (0,3)],
    ],
    'O': [
        [(0,0), (1,0), (0,1), (1,1)],
    ],
    'T': [
        [(1,0), (0,1), (1,1), (2,1)],
        [(0,0), (0,1), (1,1), (0,2)],
        [(0,0), (1,0), (2,0), (1,1)],
        [(1,0), (0,1), (1,1), (1,2)],
    ],
    'S': [
        [(1,0), (2,0), (0,1), (1,1)],
        [(0,0), (0,1), (1,1), (1,2)],
    ],
    'Z': [
        [(0,0), (1,0), (1,1), (2,1)],
        [(1,0), (0,1), (1,1), (0,2)],
    ],
    'J': [
        [(0,0), (0,1), (1,1), (2,1)],
        [(0,0), (1,0), (0,1), (0,2)],
        [(0,0), (1,0), (2,0), (2,1)],
        [(1,0), (1,1), (0,2), (1,2)],
    ],
    'L': [
        [(2,0), (0,1), (1,1), (2,1)],
        [(0,0), (0,1), (0,2), (1,2)],
        [(0,0), (1,0), (2,0), (0,1)],
        [(0,0), (1,0), (1,1), (1,2)],
    ],
}

# Colors for each piece
PIECE_COLORS = {
    'I': (0, 255, 255),    # Cyan
    'O': (255, 255, 0),    # Yellow
    'T': (128, 0, 128),    # Purple
    'S': (0, 255, 0),      # Green
    'Z': (255, 0, 0),      # Red
    'J': (0, 0, 255),      # Blue
    'L': (255, 165, 0),    # Orange
}

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
# TETRIS GAME
# =============================================================================

class TetrisGame:
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset game state."""
        # Grid stores color tuples or None
        self.grid = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]
        self.score = 0
        self.lines = 0
        self.level = 1
        self.piece = None
        self.piece_type = None
        self.piece_x = 0
        self.piece_y = 0
        self.rotation = 0
        self.game_over = False
        self.spawn_piece()

    def spawn_piece(self):
        """Spawn a new piece at top."""
        self.piece_type = random.choice(list(PIECES.keys()))
        self.piece = PIECES[self.piece_type]
        self.rotation = 0
        self.piece_x = WIDTH // 2 - 1
        self.piece_y = 0

        # Check if spawn position is blocked
        if self.check_collision(self.piece_x, self.piece_y, self.rotation):
            self.game_over = True

    def get_piece_cells(self, x, y, rotation):
        """Get absolute positions of piece cells."""
        shape = self.piece[rotation % len(self.piece)]
        return [(x + dx, y + dy) for dx, dy in shape]

    def check_collision(self, x, y, rotation):
        """Check if piece at position would collide."""
        for px, py in self.get_piece_cells(x, y, rotation):
            # Wall collision
            if px < 0 or px >= WIDTH or py >= HEIGHT:
                return True
            # Floor collision
            if py < 0:
                continue
            # Grid collision
            if self.grid[py][px] is not None:
                return True
        return False

    def lock_piece(self):
        """Lock current piece into grid."""
        color = PIECE_COLORS[self.piece_type]
        for px, py in self.get_piece_cells(self.piece_x, self.piece_y, self.rotation):
            if 0 <= py < HEIGHT and 0 <= px < WIDTH:
                self.grid[py][px] = color

    def clear_lines(self):
        """Clear completed lines and return count."""
        lines_cleared = 0
        y = HEIGHT - 1

        while y >= 0:
            if all(self.grid[y][x] is not None for x in range(WIDTH)):
                # Line is complete
                lines_cleared += 1
                # Remove line and shift everything down
                for row in range(y, 0, -1):
                    self.grid[row] = self.grid[row - 1][:]
                self.grid[0] = [None for _ in range(WIDTH)]
                # Don't decrement y - check this row again
            else:
                y -= 1

        return lines_cleared

    def move_down(self):
        """Move piece down. Returns False if can't move."""
        if not self.check_collision(self.piece_x, self.piece_y + 1, self.rotation):
            self.piece_y += 1
            return True
        return False

    def move_horizontal(self, dx):
        """Move piece horizontally."""
        if not self.check_collision(self.piece_x + dx, self.piece_y, self.rotation):
            self.piece_x += dx
            return True
        return False

    def rotate(self, direction=1):
        """Rotate piece. Returns True if successful."""
        new_rotation = (self.rotation + direction) % len(self.piece)
        if not self.check_collision(self.piece_x, self.piece_y, new_rotation):
            self.rotation = new_rotation
            return True

        # Wall kick - try moving left/right to fit
        for kick in [1, -1, 2, -2]:
            if not self.check_collision(self.piece_x + kick, self.piece_y, new_rotation):
                self.piece_x += kick
                self.rotation = new_rotation
                return True
        return False

    def hard_drop(self):
        """Drop piece to bottom instantly."""
        while self.move_down():
            pass

    def draw(self, show_ghost=True):
        """Draw current game state."""
        np.fill((0, 0, 0))

        # Draw grid
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if self.grid[y][x]:
                    set_pixel(x, y, self.grid[y][x])

        # Draw ghost piece (where piece will land)
        if show_ghost and self.piece:
            ghost_y = self.piece_y
            while not self.check_collision(self.piece_x, ghost_y + 1, self.rotation):
                ghost_y += 1

            if ghost_y != self.piece_y:
                for px, py in self.get_piece_cells(self.piece_x, ghost_y, self.rotation):
                    if 0 <= py < HEIGHT and 0 <= px < WIDTH:
                        # Dim ghost
                        color = tuple(c // 6 for c in PIECE_COLORS[self.piece_type])
                        set_pixel(px, py, color)

        # Draw current piece
        if self.piece:
            color = PIECE_COLORS[self.piece_type]
            for px, py in self.get_piece_cells(self.piece_x, self.piece_y, self.rotation):
                if 0 <= py < HEIGHT and 0 <= px < WIDTH:
                    set_pixel(px, py, color)

        show()

# =============================================================================
# TETRIS AI
# =============================================================================

class TetrisAI:
    """AI that plays Tetris by evaluating all possible moves."""

    def __init__(self, game):
        self.game = game

    def evaluate_position(self, grid):
        """
        Evaluate how good a grid position is.
        Lower score = better.
        """
        score = 0

        # Factor 1: Aggregate height (lower is better)
        heights = []
        for x in range(WIDTH):
            for y in range(HEIGHT):
                if grid[y][x] is not None:
                    heights.append(HEIGHT - y)
                    break
            else:
                heights.append(0)

        score += sum(heights) * 0.5

        # Factor 2: Complete lines (very good!)
        complete_lines = 0
        for y in range(HEIGHT):
            if all(grid[y][x] is not None for x in range(WIDTH)):
                complete_lines += 1
        score -= complete_lines * 100

        # Factor 3: Holes (very bad!)
        holes = 0
        for x in range(WIDTH):
            found_block = False
            for y in range(HEIGHT):
                if grid[y][x] is not None:
                    found_block = True
                elif found_block:
                    holes += 1
        score += holes * 10

        # Factor 4: Bumpiness (height differences between columns)
        bumpiness = 0
        for i in range(len(heights) - 1):
            bumpiness += abs(heights[i] - heights[i + 1])
        score += bumpiness * 1

        # Factor 5: Maximum height (penalize tall stacks)
        if heights:
            score += max(heights) * 2

        # Factor 6: Wells (single-width gaps)
        wells = 0
        for x in range(WIDTH):
            left_height = heights[x - 1] if x > 0 else HEIGHT
            right_height = heights[x + 1] if x < WIDTH - 1 else HEIGHT
            if heights[x] < left_height and heights[x] < right_height:
                wells += min(left_height, right_height) - heights[x]
        score += wells * 0.5

        return score

    def simulate_placement(self, x, rotation):
        """Simulate placing piece and return resulting grid."""
        # Create copy of grid
        test_grid = [row[:] for row in self.game.grid]

        # Find landing position
        y = self.game.piece_y
        shape = self.game.piece[rotation % len(self.game.piece)]

        # Move down until collision
        while True:
            collision = False
            for dx, dy in shape:
                px, py = x + dx, y + 1 + dy
                if py >= HEIGHT or px < 0 or px >= WIDTH:
                    collision = True
                    break
                if py >= 0 and test_grid[py][px] is not None:
                    collision = True
                    break
            if collision:
                break
            y += 1

        # Check if any part is off screen (invalid placement)
        for dx, dy in shape:
            px, py = x + dx, y + dy
            if px < 0 or px >= WIDTH or py < 0:
                return None  # Invalid placement

        # Place piece
        color = PIECE_COLORS[self.game.piece_type]
        for dx, dy in shape:
            px, py = x + dx, y + dy
            if 0 <= py < HEIGHT and 0 <= px < WIDTH:
                test_grid[py][px] = color

        # Clear lines
        new_grid = []
        for row in test_grid:
            if not all(cell is not None for cell in row):
                new_grid.append(row)
        while len(new_grid) < HEIGHT:
            new_grid.insert(0, [None for _ in range(WIDTH)])

        return new_grid

    def find_best_move(self):
        """Find the best move (x position and rotation)."""
        best_score = float('inf')
        best_move = (self.game.piece_x, self.game.rotation)

        num_rotations = len(self.game.piece)

        for rotation in range(num_rotations):
            # Find valid x positions for this rotation
            shape = self.game.piece[rotation]
            min_x = min(dx for dx, dy in shape)
            max_x = max(dx for dx, dy in shape)

            for x in range(-min_x, WIDTH - max_x):
                result_grid = self.simulate_placement(x, rotation)
                if result_grid is None:
                    continue

                score = self.evaluate_position(result_grid)
                if score < best_score:
                    best_score = score
                    best_move = (x, rotation)

        return best_move

# =============================================================================
# ANIMATIONS
# =============================================================================

def line_clear_animation(game, lines):
    """Animate line clear."""
    if not lines:
        return

    # Find which lines are complete
    complete_rows = []
    for y in range(HEIGHT):
        if all(game.grid[y][x] is not None for x in range(WIDTH)):
            complete_rows.append(y)

    # Flash effect
    for _ in range(3):
        for y in complete_rows:
            for x in range(WIDTH):
                set_pixel(x, y, (255, 255, 255))
        show()
        sleep(LINE_CLEAR_TIME / 6)

        for y in complete_rows:
            for x in range(WIDTH):
                set_pixel(x, y, (0, 0, 0))
        show()
        sleep(LINE_CLEAR_TIME / 6)


def game_over_animation(game):
    """Game over animation."""
    # Fill from bottom with red
    for y in range(HEIGHT - 1, -1, -1):
        for x in range(WIDTH):
            set_pixel(x, y, (150, 0, 0))
        show()
        sleep(0.05)

    sleep(0.5)

    # Fade out
    for i in range(10):
        fade = 1 - i / 10
        for y in range(HEIGHT):
            for x in range(WIDTH):
                set_pixel(x, y, (int(150 * fade), 0, 0))
        show()
        sleep(0.05)

# =============================================================================
# MAIN GAME LOOP
# =============================================================================

def run_tetris_ai():
    """Main function - AI plays Tetris."""
    print("=" * 50)
    print("  Tetris AI - Self-Playing Tetris")
    print("=" * 50)
    print("\nWatch the AI play!")
    print("Press Ctrl+C to stop\n")

    games_played = 0
    high_score = 0
    total_lines = 0

    try:
        while True:
            games_played += 1
            print(f"\n--- Game #{games_played} ---")

            game = TetrisGame()
            ai = TetrisAI(game)

            drop_speed = DROP_SPEED

            while not game.game_over:
                # AI decides best move
                target_x, target_rotation = ai.find_best_move()

                # Execute moves to reach target
                # Rotate first
                while game.rotation != target_rotation:
                    game.rotate()
                    game.draw()
                    sleep(0.03)

                # Then move horizontally
                while game.piece_x != target_x:
                    dx = 1 if target_x > game.piece_x else -1
                    game.move_horizontal(dx)
                    game.draw()
                    sleep(0.03)

                # Drop piece
                game.hard_drop()
                game.draw()
                sleep(0.05)

                # Lock piece
                game.lock_piece()

                # Check for line clears
                lines = game.clear_lines()
                if lines > 0:
                    line_clear_animation(game, lines)
                    game.lines += lines
                    game.score += [0, 100, 300, 500, 800][min(lines, 4)] * game.level
                    total_lines += lines

                    # Level up every 10 lines
                    new_level = game.lines // 10 + 1
                    if new_level > game.level:
                        game.level = new_level
                        drop_speed *= SPEED_INCREASE
                        print(f"Level up! Now level {game.level}")

                game.draw()

                # Status
                print(f"\rScore: {game.score:5d} | Lines: {game.lines:3d} | Level: {game.level}", end="")

                # Spawn next piece
                game.spawn_piece()

                sleep(drop_speed)

            # Game over
            print(f"\n\nGame Over! Score: {game.score}, Lines: {game.lines}")

            if game.score > high_score:
                high_score = game.score
                print(f"*** NEW HIGH SCORE! ***")

            game_over_animation(game)
            sleep(1)

    except KeyboardInterrupt:
        clear()
        print("\n\n" + "=" * 50)
        print("  FINAL STATISTICS")
        print("=" * 50)
        print(f"  Games Played: {games_played}")
        print(f"  High Score:   {high_score}")
        print(f"  Total Lines:  {total_lines}")
        print("=" * 50)


if __name__ == "__main__":
    run_tetris_ai()

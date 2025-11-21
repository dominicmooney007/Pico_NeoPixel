# Autonomous Snake Game - NeoPixel 8x8 Matrix
# ============================================
#
# Watch an AI play Snake! The snake automatically chases food,
# avoids walls and itself, and restarts when it loses.
#
# The AI uses a simple but effective strategy:
# 1. Try to move toward the food
# 2. Avoid immediate collisions (walls, self)
# 3. Prefer moves that keep more escape routes open
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
BRIGHTNESS = 0.35

# Game settings
GAME_SPEED = 0.12        # Seconds between moves (lower = faster)
INITIAL_LENGTH = 3       # Starting snake length
SHOW_GAME_OVER = True    # Flash on death
PAUSE_BETWEEN_GAMES = 1  # Seconds before restart

# Initialize NeoPixel
np = NeoPixel(Pin(DATA_PIN, Pin.OUT), NUM_LEDS)

# =============================================================================
# COLORS
# =============================================================================

SNAKE_HEAD = (0, 255, 0)      # Bright green
SNAKE_BODY = (0, 150, 0)      # Darker green
SNAKE_TAIL = (0, 80, 0)       # Even darker
FOOD_COLOR = (255, 0, 0)      # Red
BACKGROUND = (0, 0, 0)        # Black
GAME_OVER_COLOR = (255, 0, 0) # Red flash

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
# DIRECTIONS
# =============================================================================

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

DIRECTIONS = [UP, DOWN, LEFT, RIGHT]

def opposite(direction):
    """Get opposite direction."""
    return (-direction[0], -direction[1])

# =============================================================================
# SNAKE GAME
# =============================================================================

class SnakeGame:
    def __init__(self):
        self.reset()

    def reset(self):
        """Reset game to initial state."""
        # Start snake in center, moving right
        start_x = WIDTH // 2
        start_y = HEIGHT // 2

        self.snake = []
        for i in range(INITIAL_LENGTH):
            self.snake.append((start_x - i, start_y))

        self.direction = RIGHT
        self.food = None
        self.spawn_food()
        self.score = 0
        self.moves = 0
        self.alive = True

    def spawn_food(self):
        """Spawn food in random empty location."""
        empty_cells = []
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if (x, y) not in self.snake:
                    empty_cells.append((x, y))

        if empty_cells:
            self.food = random.choice(empty_cells)
        else:
            # Snake fills entire grid - you win!
            self.food = None

    def get_head(self):
        """Get snake head position."""
        return self.snake[0]

    def is_collision(self, pos):
        """Check if position causes collision."""
        x, y = pos
        # Wall collision
        if x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT:
            return True
        # Self collision (excluding tail which will move)
        if pos in self.snake[:-1]:
            return True
        return False

    def is_safe(self, pos):
        """Check if position is safe to move to."""
        return not self.is_collision(pos)

    def move(self, direction):
        """Move snake in direction. Returns True if alive."""
        if not self.alive:
            return False

        self.direction = direction
        head_x, head_y = self.get_head()
        new_head = (head_x + direction[0], head_y + direction[1])

        # Check collision
        if self.is_collision(new_head):
            self.alive = False
            return False

        # Move snake
        self.snake.insert(0, new_head)
        self.moves += 1

        # Check food
        if new_head == self.food:
            self.score += 1
            self.spawn_food()
            # Don't remove tail - snake grows
        else:
            self.snake.pop()  # Remove tail

        return True

    def draw(self):
        """Draw current game state."""
        np.fill((0, 0, 0))

        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            if i == 0:
                color = SNAKE_HEAD
            elif i < len(self.snake) // 2:
                color = SNAKE_BODY
            else:
                color = SNAKE_TAIL
            set_pixel(x, y, color)

        # Draw food with pulsing effect
        if self.food:
            pulse = abs((self.moves % 10) - 5) / 5  # 0 to 1
            r = int(FOOD_COLOR[0] * (0.5 + 0.5 * pulse))
            set_pixel(self.food[0], self.food[1], (r, 0, 0))

        show()

# =============================================================================
# SNAKE AI
# =============================================================================

class SnakeAI:
    """AI that plays Snake automatically."""

    def __init__(self, game):
        self.game = game

    def get_valid_moves(self):
        """Get all moves that don't cause immediate death."""
        head = self.game.get_head()
        valid = []

        for direction in DIRECTIONS:
            # Can't reverse direction
            if direction == opposite(self.game.direction):
                continue

            new_pos = (head[0] + direction[0], head[1] + direction[1])
            if self.game.is_safe(new_pos):
                valid.append(direction)

        return valid

    def distance_to_food(self, pos):
        """Manhattan distance from position to food."""
        if not self.game.food:
            return 0
        return abs(pos[0] - self.game.food[0]) + abs(pos[1] - self.game.food[1])

    def count_reachable(self, start_pos, max_depth=10):
        """
        Count how many cells are reachable from a position.
        More reachable cells = less likely to trap ourselves.
        """
        visited = set()
        visited.add(start_pos)
        # Add snake body as blocked (except tail which will move)
        for segment in self.game.snake[:-1]:
            visited.add(segment)

        frontier = [start_pos]
        count = 0

        for _ in range(max_depth):
            if not frontier:
                break
            new_frontier = []
            for pos in frontier:
                for dx, dy in DIRECTIONS:
                    new_pos = (pos[0] + dx, pos[1] + dy)
                    if (new_pos not in visited and
                        0 <= new_pos[0] < WIDTH and
                        0 <= new_pos[1] < HEIGHT):
                        visited.add(new_pos)
                        new_frontier.append(new_pos)
                        count += 1
            frontier = new_frontier

        return count

    def choose_move(self):
        """Choose the best move for the snake."""
        valid_moves = self.get_valid_moves()

        if not valid_moves:
            # No valid moves - we're doomed, just go forward
            return self.game.direction

        if len(valid_moves) == 1:
            # Only one option
            return valid_moves[0]

        head = self.game.get_head()
        best_move = valid_moves[0]
        best_score = -1000

        for direction in valid_moves:
            new_pos = (head[0] + direction[0], head[1] + direction[1])
            score = 0

            # Factor 1: Distance to food (closer is better)
            food_dist = self.distance_to_food(new_pos)
            score -= food_dist * 10

            # Factor 2: Reachable space (more is better - avoid traps)
            reachable = self.count_reachable(new_pos)
            score += reachable * 5

            # Factor 3: Prefer center of board (more escape routes)
            center_dist = abs(new_pos[0] - 3.5) + abs(new_pos[1] - 3.5)
            score -= center_dist

            # Factor 4: Avoid edges when possible
            if new_pos[0] == 0 or new_pos[0] == WIDTH - 1:
                score -= 3
            if new_pos[1] == 0 or new_pos[1] == HEIGHT - 1:
                score -= 3

            # Factor 5: If food is adjacent, prioritize it highly
            if new_pos == self.game.food:
                score += 100

            if score > best_score:
                best_score = score
                best_move = direction

        return best_move

# =============================================================================
# GAME OVER ANIMATION
# =============================================================================

def game_over_animation(game):
    """Flash the snake red on death."""
    if not SHOW_GAME_OVER:
        return

    # Flash snake red
    for _ in range(3):
        np.fill((0, 0, 0))
        for x, y in game.snake:
            set_pixel(x, y, GAME_OVER_COLOR)
        show()
        sleep(0.15)

        np.fill((0, 0, 0))
        show()
        sleep(0.15)

    # Collapse animation
    for i in range(len(game.snake)):
        np.fill((0, 0, 0))
        for j, (x, y) in enumerate(game.snake):
            if j >= i:
                fade = 1 - (j - i) / len(game.snake)
                color = (int(GAME_OVER_COLOR[0] * fade), 0, 0)
                set_pixel(x, y, color)
        show()
        sleep(0.05)

# =============================================================================
# STATS DISPLAY
# =============================================================================

def display_score(score):
    """Brief score display using pixels."""
    clear()

    # Display score as filled rows (each row = 1 point, max 8)
    display_score = min(score, HEIGHT * WIDTH)

    for i in range(display_score):
        x = i % WIDTH
        y = i // WIDTH
        if y < HEIGHT:
            set_pixel(x, y, (255, 255, 0))

    show()
    sleep(0.5)

# =============================================================================
# MAIN GAME LOOP
# =============================================================================

def run_snake_ai():
    """Main function - run autonomous snake game."""
    print("=" * 50)
    print("  Autonomous Snake Game - AI Player")
    print("=" * 50)
    print("\nWatch the AI play Snake!")
    print("Press Ctrl+C to stop\n")

    games_played = 0
    high_score = 0
    total_score = 0

    try:
        while True:
            games_played += 1
            print(f"\n--- Game #{games_played} ---")

            # Initialize game and AI
            game = SnakeGame()
            ai = SnakeAI(game)

            # Game loop
            while game.alive:
                # AI chooses move
                move = ai.choose_move()

                # Execute move
                game.move(move)

                # Draw game state
                game.draw()

                # Status update
                print(f"\rScore: {game.score:2d} | Length: {len(game.snake):2d} | Moves: {game.moves:4d}", end="")

                # Speed up slightly as snake grows
                speed = max(0.05, GAME_SPEED - len(game.snake) * 0.005)
                sleep(speed)

                # Check for win condition (filled entire grid)
                if len(game.snake) >= WIDTH * HEIGHT:
                    print("\n*** PERFECT GAME! Snake filled the grid! ***")
                    break

            # Game over
            print(f"\n\nGame Over! Final score: {game.score}")

            # Update stats
            total_score += game.score
            if game.score > high_score:
                high_score = game.score
                print(f"*** NEW HIGH SCORE: {high_score}! ***")

            avg_score = total_score / games_played
            print(f"High Score: {high_score} | Average: {avg_score:.1f}")

            # Game over animation
            game_over_animation(game)

            # Brief score display
            if game.score > 0:
                display_score(game.score)

            # Pause before restart
            clear()
            sleep(PAUSE_BETWEEN_GAMES)

    except KeyboardInterrupt:
        clear()
        print("\n\n" + "=" * 50)
        print("  FINAL STATISTICS")
        print("=" * 50)
        print(f"  Games Played: {games_played}")
        print(f"  High Score:   {high_score}")
        print(f"  Total Score:  {total_score}")
        if games_played > 0:
            print(f"  Average:      {total_score / games_played:.1f}")
        print("=" * 50)

# =============================================================================
# DEMO MODE - Single game with commentary
# =============================================================================

def demo_single_game():
    """Run a single game with detailed output."""
    print("Running single demo game...\n")

    game = SnakeGame()
    ai = SnakeAI(game)

    while game.alive and game.moves < 500:
        move = ai.choose_move()

        # Describe move
        move_names = {UP: "UP", DOWN: "DOWN", LEFT: "LEFT", RIGHT: "RIGHT"}
        head = game.get_head()
        new_head = (head[0] + move[0], head[1] + move[1])

        eating = "EATING!" if new_head == game.food else ""
        print(f"Move {game.moves}: {move_names[move]} to {new_head} {eating}")

        game.move(move)
        game.draw()
        sleep(GAME_SPEED * 2)  # Slower for demo

    print(f"\nGame over! Score: {game.score}, Moves: {game.moves}")
    game_over_animation(game)
    clear()

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    run_snake_ai()

    # Or run a single demo game:
    # demo_single_game()

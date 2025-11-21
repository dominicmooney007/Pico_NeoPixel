# NeoPixel 8x8 Matrix - Ultimate Showcase Demo
# =============================================
#
# A spectacular demonstration of everything your 8x8 NeoPixel matrix can do!
# This showcases colors, animations, patterns, shapes, and visual effects.
#
# Press Ctrl+C to stop at any time.
#

from machine import Pin
from neopixel import NeoPixel
from utime import sleep, ticks_ms, ticks_diff
import math

# =============================================================================
# CONFIGURATION
# =============================================================================

DATA_PIN = 0
WIDTH = 8
HEIGHT = 8
NUM_LEDS = WIDTH * HEIGHT
BRIGHTNESS = 0.4  # Adjust 0.1-1.0

# Initialize
np = NeoPixel(Pin(DATA_PIN, Pin.OUT), NUM_LEDS)

# =============================================================================
# CORE HELPERS
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
    """Set pixel with bounds checking."""
    if 0 <= x < WIDTH and 0 <= y < HEIGHT:
        np[xy(x, y)] = dim(color)

def clear():
    np.fill((0, 0, 0))
    np.write()

def show():
    np.write()

def fill(color):
    np.fill(dim(color))
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

def hsv_to_rgb(h, s, v):
    """Convert HSV (0-1 range) to RGB (0-255)."""
    if s == 0:
        return (int(v * 255), int(v * 255), int(v * 255))

    h = h % 1.0
    i = int(h * 6)
    f = (h * 6) - i
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))

    i = i % 6
    if i == 0: r, g, b = v, t, p
    elif i == 1: r, g, b = q, v, p
    elif i == 2: r, g, b = p, v, t
    elif i == 3: r, g, b = p, q, v
    elif i == 4: r, g, b = t, p, v
    else: r, g, b = v, p, q

    return (int(r * 255), int(g * 255), int(b * 255))

def lerp_color(c1, c2, t):
    """Linear interpolate between two colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def title(name):
    """Print demo title."""
    print(f"\n>>> {name}")

# =============================================================================
# DEMO 1: Color Spectrum
# =============================================================================

def demo_color_spectrum():
    """Smooth transition through all colors."""
    title("Color Spectrum - Full RGB Range")

    for hue in range(360):
        color = hsv_to_rgb(hue / 360, 1.0, 1.0)
        fill(color)
        sleep(0.015)

# =============================================================================
# DEMO 2: Plasma Effect
# =============================================================================

def demo_plasma():
    """Psychedelic plasma pattern using sine waves."""
    title("Plasma Effect - Mathematical Art")

    for t in range(150):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                # Combine multiple sine waves for plasma effect
                v1 = math.sin(x / 2.0 + t / 10.0)
                v2 = math.sin((x + y) / 3.0 + t / 15.0)
                v3 = math.sin(math.sqrt((x - 4)**2 + (y - 4)**2) / 2.0 + t / 12.0)
                v = (v1 + v2 + v3 + 3) / 6  # Normalize to 0-1

                color = hsv_to_rgb(v, 1.0, 1.0)
                set_pixel(x, y, color)
        show()
        sleep(0.03)

# =============================================================================
# DEMO 3: Wave Patterns
# =============================================================================

def demo_waves():
    """Multiple wave patterns."""
    title("Wave Patterns - Sine Wave Visualization")

    colors = [(255, 0, 0), (0, 255, 0), (0, 100, 255), (255, 255, 0)]

    for wave_type in range(4):
        for t in range(60):
            np.fill((0, 0, 0))

            for x in range(WIDTH):
                if wave_type == 0:  # Single sine wave
                    y = int(3.5 + 3 * math.sin(x / 1.5 + t / 5))
                elif wave_type == 1:  # Double frequency
                    y = int(3.5 + 3 * math.sin(x + t / 3))
                elif wave_type == 2:  # Standing wave
                    y = int(3.5 + 3 * math.sin(x) * math.cos(t / 5))
                else:  # Combined waves
                    y = int(3.5 + 2 * math.sin(x / 2 + t / 5) + math.sin(x + t / 3))

                if 0 <= y < HEIGHT:
                    set_pixel(x, y, colors[wave_type])
                    # Add glow below
                    if y + 1 < HEIGHT:
                        set_pixel(x, y + 1, tuple(c // 3 for c in colors[wave_type]))

            show()
            sleep(0.04)

# =============================================================================
# DEMO 4: Geometric Shapes
# =============================================================================

def demo_shapes():
    """Drawing various geometric shapes."""
    title("Geometric Shapes")

    # Expanding circles
    for radius in range(6):
        np.fill((0, 0, 0))
        cx, cy = 3.5, 3.5
        for y in range(HEIGHT):
            for x in range(WIDTH):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                if abs(dist - radius) < 0.8:
                    set_pixel(x, y, (0, 255, 255))
        show()
        sleep(0.2)

    sleep(0.3)

    # Rotating line
    for angle in range(0, 360, 5):
        np.fill((0, 0, 0))
        rad = math.radians(angle)
        for i in range(-4, 5):
            x = int(3.5 + i * math.cos(rad))
            y = int(3.5 + i * math.sin(rad))
            set_pixel(x, y, wheel(angle))
        show()
        sleep(0.03)

    # Triangle
    clear()
    triangle = [(3, 0), (0, 7), (7, 7)]
    for i in range(3):
        x1, y1 = triangle[i]
        x2, y2 = triangle[(i + 1) % 3]
        steps = max(abs(x2 - x1), abs(y2 - y1))
        if steps > 0:
            for t in range(steps + 1):
                x = int(x1 + (x2 - x1) * t / steps)
                y = int(y1 + (y2 - y1) * t / steps)
                set_pixel(x, y, (255, 100, 0))
    show()
    sleep(1)

    # Filled rectangles
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
    for i in range(4):
        np.fill((0, 0, 0))
        size = 7 - i
        offset = i
        for y in range(offset, offset + size - i):
            for x in range(offset, offset + size - i):
                set_pixel(x, y, colors[i])
        show()
        sleep(0.4)

# =============================================================================
# DEMO 5: Conway's Game of Life
# =============================================================================

def demo_game_of_life():
    """Cellular automaton simulation."""
    title("Conway's Game of Life")
    import random

    # Initialize random grid
    grid = [[random.randint(0, 1) for _ in range(WIDTH)] for _ in range(HEIGHT)]

    for generation in range(60):
        # Display current state
        np.fill((0, 0, 0))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if grid[y][x]:
                    # Color based on generation for visual interest
                    set_pixel(x, y, wheel((generation * 4 + x * 10 + y * 10) % 256))
        show()

        # Calculate next generation
        new_grid = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
        for y in range(HEIGHT):
            for x in range(WIDTH):
                # Count neighbors (toroidal wrap)
                neighbors = 0
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx = (x + dx) % WIDTH
                        ny = (y + dy) % HEIGHT
                        neighbors += grid[ny][nx]

                # Apply rules
                if grid[y][x]:
                    new_grid[y][x] = 1 if neighbors in [2, 3] else 0
                else:
                    new_grid[y][x] = 1 if neighbors == 3 else 0

        grid = new_grid
        sleep(0.15)

# =============================================================================
# DEMO 6: Fireworks
# =============================================================================

def demo_fireworks():
    """Exploding firework particles."""
    title("Fireworks Display")
    import random

    class Particle:
        def __init__(self, x, y, vx, vy, color, life):
            self.x, self.y = x, y
            self.vx, self.vy = vx, vy
            self.color = color
            self.life = life
            self.max_life = life

    particles = []

    for _ in range(8):  # 8 fireworks
        # Launch position
        cx = random.randint(2, 5)
        cy = random.randint(2, 5)
        color = wheel(random.randint(0, 255))

        # Create explosion particles
        for angle in range(0, 360, 30):
            rad = math.radians(angle)
            speed = random.uniform(0.3, 0.8)
            particles.append(Particle(
                cx, cy,
                math.cos(rad) * speed,
                math.sin(rad) * speed,
                color,
                random.randint(15, 25)
            ))

        # Animate this firework
        for _ in range(30):
            np.fill((0, 0, 0))

            for p in particles:
                if p.life > 0:
                    # Fade based on remaining life
                    brightness = p.life / p.max_life
                    c = tuple(int(v * brightness) for v in p.color)
                    set_pixel(int(p.x), int(p.y), c)

                    # Physics
                    p.x += p.vx
                    p.y += p.vy
                    p.vy += 0.05  # Gravity
                    p.life -= 1

            show()
            sleep(0.05)

        particles = []

# =============================================================================
# DEMO 7: Matrix Digital Rain
# =============================================================================

def demo_matrix_rain():
    """The Matrix-style digital rain."""
    title("Matrix Digital Rain")
    import random

    drops = [{'y': random.randint(-8, 0), 'speed': random.uniform(0.3, 0.8)}
             for _ in range(WIDTH)]

    for _ in range(80):
        np.fill((0, 0, 0))

        for x, drop in enumerate(drops):
            # Draw drop with trail
            for trail in range(6):
                y = int(drop['y']) - trail
                if 0 <= y < HEIGHT:
                    if trail == 0:
                        set_pixel(x, y, (200, 255, 200))  # Bright head
                    else:
                        intensity = 255 - trail * 45
                        set_pixel(x, y, (0, intensity, 0))

            # Move drop
            drop['y'] += drop['speed']

            # Reset when off screen
            if drop['y'] > HEIGHT + 6:
                drop['y'] = random.randint(-6, -1)
                drop['speed'] = random.uniform(0.3, 0.8)

        show()
        sleep(0.06)

# =============================================================================
# DEMO 8: Fire Simulation
# =============================================================================

def demo_fire():
    """Realistic fire effect."""
    title("Fire Simulation")
    import random

    heat = [[0] * WIDTH for _ in range(HEIGHT)]

    for _ in range(100):
        # Cool down
        for y in range(HEIGHT):
            for x in range(WIDTH):
                cooling = random.randint(0, 30)
                heat[y][x] = max(0, heat[y][x] - cooling)

        # Heat rises (from bottom)
        for y in range(HEIGHT - 1, 0, -1):
            for x in range(WIDTH):
                left = heat[y-1][max(0, x-1)]
                center = heat[y-1][x]
                right = heat[y-1][min(WIDTH-1, x+1)]
                heat[y][x] = (left + center + center + right) // 4

        # Random sparks at bottom
        for x in range(WIDTH):
            if random.random() < 0.7:
                heat[0][x] = min(255, heat[0][x] + random.randint(100, 255))

        # Render
        for y in range(HEIGHT):
            for x in range(WIDTH):
                h = heat[y][x]
                # Fire palette
                if h < 64:
                    r, g, b = h * 4, 0, 0
                elif h < 128:
                    r, g, b = 255, (h - 64) * 4, 0
                elif h < 192:
                    r, g, b = 255, 255, (h - 128) * 4
                else:
                    r, g, b = 255, 255, 255
                set_pixel(x, HEIGHT - 1 - y, (r, g, b))

        show()
        sleep(0.04)

# =============================================================================
# DEMO 9: Starfield
# =============================================================================

def demo_starfield():
    """3D starfield flying through space."""
    title("Starfield - Warp Speed")
    import random

    class Star:
        def __init__(self):
            self.reset()

        def reset(self):
            self.x = random.uniform(-2, 2)
            self.y = random.uniform(-2, 2)
            self.z = random.uniform(1, 4)

    stars = [Star() for _ in range(30)]

    for _ in range(120):
        np.fill((0, 0, 0))

        for star in stars:
            # Project 3D to 2D
            if star.z > 0:
                sx = int(4 + star.x / star.z * 4)
                sy = int(4 + star.y / star.z * 4)

                # Brightness based on distance
                brightness = int(255 * (1 - star.z / 5))
                brightness = max(0, min(255, brightness))

                if 0 <= sx < WIDTH and 0 <= sy < HEIGHT:
                    set_pixel(sx, sy, (brightness, brightness, brightness))

            # Move star closer
            star.z -= 0.08
            if star.z <= 0:
                star.reset()

        show()
        sleep(0.03)

# =============================================================================
# DEMO 10: Bouncing Ball
# =============================================================================

def demo_bouncing_ball():
    """Physics-based bouncing ball with trails."""
    title("Bouncing Ball Physics")

    x, y = 1.0, 1.0
    vx, vy = 0.3, 0.2
    gravity = 0.02
    bounce = 0.85
    trail = []

    for _ in range(150):
        np.fill((0, 0, 0))

        # Draw trail
        for i, (tx, ty) in enumerate(trail):
            fade = (i + 1) / len(trail) if trail else 1
            set_pixel(int(tx), int(ty), (int(100 * fade), 0, int(50 * fade)))

        # Draw ball
        set_pixel(int(x), int(y), (255, 50, 50))

        # Add to trail
        trail.append((x, y))
        if len(trail) > 8:
            trail.pop(0)

        # Physics
        vy += gravity
        x += vx
        y += vy

        # Bounce off walls
        if x <= 0 or x >= WIDTH - 1:
            vx = -vx * bounce
            x = max(0, min(WIDTH - 1, x))
        if y >= HEIGHT - 1:
            vy = -vy * bounce
            y = HEIGHT - 1
            if abs(vy) < 0.1:
                vy = -0.5  # Re-energize
        if y <= 0:
            vy = -vy * bounce
            y = 0

        show()
        sleep(0.04)

# =============================================================================
# DEMO 11: Kaleidoscope
# =============================================================================

def demo_kaleidoscope():
    """Symmetric kaleidoscope patterns."""
    title("Kaleidoscope - 8-fold Symmetry")

    for t in range(120):
        np.fill((0, 0, 0))

        # Generate pattern in one octant, mirror to all 8
        for y in range(4):
            for x in range(y + 1):
                # Create interesting pattern
                hue = (x * 30 + y * 40 + t * 3) % 256
                dist = math.sqrt(x**2 + y**2)
                wave = math.sin(dist + t / 10)

                if wave > 0:
                    color = wheel(hue)

                    # Mirror to all 8 sections
                    cx, cy = 3.5, 3.5
                    points = [
                        (cx + x, cy + y), (cx + y, cy + x),
                        (cx - x - 1, cy + y), (cx - y - 1, cy + x),
                        (cx + x, cy - y - 1), (cx + y, cy - x - 1),
                        (cx - x - 1, cy - y - 1), (cx - y - 1, cy - x - 1)
                    ]

                    for px, py in points:
                        set_pixel(int(px), int(py), color)

        show()
        sleep(0.05)

# =============================================================================
# DEMO 12: Audio Visualizer (Simulated)
# =============================================================================

def demo_audio_visualizer():
    """Simulated audio spectrum analyzer."""
    title("Audio Visualizer (Simulated)")
    import random

    # Simulated frequency bands
    bands = [0] * WIDTH
    targets = [0] * WIDTH

    for _ in range(80):
        np.fill((0, 0, 0))

        # Update targets periodically
        for i in range(WIDTH):
            if random.random() < 0.3:
                # Lower frequencies (left) tend to be stronger
                max_height = 8 - abs(i - 2)
                targets[i] = random.randint(1, max(1, max_height))

        # Smooth movement toward targets
        for i in range(WIDTH):
            if bands[i] < targets[i]:
                bands[i] = min(bands[i] + 1, targets[i])
            elif bands[i] > targets[i]:
                bands[i] = max(bands[i] - 0.5, targets[i])

            # Draw bar
            height = int(bands[i])
            for y in range(height):
                # Color gradient: green at bottom, yellow middle, red top
                if y < 3:
                    color = (0, 255, 0)
                elif y < 5:
                    color = (255, 255, 0)
                else:
                    color = (255, 0, 0)
                set_pixel(i, HEIGHT - 1 - y, color)

            # Peak dot
            if height > 0:
                set_pixel(i, HEIGHT - 1 - height, (255, 255, 255))

        show()
        sleep(0.06)

# =============================================================================
# DEMO 13: Spiral Galaxy
# =============================================================================

def demo_spiral_galaxy():
    """Rotating spiral galaxy."""
    title("Spiral Galaxy")

    for t in range(150):
        np.fill((0, 0, 0))

        cx, cy = 3.5, 3.5

        for y in range(HEIGHT):
            for x in range(WIDTH):
                dx = x - cx
                dy = y - cy
                dist = math.sqrt(dx**2 + dy**2)
                angle = math.atan2(dy, dx)

                # Spiral arms
                spiral = (angle + dist * 0.5 + t * 0.05) % (math.pi / 2)

                if dist < 4 and spiral < 0.4:
                    # Color varies with distance and angle
                    brightness = 1 - dist / 5
                    hue = (angle * 40 + t * 2) % 256
                    color = wheel(int(hue))
                    color = tuple(int(c * brightness) for c in color)
                    set_pixel(x, y, color)

                # Center glow
                if dist < 1.5:
                    glow = int(255 * (1 - dist / 1.5))
                    set_pixel(x, y, (glow, glow, int(glow * 0.8)))

        show()
        sleep(0.04)

# =============================================================================
# DEMO 14: Morphing Shapes
# =============================================================================

def demo_morphing():
    """Shapes morphing into each other."""
    title("Morphing Shapes")

    def draw_circle(r, color, cx=3.5, cy=3.5):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                if abs(dist - r) < 0.7:
                    set_pixel(x, y, color)

    def draw_square(size, color, cx=3.5, cy=3.5):
        half = size / 2
        for y in range(HEIGHT):
            for x in range(WIDTH):
                dx = abs(x - cx)
                dy = abs(y - cy)
                if max(dx, dy) < half and max(dx, dy) > half - 1:
                    set_pixel(x, y, color)

    def draw_diamond(size, color, cx=3.5, cy=3.5):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                dist = abs(x - cx) + abs(y - cy)
                if abs(dist - size) < 0.7:
                    set_pixel(x, y, color)

    shapes = [draw_circle, draw_square, draw_diamond]
    colors = [(255, 0, 100), (0, 255, 100), (100, 100, 255)]

    for i in range(6):
        shape = shapes[i % 3]
        color = colors[i % 3]

        # Expand
        for size in range(1, 5):
            np.fill((0, 0, 0))
            shape(size, color)
            show()
            sleep(0.1)

        # Contract
        for size in range(4, 0, -1):
            np.fill((0, 0, 0))
            shape(size, color)
            show()
            sleep(0.1)

# =============================================================================
# DEMO 15: Text Scroller (Simple Patterns)
# =============================================================================

def demo_patterns():
    """Various mesmerizing patterns."""
    title("Mesmerizing Patterns")

    # Pattern 1: Concentric squares
    for t in range(30):
        np.fill((0, 0, 0))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                dist = max(abs(x - 3.5), abs(y - 3.5))
                if (int(dist + t / 3)) % 2 == 0:
                    set_pixel(x, y, wheel(int(dist * 30 + t * 5) % 256))
        show()
        sleep(0.08)

    # Pattern 2: Diagonal stripes
    for t in range(40):
        np.fill((0, 0, 0))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                if (x + y + t // 2) % 4 < 2:
                    set_pixel(x, y, wheel((x * 20 + t * 3) % 256))
        show()
        sleep(0.06)

    # Pattern 3: Checkerboard wave
    for t in range(40):
        np.fill((0, 0, 0))
        for y in range(HEIGHT):
            for x in range(WIDTH):
                wave = math.sin(x / 2 + t / 5) + math.sin(y / 2 + t / 7)
                if wave > 0:
                    set_pixel(x, y, wheel(int(x * 20 + y * 20 + t * 2) % 256))
        show()
        sleep(0.05)

# =============================================================================
# DEMO 16: Radar Sweep
# =============================================================================

def demo_radar():
    """Radar sweep with detected blips."""
    title("Radar Sweep")
    import random

    blips = [(random.uniform(0, 2*math.pi), random.uniform(1, 3.5)) for _ in range(5)]

    for t in range(120):
        np.fill((0, 0, 0))

        sweep_angle = (t * 0.1) % (2 * math.pi)
        cx, cy = 3.5, 3.5

        # Draw fading sweep trail
        for trail in range(20):
            angle = sweep_angle - trail * 0.05
            fade = 1 - trail / 20

            for r in range(1, 5):
                x = int(cx + r * math.cos(angle))
                y = int(cy + r * math.sin(angle))
                intensity = int(100 * fade * (1 - r / 5))
                set_pixel(x, y, (0, intensity, 0))

        # Draw range circles
        for y in range(HEIGHT):
            for x in range(WIDTH):
                dist = math.sqrt((x - cx)**2 + (y - cy)**2)
                if abs(dist - 3.5) < 0.3:
                    set_pixel(x, y, (0, 40, 0))

        # Draw blips
        for blip_angle, blip_dist in blips:
            # Check if sweep just passed this blip
            angle_diff = (sweep_angle - blip_angle) % (2 * math.pi)
            if angle_diff < 0.5:
                brightness = int(255 * (1 - angle_diff / 0.5))
                bx = int(cx + blip_dist * math.cos(blip_angle))
                by = int(cy + blip_dist * math.sin(blip_angle))
                set_pixel(bx, by, (0, brightness, 0))

        show()
        sleep(0.04)

# =============================================================================
# FINALE: Rainbow Explosion
# =============================================================================

def demo_finale():
    """Grand finale - rainbow explosion."""
    title("FINALE - Rainbow Explosion!")

    # Build up
    for i in range(8):
        np.fill((0, 0, 0))
        set_pixel(3, 3, wheel(i * 30))
        set_pixel(4, 3, wheel(i * 30 + 60))
        set_pixel(3, 4, wheel(i * 30 + 120))
        set_pixel(4, 4, wheel(i * 30 + 180))
        show()
        sleep(0.1)

    # Explosion
    for radius in range(1, 10):
        for y in range(HEIGHT):
            for x in range(WIDTH):
                dist = math.sqrt((x - 3.5)**2 + (y - 3.5)**2)
                if dist < radius:
                    angle = math.atan2(y - 3.5, x - 3.5)
                    hue = int((angle + math.pi) / (2 * math.pi) * 255)
                    color = wheel(hue)
                    set_pixel(x, y, color)
        show()
        sleep(0.08)

    # Sparkle out
    for _ in range(30):
        for i in range(NUM_LEDS):
            r, g, b = np[i]
            np[i] = (max(0, r - 10), max(0, g - 10), max(0, b - 10))
        show()
        sleep(0.05)

# =============================================================================
# MAIN - RUN ALL DEMOS
# =============================================================================

def run_showcase():
    """Run the complete showcase."""
    print("=" * 50)
    print("  NeoPixel 8x8 Matrix - Ultimate Showcase")
    print("=" * 50)
    print("\nPress Ctrl+C to stop at any time\n")

    demos = [
        demo_color_spectrum,
        demo_plasma,
        demo_waves,
        demo_shapes,
        demo_game_of_life,
        demo_fireworks,
        demo_matrix_rain,
        demo_fire,
        demo_starfield,
        demo_bouncing_ball,
        demo_kaleidoscope,
        demo_audio_visualizer,
        demo_spiral_galaxy,
        demo_morphing,
        demo_patterns,
        demo_radar,
        demo_finale,
    ]

    try:
        while True:
            for demo in demos:
                demo()
                clear()
                sleep(0.3)

            print("\n" + "=" * 50)
            print("  Showcase complete! Restarting...")
            print("=" * 50)
            sleep(1)

    except KeyboardInterrupt:
        clear()
        print("\n\nShowcase ended. All LEDs off.")

# =============================================================================
# RUN
# =============================================================================

if __name__ == "__main__":
    run_showcase()

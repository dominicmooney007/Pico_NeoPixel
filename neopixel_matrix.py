# NeoPixel 8x8 Matrix - X,Y Coordinate Helper
# ============================================
#
# This module makes it easy to address pixels by x,y coordinates
# instead of raw pixel indices.
#
# UNDERSTANDING PIXEL LAYOUT:
# ---------------------------
# An 8x8 NeoPixel matrix is wired as a single strip of 64 LEDs.
# The wiring pattern determines how pixel indices map to positions.
#
# SERPENTINE LAYOUT (most common):
# Row 0: →  0   1   2   3   4   5   6   7
# Row 1: ← 15  14  13  12  11  10   9   8
# Row 2: → 16  17  18  19  20  21  22  23
# Row 3: ← 31  30  29  28  27  26  25  24
# Row 4: → 32  33  34  35  36  37  38  39
# Row 5: ← 47  46  45  44  43  42  41  40
# Row 6: → 48  49  50  51  52  53  54  55
# Row 7: ← 63  62  61  60  59  58  57  56
#
# Notice: even rows go left→right, odd rows go right→left
#
# PROGRESSIVE LAYOUT (less common):
# Row 0: →  0   1   2   3   4   5   6   7
# Row 1: →  8   9  10  11  12  13  14  15
# Row 2: → 16  17  18  19  20  21  22  23
# ... (all rows go left to right)
#

from machine import Pin
from neopixel import NeoPixel


class NeoPixelMatrix:
    """
    Helper class for working with an 8x8 NeoPixel matrix using x,y coordinates.

    Usage:
        matrix = NeoPixelMatrix(pin=0)
        matrix.set_pixel(3, 4, (255, 0, 0))  # Red at x=3, y=4
        matrix.show()
    """

    def __init__(self, pin, width=8, height=8, serpentine=True, brightness=0.3):
        """
        Initialize the matrix.

        Args:
            pin: GPIO pin number connected to DIN
            width: Matrix width (default 8)
            height: Matrix height (default 8)
            serpentine: True if odd rows are wired in reverse (most common)
            brightness: Default brightness 0.0 to 1.0
        """
        self.width = width
        self.height = height
        self.serpentine = serpentine
        self.brightness = brightness
        self.num_pixels = width * height
        self.np = NeoPixel(Pin(pin, Pin.OUT), self.num_pixels)

    def xy_to_index(self, x, y):
        """
        Convert x,y coordinate to pixel index.

        Args:
            x: Column (0 = left, 7 = right)
            y: Row (0 = top, 7 = bottom)

        Returns:
            Pixel index (0-63) or None if out of bounds
        """
        # Check bounds
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return None

        # Serpentine: odd rows are reversed
        if self.serpentine and y % 2 == 1:
            return y * self.width + (self.width - 1 - x)

        # Progressive: all rows left to right
        return y * self.width + x

    def index_to_xy(self, index):
        """
        Convert pixel index to x,y coordinate.

        Args:
            index: Pixel index (0-63)

        Returns:
            Tuple (x, y) or None if out of bounds
        """
        if index < 0 or index >= self.num_pixels:
            return None

        y = index // self.width
        x_in_row = index % self.width

        if self.serpentine and y % 2 == 1:
            x = self.width - 1 - x_in_row
        else:
            x = x_in_row

        return (x, y)

    def _apply_brightness(self, color):
        """Apply brightness to a color tuple."""
        return tuple(int(c * self.brightness) for c in color)

    def set_pixel(self, x, y, color, apply_brightness=True):
        """
        Set pixel at x,y to a color.

        Args:
            x: Column (0-7)
            y: Row (0-7)
            color: Tuple (R, G, B) with values 0-255
            apply_brightness: Whether to apply brightness setting
        """
        index = self.xy_to_index(x, y)
        if index is not None:
            if apply_brightness:
                color = self._apply_brightness(color)
            self.np[index] = color

    def get_pixel(self, x, y):
        """Get color at x,y coordinate."""
        index = self.xy_to_index(x, y)
        if index is not None:
            return self.np[index]
        return None

    def set_pixel_index(self, index, color, apply_brightness=True):
        """Set pixel by raw index (0-63)."""
        if 0 <= index < self.num_pixels:
            if apply_brightness:
                color = self._apply_brightness(color)
            self.np[index] = color

    def fill(self, color):
        """Fill entire matrix with one color."""
        color = self._apply_brightness(color)
        self.np.fill(color)

    def clear(self):
        """Turn off all pixels."""
        self.np.fill((0, 0, 0))
        self.np.write()

    def show(self):
        """Update the display. Call this after making changes!"""
        self.np.write()

    # =========================================================================
    # DRAWING HELPERS
    # =========================================================================

    def draw_row(self, y, color):
        """Draw a horizontal line across the entire row."""
        for x in range(self.width):
            self.set_pixel(x, y, color)

    def draw_column(self, x, color):
        """Draw a vertical line down the entire column."""
        for y in range(self.height):
            self.set_pixel(x, y, color)

    def draw_rectangle(self, x1, y1, x2, y2, color, filled=False):
        """
        Draw a rectangle.

        Args:
            x1, y1: Top-left corner
            x2, y2: Bottom-right corner
            color: RGB tuple
            filled: If True, fill the rectangle
        """
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                if filled or x == x1 or x == x2 or y == y1 or y == y2:
                    self.set_pixel(x, y, color)

    def draw_border(self, color):
        """Draw a border around the edge of the matrix."""
        self.draw_rectangle(0, 0, self.width - 1, self.height - 1, color)

    def set_brightness(self, brightness):
        """Set brightness level (0.0 to 1.0)."""
        self.brightness = max(0.0, min(1.0, brightness))


# =============================================================================
# TEST - Determine your matrix layout
# =============================================================================

def test_layout(pin=0):
    """
    Run this to determine if your matrix uses serpentine or progressive layout.
    Watch which direction the LEDs light up on each row.
    """
    from utime import sleep

    print("Testing matrix layout...")
    print("Watch the pattern carefully!\n")

    # Test with serpentine=False to see raw indices
    matrix = NeoPixelMatrix(pin=pin, serpentine=False, brightness=0.2)

    print("Lighting pixels 0-15 in sequence...")
    print("If row 2 goes RIGHT→LEFT, your matrix is SERPENTINE")
    print("If row 2 goes LEFT→RIGHT, your matrix is PROGRESSIVE\n")

    for i in range(16):
        matrix.clear()
        matrix.set_pixel_index(i, (255, 0, 0))
        matrix.show()
        sleep(0.3)

    matrix.clear()
    print("Test complete!")


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    from utime import sleep

    print("NeoPixel Matrix - X,Y Coordinate Demo")
    print("=" * 40)

    # Create matrix (adjust serpentine based on your matrix!)
    matrix = NeoPixelMatrix(pin=0, serpentine=True, brightness=0.3)

    # Colors
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    WHITE = (255, 255, 255)

    try:
        while True:
            # Demo 1: Draw using x,y coordinates
            print("Demo: Drawing at specific coordinates")
            matrix.clear()
            matrix.set_pixel(0, 0, RED)      # Top-left
            matrix.set_pixel(7, 0, GREEN)    # Top-right
            matrix.set_pixel(0, 7, BLUE)     # Bottom-left
            matrix.set_pixel(7, 7, WHITE)    # Bottom-right
            matrix.set_pixel(3, 3, RED)      # Center-ish
            matrix.set_pixel(4, 4, GREEN)    # Center-ish
            matrix.show()
            sleep(2)

            # Demo 2: Draw rows
            print("Demo: Drawing rows")
            matrix.clear()
            matrix.draw_row(0, RED)
            matrix.draw_row(7, BLUE)
            matrix.show()
            sleep(2)

            # Demo 3: Draw columns
            print("Demo: Drawing columns")
            matrix.clear()
            matrix.draw_column(0, GREEN)
            matrix.draw_column(7, WHITE)
            matrix.show()
            sleep(2)

            # Demo 4: Draw border
            print("Demo: Drawing border")
            matrix.clear()
            matrix.draw_border(BLUE)
            matrix.show()
            sleep(2)

            # Demo 5: Moving dot using coordinates
            print("Demo: Moving dot")
            for y in range(8):
                for x in range(8):
                    matrix.clear()
                    matrix.set_pixel(x, y, GREEN)
                    matrix.show()
                    sleep(0.05)

            print("\nRestarting demos...\n")

    except KeyboardInterrupt:
        matrix.clear()
        print("\nStopped.")

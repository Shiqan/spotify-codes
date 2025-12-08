from typing import List
from PIL import Image, ImageDraw


class Renderer:
    def __init__(
        self, bar_width: int = 20, bg_color: str = "black", bar_color: str = "white"
    ):
        """
        Initialize renderer.

        Args:
            bar_width: Width of each bar in pixels (default 20)
            bg_color: Background color (default black)
            bar_color: Bar color (default white)
        """
        self.bar_width = bar_width
        self.bg_color = bg_color
        self.bar_color = bar_color

    def render(self, bar_heights: List[int], filename: str = "code.png"):
        """
        Render bar heights to a PNG image.

        Args:
            bar_heights: List of bar heights (0-7)
            filename: Output filename
        """
        # Validate input
        if len(bar_heights) != 23:
            raise ValueError(f"Expected 23 bars, got {len(bar_heights)}")

        if not all(0 <= h <= 7 for h in bar_heights):
            raise ValueError("Bar heights must be between 0 and 7")

        # Image dimensions
        width = len(bar_heights) * self.bar_width
        height = max(bar_heights) * self.bar_width + 20  # Extra padding

        # Create image
        img = Image.new("RGB", (width, height), color=self._color_to_rgb(self.bg_color))
        draw = ImageDraw.Draw(img)

        # Draw each bar
        for i, height in enumerate(bar_heights):
            x0 = i * self.bar_width
            y0 = height * self.bar_width
            x1 = x0 + self.bar_width
            y1 = height * self.bar_width + 10  # Arbitrary bar thickness

            draw.rectangle([x0, y0, x1, y1], fill=self._color_to_rgb(self.bar_color))

        # Save image
        img.save(filename)

    def _color_to_rgb(self, color: str) -> tuple:
        """Convert color name to RGB tuple."""
        colors = {
            "black": (0, 0, 0),
            "white": (255, 255, 255),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
        }

        if color in colors:
            return colors[color]

        raise ValueError(f"Unknown color: {color}")
